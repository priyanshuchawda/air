from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QAction, QMenuBar, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from src.config.config_manager import ConfigManager
from theme_manager import ThemeManager
from src.core.camera_controller import CameraController
from src.utils.error_handler import ErrorHandler
from src.utils.visualizer import GestureVisualizer
from src.gui.status_widget import StatusWidget
from src.gui.gesture_history_list import GestureHistoryList

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize Managers
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager()
        self.error_handler = ErrorHandler()
        self.camera_controller = CameraController(self)
        
        # Set up UI
        self.setWindowTitle("AirTouch - Hand Gesture Controller")
        self.setAccessibleName("Main Application Window")
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Video feed label
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_label)
        
        # Status Widget
        self.status_widget = StatusWidget()
        self.layout.addWidget(self.status_widget)
        
        # Gesture Visualizer
        self.gesture_visualizer = GestureVisualizer()
        self.layout.addWidget(self.gesture_visualizer)
        
        # Gesture History List
        self.gesture_history_list = GestureHistoryList()
        self.layout.addWidget(self.gesture_history_list)
        
        # Menu Bar Setup
        self.setup_menu_bar()
        
        # Camera Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Load Theme
        self.theme_manager.apply_theme(self)
        
        # Start Camera
        self.start_camera()
        
    def setup_menu_bar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        
        # File Menu
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings Menu
        settings_menu = menubar.addMenu("Settings")
        config_action = QAction("Configuration", self)
        config_action.triggered.connect(self.open_config_dialog)
        settings_menu.addAction(config_action)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
    def start_camera(self):
        if self.camera_controller.start():
            self.timer.start(30)
        else:
            self.error_handler.display_error("Failed to start the camera.")
    
    def stop_camera(self):
        self.timer.stop()
        self.camera_controller.stop()
    
    def update_frame(self):
        frame = self.camera_controller.get_frame()
        if frame is not None:
            image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(image))
        else:
            self.error_handler.display_error("Failed to retrieve camera frame.")
    
    def open_config_dialog(self):
        self.config_manager.open_config_dialog(self)
    
    def show_about_dialog(self):
        QMessageBox.about(self, "About AirTouch", "Hand Gesture Control Application v1.0")
    
    def closeEvent(self, event):
        self.stop_camera()
        event.accept()
