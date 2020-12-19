#!/usr/bin/env python3
import config_serial_servo as css
import SerialServoCmd as ssc

from time import time
from time import sleep


# ssc.serial_serro_wirte_cmd(1, ssc.LOBOT_SERVO_LOAD_OR_UNLOAD_WRITE, 1)

target = 700
ssc.serial_serro_wirte_cmd(4, ssc.LOBOT_SERVO_MOVE_TIME_WRITE, target, 100)

sleep(0.01)

while True:
	pos = css.serial_servo_read_pos(4)
	print(time(), pos)

	if pos >= target * 0.95 and pos <= target * 1.05:
		break