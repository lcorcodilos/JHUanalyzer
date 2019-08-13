# 2018 version which uses central NanoAOD rather than JHitos
import pickle
import subprocess

# Just grabbing the basic centrally produced nanoAOD so this will be different from the 2016 version
input_subs = {
    "ttbar":"/store/user/lcorcodi/NanoAOD102X_private/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/*/*/*.root",
    # "ttbar-semilep":"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    # "QCDHT700":"/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAOD-102X_upgrade2018_realistic_v15-v1/NANOAODSIM",
    # "QCDHT2000":"/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAOD-102X_upgrade2018_realistic_v15-v1/NANOAODSIM",
    # "QCDHT1500":"/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAOD-102X_upgrade2018_realistic_v15-v1/NANOAODSIM",
    # "QCDHT1000":"/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAOD-102X_upgrade2018_realistic_v15-v1/NANOAODSIM",
    "dataA":"/JetHT/Run2018A-Nano1June2019-v2/NANOAOD",
    "dataB":"/JetHT/Run2018B-Nano1June2019-v2/NANOAOD ",
    "dataC1":"/JetHT/Run2018C-Nano1June2019-v1/NANOAOD",
    "dataC2":"/JetHT/Run2018C-Nano1June2019-v2/NANOAOD",
    "dataD":"/JetHT/Run2018D-Nano1June2019_ver2-v1/NANOAOD",

    "GravNar-1000":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "GravNar-1500":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "GravNar-2000":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "GravNar-2500":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-2500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "GravNar-3000":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-2500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-1000":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-1500":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-2000":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-2500":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-2500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-3000":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-3000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",

    "WWW-M1500-R0-4":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M1500-R0-4_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v4_CustomNANOAOD/190530_141205/0000/myNanoProdMc_NANO_*.root",
    "WWW-M2000-R0-1":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M2000-R0-1_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_141036/0000/myNanoProdMc_NANO_*.root",
    "WWW-M2000-R0-2":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M2000-R0-2_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_140904/0000/myNanoProdMc_NANO_*.root",
    "WWW-M2000-R0-3":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M2000-R0-3_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_140736/0000/myNanoProdMc_NANO_*.root",
    "WWW-M2500-R0-08":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M2500-R0-08_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_140601/0000/myNanoProdMc_NANO_*.root",
    "WWW-M2500-R0-1":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M2500-R0-1_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_140431/0000/myNanoProdMc_NANO_*.root",
    "WWW-M2500-R0-2":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M2500-R0-2_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_140259/0000/myNanoProdMc_NANO_*.root",
    "WWW-M2500-R0-3":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M2500-R0-3_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_140124/0000/myNanoProdMc_NANO_*.root",
    "WWW-M3000-R0-06":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3000-R0-06_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_135948/0000/myNanoProdMc_NANO_*.root",
    "WWW-M3000-R0-08":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3000-R0-08_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_135813/0000/myNanoProdMc_NANO_*.root",
    "WWW-M3000-R0-1":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3000-R0-1_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_135640/0000/myNanoProdMc_NANO_*.root",
    "WWW-M3000-R0-2":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3000-R0-2_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_135452/0000/myNanoProdMc_NANO_*.root",
    "WWW-M3000-R0-3":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3000-R0-3_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_135323/0000/myNanoProdMc_NANO_*.root",
    "WWW-M3500-R0-06":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3500-R0-06_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_135129/0000/myNanoProdMc_NANO_*.root",
    "WWW-M3500-R0-08":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3500-R0-08_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_134955/0000/myNanoProdMc_NANO_*.root",
    "WWW-M3500-R0-1":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3500-R0-1_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_134812/0000/myNanoProdMc_NANO_1.root",
    "WWW-M3500-R0-2":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M3500-R0-2_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_134224/0000/myNanoProdMc_NANO_*.root",
    "WWW-M4000-R0-06":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M4000-R0-06_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v3_CustomNANOAOD/190530_133912/0000/myNanoProdMc_NANO_*.root",
    "WWW-M4000-R0-08":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M4000-R0-08_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_133732/0000/myNanoProdMc_NANO_*.root",
    "WWW-M4000-R0-1":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M4000-R0-1_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_133600/0000/myNanoProdMc_NANO_*.root",
    "WWW-M4000-R0-2":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M4000-R0-2_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_133426/0000/myNanoProdMc_NANO_*.root",
    "WWW-M4500-R0-2":"/store/user/cmantill/CustomNANOAOD/WkkToWRadionToWWW_M4500-R0-2_TuneCP5_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2_CustomNANOAOD/190530_134630/0000/myNanoProdMc_NANO_*.root "


}
executables = []

executables.append('rm *_loc.txt')
for i in input_subs.keys():
    if '/store/user' in input_subs[i]:
        executables.append('ls /eos/uscms'+input_subs[i]+' > '+i+'_loc.txt')
        executables.append('sed -i s%/eos/uscms/%/%g '+i+'_loc.txt')
    else:
        executables.append('dasgoclient -query "file dataset='+input_subs[i]+'" > '+i+'_loc.txt')
for s in executables:
    print 'Executing: '+s
    subprocess.call([s],shell=True)


