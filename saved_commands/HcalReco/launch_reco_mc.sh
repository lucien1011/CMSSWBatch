python scripts/launch_analysis.py \
-c ../HcalReco/test/hcalNoise_fromGEN-SIM_cfg.py \
-w $PWD/work/HcalNoise_MinBias_MC \
-n 500 \
-q 1nh \
-i file_lists/MinBias_TuneZ2star_13TeV/inputListAll.txt \
-o HcalNoise_MinBias_MC \
-t "auto:mc" \
-e /eos/uscms/store/user/eberry/MinBiasMC/
