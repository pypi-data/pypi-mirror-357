"""
API Key Prompt Helpers

Helper functions for prompting for API keys throughout the application.
"""
import inquirer
from rich.console import Console
from typing import Optional, Callable
from utils.api_key_manager import get_api_key_manager

console = Console()

def prompt_for_missing_api_key(service: str, env_var: str, description: str = None) -> Optional[str]:
    """
    Prompt user for a missing API key and store it in the API Key Manager.
    
    Args:
        service: Service name (e.g., "openai", "google")
        env_var: Environment variable name (e.g., "OPENAI_API_KEY")
        description: Optional description of what the key is used for
    
    Returns:
        The API key if provided, or None if not
    """
    api_manager = get_api_key_manager()
    
    # First try to get the key from the manager
    api_key = api_manager.get_key(service)
    if api_key:
        return api_key
    
    # If no key was found, prompt the user
    console.print(f"[yellow]API key for {service.upper()} not found.[/]")
    if description:
        console.print(f"[dim]{description}[/]")
    
    # Ask if the user wants to provide the key now
    provide_key = inquirer.prompt([
        inquirer.Confirm(
            'confirm',
            message=f"Do you want to provide the {service.upper()} API key now?",
            default=True
        )
    ])
    
    if not provide_key or not provide_key['confirm']:
        return None
    
    # Prompt for the key
    api_key_prompt = inquirer.prompt([
        inquirer.Password(
            'api_key',
            message=f"Enter your {service.upper()} API key",
            validate=lambda _, x: len(x.strip()) > 0
        )
    ])
    
    if not api_key_prompt or not api_key_prompt['api_key']:
        return None
    
    api_key = api_key_prompt['api_key'].strip()
    
    # Store the key
    api_manager.store_key(service, api_key)
    console.print(f"[green]API key for {service.upper()} stored. It will be used for future operations.[/]")
    
    return api_key

def ensure_api_key(service: str, description: str = None) -> Optional[str]:
    """
    Ensure an API key is available, prompting if needed.
    
    Args:
        service: Service name (e.g., "openai", "google")
        description: Optional description of what the key is used for
    
    Returns:
        The API key if available or provided, or None if not
    """
    # Get the API key manager
    api_manager = get_api_key_manager()
    
    # Try to get the API key
    api_key = api_manager.get_key(service)
    
    # If key not found, prompt the user
    if not api_key:
        # Display friendly service name
        display_name = {
            "openai": "OpenAI",
            "google": "Google/Gemini",
            "gemini": "Google/Gemini",
            "huggingface": "HuggingFace",
            "hf": "HuggingFace",
            "anthropic": "Anthropic"
        }.get(service.lower(), service.upper())
        
        console.print(f"[yellow]The {display_name} API key is required for this operation.[/]")
        if description:
            console.print(f"[dim]{description}[/]")
        
        # Find the environment variable for this service
        from utils.api_key_manager import KEY_MAPPING
        env_var = KEY_MAPPING.get(service.lower(), f"{service.upper()}_API_KEY")
        
        # Prompt for the key
        api_key = prompt_for_missing_api_key(service, env_var, description)
    
    return api_key

def with_api_key(service: str, callback: Callable[[str], None], description: str = None) -> bool:
    """
    Execute a callback with an API key, prompting if needed.
    
    Args:
        service: Service name (e.g., "openai", "google")
        callback: Function to call with the API key
        description: Optional description of what the key is used for
    
    Returns:
        True if the callback was executed with a key, False otherwise
    """
    api_key = ensure_api_key(service, description)
    
    if not api_key:
        console.print(f"[red]Operation canceled. API key for {service.upper()} is required.[/]")
        return False
    
    # Execute the callback with the API key
    callback(api_key)
    return True 