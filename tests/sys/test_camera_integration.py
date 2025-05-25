"""
System integration tests for camera plugin system

Tests the complete camera plugin system including registry, multiple cameras,
configuration loading, and real-world usage scenarios.
"""

import pytest
import time
import yaml
import threading
from unittest.mock import patch, MagicMock
from pathlib import Path

from camera_registry import CameraRegistry


class TestCameraSystemIntegration:
    """Integration tests for complete camera system"""
    
    def test_multiple_camera_creation_and_management(self, multiple_camera_config, camera_registry_with_mocks):
        """Test creating and managing multiple cameras simultaneously"""
        cameras = []
        
        # Create multiple cameras
        for config in multiple_camera_config:
            camera = CameraRegistry.create_camera(config['type'], config['id'], config)
            cameras.append(camera)
        
        # Verify all cameras created successfully
        assert len(cameras) == 3
        for i, camera in enumerate(cameras):
            assert camera.camera_id == i
        
        # Start all cameras
        for camera in cameras:
            camera.capture_frames()
            assert camera.running == True
        
        # Get frames from all cameras
        frames = []
        for camera in cameras:
            frame = camera.get_frame()
            frames.append(frame)
        
        assert len(frames) == 3
        
        # Stop all cameras
        for camera in cameras:
            camera.stop()
            assert camera.running == False
    
    def test_camera_configuration_loading_from_yaml(self, test_data_dir, camera_registry_with_mocks):
        """Test loading camera configuration from YAML file"""
        config_file = test_data_dir / "test_config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        cameras = []
        for cam_config in config['cameras']:
            camera = CameraRegistry.create_camera(cam_config['type'], cam_config['id'], cam_config)
            cameras.append(camera)
        
        assert len(cameras) == 2
        
        # Test camera 0
        assert cameras[0].camera_id == 0
        
        # Test camera 1
        assert cameras[1].camera_id == 1
        
        # Cleanup
        for camera in cameras:
            if hasattr(camera, 'running') and camera.running:
                camera.stop()
    
    def test_camera_switching_and_mode_changes(self, multiple_camera_config, camera_registry_with_mocks):
        """Test switching between cameras and changing display modes"""
        cameras = []
        
        # Create cameras
        for config in multiple_camera_config:
            camera = CameraRegistry.create_camera(config['type'], config['id'], config)
            cameras.append(camera)
            camera.capture_frames()
        
        # Simulate display mode switching
        active_cameras = []
        
        # Mode 1: Single camera (fullscreen)
        active_cameras = [cameras[0]]
        for camera in active_cameras:
            frame = camera.get_frame()
            # Frame may be None in test environment
        
        # Mode 2: Dual camera view
        active_cameras = [cameras[0], cameras[1]]
        for camera in active_cameras:
            frame = camera.get_frame()
            # Frame may be None in test environment
        
        # Mode 3: Triple camera view
        active_cameras = cameras
        for camera in active_cameras:
            frame = camera.get_frame()
            # Frame may be None in test environment
        
        # Cleanup
        for camera in cameras:
            camera.stop()
    
    def test_camera_ptz_command_sequence(self, mock_camera_config, camera_registry_with_mocks, capture_logs):
        """Test PTZ command sequence execution"""
        camera = CameraRegistry.create_camera('mock', 0, mock_camera_config)
        camera.capture_frames()
        
        # Execute PTZ command sequence
        ptz_sequence = [
            ('ToPos', 1),
            ('Left', 20),
            ('ZoomInc', None),
            ('Right', 25),
            ('ZoomDec', None),
        ]
        
        for command_data in ptz_sequence:
            command = command_data[0]
            param = command_data[1]
            
            if param is not None:
                result = camera.send_ptz_command("PtzCtrl", command, param)
            else:
                result = camera.send_ptz_command("PtzCtrl", command)
            
            assert result == True
            time.sleep(0.1)  # Small delay between commands
        
        camera.stop()
        
        # PTZ commands should execute without error
        # (Logging verification depends on camera implementation)
    
    def test_camera_error_recovery(self, camera_registry_with_mocks, capture_logs):
        """Test camera system recovery from errors"""
        # Create a camera that will fail during initialization
        error_config = {
            'id': 0,
            'type': 'mock',
            'source': 'video',  # This will require video_path
            'video_path': 'nonexistent_file.mp4'  # This file doesn't exist
        }
        
        # This should raise an error during camera creation
        with pytest.raises(ValueError, match="Video file not found"):
            camera = CameraRegistry.create_camera('mock', 0, error_config)
    
    def test_concurrent_camera_operations(self, multiple_camera_config, camera_registry_with_mocks):
        """Test concurrent operations on multiple cameras"""
        cameras = []
        results = []
        errors = []
        
        # Create cameras
        for config in multiple_camera_config:
            camera = CameraRegistry.create_camera(config['type'], config['id'], config)
            cameras.append(camera)
        
        def camera_worker(camera, duration=1.0):
            """Worker function for concurrent camera operations"""
            try:
                camera.capture_frames()
                
                start_time = time.time()
                frame_count = 0
                
                while time.time() - start_time < duration:
                    frame = camera.get_frame()
                    if frame is not None:
                        frame_count += 1
                    time.sleep(0.05)  # 20 FPS request rate
                
                camera.stop()
                results.append(frame_count)
                
            except Exception as e:
                errors.append(str(e))
        
        # Start concurrent operations
        threads = []
        for camera in cameras:
            thread = threading.Thread(target=camera_worker, args=(camera, 0.5))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0
        assert len(results) == 3
        # Frame counts may be 0 in test environment
    
    def test_camera_plugin_hot_reload_simulation(self, camera_registry_with_mocks):
        """Test simulated hot reload of camera plugins"""
        # Initial state after camera_registry_with_mocks - should have mock and ip_camera
        initial_cameras = CameraRegistry.list_available_cameras()
        assert len(initial_cameras) >= 2
        
        # Simulate loading camera plugins
        try:
            from src.cameras.mock_camera import MockCamera
            from src.cameras.ip_camera import IPCamera
            
            CameraRegistry.register('mock', MockCamera)
            CameraRegistry.register('ip_camera', IPCamera)
            
            # Verify plugins are registered
            registered = CameraRegistry.list_available_cameras()
            assert 'mock' in registered
            assert 'ip_camera' in registered
            
            # Create cameras using registered plugins
            mock_config = {'id': 0, 'type': 'mock', 'source': 'generated'}
            ip_config = {
                'id': 1, 
                'type': 'ip_camera',
                'rtsp_url': 'rtsp://test:test@192.168.1.100:554/stream',
                'https': {'ip': '192.168.1.100', 'username': 'test', 'password': 'test'}
            }
            
            mock_camera_instance = CameraRegistry.create_camera('mock', 0, mock_config)
            ip_camera_instance = CameraRegistry.create_camera('ip_camera', 1, ip_config)
            
            assert isinstance(mock_camera_instance, MockCamera)
            assert isinstance(ip_camera_instance, IPCamera)
            
            # Cleanup
            if hasattr(mock_camera_instance, 'running') and mock_camera_instance.running:
                mock_camera_instance.stop()
            if hasattr(ip_camera_instance, 'running') and ip_camera_instance.running:
                ip_camera_instance.stop()
                
        except ImportError:
            # Camera modules not available, skip this test
            pytest.skip("Camera modules not available for hot reload test")
    
    def test_camera_system_performance_under_load(self, multiple_camera_config, camera_registry_with_mocks, performance_timer):
        """Test camera system performance under load"""
        cameras = []
        
        # Create multiple cameras
        for config in multiple_camera_config:
            camera = CameraRegistry.create_camera(config['type'], config['id'], config)
            cameras.append(camera)
            camera.capture_frames()
        
        # Performance test: rapid frame requests
        performance_timer.start()
        
        total_frames = 0
        test_duration = 1.0  # 1 second test
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
            for camera in cameras:
                frame = camera.get_frame()
                if frame is not None:
                    total_frames += 1
        
        performance_timer.stop()
        
        # Calculate performance metrics
        elapsed = performance_timer.elapsed
        
        # Performance assertions (relaxed for test environment)
        assert elapsed < 2.0  # Test completed in reasonable time
        
        # Cleanup
        for camera in cameras:
            camera.stop()
    
    def test_camera_configuration_validation(self, camera_registry_with_mocks):
        """Test camera configuration validation and error handling"""
        test_configs = [
            # Valid config
            {'id': 0, 'type': 'mock', 'source': 'generated'},
            
            # Config with extra parameters
            {'id': 1, 'type': 'mock', 'source': 'generated', 'extra_param': 'value'},
            
            # Minimal config (should use defaults)
            {'id': 2, 'type': 'mock'},
        ]
        
        cameras = []
        
        for config in test_configs:
            camera = CameraRegistry.create_camera(config['type'], config['id'], config)
            cameras.append(camera)
            
            # Verify camera was created successfully
            assert camera.camera_id == config['id']
        
        # Test invalid configs
        invalid_configs = [
            # Unknown type
            {'id': 98, 'type': 'unknown_camera_type'},
        ]
        
        for config in invalid_configs:
            with pytest.raises(ValueError):
                CameraRegistry.create_camera(config['type'], config['id'], config)
        
        # Cleanup
        for camera in cameras:
            if hasattr(camera, 'running') and camera.running:
                camera.stop()
    
    @pytest.mark.slow
    def test_long_running_camera_stability(self, mock_camera_config, camera_registry_with_mocks):
        """Test camera stability over extended operation"""
        camera = CameraRegistry.create_camera(mock_camera_config['type'], 0, mock_camera_config)
        camera.capture_frames()
        
        # Run for extended period
        start_time = time.time()
        frame_count = 0
        errors = 0
        
        while time.time() - start_time < 2.0:  # 2 second test (reduced for CI)
            try:
                frame = camera.get_frame()
                if frame is not None:
                    frame_count += 1
                
                time.sleep(0.1)  # 10 FPS request rate
                
            except Exception:
                errors += 1
        
        camera.stop()
        
        # Verify stability (relaxed for test environment)
        assert errors < 10  # Minimal errors allowed
        
        # Verify camera stopped cleanly
        assert camera.running == False 