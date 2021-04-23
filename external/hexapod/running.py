#! /usr/bin/env python
import time
import Serial_Servo_Running as SSR
import PWMServo

if __name__ == '__main__':
    # while True:
    #     print "Child Running"
    #     time.sleep(1)
    PWMServo.setServo(1, 1500, 200)


