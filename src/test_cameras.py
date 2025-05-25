#!/usr/bin/env python3
"""
Test script for camera plugin system

This script tests the camera plugin architecture by creating
different types of cameras and verifying they work correctly.
"""

import time
import logging
import cv2
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from camera_registry import CameraRegistry, create_cameras_from_config
import cameras  # Import all camera plugins

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_camera_registry():
    """Test the camera registry functionality"""
    logger.info("Testing camera registry...")
    
    # List available camera types
    available_types = CameraRegistry.list_available_cameras()
    logger.info(f"Available camera types: {available_types}")
    
    # Verify expected types are registered
    expected_types = ['ip_camera', 'mock']
    for camera_type in expected_types:
        if camera_type in available_types:
            logger.info(f"✓ {camera_type} is registered")
        else:
            logger.error(f"✗ {camera_type} is NOT registered")
            return False
    
    return True


def test_mock_cameras():
    """Test mock camera functionality"""
    logger.info("Testing mock cameras...")
    
    # Test configuration for mock cameras
    mock_configs = [
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
            'source': 'webcam',
            'webcam_index': 0,
            'fps': 30,
            'width': 640,
            'height': 480
        }
    ]
    
    cameras = []
    
    try:
        # Create mock cameras
        for config in mock_configs:
            try:
                camera = CameraRegistry.create_camera(
                    config['type'], 
                    config['id'], 
                    config
                )
                cameras.append(camera)
                logger.info(f"✓ Created {camera}")
            except Exception as e:
                logger.warning(f"Could not create camera {config['id']}: {e}")
        
        if not cameras:
            logger.error("No cameras could be created")
            return False
        
        # Start capture for available cameras
        for camera in cameras:
            try:
                camera.capture_frames()
                logger.info(f"✓ Started capture for {camera}")
            except Exception as e:
                logger.error(f"Failed to start capture for {camera}: {e}")
        
        # Test frame capture for a few seconds
        logger.info("Testing frame capture for 5 seconds...")
        start_time = time.time()
        frame_counts = {cam.camera_id: 0 for cam in cameras}
        
        while time.time() - start_time < 5:
            for camera in cameras:
                frame = camera.get_frame()
                if frame is not None:
                    frame_counts[camera.camera_id] += 1
                    
                    # Show first camera's frame
                    if camera.camera_id == 0:
                        cv2.imshow(f'Camera {camera.camera_id}', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
            
            time.sleep(0.1)
        
        cv2.destroyAllWindows()
        
        # Report results
        for camera in cameras:
            count = frame_counts[camera.camera_id]
            logger.info(f"Camera {camera.camera_id}: {count} frames captured")
            if count > 0:
                logger.info(f"✓ Camera {camera.camera_id} is working")
            else:
                logger.warning(f"⚠ Camera {camera.camera_id} produced no frames")
        
        # Test PTZ commands
        logger.info("Testing PTZ commands...")
        for camera in cameras:
            success = camera.send_ptz_command("PtzCtrl", "Left", 1)
            if success:
                logger.info(f"✓ PTZ command successful for camera {camera.camera_id}")
            else:
                logger.warning(f"⚠ PTZ command failed for camera {camera.camera_id}")
        
        # Test camera info
        logger.info("Testing camera info...")
        for camera in cameras:
            info = camera.get_camera_info()
            logger.info(f"Camera {camera.camera_id} info: {info}")
        
        return True
        
    finally:
        # Cleanup
        for camera in cameras:
            try:
                camera.stop()
                logger.info(f"Stopped camera {camera.camera_id}")
            except Exception as e:
                logger.error(f"Error stopping camera {camera.camera_id}: {e}")


def test_config_loading():
    """Test loading cameras from configuration file"""
    logger.info("Testing configuration loading...")
    
    # Test with development config
    try:
        import yaml
        
        # Load development config
        with open('mode_config_dev.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        cameras_config = config['cameras']
        logger.info(f"Loaded {len(cameras_config)} camera configurations")
        
        # Create cameras from config
        cameras = create_cameras_from_config(cameras_config)
        logger.info(f"Created {len(cameras)} cameras from configuration")
        
        if cameras:
            logger.info("✓ Configuration loading successful")
            
            # Quick test of first camera
            if cameras:
                camera = cameras[0]
                camera.capture_frames()
                time.sleep(2)
                frame = camera.get_frame()
                if frame is not None:
                    logger.info("✓ First camera producing frames")
                else:
                    logger.warning("⚠ First camera not producing frames")
                camera.stop()
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration loading failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("Starting camera plugin system tests...")
    
    tests = [
        ("Camera Registry", test_camera_registry),
        ("Mock Cameras", test_mock_cameras),
        ("Configuration Loading", test_config_loading)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results[test_name] = result
            if result:
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Camera plugin system is working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the logs above.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 