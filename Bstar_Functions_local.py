
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
    if year == '16':
        return  {
            'lumi':35872.301001,#35851.0,
            'wtagsf_HP':1.0,# HP = High purity
            'wtagsfsig_HP':0.06,
            'wtagsf_LP':0.96,# LP = Low purity
            'wtagsfsig_LP':0.11,
            # 'ttagsf':1.07,
            # 'ttagsf_errUp':0.15,
            # 'ttagsf_errDown':0.06,
            'ttbar_xsec':831.76,
            'QCDHT700_xsec':6802,
            'QCDHT1000_xsec':1206,
            'QCDHT1500_xsec':120.4,
            'QCDHT2000_xsec':25.25,
            'singletop_t_xsec':136.02,
            'singletop_tW_xsec':35.85,
            'singletop_tB_xsec':80.95,
            'singletop_tWB_xsec':35.85,
            'signalLH1200_xsec':1.944,
            'signalLH1400_xsec':0.7848,
            'signalLH1600_xsec':0.3431,
            'signalLH1800_xsec':0.1588,
            'signalLH2000_xsec':0.07711,
            'signalLH2200_xsec':0.03881,
            'signalLH2400_xsec':0.02015,
            'signalLH2600_xsec':0.01073,
            'signalLH2800_xsec':0.005829,
            'signalLH3000_xsec':0.003234,
            'signalRH1200_xsec':1.936,
            'signalRH1400_xsec':0.7816,
            'signalRH1600_xsec':0.3416,
            'signalRH1800_xsec':0.1583,
            'signalRH2000_xsec':0.07675,
            'signalRH2200_xsec':0.03864,
            'signalRH2400_xsec':0.02008,
            'signalRH2600_xsec':0.01068,
            'signalRH2800_xsec':0.005814,
            'signalRH3000_xsec':0.003224
        }
    elif year == '17':
        return  {
            'lumi':41518.865298,#35851.0,
            'wtagsf_HP':0.97,# HP = High purity
            'wtagsfsig_HP':0.06,
            'wtagsf_LP':1.14,# LP = Low purity
            'wtagsfsig_LP':0.29,
            # 'ttagsf':1.07,
            # 'ttagsf_errUp':0.15,
            # 'ttagsf_errDown':0.06,
            'ttbar_xsec':377.96, #uncertainty +4.8%-6.1%
            'QCDHT700_xsec':6802,
            'QCDHT1000_xsec':1206,
            'QCDHT1500_xsec':120.4,
            'QCDHT2000_xsec':25.25,
            'singletop_t_xsec':136.02,
            'singletop_tW_xsec':35.85,
            'singletop_tB_xsec':80.95,
            'singletop_tWB_xsec':35.85,
            'signalLH1200_xsec':1.944,
            'signalLH1400_xsec':0.7848,
            'signalLH1600_xsec':0.3431,
            'signalLH1800_xsec':0.1588,
            'signalLH2000_xsec':0.07711,
            'signalLH2200_xsec':0.03881,
            'signalLH2400_xsec':0.02015,
            'signalLH2600_xsec':0.01073,
            'signalLH2800_xsec':0.005829,
            'signalLH3000_xsec':0.003234,
            'signalRH1200_xsec':1.936,
            'signalRH1400_xsec':0.7816,
            'signalRH1600_xsec':0.3416,
            'signalRH1800_xsec':0.1583,
            'signalRH2000_xsec':0.07675,
            'signalRH2200_xsec':0.03864,
            'signalRH2400_xsec':0.02008,
            'signalRH2600_xsec':0.01068,
            'signalRH2800_xsec':0.005814,
            'signalRH3000_xsec':0.003224
        }
    elif year == '18':
        return  {
            'lumi':59660.725495,
            'wtagsf_HP':0.97,# HP = High purity
            'wtagsfsig_HP':0.06,
            'wtagsf_LP':1.14,# LP = Low purity
            'wtagsfsig_LP':0.29,
            # 'ttagsf':1.07,
            # 'ttagsf_errUp':0.15,
            # 'ttagsf_errDown':0.06,
            'ttbar_xsec':377.96, #uncertainty +4.8%-6.1%
            'QCDHT700_xsec':6802,
            'QCDHT1000_xsec':1206,
            'QCDHT1500_xsec':120.4,
            'QCDHT2000_xsec':25.25,
            'singletop_t_xsec':136.02,
            'singletop_tW_xsec':35.85,
            'singletop_tB_xsec':80.95,
            'singletop_tWB_xsec':35.85,
            'signalLH1200_xsec':1.944,
            'signalLH1400_xsec':0.7848,
            'signalLH1600_xsec':0.3431,
            'signalLH1800_xsec':0.1588,
            'signalLH2000_xsec':0.07711,
            'signalLH2200_xsec':0.03881,
            'signalLH2400_xsec':0.02015,
            'signalLH2600_xsec':0.01073,
            'signalLH2800_xsec':0.005829,
            'signalLH3000_xsec':0.003234,
            'signalRH1200_xsec':1.936,
            'signalRH1400_xsec':0.7816,
            'signalRH1600_xsec':0.3416,
            'signalRH1800_xsec':0.1583,
            'signalRH2000_xsec':0.07675,
            'signalRH2200_xsec':0.03864,
            'signalRH2400_xsec':0.02008,
            'signalRH2600_xsec':0.01068,
            'signalRH2800_xsec':0.005814,
            'signalRH3000_xsec':0.003224
        }

    
def LoadCuts(region,year):
    if year == '16':
        if region == 'default':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'tau21':[0.0,0.4],
                'deepbtag':[0.2217,1.0],
                # 'sjbtag':[0.5426,1.0],
                'wmass':[65.0,105.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }

        elif region == 'sideband':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'tau21':[0.4,1.0],
                'deepbtag':[0.2217,1.0],
                # 'sjbtag':[0.5426,1.0],
                'wmass':[65.0,105.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }

        elif region == 'ttbar':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                # 'tau21':[0.0,0.4],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'deepbtag':[0.2217,1.0],
                # 'sjbtag':[0.5426,1.0],
                'wmass':[105.0,220.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }


    if year == '17':
        if region == 'default':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'tau21':[0.0,0.45],
                'tau21LP':[0.45,0.75],
                'deepbtag':[0.1522,1.0],
                'wmass':[65.0,105.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }

        elif region == 'sideband':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'tau21':[0.45,1.0],
                'tau21LP':[0.45,0.75],
                'deepbtag':[0.1522,1.0],
                'wmass':[65.0,105.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }

        elif region == 'ttbar':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                # 'tau21':[0.0,0.4],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'deepbtag':[0.1522,1.0],
                'wmass':[105.0,220.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }

    if year == '18':
        if region == 'default':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'tau21':[0.0,0.45],
                'tau21LP':[0.45,0.75],
                'deepbtag':[0.1241,1.0],
                'wmass':[65.0,105.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }

        elif region == 'sideband':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'tau21':[0.45,1.0],
                'tau21LP':[0.45,0.75],
                'deepbtag':[0.1241,1.0],
                'wmass':[65.0,105.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }

        elif region == 'ttbar':
            return  {
                'wpt':[500.0,float("inf")],
                'tpt':[500.0,float("inf")],
                'dy':[0.0,1.8],
                'tmass':[105.0,220.0],
                'tau32loose':[0.0,0.8],
                'tau32medium':[0.0,0.65],
                'tau32tight':[0.0,0.54],
                # 'tau21':[0.0,0.4],
                'DeepAK8_top_medium':[0.4585,1.0],
                'DeepAK8_top_tight':[0.6556,1.0],
                'DeepAK8_top_very_tight':[0.8931,1.0],
                'deepbtag':[0.1241,1.0],
                'wmass':[105.0,220.0],
                'eta1':[0.0,0.8],
                'eta2':[0.8,2.4],
                'eta':[0.0,2.4]
            }

#This function loads up Ntuples based on what type of set you want to analyze.  
#This needs to be updated whenever new Ntuples are produced (unless the file locations are the same).
def Load_jetNano(string,year):
    print 'running on ' + string 

    # if di != '':
    return 'root://cmseos.fnal.gov//store/user/lcorcodi/bstar_nano/rootfiles/'+string+'_bstar'+year+'.root'
    # else:
    #     return 'bstarTrees/rootfiles/'+string+'_bstar.root'
    # # Open pickle with locations
    # jetNanoLocations = pickle.load(open("jetNanoLocations.p", "rb"))

    # if 'signal' in string:
    #     string = string.replace('signal','Bstar')



def FindDeepAK8csv(setname):
    setDict = {
        'data':{
            'location':['JetHT/JetHT_Run2016B-05Feb2018_ver1-v1_jetNano_v0p1/',
                            'JetHT/JetHT_Run2016B-05Feb2018_ver2-v1_jetNano_v0p1/',
                            'JetHT/JetHT_Run2016C-05Feb2018-v1_jetNano_v0p1/',
                            'JetHT/JetHT_Run2016E-05Feb2018-v1_jetNano_v0p1/',
                            'JetHT/JetHT_Run2016F-05Feb2018-v1_jetNano_v0p1/',
                            'JetHT/JetHT_Run2016G-05Feb2018-v1_jetNano_v0p1/',
                            'JetHT/JetHT_Run2016H-05Feb2018_ver2-v1_jetNano_v0p1/',
                            'JetHT/JetHT_Run2016H-05Feb2018_ver3-v1_jetNano_v0p1/']
        },
        'ttbar':{
            'location':['TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_jetNano_v0p1/']
        },
        'QCD':{
            'location':['QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
                            'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',
                            'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
                            'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',
                            'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
                            'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',
                            'QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
                            'QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',
                            'QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
                            'QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/']
        },
        'singletop':{
            'location':['ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin/ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin_jetNano_v0p1/',
                            'ST_t-channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin/ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin_jetNano_v0p1/',
                            'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4_jetNano_v0p1/',
                            'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4_jetNano_v0p1/']
        },
        'signalLH1200':{
            'location':['BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH1400':{
            'location':['BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH1600':{
            'location':['BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH1800':{
            'location':['BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH2000':{
            'location':['BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH2200':{
            'location':['BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH2400':{
            'location':['BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH2600':{
            'location':['BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH2800':{
            'location':['BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalLH3000':{
            'location':['BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH1200':{
            'location':['BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH1400':{
            'location':['BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH1600':{
            'location':['BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH1800':{
            'location':['BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH2000':{
            'location':['BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH2200':{
            'location':['BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH2400':{
            'location':['BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH2600':{
            'location':['BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH2800':{
            'location':['BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        },
        'signalRH3000':{
            'location':['BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/']
        }
    }

    return setDict[setname]['location']


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


def SFTdeep_Lookup( pttop, plots ):
    nom = plots['nom'].Eval(pttop)
    up = plots['up'].Eval(pttop)
    down = plots['down'].Eval(pttop)
    return [nom,up,down]

class myGenParticle:
    def __init__ (self, index, genpart):
        self.idx = index
        self.genpart = genpart
        self.status = genpart.status
        self.pdgId = genpart.pdgId
        self.vect = TLorentzVector()
        self.vect.SetPtEtaPhiM(genpart.pt,genpart.eta,genpart.phi,genpart.mass)
        self.motherIdx = genpart.genPartIdxMother

def SFT_Lookup(jet, file, genparticles, wp):
    # Idea/pseudo code
    # for all b quarks with parent top:
    #    Move up the mother chain
    #    if the next mother is top, status 22, in jet:
    #        We found the b! Test if it's in the jet
    #
    # for all quarks with parent W:
    #     Move up mother chain
    #     if next mother is top, status 22, in jet (and same as b parent):
    #        We found a q! Test if it's in the jet

    if wp == 'loose':
        workpoint = 'wp3'
    elif wp == 'medium':
        workpoint = 'wp4'
    elif wp == 'tight':
        workpoint = 'wp5'

    # Index of candidates
    bquark_candidates = []
    wquark_candidates = []
    tquark_candidates = []

    merged_particles = 0

    for ig in range(len(genparticles)):
        genpart = myGenParticle(ig,genparticles[ig])
        # Top candidate if top, status 22, and inside jet
        if abs(genpart.pdgId) == 6 and abs(genpart.status == 22):
            tquark_candidates.append(genpart.idx)
        # b candidate if b and mother is top
        elif abs(genpart.pdgId) == 5 and abs(genparticles[genpart.motherIdx].pdgId) == 6:
            bquark_candidates.append(genpart.idx)
        # q candidate if q (not top) and mother is W
        elif abs(genpart.pdgId) > 0 and abs(genpart.pdgId) < 6 and abs(genparticles[genpart.motherIdx].pdgId) == 24:
            wquark_candidates.append(genpart.idx)

    print tquark_candidates
    print bquark_candidates
    print wquark_candidates

    # Now run up the chains for b quarks to see if the mothers is a top in our tquark_candidates
    for ib in bquark_candidates:
        current_particle = myGenParticle(ib,genparticles[ib])

        while current_particle.motherIdx not in tquark_candidates and current_particle.motherIdx != -1:
            current_index = current_particle.motherIdx
            current_particle = myGenParticle(current_index,genparticles[current_index])

        if current_particle.motherIdx not in tquark_candidates:
            continue
        else:
            bquark = myGenParticle(ib,genparticles[ib])
            if jet.DeltaR(bquark.vect) <= 0.8:
                merged_particles += 1

    for iq in wquark_candidates:
        current_particle = myGenParticle(iq,genparticles[iq])

        while current_particle.motherIdx not in tquark_candidates and current_particle.motherIdx != -1:
            current_index = current_particle.motherIdx
            current_particle = myGenParticle(current_index,genparticles[current_index])

        if current_particle.motherIdx not in tquark_candidates:
            continue
        else:
            wquark = myGenParticle(iq,genparticles[iq])
            if jet.DeltaR(wquark.vect) <= 0.8:
                merged_particles += 1

    print merged_particles

    if merged_particles == 3:
        hnom = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_nominal')
        hup = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_up')
        hdown = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_down')
    elif merged_particles == 2:
        hnom = file.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_nominal')
        hup = file.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_up')
        hdown = file.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_down')
    else:
        hnom = file.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_nominal')
        hup = file.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_up')
        hdown = file.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_down')

    if jet.Perp() > 5000:
        sfbin_nom = hnom.GetNbinsX()
        sfbin_up = hup.GetNbinsX()
        sfbin_down = hdown.GetNbinsX()
    else:
        sfbin_nom = hnom.FindFixBin(jet.Perp())
        sfbin_up = hup.FindFixBin(jet.Perp())
        sfbin_down = hdown.FindFixBin(jet.Perp())

    nom = hnom.GetBinContent(sfbin_nom)
    up = hup.GetBinContent(sfbin_up)
    down = hdown.GetBinContent(sfbin_down)

    return [nom,up,down]


def SFT_Lookup_MERGEDONLY( jet, file ):
    hnom = file.Get('PUPPI_wp5/sf_mergedTop_nominal')
    hup = file.Get('PUPPI_wp5/sf_mergedTop_up')
    hdown = file.Get('PUPPI_wp5/sf_mergedTop_down')
    if jet.Perp() > 5000:
        sfbin_nom = hnom.GetNbinsX()
        sfbin_up = hup.GetNbinsX()
        sfbin_down = hdown.GetNbinsX()
    else:
        sfbin_nom = hnom.FindFixBin(jet.Perp())
        sfbin_up = hup.FindFixBin(jet.Perp())
        sfbin_down = hdown.FindFixBin(jet.Perp())

    nom = hnom.GetBinContent(sfbin_nom)
    up = hup.GetBinContent(sfbin_up)
    down = hdown.GetBinContent(sfbin_down)

    return [nom,up,down]

#This looks up the ttbar pt reweighting scale factor when making ttrees
def PTW_Lookup( GP ):
    genTpt = -100.
    genTBpt = -100  

    # For all gen particles
    for ig in GP :
        # Determine if t or tbar
        isT = ig.pdgId == 6 and ig.status == 22
        isTB = ig.pdgId == -6 and ig.status == 22

        if isT and ig.statusFlags & (1 << 13):
            genTpt = ig.pt
        elif isTB and ig.statusFlags & (1 << 13):
            genTBpt = ig.pt 
        else:
            continue

        if (genTpt<0) or (genTBpt<0):
            print "ERROR in top pt reweighting. Top or anti-top pt less than 0."
            quit()

    # wTPt = exp(0.156-0.00137*genTpt)
    # wTbarPt = exp(0.156-0.00137*genTBpt)

    wTPt = exp(0.0615-0.0005*genTpt)
    wTbarPt = exp(0.0615-0.0005*genTBpt)
    return sqrt(wTPt*wTbarPt)


# This does the W jet matching requirement by looking up the deltaR separation
# of the daughter particle from the W axis. If passes, return 1.
def WJetMatching(GP):
    passed = 0
    failedDaughters = 0
    for ig in range(0,len(GP)):
        isWp = GP[ig].pdgId== 24 and GP[ig].status == 22
        isWm = GP[ig].pdgId== -24 and GP[ig].status == 22
        if isWp or isWm:
            # Windex = GP[ig].GetIndex()
            Wvect = TLorentzVector()
            Wvect.SetPtEtaPhiM(GP[ig].pt,GP[ig].eta,GP[ig].phi,GP[ig].mass)

            daughterVects = []
            for d in GP:
                if d.genPartIdxMother == ig:
                    thisDaughterVect = TLorentzVector()
                    thisDaughterVect.SetPtEtaPhiM(d.pt,d.eta,d.phi,d.mass)
                    daughterVects.append(thisDaughterVect)

            for daughter in daughterVects:
                if Wvect.DeltaR(daughter) > 0.8:
                    failedDaughters += 1

    if failedDaughters == 0:
        passed = 1

    return passed         

 
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

# def LeptonVeto(electronColl, muonColl):
    # If an event passing this following, we need to veto
    # Muons:
    # - pt > 53 GeV
    # - |eta| < 2.4
    # - tightID
    # - relative isolation < 0.15
    

    # Electrons:
    # - pt > 53 GeV
    # - |eta| < 2.4
    # - tightID (with isolation)

    # On top of this, Alex vetos additional isolated leptons with p_T > 30GeV and
    # looseID (muons) or vetoID (electrons).

    # return veto

#This is just a quick function to automatically make a tree
#This is used right now to automatically output branches used to validate the cuts used in a run
def Make_Trees(Floats,name="Tree"):
    t = TTree(name, name);
    print "Booking trees"
    for F in Floats.keys():
        t.Branch(F, Floats[F], F+"/D")
    return t

# Quick way to get extrapolation uncertainty
def ExtrapUncert_Lookup(pt,purity,year):
    if year == '16':
        if purity == 'HP':
            x = 0.085
        elif purity == 'LP':
            x = 0.039
        elif purity == False:
            return 0
        extrap_uncert = x*log(pt/200)
        return extrap_uncert
    elif year == '17' or year == '18':
        if pt > 350 and pt < 600:
            return 0.13
        else:
            if purity == 'HP':
                x = 0.085
            elif purity == 'LP':
                x = 0.039
            elif purity == False:
                return 0
            extrap_uncert = x*log(pt/200)
            return extrap_uncert



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


# Built to wait for condor jobs to finish and then check that they didn't fail
# The script that calls this function will quit if there are any job failures
# listOfJobs input should be whatever comes before '.listOfJobs' for the set of jobs you submitted
def WaitForJobs( listOfJobs ):
    # Runs grep to count the number of jobs - output will have non-digit characters b/c of wc
    preNumberOfJobs = subprocess.check_output('grep "python" '+listOfJobs+'.listOfJobs | wc -l', shell=True)
    commentedNumberOfJobs = subprocess.check_output('grep "# python" '+listOfJobs+'.listOfJobs | wc -l', shell=True)

    # Get rid of non-digits and convert to an int
    preNumberOfJobs = int(filter(lambda x: x.isdigit(), preNumberOfJobs))
    commentedNumberOfJobs = int(filter(lambda x: x.isdigit(), commentedNumberOfJobs))
    numberOfJobs = preNumberOfJobs - commentedNumberOfJobs

    finishedJobs = 0
    # Rudementary progress bar
    while finishedJobs < numberOfJobs:
        # Count how many output files there are to see how many jobs finished
        # the `2> null.txt` writes the stderr to null.txt instead of printing it which means
        # you don't have to look at `ls: output_*.log: No such file or directory`
        finishedJobs = subprocess.check_output('ls output_*.log 2> null.txt | wc -l', shell=True)
        finishedJobs = int(filter(lambda x: x.isdigit(), finishedJobs))
        sys.stdout.write('\rProcessing ' + str(listOfJobs) + ' - ')
        # Print the count out as a 'progress bar' that refreshes (via \r)
        sys.stdout.write("%i / %i of jobs finished..." % (finishedJobs,numberOfJobs))
        # Clear the buffer
        sys.stdout.flush()
        # Sleep for one second
        time.sleep(1)


    print 'Jobs completed. Checking for errors...'
    numberOfTracebacks = subprocess.check_output('grep -i "Traceback" output*.log | wc -l', shell=True)
    numberOfSyntax = subprocess.check_output('grep -i "Syntax" output*.log | wc -l', shell=True)

    numberOfTracebacks = int(filter(lambda x: x.isdigit(), numberOfTracebacks))
    numberOfSyntax = int(filter(lambda x: x.isdigit(), numberOfSyntax))

    # Check there are no syntax or traceback errors
    # Future idea - check output file sizes
    if numberOfTracebacks > 0:
        print str(numberOfTracebacks) + ' job(s) failed with traceback error'
        quit()
    elif numberOfSyntax > 0:
        print str(numberOfSyntax) + ' job(s) failed with syntax error'
        quit()
    else:
        print 'No errors!'

# Scales the up and down pdf uncertainty distributions to the nominal value to isolate the shape uncertainty
def PDFShapeUncert(nominal, up, down):
    upShape = up.Clone("Mtw")
    downShape = down.Clone("Mtw")
    upShape.Scale(nominal.Integral()/up.Integral())
    downShape.Scale(nominal.Integral()/down.Integral())

    return upShape, downShape

# Creates ratios between the events in up/down PDF distributions to nominal distribution and
# used the ratio to derive up/down xsec values for the given mass point
def PDFNormUncert(nominal, up, down, xsec_nominal):
    ratio_up = up.Integral()/nominal.Integral()
    ratio_down = down.Integral()/nominal.Integral()

    xsec_up = ratio_up*xsec_nominal
    xsec_down = ratio_down*xsec_nominal

    return xsec_up, xsec_down

def DAK8_crosscheck(fromDAK8,fromEvent):
    # Inputs are two lists of [pt, eta, phi]
    
    for i in range(len(fromDAK8)):
        if fromDAK8[i] != fromEvent[i]:

            diff = abs(fromDAK8[i]-fromEvent[i])
            if i == 2: # if phi
                if abs(fromDAK8[i]-fromEvent[i]) > math.pi:
                    diff = 2*math.pi - abs(fromDAK8[i]-fromEvent[i])
                 

            disc = diff/(abs(fromDAK8[i])/2+abs(fromEvent[i])/2)
            
            if disc > 0.05 and i != 0:
                return False
            elif disc > 0.1:
                return False

    return True


def flatTag():
    r = random()

    return r


def linTag(a=1.):
    r = random()

    # Derived by inverting Integral(mx+b,{x,0,x})
    lin = a*math.sqrt(r)
    # norm = (a/3)

    # print quad

    return lin#/norm

def quadTag(a=1.):
    r = random()

    # Derived by inverting Integral(ax^2+bx+c,{x,0,x})
    onethird = 1./3.
    quad = a*math.pow(r,onethird)

    return quad