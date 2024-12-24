from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QPushButton, QLabel, QGridLayout)
import json

class SettingsDialog(QDialog):
    def __init__(self, command_mapper, parent=None):
        super().__init__(parent)
        self.command_mapper = command_mapper
        self.setWindowTitle("Gesture Settings")
        self.setGeometry(200, 200, 400, 300)
        
        self.available_gestures = [
            'swipe_left', 'swipe_right', 'swipe_up', 'swipe_down',
            'pinch', 'spread', 'tap', 'rotate_clockwise', 'rotate_counterclockwise'
        ]
        
        self.available_commands = [
            'previous_page', 'next_page', 'volume_up', 'volume_down',
            'zoom_in', 'zoom_out', 'click', 'rotate_right', 'rotate_left'
        ]
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        grid = QGridLayout()
        
        # Create mapping controls
        self.mapping_controls = {}
        for i, gesture in enumerate(self.available_gestures):
            label = QLabel(gesture)
            combo = QComboBox()
            combo.addItems(self.available_commands)
            
            # Set current mapping if exists
            if gesture in self.command_mapper.mappings:
                index = self.available_commands.index(
                    self.command_mapper.mappings[gesture]
                )
                combo.setCurrentIndex(index)
                
            grid.addWidget(label, i, 0)
            grid.addWidget(combo, i, 1)
            self.mapping_controls[gesture] = combo
            
        layout.addLayout(grid)
        
        # Add Save and Cancel buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.save_mappings)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def save_mappings(self):
        new_mappings = {}
        for gesture, combo in self.mapping_controls.items():
            new_mappings[gesture] = combo.currentText()
            
        self.command_mapper.mappings = new_mappings
        with open('config/gesture_mappings.json', 'w') as f:
            json.dump(new_mappings, f, indent=4)
        
        self.accept() 