#!/usr/bin/env python3
#UNCOMMENT from Serial_Servo_Running import serial_setServo as set_servo
from math import *
from time import sleep

#TMP
def set_servo(id, pos, time):
	print('set_servo(', id, pos, time, ')')


'''
            front
09 08 07 -|2 cam 5|- 16 17 18
06 05 04  |1     4|  13 14 15
03 02 01 -|0 rpi 3|- 10 11 12
^                ^
|                |
id приводов      num - номера ног
'''



class Leg:

	def angle_to_pos(self, angle, middle_pos, half_pi_pos): # принимает угол в радианах, возвращает позицию привода в диапазоне от 0 до 1000
		pos = (angle / (pi / 2)) * (half_pi_pos - middle_pos) + middle_pos
		return pos

	def get_angles(self, x, y, z): # принимает координаты точки в пространстве, возвращает углы поворота трёх приводов
		coxa = self.coxa ; femur = self.femur ; tibia = self.tibia

		coxa_angle = atan(x / z)
		if y >= 0:
			femur_angle = (pi)/(2)-asin(((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2+femur**2-tibia**2)/(2*femur*sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))+acos((sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2))/(sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))
		else:
			femur_angle = (pi)/(2)-asin(((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2+femur**2-tibia**2)/(2*femur*sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))-acos((sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2))/(sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))
		tibia_angle = asin(((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2+tibia**2-femur**2)/(2*tibia*sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))-acos((y)/(sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2))) - femur_angle
		return (coxa_angle, femur_angle, tibia_angle)

	def step_fun(self, t): # траекторная функция фазы шага, 0<=t<=1
		return ((1 - cos(pi * t)) / 2, sin(pi * t))

	def back_fun(self, t): # траекторная функция опоры
		return (1 - t, 0)


	def __init__(self, ids, middle_poss, half_pi_poss, coxa, femur, tibia, range_x, range_y, z):
		self.ids = ids
		self.middle_poss = middle_poss
		self.half_pi_poss = half_pi_poss
		self.coxa = coxa; self.femur = femur; self.tibia = tibia
		self.range_x = range_x; self.range_y = range_y
		self.z = z

	def set_point(self, point, time): # перевести ногу в точку point
		time *= 1000
		angles = self.get_angles(point[0], point[1], self.z)
		for i in range(3): # выставление нужного положение трёх приводов
			pos = self.angle_to_pos(angles[i], self.middle_poss[i], self.half_pi_poss[i])
			set_servo(self.ids[i], int(pos), int(time))

	def set_point_norm(self, point, time): # то же что и set_point, но координаты нормируются диапазоном [0;1]
		point = (point[0] * (self.range_x[1] - self.range_x[0]) + self.range_x[0], point[1] * (self.range_y[1] - self.range_y[0]) + self.range_y[0]) # разнормировка
		self.set_point(point, time)




class Spider:

	# длины звеньев
	coxa = 43
	femur = 75
	tibia = 138

	leg_to_servo = {0:(1,2,3), 1:(4,5,6), 2:(7,8,9), 3:(10,11,12), 4:(13,14,15), 5:(16,17,18)} # номер ноги -> номера приводов
	middle_poss = {1: 300, 2: 461, 3: 689, 4: 500, 5: 445, 6: 705, 7: 678, 8: 453, 9: 692, 10: 681, 11: 548, 12: 316, 13: 500, 14: 555, 15: 325, 16: 300, 17: 546, 18: 310} # значния средних положений для приводов
	half_pi_poss = {1: -85, 2: 86, 3: 1071, 4: 120, 5: 75, 6: 1090, 7: 315, 8: 87, 9: 1064, 10: 1048, 11: 922, 12: -63, 13: 875, 14: 930, 15: -67, 16: 689, 17: 920, 18: -62} # положения pi/2


	def __init__(self):
		self.legs = [SpiderLeg(x) for x in range(6)]


class SpiderLeg(Leg):
	def __init__(self, leg_id, range_x=(-50, 50), range_y=(-100, -50), z = Spider.coxa + Spider.femur):
		self.leg_id = leg_id
		ids = Spider.leg_to_servo[leg_id]
		super().__init__(ids, [Spider.middle_poss[x] for x in ids], [Spider.half_pi_poss[x] for x in ids], Spider.coxa, Spider.femur, Spider.tibia, range_x, range_y, z)


class Move:
	def __init__(self, leg, range_t, move_fun, accuracy, time):
		self.leg = leg
		self.range_t = range_t
		self.move_fun = move_fun
		self.accuracy = accuracy
		self.time = time

		self.i = 0
		self.ready = False

	def tick(self):
		if self.ready: return

		self.i += 1

		t = self.i * (self.range_t[1] - self.range_t[0]) / self.accuracy + self.range_t[0]
		point = self.move_fun(t)

		self.leg.set_point_norm(point, self.time/self.accuracy)
		if self.i == self.accuracy: self.ready = True

class Task:
	def __init__(self, moves):
		self.moves = moves

	def tick(self):
		for move in self.moves:
			move.tick()

	def autotick(self, interval):
		while not self.ready():
			self.tick()
			sleep(interval)

	def ready(self):
		for move in self.moves:
			if not move.ready: return False

		return True