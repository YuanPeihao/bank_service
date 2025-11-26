"""Logging configuration"""
import logging
import sys
from datetime import datetime

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create logger
logger = logging.getLogger("banking_api")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def log_request(method: str, path: str, **kwargs):
    """Log incoming HTTP request"""
    logger.info(f"Request: {method} {path}")


def log_operation(operation: str, account_id: int = None, **kwargs):
    """Log business operation"""
    account_info = f" account_id={account_id}" if account_id else ""
    logger.info(f"Operation: {operation}{account_info}")


def log_error(error: Exception, context: str = ""):
    """Log error with context"""
    context_info = f" - {context}" if context else ""
    logger.error(f"Error: {type(error).__name__}: {str(error)}{context_info}", exc_info=True)

