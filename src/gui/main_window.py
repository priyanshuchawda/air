from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QMenuBar, QMenu, QAction, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
from src.gui.settings_dialog import SettingsDialog
from src.utils.visualizer import GestureVisualizer
from src.gui.config_dialog import ConfigDialog
 
class MainWindow(QMainWindow):
    def __init__(self, command_mapper):
        super().__init__()
        self.command_mapper = command_mapper
        self.visualizer = GestureVisualizer()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("AirTouch")
        self.setGeometry(100, 100, 1000, 800)

        # Create central widget and layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()

        # Create control panel
        control_panel = self.create_control_panel()
        main_layout.addLayout(control_panel)

        # Create video display
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.video_label)

        # Create status bar with fixed width
        self.status_label = QLabel("No gesture detected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumWidth(300)  # Set minimum width
        self.status_label.setMaximumWidth(500)  # Set maximum width
        main_layout.addWidget(self.status_label)

        # Setup video timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms = ~33 FPS

        # Store the current frame
        self.current_frame = None
        self.current_landmarks = None
        self.current_gesture = None

        # Set fixed size for video display
        self.display_width = 640  # Fixed display width
        self.display_height = 480  # Fixed display height
        self.video_label.setFixedSize(self.display_width, self.display_height)

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Add configuration action
        config_action = QAction('Settings', self)
        config_action.setShortcut('Ctrl+,')
        config_action.triggered.connect(self.show_config_dialog)
        file_menu.addAction(config_action)
        
        # Add exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')
        
        self.show_landmarks_action = QAction('Show Landmarks', self)
        self.show_landmarks_action.setCheckable(True)
        self.show_landmarks_action.setChecked(True)
        view_menu.addAction(self.show_landmarks_action)
        
        self.show_gesture_trail_action = QAction('Show Gesture Trail', self)
        self.show_gesture_trail_action.setCheckable(True)
        self.show_gesture_trail_action.setChecked(True)
        view_menu.addAction(self.show_gesture_trail_action)

    def create_control_panel(self):
        control_layout = QHBoxLayout()
        
        # Camera control buttons
        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        control_layout.addWidget(self.stop_button)
        
        # Add recording controls
        self.record_button = QPushButton("Record Gesture")
        self.record_button.clicked.connect(self.start_recording)
        control_layout.addWidget(self.record_button)
        
        self.stop_record_button = QPushButton("Stop Recording")
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.stop_record_button.setEnabled(False)
        control_layout.addWidget(self.stop_record_button)
        
        self.gesture_name_input = QLineEdit()
        self.gesture_name_input.setPlaceholderText("Enter gesture name")
        control_layout.addWidget(self.gesture_name_input)
        
        # Add paint mode toggle button
        self.paint_mode_button = QPushButton("Paint Mode")
        self.paint_mode_button.setCheckable(True)
        self.paint_mode_button.clicked.connect(self.toggle_paint_mode)
        control_layout.addWidget(self.paint_mode_button)
        
        return control_layout

    def show_settings(self):
        dialog = SettingsDialog(self.command_mapper, self)
        dialog.exec_()

    def start_camera(self):
        self.timer.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_camera(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def set_frame(self, frame, landmarks=None, gesture=None):
        self.current_frame = frame
        self.current_landmarks = landmarks
        self.current_gesture = gesture

    def update_frame(self):
        if self.current_frame is not None:
            frame = self.current_frame.copy()

            # Draw visualizations
            if self.show_landmarks_action.isChecked() and self.current_landmarks:
                frame = self.visualizer.draw_hand_landmarks(frame, self.current_landmarks)
            
            if self.show_gesture_trail_action.isChecked() and self.current_gesture:
                frame = self.visualizer.draw_gesture_feedback(
                    frame, self.current_gesture, self.current_landmarks)

            # Convert frame to Qt format
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(
                frame.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_RGB888
            )
            self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def update_status(self, gesture):
        if gesture:
            self.status_label.setText(f"Detected gesture: {gesture}")
            self.current_gesture = gesture 

    def start_recording(self):
        gesture_name = self.gesture_name_input.text()
        if gesture_name:
            self.gesture_recorder.start_recording(gesture_name)
            self.record_button.setEnabled(False)
            self.stop_record_button.setEnabled(True)
            self.status_label.setText("Recording gesture...")

    def stop_recording(self):
        if self.gesture_recorder.stop_recording():
            self.status_label.setText(f"Gesture '{self.gesture_name_input.text()}' recorded!")
        self.record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False) 

    def show_config_dialog(self):
        """Show the configuration dialog"""
        dialog = ConfigDialog(self.config_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            # Reload configuration
            self.apply_config_changes()
    
    def apply_config_changes(self):
        """Apply configuration changes"""
        # Update camera settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,
                    self.config_manager.settings['camera']['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,
                    self.config_manager.settings['camera']['height'])
        
        # Update gesture detector settings
        self.gesture_detector.update_thresholds(
            self.config_manager.settings['gestures'])
        
        # Update visualization settings
        self.show_landmarks = self.config_manager.settings['interface']['show_landmarks']
        self.show_gesture_path = self.config_manager.settings['interface']['show_gesture_path'] 

    def set_frame(self, frame):
        """Update the displayed frame while maintaining fixed size"""
        if frame is not None:
            # Convert frame to QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, 
                           QImage.Format_RGB888)
            
            # Scale image to fit display while maintaining aspect ratio
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.display_width, self.display_height, 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            
            # Update display
            self.video_label.setPixmap(scaled_pixmap)
            self.video_label.setAlignment(Qt.AlignCenter) 

    def toggle_paint_mode(self):
        """Toggle paint mode"""
        is_painting = self.command_mapper.toggle_painting_mode()
        self.paint_mode_button.setText("Exit Paint Mode" if is_painting else "Paint Mode")
        self.status_label.setText("Paint Mode: " + ("On" if is_painting else "Off")) 