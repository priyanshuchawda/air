import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting AirTouch application...")
        logger.debug(f"Python path: {sys.path}")
        logger.debug(f"Project root: {project_root}")
        
        # Import and run main
        logger.debug("Importing main module...")
        from src.main import main
        
        logger.info("Initialization complete, running main()...")
        sys.exit(main())
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)