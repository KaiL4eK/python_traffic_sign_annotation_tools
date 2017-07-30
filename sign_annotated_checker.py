import cv2
import numpy as np
import os
from time import sleep

from PIL import Image
from PIL import ImageTk

python3_used = True
import sys
if sys.version_info[0] < 3:
	python3_used = False

if python3_used:
	import tkinter as tk
	import tkinter.filedialog as tkFileDialog
else:
	import Tkinter as tk
	import tkFileDialog



import argparse

parser = argparse.ArgumentParser(description='Process video with ANN')
parser.add_argument('root', action='store', help='Root of annotations')

args = parser.parse_args()

root = tk.Tk()

label_list_explanation 	= ['Stop', 'Pedestrian', 'Main road', 'Bus stop']
label_list 				= ['stop', 'pedestrian', 'main_road', 'bus_stop']
label_variables 		= [tk.IntVar() for label in label_list]


annotated_image_list = []

current_annotated_image 	= None
current_annotated_image_idx = 0

render_image_size 			= (640, 480)
slider_current_frame_idx 	= tk.DoubleVar()
image_widget				= None

def refresh_data():
	global image_widget

	image_to_show = np.copy(current_annotated_image.image)

	rgb_image_to_show = cv2.cvtColor(cv2.resize(image_to_show, render_image_size), cv2.COLOR_BGR2RGB)
	img_tk = ImageTk.PhotoImage(Image.fromarray(rgb_image_to_show))

	if image_widget is None:
		image_widget = tk.Label(image=img_tk)
		image_widget.image = img_tk

		image_widget.grid(row=1, column=0, padx=5, pady=5)
	else:
		image_widget.configure(image=img_tk)
		image_widget.image = img_tk

	# Zero checkboxes
	for i_var in label_variables:
		i_var.set(0)

	for label in current_annotated_image.label_list:
		if label in label_list:
			label_list_idx = label_list.index(label)
			label_variables[label_list_idx].set(1)


class AnnotatedImage:

	filename_temp = '%d-%d-%s-%s.png'

	module_delimiter        = '-'
	module_data_delimiter   = ','
	extension_delimiter     = '.'

	id_module_idx           = 0
	frame_number_module_idx = 1
	bbox_module_idx         = 2
	label_module_idx        = 3

	def __init__(self, filepath):
		self.filepath = filepath
		self.filename = os.path.basename(self.filepath)
		self.dirpath = os.path.dirname(self.filepath)

		if len(self.filename.split(self.extension_delimiter)) != 2:
			print('File extension not found: %s' % (self.filename))
			self.isInitialized = False

		info = self.filename.split(self.extension_delimiter)[0]
		module_list = info.split(self.module_delimiter)

		if len(module_list) != 4:
			print('Modules info broken: %s' % (self.filename))
			self.isInitialized = False

		self.id 			= int(module_list[self.id_module_idx])
		self.frame_idx 		= int(module_list[self.frame_number_module_idx])
		self.bbox_str 		= module_list[self.bbox_module_idx]
		self.label_list 	= module_list[self.label_module_idx].split(self.module_data_delimiter)
		self.image 			= cv2.imread(self.filepath)

		self.isInitialized = True

	def rename_image_file(self, label_list):
		new_filename = self.filename_temp % (self.id, self.frame_idx, self.bbox_str, ','.join(label_list))
		new_filepath = os.path.join(self.dirpath, new_filename)

		print('Replacing \n%s\nwith\n%s' % (self.filepath, new_filepath))
		os.rename(self.filepath, new_filepath)

		self.filepath = new_filepath
		self.filename = new_filename

	def remove_image_file(self):
		print('Removing %s' % self.filepath)
		os.remove(self.filepath)

def read_annot_images_in_root(root_dir):
	paths = (os.path.join(root, filename)
			for root, _, filenames in os.walk(root_dir)
			for filename in filenames if filename.endswith('.png'))

	for path in paths:

		annot_image = AnnotatedImage(path)
		if annot_image.isInitialized:
			annotated_image_list.append(annot_image)



def main():
	read_annot_images_in_root(args.root)

# Initialize GUI
	imageControlFrame = tk.Frame(root)
	imageControlFrame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

	def images_slider_cb(val):
		global current_annotated_image, current_annotated_image_idx

		current_annotated_image_idx = int(val)
		current_annotated_image = annotated_image_list[current_annotated_image_idx]

		refresh_data()

	def nextImage_cb():
		global current_annotated_image, current_annotated_image_idx

		current_annotated_image_idx = min( current_annotated_image_idx + 1, len(annotated_image_list) - 1 )
		slider_current_frame_idx.set(current_annotated_image_idx)
		current_annotated_image = annotated_image_list[current_annotated_image_idx]

		refresh_data()

	def prevImage_cb():
		global current_annotated_image, current_annotated_image_idx

		current_annotated_image_idx = max( current_annotated_image_idx - 1, 0 )
		slider_current_frame_idx.set(current_annotated_image_idx)
		current_annotated_image = annotated_image_list[current_annotated_image_idx]

		refresh_data()
	
	tk.Button(imageControlFrame, text='Next ->', command=nextImage_cb).pack(side=tk.RIGHT, padx=5, pady=5)
	tk.Button(imageControlFrame, text='<- Prev', command=prevImage_cb).pack(side=tk.LEFT, padx=5, pady=5)

	image_slider = tk.Scale(imageControlFrame, from_=0, to=len(annotated_image_list)-1, orient=tk.HORIZONTAL, command=images_slider_cb, variable=slider_current_frame_idx)
	image_slider.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


	def leftKey(event): prevImage_cb()
	def rightKey(event): nextImage_cb()

	root.bind('<Left>', leftKey)
	root.bind('<Right>', rightKey)

	ChkBoxControlFrame = tk.Frame(root)
	ChkBoxControlFrame.grid(row=0, column=1, rowspan=2)

	for i, label in enumerate(label_list_explanation): 
		tk.Checkbutton(ChkBoxControlFrame, text=label, variable=label_variables[i]).grid(row=i, column=0, sticky='w', padx=5, pady=5)

	BtnControlFrame = tk.Frame(ChkBoxControlFrame)
	BtnControlFrame.grid(row=len(label_list)+1, column=0)

	def save_label_btn_cb():
		new_label_list = (label_list[i] for i, l_val in enumerate(label_variables) if l_val.get() == 1)
		
		current_annotated_image.rename_image_file(new_label_list)

	def remove_label_btn_cb():
		global current_annotated_image, current_annotated_image_idx
		remove_image = annotated_image_list.pop(current_annotated_image_idx)
		image_slider.configure(to=len(annotated_image_list)-1)

		remove_image.remove_image_file()

		current_annotated_image_idx = min( current_annotated_image_idx, len(annotated_image_list) - 1 )
		current_annotated_image = annotated_image_list[current_annotated_image_idx]

		refresh_data()


	tk.Button(BtnControlFrame, text='Save',   command=save_label_btn_cb).grid(row=1, column=0, padx=5, pady=5)
	tk.Button(BtnControlFrame, text='Remove', command=remove_label_btn_cb).grid(row=2, column=0, padx=5, pady=5)

	root.resizable(0,0)
	root.mainloop()


if __name__ == '__main__':
	main()
