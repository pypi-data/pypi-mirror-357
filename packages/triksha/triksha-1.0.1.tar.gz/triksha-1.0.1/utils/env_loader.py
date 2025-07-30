"""
Environment variable loader for Dravik - ensures API keys are set properly
"""
import os
import dotenv
from pathlib import Path
from rich.console import Console
from typing import Dict, Any, Optional
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('env_loader')

console = Console()

def load_environment(verbose: bool = False) -> Dict[str, Any]:
    """Load environment variables from .env file and ensure they're set properly"""
    # First try to load from .env file
    dotenv_paths = [
        Path("/home/ubuntu/dre/dravik/.env"),  # Correct project location
        Path.home() / "dre/dravik/.env",       # User home + project path
        Path.cwd() / ".env",                  # Current directory
        Path(".env"),                         # Relative path
        Path.home() / ".env"                 # User home directory
    ]
    
    loaded = False
    for dotenv_path in dotenv_paths:
        if dotenv_path.exists():
            dotenv.load_dotenv(dotenv_path)
            console.print(f"[dim]Loaded environment variables from {dotenv_path}[/]")
            loaded = True
            break
    
    # Use ApiKeyManager to load stored keys
    try:
        from utils.api_key_manager import get_api_key_manager
        api_manager = get_api_key_manager()
        
        # Keys will be loaded during initialization
        if verbose:
            logger.info("API key manager loaded stored keys")
    except ImportError:
        logger.warning("API key manager not available")
    
    # Get keys (from environment or loaded by ApiKeyManager)
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    huggingface_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if verbose:
        logger.info(f"OpenAI API Key: {'Found' if openai_key else 'Not Found'}")
        logger.info(f"Google API Key: {'Found' if google_key else 'Not Found'}")
        logger.info(f"HuggingFace API Key: {'Found' if huggingface_key else 'Not Found'}")
    
    # Make sure API library uses these keys too by setting default API keys
    try:
        import openai
        if hasattr(openai, 'api_key') and openai_key:
            openai.api_key = openai_key
    except ImportError:
        pass
        
    try:
        import google.generativeai as genai
        if hasattr(genai, 'configure') and google_key:
            genai.configure(api_key=google_key)
    except ImportError:
        pass
    
    # Return relevant keys
    return {
        "openai_key": openai_key,
        "google_key": google_key,
        "huggingface_key": huggingface_key,
        "default_model": os.getenv("DEFAULT_MODEL", "karanxa/Dravik"),
        "num_test_prompts": int(os.getenv("NUM_TEST_PROMPTS", "10")),
        "max_prompt_length": int(os.getenv("MAX_PROMPT_LENGTH", "512"))
    }

def get_api_key(service: str, verbose: bool = False) -> Optional[str]:
    """Get API key for specific service with logging"""
    try:
        # Try to use ApiKeyManager first
        from utils.api_key_manager import get_api_key_manager
        api_manager = get_api_key_manager()
        key = api_manager.get_key(service)
        
        if verbose:
            if key:
                logger.info(f"Found API key for {service} (from API key manager)")
            else:
                logger.warning(f"No API key found for {service} (from API key manager)")
        
        return key
    except ImportError:
        # Fall back to the old method if ApiKeyManager is not available
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY", 
            "gemini": "GOOGLE_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
            "hf": "HUGGINGFACE_API_KEY"
        }
        
        env_var = key_mapping.get(service.lower())
        if not env_var:
            logger.warning(f"Unknown service: {service}")
            return None
            
        key = os.getenv(env_var)
        
        if verbose:
            if key:
                logger.info(f"Found API key for {service} (from {env_var})")
            else:
                logger.warning(f"No API key found for {service} (from {env_var})")
        
        return key

def verify_env_setup() -> Dict[str, bool]:
    """Verify that the environment is set up correctly"""
    results = {
        "env_file_exists": False,
        "openai_key": False,
        "google_key": False,
        "huggingface_key": False
    }
    
    # Check env file
    env_path = Path(__file__).parent.parent / '.env'
    results["env_file_exists"] = env_path.exists()
    
    # Load dotenv explicitly
    if results["env_file_exists"]:
        dotenv.load_dotenv(env_path)
    
    # Try to use ApiKeyManager
    try:
        from utils.api_key_manager import get_api_key_manager
        api_manager = get_api_key_manager()
        
        # Check keys
        results["openai_key"] = bool(api_manager.get_key("openai"))
        results["google_key"] = bool(api_manager.get_key("google"))
        results["huggingface_key"] = bool(api_manager.get_key("huggingface"))
    except ImportError:
        # Fall back to environment variables
        results["openai_key"] = bool(os.getenv("OPENAI_API_KEY"))
        results["google_key"] = bool(os.getenv("GOOGLE_API_KEY"))  
        results["huggingface_key"] = bool(os.getenv("HUGGINGFACE_API_KEY"))
    
    # Print diagnostic info
    print("\n=== Environment Setup Verification ===")
    print(f".env file found: {results['env_file_exists']}")
    print(f"OpenAI API key: {'Found ✅' if results['openai_key'] else 'Missing ❌'}")
    print(f"Google API key: {'Found ✅' if results['google_key'] else 'Missing ❌'}")
    print(f"HuggingFace API key: {'Found ✅' if results['huggingface_key'] else 'Missing ❌'}")
    print("====================================")
    
    return results
