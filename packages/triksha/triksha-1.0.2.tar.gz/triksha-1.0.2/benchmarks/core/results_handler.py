"""Results processing and reporting utilities"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table

class ResultsHandler:
    """Manage benchmark results and reporting"""
    
    def __init__(self, verbose: bool = False, db=None):
        self.verbose = verbose
        self.console = Console()
        self.db = db
    
    def save_results(self, results: Dict[str, Any], db=None) -> bool:
        """Save benchmark results to the database
        
        Args:
            results: Benchmark results to save
            db: Optional database instance to use (if not provided during initialization)
            
        Returns:
            bool: Success status
        """
        # Use provided database or instance variable
        database = db or self.db
        
        if not database:
            if self.verbose:
                self.console.print("[yellow]Warning: No database instance provided. Results not saved.[/]")
            return False
        
        try:
            # Generate a benchmark ID if not present
            if 'benchmark_id' not in results:
                results['benchmark_id'] = str(datetime.now().strftime("%Y%m%d%H%M%S"))
            
            # Add timestamp if not present
            if 'timestamp' not in results:
                results['timestamp'] = datetime.now().isoformat()
            
            # Save to database
            success = database.save_benchmark_result(results)
            
            if success and self.verbose:
                self.console.print(f"[green]Results saved to database with ID: {results.get('benchmark_id')}[/]")
            
            return success
            
        except Exception as e:
            if self.verbose:
                self.console.print(f"[red]Error saving results: {str(e)}[/]")
                import traceback
                traceback.print_exc()
            return False
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """Display benchmark results in a formatted table"""
        # Create table
        table = Table(title="API Bypass Test Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", style="green")
        
        # Add scores if available
        if "scores" in results:
            for metric, value in results["scores"].items():
                table.add_row(
                    metric.replace("_", " ").title(),
                    f"{value:.2f}%"
                )
        
        # Add general metrics
        table.add_row("Total Prompts", str(results.get("total_prompts", 0)))
        table.add_row(
            "Model Used",
            results.get("model", "Unknown")
        )
        
        # Display table
        self.console.print(table)
        
        # Show successful bypass examples if verbose
        if self.verbose and results.get("detailed_results"):
            successful_tests = [
                r for r in results["detailed_results"]
                if any(api_res.get("success", False) for api_res in r.get("apis", {}).values())
            ]
            
            if successful_tests:
                self.console.print("\n[bold blue]Successful Bypass Examples:[/]")
                for result in successful_tests[:3]:  # Show top 3 examples
                    self.console.print(f"\n[bold]Prompt:[/] {result['prompt']}")
                    for api, response in result["apis"].items():
                        if response.get("success", False):
                            self.console.print(f"[green]{api.upper()} Response:[/] {response.get('response', '')[:100]}...")
