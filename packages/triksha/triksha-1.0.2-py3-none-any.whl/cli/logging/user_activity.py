"""
User activity tracking and logging module.

This module provides functionality to log and monitor all user activities 
performed with the CLI tool, integrating with Linux user management.
"""

import os
import pwd
import logging
import json
import time
import socket
import uuid
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configure logging to file only, not console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(Path.home() / "dravik" / "logs" / "activity.log"),
    ]
)

class UserActivityLogger:
    """
    Class for tracking and logging user activities.
    
    This class handles logging all user interactions with the tool, capturing
    Linux user information, and providing an audit trail for all actions.
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize the UserActivityLogger.
        
        Args:
            log_dir: Custom directory for storing logs. If None, uses default.
        """
        # Set up log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path.home() / "dravik" / "logs" / "user_activity"
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up log file paths
        self.activity_log_file = self.log_dir / "activity.jsonl"
        self.audit_log_file = self.log_dir / "audit.log"
        
        # Set up audit logger - file only, no console output
        self.audit_logger = logging.getLogger("dravik_audit")
        if not self.audit_logger.handlers:
            handler = logging.FileHandler(self.audit_log_file)
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
            self.audit_logger.setLevel(logging.INFO)
            # Prevent propagation to root logger (which might have console handlers)
            self.audit_logger.propagate = False
        
        # Get session ID
        self.session_id = str(uuid.uuid4())
        
        # Log initial info
        self._log_system_info()
    
    def _get_linux_user_info(self) -> Dict[str, Any]:
        """
        Get information about the Linux user running the tool.
        
        Returns:
            Dictionary containing Linux user information
        """
        user_id = os.getuid()
        user_info = pwd.getpwuid(user_id)
        
        return {
            "username": user_info.pw_name,
            "uid": user_id,
            "gid": user_info.pw_gid,
            "full_name": user_info.pw_gecos.split(',')[0] if ',' in user_info.pw_gecos else user_info.pw_gecos,
            "home_dir": user_info.pw_dir,
            "shell": user_info.pw_shell
        }
    
    def _log_system_info(self):
        """Log system information at the start of a session."""
        try:
            # Use 'localhost' as fallback if hostname resolution fails
            try:
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
            except socket.gaierror:
                hostname = 'localhost'
                ip_address = '127.0.0.1'
            
            system_info = {
                "session_id": self.session_id,
                "hostname": hostname,
                "ip_address": ip_address,
                "timestamp": datetime.now().isoformat(),
                "event_type": "session_start",
                "user": self._get_linux_user_info()
            }
            
            # Log to activity log
            self._append_to_activity_log(system_info)
            
            # Log to audit log
            self.audit_logger.info(
                f"Session started | User: {system_info['user']['username']} | "
                f"Session ID: {self.session_id} | IP: {ip_address}"
            )
        except Exception as e:
            # Log to file only, not console
            with open(Path.home() / "dravik" / "logs" / "error.log", "a") as f:
                f.write(f"{datetime.now().isoformat()} - ERROR - Error logging system info: {str(e)}\n")
    
    def _append_to_activity_log(self, log_entry: Dict[str, Any]):
        """
        Append an entry to the activity log file.
        
        Args:
            log_entry: Dictionary containing the log information
        """
        try:
            with open(self.activity_log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            # Log to file only, not console
            logging.error(f"Error writing to activity log: {str(e)}")
    
    def log_command(self, command: str, command_type: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Log a command executed by the user.
        
        Args:
            command: The command name
            command_type: Type of command (e.g., benchmark, dataset)
            parameters: Command parameters (optional)
        """
        user_info = self._get_linux_user_info()
        
        log_entry = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "command",
            "command": command,
            "command_type": command_type,
            "parameters": parameters or {},
            "user": user_info
        }
        
        # Log to activity log
        self._append_to_activity_log(log_entry)
        
        # Log to audit log
        self.audit_logger.info(
            f"Command executed | User: {user_info['username']} | "
            f"Command: {command} | Type: {command_type}"
        )
    
    def log_event(self, event_type: str, event_data: Dict[str, Any], description: Optional[str] = None):
        """
        Log a general event or activity.
        
        Args:
            event_type: Type of event (e.g., login, file_access)
            event_data: Data related to the event
            description: Human-readable description of the event
        """
        user_info = self._get_linux_user_info()
        
        log_entry = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "event_data": event_data,
            "description": description,
            "user": user_info
        }
        
        # Log to activity log
        self._append_to_activity_log(log_entry)
        
        # Log to audit log
        self.audit_logger.info(
            f"Event | User: {user_info['username']} | "
            f"Type: {event_type} | Description: {description or 'N/A'}"
        )
    
    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """
        Log an error that occurred during tool usage.
        
        Args:
            error: Error message or exception
            context: Additional context data
        """
        user_info = self._get_linux_user_info()
        
        log_entry = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "error",
            "error": error,
            "context": context or {},
            "user": user_info
        }
        
        # Log to activity log
        self._append_to_activity_log(log_entry)
        
        # Log to audit log
        self.audit_logger.error(
            f"Error | User: {user_info['username']} | "
            f"Error: {error}"
        )
    
    def log_session_end(self, reason: Optional[str] = None):
        """
        Log the end of a user session.
        
        Args:
            reason: Reason for ending the session (optional)
        """
        user_info = self._get_linux_user_info()
        
        log_entry = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "session_end",
            "reason": reason,
            "user": user_info
        }
        
        # Log to activity log
        self._append_to_activity_log(log_entry)
        
        # Log to audit log
        self.audit_logger.info(
            f"Session ended | User: {user_info['username']} | "
            f"Session ID: {self.session_id} | Reason: {reason or 'Normal exit'}"
        )


class ActivityMonitor:
    """
    Class for querying and monitoring user activities.
    
    This class provides methods to query log files and generate reports
    about user activities for display in monitoring dashboards.
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize the ActivityMonitor.
        
        Args:
            log_dir: Custom directory for storing logs. If None, uses default.
        """
        # Set up log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path.home() / "dravik" / "logs" / "user_activity"
        
        # Set up log file paths
        self.activity_log_file = self.log_dir / "activity.jsonl"
        self.audit_log_file = self.log_dir / "audit.log"
    
    def _read_activity_log(self) -> List[Dict[str, Any]]:
        """
        Read and parse the activity log file.
        
        Returns:
            List of activity log entries
        """
        if not self.activity_log_file.exists():
            return []
        
        try:
            entries = []
            with open(self.activity_log_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
            return entries
        except Exception as e:
            logging.error(f"Error reading activity log: {str(e)}")
            return []
    
    def get_user_activities(self, 
                            username: Optional[str] = None, 
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None,
                            event_types: Optional[List[str]] = None,
                            days_ago: Optional[int] = 7) -> List[Dict[str, Any]]:
        """
        Get user activities based on filters.
        
        Args:
            username: Filter by username
            start_time: Filter by start time
            end_time: Filter by end time
            event_types: Filter by event types
            days_ago: Show activities from this many days ago (default: 7)
            
        Returns:
            List of filtered activity log entries
        """
        entries = self._read_activity_log()
        filtered_entries = []
        
        # If start_time not provided but days_ago is, calculate start_time
        if start_time is None and days_ago is not None:
            start_time = datetime.now() - timedelta(days=days_ago)
        
        for entry in entries:
            # Filter by username
            if username and entry.get("user", {}).get("username") != username:
                continue
            
            # Filter by start time
            if start_time:
                try:
                    entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                    if entry_time < start_time:
                        continue
                except (ValueError, TypeError):
                    # Skip entries with invalid timestamps
                    continue
            
            # Filter by end time
            if end_time:
                try:
                    entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                    if entry_time > end_time:
                        continue
                except (ValueError, TypeError):
                    # Skip entries with invalid timestamps
                    continue
            
            # Filter by event types
            if event_types and entry.get("event_type") not in event_types:
                continue
            
            filtered_entries.append(entry)
        
        return filtered_entries
    
    def get_user_summary(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a summary of user activities.
        
        Args:
            username: Filter by username
            
        Returns:
            Dictionary containing summary information
        """
        entries = self.get_user_activities(username=username)
        
        # Calculate summary statistics
        event_counts = {}
        command_counts = {}
        sessions = set()
        first_activity = None
        last_activity = None
        
        for entry in entries:
            # Count events by type
            event_type = entry.get("event_type")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Count commands
            if event_type == "command":
                command = entry.get("command")
                if command:
                    command_counts[command] = command_counts.get(command, 0) + 1
            
            # Track sessions
            session_id = entry.get("session_id")
            if session_id:
                sessions.add(session_id)
            
            # Track first activity
            timestamp = entry.get("timestamp")
            if timestamp:
                entry_time = datetime.fromisoformat(timestamp)
                if first_activity is None or entry_time < first_activity:
                    first_activity = entry_time
                if last_activity is None or entry_time > last_activity:
                    last_activity = entry_time
        
        return {
            "username": username,
            "total_activities": len(entries),
            "event_counts": event_counts,
            "command_counts": command_counts,
            "session_count": len(sessions),
            "first_activity": first_activity.isoformat() if first_activity else None,
            "last_activity": last_activity.isoformat() if last_activity else None
        }
    
    def get_all_users(self) -> List[str]:
        """
        Get a list of all users that have logged activities.
        
        Returns:
            List of usernames
        """
        entries = self._read_activity_log()
        users = set()
        
        for entry in entries:
            username = entry.get("user", {}).get("username")
            if username:
                users.add(username)
        
        return sorted(list(users))


# Create global instances for use throughout the application
activity_logger = UserActivityLogger()
activity_monitor = ActivityMonitor()


# Helper functions for easy access
def log_command(command: str, command_type: str, parameters: Optional[Dict[str, Any]] = None):
    """Log a command execution."""
    activity_logger.log_command(command, command_type, parameters)

def log_event(event_type: str, event_data: Dict[str, Any], description: Optional[str] = None):
    """Log a general event."""
    activity_logger.log_event(event_type, event_data, description)

def log_error(error: str, context: Optional[Dict[str, Any]] = None):
    """Log an error."""
    activity_logger.log_error(error, context)

def log_session_end(reason: Optional[str] = None):
    """Log the end of a session."""
    activity_logger.log_session_end(reason)

def log_session_start():
    """Log the start of a new session."""
    # This is effectively a wrapper for _log_system_info
    activity_logger._log_system_info()

# Sample data generation has been moved to a standalone script
# cli/logging/generate_sample_data.py 