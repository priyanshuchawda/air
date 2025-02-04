import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import logging
# src/main.py
from src.core.hand_tracker import HandTracker
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QDialog
from .core.gesture_detector import GestureDetector
from .core.command_mapper import CommandMapper
from .gui.main_window import MainWindow
from .utils.optimizer import PerformanceOptimizer
from .config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

def setup_application_logging():
    """Setup application-specific logging"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Add file handler for application logs
    file_handler = logging.FileHandler(logs_dir / "airtouch.log")
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    # Set debug level for detailed logging
    logger.setLevel(logging.DEBUG)
    logger.debug("Application logging initialized")

def initialize_components(config_manager):
    """Initialize application components with configuration"""
    try:
        logger.debug("Initializing core components...")
        
        # Initialize core components
        command_mapper = CommandMapper()
        logger.debug("CommandMapper initialized")
        
        hand_tracker = HandTracker()
        logger.debug("HandTracker initialized")
        
        gesture_detector = GestureDetector(config_manager.settings)
        logger.debug("GestureDetector initialized")
        
        optimizer = PerformanceOptimizer(config_manager.settings)
        logger.debug("PerformanceOptimizer initialized")
        
        # Return initialized components
        return command_mapper, hand_tracker, gesture_detector, optimizer
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}", exc_info=True)
        raise

def setup_camera(config_manager):
    """Initialize camera with configured settings"""
    try:
        logger.debug("Setting up camera...")
        cap = cv2.VideoCapture(config_manager.settings['camera']['device_id'])
        if not cap.isOpened():
            raise RuntimeError("Failed to open camera")
            
        # Configure camera settings
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 
                config_manager.settings['camera']['width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 
                config_manager.settings['camera']['height'])
        cap.set(cv2.CAP_PROP_FPS,
                config_manager.settings['camera']['fps'])
        
        logger.debug("Camera setup complete")
        return cap
    except Exception as e:
        logger.error(f"Camera setup failed: {e}", exc_info=True)
        raise

def main():
    """Main application entry point"""
    try:
        setup_application_logging()
        logger.info("Starting AirTouch application...")
        
        # Initialize application
        app = QApplication(sys.argv)
        logger.debug("QApplication initialized")
        
        # Create configuration manager
        config_manager = ConfigManager()
        logger.info("Configuration loaded successfully")
        
        # Initialize components
        command_mapper, hand_tracker, gesture_detector, optimizer = \
            initialize_components(config_manager)
        logger.info("Components initialized successfully")
        
        # Create main window
        window = MainWindow(command_mapper)
        window.config_manager = config_manager
        logger.info("Main window created")
        
        # Setup camera
        cap = setup_camera(config_manager)
        logger.info("Camera setup complete")
        
        # Configure optimizer
        optimizer.set_output_size(
            config_manager.settings['camera']['width'],
            config_manager.settings['camera']['height']
        )
        optimizer.start()
        logger.info("Optimizer configured and started")
        
        def process_frame():
            """Process each frame from the camera"""
            try:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    return
                
                # Optimize frame
                frame = optimizer.optimize_frame(frame)
                
                # Process frame for hand detection
                frame, landmarks = hand_tracker.find_hands(frame)
                
                # Update status based on mode
                status_text = []
                
                # Add mode status
                if command_mapper.painting_mode:
                    status_text.append("Paint Mode - Pinch to draw")
                
                # Process gestures if not in painting mode
                if not command_mapper.painting_mode and landmarks:
                    gesture = gesture_detector.update(landmarks)
                    if gesture:
                        status_text.append(f"Gesture: {gesture}")
                        command_mapper.execute_command(gesture, landmarks)
                
                # Add performance metrics
                stats = optimizer.get_stats()
                status_text.append(f"FPS: {stats['fps']:.1f}")
                
                if config_manager.settings['interface']['debug_mode']:
                    status_text.append(
                        f"Scale: {stats['frame_scale']:.2f}, "
                        f"Skip: {stats['skip_frames']}, "
                        f"GPU: {'Yes' if stats['gpu_enabled'] else 'No'}"
                    )
                
                # Update interface
                window.status_label.setText(" | ".join(status_text))
                window.set_frame(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
            except Exception as e:
                logger.error(f"Error processing frame: {e}", exc_info=True)
        
        # Connect timer to frame processing
        window.timer.timeout.connect(process_frame)
        
        # Show window and start application
        window.show()
        logger.info("Application window displayed")
        
        # Start event loop
        return_code = app.exec_()
        
        # Cleanup
        cap.release()
        logger.info("Application shutdown complete")
        return return_code
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())