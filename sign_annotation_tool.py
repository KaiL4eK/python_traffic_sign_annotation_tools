#!/usr/bin/env python

import numpy as np
import os

from Tkinter import *
from PIL import Image
from PIL import ImageTk
import cv2

import json

import Tkconstants, tkFileDialog

import argparse

parser = argparse.ArgumentParser(description='Process video with ANN')
# parser.add_argument('-w', '--weights', action='store',      help='Path to weights file')
parser.add_argument('-s', '--sliding_mode',    action='store_true', help='Don`t modify dump file')
parser.add_argument('-d', '--debug',    action='store_true', help='Debug (for development)')

args = parser.parse_args()

root = Tk()

label_list = ['stop', 'pedestrian', 'main road', 'bus']
label_variables = [IntVar() for label in label_list]
label_2_frame = None

render_image_size = (800, 600)

slider_current_frame_idx = DoubleVar()
current_frame_idx = 0
current_frame = None
image_widget = None

##############################################################

def loadAnnotation():
	global label_list, label_2_frame, label_variables

	load_data = None
	with open(dump_filepath, 'r') as infile:
		load_data = json.load(infile)

	label_list = load_data['label_list']
	label_variables = [IntVar() for label in label_list]
	label_2_frame = np.array(load_data['label_values'])
	#Reinitialize checkbox variables
	
	print('Dump successfully loaded')

def saveAnnotation():

	data = {}
	data['label_list'] = label_list
	data['label_values'] = label_2_frame.tolist()

	with open(dump_filepath, 'w') as outfile:
		json.dump(data, outfile)

	print('Dump successfully writed')

def space_cb(event): saveAnnotation()

root.bind("<space>", space_cb)

def writeLabelValues():

	for i, label in enumerate(label_list):
		label_2_frame[current_frame_idx][i] = label_variables[i].get()

		# print( label, 'is', label_variables[i].get() )

def readLabelValues():

	for i, label in enumerate(label_list):
		label_variables[i].set( str(label_2_frame[current_frame_idx][i]) )

def refresh_image():
	# grab a reference to the image panels
	global image_widget

	readLabelValues()

	image_to_show = current_frame
	rgb_image_to_show = cv2.cvtColor(image_to_show, cv2.COLOR_BGR2RGB)

	# convert the images to PIL format and then to ImageTk format
	img = ImageTk.PhotoImage(Image.fromarray(rgb_image_to_show))

	if image_widget is None:
		image_widget = Label(image=img)
		image_widget.image = img
		image_widget.grid(row=1, column=0, padx=5, pady=5)
	else:
		# update the pannels
		image_widget.configure(image=img)
		image_widget.image = img

##############################################################

def nextFrame_cb():
	global current_frame, current_frame_idx

	current_frame_idx = min( current_frame_idx + 1, frame_count - 1 )
	slider_current_frame_idx.set(current_frame_idx)
	current_frame = read_frame(cap)

	if not args.sliding_mode:
		writeLabelValues()

	refresh_image()

def prevFrame_cb():
	global current_frame, current_frame_idx

	current_frame_idx = max( current_frame_idx - 1, 0 )
	slider_current_frame_idx.set(current_frame_idx)
	cap.set(cv2.CAP_PROP_POS_FRAMES, float(current_frame_idx))
	current_frame = read_frame(cap)
	refresh_image()

videoControlFrame = Frame(root)
videoControlFrame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

Button(videoControlFrame, text='Next ->', command=nextFrame_cb).pack(side=RIGHT, padx=5, pady=5)
Button(videoControlFrame, text='<- Prev', command=prevFrame_cb).pack(side=LEFT, padx=5, pady=5)

def leftKey(event): prevFrame_cb()
def rightKey(event): nextFrame_cb()
root.bind('<Left>', leftKey)
root.bind('<Right>', rightKey)

##############################################################

if args.debug:
	filepath = '/home/alexey/data/keras_traffic_NN/raw_data/CarRegister_Videos/EMER0007.MP4'
else:
	filepath = tkFileDialog.askopenfilename(initialdir = os.path.expanduser('~'), title = "Select file", filetypes = (("video files","*.mp4"),("all files","*.*")))

dump_filepath = filepath.split('.')[0] + ".json"

if os.path.isfile(dump_filepath):
	print('Dump file is found: ' + dump_filepath)
	loadAnnotation()

##############################################################

controlFrame = Frame(root)
controlFrame.grid(row=0, column=1, rowspan=2)

ChkBoxControlFrame = Frame(controlFrame)
ChkBoxControlFrame.grid(row=0, column=0)


def labelCheckbox_cb():
	writeLabelValues()

for i, label in enumerate(label_list): 
	Checkbutton(ChkBoxControlFrame, text=label, variable=label_variables[i], command=labelCheckbox_cb).grid(row=i, column=0, sticky='w', pady=5)

##############################################################

print('Video file: ' + filepath) 

def read_frame(cap):
	ret, new_frame = cap.read()
	if new_frame is not None:
		read_frame = cv2.resize(new_frame, render_image_size, interpolation = cv2.INTER_LINEAR)
	else:
		print('Error: failed to read frame')
		read_frame = current_frame

	return read_frame

cap = cv2.VideoCapture(filepath)
frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT);

if label_2_frame is None or len(label_list) != label_2_frame.shape[1]:
	print('Initializing label array from scratch')
	label_2_frame = np.zeros((int(frame_count), len(label_list)), dtype=np.uint8)

current_frame = read_frame(cap)
refresh_image()

if args.sliding_mode:
	def videoTrackbarControl_cb(val):
		global current_frame, current_frame_idx

		current_frame_idx = int(val)
		cap.set(cv2.CAP_PROP_POS_FRAMES, float(current_frame_idx))
		current_frame = read_frame(cap)
		readLabelValues()
		refresh_image()

	video_slider = Scale(videoControlFrame, from_=0, to=frame_count, orient=HORIZONTAL, command=videoTrackbarControl_cb, variable=slider_current_frame_idx)
	video_slider.pack(side=RIGHT, fill=BOTH, expand=True)

root.resizable(0,0)
root.mainloop()