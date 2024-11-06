import cv2
import requests
import threading
import time
import yaml
from datetime import datetime, timedelta
import argparse
import pygame
import logging
from camera import Camera

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

# Initialize pygame for audio playback
pygame.mixer.init()

# Load YAML configuration
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Display functions
def resize_frame_to_fit(frame, width, height):
    """Resize frame to fit specified width and height, maintaining aspect ratio."""
    original_height, original_width = frame.shape[:2]
    scaling_factor = min(width / original_width, height / original_height)
    return cv2.resize(frame, (int(original_width * scaling_factor), int(original_height * scaling_factor)), interpolation=cv2.INTER_AREA)


def dual_capture_display(background, camera0, camera1, pos0, pos1, scale0, scale1, duration):

    logging.debug("Applying dual display")
    start_time = time.time()
    while (time.time() - start_time) < duration:

        frame0 = camera0.get_frame()
        frame1 = camera1.get_frame()
        h, w = background.shape[:2]
        target_width0, target_height0 = int(w * scale0 / 100), int(h * scale0 / 100)
        target_width1, target_height1 = int(w * scale1 / 100), int(h * scale1 / 100)

        frame0_resized = resize_frame_to_fit(frame0, target_width0, target_height0)
        frame1_resized = resize_frame_to_fit(frame1, target_width1, target_height1)

        h0, w0 = frame0_resized.shape[:2]
        h1, w1 = frame1_resized.shape[:2]

        background[pos0[1]:pos0[1] + h0, pos0[0]:pos0[0] + w0] = frame0_resized
        background[pos1[1]:pos1[1] + h1, pos1[0]:pos1[0] + w1] = frame1_resized

        cv2.imshow('Display', background)
        if cv2.waitKey(1) == ord('q'):
            break

    logging.info("Finished applying dual display.")

def fullscreen_display(background, camera, pos, scale, duration):

    logging.debug("Applying fullscreen display")
    start_time = time.time()
    while (time.time() - start_time) < duration:

        frame = camera.get_frame()
        h, w = background.shape[:2]
        target_width, target_height = int(w * scale / 100), int(h * scale / 100)
        frame_resized = resize_frame_to_fit(frame, target_width, target_height)
        h_resized, w_resized = frame_resized.shape[:2]
        background[pos[1]:pos[1] + h_resized, pos[0]:pos[0] + w_resized] = frame_resized

        cv2.imshow('Display', background)
        if cv2.waitKey(1) == ord('q'):
            break

    logging.info("Finished applying fullscreen display.")

# Asynchronous action functions
def play_audio_async(audio_path, duration):
    """Play audio asynchronously."""
    def _play_audio():
        logging.info(f"Playing audio: {audio_path} for duration: {duration} seconds")
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

        time.sleep(duration)
        pygame.mixer.music.stop()
        logging.info("Stopped playing audio.")
    
    threading.Thread(target=_play_audio).start()

def move_camera_async(camera, command, parameter, speed, id):

    logging.info(f"Moving camera {camera.camera_id} with command {command}, parameter {parameter}, speed {speed}")
    camera.send_ptz_command(command, parameter, speed=speed, id=id)    

def play_video(video_path, duration, background_image):

    logging.info(f"Playing video: {video_path} for duration: {duration} seconds")
    cap = cv2.VideoCapture(video_path)

    start_time = time.time()
    while cap.isOpened() and ((time.time() - start_time) < duration):
        ret, frame = cap.read()
        if not ret:
            break
        frame_resized = resize_frame_to_fit(frame, *background_image.shape[1::-1])
        display_frame = background_image.copy()
        display_frame[:frame_resized.shape[0], :frame_resized.shape[1]] = frame_resized
        cv2.imshow('Display', display_frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    logging.info("Finished playing video.")

def execute_camera_action(action, cameras):

    action_type = action["action"]
    logging.info(f"Executing action: {action_type}")
    
    if action_type == "camera_move":

        camera_id = action.get("camera", 0)
        camera = next((cam for cam in cameras if cam.camera_id == camera_id), None)

        if camera:
            logging.info(f"Executing move_camera_async: {action_type}")
            move_camera_async(camera, "PtzCtrl", action.get("type", ""), action.get("speed", 32), action.get("marker", ""))
            time.sleep(action.get("duration", 0))
            move_camera_async(camera, "PtzCtrl", "Stop", 32, "")

        else:
            logging.warning(f"Camera with ID {camera_id} not found for action {action}")
    else:
        logging.warning(f"Unknown action type: {action_type}")


# Main function
def VideoStreamHandler(mode_config_file='mode_config.yaml', schedule_file='orchestration.yaml', debug_time=None):

    mode_config = load_config(mode_config_file)
    schedule = load_config(schedule_file)

    cameras = [Camera(i, cam['rtsp_url'], cam['https']['ip'], cam['https']['username'], cam['https']['password'])
               for i, cam in enumerate(mode_config['cameras'])]

    for cam in cameras:
        threading.Thread(target=cam.capture_frames).start()

    background_image = cv2.imread(mode_config['background_image'])

    try:
        while True:
            time_now = debug_time if debug_time else datetime.now().time()
            logging.debug(f"Current time: {time_now}")
            display_frame = background_image.copy()

            for programme in schedule["programmes"]:
                logging.debug(f"Checking programme: {programme['name']}")
                for event in programme["events"]:
                    event_start = datetime.strptime(event["start_time"], "%H:%M").time()
                    event_end = datetime.strptime(event["end_time"], "%H:%M").time()
                    
                    logging.debug(f"Checking event: {event['name']} from {event_start} to {event_end}")

                    if event_start <= time_now < event_end:
                        logging.info(f"Executing event: {event['name']}")
                        for action in event["actions"]:
                            logging.debug(f"Processing action: {action['action']}")
                            
                            if action['action'] == 'video_mode':
                                mode_settings = mode_config['modes'].get(action['mode'])

                                if mode_settings['type'] == 'dual_view':
                                    if len(cameras) >= 2:
                                        dual_capture_display(
                                            display_frame, cameras[0], cameras[1],
                                            tuple(mode_settings['pos0']), tuple(mode_settings['pos1']),
                                            mode_settings['scale0'], mode_settings['scale1'],
                                            action['duration']
                                        )
                                    else:
                                        logging.warning(f"Only one camera working")

                                elif mode_settings['type'] == 'fullscreen_0':
                                    if cameras[0].frame is not None:
                                        fullscreen_display(display_frame, cameras[0], tuple(mode_settings['pos']), mode_settings['scale'], action['duration'])
                                    else:
                                        logging.warning(f"Camera has no available frame")

                                elif mode_settings['type'] == 'fullscreen_1':
                                    if len(cameras) > 1:
                                        if cameras[1].frame is not None:
                                            fullscreen_display(display_frame, cameras[1], tuple(mode_settings['pos']), mode_settings['scale'], action['duration'])
                                        else:
                                            logging.warning(f"Camera has no available frame")
                                    else:
                                        logging.warning(f"Only one camera working")

                            elif action['action'] == "play_video":
                                play_video(f"{action['file']}", action.get("duration", 10), background_image)

                            elif action['action'] == "play_audio":
                                play_audio_async(f"{action['file']}", action.get("duration", 10))

                            else:
                                # move_camera action
                                execute_camera_action(action, cameras)
    finally:
        for cam in cameras:
            cam.stop()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the video orchestration with optional debug time.')
    parser.add_argument('--debug-time', type=str, help="Specify a debug time in HH:MM format for testing.")
    args = parser.parse_args()

    debug_time = None
    if args.debug_time:
        try:
            debug_time = datetime.strptime(args.debug_time, "%H:%M").time()
            logging.info(f"Debug mode activated. Testing schedule at {debug_time}.")
        except ValueError:
            logging.error("Invalid time format for --debug-time. Please use HH:MM.")

    VideoStreamHandler(debug_time=debug_time)