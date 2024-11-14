import cv2
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
    """Resize the frame to fit the target dimensions and crop it if necessary."""
    # Resize the frame to fit within the target dimensions
    frame_resized = resize_frame_to_fit(frame, target_width, target_height)
    
    # Get the resized frame's height and width
    resized_height, resized_width = frame_resized.shape[:2]
    
    # Log the size of the resized frame for debugging
    # logging.info(f"Resized frame to: {resized_width}x{resized_height}")
    
    # Crop the frame to ensure it fits within the target size if it exceeds the target height or width
    if resized_height > target_height:
        frame_resized = frame_resized[:target_height, :]
        logging.info(f"Cropping height to: {target_height}")
    if resized_width > target_width:
        frame_resized = frame_resized[:, :target_width]
        logging.info(f"Cropping width to: {target_width}")
    
    return frame_resized

def left_column_right_main(background, camera_left_top, camera_left_bottom, camera_right, pos_left_top, pos_left_bottom, pos_right, scale_left, scale_right):
    """Displays two smaller images on the left and a larger image on the right."""
    
    # Capture frames from the specified cameras
    frame_left_top = camera_left_top.get_frame()
    frame_left_bottom = camera_left_bottom.get_frame()
    frame_right = camera_right.get_frame()

    # Calculate target dimensions for the left frames (34% of width and 50% of height for both)
    left_width = int(background.shape[1] * scale_left / 100)
    left_height = int(background.shape[0] * scale_left / 100)

    # Calculate target dimensions for the right frame (66% of width and 100% of height)
    right_width = int(background.shape[1] * scale_right / 100)
    right_height = background.shape[0]  # Full height for the right camera

    # Resize and crop frames to fit the layout exactly
    frame_left_top_resized = resize_and_crop(frame_left_top, left_width, left_height)
    frame_left_bottom_resized = resize_and_crop(frame_left_bottom, left_width, left_height)
    frame_right_resized = resize_and_crop(frame_right, right_width, right_height)

    # Ensure no overlap and each frame is positioned correctly

    # Position the resized frames on the background
    background[pos_left_top[1]:pos_left_top[1] + left_height, pos_left_top[0]:pos_left_top[0] + left_width] = frame_left_top_resized
    background[pos_left_bottom[1]:pos_left_bottom[1] + left_height, pos_left_bottom[0]:pos_left_bottom[0] + left_width] = frame_left_bottom_resized
    background[pos_right[1]:pos_right[1] + right_height, pos_right[0]:pos_right[0] + right_width] = frame_right_resized

    return background
