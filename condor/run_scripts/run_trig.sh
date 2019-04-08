#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/lcorcodi/10XwithNano.tgz ./
export SCRAM_ARCH=slc6_amd64_gcc700
scramv1 project CMSSW CMSSW_10_2_0
tar -xzf 10XwithNano.tgz
rm 10XwithNano.tgz

mkdir tardir; cp tarball.tgz tardir/; cd tardir
tar xzvf tarball.tgz
cp -r * ../CMSSW_10_2_0/src/BStar13TeV/
cd ../CMSSW_10_2_0/src/BStar13TeV/
eval `scramv1 runtime -sh`

echo TWTrigger.py $*
python TWTrigger.py $*
cp TWTrigger*job*.root ../../../

