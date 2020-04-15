import cv2
import serial
import time
camera_device = 1  # 1 on devices with built-in camera, most likely 0 otherwise
# noinspection PyArgumentList
cap = cv2.VideoCapture(camera_device)
device = serial.Serial(3)

device.write("forward")
time.sleep(5)
device.write("straighten")
time.sleep(5)
device.write("right")
time.sleep(5)
device.write("left")
#while 1:
    #ret, frame = cap.read()
    #grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("Camera Feed", grayFrame)
    #if cv2.waitKey(1) &0xFF == ord("x"):
        #exit if x key is pressed
        #break
