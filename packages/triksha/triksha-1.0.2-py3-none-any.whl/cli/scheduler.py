import os
import json
import sys
from datetime import datetime, timedelta
import time
import subprocess
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(Path.home() / "dravik" / "logs" / "scheduler.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("dravik.scheduler")

class ScheduledTask:
    """A scheduled task for running benchmarks."""
    
    def __init__(
        self, 
        task_id: str,
        name: str,
        command: str,
        schedule_time: datetime,
        recurring: bool = False,
        recurring_interval: Optional[int] = None,  # in days
        recurring_unit: str = "days",  # days, hours, minutes
        params: Optional[Dict[str, Any]] = None,
        last_run: Optional[datetime] = None,
        status: str = "scheduled"
    ):
        """Initialize a scheduled task.
        
        Args:
            task_id: Unique identifier for the task
            name: Display name for the task
            command: Command to run
            schedule_time: Time to run the task
            recurring: Whether the task should recur
            recurring_interval: Interval for recurring tasks
            recurring_unit: Unit for recurring interval (days, hours, minutes)
            params: Additional parameters for the command
            last_run: Last time the task was run
            status: Status of the task (scheduled, running, completed, failed)
        """
        self.task_id = task_id
        self.name = name
        self.command = command
        self.schedule_time = schedule_time
        self.recurring = recurring
        self.recurring_interval = recurring_interval
        self.recurring_unit = recurring_unit
        self.params = params or {}
        self.last_run = last_run
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "task_id": self.task_id,
            "name": self.name,
            "command": self.command,
            "schedule_time": self.schedule_time.isoformat(),
            "recurring": self.recurring,
            "recurring_interval": self.recurring_interval,
            "recurring_unit": self.recurring_unit,
            "params": self.params,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledTask':
        """Create a task from a dictionary.
        
        Args:
            data: Dictionary representation of the task
            
        Returns:
            ScheduledTask instance
        """
        return cls(
            task_id=data.get("task_id", ""),
            name=data.get("name", ""),
            command=data.get("command", ""),
            schedule_time=datetime.fromisoformat(data.get("schedule_time", datetime.now().isoformat())),
            recurring=data.get("recurring", False),
            recurring_interval=data.get("recurring_interval"),
            recurring_unit=data.get("recurring_unit", "days"),
            params=data.get("params", {}),
            last_run=datetime.fromisoformat(data.get("last_run")) if data.get("last_run") else None,
            status=data.get("status", "scheduled")
        )
    
    def is_due(self) -> bool:
        """Check if the task is due to run.
        
        Returns:
            True if the task is due, False otherwise
        """
        now = datetime.now()
        return now >= self.schedule_time and self.status == "scheduled"
    
    def update_next_run(self):
        """Update the next run time for recurring tasks."""
        if not self.recurring:
            self.status = "completed"
            return
        
        # Calculate next run time based on the last run and interval
        if self.recurring_unit == "days":
            self.schedule_time = datetime.now() + timedelta(days=self.recurring_interval)
        elif self.recurring_unit == "hours":
            self.schedule_time = datetime.now() + timedelta(hours=self.recurring_interval)
        elif self.recurring_unit == "minutes":
            self.schedule_time = datetime.now() + timedelta(minutes=self.recurring_interval)
        
        self.last_run = datetime.now()
        self.status = "scheduled"


class SchedulerService:
    """Service for scheduling and running benchmarks."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the scheduler service.
        
        Args:
            console: Rich console for output messages
        """
        self.console = console or Console()
        self.scheduler_dir = Path.home() / "dravik" / "scheduler"
        self.scheduler_dir.mkdir(exist_ok=True, parents=True)
        self.tasks_file = self.scheduler_dir / "tasks.json"
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Create logs directory
        logs_dir = Path.home() / "dravik" / "logs"
        logs_dir.mkdir(exist_ok=True, parents=True)
        
        # Load existing tasks
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from the tasks file."""
        if not self.tasks_file.exists():
            return
        
        try:
            with open(self.tasks_file, 'r') as f:
                tasks_data = json.load(f)
            
            self.tasks = {}
            for task_id, task_data in tasks_data.items():
                self.tasks[task_id] = ScheduledTask.from_dict(task_data)
            
            logger.info(f"Loaded {len(self.tasks)} tasks from {self.tasks_file}")
        except Exception as e:
            logger.error(f"Error loading tasks: {str(e)}")
    
    def save_tasks(self):
        """Save tasks to the tasks file."""
        try:
            tasks_data = {}
            for task_id, task in self.tasks.items():
                tasks_data[task_id] = task.to_dict()
            
            with open(self.tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2, default=str)
            
            logger.info(f"Saved {len(self.tasks)} tasks to {self.tasks_file}")
        except Exception as e:
            logger.error(f"Error saving tasks: {str(e)}")
    
    def add_task(self, task: ScheduledTask) -> bool:
        """Add a new task to the scheduler.
        
        Args:
            task: Task to add
            
        Returns:
            True if the task was added successfully, False otherwise
        """
        try:
            if task.task_id in self.tasks:
                logger.warning(f"Task with ID {task.task_id} already exists, overwriting")
            
            self.tasks[task.task_id] = task
            self.save_tasks()
            logger.info(f"Added task {task.task_id}: {task.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the scheduler.
        
        Args:
            task_id: ID of the task to remove
            
        Returns:
            True if the task was removed successfully, False otherwise
        """
        try:
            if task_id not in self.tasks:
                logger.warning(f"Task with ID {task_id} does not exist")
                return False
            
            del self.tasks[task_id]
            self.save_tasks()
            logger.info(f"Removed task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing task: {str(e)}")
            return False
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks.
        
        Returns:
            List of tasks as dictionaries
        """
        return [task.to_dict() for task in self.tasks.values()]
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            Task object or None if not found
        """
        return self.tasks.get(task_id)
    
    def run_task(self, task: ScheduledTask) -> bool:
        """Run a task.
        
        Args:
            task: Task to run
            
        Returns:
            True if the task was run successfully, False otherwise
        """
        try:
            logger.info(f"Running task {task.task_id}: {task.name}")
            task.status = "running"
            self.save_tasks()
            
            # Build command to run task
            cmd = [sys.executable, "-m", "cli.dravik_cli"]
            cmd.extend(task.command.split())
            
            # Add parameters
            for key, value in task.params.items():
                # Convert underscore to hyphen for command line arguments
                formatted_key = key.replace('_', '-')
                
                if isinstance(value, bool) and value:
                    cmd.append(f"--{formatted_key}")
                elif value is not None and value != "":
                    cmd.append(f"--{formatted_key}={value}")
            
            # Run the command in background without displaying output to the user interface
            logger.info(f"Running command in background: {' '.join(cmd)}")
            
            # Create logs directory for output
            logs_dir = Path.home() / "dravik" / "logs" / "scheduled_tasks"
            logs_dir.mkdir(exist_ok=True, parents=True)
            
            # Create log files for stdout and stderr
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stdout_log = logs_dir / f"{task.task_id}_{timestamp}_stdout.log"
            stderr_log = logs_dir / f"{task.task_id}_{timestamp}_stderr.log"
            
            # Open log files
            with open(stdout_log, 'w') as stdout_file, open(stderr_log, 'w') as stderr_file:
                # Start the process completely detached from the current process
                if sys.platform == 'win32':
                    # For Windows
                    from subprocess import CREATE_NO_WINDOW
                    process = subprocess.Popen(
                        cmd,
                        stdout=stdout_file,
                        stderr=stderr_file,
                        creationflags=CREATE_NO_WINDOW,
                        cwd=os.getcwd()
                    )
                else:
                    # For Unix-like systems
                    process = subprocess.Popen(
                        cmd,
                        stdout=stdout_file,
                        stderr=stderr_file,
                        start_new_session=True,  # Detach from parent process
                        cwd=os.getcwd()
                    )
            
            # Don't wait for the process to complete - let it run in background
            # We'll mark the task as running and update its status later
            logger.info(f"Task {task.task_id} started in background, logging to {stdout_log} and {stderr_log}")
            
            # Store the process ID and log paths for future reference
            task.params['process_id'] = process.pid
            task.params['stdout_log'] = str(stdout_log)
            task.params['stderr_log'] = str(stderr_log)
            task.params['start_time'] = datetime.now().isoformat()
            task.last_run = datetime.now()
            self.save_tasks()
            
            # Start a background thread to monitor this specific process
            monitor_thread = threading.Thread(
                target=self._monitor_task_process,
                args=(task, process),
                daemon=True
            )
            monitor_thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Error running task {task.task_id}: {str(e)}")
            task.status = "failed"
            self.save_tasks()
            return False
    
    def _monitor_task_process(self, task: ScheduledTask, process):
        """Monitor a specific task process and update its status when complete.
        
        Args:
            task: The task being monitored
            process: The subprocess.Popen process object
        """
        try:
            # Wait for the process to complete with a timeout
            try:
                process.wait(timeout=3600)  # 1 hour timeout, adjust as needed
            except subprocess.TimeoutExpired:
                logger.warning(f"Task {task.task_id} is taking longer than expected")
                return  # Let the normal status checking handle this case
                
            # Process completed, check return code
            return_code = process.returncode
            
            if return_code == 0:
                logger.info(f"Task {task.task_id} completed successfully with return code 0")
                task.status = "completed"
            else:
                logger.error(f"Task {task.task_id} failed with return code {return_code}")
                task.status = "failed"
            
            # Update task for next run if recurring
            task.update_next_run()
            self.save_tasks()
            
        except Exception as e:
            logger.error(f"Error monitoring task {task.task_id}: {str(e)}")
            task.status = "unknown"
            self.save_tasks()
    
    def start(self):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Check for due tasks
                for task_id, task in list(self.tasks.items()):
                    if task.is_due():
                        logger.info(f"Task {task_id} is due, running")
                        # Run the task in a separate thread to avoid blocking the scheduler
                        threading.Thread(target=self.run_task, args=(task,)).start()
                
                # Check status of running tasks
                self._check_running_tasks()
                
                # Sleep for a short time
                time.sleep(10)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(10)
        
        logger.info("Scheduler loop stopped")

    def _check_running_tasks(self):
        """Check the status of running tasks and update them."""
        for task_id, task in list(self.tasks.items()):
            if task.status == "running" and "process_id" in task.params:
                try:
                    # Try to get process status
                    pid = task.params.get("process_id")
                    
                    # Check if process exists
                    if pid is None:
                        continue
                    
                    # Convert pid to int
                    pid = int(pid)
                    
                    # Calculate run time if start_time is present
                    if "start_time" in task.params:
                        try:
                            start_time = datetime.fromisoformat(task.params["start_time"])
                            run_time = datetime.now() - start_time
                            # If running longer than 6 hours (adjust as needed), check if still alive
                            if run_time > timedelta(hours=6):
                                logger.warning(f"Task {task_id} has been running for {run_time}")
                        except Exception as e:
                            logger.warning(f"Could not calculate run time for task {task_id}: {e}")
                    
                    # Check if process is still running
                    process_running = True
                    try:
                        # This will raise an exception if the process doesn't exist
                        if sys.platform == 'win32':
                            # Windows
                            import ctypes
                            kernel32 = ctypes.windll.kernel32
                            handle = kernel32.OpenProcess(1, False, pid)
                            if handle == 0:
                                process_running = False
                            else:
                                kernel32.CloseHandle(handle)
                        else:
                            # Unix-like
                            import os
                            os.kill(pid, 0)  # This sends signal 0, which doesn't actually kill the process
                    except (OSError, ProcessLookupError):
                        # Process doesn't exist
                        process_running = False
                    except Exception as e:
                        logger.error(f"Error checking process {pid} status: {str(e)}")
                        continue
                    
                    if not process_running:
                        # Check how long since the task started
                        current_time = datetime.now()
                        time_since_start = None
                        if "start_time" in task.params:
                            try:
                                start_time = datetime.fromisoformat(task.params["start_time"])
                                time_since_start = current_time - start_time
                            except Exception as e:
                                logger.warning(f"Could not parse start time for task {task_id}: {e}")
                        
                        # If the task just started and quickly disappeared, it probably failed
                        if time_since_start and time_since_start < timedelta(minutes=1):
                            logger.error(f"Task {task_id} failed immediately after starting")
                            task.status = "failed"
                        else:
                            # Process has completed, check log files for errors
                            stderr_log = task.params.get("stderr_log")
                            if stderr_log and Path(stderr_log).exists() and Path(stderr_log).stat().st_size > 0:
                                # If stderr log has content, consider it a failure
                                with open(stderr_log, 'r') as f:
                                    error_content = f.read()
                                logger.error(f"Task {task_id} failed: {error_content[:500]}...")
                                task.status = "failed"
                            else:
                                # Otherwise, mark as completed
                                logger.info(f"Task {task_id} completed successfully")
                                task.status = "completed"
                        
                        # Update task for next run if recurring
                        task.update_next_run()
                        self.save_tasks()
                
                except Exception as e:
                    logger.error(f"Error checking task {task_id} status: {str(e)}")
                    # If we've been having consistent errors checking a task, mark it as unknown status
                    # This is to prevent tasks getting stuck in the "running" state indefinitely
                    if task.params.get("status_check_errors", 0) > 5:
                        logger.warning(f"Too many status check errors for task {task_id}, marking as unknown")
                        task.status = "unknown"
                        task.update_next_run()
                        self.save_tasks()
                    else:
                        # Increment the error counter
                        task.params["status_check_errors"] = task.params.get("status_check_errors", 0) + 1
                        self.save_tasks()
    
    def create_benchmark_task(
        self,
        name: str,
        model_configs: List[Dict[str, Any]],
        prompt_count: int = 10,
        techniques: List[str] = None,
        schedule_time: datetime = None,
        recurring: bool = False,
        recurring_interval: int = 1,
        recurring_unit: str = "days"
    ) -> Optional[str]:
        """Create a scheduled benchmark task.
        
        Args:
            name: Name of the task
            model_configs: List of model configurations to benchmark
            prompt_count: Number of prompts to generate
            techniques: List of techniques to use
            schedule_time: Time to run the task, defaults to now
            recurring: Whether the task should recur
            recurring_interval: Interval for recurring tasks
            recurring_unit: Unit for recurring interval (days, hours, minutes)
            
        Returns:
            Task ID if created successfully, None otherwise
        """
        try:
            import uuid
            task_id = str(uuid.uuid4())
            
            # Default to now if no schedule time provided
            if schedule_time is None:
                schedule_time = datetime.now()
            
            # Save model configs and parameters
            params_file = self.scheduler_dir / f"{task_id}_params.json"
            params = {
                "model_configs": model_configs,
                "prompt_count": prompt_count,
                "techniques": techniques or []
            }
            
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=2)
            
            # Create task
            task = ScheduledTask(
                task_id=task_id,
                name=name,
                command="benchmark scheduled",
                schedule_time=schedule_time,
                recurring=recurring,
                recurring_interval=recurring_interval,
                recurring_unit=recurring_unit,
                params={
                    "params_file": str(params_file),
                    "task_id": task_id
                }
            )
            
            # Add task to scheduler
            if self.add_task(task):
                return task_id
            
            return None
        except Exception as e:
            logger.error(f"Error creating benchmark task: {str(e)}")
            return None

# Global scheduler instance
_scheduler_instance = None

def get_scheduler():
    """Get the global scheduler instance.
    
    Returns:
        SchedulerService instance
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = SchedulerService()
    return _scheduler_instance

# Start the scheduler by default to ensure scheduled jobs run
scheduler = get_scheduler()
scheduler.start()  # Uncommented to enable auto-start 