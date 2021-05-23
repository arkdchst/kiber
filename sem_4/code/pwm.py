#!/usr/bin/env python3
import pigpio
import time
from LeServo import PWM_Servo


pi = pigpio.pi()
servo = PWM_Servo(pi, 6)
servo.setPosition(1000)
time.sleep(5)
