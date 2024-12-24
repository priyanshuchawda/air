import numpy as np
from typing import List, Optional

class GestureDetector:
    def __init__(self):
        self.current_landmarks = None
        self.previous_landmarks = None
        self.last_pinch_distance = None
        
        # Gesture detection thresholds
        self.gesture_thresholds = {
            'swipe_horizontal': 0.15,  # 15% of frame width
            'swipe_vertical': 0.15,    # 15% of frame height
            'pinch': 0.08,             # Distance between thumb and index for pinch
            'spread': 0.15             # Distance between thumb and index for spread
        }
        
        # Minimum change in distance to trigger pinch/spread
        self.min_distance_change = 0.02

    def update(self, landmarks: List) -> Optional[str]:
        """
        Update landmarks and detect gestures
        Returns: detected gesture or None
        """
        # Handle case when no landmarks are detected
        if not landmarks:
            self.previous_landmarks = None
            self.last_pinch_distance = None
            return None
            
        # If we have multiple hands, use the first one
        current = landmarks[0] if isinstance(landmarks[0], list) else landmarks
        
        # Store current landmarks
        self.previous_landmarks = self.current_landmarks
        self.current_landmarks = current
        
        # Detect gestures
        return self.detect_gesture()

    def detect_gesture(self) -> Optional[str]:
        """
        Detect gesture based on current landmarks
        """
        try:
            current = self.current_landmarks
            
            if not current or len(current) < 21:  # Ensure we have all landmarks
                return None
            
            # Check for pinch/spread gestures first
            pinch_gesture = self._detect_pinch_spread(current)
            if pinch_gesture:
                return pinch_gesture
            
            # If no pinch/spread, check for swipes
            if self.previous_landmarks:
                return self._detect_swipe(current, self.previous_landmarks)
            
            return None
            
        except (IndexError, TypeError) as e:
            print(f"Error detecting gesture: {e}")
            return None

    def _detect_pinch_spread(self, current: List) -> Optional[str]:
        """
        Detect pinch and spread gestures
        Returns: 'pinch', 'spread', or None
        """
        try:
            # Get thumb and index finger positions
            thumb_tip = np.array(current[4][:2])
            index_tip = np.array(current[8][:2])
            
            # Calculate current distance
            current_distance = np.linalg.norm(thumb_tip - index_tip)
            
            # Initialize last_pinch_distance if None
            if self.last_pinch_distance is None:
                self.last_pinch_distance = current_distance
                return None
            
            # Calculate distance change
            distance_change = current_distance - self.last_pinch_distance
            
            # Update last distance
            self.last_pinch_distance = current_distance
            
            # Debug print
            print(f"Distance: {current_distance:.3f}, Change: {distance_change:.3f}")
            
            # Detect gesture based on distance and change
            if abs(distance_change) > self.min_distance_change:
                if current_distance < self.gesture_thresholds['pinch']:
                    return 'pinch'
                elif current_distance > self.gesture_thresholds['spread']:
                    return 'spread'
            
            return None
            
        except (IndexError, TypeError):
            self.last_pinch_distance = None
            return None

    def _detect_swipe(self, current: List, previous: List) -> Optional[str]:
        """Detect swipe gestures"""
        try:
            # Use index finger tip for swipe detection
            dx = current[8][0] - previous[8][0]  # X movement
            dy = current[8][1] - previous[8][1]  # Y movement
            
            # Check horizontal swipe
            if abs(dx) > self.gesture_thresholds['swipe_horizontal']:
                return 'swipe_right' if dx > 0 else 'swipe_left'
            
            # Check vertical swipe
            if abs(dy) > self.gesture_thresholds['swipe_vertical']:
                return 'swipe_up' if dy < 0 else 'swipe_down'
            
            return None
            
        except (IndexError, TypeError):
            return None

    def update_thresholds(self, new_thresholds: dict):
        """Update gesture detection thresholds"""
        self.gesture_thresholds.update(new_thresholds)