python scripts/launch_analysis.py \
-c ../HcalReco/test/hcalNoise_fromGEN-SIM-RAW_62X_cfg.py \
-w $PWD/work/HcalNoise_QCD1800_RAW2DIGI-RECO_MC \
-n 1 \
-q 1nh \
-i file_lists/QCD_Pt-1800_TuneZ2star_13TeV_GEN-SIM-RAW/inputListAll.txt \
-o HcalNoise_QCD1800_PU50_MC \
-t "auto:mc" \
-e /eos/uscms/store/user/eberry/QCD1800MC_PU50/
