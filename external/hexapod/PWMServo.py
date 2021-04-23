#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import pigpio
import time
from LeServo import PWM_Servo

Servos = ()
pi = None


def setServo(servoId, pos, time):
    if servoId < 1 or servoId > 2:
        return
    if pos > 2500:
        pos = 2500
    elif pos < 500:
        pos = 500
    if time > 30000:
        time = 30000
    elif time < 20:
        time = 20
    else:
        pass
    Servos[servoId - 1].setPosition(pos, time)


def setDeviation(servoId, d):
    if servoId < 1 or servoId > 2:
        return
    if d < -300 or d > 300:
        return
    Servos[servoId - 1].setDeviation(d)


def initLeArm(d):
    global Servos
    global pi
    pi = pigpio.pi()
    servo1 = PWM_Servo(pi, 5,  deviation=d[0], control_speed=True)  # On the expansion board 7
    servo2 = PWM_Servo(pi, 6, deviation=d[1], control_speed=True)   # 8
    Servos = (servo1, servo2)
    for i in Servos:
        i.setPosition(1500, 500)
    time.sleep(0.5)

# The rotation range of 9g servo is 0~180 °, and the corresponding PWM value is 500~2500

# Set the deviation
d = [100, 50]
# Initialize head part servo
initLeArm(d)
