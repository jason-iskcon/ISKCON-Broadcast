"""
Unit tests for CameraInterface abstract base class

Tests the abstract interface definition and ensures proper inheritance
requirements for camera implementations.
"""

import pytest
from abc import ABC, abstractmethod
from unittest.mock import Mock, patch
import numpy as np

from src.camera_interface import CameraInterface


class TestCameraInterface:
    """Test suite for CameraInterface abstract base class"""
    
    def test_camera_interface_is_abstract(self):
        """Test that CameraInterface cannot be instantiated directly"""
        with pytest.raises(TypeError):
            CameraInterface(0, {})
    
    def test_camera_interface_abstract_methods(self):
        """Test that all required abstract methods are defined"""
        abstract_methods = CameraInterface.__abstractmethods__
        expected_methods = {
            'capture_frames',
            'get_frame', 
            'stop',
            'send_ptz_command',
            'is_connected'
        }
        
        assert abstract_methods == expected_methods
    
    def test_concrete_implementation_required_methods(self):
        """Test that concrete implementations must implement all abstract methods"""
        
        class IncompleteCameraImpl(CameraInterface):
            # Missing required abstract methods
            pass
        
        with pytest.raises(TypeError):
            IncompleteCameraImpl(0, {})
    
    def test_complete_concrete_implementation(self):
        """Test that complete implementations can be instantiated"""
        
        class CompleteCameraImpl(CameraInterface):
            def __init__(self, camera_id, config):
                super().__init__(camera_id, config)
                self.frames = []
                self.running = False
            
            def capture_frames(self):
                self.running = True
            
            def get_frame(self):
                return np.zeros((480, 640, 3), dtype=np.uint8)
            
            def stop(self):
                self.running = False
            
            def send_ptz_command(self, command, parameter, id=0):
                return True
            
            def is_connected(self):
                return True
        
        # Should not raise any exceptions
        camera = CompleteCameraImpl(0, {'test': 'config'})
        assert camera.camera_id == 0
        assert camera.config == {'test': 'config'}
    
    def test_camera_interface_initialization(self):
        """Test that CameraInterface properly initializes base attributes"""
        
        class TestCamera(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        config = {'type': 'test', 'fps': 30}
        camera = TestCamera(42, config)
        
        assert camera.camera_id == 42
        assert camera.config == config
        assert camera.running == False
        assert camera.frame is None
    
    def test_camera_interface_method_signatures(self):
        """Test that abstract methods have correct signatures"""
        
        class TestCamera(CameraInterface):
            def capture_frames(self):
                return "capture_frames_called"
            
            def get_frame(self):
                return "get_frame_called"
            
            def stop(self):
                return "stop_called"
            
            def send_ptz_command(self, command, parameter, id=0):
                return f"ptz_{command}_{parameter}_{id}"
            
            def is_connected(self):
                return True
        
        camera = TestCamera(0, {})
        
        # Test method calls
        assert camera.capture_frames() == "capture_frames_called"
        assert camera.get_frame() == "get_frame_called"
        assert camera.stop() == "stop_called"
        
        # Test PTZ command method
        assert camera.send_ptz_command("PtzCtrl", "Left") == "ptz_PtzCtrl_Left_0"
        assert camera.send_ptz_command("PtzCtrl", "ToPos", 5) == "ptz_PtzCtrl_ToPos_5"
        
        # Test connection check
        assert camera.is_connected() == True
    
    def test_camera_interface_inheritance_chain(self):
        """Test that CameraInterface properly inherits from ABC"""
        assert issubclass(CameraInterface, ABC)
        assert hasattr(CameraInterface, '__abstractmethods__')
    
    def test_camera_interface_get_camera_info(self):
        """Test the get_camera_info method"""
        
        class TestCamera(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        config = {'type': 'test', 'fps': 30}
        camera = TestCamera(42, config)
        
        info = camera.get_camera_info()
        
        assert info['camera_id'] == 42
        assert info['type'] == 'TestCamera'
        assert info['running'] == False
        assert info['connected'] == True
        assert info['config'] == config
    
    def test_camera_interface_string_representations(self):
        """Test __str__ and __repr__ methods"""
        
        class TestCamera(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        config = {'type': 'test'}
        camera = TestCamera(42, config)
        
        str_repr = str(camera)
        assert "TestCamera" in str_repr
        assert "id=42" in str_repr
        assert "running=False" in str_repr
        
        repr_str = repr(camera)
        assert "TestCamera" in repr_str
        assert "camera_id=42" in repr_str
        assert "config=" in repr_str
    
    @pytest.mark.parametrize("camera_id,config", [
        (0, {}),
        (1, {'type': 'test'}),
        (99, {'complex': {'nested': 'config'}}),
        (-1, {'negative_id': True}),
    ])
    def test_camera_interface_various_configs(self, camera_id, config):
        """Test CameraInterface with various camera IDs and configurations"""
        
        class MinimalCamera(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        camera = MinimalCamera(camera_id, config)
        assert camera.camera_id == camera_id
        assert camera.config == config 