#----------------------------------------------------------------------------
# Imports
#----------------------------------------------------------------------------

import subprocess as sp
import sys, os
import argparse

#----------------------------------------------------------------------------
# Get input and output folders
# NB: only EOS folders are currently supported
#----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Make an input list')
parser.add_argument('-i', metavar='INPUT' , dest='input_folders',action="append", required=True, help='List of EOS folders to be used as input')
parser.add_argument('-o', metavar="OUTPUT", dest='output_folder',action="store" , required=True, help='Output folder where input list will be stored')
args = parser.parse_args()

#----------------------------------------------------------------------------
# Get the latest/greatest EOS binary
#----------------------------------------------------------------------------

eos_bin = sp.Popen ( "find /afs/cern.ch/project/eos/installation/ -name 'eos.select' | xargs ls -rt1 | tail -1", shell=True, stdout=sp.PIPE ).communicate()[0].strip()

#----------------------------------------------------------------------------
# Get list of file paths in EOS
#----------------------------------------------------------------------------

eos_file_paths = []
for eos_folder in args.input_folders:
    eos_ls_command = eos_bin + " ls " + eos_folder 
    eos_files      = sp.Popen ( eos_ls_command, shell=True, stdout=sp.PIPE ).communicate()[0].split()
    eos_file_paths = eos_file_paths + ["\"root://eoscms/" + eos_folder + "/" + i + "\"," for i in eos_files]

#----------------------------------------------------------------------------
# If the output directory does not exist, create it
#----------------------------------------------------------------------------

if not os.path.isdir ( args.output_folder ):
    os.system ( "mkdir -p " + args.output_folder )

#----------------------------------------------------------------------------
# Write the output list
#----------------------------------------------------------------------------

output_file_path = args.output_folder + "/inputListAll.txt"
output_file = open (output_file_path,"w")
for path in eos_file_paths:
    output_file.write(path + "\n")
output_file.close()

#----------------------------------------------------------------------------
# Tell the user that we're done
#----------------------------------------------------------------------------

print "Success! I wrote an input list:"
print "\t", output_file_path

