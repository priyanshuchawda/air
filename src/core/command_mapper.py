import json
import pyautogui
import time
from pynput.keyboard import Key, Controller

class CommandMapper:
    def __init__(self, config_file=None):
        self.default_mappings = {
            'pinch': self._zoom_out,
            'spread': self._zoom_in,
            'swipe_left': self._previous_page,
            'swipe_right': self._next_page,
            'rotate_clockwise': self._rotate_right,
            'rotate_counterclockwise': self._rotate_left
        }
        self.custom_mappings = {}
        
    def execute_command(self, gesture):
        """Execute the command mapped to the gesture"""
        if gesture in self.custom_mappings:
            self.custom_mappings[gesture]()
        elif gesture in self.default_mappings:
            self.default_mappings[gesture]()
    
    def _zoom_in(self):
        """Simulate zoom in action"""
        pyautogui.hotkey('ctrl', '+')
    
    def _zoom_out(self):
        """Simulate zoom out action"""
        pyautogui.hotkey('ctrl', '-')
    
    def _next_page(self):
        pyautogui.press('right')
    
    def _previous_page(self):
        pyautogui.press('left')
    
    def _rotate_right(self):
        pyautogui.hotkey('ctrl', 'r')
    
    def _rotate_left(self):
        pyautogui.hotkey('ctrl', 'l')