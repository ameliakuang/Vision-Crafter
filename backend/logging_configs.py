import os
import logging
from datetime import datetime

def setup_logging():
    """Configure logging to write to logs directory in project root"""
    # Get the project root directory (parent of backend)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, 'logs')
    
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f'vision_crafter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file)
        ]
    )
    
    # Set third-party loggers to WARNING level to reduce noise
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
