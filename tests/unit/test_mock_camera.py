"""
Unit tests for MockCamera implementation

Tests the mock camera functionality including frame generation,
PTZ commands, and various source types.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from src.cameras.mock_camera import MockCamera


class TestMockCamera:
    """Test suite for MockCamera functionality"""
    
    def test_mock_camera_initialization(self, mock_camera_config):
        """Test MockCamera initialization with basic config"""
        camera = MockCamera(0, mock_camera_config)
        
        assert camera.camera_id == 0
        assert camera.config == mock_camera_config
        assert camera.source == mock_camera_config.get('source', 'generated')
        assert camera.fps == mock_camera_config.get('fps', 30)
        assert camera.running == False
        assert camera.frame_count == 0
    
    def test_mock_camera_generated_source(self, mock_camera_config):
        """Test MockCamera with generated content source"""
        config = {**mock_camera_config, 'source': 'generated'}
        camera = MockCamera(0, config)
        
        # Start frame capture
        camera.capture_frames()
        time.sleep(0.2)  # Let it generate some frames
        
        frame = camera.get_frame()
        assert frame is not None
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (config.get('height', 480), config.get('width', 640), 3)
        assert frame.dtype == np.uint8
        
        camera.stop()
    
    @patch('cv2.VideoCapture')
    @patch('os.path.exists')
    def test_mock_camera_video_file_source(self, mock_exists, mock_cv2_cap, mock_camera_config):
        """Test MockCamera with video file source"""
        mock_exists.return_value = True
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.return_value = 30.0  # FPS
        mock_cv2_cap.return_value = mock_cap_instance
        
        config = {
            **mock_camera_config,
            'source': 'video',
            'video_path': 'test_video.mp4'
        }
        
        camera = MockCamera(0, config)
        assert camera.source == 'video'
        
        # Verify video capture was initialized
        mock_cv2_cap.assert_called_with('test_video.mp4')
        mock_cap_instance.isOpened.assert_called()
    
    def test_mock_camera_webcam_source(self, mock_camera_config):
        """Test MockCamera with webcam source"""
        with patch('cv2.VideoCapture') as mock_cv2_cap:
            mock_cap_instance = MagicMock()
            mock_cap_instance.isOpened.return_value = True
            mock_cv2_cap.return_value = mock_cap_instance
            
            config = {
                **mock_camera_config,
                'source': 'webcam',
                'webcam_index': 0
            }
            
            camera = MockCamera(0, config)
            assert camera.source == 'webcam'
            
            # Verify webcam capture was initialized
            mock_cv2_cap.assert_called_with(0)
            mock_cap_instance.set.assert_any_call(3, 640)  # CAP_PROP_FRAME_WIDTH
            mock_cap_instance.set.assert_any_call(4, 480)  # CAP_PROP_FRAME_HEIGHT
    
    @patch('cv2.imread')
    def test_mock_camera_static_image_source(self, mock_imread, mock_camera_config):
        """Test MockCamera with static image source"""
        # Mock successful image loading
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imread.return_value = mock_frame
        
        config = {
            **mock_camera_config,
            'source': 'images',
            'image_paths': ['test_image.jpg']
        }
        
        camera = MockCamera(0, config)
        assert camera.source == 'images'
        assert camera.image_paths == ['test_image.jpg']
    
    def test_mock_camera_frame_generation_content(self, mock_camera_config):
        """Test that generated frames have correct content and properties"""
        config = {**mock_camera_config, 'source': 'generated', 'width': 320, 'height': 240}
        camera = MockCamera(0, config)
        
        # Start frame capture
        camera.capture_frames()
        time.sleep(0.1)  # Let it generate frames
        
        frame = camera.get_frame()
        assert frame is not None
        assert frame.shape == (240, 320, 3)
        assert frame.dtype == np.uint8
        
        # Check that frame contains camera info text
        # (This is a basic check - in real implementation, text would be rendered)
        assert np.any(frame > 0)  # Frame should not be all zeros
        
        camera.stop()
    
    def test_mock_camera_frame_count_increment(self, mock_camera_config):
        """Test that frame count increments during capture"""
        camera = MockCamera(0, mock_camera_config)
        
        initial_count = camera.frame_count
        assert initial_count == 0
        
        # Start frame capture
        camera.capture_frames()
        time.sleep(0.2)  # Let it generate frames
        
        final_count = camera.frame_count
        assert final_count > initial_count
        
        camera.stop()
    
    def test_mock_camera_ptz_commands(self, mock_camera_config):
        """Test PTZ command handling"""
        camera = MockCamera(0, mock_camera_config)
        
        # Test various PTZ commands
        assert camera.send_ptz_command("PtzCtrl", "Left", 25) == True
        assert camera.send_ptz_command("PtzCtrl", "Right", 25) == True
        assert camera.send_ptz_command("PtzCtrl", "Up", 25) == True
        assert camera.send_ptz_command("PtzCtrl", "Down", 25) == True
        assert camera.send_ptz_command("PtzCtrl", "ZoomInc") == True
        assert camera.send_ptz_command("PtzCtrl", "ZoomDec") == True
        assert camera.send_ptz_command("PtzCtrl", "ToPos", 5) == True
    
    def test_mock_camera_stop_behavior(self, mock_camera_config):
        """Test camera stop behavior"""
        camera = MockCamera(0, mock_camera_config)
        
        # Start camera
        camera.capture_frames()
        assert camera.running == True
        
        # Stop camera
        camera.stop()
        assert camera.running == False
    
    def test_mock_camera_get_frame_when_stopped(self, mock_camera_config):
        """Test getting frame when camera is stopped"""
        camera = MockCamera(0, mock_camera_config)
        
        # Camera not started - should return None
        frame = camera.get_frame()
        assert frame is None
    
    @pytest.mark.parametrize("fps,width,height", [
        (15, 320, 240),
        (30, 640, 480),
        (60, 1280, 720),
        (25, 800, 600),
    ])
    def test_mock_camera_various_configurations(self, fps, width, height):
        """Test MockCamera with various configurations"""
        config = {
            'source': 'generated',
            'fps': fps,
            'width': width,
            'height': height
        }
        
        camera = MockCamera(0, config)
        assert camera.fps == fps
        assert camera.width == width
        assert camera.height == height
        
        # Start frame capture
        camera.capture_frames()
        time.sleep(0.1)  # Let it generate frames
        
        frame = camera.get_frame()
        assert frame is not None
        assert frame.shape == (height, width, 3)
        
        camera.stop()
    
    def test_mock_camera_video_file_not_found(self, mock_camera_config):
        """Test MockCamera behavior with non-existent video file"""
        config = {
            **mock_camera_config,
            'source': 'video',
            'video_path': 'nonexistent_video.mp4'
        }
        
        with pytest.raises(ValueError, match="Video file not found"):
            MockCamera(0, config)
    
    def test_mock_camera_threading_behavior(self, mock_camera_config):
        """Test MockCamera threading behavior"""
        camera = MockCamera(0, mock_camera_config)
        
        # Start capture
        camera.capture_frames()
        assert camera.running == True
        assert camera._capture_thread is not None
        
        # Stop capture
        camera.stop()
        assert camera.running == False
        
        # Thread should be cleaned up
        if camera._capture_thread:
            assert not camera._capture_thread.is_alive()
    
    def test_mock_camera_frame_timing(self, mock_camera_config):
        """Test frame timing and FPS"""
        config = {**mock_camera_config, 'fps': 60}  # High FPS for timing test
        camera = MockCamera(0, config)
        
        camera.capture_frames()
        
        # Measure frame generation over short period
        start_time = time.time()
        start_count = camera.frame_count
        
        time.sleep(0.5)  # Half second
        
        end_time = time.time()
        end_count = camera.frame_count
        
        elapsed = end_time - start_time
        frames_generated = end_count - start_count
        measured_fps = frames_generated / elapsed
        
        # Should be reasonably close to target FPS (within 50% tolerance)
        assert measured_fps > config['fps'] * 0.5
        
        camera.stop()
    
    def test_mock_camera_config_validation(self, mock_camera_config):
        """Test configuration validation and defaults"""
        # Test with minimal config
        minimal_config = {'source': 'generated'}
        camera = MockCamera(0, minimal_config)
        
        # Should use defaults
        assert camera.fps == 30
        assert camera.width == 640
        assert camera.height == 480
        assert camera.loop == True
    
    def test_mock_camera_cleanup_on_exception(self, mock_camera_config):
        """Test that camera cleans up properly on exceptions"""
        camera = MockCamera(0, mock_camera_config)
        
        camera.capture_frames()
        assert camera.running == True
        
        # Force stop (simulating exception handling)
        camera.stop()
        assert camera.running == False
        
        # Should be able to restart
        camera.capture_frames()
        assert camera.running == True
        
        camera.stop()
    
    def test_mock_camera_is_connected(self, mock_camera_config):
        """Test is_connected method"""
        camera = MockCamera(0, mock_camera_config)
        
        # Generated source should always be connected
        assert camera.is_connected() == True
    
    def test_mock_camera_get_camera_info(self, mock_camera_config):
        """Test get_camera_info method"""
        camera = MockCamera(0, mock_camera_config)
        
        info = camera.get_camera_info()
        
        assert info['camera_id'] == 0
        assert info['type'] == 'MockCamera'
        assert info['source'] == mock_camera_config.get('source', 'generated')
        assert info['fps'] == mock_camera_config.get('fps', 30)
        assert info['frame_count'] == 0  # No frames generated yet
        assert 'resolution' in info 