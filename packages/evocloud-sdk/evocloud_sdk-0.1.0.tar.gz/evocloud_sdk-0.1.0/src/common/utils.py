"""
EVO Cloud SDK Utilities

Common utility functions for working with the EVO Cloud SDK.
"""

import time
import uuid
import json
import logging
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Union
from functools import wraps



logger = logging.getLogger(__name__)


def generate_order_id(prefix: str = "ORDER") -> str:
    """
    Generate a unique order ID.
    
    Args:
        prefix: Prefix for the order ID
        
    Returns:
        Unique order ID string
    """
    timestamp = int(time.time())
    random_part = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{random_part}"

def generate_trace_id() -> str:
    """
    Generate a unique trace ID.
    
    Returns:
        Unique trace ID string
    """
    return str(uuid.uuid4())

def format_amount(amount: Union[int, float, str], decimals: int = 2) -> str:
    """
    Format amount to string with proper decimal places.
    
    Args:
        amount: Amount to format
        decimals: Number of decimal places
        
    Returns:
        Formatted amount string
    """
    if isinstance(amount, str):
        amount = float(amount)
    return f"{amount:.{decimals}f}"

def validate_webhook_headers(headers: Dict[str, str]) -> bool:
    """
    Validate that webhook headers contain required fields.
    
    Args:
        headers: HTTP headers from webhook request
        
    Returns:
        True if headers are valid, False otherwise
    """
    required_headers = ["Authorization", "DateTime", "MsgID", "SignType"]
    
    # Check case-insensitive
    header_keys = [key.lower() for key in headers.keys()]
    
    for required in required_headers:
        if required.lower() not in header_keys:
            logger.warning(f"Missing required header: {required}")
            return False
    
    return True


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for retrying function calls on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each failure
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    logger.info(f"Retrying in {current_delay:.1f} seconds...")
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
        return wrapper
    return decorator


def log_api_call(func):
    """
    Decorator to log API calls with timing information.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        function_name = func.__name__
        
        try:
            logger.info(f"Starting {function_name}")
            result = func(*args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"{function_name} completed successfully in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"{function_name} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper


def configure_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """
    Configure logging for the EVO Cloud SDK.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger.info(f"Logging configured with level: {level}")


def get_beijing_time() -> datetime:
    """
    Get current Beijing time (UTC+8).
    
    Returns:
        Current Beijing time as datetime object
    """
    beijing_tz = timezone(timedelta(hours=8))
    return datetime.now(beijing_tz)


def parse_evo_datetime(datetime_str: str) -> Optional[datetime]:
    """
    Parse EVO Cloud datetime string to datetime object.
    
    Args:
        datetime_str: DateTime string in EVO Cloud format
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not datetime_str:
        return None
    
    # Common EVO Cloud datetime formats
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",      # ISO format with timezone
        "%Y-%m-%dT%H:%M:%SZ",       # ISO format with Z
        "%Y-%m-%dT%H:%M:%S",        # ISO format without timezone
        "%Y-%m-%d %H:%M:%S",        # Standard format
        "%Y%m%d%H%M%S",             # Compact format
    ]
    
    for fmt in formats:
        try:
            if fmt == "%Y-%m-%dT%H:%M:%SZ":
                # Handle Z timezone indicator
                return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Unable to parse datetime string: {datetime_str}")
    return None

