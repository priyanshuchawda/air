import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self, config_dir='config'):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'settings.json'
        self.gesture_mappings_file = self.config_dir / 'gesture_mappings.json'
        
        # Default settings
        self.settings = {
            'camera': {
                'device_id': 0,
                'width': 640,
                'height': 480,
                'fps': 30
            },
            'gestures': {
                'swipe_threshold': 0.3,
                'pinch_threshold': 0.15,
                'rotation_threshold': 30
            },
            'performance': {
                'target_fps': 30,
                'min_detection_confidence': 0.7,
                'min_tracking_confidence': 0.5
            },
            'interface': {
                'show_landmarks': True,
                'show_gesture_path': True,
                'window_width': 1000,
                'window_height': 800
            }
        }
        
        self.gesture_mappings = {}
        
        # Load configurations
        self._ensure_config_dir()
        self.load_settings()
        self.load_gesture_mappings()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Update settings while preserving defaults for missing values
                    self._update_nested_dict(self.settings, loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Create default settings file if it doesn't exist
            self.save_settings()
    
    def load_gesture_mappings(self):
        """Load gesture mappings from JSON file"""
        try:
            if self.gesture_mappings_file.exists():
                with open(self.gesture_mappings_file, 'r') as f:
                    self.gesture_mappings = json.load(f)
        except Exception as e:
            print(f"Error loading gesture mappings: {e}")
            # Create default mappings
            self.gesture_mappings = {
                'swipe_left': 'previous_page',
                'swipe_right': 'next_page',
                'pinch': 'zoom_out',
                'spread': 'zoom_in',
                'rotate_clockwise': 'rotate_right',
                'rotate_counterclockwise': 'rotate_left'
            }
            self.save_gesture_mappings()
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def save_gesture_mappings(self):
        """Save current gesture mappings to JSON file"""
        try:
            with open(self.gesture_mappings_file, 'w') as f:
                json.dump(self.gesture_mappings, f, indent=4)
        except Exception as e:
            print(f"Error saving gesture mappings: {e}")
    
    def update_settings(self, category, key, value):
        """Update a specific setting"""
        if category in self.settings and key in self.settings[category]:
            self.settings[category][key] = value
            self.save_settings()
            return True
        return False
    
    def update_gesture_mapping(self, gesture, command):
        """Update a gesture mapping"""
        self.gesture_mappings[gesture] = command
        self.save_gesture_mappings()
    
    def _update_nested_dict(self, d, u):
        """Recursively update nested dictionary while preserving structure"""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_nested_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d 