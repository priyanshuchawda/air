import json
import pyautogui
import time
from pynput.keyboard import Key, Controller
from .paint_handler import PaintHandler

class CommandMapper:
    def __init__(self, config_file=None):
        self.default_mappings = {
            'pinch': self._zoom_out,
            'pinch_hold': self._continuous_zoom_out,
            'spread': self._zoom_in,
            'nav_left': self._go_left,
            'nav_right': self._go_right,
            'nav_up': self._go_up,
            'nav_down': self._go_down
        }
        self.custom_mappings = {}
        
        # Initialize paint handler
        self.paint_handler = PaintHandler()
        self.painting_mode = False
        
        # Set up PyAutoGUI safely
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01  # Reduced delay for smoother actions
        
        # Zoom control
        self.zoom_speed = 1.0
        self.continuous_zoom_active = False
        self.last_zoom_time = time.time()
        self.zoom_interval = 0.1  # Time between continuous zoom actions
        
        # Navigation control
        self.scroll_speed = 50  # Pixels to scroll
        self.navigation_active = False
        self.last_nav_time = time.time()
        self.nav_interval = 0.05  # Time between navigation actions
    
    def execute_command(self, gesture, landmarks=None):
        """Execute the command mapped to the gesture"""
        try:
            current_time = time.time()
            
            if self.painting_mode:
                # Always process landmarks in paint mode
                self.paint_handler.handle_painting(landmarks)
                return
            
            # Handle continuous zoom
            if gesture == 'pinch_hold':
                if current_time - self.last_zoom_time >= self.zoom_interval:
                    self._continuous_zoom_out()
                    self.last_zoom_time = current_time
                return
            
            # Handle other gestures
            if gesture in self.custom_mappings:
                self.custom_mappings[gesture]()
            elif gesture in self.default_mappings:
                self.default_mappings[gesture]()
                
            # Reset continuous actions if gesture changes
            if gesture != 'pinch_hold':
                self.continuous_zoom_active = False
                
        except Exception as e:
            print(f"Error executing command: {e}")
    
    def toggle_painting_mode(self):
        """Toggle painting mode"""
        self.painting_mode = not self.painting_mode
        if not self.painting_mode:
            self.paint_handler.stop_painting()
        print(f"Paint mode: {'ON' if self.painting_mode else 'OFF'}")
        return self.painting_mode
    
    def _zoom_in(self):
        """Simulate zoom in action"""
        self._safe_key_press('ctrl', '+')
    
    def _zoom_out(self):
        """Simulate zoom out action"""
        self._safe_key_press('ctrl', '-')
    
    def _continuous_zoom_out(self):
        """Handle continuous zoom out"""
        self.continuous_zoom_active = True
        self._zoom_out()
    
    def _go_left(self):
        """Navigate left"""
        if time.time() - self.last_nav_time >= self.nav_interval:
            self._safe_key_press('left')
            self.last_nav_time = time.time()
    
    def _go_right(self):
        """Navigate right"""
        if time.time() - self.last_nav_time >= self.nav_interval:
            self._safe_key_press('right')
            self.last_nav_time = time.time()
    
    def _go_up(self):
        """Navigate up with smooth scrolling"""
        if time.time() - self.last_nav_time >= self.nav_interval:
            pyautogui.scroll(self.scroll_speed)
            self.last_nav_time = time.time()
    
    def _go_down(self):
        """Navigate down with smooth scrolling"""
        if time.time() - self.last_nav_time >= self.nav_interval:
            pyautogui.scroll(-self.scroll_speed)
            self.last_nav_time = time.time()
    
    def _safe_key_press(self, *keys):
        """Safely execute key press with error handling"""
        try:
            pyautogui.hotkey(*keys)
        except Exception as e:
            print(f"Error during key press {keys}: {e}")
    
    def set_zoom_speed(self, speed):
        """Set zoom speed (1.0 is normal)"""
        self.zoom_speed = max(0.1, min(2.0, speed))
    
    def set_scroll_speed(self, speed):
        """Set scroll speed in pixels"""
        self.scroll_speed = max(10, min(100, speed))

    def get_active_mode(self):
        """Get current active mode for UI feedback"""
        if self.painting_mode:
            return "Paint Mode"
        elif self.continuous_zoom_active:
            return "Continuous Zoom"
        else:
            return "Normal Mode"