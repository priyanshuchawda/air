import cv2
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QOpenGLWidget
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

class VideoRenderer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setViewport(QOpenGLWidget())  # Enable GPU acceleration
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self._current_frame = None
        self._buffer_frame = None

    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        self._buffer_frame = frame
        self._swap_buffers()
        
    def _swap_buffers(self):
        if self._buffer_frame is not None:
            self._current_frame = self._buffer_frame
            self._buffer_frame = None
            self._display_frame()
            
    def _display_frame(self):
        rgb_image = cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.pixmap_item.setPixmap(QPixmap.fromImage(q_img))
        self.fitInView(self.pixmap_item, 1)  # Maintain aspect ratio