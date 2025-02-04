class CameraController(QObject):
    frame_processed = pyqtSignal(np.ndarray, list, str)  # frame, landmarks, gesture
    
    def __init__(self):
        super().__init__()
        self._camera = None
        self._gesture_recognizer = GestureRecognizer()
        self._frame_processor = FrameProcessor()
        self._fps = 30
        self._is_running = False

    def initialize_camera(self, source=0):
        try:
            self._camera = cv2.VideoCapture(source)
            self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            return True
        except Exception as e:
            self.handle_error(f"Camera init error: {str(e)}")
            return False

    def start_stream(self):
        self._is_running = True
        while self._is_running:
            success, frame = self._camera.read()
            if not success:
                self.handle_error("Frame capture failed")
                continue
                
            processed = self._frame_processor.process(frame)
            self.frame_processed.emit(
                processed['frame'],
                processed['landmarks'],
                self._gesture_recognizer.recognize(processed['landmarks'])
            )
            cv2.waitKey(1000 // self._fps)

    def stop_stream(self):
        self._is_running = False
        if self._camera:
            self._camera.release()

    def handle_error(self, message):
        # Implement error recovery logic
        pass