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
# Get number of events in each file
#----------------------------------------------------------------------------

print "*** Counting number of events in each input file"

if not os.path.isfile ( args.input_list ):
    print "Input list you specified does not exist:"
    print "\t", args.input_list 
    print "Specify an existing file to continue"
    sys.exit()

input_list = open ( args.input_list, "r" ) 
d_inputFile_nevents = {}
input_files = []
total_nevents = int(0)
for iline, line in enumerate(input_list):
    line = line.strip()
    if line == "": continue
    line = line.replace(",","")
    command = "edmFileUtil " + line
    nevents = int(sp.Popen ( command, shell=True, stdout=sp.PIPE ).communicate()[0].split("\n")[1].split(",")[2].split("event")[0].strip())
    d_inputFile_nevents[line] = nevents
    input_files.append ( line )
    total_nevents += nevents
    print "\t", iline, line, int(nevents), int(total_nevents)
    
#----------------------------------------------------------------------------
# Split up jobs
#----------------------------------------------------------------------------

print "*** Splitting up jobs:"

njobs = args.njobs
nevents_per_job = int(math.ceil (float(total_nevents) / float(njobs)))
njobs_updated   = int(math.floor(float(total_nevents) / float(nevents_per_job)))
nevents_in_last_job = total_nevents - ( (njobs_updated - 1) * nevents_per_job ) 

if nevents_in_last_job > nevents_per_job:
    nevents_per_job = int(math.floor (float(total_nevents) / float(njobs)))
    njobs_updated   = int(math.ceil(float(total_nevents) / float(nevents_per_job)))
    nevents_in_last_job = total_nevents - ( (njobs_updated - 1) * nevents_per_job ) 

print "\t", "Run a total of", njobs_updated, "jobs"
print "\t", "Jobs 0-" + str(njobs_updated-2), "will process", nevents_per_job, "events"
print "\t", "Job", str(njobs_updated-1), "will process", nevents_in_last_job, "events"

l_events_to_skip = []
l_events_to_process = []
l_files_to_process = []

for ijob in range(0,njobs_updated):
    job_min_event = 1 + nevents_per_job * ijob
    job_max_event = nevents_per_job * (ijob + 1)
    
    total_events_to_skip = job_min_event - 1
    events_to_process = nevents_per_job

    if ijob == njobs_updated - 1:
        job_max_event = job_min_event + nevents_in_last_job - 1
        events_to_process = nevents_in_last_job

    nevents_in_previous_files = 0
    start_file = "BLAH"
    stop_file = "BLAH"
    for i_input_file, input_file in enumerate(input_files):
        nevents_in_this_file = d_inputFile_nevents[input_file]
        if input_file == input_files[-1]:
            nevents_in_next_file = 0
        else:
            nevents_in_next_file = d_inputFile_nevents[input_files[i_input_file+1]]

        if job_min_event > nevents_in_previous_files and job_min_event < ( nevents_in_previous_files + nevents_in_this_file ):
            start_file = i_input_file
        if job_max_event <= nevents_in_previous_files + nevents_in_this_file:
            stop_file = i_input_file
            break

        nevents_in_previous_files += nevents_in_this_file

    nevents_in_previous_files = 0
    for i_input_file in range(0, start_file):
        nevents_in_previous_files += d_inputFile_nevents[input_files[i_input_file]]
    
    files_to_process = input_files[start_file:stop_file+1]
    files_to_process_data = ""
    for input_file in files_to_process:
        files_to_process_data += input_file + ",\n"
    files_to_process_data = files_to_process_data[:-2]
    files_to_process_data = files_to_process_data.replace("/","\/")

    events_to_skip = total_events_to_skip - nevents_in_previous_files
    
    l_events_to_skip.append    ( events_to_skip    )
    l_events_to_process.append ( events_to_process ) 
    l_files_to_process.append  ( files_to_process_data  )

#----------------------------------------------------------------------------
# Split up pileup files
#----------------------------------------------------------------------------
    
if ( args.pu_input_list):

    print "*** Splitting up pileup files:"
    
    l_pu_files_to_process = []
    total_n_pu_events = int(0)
    ijob = 0
    pu_files_to_process_data = ""
    pu_input_list = open ( args.pu_input_list, "r" ) 
    for iline, line in enumerate(pu_input_list):
        line = line.strip()
        if line == "": continue
        line = line.replace(",","")
        command = "edmFileUtil " + line
        n_pu_events = int(sp.Popen ( command, shell=True, stdout=sp.PIPE ).communicate()[0].split("\n")[1].split(",")[2].split("event")[0].strip())
        total_n_pu_events += n_pu_events
        print "\t", iline, line, int(n_pu_events), int(total_n_pu_events)
        
        pu_files_to_process_data += line + ",\n"
        
        if total_n_pu_events > l_events_to_process[ijob]:
            total_n_pu_events = int(0)
            pu_files_to_process_data = pu_files_to_process_data[:-2]
            pu_files_to_process_data = pu_files_to_process_data.replace("/","\/")
            l_pu_files_to_process.append (str(pu_files_to_process_data))
            pu_files_to_process_data = ""
            ijob += 1
            if ijob == njobs_updated: break
            continue


#----------------------------------------------------------------------------
# Make python configurations
#----------------------------------------------------------------------------

print "*** Making python cfgs"

cfg_file_paths = []
output_files = []

for ijob in range (0, njobs_updated):
    new_cfg_file_name = args.input_python_cfg.replace("_cfg.py", "_" + str(ijob) + "_cfg.py")
    new_cfg_file_path = workdir_python_cfgs + "/" + os.path.basename(new_cfg_file_name)
    
    output_file_prefix = args.output_file + "_" + str(ijob)
    output_file = output_file_prefix + ".root"
    
    cp_command     = "cp " + args.input_python_cfg + " " + new_cfg_file_path
    
    perl_command_1 = "perl -pi -e 's/#FILENAMES/"     + str(l_files_to_process [ijob]) + "/g' " + new_cfg_file_path
    perl_command_2 = "perl -pi -e 's/#SKIPEVENTS/"    + str(l_events_to_skip   [ijob]) + "/g' " + new_cfg_file_path
    perl_command_3 = "perl -pi -e 's/#PROCESSEVENTS/" + str(l_events_to_process[ijob]) + "/g' " + new_cfg_file_path
    perl_command_4 = "perl -pi -e 's/OUTPUTFILENAME/" + str(output_file_prefix       ) + "/g' " + new_cfg_file_path
    perl_command_5 = "perl -pi -e 's/GLOBALTAG/"      + str(args.global_tag          ) + "/g' " + new_cfg_file_path
    
    os.system ( cp_command     )
    os.system ( perl_command_1 )
    os.system ( perl_command_2 )
    os.system ( perl_command_3 )
    os.system ( perl_command_4 )
    os.system ( perl_command_5 )

    if args.pu_input_list :
        perl_command_6 = "perl -pi -e 's/#PILEUPFILENAMES/" + l_pu_files_to_process[ijob] + "/g' " + new_cfg_file_path
        os.system ( perl_command_6 )
        
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

