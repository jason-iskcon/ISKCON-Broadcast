import cv2
import numpy as np
import time
import yaml
from datetime import datetime
import argparse
import requests
import threading

CAMERA_IP = "192.168.87.76"
USERNAME = "admin"
PASSWORD = "Gaura108"
BASE_URL = f"https://{CAMERA_IP}/api.cgi"

# Load configurations
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Camera API Commands
def get_token():
    """Get authentication token from the camera."""
    url = f"{BASE_URL}?cmd=Login"
    login_payload = [{"cmd": "Login", "param": {"User": {"Version": "0", "userName": USERNAME, "password": PASSWORD}}}]
    session = requests.Session()
    session.verify = False  # Disable SSL verification for testing
    
    try:
        response = session.post(url, json=login_payload, timeout=5)
        response_data = response.json()
        if response_data[0]["code"] == 0:
            token = response_data[0]["value"]["Token"]["name"]
            print("Token obtained:", token)
            return token, session
        else:
            print("Failed to obtain token. Response:", response_data)
    except requests.RequestException as e:
        print("Error:", e)
    return None, None

def set_ptz_preset(token, session, marker_id):
    """Move the camera to the specified PTZ preset (marker)."""
    url = f"{BASE_URL}?cmd=SetPtzPreset&token={token}"
    data = [{"cmd": "SetPtzPreset", "action": 0, "param": {"PtzPreset": {"channel": 0, "id": marker_id}}}]
    response = session.post(url, json=data, verify=False)
    if response.status_code == 200:
        print(f"Moved camera to marker ID: {marker_id}")
    else:
        print("Failed to move camera to marker")

# Camera movement
def send_ptz_command(token, session, command, parameter, speed=32, id=0):
    """Send a PTZ command to the camera with specified parameters."""
    url = f"{BASE_URL}?cmd={command}&token={token}"

    if command == "PtzCtrl":
        if parameter in ["Left", "Right", "Up", "Down", "ZoomInc", "ZoomDec"]:
            payload = [{"cmd": command, "action": 0, "param": {"channel": 0, "op": parameter, "speed": speed}}]
        elif parameter == "Stop":
            payload = [{"cmd": command, "action": 0, "param": {"channel": 0, "op": "Stop"}}]
        elif parameter == "ToPos" and id > 0:
            payload = [{"cmd": command, "action": 0, "param": {"channel": 0, "id": id, "op": parameter, "speed": speed}}]
        else:
            print(f"Invalid parameter for command {command}")
            return
    else:
        print(f"Invalid command: {command}")
        return

    response = session.post(url, json=payload, timeout=5)
    if response.status_code == 200:
        print(f"{command} {parameter} command sent successfully.")
    else:
        print(f"Failed to send {command} {parameter} command.")

def apply_camera_movement(token, session, movement):
    """
    Applies the specified camera movement using the camera's API with speed and duration.
    
    Parameters:
    - token: The authentication token for the camera API
    - session: The HTTP session object with the token
    - movement: A dictionary containing type, speed, duration, and optionally marker_id
    """
    movement_type = movement.get("type")
    speed = movement.get("speed", 32)  # Default speed
    duration = movement.get("duration", 1.0)  # Default duration

    # Execute the movement command based on the movement type
    if movement_type == 'pan_left':
        send_ptz_command(token, session, "PtzCtrl", "Left", speed=speed)
    elif movement_type == 'pan_right':
        send_ptz_command(token, session, "PtzCtrl", "Right", speed=speed)
    elif movement_type == 'tilt_up':
        send_ptz_command(token, session, "PtzCtrl", "Up", speed=speed)
    elif movement_type == 'tilt_down':
        send_ptz_command(token, session, "PtzCtrl", "Down", speed=speed)
    elif movement_type == 'zoom_in':
        send_ptz_command(token, session, "PtzCtrl", "ZoomInc", speed=speed)
    elif movement_type == 'zoom_out':
        send_ptz_command(token, session, "PtzCtrl", "ZoomDec", speed=speed)
    elif movement_type == 'move_to_marker':
        marker_id = movement.get("marker_id", 0)
        send_ptz_command(token, session, "PtzCtrl", "ToPos", id=marker_id, speed=speed)
    else:
        print(f"Invalid movement type: {movement_type}")
        return

    # Hold movement for the specified duration, then stop
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def resize_frame_to_fit(frame, width, height):
    """Resize frame to fit specified width and height, maintaining aspect ratio."""
    original_height, original_width = frame.shape[:2]
    scaling_factor = min(width / original_width, height / original_height)
    return cv2.resize(frame, (int(original_width * scaling_factor), int(original_height * scaling_factor)), interpolation=cv2.INTER_AREA)

# Dual view
def dual_capture_display(background, frame0, frame1, pos0, pos1, scale0, scale1):
    h, w = background.shape[:2]
    target_width0, target_height0 = int(w * scale0 / 100), int(h * scale0 / 100)
    target_width1, target_height1 = int(w * scale1 / 100), int(h * scale1 / 100)

    frame0_resized = resize_frame_to_fit(frame0, target_width0, target_height0)
    frame1_resized = resize_frame_to_fit(frame1, target_width1, target_height1)

    h0, w0 = frame0_resized.shape[:2]
    h1, w1 = frame1_resized.shape[:2]

    background[pos0[1]:pos0[1] + h0, pos0[0]:pos0[0] + w0] = frame0_resized
    background[pos1[1]:pos1[1] + h1, pos1[0]:pos1[0] + w1] = frame1_resized
    return background

# Fullscreen view
def fullscreen_display(background, frame, pos, scale):
    h, w = background.shape[:2]
    target_width, target_height = int(w * scale / 100), int(h * scale / 100)
    frame_resized = resize_frame_to_fit(frame, target_width, target_height)
    h_resized, w_resized = frame_resized.shape[:2]
    background[pos[1]:pos[1] + h_resized, pos[0]:pos[0] + w_resized] = frame_resized
    return background

# Main orchestration function
def main(mode_config_file='mode_config.yaml', schedule_file='orchestration.yaml', debug_time=None):
    mode_config = load_config(mode_config_file)
    schedule = load_config(schedule_file)

    background_image = cv2.imread(mode_config['background_image'])
    cap0 = cv2.VideoCapture(mode_config['sources'][0]['url'])
    cap1 = cv2.VideoCapture(mode_config['sources'][1]['url'])

    token, session = get_token()
    while True:
        time_now = debug_time if debug_time else datetime.now().time()

        for programme in schedule["programmes"]:
            for event in programme["events"]:
                event_start = datetime.strptime(event["start_time"], "%H:%M").time()
                event_end = datetime.strptime(event["end_time"], "%H:%M").time()
                
                if event_start <= time_now < event_end:
                    for action in event["actions"]:
                        if action["action"] == "video_mode":
                            mode_name = action["mode"]
                            duration = action["duration"]
                            mode_settings = mode_config['modes'][mode_name]
                            
                            for _ in range(int(duration)):
                                ret0, frame0 = cap0.read()
                                ret1, frame1 = cap1.read()
                                if not ret0 or not ret1:
                                    print("Unable to read video sources.")
                                    break

                                display_frame = background_image.copy()
                                if mode_settings['type'] == 'dual_view':
                                    pos0, pos1 = tuple(mode_settings['pos0']), tuple(mode_settings['pos1'])
                                    scale0, scale1 = mode_settings['scale0'], mode_settings['scale1']
                                    display_frame = dual_capture_display(display_frame, frame0, frame1, pos0, pos1, scale0, scale1)
                                elif mode_settings['type'] == 'fullscreen_0':
                                    display_frame = fullscreen_display(display_frame, frame0, tuple(mode_settings['pos']), mode_settings['scale'])
                                elif mode_settings['type'] == 'fullscreen_1':
                                    display_frame = fullscreen_display(display_frame, frame1, tuple(mode_settings['pos']), mode_settings['scale'])

                                cv2.imshow('Display', display_frame)
                                if cv2.waitKey(1) == ord('q'):
                                    break

                        elif action["action"] == "camera_move":
                            apply_camera_movement(token, session, action)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the video orchestration with optional debug time.')
    parser.add_argument('--debug-time', type=str, help="Specify a debug time in HH:MM format for testing.")
    args = parser.parse_args()

    debug_time = None
    if args.debug_time:
        try:
            debug_time = datetime.strptime(args.debug_time, "%H:%M").time()
            print(f"Debug mode activated. Testing at {debug_time}.")
        except ValueError:
            print("Invalid time format for --debug-time. Use HH:MM.")
    
    main(debug_time=debug_time)
