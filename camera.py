# Camera API Commands
import cv2
import requests
import time
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Camera:
    def __init__(self, camera_id, rtsp_url, ip, username, password):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.ip = ip
        self.username = username
        self.password = password
        self.base_url = f"https://{ip}/api.cgi"
        self.token, self.session = self.get_token()
        self.frame = None
        self.running = True
        self.cap = cv2.VideoCapture(rtsp_url)

    def get_frame(self):
        return self.frame
        
    def get_token(self, retries=3, timeout=10, delay=2):
        """Attempt to retrieve an authentication token with retries."""
        url = f"{self.base_url}?cmd=Login"
        login_payload = [{
            "cmd": "Login",
            "param": {
                "User": {
                    "Version": "0",
                    "userName": self.username,
                    "password": self.password
                }
            }
        }]
        
        for attempt in range(1, retries + 1):
            session = requests.Session()
            session.verify = False

            try:
                response = session.post(url, json=login_payload, timeout=timeout)
                if response.status_code == 200 and response.json():
                    token = response.json()[0]["value"]["Token"]["name"]
                    logging.info(f"Token obtained for camera {self.camera_id} on attempt {attempt}")
                    return token, session
            except requests.RequestException as e:
                logging.warning(f"Attempt {attempt} for camera {self.camera_id} failed: {e}")

            if attempt < retries:
                time.sleep(delay)
        
        logging.error(f"Failed to obtain token for camera {self.camera_id} after {retries} attempts.")
        return None, None

    def send_ptz_command(self, command, parameter, id):
        """Send a PTZ command to the camera with specified parameters."""
        url = f"{self.base_url}?cmd={command}&token={self.token}"

        if command == "PtzCtrl":
            if parameter in ["Left", "Right", "Up", "Down", "ZoomInc", "ZoomDec", "LeftUp", "LeftDown", "RightUp", "RightDown"]:
                payload = [{"cmd": command, "param": {"channel": 0, "op": parameter, "speed": 32}}]
            elif parameter == "ToPos":
                payload = [{"cmd": command, "param": {"channel": 0, "op": parameter, "id": id, "speed": 32}}]
            elif parameter == "Stop":
                payload = [{"cmd": command, "param": {"channel": 0, "op": parameter}}]
            else:
                logging.warning(f"Invalid parameter for command {command}")
                return

            response = self.session.post(url, json=payload, timeout=5)
            if response.status_code != 200:
                logging.error(f"Failed to send {command} {parameter} command to camera {self.camera_id}.")
        else:
            logging.warning(f"Only PtzCtrl commands handled currently")
    
    def capture_frames(self):
        """Continuously capture frames from the RTSP stream."""
        while self.running:
            ret, self.frame = self.cap.read()
            if not ret:
                logging.warning(f"Camera {self.camera_id} failed to capture frame.")
                break
        self.cap.release()

    def stop(self):
        """Stop the camera capture."""
        self.running = False
