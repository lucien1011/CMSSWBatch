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
parser.add_argument('-c', metavar='CFG'       , dest='input_python_cfg',action="store", required=True, help='Input CMSSW python config file')
parser.add_argument('-w', metavar="WORKDIR"   , dest='workdir'         ,action="store", required=True, help='Local working directory')
parser.add_argument('-n', metavar='NJOBS'     , dest='njobs'           ,action="store", required=True, type=int, help='Number of jobs')
parser.add_argument('-q', metavar='QUEUE'     , dest='queue'           ,action="store", required=True, help='Batch queue')
parser.add_argument('-o', metavar='OUTPUTFILE', dest='output_file'     ,action="store", required=True, help='Name of the output file')
parser.add_argument('-t', metavar='GLOBALTAG' , dest='global_tag'      ,action="store", required=True, help='GlobalTag to use')
parser.add_argument('-e', metavar='EOSDIR'    , dest='eos_directory'   ,action="store", required=False,help='EOS output directory (optional)')
args = parser.parse_args()

#----------------------------------------------------------------------------
# Are we at fermilab or CERN?
#----------------------------------------------------------------------------

at_fnal = ("fnal" in os.environ["HOSTNAME"])
at_cern = ("cern" in os.environ["HOSTNAME"])

#----------------------------------------------------------------------------
# Did we write this out to EOS?
#----------------------------------------------------------------------------

write_to_eos = False
if args.eos_directory:
    write_to_eos = True
    if at_cern:
        get_eos_bin = 'find /afs/cern.ch/project/eos/installation/ -name "eos.select" | xargs ls -rt1 | tail -1'
        eos_bin = sp.Popen ( get_eos_bin, shell=True, stdout=sp.PIPE ).communicate()[0].strip()

#----------------------------------------------------------------------------
# Lists of jobs
#----------------------------------------------------------------------------

all_jobs = []
bad_jobs = []
running_jobs = []


#----------------------------------------------------------------------------
# Get job numbers from source files
#----------------------------------------------------------------------------

print "*** Getting job numbers from src files:", 

src_folder = args.workdir + "/batch_src/"
src_files = sp.Popen ( "ls " + src_folder, shell=True, stdout=sp.PIPE ).communicate()[0].split()
for src_file in src_files:
    job_number = int(src_file.split("submit_")[1].split(".sh")[0])
    all_jobs.append ( job_number ) 
all_jobs.sort()
print "Found", len (all_jobs), "job(s)"

#----------------------------------------------------------------------------
# Get list of jobs running
#----------------------------------------------------------------------------

print "*** Getting job numbers that are still running:", 

if at_fnal:
    lines = sp.Popen ("condor_q -submitter " + os.environ["USER"], shell=True, stdout=sp.PIPE ).communicate()[0].split("\n")
    for line in lines:
        line = line.strip()
        if line == "": continue
        if "Submitter" in line: continue
        if "SUBMITTED" in line: continue
        if "suspended" in line: continue
        job_number = int(line.split()[-1].split("submit_")[1].split(".sh")[0])
        running_jobs.append ( job_number ) 

if at_cern:
    lines = sp.Popen ("bjobs", shell=True, stdout=sp.PIPE ).communicate()[0].split("\n")
    for line in lines:
        line = line.strip()
        if line == "": continue
        if "JOBID" in line: continue
        job_number = int (line.split()[6].split("_")[1].split(".sh")[0])
        running_jobs.append ( job_number ) 

print "Found", len(all_jobs) - len (running_jobs), "job(s) done running"

#----------------------------------------------------------------------------
# Make sure that the following are all there for each job
# - log file
# - output (on local disk or on EOS)
# - python cfg 
#----------------------------------------------------------------------------

print "*** Checking", len (all_jobs) - len(running_jobs), "job(s)"

cfg_file_folder = args.workdir + "/python_cfgs/"
for job_number in all_jobs:
    if job_number in bad_jobs: continue
    if job_number in running_jobs: continue
    cfg_file_name = os.path.basename(args.input_python_cfg).replace(".py","_" + str(job_number) + ".py")
    cfg_file_path = cfg_file_folder + "/" + cfg_file_name
    if not os.path.isfile ( cfg_file_path ):
        print "\tMissing python cfg file for job:", job_number
        bad_jobs.append ( job_number )

print "*** Of those jobs,", len ( all_jobs ) - len (bad_jobs) - len(running_jobs), "have python cfg files"

log_file_folder = args.workdir + "/log/"
for job_number in all_jobs:
    if job_number in bad_jobs: continue
    if job_number in running_jobs: continue
    log_file_path = log_file_folder + "/job_%d.log" % job_number
    if not os.path.isfile ( log_file_path ):
        print "\tMissing log file for job:", job_number
        print "\tI looked here:", log_file_path
        bad_jobs.append ( job_number )

print "*** Of those jobs,", len ( all_jobs ) - len (bad_jobs) - len(running_jobs), "have log files"

if write_to_eos:
    if at_cern:
        eos_files = sp.Popen ( eos_bin + " ls " + args.eos_directory, shell=True, stdout=sp.PIPE ).communicate()[0].split()
    if at_fnal:
        eos_files = sp.Popen ( "ls " + args.eos_directory, shell=True, stdout=sp.PIPE ).communicate()[0].split()
    for job_number in all_jobs:
        if job_number in bad_jobs: continue
        if job_number in running_jobs: continue
        file_name = args.output_file + "_" + str(job_number) + ".root"
        if file_name not in eos_files:
            print "\tMissing root file on EOS for job:", job_number, ":", file_name
            bad_jobs.append ( job_number )
    print "*** Of those jobs,", len ( all_jobs ) - len (bad_jobs) - len(running_jobs), "have root files on EOS"
else:
    local_files = sp.Popen ( "ls " + args.workdir + "/output/", shell=True, stdout=sp.PIPE ).communicate()[0].split()
    for job_number in all_jobs:
        if job_number in bad_jobs: continue
        if job_number in running_jobs: continue
        file_name = args.output_file + "_" + str(job_number) + ".root"
        if file_name not in local_files:
            print "\tMissing root file on local disk for job:", job_number, ":", file_name
            bad_jobs.append ( job_number )
    print "*** Of those jobs,", len ( all_jobs ) - len (bad_jobs) - len(running_jobs), "have root files on local disk"
    
#----------------------------------------------------------------------------
# For log files, look for the following strings, which suggest job failure
# - "error"
# - "exit code"
#----------------------------------------------------------------------------

print "*** Extra check for jobs with errors in their logs"

bad_strings = ["exit code", "abort", "job killed"]

if at_cern:
    grep_command = "ls " + log_file_folder + "/*.log | xargs egrep -i '"
if at_fnal:
    grep_command = "ls " + log_file_folder + "/*.stderr | xargs egrep -i '"

for bad_string in bad_strings:
    grep_command = grep_command + bad_string + "|"
grep_command = grep_command[:-1]+"'"

grep_output_entries = sp.Popen ( grep_command, shell=True,stdout=sp.PIPE).communicate()[0].split("\n")
n_entries = len ( grep_output_entries ) 
for entry in grep_output_entries:
    if not entry.strip(): continue
    log_file = os.path.basename(entry.split(":")[0])
    if at_cern:
        job_number = int(log_file.split("_")[1].split(".log")[0])
    if at_fnal:
        job_number = int(log_file.split("_")[1].split(".stderr")[0])
    if n_entries > 1:
        message  = entry.split(log_file + ":")[1]
    else:
        message = entry.strip()
    print "\tJob", job_number, " has bad log message:", message
    if job_number not in bad_jobs:
        bad_jobs.append ( job_number )

#----------------------------------------------------------------------------
# Write new submit commands
#----------------------------------------------------------------------------

print "*** Writing submit commands"

bad_jobs.sort()

workdir_lxbatch_cfg = args.workdir + "/batch_cfg"
workdir_lxbatch_src = args.workdir + "/batch_src"
workdir_log         = args.workdir + "/log"
launch_file = open("launch.sh","w")

if at_fnal:
    launch_file.write("cd " + log_file_folder + "\n")

for job_number in bad_jobs:
    cfg_file_path = workdir_lxbatch_cfg + "/config_" + str ( job_number ) + ".cfg"
    src_file_path = workdir_lxbatch_src + "/submit_" + str ( job_number ) + ".sh"
    old_log_file_path = log_file_folder + "/job_%d.log" % job_number
    new_log_file_path = log_file_folder + "/job_%d.log.resubmit" % job_number
    log_command = "mv " + old_log_file_path + " " + new_log_file_path
    eos_file = args.output_file + "_" + str(job_number) + ".root"
    if at_cern:
        if write_to_eos:
            if eos_file in eos_files:
                output_command = eos_bin + " rm " + args.eos_directory + "/" + eos_file
            else:
                output_command = ""
        else:
            output_command = "rm " + args.workdir + "/output/" + args.output_file + "_" + str(job_number) + ".root"
        if os.path.isfile ( old_log_file_path ):
            launch_file.write(log_command + "\n")
        if output_command:
            launch_file.write(output_command + "\n")
        launch_command = "bsub -q " + args.queue + " -o " + workdir_log + "/job_" + str(job_number) + ".log source " + src_file_path + "\n"
        launch_file.write(launch_command)

    if at_fnal:
        old_stderr_file_path = log_file_folder + "/job_%d.stderr" % job_number
        old_stdout_file_path = log_file_folder + "/job_%d.stdout" % job_number
        new_stderr_file_path = log_file_folder + "/job_%d.stderr.resubmit" % job_number
        new_stdout_file_path = log_file_folder + "/job_%d.stdout.resubmit" % job_number
        stderr_command = "mv " + old_stderr_file_path + " " + new_stderr_file_path
        stdout_command = "mv " + old_stdout_file_path + " " + new_stdout_file_path
        if write_to_eos:
            if eos_file in eos_files:
                output_command = "rm " + args.eos_directory + "/" + eos_file
            else:
                output_command = ""
        else:
            output_command = "rm " + args.workdir + "/output/" + args.output_file + "_" + str(job_number) + ".root"
        if os.path.isfile ( old_stderr_file_path ):
            launch_file.write( stderr_command + "\n") 
        if os.path.isfile ( old_stdout_file_path ):
            launch_file.write( stdout_command + "\n" ) 
        if os.path.isfile ( old_log_file_path ):
            launch_file.write(log_command + "\n")
        if output_command:
            launch_file.write(output_command + "\n")
        launch_command = "condor_submit " + cfg_file_path
        launch_file.write(launch_command+"\n")

if at_fnal:
    launch_file.write("cd -\n")

launch_file.close()


#----------------------------------------------------------------------------
# Tell the user
#----------------------------------------------------------------------------

if bad_jobs:
    print "Done!  Relaunch",len(bad_jobs),"jobs by doing the following:"
    print "\t", "source launch.sh"
elif running_jobs:
    print "Done!  There are", len (running_jobs), "jobs still running."
else:
    print "Done!  All jobs successful!"
