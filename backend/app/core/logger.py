import logging
import sys
from typing import Any, Dict, Optional
import json
from pathlib import Path
import os

class CustomFormatter(logging.Formatter):
    """
    Custom formatter for logs.
    """
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: grey + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class JSONFormatter(logging.Formatter):
    """
    JSON formatter for logs.
    """
    
    def format(self, record):
        log_record = {
            "time": self.formatTime(record),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "props"):
            log_record["props"] = record.props
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logger(
    name: str,
    level: int = logging.INFO,
    use_json: bool = False,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers.
    
    Args:
        name (str): Logger name
        level (int): Log level
        use_json (bool): Whether to use JSON formatter
        log_file (str, optional): Log file path
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter based on format type
    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(CustomFormatter())
    
    logger.addHandler(console_handler)
    
    # Add file handler if log file is provided
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        
        if use_json:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name, or create it if it doesn't exist.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger
    """
    return logging.getLogger(name) 