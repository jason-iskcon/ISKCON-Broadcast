import cv2
import logging
import numpy as np
import logging

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
    target_width = int(background.shape[1] * scale / 100)
    target_height = int(background.shape[0] * scale / 100)
    
    # Resize the frame to target width while maintaining the 4:3 aspect ratio
    resized_width = target_width
    resized_height = int(target_width * (3 / 4))

    # Resize the frame to fit the target width with 4:3 ratio
    frame_resized = cv2.resize(frame, (resized_width, resized_height), interpolation=cv2.INTER_AREA)

    # Calculate cropping height to center the frame vertically on the background
    if resized_height > target_height:
        crop_top = (resized_height - target_height) // 2
        crop_bottom = crop_top + target_height
        frame_resized = frame_resized[crop_top:crop_bottom, :]
    
    # Place the resized and cropped frame into the background
    h_resized, w_resized = frame_resized.shape[:2]
    background[pos[1]:pos[1] + h_resized, pos[0]:pos[0] + w_resized] = frame_resized
    return background

def dual_capture_display(background, camera0, camera1, pos0, pos1, scale0, scale1):
    """Displays feeds from two cameras in a dual view mode."""
    frame0 = camera0.get_frame()
    frame1 = camera1.get_frame()
    frame0_resized = resize_frame_to_fit(frame0, int(background.shape[1] * scale0 / 100), int(background.shape[0] * scale0 / 100))
    frame1_resized = resize_frame_to_fit(frame1, int(background.shape[1] * scale1 / 100), int(background.shape[0] * scale1 / 100))
    h0, w0 = frame0_resized.shape[:2]
    h1, w1 = frame1_resized.shape[:2]
    background[pos0[1]:pos0[1] + h0, pos0[0]:pos0[0] + w0] = frame0_resized
    background[pos1[1]:pos1[1] + h1, pos1[0]:pos1[0] + w1] = frame1_resized
    return background

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
    start_x = (new_width - target_width) // 2 if new_width > target_width else 0
    start_y = (new_height - target_height) // 2 if new_height > target_height else 0
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
    left_width = int(background.shape[1] * scale_left / 100)
    left_height = int(background.shape[0] * scale_left / 100)
    right_width = int(background.shape[1] * scale_right / 100)
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