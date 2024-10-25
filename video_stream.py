import numpy as np
import cv2

background_image = cv2.imread('assets/class_background.png', 1)

cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture('rtsp://admin:Gaura108@192.168.86.57:554/11')

while True:

    cv2.imshow('frame', background_image)
    if cv2.waitKey(1) == ord('q'):
        break


cap0.release()
cap1.release()
cv2.destroyAllWindows()

#def Refactored(frame, capture, width_denom, height_denom):

def DualCapture(cap0, cap1):
    
    ret, frame0 = cap0.read()
    width = int(cap0.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap0.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame0 = cv2.resize(frame0,((width//3)+0, (height//3)+0), interpolation = cv2.INTER_AREA)

    background_image[480:480+((height//3)+0),854:854+((width//3)+0)] = frame0

    ret, frame1 = cap1.read()
    width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame1 = cv2.resize(frame1,(width//4, height//4), interpolation = cv2.INTER_AREA)

    background_image[:height//4,:width//4] = frame1

def DualCaptureSeconds(cap0, cap1, secs):

    DualCapture(cap0, cap1)
    Sleep(secs)

def ZoomCapture(cap, secs):

    ret, frame0 = cap.read()
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame0 = cv2.resize(frame0,((width//3)+0, (height//3)+0), interpolation = cv2.INTER_AREA)

    background_image[480:480+((height//3)+0),854:854+((width//3)+0)] = frame0
