import cv2
import numpy as np
from typing import List, Tuple, Optional

class GestureVisualizer:
    def __init__(self):
        self.colors = {
            'hand_landmarks': (0, 255, 0),      # Green
            'hand_connections': (0, 200, 0),    # Dark Green
            'swipe': (255, 0, 0),              # Blue
            'pinch': (0, 0, 255),              # Red
            'pinch_hold': (255, 0, 255),       # Magenta
            'spread': (255, 165, 0),           # Orange
            'tap': (255, 255, 0),              # Cyan
            'rotate': (128, 0, 128)            # Purple
        }
        self.gesture_trail = []
        self.trail_length = 15  # Increased trail length
        self.feedback_duration = 10  # Frames to show feedback
        self.current_feedback = None
        self.feedback_frames = 0

    def draw_hand_landmarks(self, frame: np.ndarray, landmarks: List) -> np.ndarray:
        """Draw hand landmarks and connections with enhanced visualization"""
        if not landmarks:
            return frame

        frame_h, frame_w = frame.shape[:2]

        # Draw connections first (underneath landmarks)
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index finger
            (5, 9), (9, 10), (10, 11), (11, 12),  # Middle finger
            (9, 13), (13, 14), (14, 15), (15, 16),  # Ring finger
            (13, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (0, 17), (5, 9), (9, 13), (13, 17)  # Palm
        ]

        # Draw connections with alpha blending for depth effect
        for connection in connections:
            start_point = landmarks[connection[0]]
            end_point = landmarks[connection[1]]
            
            start_x = int(start_point[0] * frame_w)
            start_y = int(start_point[1] * frame_h)
            end_x = int(end_point[0] * frame_w)
            end_y = int(end_point[1] * frame_h)

            # Calculate depth for line thickness
            avg_depth = (start_point[2] + end_point[2]) / 2
            thickness = max(1, int(3 * (1 - avg_depth)))
            
            cv2.line(frame, (start_x, start_y), (end_x, end_y), 
                    self.colors['hand_connections'], thickness)

        # Draw landmarks with size based on depth
        for lm in landmarks:
            x, y = int(lm[0] * frame_w), int(lm[1] * frame_h)
            # Use depth (z) to determine circle size
            size = max(2, int(8 * (1 - lm[2])))
            cv2.circle(frame, (x, y), size, self.colors['hand_landmarks'], -1)
            cv2.circle(frame, (x, y), size + 1, (255, 255, 255), 1)

        return frame

    def draw_gesture_feedback(self, frame: np.ndarray, gesture: str, 
                            landmarks: List) -> np.ndarray:
        """Draw enhanced gesture-specific visual feedback"""
        if not gesture or not landmarks:
            return frame

        frame_h, frame_w = frame.shape[:2]

        # Update gesture trail
        index_tip = (
            int(landmarks[8][0] * frame_w),
            int(landmarks[8][1] * frame_h)
        )
        self.gesture_trail.append(index_tip)
        if len(self.gesture_trail) > self.trail_length:
            self.gesture_trail.pop(0)

        # Draw gesture trail with fading effect
        if len(self.gesture_trail) > 1:
            for i in range(1, len(self.gesture_trail)):
                alpha = i / len(self.gesture_trail)
                color = self.colors.get(gesture.split('_')[0], (255, 255, 255))
                cv2.line(frame, self.gesture_trail[i-1], self.gesture_trail[i],
                        tuple(int(c * alpha) for c in color), 2)

        # Draw gesture-specific visualizations
        if 'pinch' in gesture:
            self._draw_pinch_feedback(frame, gesture, landmarks)
        elif 'swipe' in gesture:
            self._draw_swipe_feedback(frame, gesture, landmarks)
        elif 'rotate' in gesture:
            self._draw_rotation_feedback(frame, gesture, landmarks)

        # Add gesture text with background
        self._draw_gesture_text(frame, gesture)

        return frame

    def _draw_pinch_feedback(self, frame: np.ndarray, gesture: str, 
                            landmarks: List) -> None:
        """Draw enhanced pinch gesture feedback"""
        frame_h, frame_w = frame.shape[:2]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        thumb_x = int(thumb_tip[0] * frame_w)
        thumb_y = int(thumb_tip[1] * frame_h)
        index_x = int(index_tip[0] * frame_w)
        index_y = int(index_tip[1] * frame_h)
        
        color = self.colors['pinch_hold'] if gesture == 'pinch_hold' else self.colors['pinch']
        
        # Draw connecting line with glow effect
        for i in range(3, 0, -1):
            cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y),
                    tuple(int(c * 0.5) for c in color), i * 2)
        
        # Draw finger tips with glow effect
        for i in range(3, 0, -1):
            cv2.circle(frame, (thumb_x, thumb_y), i * 3, color, -1)
            cv2.circle(frame, (index_x, index_y), i * 3, color, -1)
        
        # Add visual feedback for pinch hold
        if gesture == 'pinch_hold':
            center_x = (thumb_x + index_x) // 2
            center_y = (thumb_y + index_y) // 2
            radius = int(np.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2) / 4)
            
            # Draw ripple effect
            for i in range(3):
                cv2.circle(frame, (center_x, center_y), 
                          radius + i * 5, self.colors['pinch_hold'], 1)

    def _draw_swipe_feedback(self, frame: np.ndarray, gesture: str, 
                            landmarks: List) -> None:
        """Draw enhanced swipe gesture feedback"""
        frame_h, frame_w = frame.shape[:2]
        tip = landmarks[8]  # Index finger tip
        x, y = int(tip[0] * frame_w), int(tip[1] * frame_h)
        direction = gesture.split('_')[1]
        
        # Draw arrow
        arrow_length = 50
        if direction == 'left':
            cv2.arrowedLine(frame, (x + arrow_length, y), (x - arrow_length, y),
                          self.colors['swipe'], 3, tipLength=0.3)
        elif direction == 'right':
            cv2.arrowedLine(frame, (x - arrow_length, y), (x + arrow_length, y),
                          self.colors['swipe'], 3, tipLength=0.3)
        elif direction == 'up':
            cv2.arrowedLine(frame, (x, y + arrow_length), (x, y - arrow_length),
                          self.colors['swipe'], 3, tipLength=0.3)
        elif direction == 'down':
            cv2.arrowedLine(frame, (x, y - arrow_length), (x, y + arrow_length),
                          self.colors['swipe'], 3, tipLength=0.3)

    def _draw_rotation_feedback(self, frame: np.ndarray, gesture: str, 
                              landmarks: List) -> None:
        """Draw enhanced rotation gesture feedback"""
        frame_h, frame_w = frame.shape[:2]
        center = landmarks[0]  # Palm center
        x = int(center[0] * frame_w)
        y = int(center[1] * frame_h)
        radius = 50
        
        # Draw circular arrow
        if 'clockwise' in gesture:
            start_angle = 0
            end_angle = 270
        else:
            start_angle = 270
            end_angle = 0
        
        # Draw multiple circles for dynamic effect
        for i in range(3):
            cv2.ellipse(frame, (x, y), (radius + i * 5, radius + i * 5),
                       0, start_angle, end_angle, self.colors['rotate'], 2)

    def _draw_gesture_text(self, frame: np.ndarray, gesture: str) -> None:
        """Draw gesture text with background"""
        text = f"Gesture: {gesture}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.8
        thickness = 2
        color = self.colors.get(gesture.split('_')[0], (255, 255, 255))
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, scale, thickness)
        
        # Draw background rectangle
        padding = 10
        cv2.rectangle(frame,
                     (10, 10),
                     (15 + text_width + padding * 2, 15 + text_height + padding * 2),
                     (0, 0, 0), -1)
        
        # Draw text
        cv2.putText(frame, text,
                    (15 + padding, 15 + text_height + padding),
                    font, scale, color, thickness)