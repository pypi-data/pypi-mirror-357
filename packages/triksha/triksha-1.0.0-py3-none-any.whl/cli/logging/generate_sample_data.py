"""
Standalone script to generate sample user activity log data.

This module also provides a function to remove sample data.
"""

import os
import json
import uuid
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

def remove_sample_data():
    """
    Remove any sample activity log data.
    
    This function checks if the activity log contains sample data
    (identified by the 'demo-server' hostname) and deletes it if found.
    """
    # Get log file paths
    log_dir = Path.home() / "dravik" / "logs" / "user_activity"
    activity_log_file = log_dir / "activity.jsonl"
    audit_log_file = log_dir / "audit.log"
    
    # Check if files exist
    if not activity_log_file.exists():
        print("No activity log file found.")
        return False
    
    # Check if file contains sample data
    contains_sample_data = False
    try:
        with open(activity_log_file, "r") as f:
            for line in f:
                if line and "demo-server" in line:
                    contains_sample_data = True
                    break
    except Exception as e:
        print(f"Error checking activity log: {str(e)}")
        return False
    
    # Delete files if they contain sample data
    if contains_sample_data:
        try:
            activity_log_file.unlink(missing_ok=True)
            audit_log_file.unlink(missing_ok=True)
            print("Sample data removed successfully.")
            return True
        except Exception as e:
            print(f"Error removing sample data: {str(e)}")
            return False
    else:
        print("No sample data found.")
        return False

def generate_sample_data(num_days=7, activities_per_day=5):
    """
    Generate sample activity log data for demonstration purposes.
    
    Args:
        num_days: Number of days of historical data to generate
        activities_per_day: Number of activities per day to generate
    """
    # Create log directory if it doesn't exist
    log_dir = Path.home() / "dravik" / "logs" / "user_activity"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create activity log file
    activity_log_file = log_dir / "activity.jsonl"
    
    # Create audit log file
    audit_log_file = log_dir / "audit.log"
    
    # Sample user data
    users = [
        {"username": "admin", "uid": 1000, "gid": 1000, "full_name": "System Administrator", 
         "home_dir": "/home/admin", "shell": "/bin/bash"},
        {"username": "analyst", "uid": 1001, "gid": 1001, "full_name": "Security Analyst", 
         "home_dir": "/home/analyst", "shell": "/bin/bash"},
        {"username": "dev", "uid": 1002, "gid": 1002, "full_name": "Developer", 
         "home_dir": "/home/dev", "shell": "/bin/zsh"}
    ]
    
    # Add current user
    import pwd
    user_id = os.getuid()
    user_info = pwd.getpwuid(user_id)
    current_user = {
        "username": user_info.pw_name,
        "uid": user_id,
        "gid": user_info.pw_gid,
        "full_name": user_info.pw_gecos.split(',')[0] if ',' in user_info.pw_gecos else user_info.pw_gecos,
        "home_dir": user_info.pw_dir,
        "shell": user_info.pw_shell
    }
    users.append(current_user)
    
    # Sample commands
    commands = [
        {"command": "benchmark", "command_type": "static_benchmark", 
         "parameters": {"model": "gpt-4", "dataset": "adversarial-qa"}},
        {"command": "redteam", "command_type": "conversation_redteam", 
         "parameters": {"model": "claude-3-sonnet"}},
        {"command": "dataset", "command_type": "manage_dataset", 
         "parameters": {"action": "view"}},
        {"command": "results", "command_type": "view_results", 
         "parameters": {"benchmark_id": "bench-2023-05-12"}},
        {"command": "guardrail", "command_type": "register_guardrail", 
         "parameters": {"type": "custom-api"}}
    ]
    
    # Sample events
    events = [
        {"event_type": "login", "event_data": {"source_ip": "192.168.1.100"}, 
         "description": "User logged in to the system"},
        {"event_type": "file_access", "event_data": {"file": "/data/benchmarks/results.json"}, 
         "description": "User accessed benchmark results file"},
        {"event_type": "config_change", "event_data": {"setting": "email_notifications", "value": "true"}, 
         "description": "User enabled email notifications"},
        {"event_type": "dataset_upload", "event_data": {"dataset": "custom-jailbreak-prompts.json", "size": "1.2MB"}, 
         "description": "User uploaded a custom dataset"},
        {"event_type": "api_key_update", "event_data": {"provider": "openai"}, 
         "description": "User updated API key for provider"}
    ]
    
    # Sample errors
    errors = [
        {"error": "API rate limit exceeded", "context": {"provider": "openai", "model": "gpt-4"}},
        {"error": "Invalid dataset format", "context": {"file": "custom_dataset.json"}},
        {"error": "Model not available", "context": {"model": "llama-3-70b"}},
        {"error": "Benchmark timeout", "context": {"benchmark_id": "bench-2023-05-15"}},
        {"error": "Invalid API key", "context": {"provider": "anthropic"}}
    ]
    
    # Generate sessions (one per day)
    sessions = []
    now = datetime.now()
    
    for day in range(num_days):
        session_date = now - timedelta(days=day)
        for user in users:
            session_id = str(uuid.uuid4())
            sessions.append({
                "user": user,
                "session_id": session_id,
                "date": session_date,
                "activities": []
            })
    
    # Open log file for writing
    with open(activity_log_file, "w") as f:
        # For each session, generate activities
        for session in sessions:
            # Session start
            start_time = session["date"].replace(hour=random.randint(8, 12), 
                                                 minute=random.randint(0, 59),
                                                 second=random.randint(0, 59))
            
            session_start = {
                "session_id": session["session_id"],
                "hostname": "demo-server",  # This is the marker for sample data
                "ip_address": f"192.168.1.{random.randint(2, 254)}",
                "timestamp": start_time.isoformat(),
                "event_type": "session_start",
                "user": session["user"]
            }
            
            f.write(json.dumps(session_start) + "\n")
            
            # Random activities for this session
            for i in range(random.randint(activities_per_day, activities_per_day*2)):
                # Increment time for each activity
                activity_time = start_time + timedelta(minutes=random.randint(5, 120))
                
                # Random type of entry (command, event, error)
                entry_type = random.choice(["command", "event", "error"])
                
                if entry_type == "command":
                    # Random command
                    command = random.choice(commands)
                    entry = {
                        "session_id": session["session_id"],
                        "timestamp": activity_time.isoformat(),
                        "event_type": "command",
                        "command": command["command"],
                        "command_type": command["command_type"],
                        "parameters": command["parameters"],
                        "user": session["user"]
                    }
                    
                elif entry_type == "event":
                    # Random event
                    event = random.choice(events)
                    entry = {
                        "session_id": session["session_id"],
                        "timestamp": activity_time.isoformat(),
                        "event_type": event["event_type"],
                        "event_data": event["event_data"],
                        "description": event["description"],
                        "user": session["user"]
                    }
                    
                else:  # error
                    # Random error
                    error = random.choice(errors)
                    entry = {
                        "session_id": session["session_id"],
                        "timestamp": activity_time.isoformat(),
                        "event_type": "error",
                        "error": error["error"],
                        "context": error["context"],
                        "user": session["user"]
                    }
                
                f.write(json.dumps(entry) + "\n")
            
            # Session end
            end_time = activity_time + timedelta(minutes=random.randint(10, 60))
            
            session_end = {
                "session_id": session["session_id"],
                "timestamp": end_time.isoformat(),
                "event_type": "session_end",
                "reason": "Normal exit",
                "user": session["user"]
            }
            
            f.write(json.dumps(session_end) + "\n")
    
    # Create sample audit log entries
    with open(audit_log_file, "w") as f:
        for session in sessions:
            start_time = datetime.fromisoformat(session_start["timestamp"])
            f.write(f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} [INFO] Session started | "
                   f"User: {session['user']['username']} | Session ID: {session['session_id']} | "
                   f"IP: {session_start['ip_address']}\n")
            
            end_time = datetime.fromisoformat(session_end["timestamp"])
            f.write(f"{end_time.strftime('%Y-%m-%d %H:%M:%S')} [INFO] Session ended | "
                   f"User: {session['user']['username']} | Session ID: {session['session_id']} | "
                   f"Reason: Normal exit\n")
    
    print(f"Generated sample activity data for {num_days} days with {len(sessions)} sessions")
    return True

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate or remove sample user activity data")
    parser.add_argument("--generate", action="store_true", help="Generate sample data")
    parser.add_argument("--remove", action="store_true", help="Remove sample data")
    parser.add_argument("--days", type=int, default=7, help="Number of days of data to generate")
    parser.add_argument("--activities", type=int, default=5, help="Activities per day to generate")
    
    args = parser.parse_args()
    
    if args.remove:
        remove_sample_data()
    elif args.generate:
        generate_sample_data(num_days=args.days, activities_per_day=args.activities)
    else:
        # Default action is to remove sample data
        remove_sample_data() 