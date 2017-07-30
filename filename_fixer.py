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

if __name__ == '__main__':
	main()
