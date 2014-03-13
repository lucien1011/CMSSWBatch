#----------------------------------------------------------------------------
# Imports
#----------------------------------------------------------------------------

import subprocess as sp
import sys, os, math
import argparse

#----------------------------------------------------------------------------
# Get important variables
#----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Launch an analysis')
parser.add_argument('-c', metavar='CFG'      , dest='input_python_cfg',action="store", required=True, help='Input CMSSW python config file')
parser.add_argument('-w', metavar="WORKDIR"  , dest='workdir'         ,action="store", required=True, help='Local working directory')
parser.add_argument('-n', metavar='NJOBS'    , dest='njobs'           ,action="store", required=True, type=int, help='Number of jobs')
parser.add_argument('-q', metavar='QUEUE'    , dest='queue'           ,action="store", required=True, help='Batch queue')
parser.add_argument('-i', metavar='INPUTLIST', dest='input_list'      ,action="store", required=True, help='Input list of files to run on')
args = parser.parse_args()

#----------------------------------------------------------------------------
# Make work directories
#----------------------------------------------------------------------------

workdir = args.workdir
workdir_input_lists = workdir + "/input_lists" 
workdir_python_cfgs = workdir + "/python_cfgs" 
workdir_lxbatch_src = workdir + "/lxbatch_src"
workdir_output      = workdir + "/output"
workdir_log         = workdir + "/log"

if os.path.isdir ( workdir ):
    print "working directory you specified already exists:"
    print "\t", workdir
    print "Remove it or choose a new directory to continue"
    sys.exit()

os.system ("mkdir -p " + workdir )
os.system ("mkdir -p " + workdir_input_lists )
os.system ("mkdir -p " + workdir_python_cfgs )
os.system ("mkdir -p " + workdir_lxbatch_src )
os.system ("mkdir -p " + workdir_output )
os.system ("mkdir -p " + workdir_log )
    
#----------------------------------------------------------------------------
# Make input lists
#----------------------------------------------------------------------------

if not os.path.isfile ( args.input_list ):
    print "Input list you specified does not exist:"
    print "\t", args.input_list 
    print "Specify an existing file to continue"
    sys.exit()

njobs  = args.njobs
nfiles = int (sp.Popen ("cat " + args.input_list + " | wc -l", shell=True, stdout=sp.PIPE ).communicate()[0])
files_per_job = int(math.ceil(float(nfiles) / float(njobs)))
njobs_updated = int(math.ceil(float(nfiles) / float(files_per_job)))
input_lists = []

for ijob in range (0, njobs_updated):
    min_file = int(ijob * files_per_job) 
    max_file = int(min(min_file + files_per_job -1, nfiles -1)) 
    n_files  = max_file - min_file + 1
    tmp_input_list = workdir_input_lists + "/inputList_" + str(ijob) + ".txt"
    command = "cat " + args.input_list + " | head -" + str(max_file+1) + " | tail -" + str(n_files) + " > " + tmp_input_list
    input_lists.append ( tmp_input_list )
    os.system ( command ) 

#----------------------------------------------------------------------------
# Make python cfgs
#----------------------------------------------------------------------------

cfg_file_paths = []

for ijob in range (0, njobs_updated):
    new_cfg_file_name = args.input_python_cfg.replace("_cfg.py", "_" + str(ijob) + "_cfg.py")
    new_cfg_file_path = workdir_python_cfgs + "/" + os.path.basename(new_cfg_file_name)
    
    input_list = open (input_lists[ijob],"r")
    input_list_raw_data = input_list.read()
    input_list_data = input_list_raw_data.replace("/","\/")
    input_list.close()
    
    cp_command     = "cp " + args.input_python_cfg + " " + new_cfg_file_path
    perl_command_1 = "perl -pi -e 's/#FILENAMES/" + input_list_data + "/g' " + new_cfg_file_path
    perl_command_2 = "perl -pi -e 's/JOBNUMBER/" + str(ijob) + "/g' " + new_cfg_file_path
    
    os.system ( cp_command     )
    os.system ( perl_command_1 )
    os.system ( perl_command_2 )

    cfg_file_paths.append ( new_cfg_file_path ) 

#----------------------------------------------------------------------------
# Make src files for batch
#----------------------------------------------------------------------------

src_file_paths = []
for ijob in range (0, njobs_updated):
    src_file_path = workdir_lxbatch_src + "/submit_" + str ( ijob ) + ".sh"
    src_file = open (src_file_path,"w")
    src_file.write("#!/bin/bash\n")
    src_file.write("cd " + os.environ["CMSSW_BASE"] + "\n")
    src_file.write("eval `scramv1 runtime -sh`\n")
    src_file.write("cd " + workdir_output + "\n")
    src_file.write("cmsRun " + cfg_file_paths[ijob] + "\n")
    src_file.close()
    src_file_paths.append ( src_file_path ) 

#----------------------------------------------------------------------------
# Make launch path
#----------------------------------------------------------------------------

launch_file = open("launch.sh","w")
for ijob in range (0, njobs_updated):
    launch_file.write("bsub -q " + args.queue + " -o " + workdir_log + "/job_" + str(ijob) + ".log source " + src_file_paths[ijob] + "\n")
launch_file.close()

#----------------------------------------------------------------------------
# Tell the user
#----------------------------------------------------------------------------

print "Done!  Launch",njobs_updated,"jobs by doing the following:"
print "\t", "source launch.sh"
