
from DBHandler import getFilesFromRun
import argparse

parser = argparse.ArgumentParser(description='Make an input list')

parser.add_argument('-r', metavar="runList", dest='runList',action="store" , required=True, help='the run number list',type=str)

parser.add_argument('-p', metavar="PD", dest='dataset',action="store" , required=True, help='the PD',type=str)
parser.add_argument('-o', metavar="output", dest='output_folder',action="store" , required=True, help='output folder where input list will be stored')

args = parser.parse_args()

outPath = "/afs/cern.ch/work/k/klo/hcal/PromptAnalysis/CMSSW_7_4_10/src/batch/file_list/Collision_HF5050_ZeroBias/inputListAll.txt"
PD = args.dataset 
runList = map(int,args.runList.split(","))

filePathList = []
for run in runList:
	print "Getting files for run %s"%run
	tempList = getFilesFromRun(PD,run)
	filePathList += tempList
	print "Number of files for this run: %s"%len(tempList)

file = open(outPath+"inputListAll.txt","w")
for filePath in filePathList:
	file.write("\""+filePath+"\",\n")
file.close()



