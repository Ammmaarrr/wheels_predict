import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

def setup_logger(name, log_file=None, level=logging.INFO):
    """Set up a logger with console and file handlers.
    
    Args:
        name (str): Logger name (usually __name__ of the calling module)
        log_file (str, optional): Path to log file. If None, uses {name}.log
        level (int, optional): Logging level. Defaults to INFO.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    if log_file is None:
        log_file = os.path.join(logs_dir, f"{name}.log")
    
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation (10MB max size, keep 5 backup files)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Alias for backward compatibility and convenience
def get_logger(name, log_file=None, level=logging.INFO):
    """Get a logger instance - alias for setup_logger.
    
    Args:
        name (str): Logger name (usually __name__ of the calling module)
        log_file (str, optional): Path to log file. If None, uses {name}.log
        level (int, optional): Logging level. Defaults to INFO.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger(name, log_file, level)

# Custom exception for API errors
class APIError(Exception):
    """Custom exception for API-related errors."""
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def log_error(logger, error, additional_info=None):
    """Standardized error logging function.
    
    Args:
        logger (logging.Logger): Logger instance
        error (Exception): The error to log
        additional_info (dict, optional): Additional context about the error
    """
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'additional_info': additional_info or {}
    }
    logger.error(f"Error occurred: {error_info}", exc_info=True)
