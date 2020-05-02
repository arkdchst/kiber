from Serial_Servo_Running import serial_setServo as set_servo
from math import *
from time import sleep

coxa = 43
femur = 75
tibia = 138


num_to_ids = {0:(1,2,3), 2:(7,8,9), 3:(10,11,12), 5:(16,17,18)}
middle_pos = {1: 300, 2: 461, 3:689, 7: 678, 8: 453, 9: 692, 10: 681, 11: 548, 12: 316, 16: 300, 17: 546, 18: 310}
half_pi_pos = {1: -85, 2: 86, 3: 1071, 7: 315, 8: 87, 9: 1064, 10: 1048, 11: 922, 12: -63, 16: 689, 17: 920, 18: -62}

def angle_to_pos(angle, id):
	pos = (angle / (pi / 2)) * (half_pi_pos[id] - middle_pos[id]) + middle_pos[id]
	return pos


def get_angles(x, y, z):
	coxa_angle = atan(x / z)
	if y >= 0:
		femur_angle = (pi)/(2)-asin(((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2+femur**2-tibia**2)/(2*femur*sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))+acos((sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2))/(sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))
	else:
		femur_angle = (pi)/(2)-asin(((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2+femur**2-tibia**2)/(2*femur*sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))-acos((sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2))/(sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))
	tibia_angle = asin(((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2+tibia**2-femur**2)/(2*tibia*sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2)))-acos((y)/(sqrt((x-coxa*sin(coxa_angle))**2+(z-coxa*cos(coxa_angle))**2+y**2))) - femur_angle
	return (coxa_angle, femur_angle, tibia_angle)



def step_fun(t):
	return ((1 - cos(pi * t)) / 2, sin(pi * t))

def back_fun(t):
	return (1 - t, 0)



class Leg:
	num = None
	xmin = None
	ymin = None
	xmax = None
	ymax = None
	z = None
	def __init__(self, num, xmin=-50, ymin=-100, xmax=50, ymax=-50, z = coxa + femur):
		self.num = num
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		self.z = z
	def set_point(self, point, z, time):
		angles = get_angles(point[0], point[1], z)
		for i in range(3):
			pos = angle_to_pos(angles[i], num_to_ids[self.num][i])
			set_servo(num_to_ids[self.num][i], int(pos), int(time))
	def set_point_norm(self, point, time):
		point = (point[0] * (self.xmax - self.xmin) + self.xmin, point[1] * (self.ymax - self.ymin) + self.ymin)
		self.set_point(point, self.z, time)



class Move:
	leg = None
	from_x = None
	to_x = None
	onAir = None
	height = None
	dt = None
	interval = None
	ready = False
	t = 0
	def __init__(self, leg, from_x, to_x, onAir, height, dt, interval, aSync = False):
		self.leg = leg
		self.from_x = from_x
		self.to_x = to_x
		self.onAir = onAir
		self.height = height
		self.dt = dt
		self.interval = interval
	def tick(self):
		if self.ready: return
		self.t += self.dt
		if self.t > 1: self.t = 1
		if self.onAir:
			point = step_fun(self.t)
		else:
			point = back_fun(self.t)
		point = (point[0] * (self.to_x - self.from_x) + self.from_x, point[1] * self.height)
		self.leg.set_point_norm(point, self.interval)
		if self.t == 1: self.ready = True



def move1():
	leg0 = Leg(0, -100, -100, 0, -25)
	leg2 = Leg(2, 0, -100, 100, -25)
	leg3 = Leg(3, -100, -100, 0, -25)
	leg5 = Leg(5, 0, -100, 100, -25)

	t1 = 0.1
	dt = 0.1

	while True:
		move=Move(leg0, 0, 1, True, 1, dt, t1 * 1000)
		while not move.ready: move.tick(); sleep(t1)
		move=Move(leg2, 0, 1, True, 1, dt, t1 * 1000)
		while not move.ready: move.tick(); sleep(t1)
		moves=[Move(leg0, 0.5, 1, False, 1, dt, t1 * 1000), Move(leg2, 0.5, 1, False, 1, dt, t1 * 1000), Move(leg3, 0, 0.5, False, 1, dt, t1 * 1000), Move(leg5, 0, 0.5, False, 1, dt, t1 * 1000)]
		while not moves[0].ready:
			for x in moves:
				x.tick()
			sleep(t1)
		move=Move(leg3, 0, 1, True, 1, dt, t1 * 1000)
		while not move.ready: move.tick(); sleep(t1)
		move=Move(leg5, 0, 1, True, 1, dt, t1 * 1000)
		while not move.ready: move.tick(); sleep(t1)
		moves=[Move(leg0, 0, 0.5, False, 1, dt, t1 * 1000), Move(leg2, 0, 0.5, False, 1, dt, t1 * 1000), Move(leg3, 0.5, 1, False, 1, dt, t1 * 1000), Move(leg5, 0.5, 1, False, 1, dt, t1 * 1000)]
		while not moves[0].ready:
			for x in moves:
				x.tick()
			sleep(t1)


def move2():
	dt1 = 30
	dt2 = 12
	leg0 = Leg(0, -100, -100, 0, -25)
	leg2 = Leg(2, -dt1, -100, 100-dt1, -25)
	leg3 = Leg(3, -100, -100, 0, -25)
	leg5 = Leg(5, -dt2, -100, 100-dt2, -25)

	t1 = 0.4
	dt = 0.3
	t2 = 0.3
	dt2 = 0.4

	while True:
		move1=Move(leg2, 0, 1, True, 1, dt, t1 * 1000)
		move2=Move(leg3, 0, 1, True, 1, dt, t1 * 1000)
		while not move1.ready: move1.tick(); move2.tick(); sleep(t1)
		moves=[Move(leg0, 0, 0.5, False, 1, dt2, t2 * 1000), Move(leg2, 0.5, 1, False, 1, dt2, t2 * 1000), Move(leg3, 0.5, 1, False, 1, dt2, t2 * 1000), Move(leg5, 0, 0.5, False, 1, dt2, t2 * 1000)]
		while not moves[0].ready:
			for x in moves:
				x.tick()
			sleep(t2)
		move1=Move(leg0, 0, 1, True, 1, dt, t1 * 1000)
		move2=Move(leg5, 0, 1, True, 1, dt, t1 * 1000)
		while not move1.ready: move1.tick(); move2.tick(); sleep(t1)
		moves=[Move(leg0, 0.5, 1, False, 1, dt2, t2 * 1000), Move(leg2, 0, 0.5, False, 1, dt2, t2 * 1000), Move(leg3, 0, 0.5, False, 1, dt2, t2 * 1000), Move(leg5, 0.5, 1, False, 1, dt2, t2 * 1000)]
		while not moves[0].ready:
			for x in moves:
				x.tick()
			sleep(t2)
