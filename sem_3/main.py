#!/usr/bin/env python3
import gait
from move import *
from time import sleep

class Main:
	def __init__(self):
		self.onair_list, self.pos_list = gait.read_gait_data()

		self.spider = Spider()
		if len(self.spider.legs) != len(self.onair_list[0]):
			raise Exception()

		self.move()

	def move(self):
		time = 0.3
		accuracy = 2
		legs = self.spider.legs

		first_run = True
		while True:
			for i in range(len(self.onair_list)):
				moves = []
				for leg in legs:
					if first_run:
						move = Move(leg, self.pos_list[i][leg.leg_id], leg.step_fun if self.onair_list[i][leg.leg_id] else leg.back_fun, accuracy, 1)
					else:
						move = Move(leg, self.pos_list[i][leg.leg_id], leg.step_fun if self.onair_list[i][leg.leg_id] else leg.back_fun, accuracy, time)
					moves.append(move)
				task = Task(moves)
				if first_run:
					task.autotick(1 / accuracy)
					first_run = False
				else:
					task.autotick(time / accuracy)



if __name__ == '__main__':
	Main()