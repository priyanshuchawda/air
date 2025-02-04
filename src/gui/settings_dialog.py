from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QPushButton, QLabel, QGridLayout,
                            QFrame, QGroupBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
import json

class SettingsDialog(QDialog):
    def __init__(self, command_mapper, parent=None):
        super().__init__(parent)
        self.command_mapper = command_mapper
        self.setWindowTitle("Gesture Settings")
        self.setGeometry(200, 200, 500, 600)
        
        self.available_gestures = [
            'swipe_left', 'swipe_right', 'swipe_up', 'swipe_down',
            'pinch', 'pinch_hold', 'spread', 'rotate_clockwise', 
            'rotate_counterclockwise'
        ]
        
        self.available_commands = [
            'previous_page', 'next_page', 'scroll_up', 'scroll_down',
            'zoom_out', 'continuous_zoom_out', 'zoom_in', 'rotate_right', 
            'rotate_left'
        ]
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Gesture Mappings Group
        mappings_group = QGroupBox("Gesture Mappings")
        grid = QGridLayout()
        
        # Headers
        grid.addWidget(QLabel("Gesture"), 0, 0)
        grid.addWidget(QLabel("Command"), 0, 1)
        
        # Create mapping controls
        self.mapping_controls = {}
        for i, gesture in enumerate(self.available_gestures, 1):
            label = QLabel(gesture)
            combo = QComboBox()
            combo.addItems(self.available_commands)
            
            # Set current mapping if exists
            current_command = None
            if gesture in self.command_mapper.default_mappings:
                current_command = self.command_mapper.default_mappings[gesture].__name__[1:]
            elif gesture in self.command_mapper.custom_mappings:
                current_command = self.command_mapper.custom_mappings[gesture].__name__[1:]
            
            if current_command in self.available_commands:
                combo.setCurrentText(current_command)
            
            grid.addWidget(label, i, 0)
            grid.addWidget(combo, i, 1)
            self.mapping_controls[gesture] = combo
        
        mappings_group.setLayout(grid)
        layout.addWidget(mappings_group)
        
        # Speed Settings Group
        speed_group = QGroupBox("Speed Settings")
        speed_layout = QGridLayout()
        
        # Zoom Speed
        zoom_label = QLabel("Zoom Speed:")
        self.zoom_speed = QDoubleSpinBox()
        self.zoom_speed.setRange(0.1, 2.0)
        self.zoom_speed.setSingleStep(0.1)
        self.zoom_speed.setValue(self.command_mapper.zoom_speed)
        speed_layout.addWidget(zoom_label, 0, 0)
        speed_layout.addWidget(self.zoom_speed, 0, 1)
        
        # Scroll Speed
        scroll_label = QLabel("Scroll Speed:")
        self.scroll_speed = QSpinBox()
        self.scroll_speed.setRange(10, 100)
        self.scroll_speed.setSingleStep(5)
        self.scroll_speed.setValue(self.command_mapper.scroll_speed)
        speed_layout.addWidget(scroll_label, 1, 0)
        speed_layout.addWidget(self.scroll_speed, 1, 1)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # Add Save and Cancel buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_mappings)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Apply styles
        self.apply_styles()
        
        self.setLayout(layout)
    
    def apply_styles(self):
        """Apply custom styles to the dialog"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: white;
            }
            QPushButton {
                padding: 6px 20px;
                border: 2px solid #8f8f91;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QComboBox {
                padding: 4px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QSpinBox, QDoubleSpinBox {
                padding: 4px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
        """)

    def save_mappings(self):
        """Save gesture mappings and speed settings"""
        try:
            # Update speed settings
            self.command_mapper.set_zoom_speed(self.zoom_speed.value())
            self.command_mapper.set_scroll_speed(self.scroll_speed.value())
            
            # Update mappings
            new_mappings = {}
            for gesture, combo in self.mapping_controls.items():
                command = combo.currentText()
                method_name = f"_{command}"
                if hasattr(self.command_mapper, method_name):
                    new_mappings[gesture] = getattr(self.command_mapper, method_name)
            
            # Save to gesture_mappings.json
            serializable_mappings = {
                gesture: method.__name__[1:] 
                for gesture, method in new_mappings.items()
            }
            
            with open('config/gesture_mappings.json', 'w') as f:
                json.dump(serializable_mappings, f, indent=4)
            
            # Update command mapper
            self.command_mapper.custom_mappings.update(new_mappings)
            
            self.accept()
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.reject()