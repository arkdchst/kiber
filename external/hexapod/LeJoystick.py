#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import pygame
import time
import os
from socket import *


HOST = "127.0.0.1"
PORT = 1065
client = None
js = None

key_map = {"PSB_CROSS": 2, "PSB_CIRCLE": 1, "PSB_SQUARE": 3, "PSB_TRIANGLE": 0,
           "PSB_L1": 4, "PSB_R1": 5, "PSB_L2": 6, "PSB_R2": 7,
           "PSB_SELECT": 8, "PSB_START": 9, "PSB_L3": 10, "PSB_R3": 11}
action_map = ["CROSS", "CIRCLE", "", "SQUARE", "TRIANGLE", "L1", "R1", "L2", "R2", "SELECT", "START", "", "L3", "R3"]


pygame.init()
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.display.init()
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    js = pygame.joystick.Joystick(0)
    js.init()
    jsName = js.get_name()
    print("Name of the joystick:", jsName)
    jsAxes = js.get_numaxes()
    print("Number of axis:", jsAxes)
    jsButtons = js.get_numbuttons()
    print("Number of buttons:", jsButtons)
    jsBall = js.get_numballs()
    print("Numbe of balls:", jsBall)
    jsHat = js.get_numhats()
    print("Number of hats:", jsHat)

pygame.joystick.init()
connected = False
cmd = ""
p_n_num = 0
p_n_flag = False   # False for positive status, True for negative status and default  is positive status
p_n_one = False    # Switching has completed
p_n_key_on = False  # The sign is pressed for the first time


def control_code():
    '''
    Servo control function
    :return:
    '''
    global cmd
    global client
    global p_n_num
    global p_n_flag
    global p_n_one
    global p_n_key_on
    if js.get_button(key_map["PSB_SELECT"]):  # The positive and negative status switching
        time.sleep(0.5)
        if js.get_button(key_map["PSB_SELECT"]):  # The positive and negative status switching
            p_n_flag = not p_n_flag
            p_n_one = False
            p_n_key_on = True
    if p_n_one is False and p_n_key_on:
        if p_n_flag:     # negative status
            p_n_num = 15
            cmd = "I003-" + str(30) + "-1\r\n"  # The positive status switch to the negative status
            client.send(cmd.encode())
        else:            # positive status
            p_n_num = 0
            cmd = "I003-" + str(31) + "-1\r\n"  # The negative status switch to the positive status
            client.send(cmd.encode())
        p_n_one = True
    if js.get_button(key_map["PSB_R1"]):  # R1
        if p_n_flag is False:
            cmd = "I003-" + "rotate" + "-1\r\n"  # Dancing
            client.send(cmd.encode())
        # print 'R1'
    if js.get_button(key_map["PSB_R2"]):  # R2
        if p_n_flag is False:
            cmd = "I003-" + str(37) + "-1\r\n"  # Push-ups
            client.send(cmd.encode())
        # print 'R2'
    if js.get_button(key_map["PSB_SQUARE"]):  # 口
        # print '口'
        cmd = "I003-" + str(11 + p_n_num) + "-1\r\n"  # Move to the right
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_CIRCLE"]):  # ○
        # print 'O'
        cmd = "I003-" + str(12 + p_n_num) + "-1\r\n"  # Move to the left
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_TRIANGLE"]):  # △
        # print '△'
        cmd = "I003-" + str(13 + p_n_num) + "-1\r\n"  # Go forward
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_CROSS"]):  # X
        # print 'X'
        cmd = "I003-" + str(14 + p_n_num) + "-1\r\n"  # Go backward
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_L1"]):
        print 'L1'
        print p_n_flag
        if p_n_flag is False:
            cmd = "I003-" + "wag_tail" + "-1\r\n"  # Wagged its tail
            client.send(cmd.encode())
    if js.get_button(key_map["PSB_L2"]):
        print 'L2'
        print p_n_flag
        if p_n_flag is False:
            cmd = "I003-" + "sit_down" + "-1\r\n"  # Sit down
            client.send(cmd.encode())

    # Up, down, left and right buton
    hat = js.get_hat(0)
    if hat[0] > 0:
        # print 'Button _ right'
        cmd = "I003-" + str(9 + p_n_num) + "-1\r\n"  # Turn right with small steps
        client.send(cmd.encode())
    elif hat[0] < 0:
        # print 'Button _ left'
        cmd = "I003-" + str(7 + p_n_num) + "-1\r\n"  # Turn left with small steps
        client.send(cmd.encode())
    else:
        pass
    if hat[1] > 0:
        # print 'Button _ up'
        cmd = "I003-" + str(1 + p_n_num) + "-1\r\n"    # Go forward with small step
        client.send(cmd.encode())
    elif hat[1] < 0:
        # print 'Button _ down'
        cmd = "I003-" + str(4 + p_n_num) + "-1\r\n"    # Go backward with small step
        client.send(cmd.encode())
    else:
        pass
    # The left side joystick
    lx = js.get_axis(0)
    ly = js.get_axis(1)
    # The right side joystick
    rx = js.get_axis(2)
    ry = js.get_axis(3)
    if lx > 0.5:
        print 'lx: right'
        cmd = "I003-" + str(9 + p_n_num) + "-1\r\n"  # Turn right with small steps

        client.send(cmd.encode())
    elif lx < -0.5:
        print 'lx: left'
        cmd = "I003-" + str(7 + p_n_num) + "-1\r\n"  # Turn left with small steps
        client.send(cmd.encode())
    else:
        pass

    if ly > 0.5:
        print 'lx: down'
        cmd = "I003-" + str(5 + p_n_num) + "-1\r\n"  # Go forward with medium step
        client.send(cmd.encode())
    elif ly < -0.5:
        print 'lx: up'
        cmd = "I003-" + str(2 + p_n_num) + "-1\r\n"  # Go backward with medium step
        client.send(cmd.encode())
    else:
        pass
    if rx > 0.5:
        print 'rx: right'
        cmd = "I003-" + str(10 + p_n_num) + "-1\r\n"  # Turn right with big steps
        client.send(cmd.encode())
    elif rx < -0.5:
        print 'rx: left'
        cmd = "I003-" + str(8 + p_n_num) + "-1\r\n"  # Turn left with big steps
        client.send(cmd.encode())
    else:
        pass
    if ry > 0.5:
        print 'rx: down'
        cmd = "I003-" + str(6 + p_n_num) + "-1\r\n"  # Go forward with big step
        client.send(cmd.encode())
    elif ry < -0.5:
        print 'rx: up'
        cmd = "I003-" + str(3 + p_n_num) + "-1\r\n"  # Go backward with big step
        client.send(cmd.encode())
    else:
        pass
    if js.get_button(key_map["PSB_START"]):  # Stand
        cmd = "I003-" + str(0 + p_n_num) + "-1\r\n"
        client.send(cmd.encode())
    cmd = ""


while True:
    if os.path.exists("/dev/input/js0") is True:
        if connected is False:
            pygame.joystick.quit()
            pygame.joystick.init()
            jscount = pygame.joystick.get_count()
            if jscount > 0:
                try:
                    js = pygame.joystick.Joystick(0)
                    js.init()
                    js.get_hat(0)
                    client = socket(AF_INET, SOCK_STREAM)   # Set up client
                    client.connect((HOST, PORT))    # Connect to the server terminal
                    connected = True
                except Exception as e:
                    print(e)
            else:
                pygame.joystick.quit()
        else:
            pass
    else:
        if connected is True:
            connected = False
            js.quit()
            pygame.joystick.quit()
            client.close()
        else:
            pass
    if connected is True:
        pygame.event.pump()
        try:
            control_code()
        except Exception as e:
            print(e)
            connected = False
            client.close()
    time.sleep(0.06)
