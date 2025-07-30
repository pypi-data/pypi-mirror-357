"""Interactive benchmarking command implementation

This module provides CLI commands for creating and running interactive benchmarks.
"""
import os
import asyncio
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
import inquirer

from .command import BenchmarkCommands
from ...utils.cli import Command, argument, option
from ...utils.logger import get_logger
from benchmarks.interactive.session_manager import InteractiveBenchmarkSession
from benchmarks.interactive.benchmark_executor import AdaptiveBenchmarkExecutor
from benchmarks.interactive.interactive_ui import InteractiveBenchmarkUI
from benchmarks.interactive.metrics_manager import CustomMetricsManager

logger = get_logger(__name__)

class InteractiveBenchmarkCommands(Command):
    """Commands for interactive benchmarking"""
    
    name = "interactive"
    help = "Run interactive and adaptive benchmarks"
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.ui = InteractiveBenchmarkUI(console=self.console)
        self.metrics_manager = CustomMetricsManager()
    
    @argument("session_id", type=str, required=False, help="Session ID to resume")
    @option("--new", is_flag=True, help="Start a new session")
    @option("--config", type=str, help="Path to session configuration JSON")
    async def run(self, session_id: Optional[str] = None, new: bool = False, 
                  config: Optional[str] = None) -> None:
        """Run an interactive benchmark session"""
        session = None
        
        if new or not session_id:
            # Create new session
            session = self.ui.create_new_session()
            
            # Load config from file or configure interactively
            if config:
                try:
                    with open(config, 'r') as f:
                        config_data = json.load(f)
                    
                    session.set_config(config_data)
                    self.console.print(f"Loaded configuration from [cyan]{config}[/]")
                except Exception as e:
                    self.console.print(f"[red]Error loading config:[/] {str(e)}")
                    # Fall back to interactive configuration
                    if not self.ui.configure_session(session):
                        self.console.print("[red]Configuration canceled.[/]")
                        return
            else:
                # Configure interactively
                if not self.ui.configure_session(session):
                    self.console.print("[red]Configuration canceled.[/]")
                    return
        else:
            # Resume existing session
            try:
                session = InteractiveBenchmarkSession.load_session(session_id)
                self.console.print(f"Resumed session [cyan]{session_id}[/]")
            except Exception as e:
                self.console.print(f"[red]Error loading session:[/] {str(e)}")
                return
        
        # Display status
        self.ui.display_session_status(session)
        
        # Confirm
        if not inquirer.confirm("Start benchmark?", default=True):
            self.console.print("Benchmark canceled.")
            return
        
        # Run benchmark
        try:
            executor = AdaptiveBenchmarkExecutor(session)
            
            # Run in background task with progress
            with Progress() as progress:
                task = progress.add_task("[cyan]Running benchmark...", total=None)
                
                # Run benchmark
                results = await executor.run_benchmark()
                
                progress.update(task, completed=100)
            
            # Display results
            self.ui.display_results(results)
            
            # Save results
            results_dir = os.path.join("benchmark_results", "interactive")
            os.makedirs(results_dir, exist_ok=True)
            results_file = os.path.join(results_dir, f"{session.session_id}.json")
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.console.print(f"Results saved to [cyan]{results_file}[/]")
            
        except KeyboardInterrupt:
            self.console.print("[yellow]Benchmark interrupted.[/]")
        except Exception as e:
            self.console.print(f"[red]Error during benchmark:[/] {str(e)}")
    
    @option("--category", type=str, help="Filter by metric category")
    def list_metrics(self, category: Optional[str] = None) -> None:
        """List available benchmark metrics"""
        if category:
            metrics = self.metrics_manager.list_templates(category)
            self.console.print(f"[bold]Available metrics in category '{category}':[/]")
        else:
            metrics = self.metrics_manager.list_templates()
            self.console.print("[bold]All available metrics:[/]")
        
        for metric in metrics:
            self.console.print(
                f"[cyan]{metric['display_name']}[/] ({metric['name']}) "
                f"- {metric['description']}"
            )
    
    def list_sessions(self) -> None:
        """List existing benchmark sessions"""
        sessions_dir = Path(InteractiveBenchmarkSession.SESSIONS_DIR)
        
        if not sessions_dir.exists():
            self.console.print("[yellow]No sessions found.[/]")
            return
        
        sessions = []
        for file in sessions_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                session_id = data.get('session_id', file.stem)
                config = data.get('config', {})
                state = data.get('state', 'UNKNOWN')
                
                sessions.append({
                    'id': session_id,
                    'name': config.get('benchmark_name', 'Unnamed'),
                    'state': state,
                    'examples': len(data.get('examples', [])),
                    'results': len(data.get('results', [])),
                    'file': file
                })
            except:
                # Skip invalid files
                pass
        
        if not sessions:
            self.console.print("[yellow]No valid sessions found.[/]")
            return
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda s: os.path.getctime(s['file']), reverse=True)
        
        # Display as table
        from rich.table import Table
        
        table = Table(title="Interactive Benchmark Sessions")
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("State", style="green")
        table.add_column("Examples", justify="right")
        table.add_column("Results", justify="right")
        
        for session in sessions:
            table.add_row(
                session['id'],
                session['name'],
                session['state'],
                str(session['examples']),
                str(session['results'])
            )
        
        self.console.print(table)
    
    @argument("session_id", type=str, help="Session ID to delete")
    def delete_session(self, session_id: str) -> None:
        """Delete a benchmark session"""
        try:
            session_file = os.path.join(
                InteractiveBenchmarkSession.SESSIONS_DIR, 
                f"{session_id}.json"
            )
            
            if not os.path.exists(session_file):
                self.console.print(f"[red]Session not found:[/] {session_id}")
                return
            
            # Confirm
            if not inquirer.confirm(f"Delete session {session_id}?", default=False):
                self.console.print("Operation canceled.")
                return
            
            # Delete file
            os.remove(session_file)
            self.console.print(f"[green]Session deleted:[/] {session_id}")
            
        except Exception as e:
            self.console.print(f"[red]Error deleting session:[/] {str(e)}")
    
    @argument("name", type=str, help="Name for the metric suite")
    @option("--category", type=str, multiple=True, help="Categories to include (multiple allowed)")
    @option("--output", type=str, help="Output file path for the suite")
    def create_metric_suite(self, name: str, category: Optional[List[str]] = None,
                           output: Optional[str] = None) -> None:
        """Create a metric suite from existing metrics"""
        metrics = []
        
        if category:
            # Get metrics from specified categories
            for cat in category:
                cat_metrics = self.metrics_manager.list_templates(cat)
                metrics.extend(cat_metrics)
        else:
            # Interactive selection
            all_categories = self.metrics_manager.list_template_categories()
            
            cat_questions = [
                inquirer.Checkbox(
                    'categories',
                    message="Select metric categories to include",
                    choices=[(cat.capitalize(), cat) for cat in all_categories]
                )
            ]
            
            cat_answers = inquirer.prompt(cat_questions)
            if not cat_answers or not cat_answers['categories']:
                self.console.print("[yellow]No categories selected.[/]")
                return
            
            # Get all metrics from selected categories
            for cat in cat_answers['categories']:
                cat_metrics = self.metrics_manager.list_templates(cat)
                
                # Allow selecting specific metrics from category
                metric_choices = [(m['display_name'], m) for m in cat_metrics]
                
                metric_questions = [
                    inquirer.Checkbox(
                        'selected_metrics',
                        message=f"Select metrics from {cat}",
                        choices=metric_choices
                    )
                ]
                
                metric_answers = inquirer.prompt(metric_questions)
                if metric_answers and metric_answers['selected_metrics']:
                    metrics.extend(metric_answers['selected_metrics'])
        
        if not metrics:
            self.console.print("[red]No metrics selected.[/]")
            return
        
        # Ask for description
        desc_questions = [
            inquirer.Text(
                'description',
                message="Suite description",
                default=f"Metric suite: {name}"
            )
        ]
        
        desc_answers = inquirer.prompt(desc_questions)
        description = desc_answers['description'] if desc_answers else f"Metric suite: {name}"
        
        # Create suite
        suite = self.metrics_manager.create_metric_suite(name, metrics, description)
        
        self.console.print(f"[green]Created metric suite:[/] {name} with {len(metrics)} metrics")
        
        # Save to custom output if specified
        if output:
            try:
                with open(output, 'w') as f:
                    json.dump(suite, f, indent=2)
                
                self.console.print(f"Suite saved to [cyan]{output}[/]")
            except Exception as e:
                self.console.print(f"[red]Error saving suite:[/] {str(e)}")


# Register with BenchmarkCommands
BenchmarkCommands.register_subcommand(InteractiveBenchmarkCommands())

# Add to main CLI if this is imported directly
if __name__ == "__main__":
    from cli.main import cli
    cli.add_command(InteractiveBenchmarkCommands().run)
