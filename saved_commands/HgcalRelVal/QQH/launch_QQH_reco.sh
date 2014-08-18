python scripts/launch_analysis.py \
-c ../tmp/step3_RAW2DIGI_L1Reco_RECO.py \
-w $PWD/work/HgcalRelVal_QQH_RECO \
-n 100 \
-q 1nh \
-i file_lists/HgcalRelVal_QQH_DIGI-RAW/inputListAll.txt \
-o HgcalRelVal_QQH_MC_RECO \
-t "auto:mc" \
-e /eos/cms/store/user/eberry/HGCAL/HgcalRelVal_QQH_MC_RECO/
