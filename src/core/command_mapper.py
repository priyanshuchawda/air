import json
import pyautogui
import time
from pynput.keyboard import Key, Controller
from .paint_handler import PaintHandler

class CommandMapper:
    def __init__(self, config_file=None):
        self.default_mappings = {
            'pinch': self._zoom_out,
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
        pyautogui.PAUSE = 0.01  # Reduced delay for smoother painting
    
    def execute_command(self, gesture, landmarks=None):
        """Execute the command mapped to the gesture"""
        try:
            if self.painting_mode:
                # Always process landmarks in paint mode
                self.paint_handler.handle_painting(landmarks)
                return
                
            if gesture in self.custom_mappings:
                self.custom_mappings[gesture]()
            elif gesture in self.default_mappings:
                self.default_mappings[gesture]()
                
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
        pyautogui.hotkey('ctrl', '+')
    
    def _zoom_out(self):
        """Simulate zoom out action"""
        pyautogui.hotkey('ctrl', '-')
    
    def _go_left(self):
        """Navigate left"""
        pyautogui.press('left')
    
    def _go_right(self):
        """Navigate right"""
        pyautogui.press('right')
    
    def _go_up(self):
        """Navigate up"""
        pyautogui.press('up')
    
    def _go_down(self):
        """Navigate down"""
        pyautogui.press('down')