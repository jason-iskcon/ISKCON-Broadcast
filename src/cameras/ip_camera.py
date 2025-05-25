"""
IP Camera Plugin for ISKCON-Broadcast

This module provides a wrapper around the existing Camera class
to make it compatible with the plugin interface without modifying
the original camera.py file.
"""

import threading
import logging
from typing import Optional
import numpy as np

from camera_interface import CameraInterface
from camera_registry import register_camera
from camera import Camera  # Import the existing Camera class

logger = logging.getLogger(__name__)


@register_camera("ip_camera")
class IPCamera(CameraInterface):
    """
    Wrapper for existing Camera class to match plugin interface
    
    This maintains backward compatibility with existing configurations
    while providing the new plugin interface.
    """
    
    def __init__(self, camera_id: int, config: dict):
        """
        Initialize IP camera wrapper
        
        Args:
            camera_id: Unique identifier for this camera
            config: Configuration dictionary containing:
                - rtsp_url: RTSP stream URL
                - https: Dictionary with ip, username, password
        """
        super().__init__(camera_id, config)
        
        # Extract configuration for the original Camera class
        rtsp_url = config.get('rtsp_url', '')
        https_config = config.get('https', {})
        ip = https_config.get('ip', '')
        username = https_config.get('username', '')
        password = https_config.get('password', '')
        
        # Validate required configuration
        if not all([rtsp_url, ip, username, password]):
            raise ValueError(
                f"IP camera {camera_id} missing required configuration. "
                f"Need: rtsp_url, https.ip, https.username, https.password"
            )
        
        # Create the original Camera instance
        try:
            self._camera = Camera(
                camera_id=camera_id,
                rtsp_url=rtsp_url,
                ip=ip,
                username=username,
                password=password
            )
            logger.info(f"Created IP camera {camera_id} for {ip}")
        except Exception as e:
            logger.error(f"Failed to create IP camera {camera_id}: {e}")
            raise
        
        self._capture_thread = None
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get current frame from camera
        
        Returns:
            Current frame as numpy array or None if no frame available
        """
        return self._camera.get_frame()
    
    def send_ptz_command(self, command: str, parameter: str, id: int = 0) -> bool:
        """
        Send PTZ command to camera
        
        Args:
            command: Command type (e.g., "PtzCtrl")
            parameter: Command parameter (e.g., "Left", "Right", "ZoomInc", "ToPos")
            id: Additional identifier for command (e.g., preset position)
            
        Returns:
            True if command was sent successfully, False otherwise
        """
        try:
            self._camera.send_ptz_command(command, parameter, id)
            logger.debug(f"Sent PTZ command to camera {self.camera_id}: {command} {parameter}")
            return True
        except Exception as e:
            logger.error(f"Failed to send PTZ command to camera {self.camera_id}: {e}")
            return False
    
    def capture_frames(self) -> None:
        """
        Start capturing frames in a separate thread
        """
        if self.running:
            logger.warning(f"Camera {self.camera_id} is already capturing frames")
            return
        
        self.running = True
        self._capture_thread = threading.Thread(
            target=self._camera.capture_frames,
            name=f"IPCamera-{self.camera_id}-Capture"
        )
        self._capture_thread.daemon = True
        self._capture_thread.start()
        logger.info(f"Started frame capture for IP camera {self.camera_id}")
    
    def stop(self) -> None:
        """
        Stop camera capture and cleanup
        """
        if not self.running:
            return
        
        self.running = False
        self._camera.stop()
        
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=5.0)
            if self._capture_thread.is_alive():
                logger.warning(f"Camera {self.camera_id} capture thread did not stop gracefully")
        
        logger.info(f"Stopped IP camera {self.camera_id}")
    
    def is_connected(self) -> bool:
        """
        Check if camera is connected and responding
        
        Returns:
            True if camera has a valid token (is authenticated), False otherwise
        """
        return hasattr(self._camera, 'token') and self._camera.token is not None
    
    def get_camera_info(self) -> dict:
        """
        Get camera information including IP camera specific details
        
        Returns:
            Dictionary containing camera information
        """
        info = super().get_camera_info()
        info.update({
            'ip': self.config.get('https', {}).get('ip', ''),
            'rtsp_url': self.config.get('rtsp_url', ''),
            'has_token': hasattr(self._camera, 'token') and self._camera.token is not None
        })
        return info 