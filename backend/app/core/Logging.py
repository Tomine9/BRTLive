import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import asyncio
from functools import wraps

def setup_logging(level: str = "INFO", log_to_file: bool = True):
    """
    Setup application logging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to write logs to file
    """
    
    handlers = []
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    handlers.append(console_handler)
    
    # File handler (optional)
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"brtlive_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=handlers,
        force=True  # Override any existing config
    )
    
    # Quiet noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module"""
    return logging.getLogger(name)

# Async logging wrapper
async def async_log(logger: logging.Logger, level: str, message: str):
    """
    Log message asynchronously (runs in executor to avoid blocking)
    
    Args:
        logger: Logger instance
        level: Log level (info, error, warning, debug)
        message: Message to log
    """
    loop = asyncio.get_event_loop()
    log_func = getattr(logger, level.lower())
    await loop.run_in_executor(None, log_func, message)

# Async decorator for logging function calls
def async_log_calls(logger: Optional[logging.Logger] = None):
    """
    Decorator to log async function calls
    
    Usage:
        @async_log_calls()
        async def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)

            logger.info("Calling %s", func.__name__)
            try:
                result = await func(*args, **kwargs)
                logger.info("✅ %s completed", func.__name__)
                return result
            except Exception as e:
                logger.error("❌ %s failed: %s", func.__name__, e)
                raise
        return wrapper
    return decorator

# Context manager for async logging
class AsyncLogContext:
    """
    Context manager for logging async operations
    
    Usage:
        async with AsyncLogContext("Creating bus", logger):
            # do work
            pass
    """
    def __init__(self, operation: str, logger: logging.Logger):
        self.operation = operation
        self.logger = logger
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = asyncio.get_event_loop().time()
        self.logger.info(f"Starting: {self.operation}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = asyncio.get_event_loop().time() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"✅ Completed: {self.operation} ({duration:.2f}s)")
        else:
            self.logger.error(f"❌ Failed: {self.operation} ({duration:.2f}s) - {exc_val}")
        
        return False  # Don't suppress exceptions