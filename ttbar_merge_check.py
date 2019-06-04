#####################################################################
# GenParticleChecker.py - Lucas Corcodilos 5/3/19                   #
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
    # ak8JetsColl = Collection(event, 'FatJet')
    genParticlesColl = Collection(event, 'GenPart')

    # if not (ak8JetsColl[0].pt > 400 and ak8JetsColl[1] > 400):
    #   continue

    # jet1,jet2 = TLorentzVector(),TLorentzVector()
    # jet1,jet2 = jet1.SetPtEtaPhiM(ak8JetsColl[0].pt, ak8JetsColl[0].eta, ak8JetsColl[0].phi, ak8JetsColl[0].msoftdrop), jet2.SetPtEtaPhiM(ak8JetsColl[1].pt, ak8JetsColl[1].eta, ak8JetsColl[1].phi, ak8JetsColl[1].msoftdrop)

    # top_indices = []
    # w_indices = []
    # b_indices = []
    # q_indices = []

    particle_tree = GenParticleTree()

    for i,p in enumerate(genParticlesColl):
        # Internal class info
        this_gen_part = GenParticleObj(i,p)
        this_gen_part.SetStatusFlags(constants.GenParticleStatusFlags)
        this_gen_part.SetPDGName(constants.PDGIds,abs(this_gen_part.pdgId))
        

        if abs(this_gen_part.pdgId) == 6:# and this_gen_part.status == 62: # 22 means intermediate part of hardest subprocess, only other to appear is 62 (outgoing subprocess particle with primordial kT included)
            particle_tree.AddParticle(this_gen_part)
            # top_indices.append(i)

        elif abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
            particle_tree.AddParticle(this_gen_part)
            # w_indices.append(i)

        elif abs(this_gen_part.pdgId) == 5:# and this_gen_part.status == 23:
            particle_tree.AddParticle(this_gen_part)
            # b_indices.append(i) # 23 means outgoing part of hardest subprocess, only other option is 52 (above), 71 (copied partons to collect into contiguous colour singlet) or 73 (combination of very nearby partons into one)



        # elif abs(this_gen_part.pdgId) >=1 and abs(this_gen_part.pdgId) <= 5:
        #     q_indices.append(i)

    particle_tree.PrintTree(entry,options=['status','statusFlags:fromHardProcess'])
    raw_input('')

    # top_family_tree = {}
    # for t in top_indices:
    #     top_family_tree[t] = {'bquark':-1,'Wboson':-1}

    # # See if we can trace back the Ws and bs
    # for ibottom in b_indices:
    #     this_bquark = GenParticleObj(ibottom, genParticlesColl[ibottom])
    #     for itop in top_indices:
    #         if this_bquark.motherIdx == itop:
    #             # print 'Found daughter bottom of top'
    #             top_family_tree[itop]['bquark'] = ibottom

    # for iW in w_indices:
    #     this_wboson = GenParticleObj(iW, genParticlesColl[iW])
    #     for itop in top_indices:
    #         if this_wboson.motherIdx == itop:
    #             # print 'Found daughter W of top'
    #             top_family_tree[itop]['Wboson'] = iW

    # for top in top_family_tree.keys():
    #     if top_family_tree[top]['bquark'] == -1 or top_family_tree[top]['Wboson'] == -1:
    #         print 'Failed to find bottom and W: %s' % count


