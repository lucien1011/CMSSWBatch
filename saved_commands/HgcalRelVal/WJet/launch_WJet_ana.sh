python scripts/launch_analysis.py \
-c ../HGCALANA/HgcalTupleMaker/analysis_cfg.py \
-w $PWD/work/HgcalRelVal_WJet_ANA \
-n 100 \
-q 1nh \
-i file_lists/HgcalRelVal_WJet_RECO/inputListAll.txt \
-o HgcalRelVal_WJet_MC_ANA \
-t "auto:mc" \
-e /eos/cms/store/user/eberry/HGCAL/HgcalRelVal_WJet_MC_SLHC21_ANA/
