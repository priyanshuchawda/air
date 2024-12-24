from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QLabel, QSpinBox, QDoubleSpinBox, QCheckBox,
                            QPushButton, QComboBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt

class ConfigDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the configuration dialog UI"""
        self.setWindowTitle("AirTouch Configuration")
        self.setMinimumWidth(500)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_camera_tab(), "Camera")
        tabs.addTab(self._create_gestures_tab(), "Gestures")
        tabs.addTab(self._create_performance_tab(), "Performance")
        tabs.addTab(self._create_interface_tab(), "Interface")
        
        layout.addWidget(tabs)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        apply_button = QPushButton("Apply")
        
        save_button.clicked.connect(self.save_and_close)
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self.apply_changes)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        
        layout.addLayout(button_layout)
    
    def _create_camera_tab(self):
        """Create camera settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Camera device selection
        self.camera_device = QSpinBox()
        self.camera_device.setValue(
            self.config_manager.settings['camera']['device_id'])
        layout.addRow("Camera Device:", self.camera_device)
        
        # Resolution
        self.camera_width = QSpinBox()
        self.camera_width.setRange(320, 1920)
        self.camera_width.setValue(
            self.config_manager.settings['camera']['width'])
        layout.addRow("Width:", self.camera_width)
        
        self.camera_height = QSpinBox()
        self.camera_height.setRange(240, 1080)
        self.camera_height.setValue(
            self.config_manager.settings['camera']['height'])
        layout.addRow("Height:", self.camera_height)
        
        return widget
    
    def _create_gestures_tab(self):
        """Create gestures settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Gesture thresholds
        self.swipe_threshold = QDoubleSpinBox()
        self.swipe_threshold.setRange(0.1, 1.0)
        self.swipe_threshold.setSingleStep(0.1)
        self.swipe_threshold.setValue(
            self.config_manager.settings['gestures']['swipe_threshold'])
        layout.addRow("Swipe Threshold:", self.swipe_threshold)
        
        self.pinch_threshold = QDoubleSpinBox()
        self.pinch_threshold.setRange(0.05, 0.5)
        self.pinch_threshold.setSingleStep(0.05)
        self.pinch_threshold.setValue(
            self.config_manager.settings['gestures']['pinch_threshold'])
        layout.addRow("Pinch Threshold:", self.pinch_threshold)
        
        return widget
    
    def _create_performance_tab(self):
        """Create performance settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Target FPS
        self.target_fps = QSpinBox()
        self.target_fps.setRange(15, 60)
        self.target_fps.setValue(
            self.config_manager.settings['performance']['target_fps'])
        layout.addRow("Target FPS:", self.target_fps)
        
        # Confidence thresholds
        self.detection_confidence = QDoubleSpinBox()
        self.detection_confidence.setRange(0.5, 1.0)
        self.detection_confidence.setSingleStep(0.1)
        self.detection_confidence.setValue(
            self.config_manager.settings['performance']['min_detection_confidence'])
        layout.addRow("Detection Confidence:", self.detection_confidence)
        
        return widget
    
    def _create_interface_tab(self):
        """Create interface settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Display options
        self.show_landmarks = QCheckBox()
        self.show_landmarks.setChecked(
            self.config_manager.settings['interface']['show_landmarks'])
        layout.addRow("Show Landmarks:", self.show_landmarks)
        
        self.show_gesture_path = QCheckBox()
        self.show_gesture_path.setChecked(
            self.config_manager.settings['interface']['show_gesture_path'])
        layout.addRow("Show Gesture Path:", self.show_gesture_path)
        
        return widget
    
    def apply_changes(self):
        """Apply the current configuration changes"""
        # Update camera settings
        self.config_manager.update_settings('camera', 'device_id', 
                                          self.camera_device.value())
        self.config_manager.update_settings('camera', 'width', 
                                          self.camera_width.value())
        self.config_manager.update_settings('camera', 'height', 
                                          self.camera_height.value())
        
        # Update gesture settings
        self.config_manager.update_settings('gestures', 'swipe_threshold',
                                          self.swipe_threshold.value())
        self.config_manager.update_settings('gestures', 'pinch_threshold',
                                          self.pinch_threshold.value())
        
        # Update performance settings
        self.config_manager.update_settings('performance', 'target_fps',
                                          self.target_fps.value())
        self.config_manager.update_settings('performance', 'min_detection_confidence',
                                          self.detection_confidence.value())
        
        # Update interface settings
        self.config_manager.update_settings('interface', 'show_landmarks',
                                          self.show_landmarks.isChecked())
        self.config_manager.update_settings('interface', 'show_gesture_path',
                                          self.show_gesture_path.isChecked())
    
    def save_and_close(self):
        """Save changes and close dialog"""
        self.apply_changes()
        self.accept() 