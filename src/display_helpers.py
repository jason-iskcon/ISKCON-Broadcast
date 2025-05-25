import cv2
import logging
import numpy as np
from display_constants import (
    PERCENTAGE_DIVISOR,
    ASPECT_RATIO_HEIGHT_FACTOR,
    CROP_CENTER_DIVISOR,
    calculate_scaled_dimensions,
    get_center_crop_offset
)

def resize_frame_to_fit(frame, target_width, target_height):
    """Resize frame to fit the exact target dimensions."""
    # Resize frame to the exact target size
    resized_frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)
    
    # If the resized frame is larger than target size in any dimension, crop it
    return resized_frame

def fullscreen_display(background, camera, pos, scale):
    """Displays the camera feed in fullscreen mode with 4:3 aspect ratio adjustment."""
    frame = camera.get_frame()
    
    # Target dimensions to fit the background scale
    target_width, target_height = calculate_scaled_dimensions(
        background.shape[1], background.shape[0], scale
    )
    
    # Resize the frame to target width while maintaining the 4:3 aspect ratio
    resized_width = target_width
    resized_height = int(target_width * ASPECT_RATIO_HEIGHT_FACTOR)

    # Resize the frame to fit the target width with 4:3 ratio
    frame_resized = cv2.resize(frame, (resized_width, resized_height), interpolation=cv2.INTER_AREA)

    # Calculate cropping height to center the frame vertically on the background
    if resized_height > target_height:
        crop_top = get_center_crop_offset(resized_height, target_height)
        crop_bottom = crop_top + target_height
        frame_resized = frame_resized[crop_top:crop_bottom, :]
    
    # Place the resized and cropped frame into the background
    h_resized, w_resized = frame_resized.shape[:2]
    background[pos[1]:pos[1] + h_resized, pos[0]:pos[0] + w_resized] = frame_resized
    return background

def dual_capture_display(
    background, 
    cameras, 
    cam_top_left, 
    pos_top_left, 
    cam_bottom_right, 
    pos_bottom_right, 
    scale_top_left, 
    scale_bottom_right
):
    """
    Displays two camera views: one at the top-left and another at the bottom-right.

    Parameters:
    - background: Base image on which to overlay camera frames.
    - cameras: Dictionary of camera objects.
    - cam_top_left: Camera ID for the top-left view.
    - pos_top_left: [x, y] position of the top-left view on the background.
    - cam_bottom_right: Camera ID for the bottom-right view.
    - pos_bottom_right: [x, y] position of the bottom-right view on the background.
    - scale_top_left: Scale percentage for the top-left view.
    - scale_bottom_right: Scale percentage for the bottom-right view.

    Returns:
    - Updated background with the camera views.
    """
    try:
        # Capture frames from the specified cameras
        frame_top_left = cameras[cam_top_left].get_frame()
        frame_bottom_right = cameras[cam_bottom_right].get_frame()

        # Calculate target dimensions for each frame
        top_left_width, top_left_height = calculate_scaled_dimensions(
            background.shape[1], background.shape[0], scale_top_left
        )
        bottom_right_width, bottom_right_height = calculate_scaled_dimensions(
            background.shape[1], background.shape[0], scale_bottom_right
        )

        # Resize and crop frames while maintaining their aspect ratios
        frame_top_left_resized = crop_and_resize(frame_top_left, top_left_width, top_left_height)
        frame_bottom_right_resized = crop_and_resize(frame_bottom_right, bottom_right_width, bottom_right_height)

        # Position the resized frames on the background
        background[
            pos_top_left[1]:pos_top_left[1] + top_left_height,
            pos_top_left[0]:pos_top_left[0] + top_left_width
        ] = frame_top_left_resized

        background[
            pos_bottom_right[1]:pos_bottom_right[1] + bottom_right_height,
            pos_bottom_right[0]:pos_bottom_right[0] + bottom_right_width
        ] = frame_bottom_right_resized

        return background

    except Exception as e:
        logging.error(f"An error occurred in dual_view: {e}")
        raise

def crop_and_resize(frame, target_width, target_height):
    """
    Resize the frame to the target dimensions while maintaining aspect ratio.
    Crop any excess parts to fit the target size.

    Parameters:
    - frame: Input frame to be resized and cropped.
    - target_width: Desired width after resizing.
    - target_height: Desired height after resizing.

    Returns:
    - The resized and cropped frame.
    """
    try:
        # Get original dimensions
        original_height, original_width = frame.shape[:2]

        # Compute aspect ratios
        aspect_ratio_original = original_width / original_height
        aspect_ratio_target = target_width / target_height

        # Resize while preserving aspect ratio
        if aspect_ratio_original > aspect_ratio_target:
            # Wider than target: match height and crop width
            new_height = target_height
            new_width = int(target_height * aspect_ratio_original)
        else:
            # Taller than target: match width and crop height
            new_width = target_width
            new_height = int(target_width / aspect_ratio_original)

        frame_resized = cv2.resize(frame, (new_width, new_height))

        # Crop to target dimensions
        x_crop = get_center_crop_offset(new_width, target_width)
        y_crop = get_center_crop_offset(new_height, target_height)

        frame_cropped = frame_resized[y_crop:y_crop + target_height, x_crop:x_crop + target_width]

        return frame_cropped

    except Exception as e:
        logging.error(f"Error in crop_and_resize: {e}")
        raise

def resize_and_crop(frame, target_width, target_height):
    """Resize the frame to fit the target dimensions while preserving the aspect ratio, and crop any excess."""
    # Get original dimensions
    original_height, original_width = frame.shape[:2]
    
    # Calculate aspect ratios
    target_aspect_ratio = target_width / target_height
    frame_aspect_ratio = original_width / original_height

    # Resize the frame while preserving aspect ratio
    if frame_aspect_ratio > target_aspect_ratio:
        # Wider than target, fit height and crop width
        scale = target_height / original_height
        new_width = int(original_width * scale)
        new_height = target_height
    else:
        # Taller than target, fit width and crop height
        scale = target_width / original_width
        new_width = target_width
        new_height = int(original_height * scale)
    
    resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Crop the resized frame to the target dimensions
    start_x = get_center_crop_offset(new_width, target_width)
    start_y = get_center_crop_offset(new_height, target_height)
    cropped_frame = resized_frame[start_y:start_y + target_height, start_x:start_x + target_width]

    return cropped_frame

def left_column_right_main(
    background, 
    cameras,  # Dictionary of camera objects
    cam_left_top, 
    pos_left_top, 
    cam_left_bottom, 
    pos_left_bottom, 
    cam_right, 
    pos_right, 
    scale_left, 
    scale_right
):
    """
    Displays two smaller images on the left and a larger image on the right.

    Parameters:
        background: The canvas to overlay the frames.
        cameras: A dictionary where keys are camera indices and values are camera objects.
        cam_left_top: Index of the top-left camera.
        pos_left_top: Position [x, y] for the top-left camera.
        cam_left_bottom: Index of the bottom-left camera.
        pos_left_bottom: Position [x, y] for the bottom-left camera.
        cam_right: Index of the right camera.
        pos_right: Position [x, y] for the right camera.
        scale_left: Scaling percentage for the left column.
        scale_right: Scaling percentage for the right column.
    """
    # Capture frames from the specified cameras
    frame_left_top = cameras[cam_left_top].get_frame()
    frame_left_bottom = cameras[cam_left_bottom].get_frame()
    frame_right = cameras[cam_right].get_frame()

    # Calculate target dimensions based on scaling percentages
    left_width, left_height = calculate_scaled_dimensions(
        background.shape[1], background.shape[0], scale_left
    )
    right_width, _ = calculate_scaled_dimensions(
        background.shape[1], background.shape[0], scale_right
    )
    right_height = background.shape[0]  # Full height for the right camera

    # Resize and crop frames to fit exactly within their designated areas
    frame_left_top_resized = resize_and_crop(frame_left_top, left_width, left_height)
    frame_left_bottom_resized = resize_and_crop(frame_left_bottom, left_width, left_height)
    frame_right_resized = resize_and_crop(frame_right, right_width, right_height)

    # Overlay resized frames on the background
    background[
        pos_left_top[1]:pos_left_top[1] + left_height,
        pos_left_top[0]:pos_left_top[0] + left_width
    ] = frame_left_top_resized
    background[
        pos_left_bottom[1]:pos_left_bottom[1] + left_height,
        pos_left_bottom[0]:pos_left_bottom[0] + left_width
    ] = frame_left_bottom_resized
    background[
        pos_right[1]:pos_right[1] + right_height,
        pos_right[0]:pos_right[0] + right_width
    ] = frame_right_resized

    return background