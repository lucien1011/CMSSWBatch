python scripts/launch_analysis.py \
-c ../HCALPFG/HcalTupleMaker/test/analysis_splash_cfg.py \
-w $PWD/work/UnstableCollisions \
-n 500 \
-q 1nh \
-i file_lists/UnstableCollisions/inputListAll.txt \
-o HcalTupleMaker_UnstableCollisions \
-t "auto:mc" \
-e /eos/cms/store/user/eberry/UnstableCollisions/
