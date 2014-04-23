#----------------------------------------------------------------------------
# Imports
#----------------------------------------------------------------------------

import subprocess as sp
import sys, os, math
import argparse

#----------------------------------------------------------------------------
# Get important variables
#----------------------------------------------------------------------------

print "*** Parsing input"

parser = argparse.ArgumentParser(description='Launch an analysis')
parser.add_argument('-c', metavar='CFG'        , dest='input_python_cfg',action="store", required=True , help='Input CMSSW python config file')
parser.add_argument('-w', metavar="WORKDIR"    , dest='workdir'         ,action="store", required=True , help='Local working directory')
parser.add_argument('-n', metavar='NJOBS'      , dest='njobs'           ,action="store", required=True , type=int, help='Number of jobs')
parser.add_argument('-i', metavar='INPUTLIST'  , dest='input_list'      ,action="store", required=True , help='Input list of files to run on')
parser.add_argument('-p', metavar='PUINPUTLIST', dest='pu_input_list'   ,action="store", required=False, help='Input list of files for pileup')
parser.add_argument('-o', metavar='OUTPUTFILE' , dest='output_file'     ,action="store", required=True , help='Name of the output file')
parser.add_argument('-t', metavar='GLOBALTAG'  , dest='global_tag'      ,action="store", required=True , help='GlobalTag to use')
parser.add_argument('-q', metavar='QUEUE'      , dest='queue'           ,action="store", required=False, help='Batch queue (only needed at CERN)')
parser.add_argument('-e', metavar='EOSDIR'     , dest='eos_directory'   ,action="store", required=False, help='EOS output directory (optional)')
parser.add_argument('-s', metavar='SHORT'      , dest='short'           ,action="store", required=False, help='Run on the "SHORT" queue at FNAL (optional)')

args = parser.parse_args()

#----------------------------------------------------------------------------
# Are we at fermilab or CERN?
#----------------------------------------------------------------------------

at_fnal = ("fnal" in os.environ["HOSTNAME"])
at_cern = ("cern" in os.environ["HOSTNAME"])

if (not args.queue) and at_cern:
    print "You need to specify a queue if you run at CERN.  Bailing."
    sys.exit()

#----------------------------------------------------------------------------
# Should we write this out to EOS?
# If we should, then make the EOS directory
#----------------------------------------------------------------------------

print "*** Setting up EOS"

if args.eos_directory:

    ls_command = ""
    if at_cern:
        get_eos_bin = 'find /afs/cern.ch/project/eos/installation/ -name "eos.select" | xargs ls -rt1 | tail -1'
        eos_bin = sp.Popen ( get_eos_bin, shell=True, stdout=sp.PIPE ).communicate()[0].strip()
        ls_command    = eos_bin + " ls "    + args.eos_directory
        mkdir_command = eos_bin + " mkdir -p " + args.eos_directory
    elif at_fnal:
        ls_command    = "ls "       + args.eos_directory
        mkdir_command = "mkdir -p " + args.eos_directory
    else:
        print "Don't know how to handle mass storage for this hostname:", os.environ["HOSTNAME"]
        sys.exit()

    eos_directory_contents_stderr = sp.Popen ( ls_command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE ).communicate()[1]
    eos_directory_exists = False
    if not eos_directory_contents_stderr:
        eos_directory_exists = True
        
    print "*** Mass storage directory exists?", eos_directory_exists
    if eos_directory_exists :
        print "*** Warning. Mass storage directory you specified already exists:"
        print "\t", args.eos_directory
    else:
        print "*** Making mass storage directory you specified:"
        print "\t", args.eos_directory
        os.system ( mkdir_command )

#----------------------------------------------------------------------------
# Make work directories
#----------------------------------------------------------------------------

print "*** Making work directories"

workdir = args.workdir
workdir_input_lists    = workdir + "/input_lists" 
workdir_python_cfgs    = workdir + "/python_cfgs" 
workdir_batch_src      = workdir + "/batch_src"
workdir_batch_cfg      = workdir + "/batch_cfg"
workdir_output         = workdir + "/output"
workdir_log            = workdir + "/log"
workdir_pu_input_lists = workdir + "/pu_input_lists"

if os.path.isdir ( workdir ):
    print "working directory you specified already exists:"
    print "\t", workdir
    print "Remove it or choose a new directory to continue"
    sys.exit()

os.system ("mkdir -p " + workdir )
os.system ("mkdir -p " + workdir_input_lists )
os.system ("mkdir -p " + workdir_pu_input_lists )
os.system ("mkdir -p " + workdir_python_cfgs )
os.system ("mkdir -p " + workdir_batch_src )
os.system ("mkdir -p " + workdir_batch_cfg )
os.system ("mkdir -p " + workdir_output )
os.system ("mkdir -p " + workdir_log )
    
#----------------------------------------------------------------------------
# Make input lists
#----------------------------------------------------------------------------

print "*** Making input lists"

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
# Make pileup input lists
#----------------------------------------------------------------------------

if args.pu_input_list : 
    print "*** Making pileup input lists"

    if not os.path.isfile ( args.pu_input_list ):
        print "Pileup input list you specified does not exist:"
        print "\t", args.pu_input_list 
        print "Specify an existing file to continue"
        sys.exit()
        
    n_pu_files = int (sp.Popen ("cat " + args.pu_input_list + " | wc -l", shell=True, stdout=sp.PIPE ).communicate()[0])
    if not args.nsubjobs:
        pu_files_per_job = int(math.floor(float(n_pu_files) / float(njobs_updated)))
    else:
        pu_files_per_job = int(math.floor(float(n_pu_files) / float(njobs_updated * args.nsubjobs)))
    print "n pu files =", n_pu_files
    print "pu files per job =", pu_files_per_job
        
    pu_input_lists = []
    
    sys.exit()

    for ijob in range (0, njobs_updated):
        min_file = int(ijob * pu_files_per_job) 
        max_file = int(min(min_file + pu_files_per_job -1, n_pu_files -1)) 
        n_files  = max_file - min_file + 1
        if n_files == 0:
            print "ERROR: n_files = 0" 
            sys.exit()
        tmp_input_list = workdir_pu_input_lists + "/inputList_" + str(ijob) + ".txt"
        command = "cat " + args.pu_input_list + " | head -" + str(max_file+1) + " | tail -" + str(n_files) + " > " + tmp_input_list
        pu_input_lists.append ( tmp_input_list )
        os.system ( command ) 

#----------------------------------------------------------------------------
# Make python cfgs
#----------------------------------------------------------------------------

print "*** Making python cfgs"

cfg_file_paths = []
output_files = []

for ijob in range (0, njobs_updated):
    new_cfg_file_name = args.input_python_cfg.replace("_cfg.py", "_" + str(ijob) + "_cfg.py")
    new_cfg_file_path = workdir_python_cfgs + "/" + os.path.basename(new_cfg_file_name)
    
    input_list = open (input_lists[ijob],"r")
    input_list_raw_data = input_list.read()
    input_list_data = input_list_raw_data.replace("/","\/")
    input_list.close()

    if args.pu_input_list : 
        pu_input_list = open (pu_input_lists[ijob],"r")
        pu_input_list_raw_data = pu_input_list.read()
        pu_input_list_data = pu_input_list_raw_data.replace("/","\/")
        pu_input_list.close()
        
    output_file_prefix = args.output_file + "_" + str(ijob)
    output_file = output_file_prefix + ".root"
    
    cp_command     = "cp " + args.input_python_cfg + " " + new_cfg_file_path
    
    perl_command_1 = "perl -pi -e 's/#FILENAMES/" + input_list_data + "/g' " + new_cfg_file_path
    perl_command_2 = "perl -pi -e 's/OUTPUTFILENAME/" + output_file_prefix + "/g' " + new_cfg_file_path
    perl_command_3 = "perl -pi -e 's/GLOBALTAG/" + args.global_tag + "/g' " + new_cfg_file_path
    
    os.system ( cp_command     )
    os.system ( perl_command_1 )
    os.system ( perl_command_2 )
    os.system ( perl_command_3 )

    if args.pu_input_list :
        perl_command_4 = "perl -pi -e 's/#PILEUPFILENAMES/" + pu_input_list_data + "/g' " + new_cfg_file_path
        os.system ( perl_command_4 )
        
    cfg_file_paths.append ( new_cfg_file_path ) 
    output_files.append ( output_file )

#----------------------------------------------------------------------------
# Make src files for batch
#----------------------------------------------------------------------------

print "*** Making batch src files"

src_file_paths = []
for ijob in range (0, njobs_updated):
    src_file_path = workdir_batch_src + "/submit_" + str ( ijob ) + ".sh"
    src_file = open (src_file_path,"w")
    src_file.write("#!/bin/bash\n")
    src_file.write("cd " + os.environ["CMSSW_BASE"] + "\n")
    src_file.write("eval `scramv1 runtime -sh`\n")
    if at_cern:
        src_file.write("cd " + workdir_output + "\n")
        scratch_dir = "/tmp/" + os.environ["USER"]
        if not os.path.isdir ( scratch_dir ):
            os.system ( "mkdir " + scratch_dir )
        src_file.write("cd " + scratch_dir + "\n")
        src_file.write("cmsRun " + cfg_file_paths[ijob] + "\n")
        src_file.write("xrdcp " + output_files[ijob] + " root://eoscms/" + args.eos_directory.strip() + "/" + output_files[ijob] + "\n")
        src_file.write("rm " + output_files[ijob])
    if at_fnal:
        scratch_dir = "$_CONDOR_SCRATCH_DIR"
        src_file.write("cd " + scratch_dir + "\n")
        src_file.write("cmsRun " + os.path.basename(cfg_file_paths[ijob]) + "\n")
        src_file.write("mv " + output_files[ijob] + " " + args.eos_directory.strip() + "/" + output_files[ijob] + "\n")
        os.system("chmod u+x " + src_file_path + "\n")

    src_file.close()
    src_file_paths.append ( src_file_path ) 

#----------------------------------------------------------------------------
# If at FNAL, you need a batch cfg file
# http://www.uscms.org/uscms_at_work/computing/setup/batch_systems.shtml
#----------------------------------------------------------------------------

print "*** Making batch cfg files (if you're at FNAL)"

batch_cfg_file_paths = []
if at_fnal:
    for ijob in range (0, njobs_updated):
        cfg_file_path = workdir_batch_cfg + "/config_" + str ( ijob ) + ".cfg"
        cfg_file = open (cfg_file_path,"w")
        cfg_file.write("universe = vanilla\n")
        cfg_file.write("Executable = " + src_file_paths[ijob] + "\n")
        cfg_file.write("Should_Transfer_Files = YES\n")
        cfg_file.write("WhenToTransferOutput = ON_EXIT\n")
        cfg_file.write("Transfer_Input_Files = " + cfg_file_paths[ijob] + "\n")
        cfg_file.write("Output = job_"+str(ijob)+".stdout\n")
        cfg_file.write("Error = job_"+str(ijob)+".stderr\n")
        cfg_file.write("Log = job_"+str(ijob)+".log\n")
        cfg_file.write("notify_user = "+os.environ["USER"]+"@FNAL.GOV\n")
        cfg_file.write("Queue 1\n")
        if args.short:
            cfg_file.write("+LENGTH='SHORT'\n")
        batch_cfg_file_paths.append ( cfg_file_path ) 

#----------------------------------------------------------------------------
# Make launch path
#----------------------------------------------------------------------------

print "*** Writing submit commands"

launch_file = open("launch.sh","w")

if at_fnal:
    launch_file.write("cd " + workdir_log + "\n")

for ijob in range (0, njobs_updated):
    if at_cern:
        launch_file.write("bsub -q " + args.queue + " -o " + workdir_log + "/job_" + str(ijob) + ".log source " + src_file_paths[ijob] + "\n")
    if at_fnal:
        launch_file.write("condor_submit " + batch_cfg_file_paths[ijob] + "\n")
if at_fnal:
    launch_file.write("cd -\n")
launch_file.close()

#----------------------------------------------------------------------------
# Tell the user
#----------------------------------------------------------------------------

print "Done!  Launch",njobs_updated,"jobs by doing the following:"
print "\t", "source launch.sh"
