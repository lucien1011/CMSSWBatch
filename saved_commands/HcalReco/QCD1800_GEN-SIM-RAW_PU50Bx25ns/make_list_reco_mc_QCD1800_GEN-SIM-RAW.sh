# QCD for signal
# /QCD_Pt-1800_TuneZ2star_13TeV_pythia6/Fall13-POSTLS162_V1-v1/GEN-SIM

python scripts/make_file_list.py \
-i /pnfs/cms/WAX/11/store/mc/Fall13/QCD_Pt-1800_TuneZ2star_13TeV_pythia6/GEN-SIM/POSTLS162_V1-v1/30000/ \
-o file_lists/QCD_Pt-1800_TuneZ2star_13TeV

# MinBias for pileup
# /MinBias_TuneZ2star_13TeV-pythia6/Summer13-START53_V7C-v1/GEN-SIM

python scripts/make_file_list.py \
-i /pnfs/cms/WAX/11/store/mc/Summer13/MinBias_TuneZ2star_13TeV-pythia6/GEN-SIM/START53_V7C-v1/10000/ \
-o file_lists/MinBias_TuneZ2star_13TeV

