"""Fix Red Teaming CLI Module

This module provides command-line utilities to fix issues with the conversation red teaming module.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from pathlib import Path
import os
import re
import inquirer
import shutil
import sys

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Add project root to path if not already there
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import the necessary modules from the benchmark directory
try:
    from benchmark.conversation_red_teaming import run_red_teaming_conversation
except ImportError:
    # Show a helpful error message
    Console().print("[red]Error: Could not import the conversation_red_teaming module.[/]")
    Console().print("[yellow]Make sure the benchmark directory is in your Python path.[/]")


class RedTeamingFixCommands:
    """Commands for fixing red teaming conversation issues"""

    def __init__(self, db=None, config=None):
        """Initialize with optional database and config dependencies"""
        self.db = db
        self.config = config
        self.console = Console()
        self.target_file = Path(__file__).parent.parent.parent / "benchmark" / "conversation_red_teaming.py"
        self.backup_file = self.target_file.with_suffix(".py.bak")

    def register_subparser(self, subparsers):
        """Register this module with the CLI argument parser"""
        parser = subparsers.add_parser(
            "redt",  # Short command name
            help="Red teaming conversation tools and fixes"
        )

        # Create subparsers for redt commands
        redt_subparsers = parser.add_subparsers(
            dest="redt_command",
            help="Red teaming command"
        )

        # Fix command
        fix_parser = redt_subparsers.add_parser(
            "fix",
            help="Fix issues with the red teaming conversation module"
        )
        fix_parser.add_argument(
            "--backup", 
            action="store_true",
            help="Create a backup of the original file before fixing"
        )

        # Test command
        test_parser = redt_subparsers.add_parser(
            "test",
            help="Test the red teaming conversation module"
        )
        test_parser.add_argument(
            "--model", 
            type=str, 
            default="distilbert/distilgpt2",
            help="HuggingFace model to use for red teaming"
        )
        test_parser.add_argument(
            "--target", 
            type=str, 
            default="ollama",
            help="Target type (openai, gemini, ollama)"
        )
        test_parser.add_argument(
            "--target-id", 
            type=str, 
            default="gemma:2b",
            help="Target model ID"
        )
        test_parser.add_argument(
            "--turns", 
            type=int, 
            default=3,
            help="Number of conversation turns"
        )

        return parser

    def handle(self, args):
        """Handle the red teaming commands"""
        if args.redt_command == "fix":
            self.fix_red_teaming_module(create_backup=args.backup)
            return 0
        elif args.redt_command == "test":
            self.test_red_teaming_module(
                model=args.model,
                target_type=args.target,
                target_id=args.target_id,
                turns=args.turns
            )
            return 0
        else:
            self.console.print("[yellow]Invalid red teaming command[/]")
            return 1

    def fix_red_teaming_module(self, create_backup=True):
        """Fix the issues in the conversation red teaming module"""
        self.console.print(Panel(
            "[bold]Red Teaming Conversation Module Fix[/]",
            border_style="cyan"
        ))

        # Check if the file exists
        if not self.target_file.exists():
            self.console.print(f"[red]Error: Target file {self.target_file} not found![/]")
            return

        # Create a backup if requested
        if create_backup:
            try:
                shutil.copy2(self.target_file, self.backup_file)
                self.console.print(f"[green]Backup created at {self.backup_file}[/]")
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not create backup - {str(e)}[/]")
                if not inquirer.confirm("Continue without backup?", default=False):
                    self.console.print("[yellow]Operation cancelled.[/]")
                    return

        # Read the original file
        try:
            with open(self.target_file, 'r') as f:
                original_content = f.read()
        except Exception as e:
            self.console.print(f"[red]Error reading file: {str(e)}[/]")
            return

        # Apply the fixes
        try:
            # First fix: Update the message extraction logic for the first message
            first_fix_pattern = re.compile(
                "(# First attack prompt from the red teaming model.*?" +  # Start of the section
                "with console\\.status.*?Preparing initial prompt.*?" +  # Status indicator
                "# Extract only the actual conversational message.*?)" +  # Comment before pattern we want to edit
                "actual_message = None", re.DOTALL  # Pattern to replace
            )
            
            first_fix_replacement = "\\1actual_message = \"\"  # Initialize as empty string for better handling"

            # Apply the first fix
            fixed_content = re.sub(first_fix_pattern, first_fix_replacement, original_content)
            
            # Check if the first pattern was matched and replaced
            if fixed_content == original_content:
                self.console.print("[yellow]Warning: First pattern not found. Skipping this fix.[/]")

            # Second fix: Add an automatic fallback for empty message
            second_fix_pattern = re.compile(
                r'(# If all extraction methods failed, use a friendly default\s*'  # Comment before if statement
                r'if not actual_message or len\(actual_message\) < 5 or.*?)'  # If statement
                r'red_team_message = "Hey there\! How are you doing today\?"', re.DOTALL  # Pattern to replace
            )
            
            second_fix_replacement = r'''\1red_team_message = fallback_messages.get(attack_vector, "Hey there! How are you doing today?")
            # Log the fallback for debugging
            print(f"[bold yellow]DEBUG: Using fallback message for initial prompt: {red_team_message}[/]")'''  # Triple quotes for multiline string

            # Apply the second fix
            second_fixed_content = re.sub(second_fix_pattern, second_fix_replacement, fixed_content)
            
            # Check if the second pattern was matched and replaced
            if second_fixed_content == fixed_content:
                self.console.print("[yellow]Warning: Second pattern not found. Skipping this fix.[/]")
            else:
                fixed_content = second_fixed_content
            
            # Third fix: Update the message extraction for subsequent turns
            third_fix_pattern = re.compile(
                r'(# If all extraction methods failed, use a friendly default\s*'  # Comment before if statement
                r'if not actual_message or len\(actual_message\) < 5 or.*?)'  # If statement
                r'red_team_message = "That\'s interesting\. Can you tell me more about that\?"', re.DOTALL  # Pattern to replace
            )
            
            third_fix_replacement = r'''\1# Use different fallback messages based on the turn number to avoid repetition
                fallback_index = (turn - 1) % len(fallback_messages)
                red_team_message = fallback_messages[fallback_index]
                # Log the fallback for debugging
                print(f"[bold yellow]DEBUG: Using fallback message for turn {turn}: {red_team_message}[/]")'''

            # Apply the third fix
            third_fixed_content = re.sub(third_fix_pattern, third_fix_replacement, fixed_content)
            
            # Check if the third pattern was matched and replaced
            if third_fixed_content == fixed_content:
                self.console.print("[yellow]Warning: Third pattern not found. Skipping this fix.[/]")
            else:
                fixed_content = third_fixed_content

            # Only save if at least one fix was applied successfully
            if fixed_content != original_content:
                # Save the fixed content
                with open(self.target_file, 'w') as f:
                    f.write(fixed_content)
                self.console.print("[green]✓[/] Red teaming conversation module has been fixed successfully!")
            else:
                self.console.print("[yellow]No changes were made to the file. No patterns matched.[/]")
                return

            self.console.print("[green]✓[/] Red teaming conversation module has been fixed successfully!")
            self.console.print("\nChanges made:")
            self.console.print("  1. [bold]Fixed message extraction logic[/bold] for the initial prompt")
            self.console.print("  2. [bold]Added improved fallback mechanisms[/bold] to avoid empty messages")
            self.console.print("  3. [bold]Enhanced logging[/bold] to help debug message extraction issues")
            self.console.print("\nYou can test the fix with the command: [cyan]dravik redt test[/]")
            
        except Exception as e:
            self.console.print(f"[red]Error applying fixes: {str(e)}[/]")
            if self.backup_file.exists():
                self.console.print("[yellow]Restoring from backup...")
                try:
                    shutil.copy2(self.backup_file, self.target_file)
                    self.console.print("[green]Restored from backup successfully.")
                except Exception as restore_err:
                    self.console.print(f"[red]Error restoring from backup: {str(restore_err)}[/]")

    def test_red_teaming_module(self, model="distilbert/distilgpt2", target_type="ollama", target_id="gemma:2b", turns=3):
        """Test the red teaming conversation module"""
        self.console.print(Panel(
            "[bold]Red Teaming Conversation Module Test[/]",
            border_style="green"
        ))

        # Check if the necessary imports are available
        try:
            # Make sure we can import the run_red_teaming_conversation function
            from benchmark.conversation_red_teaming import run_red_teaming_conversation
        except ImportError:
            self.console.print("[red]Error: Required modules could not be imported![/]")
            self.console.print("[yellow]Please make sure the benchmark directory is in your Python path.[/]")
            self.console.print("[yellow]You may need to run this command from the project root directory.[/]")
            return

        self.console.print(f"Starting test with:")
        self.console.print(f"[cyan]Red Team Model:[/] {model}")
        self.console.print(f"[cyan]Target Type:[/] {target_type}")
        self.console.print(f"[cyan]Target ID:[/] {target_id}")
        self.console.print(f"[cyan]Conversation Turns:[/] {turns}")
        
        # Ask for confirmation
        if not inquirer.confirm("Continue with test?", default=True):
            self.console.print("[yellow]Test cancelled.[/]")
            return

        try:
            # Run the red teaming conversation
            # Using "advisor_model_path" same as model for simplicity in testing
            with self.console.status("[bold blue]Running red teaming conversation test...[/]", spinner="dots") as status:
                conversation = run_red_teaming_conversation(
                    hf_model_path=model,
                    advisor_model_path=model,
                    target_type=target_type,
                    target_id=target_id,
                    num_turns=turns,
                    use_cache=False,  # Don't use cache for testing
                    attack_vector="Crescendo"  # Use Crescendo as default attack vector
                )

            # Test success check
            if len(conversation) > 0:
                message_count = len([msg for msg in conversation if msg.startswith("[RedTeam]:")])
                if message_count > 0:
                    self.console.print("\n[green]✓[/] Test successful! Red team sent message(s).")
                    self.console.print(f"[dim]Total messages: {len(conversation)}, Red team messages: {message_count}[/]")
                else:
                    self.console.print("\n[yellow]⚠[/] Test complete, but no red team messages were detected.")
            else:
                self.console.print("\n[yellow]⚠[/] Test complete, but no conversation was recorded.")

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Test interrupted by user.[/]")
            return
            
        except ImportError as e:
            self.console.print(f"[red]Import error: {str(e)}[/]")
            self.console.print("[yellow]Please make sure all required packages are installed.[/]")
            self.console.print("You may need to install additional dependencies:")
            self.console.print("[dim]pip install transformers torch rich inquirer huggingface_hub openai[/]")
            return
            
        except Exception as e:
            self.console.print(f"[red]Error during test: {str(e)}[/]")
            self.console.print("[red]Test failed.[/]")
            # Print traceback for debugging
            import traceback
            self.console.print("\n[dim]Error details:[/]")
            self.console.print(f"[dim]{traceback.format_exc()}[/]")

if __name__ == "__main__":
    # Allow direct execution of this file for testing
    console = Console()
    console.print("[bold cyan]Red Teaming Fix CLI Module - Direct Execution[/]")
    console.print("[dim]This module should normally be run through the Dravik CLI.[/]")
    
    # Check arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        fix_cmd = RedTeamingFixCommands()
        fix_cmd.fix_red_teaming_module(create_backup=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Get optional arguments for test
        model = "distilbert/distilgpt2"
        target_type = "ollama"
        target_id = "gemma:2b"
        turns = 3
        
        # Check for model argument
        if len(sys.argv) > 3 and sys.argv[2] == "--model":
            model = sys.argv[3]
        # Check for target type argument
        if len(sys.argv) > 5 and sys.argv[4] == "--target":
            target_type = sys.argv[5]
        # Check for target ID argument
        if len(sys.argv) > 7 and sys.argv[6] == "--target-id":
            target_id = sys.argv[7]
            
        fix_cmd = RedTeamingFixCommands()
        fix_cmd.test_red_teaming_module(model, target_type, target_id, turns)
    else:
        console.print("""Usage:
  python fix_red_teaming.py --fix    # Fix issues in the conversation red teaming module
  python fix_red_teaming.py --test   # Test the conversation red teaming module""")
