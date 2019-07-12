# 2018 version which uses central NanoAOD rather than JHitos
import pickle
import subprocess

# Just grabbing the basic centrally produced nanoAOD so this will be different from the 2016 version
input_subs = {
    #"ttbar":"/store/user/lcorcodi/NanoAOD102X_private/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/*/*/*.root",
    # "ttbar-semilep":"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    #"QCDHT700":"/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    #"QCDHT1000":"/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    #"QCDHT1500":"/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    #"QCDHT2000":"/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    #"dataA":"/JetHT/Run2018A-Nano1June2019-v2/NANOAOD",
    #"dataB":"/JetHT/Run2018B-Nano1June2019-v2/NANOAOD ",
    #"dataC1":"/JetHT/Run2018C-Nano1June2019-v1/NANOAOD",
    #"dataC2":"/JetHT/Run2018C-Nano1June2019-v2/NANOAOD",
    #"dataD":"/JetHT/Run2018D-Nano1June2019_ver2-v1/NANOAOD",

    #"GravNar-1000":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    #"GravNar-1500":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    #"GravNar-2000":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    #"GravNar-2500":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-2500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    #"GravNar-3000":"/store/user/lcorcodi/NanoAOD102X_private/BulkGravTohhTohbbhbb_narrow_M-2500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-1000":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-1500":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-2000":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-2500":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-2500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root",
    "RadNar-3000":"/store/user/lcorcodi/NanoAOD102X_private/RadionTohhTohbbhbb_narrow_M-3000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/*/0000/*.root"


}
executables = []

# loj = open('../../treeMaker.listOfJobs','w')

for i in input_subs.keys():
    if '/store/user' in input_subs[i]:
        executables.append('ls /eos/uscms'+input_subs[i]+' > '+i+'_loc.txt')
        executables.append('sed -i s%/eos/uscms/%/%g '+i+'_loc.txt')
    else:
        executables.append('dasgoclient -query "file dataset='+input_subs[i]+'" > '+i+'_loc.txt')
for s in executables:
    print 'Executing: '+s
    subprocess.call([s],shell=True)


