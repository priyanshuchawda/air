import numpy as np
from typing import List, Optional

class GestureDetector:
    def __init__(self):
        self.current_landmarks = None
        self.previous_landmarks = None
        self.last_pinch_distance = None
        
        # Gesture detection thresholds
        self.gesture_thresholds = {
            'pinch': 0.08,             # Distance between thumb and index for pinch
            'spread': 0.15,            # Distance between thumb and index for spread
            'position': 0.2            # Position threshold for navigation
        }
        
        # Screen regions for position-based detection
        self.regions = {
            'left': 0.3,    # Left 30% of screen
            'right': 0.7,   # Right 70% of screen
            'top': 0.3,     # Top 30% of screen
            'bottom': 0.7   # Bottom 70% of screen
        }
        
        self.min_distance_change = 0.02
        self.pointing_threshold = 0.1  # Threshold for detecting pointing gesture

    def update(self, landmarks: List) -> Optional[str]:
        """
        Update landmarks and detect gestures
        Returns: detected gesture or None
        """
        if not landmarks:
            self.previous_landmarks = None
            self.last_pinch_distance = None
            return None
            
        current = landmarks[0] if isinstance(landmarks[0], list) else landmarks
        
        self.previous_landmarks = self.current_landmarks
        self.current_landmarks = current
        
        return self.detect_gesture()

    def detect_gesture(self) -> Optional[str]:
        """
        Detect gesture based on current landmarks
        """
        try:
            current = self.current_landmarks
            
            if not current or len(current) < 21:
                return None
            
            # First check for pinch/spread gestures
            pinch_gesture = self._detect_pinch_spread(current)
            if pinch_gesture:
                return pinch_gesture
            
            # If no pinch/spread, check for pointing gestures
            pointing_gesture = self._detect_pointing(current)
            if pointing_gesture:
                return pointing_gesture
            
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
            thumb_tip = np.array(current[4][:2])  # Thumb tip
            index_tip = np.array(current[8][:2])  # Index finger tip
            thumb_mcp = np.array(current[2][:2])  # Thumb base
            index_mcp = np.array(current[5][:2])  # Index finger base
            
            # Calculate distances
            current_distance = np.linalg.norm(thumb_tip - index_tip)
            base_distance = np.linalg.norm(thumb_mcp - index_mcp)
            
            # Normalize distance by base distance
            normalized_distance = current_distance / base_distance
            
            # Initialize last_pinch_distance if None
            if self.last_pinch_distance is None:
                self.last_pinch_distance = normalized_distance
                return None
            
            # Calculate distance change
            distance_change = normalized_distance - self.last_pinch_distance
            
            # Update last distance
            self.last_pinch_distance = normalized_distance
            
            # Debug print
            print(f"Normalized distance: {normalized_distance:.3f}, Change: {distance_change:.3f}")
            
            # Detect gesture based on normalized distance and change
            if abs(distance_change) > self.min_distance_change:
                if normalized_distance < 0.5:  # Adjusted threshold
                    return 'pinch'
                elif normalized_distance > 1.2:  # Adjusted threshold
                    return 'spread'
            
            return None
            
        except (IndexError, TypeError) as e:
            print(f"Error in pinch detection: {e}")
            self.last_pinch_distance = None
            return None

    def _detect_pointing(self, current: List) -> Optional[str]:
        """
        Detect pointing gesture and direction
        Uses index finger position and orientation
        """
        try:
            # Get index finger points
            index_tip = current[8]    # Index finger tip
            index_pip = current[6]    # Index finger middle joint
            
            # Check if index finger is extended (pointing)
            if self._is_finger_extended(current):
                # Get position in frame
                x, y = index_tip[0], index_tip[1]
                
                # Determine direction based on position in frame
                if x < self.regions['left']:
                    return 'nav_left'
                elif x > self.regions['right']:
                    return 'nav_right'
                elif y < self.regions['top']:
                    return 'nav_up'
                elif y > self.regions['bottom']:
                    return 'nav_down'
            
            return None
            
        except (IndexError, TypeError):
            return None

    def _is_finger_extended(self, landmarks: List) -> bool:
        """
        Check if index finger is extended (pointing)
        """
        try:
            # Get relevant finger joints
            mcp = np.array(landmarks[5][:2])  # Base of index finger
            pip = np.array(landmarks[6][:2])  # First joint
            tip = np.array(landmarks[8][:2])  # Finger tip
            
            # Calculate distances
            mcp_pip_dist = np.linalg.norm(pip - mcp)
            pip_tip_dist = np.linalg.norm(tip - pip)
            
            # Finger is extended if tip is further from base than middle joint
            return pip_tip_dist > mcp_pip_dist
            
        except (IndexError, TypeError):
            return False

    def update_thresholds(self, new_thresholds: dict):
        """Update gesture detection thresholds"""
        self.gesture_thresholds.update(new_thresholds)