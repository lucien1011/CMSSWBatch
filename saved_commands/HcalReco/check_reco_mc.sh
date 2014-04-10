python scripts/check_output.py \
-c hcalNoise_cfg.py \
-w $PWD/work/HcalNoise_MinBias_MC \
-n 1 \
-q 1nh \
-i file_lists/MinBias_TuneZ2star_13TeV/inputListAll_1.txt \
-o HcalNoise_MinBias_MC \
-t "auto:mc" \
-e /eos/uscms/store/user/eberry/MinBiasMC/
