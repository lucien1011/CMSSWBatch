python scripts/launch_analysis.py \
-c ../HcalReco/test/hcalNoise_fromGEN-SIM_62X_cfg.py \
-w $PWD/work/HcalNoise_QCD1800_MC \
-n 500 \
-q 1nh \
-i file_lists/QCD_Pt-1800_TuneZ2star_13TeV/inputListAll.txt \
-o HcalNoise_QCD1800_MC \
-t "auto:mc" \
-e /eos/uscms/store/user/eberry/QCD1800MC/
