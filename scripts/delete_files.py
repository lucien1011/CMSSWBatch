
import argparse
import os

parser = argparse.ArgumentParser(description='Delete some files on EOS')

parser.add_argument('-i', metavar="inputFolder", dest='input_folder',action="store" , required=True, help='input folder',type=str)
parser.add_argument('-s', metavar="step", dest='step',action="store" , required=True, help='input folder',type=int)

args = parser.parse_args()
inputDir = args.input_folder
step = args.step

files = [ inputDir+f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir,f)) ]

files.sort()

for i,file in enumerate(files):
	if i % step == 0:
		os.remove(file)
