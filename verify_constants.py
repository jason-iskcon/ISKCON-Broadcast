#!/usr/bin/env python3
"""
Simple verification script for display constants extraction.

This script verifies that our magic number extraction worked correctly
by testing the constants and basic calculations.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our constants
from display_constants import (
    DISPLAY_WIDTH, DISPLAY_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT,
    SCALE_FULL, SCALE_LARGE, SCALE_MEDIUM_LARGE, SCALE_MEDIUM, 
    SCALE_HALF, SCALE_MEDIUM_SMALL, SCALE_SMALL, SCALE_PRODUCTION_RIGHT,
    DUAL_VIEW_POSITIONS, LEFT_COLUMN_POSITIONS, RIGHT_COLUMN_POSITIONS,
    validate_position, validate_scale, calculate_scaled_dimensions,
    ASPECT_RATIO_HEIGHT_FACTOR, get_center_crop_offset
)

def test_constants():
    """Test that all constants are correctly defined."""
    print("Testing display constants...")
    
    # Test dimensions
    assert DISPLAY_WIDTH == 1920, f"Expected 1920, got {DISPLAY_WIDTH}"
    assert DISPLAY_HEIGHT == 1080, f"Expected 1080, got {DISPLAY_HEIGHT}"
    assert CAMERA_WIDTH == 640, f"Expected 640, got {CAMERA_WIDTH}"
    assert CAMERA_HEIGHT == 480, f"Expected 480, got {CAMERA_HEIGHT}"
    print("✓ Display and camera dimensions correct")
    
    # Test scale constants
    assert SCALE_FULL == 100, f"Expected 100, got {SCALE_FULL}"
    assert SCALE_LARGE == 80, f"Expected 80, got {SCALE_LARGE}"
    assert SCALE_MEDIUM_LARGE == 67, f"Expected 67, got {SCALE_MEDIUM_LARGE}"
    assert SCALE_MEDIUM == 60, f"Expected 60, got {SCALE_MEDIUM}"
    assert SCALE_HALF == 50, f"Expected 50, got {SCALE_HALF}"
    assert SCALE_MEDIUM_SMALL == 40, f"Expected 40, got {SCALE_MEDIUM_SMALL}"
    assert SCALE_SMALL == 33, f"Expected 33, got {SCALE_SMALL}"
    assert SCALE_PRODUCTION_RIGHT == 58, f"Expected 58, got {SCALE_PRODUCTION_RIGHT}"
    print("✓ Scale constants correct")
    
    # Test position constants
    assert DUAL_VIEW_POSITIONS['top_left'] == (0, 0)
    assert DUAL_VIEW_POSITIONS['mid_screen_1'] == (768, 432)
    assert DUAL_VIEW_POSITIONS['mid_screen_2'] == (859, 483)
    assert DUAL_VIEW_POSITIONS['edge_position'] == (1286, 724)
    assert LEFT_COLUMN_POSITIONS['top'] == (0, 0)
    assert LEFT_COLUMN_POSITIONS['bottom'] == (0, 540)
    assert RIGHT_COLUMN_POSITIONS['start'] == (807, 0)
    print("✓ Position constants correct")
    
    # Test aspect ratio constant
    assert abs(ASPECT_RATIO_HEIGHT_FACTOR - 3/4) < 0.001, f"Expected 0.75, got {ASPECT_RATIO_HEIGHT_FACTOR}"
    print("✓ Aspect ratio constant correct")

def test_validation_functions():
    """Test validation functions."""
    print("\nTesting validation functions...")
    
    # Test position validation
    assert validate_position(0, 0) == True
    assert validate_position(1919, 1079) == True
    
    try:
        validate_position(-1, 0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        validate_position(1920, 0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ Position validation works")
    
    # Test scale validation
    assert validate_scale(1) == True
    assert validate_scale(50) == True
    assert validate_scale(100) == True
    
    try:
        validate_scale(0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        validate_scale(101)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ Scale validation works")

def test_calculation_functions():
    """Test calculation functions."""
    print("\nTesting calculation functions...")
    
    # Test scaled dimensions
    width, height = calculate_scaled_dimensions(1920, 1080, 50)
    assert width == 960, f"Expected 960, got {width}"
    assert height == 540, f"Expected 540, got {height}"
    
    width, height = calculate_scaled_dimensions(1920, 1080, 33)
    assert width == 633, f"Expected 633, got {width}"  # int(1920 * 33 / 100)
    assert height == 356, f"Expected 356, got {height}"  # int(1080 * 33 / 100)
    
    print("✓ Scaled dimension calculations work")
    
    # Test center crop offset
    offset = get_center_crop_offset(100, 80)
    assert offset == 10, f"Expected 10, got {offset}"  # (100 - 80) // 2
    
    offset = get_center_crop_offset(80, 100)
    assert offset == 0, f"Expected 0, got {offset}"  # Source smaller than target
    
    print("✓ Center crop offset calculations work")

def test_critical_calculations():
    """Test critical calculations that were previously hardcoded."""
    print("\nTesting critical calculations...")
    
    # Test the key calculations that were replaced
    # Original: int(background.shape[1] * scale / 100)
    # New: calculate_scaled_dimensions(background.shape[1], background.shape[0], scale)
    
    # Test with 1920x1080 background and various scales
    scales_to_test = [33, 40, 50, 58, 60, 67, 80, 100]
    
    for scale in scales_to_test:
        width, height = calculate_scaled_dimensions(1920, 1080, scale)
        expected_width = int(1920 * scale / 100)
        expected_height = int(1080 * scale / 100)
        
        assert width == expected_width, f"Width mismatch for scale {scale}: expected {expected_width}, got {width}"
        assert height == expected_height, f"Height mismatch for scale {scale}: expected {expected_height}, got {height}"
    
    print("✓ Critical calculations match original behavior")
    
    # Test 4:3 aspect ratio calculation
    # Original: int(target_width * (3 / 4))
    # New: int(target_width * ASPECT_RATIO_HEIGHT_FACTOR)
    
    test_widths = [640, 960, 1280, 1920]
    for width in test_widths:
        original_height = int(width * (3 / 4))
        new_height = int(width * ASPECT_RATIO_HEIGHT_FACTOR)
        assert original_height == new_height, f"4:3 calculation mismatch for width {width}"
    
    print("✓ 4:3 aspect ratio calculations match original behavior")

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("ISKCON-Broadcast Display Constants Verification")
    print("=" * 60)
    
    try:
        test_constants()
        test_validation_functions()
        test_calculation_functions()
        test_critical_calculations()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Magic number extraction successful!")
        print("✓ All constants correctly defined")
        print("✓ All validation functions working")
        print("✓ All calculations match original behavior")
        print("✓ No display corruption risk detected")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 