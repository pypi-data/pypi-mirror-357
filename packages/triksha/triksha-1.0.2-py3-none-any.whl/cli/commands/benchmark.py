"""
Main benchmark module that imports and uses the modular benchmark structure.
This file serves as a wrapper around the new modular benchmark system.
"""
from typing import Dict, Any, Optional
from rich.console import Console
from .benchmark.command import BenchmarkCommands as ModularBenchmarkCommands

class BenchmarkCommands:
    """
    Main benchmark commands interface - wrapper around modular architecture.
    
    This class maintains backward compatibility with existing code while
    delegating most functionality to the new modular components.
    """
    
    def __init__(self, db, config):
        """Initialize benchmark commands with database and config"""
        # Create an instance of the modular benchmark commands
        self.modular_commands = ModularBenchmarkCommands(db=db, config=config)
        self.console = Console()
        self.db = db
        self.config = config
        
        # For debugging and transitional phase
        self.console.print("[dim]Using modular benchmark architecture[/]", highlight=False)
    
    def run_benchmarks(self):
        """Handle benchmark workflow with backup support"""
        return self.modular_commands.run_benchmarks()
    
    def _should_resume(self) -> bool:
        """Ask user if they want to resume a previous session"""
        # Delegate to modular UI
        return self.modular_commands.ui.should_resume_session()
    
    def _select_session(self, sessions):
        """Have user select a session to resume"""
        # Delegate to modular UI
        return self.modular_commands.ui.select_session(sessions)
    
    def _get_benchmark_type(self):
        """Get benchmark type selection from user"""
        # Delegate to modular UI
        return self.modular_commands.ui.get_benchmark_type()
    
    async def _get_available_api_models(self):
        """Get available models for benchmarking"""
        # Delegate to modular UI
        models_with_details = await self.modular_commands.ui._get_available_api_models()
        
        # Convert to the expected format for backward compatibility
        return {
            "openai": [m["value"] for m in models_with_details["openai"]],
            "gemini": [m["value"] for m in models_with_details["gemini"]]
        }
    
    def _run_api_benchmark(self, resume_session=None):
        """Run API-based bypass testing"""
        # Forward to modular commands
        self.modular_commands._run_api_benchmark(resume_session)
    
    def _run_performance_benchmark(self, benchmark_type):
        """Run performance benchmarks"""
        # Forward to modular commands
        self.modular_commands._run_performance_benchmark(benchmark_type)
    
    def _save_to_lancedb(self, results: Dict[str, Any], results_file: str) -> bool:
        """Save benchmark results to LanceDB"""
        # Delegate to modular storage
        return self.modular_commands.results_viewer.storage.save_benchmark_results(
            results, results_file
        )
    
    def _display_api_results(self, results: Dict[str, Any]):
        """Display API benchmark results and store them in LanceDB"""
        # Delegate to modular results viewer
        return self.modular_commands.results_viewer.display_api_results(results)
    
    def list_benchmark_results(self):
        """List all benchmark results from the database"""
        # Delegate to modular results viewer
        return self.modular_commands.results_viewer.list_all_results()
    
    def view_benchmark_results(self):
        """View detailed benchmark results"""
        # Delegate to modular results viewer
        return self.modular_commands.results_viewer.view_detailed_results()
    
    def export_benchmark_data(self):
        """Export benchmark data for reports"""
        # Delegate to modular results viewer
        return self.modular_commands.results_viewer.export_results()
    
    def show_benchmark_statistics(self):
        """Show statistics across all benchmarks"""
        # Delegate to modular results viewer
        return self.modular_commands.results_viewer.show_statistics()
    
    # Compatibility method for displaying benchmark summary
    def _display_benchmark_summary(self, benchmark_data):
        """Display summary of benchmark results"""
        # Delegate to modular results viewer
        return self.modular_commands.results_viewer._display_benchmark_summary(benchmark_data)
    
    # Compatibility method for showing bypass examples
    def _show_bypass_examples(self, benchmark_data, limit=3):
        """Show examples of successful bypasses"""
        # Delegate to modular results viewer
        return self.modular_commands.results_viewer._show_bypass_examples(
            benchmark_data, limit
        )
    
    # Compatibility method for displaying full benchmark
    def _display_full_benchmark(self, benchmark_data, results_file):
        """Display full benchmark details"""
        # Delegate to modular results viewer
        return self.modular_commands.results_viewer._display_full_benchmark(
            benchmark_data, results_file
        )
