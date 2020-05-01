from Serial_Servo_Running import serial_setServo as set_servo
from math import *
from time import sleep

coxa = 43
femur = 75
tibia = 138


'''
 9  8  7 |2 5| 16 17 18
 6  5  4 |1 4| 13 14 15
 3  2  1 |0 3| 10 11 12
'''

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




def stepfun(t):
	t = t % 6
	if t >= 0 and t < 1:
		return (0, t)
	if t >= 1 and t < 2:
		return (t-1, 1)
	if t >= 2 and t < 3:
		return (1, 3-t)
	if t >= 3 and t < 6:
		return (2-t/3, 0)



class Leg:
	num = None

	xmin = None
	ymin = None
	xmax = None
	ymax = None

	z = None

	def __init__(self, num, xmin=-50, ymin=-100, xmax=50, ymax=-50, z = coxa + femur + 50):
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


