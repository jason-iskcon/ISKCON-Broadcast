#!/usr/bin/env python3
"""
Demo script to show mock cameras working with video display

This script demonstrates the camera plugin system working with
the display helpers to show multiple mock cameras in different layouts.
"""

import cv2
import time
import logging
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from camera_registry import CameraRegistry, create_cameras_from_config
import cameras  # Import all camera plugins
from display_helpers import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_mock_cameras():
    """Demo the mock camera system with video display"""
    
    logger.info("🎬 Starting Mock Camera Demo...")
    
    # Create mock cameras configuration
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
    
    # Create cameras
    cameras = create_cameras_from_config(mock_configs)
    logger.info(f"Created {len(cameras)} mock cameras")
    
    if not cameras:
        logger.error("No cameras created!")
        return
    
    # Start camera capture
    for cam in cameras:
        cam.capture_frames()
        logger.info(f"Started capture for {cam}")
    
    # Load background image
    try:
        display_frame = cv2.imread('../assets/default_background.png')
        if display_frame is None:
            # Create a simple background if file not found
            display_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
            display_frame[:] = (50, 50, 50)  # Dark gray background
            logger.info("Using generated background")
        else:
            logger.info("Loaded background image")
    except Exception as e:
        logger.warning(f"Could not load background: {e}")
        display_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        display_frame[:] = (50, 50, 50)
    
    logger.info("🎥 Starting video display demo...")
    logger.info("Press 'q' to quit, '1' for fullscreen, '2' for dual view, '3' for triple view")
    
    display_mode = 'fullscreen'
    start_time = time.time()
    
    try:
        while True:
            # Reset display frame
            if display_frame is not None:
                current_frame = display_frame.copy()
            else:
                current_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
                current_frame[:] = (50, 50, 50)
            
            # Apply different display modes
            if display_mode == 'fullscreen' and len(cameras) > 0:
                # Show first camera fullscreen
                current_frame = fullscreen_display(current_frame, cameras[0], (0, 0), 100)
                
            elif display_mode == 'dual' and len(cameras) >= 2:
                # Show dual view
                current_frame = dual_capture_display(
                    current_frame, 
                    cameras, 
                    0,  # cam_top_left
                    (0, 0),  # pos_top_left
                    1,  # cam_bottom_right
                    (960, 540),  # pos_bottom_right
                    50,  # scale_top_left
                    50   # scale_bottom_right
                )
                
            elif display_mode == 'triple' and len(cameras) >= 3:
                # Show triple view (left column + right main)
                current_frame = left_column_right_main(
                    current_frame,
                    cameras,
                    1,  # cam_left_top
                    (0, 0),  # pos_left_top
                    2,  # cam_left_bottom
                    (0, 540),  # pos_left_bottom
                    0,  # cam_right
                    (480, 0),  # pos_right
                    40,  # scale_left
                    60   # scale_right
                )
            
            # Add demo info overlay
            elapsed = time.time() - start_time
            info_text = [
                f"Mock Camera Demo - {display_mode.upper()} mode",
                f"Running time: {elapsed:.1f}s",
                f"Active cameras: {len([c for c in cameras if c.running])}",
                "Controls: 1=Fullscreen, 2=Dual, 3=Triple, Q=Quit"
            ]
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            for i, text in enumerate(info_text):
                y = 30 + i * 25
                cv2.putText(current_frame, text, (10, y), font, 0.6, (255, 255, 255), 1)
            
            # Display the frame
            cv2.imshow('ISKCON-Broadcast Mock Camera Demo', current_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Demo stopped by user")
                break
            elif key == ord('1'):
                display_mode = 'fullscreen'
                logger.info("Switched to fullscreen mode")
            elif key == ord('2'):
                display_mode = 'dual'
                logger.info("Switched to dual view mode")
            elif key == ord('3'):
                display_mode = 'triple'
                logger.info("Switched to triple view mode")
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.033)  # ~30 FPS
    
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    
    finally:
        # Cleanup
        cv2.destroyAllWindows()
        for cam in cameras:
            cam.stop()
            logger.info(f"Stopped {cam}")
        
        logger.info("🎬 Mock Camera Demo completed!")


def main():
    """Main function"""
    logger.info("🚀 ISKCON-Broadcast Mock Camera Demo")
    logger.info("=" * 50)
    
    try:
        demo_mock_cameras()
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 