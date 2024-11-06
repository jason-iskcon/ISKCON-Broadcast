import cv2
import time
import asyncio
import logging
import yaml
import numpy as np
import pygame
import threading
from camera import Camera

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

async def process_camera_move(task):
    logging.info(f"Processing camera move: {task}")
    cameras[0].send_ptz_command(command="PtzCtrl", parameter=task['type'], id=task.get('marker', 0))
    await asyncio.sleep(task['duration'])  # Simulate camera movement duration
    cameras[0].send_ptz_command(command="PtzCtrl", parameter="Stop", id=0)

async def play_audio(task):
    """Play audio asynchronously using asyncio."""
    logging.info(f"Playing audio: {task['file']} for {task['duration']} seconds")
    pygame.mixer.music.load(task['file'])
    pygame.mixer.music.play()
    await asyncio.sleep(task['duration'])
    pygame.mixer.music.stop()
    logging.info("Audio playback ended.")

async def play_video(task, display_frame):
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

def resize_frame_to_fit(frame, width, height):
    """Resize frame to fit specified width and height, maintaining aspect ratio."""
    original_height, original_width = frame.shape[:2]
    scaling_factor = min(width / original_width, height / original_height)
    return cv2.resize(frame, (int(original_width * scaling_factor), int(original_height * scaling_factor)), interpolation=cv2.INTER_AREA)

def fullscreen_display(background, camera, pos, scale):
    frame = camera.get_frame()
    target_width, target_height = int(background.shape[1] * scale / 100), int(background.shape[0] * scale / 100)
    frame_resized = resize_frame_to_fit(frame, target_width, target_height)
    h_resized, w_resized = frame_resized.shape[:2]
    background[pos[1]:pos[1] + h_resized, pos[0]:pos[0] + w_resized] = frame_resized
    return background

def dual_capture_display(background, camera0, camera1, pos0, pos1, scale0, scale1):
    frame0 = camera0.get_frame()
    frame1 = camera1.get_frame()
    frame0_resized = resize_frame_to_fit(frame0, int(background.shape[1] * scale0 / 100), int(background.shape[0] * scale0 / 100))
    frame1_resized = resize_frame_to_fit(frame1, int(background.shape[1] * scale1 / 100), int(background.shape[0] * scale1 / 100))
    h0, w0 = frame0_resized.shape[:2]
    h1, w1 = frame1_resized.shape[:2]
    background[pos0[1]:pos0[1] + h0, pos0[0]:pos0[0] + w0] = frame0_resized
    background[pos1[1]:pos1[1] + h1, pos1[0]:pos1[0] + w1] = frame1_resized
    return background

async def display_video_mode(task, camera_tasks):
    logging.info(f"Displaying video mode: {task['mode']} for {task['duration']} seconds")
    mode_settings = mode_config['modes'].get(task['mode'])
    duration = task['duration']
    end_time = time.time() + duration
    global display_frame

    while time.time() < end_time:
        # Apply display mode configurations
        if mode_settings['type'] == 'dual_view':
            display_frame = dual_capture_display(display_frame, cameras[0], cameras[1],
                                                 tuple(mode_settings['pos0']), tuple(mode_settings['pos1']),
                                                 mode_settings['scale0'], mode_settings['scale1'])
        elif task['mode'] == 'fullscreen_0':
            display_frame = fullscreen_display(display_frame, cameras[0], tuple(mode_settings['pos']), mode_settings['scale'])
        elif task['mode'] == 'fullscreen_1':
            display_frame = fullscreen_display(display_frame, cameras[1], tuple(mode_settings['pos']), mode_settings['scale'])

        cv2.imshow('Display', display_frame)
        if cv2.waitKey(1) == ord('q'):
            break
        await asyncio.sleep(0.1)

    await asyncio.gather(*camera_tasks)
    cv2.destroyAllWindows()
    logging.info("Video mode display ended.")

async def process_action(task):
    if task['action'] == 'camera_move':
        await process_camera_move(task)
    elif task['action'] == 'play_audio':
        await play_audio(task)
    elif task['action'] == 'play_video':
        await play_video(task)
    elif task['action'] == 'video_mode':
        camera_tasks = [asyncio.create_task(process_camera_move(camera_move_task)) for camera_move_task in task.get("camera_moves", [])]
        await display_video_mode(task, camera_tasks)

async def action_dispatcher(actions):
    video_task = None
    audio_task = None
    video_mode_task = None
    camera_move_tasks = []

    for action in actions:
        if action['action'] == 'play_audio':
            audio_task = asyncio.create_task(play_audio(action))
        elif action['action'] == 'play_video':
            video_task = asyncio.create_task(play_video(action, display_frame))
        elif action['action'] == 'video_mode':
            video_mode_task = action
        elif action['action'] == 'camera_move':
            camera_move_tasks.append(action)

    # Run play_video and play_audio concurrently
    if video_task and audio_task:
        await asyncio.gather(video_task, audio_task)
    elif video_task:
        await video_task
    elif audio_task:
        await audio_task

    # Now handle video_mode with camera moves
    if video_mode_task:
        await display_video_mode(video_mode_task, [asyncio.create_task(process_camera_move(task)) for task in camera_move_tasks])

async def main():
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
