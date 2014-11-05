python scripts/launch_analysis.py \
-c ../HGCALANA/HgcalTupleMaker/mc_production/step3_RAW2DIGI_L1Reco_RECO.py \
-w $PWD/work/HgcalRelVal_QQH_RECO_PU \
-n 100 \
-q 8nh \
-i file_lists/HgcalRelVal_QQH_DIGI-RAW/inputListAll.txt \
-o HgcalRelVal_QQH_MC_RECO \
-t "auto:mc" \
-e /eos/cms/store/user/eberry/HGCAL/HgcalRelVal_QQH_MC_RECO_PU/
