#!/usr/bin/env python3

import hcsr04
import Serial_Servo_Running as SSR
from time import time, sleep

sonar = hcsr04.Measurement(12, 16)

sample_size = 1
sample_wait = 0.01


count = 5

interval = 0.1

def check_values(values):
	# for value in values:
	# 	if value >= 100:
	# 		return False

	avg = sum(values)/len(values)

	ok_range = lambda x: x >= avg * 0.9 and x <= avg * 1.1

	for value in values:
		if not ok_range(value):
			return False

	return avg

while True:
	values1 = []
	for i in range(count):
		values1.append(sonar.distance_metric(sonar.raw_distance(sample_size, sample_wait)))
	time1 = time()

	avg1 = check_values(values1)
	if avg1 == False: continue

	sleep(interval)

	values2 = []
	for i in range(count):
		values2.append(sonar.distance_metric(sonar.raw_distance(sample_size, sample_wait)))
	time2 = time()

	avg2 = check_values(values2)
	if avg2 == False: continue

	velocity = -(avg2 - avg1)/(time2 - time1)
	if velocity < 35:
		continue

	print(velocity)
