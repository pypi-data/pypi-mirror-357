"""Base benchmark class definitions"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from ..utils.backup_manager import BackupManager

class BaseBenchmark:
    """Base class for all benchmarks"""
    
    def __init__(self, verbose: bool = False, db=None):
        """Initialize base benchmark with common attributes
        
        Args:
            verbose: Whether to output verbose logging
            db: Optional database instance for saving results
        """
        self.verbose = verbose
        self.console = Console()
        self.db = db
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_prompts": 0,
            "metrics": {},
            "detailed_results": []
        }
        self.backup_manager = BackupManager()
    
    def _log(self, message: str, level: str = "info"):
        """Log messages based on verbosity"""
        if not self.verbose:
            return
            
        if level == "info":
            self.console.print(f"[blue]{message}[/]")
        elif level == "success":
            self.console.print(f"[green]{message}[/]")
        elif level == "warning":
            self.console.print(f"[yellow]{message}[/]")
        elif level == "error":
            self.console.print(f"[red]{message}[/]")
        else:
            self.console.print(message)
    
    def save_results(self, db=None) -> bool:
        """Save benchmark results to the database
        
        Args:
            db: Optional database instance (if not provided during initialization)
            
        Returns:
            bool: Success status
        """
        # Use temporary file backup for local development/testing
        self.backup_manager.save_state(self.results, "completed")
        
        # Use provided database or instance variable
        database = db or self.db
        
        if not database:
            self._log("No database instance available. Results only saved locally.", "warning")
            return False
            
        try:
            # Generate a benchmark ID if not present
            if 'benchmark_id' not in self.results:
                self.results['benchmark_id'] = str(datetime.now().strftime("%Y%m%d%H%M%S"))
            
            # Add timestamp if not present
            if 'timestamp' not in self.results:
                self.results['timestamp'] = datetime.now().isoformat()
            
            # Save to database
            success = database.save_benchmark_result(self.results)
            
            if success:
                self._log(f"Results saved to database with ID: {self.results.get('benchmark_id')}", "success")
            else:
                self._log("Could not save results to database", "warning")
                
            return success
            
        except Exception as e:
            self._log(f"Error saving results to database: {str(e)}", "error")
            import traceback
            traceback.print_exc()
            return False
    
    def load_results(self, session_id: str) -> bool:
        """Load benchmark results from a session"""
        loaded_results = self.backup_manager.load_latest_state(session_id)
        if loaded_results:
            self.results = loaded_results
            return True
        return False
