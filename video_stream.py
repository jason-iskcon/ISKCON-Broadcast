import cv2
import numpy as np
import time
import yaml
from datetime import datetime
import argparse

def load_config(file_path):
    """Load YAML configuration file."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_current_orchestration(schedule, time_now):
    """Get the appropriate orchestration based on the current or debug time."""
    for item in schedule:
        start_time = datetime.strptime(item['start'], "%H:%M").time()
        end_time = datetime.strptime(item['end'], "%H:%M").time()
        if start_time <= time_now < end_time:
            return item['orchestration_file']
    return None

def resize_frame_to_fit(frame, width, height):
    """Resize frame to fit specified width and height, maintaining aspect ratio."""
    original_height, original_width = frame.shape[:2]
    scaling_factor = min(width / original_width, height / original_height)
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

def dual_capture_display(background, frame0, frame1, pos0, pos1, scale0, scale1):
    """Display both captures in specified positions and scales."""
    # Calculate target dimensions based on background and scale
    h0, w0 = background.shape[:2]
    target_width0 = int(w0 * scale0 / 100)
    target_height0 = int(h0 * scale0 / 100)
    target_width1 = int(w0 * scale1 / 100)
    target_height1 = int(h0 * scale1 / 100)

    # Resize frames to calculated dimensions
    frame0_resized = resize_frame_to_fit(frame0, target_width0, target_height0)
    frame1_resized = resize_frame_to_fit(frame1, target_width1, target_height1)

    # Get resized frame dimensions
    h0_resized, w0_resized = frame0_resized.shape[:2]
    h1_resized, w1_resized = frame1_resized.shape[:2]

    # Ensure frames fit within designated positions on the background
    background[pos0[1]:pos0[1] + h0_resized, pos0[0]:pos0[0] + w0_resized] = frame0_resized
    background[pos1[1]:pos1[1] + h1_resized, pos1[0]:pos1[0] + w1_resized] = frame1_resized
    return background

def fullscreen_display(background, frame, pos, scale):
    """Display a single capture full-screen or in specified position and scale."""
    # Calculate target dimensions based on background and scale
    h, w = background.shape[:2]
    target_width = int(w * scale / 100)
    target_height = int(h * scale / 100)

    # Resize frame to calculated dimensions
    frame_resized = resize_frame_to_fit(frame, target_width, target_height)

    # Place resized frame on background at specified position
    h_resized, w_resized = frame_resized.shape[:2]
    background[pos[1]:pos[1] + h_resized, pos[0]:pos[0] + w_resized] = frame_resized
    return background

def main(mode_config_file='mode_config.yaml', schedule_file='temple_schedule.yaml', debug_time=None):
    # Load configurations
    mode_config = load_config(mode_config_file)
    schedule = load_config(schedule_file)
    
    # Load background image and video captures
    background_image = cv2.imread(mode_config['background_image'], 1)
    cap0 = cv2.VideoCapture(mode_config['sources'][0]['url'])
    cap1 = cv2.VideoCapture(mode_config['sources'][1]['url'])

    current_step = 0
    start_time = time.time()
    orchestration_config = None

    while True:
        # Determine current or debug time for orchestration selection
        time_now = debug_time if debug_time else datetime.now().time()
        
        orchestration_file = get_current_orchestration(schedule, time_now)
        if orchestration_file and (orchestration_config is None or orchestration_file != orchestration_config.get('file')):
            orchestration_config = load_config(orchestration_file)
            orchestration_config['file'] = orchestration_file  # Track the current file

        # Exit if no valid orchestration for current time
        if orchestration_config is None:
            print("No orchestration defined for current time.")
            break
        
        # Get current orchestration step
        step = orchestration_config['steps'][current_step]
        mode_name = step['mode']
        duration = step['duration']
        loop_count = step.get('loops', 1)
        
        # Initialize loop counters
        for loop in range(loop_count):
            ret0, frame0 = cap0.read()
            ret1, frame1 = cap1.read()
            
            if not ret0 or not ret1:
                print("Error: Unable to read from one or more capture sources.")
                break

            elapsed_time = time.time() - start_time

            # Switch to the next mode after the duration
            if elapsed_time > duration:
                start_time = time.time()
                current_step = (current_step + 1) % len(orchestration_config['steps'])

            # Clear the background for each frame
            display_frame = background_image.copy()
            mode_settings = mode_config['modes'][mode_name]

            # Select and display the current mode
            if mode_settings['type'] == 'dual':
                pos0 = tuple(mode_settings['pos0'])
                pos1 = tuple(mode_settings['pos1'])
                scale0 = mode_settings['scale0']  # Percentage
                scale1 = mode_settings['scale1']  # Percentage
                display_frame = dual_capture_display(display_frame, frame0, frame1, pos0, pos1, scale0, scale1)
            
            elif mode_settings['type'] == 'fullscreen_0':
                pos = tuple(mode_settings['pos'])
                scale = mode_settings['scale']  # Percentage
                display_frame = fullscreen_display(display_frame, frame0, pos, scale)
            
            elif mode_settings['type'] == 'fullscreen_1':
                pos = tuple(mode_settings['pos'])
                scale = mode_settings['scale']  # Percentage
                display_frame = fullscreen_display(display_frame, frame1, pos, scale)

            cv2.imshow('Display', display_frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) == ord('q'):
                break

    # Release resources
    cap0.release()
    cap1.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the video orchestration with optional debug time.')
    parser.add_argument('--debug-time', type=str, help="Specify a debug time in HH:MM format to test a specific schedule.")
    args = parser.parse_args()

    debug_time = None
    if args.debug_time:
        try:
            debug_time = datetime.strptime(args.debug_time, "%H:%M").time()
            print(f"Debug mode activated. Testing schedule at {debug_time}.")
        except ValueError:
            print("Invalid time format for --debug-time. Please use HH:MM.")
    
    main(debug_time=debug_time)
