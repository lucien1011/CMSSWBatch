
from DBHandler import getFilesFromRun

outPath = "/afs/cern.ch/work/k/klo/hcal/PromptAnalysis/CMSSW_7_4_10/src/batch/file_list/Collision_HF5050_ZeroBias/inputListAll.txt"
# PD = "/ZeroBias/Run2015C-v1/RAW"
PD = "/ZeroBias/Run2015D-v1/RAW"
runList = [
256004,
256217,
256353,
256464,
256677, 
256843, 
256936,
257058,
]

filePathList = []
for run in runList:
	print "Getting files for run %s"%run
	tempList = getFilesFromRun(PD,run)
	filePathList += tempList
	print "Number of files for this run: %s"%len(tempList)

file = open(outPath,"w")
for filePath in filePathList:
	file.write("\""+filePath+"\",\n")
file.close()



