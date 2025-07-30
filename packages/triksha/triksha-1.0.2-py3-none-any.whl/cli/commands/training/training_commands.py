"""Training commands for the Dravik CLI"""
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import inquirer

from .ui import TrainingUI
from .model_manager import ModelManager
from .dataset_handler import DatasetHandler
from .config_manager import ConfigManager
from .metrics import TrainingMetricsManager

class TrainingCommands:
    """Command class for training operations"""
    
    def __init__(self, db, config):
        """
        Initialize training commands
        
        Args:
            db: Database connection
            config: Application configuration
        """
        self.db = db
        self.config = config
        self.console = Console()
        
        # Setup directories
        self.training_dir = Path(config.get('training_dir', 'training_outputs'))
        self.training_dir.mkdir(exist_ok=True, parents=True)
        self.configs_dir = Path(config.get('configs_dir', 'training_configs'))
        self.configs_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize component managers
        self.ui = TrainingUI(self.console)
        self.model_manager = ModelManager(db, config)
        self.dataset_handler = DatasetHandler(db, config)
        self.config_manager = ConfigManager(db, config, self.configs_dir)
        self.metrics_manager = TrainingMetricsManager(db, config)
    
    def train_model(self, dataset: Optional[Dict[str, Any]] = None):
        """Guide users through setting up and running model fine-tuning"""
        self.console.print(Panel.fit(
            "[bold]Model Fine-tuning[/]\n\n"
            "This wizard will guide you through the process of fine-tuning a language model.\n"
            "You'll select a model and training configuration.",
            title="[green]MODEL FINE-TUNING WIZARD[/]",
            border_style="green"
        ))
        
        try:
            # If no dataset provided, show available datasets first
            if not dataset:
                self.console.print("\n[bold cyan]Available Datasets:[/]")
                self.dataset_handler.display_datasets()
                dataset = self.dataset_handler.select_dataset_for_training()
                if not dataset:
                    return
            
            # Get configuration (new or saved)
            training_config = self.ui.get_training_config(
                self.config_manager.list_configs(),
                self.model_manager.get_available_models(),
                dataset
            )
            
            if not training_config:
                return
            
            # Add dataset info to config
            training_config['dataset_info'] = dataset['info']
            training_config['dataset_format'] = dataset['format']
            
            # Ask if user wants to use Kubernetes
            if inquirer.confirm("Would you like to run this training job on Kubernetes?", default=False):
                training_config['use_kubernetes'] = True
                
                # Get Kubernetes-specific configuration
                k8s_config = self.ui.get_kubernetes_config()
                if k8s_config:
                    training_config.update(k8s_config)
                else:
                    self.console.print("[yellow]Kubernetes configuration cancelled. Falling back to local training.[/]")
                    training_config['use_kubernetes'] = False
            
            # Confirm and save config if needed
            if not self.ui.confirm_training_config(training_config):
                self.console.print("[yellow]Training cancelled by user.[/]")
                return
                
            if training_config.get('save_config', False):
                self.config_manager.save_config(training_config)
            
            # Run the actual training with dataset
            self.ui.run_training_process(
                training_config,
                self.model_manager,
                self.metrics_manager,
                self.training_dir,
                dataset=dataset
            )
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Training setup cancelled by user.[/]")
        except Exception as e:
            self.console.print(f"[bold red]Error during training setup: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
    
    def view_training_history(self):
        """Display past training runs and their metrics"""
        try:
            # Check for active Kubernetes jobs first
            active_k8s_runs = self.metrics_manager.get_active_kubernetes_runs()
            if active_k8s_runs:
                self.console.print(Panel(
                    f"[bold yellow]Active Kubernetes Training Jobs: {len(active_k8s_runs)}[/]\n\n"
                    "There are training jobs currently running on Kubernetes.",
                    title="[blue]KUBERNETES JOBS[/]",
                    border_style="blue"
                ))
                
                # Show active jobs
                for run in active_k8s_runs:
                    status = run.get('kubernetes_status', 'Unknown')
                    status_color = {
                        'Pending': 'yellow',
                        'Running': 'green',
                        'Succeeded': 'bold green',
                        'Failed': 'bold red'
                    }.get(status, 'white')
                    
                    self.console.print(f"• {run['name']}: [{status_color}]{status}[/]")
                
                self.console.print()
            
            # Get all training history
            training_runs = self.metrics_manager.get_training_runs(include_kubernetes=True)
            
            if not training_runs and not active_k8s_runs:
                self.console.print("[yellow]No training history found.[/]")
                return
                
            # Display training history and handle user interaction
            selected_run = self.ui.display_training_history(training_runs)
            if selected_run:
                # Get detailed metrics for the selected run
                detailed_metrics = self.metrics_manager.get_detailed_metrics(selected_run["id"])
                # Show detailed view
                self.ui.display_detailed_metrics(selected_run, detailed_metrics)
                
                # If it's a Kubernetes job, offer job-specific actions
                if selected_run.get('kubernetes_pod') and selected_run['status'] in ['in_progress', 'running', 'paused']:
                    self._handle_kubernetes_job_actions(selected_run)
                # Otherwise offer model loading/exporting options
                elif self.ui.should_load_model(selected_run):
                    self.model_manager.load_model(selected_run["model_path"])
                
        except Exception as e:
            self.console.print(f"[bold red]Error viewing training history: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
    
    def _handle_kubernetes_job_actions(self, run: Dict[str, Any]):
        """Handle actions for active Kubernetes jobs"""
        actions = []
        
        # Add pause/resume option based on current status
        if run['status'] in ['in_progress', 'running']:
            actions.append(('Pause training', 'pause'))
        elif run['status'] == 'paused':
            actions.append(('Resume training', 'resume'))
            
        # Add other options
        actions.extend([
            ('View pod logs', 'logs'),
            ('View pod details', 'details'),
            ('Back', 'back')
        ])
        
        questions = [
            inquirer.List(
                'action',
                message="Select an action",
                choices=[choice[0] for choice in actions]
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers:
            return
            
        action = next(action[1] for action in actions if action[0] == answers['action'])
        
        if action == 'pause':
            self.metrics_manager.pause_training_run(run['id'])
        elif action == 'resume':
            self.metrics_manager.resume_training_run(run['id'])
        elif action == 'logs':
            self.ui._display_kubernetes_logs(run['kubernetes_pod'])
        elif action == 'details':
            self.ui._display_kubernetes_pod_details(run['kubernetes_pod'])
    
    def manage_training_configs(self):
        """Allow users to create/edit/delete training configurations"""
        try:
            # List existing configs
            configs = self.config_manager.list_configs()
            
            # Get user action (create, edit, delete, import, export)
            action, selected_config = self.ui.get_config_action(configs)
            
            if action == "create":
                # Create new config through UI
                new_config = self.ui.create_config(
                    self.model_manager.get_available_models(),
                    self.dataset_handler.get_available_datasets()
                )
                if new_config:
                    self.config_manager.save_config(new_config)
                    
            elif action == "edit" and selected_config:
                # Edit existing config
                edited_config = self.ui.edit_config(
                    selected_config,
                    self.model_manager.get_available_models(),
                    self.dataset_handler.get_available_datasets()
                )
                if edited_config:
                    self.config_manager.save_config(edited_config)
                    
            elif action == "delete" and selected_config:
                # Delete config with confirmation
                if self.ui.confirm_deletion(selected_config["name"]):
                    self.config_manager.delete_config(selected_config["id"])
                    
            elif action == "import":
                # Import config from file
                config_path = self.ui.get_import_path()
                if config_path:
                    self.config_manager.import_config(config_path)
                    
            elif action == "export" and selected_config:
                # Export config to file
                export_path = self.ui.get_export_path(selected_config["name"])
                if export_path:
                    self.config_manager.export_config(selected_config["id"], export_path)
                    
        except Exception as e:
            self.console.print(f"[bold red]Error managing training configs: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
