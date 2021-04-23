#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cv2
import PWMServo
import time
import threading
import urllib
import hexapod
import numpy as np

color = 0
rR = 0
rG = 0
rB = 0

orgFrame = None
stream = None
bytes = ''
Running = False
get_image_ok = False


def cv_continue():
    global stream
    global Running
    print(' CV Colour identification')
    if Running is False:
        # Connect to the power switch
        if stream:
            stream.close()
        stream = urllib.urlopen("http://127.0.0.1:8080/?action=stream?dummy=param.mjpg")
        bytes = ''
        # # Perform action group reset position
        Running = True


def get_image():
    global Running
    global orgFrame
    global bytes
    global get_image_ok
    while True:
        if Running:
            try:
                bytes += stream.read(4096)  # Receive data
                a = bytes.find('\xff\xd8')  # Find the frame head
                b = bytes.find('\xff\xd9')  # Find the frame tail
                if a != -1 and b != -1:
                    jpg = bytes[a:b + 2]  # Take the image data
                    bytes = bytes[b + 2:]  # Delete the data that has been taken out
                    orgFrame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)  # Decode the image
                    orgFrame = cv2.resize(orgFrame, (480, 360), interpolation=cv2.INTER_LINEAR)  # 
                    get_image_ok = True
            except Exception as e:
                print(e)
                continue
        else:
            time.sleep(0.01)


th1 = threading.Thread(target=get_image)
th1.setDaemon(True)     # Set the background thread, which defaults is "False", and when it set to "True", the main thread doesn't have to wait for the sub-threads
th1.start()

# The red, green and blue HSV value dictionary
color_dist = {'red': {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'green': {'Lower': np.array([35, 43, 46]), 'Upper': np.array([77, 255, 255])},
              }


def run_action(type):
    if type == 0:  # The camera echo
        PWMServo.setServo(1, 1500, 100)
        time.sleep(0.1)
        PWMServo.setServo(2, 1500, 100)
        time.sleep(0.1)
    elif type == 1:  # Nod
        PWMServo.setServo(2, 1200, 200)
        time.sleep(0.2)
        PWMServo.setServo(2, 1700, 200)
        time.sleep(0.2)
    elif type == 2:  # Shake head
        PWMServo.setServo(1, 1200, 200)
        time.sleep(0.2)
        PWMServo.setServo(1, 1700, 200)
        time.sleep(0.2)


if __name__ == '__main__':
    cv_continue()
    hexapod.hexapod_init()
    run_action(0)
    while True:
        get_color = False
        if orgFrame is not None and get_image_ok:
            res = frame = orgFrame
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            for i in color_dist:
                mask = cv2.inRange(hsv, color_dist[i]['Lower'], color_dist[i]['Upper'])
                mask = cv2.erode(mask, None, iterations=2)
                # Expand
                mask = cv2.dilate(mask, None, iterations=2)
                # cv2.imshow('mask', mask)
                # Find the contour
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                center = None
                if len(cnts) > 0:
                    c = max(cnts, key=cv2.contourArea)
                    # Determine the minimumcircumcircle origin coordinates x, y and radius
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    if radius >= 50:  # The radius is greater than 140
                        cv2.circle(res, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                        if i == 'red':
                            run_action(1)
                            run_action(1)
                            run_action(0)
                        elif i == 'blue':
                            run_action(2)
                            run_action(2)
                            run_action(0)
                        elif i == 'green':
                            run_action(2)
                            run_action(2)
                            run_action(0)
                    else:
                        run_action(0)

            # cv2.imshow('cv_ball_frame', res)
            get_image_ok = False
            cv2.waitKey(1)
        else:
            time.sleep(0.01)
