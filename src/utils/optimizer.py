import cv2
import numpy as np
import time
import logging
from collections import deque
from threading import Lock
from typing import Dict, Any, Optional, Tuple

class PerformanceOptimizer:
    def __init__(self, config: Dict[str, Any] = None):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize frame timing
        self.frame_times = deque(maxlen=30)  # Fixed size deque for better memory management
        self.processing_lock = Lock()
        self.last_frame_time = time.time()
        
        # Load configuration
        self.config = config or {}
        self.target_fps = self.config.get('performance', {}).get('target_fps', 30)
        
        # Performance settings
        self.frame_scale = self.config.get('performance', {}).get('frame_scale', 1.0)
        self.skip_frames = 0
        self.frame_count = 0
        
        # Output settings
        self.output_width = 640
        self.output_height = 480
        
        # GPU acceleration
        self.use_gpu = False
        self.gpu_frame = None
        if self.config.get('performance', {}).get('enable_gpu', False):
            self.enable_gpu_acceleration()
        
        # Performance monitoring
        self.current_fps = 0.0
        self.avg_processing_time = 0.0
        self.processing_times = deque(maxlen=30)
        
        # Quality control
        self.min_scale = 0.4
        self.max_scale = 1.0
        self.quality_adjustment_threshold = 5  # Frames before quality adjustment
        self.quality_check_counter = 0
    
    def start(self):
        """Initialize the optimizer"""
        self.last_frame_time = time.time()
        self.frame_times.clear()
        self.processing_times.clear()
        self.logger.info("Performance optimizer started")
    
    def optimize_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Optimize frame processing based on performance metrics
        Args:
            frame: Input frame to optimize
        Returns:
            np.ndarray: Optimized frame
        """
        start_time = time.time()
        
        try:
            with self.processing_lock:
                # Skip frames if necessary
                self.frame_count += 1
                if self.skip_frames > 0 and self.frame_count % (self.skip_frames + 1) != 0:
                    return self._ensure_output_size(frame)
                
                # Process frame
                processed_frame = self._process_frame(frame)
                
                # Update performance metrics
                self._update_metrics(start_time)
                
                # Periodically check and adjust quality
                self.quality_check_counter += 1
                if self.quality_check_counter >= self.quality_adjustment_threshold:
                    self._dynamic_quality_adjustment()
                    self.quality_check_counter = 0
                
                return self._ensure_output_size(processed_frame)
                
        except Exception as e:
            self.logger.error(f"Error in frame optimization: {e}")
            return self._ensure_output_size(frame)
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process frame using GPU or CPU
        """
        try:
            if self.use_gpu and self.gpu_frame is not None:
                return self._process_frame_gpu(frame)
            return self._process_frame_cpu(frame)
        except Exception as e:
            self.logger.error(f"Error in frame processing: {e}")
            return frame
    
    def _process_frame_cpu(self, frame: np.ndarray) -> np.ndarray:
        """Process frame using CPU"""
        if self.frame_scale != 1.0:
            process_width = int(frame.shape[1] * self.frame_scale)
            process_height = int(frame.shape[0] * self.frame_scale)
            return cv2.resize(frame, (process_width, process_height))
        return frame
    
    def _process_frame_gpu(self, frame: np.ndarray) -> np.ndarray:
        """Process frame using GPU"""
        try:
            self.gpu_frame.upload(frame)
            
            if self.frame_scale != 1.0:
                width = int(frame.shape[1] * self.frame_scale)
                height = int(frame.shape[0] * self.frame_scale)
                self.gpu_frame = cv2.cuda.resize(self.gpu_frame, (width, height))
            
            return self.gpu_frame.download()
            
        except cv2.error as e:
            self.logger.error(f"GPU processing error: {e}")
            self.use_gpu = False  # Fallback to CPU
            return self._process_frame_cpu(frame)
    
    def _ensure_output_size(self, frame: np.ndarray) -> np.ndarray:
        """
        Ensure the frame is at the correct output size
        """
        if frame.shape[1] != self.output_width or frame.shape[0] != self.output_height:
            return cv2.resize(frame, (self.output_width, self.output_height))
        return frame
    
    def set_output_size(self, width: int, height: int):
        """Set the desired output size"""
        self.output_width = width
        self.output_height = height
    
    def _update_metrics(self, start_time: float):
        """Update performance metrics"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        processing_time = current_time - start_time
        
        self.frame_times.append(frame_time)
        self.processing_times.append(processing_time)
        
        self.last_frame_time = current_time
        self.current_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
        self.avg_processing_time = sum(self.processing_times) / len(self.processing_times)
    
    def _dynamic_quality_adjustment(self):
        """
        Dynamically adjust processing quality based on performance metrics
        """
        fps_ratio = self.current_fps / self.target_fps
        
        if fps_ratio < 0.6:  # Severe performance issues
            self._decrease_quality(0.15)
        elif fps_ratio < 0.8:  # Minor performance issues
            self._decrease_quality(0.1)
        elif fps_ratio > 1.2 and self.avg_processing_time < 1.0 / (self.target_fps * 1.2):
            self._increase_quality(0.1)
    
    def _decrease_quality(self, amount: float):
        """Decrease processing quality"""
        if self.skip_frames < 2:
            self.skip_frames += 1
        elif self.frame_scale > self.min_scale:
            self.frame_scale = max(self.min_scale, self.frame_scale - amount)
        self.logger.debug(f"Decreased quality - Scale: {self.frame_scale:.2f}, Skip: {self.skip_frames}")
    
    def _increase_quality(self, amount: float):
        """Increase processing quality"""
        if self.skip_frames > 0:
            self.skip_frames -= 1
        elif self.frame_scale < self.max_scale:
            self.frame_scale = min(self.max_scale, self.frame_scale + amount)
        self.logger.debug(f"Increased quality - Scale: {self.frame_scale:.2f}, Skip: {self.skip_frames}")
    
    def enable_gpu_acceleration(self) -> bool:
        """
        Enable GPU acceleration if available
        Returns:
            bool: True if GPU acceleration enabled, False otherwise
        """
        try:
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                self.use_gpu = True
                self.gpu_frame = cv2.cuda_GpuMat()
                self.logger.info("GPU acceleration enabled")
                return True
        except Exception as e:
            self.logger.warning(f"Failed to enable GPU acceleration: {e}")
            self.use_gpu = False
        return False
    
    def get_fps(self) -> float:
        """Get current FPS"""
        return self.current_fps
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics
        Returns:
            Dict containing performance metrics
        """
        return {
            'fps': self.current_fps,
            'frame_scale': self.frame_scale,
            'skip_frames': self.skip_frames,
            'avg_processing_time': self.avg_processing_time,
            'gpu_enabled': self.use_gpu,
            'target_fps': self.target_fps
        }