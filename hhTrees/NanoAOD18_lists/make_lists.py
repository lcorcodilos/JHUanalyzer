# 2018 version which uses central NanoAOD rather than JHitos
import pickle
import subprocess

# Just grabbing the basic centrally produced nanoAOD so this will be different from the 2016 version
input_subs = {
    "ttbar":"/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "ttbar_semilep":"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAOD-102X_upgrade2018_realistic_v15-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAOD-102X_upgrade2018_realistic_v15-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAOD-102X_upgrade2018_realistic_v15-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAOD-102X_upgrade2018_realistic_v15-v1/NANOAODSIM",
    "dataA":"/JetHT/Run2018A-Nano14Dec2018-v1/NANOAOD",
    "dataB":"/JetHT/Run2018B-Nano14Dec2018-v1/NANOAOD",
    "dataC":"/JetHT/Run2018C-Nano14Dec2018-v1/NANOAOD",
    "dataD":"/JetHT/Run2018D-Nano14Dec2018_ver2-v1/NANOAOD",

    "RadNar_1000":"/RadionTohhTohbbhbb_narrow_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    # "RadNar_1200":"/RadionTohhTohbbhbb_narrow_M-1200_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadNar_1500":"/RadionTohhTohbbhbb_narrow_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadNar_2000":"/RadionTohhTohbbhbb_narrow_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadNar_2500":"/RadionTohhTohbbhbb_narrow_M-2500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadNar_3000":"/RadionTohhTohbbhbb_narrow_M-3000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",

    "RadWid05_1000":"/RadionTohhTohbbhbb_width0p05_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadWid05_1500":"/RadionTohhTohbbhbb_width0p05_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadWid05_2000":"/RadionTohhTohbbhbb_width0p05_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadWid05_2400":"/RadionTohhTohbbhbb_width0p05_M-2400_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadWid05_3000":"/RadionTohhTohbbhbb_width0p05_M-3000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",

    "RadWid10_1500":"/RadionTohhTohbbhbb_width0p10_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadWid10_2000":"/RadionTohhTohbbhbb_width0p10_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadWid10_2400":"/RadionTohhTohbbhbb_width0p10_M-2400_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "RadWid10_3000":"/RadionTohhTohbbhbb_width0p10_M-3000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",

    "GravNar_1000":"/BulkGravTohhTohbbhbb_narrow_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravNar_1500":"/BulkGravTohhTohbbhbb_narrow_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravNar_2000":"/BulkGravTohhTohbbhbb_narrow_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravNar_2500":"/BulkGravTohhTohbbhbb_narrow_M-2500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravNar_3000":"/BulkGravTohhTohbbhbb_narrow_M-30000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",

    "GravWid05_1000":"/BulkGravTohhTohbbhbb_width0p05_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravWid05_1500":"/BulkGravTohhTohbbhbb_width0p05_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravWid05_2000":"/BulkGravTohhTohbbhbb_width0p05_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravWid05_2400":"/BulkGravTohhTohbbhbb_width0p05_M-2400_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravWid05_3000":"/BulkGravTohhTohbbhbb_width0p05_M-30000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",

    "GravWid10_1000":"/BulkGravTohhTohbbhbb_width0p05_M-1000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravWid10_1500":"/BulkGravTohhTohbbhbb_width0p05_M-1500_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravWid10_2000":"/BulkGravTohhTohbbhbb_width0p05_M-2000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravWid10_2400":"/BulkGravTohhTohbbhbb_width0p05_M-2400_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",
    "GravWid10_3000":"/BulkGravTohhTohbbhbb_width0p05_M-30000_TuneCP2_PSweights_13TeV-madgraph_pythia8/RunIIAutumn18NanoAODv4-Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/NANOAODSIM",

}
executables = []

# loj = open('../../treeMaker.listOfJobs','w')

for i in input_subs.keys():
    executables.append('dasgoclient -query "file dataset='+input_subs[i]+'" > '+i+'_loc.txt')
    # loj.write("python tardir/bstarTreeMaker.py "+i+'\n')
for s in executables:
    subprocess.call([s],shell=True)


