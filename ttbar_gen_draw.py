#####################################################################
# ttbar_gen_draw.py - Lucas Corcodilos 5/4/19                       #
# -----------------------------------------------                   #
# Script to make a generator particle tree from ttbar all-hadronic  #
# decays in NanoAOD format where we attempt to identify the         #
# the daughter Ws and bs.                                           #
# -----------------------------------------------                   #
# Prerequisites                                                     #
# -----------------------------------------------                   #
# * `pip install graphviz` -> python interface to graphiz           #
# * Download and install actual graphviz from here                  # 
#   https://graphviz.gitlab.io/_pages/Download/Download_source.html #
# * Will not work on CMSSW because of these dependencies            #
#####################################################################

import ROOT
from ROOT import *
import math, sys, os
import pprint 
pp = pprint.PrettyPrinter(indent=4)
import GenParticleChecker
from GenParticleChecker import *

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.JetSysColl import JetSysColl, JetSysObj
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim

#####################
#####################
## Begin main code ##
#####################
#####################
constants = GenParticleConstants()

if os.environ.get('CMSSW_BASE') == None:
    file = TFile.Open('~/CMS/temp/ttbar_bstar18.root')
else:
    file = TFile.Open('root://cmseos.fnal.gov//store/user/lcorcodi/bstar_nano/rootfiles/ttbar_bstar18.root')

################################
# Grab event tree from nanoAOD #
################################
inTree = file.Get("Events")
elist,jsonFiter = preSkim(inTree,None,'')
inTree = InputTree(inTree,elist)
treeEntries = inTree.entries

count = 0

##############
# Begin Loop #
##############
nevents = 10000
for entry in range(0,nevents):
    count   =   count + 1
    sys.stdout.write("%i / %i ... \r" % (count,nevents))
    sys.stdout.flush()

    # Grab the event
    event = Event(inTree, entry)

    # Have to grab Collections for each collection of interest
    # -- collections are for types of objects where there could be multiple values
    #    for a single event
    genParticlesColl = Collection(event, 'GenPart')

    particle_tree = GenParticleTree()

    for i,p in enumerate(genParticlesColl):
        # Internal class info
        this_gen_part = GenParticleObj(i,p)
        this_gen_part.SetStatusFlags(constants.GenParticleStatusFlags)
        this_gen_part.SetPDGName(constants.PDGIds,abs(this_gen_part.pdgId))
        

        if abs(this_gen_part.pdgId) == 6:# and this_gen_part.status == 62: # 22 means intermediate part of hardest subprocess, only other to appear is 62 (outgoing subprocess particle with primordial kT included)
            particle_tree.AddParticle(this_gen_part)

        elif abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
            particle_tree.AddParticle(this_gen_part)

        elif abs(this_gen_part.pdgId) == 5:# and this_gen_part.status == 23:
            particle_tree.AddParticle(this_gen_part)


    particle_tree.PrintTree(entry,options=['status','statusFlags:fromHardProcess'])
    raw_input('')

