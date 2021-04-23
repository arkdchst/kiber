#!/usr/bin/python
# -*- coding: UTF-8 -*-
import math
import SerialServoCmd as Servoctrl
import time
import PWMServo


# Enter the number of the leg and the coordinate of the foot end thereby controlling the movement of the leg
# leg:0~5
# Position array, store the coordinates of the foot end
# The speed of running this action group
def get_angle(leg, position, speed):
    angle = []
    output = []

    C = 44.60
    F = 75.00
    T = 126.50

    factor = 180 / math.pi / 0.24

    angle.append(math.atan(position[1]/position[0]))

    L = position[1] / math.sin(angle[0])

    temp = math.pow(position[2], 2) + pow(L - C, 2)

    ft = math.sqrt(temp)

    a = math.atan(position[2] / (L - C))

    b = math.acos((math.pow(F, 2) + math.pow(ft, 2) - math.pow(T, 2)) / (2 * F * ft))

    angle.append(a + b)

    angle.append(math.acos((math.pow(ft, 2) - math.pow(F, 2) - math.pow(T, 2)) / (2 * F * T)))

    if leg < 3:
        output.append(313 + angle[0] * factor)
        output.append(500 - angle[1] * factor)
        output.append(687 - angle[2] * factor - 5)
    else:
        output.append(687 - angle[0] * factor)
        output.append(500 + angle[1] * factor)
        output.append(313 + angle[2] * factor + 5)
    for i in range(1, 4):
        Servoctrl.serial_serro_wirte_cmd(leg * 3 + i, Servoctrl.LOBOT_SERVO_MOVE_TIME_WRITE, int(output[i - 1]), speed)


# Standing status
def hexapod_init():
    get_angle(0, [100.0, 100.0, -70.0], 1000)
    get_angle(1, [100.0, 100.0, -70.0], 1000)
    get_angle(2, [100.0, 100.0, -70.0], 1000)
    get_angle(3, [100.0, 100.0, -70.0], 1000)
    get_angle(4, [100.0, 100.0, -70.0], 1000)
    get_angle(5, [100.0, 100.0, -70.0], 1000)
    time.sleep(1)


def camera_pos_init():
    PWMServo.setServo(1, 1500, 100)
    time.sleep(0.1)
    PWMServo.setServo(2, 1500, 100)
    time.sleep(0.1)


# Sitting status
def hexapod_sit():
    get_angle(0, [100.0, 100.0, 20.0], 1000)
    get_angle(1, [100.0, 100.0, 20.0], 1000)
    get_angle(2, [100.0, 100.0, 20.0], 1000)
    get_angle(3, [100.0, 100.0, 20.0], 1000)
    get_angle(4, [100.0, 100.0, 20.0], 1000)
    get_angle(5, [100.0, 100.0, 20.0], 1000)
    time.sleep(1)


# angle:When it is positive, the foot rotates counterclockwise
#       When it is negative, the foot rotates clockwise
# leg：The code for each leg，0~5
def get_point(leg, angle):
    angle = angle * math.pi / 180   # Degree measure, radian measure
    R = 271.5
    RM = 232.5
    base_angle_FB = 0.9465
    base_angle_M = 0.7853

    if leg == 0:
        x = R * math.cos(base_angle_FB + angle) - 58.5
        y = R * math.sin(base_angle_FB + angle) - 120.0
    elif leg == 1:
        x = RM * math.cos(base_angle_M + angle) - 64.70
        y = RM * math.sin(base_angle_M + angle) - 64.70
    elif leg == 2:
        x = R * math.sin(base_angle_FB - angle) - 120.0
        y = R * math.cos(base_angle_FB - angle) - 58.5
    elif leg == 3:
        x = R * math.cos(base_angle_FB - angle) - 58.5
        y = R * math.sin(base_angle_FB - angle) - 120.0
    elif leg == 4:
        x = RM * math.cos(base_angle_M - angle) - 64.70
        y = RM * math.sin(base_angle_M - angle) - 64.70
    elif leg == 5:
        x = R * math.sin(base_angle_FB + angle) - 120.0
        y = R * math.cos(base_angle_FB + angle) - 58.5
    else:
        x = 100
        y = 100
    return [x, y, -70]


# angle：When it is positive, turn to the right
#        When it is negative, turn to the left
# The angle of complete turning period of rotation is Angle *2
# All the angle that you detect should be divided by 2 before you transfer
# Speed:  milliseconds that is used to complete rotation and the speed better not less than 100ms
def turn(angle, speed):
    lift = (100, 100, -40)
    if angle > 0:
        print('R')
    else:
        print('L')

    leg0 = get_point(0, angle)
    leg1 = get_point(1, -angle)
    leg2 = get_point(1, angle)
    leg3 = get_point(3, -angle)
    leg4 = get_point(4, angle)
    leg5 = get_point(5, -angle)

    get_angle(0, leg0, 2 * speed)
    get_angle(1, lift, speed)
    get_angle(2, leg2, 2 * speed)
    get_angle(3, lift, speed)
    get_angle(4, leg4, 2 * speed)
    get_angle(5, lift, speed)
    time.sleep(speed * 0.001)

    get_angle(1, leg1, speed)
    get_angle(3, leg3, speed)
    get_angle(5, leg5, speed)
    time.sleep(speed * 0.001)

    leg0 = get_point(0, -angle)
    leg1 = get_point(1, angle)
    leg2 = get_point(1, -angle)
    leg3 = get_point(3, angle)
    leg4 = get_point(4, -angle)
    leg5 = get_point(5, angle)

    get_angle(0, lift, speed)
    get_angle(1, leg1, 2 * speed)
    get_angle(2, lift, speed)
    get_angle(3, leg3, 2 * speed)
    get_angle(4, lift, speed)
    get_angle(5, leg5, 2 * speed)
    time.sleep(speed * 0.001)

    get_angle(0, leg0, speed)
    get_angle(2, leg2, speed)
    get_angle(4, leg4, speed)
    time.sleep(speed * 0.001)



if __name__ == '__main__':
    hexapod_init()
    time.sleep(1)
    turn(10, 200)
    turn(-10, 200)





