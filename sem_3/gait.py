#!/usr/bin/env python3
# from move import *

def get_fill_len(list_, index):
	value = list_[index]

	left = get_fill_index(list_, index, -1)
		
	right = get_fill_index(list_, index, 1)

	if left <= right:
		return right - left + 1
	else:
		return right - (left - len(list_)) + 1

def get_fill_index(list_, start, inc):
	index = start
	while True:
		new_index = (index + inc) % len(list_)

		if list_[new_index] != list_[start]:
			break
		else:
			index = new_index

	return index


def get_pos_list(onair_list):
	if len(set(onair_list)) != 2:
		raise Exception()

	index = get_fill_index(onair_list, 0, -1)
	pos_list = [None] * len(onair_list)
	value = 0
	while not pos_list[index]:
		newvalue = value + 1/get_fill_len(onair_list, index)
		pos_list[index] = [value, newvalue]
		value = newvalue

		new_index = (index + 1) % len(onair_list)
		if onair_list[new_index] != onair_list[index]:
			value = 0

		index = new_index

	return pos_list

def check_lines(lines):
	if len(lines) == 0 or len(lines[0]) == 0: return False

	for line in lines:
		if len(line) != len(lines[0]): return False
		set_ = set(line)
		if len(set_) > 2: return False
		if not set_.issubset({'0','1'}): return False
	return True

def parse_onair_dict(str_):
	lines = str_.strip().split('\n')
	if not check_lines(lines):
		raise Exception('File format error')
	
	onair = {x:[] for x in range(len(lines[0]))}

	for line in lines:
		for key in range(len(line)):
			onair[key].append(line[key] == '1')

	return onair


def read_gait_data(filename = 'in.txt'):
	with open(filename) as f:
		str_ = f.read()
	onair_dict = parse_onair_dict(str_)

	pos_dict = {}
	for key in onair_dict:
		pos_dict[key] = get_pos_list(onair_dict[key])

	return transpose_dict(onair_dict), transpose_dict(pos_dict)

def transpose_dict(dict_):
	list_ = []
	for row_num in range(len(dict_[0])):
		row = {}
		for leg in dict_:
			row[leg] = dict_[leg][row_num]
		list_.append(row)
	return list_