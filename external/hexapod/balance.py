#! usr/bin/env python
# -*- coding:UTF-8 -*-
import hexapod
import math
import time
import Wave_filter
import mpu6050

factor = 180 / math.pi
offset = None

offset_row = 0.0
offset_pit = 0.0
offset_m = 0.0


def balance(row, pit, speed):

    global offset_row
    global offset_pit
    global offset_m

    leg0 = [100.0, 100.0, -70.0]
    leg1 = [100.0, 100.0, -70.0]
    leg2 = [100.0, 100.0, -70.0]
    leg3 = [100.0, 100.0, -70.0]
    leg4 = [100.0, 100.0, -70.0]
    leg5 = [100.0, 100.0, -70.0]

    L = 220.00
    W = 158.50
    MW = 266.90

# Avoid small range jitter
    if math.fabs(row) < 0.5:
        row = 0
    if math.fabs(pit) < 0.5:
        pit = 0

    row *= math.pi / 180
    pit *= math.pi / 180
# Calculate the position of each leg position at the input angle
    offset_m += MW * math.tan(row)
    offset_row += W * math.tan(row)
    offset_pit += L * math.tan(pit)

# Limit
    if math.fabs(offset_m) > 100 or math.fabs(offset_row + offset_pit) > 100 or math.fabs(offset_pit - offset_row) > 100:
        print 'fail'
        return

    leg5[2] = leg5[2] - offset_row - offset_pit
    leg4[2] = leg4[2] - offset_m
    leg3[2] = leg3[2] - offset_row + offset_pit
    leg2[2] = leg2[2] + offset_row - offset_pit
    leg1[2] = leg1[2] + offset_m
    leg0[2] = leg0[2] + offset_row + offset_pit

    hexapod.get_angle(5, leg5, speed)
    hexapod.get_angle(4, leg4, speed)
    hexapod.get_angle(3, leg3, speed)
    hexapod.get_angle(2, leg2, speed)
    hexapod.get_angle(1, leg1, speed)
    hexapod.get_angle(0, leg0, speed)
    time.sleep(speed * 0.001)


# Get the initial deviation of the sensor, measure 100 times, and take the average value
def get_offset():
    offset_ax = 0.0
    offset_ay = 0.0
    offset_az = 0.0
    offset_gx = 0.0
    offset_gy = 0.0
    offset_gz = 0.0
    global mpu
    for i in range(0, 100):
        a_date = mpu.get_accel_data(g=True)
        g_date = mpu.get_gyro_data()
        offset_ax += a_date['x']
        offset_ay += a_date['y']
        offset_az += a_date['z']
        offset_gx += g_date['x']
        offset_gy += g_date['y']
        offset_gz += g_date['z']
    return {'ax': offset_ax/100, 'ay': offset_ay/100, 'az': offset_az/100 - 1,
            'gx': offset_gx/100, 'gy': offset_gy/100, 'gz': offset_gz/100}


def get_gm(m):
    global mpu
    global gx
    global gy
    global gz
    global t
    # global dt
    global offset
    if m == 'x':
        gyro_date = mpu.get_gyro_data()
        gx += (gyro_date['x'] - offset['gx']) * (time.time() - t)
        t = time.time()
        return gx
    elif m == 'y':
        gyro_date = mpu.get_gyro_data()

        gy += (gyro_date['y'] - offset['gy']) * (time.time() - t)
        t = time.time()
        return gy
    elif m == 'z':
        gyro_date = mpu.get_gyro_data()
        gz += (gyro_date['z'] - offset['gz']) * (time.time() - t)
        t = time.time()
        return gz


# Run initialization. When performing this function, the hexapod robot body should place on the smooth place
def balance_init():
    global offset
    hexapod.camera_pos_init()  # Camera position initialization
    hexapod.hexapod_sit()  # The six legs of heaxpod robot should leave the ground and switch it to the sitting status, easy to measure deviation
    time.sleep(1)
    offset = get_offset()  # Obtain the deviation
    hexapod.hexapod_init()  # Ready to start
    time.sleep(1)


def rolling():
    balance(0.2094, 0.2094, 1000)
    time.sleep(1)
    R = 0.2443
    while 1:
        for i in range(0, 20):
            A = i * 0.314
            row = R * math.cos(A)
            pit = R * math.sin(A)
            balance(row, pit, 100)
            time.sleep(0.1)


mpu = mpu6050.mpu6050(0x68)
mpu.set_gyro_range(mpu.GYRO_RANGE_2000DEG)
mpu.set_accel_range(mpu.ACCEL_RANGE_2G)
last_ang_R = 0
last_ang_P = 0
if __name__ == '__main__':
    print "Body self-balance"
    balance_init()
    t = time.time()
    while True:
        accel_date = mpu.get_accel_data(g=True)
        gyro_date = mpu.get_gyro_data()

        ax = accel_date['x'] - offset['ax']
        ay = accel_date['y'] - offset['ay']
        az = accel_date['z'] - offset['az']
        gx = gyro_date['x'] - offset['gx']
        gy = gyro_date['y'] - offset['gy']

        angle_x = math.atan2(ax, az)
        angle_y = math.atan2(ay, az)

        angle_R = Wave_filter.filter_r(angle_x * factor, gy)
        angle_P = Wave_filter.filter_p(angle_y * factor, gx)
        # print angle_R, angle_P
        balance(angle_R, angle_P, 50)
        time.sleep(0.05)
