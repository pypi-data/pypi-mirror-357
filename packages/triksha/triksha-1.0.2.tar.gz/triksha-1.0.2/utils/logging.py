"""Logging utilities for scripts"""
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dataset_fix.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("dravik")

def log_info(message):
    """Log an info message"""
    logger.info(message)
    
def log_success(message):
    """Log a success message"""
    logger.info(f"SUCCESS: {message}")
    
def log_error(message):
    """Log an error message"""
    logger.error(message)
    
def log_warning(message):
    """Log a warning message"""
    logger.warning(message) 