"""Command-line interface for dependency management"""
import argparse
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.dependency_manager import DependencyManager

def main():
    """Main entry point for the dependency CLI"""
    console = Console()
    
    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="Dravik Dependency Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("--model", type=str, help="Model to install dependencies for")
    install_parser.add_argument("--sentencepiece", action="store_true", help="Install SentencePiece")
    install_parser.add_argument("--tiktoken", action="store_true", help="Install tiktoken")
    install_parser.add_argument("--all", action="store_true", help="Install all dependencies")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check dependencies")
    check_parser.add_argument("--model", type=str, help="Model to check dependencies for")
    check_parser.add_argument("--all", action="store_true", help="Check all dependencies")
    
    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Fix common dependency issues")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if not args.command:
        parser.print_help()
        return
        
    if args.command == "install":
        handle_install(args, console)
    elif args.command == "check":
        handle_check(args, console)
    elif args.command == "fix":
        handle_fix(console)

def handle_install(args, console: Console):
    """Handle the install command"""
    console.print(Panel("[bold]Installing Dependencies[/]", style="cyan"))
    
    # Install all dependencies
    if args.all:
        console.print("Installing all dependencies...")
        
        # Install model-specific dependencies
        for model in ["gemma", "llama", "mistral", "mixtral", "phi", "qwen"]:
            success = DependencyManager.ensure_model_dependencies(model)
            if success:
                console.print(f"[green]✓ Dependencies for {model} installed successfully[/]")
            else:
                console.print(f"[red]✗ Failed to install some dependencies for {model}[/]")
                console.print(f"Please install manually with: [cyan]pip install {' '.join(DependencyManager.get_installation_commands(model))}[/]")
        
        return
        
    # Install dependencies for specific model
    if args.model:
        console.print(f"Installing dependencies for model: [bold]{args.model}[/]")
        success = DependencyManager.ensure_model_dependencies(args.model)
        
        if success:
            console.print(f"[green]✓ Dependencies for {args.model} installed successfully[/]")
        else:
            console.print(f"[red]✗ Failed to install some dependencies for {args.model}[/]")
            console.print(f"Please install manually with:")
            for cmd in DependencyManager.get_installation_commands(args.model):
                console.print(f"  [cyan]{cmd}[/]")
        
        return
        
    # Install specific packages
    if args.sentencepiece:
        console.print("Installing SentencePiece...")
        try:
            import sentencepiece
            console.print("[green]✓ SentencePiece is already installed[/]")
        except ImportError:
            success = DependencyManager.install_package("sentencepiece>=0.1.97")
            if success:
                console.print("[green]✓ SentencePiece installed successfully[/]")
            else:
                console.print("[red]✗ Failed to install SentencePiece[/]")
                console.print("Please install manually with: [cyan]pip install sentencepiece>=0.1.97[/]")
    
    if args.tiktoken:
        console.print("Installing tiktoken...")
        try:
            import tiktoken
            console.print("[green]✓ tiktoken is already installed[/]")
        except ImportError:
            success = DependencyManager.install_package("tiktoken>=0.5.0")
            if success:
                console.print("[green]✓ tiktoken installed successfully[/]")
            else:
                console.print("[red]✗ Failed to install tiktoken[/]")
                console.print("Please install manually with: [cyan]pip install tiktoken>=0.5.0[/]")
    
    # No arguments provided
    if not any([args.all, args.model, args.sentencepiece, args.tiktoken]):
        console.print("[yellow]No dependencies specified to install.[/]")
        console.print("Use --model, --sentencepiece, --tiktoken, or --all")

def handle_check(args, console: Console):
    """Handle the check command"""
    console.print(Panel("[bold]Checking Dependencies[/]", style="cyan"))
    
    # Check all dependencies
    if args.all:
        console.print("Checking all dependencies...")
        all_ok = True
        
        for model in ["gemma", "llama", "mistral", "mixtral", "phi", "qwen"]:
            console.print(f"\n[bold]Checking {model}:[/]")
            
            # Get required packages for this model
            required_packages = []
            for arch, packages in DependencyManager.MODEL_DEPENDENCIES.items():
                if arch.lower() in model:
                    required_packages.extend(packages)
            
            # Check each package
            if not required_packages:
                console.print("  No specific dependencies required")
                continue
                
            for package_spec in required_packages:
                base_package = package_spec.split(">=")[0].split("==")[0].strip()
                installed = DependencyManager.check_dependency(base_package)
                
                status = "[green]✓ Installed[/]" if installed else "[red]✗ Missing[/]"
                console.print(f"  • {package_spec}: {status}")
                
                if not installed:
                    all_ok = False
        
        if all_ok:
            console.print("\n[green]All dependencies are installed![/]")
        else:
            console.print("\n[yellow]Some dependencies are missing. Use 'install' command to install them.[/]")
        
        return
        
    # Check dependencies for specific model
    if args.model:
        console.print(f"Checking dependencies for model: [bold]{args.model}[/]")
        
        # Get required packages
        required_packages = []
        for arch, packages in DependencyManager.MODEL_DEPENDENCIES.items():
            if arch.lower() in args.model.lower():
                required_packages.extend(packages)
        
        # Check each package
        all_installed = True
        if not required_packages:
            console.print("[yellow]No specific dependencies identified for this model.[/]")
            return
            
        for package_spec in required_packages:
            base_package = package_spec.split(">=")[0].split("==")[0].strip()
            installed = DependencyManager.check_dependency(base_package)
            
            status = "[green]✓ Installed[/]" if installed else "[red]✗ Missing[/]"
            console.print(f"  • {package_spec}: {status}")
            
            if not installed:
                all_installed = False
        
        if all_installed:
            console.print("[green]All dependencies are installed![/]")
        else:
            console.print("[yellow]Some dependencies are missing. Use 'install' command to install them.[/]")
            console.print(f"Run: [cyan]python -m cli.dependency_cli install --model {args.model}[/]")
        
        return
    
    # No arguments provided
    console.print("[yellow]No check option specified.[/]")
    console.print("Use --model or --all")

def handle_fix(console: Console):
    """Handle the fix command"""
    console.print(Panel("[bold]Fixing Common Dependency Issues[/]", style="cyan"))
    
    # Try to fix common issues
    console.print("Checking for common dependency issues...")
    
    # Check for system dependencies (Linux only)
    if sys.platform.startswith('linux'):
        try:
            console.print("Checking for system dependencies...")
            import subprocess
            
            # Check if we have apt-get
            try:
                subprocess.run(["apt-get", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                
                # Install system dependencies for SentencePiece
                console.print("Installing system dependencies for SentencePiece...")
                cmd = [
                    "sudo", "apt-get", "update", "&&",
                    "sudo", "apt-get", "install", "-y",
                    "cmake", "build-essential", "pkg-config", "libgoogle-perftools-dev"
                ]
                process = subprocess.run(" ".join(cmd), shell=True, check=False)
                
                if process.returncode == 0:
                    console.print("[green]✓ System dependencies installed[/]")
                else:
                    console.print("[yellow]Could not install system dependencies automatically[/]")
            except:
                console.print("[yellow]apt-get not found, skipping system dependency installation[/]")
        except:
            console.print("[yellow]Could not check system dependencies[/]")
    
    # Try to reinstall problematic packages
    console.print("\nAttempting to reinstall potentially problematic packages...")
    
    packages_to_reinstall = ["sentencepiece", "tokenizers", "transformers"]
    for package in packages_to_reinstall:
        try:
            console.print(f"Reinstalling {package}...")
            cmd = [sys.executable, "-m", "pip", "install", "--force-reinstall", package]
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            
            if process.returncode == 0:
                console.print(f"[green]✓ {package} reinstalled[/]")
            else:
                console.print(f"[yellow]Could not reinstall {package}[/]")
        except:
            console.print(f"[yellow]Error during {package} reinstallation[/]")
    
    console.print("\n[bold]Fix process complete[/]")
    console.print("If issues persist, try manually installing dependencies:")
    console.print("  [cyan]pip install sentencepiece>=0.1.97 tiktoken>=0.5.0[/]")

if __name__ == "__main__":
    main()
