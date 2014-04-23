python scripts/launch_analysis.py \
-c ../HcalReco/test/hcalNoise_fromGEN-SIM_toGEN-SIM-RAW_62X_withMixer_cfg.py \
-w $PWD/work/HcalNoise_QCD1800_GEN-SIM-RAW_MC \
-n 900 \
-q 1nh \
-i file_lists/QCD_Pt-1800_TuneZ2star_13TeV/inputListAll.txt \
-p file_lists/MinBias_TuneZ2star_13TeV/inputListAll.txt \
-o HcalNoise_QCD1800_GEN-SIM-RAW_MC \
-t "auto:mc" \
-e /eos/uscms/store/user/eberry/QCD1800MC_GEN-SIM-RAW/
