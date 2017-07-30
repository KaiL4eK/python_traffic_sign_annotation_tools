import os

import argparse

parser = argparse.ArgumentParser(description='Process video with ANN')
parser.add_argument('root', action='store', help='Root of annotations')

args = parser.parse_args()

old_module_delimiter = ':'
new_module_delimiter = '-'

def main():
	paths = (os.path.join(root, filename)
			for root, _, filenames in os.walk(args.root)
			for filename in filenames if old_module_delimiter in filename)

	for path in paths:
		newname = path.replace(old_module_delimiter, new_module_delimiter)
		if newname != path:
			os.rename(path, newname)
	
	return

	root_file_list = os.listdir(args.root)
	for i in root_file_list:
		i_path = os.path.join(args.root, i)
		if os.path.isdir(i_path):
			for image_name in os.listdir(i_path):

				if old_module_delimiter in image_name:
					new_image_name = image_name.replace(old_module_delimiter, new_module_delimiter)
					old_image_path = os.path.join(i_path, image_name)
					new_image_path = os.path.join(i_path, new_image_name)

					print('Rename from %s to %s' % (old_image_path, new_image_path))

					os.rename(old_image_path, new_image_name)

if __name__ == '__main__':
	main()
