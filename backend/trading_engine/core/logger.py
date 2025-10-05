"""
Logging configuration for the trading engine.
"""
import sys
from pathlib import Path
from loguru import logger

from config import settings


def setup_logger():
    """Configure logger with appropriate settings."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )
    
    # File handler if enabled
    if settings.log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Main log file
        logger.add(
            log_dir / "trading_engine.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.log_level,
            rotation="100 MB",
            retention="30 days",
            compression="zip",
        )
        
        # Error log file
        logger.add(
            log_dir / "errors.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="50 MB",
            retention="90 days",
            compression="zip",
        )
        
        # Trading activity log
        logger.add(
            log_dir / "trading_activity.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            level="INFO",
            rotation="50 MB",
            retention="365 days",
            compression="zip",
            filter=lambda record: "TRADE" in record["extra"],
        )
    
    logger.info(f"Logger initialized with level: {settings.log_level}")
    logger.info(f"Trading mode: {settings.trading_mode}")


def get_trade_logger():
    """Get logger for trading activity."""
    return logger.bind(TRADE=True)
