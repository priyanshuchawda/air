import sys
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting import test")

try:
    logger.debug("Importing config_manager")
    from src.config.config_manager import ConfigManager
    logger.debug("ConfigManager imported successfully")

    logger.debug("Importing hand_tracker")
    from src.core.hand_tracker import HandTracker
    logger.debug("HandTracker imported successfully")

    logger.debug("Importing gesture_detector")
    from src.core.gesture_detector import GestureDetector
    logger.debug("GestureDetector imported successfully")

    logger.debug("Importing main_window")
    from src.gui.main_window import MainWindow
    logger.debug("MainWindow imported successfully")

    logger.debug("All imports successful!")
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)