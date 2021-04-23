# -*- coding:UTF-8 -*-
import hcsr04
import time
import threading
import hexapod
import Serial_Servo_Running as SSR


distance_ok = False
distance = 0.0

GPIO_TRIG = 12   # The ultrasonic trig pin corresponding IO number
GPIO_ECHO = 16   # The ultrasonic echo pin corresponding IO number

sonar = hcsr04.Measurement(GPIO_TRIG, GPIO_ECHO)


def move():
    global distance
    global distance_ok
    while True:
        if distance_ok:
            if distance > 50.0:
                distance_ok = False
                SSR.running_action_group("41", 1)
            else:
                hexapod.turn(11.25, 100)
                hexapod.turn(11.25, 100)
                hexapod.turn(11.25, 100)
                # hexapod.turn(11.25, 100)
                distance_ok = False

        else:
            time.sleep(0.01)


th1 = threading.Thread(target=move)
th1.setDaemon(True)     # the background thread, which defaults is "False", and if is set to "True", the thread doesn't have to wait for the sub-threads
th1.start()


hexapod.hexapod_init()
hexapod.camera_pos_init()
if __name__ == '__main__':
    print "Ultrasonic obstacle avoidance"
    while True:
        if distance_ok is False:
            distance = sonar.distance_metric(sonar.raw_distance(2, 0.08))
            distance_ok = True
        else:
            time.sleep(0.01)
