"""
Utility to fix benchmark result locations and ensure they are properly saved/retrieved.
"""
import os
import shutil
import json
from pathlib import Path
from glob import glob
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def find_benchmark_files():
    """Find all benchmark result files across possible locations"""
    possible_locations = [
        Path("benchmark_results"),
        Path.home() / "benchmark_results",
        Path.home() / "revert" / "dravik" / "benchmark_results",
        Path("/home/ubuntu/revert/dravik/benchmark_results"),
        Path(os.getcwd()) / "benchmark_results"
    ]
    
    all_files = []
    for location in possible_locations:
        if location.exists():
            console.print(f"[dim]Checking {location}...[/]")
            json_files = list(location.glob("*.json"))
            all_files.extend(json_files)
            console.print(f"[dim]Found {len(json_files)} files[/]")
    
    return all_files

def consolidate_results():
    """Move all benchmark files to the canonical location"""
    target_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")
    target_dir.mkdir(exist_ok=True, parents=True)
    
    files = find_benchmark_files()
    if not files:
        console.print("[yellow]No benchmark files found in any location.[/]")
        return
    
    console.print(f"[green]Found {len(files)} benchmark files across all locations.[/]")
    
    # Create a table of files
    table = Table(title="Benchmark Files Found")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Timestamp", style="green")
    table.add_column("Location", style="yellow")
    table.add_column("Size", style="magenta")
    table.add_column("Status", style="blue")
    
    moved_count = 0
    error_count = 0
    
    for i, file_path in enumerate(sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)):
        try:
            # Load the file to extract timestamp
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    timestamp = data.get('timestamp', 'Unknown')
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        formatted_timestamp = timestamp
                except:
                    formatted_timestamp = "Invalid JSON"
            
            size = file_path.stat().st_size / 1024  # KB
            
            # If file is not in target directory, copy it
            if file_path.parent.absolute() != target_dir.absolute():
                target_file = target_dir / file_path.name
                if not target_file.exists():
                    shutil.copy2(file_path, target_dir)
                    status = "✓ Moved"
                    moved_count += 1
                else:
                    # Check if they're identical
                    if file_path.stat().st_size == target_file.stat().st_size:
                        status = "✓ Already exists (same size)"
                    else:
                        # Keep both with different names
                        new_name = f"{file_path.stem}_copy{file_path.suffix}"
                        shutil.copy2(file_path, target_dir / new_name)
                        status = "✓ Copied with new name"
                        moved_count += 1
            else:
                status = "✓ Already in correct location"
                
            table.add_row(
                str(i+1),
                formatted_timestamp,
                str(file_path.parent),
                f"{size:.1f} KB",
                status
            )
                
        except Exception as e:
            table.add_row(
                str(i+1),
                "Error",
                str(file_path.parent),
                "Unknown",
                f"❌ Error: {str(e)}"
            )
            error_count += 1
    
    console.print(table)
    console.print(f"[green]Successfully moved {moved_count} files to {target_dir}[/]")
    if error_count > 0:
        console.print(f"[yellow]Encountered errors with {error_count} files[/]")
    
    # Update permissions to ensure readability
    for file in target_dir.glob("*.json"):
        try:
            file.chmod(0o644)  # rw-r--r--
        except:
            pass

def ensure_directories_exist():
    """Create all necessary directories with proper permissions"""
    directories = [
        Path("/home/ubuntu/revert/dravik/benchmark_results"),
        Path("benchmark_results")
    ]
    
    for directory in directories:
        try:
            directory.mkdir(exist_ok=True, parents=True)
            # Make directory readable and writable
            os.chmod(directory, 0o755)  # rwxr-xr-x
            console.print(f"[green]Ensured directory exists: {directory.absolute()}[/]")
        except Exception as e:
            console.print(f"[red]Error creating directory {directory}: {str(e)}[/]")
            
    # Create a test file to ensure write permissions work
    try:
        test_file = Path("/home/ubuntu/revert/dravik/benchmark_results/test_write.txt")
        with open(test_file, 'w') as f:
            f.write(f"Write test at {datetime.now().isoformat()}")
        console.print(f"[green]Successfully wrote test file to verify permissions[/]")
        test_file.unlink()  # Delete the test file
    except Exception as e:
        console.print(f"[red]Error writing test file: {str(e)}[/]")

if __name__ == "__main__":
    console.print(Panel.fit("[bold blue]Benchmark Results Fixer[/]", subtitle="Fix benchmark result locations"))
    
    ensure_directories_exist()
    consolidate_results()
    
    console.print("\n[bold green]What to do next:[/]")
    console.print("1. Run a new benchmark test")
    console.print("2. Check results with 'View results' option")
    console.print("3. If issues persist, check actual permissions with 'ls -la /home/ubuntu/revert/dravik/benchmark_results'")
