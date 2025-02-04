class FrameProcessor:
    def __init__(self):
        self._prev_frame = None
        self._diff_threshold = 0.1  # Only process frames with >10% changes

    def process(self, frame):
        if self._should_skip(frame):
            return {'frame': frame, 'landmarks': None}
            
        # Actual processing logic
        return {
            'frame': frame,
            'landmarks': self._detect_landmarks(frame),
            'motion_vectors': self._calculate_motion()
        }

    def _should_skip(self, frame):
        if self._prev_frame is None:
            self._prev_frame = frame
            return False
            
        diff = cv2.absdiff(frame, self._prev_frame)
        non_zero = np.count_nonzero(diff)
        diff_ratio = non_zero / diff.size
        self._prev_frame = frame
        return diff_ratio < self._diff_threshold