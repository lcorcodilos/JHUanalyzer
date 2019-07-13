# 2016 version which uses central NanoAOD
import subprocess, glob

input_subs = {
    "ttbar":"/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT700ext":"/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT2000ext":"/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT1500ext":"/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT1000ext":"/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "dataB2":"/JetHT/Run2016B_ver2-Nano1June2019_ver2-v2/NANOAOD",
    "dataC":"/JetHT/Run2016C-Nano1June2019-v1/NANOAOD",
    "dataD":"/JetHT/Run2016D-Nano1June2019-v1/NANOAOD",
    "dataE":"/JetHT/Run2016E-Nano1June2019-v1/NANOAOD",
    "dataF":"/JetHT/Run2016F-Nano1June2019-v1/NANOAOD",
    "dataG":"/JetHT/Run2016G-Nano1June2019-v1/NANOAOD",
    "dataH":"/JetHT/Run2016H-Nano1June2019-v1/NANOAOD",
}
executables = []

# Remove files first
print 'rm *_loc.txt'
subprocess.call(['rm *_loc.txt'],shell=True)

for i in input_subs.keys():
    if '/store/user/' in input_subs[i]:
        files = glob.glob('/eos/uscms'+input_subs[i])
        out = open(i+'_loc.txt','w')
        for f in files:
            out.write(f.replace('/eos/uscms','root://cmsxrootd.fnal.gov/')+'\n')
        out.close()
    else:
        executables.append('dasgoclient -query "file dataset='+input_subs[i]+'" > '+i+'_loc.txt')
for s in executables:
    print s
    subprocess.call([s],shell=True)


