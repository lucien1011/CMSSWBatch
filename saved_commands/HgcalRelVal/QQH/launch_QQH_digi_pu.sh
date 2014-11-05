python scripts/launch_analysis.py \
-c ../HGCALANA/HgcalTupleMaker/mc_production/step2_DIGI_L1_DIGI2RAW_PU140_BX25.py \
-w $PWD/work/HgcalRelVal_QQH_DIGI-RAW-PU \
-n 100 \
-p file_lists/MinBias/inputListAll.txt \
-q 8nh \
-i file_lists/HgcalRelVal_QQH_GEN-SIM/inputListAll.txt \
-o HgcalRelVal_QQH_MC_DIGI-RAW-PU \
-t "auto:mc" \
-e /eos/cms/store/user/eberry/HGCAL/HgcalRelVal_QQH_MC_DIGI-RAW-PU/
