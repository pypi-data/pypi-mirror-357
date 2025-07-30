"""Utility functions for handling Rich text formatting"""
import re
from typing import Any

def escape_rich_markup(text: Any) -> str:
    """
    Escape Rich markup characters in text to prevent rendering errors.
    
    Args:
        text: Text to escape (will be converted to string)
        
    Returns:
        Escaped text safe for Rich console output
    """
    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)
    
    # More aggressive escaping to handle all potential markup characters
    # Replace [ with \[ and ] with \]
    escaped = text.replace("[", "\\[").replace("]", "\\]")
    
    # Handle other potential markup-like patterns
    escaped = re.sub(r"@\w+", lambda m: f"\\{m.group(0)}", escaped)  # @mentions
    escaped = re.sub(r"#\w+", lambda m: f"\\{m.group(0)}", escaped)  # #hashtags
    
    return escaped

def safe_rich_print(console, content: Any, **kwargs):
    """
    Safely print content through Rich console by escaping markup.
    
    Args:
        console: Rich console instance
        content: Content to print
        **kwargs: Additional kwargs for console.print
    """
    if isinstance(content, str):
        # Ensure content is printed as literal text with no markup interpretation
        console.print(escape_rich_markup(content), markup=False, **kwargs)
    else:
        # For non-string content, first convert to string then escape
        console.print(escape_rich_markup(str(content)), markup=False, **kwargs)
