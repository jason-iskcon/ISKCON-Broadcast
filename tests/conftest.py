"""
Pytest configuration and shared fixtures for ISKCON-Broadcast tests

This module provides common fixtures, test utilities, and configuration
for all test suites in the ISKCON-Broadcast testing framework.
"""

import pytest
import sys
import os
import tempfile
import shutil
import logging
import threading
import time
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import core modules for testing
from camera_interface import CameraInterface
from camera_registry import CameraRegistry, register_camera


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def temp_dir():
    """Fixture providing a temporary directory for test files"""
    temp_path = tempfile.mkdtemp(prefix="iskcon_broadcast_test_")
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_camera_config():
    """Fixture providing a standard mock camera configuration"""
    return {
        'id': 0,
        'type': 'mock',
        'source': 'generated',
        'fps': 30,
        'width': 640,
        'height': 480
    }


@pytest.fixture
def ip_camera_config():
    """Fixture providing a standard IP camera configuration"""
    return {
        'id': 0,
        'type': 'ip_camera',
        'rtsp_url': 'rtsp://test:test@192.168.1.100:554/stream',
        'https': {
            'ip': '192.168.1.100',
            'username': 'test',
            'password': 'test'
        }
    }


@pytest.fixture
def multiple_camera_config():
    """Fixture providing configuration for multiple cameras"""
    return [
        {
            'id': 0,
            'type': 'mock',
            'source': 'generated',
            'fps': 30,
            'width': 640,
            'height': 480
        },
        {
            'id': 1,
            'type': 'mock',
            'source': 'generated',
            'fps': 30,
            'width': 640,
            'height': 480
        },
        {
            'id': 2,
            'type': 'mock',
            'source': 'generated',
            'fps': 30,
            'width': 640,
            'height': 480
        }
    ]


@pytest.fixture
def clean_camera_registry():
    """Fixture that ensures a clean camera registry for each test"""
    # Store original registry state
    original_cameras = CameraRegistry._cameras.copy()
    
    # Clear registry before test
    CameraRegistry.clear_registry()
    
    yield CameraRegistry
    
    # Restore original registry state after test
    CameraRegistry.clear_registry()
    CameraRegistry._cameras.update(original_cameras)


@pytest.fixture
def camera_registry_with_mocks():
    """Fixture that provides a registry with mock cameras registered"""
    # Store original registry state
    original_cameras = CameraRegistry._cameras.copy()
    
    # Clear registry and register mock cameras
    CameraRegistry.clear_registry()
    
    # Register the standard camera types
    try:
        from src.cameras.mock_camera import MockCamera
        from src.cameras.ip_camera import IPCamera
        CameraRegistry.register('mock', MockCamera)
        CameraRegistry.register('ip_camera', IPCamera)
    except ImportError:
        # Camera modules may not be available in all test contexts
        pass
    
    yield CameraRegistry
    
    # Restore original registry state after test
    CameraRegistry.clear_registry()
    CameraRegistry._cameras.update(original_cameras)


@pytest.fixture
def mock_camera(mock_camera_config, clean_camera_registry):
    """Fixture providing a mock camera instance"""
    try:
        from src.cameras.mock_camera import MockCamera
        CameraRegistry.register('mock', MockCamera)
        camera = CameraRegistry.create_camera('mock', mock_camera_config['id'], mock_camera_config)
        yield camera
        if hasattr(camera, 'stop'):
            camera.stop()
    except ImportError:
        # Create a minimal mock camera for testing
        class TestMockCamera(CameraInterface):
            def __init__(self, camera_id, config):
                super().__init__(camera_id, config)
                self.running = False
            def capture_frames(self): self.running = True
            def get_frame(self): return None
            def stop(self): self.running = False
            def move_left(self, speed=20, duration=1.0): pass
            def move_right(self, speed=20, duration=1.0): pass
            def move_up(self, speed=20, duration=1.0): pass
            def move_down(self, speed=20, duration=1.0): pass
            def zoom_in(self, speed=20, duration=1.0): pass
            def zoom_out(self, speed=20, duration=1.0): pass
            def move_to_position(self, position, speed=20): pass
        
        CameraRegistry.register('mock', TestMockCamera)
        camera = CameraRegistry.create_camera('mock', mock_camera_config['id'], mock_camera_config)
        yield camera
        camera.stop()


@pytest.fixture
def running_mock_camera(mock_camera):
    """Fixture providing a running mock camera instance"""
    mock_camera.capture_frames()
    time.sleep(0.1)  # Allow camera to start
    yield mock_camera
    mock_camera.stop()


@pytest.fixture
def mock_cv2():
    """Fixture providing a mocked cv2 module"""
    with patch('cv2.VideoCapture') as mock_cap, \
         patch('cv2.imread') as mock_imread, \
         patch('cv2.imshow') as mock_imshow, \
         patch('cv2.waitKey') as mock_waitkey, \
         patch('cv2.destroyAllWindows') as mock_destroy:
        
        # Configure mock VideoCapture
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.read.return_value = (True, Mock())
        mock_cap_instance.get.return_value = 30.0  # FPS
        mock_cap.return_value = mock_cap_instance
        
        # Configure other mocks
        mock_imread.return_value = Mock()
        mock_waitkey.return_value = ord('q')
        
        yield {
            'VideoCapture': mock_cap,
            'imread': mock_imread,
            'imshow': mock_imshow,
            'waitKey': mock_waitkey,
            'destroyAllWindows': mock_destroy,
            'cap_instance': mock_cap_instance
        }


@pytest.fixture
def mock_pygame():
    """Fixture providing a mocked pygame module"""
    with patch('pygame.mixer.init') as mock_init, \
         patch('pygame.mixer.music.load') as mock_load, \
         patch('pygame.mixer.music.play') as mock_play, \
         patch('pygame.mixer.music.stop') as mock_stop:
        
        yield {
            'init': mock_init,
            'load': mock_load,
            'play': mock_play,
            'stop': mock_stop
        }


@pytest.fixture
def mock_yaml_config():
    """Fixture providing mock YAML configuration data"""
    return {
        'background_image': 'test_background.png',
        'cameras': [
            {
                'id': 0,
                'type': 'mock',
                'source': 'generated',
                'fps': 30,
                'width': 640,
                'height': 480
            }
        ],
        'modes': {
            'fullscreen_0': {
                'type': 'full_screen',
                'pos': [0, 0],
                'scale': 100
            },
            'dual_0_1': {
                'type': 'dual_view',
                'cam_top_left': 0,
                'pos_top_left': [0, 0],
                'cam_bottom_right': 1,
                'pos_bottom_right': [640, 360],
                'scale_top_left': 50,
                'scale_bottom_right': 50
            }
        }
    }


@pytest.fixture
def mock_orchestration_config():
    """Fixture providing mock orchestration configuration"""
    return {
        'programmes': [
            {
                'name': 'Test Programme',
                'start_time': '12:00',
                'end_time': '13:00',
                'events': [
                    {
                        'name': 'Test Event',
                        'start_time': '12:00',
                        'end_time': '12:15',
                        'actions': [
                            {
                                'action': 'video_mode',
                                'type': 'full_screen',
                                'mode': 'fullscreen_0',
                                'duration': 10
                            },
                            {
                                'action': 'camera_move',
                                'camera': 0,
                                'type': 'Left',
                                'speed': 20,
                                'duration': 2.0
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def capture_logs():
    """Fixture for capturing log messages during tests"""
    log_capture = []
    
    class TestLogHandler(logging.Handler):
        def emit(self, record):
            log_capture.append(self.format(record))
    
    handler = TestLogHandler()
    handler.setLevel(logging.DEBUG)
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    original_level = root_logger.level
    root_logger.setLevel(logging.DEBUG)
    
    yield log_capture
    
    # Cleanup
    root_logger.removeHandler(handler)
    root_logger.setLevel(original_level)


@pytest.fixture
def mock_threading():
    """Fixture providing controlled threading for tests"""
    threads = []
    
    def mock_thread_start(self):
        threads.append(self)
        # Don't actually start the thread in tests
        self._started = True
    
    with patch.object(threading.Thread, 'start', mock_thread_start):
        yield threads


@pytest.fixture
def performance_timer():
    """Fixture for measuring test performance"""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.name = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        def __call__(self, name):
            """Allow timer to be used as context manager factory"""
            self.name = name
            return self
        
        def __enter__(self):
            self.start()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Test markers for categorizing tests
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "camera: mark test as camera-related"
    )
    config.addinivalue_line(
        "markers", "orchestration: mark test as orchestration-related"
    )
    config.addinivalue_line(
        "markers", "display: mark test as display-related"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location"""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "sys" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "perf" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Add markers based on test name patterns
        if "camera" in item.name.lower():
            item.add_marker(pytest.mark.camera)
        if "orchestration" in item.name.lower():
            item.add_marker(pytest.mark.orchestration)
        if "display" in item.name.lower():
            item.add_marker(pytest.mark.display)


# Session-level setup and teardown
@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Session-level setup for all tests"""
    # Ensure test environment is clean
    os.environ['ISKCON_BROADCAST_TEST_MODE'] = '1'
    
    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    yield
    
    # Session cleanup
    if 'ISKCON_BROADCAST_TEST_MODE' in os.environ:
        del os.environ['ISKCON_BROADCAST_TEST_MODE'] 