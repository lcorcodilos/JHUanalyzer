# 2017 version which uses central NanoAOD
import subprocess

input_subs = {
    "ttbar":"/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "ttbar-semilep":"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    # "QCDHT700":"/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "dataB":"/JetHT/Run2017B-Nano1June2019-v1/NANOAOD",
    "dataC":"/JetHT/Run2017C-Nano1June2019-v1/NANOAOD",
    "dataD":"/JetHT/Run2017D-Nano1June2019-v1/NANOAOD",
    "dataE":"/JetHT/Run2017E-Nano1June2019-v1/NANOAOD",
    "dataF":"/JetHT/Run2017F-Nano1June2019-v1/NANOAOD",
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


