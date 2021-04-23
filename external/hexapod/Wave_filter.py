#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

K1 = 0.15
angle_R = 0.0
angle_P = 0.0
rt = pt = time.time()
dt = 0.01


def filter_r(angle_m, gyro_m):
    '''
    filter_r: first order complementary filtering for roll
    angle_m: the angle obtained by the accelerometer is the angle of the X-axis
    gyro_m: angular velocity obtained by gyroscope is the value of the Y-axis gyroscope
    '''
    global angle_R
    global K1
    global dt
    angle_R = K1 * angle_m + (1 - K1) * (angle_R + gyro_m * dt)

    return angle_R


def filter_p(angle_m, gyro_m):
    '''
    filter_r: first order complementary filtering for roll
    angle_m: the angle obtained by the accelerometer is the angle of the Y-axis
     gyro_m: angular velocity obtained by gyroscope is the value of the X-axis gyroscope
    '''
    global angle_P
    global K1
    global dt
    angle_P = K1 * angle_m + (1 - K1) * (angle_P + gyro_m * dt)

    return angle_P

