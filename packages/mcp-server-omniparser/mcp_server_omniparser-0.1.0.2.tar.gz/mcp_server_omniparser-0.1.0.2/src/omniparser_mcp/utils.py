"""
Utility functions for logging, error handling, and common operations.
"""

import logging
import logging.handlers
import os
import traceback
import functools
from typing import Any, Dict, Optional, Callable
from pathlib import Path


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        Configured logger instance
    """
    log_config = config.get("logging", {})
    
    # Create logger
    logger = logging.getLogger("omniparser_mcp")
    logger.setLevel(getattr(logging, log_config.get("level", "INFO")))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    log_file = log_config.get("file")
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Rotating file handler
            max_size = log_config.get("max_size_mb", 10) * 1024 * 1024  # Convert MB to bytes
            backup_count = log_config.get("backup_count", 3)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_size, backupCount=backup_count
            )
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file}")
            
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {e}")
    
    return logger


def handle_exceptions(logger: Optional[logging.Logger] = None):
    """
    Decorator for handling exceptions in functions.
    
    Args:
        logger: Logger instance to use for error logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Error in {func.__name__}: {str(e)}"
                if logger:
                    logger.error(error_msg)
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                # Return error result in expected format
                return {
                    "success": False,
                    "error": str(e),
                    "function": func.__name__
                }
        return wrapper
    return decorator


def handle_async_exceptions(logger: Optional[logging.Logger] = None):
    """
    Decorator for handling exceptions in async functions.
    
    Args:
        logger: Logger instance to use for error logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Error in {func.__name__}: {str(e)}"
                if logger:
                    logger.error(error_msg)
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                # Return error result in expected format
                return {
                    "success": False,
                    "error": str(e),
                    "function": func.__name__
                }
        return wrapper
    return decorator


def validate_coordinates(x: int, y: int, screen_width: int, screen_height: int) -> bool:
    """
    Validate that coordinates are within screen bounds.
    
    Args:
        x: X coordinate
        y: Y coordinate
        screen_width: Screen width
        screen_height: Screen height
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    return 0 <= x <= screen_width and 0 <= y <= screen_height


def sanitize_window_title(title: str) -> str:
    """
    Sanitize window title for safe use in file paths and logging.
    
    Args:
        title: Window title to sanitize
        
    Returns:
        Sanitized title
    """
    # Remove or replace problematic characters
    sanitized = title.replace('/', '_').replace('\\', '_').replace(':', '_')
    sanitized = sanitized.replace('<', '_').replace('>', '_').replace('|', '_')
    sanitized = sanitized.replace('?', '_').replace('*', '_').replace('"', '_')
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100] + "..."
    
    return sanitized


def format_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Format an exception into a standardized error response.
    
    Args:
        error: Exception to format
        context: Additional context information
        
    Returns:
        Formatted error response dictionary
    """
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
        "traceback": traceback.format_exc() if hasattr(error, '__traceback__') else None
    }


def format_success_response(data: Any, message: str = "") -> Dict[str, Any]:
    """
    Format a successful operation into a standardized response.
    
    Args:
        data: Data to include in response
        message: Optional success message
        
    Returns:
        Formatted success response dictionary
    """
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return response


def retry_operation(max_retries: int = 3, delay: float = 1.0, 
                   logger: Optional[logging.Logger] = None):
    """
    Decorator for retrying operations that might fail temporarily.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        logger: Logger instance for retry logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        if logger:
                            logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        if logger:
                            logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


def safe_get_nested(data: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """
    Safely get a nested value from a dictionary using dot notation.
    
    Args:
        data: Dictionary to search in
        keys: Dot-separated key path (e.g., "config.automation.delay")
        default: Default value if key not found
        
    Returns:
        Value at the specified path or default
    """
    try:
        current = data
        for key in keys.split('.'):
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def ensure_directory_exists(path: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize performance timer.
        
        Args:
            operation_name: Name of the operation being timed
            logger: Logger instance for timing output
        """
        self.operation_name = operation_name
        self.logger = logger
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        """Start timing."""
        import time
        self.start_time = time.time()
        if self.logger:
            self.logger.debug(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log result."""
        import time
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if self.logger:
            if exc_type is None:
                self.logger.debug(f"Completed {self.operation_name} in {duration:.3f}s")
            else:
                self.logger.debug(f"Failed {self.operation_name} after {duration:.3f}s: {exc_val}")
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the timed operation."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
