# 2017 version which uses central NanoAOD rather than JHitos
import pickle
import subprocess
import glob

# Just grabbing the basic centrally produced nanoAOD so this will be different from the 2016 version
input_subs = {
    "ttbar":"/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16NanoAODv3-PUMoriond17_backup_94X_mcRun2_asymptotic_v3-v2/NANOAODSIM",
    "singletop_tW":"/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/NANOAODSIM",
    "singletop_tWB":"/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/NANOAODSIM",
    "singletop_t":"/ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/NANOAODSIM",
    "singletop_tB":"/ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/NANOAODSIM",
    "QCDHT2000ext":"/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/NANOAODSIM",
    "QCDHT1500ext":"/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/NANOAODSIM",
    "QCDHT1000ext":"/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/NANOAODSIM",
    #"dataA":"",
    "dataB":"/JetHT/Run2016B_ver1-Nano14Dec2018_ver1-v1/NANOAOD",
    "dataB2":"/JetHT/Run2016B_ver2-Nano14Dec2018_ver2-v1/NANOAOD",
    "dataC":"/JetHT/Run2016C-Nano14Dec2018-v1/NANOAOD",
    "dataD":"/JetHT/Run2016D-Nano14Dec2018-v1/NANOAOD",
    "dataE":"/JetHT/Run2016E-Nano14Dec2018-v1/NANOAOD",
    "dataF":"/JetHT/Run2016F-Nano14Dec2018-v1/NANOAOD",
    "dataG":"/JetHT/Run2016G-Nano14Dec2018-v1/NANOAOD",
    "dataH":"/JetHT/Run2016H-Nano14Dec2018-v1/NANOAOD",
    "signalLH1200":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH1400":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH1600":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH1800":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH2000":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH2200":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH2400":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH2600":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH2800":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalLH3000":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH1200":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH1400":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH1600":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH1800":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH2000":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH2200":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH2400":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH2600":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH2800":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    "signalRH3000":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root"

}
executables = []

# loj = open('../../treeMaker.listOfJobs','w')

for i in input_subs.keys():
    if 'signal' in i:
        files = glob.glob('/eos/uscms'+input_subs[i])
        out = open(i+'_loc.txt','w')
        for f in files:
            out.write(f.replace('/eos/uscms','root://cmsxrootd.fnal.gov/')+'\n')
        out.close

        # executables.append('dasgoclient -query "file dataset='+input_subs[i]+' instance=prod/phys03" > '+i+'_loc.txt')
    else:
        executables.append('dasgoclient -query "file dataset='+input_subs[i]+'" > '+i+'_loc.txt')
    # loj.write("python tardir/bstarTreeMaker.py "+i+'\n')
for s in executables:
    print s
    subprocess.call([s],shell=True)


