"""Logging Configuration"""
import logging
import sys
from pathlib import Path

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Get logger
logger = logging.getLogger(__name__)
logger.info("Logging configured")