import sys
import cv2
from PyQt5.QtWidgets import QApplication
from core.hand_tracker import HandTracker
from core.gesture_detector import GestureDetector
from core.command_mapper import CommandMapper
from gui.main_window import MainWindow
from utils.optimizer import PerformanceOptimizer
from config.config_manager import ConfigManager

def main():
    # Initialize components
    app = QApplication(sys.argv)
    
    # Create configuration manager
    config_manager = ConfigManager()
    
    # Initialize components with configuration
    command_mapper = CommandMapper(config_manager.gesture_mappings_file)
    window = MainWindow(command_mapper)
    window.config_manager = config_manager
    
    hand_tracker = HandTracker()
    gesture_detector = GestureDetector()
    optimizer = PerformanceOptimizer()
    
    # Initialize video capture with configured settings
    cap = cv2.VideoCapture(config_manager.settings['camera']['device_id'])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 
            config_manager.settings['camera']['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 
            config_manager.settings['camera']['height'])
    
    # Set optimizer output size to match display
    optimizer.set_output_size(
        config_manager.settings['camera']['width'],
        config_manager.settings['camera']['height']
    )
    
    # Start performance optimization
    optimizer.start()

    def process_frame():
        ret, frame = cap.read()
        if ret:
            # Optimize frame
            frame = optimizer.optimize_frame(frame)
            
            # Process frame
            frame, landmarks = hand_tracker.find_hands(frame)
            gesture = gesture_detector.update(landmarks)
            
            if gesture:
                window.update_status(f"Gesture: {gesture} (FPS: {optimizer.get_fps():.1f})")
                command_mapper.execute_command(gesture)
            
            # Update GUI with the new frame
            window.set_frame(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            window.update_frame()

    # Connect timer to frame processing
    window.timer.timeout.connect(process_frame)
    
    # Show window and start application
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 