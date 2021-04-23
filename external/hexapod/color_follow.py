#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cv2
import PWMServo
import time
import threading
import urllib
import numpy as np
import hexapod
import pid

x_output = 0
y_output = 0
update_ok = False
x_dis = 1500
y_dis = 1500
x_pid = pid.PID(P=0.3, I=0.15, D=0)
y_pid = pid.PID(P=0.3, I=0.15, D=0)
img_w = 480
img_h = 360

orgFrame = None
stream = None
bytes = ''
Running = False
get_image_ok = False


def cv_stop(signum, frame):
    global Running

    print("cv_ball_color_Stop")
    if Running is True:
        Running = False
    cv2.destroyWindow('cv_ball_frame')
    cv2.destroyAllWindows()


def cv_continue(signum, frame):
    global stream
    global Running
    print('CV Colour tracking')
    if Running is False:
        # Connect to the power switch
        if stream:
            stream.close()
        stream = urllib.urlopen("http://127.0.0.1:8080/?action=stream?dummy=param.mjpg")
        bytes = ''
        # # Perform action group reset position
        Running = True


# According to the PID output, adjust the position of the camera
def adjust():
    global x_output
    global y_output
    global update_ok
    global x_dis
    while True:
        if update_ok:
            # print x_output
            PWMServo.setServo(1, int(x_dis), 20)
            time.sleep(0.02)
            PWMServo.setServo(2, int(y_dis), 20)
            time.sleep(0.02)
            update_ok = False
        else:
            time.sleep(0.01)


th2 = threading.Thread(target=adjust)
th2.setDaemon(True)     # Set the background thread, which defaults is "False", and when it set to "True", the main thread doesn't have to wait for the sub-threads
th2.start()


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
                    bytes = bytes[b + 2:]  # Remove the data that has been taken out
                    orgFrame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)  # Decode the image
                    orgFrame = cv2.resize(orgFrame, (480, 360), interpolation=cv2.INTER_LINEAR)  # Scale the image to
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


if __name__ == '__main__':
    cv_continue(0, 0)
    hexapod.camera_pos_init()
    hexapod.hexapod_init()
    while True:
        get_color = False
        if orgFrame is not None and get_image_ok:
            res = orgFrame
            hsv = cv2.cvtColor(res, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, color_dist['blue']['Lower'], color_dist['blue']['Upper'])
            mask = cv2.erode(mask, None, iterations=2)
            # Expand
            mask = cv2.dilate(mask, None, iterations=2)
            # cv2.imshow('mask', mask)
            # Find the contour
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            center_x = 240.0
            center_y = 180.0
            if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                # etermine the minimumcircumcircle origin coordinates x, y and radius
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                ball_x = int(x)
                ball_y = int(y)
                # M = cv2.moments(c)

                if radius >= 10:

                    cv2.circle(res, (int(x), int(y)), int(radius), (0, 255, 255), 2)  # The smallest circumcircle of an object
                    cv2.circle(res, (int(x), int(y)), 5, (0, 255, 255), -1)  # The object center

                    x_pid.SetPoint = center_x
                    y_pid.SetPoint = center_y
                    x_pid.update(ball_x)
                    y_pid.update(ball_y)
                    x_output = x_pid.output
                    y_output = y_pid.output
                    x_dis += x_output
                    y_dis -= y_output
                    if x_dis < 500:
                        x_dis = 500
                    elif x_dis > 2500:
                        x_dis = 2500

                    if y_dis < 500:
                        y_output = 500
                    elif y_output > 2500:
                        y_output = 2500

                    update_ok = True

            cv2.line(res, ((img_w / 2) - 20, (img_h / 2)), ((img_w / 2) + 20, (img_h / 2)), (255, 255, 0), 1)
            cv2.line(res, ((img_w / 2), (img_h / 2) - 20), ((img_w / 2), (img_h / 2) + 20), (255, 255, 0), 1)
            # cv2.imshow('cv_ball_frame', res)
            get_image_ok = False
            cv2.waitKey(1)
        else:
            time.sleep(0.01)

