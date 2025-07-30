"""
Utility to diagnose and fix benchmark result storage issues.
This fixes problems with benchmark results not being saved or found.
"""
import os
import sys
import json
import glob
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.logging import RichHandler
from rich.prompt import Confirm

# Set up rich console
console = Console()

# Configure logging
FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
log = logging.getLogger("benchmark_fix")

class BenchmarkStorageFix:
    def __init__(self):
        """Initialize the diagnostic tool"""
        self.potential_dirs = [
            Path("/home/ubuntu/revert/dravik/benchmark_results"),
            Path.home() / "revert" / "dravik" / "benchmark_results",
            Path.cwd() / "benchmark_results",
            Path("benchmark_results"),
            Path.home() / "benchmark_results",
        ]
        
        self.benchmark_files = []
        self.fixed_count = 0
        self.errors = []
        self.target_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")
    
    def run_diagnostics(self):
        """Run diagnostics on benchmark storage"""
        console.print(Panel.fit("[bold blue]Benchmark Results Storage Diagnostics[/]"))
        
        # Test if we can create a temporary file
        self._test_write_permissions()
        
        # Check all directories where benchmark results might be stored
        self._check_directories()
        
        # Search for benchmark files in all locations
        self._find_benchmark_files()
        
        # Check if benchmark results are being saved
        self._check_recent_benchmark_run()
    
    def _test_write_permissions(self):
        """Test if we can create files"""
        console.print("[bold]Testing write permissions...[/]")
        try:
            # Create a test file in /tmp
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tmp.write(b"test")
                console.print(f"[green]✓[/] Can create temp files")
            
            # Try to create a file in the target directory
            self.target_dir.mkdir(exist_ok=True, parents=True)
            test_file = self.target_dir / "write_test.tmp"
            with open(test_file, 'w') as f:
                f.write("Test write: " + datetime.now().isoformat())
            console.print(f"[green]✓[/] Can write to target directory: {self.target_dir}")
            
            # Clean up
            if test_file.exists():
                test_file.unlink()
            
        except Exception as e:
            console.print(f"[bold red]✗[/] Write permission error: {str(e)}")
            self.errors.append(f"Write permission issue: {str(e)}")
    
    def _check_directories(self):
        """Check all potential benchmark directories"""
        console.print("\n[bold]Checking benchmark directories...[/]")
        
        dir_table = Table(title="Benchmark Result Directories")
        dir_table.add_column("Directory", style="cyan")
        dir_table.add_column("Exists", style="green")
        dir_table.add_column("Readable", style="green")
        dir_table.add_column("Writable", style="green")
        dir_table.add_column("JSON Files", style="yellow")
        
        for directory in self.potential_dirs:
            exists = directory.exists()
            readable = False
            writable = False
            file_count = 0
            
            if exists:
                readable = os.access(directory, os.R_OK)
                writable = os.access(directory, os.W_OK)
                try:
                    file_count = len(list(directory.glob('*.json')))
                except Exception:
                    file_count = "Error"
            
            dir_table.add_row(
                str(directory),
                "✓" if exists else "✗",
                "✓" if readable else "✗",
                "✓" if writable else "✗",
                str(file_count)
            )
            
            # Create directory if it doesn't exist
            if not exists and str(directory).startswith(("/home/ubuntu", str(Path.home()))):
                try:
                    directory.mkdir(exist_ok=True, parents=True)
                    console.print(f"[green]Created missing directory: {directory}[/]")
                    self.fixed_count += 1
                except Exception as e:
                    console.print(f"[red]Could not create directory {directory}: {e}[/]")
                    self.errors.append(f"Directory creation issue: {str(e)}")
        
        console.print(dir_table)
    
    def _find_benchmark_files(self):
        """Find benchmark files in all potential locations"""
        console.print("\n[bold]Searching for benchmark files...[/]")
        
        for directory in self.potential_dirs:
            if directory.exists():
                try:
                    # Find all JSON files
                    json_files = list(directory.glob('*.json'))
                    self.benchmark_files.extend(json_files)
                    
                    if json_files:
                        console.print(f"[green]Found {len(json_files)} JSON files in {directory}[/]")
                        
                        # Check most recent file
                        newest_file = max(json_files, key=lambda p: p.stat().st_mtime)
                        mod_time = datetime.fromtimestamp(newest_file.stat().st_mtime)
                        console.print(f"  Most recent file: {newest_file.name} ({mod_time})")
                        
                        # Check if file is a valid benchmark result
                        try:
                            with open(newest_file, 'r') as f:
                                data = json.load(f)
                                if 'detailed_results' in data:
                                    console.print(f"  [green]✓[/] Valid benchmark file with {len(data.get('detailed_results', []))} test results")
                                else:
                                    console.print(f"  [yellow]⚠[/] File doesn't appear to be a benchmark result (no detailed_results key)")
                        except Exception as e:
                            console.print(f"  [red]✗[/] Error reading file: {e}")
                except Exception as e:
                    console.print(f"[red]Error accessing {directory}: {e}[/]")
        
        if not self.benchmark_files:
            console.print("[yellow]No benchmark files found in any location[/]")
    
    def _check_recent_benchmark_run(self):
        """Check if we can find evidence of the most recent benchmark run"""
        console.print("\n[bold]Checking for recent benchmark runs...[/]")
        
        # Look for temporary files that might indicate a recent run
        temp_directories = [tempfile.gettempdir(), "/tmp", "/var/tmp"]
        found_temp_files = []
        
        for directory in temp_directories:
            temp_dir = Path(directory)
            if temp_dir.exists():
                # Look for any files that might be related to benchmarks
                for pattern in ["benchmark*", "*result*", "dravik*"]:
                    found_temp_files.extend(list(temp_dir.glob(pattern)))
        
        if found_temp_files:
            console.print(f"[green]Found {len(found_temp_files)} potential temporary benchmark files[/]")
            
            # List the 5 most recent files
            recent_files = sorted(found_temp_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
            for file in recent_files:
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                console.print(f"  {file.name} ({mod_time})")
        else:
            console.print("[yellow]No temporary benchmark files found[/]")
        
        # Check for logs that might contain benchmark information
        log_dirs = ["/var/log", Path.home() / ".local" / "share" / "dravik"]
        found_logs = []
        
        for log_dir in log_dirs:
            if Path(log_dir).exists():
                found_logs.extend(list(Path(log_dir).glob("*.log")))
        
        if found_logs:
            console.print(f"[green]Found {len(found_logs)} potential log files to check[/]")
            
            # Check a few recent logs for benchmark keywords
            recent_logs = sorted(found_logs, key=lambda p: p.stat().st_mtime, reverse=True)[:3]
            for log_file in recent_logs:
                try:
                    with open(log_file, 'r') as f:
                        content = f.read()
                        if "benchmark" in content.lower() or "result" in content.lower():
                            console.print(f"  [yellow]{log_file.name}[/] contains benchmark-related content")
                except:
                    pass
    
    def fix_issues(self):
        """Fix identified issues"""
        console.print("\n[bold blue]Fixing Benchmark Storage Issues[/]")
        
        # 1. Create the target directory with proper permissions
        self._ensure_target_dir()
        
        # 2. Consolidate all benchmark files to the target directory
        self._consolidate_benchmark_files()
        
        # 3. Create a sample benchmark file if none exist
        self._create_sample_benchmark()
        
        # 4. Update the backup manager to use absolute paths
        self._update_backup_manager()
        
        # 5. Check permissions one more time
        self._fix_permissions()
        
        # 6. Summarize fixes
        self._show_summary()
    
    def _ensure_target_dir(self):
        """Ensure the target directory exists with proper permissions"""
        try:
            self.target_dir.mkdir(exist_ok=True, parents=True)
            os.chmod(str(self.target_dir), 0o755)  # rwxr-xr-x
            console.print(f"[green]✓[/] Created target directory with proper permissions: {self.target_dir}")
            self.fixed_count += 1
        except Exception as e:
            console.print(f"[red]✗[/] Could not create target directory: {e}")
            self.errors.append(f"Target directory creation failed: {str(e)}")
    
    def _consolidate_benchmark_files(self):
        """Consolidate all benchmark files to the target directory"""
        if not self.benchmark_files:
            console.print("[yellow]No benchmark files to consolidate[/]")
            return
            
        console.print(f"[bold]Consolidating {len(self.benchmark_files)} benchmark files to {self.target_dir}...[/]")
        
        moved_count = 0
        for file in self.benchmark_files:
            if file.parent != self.target_dir:
                try:
                    target_file = self.target_dir / file.name
                    if not target_file.exists():
                        shutil.copy2(file, target_file)
                        console.print(f"[green]✓[/] Copied {file.name} to target directory")
                        moved_count += 1
                    else:
                        console.print(f"[yellow]⚠[/] File {file.name} already exists in target directory")
                except Exception as e:
                    console.print(f"[red]✗[/] Could not copy {file.name}: {e}")
                    self.errors.append(f"File copy failed: {str(e)}")
        
        console.print(f"[green]Consolidated {moved_count} benchmark files[/]")
        self.fixed_count += moved_count
    
    def _create_sample_benchmark(self):
        """Create a sample benchmark file if none exist"""
        if not list(self.target_dir.glob('*.json')):
            try:
                sample_file = self.target_dir / f"benchmark_results_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                # Create a minimal valid benchmark result file
                sample_data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_prompts": 1,
                    "bypass_success": {
                        "openai": 0,
                        "gemini": 0
                    },
                    "detailed_results": [
                        {
                            "prompt": "This is a sample prompt",
                            "timestamp": datetime.now().isoformat(),
                            "apis": {
                                "openai": {"success": True, "response": "Sample response"},
                                "gemini": {"success": True, "response": "Sample response"}
                            }
                        }
                    ],
                    "scores": {
                        "openai_bypass_rate": 0.0,
                        "gemini_bypass_rate": 0.0
                    },
                    "model_tested": "sample"
                }
                
                with open(sample_file, 'w') as f:
                    json.dump(sample_data, f, indent=2)
                
                console.print(f"[green]✓[/] Created sample benchmark file: {sample_file.name}")
                self.fixed_count += 1
                
            except Exception as e:
                console.print(f"[red]✗[/] Could not create sample benchmark file: {e}")
                self.errors.append(f"Sample file creation failed: {str(e)}")
    
    def _update_backup_manager(self):
        """Create a helper script to update the backup manager"""
        try:
            helper_script = self.target_dir.parent / "utils" / "update_backup_manager.py"
            self.target_dir.parent.joinpath("utils").mkdir(exist_ok=True, parents=True)
            
            with open(helper_script, 'w') as f:
                f.write("""
# Update backup manager to use absolute paths for benchmark results
import os
from pathlib import Path

def update_backup_manager():
    backup_manager_path = Path("/home/ubuntu/revert/dravik/benchmarks/utils/backup_manager.py")
    
    if not backup_manager_path.exists():
        print(f"Backup manager not found at {backup_manager_path}")
        return False
        
    with open(backup_manager_path, 'r') as f:
        content = f.read()
    
    # Check if already using absolute paths
    if 'Path("/home/ubuntu/revert/dravik/benchmark_results")' in content:
        print("Backup manager already using absolute paths!")
        return True
        
    # Replace relative path with absolute
    modified_content = content.replace(
        'benchmark_dir = Path("benchmark_results")',
        'benchmark_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")'
    )
    
    # Add path creation if not present
    if "benchmark_dir.mkdir(exist_ok=True, parents=True)" not in content:
        modified_content = modified_content.replace(
            'benchmark_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")',
            'benchmark_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")\\n        benchmark_dir.mkdir(exist_ok=True, parents=True)'
        )
    
    # Write back the changes
    with open(backup_manager_path, 'w') as f:
        f.write(modified_content)
        
    print(f"Updated {backup_manager_path} to use absolute paths")
    return True

if __name__ == "__main__":
    update_backup_manager()
""")
            
            console.print(f"[green]✓[/] Created helper script to update backup manager: {helper_script}")
            self.fixed_count += 1
            
        except Exception as e:
            console.print(f"[red]✗[/] Could not create helper script: {e}")
            self.errors.append(f"Helper script creation failed: {str(e)}")
    
    def _fix_permissions(self):
        """Fix permissions for benchmark files"""
        try:
            # Set directory permissions
            os.chmod(str(self.target_dir), 0o755)  # rwxr-xr-x
            
            # Set file permissions for all JSON files
            for file in self.target_dir.glob('*.json'):
                os.chmod(str(file), 0o644)  # rw-r--r--
            
            console.print(f"[green]✓[/] Fixed permissions for benchmark directory and files")
            self.fixed_count += 1
            
        except Exception as e:
            console.print(f"[red]✗[/] Could not fix permissions: {e}")
            self.errors.append(f"Permission fix failed: {str(e)}")
    
    def _show_summary(self):
        """Show a summary of fixes"""
        console.print("\n[bold]Summary of Fixes[/]")
        
        if self.fixed_count > 0:
            console.print(f"[green]✓[/] Successfully fixed {self.fixed_count} issues")
        else:
            console.print("[yellow]No issues were fixed[/]")
            
        if self.errors:
            console.print(f"[red]✗[/] Encountered {len(self.errors)} errors:")
            for error in self.errors:
                console.print(f"  - {error}")
        
        console.print("\n[bold]Next Steps:[/]")
        console.print("1. Try running 'Fix benchmark results' from the benchmark menu")
        console.print("2. Run a new benchmark to test if results are saved correctly")
        console.print("3. If issues persist, run this diagnostic tool again with:")
        console.print("   python /home/ubuntu/revert/dravik/utils/benchmark_storage_fix.py")

def main():
    """Main function to run the diagnostics and fix"""
    fixer = BenchmarkStorageFix()
    
    console.print(Panel.fit(
        "[bold blue]Benchmark Results Storage Diagnostics and Fix[/]",
        subtitle="Troubleshoot and fix benchmark result storage issues"
    ))
    
    # Run diagnostics
    fixer.run_diagnostics()
    
    # Ask whether to fix issues
    if Confirm.ask("\nDo you want to fix the identified issues?"):
        fixer.fix_issues()
        
        # Create a symbolic link to the original benchmark directory if needed
        relative_benchmark_dir = Path("benchmark_results")
        if not relative_benchmark_dir.exists() and fixer.target_dir.exists():
            try:
                relative_benchmark_dir.symlink_to(fixer.target_dir)
                console.print(f"[green]✓[/] Created symbolic link from {relative_benchmark_dir} to {fixer.target_dir}")
            except Exception as e:
                console.print(f"[yellow]Could not create symbolic link: {e}[/]")
    
    console.print("\n[bold green]Diagnostics and fixes completed![/]")
    console.print("You should now be able to see benchmark results when using the 'View results' option.")

if __name__ == "__main__":
    main()
