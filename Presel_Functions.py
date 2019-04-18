
##################################################################
##                                                              ##
## Name: Bstar_Functions.py                                     ##
## Author: Kevin Nash                                           ##
## Date: 5/13/2015                                              ##
## Purpose: This contains all functions used by the             ##
##      analysis.  A method is generally placed here if         ##
##      it is called more than once in reproducing all          ##
##      analysis results.  The functions contained here         ##
##      Are capable of tuning the analysis - such as changing   ##
##      cross sections, updating lumi, changing file            ##
##      locations, etc. with all changes propegating            ##
##      to all relevant files automatically.                    ##
##                                                              ##
##################################################################

import os
import array
import glob
import math
import itertools
from random import random
from math import sqrt, exp, log
import ROOT
import sys
import time
import subprocess
import cppyy
import pickle
from array import *
from ROOT import *
from PhysicsTools.NanoAODTools.postprocessing.tools import *

#This is the most impostant Function.  Correct information here is essential to obtaining valid results.
#In order we have Luminosity, top tagging scale factor, cross sections for wprime right,left,mixed,ttbar,qcd, and singletop and their corresponding event numbers
#If I wanted to access the left handed W' cross section at 1900 GeV I could do Xsecl1900 = LoadConstants()['xsec_wpl']['1900']
def LoadConstants(year):
    constants = {
        'QCDHT700_xsec':6802,
        'QCDHT1000_xsec':1206,
        'QCDHT1500_xsec':120.4,
        'QCDHT2000_xsec':25.25,
        'GravNar_1000_xsec':2.66,
        # 'GravNar_1500_xsec':,
        'GravNar_2000_xsec':0.041,
        'GravNar_2500_xsec':0.007,
        'GravNar_3000_xsec':0.0017
    }
    if year == '16':
        constants['ttbar_xsec'] = 831.76,
        constants['lumi'] = 35872.301001
        
    elif year == '17':
        constants['lumi'] = 41518.865298,#35851.0,
        constants['ttbar_xsec'] = 377.96 #uncertainty +4.8%-6.1%
        constants['ttbar_semilep_xsec'] = 365.34

    elif year == '18':
        constants['lumi'] = 59660.725495,
        constants['ttbar_xsec'] = 377.96, #uncertainty +4.8%-6.1%
        constants['ttbar_semilep_xsec'] = 365.34
        
    return constants
    
def LoadCuts(region,year):
    cuts = {
        'hpt':[400.0,float("inf")],
        'bpt':[50.0,float("inf")],
        'hmass':[105.0,135.0],
        'bbmass':[90.,140.],
        'deepbtag':[0.4184,1.0],
        'doublebtag':[0.8,1.0],
        'eta':[0.0,2.4]
        'deltaEta':[0.0,2.0]
        'mreduced':[750.,float('inf')]
    }

    return cuts

#This function loads up Ntuples based on what type of set you want to analyze.  
#This needs to be updated whenever new Ntuples are produced (unless the file locations are the same).
def Load_jetNano(string,year):
    print 'running on ' + string 
    return 'root://cmseos.fnal.gov//store/user/lcorcodi/bstar_nano/rootfiles/'+string+'_hh'+year+'.root'


def PDF_Lookup(pdfs , pdfOP ):
    # Computes the variance of the pdf weights to estimate the up and down uncertainty for each set (event)
    ilimweight = 0.0

    limitedpdf = []
    for ipdf in range(pdfs.GetSize()):
        curpdf = pdfs[ipdf]
        if abs(curpdf)<1000.0:
            limitedpdf.append(curpdf)

    if len(limitedpdf) == 0:
        return 1

    limave =  limitedpdf
    limave =  reduce(lambda x, y: x + y, limitedpdf) / len(limitedpdf)
    #print ave
    for limpdf in limitedpdf :
        ilimweight = ilimweight + (limpdf-limave)*(limpdf-limave)

    if pdfOP == "up" :
        return min(13.0,1.0+sqrt((ilimweight) / (len(limitedpdf))))
    else :
        return max(-12.0,1.0-sqrt((ilimweight) / (len(limitedpdf))))

def Trigger_Lookup( H , TRP ):
    Weight = 1.0
    Weightup = 1.0
    Weightdown = 1.0
    if H < 2000.0:
        bin0 = TRP.FindBin(H) 
        jetTriggerWeight = TRP.GetBinContent(bin0)
        Weight = jetTriggerWeight
        deltaTriggerEff  = 0.5*(1.0-jetTriggerWeight)
        Weightup  =   min(1.0,jetTriggerWeight + deltaTriggerEff)
        Weightdown  =   max(0.0,jetTriggerWeight - deltaTriggerEff)
        
    return [Weight,Weightup,Weightdown]

class myGenParticle:
    def __init__ (self, index, genpart):
        self.idx = index
        self.genpart = genpart
        self.status = genpart.status
        self.pdgId = genpart.pdgId
        self.vect = TLorentzVector()
        self.vect.SetPtEtaPhiM(genpart.pt,genpart.eta,genpart.phi,genpart.mass)
        self.motherIdx = genpart.genPartIdxMother

def PU_Lookup(PU , PUP):
    # PU == on, up, down
    thisbin = PUP.FindBin(float(PU))
    return PUP.GetBinContent(thisbin)


def Hemispherize(fatjetCollection,jetCollection):
    # Compares ak4 jets against leading ak8 and looks for any in opposite hemisphere

    # First find the highest pt ak8 jet with mass > 40 geV
    for fjet in range(0,len(fatjetCollection)):
        if fatjetCollection[fjet].msoftdrop > 40:
            candidateFatJetIndex = fjet
            break
    leadFatJet = fatjetCollection[candidateFatJetIndex]
    
    # Maintain same indexing for these throughout next bit
    candidateJetIndices = []
    candidateLVs = []

    # Check the AK4s against the AK8
    for ijet in range(0,len(jetCollection)):
        if abs(deltaPhi(leadFatJet.phi,jetCollection[ijet].phi))>TMath.Pi()/2.0:
            candidateJetIndices.append(ijet)
            thisLV = TLorentzVector() # for later use
            thisLV.SetPtEtaPhiM(jetCollection[ijet].pt,jetCollection[ijet].eta,jetCollection[ijet].phi,jetCollection[ijet].msoftdrop)
            candidateLVs.append(thisLV)

    # If not enough jets, end it
    if len(candidateJetIndices) < 2:
        return False
    # Else compare jets and find those within R of 1.5 (make pairs)
    else:
        passing_pair_indices = []
        passing_pair_lvs = []
        # Compare all pairs
        for pairs in itertools.combinations(range(0,len(candidateJetIndices)),2):   # this is providing pairs of indices of the candidateJetIndices list! (not the indices of the jetCollection!)
            lv1 = candidateLVs[pairs[0]]
            index1 = candidateJetIndices[pairs[0]]
            lv2 = candidateLVs[pairs[1]]
            index2 = candidateJetIndices[pairs[1]]
            if lv1.deltaR(lv2) < 1.5:
                # Save out collection index of those that pass
                passing_pair_indices.append([index1,index2])
                passing_pair_lvs.append([lv1,lv2])


        while len(passing_pair_indices) > 0:
            # Check if the ak4 jets are in a larger ak8
            # If they are, pop them out of our two lists for consideration
            for fjet in range(0,len(fatjetCollection)):
                fjetLV = TLorentzVector()
                fjetLV.SetPtEtaPhiM(fatjetCollection[fjet].pt,fatjetCollection[fjet].eta,fatjetCollection[fjet].phi,fatjetCollection[fjet].msoftdrop)
                for i,p in enumerate(passing_pair_lvs):
                    for lv in p:
                        if fjetLV.deltaR(lv) < 0.8:
                            passing_pair_lvs.pop(i)
                            passing_pair_indices.pop(i)
                            break # if we don't break, we could pop `p` while on the first lv and then who knows what gets read for second lv and we could start popping stuff we want to keep

        # if STILL greater than 1 pair...
        if len(passing_pair_indices) > 1:
            # Now pick based on summed btag values
            candidatePairIdx = []
            candidatePairLV = []
            btagsum = 0
            for ipp in range(0,len(passing_pair_indices)):
                thisbtagsum = jetCollection[passing_pair_indices[ipp][0]].btagDeepB + jetCollection[passing_pair_indices[ipp][1]].btagDeepB
                if thisbtagsum > btagsum:
                    btagsum = thisbtagsum
                    candidatePairIdx = passing_pair_indices[ipp]
                    candidatePairLV = passing_pair_lvs[ipp]

        # finally return
        if len(candidatePairIdx) == 0: # if no pairs, break out
            return False
        elif len(candidatePairIdx) == 1:
            candidatePairIdx = passing_pair_indices[0]
            return candidatePairIdx

def Weightify(wd,outname):
    final_w = 1.0
    corrections = ['Pileup','Topsf','sjbsf','Wsf','Trigger','Ptreweight']

    if outname == 'nominal':
        for c in corrections:
            if 'nom' in wd[c].keys():
                final_w = final_w*wd[c]['nom']


    elif outname.split('_')[0] in corrections:
        if outname.split('_')[1] in wd[outname.split('_')[0]].keys():
            final_w = wd[outname.split('_')[0]][outname.split('_')[1]]
        for c in corrections:
            if (c != outname.split('_')[0]) and ('nom' in wd[c].keys()):
                final_w = final_w*wd[c]['nom']

    else:
        final_w = wd[outname.split('_')[0]][outname.split('_')[1]]
        for c in corrections:
            if 'nom' in wd[c].keys():
                final_w = final_w*wd[c]['nom']
    
    return final_w

#This is just a quick function to automatically make a tree
#This is used right now to automatically output branches used to validate the cuts used in a run
def Make_Trees(Floats,name="Tree"):
    t = TTree(name, name);
    print "Booking trees"
    for F in Floats.keys():
        t.Branch(F, Floats[F], F+"/D")
    return t

#Makes the blue pull plots
def Make_Pull_plot( DATA,BKG,BKGUP,BKGDOWN ):
    pull = DATA.Clone("pull")
    pull.Add(BKG,-1)
    sigma = 0.0
    FScont = 0.0
    BKGcont = 0.0
    for ibin in range(1,pull.GetNbinsX()+1):
        FScont = DATA.GetBinContent(ibin)
        BKGcont = BKG.GetBinContent(ibin)
        if FScont>=BKGcont:
            FSerr = DATA.GetBinErrorLow(ibin)
            BKGerr = abs(BKGUP.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        if FScont<BKGcont:
            FSerr = DATA.GetBinErrorUp(ibin)
            BKGerr = abs(BKGDOWN.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        sigma = sqrt(FSerr*FSerr + BKGerr*BKGerr)
        if FScont == 0.0:
            pull.SetBinContent(ibin, 0.0 )  
        else:
            if sigma != 0 :
                pullcont = (pull.GetBinContent(ibin))/sigma
                pull.SetBinContent(ibin, pullcont)
            else :
                pull.SetBinContent(ibin, 0.0 )
    return pull
