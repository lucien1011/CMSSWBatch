
from DBHandler import getFilesFromRun
import argparse
import os

parser = argparse.ArgumentParser(description='Make an input list')

parser.add_argument('-r', metavar="runList", dest='runList',action="store" , required=True, help='the run number list',type=str)
parser.add_argument('-s', metavar="runstep", dest='runStep',action="store" , required=False, help='the run number step',type=int)

parser.add_argument('-p', metavar="PD", dest='dataset',action="store" , required=True, help='the PD',type=str)
parser.add_argument('-o', metavar="output", dest='output_folder',action="store" , required=True, help='output folder where input list will be stored',type=str)
parser.add_argument('-w', metavar="write", dest="write", action="store", required=False, help='write to output folder',type=bool,default=True)

args = parser.parse_args()
outdir = args.output_folder
PD = args.dataset

if "-" in args.runList:
	tempList = args.runList.split("-")
	if len(tempList) != 2:
		raise RuntimeError, "Invalid format for run range"
	if not hasattr(args,"runStep"):
		raise RuntimeError, "Please provide the run step"
	else:
		runStep = args.runStep
	lowerRange = int(args.runList.split("-")[0])
	upperRange = int(args.runList.split("-")[1])
	runList = range(lowerRange,upperRange,runStep)
else:
	runList = map(int,args.runList.split(","))

filePathList = []
validRunList = []
for run in runList:
	print "Getting files for run %s"%run
	tempList = getFilesFromRun(PD,run)
	filePathList += tempList
	print "Number of files for this run: %s"%len(tempList)
	if (len(tempList) != 0):
		validRunList.append(run)

if not os.path.isdir ( outdir ):
	os.system ( "mkdir -p " + outdir )

if args.write:
	file = open(outdir+"/inputListAll.txt","w")
	for filePath in filePathList:
		file.write("\""+filePath+"\",\n")
	file.close()

validRunList.sort()
print "==========================================="
print "------------------Summary------------------"
print "==========================================="
print "Total number of required runs: %s"%len(runList)
print "Total number of valid runs: %s"%len(validRunList)
print "Total number of files: %s"%len(filePathList)
runString = ""
for validRun in validRunList:
	runString += "%s "%validRun
print "List of valid runs:"
print runString



