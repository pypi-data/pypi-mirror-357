"""Utility for fixing transformers installation issues"""
import os
import sys
import subprocess
import importlib
import logging
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict

logger = logging.getLogger(__name__)

def check_transformers() -> Tuple[bool, Optional[str]]:
    """
    Check if transformers is installed and get version
    
    Returns:
        (installed, version) tuple
    """
    try:
        import transformers
        return True, transformers.__version__
    except ImportError:
        return False, None

def get_transformers_path() -> Optional[str]:
    """
    Get the installation path of transformers
    
    Returns:
        Path to transformers or None if not found
    """
    try:
        import transformers
        return str(Path(transformers.__file__).parent)
    except ImportError:
        return None

def check_gemma_modules() -> Dict[str, bool]:
    """
    Check for Gemma-related modules in transformers
    
    Returns:
        Dictionary of module paths and whether they exist
    """
    transformers_path = get_transformers_path()
    if not transformers_path:
        return {}
    
    # Modules to check
    modules = {
        "models/gemma": False,
        "models/gemma/tokenization_gemma.py": False,
        "models/gemma/modeling_gemma.py": False,
        "models/gemma/configuration_gemma.py": False
    }
    
    # Check each module
    for module_path in modules:
        full_path = os.path.join(transformers_path, module_path)
        modules[module_path] = os.path.exists(full_path)
    
    return modules

def install_latest_transformers() -> bool:
    """
    Install the latest version of transformers from PyPI
    
    Returns:
        True if successful
    """
    try:
        logger.info("Installing latest transformers from PyPI...")
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "transformers"]
        
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            logger.info("Successfully installed latest transformers from PyPI")
            return True
        else:
            logger.error(f"Failed to install transformers from PyPI: {process.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error installing transformers: {e}")
        return False

def install_transformers_from_git() -> bool:
    """
    Install transformers from GitHub
    
    Returns:
        True if successful
    """
    try:
        logger.info("Installing transformers from GitHub...")
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "git+https://github.com/huggingface/transformers.git"]
        
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            logger.info("Successfully installed transformers from GitHub")
            return True
        else:
            logger.error(f"Failed to install transformers from GitHub: {process.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error installing transformers from GitHub: {e}")
        return False

def fix_gemma_tokenizer_import() -> bool:
    """
    Try to fix Gemma tokenizer import issues
    
    Returns:
        True if successfully fixed
    """
    try:
        installed, version = check_transformers()
        
        if not installed:
            logger.error("Transformers is not installed")
            logger.info("Installing transformers...")
            return install_latest_transformers()
        
        logger.info(f"Transformers is installed (version {version})")
        
        # Check if transformers version is recent enough
        major, minor, patch = map(int, version.split('.')[:3])
        
        # Check Gemma module paths
        modules = check_gemma_modules()
        logger.info(f"Gemma modules status: {modules}")
        
        missing_modules = [m for m, exists in modules.items() if not exists]
        
        if missing_modules:
            logger.warning(f"Missing Gemma modules: {', '.join(missing_modules)}")
            
            # If version is too old or modules are missing, update
            if major < 4 or (major == 4 and minor < 38):
                logger.info(f"Transformers version {version} is too old for Gemma-3, updating...")
                if install_latest_transformers():
                    # Check if modules are now available
                    if not all(check_gemma_modules().values()):
                        logger.warning("Still missing Gemma modules after update, trying from GitHub...")
                        return install_transformers_from_git()
                    return True
                else:
                    logger.warning("Failed to update transformers, trying from GitHub...")
                    return install_transformers_from_git()
            else:
                # If version should be new enough but modules are missing, try GitHub
                logger.warning("Transformers version should be new enough but Gemma modules are missing")
                logger.info("Installing from GitHub to fix...")
                return install_transformers_from_git()
        else:
            logger.info("All Gemma modules appear to be present")
            return True
    except Exception as e:
        logger.error(f"Error fixing Gemma tokenizer import: {e}")
        return False

def reload_transformers_modules():
    """
    Reload transformers modules to pick up changes
    """
    try:
        logger.info("Reloading transformers modules...")
        
        # Find all transformers modules in sys.modules
        transformers_modules = [m for m in list(sys.modules.keys()) if m.startswith('transformers')]
        
        # Remove them from sys.modules
        for module in transformers_modules:
            del sys.modules[module]
        
        # Import transformers again
        import transformers
        logger.info(f"Reloaded transformers (version {transformers.__version__})")
    except Exception as e:
        logger.error(f"Error reloading transformers modules: {e}")

def fix_transformers_installation() -> bool:
    """
    Main function to fix transformers installation
    
    Returns:
        True if successful
    """
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Check current installation
        installed, version = check_transformers()
        logger.info(f"Transformers installed: {installed}, version: {version}")
        
        # Fix Gemma tokenizer import
        if fix_gemma_tokenizer_import():
            # Reload modules
            reload_transformers_modules()
            
            # Final check
            modules = check_gemma_modules()
            if all(modules.values()):
                logger.info("Successfully fixed Gemma tokenizer import issue")
                return True
            else:
                missing = [m for m, exists in modules.items() if not exists]
                logger.warning(f"Still missing some Gemma modules: {missing}")
                return False
        else:
            logger.error("Failed to fix Gemma tokenizer import issue")
            return False
    except Exception as e:
        logger.error(f"Error fixing transformers installation: {e}")
        return False

if __name__ == "__main__":
    # Setup basic logging when run as script
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Checking transformers installation for Gemma-3 compatibility...")
    success = fix_transformers_installation()
    
    if success:
        print("Successfully fixed transformers installation")
    else:
        print("Failed to fix transformers installation")
        print("Please try manually running:")
        print("  pip install --upgrade git+https://github.com/huggingface/transformers.git")
