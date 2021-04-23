#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# After the ball color identification, execute this action group

import cv2
import numpy as np
import time
import urllib
import threading
import signal
import hexapod
import PWMServo
import math
import Serial_Servo_Running as SSR

last_turn = None
stream = None
bytes = ''
orgFrame = None
Running = False
get_image_ok = False
cv_ok = False
angle_factor = 0.125
line_out = False
# The weighted value in three regions   from top to bottom
weight = [0, 0.5, 0.5]
weight_sum = 0
for w in range(len(weight)):
    weight_sum += weight[w]

# The robot rotation angle
deflection_angle = 0

# Pause the callback of the signal


def cv_stop(signum, frame):
    global Running

    print("cv_ball_color_Stop")
    if Running is True:
        Running = False
    cv2.destroyWindow('cv_ball_frame')
    cv2.destroyAllWindows()


# Continue the callback of the signal
def cv_continue(signum, frame):
    global stream
    global Running
    print("Line following")
    if Running is False:
        # Connect to the power switch
        if stream:
            stream.close()
        stream = urllib.urlopen("http://127.0.0.1:8080/?action=stream?dummy=param.mjpg")
        bytes = ''
        # # Perform action group to reset position
        Running = True


#   Register the signal callback
signal.signal(signal.SIGTSTP, cv_stop)
signal.signal(signal.SIGCONT, cv_continue)


# The color dictionary used to identify
color_dist = {'red': {'Lower': np.array([0, 50, 50]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'cyan': {'Lower': np.array([35, 43, 46]), 'Upper': np.array([77, 255, 255])},
              'black': {'Lower': np.array([0, 0, 0]), 'Upper': np.array([180, 255, 95])},
              }


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
                    jpg = bytes[a:b + 2]  # Take image data
                    bytes = bytes[b + 2:]  # Delete the data that has been taken
                    orgFrame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)  # Decode the image
                    orgFrame = cv2.resize(orgFrame, (480, 360), interpolation=cv2.INTER_LINEAR)  # Scale the image to
                    get_image_ok = True
            except Exception as e:
                print(e)
                continue
        else:
            time.sleep(0.01)


# Display image thread
th1 = threading.Thread(target=get_image)
th1.setDaemon(True)     #et the background thread, which defaults is "False", and if is set to "True", the thread doesn't have to wait for the sub-threads
th1.start()


def get_x(img):
    '''
    The center coordinate X of the color block in the image
    :param img:
    :return:
    '''
    x = 0
    # Gaussian blur
    gs_frame = cv2.GaussianBlur(img, (5, 5), 0)
    # Convert colour space
    hsv = cv2.cvtColor(gs_frame, cv2.COLOR_BGR2HSV)
    # View the color
    mask = cv2.inRange(hsv, color_dist['black']['Lower'], color_dist['black']['Upper'])
    # erosion
    mask = cv2.erode(mask, None, iterations=2)
    # Expansion
    mask = cv2.dilate(mask, None, iterations=2)
    # View the contour
    # cv2.imshow('mask', mask)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cnts):
        c = max(cnts, key=cv2.contourArea)  # Find the largest area
        area = cv2.contourArea(c)
        # Gets the smallers enclosing rectangle
        rect = cv2.minAreaRect(c)
        if area >= 500:
            xy = rect[0]
            xy = int(xy[0]), int(xy[1])
            cv2.circle(img, (xy[0], xy[1]), 3, (0, 255, 0), -1)
            x = xy[0]
            box = cv2.cv.BoxPoints(rect)
            # Data type conversion
            box = np.int0(box)
            # Contour drawing
            cv2.drawContours(img, [box], 0, (0, 255, 255), 1)
    return x


def line():
    global cv_ok
    global deflection_angle
    global line_count, line_flag
    global last_turn
    global line_out
    while True:
        if cv_ok:
            if -20 <= deflection_angle <= 20:
                SSR.running_action_group('41', 1)
                print("ST")
            else:
                hexapod.turn(deflection_angle / 15, 150)
                time.sleep(0.15)
            cv_ok = False
        else:
            if line_out:
                if last_turn == 'R':
                    print "last_turn"
                    hexapod.turn(5, 150)
                elif last_turn == 'L':
                    print "last_turn"
                    hexapod.turn(-5, 150)
                line_out = False
            else:
                time.sleep(0.05)


th2 = threading.Thread(target=line)
th2.setDaemon(True)     # he background thread, which defaults is "False", and if is set to "True", the thread doesn't have to wait for the sub-threads
th2.start()


def camera_pos_init():
    PWMServo.setServo(1, 1500, 200)
    time.sleep(0.2)
    PWMServo.setServo(2, 2000, 200)
    time.sleep(0.2)


# Temporary use
# Enable camera
# turn_left_right(-35)
if __name__ == '__main__':

    cv_continue(0, 0)
    SSR.running_action_group('25', 1)
    x_list = []
    line_center = 0.0
    camera_pos_init()
    while True:
        if orgFrame is not None and get_image_ok:
            t1 = cv2.getTickCount()
            f = orgFrame
            # Gets the size of the total image
            img_h, img_w = f.shape[:2]
            # cv2.imshow('f', f)
            up_frame = f[0:65, 0:480]
            center_frame = f[145:210, 0:480]
            down_frame = f[290:355, 0:480]

            up_x = get_x(up_frame)
            center_x = get_x(center_frame)
            down_x = get_x(down_frame)

            if down_x != 0:
                line_center = down_x
                # print('c_x', deflection_angle)
                if line_center >= 360:
                    last_turn = 'R'
                elif line_center <= 120:
                    last_turn = 'L'

                d_line = line_center - img_w / 2
                deflection_angle = d_line * angle_factor
                # print("offset", deflection_angle)
                cv_ok = True
            elif center_x != 0:
                line_center = center_x
                # print('d_x', deflection_angle)
                if line_center >= 360:
                    last_turn = 'R'
                elif line_center <= 120:
                    last_turn = 'L'

                d_line = line_center - img_w / 2
                deflection_angle = d_line * angle_factor
                # print("offset", deflection_angle)
                cv_ok = True
            elif up_x != 0 and down_x != 0:
                line_center = (up_x + down_x) / 2
                # print('ud_x', deflection_angle)
                d_line = line_center - img_w / 2
                deflection_angle = d_line * angle_factor
                # print("offset", deflection_angle)
                cv_ok = True
            elif up_x != 0:
                line_center = up_x
                if line_center >= 360:
                    last_turn = 'R'
                elif line_center <= 120:
                    last_turn = 'L'
                # print('u_x', deflection_angle)
                d_line = line_center - img_w / 2
                deflection_angle = d_line * angle_factor
                # print("offset", deflection_angle)
                cv_ok = True
            elif up_x == 0 and down_x == 0 and center_x == 0:
                line_out = True

            # Draw a cross in the center of the screen
            cv2.line(f, ((img_w / 2) - 20, (img_h / 2)), ((img_w / 2) + 20, (img_h / 2)), (255, 255, 0), 1)
            cv2.line(f, ((img_w / 2), (img_h / 2) - 20), ((img_w / 2), (img_h / 2) + 20), (255, 255, 0), 1)
            # cv2.namedWindow("cv_ball_frame", cv2.WINDOW_AUTOSIZE)
            # cv2.imshow('cv_ball_frame', f)
            cv2.waitKey(1)
            get_image_ok = False
            t2 = cv2.getTickCount()
            time_r = (t2 - t1) / cv2.getTickFrequency() * 1000
            # print("%sms" % time_r)
        else:
            time.sleep(0.01)

