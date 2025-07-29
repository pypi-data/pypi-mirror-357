#!/usr/bin/env python3
"""
Scheduler service for running tasks in the background.

This module provides a daemon service that runs in the background
and executes scheduled tasks even when the user has exited the CLI tool.
"""
import os
import sys
import time
import logging
import signal
import atexit
from pathlib import Path
import json
import subprocess
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(Path.home() / "dravik" / "logs" / "scheduler_service.log")),
    ]
)
logger = logging.getLogger("dravik.scheduler_service")

# Define daemon directories
DAEMON_DIR = Path.home() / "dravik" / "daemon"
PID_FILE = DAEMON_DIR / "scheduler.pid"
STATUS_FILE = DAEMON_DIR / "scheduler_status.json"

def is_running():
    """Check if the scheduler service is running.
    
    Returns:
        bool: True if running, False otherwise
    """
    if not PID_FILE.exists():
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # Process doesn't exist or invalid PID
        return False

def get_status():
    """Get the status of the scheduler service.
    
    Returns:
        dict: Status information
    """
    if not STATUS_FILE.exists():
        return {
            "running": False,
            "start_time": None,
            "tasks_executed": 0,
            "last_check_time": None
        }
    
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading status file: {e}")
        return {
            "running": False,
            "start_time": None,
            "tasks_executed": 0,
            "last_check_time": None
        }

def update_status(status_data):
    """Update the status file.
    
    Args:
        status_data (dict): Status data to write
    """
    DAEMON_DIR.mkdir(exist_ok=True, parents=True)
    
    try:
        with open(STATUS_FILE, 'w') as f:
            json.dump(status_data, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error updating status file: {e}")

def daemonize():
    """Daemonize the process."""
    # First fork
    try:
        pid = os.fork()
        if pid > 0:
            # Exit first parent
            sys.exit(0)
    except OSError as e:
        logger.error(f"Fork #1 failed: {e}")
        sys.exit(1)
    
    # Decouple from parent environment
    os.chdir('/')
    os.setsid()
    os.umask(0)
    
    # Second fork
    try:
        pid = os.fork()
        if pid > 0:
            # Exit from second parent
            sys.exit(0)
    except OSError as e:
        logger.error(f"Fork #2 failed: {e}")
        sys.exit(1)
    
    # Create daemon directories
    DAEMON_DIR.mkdir(exist_ok=True, parents=True)
    
    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    
    si = open(os.devnull, 'r')
    so = open(str(Path.home() / "dravik" / "logs" / "scheduler_daemon_stdout.log"), 'a+')
    se = open(str(Path.home() / "dravik" / "logs" / "scheduler_daemon_stderr.log"), 'a+')
    
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    
    # Write PID file
    pid = str(os.getpid())
    with open(PID_FILE, 'w+') as f:
        f.write(pid)
    
    # Register cleanup function
    atexit.register(cleanup)
    
    # Initialize status
    update_status({
        "running": True,
        "start_time": datetime.now().isoformat(),
        "tasks_executed": 0,
        "last_check_time": datetime.now().isoformat()
    })

def cleanup():
    """Clean up when the daemon exits."""
    logger.info("Cleaning up daemon resources")
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    
    update_status({
        "running": False,
        "start_time": None,
        "tasks_executed": 0,
        "last_check_time": None
    })

def start_service():
    """Start the scheduler service."""
    # Check if already running
    if is_running():
        print("Scheduler service is already running.")
        return
    
    print("Starting scheduler service...")
    
    # Get the path to the Python executable
    python_executable = sys.executable
    
    # Get the path to this script
    script_path = os.path.abspath(__file__)
    
    # Launch the service process
    subprocess.Popen(
        [python_executable, script_path, "--run-service"],
        start_new_session=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a moment for the service to start
    time.sleep(2)
    
    if is_running():
        print("Scheduler service started successfully.")
    else:
        print("Failed to start scheduler service. Check logs for details.")

def stop_service():
    """Stop the scheduler service."""
    if not is_running():
        print("Scheduler service is not running.")
        return
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        print(f"Stopping scheduler service (PID: {pid})...")
        os.kill(pid, signal.SIGTERM)
        
        # Wait for the service to stop
        for _ in range(5):
            if not is_running():
                print("Scheduler service stopped successfully.")
                return
            time.sleep(1)
        
        # Force kill if still running
        if is_running():
            os.kill(pid, signal.SIGKILL)
            print("Scheduler service forcefully terminated.")
        
    except (OSError, ValueError) as e:
        print(f"Error stopping scheduler service: {e}")
        # Clean up anyway
        if PID_FILE.exists():
            PID_FILE.unlink()

def check_status():
    """Check and print the status of the scheduler service."""
    if is_running():
        status = get_status()
        start_time = datetime.fromisoformat(status.get("start_time")) if status.get("start_time") else None
        last_check = datetime.fromisoformat(status.get("last_check_time")) if status.get("last_check_time") else None
        
        uptime = ""
        if start_time:
            delta = datetime.now() - start_time
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{days}d {hours}h {minutes}m {seconds}s"
        
        print("Scheduler service is running")
        print(f"Uptime: {uptime}")
        print(f"Tasks executed: {status.get('tasks_executed', 0)}")
        print(f"Last check: {last_check.strftime('%Y-%m-%d %H:%M:%S') if last_check else 'Never'}")
    else:
        print("Scheduler service is not running.")
        print("\nTo run scheduled tasks when the CLI is closed, start the daemon:")
        print("  dravik scheduler --action=start-daemon")
        print("\nTo make it start automatically at system boot:")
        print("  dravik scheduler --action=install-service")

def run_service():
    """Run the scheduler service daemon."""
    # Daemonize the process
    daemonize()
    
    logger.info("Scheduler service daemon started")
    
    # Import scheduler module
    try:
        from cli.scheduler import get_scheduler
        scheduler = get_scheduler()
        
        # Scheduler should already be started (we uncommented that line),
        # but let's make sure
        if not getattr(scheduler, 'running', False):
            logger.info("Scheduler not running, starting it explicitly")
            scheduler.start()
        else:
            logger.info("Scheduler already running")
        
        logger.info("Scheduler instance confirmed running within the daemon process")
    except Exception as e:
        logger.error(f"Error importing or starting scheduler: {e}")
        sys.exit(1)
    
    tasks_executed = 0
    last_save_check = datetime.now()
    
    # Set up signal handler
    def handle_signal(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        # Try to stop the scheduler gracefully
        try:
            scheduler.stop()
            logger.info("Scheduler stopped gracefully")
        except Exception as stop_error:
            logger.error(f"Error stopping scheduler: {stop_error}")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    # Main service loop
    try:
        while True:
            try:
                # Reload tasks from file occasionally to catch any external changes
                current_time = datetime.now()
                if (current_time - last_save_check).total_seconds() > 300:  # 5 minutes
                    scheduler.load_tasks()
                    last_save_check = current_time
                    logger.debug("Reloaded tasks from file")
                
                # Check for due tasks
                due_tasks = []
                for task_id, task in list(scheduler.tasks.items()):
                    if task.is_due():
                        logger.info(f"Task {task_id} is due, executing...")
                        due_tasks.append(task)
                
                # Execute due tasks
                for task in due_tasks:
                    try:
                        if scheduler.run_task(task):
                            tasks_executed += 1
                            
                            # Update executed task count in status
                            status = get_status()
                            status["tasks_executed"] = tasks_executed
                            update_status(status)
                            
                            logger.info(f"Task {task.task_id} executed successfully")
                        else:
                            logger.error(f"Failed to execute task {task.task_id}")
                    except Exception as task_error:
                        logger.error(f"Error executing task {task.task_id}: {task_error}")
                
                # Also check status of running tasks
                scheduler._check_running_tasks()
            except Exception as e:
                logger.error(f"Error processing tasks: {e}")
                import traceback
                logger.error(traceback.format_exc())
            
            # Update status to show we're still alive
            status = get_status()
            status["last_check_time"] = datetime.now().isoformat()
            status["tasks_executed"] = tasks_executed
            update_status(status)
            
            # Sleep for a short time
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Error in scheduler service: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Try to stop the scheduler gracefully
        try:
            scheduler.stop()
            logger.info("Scheduler stopped gracefully")
        except Exception as stop_error:
            logger.error(f"Error stopping scheduler: {stop_error}")
        logger.info("Scheduler service daemon stopped")

def run_as_daemon():
    """Run the scheduler service as a daemon.
    
    This function is called by the CLI when running the service.
    """
    run_service()

def install_systemd_service():
    """Install the scheduler as a systemd service on Linux systems."""
    if sys.platform != 'linux':
        print("This command is only supported on Linux systems.")
        return
    
    try:
        # Get the path to the Python executable
        python_executable = sys.executable
        
        # Get the path to this script
        script_path = os.path.abspath(__file__)
        
        # Create service file content
        service_content = f"""[Unit]
Description=Dravik Scheduler Service
After=network.target

[Service]
Type=simple
User={os.getlogin()}
ExecStart={python_executable} {script_path} --run-service
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=dravik-scheduler

[Install]
WantedBy=multi-user.target
"""
        
        # Path for user service
        service_path = Path.home() / ".config" / "systemd" / "user"
        service_path.mkdir(exist_ok=True, parents=True)
        service_file = service_path / "dravik-scheduler.service"
        
        # Write service file
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"Service file created at: {service_file}")
        print("\nTo enable and start the service, run the following commands:")
        print("systemctl --user daemon-reload")
        print("systemctl --user enable dravik-scheduler.service")
        print("systemctl --user start dravik-scheduler.service")
        print("\nTo check status:")
        print("systemctl --user status dravik-scheduler.service")
        
        return True
    except Exception as e:
        print(f"Error installing systemd service: {e}")
        return False

def install_macos_service():
    """Install the scheduler as a LaunchAgent service on macOS systems."""
    if sys.platform != 'darwin':
        print("This command is only supported on macOS systems.")
        return
    
    try:
        # Get the path to the Python executable
        python_executable = sys.executable
        
        # Get the path to this script
        script_path = os.path.abspath(__file__)
        
        # Create plist file content
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dravik.scheduler</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_executable}</string>
        <string>{script_path}</string>
        <string>--run-service</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{Path.home() / "dravik" / "logs" / "scheduler_stdout.log"}</string>
    <key>StandardErrorPath</key>
    <string>{Path.home() / "dravik" / "logs" / "scheduler_stderr.log"}</string>
</dict>
</plist>
"""
        
        # Path for LaunchAgent
        agent_path = Path.home() / "Library" / "LaunchAgents"
        agent_path.mkdir(exist_ok=True, parents=True)
        agent_file = agent_path / "com.dravik.scheduler.plist"
        
        # Write plist file
        with open(agent_file, 'w') as f:
            f.write(plist_content)
        
        print(f"LaunchAgent file created at: {agent_file}")
        print("\nTo load the agent, run the following command:")
        print(f"launchctl load {agent_file}")
        print("\nThe service will start automatically at login.")
        print("To start it immediately, run:")
        print(f"launchctl start com.dravik.scheduler")
        
        return True
    except Exception as e:
        print(f"Error installing macOS service: {e}")
        return False

# Export these functions for import from other modules
__all__ = [
    'start_service',
    'stop_service',
    'check_status',
    'run_as_daemon',
    'install_systemd_service',
    'install_macos_service'
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run-service":
        run_service()
    else:
        print("This script should be run with --run-service argument to start the daemon.")
        print("Use 'dravik scheduler --action=start' to start the service.") 