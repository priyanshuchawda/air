import cv2
import numpy as np
import time
from threading import Lock

class PerformanceOptimizer:
    def __init__(self):
        self.frame_times = []
        self.max_frame_history = 30
        self.processing_lock = Lock()
        self.last_frame_time = time.time()
        self.target_fps = 30
        
        # Performance settings
        self.frame_scale = 1.0  # Scale factor for frame resolution
        self.skip_frames = 0    # Number of frames to skip
        self.frame_count = 0
        
        # Output settings
        self.output_width = 640
        self.output_height = 480
        
        # Stats
        self.current_fps = 0
        self.avg_processing_time = 0
    
    def start(self):
        """Initialize the optimizer"""
        self.last_frame_time = time.time()
        self.frame_times.clear()
        
    def optimize_frame(self, frame):
        """
        Optimize frame processing based on performance metrics
        """
        with self.processing_lock:
            # Skip frames if necessary
            self.frame_count += 1
            if self.skip_frames > 0 and self.frame_count % (self.skip_frames + 1) != 0:
                return self._ensure_output_size(frame)
            
            # Resize frame if scale factor is not 1.0
            if self.frame_scale != 1.0:
                process_width = int(frame.shape[1] * self.frame_scale)
                process_height = int(frame.shape[0] * self.frame_scale)
                frame = cv2.resize(frame, (process_width, process_height))
            
            # Update performance metrics
            current_time = time.time()
            frame_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Update FPS calculation
            self.frame_times.append(frame_time)
            if len(self.frame_times) > self.max_frame_history:
                self.frame_times.pop(0)
            
            self.current_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
            
            # Adjust settings based on performance
            self._adjust_settings()
            
            # Ensure consistent output size
            return self._ensure_output_size(frame)
    
    def _ensure_output_size(self, frame):
        """Ensure the frame is at the correct output size"""
        if frame.shape[1] != self.output_width or frame.shape[0] != self.output_height:
            frame = cv2.resize(frame, (self.output_width, self.output_height))
        return frame
    
    def set_output_size(self, width, height):
        """Set the desired output size"""
        self.output_width = width
        self.output_height = height
    
    def _adjust_settings(self):
        """
        Dynamically adjust processing settings based on performance
        """
        if self.current_fps < self.target_fps * 0.8:  # Below 80% of target
            if self.frame_scale > 0.5:
                self.frame_scale -= 0.1
            elif self.skip_frames < 2:
                self.skip_frames += 1
        elif self.current_fps > self.target_fps * 1.2:  # Above 120% of target
            if self.skip_frames > 0:
                self.skip_frames -= 1
            elif self.frame_scale < 1.0:
                self.frame_scale += 0.1
    
    def get_fps(self):
        """Get current FPS"""
        return self.current_fps
    
    def get_stats(self):
        """Get performance statistics"""
        return {
            'fps': self.current_fps,
            'frame_scale': self.frame_scale,
            'skip_frames': self.skip_frames,
            'avg_processing_time': self.avg_processing_time
        } 

    def enable_gpu_acceleration(self):
        """Enable GPU acceleration if available"""
        try:
            # Check if CUDA is available
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                self.use_gpu = True
                self.gpu_frame = cv2.cuda_GpuMat()
                return True
        except:
            pass
        return False

    def _optimize_frame_gpu(self, frame):
        """Process frame using GPU acceleration"""
        self.gpu_frame.upload(frame)
        
        # Apply GPU-accelerated operations
        if self.frame_scale != 1.0:
            width = int(frame.shape[1] * self.frame_scale)
            height = int(frame.shape[0] * self.frame_scale)
            self.gpu_frame = cv2.cuda.resize(self.gpu_frame, (width, height))
        
        # Download result back to CPU
        return self.gpu_frame.download()

    def _dynamic_quality_adjustment(self):
        """Dynamically adjust processing quality based on performance"""
        if self.current_fps < self.target_fps * 0.6:  # Severe performance issues
            self.frame_scale = max(0.4, self.frame_scale - 0.15)
            self.skip_frames = min(2, self.skip_frames + 1)
        elif self.current_fps < self.target_fps * 0.8:  # Minor performance issues
            self.frame_scale = max(0.6, self.frame_scale - 0.1)
        elif self.current_fps > self.target_fps * 1.2:  # Excess performance
            self.frame_scale = min(1.0, self.frame_scale + 0.1)
            self.skip_frames = max(0, self.skip_frames - 1) 