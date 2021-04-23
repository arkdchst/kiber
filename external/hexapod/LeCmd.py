# encoding: utf-8
import os
import LeActList
import threading
import Serial_Servo_Running
import time
import sys
import config_serial_servo


actdir = "/home/pi/hexapod/ActionGroups/"

Deviation = None
# # Calibrate action group
Calibration = (500, 500, 687, 500, 500, 687, 500, 500, 687, 500, 500, 313, 500, 500, 313, 500, 500, 313)


class LeError(Exception):
    def __init__(self, data=(), msg="LeError"):
        self.data = data
        self.msg = msg


def cmd_i000(par):  # Command 000    empty command
    pass


def cmd_i001(par):  # Command 001 servo movement
    if par[0] > 30000:  # Time limitation
        par[0] = 30000
    if par[0] < 20:
        par[0] = 20
    if not par[1] * 2 + 2 == len(par) or not len(par) >= 4:
        raise LeError(tuple(par), "1. The length of servo movement command error ")
    Servos = par[2:]
    for i in range(0, len(Servos), 2):
        if Servos[i] > 18 or Servos[i] < 1 or Servos[i+1] > 1000 or Servos[i+1] < 0:
            raise LeError((Servos[i], Servos[i+1]), "Servo movement parameter error")
        # A serial port servo
        Serial_Servo_Running.serial_setServo(Servos[i], Servos[i + 1], par[0])


def cmd_i002(par):  # Command 002   stop moving
    Serial_Servo_Running.stop_action_group()


def cmd_i003(sock, data=["", ""]):  # Command 003  runs the action group
    if (not len(data) == 2) or (not data) or (not data[0]) or (not data[1]) :
        raise LeError(tuple(data), "Running action group command error")
    par = None
    try:
        par = int(data[1])
    except:
        raise LeError((data[1],), "The number of running action group error")
    print(data[0])
    print(par)
    if not par is None:
        try:
            threading.Thread(target=Serial_Servo_Running.running_action_group, args=(data[0], par)).start()
            # LeArm.runActionGroup(data[0], par)
        except Exception, e:
            print(e)
        # LeArm.runActionGroup(data[0], par)


def cmd_i004(sock, data=[]):  # Command 004   check the action group
    actList = LeActList.listActions(actdir)
    actList.sort()
    if not len(actList) is 0:
        
        for i in range(0, len(actList), 10):
            str_head = "I004-" + str(len(actList))
            str_tial = "-" + str(i+1) + "-"
            str_tial1 = ""
            t = 10
            for j in range(0, 10, 1):
                if i+j < len(actList):
                    str_tial1 += "-" + actList[i+j][:-4]
                else:
                    if t == 10:
                        t = j
            if str_tial1:
                str_head = str_head + str_tial + str(i+t) + str_tial1 + "\r\n"
                sock.sendall(str_head)
    else:
        s = "I004-0-0-0\r\n"
        sock.sendall(s)

    print(len(actList))
    print(actList)


def cmd_i005(sock, data=[]):  # Command 005   delete an action group
    if data:
        for d in data:
            if d:
                os.remove(actdir + d + ".d6a")


def cmd_i006(sock, data=[]):  # Command 006  delete all the action group
    actList = LeActList.listActions(actdir)
    for d in actList:
        os.remove(actdir + d)


def cmd_i007(sock, data=[]):    # Handle control
    try:
        time = int(data[0])
        servo_num = int(data[1])
        # print(time,servo_num)
        servo_data = []
        for i in range(servo_num):
            servo_id = int(data[2 + i * 2])
            servo_pos = int(data[3 + i * 2])
            servo_data.append((servo_id, servo_pos-10000))
        # print(servo_data)
    except:
        raise LeError(tuple(data), "canshucuowu")
    try:
        for d in servo_data:
            Serial_Servo_Running.serial_setServo(d[0], d[1], time)
            time.sleep(0.5)
    except Exception as e:
        print(e)


def read_deviation():
    # Read internal deviation of servo
    d = []
    for i in range(1, 19, 1):
        zf_d = config_serial_servo.serial_servo_read_deviation(i)
        if zf_d > 127:  # Negative number
            zf_d = -(0xff - (zf_d - 1))
        d.append(zf_d)
    return d


def cmd_i008(sock, data=[]):      # Modify the deviation
    # 1、Read the P value of servo interface
    if not 36 == len(data):
        raise LeError(tuple(data), "1、The length of servo movement command error")
    Servos = data[:]
    j = 0
    upper_d = []    # The servo value on the interface
    for i in range(0, len(Servos), 2):
        j += 1
        upper_d.append(int(Servos[i+1]))
    ########################################################
    if not len(Calibration) == 18 and not len(upper_d) == 18:
        print("The number of deviation error")
        s = "I008-dev-no\r\n"
        sock.sendall(s)
        sys.exit()
    else:
        new_d = []
        for i in range(0, len(upper_d), 1):
            if -125 > (upper_d[i] - Calibration[i]) > 125:
                print("The deviation value is out of range-125~125")
                s = "I008-dev-error-range\r\n"
                sock.sendall(s)
                sys.exit()
            else:
                # Interface value - calibration value
                new_d.append(upper_d[i] - Calibration[i])
    # Configure the deviation
    for i in range(0, len(new_d), 1):
        Serial_Servo_Running.setDeviation(i+1, new_d[i])
        time.sleep(0.1)
    s = "I008-dev-ok\r\n"
    sock.sendall(s)     # Send the modification deviation successfully


def cmd_i009(sock, data=[]):  # Read internal deviation of servo
    global Deviation
    # 1、Read internal deviation of servo
    Deviation = read_deviation()
    # 2、Clear internal deviation of servo
    for i in range(0, 18, 1):
        Serial_Servo_Running.setDeviation(i+1, 0)
        time.sleep(0.05)
    # 3、Calculate calibration value + deviation value, generate character string command
    str_head = "I009-"
    str_head += str(len(Deviation))
    str_tial = ''
    for i in range(0, len(Deviation), 1):
        str_tial += "-" + str(i+1) + "-" + str(Calibration[i] + Deviation[i])
    str_head += str_tial
    print str_head
    # 4、Send data to PC software
    sock.sendall(str_head)


cmd_list = [cmd_i000, cmd_i001, cmd_i002, cmd_i003, cmd_i004, cmd_i005, cmd_i006,
            cmd_i007, cmd_i008, cmd_i009]


if __name__ == '__main__':
    read_deviation()

