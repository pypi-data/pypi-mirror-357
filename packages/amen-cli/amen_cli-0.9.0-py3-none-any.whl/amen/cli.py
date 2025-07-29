import os
import sys
import subprocess
import venv
from pathlib import Path
import re
import time
import psutil
from datetime import datetime
from rich.live import Live
from rich.table import Table
from rich import box

import click
import questionary
import requests  
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from . import __version__

from .frameworks import FRAMEWORKS
from .templates import TemplateManager
from .editor import edit_file

console = Console()

PACKAGE_CACHE_DIR = Path.home() / ".amen" / "package_cache"
PACKAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

class PipNetworkError(Exception):
    pass

VALID_FRAMEWORKS = ['flask', 'fastapi', 'bottle', 'pyramid']
VALID_PROJECT_TYPES = ['webapp', 'api']

def get_venv_path(app_path: Path) -> Path:
    """Get virtual environment path based on OS"""
    return app_path / "venv"

def get_pip_path(venv_path: Path) -> Path:
    """Get pip executable path based on OS"""
    if sys.platform.startswith('linux'):
        return venv_path / "bin" / "pip"
    return venv_path / "Scripts" / "pip"

def get_python_path(venv_path: Path) -> Path:
    """Get python executable path based on OS"""
    if sys.platform.startswith('linux'):
        return venv_path / "bin" / "python"
    return venv_path / "Scripts" / "python"

def create_project(path, framework, project_type):
    """
    Create a new project with the specified framework and type.
    
    Args:
        path (str): Project directory path
        framework (str): Web framework to use
        project_type (str): Type of project (webapp/api)
    """
    if framework not in VALID_FRAMEWORKS:
        raise ValueError(f"Invalid framework. Choose from: {VALID_FRAMEWORKS}")
    
    if project_type not in VALID_PROJECT_TYPES:
        raise ValueError(f"Invalid project type. Choose from: {VALID_PROJECT_TYPES}")

    # Create project directory
    os.makedirs(path, exist_ok=True)
    
    # Create basic structure
    os.makedirs(os.path.join(path, "app"), exist_ok=True)
    os.makedirs(os.path.join(path, "app", "templates"), exist_ok=True)
    os.makedirs(os.path.join(path, "app", "static"), exist_ok=True)
    
    # Create empty files
    open(os.path.join(path, "requirements.txt"), 'a').close()
    open(os.path.join(path, "README.md"), 'a').close()

class AmenCLI:
    def __init__(self):
        self.template_manager = TemplateManager()
    
    def welcome_banner(self):
        """Display welcome banner"""
        from . import __version__
        console.print(Panel.fit(
            f"""AMEN: inspired by the laravel installer, a python Web Application Scaffolding
        Create your web applications with ease!
        By [bold magenta]Tanaka Chinengundu[/bold magenta]
        [bold blue]Version: {__version__}[/bold blue]
            """,
            border_style="magenta"
        ))
        console.print()
    
    def select_framework(self) -> str:
        """Interactive framework selection"""
        frameworks = list(FRAMEWORKS.keys())
        
        choice = questionary.select(
            "🚀 Select a web framework:",
            choices=[
                questionary.Choice(f"{FRAMEWORKS[fw]['name']} - {FRAMEWORKS[fw]['description']}", fw)
                for fw in frameworks
            ]
        ).ask()
        
        return choice
    
    def select_app_type(self) -> str:
        """Select application type"""
        return questionary.select(
            "🏗️  What type of application?",
            choices=[
                questionary.Choice("Full Web Application (with frontend)", "webapp"),
                questionary.Choice("API Only", "api"),
            ]
        ).ask()
    
    def get_app_name(self) -> str:
        """Get application name"""
        return questionary.text(
            "📝 Enter your application name:",
            validate=lambda x: len(x.strip()) > 0 or "Application name cannot be empty"
        ).ask().strip()
    
    def select_database(self) -> str:
        """Select database type"""
        return questionary.select(
            "💾 Select a database:",
            choices=[
                questionary.Choice("SQLite3 - Lightweight, serverless database", "sqlite3"),
                questionary.Choice("MySQL - Robust client-server database", "mysql"),
                questionary.Choice("None - No database", "none"),
            ]
        ).ask()

    def create_virtual_environment(self, app_path: Path) -> bool:
        """Create virtual environment"""
        venv_path = get_venv_path(app_path)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Creating virtual environment...", total=None)
                venv.create(venv_path, with_pip=True)
                progress.update(task, description="✅ Virtual environment created")
            
            return True
        except Exception as e:
            console.print(f"❌ Error creating virtual environment: {e}", style="red")
            return False

    def _cache_packages(self, packages: list[str], progress: Progress, task_id: int):
        """Cache packages to the PACKAGE_CACHE_DIR."""
        packages_to_cache = []
        for package in packages:
            if not (PACKAGE_CACHE_DIR / f"{package}.whl").exists():
                packages_to_cache.append(package)

        if not packages_to_cache:
            console.print("✅ All packages already cached.", style="green")
            return

        try:
            progress.update(task_id, description="Caching packages...")
            subprocess.run(
                [sys.executable, "-m", "pip", "download", "--no-cache-dir", "-d", str(PACKAGE_CACHE_DIR), *packages_to_cache],
                check=True,
                capture_output=True
            )
            progress.update(task_id, description="✅ Packages cached")
        except subprocess.CalledProcessError:
            # Silently ignore caching errors
            console.print(f"⚠️ Error caching packages (network issue). Proceeding with available cache.", style="yellow")
            progress.update(task_id, description="⚠️ Error caching packages")
        except OSError as e:
            console.print(f"❌ Network error during caching: {e}", style="red")
            progress.update(task_id, description="❌ Network error during caching")

    def install_framework(self, app_path: Path, framework: str) -> bool:
        """Install selected framework in virtual environment"""
        venv_path = get_venv_path(app_path)
        pip_path = get_pip_path(venv_path)

        framework_info = FRAMEWORKS[framework]
        packages = framework_info['packages']

        # Check if packages are cached
        cached_packages = all((PACKAGE_CACHE_DIR / f"{pkg}.whl").exists() for pkg in packages)

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task_id = progress.add_task(f"Installing {framework_info['name']}...", total=None)

                if cached_packages:
                    console.print("📦 Installing packages from cache...", style="green")
                else:
                    try:
                        self._cache_packages(packages, progress, task_id)
                    except OSError as e:
                        console.print(f"⚠️ Could not cache packages due to network error: Installing from available cache.", style="yellow")
                        if not cached_packages:
                            console.print("❌ No cached packages found. Installation cannot proceed.", style="red")
                            return False

                progress.update(task_id, description=f"Installing {framework_info['name']}...")
                # Install packages from the cache
                subprocess.run(
                    [str(pip_path), "install", "--no-index", "--find-links", str(PACKAGE_CACHE_DIR), *packages],
                    check=True,
                    capture_output=True
                )

                progress.update(task_id, description=f"✅ {framework_info['name']} installed")

            return True
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Error installing {framework_info['name']}: {e}", style="red")
            return False
    
    def create_app(self):
        """Main app creation flow"""
        self.welcome_banner()
        
        # Get user choices
        framework = self.select_framework()
        if not framework:
            console.print("❌ No framework selected. Exiting.", style="red")
            return
            
        app_type = self.select_app_type()
        if not app_type:
            console.print("❌ No application type selected. Exiting.", style="red")
            return
            
        app_name = self.get_app_name()
        if not app_name:
            console.print("❌ No application name provided. Exiting.", style="red")
            return

        database = self.select_database()
        # Remove the exit condition for database selection
        # Continue with project creation regardless of database choice
        
        # Create application directory
        app_path = Path.cwd() / app_name
        
        if app_path.exists():
            overwrite = questionary.confirm(
                f"Directory '{app_name}' already exists. Overwrite?"
            ).ask()
            
            if not overwrite:
                console.print("❌ Operation cancelled.", style="yellow")
                return
            
            import shutil
            shutil.rmtree(app_path)

        app_path.mkdir()
        console.print(f"📁 Created directory: {app_path}", style="green")

        # Create virtual environment
        if not self.create_virtual_environment(app_path):
            return

        # Install framework
        if not self.install_framework(app_path, framework):
            return

        # Generate project structure
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating project structure...", total=None)
            self.template_manager.generate_structure(app_path, framework, app_type, app_name, database)
            progress.update(task, description="✅ Project structure generated")

        # Create .amen_config file
        with open(app_path / ".amen_config", "w") as f:
            f.write(framework + "\n")  

        console.print(Panel(
            f"""🎉 Successfully created '{app_name}'!

📁 Next Steps:
   1. cd {app_name}
   2. source venv/bin/activate  (Linux/Mac) or venv\\Scripts\\activate (Windows)
   3. amen run {app_name}
   
Your app will be running at http://localhost:{FRAMEWORKS[framework]['default_port']}
            """.strip(),
            title="🎊 Project Created Successfully!",
            border_style="green"
        ))

@click.group()
def main():
    """Amen - inspired by the laravel installer. Python web framework scaffolding tool"""
    pass

@main.command()
@click.option(
    "--framework", "-f",
    type=click.Choice(list(FRAMEWORKS.keys()), case_sensitive=False),
    help="Framework to use for the new project (e.g., flask, fastapi)"
)
@click.option(
    "--type", "-t",
    type=click.Choice(['webapp', 'api'], case_sensitive=False),
    help="Type of application to create (webapp or api)"
)
@click.option(
    "--name", "-n",
    type=str,
    help="Name of the application"
)
def create(framework, type, name):
    """Create a new web application"""
    cli = AmenCLI()
    # If framework is provided, override the interactive prompt
    if framework:
        original_select_framework = cli.select_framework
        cli.select_framework = lambda: framework.lower()
   
    if type:
        original_select_app_type = cli.select_app_type
        cli.select_app_type = lambda: type.lower()
   
    if name:
        original_get_app_name = cli.get_app_name
        cli.get_app_name = lambda: name
    cli.create_app()

@main.command()
@click.argument("app_name", type=str)
def run(app_name):
    """Runs the development server for a created application."""
    app_path = str(Path.cwd() / app_name)

    print("App path", app_path)
    if not Path(app_path).exists() or not Path(app_path).is_dir():
        console.print(f"❌ Application '{app_name}' not found.", style="red")
        return

    venv_path = get_venv_path(Path(app_path))
    if not venv_path.exists() or not venv_path.is_dir():
        console.print(f"❌ Virtual environment not found for '{app_name}'.", style="red")
        console.print("   Please create the application using `amen create` first.", style="yellow")
        return

    # Find the framework used by the application (read from a config file or similar)
    config_file = Path(app_path) / ".amen_config"
    if not config_file.exists():
        console.print(f"❌ Configuration file '.amen_config' not found in '{app_name}'.", style="red")
        console.print("   Please ensure the application was created with `amen create`.", style="yellow")
        return

    with open(config_file, "r") as f:
        framework = f.readline().strip() 

    if framework not in FRAMEWORKS:
        console.print(f"❌ Unsupported framework '{framework}' in '.amen_config'.", style="red")
        return

    entry_file = "run.py"
    default_port = FRAMEWORKS[framework]['default_port']

    # Construct the run command
    run_command = f"\"{get_python_path(venv_path)}\" \"{Path(app_path) / entry_file}\""

    try:
        console.print(f"🚀 Starting '{app_name}' using {framework}...", style="green")
        env = os.environ.copy()  # Copy existing environment variables
        env["PYTHONPATH"] = str(Path(app_path))  # Add app path to PYTHONPATH
        process = subprocess.Popen(run_command, shell=True, cwd=str(Path(app_path)), env=env)
        process.wait() 
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Error running the application: {e}", style="red")
    except FileNotFoundError as e:
        console.print(f"❌ Error: {e}.  Make sure {entry_file} exists.", style="red")

@main.command()
@click.argument("app_name", type=str)
def test(app_name):
    """Run tests for the specified application using pytest and generate a coverage report."""
    app_path = str(Path.cwd() / app_name)

    if not Path(app_path).exists() or not Path(app_path).is_dir():
        console.print(f"❌ Application '{app_name}' not found.", style="red")
        return

    venv_path = get_venv_path(Path(app_path))
    if not venv_path.exists() or not venv_path.is_dir():
        console.print(f"❌ Virtual environment not found for '{app_name}'.", style="red")
        console.print("   Please create the application using `amen create` first.", style="yellow")
        return

    # Determine pytest path based on OS
    if sys.platform == "win32":
        pytest_path = venv_path / "Scripts" / "pytest"
    else:
        pytest_path = venv_path / "bin" / "pytest"

    try:
        console.print(f"🧪 Running tests for '{app_name}'...", style="blue")
        # Run pytest with coverage
        subprocess.run(
            [str(pytest_path), "--cov=.", "--cov-report=term-missing"],
            cwd=str(Path(app_path)),
            check=True,
        )
        console.print(f"✅ Tests completed successfully for '{app_name}'.", style="green")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Tests failed: {e}", style="red")
    except FileNotFoundError as e:
        console.print(f"❌ Error: {e}. Make sure pytest is installed in the virtual environment.", style="red")

@main.command()
def update():
    """Check for a new version on PyPI and upgrade the package."""
    package_name = "amen-cli"
    console.print(f"🔍 Checking for updates for '{package_name}'...", style="blue")

    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
        )
        current_version = result.stdout.split("Version: ")[1].splitlines()[0]

        if current_version == latest_version:
            console.print(f"✅ You are already using the latest version ({current_version}).", style="green")
        else:
            console.print(f"⬆️ New version available: {latest_version} (current: {current_version}).", style="yellow")
            update = questionary.confirm("Do you want to update to the latest version?").ask()
            if update:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Installing update...", total=None)
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--use-feature=fast-deps", "--upgrade", "--user", f"{package_name}=={latest_version}"],
                        check=True,
                        capture_output=True,
                    )
                    progress.update(task, description="✅ Update completed")
                console.print(f"✅ Successfully updated to version {latest_version}.", style="green")
            else:
                console.print("❌ Update cancelled.", style="red")
    except requests.RequestException as e:
        console.print(f"❌ Failed to fetch version information: {e}", style="red")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Failed to update the package: {e}", style="red")
    except Exception as e:
        console.print(f"❌ An unexpected error occurred: {e}", style="red")

@main.command
def about():
    from . import __version__, __description__,__author__,__url__, SUPPORTED_FRAMEWORKS
    console.print(Panel.fit(f"""
                    Current version: [blue]{__version__}[/blue]
                    Description: [white]{__description__}[/white]
                    Developed by: [bold magenta]{__author__}[/bold magenta]
                    Project URL: [bright_cyan][link={__url__}]{__url__}[/link][/bright_cyan]
                            """, style="green"))

@main.command()
@click.argument("app_name", type=str)
@click.option(
    "--framework",
    "-f",
    type=click.Choice(list(FRAMEWORKS.keys()), case_sensitive=False),
    help="Specify the framework (flask, fastapi, etc.). If not provided, it will be detected from .amen_config.",
)
def config(app_name, framework):

    """Manage project-specific configuration settings."""
    app_path = Path.cwd() / app_name

    if not app_path.exists() or not app_path.is_dir():
        console.print(f"❌ Application '{app_name}' not found.", style="red")
        return

    config_file = app_path / ".env"
    if not config_file.exists():
        console.print(f"⚙️  Creating .env file for '{app_name}'.", style="yellow")
        config_file.touch()

    console.print(f"⚙️  Opening .env file for '{app_name}' in Ring editor.", style="green")
    
    try:
        edit_file(str(config_file))
    except Exception as e:
        console.print(f"❌ Failed to open .env file: {e}", style="red")


@main.command()
@click.argument("app_name", type=str)
@click.option(
    "--format", "-f",
    type=click.Choice(['txt', 'json', 'csv', 'xml'], case_sensitive=False),
    default='txt',
    help="Output format for the security audit report"
)
@click.option(
    "--severity", "-s",
    type=click.Choice(['low','l','m','h', 'medium', 'high'], case_sensitive=False),
    help="Filter issues by severity level"
)
@click.option(
    "--output", "-o",
    type=str,
    help="Save audit report to specified file"
)
def audit(app_name, format, severity, output):
    """Run security audit on the specified application using bandit."""
    app_path = Path.cwd() / app_name

    if not app_path.exists() or not app_path.is_dir():
        console.print(f"❌ Application '{app_name}' not found.", style="red")
        return

    venv_path = get_venv_path(app_path)
    if not venv_path.exists() or not venv_path.is_dir():
        console.print(f"❌ Virtual environment not found for '{app_name}'.", style="red")
        console.print("   Please create the application using `amen create` first.", style="yellow")
        return

    # Build bandit command (using globally installed bandit)
    bandit_cmd = ["bandit", "-r", str(app_path)]  # Pass the full path to bandit
    
    # Add format option
    if format != 'txt':
        bandit_cmd.extend(["-f", format])
    
    # Add severity filter
    if severity:
        severity_map = {'low': 'l', 'medium': 'm', 'high': 'h'}
        bandit_cmd.extend(["--severity-level", severity_map[severity]])
    
    # Add output file option
    if output:
        bandit_cmd.extend(["-o", output])

    try:
        console.print(f"🔍 Running security audit for '{app_name}'...", style="blue")
        
        # Run bandit
        result = subprocess.run(
            bandit_cmd,
            cwd=str(app_path),
            capture_output=True,
            text=True
        )
        
        # Bandit returns exit code 1 when issues are found, which is normal
        if result.returncode == 0:
            console.print(f"✅ Security audit completed - No issues found!", style="green")
        elif result.returncode == 1:
            console.print(f"⚠️  Security audit completed - Issues found:", style="yellow")
        else:
            console.print(f"❌ Security audit failed with exit code {result.returncode}", style="red")
            if result.stderr:
                console.print(f"Error: {result.stderr}", style="red")
            return
        
        # Display results
        if not output:
            if result.stdout:
                console.print(result.stdout)
            if result.stderr and result.returncode != 1:
                console.print("\nWarnings/Errors:", style="yellow")
                console.print(result.stderr)
        else:
            console.print(f"📄 Audit report saved to: {output}", style="green")
            
    except FileNotFoundError as e:
        console.print(f"❌ Error: {e}. Make sure bandit is properly installed.", style="red")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Security audit failed: {e}", style="red")

@main.command()
@click.option('--port', '-p', default=5050, help='Port to run the web interface on')
def web(port):
    """Launch web interface for creating projects"""
    from .web import run_web_interface
    try:
        run_web_interface(port)
    except Exception as e:
        console.print(f"❌ Error starting web interface: {e}", style="red")
        console.print("   Make sure Flask is installed in your environment.", style="yellow")


@main.command()
@click.argument("app_name", type=str)
@click.option("--port", "-p", type=int, help="Port to monitor")
@click.option("--refresh", "-r", type=float, default=0.1, help="Refresh rate in seconds")
@click.option("--web", is_flag=True, help="Run web-based monitor")
def monitor(app_name, port, refresh, web):
    """Monitor application status and resource usage"""
    app_path = Path.cwd() / app_name

    if not app_path.exists():
        console.print(f"❌ Application '{app_name}' not found.", style="red")
        return

    if web:
        from .monitor_web import run_monitor_web
        run_monitor_web(app_name=app_name, port=port, refresh=refresh)


    try:
        def get_process_info(port):
            """Get process information for the given port"""
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    for conn in proc.net_connections():
                        if conn.laddr.port == port:
                            return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return None

        def generate_table(proc):
            """Generate rich table with monitoring data"""
            table = Table(
                title=f"Application Monitor - {app_name}",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold magenta"
            )
            
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Time", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            if proc:
                table.add_row("Status", "[green]Running[/green]")
                table.add_row("PID", str(proc.pid))
                table.add_row("CPU Usage", f"{proc.cpu_percent()}%")
                table.add_row("Memory Usage", f"{proc.memory_percent():.1f}%")
                
                # Add memory details
                mem_info = proc.memory_info()
                table.add_row("RSS Memory", f"{mem_info.rss / (1024*1024):.1f} MB")
                table.add_row("VMS Memory", f"{mem_info.vms / (1024*1024):.1f} MB")
                
                # Add thread count
                table.add_row("Threads", str(proc.num_threads()))
                
                # Add open files count
                try:
                    table.add_row("Open Files", str(len(proc.open_files())))
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    table.add_row("Open Files", "N/A")
            else:
                table.add_row("Status", "[red]Not Running[/red]")
            
            return table

        console.print(f"🔍 Monitoring {app_name}...", style="blue")
        console.print(f"Press Ctrl+C to stop monitoring", style="yellow")
        
        with Live(refresh_per_second=1/refresh) as live:
            while True:
                proc = get_process_info(port) if port else None
                live.update(generate_table(proc))
                time.sleep(refresh)

    except KeyboardInterrupt:
        console.print("\n✋ Monitoring stopped", style="yellow")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


if __name__ == "__main__":
    main()