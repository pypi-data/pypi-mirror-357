"""Callback handlers for benchmark progress tracking"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import json
from datetime import datetime

class BenchmarkCallbacks:
    """Callback handlers for benchmark progress tracking"""
    
    def __init__(self, output_dir: str):
        """Initialize callbacks with output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.active_file = self.output_dir / "benchmark_active.json"
        self.start_time = datetime.now()
        
        # Initialize progress tracking
        self.progress = {
            "status": "in_progress",
            "created_at": self.start_time.isoformat(),
            "current_step": 0,
            "total_steps": 0,
            "examples_completed": 0,
            "total_examples": 0
        }
        
        # Initial save
        self._save_progress()
    
    def on_benchmark_begin(self, total_examples: int, total_steps: int = 0):
        """Called when benchmark begins"""
        self.progress.update({
            "total_examples": total_examples,
            "total_steps": total_steps,
            "start_time": self.start_time.isoformat()
        })
        self._save_progress()
    
    def on_example_begin(self, example_idx: int, example: Dict[str, Any]):
        """Called when processing a new example"""
        self.progress.update({
            "current_example": example_idx,
            "current_example_data": {
                "id": example.get("id", str(example_idx)),
                "type": example.get("type", "unknown")
            }
        })
        self._save_progress()
    
    def on_example_complete(self, example_idx: int, result: Dict[str, Any]):
        """Called when an example is processed"""
        self.progress.update({
            "examples_completed": example_idx + 1,
            "last_result": {
                "id": result.get("id", str(example_idx)),
                "success": result.get("success", False),
                "score": result.get("score", 0)
            }
        })
        
        # Calculate elapsed time
        elapsed = datetime.now() - self.start_time
        self.progress["elapsed_time"] = str(elapsed).split('.')[0]  # HH:MM:SS
        
        # Calculate estimated time remaining
        if example_idx > 0 and self.progress["total_examples"] > 0:
            completed = example_idx + 1
            total = self.progress["total_examples"]
            time_per_example = elapsed.total_seconds() / completed
            remaining_seconds = time_per_example * (total - completed)
            
            import time
            self.progress["estimated_remaining"] = str(datetime.fromtimestamp(remaining_seconds) - datetime.fromtimestamp(0)).split('.')[0]
        
        self._save_progress()
    
    def on_benchmark_complete(self, results: Dict[str, Any]):
        """Called when benchmark is complete"""
        # Remove active file and create completed info file
        try:
            if self.active_file.exists():
                self.active_file.unlink()
                
            # Save final results
            with open(self.output_dir / "benchmark_results.json", 'w') as f:
                json.dump({
                    "status": "completed",
                    "created_at": self.start_time.isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "results": results
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving benchmark results: {e}")
    
    def on_benchmark_error(self, error: str, traceback_text: Optional[str] = None):
        """Called when benchmark fails with an error"""
        try:
            # Update progress with error
            self.progress.update({
                "status": "failed",
                "error": error,
                "error_time": datetime.now().isoformat()
            })
            
            if traceback_text:
                self.progress["traceback"] = traceback_text
                
            self._save_progress()
            
            # Save detailed error info
            error_file = self.output_dir / "benchmark_error.json"
            with open(error_file, 'w') as f:
                json.dump({
                    "status": "failed",
                    "created_at": self.start_time.isoformat(),
                    "failed_at": datetime.now().isoformat(),
                    "error": error,
                    "traceback": traceback_text
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving benchmark error: {e}")
    
    def _save_progress(self):
        """Save current progress to active file"""
        try:
            with open(self.active_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"Error saving benchmark progress: {e}")
