import logging
from PyQt5.QtCore import QTimer

class ErrorHandler:
    def __init__(self, max_retries=3, retry_interval=5000):
        self.retry_count = 0
        self.max_retries = max_retries
        self.retry_timer = QTimer()
        self.retry_timer.setInterval(retry_interval)
        self.retry_timer.timeout.connect(self._retry_operation)

    def handle(self, operation, error_message):
        logging.error(f"Error: {error_message}")
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.retry_timer.start()
            return True
        return False

    def _retry_operation(self):
        self.retry_timer.stop()
        # Implement actual retry logic