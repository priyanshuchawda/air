import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, List, Optional

class HandTracker:
    def __init__(self, max_hands=2, min_detection_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5,
            model_complexity=1  # Increased model complexity for better accuracy
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.previous_landmarks = []
        self.smoothing_factor = 0.5  # For landmark smoothing

    def find_hands(self, frame: np.ndarray, draw: bool = True) -> Tuple[np.ndarray, List]:
        """
        Detect and track hands in the frame with smoothing
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(frame_rgb)
        all_landmarks = []

        if self.results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                # Extract landmarks
                current_landmarks = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
                
                # Apply smoothing if previous landmarks exist
                if len(self.previous_landmarks) > hand_idx:
                    current_landmarks = self._smooth_landmarks(
                        current_landmarks, 
                        self.previous_landmarks[hand_idx]
                    )
                
                if draw:
                    self._draw_hand_landmarks(frame, hand_landmarks, hand_idx)
                
                all_landmarks.append(current_landmarks)

            self.previous_landmarks = all_landmarks
        else:
            self.previous_landmarks = []

        return frame, all_landmarks

    def _smooth_landmarks(self, current: List, previous: List) -> List:
        """Apply exponential smoothing to landmarks"""
        if not previous:
            return current
        return [
            [
                current[i][j] * (1 - self.smoothing_factor) + 
                previous[i][j] * self.smoothing_factor
                for j in range(3)
            ]
            for i in range(len(current))
        ]

    def _draw_hand_landmarks(self, frame: np.ndarray, landmarks, hand_idx: int):
        """Draw enhanced hand landmarks with depth information"""
        # Custom drawing specifications
        landmark_spec = self.mp_draw.DrawingSpec(
            color=(0, 255, 0) if hand_idx == 0 else (255, 0, 0),
            thickness=2,
            circle_radius=2
        )
        connection_spec = self.mp_draw.DrawingSpec(
            color=(0, 200, 0) if hand_idx == 0 else (200, 0, 0),
            thickness=1
        )
        
        self.mp_draw.draw_landmarks(
            frame,
            landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            landmark_spec,
            connection_spec
        ) 