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
parser.add_argument('-f', metavar='FNALDIR'   , dest='fnal_dir',action="store", required=True, help='Start directory on FNAL EOS')
parser.add_argument('-c', metavar='CERNDIR'   , dest='cern_dir',action="store", required=True, help='End directory on CERN EOS')
args = parser.parse_args()

#----------------------------------------------------------------------------
# Look in the directory and see what to copy
#----------------------------------------------------------------------------

print "*** Examining directory:",

ls_command = "lcg-ls \"srm://cmseos.fnal.gov:8443/srm/v2/server?SFN=" + args.fnal_dir + "\""
ls_stdout,ls_stderr = sp.Popen ( ls_command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE).communicate()

ls_stderr = ls_stderr.strip()

if ls_stderr:
    print "\n\nError when running \"lcg-ls\" command:\n"
    print ls_stderr
    print "\nYou probably need to run the following commands from an SLC5 machine:\n"
    print "source /afs/cern.ch/cms/LCG/LCG-2/UI/cms_ui_env.sh"
    print "grid-proxy-init -valid 24:00"
    print "\n"
    sys.exit()

files = ls_stdout.split()

print "I found", len(files), "files to copy"

#----------------------------------------------------------------------------
# Copy each file
#----------------------------------------------------------------------------

get_eos_bin = 'find /afs/cern.ch/project/eos/installation/ -name "eos.select" | xargs ls -rt1 | tail -1'
eos_bin = sp.Popen ( get_eos_bin, shell=True, stdout=sp.PIPE ).communicate()[0].strip()

for i,file in enumerate(files):

    print "*** Processing file", i+1, "/", len(files), ":", os.path.basename(file)

    srmcp_command = "srmcp -srm_protocol_version=2 -use_urlcopy_script=true -urlcopy=${SRM_PATH}/sbin/url-copy.sh "
    fnal_srm_path = "srm://cmseos.fnal.gov:8443/srm/v2/server?SFN=" + file
    scratch_dir   = "/tmp/" + os.environ["USER"] 
    cern_tmp_path = scratch_dir + "/" + os.path.basename(file)
    cern_eos_path = args.cern_dir + "/" + os.path.basename(file)
    eosls_command = eos_bin + " ls " + cern_eos_path
    eosls_stdout, eosls_stderr  = sp.Popen ( eosls_command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE).communicate()
    tmpcp_command = srmcp_command + "\"" + fnal_srm_path + "\" \"file://" + cern_tmp_path + "\" >> log.txt 2>&1 "
    eoscp_command = "xrdcp " + cern_tmp_path + " " + "root://eoscms/" + cern_eos_path  + " >> log.txt 2>&1 "

    print "\tChecking CERN EOS:",
    if eosls_stdout.strip() == os.path.basename(file):
        print cern_eos_path, "exists!  Skipping."
        continue
    else:
        print "All clear"

    print "\tClearing CERN scratch"
    if os.path.isfile(cern_tmp_path):
        os.system ("rm " + cern_tmp_path)
        
    print "\tCopying from FNAL EOS to CERN scratch..."
    os.system ( tmpcp_command ) 
    print "\tCopying from CERN scratch to CERN EOS..."
    os.system ( eoscp_command ) 
    print "\tDone!"
    
print "All done!"
