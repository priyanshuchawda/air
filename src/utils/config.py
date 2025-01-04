import json
import os

class Config:
    def __init__(self):
        self.config_path = "config/settings.json"
        self.default_config = {
            "camera_index": 0,
            "gesture_sensitivity": 0.3,
            "commands": {
                "SWIPE_LEFT": "previous",
                "SWIPE_RIGHT": "next",
                "PINCH": "zoom",
                "TAP": "click"
            }
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = self.default_config
            self.save_config()

    def save_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=4) 