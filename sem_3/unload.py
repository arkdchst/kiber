#!/usr/bin/env python3
import SerialServoCmd

for id in range(0, 18+1):
	SerialServoCmd.serial_serro_wirte_cmd(id, SerialServoCmd.LOBOT_SERVO_LOAD_OR_UNLOAD_WRITE, 0)

