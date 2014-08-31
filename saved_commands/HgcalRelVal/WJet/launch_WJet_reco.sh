python scripts/launch_analysis.py \
-c ../HGCALANA/HgcalTupleMaker/mc_production/step3_RAW2DIGI_L1Reco_RECO.py \
-w $PWD/work/HgcalRelVal_WJet_RECO \
-n 100 \
-q 1nh \
-i file_lists/HgcalRelVal_WJet_DIGI-RAW/inputListAll.txt \
-o HgcalRelVal_WJet_MC_RECO \
-t "auto:mc" \
-e /eos/cms/store/user/eberry/HGCAL/HgcalRelVal_WJet_MC_RECO/
