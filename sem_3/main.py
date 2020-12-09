#!/usr/bin/env python3
import move
from time import sleep

def wait(threads):
	for thread in threads: thread.join()

if __name__ == '__main__':
	s = move.Spider()

	l1 = [s.legs[0], s.legs[4], s.legs[2]]
	l2 = [s.legs[3], s.legs[1], s.legs[5]]

	k = 1.1
	for leg in s.legs[3:6]:
		leg.range_x = leg.range_x[0] * k, leg.range_x[1] * k


	threads = []
	for l in l1: threads.append(l.move(False, False, 1, init=True))
	for l in l2: threads.append(l.move(True, True, 1, init=True))
	for thread in threads: thread.join()

	step_len = s.ranges[0][0][1] - s.ranges[0][0][0]

	time = (step_len / 550) # * 0.9 # total time for one step
	uptime = time/12 # time to move leg up
	for _ in range(int(3000/step_len)):
		print(_)
		threads1 = []
		threads2 = []
		for l in l2: threads2.append(l.move(False, False, time))
		for l in l1: threads1.append(l.move(False, True, uptime))
		wait(threads1)

		threads1 = []
		for l in l1: threads1.append(l.move(True, True, time - uptime * 2))
		wait(threads1)

		threads1 = []
		for l in l1: threads1.append(l.move(True, False, uptime))
		wait(threads1)

		wait(threads2)

		l1, l2 = l2, l1
