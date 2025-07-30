import typer
import asyncio
import time
import psutil
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import json

from agent.main import AgentFramework
from agent.base import Agent, AgentTask

# Ensure there's only one app instance
app = typer.Typer()  # Create app only once
console = Console()

@app.callback()
def callback():
    """
    Agent command group for interacting with the AI agent framework
    """
    pass

def get_resource_monitor_display() -> str:
    """Get current system resource usage formatted as a string"""
    try:
        # Get real-time CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Initialize GPU data
        gpu_percent = None
        
        # Try to get GPU info using multiple methods
        try:
            import importlib
            if importlib.util.find_spec("GPUtil"):
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_percent = f"{gpus[0].load * 100:.1f}"
            elif importlib.util.find_spec("torch"):
                import torch
                if torch.cuda.is_available():
                    current_mem = torch.cuda.memory_allocated(0)
                    total_mem = torch.cuda.get_device_properties(0).total_memory
                    gpu_percent = f"{(current_mem / total_mem * 100):.1f}"
        except Exception:
            pass
        
        # Format the resource display with actual numbers
        resource_display = f"CPU: {cpu_percent:.1f}% | RAM: {memory_percent:.1f}%"
        if gpu_percent:
            resource_display += f" | GPU: {gpu_percent}%"
        
    except Exception:
        resource_display = "System Stats Unavailable"
        
    return resource_display

@app.command()
def monitor():
    """Monitor system resources during agent operations"""
    try:
        console.print("[bold]Monitoring System Resources...[/]")
        console.print("Press Ctrl+C to stop monitoring")
        
        with Live("", refresh_per_second=2) as live:
            while True:
                status = get_resource_monitor_display()
                live.update(f"[bold]System Resources:[/] {status}")
                time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[bold green]Monitoring stopped[/]")
