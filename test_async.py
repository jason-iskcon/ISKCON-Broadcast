import cv2
import time
import asyncio
import logging
import yaml
import numpy as np
import pygame
import threading
from collections import deque
from camera import Camera
from display_helpers import *
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

mode_config_file = 'mode_config.yaml'
schedule_file = 'orchestration.yaml'
mode_config = load_config(mode_config_file)
schedule = load_config(schedule_file)

# Initialize cameras
cameras = [Camera(i, cam['rtsp_url'], cam['https']['ip'], cam['https']['username'], cam['https']['password'])
           for i, cam in enumerate(mode_config['cameras'])]

for cam in cameras:
    threading.Thread(target=cam.capture_frames).start()

# Load background image
display_frame = cv2.imread(mode_config['background_image'])

# Initialize pygame for audio playback
pygame.mixer.init()

# Queue for storing camera move tasks
camera_move_queue = deque()

async def process_camera_move(task):
    """Processes a single camera move."""
    logging.info(f"Processing camera move: {task}")
    cameras[0].send_ptz_command(command="PtzCtrl", parameter=task['type'], id=task.get('marker', 0))
    await asyncio.sleep(task['duration'])  # Simulate camera movement duration
    cameras[0].send_ptz_command(command="PtzCtrl", parameter="Stop", id=0)

async def process_camera_move_queue():
    """Processes each camera move in the queue sequentially."""
    while camera_move_queue:
        task = camera_move_queue.popleft()  # Get the next task in the queue
        await process_camera_move(task)  # Process the camera move

async def play_audio(task):
    """Plays audio for a specified duration."""
    logging.info(f"Playing audio: {task['file']} for {task['duration']} seconds")
    pygame.mixer.music.load(task['file'])
    pygame.mixer.music.play()
    await asyncio.sleep(task['duration'])
    pygame.mixer.music.stop()
    logging.info("Audio playback ended.")

async def play_video(task, display_frame):
    """Plays video for a specified duration and updates the display frame."""
    video_file = task['file']
    duration = task['duration']
    logging.info(f"Starting video playback: {video_file} for {duration} seconds")

    cap = cv2.VideoCapture(video_file)
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        elapsed_time = time.time() - start_time

        # Stop playback if specified duration is reached
        if elapsed_time >= duration:
            logging.info("Specified duration reached, stopping video playback.")
            break

        if not ret:
            logging.warning("End of video file or error.")
            break

        # Resize the video frame to fit the display frame
        resized_frame = resize_frame_to_fit(frame, display_frame.shape[1], display_frame.shape[0])

        # Copy resized video frame onto display_frame
        np.copyto(display_frame, resized_frame)

        cv2.imshow("Display", display_frame)

        # Allow OpenCV to process frames smoothly
        if cv2.waitKey(1) & 0xFF == ord('q'):
            logging.info("Video playback interrupted by user.")
            break
        
        await asyncio.sleep(0)  # Yield to other tasks

    cap.release()
    logging.info("Video playback ended.")


async def display_video_mode(task, camera_tasks):
    logging.info(f"Displaying video mode: {task['mode']} for {task['duration']} seconds")
    mode_settings = mode_config['modes'].get(task['mode'])
    duration = task['duration']
    end_time = time.time() + duration
    global display_frame
    display_frame = cv2.imread(mode_config['background_image'])

    while time.time() < end_time:
        # Apply display mode configurations
        if mode_settings['type'] == 'dual_view':
            display_frame = dual_capture_display(
                display_frame, 
                cameras, 
                mode_settings['cam_top_left'],
                tuple(mode_settings['pos_top_left']), 
                mode_settings['cam_bottom_right'],
                tuple(mode_settings['pos_bottom_right']),
                mode_settings['scale_top_left'], 
                mode_settings['scale_bottom_right']
            )
        elif mode_settings['type'] == 'full_screen':
            display_frame = fullscreen_display(display_frame, cameras[0], tuple(mode_settings['pos']), mode_settings['scale'])
        elif mode_settings['type'] == 'left_column_right_main':
            display_frame = left_column_right_main(
                display_frame,
                cameras,
                mode_settings['cam_left_top'],
                tuple(mode_settings['pos_left_top']),
                mode_settings['cam_left_bottom'],
                tuple(mode_settings['pos_left_bottom']),
                mode_settings['cam_right'],
                tuple(mode_settings['pos_right']),
                mode_settings['scale_left'],
                mode_settings['scale_right']
            )

        cv2.imshow('Display', display_frame)
        if cv2.waitKey(1) == ord('q'):
            break
        await asyncio.sleep(0.1)

    cv2.destroyAllWindows()
    logging.info("Video mode display ended.")

async def action_dispatcher(actions):
    """Dispatches tasks for audio, video, video_mode, and camera_move actions."""
    video_task = None
    audio_task = None
    video_mode_tasks = []  # List to hold multiple video_mode tasks

    for action in actions:
        if action['action'] == 'play_audio':
            audio_task = asyncio.create_task(play_audio(action))
        elif action['action'] == 'play_video':
            video_task = asyncio.create_task(play_video(action, display_frame))
        elif action['action'] == 'video_mode':
            video_mode_tasks.append(action)  # Add each video_mode action to the list
        elif action['action'] == 'camera_move':
            # Append only the command details (dict) for processing in the queue
            camera_move_queue.append(action)

    # Run play_video and play_audio concurrently
    if video_task and audio_task:
        await asyncio.gather(video_task, audio_task)
    elif video_task:
        await video_task
    elif audio_task:
        await audio_task

    # Process each video_mode action sequentially with queued camera moves
    for video_mode_task in video_mode_tasks:
        # Run video mode display concurrently with camera moves
        await asyncio.gather(
            display_video_mode(video_mode_task, list(camera_move_queue)),  # Pass a copy of camera tasks
            process_camera_move_queue()  # Process camera moves sequentially in parallel
        )

async def main():
    """Main function to process all scheduled programmes and events."""
    for programme in schedule['programmes']:
        logging.info(f"Starting programme: {programme['name']}")
        for event in programme['events']:
            logging.info(f"Starting event: {event['name']}")
            await action_dispatcher(event['actions'])
        logging.info(f"Programme ended: {programme['name']}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        cv2.destroyAllWindows()
