from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Dict, Any, List

class DisplayManager:
    def __init__(self, console: Console):
        self.console = console

    def show_banner(self):
        """Display welcome banner"""
        banner = """
╔═══════════════════════════════════════════╗
║                 DRAVIK CLI                 ║
║       Advanced LLM Training Pipeline      ║
║                                           ║
║      Type 'exit' at any time to quit     ║
╚═══════════════════════════════════════════╝
        """
        self.console.print(Panel(banner, border_style="blue"))

    def show_error(self, message: str):
        """Display error message"""
        self.console.print(f"[bold red]Error: {message}[/]")

    def show_success(self, message: str):
        """Display success message"""
        self.console.print(f"[bold green]✓[/] {message}")

    def show_info(self, message: str):
        """Display info message"""
        self.console.print(f"[blue]{message}[/]")

    def show_warning(self, message: str):
        """Display warning message"""
        self.console.print(f"[yellow]Warning: {message}[/]")

    def show_config(self, config: Dict[str, Any]):
        """Display configuration"""
        self.console.print("\n[bold blue]Current Configuration:[/]")
        for key, value in config.items():
            self.console.print(f"{key}: {value}")

    def show_dataset_summary(self, name: str, data: Dict[str, Any]):
        """Display dataset summary"""
        self.console.print("\n[bold blue]Dataset Summary:[/]")
        self.console.print(f"Name: {name}")
        if "meta" in data:
            self.console.print("\n[bold blue]Metadata:[/]")
            for key, value in data["meta"].items():
                self.console.print(f"{key}: {value}")
        self.console.print(f"\nTotal records: {len(data.get('data', []))}")

    def show_benchmark_results(self, results: Dict[str, Any]):
        """Display benchmark results in a table"""
        table = Table(title="Benchmark Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", style="green")
        
        for metric, score in results["metrics"].items():
            table.add_row(metric, f"{score:.3f}")
        
        self.console.print(table)

    def show_table(self, title: str, headers: List[str], rows: List[List[str]]):
        """Display data in table format"""
        table = Table(title=title)
        for header in headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*row)
        self.console.print(table)

    # Add more display methods as needed...
