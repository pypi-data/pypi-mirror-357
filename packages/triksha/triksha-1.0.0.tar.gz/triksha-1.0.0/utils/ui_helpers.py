"""UI helper utilities for better input handling in CLI"""
import inquirer
from rich.console import Console
from typing import Optional, Dict, Any, List

def get_pasted_input(message: str, default: str = "", validate: Optional[callable] = None) -> str:
    """
    Enhanced input handler that properly manages pasted content.
    
    This function provides a better alternative to inquirer.Text for cases where
    users might paste lengthy content. It properly handles the paste operation
    and prevents multiple prompt repetitions.
    
    Args:
        message: The prompt message to display
        default: Default value if user provides empty input
        validate: Optional validation function
    
    Returns:
        The input string from the user
    """
    console = Console()
    
    # Display the prompt with rich formatting
    prompt_text = f"[bold cyan]?[/] [bold]{message}[/]"
    if default:
        prompt_text += f" [dim](default: {default})[/]"
    prompt_text += ": "
    
    console.print(prompt_text, end="")
    
    # Get raw input which handles pasting better than inquirer
    value = input()
    
    # Use default if empty
    if not value.strip() and default:
        value = default
    
    # Validate if a validation function was provided
    if validate and value:
        valid, message = validate(value)
        while not valid:
            console.print(f"[bold red]Invalid input: {message}[/]")
            console.print(prompt_text, end="")
            value = input()
            if not value.strip() and default:
                value = default
                break
            valid, message = validate(value)
    
    return value

def create_inquirer_list(message: str, choices: List, default=None):
    """Create a standard inquirer list with consistent styling"""
    return inquirer.List('result', message=message, choices=choices, default=default)

def create_inquirer_confirm(message: str, default: bool = True):
    """Create a standard inquirer confirmation with consistent styling"""
    return inquirer.Confirm('result', message=message, default=default)

def get_dataset_name(message: str = "Enter HuggingFace dataset name", 
                     default: str = "", 
                     examples: List[str] = None) -> str:
    """
    Get a dataset name input with special handling for pasted content.
    
    Args:
        message: The prompt message
        default: Default dataset name
        examples: Optional list of example datasets to show
    
    Returns:
        Dataset name input by the user
    """
    console = Console()
    
    # Show examples if provided
    if examples:
        console.print("[dim]Examples:[/]")
        for example in examples[:3]:
            console.print(f"[dim]  • {example}[/]")
    
    # Custom validator for dataset names
    def validate_dataset(value):
        if not value or not value.strip():
            return False, "Dataset name cannot be empty"
        if len(value.split("/")) < 2 and "/" not in value:
            return False, "Dataset should be in format 'username/dataset'"
        return True, ""
    
    # Get input with paste handling
    return get_pasted_input(
        message=message,
        default=default,
        validate=validate_dataset
    )
