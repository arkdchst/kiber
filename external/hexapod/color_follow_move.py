# -*- coding:UTF-8 -*-

import cv2
import PWMServo
import time
import threading
import urllib
import numpy as np
import Serial_Servo_Running as SSR
import hexapod


update_ok = False
img_w = 480
img_h = 360
ball_x = 0
angle_factor = 0.167
orgFrame = None
stream = None
bytes = ''
radius = 0
Get_Angle = False
angle = 0.0
Running = False
get_image_ok = False


def cv_stop():
    global Running

    print("Stop: CV Organism colour tracking")
    if Running is True:
        Running = False
    cv2.destroyWindow('cv_ball_frame')
    cv2.destroyAllWindows()


def cv_continue():
    global stream
    global Running
    print(' CV Organism colour tracking')
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
                    bytes = bytes[b + 2:]  # Remove the data that has been taken out
                    orgFrame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)  # 对图片进行解码
                    orgFrame = cv2.resize(orgFrame, (480, 360), interpolation=cv2.INTER_LINEAR)  # 将图片缩放到
                    get_image_ok = True
            except Exception as e:
                print(e)
                continue
        else:
            time.sleep(0.01)


th1 = threading.Thread(target=get_image)
th1.setDaemon(True)     # Set the background thread, which defaults is "False", and when it set to "True", the main thread doesn't have to wait for the sub-threads
th1.start()


color_dist = {'red': {'Lower': np.array([0, 60, 60]), 'Upper': np.array([6, 255, 255])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'green': {'Lower': np.array([35, 43, 46]), 'Upper': np.array([77, 255, 255])},
              }


def follow():
    global ball_x
    global img_w
    global Get_Angle
    global radius
    while True:
        if Get_Angle:
            if ball_x < img_w/2 - 50 or ball_x > img_w/2 + 50:
                hexapod.turn(angle/6, 100)
                Get_Angle = False
            else:
                if 5 < radius <= 35:
                    SSR.running_action_group("41", 1)
                    print "ST"
                else:
                    print "STOP"
                    time.sleep(0.01)
        else:
            time.sleep(0.01)


th2 = threading.Thread(target=follow)
th2.setDaemon(True)     # Set the background thread, which defaults is "False", and when it set to "True", the main thread doesn't have to wait for the sub-threads
th2.start()


def cam_pos_init():
    PWMServo.setServo(1, 1500, 50)
    time.sleep(0.05)
    PWMServo.setServo(2, 1300, 50)
    time.sleep(0.05)


cam_pos_init()
hexapod.hexapod_init()
if __name__ == '__main__':
    cv_continue()
    while True:
        get_color = False
        if orgFrame is not None and get_image_ok:
            res = orgFrame
            hsv = cv2.cvtColor(res, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, color_dist['blue']['Lower'], color_dist['blue']['Upper'])
            mask = cv2.erode(mask, None, iterations=2)
            # Expand
            mask = cv2.dilate(mask, None, iterations=2)
            # Find the contour
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            if len(cnts) > 0:
                c = max(cnts, key=cv2.contourArea)
                # etermine the minimumcircumcircle origin coordinates x, y and radius
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                ball_x = int(x)

                cv2.circle(res, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(res, (int(x), int(y)), 5, (0, 255, 255), -1)

                if Get_Angle is False:
                    angle = (ball_x - img_w/2) * angle_factor
                    Get_Angle = True
                else:
                    Get_Angle = False

            cv2.line(res, ((img_w / 2) - 20, (img_h / 2)), ((img_w / 2) + 20, (img_h / 2)), (255, 255, 0), 1)
            cv2.line(res, ((img_w / 2), (img_h / 2) - 20), ((img_w / 2), (img_h / 2) + 20), (255, 255, 0), 1)
            # cv2.imshow('cv_ball_frame', res)

            get_image_ok = False
            cv2.waitKey(1)
        else:
            time.sleep(0.01)

