"""
Camera Registry and Factory for ISKCON-Broadcast

This module provides a registry system for camera plugins and a factory
for creating camera instances. It supports automatic plugin discovery
and registration through decorators.
"""

from typing import Dict, Type, List
import logging
from .camera_interface import CameraInterface

logger = logging.getLogger(__name__)


class CameraRegistry:
    """Registry for camera plugin types"""
    
    _cameras: Dict[str, Type[CameraInterface]] = {}
    
    @classmethod
    def register(cls, camera_type: str, camera_class: Type[CameraInterface]) -> None:
        """
        Register a camera implementation
        
        Args:
            camera_type: String identifier for the camera type
            camera_class: Camera class that implements CameraInterface
        """
        if not issubclass(camera_class, CameraInterface):
            raise ValueError(f"Camera class {camera_class.__name__} must inherit from CameraInterface")
        
        if camera_type in cls._cameras:
            logger.warning(f"Overriding existing camera type: {camera_type}")
        
        cls._cameras[camera_type] = camera_class
        logger.info(f"Registered camera type: {camera_type} -> {camera_class.__name__}")
    
    @classmethod
    def create_camera(cls, camera_type: str, camera_id: int, config: dict) -> CameraInterface:
        """
        Factory method to create camera instances
        
        Args:
            camera_type: Type of camera to create
            camera_id: Unique identifier for the camera
            config: Configuration dictionary for the camera
            
        Returns:
            Camera instance implementing CameraInterface
            
        Raises:
            ValueError: If camera_type is not registered
        """
        if camera_type not in cls._cameras:
            available_types = list(cls._cameras.keys())
            raise ValueError(
                f"Unknown camera type: {camera_type}. "
                f"Available types: {available_types}"
            )
        
        camera_class = cls._cameras[camera_type]
        logger.info(f"Creating camera: {camera_type} (id={camera_id})")
        
        try:
            return camera_class(camera_id, config)
        except Exception as e:
            logger.error(f"Failed to create camera {camera_type} (id={camera_id}): {e}")
            raise
    
    @classmethod
    def list_available_cameras(cls) -> List[str]:
        """
        List all registered camera types
        
        Returns:
            List of available camera type strings
        """
        return list(cls._cameras.keys())
    
    @classmethod
    def get_camera_class(cls, camera_type: str) -> Type[CameraInterface]:
        """
        Get the camera class for a given type
        
        Args:
            camera_type: Type of camera
            
        Returns:
            Camera class
            
        Raises:
            ValueError: If camera_type is not registered
        """
        if camera_type not in cls._cameras:
            raise ValueError(f"Unknown camera type: {camera_type}")
        return cls._cameras[camera_type]
    
    @classmethod
    def unregister(cls, camera_type: str) -> bool:
        """
        Unregister a camera type
        
        Args:
            camera_type: Type of camera to unregister
            
        Returns:
            True if camera was unregistered, False if it wasn't registered
        """
        if camera_type in cls._cameras:
            del cls._cameras[camera_type]
            logger.info(f"Unregistered camera type: {camera_type}")
            return True
        return False
    
    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered camera types (mainly for testing)"""
        cls._cameras.clear()
        logger.info("Cleared camera registry")


def register_camera(camera_type: str):
    """
    Decorator for easy camera registration
    
    Args:
        camera_type: String identifier for the camera type
        
    Example:
        @register_camera("mock")
        class MockCamera(CameraInterface):
            pass
    """
    def decorator(camera_class: Type[CameraInterface]):
        CameraRegistry.register(camera_type, camera_class)
        return camera_class
    return decorator


def create_cameras_from_config(cameras_config: List[dict]) -> List[CameraInterface]:
    """
    Create multiple cameras from configuration
    
    Args:
        cameras_config: List of camera configuration dictionaries
        
    Returns:
        List of camera instances
        
    Example:
        cameras_config = [
            {"id": 0, "type": "ip_camera", "rtsp_url": "rtsp://..."},
            {"id": 1, "type": "mock", "source": "video", "video_path": "test.mp4"}
        ]
    """
    cameras = []
    
    for i, cam_config in enumerate(cameras_config):
        camera_id = cam_config.get('id', i)
        camera_type = cam_config.get('type', 'ip_camera')  # Default to existing type
        
        try:
            camera = CameraRegistry.create_camera(camera_type, camera_id, cam_config)
            cameras.append(camera)
        except Exception as e:
            logger.error(f"Failed to create camera {camera_id}: {e}")
            # Continue with other cameras rather than failing completely
    
    return cameras 