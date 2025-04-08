"""
Logging utilities for Mixxx AI DJ Copilot.

This module provides a comprehensive logging system that can be used throughout the application.
It supports console and file logging with rotating file handlers, custom formatting,
component-specific log levels, and contextual logging.

Usage:
    from utils.logging_utils import get_logger
    
    # Get a logger for a specific component
    logger = get_logger('data_capture')
    
    # Use the logger
    logger.debug("Detailed debugging information")
    logger.info("General information")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical error message")
    
    # Contextual logging
    with logger.context(track_id='123', session_id='abc'):
        logger.info("This log will include track_id and session_id context")
"""

import json
import logging
import logging.handlers
import os
import sys
import threading
import time
from functools import wraps
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable

# Thread local storage for context variables
_context_storage = threading.local()


class ContextualLogger(logging.Logger):
    """
    Extended Logger class that supports context-based logging.
    Allows adding contextual information to log messages using a context manager.
    """
    
    def __init__(self, name, level=logging.NOTSET):
        """Initialize the contextual logger."""
        super().__init__(name, level)
        
    def _get_context(self) -> Dict[str, Any]:
        """Retrieve the current context from thread-local storage."""
        if not hasattr(_context_storage, 'context'):
            _context_storage.context = {}
        return _context_storage.context.copy()
    
    def context(self, **kwargs):
        """
        Context manager for adding context to log messages.
        
        Args:
            **kwargs: Context variables to add to log messages within this context.
            
        Example:
            with logger.context(user_id='123', action='login'):
                logger.info('User logged in')  # Log will include user_id and action
        """
        return LoggingContext(**kwargs)
    
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        """
        Override _log to include context information.
        This is called by all logging methods (debug, info, etc.).
        """
        if extra is None:
            extra = {}
        
        # Add context to extra
        context = self._get_context()
        if context:
            context_str = ' '.join(f"{k}={v}" for k, v in context.items())
            msg = f"{msg} [{context_str}]"
        
        # Call the original _log method
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel + 1)


class LoggingContext:
    """
    Context manager for adding context to log messages.
    Used by the ContextualLogger.context() method.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the logging context with provided key-value pairs.
        
        Args:
            **kwargs: Context variables to add to log messages.
        """
        self.old_context = {}
        self.new_context = kwargs
    
    def __enter__(self):
        """
        Enter the context, saving the old context and setting the new one.
        """
        if not hasattr(_context_storage, 'context'):
            _context_storage.context = {}
        
        # Save the old context
        self.old_context = _context_storage.context.copy()
        
        # Update with new context
        _context_storage.context.update(self.new_context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context, restoring the old context.
        """
        # Restore the old context
        _context_storage.context = self.old_context


class ColorFormatter(logging.Formatter):
    """
    Custom formatter that adds color to console output based on log level.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[91m\033[1m',  # Bold Red
        'RESET': '\033[0m'   # Reset to default
    }
    
    def __init__(self, fmt=None, datefmt=None, style='%', use_colors=True):
        """
        Initialize the color formatter.
        
        Args:
            fmt: Format string for log messages
            datefmt: Date format string
            style: Style of the format string (%, {, or $)
            use_colors: Whether to use colors in output (should be disabled for file logging)
        """
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors
    
    def format(self, record):
        """
        Format the log record, adding color codes if enabled.
        """
        # Make a copy of the record to avoid modifying the original
        record_copy = logging.makeLogRecord(record.__dict__)
        
        if self.use_colors and record_copy.levelname in self.COLORS:
            record_copy.levelname = f"{self.COLORS[record_copy.levelname]}{record_copy.levelname}{self.COLORS['RESET']}"
        
        return super().format(record_copy)


def configure_logging(config: Optional[Dict] = None) -> None:
    """
    Configure the logging system based on provided or default configuration.
    
    Args:
        config: Configuration dictionary. If None, reasonable defaults will be used.
    """
    # Default logging configuration
    default_log_config = {
        "level": "INFO",
        "console": {
            "enabled": True,
            "level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        },
        "file": {
            "enabled": True,
            "level": "DEBUG",
            "path": "logs",
            "filename": "dj_copilot.log",
            "max_size_mb": 10,
            "backup_count": 5,
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
        },
        "components": {
            "data_capture": "DEBUG",
            "analysis": "INFO",
            "recommendation": "INFO",
            "dj_generator": "INFO",
            "ui": "INFO",
            "external_api": "INFO"
        }
    }
    
    # Extract logging configuration - use app debug mode if available
    log_config = default_log_config
    
    if config is not None:
        # Override with any logging-specific config if present
        if 'logging' in config:
            log_config.update(config['logging'])
        
        # Set default level based on app debug mode if available
        if config.get('app', {}).get('debug_mode', False):
            if 'level' not in log_config:
                log_config['level'] = 'DEBUG'
            
            # Set component levels to DEBUG if not explicitly set
            if 'components' in log_config:
                for component, level in log_config['components'].items():
                    if level == 'INFO':
                        log_config['components'][component] = 'DEBUG'
    
    # Set the default level for all loggers
    root_level = getattr(logging, log_config.get('level', 'INFO'))
    root_logger = logging.getLogger()
    root_logger.setLevel(root_level)
    
    # Clear any existing handlers to avoid duplicates during reconfigurations
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
    
    # Replace the default Logger class with our ContextualLogger
    logging.setLoggerClass(ContextualLogger)
    
    # Configure console logging
    console_config = log_config.get('console', {})
    if console_config.get('enabled', True):
        console_handler = configure_console_handler(console_config)
        root_logger.addHandler(console_handler)
    
    # Configure file logging
    file_config = log_config.get('file', {})
    if file_config.get('enabled', True):
        file_handler = configure_file_handler(file_config)
        if file_handler:
            root_logger.addHandler(file_handler)
    
    # Configure component-specific loggers
    configure_component_loggers(log_config.get('components', {}))
    
    # Log configuration complete
    root_logger.debug("Logging system initialized")


def configure_console_handler(config: Dict) -> logging.Handler:
    """
    Configure and return a console handler based on configuration.
    
    Args:
        config: Console handler configuration dictionary.
        
    Returns:
        Configured console handler.
    """
    level = getattr(logging, config.get('level', 'INFO'))
    formatter_str = config.get('format', "%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    
    # Create console handler
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level)
    
    # Set formatter with colors
    formatter = ColorFormatter(formatter_str, use_colors=True)
    handler.setFormatter(formatter)
    
    return handler


def configure_file_handler(config: Dict) -> Optional[logging.Handler]:
    """
    Configure and return a rotating file handler based on configuration.
    
    Args:
        config: File handler configuration dictionary.
        
    Returns:
        Configured file handler, or None if configuration fails.
    """
    level = getattr(logging, config.get('level', 'DEBUG'))
    formatter_str = config.get('format', "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s")
    
    # Get log file path
    log_dir = Path(config.get('path', 'logs'))
    log_file = config.get('filename', 'dj_copilot.log')
    log_path = log_dir / log_file
    
    # Create log directory if it doesn't exist
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating log directory: {e}")
        return None
    
    # Create rotating file handler
    try:
        max_bytes = config.get('max_size_mb', 10) * 1024 * 1024  # Convert MB to bytes
        backup_count = config.get('backup_count', 5)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=str(log_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        handler.setLevel(level)
        
        # Set formatter without colors
        formatter = ColorFormatter(formatter_str, use_colors=False)
        handler.setFormatter(formatter)
        
        return handler
    except Exception as e:
        print(f"Error configuring file handler: {e}")
        return None


def configure_component_loggers(component_config: Dict) -> None:
    """
    Configure loggers for specific components based on configuration.
    
    Args:
        component_config: Component logger configuration dictionary.
    """
    for component, level_str in component_config.items():
        level = getattr(logging, level_str, logging.INFO)
        logger = logging.getLogger(component)
        logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific component.
    
    Args:
        name: Component name or logger name.
        
    Returns:
        Logger instance for the specified component.
    """
    return logging.getLogger(name)


def log_execution_time(logger=None, level=logging.DEBUG):
    """
    Decorator to log the execution time of a function.
    
    Args:
        logger: Logger to use. If None, a logger with the function's module name will be used.
        level: Logging level to use.
        
    Example:
        @log_execution_time()
        def slow_function():
            time.sleep(1)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger if not provided
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            # Log start and measure time
            start_time = time.time()
            logger.log(level, f"Starting {func.__name__}")
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Log completion time
                elapsed_time = time.time() - start_time
                logger.log(level, f"Completed {func.__name__} in {elapsed_time:.4f} seconds")
                
                return result
            except Exception as e:
                # Log exception
                elapsed_time = time.time() - start_time
                logger.exception(f"Exception in {func.__name__} after {elapsed_time:.4f} seconds: {str(e)}")
                raise
        
        return wrapper
    return decorator


def log_function_call(logger=None, level=logging.DEBUG, log_args=True, log_result=False):
    """
    Decorator to log function calls, optionally including arguments and return value.
    
    Args:
        logger: Logger to use. If None, a logger with the function's module name will be used.
        level: Logging level to use.
        log_args: Whether to log function arguments.
        log_result: Whether to log function return value.
        
    Example:
        @log_function_call(log_args=True, log_result=True)
        def add(a, b):
            return a + b
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger if not provided
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            # Prepare call information
            call_info = f"Calling {func.__name__}"
            
            # Log arguments if requested
            if log_args and (args or kwargs):
                args_str = ', '.join([repr(arg) for arg in args]) if args else ''
                kwargs_str = ', '.join([f"{k}={repr(v)}" for k, v in kwargs.items()]) if kwargs else ''
                
                # Combine args and kwargs strings
                params = []
                if args_str:
                    params.append(args_str)
                if kwargs_str:
                    params.append(kwargs_str)
                
                call_info += f" with args: {', '.join(params)}"
            
            # Log the call
            logger.log(level, call_info)
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Log the result if requested
            if log_result:
                # Limit result length for logging
                result_str = repr(result)
                if len(result_str) > 1000:
                    result_str = result_str[:1000] + "..."
                
                logger.log(level, f"{func.__name__} returned: {result_str}")
            
            return result
        
        return wrapper
    return decorator


def load_config_from_file(config_path: Union[str, Path]) -> Dict:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        Configuration dictionary.
        
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the configuration file contains invalid JSON.
    """
    config_path = Path(config_path)
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError:
        print(f"Invalid JSON in configuration file: {config_path}")
        raise


def initialize_logging(config_path: Optional[Union[str, Path]] = None) -> None:
    """
    Initialize the logging system with configuration from a file.
    
    Args:
        config_path: Path to the configuration file. If None, default configuration will be used.
    """
    try:
        if config_path:
            config = load_config_from_file(config_path)
            configure_logging(config)
        else:
            # Use default configuration
            configure_logging(None)
    except Exception as e:
        print(f"Error initializing logging: {e}")
        print("Using default logging configuration")
        configure_logging(None)


# Examples and usage of the module when run directly
if __name__ == "__main__":
    # Sample configuration to demonstrate integration with the app config
    example_config = {
        "app": {
            "name": "Mixxx AI DJ Copilot",
            "version": "0.1.0",
            "debug_mode": True
        },
        "logging": {
            "level": "INFO",
            "console": {
                "enabled": True,
                "level": "INFO"
            },
            "file": {
                "path": "example_logs",
                "filename": "example.log"
            },
            "components": {
                "data_capture": "DEBUG"
            }
        }
    }
    
    # Initialize logging with example configuration
    configure_logging(example_config)
    
    # Get loggers for different components
    main_logger = get_logger("main")
    data_logger = get_logger("data_capture")
    analysis_logger = get_logger("analysis")
    
    # Basic logging example
    main_logger.debug("This is a debug message")
    main_logger.info("This is an info message")
    main_logger.warning("This is a warning message")
    main_logger.error("This is an error message")
    
    # Context-based logging example
    with main_logger.context(user="test_user", operation="example"):
        main_logger.info("This log includes context information")
    
    # Nested context example
    with main_logger.context(session="123"):
        main_logger.info("Log with session context")
        
        with main_logger.context(track="456"):
            main_logger.info("Log with session and track context")
        
        main_logger.info("Back to just session context")
    
    # Example of component-specific logging levels
    data_logger.debug("Data capture debug message - should appear since level is DEBUG")
    analysis_logger.debug("Analysis debug message - might not appear depending on level")
    
    # Example of decorators
    @log_execution_time()
    def slow_function():
        time.sleep(0.5)
        return "Done"
    
    @log_function_call(log_args=True, log_result=True)
    def add(a, b):
        return a + b
    
    # Run the example functions
    slow_function()
    add(2, 3)
    
    print("Logging example completed. Check the example_logs directory for the log file.")