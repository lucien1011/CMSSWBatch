Scripts to run batch jobs of CMSSW python config files

Supported releases:
  * All CMSSW releases

Recipe:
  * git clone git@github.com:edmundaberry/CMSSWBatch.git batch
  * Make input lists with scripts/make_file_list.py
  * Launch analysis with scripts/launch_analysis.py
  * Check output with scripts/check_output.py    (coming soon)

Tags:
  * V00-00-00: Initial commit
  * V00-00-01: Added output file name functionality to launch_analysis script
  * V00-01-00: Added some saved commands.  Added EOS functionality.