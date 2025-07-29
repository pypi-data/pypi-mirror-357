#!/usr/bin/env python3
"""
Dravik CLI - Main Entry Point

Command line interface for the Dravik dataset management system
"""

import os
import sys
import argparse
import logging
import uuid
from typing import List, Optional
from pathlib import Path

# Import command handlers
from .commands.dataset import DatasetCommands
from .commands.delete_dataset import DatasetDeletionCommands
from .commands.fix_red_teaming import RedTeamingFixCommands
from .commands.monitoring import MonitoringCommands

# Import scheduler service
from .scheduler_service import is_running, start_service

# Import logging utilities
from .logging import log_session_start, log_session_end, log_command, log_error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_parser():
    """
    Set up command line argument parser
    
    Returns:
        ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Dravik Dataset Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add version info
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Dravik Dataset Management CLI v0.1.0'
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Command to execute'
    )
    
    # Register command handlers
    commands = [
        DatasetCommands(),
        DatasetDeletionCommands(),
        RedTeamingFixCommands(),
        MonitoringCommands()
    ]
    
    for command in commands:
        command.register_subparser(subparsers)
    
    return parser, commands

def main(args: Optional[List[str]] = None):
    """
    Main entry point for the CLI
    
    Args:
        args: Command line arguments (uses sys.argv if None)
    
    Returns:
        int: Exit code
    """
    # Check if scheduler daemon is running, start it if not
    try:
        if not is_running():
            logger.info("Starting scheduler daemon automatically")
            # Check if config file exists with auto-start disabled
            config_path = Path.home() / "dravik" / "config" / "scheduler.config"
            if config_path.exists():
                with open(config_path, "r") as f:
                    if "auto_start=false" in f.read().lower():
                        logger.info("Scheduler auto-start disabled in config")
                    else:
                        # Start the scheduler service
                        try:
                            # Import and start the scheduler instance
                            from .scheduler import get_scheduler
                            scheduler = get_scheduler()
                            scheduler.start()
                            # Start the daemon service
                            start_service()
                            logger.info("Scheduler daemon started automatically")
                        except Exception as e:
                            logger.warning(f"Failed to auto-start scheduler: {str(e)}")
            else:
                # Config doesn't exist, start scheduler by default
                try:
                    # Import and start the scheduler instance
                    from .scheduler import get_scheduler
                    scheduler = get_scheduler()
                    scheduler.start()
                    # Start the daemon service
                    start_service()
                    logger.info("Scheduler daemon started automatically")
                except Exception as e:
                    logger.warning(f"Failed to auto-start scheduler: {str(e)}")
    except Exception as e:
        logger.warning(f"Error checking scheduler status: {str(e)}")
    
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    
    # Log session start
    log_session_start(session_id=session_id)
    
    try:
        parser, commands = setup_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            log_session_end(session_id=session_id, reason="No command specified")
            return 0
        
        # Log the command being executed
        command_str = parsed_args.command
        if args:
            command_str = ' '.join(args)
        elif len(sys.argv) > 1:
            command_str = ' '.join(sys.argv[1:])
            
        log_command(
            command=command_str,
            command_type=parsed_args.command,
            session_id=session_id
        )
        
        # Find the appropriate command handler
        result = 1
        for command in commands:
            command_class_name = command.__class__.__name__
            command_prefix = command_class_name.replace('Commands', '').lower()
            
            # Check if this handler should handle the command
            if parsed_args.command == command_prefix or command_class_name.lower().startswith(parsed_args.command):
                try:
                    result = command.handle(parsed_args)
                except Exception as e:
                    log_error(
                        error=str(e),
                        command=command_str,
                        session_id=session_id
                    )
                    logger.exception(f"Error executing command: {e}")
                    result = 1
                break
        
        if result != 0:
            log_session_end(session_id=session_id, reason=f"Command failed with code {result}")
        else:
            log_session_end(session_id=session_id, reason="Command completed successfully")
            
        return result
    except Exception as e:
        log_error(
            error=str(e),
            command="CLI initialization",
            session_id=session_id
        )
        log_session_end(session_id=session_id, reason=f"Unexpected error: {str(e)}")
        logger.exception(f"Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
