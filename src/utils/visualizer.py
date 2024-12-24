import cv2
import numpy as np

class GestureVisualizer:
    def __init__(self):
        self.colors = {
            'hand_landmarks': (0, 255, 0),     # Green
            'swipe': (255, 0, 0),              # Blue
            'pinch': (0, 0, 255),              # Red
            'tap': (255, 255, 0),              # Cyan
            'rotate': (255, 0, 255)            # Magenta
        }
        self.gesture_trail = []
        self.trail_length = 10

    def draw_hand_landmarks(self, frame, landmarks):
        """Draw hand landmarks and connections"""
        if not landmarks:
            return frame

        # Draw landmarks
        for lm in landmarks:
            x, y = int(lm[0] * frame.shape[1]), int(lm[1] * frame.shape[0])
            cv2.circle(frame, (x, y), 4, self.colors['hand_landmarks'], -1)

        # Draw connections between landmarks
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index finger
            (5, 9), (9, 10), (10, 11), (11, 12),  # Middle finger
            (9, 13), (13, 14), (14, 15), (15, 16),  # Ring finger
            (13, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (0, 17)  # Palm
        ]

        for connection in connections:
            start_point = landmarks[connection[0]]
            end_point = landmarks[connection[1]]
            
            start_x = int(start_point[0] * frame.shape[1])
            start_y = int(start_point[1] * frame.shape[0])
            end_x = int(end_point[0] * frame.shape[1])
            end_y = int(end_point[1] * frame.shape[0])
            
            cv2.line(frame, (start_x, start_y), (end_x, end_y), 
                    self.colors['hand_landmarks'], 2)

        return frame

    def draw_gesture_feedback(self, frame, gesture, landmarks):
        """Draw gesture-specific visual feedback"""
        if not gesture or not landmarks:
            return frame

        # Update gesture trail
        index_finger_tip = (
            int(landmarks[8][0] * frame.shape[1]),
            int(landmarks[8][1] * frame.shape[0])
        )
        self.gesture_trail.append(index_finger_tip)
        if len(self.gesture_trail) > self.trail_length:
            self.gesture_trail.pop(0)

        # Draw gesture trail
        if len(self.gesture_trail) > 1:
            for i in range(1, len(self.gesture_trail)):
                cv2.line(frame, self.gesture_trail[i-1], self.gesture_trail[i],
                        self.colors.get(gesture.split('_')[0], (255, 255, 255)), 2)

        # Draw gesture-specific visualizations
        if 'swipe' in gesture:
            self._draw_swipe_feedback(frame, gesture, landmarks)
        elif 'pinch' in gesture:
            self._draw_pinch_feedback(frame, landmarks)
        elif 'rotate' in gesture:
            self._draw_rotation_feedback(frame, gesture, landmarks)

        # Add gesture text
        cv2.putText(frame, gesture, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, self.colors.get(gesture.split('_')[0], (255, 255, 255)), 2)

        return frame

    def _draw_swipe_feedback(self, frame, gesture, landmarks):
        """Draw swipe gesture feedback"""
        direction = gesture.split('_')[1]
        tip = landmarks[8]  # Index finger tip
        x, y = int(tip[0] * frame.shape[1]), int(tip[1] * frame.shape[0])
        
        # Draw direction arrow
        if direction == 'left':
            cv2.arrowedLine(frame, (x + 50, y), (x - 50, y), 
                           self.colors['swipe'], 2)
        elif direction == 'right':
            cv2.arrowedLine(frame, (x - 50, y), (x + 50, y), 
                           self.colors['swipe'], 2)
        elif direction == 'up':
            cv2.arrowedLine(frame, (x, y + 50), (x, y - 50), 
                           self.colors['swipe'], 2)
        elif direction == 'down':
            cv2.arrowedLine(frame, (x, y - 50), (x, y + 50), 
                           self.colors['swipe'], 2)

    def _draw_pinch_feedback(self, frame, landmarks):
        """Draw pinch gesture feedback"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        thumb_x = int(thumb_tip[0] * frame.shape[1])
        thumb_y = int(thumb_tip[1] * frame.shape[0])
        index_x = int(index_tip[0] * frame.shape[1])
        index_y = int(index_tip[1] * frame.shape[0])
        
        cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), 
                self.colors['pinch'], 2)
        cv2.circle(frame, (thumb_x, thumb_y), 8, self.colors['pinch'], -1)
        cv2.circle(frame, (index_x, index_y), 8, self.colors['pinch'], -1)

    def _draw_rotation_feedback(self, frame, gesture, landmarks):
        """Draw rotation gesture feedback"""
        center = landmarks[0]  # Palm center
        x = int(center[0] * frame.shape[1])
        y = int(center[1] * frame.shape[0])
        radius = 50
        
        # Draw circular arrow
        if 'clockwise' in gesture:
            cv2.ellipse(frame, (x, y), (radius, radius), 0, 0, 270, 
                       self.colors['rotate'], 2)
            cv2.arrowedLine(frame, (x, y - radius), (x + radius, y - radius), 
                           self.colors['rotate'], 2)
        else:
            cv2.ellipse(frame, (x, y), (radius, radius), 0, 270, 0, 
                       self.colors['rotate'], 2)
            cv2.arrowedLine(frame, (x + radius, y - radius), (x, y - radius), 
                           self.colors['rotate'], 2) 