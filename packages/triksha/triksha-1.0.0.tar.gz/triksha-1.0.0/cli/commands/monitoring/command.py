"""
User activity monitoring dashboard commands.

This module provides commands for viewing and analyzing user activities
through a monitoring dashboard interface.
"""

import os
import textwrap
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import argparse

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn
from rich import box

from cli.logging.user_activity import activity_monitor, log_event


class MonitoringCommands:
    """Commands for monitoring user activities."""
    
    def __init__(self, console=None):
        """
        Initialize monitoring commands.
        
        Args:
            console: Rich console instance for output
        """
        self.console = console or Console()
        self.monitor = activity_monitor
    
    def register_subparser(self, subparsers):
        """
        Register this command with the given subparsers.
        
        Args:
            subparsers: Subparsers object from argparse
        """
        monitor_parser = subparsers.add_parser(
            'monitor',
            help='View user activity monitoring dashboard',
            description='Interactive dashboard for monitoring user activity across the CLI tool'
        )
        
        monitor_parser.add_argument(
            '--user',
            help='Filter dashboard to show only activities for the specified user',
            type=str
        )
        
        monitor_parser.add_argument(
            '--since',
            help='Show activities since the specified date (YYYY-MM-DD)',
            type=str
        )
        
        return monitor_parser
    
    def handle(self, args):
        """
        Handle the monitor command.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            int: Exit code
        """
        try:
            # Initialize with any filters from command line
            filters = {}
            
            if hasattr(args, 'user') and args.user:
                filters['username'] = args.user
                
            if hasattr(args, 'since') and args.since:
                try:
                    start_time = datetime.strptime(args.since, "%Y-%m-%d")
                    filters['start_time'] = start_time
                except ValueError:
                    self.console.print("[yellow]Invalid date format. Expected YYYY-MM-DD.[/]")
            
            # Run the dashboard
            self.run()
            return 0
        except Exception as e:
            self.console.print(f"[bold red]Error running monitoring dashboard: {str(e)}[/]")
            import traceback
            traceback.print_exc()
            return 1
    
    def show_dashboard(self):
        """
        Display the main monitoring dashboard with user activity statistics.
        """
        # Get all users with activity
        users = self.monitor.get_all_users()
        
        if not users:
            self.console.print(Panel("[yellow]No user activity data found.[/]", 
                                   title="User Activity Dashboard", 
                                   border_style="yellow"))
            return
        
        # Get activity summaries for all users
        user_summaries = []
        for username in users:
            summary = self.monitor.get_user_summary(username)
            user_summaries.append(summary)
        
        # Sort by activity count (most active first)
        user_summaries.sort(key=lambda x: x.get("total_activities", 0), reverse=True)
        
        # Create the dashboard layout
        self.console.print("\n[bold cyan]User Activity Monitoring Dashboard[/]\n")
        
        # User activity summary table
        table = Table(title="User Activity Summary", box=box.ROUNDED)
        table.add_column("Username", style="cyan")
        table.add_column("Sessions", justify="right")
        table.add_column("Total Activities", justify="right")
        table.add_column("Last Activity", justify="right")
        table.add_column("Most Used Command", justify="left")
        
        for summary in user_summaries:
            username = summary.get("username", "Unknown")
            session_count = str(summary.get("session_count", 0))
            total_activities = str(summary.get("total_activities", 0))
            last_activity = summary.get("last_activity", "Unknown")
            if last_activity and last_activity != "Unknown":
                try:
                    last_dt = datetime.fromisoformat(last_activity)
                    last_activity = last_dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    pass
            
            # Determine most used command
            command_counts = summary.get("command_counts", {})
            most_used_command = "None"
            if command_counts:
                most_used_command = max(command_counts.items(), key=lambda x: x[1])[0]
            
            table.add_row(username, session_count, total_activities, last_activity, most_used_command)
        
        self.console.print(table)
        
        # Overall activity metrics
        total_users = len(users)
        total_sessions = sum(summary.get("session_count", 0) for summary in user_summaries)
        total_activities = sum(summary.get("total_activities", 0) for summary in user_summaries)
        
        metrics_panel = Panel(
            f"[bold]Total Users:[/] {total_users}   "
            f"[bold]Total Sessions:[/] {total_sessions}   "
            f"[bold]Total Activities:[/] {total_activities}",
            title="System Metrics",
            border_style="blue"
        )
        self.console.print(metrics_panel)
        
        # Show options for detailed views
        self.console.print("\n[bold cyan]Available Actions:[/]")
        self.console.print("  1. View detailed user activity")
        self.console.print("  2. View command statistics")
        self.console.print("  3. View session history")
        self.console.print("  4. Return to main menu")
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"], default="4")
        
        if choice == "1":
            self._show_user_detail_prompt()
        elif choice == "2":
            self._show_command_statistics()
        elif choice == "3":
            self._show_session_history()
    
    def _show_user_detail_prompt(self):
        """Show prompt for selecting a user to view detailed activity."""
        users = self.monitor.get_all_users()
        if not users:
            self.console.print("[yellow]No users found.[/]")
            return
        
        # Create numbered list of users
        self.console.print("\n[bold cyan]Select a user:[/]")
        for i, username in enumerate(users, 1):
            self.console.print(f"  {i}. {username}")
        self.console.print(f"  {len(users) + 1}. Return to dashboard")
        
        # Get user selection
        max_choice = len(users) + 1
        choice = Prompt.ask(
            "Select a user",
            choices=[str(i) for i in range(1, max_choice + 1)],
            default=str(max_choice)
        )
        
        if int(choice) == max_choice:
            self.show_dashboard()
            return
        
        selected_user = users[int(choice) - 1]
        self._show_user_details(selected_user)
    
    def _show_user_details(self, username: str):
        """
        Show detailed activity for a specific user.
        
        Args:
            username: Username to display details for
        """
        # Get user summary
        summary = self.monitor.get_user_summary(username)
        
        # Get detailed activities
        activities = self.monitor.get_user_activities(username=username)
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Create user details panel
        details_text = [
            f"[bold]Username:[/] {username}",
            f"[bold]Total Activities:[/] {summary.get('total_activities', 0)}",
            f"[bold]Session Count:[/] {summary.get('session_count', 0)}",
            f"[bold]First Activity:[/] {self._format_timestamp(summary.get('first_activity'))}",
            f"[bold]Last Activity:[/] {self._format_timestamp(summary.get('last_activity'))}"
        ]
        
        details_panel = Panel(
            "\n".join(details_text),
            title=f"User Details: {username}",
            border_style="cyan"
        )
        
        self.console.print(details_panel)
        
        # Create activity table
        table = Table(title=f"Recent Activities for {username}", box=box.ROUNDED)
        table.add_column("Time", style="cyan", width=20)
        table.add_column("Event Type", style="green", width=15)
        table.add_column("Details", style="white")
        
        # Add recent activities to table (up to 20)
        for activity in activities[:20]:
            timestamp = self._format_timestamp(activity.get("timestamp"))
            event_type = activity.get("event_type", "Unknown")
            
            # Format details based on event type
            details = self._format_activity_details(activity)
            
            table.add_row(timestamp, event_type, details)
        
        self.console.print(table)
        
        # Show options for filtering
        self.console.print("\n[bold cyan]Filter Options:[/]")
        self.console.print("  1. Filter by event type")
        self.console.print("  2. Filter by date range")
        self.console.print("  3. Return to user selection")
        self.console.print("  4. Return to dashboard")
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"], default="4")
        
        if choice == "1":
            self._filter_by_event_type(username)
        elif choice == "2":
            self._filter_by_date_range(username)
        elif choice == "3":
            self._show_user_detail_prompt()
        else:
            self.show_dashboard()
    
    def _format_timestamp(self, timestamp: Optional[str]) -> str:
        """Format ISO timestamp to human-readable format."""
        if not timestamp:
            return "Unknown"
        
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return timestamp
    
    def _format_activity_details(self, activity: Dict[str, Any]) -> str:
        """Format activity details based on event type."""
        event_type = activity.get("event_type", "Unknown")
        
        if event_type == "command":
            command = activity.get("command", "Unknown")
            command_type = activity.get("command_type", "")
            return f"Command: {command} (Type: {command_type})"
        
        elif event_type == "session_start":
            return f"Session started from {activity.get('hostname', 'Unknown')}"
        
        elif event_type == "session_end":
            reason = activity.get("reason", "Normal exit")
            return f"Session ended: {reason}"
        
        elif event_type == "error":
            return f"Error: {activity.get('error', 'Unknown error')}"
        
        elif event_type == "event":
            description = activity.get("description", "No description")
            return description
        
        return str(activity.get("event_data", "No details"))
    
    def _filter_by_event_type(self, username: str):
        """Show activities filtered by event type."""
        # Get all activities
        activities = self.monitor.get_user_activities(username=username)
        
        # Extract unique event types
        event_types = set(activity.get("event_type", "Unknown") for activity in activities)
        event_types = sorted(list(event_types))
        
        # Create numbered list of event types
        self.console.print("\n[bold cyan]Select event type to filter:[/]")
        for i, event_type in enumerate(event_types, 1):
            self.console.print(f"  {i}. {event_type}")
        self.console.print(f"  {len(event_types) + 1}. Return to user details")
        
        # Get event type selection
        max_choice = len(event_types) + 1
        choice = Prompt.ask(
            "Select event type",
            choices=[str(i) for i in range(1, max_choice + 1)],
            default=str(max_choice)
        )
        
        if int(choice) == max_choice:
            self._show_user_details(username)
            return
        
        selected_event_type = event_types[int(choice) - 1]
        
        # Filter activities by selected event type
        filtered_activities = self.monitor.get_user_activities(
            username=username,
            event_types=[selected_event_type]
        )
        filtered_activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Display filtered activities
        table = Table(title=f"{selected_event_type} Activities for {username}", box=box.ROUNDED)
        table.add_column("Time", style="cyan", width=20)
        table.add_column("Details", style="white")
        
        for activity in filtered_activities:
            timestamp = self._format_timestamp(activity.get("timestamp"))
            details = self._format_activity_details(activity)
            table.add_row(timestamp, details)
        
        self.console.print(table)
        
        # Return to user details after viewing
        input("\nPress Enter to return to user details...")
        self._show_user_details(username)
    
    def _filter_by_date_range(self, username: str):
        """Show activities filtered by date range."""
        self.console.print("\n[bold cyan]Filter activities by date range[/]")
        
        # Get start date
        start_date_str = Prompt.ask(
            "Start date (YYYY-MM-DD or empty for all)",
            default=""
        )
        
        # Get end date
        end_date_str = Prompt.ask(
            "End date (YYYY-MM-DD or empty for today)",
            default=""
        )
        
        # Parse dates
        start_time = None
        end_time = None
        
        if start_date_str:
            try:
                start_time = datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                self.console.print("[yellow]Invalid start date format. Using no start date filter.[/]")
        
        if end_date_str:
            try:
                # Set end time to end of day
                end_time = datetime.strptime(end_date_str, "%Y-%m-%d")
                end_time = end_time.replace(hour=23, minute=59, second=59)
            except ValueError:
                self.console.print("[yellow]Invalid end date format. Using today as end date.[/]")
                end_time = datetime.now()
        else:
            # Default to now if not specified
            end_time = datetime.now()
        
        # Filter activities by date range
        filtered_activities = self.monitor.get_user_activities(
            username=username,
            start_time=start_time,
            end_time=end_time
        )
        filtered_activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Display filtered activities
        date_range_str = ""
        if start_time:
            date_range_str += f"from {start_time.strftime('%Y-%m-%d')}"
        if end_time:
            date_range_str += f" to {end_time.strftime('%Y-%m-%d')}"
        
        table = Table(title=f"Activities for {username} {date_range_str}", box=box.ROUNDED)
        table.add_column("Time", style="cyan", width=20)
        table.add_column("Event Type", style="green", width=15)
        table.add_column("Details", style="white")
        
        for activity in filtered_activities:
            timestamp = self._format_timestamp(activity.get("timestamp"))
            event_type = activity.get("event_type", "Unknown")
            details = self._format_activity_details(activity)
            table.add_row(timestamp, event_type, details)
        
        self.console.print(table)
        
        # Return to user details after viewing
        input("\nPress Enter to return to user details...")
        self._show_user_details(username)
    
    def _show_command_statistics(self):
        """Show statistics about command usage across all users."""
        # Get all activities
        all_activities = self.monitor.get_user_activities()
        
        # Extract command usage
        command_usage = {}
        command_by_user = {}
        
        for activity in all_activities:
            if activity.get("event_type") == "command":
                command = activity.get("command")
                username = activity.get("user", {}).get("username", "Unknown")
                
                if command:
                    # Count overall usage
                    command_usage[command] = command_usage.get(command, 0) + 1
                    
                    # Count by user
                    if command not in command_by_user:
                        command_by_user[command] = {}
                    command_by_user[command][username] = command_by_user[command].get(username, 0) + 1
        
        # Sort commands by frequency
        sorted_commands = sorted(command_usage.items(), key=lambda x: x[1], reverse=True)
        
        # Create command usage table
        table = Table(title="Command Usage Statistics", box=box.ROUNDED)
        table.add_column("Command", style="cyan")
        table.add_column("Usage Count", style="green", justify="right")
        table.add_column("Top User", style="yellow")
        
        for command, count in sorted_commands:
            # Find top user for this command
            top_user = None
            top_count = 0
            
            for user, user_count in command_by_user[command].items():
                if user_count > top_count:
                    top_count = user_count
                    top_user = user
            
            top_user_str = f"{top_user} ({top_count} times)" if top_user else "N/A"
            table.add_row(command, str(count), top_user_str)
        
        self.console.print(table)
        
        # Return to dashboard after viewing
        input("\nPress Enter to return to dashboard...")
        self.show_dashboard()
    
    def _show_session_history(self):
        """Show history of user sessions."""
        # Get all activities
        all_activities = self.monitor.get_user_activities()
        
        # Extract session starts and ends
        sessions = {}
        
        for activity in all_activities:
            if activity.get("event_type") == "session_start":
                session_id = activity.get("session_id")
                if session_id:
                    username = activity.get("user", {}).get("username", "Unknown")
                    timestamp = activity.get("timestamp")
                    hostname = activity.get("hostname", "Unknown")
                    ip_address = activity.get("ip_address", "Unknown")
                    
                    sessions[session_id] = {
                        "username": username,
                        "start_time": timestamp,
                        "end_time": None,
                        "hostname": hostname,
                        "ip_address": ip_address,
                        "reason": None
                    }
            
            elif activity.get("event_type") == "session_end":
                session_id = activity.get("session_id")
                if session_id and session_id in sessions:
                    sessions[session_id]["end_time"] = activity.get("timestamp")
                    sessions[session_id]["reason"] = activity.get("reason")
        
        # Convert to list and sort by start time (newest first)
        session_list = list(sessions.values())
        session_list.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        
        # Create session history table
        table = Table(title="Session History", box=box.ROUNDED)
        table.add_column("User", style="cyan")
        table.add_column("Start Time", style="green")
        table.add_column("End Time", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Hostname/IP", style="dim")
        
        for session in session_list:
            username = session.get("username", "Unknown")
            start_time_str = self._format_timestamp(session.get("start_time"))
            
            # Handle end time
            end_time = session.get("end_time")
            if end_time:
                end_time_str = self._format_timestamp(end_time)
                
                # Calculate duration
                try:
                    start_dt = datetime.fromisoformat(session.get("start_time", ""))
                    end_dt = datetime.fromisoformat(end_time)
                    duration = end_dt - start_dt
                    duration_str = str(duration).split('.')[0]  # Remove microseconds
                except (ValueError, TypeError):
                    duration_str = "Unknown"
            else:
                end_time_str = "[italic]Active[/]"
                duration_str = "[italic]In progress[/]"
            
            host_info = f"{session.get('hostname', 'Unknown')} ({session.get('ip_address', 'Unknown')})"
            
            table.add_row(username, start_time_str, end_time_str, duration_str, host_info)
        
        self.console.print(table)
        
        # Return to dashboard after viewing
        input("\nPress Enter to return to dashboard...")
        self.show_dashboard()
    
    def run(self):
        """
        Run the monitoring dashboard in interactive mode.
        
        This is the main entry point for the monitoring dashboard when used
        from the CLI menu.
        """
        try:
            # Display intro message
            self.console.print("\n[bold cyan]Loading user activity data...[/]")
            
            # Log this viewing activity silently
            try:
                from cli.logging.user_activity import log_event
                log_event("dashboard_view", 
                         {"view_type": "activity_monitor"}, 
                         "User viewed the activity monitoring dashboard")
            except Exception:
                # Silent fail if logging is unavailable
                pass
            
            # Show dashboard with historical data by default (7 days)
            self.show_dashboard()
            
            # Loop to allow navigation back to dashboard
            while True:
                action = Prompt.ask(
                    "\n[bold]Select an action[/]",
                    choices=["1", "2", "3", "q", "b"],
                    default="b"
                )
                
                if action == "1":
                    # Filter by user
                    users = self.monitor.get_all_users()
                    if not users:
                        self.console.print("[yellow]No users found in the activity log.[/]")
                        continue
                        
                    self.console.print("\n[bold]Available users:[/]")
                    for i, user in enumerate(users, 1):
                        self.console.print(f"  {i}. {user}")
                        
                    user_choice = Prompt.ask(
                        "Select a user number to filter by",
                        choices=[str(i) for i in range(1, len(users) + 1)] + ["b"],
                        default="b"
                    )
                    
                    if user_choice == "b":
                        self.show_dashboard()
                        continue
                        
                    selected_user = users[int(user_choice) - 1]
                    self._show_user_details(selected_user)
                    
                elif action == "2":
                    # Filter by date range
                    date_range = self._filter_by_date_range(None)
                    if date_range:
                        start_date, end_date = date_range
                        activities = self.monitor.get_user_activities(
                            start_time=start_date,
                            end_time=end_date
                        )
                        
                        if not activities:
                            self.console.print("[yellow]No activities found in the selected date range.[/]")
                            continue
                            
                        self._display_activities(activities, f"Activities from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                    
                elif action == "3":
                    # Filter by event type
                    self._filter_by_event_type(None)
                    
                elif action in ["q", "b"]:
                    # Return to main menu
                    break
                    
            return 0
        except Exception as e:
            self.console.print(f"[bold red]Error in monitoring dashboard: {str(e)}[/]")
            import traceback
            traceback.print_exc()
            return 1
        
    def _display_activities(self, activities, title):
        """Display a list of activities with formatting"""
        if not activities:
            self.console.print(f"[yellow]No activities found for {title}.[/]")
            return
            
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Time", style="cyan", no_wrap=True)
        table.add_column("User", style="green")
        table.add_column("Event Type", style="yellow")
        table.add_column("Details", style="white")
        
        for activity in activities:
            timestamp = self._format_timestamp(activity.get("timestamp"))
            username = activity.get("user", {}).get("username", "Unknown")
            event_type = activity.get("event_type", "Unknown")
            details = self._format_activity_details(activity)
            
            table.add_row(timestamp, username, event_type, details)
            
        self.console.print(table) 