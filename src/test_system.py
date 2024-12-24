import cv2
import sys
from PyQt5.QtWidgets import QApplication
from core.hand_tracker import HandTracker
from core.gesture_detector import GestureDetector
from core.command_mapper import CommandMapper
from gui.main_window import MainWindow
from utils.optimizer import PerformanceOptimizer
from utils.gesture_recorder import GestureRecorder
from utils.visualizer import GestureVisualizer

def test_system():
    # Initialize components
    app = QApplication(sys.argv)
    command_mapper = CommandMapper()
    hand_tracker = HandTracker()
    gesture_detector = GestureDetector()
    optimizer = PerformanceOptimizer()
    gesture_recorder = GestureRecorder()
    
    # Create main window
    window = MainWindow(command_mapper)
    window.gesture_recorder = gesture_recorder
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    optimizer.start()

    def process_frame():
        ret, frame = cap.read()
        if ret:
            # Optimize frame
            frame = optimizer.optimize_frame(frame)
            
            # Process frame
            frame, landmarks = hand_tracker.find_hands(frame)
            gesture = gesture_detector.update(landmarks)
            
            # Record gesture if recording
            if gesture_recorder.recording:
                gesture_recorder.add_frame(landmarks)
            
            # Execute command if gesture detected
            if gesture:
                command_mapper.execute_command(gesture)
            
            # Update GUI
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            window.set_frame(frame_rgb, landmarks, gesture)
            window.update_status(f"Gesture: {gesture} (FPS: {optimizer.get_fps():.1f})")

    # Connect timer to frame processing
    window.timer.timeout.connect(process_frame)
    
    # Show window and start application
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_system()) 