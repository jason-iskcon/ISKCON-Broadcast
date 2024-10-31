import requests
import time

# Camera credentials and IP address
CAMERA_IP = "192.168.87.76"
USERNAME = "admin"
PASSWORD = "Gaura108"

# Base URL for API requests
BASE_URL = f"https://{CAMERA_IP}/api.cgi"

def get_token():
    """Get authentication token from the camera."""
    url = f"{BASE_URL}?cmd=Login"
    login_payload = [
        {
            "cmd": "Login",
            "param": {
                "User": {
                    "Version": "0",
                    "userName": USERNAME,
                    "password": PASSWORD
                }
            }
        }
    ]
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

def send_ptz_command(token, session, command, parameter, speed=32, id=0):
    """Send PTZ command to the camera."""
    url = f"{BASE_URL}?cmd={command}&token={token}"
    
    if command == "PtzCtrl":
        if parameter in ["Left", "Right", "Up", "Down", "LeftUp", "RightUp", "LeftDown", "RightDown", "ZoomInc", "ZoomDec", "FocusInc", "FocusDec"]:
            payload = [{"cmd": command, "action": 0, "param": {"channel": 0, "op": parameter, "speed": speed}}]
        elif parameter == "Stop":
            payload = [{"cmd": command, "action": 0, "param": {"channel": 0, "op": parameter}}]
        elif parameter == "ZoomPos":
            payload = [{"cmd": command, "action": 0, "param": {"ZoomFocus": {"channel": 0, "op": parameter, "pos": speed}}}]
        elif parameter == "ToPos":
            payload = [{"cmd": command, "action": 0, "param": {"channel": 0, "id": id, "op": parameter, "speed": speed}}]
        elif parameter in ["StartPatrol", "StopPatrol"]:
            payload = [{"cmd": command, "action": 0, "param": {"channel": 0, "id": id, "op": parameter}}]
        else:
            print(f"Invalid parameter for command {command}")
            return
    elif command == "GetPtzPatrol":
        payload = [{"cmd": command, "action": 0, "param": {"channel": 0}}]
    elif command == "SetPtzPatrol":
        payload = [{"cmd": command, "action": 0, "param": {"PtzPatrol": parameter}}]
    else:
        print(f"Invalid command: {command}")
        return
    
    try:
        response = session.post(url, json=payload, timeout=5)
        if response.status_code == 200 and response.json()[0]["value"]["rspCode"] == 200:
            print(f"{command} {parameter} command sent successfully.")
        else:
            print(f"Failed to send {command} {parameter} command. Response: {response.json()}")
    except requests.RequestException as e:
        print("Error:", e)

# Higher-level control functions
def pan_right(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "Right", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def pan_left(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "Left", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def tilt_up(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "Up", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def tilt_down(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "Down", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def zoom_in(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "ZoomInc", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def zoom_out(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "ZoomDec", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

# Diagonal movement functions
def pan_tilt_left_up(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "LeftUp", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def pan_tilt_right_up(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "RightUp", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def pan_tilt_left_down(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "LeftDown", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

def pan_tilt_right_down(token, session, duration=1.0, speed=32):
    send_ptz_command(token, session, "PtzCtrl", "RightDown", speed=speed)
    time.sleep(duration)
    send_ptz_command(token, session, "PtzCtrl", "Stop")

# Execute commands
token, session = get_token()
if token:

    # Examples of refined control commands
    pan_left(token, session, duration=6, speed=32)
    # pan_tilt_left_up(token, session, duration=1.0, speed=20)
    # zoom_in(token, session, duration=1.0, speed=20)
    # pan_tilt_right_down(token, session, duration=1.0, speed=16)
    tilt_up(token, session, duration=1.5, speed=24)
    # zoom_out(token, session, duration=1.0, speed=20)
