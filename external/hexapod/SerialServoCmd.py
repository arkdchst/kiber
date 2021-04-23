#!/usr/bin/python
# encoding: utf-8
import serial
import pigpio
import time
import ctypes

LOBOT_SERVO_FRAME_HEADER         = 0x55
LOBOT_SERVO_MOVE_TIME_WRITE      = 1
LOBOT_SERVO_MOVE_TIME_READ       = 2
LOBOT_SERVO_MOVE_TIME_WAIT_WRITE = 7
LOBOT_SERVO_MOVE_TIME_WAIT_READ  = 8
LOBOT_SERVO_MOVE_START           = 11
LOBOT_SERVO_MOVE_STOP            = 12
LOBOT_SERVO_ID_WRITE             = 13
LOBOT_SERVO_ID_READ              = 14
LOBOT_SERVO_ANGLE_OFFSET_ADJUST  = 17
LOBOT_SERVO_ANGLE_OFFSET_WRITE   = 18
LOBOT_SERVO_ANGLE_OFFSET_READ    = 19
LOBOT_SERVO_ANGLE_LIMIT_WRITE    = 20
LOBOT_SERVO_ANGLE_LIMIT_READ     = 21
LOBOT_SERVO_VIN_LIMIT_WRITE      = 22
LOBOT_SERVO_VIN_LIMIT_READ       = 23
LOBOT_SERVO_TEMP_MAX_LIMIT_WRITE = 24
LOBOT_SERVO_TEMP_MAX_LIMIT_READ  = 25
LOBOT_SERVO_TEMP_READ            = 26
LOBOT_SERVO_VIN_READ             = 27
LOBOT_SERVO_POS_READ             = 28
LOBOT_SERVO_OR_MOTOR_MODE_WRITE  = 29
LOBOT_SERVO_OR_MOTOR_MODE_READ   = 30
LOBOT_SERVO_LOAD_OR_UNLOAD_WRITE = 31
LOBOT_SERVO_LOAD_OR_UNLOAD_READ  = 32
LOBOT_SERVO_LED_CTRL_WRITE       = 33
LOBOT_SERVO_LED_CTRL_READ        = 34
LOBOT_SERVO_LED_ERROR_WRITE      = 35
LOBOT_SERVO_LED_ERROR_READ       = 36

pi = pigpio.pi()  # Initialize the pigpio library
serialHandle = serial.Serial("/dev/ttyAMA0", 115200)  # Initialize serial port with 115200 baud rate


def portInit():  # Configure the IO port you already used
    pi.set_mode(17, pigpio.OUTPUT)  # Configure RX_CON and GPIO17 as the output
    pi.write(17, 0)
    pi.set_mode(27, pigpio.OUTPUT)  #Configure TX_CON and GPIO27 as the input
    pi.write(27, 1)


portInit()


def portWrite():  # Configure single line serial port to output
    pi.write(27, 1)  # Raise TX_CON and GPIO27
    pi.write(17, 0)  # Decrease RX_CON and GPIO17


def portRead():  # Configure single line serial port to input
    pi.write(17, 1)  # Raise RX_CON and GPIO17
    pi.write(27, 0)  # Decrease TX_CON and GPIO27


def portRest():
    time.sleep(0.1)
    serialHandle.close()
    pi.write(17, 1)
    pi.write(27, 1)
    serialHandle.open()
    time.sleep(0.1)


def checksum(buf):
    # Calculation and checking
    sum = 0x00
    for b in buf:  # Sum
        sum += b
    sum = sum - 0x55 - 0x55  # Remove two 0x55 at the beginning of the command
    sum = ~sum  # Obtain the opposite number
    return sum & 0xff


def serial_serro_wirte_cmd(id=None, w_cmd=None, dat1=None, dat2=None):
    '''
    Write the command
    :param id:
    :param w_cmd:
    :param dat1:
    :param dat2:
    :return:
    '''
    portWrite()
    buf = bytearray(b'\x55\x55')  # Frame head
    buf.append(id)
    # The length of command
    if dat1 is None and dat2 is None:
        buf.append(3)
    elif dat1 is not None and dat2 is None:
        buf.append(4)
    elif dat1 is not None and dat2 is not None:
        buf.append(7)

    buf.append(w_cmd)  # Command
    # Write the data
    if dat1 is None and dat2 is None:
        pass
    elif dat1 is not None and dat2 is None:
        buf.append(dat1 & 0xff)  # Deviation
    elif dat1 is not None and dat2 is not None:
        buf.extend([(0xff & dat1), (0xff & (dat1 >> 8))])  # Divide into the the low 8 bits and the high 8 bits and save them to cache
        buf.extend([(0xff & dat2), (0xff & (dat2 >> 8))])  # Divide into the the low 8 bits and the high 8 bits and save them to cache
    # Checksum
    buf.append(checksum(buf))
    # for i in buf:
    #     print('%x' %i)
    serialHandle.write(buf)  # Send


def serial_servo_read_cmd(id=None, r_cmd=None):
    '''
    Send the "read command" instruction
    :param id:
    :param r_cmd:
    :param dat:
    :return:
    '''
    portWrite()
    buf = bytearray(b'\x55\x55')  # Frame head
    buf.append(id)
    buf.append(3)  # The length of command
    buf.append(r_cmd)  # Command
    buf.append(checksum(buf))  # Checksum
    serialHandle.write(buf)  # Send
    time.sleep(0.00034)


def serial_servo_get_rmsg(cmd):
    '''
    # Gets the data specify for reading command
    :param cmd: Read the command
    :return: Data
    '''
    serialHandle.flushInput()  # Clear the receiving cache
    portRead()  # Configure the single line serial port to input
    time.sleep(0.005)  # Wait for the completion of reception
    count = serialHandle.inWaiting()    # Gets the number of bytes in the received cache
    if count != 0:  # If the received data is not blank
        recv_data = serialHandle.read(count)  # Read the received data
        # for i in recv_data:
        #     print('%#x' %ord(i))
        # Is it read ID command
        if recv_data[0] == 0x55 and recv_data[1] == 0x55 and recv_data[4] == cmd:
            # print 'ok'
            dat_len = recv_data[3]
            serialHandle.flushInput()  # Clear the received cache
            if dat_len == 4:
                # print ctypes.c_int8(ord(recv_data[5])).value    # Convert to the signed integer
                return recv_data[5]
            elif dat_len == 5:
                pos = 0xffff & (recv_data[5] | (0xff00 & ((recv_data[6]) << 8)))
                return ctypes.c_int16(pos).value
            elif dat_len == 7:
                pos1 = 0xffff & (recv_data[5] | (0xff00 & ((recv_data[6]) << 8)))
                pos2 = 0xffff & (recv_data[7] | (0xff00 & ((recv_data[8]) << 8)))
                return ctypes.c_int16(pos1).value, ctypes.c_int16(pos2).value
        else:
            return None
    else:
        serialHandle.flushInput()  # Clear the received cache

        return None
