import numpy as np
import json
import os
from datetime import datetime

class GestureRecorder:
    def __init__(self, save_dir='config/custom_gestures'):
        self.save_dir = save_dir
        self.recording = False
        self.current_gesture = []
        self.recorded_gestures = {}
        
        # Create save directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        self.load_recorded_gestures()

    def start_recording(self, gesture_name):
        """Start recording a new gesture"""
        self.recording = True
        self.current_gesture = []
        self.gesture_name = gesture_name

    def stop_recording(self):
        """Stop recording and save the gesture"""
        if self.recording and len(self.current_gesture) > 0:
            self.recorded_gestures[self.gesture_name] = self.current_gesture
            self.save_gesture(self.gesture_name)
            self.recording = False
            return True
        return False

    def add_frame(self, landmarks):
        """Add landmarks from current frame to recording"""
        if self.recording and landmarks:
            self.current_gesture.append(landmarks)

    def save_gesture(self, gesture_name):
        """Save recorded gesture to file"""
        file_path = os.path.join(self.save_dir, f"{gesture_name}.json")
        gesture_data = {
            'name': gesture_name,
            'timestamp': datetime.now().isoformat(),
            'landmarks': self.current_gesture
        }
        with open(file_path, 'w') as f:
            json.dump(gesture_data, f)

    def load_recorded_gestures(self):
        """Load all recorded gestures from files"""
        if not os.path.exists(self.save_dir):
            return

        for file_name in os.listdir(self.save_dir):
            if file_name.endswith('.json'):
                file_path = os.path.join(self.save_dir, file_name)
                with open(file_path, 'r') as f:
                    gesture_data = json.load(f)
                    self.recorded_gestures[gesture_data['name']] = gesture_data['landmarks']

    def compare_gesture(self, current_landmarks):
        """Compare current landmarks with recorded gestures"""
        if not current_landmarks:
            return None

        best_match = None
        min_distance = float('inf')

        for name, recorded_landmarks in self.recorded_gestures.items():
            distance = self._calculate_gesture_distance(current_landmarks, recorded_landmarks)
            if distance < min_distance:
                min_distance = distance
                best_match = name

        # Return match if distance is below threshold
        threshold = 0.3
        return best_match if min_distance < threshold else None

    def _calculate_gesture_distance(self, current, recorded):
        """Calculate distance between current and recorded gesture"""
        if len(recorded) == 0:
            return float('inf')

        # Use Dynamic Time Warping (DTW) for comparison
        dtw_matrix = np.zeros((len(current), len(recorded)))
        for i in range(len(current)):
            for j in range(len(recorded)):
                cost = np.linalg.norm(np.array(current[i]) - np.array(recorded[j]))
                dtw_matrix[i, j] = cost

        return dtw_matrix[-1, -1] / (len(current) + len(recorded)) 