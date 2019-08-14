#!/bin/bash
echo "Run script starting"
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/lcorcodi/10_6_2.tgz ./
export SCRAM_ARCH=slc7_amd64_gcc700
scramv1 project CMSSW CMSSW_10_6_2
tar -xzf 10_6_2.tgz
rm 10_6_2.tgz

mkdir tardir; cp tarball.tgz tardir/; cd tardir/
tar -xzf tarball.tgz; rm tarball.tgz
cp -r * CMSSW_10_6_2/src/; cd ../CMSSW_10_6_2/src/
git clone git@github.com:lcorcodilos/JHUanalyzer.git
cd JHUanalyzer; git checkout rdfDev; cd ../
eval `scramv1 runtime -sh`

echo hh16_preselection.py $*
python hh16_preselection.py $*
