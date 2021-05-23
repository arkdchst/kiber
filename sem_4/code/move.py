#!/usr/bin/env python3
from math import *
from time import sleep
import threading
import config_serial_servo as css
import Serial_Servo_Running as ssr

import ctypes
libss = ctypes.CDLL('libss.so')
libss.serial_setServo.argtypes=(ctypes.c_ubyte, ctypes.c_int, ctypes.c_int)

def set_servo(id, pos, time):
	time *= 1000
	time = int(time)
	pos = int(pos)

	libss.serial_setServo(id, pos, time)
	# print('set_servo(', id, pos, time, ')')


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

	def __init__(self, ids, middle_poss, half_pi_poss, coxa, femur, tibia, range_x, y, h, z):
		self.ids = ids # [coxa, femur, tibia]
		self.middle_poss = middle_poss
		self.half_pi_poss = half_pi_poss
		self.coxa = coxa; self.femur = femur; self.tibia = tibia
		self.range_x = range_x
		self.y = y
		self.h = h # step height
		self.z = z
		self.is_fore = False
		self.is_up = False


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

	def get_angles_up(self, x, y, z, h):
		(coxa_angle, femur_angle, tibia_angle) = self.get_angles(x, y, z)

		def mirror(tibia_angle):
			return -pi/2 - (femur_angle + tibia_angle - (-pi/2)) - femur_angle

		def get_new_tibia_angle(tibia_angle):
			return acos((self.femur * cos(femur_angle + tibia_angle + pi/2) - h) / self.femur) - femur_angle - pi/2
		
		if femur_angle + tibia_angle < -pi/2:
			new_tibia_angle = mirror(get_new_tibia_angle(mirror(tibia_angle)))
		else:
			new_tibia_angle = get_new_tibia_angle(tibia_angle)

		return (coxa_angle, femur_angle, new_tibia_angle)


	def step_fun(self, t): # траекторная функция фазы шага, 0<=t<=1
		return ((1 - cos(pi * t)) / 2, sin(pi * t))

	def back_fun(self, t): # траекторная функция опоры
		return (1 - t, 0)

	def set_servos(self, poss, time):
		for i in range(3): # выставление нужного положение трёх приводов
			set_servo(self.ids[i], poss[i], time)

	def angles_to_poss(self, angles):
		poss = [self.angle_to_pos(angles[i], self.middle_poss[i], self.half_pi_poss[i]) for i in range(3)]
		return poss

	def raw_to_angles(self, raw, up=False): # перевести ногу в точку raw
		if up:
			angles = self.get_angles_up(raw[0], raw[1], self.z, self.h)
		else:
			angles = self.get_angles(raw[0], raw[1], self.z)
		return angles

	def point_to_raw(self, point): # разнормировка 1D точки
		raw = (point * (self.range_x[1] - self.range_x[0]) + self.range_x[0], self.y)
		return raw


	def move(self, fore, up, time, init=False):
		if init:
			if fore: points = [1]
			else: points = [0]
		if not up and self.is_up == up and self.is_fore != fore:
			if fore: points = [0.5, 1]
			else: points = [0.5, 0]
		elif up:
			if fore: points = [1.1]
			else: points = [0.1]
		else:
			if fore: points = [1]
			else: points = [0]


		angles_seq = [list(self.raw_to_angles(self.point_to_raw(point), up)) for point in points]

		poss_seq = [self.angles_to_poss(angles) for angles in angles_seq]

		def move():
			for poss in poss_seq:
				self.set_servos(poss, time/len(poss_seq))
				sleep(time/len(poss_seq))

		thread = threading.Thread(target=move, daemon=True)
		thread.start()

		self.is_fore = fore
		self.is_up = up

		return thread


class Spider:

	# длины звеньев
	coxa = 43
	femur = 75
	tibia = 138

	leg_to_servo = {0:(1,2,3), 1:(4,5,6), 2:(7,8,9), 3:(10,11,12), 4:(13,14,15), 5:(16,17,18)} # номер ноги -> номера приводов
	middle_poss = {1: 300, 2: 461, 3: 689, 4: 500, 5: 449, 6: 696, 7: 678, 8: 453, 9: 692, 10: 681, 11: 548, 12: 316, 13:500, 14:550, 15:321, 16: 300, 17: 546, 18: 310}#значния средних положений для приводов
	half_pi_poss = {1: -85, 2: 86, 3: 1071, 4:130, 5:76, 6:1061, 7: 315, 8: 87, 9: 1064, 10: 1048, 11: 922, 12: -63, 13:872, 14:914, 15:-61, 16: 689, 17: 920, 18: -62}#положения pi/2



	def __init__(self):
		step_len = 65
		notside_centre = 50
		side_z = 130
		notside_z = 100
		y = -60
		h = 10
		self.ranges = {	0: ((-notside_centre-step_len, -notside_centre+step_len),	notside_z),
						1: ((-step_len,step_len),									side_z),
						2: ((notside_centre-step_len,notside_centre+step_len),		notside_z),
						3: ((-notside_centre-step_len, -notside_centre+step_len),	notside_z),
						4: ((-step_len, step_len),									side_z),
						5: ((notside_centre-step_len, notside_centre+step_len),		notside_z)
						}
		self.legs = [SpiderLeg(x, range_x=self.ranges[x][0], y=y, h=h, z=self.ranges[x][1]) for x in range(6)]


class SpiderLeg(Leg):
	def __init__(self, leg_id, range_x, y, h, z):
		self.leg_id = leg_id
		ids = Spider.leg_to_servo[leg_id]
		super().__init__(ids, [Spider.middle_poss[x] for x in ids], [Spider.half_pi_poss[x] for x in ids], Spider.coxa, Spider.femur, Spider.tibia, range_x, y, h, z)


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

		self.leg.set_point(point, self.time/self.accuracy)
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
