"""
Utility script to find recent benchmark results that might not be showing up in the listing.
This helps diagnose issues with benchmark results storage and retrieval.
"""

import os
import json
import glob
import sys
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def find_all_benchmark_files(results_dir: str = None) -> list:
    """Find all benchmark result files in the system regardless of location"""
    if results_dir is None:
        # Check standard locations
        possible_dirs = [
            "benchmark_results",
            os.path.join(os.getcwd(), "benchmark_results"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmark_results"),
            "/home/ubuntu/revert/dravik/benchmark_results"
        ]
        
        results_dir = None
        for directory in possible_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                results_dir = directory
                break
    
        if results_dir is None:
            console.print("[red]Could not locate the benchmark_results directory![/]")
            console.print("[yellow]Please specify the path to the benchmark_results directory.[/]")
            return []
    
    console.print(f"[blue]Searching for benchmark files in: [bold]{results_dir}[/][/]")
    
    # Find all JSON files
    json_pattern = os.path.join(results_dir, "*.json")
    benchmark_files = glob.glob(json_pattern)
    
    return benchmark_files

def list_all_results(benchmark_files: list) -> None:
    """List all benchmark results found"""
    # Sort by modification time, newest first
    files_with_mtime = [(f, os.path.getmtime(f)) for f in benchmark_files]
    files_with_mtime.sort(key=lambda x: x[1], reverse=True)
    
    table = Table(title="All Benchmark Results Found")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Timestamp", style="green")
    table.add_column("File Modified", style="green")
    table.add_column("Model Tested", style="yellow")
    table.add_column("Total Prompts", style="magenta")
    table.add_column("Success Rate", style="blue")
    table.add_column("Filename", style="dim")
    
    for i, (file_path, mtime) in enumerate(files_with_mtime):
        try:
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    
                    # Format file modification time
                    mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Extract timestamp from data
                    timestamp = data.get('timestamp', 'Unknown')
                    formatted_timestamp = timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                    
                    # Extract other information
                    model_tested = data.get('model_tested', 'Unknown')
                    total_prompts = data.get('total_prompts', 0)
                    
                    # Calculate success rate
                    bypass_success = data.get('bypass_success', {})
                    providers = ['openai', 'gemini', 'custom']
                    success_values = [bypass_success.get(provider, 0) for provider in providers if provider in bypass_success]
                    avg_success = sum(success_values) / len(success_values) if success_values else 0
                    success_rate = f"{avg_success / total_prompts * 100:.1f}%" if total_prompts > 0 else "N/A"
                    
                    # Get filename for display
                    filename = os.path.basename(file_path)
                    
                    table.add_row(
                        str(i+1),
                        formatted_timestamp,
                        mod_time,
                        model_tested,
                        str(total_prompts),
                        success_rate,
                        filename
                    )
                except json.JSONDecodeError:
                    table.add_row(
                        str(i+1),
                        "Error",
                        mod_time,
                        "Invalid JSON",
                        "N/A",
                        "N/A",
                        os.path.basename(file_path)
                    )
        except Exception as e:
            table.add_row(
                str(i+1),
                "Error",
                datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                f"Error: {str(e)}",
                "N/A",
                "N/A",
                os.path.basename(file_path)
            )
    
    console.print(table)

def check_results_directory():
    """Check if benchmark results directory exists and has proper permissions"""
    possible_dirs = [
        "benchmark_results",
        os.path.join(os.getcwd(), "benchmark_results"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmark_results"),
        "/home/ubuntu/revert/dravik/benchmark_results"
    ]
    
    dir_table = Table(title="Benchmark Results Directories")
    dir_table.add_column("Path", style="cyan")
    dir_table.add_column("Exists", style="green")
    dir_table.add_column("Readable", style="yellow")
    dir_table.add_column("Writable", style="magenta")
    dir_table.add_column("File Count", style="blue")
    
    for directory in possible_dirs:
        exists = os.path.exists(directory)
        readable = False
        writable = False
        file_count = 0
        
        if exists:
            readable = os.access(directory, os.R_OK)
            writable = os.access(directory, os.W_OK)
            try:
                file_count = len([f for f in os.listdir(directory) if f.endswith('.json')])
            except:
                file_count = "Error counting"
        
        dir_table.add_row(
            directory,
            "✅" if exists else "❌",
            "✅" if readable else "❌",
            "✅" if writable else "❌",
            str(file_count)
        )
    
    console.print(dir_table)

def find_recent_benchmarks(days=1):
    """Find benchmarks from the last N days"""
    files = find_all_benchmark_files()
    
    if not files:
        console.print("[yellow]No benchmark files found.[/]")
        return
    
    # Get current time
    now = datetime.now().timestamp()
    seconds_in_day = 86400
    cutoff = now - (days * seconds_in_day)
    
    # Filter files by modification time
    recent_files = [f for f in files if os.path.getmtime(f) > cutoff]
    
    if recent_files:
        console.print(f"[green]Found {len(recent_files)} benchmark files from the last {days} day(s).[/]")
        list_all_results(recent_files)
    else:
        console.print(f"[yellow]No benchmark files found from the last {days} day(s).[/]")
        # If no recent files, suggest checking for any files
        console.print("[blue]Checking for any benchmark files...[/]")
        list_all_results(files)

def main():
    """Main function to run the script"""
    console.print(Panel.fit("[bold blue]Benchmark Results Finder[/]", 
                           subtitle="Find missing benchmark results"))
    
    console.print("[yellow]Checking benchmark directories...[/]")
    check_results_directory()
    
    console.print("\n[yellow]Looking for recent benchmark results (last 24 hours)...[/]")
    find_recent_benchmarks(days=1)
    
    console.print("\n[bold green]Recommendations:[/]")
    console.print("1. Check that the benchmark_results directory exists and has proper permissions")
    console.print("2. Verify that benchmark runs are correctly saving their results")
    console.print("3. Look in alternative locations if results were saved elsewhere")
    console.print("4. Check if the database is properly configured to track benchmark results")

if __name__ == "__main__":
    main()
