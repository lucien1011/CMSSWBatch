
import subprocess as sp
from whereAmI import whereAmI 

def getDBPath(PDName,run,lumi):
	cmdList = ["das_client.py","--query","file dataset=%s run=%s lumi=%s"%(PDName,run,lumi),"--limit","0"]
	process = sp.Popen(cmdList,stdout=sp.PIPE)

	if whereAmI() == "Imperial":
		return "root://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/cms"+process.communicate()[0].split("\n")[0]
	else:
		raise RuntimeError, "getDBPath function only supports IC for the moment."

def getFilesFromPD(PDName):
	cmdList = ["das_client.py","--query","file dataset=%s"%(PDName),"--limit","0"]
	process = sp.Popen(cmdList,stdout=sp.PIPE)
	
	if whereAmI() == "Imperial":
		return ["root://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/cms"+fileName for fileName in process.communicate()[0].split("\n") if fileName.endswith(".root")]
	else:
		raise RuntimeError, "getFilesFromPD function only supports IC for the moment."

def getFilesFromRun(PDName,runNumber):
	cmdList = ["das_client.py","--query","file dataset=%s run=%s"%(PDName,runNumber),"--limit","0"]
	process = sp.Popen(cmdList,stdout=sp.PIPE)
	
	if whereAmI() == "CERN":
		return ["root://eoscms//eos/cms"+fileName for fileName in process.communicate()[0].split("\n") if fileName.endswith(".root")]
	else:
		raise RuntimeError, "getFilesFromRun function only supports IC for the moment."


