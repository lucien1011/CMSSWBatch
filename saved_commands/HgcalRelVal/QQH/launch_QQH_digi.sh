python scripts/launch_analysis.py \
-c ../HGCALANA/HgcalTupleMaker/mc_production/step2_DIGI_L1_DIGI2RAW.py \
-w $PWD/work/HgcalRelVal_QQH_DIGI-RAW \
-n 100 \
-q 1nh \
-i file_lists/HgcalRelVal_QQH_GEN-SIM/inputListAll.txt \
-o HgcalRelVal_QQH_MC_DIGI-RAW \
-t "auto:mc" \
-e /eos/cms/store/user/eberry/HGCAL/HgcalRelVal_QQH_MC_DIGI-RAW/
