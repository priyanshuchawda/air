import pyautogui
import numpy as np
from typing import List, Optional
import time

class PaintHandler:
    def __init__(self):
        self.is_painting = False
        self.last_point = None
        self.smoothing_factor = 0.7
        self.min_movement = 3
        self.last_update_time = time.time()
        self.update_interval = 0.01
        
        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        # Drawing threshold
        self.drawing_threshold = 0.15

    def handle_painting(self, landmarks: Optional[List]) -> None:
        """Handle painting mode using hand landmarks"""
        # Validate landmarks
        if not landmarks or not isinstance(landmarks, list) or len(landmarks) < 21:
            if self.is_painting:
                pyautogui.mouseUp()
                self.is_painting = False
            self.last_point = None
            return

        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return

        self.last_update_time = current_time

        try:
            # Get finger positions
            index_tip = landmarks[8]  # Index finger tip
            thumb_tip = landmarks[4]  # Thumb tip

            # Convert coordinates to screen space
            screen_x = int(index_tip[0] * self.screen_width)
            screen_y = int(index_tip[1] * self.screen_height)

            # Apply smoothing
            if self.last_point is not None:
                screen_x = int(screen_x * (1 - self.smoothing_factor) + 
                             self.last_point[0] * self.smoothing_factor)
                screen_y = int(screen_y * (1 - self.smoothing_factor) + 
                             self.last_point[1] * self.smoothing_factor)

            # Check if fingers are close (drawing gesture)
            distance = self._calculate_distance(thumb_tip, index_tip)
            is_drawing_gesture = distance < self.drawing_threshold

            if is_drawing_gesture:
                if not self.is_painting:
                    pyautogui.mouseDown(screen_x, screen_y)
                    self.is_painting = True
                elif self._should_update_position(screen_x, screen_y):
                    pyautogui.moveTo(screen_x, screen_y)
            else:
                if self.is_painting:
                    pyautogui.mouseUp()
                    self.is_painting = False

            self.last_point = (screen_x, screen_y)

        except (IndexError, TypeError) as e:
            print(f"Error in paint handler: {e}")
            if self.is_painting:
                pyautogui.mouseUp()
                self.is_painting = False
            self.last_point = None

    def _calculate_distance(self, p1: List, p2: List) -> float:
        """Calculate normalized distance between two points"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def _should_update_position(self, x: int, y: int) -> bool:
        """Check if should update cursor position"""
        if not self.last_point:
            return True
        distance = np.sqrt((x - self.last_point[0])**2 + (y - self.last_point[1])**2)
        return distance >= self.min_movement

    def stop_painting(self):
        """Stop painting mode"""
        if self.is_painting:
            pyautogui.mouseUp()
        self.is_painting = False
        self.last_point = None 