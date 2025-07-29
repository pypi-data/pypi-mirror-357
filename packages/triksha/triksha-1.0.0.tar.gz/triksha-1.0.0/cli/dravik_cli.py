#!/usr/bin/env python3
"""
Command-line entry point for Dravik CLI tools

This script serves as the main entry point for various Dravik CLI commands
including dataset formatting, dependency management, training, and scheduled benchmarking.

Usage:
  dravik dataset download [--id ID] [--subset SUBSET]
  dravik dataset format [--input INPUT] [--type TYPE]
  dravik dataset view [--id ID]
  dravik dataset export [--id ID] [--format FORMAT]
  dravik dataset delete [--id ID]
  dravik train --model MODEL --dataset DATASET
  dravik benchmark [COMMAND]
  dravik scheduled [--action ACTION] [--id ID]
  dravik settings email [--action ACTION]
  dravik scheduler [--action ACTION]
"""
import argparse
import importlib.util
import sys
from pathlib import Path
from rich.console import Console

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from cli.commands.dataset import DatasetCommands
from cli.commands.benchmark.command import BenchmarkCommands
from cli.commands.fix_red_teaming import RedTeamingFixCommands
from cli.core import TrikshaCLI
from db_handler import DravikDB

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Dravik CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Dataset command
    dataset_parser = subparsers.add_parser("dataset", help="Dataset operations")
    dataset_subparsers = dataset_parser.add_subparsers(dest="dataset_command", help="Dataset command")
    
    # Dataset download command
    dataset_download_parser = dataset_subparsers.add_parser("download", help="Download a dataset from HuggingFace")
    dataset_download_parser.add_argument("--id", type=str, help="HuggingFace dataset ID")
    dataset_download_parser.add_argument("--subset", type=str, help="Dataset subset")
    
    # Dataset format command
    dataset_format_parser = dataset_subparsers.add_parser("format", help="Format a dataset")
    dataset_format_parser.add_argument("--input", type=str, help="Input dataset ID")
    dataset_format_parser.add_argument("--type", type=str, choices=["jailbreak", "safety"], default="jailbreak", help="Format type")
    
    # Dataset view command
    dataset_view_parser = dataset_subparsers.add_parser("view", help="View datasets")
    dataset_view_parser.add_argument("--id", type=str, help="Dataset ID to view")
    
    # Dataset export command
    dataset_export_parser = dataset_subparsers.add_parser("export", help="Export a dataset")
    dataset_export_parser.add_argument("--id", type=str, help="Dataset ID to export")
    dataset_export_parser.add_argument("--format", type=str, choices=["json", "csv"], default="json", help="Export format")
    
    # Dataset delete command
    dataset_delete_parser = dataset_subparsers.add_parser("delete", help="Delete a dataset")
    dataset_delete_parser.add_argument("--id", type=str, help="Dataset ID to delete")
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Benchmark operations")
    benchmark_subparsers = benchmark_parser.add_subparsers(dest="benchmark_command", help="Benchmark command")
    
    # Main benchmark command
    benchmark_run_parser = benchmark_subparsers.add_parser("run", help="Run a benchmark")
    benchmark_run_parser.add_argument("--model", type=str, help="Model to benchmark")
    benchmark_run_parser.add_argument("--dataset", type=str, help="Dataset to use for benchmarking")
    benchmark_run_parser.add_argument("--templates", type=str, help="Jailbreak templates to use")
    
    # Scheduled benchmark command
    benchmark_scheduled_parser = benchmark_subparsers.add_parser("scheduled", help="Run a scheduled benchmark")
    benchmark_scheduled_parser.add_argument("--params-file", type=str, required=True, help="Path to JSON file with benchmark parameters")
    benchmark_scheduled_parser.add_argument("--task-id", type=str, required=True, help="Task ID for the scheduled benchmark")
    
    # Benchmark results commands
    benchmark_results_parser = benchmark_subparsers.add_parser("results", help="View results")
    benchmark_results_parser.add_argument("--id", type=int, help="ID of specific benchmark to view")
    
    # Benchmark export command
    benchmark_export_parser = benchmark_subparsers.add_parser("export", help="Export results")
    benchmark_export_parser.add_argument("--id", type=int, help="ID of specific benchmark to export")
    benchmark_export_parser.add_argument("--format", type=str, choices=["json", "csv"], default="csv", help="Export format")
    
    # Red Teaming command
    redt_parser = subparsers.add_parser("redt", help="Red teaming conversation tools and fixes")
    redt_subparsers = redt_parser.add_subparsers(dest="redt_command", help="Red teaming command")
    
    # Red Teaming fix command
    redt_fix_parser = redt_subparsers.add_parser("fix", help="Fix issues with the red teaming conversation module")
    redt_fix_parser.add_argument("--backup", action="store_true", help="Create a backup of the original file before fixing")
    
    # Red Teaming test command
    redt_test_parser = redt_subparsers.add_parser("test", help="Test the red teaming conversation module")
    redt_test_parser.add_argument("--model", type=str, default="distilbert/distilgpt2", help="HuggingFace model to use")
    redt_test_parser.add_argument("--target", type=str, default="ollama", help="Target type (openai, gemini, ollama)")
    redt_test_parser.add_argument("--target-id", type=str, default="gemma:2b", help="Target model ID")
    redt_test_parser.add_argument("--turns", type=int, default=3, help="Number of conversation turns")
    
    # Scheduled command for managing scheduled tasks
    scheduled_parser = subparsers.add_parser("scheduled", help="Manage scheduled benchmarks")
    scheduled_parser.add_argument("--action", type=str, choices=["list", "configure", "delete", "logs"], default="list", help="Action to perform")
    scheduled_parser.add_argument("--id", type=str, help="ID of the scheduled task (for delete action)")
    
    # Scheduler service command
    scheduler_parser = subparsers.add_parser("scheduler", help="Manage the scheduler service")
    scheduler_parser.add_argument("--action", type=str, choices=["start", "stop", "status", "start-daemon", "install-service", "config-autostart", "run-now"], 
                                  default="status", help="Action to perform on the scheduler service")
    scheduler_parser.add_argument("--enable", type=str, choices=["true", "false"], 
                                  help="Enable or disable auto-starting the scheduler (for config-autostart action)")
    scheduler_parser.add_argument("--task-id", type=str, help="Task ID for run-now action")
    
    # Training command
    train_parser = subparsers.add_parser("train", help="Training operations")
    train_parser.add_argument("--model", type=str, required=True, help="Model to train")
    train_parser.add_argument("--dataset", type=str, required=True, help="Dataset to train on")
    train_parser.add_argument("--output", type=str, help="Output directory")
    
    # Settings command
    settings_parser = subparsers.add_parser("settings", help="Configuration settings")
    settings_subparsers = settings_parser.add_subparsers(dest="settings_type")
    
    # Email settings command
    email_settings_parser = settings_subparsers.add_parser("email", help="Email notification settings")
    email_settings_parser.add_argument("--action", type=str, choices=["setup", "disable", "status"], 
                                      help="Action to perform", required=True)
    
    args = parser.parse_args()
    
    # Initialize database and config
    db = DravikDB()
    config = {}  # Load config from file if needed
    
    if args.command == "dataset":
        dataset_commands = DatasetCommands(db, config)
        
        if args.dataset_command == "download":
            if args.id:
                dataset_info = {
                    'dataset_id': args.id,
                    'subset': args.subset
                }
                dataset_commands.download_dataset(dataset_info)
            else:
                dataset_commands.download_dataset()
        
        elif args.dataset_command == "format":
            if args.input:
                dataset_commands.format_for_adversarial(args.input, args.type)
            else:
                dataset_commands.format_dataset()
        
        elif args.dataset_command == "view":
            if args.id:
                dataset_commands.view_dataset(args.id)
            else:
                dataset_commands.list_and_view_datasets()
        
        elif args.dataset_command == "export":
            if args.id:
                dataset_commands.export_dataset(args.id, args.format)
            else:
                dataset_commands.export_dataset()
        
        elif args.dataset_command == "delete":
            if args.id:
                dataset_commands.delete_dataset(args.id)
            else:
                dataset_commands.delete_dataset()
        
        else:
            Console().print("[yellow]Unknown dataset command. Use one of: download, format, view, export, delete[/]")
    
    elif args.command == "train":
        cli = TrikshaCLI()
        cli.handle_training_commands(args)
    
    elif args.command == "benchmark":
        benchmark_commands = BenchmarkCommands(db, config)
        
        if args.benchmark_command == "scheduled":
            # Handle scheduled benchmark command
            benchmark_commands.run_scheduled_benchmark_command(
                params_file=args.params_file,
                task_id=args.task_id
            )
        elif args.benchmark_command is None:
            # Run interactive benchmark menu
            benchmark_commands.handle_benchmark_commands()
        else:
            benchmark_commands.run(args)
    
    elif args.command == "scheduled":
        benchmark_commands = BenchmarkCommands(db, config)
        
        if args.action == "configure":
            benchmark_commands.configure_scheduled_benchmark()
        elif args.action == "list":
            benchmark_commands.list_scheduled_benchmarks()
        elif args.action == "delete":
            if args.id:
                # Import scheduler and remove task directly
                from cli.scheduler import get_scheduler
                scheduler = get_scheduler()
                if scheduler.remove_task(args.id):
                    Console().print(f"[green]Successfully deleted scheduled benchmark with ID: {args.id}[/]")
                else:
                    Console().print(f"[red]Failed to delete scheduled benchmark with ID: {args.id}[/]")
            else:
                benchmark_commands.delete_scheduled_benchmark()
        elif args.action == "logs":
            # View logs for scheduled tasks
            benchmark_commands.view_scheduled_task_logs()
        else:
            Console().print("[yellow]Unknown scheduled command. Use --action=list|configure|delete|logs[/]")
    
    elif args.command == "scheduler":
        # Import and use the scheduler_service module
        try:
            from cli.scheduler_service import start_service, stop_service, check_status, run_as_daemon, is_running
            
            if args.action == "start":
                # First start the scheduler instance
                from cli.scheduler import get_scheduler
                scheduler = get_scheduler()
                scheduler.start()
                Console().print("[green]Scheduler instance started.[/]")
                
                # Then start the service
                start_service()
            elif args.action == "stop":
                stop_service()
            elif args.action == "status":
                check_status()
            elif args.action == "start-daemon":
                run_as_daemon()
            elif args.action == "install-service":
                # Install the service based on platform
                import platform
                system = platform.system()
                
                if system == "Linux":
                    from cli.scheduler_service import install_systemd_service
                    install_systemd_service()
                elif system == "Darwin":
                    from cli.scheduler_service import install_macos_service
                    install_macos_service()
                else:
                    Console().print(f"[yellow]Automatic service installation not supported on {system}.[/]")
                    Console().print("[yellow]Please run 'dravik scheduler --action=start-daemon' manually.[/]")
            elif args.action == "config-autostart":
                # Configure auto-start setting
                config_dir = Path.home() / "dravik" / "config"
                config_dir.mkdir(exist_ok=True, parents=True)
                config_file = config_dir / "scheduler.config"
                
                if args.enable is not None:
                    # User provided a value, update the config
                    with open(config_file, "w") as f:
                        f.write(f"auto_start={args.enable.lower()}")
                    
                    if args.enable.lower() == "true":
                        Console().print("[green]Scheduler will now start automatically when using the CLI.[/]")
                        # Also start it immediately if it's not running
                        if not is_running():
                            from cli.scheduler import get_scheduler
                            scheduler = get_scheduler()
                            scheduler.start()
                            start_service()
                            Console().print("[green]Scheduler daemon has been started.[/]")
                    else:
                        Console().print("[yellow]Scheduler auto-start has been disabled.[/]")
                        Console().print("You can still start it manually with: dravik scheduler --action=start")
                else:
                    # Show current setting
                    auto_start = "true"  # Default is enabled
                    if config_file.exists():
                        with open(config_file, "r") as f:
                            content = f.read().lower()
                            if "auto_start=false" in content:
                                auto_start = "false"
                    
                    Console().print(f"Scheduler auto-start is currently: [bold]{auto_start}[/]")
                    Console().print("\nTo change this setting, run:")
                    Console().print("  dravik scheduler --action=config-autostart --enable=true")
                    Console().print("  or")
                    Console().print("  dravik scheduler --action=config-autostart --enable=false")
            elif args.action == "run-now":
                if not args.task_id:
                    Console().print("[red]Error: --task-id is required for run-now action[/]")
                    Console().print("[yellow]Usage: dravik scheduler --action=run-now --task-id=<task_id>[/]")
                    return
                
                # Get the scheduler and run the task immediately
                from cli.scheduler import get_scheduler
                scheduler = get_scheduler()
                
                # Start the scheduler if it's not running
                if not is_running():
                    scheduler.start()
                    Console().print("[yellow]Scheduler was not running. Starting it now.[/]")
                
                # Run the task immediately
                if scheduler.run_task_immediately(args.task_id):
                    Console().print(f"[green]Successfully started task {args.task_id}[/]")
                    Console().print("[yellow]The task is now running in the background.[/]")
                    Console().print("[yellow]You can check logs in ~/dravik/logs/scheduled_tasks/[/]")
                else:
                    Console().print(f"[red]Failed to run task {args.task_id}[/]")
                    Console().print("[yellow]Check if the task ID is correct using 'dravik scheduled --action=list'[/]")
            else:
                # Unknown action
                Console().print("[yellow]Unknown scheduler action. Use --action=start|stop|status|start-daemon|install-service|config-autostart|run-now[/]")
                
        except ImportError as e:
            Console().print(f"[red]Error importing scheduler service: {e}[/]")
            Console().print("[yellow]Make sure python-daemon is installed: pip install python-daemon>=2.3.0[/]")
    
    elif args.command == "redt":
        redt_commands = RedTeamingFixCommands(db, config)
        redt_commands.handle(args)
    
    elif args.command == "settings":
        if args.settings_type == "email":
            # Import email service module
            from cli.notification.email_service import EmailNotificationService
            
            # Create email service
            email_service = EmailNotificationService()
            console = Console()
            
            if args.action == "setup":
                email_service.setup()
            elif args.action == "disable":
                email_service.disable()
            elif args.action == "status":
                if email_service.is_configured():
                    console.print("[green]Email notifications are enabled.[/]")
                    console.print(f"[green]Configured email: {email_service.config.get('email')}[/]")
                    if email_service.config.get('include_csv', False):
                        console.print("[green]CSV Results: Attached to email[/]")
                    else:
                        console.print("[yellow]CSV Results: Not enabled[/]")
                else:
                    console.print("[red]Email notifications are not enabled.[/]")
                    console.print("[yellow]Use --action=setup to configure email notifications.[/]")
        else:
            Console().print("[yellow]Unknown settings type. Use one of: email[/]")
    
    else:
        Console().print("[yellow]Unknown command. Use one of: dataset, train, benchmark, scheduled, scheduler, redt, settings[/]")

if __name__ == "__main__":
    main()
