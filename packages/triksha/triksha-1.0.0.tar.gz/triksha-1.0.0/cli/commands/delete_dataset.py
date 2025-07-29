"""
Dataset Deletion Command Interface

This module provides CLI commands for dataset deletion operations
"""

import os
import logging
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from tabulate import tabulate

from datasets.core.deletion import DatasetDeletionManager
from datasets.core.registry import DatasetRegistry

logger = logging.getLogger(__name__)

class DatasetDeletionCommands:
    """
    Command line interface for dataset deletion operations
    """
    
    def __init__(self):
        """Initialize dataset deletion commands"""
        self.deletion_manager = DatasetDeletionManager()
        self.registry = DatasetRegistry()
    
    def register_subparser(self, subparsers):
        """
        Register this module's subparser and arguments
        
        Args:
            subparsers: Subparsers object from argparse
        """
        # Main delete parser
        delete_parser = subparsers.add_parser(
            'delete',
            help='Delete datasets',
            description='Commands for deleting datasets'
        )
        
        delete_subparsers = delete_parser.add_subparsers(
            dest='delete_command',
            help='Delete sub-command'
        )
        
        # Delete dataset command
        delete_dataset_parser = delete_subparsers.add_parser(
            'dataset',
            help='Delete a dataset',
            description='Delete a raw or formatted dataset'
        )
        
        delete_dataset_parser.add_argument(
            'dataset_id',
            help='ID or name of the dataset to delete'
        )
        
        delete_dataset_parser.add_argument(
            '--type', '-t',
            choices=['raw', 'formatted'],
            default='formatted',
            help='Type of dataset to delete (raw or formatted)'
        )
        
        delete_dataset_parser.add_argument(
            '--permanent', '-p',
            action='store_true',
            help='Permanently delete the dataset (cannot be restored)'
        )
        
        delete_dataset_parser.add_argument(
            '--reason', '-r',
            help='Reason for deletion (for audit logs)'
        )
        
        delete_dataset_parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Force deletion without confirmation prompt'
        )
        
        # List deleted datasets command
        list_deleted_parser = delete_subparsers.add_parser(
            'list',
            help='List deleted datasets',
            description='List datasets that have been deleted'
        )
        
        list_deleted_parser.add_argument(
            '--type', '-t',
            choices=['raw', 'formatted', 'all'],
            default='all',
            help='Type of deleted datasets to list'
        )
        
        list_deleted_parser.add_argument(
            '--limit', '-l',
            type=int,
            default=10,
            help='Maximum number of datasets to list'
        )
        
        # Restore dataset command
        restore_parser = delete_subparsers.add_parser(
            'restore',
            help='Restore a deleted dataset',
            description='Restore a dataset from the recycle bin'
        )
        
        restore_parser.add_argument(
            'dataset_id',
            help='ID or name of the dataset to restore'
        )
        
        restore_parser.add_argument(
            '--type', '-t',
            choices=['raw', 'formatted'],
            default='formatted',
            help='Type of dataset to restore (raw or formatted)'
        )
        
        # Recycle bin commands
        recycle_parser = delete_subparsers.add_parser(
            'recycle',
            help='Manage recycle bin',
            description='Commands for managing the dataset recycle bin'
        )
        
        recycle_subparsers = recycle_parser.add_subparsers(
            dest='recycle_command',
            help='Recycle bin sub-command'
        )
        
        # List recycle bin contents
        recycle_list_parser = recycle_subparsers.add_parser(
            'list',
            help='List recycle bin contents',
            description='List datasets in the recycle bin'
        )
        
        # Empty recycle bin
        recycle_empty_parser = recycle_subparsers.add_parser(
            'empty',
            help='Empty recycle bin',
            description='Permanently delete datasets in the recycle bin'
        )
        
        recycle_empty_parser.add_argument(
            '--days', '-d',
            type=int,
            default=30,
            help='Delete items older than this many days'
        )
        
        recycle_empty_parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Force emptying without confirmation prompt'
        )
    
    def handle(self, args):
        """
        Handle the delete command
        
        Args:
            args: Parsed arguments
        """
        if not hasattr(args, 'delete_command') or not args.delete_command:
            print("Error: No delete sub-command specified")
            return 1
            
        if args.delete_command == 'dataset':
            return self._handle_delete_dataset(args)
        elif args.delete_command == 'list':
            return self._handle_list_deleted(args)
        elif args.delete_command == 'restore':
            return self._handle_restore_dataset(args)
        elif args.delete_command == 'recycle':
            if not hasattr(args, 'recycle_command') or not args.recycle_command:
                print("Error: No recycle bin sub-command specified")
                return 1
                
            if args.recycle_command == 'list':
                return self._handle_recycle_list(args)
            elif args.recycle_command == 'empty':
                return self._handle_recycle_empty(args)
        
        print(f"Error: Unknown command: {args.delete_command}")
        return 1
    
    def _handle_delete_dataset(self, args):
        """Handle dataset deletion command"""
        dataset_id = args.dataset_id
        dataset_type = args.type
        permanent = args.permanent
        reason = args.reason
        force = args.force
        
        # Validate dataset exists
        if dataset_type == 'formatted':
            datasets = self.registry.list_datasets(active_only=True)
            dataset_info = next((d for d in datasets if d['id'] == dataset_id), None)
            
            if not dataset_info:
                # Try searching by name
                dataset_info = next((d for d in datasets if d['name'] == dataset_id), None)
                
                if dataset_info:
                    dataset_id = dataset_info['id']
                else:
                    print(f"Error: Formatted dataset '{dataset_id}' not found")
                    return 1
        
        # Confirm deletion
        if not force:
            action = "permanently delete" if permanent else "move to recycle bin"
            confirm = input(f"Are you sure you want to {action} the {dataset_type} dataset '{dataset_id}'? [y/N] ")
            if confirm.lower() != 'y':
                print("Deletion cancelled")
                return 0
        
        # Delete the dataset
        success = self.deletion_manager.delete_dataset(
            dataset_id=dataset_id,
            dataset_type=dataset_type,
            permanent=permanent,
            reason=reason,
            deleted_by=os.environ.get('USER', 'unknown')
        )
        
        if success:
            action = "Permanently deleted" if permanent else "Moved to recycle bin"
            print(f"{action} {dataset_type} dataset: {dataset_id}")
            return 0
        else:
            print(f"Error: Failed to delete {dataset_type} dataset: {dataset_id}")
            return 1
    
    def _handle_list_deleted(self, args):
        """Handle listing deleted datasets command"""
        dataset_type = args.type
        limit = args.limit
        
        # Get deletion history
        if dataset_type in ['raw', 'formatted']:
            history = self.deletion_manager.get_deletion_history(dataset_type=dataset_type)
        else:
            history = self.deletion_manager.get_deletion_history()
            
        if history.empty:
            print("No deleted datasets found")
            return 0
            
        # Limit results
        if limit > 0:
            history = history.head(limit)
            
        # Format for display
        display_df = history[['dataset_id', 'dataset_name', 'dataset_type', 
                             'deleted_at', 'permanent', 'reason', 'backed_up']]
                             
        # Convert boolean columns to Yes/No
        display_df['permanent'] = display_df['permanent'].map({1: 'Yes', 0: 'No'})
        display_df['backed_up'] = display_df['backed_up'].map({1: 'Yes', 0: 'No'})
        
        # Rename columns for display
        display_df = display_df.rename(columns={
            'dataset_id': 'ID',
            'dataset_name': 'Name',
            'dataset_type': 'Type',
            'deleted_at': 'Deleted At',
            'permanent': 'Permanent',
            'reason': 'Reason',
            'backed_up': 'Backed Up'
        })
        
        # Display as table
        print("\nDeleted Datasets:")
        print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))
        
        print(f"\nShowing {len(display_df)} of {len(history)} deleted datasets")
        return 0
    
    def _handle_restore_dataset(self, args):
        """Handle dataset restoration command"""
        dataset_id = args.dataset_id
        dataset_type = args.type
        
        # Restore the dataset
        success = self.deletion_manager.restore_dataset(
            dataset_id=dataset_id,
            dataset_type=dataset_type,
            restored_by=os.environ.get('USER', 'unknown')
        )
        
        if success:
            print(f"Restored {dataset_type} dataset: {dataset_id}")
            return 0
        else:
            print(f"Error: Failed to restore {dataset_type} dataset: {dataset_id}")
            print("Note: Only datasets in the recycle bin can be restored")
            return 1
    
    def _handle_recycle_list(self, args):
        """Handle listing recycle bin contents command"""
        contents = self.deletion_manager.get_recycle_bin_contents()
        
        if contents.empty:
            print("Recycle bin is empty")
            return 0
            
        # Format for display
        display_df = contents[['dataset_id', 'dataset_type', 'deleted_at', 'expiry_date']]
        
        # Rename columns for display
        display_df = display_df.rename(columns={
            'dataset_id': 'ID',
            'dataset_type': 'Type',
            'deleted_at': 'Deleted At',
            'expiry_date': 'Expires On'
        })
        
        # Display as table
        print("\nRecycle Bin Contents:")
        print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))
        
        print(f"\nTotal items in recycle bin: {len(display_df)}")
        print("Use 'delete restore <dataset_id> --type <type>' to restore a dataset")
        return 0
    
    def _handle_recycle_empty(self, args):
        """Handle emptying recycle bin command"""
        days = args.days
        force = args.force
        
        # Confirm emptying
        if not force:
            confirm = input(f"Are you sure you want to permanently delete all items in the recycle bin older than {days} days? [y/N] ")
            if confirm.lower() != 'y':
                print("Operation cancelled")
                return 0
        
        # Empty the recycle bin
        deleted_count = self.deletion_manager.empty_recycle_bin(days_old=days)
        
        print(f"Permanently deleted {deleted_count} items from the recycle bin")
        return 0
