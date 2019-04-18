
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

        'ttbar_xsec':831.76,
        'QCDHT700_xsec':6802,
        'QCDHT1000_xsec':1206,
        'QCDHT1500_xsec':120.4,
        'QCDHT2000_xsec':25.25
    }
    if year == '16':
        constants['lumi'] = 35872.301001
        
    elif year == '17':
        constants['lumi'] = 41518.865298,#35851.0,
        constants['ttbar_xsec'] = 377.96, #uncertainty +4.8%-6.1%

    elif year == '18':
        constants['lumi'] = 59660.725495
        constants['ttbar_xsec'] = 377.96, #uncertainty +4.8%-6.1%
        
    return constants
    
def LoadCuts(region,year):
    cuts = {
        'hpt':[250.0,float("inf")],
        'bpt':[50.0,float("inf")],
        'hmass':[105.0,135.0],
        'deepbtag':[0.4184,1.0],
        'doublebtag':[0.8,1.0],
        'eta':[0.0,2.4]
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


def Hemispherize(jetCollection):
    Jetsh1 = []
    Jetsh0 = []
    for ijet in range(0,len(jetCollection)):
        if abs(deltaPhi(jetCollection[0].phi,jetCollection[ijet].phi))>TMath.Pi()/2.0:
            Jetsh1.append(ijet)
        else:
            Jetsh0.append(ijet)

    return Jetsh0,Jetsh1

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
