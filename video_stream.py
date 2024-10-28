import cv2
import numpy as np
import time
import yaml

def load_config(file_path):
    """Load YAML configuration file."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def resize_frame(frame, target_width, target_height):
    """Resize the frame to a target width and height."""
    return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)

def dual_capture_display(background, frame0, frame1, pos0, pos1, size0, size1):
    """Display both captures in specified positions and sizes."""
    frame0_resized = resize_frame(frame0, *size0)
    frame1_resized = resize_frame(frame1, *size1)
    background[pos0[1]:pos0[1]+size0[1], pos0[0]:pos0[0]+size0[0]] = frame0_resized
    background[pos1[1]:pos1[1]+size1[1], pos1[0]:pos1[0]+size1[0]] = frame1_resized
    return background

def fullscreen_display(background, frame, pos, size):
    """Display a single capture full-screen or in specified position and size."""
    frame_resized = resize_frame(frame, *size)
    background[pos[1]:pos[1]+size[1], pos[0]:pos[0]+size[0]] = frame_resized
    return background

def main(mode_config_file='mode_config.yaml', orchestration_file='orchestration.yaml'):
    # Load configurations
    mode_config = load_config(mode_config_file)
    orchestration = load_config(orchestration_file)
    
    # Load background image and video captures
    background_image = cv2.imread(mode_config['background_image'], 1)
    cap0 = cv2.VideoCapture(mode_config['sources'][0]['url'])
    cap1 = cv2.VideoCapture(mode_config['sources'][1]['url'])
    
    current_step = 0
    start_time = time.time()

    while True:
        # Get current orchestration step
        step = orchestration['steps'][current_step]
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
                current_step = (current_step + 1) % len(orchestration['steps'])

            # Clear the background for each frame
            display_frame = background_image.copy()
            mode_settings = mode_config['modes'][mode_name]

            # Select and display the current mode
            if mode_settings['type'] == 'dual':
                pos0 = tuple(mode_settings['pos0'])
                pos1 = tuple(mode_settings['pos1'])
                size0 = tuple(mode_settings['size0'])
                size1 = tuple(mode_settings['size1'])
                display_frame = dual_capture_display(display_frame, frame0, frame1, pos0, pos1, size0, size1)
            
            elif mode_settings['type'] == 'fullscreen_0':
                pos = tuple(mode_settings['pos'])
                size = tuple(mode_settings['size'])
                display_frame = fullscreen_display(display_frame, frame0, pos, size)
            
            elif mode_settings['type'] == 'fullscreen_1':
                pos = tuple(mode_settings['pos'])
                size = tuple(mode_settings['size'])
                display_frame = fullscreen_display(display_frame, frame1, pos, size)

            cv2.imshow('Display', display_frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) == ord('q'):
                break

    # Release resources
    cap0.release()
    cap1.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
