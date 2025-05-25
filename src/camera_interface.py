"""
Abstract Camera Interface for ISKCON-Broadcast

This module defines the base interface that all camera implementations must follow.
This ensures consistent behavior across different camera types (IP cameras, mock cameras, 
ONVIF cameras, USB cameras, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)


class CameraInterface(ABC):
    """Abstract base class for all camera implementations"""
    
    def __init__(self, camera_id: int, config: Dict[str, Any]):
        """
        Initialize camera with ID and configuration
        
        Args:
            camera_id: Unique identifier for this camera
            config: Camera-specific configuration dictionary
        """
        self.camera_id = camera_id
        self.config = config
        self.running = False
        self.frame = None
        
    @abstractmethod
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get current frame from camera
        
        Returns:
            Current frame as numpy array (BGR format) or None if no frame available
        """
        pass
    
    @abstractmethod
    def send_ptz_command(self, command: str, parameter: str, id: int = 0) -> bool:
        """
        Send PTZ (Pan-Tilt-Zoom) command to camera
        
        Args:
            command: Command type (e.g., "PtzCtrl")
            parameter: Command parameter (e.g., "Left", "Right", "ZoomInc", "ToPos")
            id: Additional identifier for command (e.g., preset position)
            
        Returns:
            True if command was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def capture_frames(self) -> None:
        """
        Start capturing frames (usually in separate thread)
        This method should run continuously until stop() is called
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop camera capture and cleanup resources
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if camera is connected and responding
        
        Returns:
            True if camera is connected and operational, False otherwise
        """
        pass
    
    def get_camera_info(self) -> Dict[str, Any]:
        """
        Get camera information and status
        
        Returns:
            Dictionary containing camera information
        """
        return {
            'camera_id': self.camera_id,
            'type': self.__class__.__name__,
            'running': self.running,
            'connected': self.is_connected(),
            'config': self.config
        }
    
    def __str__(self) -> str:
        """String representation of camera"""
        return f"{self.__class__.__name__}(id={self.camera_id}, running={self.running})"
    
    def __repr__(self) -> str:
        """Detailed string representation of camera"""
        return f"{self.__class__.__name__}(camera_id={self.camera_id}, config={self.config})" 