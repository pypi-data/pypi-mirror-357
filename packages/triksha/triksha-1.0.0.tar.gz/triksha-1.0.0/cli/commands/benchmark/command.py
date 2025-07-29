"""
Benchmark Command Module

This module provides the main interface for running benchmarks in the Triksha framework.
It includes support for API benchmarks, Kubernetes benchmarks, and result viewing.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import inquirer
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich import print as rprint
except ImportError:
    # Fallback for missing dependencies
    inquirer = None
    Console = None
    Panel = None
    Table = None
    Live = None
    Progress = None
    SpinnerColumn = None
    TextColumn = None
    Text = None
    rprint = print

# Import benchmark components with error handling
try:
    from .runners import APIBenchmarkRunner, KubernetesBenchmarkManager
except ImportError:
    class APIBenchmarkRunner:
        def __init__(self, *args, **kwargs):
            pass
        def run_benchmark(self, *args, **kwargs):
            return {"error": "APIBenchmarkRunner not available"}
    
    class KubernetesBenchmarkManager:
        def __init__(self, *args, **kwargs):
            pass
        def run_kubernetes_benchmark(self, *args, **kwargs):
            return {"error": "KubernetesBenchmarkManager not available"}

try:
    from .results import ResultsViewer
except ImportError:
    class ResultsViewer:
        def __init__(self, *args, **kwargs):
            pass
        def view_results(self, *args, **kwargs):
            print("ResultsViewer not available")

try:
    from ....benchmarks.utils.backup_manager import BackupManager
except ImportError:
    class BackupManager:
        def __init__(self, *args, **kwargs):
            pass
        def backup_results(self, *args, **kwargs):
            return False

try:
    from ....system_monitor import setup_system_monitor
except ImportError:
    def setup_system_monitor(*args, **kwargs):
        return None

try:
    from ...notification.email_service import EmailNotificationService
except ImportError:
    class EmailNotificationService:
        def __init__(self, *args, **kwargs):
            pass
        def send_notification(self, *args, **kwargs):
            return False

# Retry logic implementation
class RetryableError(Exception):
    """Base class for errors that can be retried."""
    pass

class RateLimitError(RetryableError):
    """Raised when rate limit is exceeded."""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after

class NetworkError(RetryableError):
    """Raised when network issues occur."""
    pass

class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(self, max_retries=3, initial_delay=1.0, max_delay=60.0, 
                 exponential_base=2.0, jitter=True):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def calculate_delay(attempt, config):
    """Calculate delay for retry attempt."""
    import random
    
    delay = config.initial_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay

def is_retryable_error(error):
    """Check if error is retryable."""
    return isinstance(error, RetryableError)

def extract_retry_after(error):
    """Extract retry-after information from error."""
    if hasattr(error, 'retry_after') and error.retry_after:
        return error.retry_after
    return None

class BenchmarkUI:
    """UI components for benchmark operations."""
    
    def __init__(self):
        self.console = Console() if Console else None
    
    def display_benchmark_menu(self):
        """Display benchmark selection menu."""
        if not inquirer:
            print("1. API Benchmark")
            print("2. Kubernetes Benchmark")
            print("3. View Results")
            print("4. Back to Main Menu")
            choice = input("Select option: ")
            return {"benchmark_type": choice}
        
        questions = [
            inquirer.List('benchmark_type',
                         message="What type of benchmark would you like to run?",
                         choices=[
                             ('API Benchmark', 'api'),
                             ('Kubernetes Benchmark', 'kubernetes'),
                             ('View Results', 'view_results'),
                             ('Back to Main Menu', 'back')
                         ])
        ]
        return inquirer.prompt(questions)

    def get_api_benchmark_config(self):
        """Get API benchmark configuration."""
        if not inquirer:
            config = {}
            config['model_name'] = input("Model name: ")
            config['num_requests'] = int(input("Number of requests: ") or "10")
            config['concurrency'] = int(input("Concurrency level: ") or "1")
            return config
        
        questions = [
            inquirer.Text('model_name', message="Model name"),
            inquirer.Text('num_requests', message="Number of requests", default="10"),
            inquirer.Text('concurrency', message="Concurrency level", default="1"),
            inquirer.Confirm('save_results', message="Save results?", default=True)
        ]
        return inquirer.prompt(questions)

    def get_kubernetes_config(self):
        """Get Kubernetes benchmark configuration."""
        if not inquirer:
            config = {}
            config['namespace'] = input("Kubernetes namespace: ") or "default"
            config['replicas'] = int(input("Number of replicas: ") or "3")
            return config
        
        questions = [
            inquirer.Text('namespace', message="Kubernetes namespace", default="default"),
            inquirer.Text('replicas', message="Number of replicas", default="3"),
            inquirer.Confirm('auto_scale', message="Enable auto-scaling?", default=False)
        ]
        return inquirer.prompt(questions)

    def display_progress(self, message):
        """Display progress information."""
        if self.console:
            self.console.print(f"[blue]{message}[/blue]")
        else:
            print(message)

    def display_results(self, results):
        """Display benchmark results."""
        if self.console and Table:
            table = Table(title="Benchmark Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in results.items():
                table.add_row(str(key), str(value))
            
            self.console.print(table)
        else:
            print("Benchmark Results:")
            for key, value in results.items():
                print(f"{key}: {value}")

class BenchmarkCommands:
    """Main benchmark commands interface."""
    
    def __init__(self):
        self.ui = BenchmarkUI()
        self.api_runner = APIBenchmarkRunner()
        self.k8s_manager = KubernetesBenchmarkManager()
        self.results_viewer = ResultsViewer()
        self.backup_manager = BackupManager()
        
    def run_benchmark_menu(self):
        """Run the benchmark menu interface."""
        while True:
            choice = self.ui.display_benchmark_menu()
            
            if not choice or choice.get('benchmark_type') == 'back':
                break
            
            benchmark_type = choice['benchmark_type']
            
            if benchmark_type == 'api':
                self.run_api_benchmark()
            elif benchmark_type == 'kubernetes':
                self.run_kubernetes_benchmark()
            elif benchmark_type == 'view_results':
                self.view_results()
            elif benchmark_type in ['1', '2', '3', '4']:
                # Handle numeric choices for fallback mode
                if benchmark_type == '1':
                    self.run_api_benchmark()
                elif benchmark_type == '2':
                    self.run_kubernetes_benchmark()
                elif benchmark_type == '3':
                    self.view_results()
                elif benchmark_type == '4':
                    break

    def run_api_benchmark(self):
        """Run API benchmark."""
        self.ui.display_progress("Setting up API benchmark...")
        
        config = self.ui.get_api_benchmark_config()
        if not config:
            return
        
        try:
            # Convert string inputs to appropriate types
            num_requests = int(config.get('num_requests', 10))
            concurrency = int(config.get('concurrency', 1))
            
            self.ui.display_progress(f"Running benchmark with {num_requests} requests...")
            
            results = self.api_runner.run_benchmark(
                model_name=config['model_name'],
                num_requests=num_requests,
                concurrency=concurrency
            )
            
            self.ui.display_results(results)
            
            if config.get('save_results', True):
                self.save_results(results, 'api_benchmark')
                
        except Exception as e:
            self.ui.display_progress(f"Error running API benchmark: {e}")

    def run_kubernetes_benchmark(self):
        """Run Kubernetes benchmark."""
        self.ui.display_progress("Setting up Kubernetes benchmark...")
        
        config = self.ui.get_kubernetes_config()
        if not config:
            return
        
        try:
            replicas = int(config.get('replicas', 3))
            
            self.ui.display_progress(f"Deploying {replicas} replicas...")
            
            results = self.k8s_manager.run_kubernetes_benchmark(
                namespace=config['namespace'],
                replicas=replicas,
                auto_scale=config.get('auto_scale', False)
            )
            
            self.ui.display_results(results)
            self.save_results(results, 'kubernetes_benchmark')
            
        except Exception as e:
            self.ui.display_progress(f"Error running Kubernetes benchmark: {e}")

    def view_results(self):
        """View benchmark results."""
        self.ui.display_progress("Loading results...")
        self.results_viewer.view_results()

    def save_results(self, results, benchmark_type):
        """Save benchmark results."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{benchmark_type}_results_{timestamp}.json"
            
            os.makedirs("benchmark_results", exist_ok=True)
            filepath = os.path.join("benchmark_results", filename)
            
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.ui.display_progress(f"Results saved to {filepath}")
            
            # Backup results
            self.backup_manager.backup_results(filepath)
            
        except Exception as e:
            self.ui.display_progress(f"Error saving results: {e}")

# Main function for CLI usage
def main():
    """Main entry point for benchmark commands."""
    try:
        benchmark_commands = BenchmarkCommands()
        benchmark_commands.run_benchmark_menu()
    except KeyboardInterrupt:
        print("\nBenchmark cancelled by user")
    except Exception as e:
        print(f"Error in benchmark commands: {e}")

if __name__ == "__main__":
    main() 