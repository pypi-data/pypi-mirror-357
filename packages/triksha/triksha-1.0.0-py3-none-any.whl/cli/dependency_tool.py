"""CLI tool for managing model dependencies"""
import argparse
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.dependency_manager import DependencyManager

def main():
    """Main entry point for dependency management tool"""
    console = Console()
    
    parser = argparse.ArgumentParser(
        description="Dravik Dependency Management Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check dependencies for a model')
    check_parser.add_argument('model', help='Model name to check dependencies for')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install dependencies for a model')
    install_parser.add_argument('model', help='Model name to install dependencies for')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List known model dependencies')
    
    # Check missing command
    missing_parser = subparsers.add_parser('missing', help='Check for missing dependencies in requirements.txt')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'check':
        check_dependencies(args.model, console)
    elif args.command == 'install':
        install_dependencies(args.model, console)
    elif args.command == 'list':
        list_dependencies(console)
    elif args.command == 'missing':
        check_missing(console)
    else:
        parser.print_help()

def check_dependencies(model_name: str, console: Console):
    """Check dependencies for a model"""
    console.print(Panel(f"Checking dependencies for model: [bold cyan]{model_name}[/]"))
    
    required_packages = []
    for arch, packages in DependencyManager.MODEL_DEPENDENCIES.items():
        if arch.lower() in model_name.lower():
            required_packages.extend(packages)
    
    if not required_packages:
        console.print("[yellow]No specific dependencies identified for this model.[/]")
        return
    
    console.print(f"Required dependencies:")
    
    for package_spec in required_packages:
        base_package = package_spec.split(">=")[0].split("==")[0].strip()
        installed = DependencyManager.check_dependency(base_package)
        
        status = "[green]✓ Installed[/]" if installed else "[red]✗ Missing[/]"
        console.print(f"  • {package_spec}: {status}")
        
    # Show overall status
    all_installed = all(
        DependencyManager.check_dependency(pkg.split(">=")[0].split("==")[0].strip()) 
        for pkg in required_packages
    )
    
    if all_installed:
        console.print("[green]All dependencies are installed.[/]")
    else:
        console.print("[yellow]Some dependencies are missing. Run 'install' command to install them.[/]")
        console.print("Command to install missing dependencies:")
        console.print(Syntax(
            f"python -m cli.dependency_tool install {model_name}",
            "bash"
        ))

def install_dependencies(model_name: str, console: Console):
    """Install dependencies for a model"""
    console.print(Panel(f"Installing dependencies for model: [bold cyan]{model_name}[/]"))
    
    success = DependencyManager.ensure_model_dependencies(model_name)
    
    if success:
        console.print("[green]All dependencies are now installed.[/]")
    else:
        console.print("[red]Failed to install some dependencies.[/]")
        console.print("Please try to install them manually with:")
        
        for cmd in DependencyManager.get_installation_commands(model_name):
            console.print(f"  {cmd}")

def list_dependencies(console: Console):
    """List known model dependencies"""
    console.print(Panel("[bold]Known Model Dependencies[/]"))
    
    for arch, packages in DependencyManager.MODEL_DEPENDENCIES.items():
        console.print(f"[bold cyan]{arch}[/]:")
        for package in packages:
            console.print(f"  • {package}")
        console.print()

def check_missing(console: Console):
    """Check for missing dependencies in requirements.txt"""
    console.print(Panel("[bold]Checking Missing Dependencies[/]"))
    
    # Get all unique dependencies from MODEL_DEPENDENCIES
    all_dependencies = set()
    for packages in DependencyManager.MODEL_DEPENDENCIES.values():
        for package in packages:
            # Strip version info
            base_package = package.split(">=")[0].split("==")[0].strip()
            all_dependencies.add(base_package)
    
    # Check if requirements.txt exists
    req_file = Path(__file__).parent.parent / "requirements.txt"
    if not req_file.exists():
        console.print(f"[yellow]requirements.txt not found at {req_file}[/]")
        return
    
    # Read requirements.txt
    with open(req_file, 'r') as f:
        requirements = f.readlines()
    
    # Extract package names from requirements
    req_packages = set()
    for line in requirements:
        line = line.strip()
        if line and not line.startswith('#'):
            # Split by comparison operators and whitespace
            package = line.split('>=')[0].split('==')[0].split('>')[0].split('<')[0].strip()
            req_packages.add(package)
    
    # Find missing dependencies
    missing = all_dependencies - req_packages
    
    if missing:
        console.print("[yellow]Missing dependencies in requirements.txt:[/]")
        for package in sorted(missing):
            console.print(f"  • {package}")
            
        # Get the original version requirements for missing packages
        missing_with_versions = []
        for packages in DependencyManager.MODEL_DEPENDENCIES.values():
            for package in packages:
                base_package = package.split(">=")[0].split("==")[0].strip()
                if base_package in missing:
                    missing_with_versions.append(package)
        
        console.print("\nAdd these lines to requirements.txt:")
        for package in sorted(missing_with_versions):
            console.print(f"{package}")
    else:
        console.print("[green]All model dependencies are included in requirements.txt.[/]")

if __name__ == "__main__":
    main()
