import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass

class ConfigManager:
    def __init__(self, config_dir=None):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Setup paths - look for config in project root
        if config_dir is None:
            # Get the project root directory (two levels up from this file)
            current_dir = Path(__file__).parent.parent.parent
            config_dir = current_dir / 'config'
        else:
            config_dir = Path(config_dir)
            
        self.config_dir = config_dir
        self.config_file = self.config_dir / 'settings.json'
        self.gesture_mappings_file = self.config_dir / 'gesture_mappings.json'
        
        # Default settings with validation rules
        self.settings = {
            'camera': {
                'device_id': self._get_env_int('AIRTOUCH_CAMERA_ID', 0),
                'width': self._get_env_int('AIRTOUCH_CAMERA_WIDTH', 640),
                'height': self._get_env_int('AIRTOUCH_CAMERA_HEIGHT', 480),
                'fps': self._get_env_int('AIRTOUCH_CAMERA_FPS', 30)
            },
            'gestures': {
                'swipe_threshold': 0.3,
                'pinch_threshold': 0.15,
                'rotation_threshold': 30,
                'min_distance_change': 0.02,
                'pointing_threshold': 0.1
            },
            'performance': {
                'target_fps': self._get_env_int('AIRTOUCH_TARGET_FPS', 30),
                'min_detection_confidence': 0.7,
                'min_tracking_confidence': 0.5,
                'enable_gpu': self._get_env_bool('AIRTOUCH_ENABLE_GPU', False),
                'frame_scale': self._get_env_float('AIRTOUCH_FRAME_SCALE', 1.0)
            },
            'interface': {
                'show_landmarks': True,
                'show_gesture_path': True,
                'window_width': 1000,
                'window_height': 800,
                'debug_mode': self._get_env_bool('AIRTOUCH_DEBUG', False)
            }
        }
        
        # Validation rules
        self.validation_rules = {
            'camera': {
                'device_id': lambda x: isinstance(x, int) and x >= 0,
                'width': lambda x: isinstance(x, int) and 100 <= x <= 4096,
                'height': lambda x: isinstance(x, int) and 100 <= x <= 4096,
                'fps': lambda x: isinstance(x, int) and 1 <= x <= 120
            },
            'gestures': {
                'swipe_threshold': lambda x: isinstance(x, (int, float)) and 0 < x < 1,
                'pinch_threshold': lambda x: isinstance(x, (int, float)) and 0 < x < 1,
                'rotation_threshold': lambda x: isinstance(x, (int, float)) and 0 < x <= 180
            },
            'performance': {
                'target_fps': lambda x: isinstance(x, int) and 1 <= x <= 120,
                'min_detection_confidence': lambda x: isinstance(x, float) and 0 < x <= 1,
                'min_tracking_confidence': lambda x: isinstance(x, float) and 0 < x <= 1
            }
        }
        
        # Default gesture mappings
        self.gesture_mappings = {
            'swipe_left': 'previous_page',
            'swipe_right': 'next_page',
            'pinch': 'zoom_out',
            'spread': 'zoom_in',
            'rotate_clockwise': 'rotate_right',
            'rotate_counterclockwise': 'rotate_left',
            'nav_up': 'scroll_up',
            'nav_down': 'scroll_down'
        }
        
        # Load configurations
        self._ensure_config_dir()
        self.load_settings()
        self.load_gesture_mappings()
    
    def _get_env_int(self, key: str, default: int) -> int:
        """Get integer from environment variable"""
        try:
            return int(os.getenv(key, default))
        except (TypeError, ValueError):
            self.logger.warning(f"Invalid {key} environment variable, using default: {default}")
            return default

    def _get_env_float(self, key: str, default: float) -> float:
        """Get float from environment variable"""
        try:
            return float(os.getenv(key, default))
        except (TypeError, ValueError):
            self.logger.warning(f"Invalid {key} environment variable, using default: {default}")
            return default

    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Get boolean from environment variable"""
        val = os.getenv(key, str(default)).lower()
        return val in ('true', '1', 'yes', 'on')

    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create config directory: {e}")
            raise

    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Validate settings against rules
        Raises ConfigValidationError if validation fails
        """
        try:
            for category, rules in self.validation_rules.items():
                if category in settings:
                    for key, validator in rules.items():
                        if key in settings[category]:
                            value = settings[category][key]
                            if not validator(value):
                                raise ConfigValidationError(
                                    f"Invalid value for {category}.{key}: {value}"
                                )
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise ConfigValidationError(str(e))

    def load_settings(self):
        """Load settings from JSON file with validation"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Validate before updating
                    if self.validate_settings(loaded_settings):
                        self._update_nested_dict(self.settings, loaded_settings)
                    self.logger.info(f"Loaded settings from {self.config_file}")
            else:
                self.logger.info(f"No settings file found at {self.config_file}, using defaults")
                self.save_settings()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in settings file: {e}")
            self._backup_and_reset_settings()
        except ConfigValidationError as e:
            self.logger.error(f"Invalid settings: {e}")
            self._backup_and_reset_settings()
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self._backup_and_reset_settings()

    def _backup_and_reset_settings(self):
        """Backup invalid settings and reset to defaults"""
        if self.config_file.exists():
            backup_path = self.config_file.with_suffix('.json.bak')
            self.config_file.rename(backup_path)
            self.logger.info(f"Backed up invalid settings to {backup_path}")
        self.save_settings()

    def load_gesture_mappings(self):
        """Load gesture mappings from JSON file"""
        try:
            if self.gesture_mappings_file.exists():
                with open(self.gesture_mappings_file, 'r') as f:
                    self.gesture_mappings = json.load(f)
                self.logger.info(f"Loaded gesture mappings from {self.gesture_mappings_file}")
            else:
                self.logger.info(f"No gesture mappings file found at {self.gesture_mappings_file}, using defaults")
                self.save_gesture_mappings()
        except Exception as e:
            self.logger.error(f"Error loading gesture mappings: {e}")
            self.save_gesture_mappings()

    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.logger.info(f"Saved settings to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")

    def save_gesture_mappings(self):
        """Save current gesture mappings to JSON file"""
        try:
            with open(self.gesture_mappings_file, 'w') as f:
                json.dump(self.gesture_mappings, f, indent=4)
            self.logger.info(f"Saved gesture mappings to {self.gesture_mappings_file}")
        except Exception as e:
            self.logger.error(f"Error saving gesture mappings: {e}")

    def update_settings(self, category: str, key: str, value: Any) -> bool:
        """
        Update a specific setting with validation
        Returns: bool indicating success
        """
        try:
            if category in self.settings and key in self.settings[category]:
                # Create temporary settings for validation
                temp_settings = {category: {key: value}}
                if self.validate_settings(temp_settings):
                    self.settings[category][key] = value
                    self.save_settings()
                    return True
            return False
        except ConfigValidationError as e:
            self.logger.error(f"Validation error updating settings: {e}")
            return False

    def update_gesture_mapping(self, gesture: str, command: str):
        """Update a gesture mapping"""
        self.gesture_mappings[gesture] = command
        self.save_gesture_mappings()

    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value with default fallback
        """
        try:
            return self.settings[category][key]
        except KeyError:
            self.logger.warning(f"Setting {category}.{key} not found, using default: {default}")
            return default

    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """Recursively update nested dictionary while preserving structure"""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_nested_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d