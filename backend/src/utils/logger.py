import sys
import os
from loguru import logger

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Remove default logger to prevent duplicates
logger.remove()

# Add console sink
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add rotating file sink
logger.add(
    "logs/ingestion.log",
    rotation="10 MB",
    retention="5 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

def get_logger():
    return logger
