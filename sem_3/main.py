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
		time = 1
		accuracy = 2
		legs = self.spider.legs

		while True:
			for i in range(len(self.onair_list)):
				moves = []
				for leg in legs:
					move = Move(leg, self.pos_list[i][leg.leg_id], leg.step_fun if self.onair_list[i] else leg.back_fun, accuracy, time)
					moves.append(move)
				task = Task(moves)
				task.autotick(time / accuracy)



if __name__ == '__main__':
	Main()