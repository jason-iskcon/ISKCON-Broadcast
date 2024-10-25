import cv2
import numpy as np
import json
import time

# Initialize the camera
cap = cv2.VideoCapture(0)

# Parameters for apple detection (Red color in HSV)
lower_red_1 = np.array([0, 100, 100])    # Lower bound for red (in Hue)
upper_red_1 = np.array([10, 255, 255])   # Upper bound for lower red
lower_red_2 = np.array([160, 100, 100])  # Lower bound for upper red
upper_red_2 = np.array([180, 255, 255])  # Upper bound for upper red

# Log to store movement data
movement_log = []

# Define pan, tilt, and zoom parameters
pan = 0
tilt = 0
zoom = 1.0
zoom_step = 0.1  # Example zoom step for demonstration

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create masks for the red apple
    mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Apply morphological operations to reduce noise and enhance the apple shape
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours of the detected apple
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if contours:
        # Get the largest contour
        c = max(contours, key=cv2.contourArea)
        
        area = cv2.contourArea(c)

        # Only consider contours that are large enough and have an appropriate shape
        if area > 500:  # Minimum area threshold for an apple
            # Fit an ellipse to the contour (works for non-round shapes)
            if len(c) >= 5:  # An ellipse requires at least 5 points
                ellipse = cv2.fitEllipse(c)
                (x, y), (MA, ma), angle = ellipse  # Get the ellipse parameters
                aspect_ratio = MA / ma

                # Filter based on an expected aspect ratio for an apple (near 1.0)
                if 0.8 < aspect_ratio < 1.2:  # Adjust these values as needed
                    center = (int(x), int(y))

                    # Log the pan, tilt, and zoom actions
                    movement_log.append({
                        'timestamp': time.time(),
                        'pan': pan,
                        'tilt': tilt,
                        'zoom': zoom
                    })

                    # Move the camera based on the apple's position (pseudo-logic here)
                    if center[0] < frame.shape[1] // 2 - 50:
                        pan -= 1  # Move left
                    elif center[0] > frame.shape[1] // 2 + 50:
                        pan += 1  # Move right

                    if center[1] < frame.shape[0] // 2 - 50:
                        tilt -= 1  # Move up
                    elif center[1] > frame.shape[0] // 2 + 50:
                        tilt += 1  # Move down
                    
                    # Simulate zooming in or out
                    if area > 5000:  # Example threshold for zooming in
                        zoom += zoom_step
                    else:
                        zoom = max(1.0, zoom - zoom_step)  # Don't zoom out below 1.0

                    # Draw the detected apple
                    cv2.ellipse(frame, ellipse, (0, 255, 0), 2)  # Draw the fitted ellipse

    # Display the resulting frame
    cv2.imshow('Frame', frame)

    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()

# Save movement log to a JSON file
with open('movement_log.json', 'w') as log_file:
    json.dump(movement_log, log_file, indent=4)

print("Movement log saved to 'movement_log.json'")
