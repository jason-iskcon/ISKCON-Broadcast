"""
Camera Plugins Package for ISKCON-Broadcast

This package contains all camera plugin implementations.
Each camera type should be in its own module and register itself
using the @register_camera decorator.
"""

# Import all camera implementations to trigger registration
import cameras.ip_camera
import cameras.mock_camera

# Make camera types available at package level
__all__ = ['ip_camera', 'mock_camera'] 