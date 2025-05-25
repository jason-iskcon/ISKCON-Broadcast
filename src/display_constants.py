"""
Display Constants for ISKCON-Broadcast

This module centralizes all magic numbers and constants used in the display system
to improve maintainability and prevent display corruption from hardcoded values.

CRITICAL: Any changes to these constants must be validated against the test suite
in tests/integration/test_critical_positioning.py to ensure no display corruption.
"""

# =============================================================================
# DISPLAY DIMENSIONS
# =============================================================================

# Standard HD display dimensions
DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
DISPLAY_ASPECT_RATIO = DISPLAY_WIDTH / DISPLAY_HEIGHT  # 16:9

# Standard camera frame dimensions  
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_ASPECT_RATIO = CAMERA_WIDTH / CAMERA_HEIGHT  # 4:3

# =============================================================================
# ASPECT RATIOS
# =============================================================================

# Common aspect ratios used in calculations
ASPECT_RATIO_16_9 = 16 / 9
ASPECT_RATIO_4_3 = 4 / 3

# Aspect ratio calculation constants
ASPECT_RATIO_HEIGHT_FACTOR = 3 / 4  # Used in fullscreen_display for 4:3 ratio

# =============================================================================
# SCALE PERCENTAGES
# =============================================================================

# Standard scale values used in configurations
SCALE_FULL = 100
SCALE_LARGE = 80
SCALE_MEDIUM_LARGE = 67
SCALE_MEDIUM = 60
SCALE_HALF = 50
SCALE_MEDIUM_SMALL = 40
SCALE_SMALL = 33

# Special scale values
SCALE_PRODUCTION_RIGHT = 58  # Used in production right column configurations

# =============================================================================
# STANDARD POSITIONS
# =============================================================================

# Origin position
ORIGIN = (0, 0)

# Common positions used in dual view configurations
DUAL_VIEW_POSITIONS = {
    'top_left': (0, 0),
    'mid_screen_1': (768, 432),
    'mid_screen_2': (859, 483), 
    'edge_position': (1286, 724),
}

# Left column configuration positions
LEFT_COLUMN_POSITIONS = {
    'top': (0, 0),
    'bottom': (0, 540),  # Half height offset
}

# Right column configuration positions  
RIGHT_COLUMN_POSITIONS = {
    'start': (807, 0),  # Standard right column start position
}

# =============================================================================
# LAYOUT CALCULATIONS
# =============================================================================

# Left column height calculation
LEFT_COLUMN_HEIGHT_OFFSET = 540  # Half of DISPLAY_HEIGHT

# Right column width calculation base
RIGHT_COLUMN_X_OFFSET = 807  # Standard offset for right column start

# =============================================================================
# PERCENTAGE CONVERSION
# =============================================================================

PERCENTAGE_DIVISOR = 100  # For converting scale percentages to decimals

# =============================================================================
# FRAME PROCESSING CONSTANTS
# =============================================================================

# Cropping and centering calculations
CROP_CENTER_DIVISOR = 2  # For centering calculations (// 2)

# Line spacing for text rendering
TEXT_LINE_SPACING = 5  # Pixels between text lines

# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

# Minimum and maximum scale values
MIN_SCALE_PERCENTAGE = 1
MAX_SCALE_PERCENTAGE = 100

# Display bounds for validation
MAX_DISPLAY_X = DISPLAY_WIDTH - 1
MAX_DISPLAY_Y = DISPLAY_HEIGHT - 1

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_position(x, y):
    """Validate that a position is within display bounds.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        bool: True if position is valid
        
    Raises:
        ValueError: If position is out of bounds
    """
    if not (0 <= x <= MAX_DISPLAY_X):
        raise ValueError(f"X position {x} out of bounds [0, {MAX_DISPLAY_X}]")
    if not (0 <= y <= MAX_DISPLAY_Y):
        raise ValueError(f"Y position {y} out of bounds [0, {MAX_DISPLAY_Y}]")
    return True

def validate_scale(scale):
    """Validate that a scale percentage is within valid range.
    
    Args:
        scale: Scale percentage
        
    Returns:
        bool: True if scale is valid
        
    Raises:
        ValueError: If scale is out of range
    """
    if not (MIN_SCALE_PERCENTAGE <= scale <= MAX_SCALE_PERCENTAGE):
        raise ValueError(f"Scale {scale} out of range [{MIN_SCALE_PERCENTAGE}, {MAX_SCALE_PERCENTAGE}]")
    return True

def calculate_scaled_dimensions(base_width, base_height, scale_percentage):
    """Calculate scaled dimensions from base dimensions and scale percentage.
    
    Args:
        base_width: Base width in pixels
        base_height: Base height in pixels  
        scale_percentage: Scale as percentage (1-100)
        
    Returns:
        tuple: (scaled_width, scaled_height)
    """
    validate_scale(scale_percentage)
    scaled_width = int(base_width * scale_percentage / PERCENTAGE_DIVISOR)
    scaled_height = int(base_height * scale_percentage / PERCENTAGE_DIVISOR)
    return scaled_width, scaled_height

def calculate_4_3_dimensions(target_width):
    """Calculate height for 4:3 aspect ratio given width.
    
    Args:
        target_width: Target width in pixels
        
    Returns:
        int: Height for 4:3 aspect ratio
    """
    return int(target_width * ASPECT_RATIO_HEIGHT_FACTOR)

# =============================================================================
# COMMON CALCULATIONS
# =============================================================================

def get_center_crop_offset(source_size, target_size):
    """Calculate offset for center cropping.
    
    Args:
        source_size: Source dimension
        target_size: Target dimension
        
    Returns:
        int: Offset for centering
    """
    return (source_size - target_size) // CROP_CENTER_DIVISOR if source_size > target_size else 0 