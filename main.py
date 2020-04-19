import cv2
import imutils
import serial
import numpy as np
import math
import time
# Source 1: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html#object-tracking
# Source 2: https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
camera_device = 0  # 1 on devices with built-in camera, most likely 0 otherwise
ideal_pos = [321, 464]  # testing reveals that this around where the bottom-center of screen is
MIN_DIST = 150  # threshold for distance being considered roughly 0
MIN_TURNDIST = 400 # Threshold for turning
MIN_T = 500
CMD_DELAY = 1  # how much to delay between commands
cam = cv2.VideoCapture(camera_device)
try:
    device = serial.Serial("/dev/ttyACM0", 9600)
except Exception:
    device = None


def drive(direction):  # valid dir: ['f', 'b', 'p', 'l', 'r', 's']
    global device
    global CMD_DELAY
    if device is not None:
        device.write(direction.encode())
        time.sleep(CMD_DELAY)

def main():
    global cam
    global ideal_pos
    global MIN_TURNDIST
    global MIN_DIST
    global MIN_T
    while 1:
        ret, raw_img = cam.read()
        if ret:
            lb = np.array([110, 50, 10])
            ub = np.array([130, 255, 255])
            hsv = cv2.cvtColor(raw_img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lb, ub)
            result_color = cv2.bitwise_and(raw_img, raw_img, mask=mask)
            gray = cv2.cvtColor(result_color, cv2.COLOR_RGB2GRAY)

            blurred = cv2.GaussianBlur(gray, (15, 15), 0)
            thresh = cv2.threshold(blurred, 10, 255, cv2.THRESH_BINARY)[1]
            centroids = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            centroids = imutils.grab_contours(centroids)
            max_area = 0  # counter for the largest object picked up with the countour area scan
            screen_pos = [0, 0]  # x,y of the center of the largest object on screen
            for c in centroids:
                # compute the center of the contour
                M = cv2.moments(c)
                if cv2.contourArea(c) > MIN_T:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    if cv2.contourArea(c) > max_area:
                        max_area = cv2.contourArea(c)
                        screen_pos[0] = cX
                        screen_pos[1] = cY
                    # draw the contour and center of the shape on the image
                    cv2.drawContours(raw_img, [c], -1, (0, 255, 0), 2)
                    cv2.circle(raw_img, (cX, cY), 7, (255, 255, 255), -1)
                    cv2.putText(raw_img, "center", (cX - 20, cY - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    # show the image
                    cv2.imshow("Image", raw_img)
                else:
                    cv2.imshow("Image", raw_img)
            if len(centroids) == 0:
                cv2.imshow("Image", raw_img)
                drive('p')  # stops car
                drive('s')  # stops turning
            else:
                x_dist = ideal_pos[0] - screen_pos[0]
                y_dist = ideal_pos[1] - screen_pos[1]  # should always be positive
                if math.fabs(x_dist) > MIN_TURNDIST and y_dist > MIN_DIST:
                    # If image is more then minimum distance offset, attempt to turn towards it
                    # Will also not attempt turning if it's already too close
                    if x_dist < 0:
                        drive('r')
                    elif x_dist > 200:
                        drive('l')
                elif math.fabs(x_dist) <= MIN_TURNDIST:
                    # If roughly centered, stop steering
                    drive('s')
                if y_dist > MIN_DIST:
                    # drive towards object if not too close
                    drive('f')
                elif y_dist <= MIN_DIST:
                    drive('p')  # stops car
                    drive('s')  # stops turning
                #print("X dist: ", x_dist)
                #print("Y dist: ", y_dist)
            #cv2.imshow("result", thresh)
            if cv2.waitKey(1) &0xFF == ord("x"):
                # exit if x key is pressed
                break

main()
