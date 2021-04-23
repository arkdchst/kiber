#!/usr/bin/python
# encoding: utf-8
# Set serial servo parameters
# Only one servo can be set at one time, and the raspberry PI extension board can only be connected to one servo, so you have to set the parameter of servos one by one

from SerialServoCmd import *


def serial_servo_set_id(oldid, newid):
    """
    Set the servo ID number, default number is 1
    :param oldid: Default ID number
    :param newid: New ID number
    """
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_ID_WRITE, newid)


def serial_servo_read_id(id=None):
    """
    Read serial servo ID 
    :param id: Don;t have default
    :return: reture to the servo id
    """
    while True:
        if id is None:  # There can only be oneservo on the bus
            serial_servo_read_cmd(0xfe, LOBOT_SERVO_ID_READ)
        else:
            serial_servo_read_cmd(id, LOBOT_SERVO_ID_READ)
        # Obtain content
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ID_READ)
        if msg is not None:
            return msg


def serial_servo_stop(id=None):
    '''
    Stop servo working
    :param id:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_MOVE_STOP)


def serial_servo_set_deviation(id, d=0):
    """
    Set the deviation, power down protection
    :param id: servo id
    :param d:  Deviation
    """
    # Set the deviation
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_ADJUST, d)
    # Set to the power down protection
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_WRITE)


def serial_servo_read_deviation(id):
    '''
    Read the deviation
    :param id: Servo ID number
    :return:
    '''
    # Send read deviation instruction
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_READ)
        # Obtain
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ANGLE_OFFSET_READ)
        if msg is not None:
            return msg


def serial_servo_set_angle_limit(id, low, high):
    '''
    Set the rotation range of the servo
    :param id:
    :param low:
    :param high:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_LIMIT_WRITE, low, high)


def serial_servo_read_angle_limit(id):
    '''
    Read the rotation range of the servo
    :param id:
    :return: Return to the tuples 0： Low  1： High
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_ANGLE_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ANGLE_LIMIT_READ)
        if msg is not None:
            return msg


def serial_servo_set_vin_limit(id, low, high):
    '''
    Set the rotation range of the servo
    :param id:
    :param low:
    :param high:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_VIN_LIMIT_WRITE, low, high)


def serial_servo_read_vin_limit(id):
    '''
    Read the rotation range of the servo
    :param id:
    :return: Return to the tuples 0： Low  1： High
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_VIN_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_VIN_LIMIT_READ)
        if msg is not None:
            return msg


def serial_servo_set_max_temp(id, m_temp):
    '''
    Set the temperature alarm of the servo
    :param id:
    :param m_temp:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_TEMP_MAX_LIMIT_WRITE, m_temp)


def serial_servo_read_temp_limit(id):
    '''
    Read the temperature alarm range of the servo
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_TEMP_MAX_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_TEMP_MAX_LIMIT_READ)
        if msg is not None:
            return msg


def serial_servo_read_pos(id):
    '''
    Read the current position of the servo
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_POS_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_POS_READ)
        if msg is not None:
            return msg


def serial_servo_read_temp(id):
    '''
    Read the temperature of the servo
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_TEMP_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_TEMP_READ)
        if msg is not None:
            return msg


def serial_servo_read_vin(id):
    '''
    Read the temperature of the servo
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_VIN_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_VIN_READ)
        if msg is not None:
            return msg


def serial_servo_rest_pos(oldid):
    # Clean the deviation and adjust the P value to middle （500）
    serial_servo_set_deviation(oldid, 0)    # Clean the deviation
    time.sleep(0.1)
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_MOVE_TIME_WRITE, 500, 100)    # adjust the P value to middle


def serial_servo_set_pos(oldid, pos, time):
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_MOVE_TIME_WRITE, pos, time)


def serial_servo_set_speed(oldid, speed):
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_OR_MOTOR_MODE_WRITE, 1, speed)


def serial_servo_set_servo_mode(oldid, mode):
    # 0 Servo model 1 Motor model
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_OR_MOTOR_MODE_WRITE, mode, 0)


def serial_servo_set_servo_load(oldid, mode):
    # 0 upload.  Manually rotate the servo After unloading.  1 load. Don;t rotate the servo
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_LOAD_OR_UNLOAD_WRITE, mode)


def show_servo_state():
    '''
    Display information
    :return:
    '''
    oldid = serial_servo_read_id()
    portRest()
    if oldid is not None:
        print('Current servo ID：%d' % oldid)
        pos = serial_servo_read_pos(oldid)
        print('Current servo angle：%d' % pos)
        portRest()

        now_temp = serial_servo_read_temp(oldid)
        print('Current servo temperture：%d°' % now_temp)
        portRest()

        now_vin = serial_servo_read_vin(oldid)
        print('Current voltage of the servo：%dmv' % now_vin)
        portRest()

        d = serial_servo_read_deviation(oldid)
        print('Current servo deviation：%d' % ctypes.c_int8(d).value)
        portRest()

        limit = serial_servo_read_angle_limit(oldid)
        print('The current controllable angle of the servo%d-%d' % (limit[0], limit[1]))
        portRest()

        vin = serial_servo_read_vin_limit(oldid)
        print('The current servo alarm voltage%dmv-%dmv' % (vin[0], vin[1]))
        portRest()

        temp = serial_servo_read_temp_limit(oldid)
        print('The current alarm temperature of servo is 50°-%d°' % temp)
        portRest()
    return oldid


if __name__ == '__main__':
    serial_servo_set_deviation(1, 100)
    # serial_servo_set_servo_load(1, 1)
    # serial_servo_set_speed(1, 0)
    # time.sleep(3)
    # portInit()
    # serial_servo_read_cmd(1, LOBOT_SERVO_LOAD_OR_UNLOAD_READ)
    # msg = serial_servo_get_rmsg(LOBOT_SERVO_LOAD_OR_UNLOAD_READ)
    # print(msg)
    # serial_servo_set_pos(1, 200, 100)

#     portInit()
#    oldid = show_servo_state()
#     while True:
#         print '*' * 50
#         print '1、Set servo ID'
#         print '2、Set servo deviation'
#         print '3、Set the rotation angle range of the servo'
#         print '4、Set theservo voltage alarm range'
#         print '5、Set the temperature alarm range of the servo'
#         print '6、Display servo status'
#         print '7、Medium servo'
#         print '8、Exit'
#         print '*' * 50
#         num = input('Please enter the number you want to configure')
#         num6_flag = 0
#         while 1 <= num <= 7:
#             if num == 1:
#                 num6_flag = 0
#                 n_id = input('Please enter the new servo ID number（Range：0-253）')
#                 if n_id > 253:
#                     print 'Exceed the range, please re-enter'
#                 else:
#                     serial_servo_set_id(oldid, n_id)
#                     portRest()
#                     if serial_servo_read_id() == n_id:
#                         # If it is not successed, repeat it
#                         oldid = n_id
#                         print 'Setting has completed'
#                         break
#             elif num == 2:
#                 num6_flag = 0
#                 n_d = input('请Please enter deviation value of servo（Range：-125 ~ 125）')
#                 if n_d < -125 or n_d > 125:
#                     print 'Exceed the range, please re-enter'
#                 else:
#                     serial_servo_set_deviation(oldid, n_d)
#                     time.sleep(0.1)
#                     portRest()
#                     zf_d = serial_servo_read_deviation(oldid)
#                     if zf_d > 127:  # the negative number
#                         zf_d = -(0xff - (zf_d - 1))
#                     if zf_d == n_d:
#                         print 'Setting has completed'
#                         break
#             elif num == 3:
#                 num6_flag = 0
#                 print 'Please enter the rotation range of the servo（0 ~ 1000）'
#                 low_ang_limit = input('Please enter the low range value')
#                 high_ang_limit = input('Please enter the high range value')
#                 if low_ang_limit < 0 or high_ang_limit < 0 or low_ang_limit >= 1000 or high_ang_limit > 1000:
#                     print 'Exceed the range, please re-enter'
#                 else:
#                     serial_servo_set_angle_limit(oldid, low_ang_limit, high_ang_limit)
#                     portRest()
#                     lim = serial_servo_read_angle_limit(oldid)
#                     if lim[0] == low_ang_limit and lim[1] == high_ang_limit:
#                         print 'Setting has completed '
#                         break
#             elif num == 4:
#                 num6_flag = 0
#                 print 'Please enter the voltage alarm range of the servo（4500 ~ 12000）mv'
#                 low_vin_limit = input('Please enter a low range value')
#                 high_vin_limit = input('Please enter a high range value')
#                 if low_vin_limit < 4500 or high_vin_limit < 4500 or low_vin_limit >= 12000 or high_vin_limit > 12000:
#                     print 'Exceed the range, please re-enter'
#                 else:
#                     serial_servo_set_vin_limit(oldid, low_vin_limit, high_vin_limit)
#                     portRest()
#                     vin = serial_servo_read_vin_limit(oldid)
#                     if vin[0] == low_vin_limit and vin[1] == high_vin_limit:
#                         print 'Setting has completed'
#                         break
#             if num == 5:
#                 num6_flag = 0
#                 n_temp = input('Please enter the temperature alarm range of the servo（range：50-100）degress')
#                 if n_temp > 100 or n_temp < 50:
#                     print 'Exceed the range, please re-enter'
#                 else:
#                     serial_servo_set_max_temp(oldid, n_temp)
#                     portRest()
#                     if serial_servo_read_temp_limit(oldid) == n_temp:
#                         # Repeat it, if the setting is not completed
#                         print 'Setting has completed'
#                         break
#             elif num == 6:
#                 if num6_flag == 0:
#                     oldid = show_servo_state()
#                     num6_flag = 1
#                 break
#             elif num == 7:
#                 num6_flag = 0
#                 serial_servo_rest_pos(oldid)
#                 print 'Median setting has completed'
#                 break
#         if num == 8:
#             break
#         elif num < 1 or num > 8:
#             print 'Enter error, please re-enter'
    # serial_servo_set_id(9, 20)
    # portRest()

    # serial_servo_set_deviation(20, 45)
    # portRest()
    # serial_servo_read_deviation(20)
    # time.sleep(1)



