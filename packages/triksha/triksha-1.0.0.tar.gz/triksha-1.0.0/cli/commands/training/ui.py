"""UI components for training operations"""
import inquirer
import time
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from uuid import uuid4

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich import box
from rich.markdown import Markdown

class TrainingUI:
    """User interface for training interactions"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def run_training_process(self, 
                            config: Dict[str, Any],
                            model_manager,
                            metrics_manager,
                            output_dir: str,
                            dataset: Optional[Dict[str, Any]] = None) -> None:
        """Run the training process"""
        try:
            # Validate dataset
            if not dataset:
                self.console.print("[red]No dataset provided for training[/]")
                return
                
            # Create output directory for this run
            run_id = f"{config['name']}_{int(time.time())}"
            run_dir = Path(output_dir) / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            config_path = run_dir / "config.json"
            with open(config_path, 'w') as f:
                # Remove the actual dataset to avoid serialization issues
                config_to_save = config.copy()
                config_to_save.pop('dataset', None)
                json.dump(config_to_save, f, indent=2)
            
            # Initialize training run in metrics database
            run_info = {
                'id': run_id,
                'name': config['name'],
                'description': config.get('description', ''),
                'model': config['model_id'],
                'dataset': config['dataset_info']['name'],
                'output_dir': str(run_dir),
                'config_path': str(config_path),
                'start_time': datetime.now().isoformat()
            }
            
            metrics_manager.create_training_run(run_info)
            
            # Start training
            if config.get('use_kubernetes'):
                self._run_kubernetes_training(config, run_info, dataset, metrics_manager)
            else:
                self._run_local_training(config, run_info, dataset, metrics_manager)
                
        except Exception as e:
            self.console.print(f"[red]Error starting training process: {str(e)}[/]")
            import traceback
            self.console.print(traceback.format_exc())
    
    def _run_kubernetes_training(self, config: Dict[str, Any], model_manager: Any, 
                               metrics_manager: Any, output_dir: Path, run_id: str) -> None:
        """Run training on Kubernetes"""
        try:
            # Create Kubernetes job
            from kubernetes import client, config as k8s_config
            k8s_config.load_kube_config()
            
            # Create unique names
            pod_name = f"dravik-training-{run_id[:8]}"
            
            # Create the training pod
            pod = client.V1Pod(
                metadata=client.V1ObjectMeta(
                    name=pod_name,
                    labels={"app": "dravik-training"}
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="training",
                            image="dravik/training:latest",  # Make sure this image exists
                            env=[
                                client.V1EnvVar(name="TRAINING_RUN_ID", value=run_id),
                                client.V1EnvVar(name="TRAINING_CONFIG", value=json.dumps(config)),
                                client.V1EnvVar(name="TRAINING_OUTPUT_DIR", value=str(output_dir))
                            ]
                        )
                    ],
                    restart_policy="Never"
                )
            )
            
            # Create pod in Kubernetes
            api = client.CoreV1Api()
            api.create_namespaced_pod(namespace="default", body=pod)
            
            # Update config with Kubernetes info
            config['kubernetes_pod'] = pod_name
            config['kubernetes_status'] = 'Pending'
            
            # Create training run record
            metrics_manager.create_training_run(run_id, config, pod_name)
            
            # Show initial status
            self.console.print(f"[green]✓ Training job started on Kubernetes[/]")
            self.console.print(f"[green]Pod name: {pod_name}[/]")
            
            # Monitor pod status
            self._display_pod_status(run_id, pod_name, metrics_manager)
            
        except Exception as e:
            self.console.print(f"[bold red]Error starting Kubernetes training: {str(e)}[/]")
            import traceback
            traceback.print_exc()
    
    def _display_pod_status(self, run_id: str, pod_name: str, metrics_manager: Any) -> None:
        """Display real-time pod status"""
        from kubernetes import client, config as k8s_config
        from kubernetes.client.rest import ApiException
        
        try:
            api = client.CoreV1Api()
            
            with Live(self._create_pod_status_display(pod_name, "Initializing..."), refresh_per_second=1) as live:
                while True:
                    try:
                        # Get pod status
                        pod = api.read_namespaced_pod(name=pod_name, namespace="default")
                        status = pod.status.phase
                        
                        # Update metrics database
                        metrics_manager.update_kubernetes_status(run_id)
                        
                        # Update display
                        live.update(self._create_pod_status_display(pod_name, status))
                        
                        # Check if we're done
                        if status in ["Succeeded", "Failed"]:
                            break
                            
                        time.sleep(2)
                        
                    except ApiException as e:
                        if e.status == 404:
                            self.console.print("[red]Pod not found. Training job may have been deleted.[/]")
                            break
                        raise
                        
        except Exception as e:
            self.console.print(f"[bold red]Error monitoring pod status: {str(e)}[/]")
    
    def _create_pod_status_display(self, pod_name: str, status: str) -> Panel:
        """Create a status display for Kubernetes pod"""
        status_color = {
            "Pending": "yellow",
            "Running": "green",
            "Succeeded": "bold green",
            "Failed": "bold red"
        }.get(status, "white")
        
        content = f"""
[bold]Training Pod:[/] {pod_name}
[bold]Status:[/] [{status_color}]{status}[/]
        """
        
        return Panel(content, title="[bold]Kubernetes Training Status[/]", border_style="blue")
    
    def display_training_history(self, training_runs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Display training history with Kubernetes support"""
        self.console.print(Panel("[bold]Training History[/]", border_style="green"))
        
        if not training_runs:
            self.console.print("[yellow]No training history found.[/]")
            return None
        
        # Create table of runs
        table = Table(box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Approach", style="yellow")
        table.add_column("Status", style="bold")
        table.add_column("Type", style="magenta")
        table.add_column("Date", style="blue")
        table.add_column("Duration", style="magenta")
        
        for run in training_runs:
            # Determine status style
            status = run["status"]
            status_style = {
                "completed": "green",
                "failed": "red",
                "in_progress": "yellow",
                "initializing": "blue",
                "paused": "yellow"
            }.get(status.lower(), "white")
            
            # Format date
            created_date = run["created_at"].split("T")[0] if "T" in run.get("created_at", "") else run.get("created_at", "")
            
            # Format duration
            duration = run.get("duration_seconds", 0)
            if duration:
                hours, remainder = divmod(int(duration), 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"
            else:
                duration_str = "N/A"
            
            # Determine if it's a Kubernetes job
            is_k8s = bool(run.get("kubernetes_pod"))
            job_type = "[blue]K8s[/]" if is_k8s else "Local"
            
            table.add_row(
                run["name"],
                run["model_id"].split("/")[-1],
                run["approach"].upper(),
                f"[{status_style}]{status}[/]",
                job_type,
                created_date,
                duration_str
            )
            
        self.console.print(table)
        
        # Let user select a run to view
        run_choices = [(f"{r['name']} ({r['model_id'].split('/')[-1]})", r) for r in training_runs]
        run_choices.append(("Back", None))
        
        questions = [
            inquirer.List(
                'run',
                message="Select a training run to view details",
                choices=run_choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['run'] if answers else None
    
    def _update_epoch_end(self, metrics_manager, run_id: str, metrics: Dict[str, Any], epoch: int, epoch_metrics: Dict[str, Any]):
        """Handle epoch end event"""
        metrics["epochs_completed"] += 1
        
        # Save metrics to database
        epoch_data = {
            "epoch": epoch,
            "loss": metrics["loss"],
            "learning_rate": metrics["learning_rate"],
            "timestamp": time.time(),
            **epoch_metrics
        }
        metrics_manager.save_training_metrics(run_id, epoch_data)
        
        # Update display if we have access to live display
        if hasattr(self, 'live_display'):
            try:
                self.live_display.update(self._create_progress_display(None, metrics))
            except:
                pass
    
    def _handle_training_complete(self, metrics_manager, run_id: str, model_path: str, 
                               start_time: float, output_dir: Path):
        """Handle training completion"""
        # Calculate duration
        duration = time.time() - start_time
        
        # Mark training as complete in the database
        metrics_manager.complete_training_run(run_id, str(model_path), duration)
        
        # Format duration
        hours, remainder = divmod(int(duration), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"
        
        # Display completion message
        self.console.print(f"\n[bold green]✓ Training complete in {duration_str}![/]")
        self.console.print(f"[green]Model saved to: {model_path}[/]")
        self.console.print(f"[green]Training outputs directory: {output_dir}[/]")
    
    def display_detailed_metrics(self, run: Dict[str, Any], metrics: Dict[str, Any]):
        """Display detailed metrics for a training run"""
        self.console.print(Panel(f"[bold]Training Run: {run['name']}[/]", border_style="green"))
        
        # Basic info table
        info_table = Table(box=box.SIMPLE)
        info_table.add_column("Parameter", style="cyan")
        info_table.add_column("Value", style="green")
        
        # Add basic run info
        info_table.add_row("Model", run["model_id"])
        info_table.add_row("Approach", run["approach"].upper())
        info_table.add_row("Status", run["status"])
        info_table.add_row("Created", run["created_at"])
        if run.get("completed_at"):
            info_table.add_row("Completed", run["completed_at"])
            
        # Add duration if available
        if run.get("duration_seconds"):
            hours, remainder = divmod(int(run["duration_seconds"]), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"
            info_table.add_row("Duration", duration_str)
            
        # Add model path if available
        if run.get("model_path"):
            info_table.add_row("Model Path", run["model_path"])
        
        # Add Kubernetes information if available
        try:
            config = json.loads(run.get("config", "{}"))
            if "kubernetes_pod" in config:
                info_table.add_row("Kubernetes Pod", config["kubernetes_pod"])
                if "kubernetes_status" in config:
                    info_table.add_row("Pod Status", config["kubernetes_status"])
        except (json.JSONDecodeError, TypeError):
            pass
            
        self.console.print(info_table)
        
        # Check if we have epoch metrics
        if "epochs" in metrics and metrics["epochs"]:
            self.console.print("\n[bold]Training Metrics by Epoch:[/]")
            
            # Create metrics table
            metrics_table = Table(box=box.SIMPLE)
            metrics_table.add_column("Epoch", style="cyan")
            metrics_table.add_column("Loss", style="green")
            metrics_table.add_column("Learning Rate", style="blue")
            
            # Add additional metrics columns if available
            additional_metrics = metrics.get("additional_metrics", [])
            for metric_name in additional_metrics:
                metrics_table.add_column(metric_name.replace("_", " ").title(), style="yellow")
                
            # Add rows for each epoch
            for epoch_data in metrics["epochs"]:
                row = [
                    str(epoch_data["epoch"]),
                    f"{epoch_data.get('loss', 0):.4f}",
                    f"{epoch_data.get('learning_rate', 0):.2e}",
                ]
                
                # Add values for additional metrics
                for metric_name in additional_metrics:
                    if metric_name in epoch_data:
                        value = epoch_data[metric_name]
                        if isinstance(value, float):
                            row.append(f"{value:.4f}")
                        else:
                            row.append(str(value))
                    else:
                        row.append("N/A")
                
                metrics_table.add_row(*row)
                
            self.console.print(metrics_table)
            
            # Show final loss
            if run.get("final_loss"):
                self.console.print(f"\n[bold]Final loss:[/] {run.get('final_loss'):.4f}")
        else:
            self.console.print("\n[yellow]No metrics data available for this run.[/]")
        
        # Show K8s training controls if job is running in Kubernetes
        is_kubernetes_job = False
        pod_name = None
        
        try:
            config = json.loads(run.get("config", "{}"))
            if "kubernetes_pod" in config:
                is_kubernetes_job = True
                pod_name = config["kubernetes_pod"]
        except (json.JSONDecodeError, TypeError):
            pass
            
        if is_kubernetes_job and run["status"] in ["in_progress", "running", "paused"]:
            # Show pause/resume controls
            self.console.print("\n[bold cyan]Kubernetes Job Controls:[/]")
            
            actions = []
            
            # Add pause/resume option based on current status
            if run["status"] in ["in_progress", "running"]:
                actions.append(("Pause training", "pause"))
            elif run["status"] == "paused":
                actions.append(("Resume training", "resume"))
                
            # Add other options
            actions.extend([
                ("View Kubernetes pod logs", "logs"),
                ("View pod details", "details"),
                ("Back", "back")
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
                
            selected_action = answers['action']
            
            # Map the selected action to the action code
            action_code = None
            for choice in actions:
                if choice[0] == selected_action:
                    action_code = choice[1]
                    break
                    
            # Execute the selected action
            if action_code == "pause":
                from .metrics import TrainingMetricsManager
                metrics_manager = TrainingMetricsManager(self.console._console.file, {})
                if metrics_manager.pause_training_run(run["id"]):
                    self.console.print("[green]✓ Training job paused successfully[/]")
                else:
                    self.console.print("[red]Failed to pause training job[/]")
                    
            elif action_code == "resume":
                from .metrics import TrainingMetricsManager
                metrics_manager = TrainingMetricsManager(self.console._console.file, {})
                if metrics_manager.resume_training_run(run["id"]):
                    self.console.print("[green]✓ Training job resumed successfully[/]")
                else:
                    self.console.print("[red]Failed to resume training job[/]")
                    
            elif action_code == "logs" and pod_name:
                self._display_kubernetes_logs(pod_name)
                
            elif action_code == "details" and pod_name:
                self._display_kubernetes_pod_details(pod_name)
                
    def _display_kubernetes_logs(self, pod_name: str) -> None:
        """Display logs from a Kubernetes pod"""
        from kubernetes import client, config as k8s_config
        
        try:
            k8s_config.load_kube_config()
            k8s_api = client.CoreV1Api()
            
            self.console.print(f"[bold]Fetching logs for pod: {pod_name}[/]")
            
            # Get the logs
            logs = k8s_api.read_namespaced_pod_log(
                name=pod_name,
                namespace="default",
                container="training-container",
                tail_lines=200  # Get last 200 lines
            )
            
            # Display the logs
            self.console.print(Panel(logs, title="[bold]Pod Logs (Last 200 Lines)[/]", border_style="blue"))
            
        except Exception as e:
            self.console.print(f"[red]Error fetching pod logs: {str(e)}[/]")
            
    def _display_kubernetes_pod_details(self, pod_name: str) -> None:
        """Display detailed information about a Kubernetes pod"""
        from kubernetes import client, config as k8s_config
        
        try:
            k8s_config.load_kube_config()
            k8s_api = client.CoreV1Api()
            
            self.console.print(f"[bold]Fetching details for pod: {pod_name}[/]")
            
            # Get pod details
            pod = k8s_api.read_namespaced_pod(name=pod_name, namespace="default")
            
            # Display pod information
            details_table = Table(box=box.SIMPLE)
            details_table.add_column("Property", style="cyan")
            details_table.add_column("Value", style="green")
            
            details_table.add_row("Name", pod.metadata.name)
            details_table.add_row("Namespace", pod.metadata.namespace)
            details_table.add_row("Status", pod.status.phase)
            details_table.add_row("Pod IP", pod.status.pod_ip or "N/A")
            details_table.add_row("Node", pod.spec.node_name or "N/A")
            details_table.add_row("Start Time", str(pod.status.start_time) if pod.status.start_time else "N/A")
            
            # Show container information
            if pod.spec.containers:
                container = pod.spec.containers[0]
                details_table.add_row("Container Name", container.name)
                details_table.add_row("Container Image", container.image)
                
                # Show resource requests and limits
                if container.resources:
                    if container.resources.requests:
                        for resource, value in container.resources.requests.items():
                            details_table.add_row(f"Request {resource}", str(value))
                            
                    if container.resources.limits:
                        for resource, value in container.resources.limits.items():
                            details_table.add_row(f"Limit {resource}", str(value))
            
            self.console.print(details_table)
            
            # Show pod conditions
            if pod.status.conditions:
                self.console.print("\n[bold]Pod Conditions:[/]")
                conditions_table = Table(box=box.SIMPLE)
                conditions_table.add_column("Type", style="cyan")
                conditions_table.add_column("Status", style="green")
                conditions_table.add_column("Last Transition", style="yellow")
                
                for condition in pod.status.conditions:
                    status_style = "green" if condition.status == "True" else "red"
                    conditions_table.add_row(
                        condition.type,
                        f"[{status_style}]{condition.status}[/]",
                        str(condition.last_transition_time) if condition.last_transition_time else "N/A"
                    )
                    
                self.console.print(conditions_table)
                
        except Exception as e:
            self.console.print(f"[red]Error fetching pod details: {str(e)}[/]")
    
    def should_load_model(self, run: Dict[str, Any]) -> bool:
        """Ask if user wants to load the model from a training run"""
        if run.get("model_path") and os.path.exists(run["model_path"]):
            return inquirer.confirm(
                message=f"Would you like to load this model?",
                default=False
            )
        else:
            self.console.print("[yellow]Model file not found or path not specified.[/]")
            return False
    
    # Configuration management UI methods
    def get_config_action(self, configs: List[Dict[str, Any]]) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Get user action for configuration management"""
        self.console.print(Panel("[bold]Training Configuration Management[/]", border_style="blue"))
        
        if configs:
            # Display existing configs
            table = Table(box=box.ROUNDED)
            table.add_column("Name", style="cyan")
            table.add_column("Model", style="green")
            table.add_column("Approach", style="yellow")
            table.add_column("Created", style="dim")
            
            for config in configs:
                created_at = config.get("created_at", "Unknown").split("T")[0] if "T" in config.get("created_at", "") else "Unknown"
                table.add_row(
                    config["name"],
                    config["model_id"].split("/")[-1],
                    config["approach"].upper(),
                    created_at
                )
            
            self.console.print(table)
            
            # Actions with existing configs
            action_choices = [
                ("Create new configuration", ("create", None)),
                ("Edit existing configuration", "edit"),
                ("Delete configuration", "delete"),
                ("Import configuration from file", ("import", None)),
                ("Export configuration", "export"),
                ("Back", ("back", None))
            ]
            
            # For edit, delete and export actions, we need to select a config
            questions = [
                inquirer.List(
                    'action',
                    message="Select an action",
                    choices=[choice[0] for choice in action_choices]
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers:
                return "back", None
                
            selected_action = answers['action']
            
            # Handle actions that require selecting a config
            if selected_action in ["Edit existing configuration", "Delete configuration", "Export configuration"]:
                config_choices = [(f"{c['name']} ({c['model_id'].split('/')[-1]})", c) for c in configs]
                config_choices.append(("Cancel", None))
                
                config_questions = [
                    inquirer.List(
                        'config',
                        message=f"Select configuration to {selected_action.lower().split()[0]}",
                        choices=config_choices
                    )
                ]
                
                config_answers = inquirer.prompt(config_questions)
                if not config_answers or not config_answers['config']:
                    return "back", None
                    
                # Map the action name to action code
                action_map = {
                    "Edit existing configuration": "edit",
                    "Delete configuration": "delete",
                    "Export configuration": "export"
                }
                
                return action_map[selected_action], config_answers['config']
            else:
                # Map the selected action to the action code
                for choice in action_choices:
                    if choice[0] == selected_action:
                        return choice[1][0], choice[1][1]
        else:
            # No configs exist yet
            action_choices = [
                ("Create new configuration", "create"),
                ("Import configuration from file", "import"),
                ("Back", "back")
            ]
            
            questions = [
                inquirer.List(
                    'action',
                    message="Select an action",
                    choices=[choice[0] for choice in action_choices]
                )
            ]
            
            answers = inquirer.prompt(questions)
            if not answers:
                return "back", None
                
            selected_action = answers['action']
            
            # Map the selected action to the action code
            for choice in action_choices:
                if choice[0] == selected_action:
                    return choice[1], None
        
        return "back", None
    
    def create_config(self, available_models: List[Dict[str, Any]], 
                    available_datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create a new configuration"""
        self.console.print(Panel("[bold]Create New Training Configuration[/]", border_style="blue"))
        
        # Reuse the setup_new_config method
        return self._setup_new_config(available_models, available_datasets)
    
    def edit_config(self, config: Dict[str, Any], available_models: List[Dict[str, Any]], 
                  available_datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Edit an existing configuration"""
        self.console.print(Panel(f"[bold]Editing Configuration: {config['name']}[/]", border_style="blue"))
        
        # Show the current config
        self.console.print("\n[bold]Current Configuration:[/]")
        self.confirm_training_config(config)
        
        # Ask which parts to edit
        edit_choices = [
            ("Name", "name"),
            ("Model", "model_id"),
            ("Training approach", "approach"),
            ("Dataset", "dataset"),
            ("Training parameters", "training_params"),
            ("Cancel editing", "cancel")
        ]
        
        questions = [
            inquirer.Checkbox(
                'edit_fields',
                message="Select fields to edit (use space to select, enter to confirm)",
                choices=[(c[0], c[1]) for c in edit_choices if c[1] != "cancel"]
            )
        ]
        
        answers = inquirer.prompt(questions)
        if not answers or not answers['edit_fields'] or "cancel" in answers['edit_fields']:
            return None
            
        # Create a copy of the config to edit
        edited_config = config.copy()
        
        # Edit each selected field
        for field in answers['edit_fields']:
            if field == "name":
                name_q = [
                    inquirer.Text(
                        'name',
                        message="Configuration name",
                        default=config["name"]
                    )
                ]
                name_ans = inquirer.prompt(name_q)
                if name_ans:
                    edited_config["name"] = name_ans["name"]
                    
            elif field == "model_id":
                model_choices = [(m["display_name"], m["id"]) for m in available_models]
                model_q = [
                    inquirer.List(
                        'model_id',
                        message="Select base model",
                        choices=model_choices,
                        default=next((m["id"] for m in available_models if m["id"] == config["model_id"]), None)
                    )
                ]
                model_ans = inquirer.prompt(model_q)
                if model_ans:
                    edited_config["model_id"] = model_ans["model_id"]
                    
            elif field == "approach":
                approach_choices = [
                    ("LoRA - Low-Rank Adaptation", "lora"),
                    ("QLoRA - Quantized Low-Rank Adaptation", "qlora"),
                    ("Full Fine-tuning", "full")
                ]
                approach_q = [
                    inquirer.List(
                        'approach',
                        message="Select training approach",
                        choices=approach_choices,
                        default=next((a[1] for a in approach_choices if a[1] == config["approach"]), None)
                    )
                ]
                approach_ans = inquirer.prompt(approach_q)
                if approach_ans:
                    edited_config["approach"] = approach_ans["approach"]
                    
            elif field == "dataset":
                # Dataset selection is more complex, reuse the existing logic
                self.console.print("\n[bold]Select new dataset:[/]")
                if not available_datasets:
                    self.console.print("[yellow]No prepared datasets found.[/]")
                    dataset_q = [
                        inquirer.Text(
                            'dataset_path',
                            message="Enter path to dataset file or directory",
                            validate=lambda _, x: Path(x).exists(),
                            default=config["dataset"].get("path", "") if isinstance(config["dataset"], dict) else ""
                        )
                    ]
                    dataset_ans = inquirer.prompt(dataset_q)
                    if dataset_ans:
                        edited_config["dataset"] = {"path": dataset_ans["dataset_path"], "type": "custom"}
                else:
                    dataset_choices = [(f"{d['name']} ({d['samples']} samples)", d) for d in available_datasets]
                    dataset_choices.append(("Custom dataset", {"type": "custom"}))
                    
                    dataset_q = [
                        inquirer.List(
                            'dataset',
                            message="Select dataset",
                            choices=dataset_choices
                        )
                    ]
                    dataset_ans = inquirer.prompt(dataset_q)
                    if dataset_ans:
                        selected_dataset = dataset_ans["dataset"]
                        if selected_dataset["type"] == "custom":
                            path_q = [
                                inquirer.Text(
                                    'dataset_path',
                                    message="Enter path to dataset file or directory",
                                    validate=lambda _, x: Path(x).exists(),
                                    default=config["dataset"].get("path", "") if isinstance(config["dataset"], dict) else ""
                                )
                            ]
                            path_ans = inquirer.prompt(path_q)
                            if path_ans:
                                edited_config["dataset"] = {"path": path_ans["dataset_path"], "type": "custom"}
                        else:
                            edited_config["dataset"] = selected_dataset
                            
            elif field == "training_params":
                # Edit training parameters
                self.console.print("\n[bold]Edit training parameters:[/]")
                edited_config["training_params"] = self._configure_training_parameters(
                    edited_config["approach"], 
                    config["training_params"]
                )
        
        # Confirm the edited config
        self.console.print("\n[bold]Updated Configuration:[/]")
        if not self.confirm_training_config(edited_config):
            return None
            
        return edited_config
    
    def _configure_training_parameters(self, approach: str, defaults: Dict[str, Any] = None) -> Dict[str, Any]:
        """Configure training parameters with optional defaults"""
        if defaults is None:
            # Set defaults based on approach
            defaults = {
                "lora": {"epochs": 3, "batch_size": 8, "learning_rate": 2e-5, "lora_rank": 8, "lora_alpha": 16},
                "qlora": {"epochs": 4, "batch_size": 4, "learning_rate": 2e-5, "lora_rank": 16, "lora_alpha": 32},
                "full": {"epochs": 2, "batch_size": 4, "learning_rate": 5e-6}
            }.get(approach, {"epochs": 3, "batch_size": 8, "learning_rate": 2e-5})
        
        questions = [
            inquirer.Text(
                'epochs',
                message="Number of epochs",
                default=str(defaults.get("epochs", 3)),
                validate=lambda _, x: x.isdigit() and 1 <= int(x) <= 50
            ),
            inquirer.Text(
                'batch_size',
                message="Batch size",
                default=str(defaults.get("batch_size", 8)),
                validate=lambda _, x: x.isdigit() and 1 <= int(x) <= 128
            ),
            inquirer.Text(
                'learning_rate',
                message="Learning rate",
                default=str(defaults.get("learning_rate", 2e-5)),
                validate=lambda _, x: self._validate_float(x, 1e-7, 1e-2)
            )
        ]
        
        # Add LoRA-specific parameters if using LoRA/QLoRA
        if approach in ["lora", "qlora"]:
            questions.append(
                inquirer.Text(
                    'lora_rank',
                    message="LoRA rank",
                    default=str(defaults.get("lora_rank", 8)),
                    validate=lambda _, x: x.isdigit() and 1 <= int(x) <= 128
                )
            )
            
            questions.append(
                inquirer.Text(
                    'lora_alpha',
                    message="LoRA alpha",
                    default=str(defaults.get("lora_alpha", 16)),
                    validate=lambda _, x: x.isdigit() and 1 <= int(x) <= 128
                )
            )
        
        # Advanced options
        include_advanced = inquirer.confirm(
            message="Configure advanced options?",
            default=False
        )
        
        if include_advanced:
            advanced_questions = [
                inquirer.Text(
                    'warmup_steps',
                    message="Warmup steps",
                    default=str(defaults.get("warmup_steps", 100)),
                    validate=lambda _, x: x.isdigit() and 0 <= int(x) <= 1000
                ),
                inquirer.Text(
                    'weight_decay',
                    message="Weight decay",
                    default=str(defaults.get("weight_decay", 0.01)),
                    validate=lambda _, x: self._validate_float(x, 0, 1)
                ),
                inquirer.Confirm(
                    'gradient_checkpointing',
                    message="Use gradient checkpointing (saves memory)",
                    default=defaults.get("gradient_checkpointing", True)
                )
            ]
            questions.extend(advanced_questions)
        
        # Get answers and convert to appropriate types
        answers = inquirer.prompt(questions)
        if not answers:
            raise KeyboardInterrupt
            
        # Convert string values to appropriate types
        params = {
            "epochs": int(answers["epochs"]),
            "batch_size": int(answers["batch_size"]),
            "learning_rate": float(answers["learning_rate"])
        }
        
        # Add LoRA parameters if applicable
        if approach in ["lora", "qlora"]:
            params["lora_rank"] = int(answers["lora_rank"])
            params["lora_alpha"] = int(answers["lora_alpha"])
        
        # Add advanced parameters if configured
        if include_advanced:
            params["warmup_steps"] = int(answers["warmup_steps"])
            params["weight_decay"] = float(answers["weight_decay"])
            params["gradient_checkpointing"] = answers["gradient_checkpointing"]
            
        # Copy any other parameters from defaults that weren't explicitly set
        for key, value in defaults.items():
            if key not in params:
                params[key] = value
        
        return params
    
    def confirm_deletion(self, config_name: str) -> bool:
        """Confirm deletion of a configuration"""
        return inquirer.confirm(
            message=f"Are you sure you want to delete configuration '{config_name}'?",
            default=False
        )
    
    def get_import_path(self) -> Optional[str]:
        """Get path to import configuration from"""
        questions = [
            inquirer.Text(
                'import_path',
                message="Enter path to configuration file",
                validate=lambda _, x: Path(x).exists() and Path(x).is_file()
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['import_path'] if answers else None
    
    def get_export_path(self, config_name: str) -> Optional[str]:
        """Get path to export configuration to"""
        # Create a default filename based on the config name
        default_path = f"exported_{config_name.replace(' ', '_')}.json"
        
        questions = [
            inquirer.Text(
                'export_path',
                message="Enter path to save configuration file",
                default=default_path
            )
        ]
        
        answers = inquirer.prompt(questions)
        return answers['export_path'] if answers else None
    
    def _run_local_training(self, config: Dict[str, Any], model_manager: Any, metrics_manager: Any, 
                         output_dir: Path, run_id: str) -> None:
        """Fallback method to run training locally without Kubernetes"""
        # Create display for training progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            refresh_per_second=10
        ) as progress:
            self.console.print(f"\n[bold]Starting training on model: {config['model_id']}[/]")
            self.console.print(f"[green]Output directory: {str(output_dir)}[/]")
            
            # Setup training progress display
            local_training_task = progress.add_task("Initializing training...", total=100)
            metrics = {
                "loss": 0.0,
                "learning_rate": 0.0,
                "epochs_completed": 0,
                "steps_completed": 0,
                "total_steps": 100
            }
            
            # Record start time
            start_time = time.time()
            
            # Define callbacks for training
            def on_start():
                progress.update(local_training_task, description="Training started")
            
            def on_epoch_begin(epoch, total_epochs, steps):
                progress.update(local_training_task, description=f"Epoch {epoch}/{total_epochs}")
                metrics["total_steps"] = steps
            
            def on_step(step, total_steps, loss, lr):
                progress.update(
                    local_training_task, 
                    description=f"Epoch {metrics['epochs_completed'] + 1} - Step {step}/{total_steps}",
                    completed=int(100 * step / total_steps)
                )
                metrics["loss"] = loss
                metrics["learning_rate"] = lr
                metrics["steps_completed"] = step
            
            def on_epoch_end(epoch, epoch_metrics):
                self._update_epoch_end(metrics_manager, run_id, metrics, epoch, epoch_metrics)
            
            def on_complete(model_path):
                progress.update(local_training_task, description="Training complete!", completed=100)
                self._handle_training_complete(metrics_manager, run_id, model_path, start_time, output_dir)
            
            # Setup callbacks dict
            callbacks = {
                "on_start": on_start,
                "on_epoch_begin": on_epoch_begin,
                "on_step": on_step,
                "on_epoch_end": on_epoch_end,
                "on_complete": on_complete
            }
            
            # Run training with callbacks
            model_manager.train_model(config, str(output_dir), callbacks)

    def _create_progress_display(self, progress, metrics):
        """Create a rich layout for displaying training progress"""
        layout = Layout()
        
        # Header section
        header = Panel(
            f"[bold]Training model: {metrics.get('model_name', 'Unknown')}[/]",
            border_style="green"
        )
        
        # Metrics section
        metrics_table = Table(box=box.SIMPLE)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        
        # Add available metrics
        metrics_table.add_row("Current loss", f"{metrics.get('loss', 0.0):.4f}")
        metrics_table.add_row("Learning rate", f"{metrics.get('learning_rate', 0.0):.6f}")
        metrics_table.add_row("Epochs completed", f"{metrics.get('epochs_completed', 0)}")
        metrics_table.add_row("Steps completed", f"{metrics.get('steps_completed', 0)}/{metrics.get('total_steps', 0)}")
        
        # Create layout
        layout.split(
            Layout(header, size=3),
            Layout(Align.center(metrics_table), size=10)
        )
        
        return layout

    def get_training_config(self, 
                            existing_configs: List[Dict[str, Any]], 
                            available_models: List[Dict[str, Any]],
                            available_datasets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get training configuration from user"""
        try:
            # First ask if user wants to use an existing config
            if existing_configs:
                use_existing = inquirer.confirm("Would you like to use an existing training configuration?", default=False)
                if use_existing:
                    config_choices = [(f"{c['name']} ({c['model']})", c) for c in existing_configs]
                    config_choice = inquirer.prompt([
                        inquirer.List(
                            'config',
                            message="Select a configuration",
                            choices=config_choices
                        )
                    ])
                    
                    if config_choice:
                        return config_choice['config']
            
            # Create new configuration
            questions = []
            
            # Select model
            if available_models:
                model_choices = [(f"{m['name']} ({m['type']})", m['id']) for m in available_models]
                questions.append(
                    inquirer.List(
                        'model_id',
                        message="Select a model to fine-tune",
                        choices=model_choices
                    )
                )
            else:
                self.console.print("[red]No models available for fine-tuning[/]")
                return None
            
            # Select dataset
            if available_datasets:
                dataset_choices = [
                    (f"{d['name']} ({d['samples']} samples, {d['format']} - {d['source']})", d['id']) 
                    for d in available_datasets
                ]
                questions.append(
                    inquirer.List(
                        'dataset_id',
                        message="Select a dataset for training",
                        choices=dataset_choices
                    )
                )
            else:
                self.console.print("[red]No datasets available for training[/]")
                return None
            
            # Get training parameters
            questions.extend([
                inquirer.Text(
                    'name',
                    message="Enter a name for this training run",
                    validate=lambda _, x: bool(x.strip())
                ),
                inquirer.Text(
                    'description',
                    message="Enter a description (optional)",
                    default=""
                ),
                inquirer.Text(
                    'epochs',
                    message="Number of epochs",
                    default="3",
                    validate=lambda _, x: x.isdigit() and int(x) > 0
                ),
                inquirer.Text(
                    'batch_size',
                    message="Batch size",
                    default="4",
                    validate=lambda _, x: x.isdigit() and int(x) > 0
                ),
                inquirer.Text(
                    'learning_rate',
                    message="Learning rate",
                    default="2e-5",
                    validate=lambda _, x: float(x) > 0
                ),
                inquirer.Confirm(
                    'save_config',
                    message="Would you like to save this configuration for future use?",
                    default=False
                )
            ])
            
            answers = inquirer.prompt(questions)
            if not answers:
                return None
            
            # Create configuration
            config = {
                'name': answers['name'],
                'description': answers['description'],
                'model_id': answers['model_id'],
                'dataset_id': answers['dataset_id'],
                'training_params': {
                    'epochs': int(answers['epochs']),
                    'batch_size': int(answers['batch_size']),
                    'learning_rate': float(answers['learning_rate'])
                },
                'save_config': answers['save_config']
            }
            
            return config
            
        except Exception as e:
            self.console.print(f"[red]Error getting training configuration: {str(e)}[/]")
            return None

    def confirm_training_config(self, config: Dict[str, Any]) -> bool:
        """Display and confirm training configuration"""
        try:
            self.console.print("\n[bold]Training Configuration Summary:[/]")
            
            # Create a table for better visualization
            table = Table(box=box.ROUNDED)
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            
            # Basic info
            table.add_row("Name", config['name'])
            if config.get('description'):
                table.add_row("Description", config['description'])
            
            # Model info
            table.add_row("Model ID", config['model_id'])
            
            # Dataset info
            dataset_info = config.get('dataset_info', {})
            table.add_row("Dataset", f"{dataset_info.get('name', 'Unknown')} ({dataset_info.get('format', 'Unknown')})")
            table.add_row("Samples", str(dataset_info.get('samples', 'Unknown')))
            
            # Training parameters
            params = config.get('training_params', {})
            table.add_row("Epochs", str(params.get('epochs', 'Not specified')))
            table.add_row("Batch Size", str(params.get('batch_size', 'Not specified')))
            table.add_row("Learning Rate", str(params.get('learning_rate', 'Not specified')))
            
            # Kubernetes info if applicable
            if config.get('use_kubernetes'):
                table.add_row("Execution", "[bold blue]Kubernetes[/]")
                if 'kubernetes_config' in config:
                    k8s_config = config['kubernetes_config']
                    table.add_row("K8s Namespace", k8s_config.get('namespace', 'default'))
                    table.add_row("K8s Resources", f"CPU: {k8s_config.get('cpu', '2')}, Memory: {k8s_config.get('memory', '8Gi')}")
            else:
                table.add_row("Execution", "Local")
            
            self.console.print(table)
            
            # Ask for confirmation
            return inquirer.confirm("Proceed with this configuration?", default=True)
            
        except Exception as e:
            self.console.print(f"[red]Error displaying configuration: {str(e)}[/]")
            return False