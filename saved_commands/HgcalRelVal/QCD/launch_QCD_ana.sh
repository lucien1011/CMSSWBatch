python scripts/launch_analysis.py \
-c ../HGCALANA/HgcalTupleMaker/analysis_pandora_cfg.py \
-w $PWD/work/HgcalRelVal_QCD_ANA \
-n 500 \
-q 8nh \
-i file_lists/HgcalRelVal_QCD_RECO/inputListAll.txt \
-o HgcalRelVal_QCD_MC_ANA \
-t "auto:mc" \
-e /eos/cms/store/user/eberry/HGCAL/HgcalRelVal_QCD_MC_SLHC25_patch1_ANA/
