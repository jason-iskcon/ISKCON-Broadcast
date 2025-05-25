"""
Mock Camera Plugin for ISKCON-Broadcast

This module provides a mock camera implementation for development
and testing without requiring actual camera hardware.
"""

import cv2
import numpy as np
import threading
import time
import logging
from typing import Optional, List
import os

from camera_interface import CameraInterface
from camera_registry import register_camera

logger = logging.getLogger(__name__)


@register_camera("mock")
class MockCamera(CameraInterface):
    """
    Mock camera for development/testing without hardware
    
    Supports multiple input sources:
    - Video files (MP4, AVI, etc.)
    - Static images (JPG, PNG, etc.)
    - Generated content (colored frames with text)
    - Webcam fallback
    """
    
    def __init__(self, camera_id: int, config: dict):
        """
        Initialize mock camera
        
        Args:
            camera_id: Unique identifier for this camera
            config: Configuration dictionary containing:
                - source: 'video', 'images', 'generated', or 'webcam'
                - video_path: Path to video file (for 'video' source)
                - image_paths: List of image paths (for 'images' source)
                - webcam_index: Webcam index (for 'webcam' source, default 0)
                - fps: Frame rate for playback (default 30)
                - loop: Whether to loop video/images (default True)
                - width: Frame width (default 640)
                - height: Frame height (default 480)
        """
        super().__init__(camera_id, config)
        
        self.source = config.get('source', 'generated')
        self.fps = config.get('fps', 30)
        self.loop = config.get('loop', True)
        self.width = config.get('width', 640)
        self.height = config.get('height', 480)
        
        self._cap = None
        self._capture_thread = None
        self._frame_count = 0
        self._last_frame_time = 0
        
        # Initialize based on source type
        self._init_source()
        
        logger.info(f"Created mock camera {camera_id} with source: {self.source}")
    
    def _init_source(self):
        """Initialize the camera source based on configuration"""
        if self.source == 'video':
            self._init_video_source()
        elif self.source == 'images':
            self._init_images_source()
        elif self.source == 'webcam':
            self._init_webcam_source()
        elif self.source == 'generated':
            self._init_generated_source()
        else:
            raise ValueError(f"Unknown mock camera source: {self.source}")
    
    def _init_video_source(self):
        """Initialize video file source"""
        video_path = self.config.get('video_path', '')
        if not video_path or not os.path.exists(video_path):
            raise ValueError(f"Video file not found: {video_path}")
        
        self._cap = cv2.VideoCapture(video_path)
        if not self._cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        self.fps = self._cap.get(cv2.CAP_PROP_FPS) or self.fps
        logger.info(f"Loaded video: {video_path} ({self.fps} fps)")
    
    def _init_images_source(self):
        """Initialize static images source"""
        self.image_paths = self.config.get('image_paths', [])
        if not self.image_paths:
            # Use default test image if none provided
            self.image_paths = [self._create_test_image()]
        
        self.current_image = 0
        logger.info(f"Loaded {len(self.image_paths)} images")
    
    def _init_webcam_source(self):
        """Initialize webcam source"""
        webcam_index = self.config.get('webcam_index', 0)
        self._cap = cv2.VideoCapture(webcam_index)
        if not self._cap.isOpened():
            raise ValueError(f"Could not open webcam {webcam_index}")
        
        # Set webcam properties
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        logger.info(f"Opened webcam {webcam_index}")
    
    def _init_generated_source(self):
        """Initialize generated content source"""
        # No initialization needed for generated content
        logger.info("Using generated content source")
    
    def _create_test_image(self) -> str:
        """Create a test image and return its path"""
        # Create a simple test image
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        img[:] = (64, 128, 192)  # Blue-ish background
        
        # Add text
        text = f"Mock Camera {self.camera_id}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = (self.height + text_size[1]) // 2
        cv2.putText(img, text, (text_x, text_y), font, 1, (255, 255, 255), 2)
        
        # Save to assets directory
        test_image_path = f"../assets/mock_camera_{self.camera_id}_test.jpg"
        cv2.imwrite(test_image_path, img)
        return test_image_path
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame from mock camera"""
        return self.frame
    
    def send_ptz_command(self, command: str, parameter: str, id: int = 0) -> bool:
        """
        Mock PTZ command - just log the command
        
        Args:
            command: Command type
            parameter: Command parameter
            id: Additional identifier
            
        Returns:
            Always True (mock implementation)
        """
        logger.info(f"Mock PTZ command on camera {self.camera_id}: {command} {parameter} (id={id})")
        return True
    
    def capture_frames(self) -> None:
        """Start capturing frames in a separate thread"""
        if self.running:
            logger.warning(f"Mock camera {self.camera_id} is already capturing frames")
            return
        
        self.running = True
        self._capture_thread = threading.Thread(
            target=self._capture_loop,
            name=f"MockCamera-{self.camera_id}-Capture"
        )
        self._capture_thread.daemon = True
        self._capture_thread.start()
        logger.info(f"Started frame capture for mock camera {self.camera_id}")
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        frame_interval = 1.0 / self.fps
        
        while self.running:
            start_time = time.time()
            
            # Generate frame based on source type
            if self.source == 'video':
                self.frame = self._get_video_frame()
            elif self.source == 'images':
                self.frame = self._get_image_frame()
            elif self.source == 'webcam':
                self.frame = self._get_webcam_frame()
            elif self.source == 'generated':
                self.frame = self._get_generated_frame()
            
            self._frame_count += 1
            
            # Maintain frame rate
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _get_video_frame(self) -> Optional[np.ndarray]:
        """Get frame from video file"""
        if not self._cap or not self._cap.isOpened():
            return None
        
        ret, frame = self._cap.read()
        if not ret:
            if self.loop:
                # Restart video from beginning
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self._cap.read()
            if not ret:
                return None
        
        return frame
    
    def _get_image_frame(self) -> Optional[np.ndarray]:
        """Get frame from image sequence"""
        if not self.image_paths:
            return None
        
        image_path = self.image_paths[self.current_image]
        frame = cv2.imread(image_path)
        
        if frame is None:
            logger.warning(f"Could not load image: {image_path}")
            return None
        
        # Move to next image
        if self.loop:
            self.current_image = (self.current_image + 1) % len(self.image_paths)
        
        return frame
    
    def _get_webcam_frame(self) -> Optional[np.ndarray]:
        """Get frame from webcam"""
        if not self._cap or not self._cap.isOpened():
            return None
        
        ret, frame = self._cap.read()
        return frame if ret else None
    
    def _get_generated_frame(self) -> np.ndarray:
        """Generate a synthetic frame"""
        # Create frame with changing colors
        hue = (self._frame_count * 2) % 180
        color = cv2.cvtColor(np.uint8([[[hue, 255, 200]]]), cv2.COLOR_HSV2BGR)[0][0]
        
        frame = np.full((self.height, self.width, 3), color, dtype=np.uint8)
        
        # Add camera info text
        text_lines = [
            f"Mock Camera {self.camera_id}",
            f"Frame: {self._frame_count}",
            f"Time: {time.strftime('%H:%M:%S')}",
            f"Source: {self.source}"
        ]
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 1
        line_height = 25
        
        for i, line in enumerate(text_lines):
            y = 30 + i * line_height
            cv2.putText(frame, line, (10, y), font, font_scale, (255, 255, 255), thickness)
        
        return frame
    
    def stop(self) -> None:
        """Stop camera capture and cleanup"""
        if not self.running:
            return
        
        self.running = False
        
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=2.0)
        
        if self._cap:
            self._cap.release()
            self._cap = None
        
        logger.info(f"Stopped mock camera {self.camera_id}")
    
    def is_connected(self) -> bool:
        """
        Check if mock camera is "connected"
        
        Returns:
            True if source is available, False otherwise
        """
        if self.source == 'video' or self.source == 'webcam':
            return self._cap is not None and self._cap.isOpened()
        elif self.source == 'images':
            return len(self.image_paths) > 0
        elif self.source == 'generated':
            return True
        return False
    
    def get_camera_info(self) -> dict:
        """Get mock camera information"""
        info = super().get_camera_info()
        info.update({
            'source': self.source,
            'fps': self.fps,
            'frame_count': self._frame_count,
            'resolution': f"{self.width}x{self.height}"
        })
        
        if self.source == 'video':
            info['video_path'] = self.config.get('video_path', '')
        elif self.source == 'images':
            info['image_count'] = len(self.image_paths)
        elif self.source == 'webcam':
            info['webcam_index'] = self.config.get('webcam_index', 0)
        
        return info 