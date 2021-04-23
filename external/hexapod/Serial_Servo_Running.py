#!/usr/bin/env python3
# encoding: utf-8
import time
import os
import sqlite3 as sql
import SerialServoCmd as ssc
import config_serial_servo
import threading
from hwax import HWAX

runningAction = False
stopRunning = False
stop = True

def serial_setServo(s_id, pos, s_time):
    if pos > 1000:
        pos = 1000
    elif pos < 0:
        pos = 0
    else:
        pass
    if s_time > 30000:
        s_time = 30000
    elif s_time < 10:
        s_time = 10
    ssc.serial_serro_wirte_cmd(s_id, ssc.LOBOT_SERVO_MOVE_TIME_WRITE, pos, s_time)

def setDeviation(servoId, d):
    '''
    Configure servo deviation
    :param servoId:
    :param d:
    :return:
    '''
    global runningAction
    if servoId < 1 or servoId > 16:
        return
    if d < -200 or d > 200:
        return
    if runningAction is False:
        config_serial_servo.serial_servo_set_deviation(servoId, d)
 
def stop_servo():
    for i in range(16):
        config_serial_servo.serial_servo_stop(i+1) 

def stop_action_group():
    '''
    Stop action group running
    :return: Empty
    '''
    global stopRunning
    global stop
    
    stopRunning = True
    while stop:
        pass

def write_data(data):
    out_file = open("/home/pi/human_code/share.txt", "w")
    out_file.write(str(data))
    out_file.close()    

def running_action_group(actnum, times):
    '''
    Threads run action groups
    :param actNum:Action group filename
    :param times:The times of running. when the number of times is 0, it means infinite loop. Call "stopActionGroup"  can stop it
    :return:无
    '''
    global stopRunning
    try:
        if not stopRunning:
            th = threading.Thread(target = run_ActionGroup, args=(actnum, times))
            th.setDaemon(True)
            th.start()           
    except Exception as e:
        print(e)   

def run_ActionGroup(actNum, times):
    '''
    Run the action group
    :param actNum:Action group filename
    :param times:The times of running. when the number of times is 0, it means infinite loop, which cannot be stopped
    :return:无
    '''
    global runningAction
    global stopRunning
    global stop
    
    if not stopRunning:
        stop = False
        write_data(stop)
        d6aNum = "/home/pi/human_code/ActionGroups/" + actNum + ".d6a"
        hwaxNum = "/home/pi/human_code/ActionGroups/" + actNum + ".hwax"

        if times == 0:#Classify the times of imcoming 
            times = 1
            state = False
        else:
            times = abs(times)
            state = True
        if os.path.exists(hwaxNum) is True:
            ssc.portWrite()
            hwax = HWAX(hwaxNum, ssc.serialHandle)
            hwax.reset()
            while times:
                if state:
                    times -= 1
                if stop is False:#Action group stop flag bit is not             
                    if runningAction is False:
                        runningAction = True                   
                        while True:
                            if stopRunning is True:
                                stop = True
                                write_data(stop)
                                runningAction = False                           
                                break
                            ret = hwax.next()
                            if ret is None:
                                runningAction = False
                                hwax.reset()
                                break
                    else:                        
                        break
                else:
                    stopRunning = False
                    break
                    
        elif os.path.exists(d6aNum) is True: # If the action group exists
            while times:
                if state:
                    times -= 1        
                if stop is False:#Action group stop flag bit is not   
                    ag = sql.connect(d6aNum)# Open the database actNum
                    cu = ag.cursor()# Defines a cursor
                    cu.execute("select * from ActionGroup") # Inquire
                    if runningAction is False:# None of action groups are running
                        runningAction = True
                        while True:
                            if stopRunning is True:                                
                                stop = True
                                write_data(stop)
                                runningAction = False
                                cu.close()# Close a database link
                                ag.close()# Close the cursor
                                break
                            act = cu.fetchone() # Return to the first item in the list, do it again, it will return to the second item
                            if act is not None:
                                for i in range(0, len(act)-2, 1):
                                    serial_setServo(i+1, act[2 + i], act[1])
                                time.sleep(float(act[1])/1000.0)
                            else:
                                runningAction = False
                                cu.close()
                                ag.close()
                                break
                    else:
                        stopRunning = False
                        break
                else:
                    stopRunning = False
                    break   
        else:
            runningAction = False
            print("The action group file could not be found")
    stop = True
    write_data(stop) 
    stopRunning = False 

if __name__ == '__main__':
    running_action_group('1', 10)
    time.sleep(2)
    stop_action_group()
    runActionGroup('1', 10)
