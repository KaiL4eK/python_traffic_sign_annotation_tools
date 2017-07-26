#!/usr/bin/env python

import numpy as np
import os
from time import sleep

from PIL import Image
from PIL import ImageTk
import Tkinter as tk


import cv2

import json

import Tkconstants, tkFileDialog, tkSimpleDialog

import argparse

parser = argparse.ArgumentParser(description='Process video with ANN')
parser.add_argument('-d', '--debug', action='store_true', help='Debug (for development)')

args = parser.parse_args()

class DataLabel:
	def __init__(self, frame_idx=0, thresh_rect=None, category_mask=None):
		self.frame_idx 		= frame_idx
		self.thresh_rect 	= thresh_rect
		self.category_mask	= category_mask


class Point:
	def __init__(self, x=0.0, y=0.0, limit_size=None):
		self.x = x
		self.y = y

		if limit_size:
			self.x = max(self.x, 0)
			self.y = max(self.y, 0)

			self.x = min(self.x, limit_size[0] - 1)
			self.y = min(self.y, limit_size[1] - 1)

	def get_values(self):
		return (self.x, self.y)

class Rectangle:
  	def __init__ (self, ul = Point(), lr = Point()):
	    self.ul = ul
	    self.lr = lr

root = tk.Tk()

# Id, frame_id, pixel_bb, classes
filename_temp = '%d:%d:%s:%s.png'
last_inactive_file_id = 0

label_list_explanation 	= ['Stop', 'Pedestrian', 'Main road', 'Bus stop']
label_list 				= ['stop', 'pedestrian', 'main_road', 'bus_stop']
label_variables = [tk.IntVar() for label in label_list]

render_image_size = (640, 480)

slider_current_frame_idx = tk.DoubleVar()
current_frame_idx = 0
current_frame = None
full_size_frame = None
image_widget = None

##############################################################
# Mouse drawing on image

bounding_rect = None

def image_mouse_press_cb(event):
	global bounding_rect

	point = Point(x = event.x, y = event.y, limit_size = render_image_size)
	bounding_rect = Rectangle( ul = point, lr = point )
	refresh_image()

	# (x, y) = point.get_values()
	# print 'Clicked at', x, y

def image_mouse_move_cb(event):

	point = Point(x = event.x, y = event.y, limit_size = render_image_size)
	bounding_rect.lr = point
	refresh_image()

	# (x, y) = point.get_values()
	# print 'Move at', x, y

def image_mouse_release_cb(event):
	global bounding_rect

	point = Point(x = event.x, y = event.y, limit_size = render_image_size)
	bounding_rect.lr = point

	saving_label_window()

	bounding_rect = None
	refresh_image()

	# (x, y) = point.get_values()
	# print 'Release at', x, y


def saving_label_window():
	(ul_x, ul_y) = bounding_rect.ul.get_values()
	(lr_x, lr_y) = bounding_rect.lr.get_values()

	ul_x = float(ul_x) / render_image_size[0]
	lr_x = float(lr_x) / render_image_size[0]
	ul_y = float(ul_y) / render_image_size[1]
	lr_y = float(lr_y) / render_image_size[1]

	ul_fs_x = int(ul_x * full_size_frame.shape[1])
	lr_fs_x = int(lr_x * full_size_frame.shape[1])
	ul_fs_y = int(ul_y * full_size_frame.shape[0])
	lr_fs_y = int(lr_y * full_size_frame.shape[0])

	top = tk.Toplevel()
	top.title('Thresh image')

	thresh_image = full_size_frame[ul_fs_y:lr_fs_y, ul_fs_x:lr_fs_x]
	thresh_image_tk = cv2.cvtColor(thresh_image, cv2.COLOR_BGR2RGB)
	thresh_image_tk = cv2.resize(thresh_image_tk, (320, 240), interpolation = cv2.INTER_LINEAR)
	thresh_image_tk = ImageTk.PhotoImage(Image.fromarray(thresh_image_tk))
	thresh_image_widget = tk.Label(top, image=thresh_image_tk)
	thresh_image_widget.image = thresh_image_tk
	thresh_image_widget.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

	def save_label_btn_cb():
		global last_inactive_file_id

		filepath = filename_temp % (last_inactive_file_id, current_frame_idx, 
									','.join(str(i) for i in [ul_fs_x, ul_fs_y, lr_fs_x, lr_fs_y]), 
									','.join(label_list[i] for i, l_val in enumerate(label_variables) if l_val.get() == 1 ))
		last_inactive_file_id += 1

		cv2.imwrite( os.path.join(save_folder, filepath), thresh_image )
		print('Saved file: %s' % filepath)
		top.destroy()

	def cancel_label_btn_cb():
		top.destroy()

	ChkBoxControlFrame = tk.Frame(top)
	ChkBoxControlFrame.grid(row=0, column=4)

	for i, label in enumerate(label_list_explanation): 
		tk.Checkbutton(ChkBoxControlFrame, text=label, variable=label_variables[i]).grid(row=i, column=4, sticky='w', padx=5, pady=5)

	tk.Button(top, text='Ok', command=save_label_btn_cb).grid(row=1, column=0, columnspan=2, padx=5, pady=5)
	tk.Button(top, text='Cancel', command=cancel_label_btn_cb).grid(row=1, column=2, columnspan=2, padx=5, pady=5)


def refresh_image():
	global image_widget

	image_to_show = np.copy(current_frame)

	if bounding_rect:
		cv2.rectangle(image_to_show, bounding_rect.ul.get_values(), bounding_rect.lr.get_values(), color=(255, 0, 0), thickness=2)

	rgb_image_to_show = cv2.cvtColor(image_to_show, cv2.COLOR_BGR2RGB)
	img_tk = ImageTk.PhotoImage(Image.fromarray(rgb_image_to_show))

	if image_widget is None:
		image_widget = tk.Label(image=img_tk)
		image_widget.image = img_tk

		image_widget.grid(row=1, column=0, padx=5, pady=5)
		image_widget.bind('<Button-1>', image_mouse_press_cb)
		image_widget.bind('<B1-Motion>', image_mouse_move_cb)
		image_widget.bind('<ButtonRelease-1>', image_mouse_release_cb)
	else:
		# update the pannels
		image_widget.configure(image=img_tk)
		image_widget.image = img_tk

##############################################################

if args.debug:
	filepath = '/home/alexey/data/keras_traffic_NN/raw_data/CarRegister_Videos/EMER0007.MP4'
else:
	filepath = tkFileDialog.askopenfilename(initialdir = os.path.expanduser('~'), title = "Select file", filetypes = (("video files",("*.mp4", "*.MP4")),("all files","*.*")))

if not filepath:
	exit(1)

save_folder = filepath.split('.')[0] + '_annotation2'

print('Save folder: ' + save_folder)
if not os.path.exists(save_folder):
	os.makedirs(save_folder)

files = os.listdir(save_folder)
for file in files:
	current_id = int(file.split(':')[0])
	last_inactive_file_id = max(last_inactive_file_id, current_id + 1)

print('Last id: %d' % last_inactive_file_id)

##############################################################

def nextFrame_cb():
	global current_frame, current_frame_idx

	current_frame_idx = min( current_frame_idx + 1, frame_count - 1 )
	slider_current_frame_idx.set(current_frame_idx)
	current_frame = read_frame(cap)

	refresh_image()

def prevFrame_cb():
	global current_frame, current_frame_idx

	current_frame_idx = max( current_frame_idx - 1, 0 )
	slider_current_frame_idx.set(current_frame_idx)
	cap.set(cv2.CAP_PROP_POS_FRAMES, float(current_frame_idx))
	current_frame = read_frame(cap)
	refresh_image()

videoControlFrame = tk.Frame(root)
videoControlFrame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

tk.Button(videoControlFrame, text='Next ->', command=nextFrame_cb).pack(side=tk.RIGHT, padx=5, pady=5)
tk.Button(videoControlFrame, text='<- Prev', command=prevFrame_cb).pack(side=tk.LEFT, padx=5, pady=5)

command_executed = True

def leftKey(event): 
	global command_executed

	def execute_command():
		global command_executed
		command_executed = True
		prevFrame_cb()

	if command_executed:
		command_executed = False
		root.after(50, execute_command)	

def rightKey(event): nextFrame_cb()
root.bind('<Left>', leftKey)
root.bind('<Right>', rightKey)


##############################################################

print('Video file: ' + filepath) 

def read_frame(cap):
	global full_size_frame

	ret, new_frame = cap.read()
	if new_frame is not None:
		full_size_frame = new_frame
		read_frame = cv2.resize(new_frame, render_image_size, interpolation = cv2.INTER_LINEAR)
	else:
		print('Error: failed to read frame')
		read_frame = current_frame

	return read_frame

cap = cv2.VideoCapture(filepath)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

current_frame = read_frame(cap)
refresh_image()

def videoTrackbarControl_cb(val):
	global current_frame, current_frame_idx

	current_frame_idx = int(val)
	cap.set(cv2.CAP_PROP_POS_FRAMES, float(current_frame_idx))
	current_frame = read_frame(cap)
	# readLabelValues()
	refresh_image()

video_slider = tk.Scale(videoControlFrame, from_=0, to=frame_count-1, orient=tk.HORIZONTAL, command=videoTrackbarControl_cb, variable=slider_current_frame_idx)
video_slider.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

root.resizable(0,0)
root.mainloop()