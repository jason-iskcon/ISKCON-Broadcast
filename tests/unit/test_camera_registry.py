"""
Unit tests for CameraRegistry and camera plugin system

Tests camera registration, factory creation, and plugin management.
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch

from src.camera_registry import CameraRegistry, register_camera
from src.camera_interface import CameraInterface


class TestCameraRegistry:
    """Test suite for CameraRegistry functionality"""
    
    def test_camera_registry_initial_state(self, clean_camera_registry):
        """Test that registry starts in clean state when cleaned"""
        # After clean_camera_registry fixture, should be empty
        assert len(CameraRegistry._cameras) == 0
        assert CameraRegistry.list_available_cameras() == []
    
    def test_camera_plugin_decorator(self, clean_camera_registry):
        """Test camera registration using decorator"""
        
        @register_camera("test_decorator")
        class DecoratorTestCamera(CameraInterface):
            def __init__(self, camera_id, config):
                super().__init__(camera_id, config)
            
            def capture_frames(self):
                pass
            
            def get_frame(self):
                return None
            
            def stop(self):
                pass
            
            def send_ptz_command(self, command, parameter, id=0):
                return True
            
            def is_connected(self):
                return True
        
        # Verify registration
        assert "test_decorator" in CameraRegistry.list_available_cameras()
        assert CameraRegistry.get_camera_class("test_decorator") == DecoratorTestCamera
    
    def test_register_camera_method(self, clean_camera_registry):
        """Test manual camera registration"""
        
        class ManualTestCamera(CameraInterface):
            def __init__(self, camera_id, config):
                super().__init__(camera_id, config)
            
            def capture_frames(self):
                pass
            
            def get_frame(self):
                return None
            
            def stop(self):
                pass
            
            def send_ptz_command(self, command, parameter, id=0):
                return True
            
            def is_connected(self):
                return True
        
        # Manual registration
        CameraRegistry.register("manual_test", ManualTestCamera)
        
        # Verify registration
        assert "manual_test" in CameraRegistry.list_available_cameras()
        assert CameraRegistry.get_camera_class("manual_test") == ManualTestCamera
    
    def test_create_camera_success(self, clean_camera_registry):
        """Test successful camera creation"""
        
        class FactoryTestCamera(CameraInterface):
            def __init__(self, camera_id, config):
                super().__init__(camera_id, config)
                self.test_value = config.get('test_value', 'default')
            
            def capture_frames(self):
                pass
            
            def get_frame(self):
                return None
            
            def stop(self):
                pass
            
            def send_ptz_command(self, command, parameter, id=0):
                return True
            
            def is_connected(self):
                return True
        
        # Register camera
        CameraRegistry.register("factory_test", FactoryTestCamera)
        
        # Create camera instance
        config = {'test_value': 'custom'}
        camera = CameraRegistry.create_camera('factory_test', 1, config)
        
        # Verify creation
        assert isinstance(camera, FactoryTestCamera)
        assert camera.camera_id == 1
        assert camera.config == config
        assert camera.test_value == 'custom'
    
    def test_create_camera_unknown_type(self, clean_camera_registry):
        """Test camera creation with unknown type"""
        with pytest.raises(ValueError, match="Unknown camera type"):
            CameraRegistry.create_camera('nonexistent_type', 0, {})
    
    def test_get_registered_cameras(self, clean_camera_registry):
        """Test listing registered camera types"""
        
        class CameraA(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        class CameraB(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        # Register cameras
        CameraRegistry.register("camera_a", CameraA)
        CameraRegistry.register("camera_b", CameraB)
        
        # Check registered cameras
        registered = CameraRegistry.list_available_cameras()
        assert len(registered) == 2
        assert "camera_a" in registered
        assert "camera_b" in registered
    
    def test_clear_registry(self, clean_camera_registry):
        """Test clearing the camera registry"""
        
        class TempCamera(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        # Register a camera
        CameraRegistry.register("temp", TempCamera)
        assert len(CameraRegistry.list_available_cameras()) == 1
        
        # Clear registry
        CameraRegistry.clear_registry()
        assert len(CameraRegistry.list_available_cameras()) == 0
    
    def test_duplicate_registration(self, clean_camera_registry):
        """Test handling of duplicate camera type registration"""
        
        class Camera1(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        class Camera2(CameraInterface):
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        # Register first camera
        CameraRegistry.register("duplicate_test", Camera1)
        assert CameraRegistry.get_camera_class("duplicate_test") == Camera1
        
        # Register second camera with same name (should override)
        CameraRegistry.register("duplicate_test", Camera2)
        assert CameraRegistry.get_camera_class("duplicate_test") == Camera2
    
    def test_camera_creation_with_initialization_error(self, clean_camera_registry):
        """Test camera creation when initialization fails"""
        
        class ErrorCamera(CameraInterface):
            def __init__(self, camera_id, config):
                super().__init__(camera_id, config)
                raise RuntimeError("Initialization failed")
            
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        CameraRegistry.register("error_camera", ErrorCamera)
        
        with pytest.raises(RuntimeError, match="Initialization failed"):
            CameraRegistry.create_camera('error_camera', 0, {})
    
    @pytest.mark.parametrize("camera_type,camera_id,config", [
        ("test_type_1", 0, {}),
        ("test_type_2", 5, {'fps': 30}),
        ("test_type_3", 99, {'complex': {'nested': True}}),
    ])
    def test_camera_creation_parametrized(self, clean_camera_registry, camera_type, camera_id, config):
        """Test camera creation with various parameters"""
        
        class ParametrizedCamera(CameraInterface):
            def __init__(self, camera_id, config):
                super().__init__(camera_id, config)
            
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        # Register camera
        CameraRegistry.register(camera_type, ParametrizedCamera)
        
        # Create camera
        camera = CameraRegistry.create_camera(camera_type, camera_id, config)
        
        # Verify
        assert isinstance(camera, ParametrizedCamera)
        assert camera.camera_id == camera_id
        assert camera.config == config
    
    def test_registry_thread_safety_simulation(self, clean_camera_registry):
        """Test registry operations under simulated concurrent access"""
        
        class ThreadTestCamera(CameraInterface):
            def __init__(self, camera_id, config):
                super().__init__(camera_id, config)
            
            def capture_frames(self): pass
            def get_frame(self): pass
            def stop(self): pass
            def send_ptz_command(self, command, parameter, id=0): return True
            def is_connected(self): return True
        
        results = []
        errors = []
        
        def register_and_create(thread_id):
            """Function to run in multiple threads"""
            try:
                camera_type = f"thread_camera_{thread_id}"
                
                # Register camera type
                CameraRegistry.register(camera_type, ThreadTestCamera)
                
                # Create camera instance
                camera = CameraRegistry.create_camera(camera_type, thread_id, {'thread_id': thread_id})
                
                results.append({
                    'thread_id': thread_id,
                    'camera_type': camera_type,
                    'camera_id': camera.camera_id,
                    'success': True
                })
                
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_and_create, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        # Verify all cameras were registered
        registered_cameras = CameraRegistry.list_available_cameras()
        for i in range(5):
            assert f"thread_camera_{i}" in registered_cameras 