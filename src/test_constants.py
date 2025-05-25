#!/usr/bin/env python3
"""
Simple test for display constants.
"""

from display_constants import (
    DISPLAY_WIDTH, DISPLAY_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT,
    SCALE_FULL, SCALE_LARGE, SCALE_MEDIUM_LARGE, SCALE_MEDIUM, 
    SCALE_HALF, SCALE_MEDIUM_SMALL, SCALE_SMALL, SCALE_PRODUCTION_RIGHT,
    DUAL_VIEW_POSITIONS, LEFT_COLUMN_POSITIONS, RIGHT_COLUMN_POSITIONS,
    validate_position, validate_scale, calculate_scaled_dimensions,
    ASPECT_RATIO_HEIGHT_FACTOR, get_center_crop_offset
)

def main():
    print("Testing display constants...")
    
    # Test basic constants
    print(f"Display: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    print(f"Camera: {CAMERA_WIDTH}x{CAMERA_HEIGHT}")
    print(f"Scales: {SCALE_SMALL}, {SCALE_MEDIUM_SMALL}, {SCALE_HALF}, {SCALE_PRODUCTION_RIGHT}, {SCALE_MEDIUM}, {SCALE_MEDIUM_LARGE}, {SCALE_LARGE}, {SCALE_FULL}")
    
    # Test calculations
    width, height = calculate_scaled_dimensions(1920, 1080, 50)
    print(f"50% scale: {width}x{height}")
    
    width, height = calculate_scaled_dimensions(1920, 1080, 33)
    print(f"33% scale: {width}x{height}")
    
    # Test 4:3 aspect ratio
    test_width = 960
    original_calc = int(test_width * (3 / 4))
    new_calc = int(test_width * ASPECT_RATIO_HEIGHT_FACTOR)
    print(f"4:3 aspect ratio for {test_width}: original={original_calc}, new={new_calc}, match={original_calc == new_calc}")
    
    # Test center crop
    offset = get_center_crop_offset(100, 80)
    print(f"Center crop offset (100->80): {offset}")
    
    # Test positions
    print(f"Dual view positions: {DUAL_VIEW_POSITIONS}")
    print(f"Left column positions: {LEFT_COLUMN_POSITIONS}")
    print(f"Right column positions: {RIGHT_COLUMN_POSITIONS}")
    
    print("✓ All constants loaded and working!")

if __name__ == "__main__":
    main() 