"""Database storage for benchmark results"""
import uuid
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime
from rich.console import Console

class DatabaseStorage:
    """Handle database storage for benchmark results"""
    
    def __init__(self, db, console: Console):
        """Initialize database storage"""
        self.db = db
        self.console = console
    
    def save_benchmark_results(self, results: Dict[str, Any], results_file: str) -> bool:
        """Save benchmark results to LanceDB"""
        try:
            # Create a unique benchmark ID
            benchmark_id = str(uuid.uuid4())
            
            # Extract important metadata for the database
            timestamp = datetime.now().isoformat()
            model_tested = results.get("model_tested", "Unknown")
            
            # Get API models used
            models_used = results.get("models_used", {})
            openai_model = models_used.get("openai", "Unknown")
            gemini_model = models_used.get("gemini", "Unknown")
            
            # Get bypass rates
            scores = results.get("scores", {})
            openai_bypass_rate = scores.get("openai_bypass_rate", 0)
            gemini_bypass_rate = scores.get("gemini_bypass_rate", 0)
            
            # Format data for LanceDB
            benchmark_data = {
                "benchmark_id": benchmark_id,
                "timestamp": timestamp,
                "model_tested": model_tested,
                "openai_model": openai_model,
                "gemini_model": gemini_model,
                "openai_bypass_rate": float(openai_bypass_rate),
                "gemini_bypass_rate": float(gemini_bypass_rate),
                "total_prompts": results.get("total_prompts", 0),
                "prompts_generated": results.get("metrics", {}).get("test_prompts_generated", 0),
                "results_file": results_file,
                "successful_bypasses": sum(
                    1 for result in results.get("detailed_results", [])
                    if any(r.get("success", False) for r in result.get("apis", {}).values())
                )
            }
            
            # Fix the table existence check
            try:
                # Check if table exists by trying to access it
                benchmarks_table = self.db.open_table("benchmarks")
                # If we reach here, the table exists, so add to it
                benchmarks_table.add([benchmark_data])
                self.console.print(f"[green]Added benchmark result to database[/]")
            except Exception as table_error:
                # Table doesn't exist or other error, create it
                self.console.print(f"[yellow]Creating new benchmarks table: {str(table_error)}[/]")
                self.db.create_table("benchmarks", data=[benchmark_data])
                self.console.print(f"[green]Created benchmarks table and stored result[/]")
            
            return True
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save to database: {str(e)}[/]")
            return False
    
    def get_all_benchmarks(self) -> Optional[pd.DataFrame]:
        """Get all benchmark results from database"""
        try:
            # Check if table exists
            benchmarks_table = self.db.open_table("benchmarks")
            return benchmarks_table.search().to_pandas()
        except Exception:
            return None
    
    def get_benchmark_by_id(self, benchmark_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific benchmark by ID"""
        try:
            benchmarks_table = self.db.open_table("benchmarks")
            results = benchmarks_table.search().filter(f"benchmark_id = '{benchmark_id}'").to_pandas()
            
            if len(results) == 0:
                return None
                
            return results.iloc[0].to_dict()
        except Exception:
            return None
