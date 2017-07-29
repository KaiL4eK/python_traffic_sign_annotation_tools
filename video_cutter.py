#!/usr/bin/env python3

import cv2
import os
import argparse

parser = argparse.ArgumentParser(description='Process video by hands to get nagatives')
parser.add_argument('filepath', action='store', help='Path to video file to process')

args = parser.parse_args()

try:
    xrange
except NameError:
    xrange = range

def main():
	print('Open file to read: ' + args.filepath)

	cap = cv2.VideoCapture(args.filepath)
	if not cap.isOpened():
		print('Failed to open video')
		exit(1)

	file_basename = os.path.basename(args.filepath.split('.')[0])
	save_folder = args.filepath.split('.')[0] + '_frames_1_10'

	print('Saving to: ' + save_folder)
	if not os.path.exists(save_folder):
		os.makedirs(save_folder)

	counter 		= 0

	while True:
		ret, frame = cap.read()
		if not ret:
			exit(1)
		
		if counter % 10 == 0:
			filepath = os.path.join(save_folder, file_basename)
			filepath = filepath + '_{}'.format(counter / 10) + '.png'

			cv2.imwrite(filepath, frame)
			print(filepath, counter)

		counter += 1

if __name__ == '__main__':
	main()

