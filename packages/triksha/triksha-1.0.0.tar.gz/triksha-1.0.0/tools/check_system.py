"""System check utility for Dravik"""
import os
import sys
import importlib
import subprocess
import platform
from pathlib import Path
import torch
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.dependency_manager import DependencyManager

def check_system_setup():
    """Check system setup for Dravik"""
    console = Console()
    
    console.print(Panel(
        "[bold]Dravik System Check[/]\n\n"
        "This utility checks your system setup for Dravik.",
        title="SYSTEM CHECK",
        border_style="green"
    ))
    
    # System information
    console.print("[bold]System Information:[/]")
    system_info = Table(show_header=False)
    system_info.add_column("Property")
    system_info.add_column("Value")
    
    system_info.add_row("Platform", platform.platform())
    system_info.add_row("Python Version", platform.python_version())
    system_info.add_row("Installation Path", sys.executable)
    
    # Add torch info
    if importlib.util.find_spec("torch"):
        import torch
        system_info.add_row("PyTorch Version", torch.__version__)
        system_info.add_row("CUDA Available", str(torch.cuda.is_available()))
        if torch.cuda.is_available():
            system_info.add_row("CUDA Version", torch.version.cuda)
            system_info.add_row("GPU Device", torch.cuda.get_device_name(0))
    
    console.print(system_info)
    
    # Check critical dependencies
    console.print("\n[bold]Critical Dependencies:[/]")
    critical_deps = [
        "transformers", "datasets", "accelerate", "peft", 
        "bitsandbytes", "sentencepiece", "tiktoken"
    ]
    
    deps_table = Table(show_header=False)
    deps_table.add_column("Package")
    deps_table.add_column("Status")
    deps_table.add_column("Version")
    
    for package in critical_deps:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "Unknown")
            deps_table.add_row(package, "[green]✓ Installed[/]", version)
        except ImportError:
            deps_table.add_row(package, "[red]✗ Missing[/]", "N/A")
    
    console.print(deps_table)
    
    # Check model-specific dependencies
    console.print("\n[bold]Model-Specific Dependencies:[/]")
    
    model_table = Table(title="Model Dependencies")
    model_table.add_column("Model")
    model_table.add_column("Dependencies")
    model_table.add_column("Status")
    
    for model, packages in DependencyManager.MODEL_DEPENDENCIES.items():
        pkg_status = []
        all_installed = True
        
        for package in packages:
            base_pkg = package.split(">=")[0].split("==")[0].strip()
            try:
                importlib.import_module(base_pkg)
                pkg_status.append(f"[green]✓ {base_pkg}[/]")
            except ImportError:
                pkg_status.append(f"[red]✗ {base_pkg}[/]")
                all_installed = False
        
        status = "[green]OK[/]" if all_installed else "[yellow]Missing Dependencies[/]"
        model_table.add_row(model, ", ".join(pkg_status), status)
    
    console.print(model_table)
    
    # Check environment variables
    console.print("\n[bold]Environment Variables:[/]")
    env_vars = Table(show_header=False)
    env_vars.add_column("Variable")
    env_vars.add_column("Status")
    
    # List of important env vars to check
    important_vars = [
        "HF_TOKEN", "HUGGINGFACE_TOKEN", "OPENAI_API_KEY", "GOOGLE_API_KEY"
    ]
    
    for var in important_vars:
        if var in os.environ:
            # Obfuscate the value for security
            value = os.environ[var]
            if value:
                masked = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
                env_vars.add_row(var, f"[green]✓ Set[/] ({masked})")
            else:
                env_vars.add_row(var, "[yellow]⚠ Empty[/]")
        else:
            env_vars.add_row(var, "[red]✗ Not Set[/]")
    
    console.print(env_vars)
    
    # Check database setup
    console.print("\n[bold]Database Setup:[/]")
    db_path = Path.home() / "dravik" / "data" / "lancedb"
    if db_path.exists():
        num_files = len(list(db_path.glob("*")))
        console.print(f"[green]✓ Database directory exists[/] ({num_files} files)")
    else:
        console.print(f"[yellow]⚠ Database directory not found[/] ({db_path})")
    
    # Generate recommendations
    console.print("\n[bold]Recommendations:[/]")
    recommendations = []
    
    # Check for missing critical dependencies
    for package in critical_deps:
        try:
            importlib.import_module(package)
        except ImportError:
            recommendations.append(f"Install missing dependency: [cyan]pip install {package}[/]")
    
    # Check for HF token
    if not any(var in os.environ and os.environ[var] for var in ["HF_TOKEN", "HUGGINGFACE_TOKEN"]):
        recommendations.append("Set up HuggingFace token with [cyan]export HF_TOKEN=your_token[/]")
    
    # Check for database directory
    if not db_path.exists():
        recommendations.append(f"Create database directory: [cyan]mkdir -p {db_path}[/]")
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            console.print(f"{i+1}. {rec}")
    else:
        console.print("[green]✓ Your system appears to be properly configured![/]")
    
    # Summary
    console.print(Panel(
        "[bold]System Check Complete[/]\n\n"
        "If you encountered any issues, refer to the documentation\n"
        "or run the dependency installer with:\n"
        "[cyan]python -m cli.dependency_tool install <model_name>[/]",
        border_style="green"
    ))

if __name__ == "__main__":
    check_system_setup()
