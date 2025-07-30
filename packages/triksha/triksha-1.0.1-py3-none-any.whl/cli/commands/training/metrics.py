"""Training metrics management"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from rich.console import Console
import kubernetes
from kubernetes import client, config

class TrainingMetricsManager:
    """Manages training metrics and history"""
    
    def __init__(self, db, config):
        """Initialize metrics manager"""
        self.db = db
        self.config = config
        self.console = Console()
        
        # Ensure the metrics table exists
        self._create_metrics_table()
        
        # Try to initialize Kubernetes client
        try:
            config.load_kube_config()
            self.k8s_api = client.CoreV1Api()
            self.k8s_available = True
        except:
            self.k8s_available = False
    
    def _create_metrics_table(self) -> None:
        """Create the metrics table if it doesn't exist"""
        try:
            cursor = self.db.cursor()
            
            # Create training runs table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_runs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                model_id TEXT NOT NULL,
                approach TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT DEFAULT 'in_progress',
                duration_seconds INTEGER,
                model_path TEXT,
                config TEXT,
                kubernetes_pod TEXT,
                kubernetes_status TEXT
            )
            ''')
            
            # Create training metrics table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                loss REAL,
                learning_rate REAL,
                timestamp REAL,
                metrics TEXT,
                FOREIGN KEY (run_id) REFERENCES training_runs(id)
            )
            ''')
            
            self.db.commit()
        
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not create metrics tables: {str(e)}[/]")
    
    def register_training_run(self, run_config: Dict[str, Any]) -> str:
        """Register a new training run"""
        try:
            # Get key information
            run_id = run_config.get("id", str(datetime.now().timestamp()))
            name = run_config.get("name", f"Training_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            model_id = run_config.get("model_id", "unknown")
            approach = run_config.get("approach", "unknown")
            
            # Insert into database
            cursor = self.db.cursor()
            cursor.execute('''
            INSERT INTO training_runs 
            (id, name, model_id, approach, created_at, status, config) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_id, 
                name, 
                model_id, 
                approach, 
                datetime.now().isoformat(),
                "in_progress",
                json.dumps(run_config)
            ))
            
            self.db.commit()
            return run_id
        
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not register training run: {str(e)}[/]")
            return str(datetime.now().timestamp())
    
    def save_training_metrics(self, run_id: str, metrics: Dict[str, Any]) -> bool:
        """Save metrics for a training run"""
        try:
            epoch = metrics.get("epoch", 0)
            loss = metrics.get("loss", 0.0)
            learning_rate = metrics.get("learning_rate", 0.0)
            timestamp = metrics.get("timestamp", datetime.now().timestamp())
            
            # Extract other metrics
            other_metrics = {k: v for k, v in metrics.items() 
                           if k not in ["epoch", "loss", "learning_rate", "timestamp"]}
            
            cursor = self.db.cursor()
            cursor.execute('''
            INSERT INTO training_metrics
            (run_id, epoch, loss, learning_rate, timestamp, metrics)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                run_id,
                epoch,
                loss,
                learning_rate,
                timestamp,
                json.dumps(other_metrics)
            ))
            
            self.db.commit()
            return True
        
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save metrics: {str(e)}[/]")
            return False
    
    def complete_training_run(self, run_id: str, model_path: str, duration_seconds: float) -> bool:
        """Mark a training run as complete"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
            UPDATE training_runs
            SET status = ?, completed_at = ?, model_path = ?, duration_seconds = ?
            WHERE id = ?
            ''', (
                "completed",
                datetime.now().isoformat(),
                model_path,
                int(duration_seconds),
                run_id
            ))
            
            self.db.commit()
            return True
        
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not complete training run: {str(e)}[/]")
            return False
    
    def get_training_runs(self, include_kubernetes: bool = True) -> List[Dict[str, Any]]:
        """Get a list of training runs"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
            SELECT id, name, model_id, approach, created_at, completed_at, status, duration_seconds, model_path
            FROM training_runs
            ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            
            runs = []
            for row in rows:
                run = {
                    "id": row[0],
                    "name": row[1],
                    "model_id": row[2],
                    "approach": row[3],
                    "created_at": row[4],
                    "completed_at": row[5],
                    "status": row[6],
                    "duration_seconds": row[7],
                    "model_path": row[8]
                }
                runs.append(run)
                
            if include_kubernetes and self.k8s_available:
                for run in runs:
                    if run.get('kubernetes_pod'):
                        # Update status before returning
                        self.update_kubernetes_status(run['id'])
            
            # Fetch updated records
            cursor.execute('''
            SELECT id, name, model_id, approach, created_at, completed_at, status, duration_seconds, model_path
            FROM training_runs
            ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            
            for row in rows:
                run = {
                    "id": row[0],
                    "name": row[1],
                    "model_id": row[2],
                    "approach": row[3],
                    "created_at": row[4],
                    "completed_at": row[5],
                    "status": row[6],
                    "duration_seconds": row[7],
                    "model_path": row[8]
                }
                runs.append(run)
            
            return runs
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not retrieve training runs: {str(e)}[/]")
            return []
    
    def get_detailed_metrics(self, run_id: str) -> Dict[str, Any]:
        """Get detailed metrics for a training run"""
        try:
            # First get the run details
            cursor = self.db.cursor()
            cursor.execute('''
            SELECT id, name, model_id, approach, created_at, completed_at, status, duration_seconds, model_path, config
            FROM training_runs
            WHERE id = ?
            ''', (run_id,))
            
            row = cursor.fetchone()
            if not row:
                return {"error": "Run not found"}
                
            run_info = {
                "id": row[0],
                "name": row[1],
                "model_id": row[2],
                "approach": row[3],
                "created_at": row[4],
                "completed_at": row[5],
                "status": row[6],
                "duration_seconds": row[7],
                "model_path": row[8]
            }
            
            # Try to parse the config
            try:
                config = json.loads(row[9]) if row[9] else {}
                run_info["config"] = config
            except:
                run_info["config"] = {}
            
            # Now get the metrics for each epoch
            cursor.execute('''
            SELECT epoch, loss, learning_rate, timestamp, metrics
            FROM training_metrics
            WHERE run_id = ?
            ORDER BY epoch ASC, timestamp ASC
            ''', (run_id,))
            
            metrics_rows = cursor.fetchall()
            
            # Process the metrics
            epochs = []
            additional_metrics = set()
            
            for metrics_row in metrics_rows:
                epoch_data = {
                    "epoch": metrics_row[0],
                    "loss": metrics_row[1],
                    "learning_rate": metrics_row[2],
                    "timestamp": metrics_row[3]
                }
                
                # Add other metrics if available
                try:
                    other_metrics = json.loads(metrics_row[4]) if metrics_row[4] else {}
                    epoch_data.update(other_metrics)
                    
                    # Track all the additional metric names we've seen
                    additional_metrics.update(other_metrics.keys())
                except:
                    pass
                    
                epochs.append(epoch_data)
            
            # Calculate overall metrics
            if epochs:
                final_epoch = epochs[-1]
                final_loss = final_epoch.get("loss", 0.0)
                run_info["final_loss"] = final_loss
                
                # Calculate average loss across epochs
                total_loss = sum(epoch.get("loss", 0.0) for epoch in epochs)
                run_info["avg_loss"] = total_loss / len(epochs) if epochs else 0.0
            
            # Combine into a comprehensive result
            return {
                "run": run_info,
                "epochs": epochs,
                "additional_metrics": list(additional_metrics)
            }
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not retrieve detailed metrics: {str(e)}[/]")
            return {"error": str(e)}
    
    def export_metrics(self, run_id: str, output_path: str) -> bool:
        """Export metrics for a run to a file"""
        try:
            metrics = self.get_detailed_metrics(run_id)
            
            with open(output_path, 'w') as f:
                json.dump(metrics, f, indent=2)
                
            self.console.print(f"[green]Metrics exported to: {output_path}[/]")
            return True
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not export metrics: {str(e)}[/]")
            return False
    
    def delete_run(self, run_id: str) -> bool:
        """Delete a training run and its metrics"""
        try:
            # First delete the metrics
            cursor = self.db.cursor()
            cursor.execute('''
            DELETE FROM training_metrics
            WHERE run_id = ?
            ''', (run_id,))
            
            # Then delete the run
            cursor.execute('''
            DELETE FROM training_runs
            WHERE id = ?
            ''', (run_id,))
            
            self.db.commit()
            self.console.print(f"[green]Training run {run_id} deleted successfully[/]")
            return True
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not delete training run: {str(e)}[/]")
            return False
    
    def update_run_status(self, run_id: str, status: str, additional_data: Dict[str, Any] = None) -> bool:
        """Update the status of a training run and add additional metadata
        
        Args:
            run_id: ID of the training run
            status: New status (in_progress, completed, failed, paused)
            additional_data: Additional data to store with the run
            
        Returns:
            bool: Success status
        """
        try:
            cursor = self.db.cursor()
            
            # Start building the query and parameters
            query_parts = ["UPDATE training_runs SET status = ?"]
            query_params = [status]
            
            # Add additional data fields to the update query if provided
            if additional_data:
                for key, value in additional_data.items():
                    # We need to get the current config first, modify it, and update it
                    if key == "config":
                        # Skip config for now, we'll handle it separately
                        continue
                    else:
                        # Add column to update if it exists
                        cursor.execute(f"PRAGMA table_info(training_runs)")
                        columns = [info[1] for info in cursor.fetchall()]
                        
                        if key in columns:
                            query_parts.append(f"{key} = ?")
                            query_params.append(value)
                        else:
                            self.console.print(f"[yellow]Warning: Column '{key}' not found in training_runs table[/]")
            
            # Construct the final query and execute
            query = f"{' , '.join(query_parts)} WHERE id = ?"
            query_params.append(run_id)
            
            cursor.execute(query, query_params)
            
            # If we have kubernetes related data, store it in the config
            kubernetes_data = {k: v for k, v in additional_data.items() if k.startswith("kubernetes_")} if additional_data else {}
            
            if kubernetes_data:
                # Get current config
                cursor.execute("SELECT config FROM training_runs WHERE id = ?", (run_id,))
                result = cursor.fetchone()
                
                if result and result[0]:
                    try:
                        config = json.loads(result[0])
                        
                        # Update with kubernetes data
                        for k, v in kubernetes_data.items():
                            config[k] = v
                            
                        # Save updated config
                        cursor.execute("UPDATE training_runs SET config = ? WHERE id = ?", 
                                      (json.dumps(config), run_id))
                    except json.JSONDecodeError:
                        self.console.print(f"[yellow]Warning: Could not parse config JSON for run {run_id}[/]")
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not update run status: {str(e)}[/]")
            return False
    
    def pause_training_run(self, run_id: str) -> bool:
        """Pause a running training job on Kubernetes
        
        Args:
            run_id: ID of the training run
            
        Returns:
            bool: Success status
        """
        try:
            # First, update status in database
            success = self.update_run_status(run_id, "paused")
            
            if not success:
                return False
                
            # Get pod name from run info
            cursor = self.db.cursor()
            cursor.execute("SELECT config FROM training_runs WHERE id = ?", (run_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                self.console.print(f"[yellow]Warning: Could not find configuration for run {run_id}[/]")
                return False
                
            try:
                config = json.loads(result[0])
                pod_name = config.get("kubernetes_pod")
                
                if not pod_name:
                    self.console.print(f"[yellow]Warning: No Kubernetes pod found for run {run_id}[/]")
                    return False
                    
                # Try to pause the pod by setting a label
                try:
                    k8s_api = client.CoreV1Api()
                    
                    # Add pause label to pod
                    body = {
                        "metadata": {
                            "labels": {
                                "dravik.ai/paused": "true"
                            }
                        }
                    }
                    
                    k8s_api.patch_namespaced_pod(name=pod_name, namespace="default", body=body)
                    
                    # We'll have a custom controller watching for this label to handle the actual pause
                    # through a sidecar container or similar mechanism
                    
                    return True
                    
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not pause Kubernetes pod: {str(e)}[/]")
                    return False
                    
            except json.JSONDecodeError:
                self.console.print(f"[yellow]Warning: Could not parse config JSON for run {run_id}[/]")
                return False
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not pause training run: {str(e)}[/]")
            return False
    
    def resume_training_run(self, run_id: str) -> bool:
        """Resume a paused training job on Kubernetes
        
        Args:
            run_id: ID of the training run
            
        Returns:
            bool: Success status
        """
        try:
            # First, update status in database
            success = self.update_run_status(run_id, "running")
            
            if not success:
                return False
                
            # Get pod name from run info
            cursor = self.db.cursor()
            cursor.execute("SELECT config FROM training_runs WHERE id = ?", (run_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                self.console.print(f"[yellow]Warning: Could not find configuration for run {run_id}[/]")
                return False
                
            try:
                config = json.loads(result[0])
                pod_name = config.get("kubernetes_pod")
                
                if not pod_name:
                    self.console.print(f"[yellow]Warning: No Kubernetes pod found for run {run_id}[/]")
                    return False
                    
                # Try to resume the pod by removing the pause label
                try:
                    k8s_api = client.CoreV1Api()
                    
                    # Remove pause label from pod
                    body = {
                        "metadata": {
                            "labels": {
                                "dravik.ai/paused": None  # Remove the label
                            }
                        }
                    }
                    
                    k8s_api.patch_namespaced_pod(name=pod_name, namespace="default", body=body)
                    
                    # We'll have a custom controller watching for this label change to handle the actual resume
                    
                    return True
                    
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Could not resume Kubernetes pod: {str(e)}[/]")
                    return False
                    
            except json.JSONDecodeError:
                self.console.print(f"[yellow]Warning: Could not parse config JSON for run {run_id}[/]")
                return False
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not resume training run: {str(e)}[/]")
            return False
    
    def update_kubernetes_status(self, run_id: str) -> None:
        """Update status of Kubernetes training job"""
        if not self.k8s_available:
            return
            
        cursor = self.db.cursor()
        
        # Get the pod name
        cursor.execute('SELECT kubernetes_pod FROM training_runs WHERE id = ?', (run_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            return
            
        pod_name = result[0]
        
        try:
            # Get pod status
            pod = self.k8s_api.read_namespaced_pod(name=pod_name, namespace="default")
            status = pod.status.phase
            
            # Map Kubernetes status to our status
            status_map = {
                'Pending': 'initializing',
                'Running': 'in_progress',
                'Succeeded': 'completed',
                'Failed': 'failed'
            }
            
            our_status = status_map.get(status, status.lower())
            
            # Update the database
            cursor.execute('''
            UPDATE training_runs 
            SET status = ?, kubernetes_status = ?
            WHERE id = ?
            ''', (our_status, status, run_id))
            
            self.db.commit()
            
        except Exception as e:
            print(f"Error updating Kubernetes status: {e}")
