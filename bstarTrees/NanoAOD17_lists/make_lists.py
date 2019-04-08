# 2017 version which uses central NanoAOD rather than JHitos
import pickle
import subprocess

# Just grabbing the basic centrally produced nanoAOD so this will be different from the 2016 version
input_subs = {
    "ttbar":"/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "singletop_tW":"/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/NANOAODSIM",
    "singletop_tWB":"/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/NANOAODSIM",
    "singletop_t":"/ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "singletop_tB":"/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    #"dataA":"",
    "dataB":"/JetHT/Run2017B-Nano14Dec2018-v1/NANOAOD",
    "dataC":"/JetHT/Run2017C-Nano14Dec2018-v1/NANOAOD",
    "dataD":"/JetHT/Run2017D-Nano14Dec2018-v1/NANOAOD",
    "dataE":"/JetHT/Run2017E-Nano14Dec2018-v1/NANOAOD",
    "dataF":"/JetHT/Run2017F-Nano14Dec2018-v1/NANOAOD",
    # "signalLH1200":"BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH1400":"BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH1600":"BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH1800":"BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH2000":"BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH2200":"BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH2400":"BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH2600":"BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH2800":"BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalLH3000":"BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH1200":"BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH1400":"BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH1600":"BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH1800":"BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH2000":"BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH2200":"BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH2400":"BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH2600":"BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH2800":"BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1",
    # "signalRH3000":"BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1"

}
executables = []

# loj = open('../../treeMaker.listOfJobs','w')

for i in input_subs.keys():
    executables.append('dasgoclient -query "file dataset='+input_subs[i]+'" > '+i+'_loc.txt')
    # loj.write("python tardir/bstarTreeMaker.py "+i+'\n')
for s in executables:
    subprocess.call([s],shell=True)


