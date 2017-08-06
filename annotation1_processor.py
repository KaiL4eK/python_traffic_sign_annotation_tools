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

    dir_list = os.listdir(args.filepath)
    for i in dir_list:
        i_path = os.path.join(args.filepath, i)
        if os.path.isdir(i_path):
            print('Open new dir: ' + i_path)
            image_dir_list = os.listdir(i_path)
            for image_name in image_dir_list:
                if len(image_name.split('.')) == 2:
                    frame_name = image_name.split('.')[0]
                    frame_path = os.path.join(i_path, frame_name)
                    mask_path = frame_path + '.mask.0.png'
                    frame_path = frame_path + '.png'

                    if not os.path.exists(mask_path):
                    	print(frame_path)
                    	os.remove(frame_path)

                    


if __name__ == '__main__':
	main()

