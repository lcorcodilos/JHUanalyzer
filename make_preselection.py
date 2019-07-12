#################################################################
# make_preselection.py - Written by Lucas Corcodilos, 7/13/18   #
# -----------------------------------------------------------   #
# Reads the jetNano trees on EOS, builds the 2D distributions   #
# for 2D Alphabet, and creates and stores an even smaller TTree #
# that can be used later to analyze variable distributions with #
# the 2D Alphabet Rp/f applied.                                 #
#################################################################

import ROOT
from ROOT import *

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.JetSysColl import JetSysColl, JetSysObj
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim


# import FatJetNNHelper
# from FatJetNNHelper import *

import pickle
from optparse import OptionParser
import copy
import math
from math import sqrt
import sys
import time

import Presel_Functions
from Presel_Functions import *


if __name__ == "__main__":
    
    parser = OptionParser()

    parser.add_option('-s', '--set', metavar='F', type='string', action='store',
                    default   =   'data',
                    dest      =   'set',
                    help      =   'dataset (ie data,ttbar etc)')
    parser.add_option('-r', '--region', metavar='F', type='string', action='store',
                    default   =   'default',
                    dest      =   'region',
                    help      =   'default, sideband, ttbar')
    parser.add_option('-y', '--year', metavar='FILE', type='string', action='store',
                    default   =   '',
                    dest      =   'year',
                    help      =   'Year (16,17,18)')
    parser.add_option('-J', '--JES', metavar='F', type='string', action='store',
                    default   =   'nominal',
                    dest      =   'JES',
                    help      =   'nominal, up, or down')
    parser.add_option('-R', '--JER', metavar='F', type='string', action='store',
                    default   =   'nominal',
                    dest      =   'JER',
                    help      =   'nominal, up, or down')
    parser.add_option('-a', '--JMS', metavar='F', type='string', action='store',
                    default   =   'nominal',
                    dest      =   'JMS',
                    help      =   'nominal, up, or down')
    parser.add_option('-b', '--JMR', metavar='F', type='string', action='store',
                    default   =   'nominal',
                    dest      =   'JMR',
                    help      =   'nominal, up, or down')
    parser.add_option('-j', '--job', metavar='F', type='string', action='store',
                    default   =   'all',
                    dest      =   'job',
                    help      =   'job number')
    parser.add_option('-n', '--njobs', metavar='F', type='string', action='store',
                    default   =   '1',
                    dest      =   'njobs',
                    help      =   'number of jobs')
    parser.add_option('-d', '--doublebtagger', metavar='F', type='string', action='store',
                    default   =   'btagHbb',
                    dest      =   'doublebtagger',
                    help      =   'Variable name in NanoAOD for double b tagger to be used. btagHbb (default), deepTagMD_HbbvsQCD, deepTagMD_ZHbbvsQCD, btagDDBvL')
    

    (options, args) = parser.parse_args()

    # Prep for deepcsv b-tag if deepak8 is off
    # From https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration
    gSystem.Load('libCondFormatsBTauObjects') 
    gSystem.Load('libCondToolsBTau') 
    # if options.year == '16':
    #     calib = BTagCalibration('DeepCSV', 'SFs/DeepCSV_2016LegacySF_V1.csv')
    # elif options.year == '17':
    #     calib = BTagCalibration('DeepCSV', 'SFs/subjet_DeepCSV_94XSF_V4_B_F.csv')
    if options.year == '18':
        calib = BTagCalibration('DeepCSV', 'SFs/DeepCSV_102XSF_V1.csv')
            
    v_sys = getattr(ROOT, 'vector<string>')()
    v_sys.push_back('up')
    v_sys.push_back('down')

    reader = BTagCalibrationReader(
            0,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
            "central",      # central systematic type
            v_sys,          # vector of other sys. types
    )   

    reader.load(
            calib, 
            0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
            "incl"      # measurement type
    ) 

    ################################
    # Setup double b tagger option #
    ################################
    doubleB_titles = {'btagHbb':'Double b',
                      'deepTagMD_HbbvsQCD': 'DeepAK8 MD Hbb',
                      'deepTagMD_ZHbbvsQCD': 'DeepAK8 MD ZHbb',
                      'btagDDBvL': 'Deep Double b'}
    doubleB_abreviations = {'btagHbb':'doubleB',
                      'deepTagMD_HbbvsQCD': 'dak8MDHbb',
                      'deepTagMD_ZHbbvsQCD': 'dak8MDZHbb',
                      'btagDDBvL': 'DeepDB'}
    doubleB_name = options.doublebtagger
    doubleB_title = doubleB_titles[doubleB_name]
    doubleB_short = doubleB_abreviations[doubleB_name]

    ######################################
    # Make strings for final file naming #
    ######################################
    # JECs
    runOthers = True
    if 'data' not in options.set:
        mass_name = ''
    else:
        mass_name = '_nom'
    mod = ''
    if options.JES!='nominal':
        mod = '_JES' + '_' + options.JES
        mass_name = '_jesTotal'+options.JES.capitalize()
        runOthers = False
    if options.JER!='nominal':
        mod = '_JER' + '_' + options.JER
        mass_name = '_jer'+options.JER.capitalize()
        runOthers = False
    if options.JMS!='nominal':
        mod = '_JMS' + '_' + options.JMS
        mass_name = '_jms'+options.JMS.capitalize()
        runOthers = False
    if options.JMR!='nominal':
        mod = '_JMR' + '_' + options.JMR
        mass_name = '_jmr'+options.JMR.capitalize()
        runOthers = False


    #######################
    # Setup job splitting #
    #######################
    if int(options.job) > int(options.njobs):
        raise RuntimeError('ERROR: Trying to run job '+options.job+' out of '+options.njobs)
    jobs=int(options.njobs)
    if jobs != 1:
        num=int(options.job)
        jobs=int(options.njobs)
        print "Running over " +str(jobs)+ " jobs"
        print "This will process job " +str(num)
    else:
        print "Running over all events"

    #################################
    # Load cut values and constants #
    #################################
    Cons = LoadConstants(options.year)
    lumi = Cons['lumi']

    Cuts = LoadCuts(options.region,options.year)

    ##########################################################
    # Load Trigger, Pileup reweight, and ttag sf if not data #
    ##########################################################
    if False:#options.set != 'data':
        print "Triggerweight_data"+options.year+"_pre_"+pretrig_string+".root"
        print 'TriggerWeight_'+tname+'_Ht'
        TrigFile = TFile.Open("trigger/Triggerweight_data"+options.year+"_pre_"+pretrig_string+".root")
        TrigPlot = TrigFile.Get('TriggerWeight_'+tname+'_Ht')
        TrigPlot1 = TrigPlot.Clone()
        
    if 'data' not in options.set:
        PileFile = TFile.Open("pileup/PileUp_Ratio_ttbar"+options.year+".root")
        PilePlots = {
            "nom": PileFile.Get("Pileup_Ratio"),
            "up": PileFile.Get("Pileup_Ratio_up"),
            "down": PileFile.Get("Pileup_Ratio_down")}
        
        # ttagsffile = TFile.Open('SFs/20'+tempyear+'TopTaggingScaleFactors.root')
    # print("Trigger loaded")

    #############################
    # Make new file for storage #
    #############################
    if jobs!=1:
        f = TFile( "HHpreselection"+options.year+"_"+options.set+"_job"+options.job+"of"+options.njobs+mod+'_'+doubleB_short+'_'+options.region+".root", "recreate" )
    else:
        f = TFile( "HHpreselection"+options.year+"_"+options.set+mod+'_'+doubleB_short+'_'+options.region+".root", "recreate" )
    f.cd()

    # print("New rootfile made")
    ###################
    # Book histograms #
    ###################
    hh11_cutflow = ROOT.TH1D('hh11_cutflow', 'hh11_cutflow', 9, 0.5, 9.5)
    hh11_cutflow.GetXaxis().SetBinLabel(1, "no cuts")
    hh11_cutflow.GetXaxis().SetBinLabel(2, "eta")
    hh11_cutflow.GetXaxis().SetBinLabel(3, "p_{T}(H) both jets")
    hh11_cutflow.GetXaxis().SetBinLabel(4, "m_{h}")
    # hh11_cutflow.GetXaxis().SetBinLabel(5, "m_{h reduced}")
    hh11_cutflow.GetXaxis().SetBinLabel(5, "|\Delta \eta|")
    hh11_cutflow.GetXaxis().SetBinLabel(6, "\tau_{21} both jets")
    hh11_cutflow.GetXaxis().SetBinLabel(7,"LL - "+doubleB_title)
    hh11_cutflow.GetXaxis().SetBinLabel(8,"TT - "+doubleB_title)

    hh21_cutflow = TH1F("hh21_cutflow","hh21_cutflow",8,0.5,8.5)
    hh21_cutflow.GetXaxis().SetBinLabel(1, "no cuts")
    hh21_cutflow.GetXaxis().SetBinLabel(2, "eta")
    hh21_cutflow.GetXaxis().SetBinLabel(3, "p_{T}(H)")
    hh21_cutflow.GetXaxis().SetBinLabel(4, "p_{T}(b) both b quarks")
    hh21_cutflow.GetXaxis().SetBinLabel(5, "m_{bb}")
    hh21_cutflow.GetXaxis().SetBinLabel(6, "DeepCSV")
    hh21_cutflow.GetXaxis().SetBinLabel(7, "|\Delta \eta|")
    hh21_cutflow.GetXaxis().SetBinLabel(7, doubleB_title+" tag")

    hh11_doubleB = TH1F('hh11_doubleB','1+1 '+doubleB_title+' tag',20,0,1)
    hh21_doubleB = TH1F('hh21_doubleB','2+1 '+doubleB_title+' tag',20,0,1)
    hh11_doubleB.Sumw2()
    hh21_doubleB.Sumw2()

    MhhvMh21Pass     = TH2F("MhhvMh21Pass",     "2+1 mass of HH vs mass of AK8 jet H - Pass", 9, 40, 220, 13, 700, 2000 )
    MhhvMh21Fail     = TH2F("MhhvMh21Fail",     "2+1 mass of HH vs mass of AK8 jet H - Fail", 9, 40, 220, 13, 700, 2000 )
    MhhvMh21Pass.Sumw2()
    MhhvMh21Fail.Sumw2()

    MhhvMh11TTPass = ROOT.TH2D('MhhvMh11TTPass' ,'1+1 mass of HH vs mass of AK8 jet H - Pass TT' ,9 ,40 ,220 ,20 ,1000 ,3000) 
    MhhvMh11LLPass = ROOT.TH2D('MhhvMh11LLPass' ,'1+1 mass of HH vs mass of AK8 jet H - Pass LL' ,9 ,40 ,220 ,20 ,1000 ,3000) 
    MhhvMh11TTFail = ROOT.TH2D('MhhvMh11TTFail' ,'1+1 mass of HH vs mass of AK8 jet H - Fail TT' ,9 ,40 ,220 ,20 ,1000 ,3000) 
    MhhvMh11LLFail = ROOT.TH2D('MhhvMh11LLFail' ,'1+1 mass of HH vs mass of AK8 jet H - Fail LL' ,9 ,40 ,220 ,20 ,1000 ,3000) 
    MhhvMh11TTPass.Sumw2()
    MhhvMh11LLPass.Sumw2()
    MhhvMh11TTFail.Sumw2()
    MhhvMh11LLFail.Sumw2()

    nev = TH1F("nev",   "nev",      1, 0, 1 )

    if runOthers == True:
        if 'data' not in options.set:
            # Pass - 2+1 
            MhhvMh21PassPDFup   = TH2F("MhhvMh21PassPDFup", "2+1 mass of HH vs mass of AK8 jet H PDF up - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassPDFdown = TH2F("MhhvMh21PassPDFdown",   "2+1 mass of HH vs mass of AK8 jet H PDF down - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassPDFup.Sumw2()
            MhhvMh21PassPDFdown.Sumw2()

            MhhvMh21PassPUup   = TH2F("MhhvMh21PassPUup", "2+1 mass of HH vs mass of AK8 jet H PU up - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassPUdown = TH2F("MhhvMh21PassPUdown",   "2+1 mass of HH vs mass of AK8 jet H PU down - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassPUup.Sumw2()
            MhhvMh21PassPUdown.Sumw2()

            MhhvMh21PassBtagup   = TH2F("MhhvMh21PassBtagup", "2+1 mass of HH vs mass of AK8 jet H Btag up - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassBtagdown = TH2F("MhhvMh21PassBtagdown",   "2+1 mass of HH vs mass of AK8 jet H Btag down - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassBtagup.Sumw2()
            MhhvMh21PassBtagdown.Sumw2()

            # MhhvMh21PassTrigup   = TH2F("MhhvMh21PassTrigup", "2+1 mass of HH vs mass of AK8 jet H trig up - Pass", 9, 40, 220, 13, 700, 2000 )
            # MhhvMh21PassTrigdown = TH2F("MhhvMh21PassTrigdown",   "2+1 mass of HH vs mass of AK8 jet H trig down - Pass", 9, 40, 220, 13, 700, 2000 )
            # MhhvMh21PassTrigup.Sumw2()
            # MhhvMh21PassTrigdown.Sumw2()

            # Fail - 2+1 
            MhhvMh21FailPDFup   = TH2F("MhhvMh21FailPDFup", "2+1 mass of HH vs mass of AK8 jet H PDF up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailPDFdown = TH2F("MhhvMh21FailPDFdown",   "2+1 mass of HH vs mass of AK8 jet H PDF up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailPDFup.Sumw2()
            MhhvMh21FailPDFdown.Sumw2()

            MhhvMh21FailPUup   = TH2F("MhhvMh21FailPUup", "2+1 mass of HH vs mass of AK8 jet H PU up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailPUdown = TH2F("MhhvMh21FailPUdown",   "2+1 mass of HH vs mass of AK8 jet H PU up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailPUup.Sumw2()
            MhhvMh21FailPUdown.Sumw2()

            MhhvMh21FailBtagup   = TH2F("MhhvMh21FailBtagup", "2+1 mass of HH vs mass of AK8 jet H Btag up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailBtagdown = TH2F("MhhvMh21FailBtagdown",   "2+1 mass of HH vs mass of AK8 jet H Btag up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailBtagup.Sumw2()
            MhhvMh21FailBtagdown.Sumw2()

            # MhhvMh21FailTrigup   = TH2F("MhhvMh21FailTrigup", "2+1 mass of HH vs mass of AK8 jet H trig up - Fail", 9, 40, 220, 13, 700, 2000 )
            # MhhvMh21FailTrigdown = TH2F("MhhvMh21FailTrigdown",   "2+1 mass of HH vs mass of AK8 jet H trig up - Fail", 9, 40, 220, 13, 700, 2000 )
            # MhhvMh21FailTrigup.Sumw2()
            # MhhvMh21FailTrigdown.Sumw2()

            # Pass - 1+1 TT
            MhhvMh11TTPassPDFup   = TH2F("MhhvMh11TTPassPDFup", "1+1 mass of HH vs mass of AK8 jet H PDF up - Pass TT", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassPDFdown = TH2F("MhhvMh11TTPassPDFdown",   "mass of HH vs mass of AK8 jet H PDF down - Pass TT", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassPDFup.Sumw2()
            MhhvMh11TTPassPDFdown.Sumw2()

            MhhvMh11TTPassPUup   = TH2F("MhhvMh11TTPassPUup", "1+1 mass of HH vs mass of AK8 jet H PU up - Pass TT", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassPUdown = TH2F("MhhvMh11TTPassPUdown",   "1+1 mass of HH vs mass of AK8 jet H PU down - Pass TT", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassPUup.Sumw2()
            MhhvMh11TTPassPUdown.Sumw2()

            # MhhvMh11TTPassBtagup   = TH2F("MhhvMh11TTPassBtagup", "1+1 mass of HH vs mass of AK8 jet H Btag up - Pass TT", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11TTPassBtagdown = TH2F("MhhvMh11TTPassBtagdown",   "1+1 mass of HH vs mass of AK8 jet H Btag down - Pass TT", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11TTPassBtagup.Sumw2()
            # MhhvMh11TTPassBtagdown.Sumw2()

            # MhhvMh11TTPassTrigup   = TH2F("MhhvMh11TTPassTrigup", "1+1 mass of HH vs mass of AK8 jet H trig up - Pass TT", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11TTPassTrigdown = TH2F("MhhvMh11TTPassTrigdown",   "1+1 mass of HH vs mass of AK8 jet H trig down - Pass TT", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11TTPassTrigup.Sumw2()
            # MhhvMh11TTPassTrigdown.Sumw2()

            # Fail - 1+1 TT
            MhhvMh11TTFailPDFup   = TH2F("MhhvMh11TTFailPDFup", "1+1 mass of HH vs mass of AK8 jet H PDF up - Fail TT", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailPDFdown = TH2F("MhhvMh11TTFailPDFdown",   "1+1 mass of HH vs mass of AK8 jet H PDF up - Fail TT", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailPDFup.Sumw2()
            MhhvMh11TTFailPDFdown.Sumw2()

            MhhvMh11TTFailPUup   = TH2F("MhhvMh11TTFailPUup", "1+1 mass of HH vs mass of AK8 jet H PU up - Fail TT", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailPUdown = TH2F("MhhvMh11TTFailPUdown",   "1+1 mass of HH vs mass of AK8 jet H PU up - Fail TT", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailPUup.Sumw2()
            MhhvMh11TTFailPUdown.Sumw2()

            # MhhvMh11TTFailBtagup   = TH2F("MhhvMh11TTFailBtagup", "1+1 mass of HH vs mass of AK8 jet H Btag up - Fail TT", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11TTFailBtagdown = TH2F("MhhvMh11TTFailBtagdown",   "1+1 mass of HH vs mass of AK8 jet H Btag up - Fail TT", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11TTFailBtagup.Sumw2()
            # MhhvMh11TTFailBtagdown.Sumw2()

            # MhhvMh11TTFailTrigup   = TH2F("MhhvMh11TTFailTrigup", "1+1 mass of HH vs mass of AK8 jet H trig up - Fail TT", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11TTFailTrigdown = TH2F("MhhvMh11TTFailTrigdown",   "1+1 mass of HH vs mass of AK8 jet H trig up - Fail TT", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11TTFailTrigup.Sumw2()
            # MhhvMh11TTFailTrigdown.Sumw2()

            # Pass - 1+1 LL 
            MhhvMh11LLPassPDFup   = TH2F("MhhvMh11LLPassPDFup", "1+1 mass of HH vs mass of AK8 jet H PDF up - Pass LL", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassPDFdown = TH2F("MhhvMh11LLPassPDFdown",   "1+1 mass of HH vs mass of AK8 jet H PDF down - Pass LL", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassPDFup.Sumw2()
            MhhvMh11LLPassPDFdown.Sumw2()

            MhhvMh11LLPassPUup   = TH2F("MhhvMh11LLPassPUup", "1+1 mass of HH vs mass of AK8 jet H PU up - Pass LL", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassPUdown = TH2F("MhhvMh11LLPassPUdown",   "1+1 mass of HH vs mass of AK8 jet H PU down - Pass LL", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassPUup.Sumw2()
            MhhvMh11LLPassPUdown.Sumw2()

            # MhhvMh11LLPassBtagup   = TH2F("MhhvMh11LLPassBtagup", "1+1 mass of HH vs mass of AK8 jet H Btag up - Pass LL", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11LLPassBtagdown = TH2F("MhhvMh11LLPassBtagdown",   "1+1 mass of HH vs mass of AK8 jet H Btag down - Pass LL", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11LLPassBtagup.Sumw2()
            # MhhvMh11LLPassBtagdown.Sumw2()

            # MhhvMh11LLPassTrigup   = TH2F("MhhvMh11LLPassTrigup", "1+1 mass of HH vs mass of AK8 jet H trig up - Pass LL", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11LLPassTrigdown = TH2F("MhhvMh11LLPassTrigdown",   "1+1 mass of HH vs mass of AK8 jet H trig down - Pass LL", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11LLPassTrigup.Sumw2()
            # MhhvMh11LLPassTrigdown.Sumw2()

            # Fail - 1+1 LL 
            MhhvMh11LLFailPDFup   = TH2F("MhhvMh11LLFailPDFup", "1+1 mass of HH vs mass of AK8 jet H PDF up - Fail LL", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailPDFdown = TH2F("MhhvMh11LLFailPDFdown",   "1+1 mass of HH vs mass of AK8 jet H PDF up - Fail LL", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailPDFup.Sumw2()
            MhhvMh11LLFailPDFdown.Sumw2()

            MhhvMh11LLFailPUup   = TH2F("MhhvMh11LLFailPUup", "1+1 mass of HH vs mass of AK8 jet H PU up - Fail LL", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailPUdown = TH2F("MhhvMh11LLFailPUdown",   "1+1 mass of HH vs mass of AK8 jet H PU up - Fail LL", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailPUup.Sumw2()
            MhhvMh11LLFailPUdown.Sumw2()

            # MhhvMh11LLFailBtagup   = TH2F("MhhvMh11LLFailBtagup", "1+1 mass of HH vs mass of AK8 jet H Btag up - Fail LL", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11LLFailBtagdown = TH2F("MhhvMh11LLFailBtagdown",   "1+1 mass of HH vs mass of AK8 jet H Btag up - Fail LL", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11LLFailBtagup.Sumw2()
            # MhhvMh11LLFailBtagdown.Sumw2()

            # MhhvMh11LLFailTrigup   = TH2F("MhhvMh11LLFailTrigup", "1+1 mass of HH vs mass of AK8 jet H trig up - Fail LL", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11LLFailTrigdown = TH2F("MhhvMh11LLFailTrigdown",   "1+1 mass of HH vs mass of AK8 jet H trig up - Fail LL", 9, 40, 220, 20, 1000, 3000 )
            # MhhvMh11LLFailTrigup.Sumw2()
            # MhhvMh11LLFailTrigdown.Sumw2()


    print("Histograms booked")
    ###############################
    # Grab root file that we want #
    ###############################
    file_string = Load_jetNano(options.set,options.year)
    file = TFile.Open(file_string)
    print("root file"+file_string+" loaded")

    ################################
    # Grab event tree from nanoAOD #
    ################################
    inTree = file.Get("Events")
    elist,jsonFilter = preSkim(inTree,None,'')
    inTree = InputTree(inTree,elist)
    treeEntries = inTree.entries
    print("event tree loaded")

    #############################
    # Get process normalization #
    #############################
    norm_weight = 1
    if 'data' not in options.set:
        runs_tree = file.Get("Runs")
        nevents_gen = 0
        
        for i in runs_tree:
            nevents_gen+=i.genEventCount

        xsec = Cons[options.set+'_xsec'] 
        norm_weight = lumi*xsec/float(nevents_gen)

    #####################################
    # Design the splitting if necessary #
    #####################################
    if jobs != 1:
        evInJob = int(treeEntries/jobs)
        lowBinEdge = evInJob*(num-1)
        highBinEdge = evInJob*num
        if num == jobs:
            highBinEdge = treeEntries
    else:
        lowBinEdge = 0
        highBinEdge = treeEntries

    print "Range of events: (" + str(lowBinEdge) + ", " + str(highBinEdge) + ")"

    count = 0
    
    ##############
    # Begin Loop #
    ##############
    start = time.time()
    last_event_time = start
    event_time_sum = 0
    for entry in range(lowBinEdge,highBinEdge):        
        count   =   count + 1
        #if count > 1:
        #    current_event_time = time.time()
        #    event_time_sum += (current_event_time - last_event_time)
        #    sys.stdout.write("%i / %i ... \r" % (count,(highBinEdge-lowBinEdge)))
        #    sys.stdout.write("Avg time = %f " % (event_time_sum/count) )
        #    sys.stdout.flush()
        #    last_event_time = current_event_time
        if count % 10000 == 0 :
            print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

        # Grab the event
        event = Event(inTree, entry)
        # print("Event grabbed")

        # Apply triggers first
        if 'data' in options.set: 
            isData = True
        else:
            isData = False
        if isData:
            isTriggered = event.HLT_PFHT1050 \
              or event.HLT_AK8PFHT900_TrimMass50 \
              or event.HLT_AK8PFJet420_TrimMass30 \
              or event.HLT_AK8PFJet500 
        else:
            isTriggered = event.HLT_PFHT780 \
              or event.HLT_AK8PFHT750_TrimMass50 \
              or event.HLT_AK8PFJet360_TrimMass30 \
              or event.HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p17 

        if not isTriggered: 
            continue

        # Filters
        filters = [event.Flag_goodVertices,
                   event.Flag_HBHENoiseFilter,
                   event.Flag_HBHENoiseIsoFilter,
                   event.Flag_globalTightHalo2016Filter,
                   event.Flag_EcalDeadCellTriggerPrimitiveFilter,
                   event.Flag_eeBadScFilter]

        filterFails = 0
        for thisFilter in filters:
            if thisFilter == 0:
                filterFails += 1
        if filterFails > 0:
            continue

        # Have to grab Collections for each collection of interest
        # -- collections are for types of objects where there could be multiple values
        #    for a single event
        ak8JetsColl = Collection(event, "FatJet")
        ak4JetsColl = Collection(event, "Jet")

        # Selections
        HHsel11 = {}
        HHsel21 = {}

        # Now jetID which (in binary #s) is stored with bit1 as loose, bit2 as tight, and filters (after grabbing jet collections)
        if len(ak8JetsColl) >= 1 and ((ak8JetsColl[0].jetId & 1 == 1) or (ak8JetsColl[0].jetId & 2 == 2)):   
            HHsel21['jetIds'] = True
            if len(ak8JetsColl) >= 2 and ((ak8JetsColl[1].jetId & 1 == 1) or (ak8JetsColl[1].jetId & 2 == 2)):    
                HHsel11['jetIds'] = True
            else:
                HHsel11['jetIds'] = False
        else:
            continue

        # check if we have enough jets
        if len(ak8JetsColl) >= 2:
            HHsel11['nFatJet'] = True
            HHsel21['nFatJet'] = True
        elif len(ak8JetsColl) == 1:
            HHsel11['nFatJet'] = False
            HHsel21['nFatJet'] = True
        elif len(ak8JetsColl) < 1:
            # HHsel11['nFatJet'] = False
            # HHsel21['nFatJet'] = False
            continue

        # Start 1+1 stuff
        HHsel11['eta'] =    (Cuts['eta'][0]<abs(ak8JetsColl[0].eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(ak8JetsColl[1].eta)<Cuts['eta'][1])
        HHsel11['dEta'] =   Cuts['dEtaAK8'][0] < abs(ak8JetsColl[0].eta - ak8JetsColl[1].eta) < Cuts['dEtaAK8'][1]
        HHsel11['pt'] =     Cuts['hpt'][0] < ak8JetsColl[0].pt < Cuts['hpt'][1] and Cuts['hpt'][0] < ak8JetsColl[1].pt < Cuts['hpt'][1]
        HHsel11['hmass'] =  Cuts['hmass'][0] < ak8JetsColl[1].msoftdrop < Cuts['hmass'][1]
        if ak8JetsColl[0].tau1 > 0 and ak8JetsColl[1].tau1 > 0:
            HHsel11['tau21'] = (Cuts['tau21'][0] < ak8JetsColl[0].tau2/ak8JetsColl[0].tau1 < Cuts['tau21'][1]) and (Cuts['tau21'][0] < ak8JetsColl[1].tau2/ak8JetsColl[1].tau1 < Cuts['tau21'][1])            
        else:
            continue
        h_jet0, h_jet1 = ROOT.TLorentzVector(), ROOT.TLorentzVector()
        h_jet0.SetPtEtaPhiM(ak8JetsColl[0].pt, ak8JetsColl[0].eta, ak8JetsColl[0].phi, ak8JetsColl[0].msoftdrop)
        h_jet1.SetPtEtaPhiM(ak8JetsColl[1].pt, ak8JetsColl[1].eta, ak8JetsColl[1].phi, ak8JetsColl[1].msoftdrop)
        mhh11 = (h_jet0 + h_jet1).M()
        mhhred11 = mhh11 - h_jet0.M() - h_jet1.M() + 250
        HHsel11['reduced_hhmass'] = Cuts['mreduced'][0] < mhhred11 < Cuts['mreduced'][1]

        HHsel11['DoubleB_lead_tight'] = (Cuts['doublebtagTight'][0] < getattr(ak8JetsColl[0],doubleB_name) < Cuts['doublebtagTight'][1])
        HHsel11['DoubleB_lead_loose'] = (Cuts['doublebtagLoose'][0] < getattr(ak8JetsColl[0],doubleB_name) < Cuts['doublebtagLoose'][1])
        HHsel11['DoubleB_sublead_tight'] = (Cuts['doublebtagTight'][0] < getattr(ak8JetsColl[1],doubleB_name) < Cuts['doublebtagTight'][1])
        HHsel11['DoubleB_sublead_loose'] = (Cuts['doublebtagLoose'][0] < getattr(ak8JetsColl[1],doubleB_name) < Cuts['doublebtagLoose'][1])

        HHsel11['SRTT'] = HHsel11['DoubleB_lead_tight'] and HHsel11['DoubleB_sublead_tight']
        HHsel11['SRLL'] = HHsel11['DoubleB_lead_loose'] and HHsel11['DoubleB_sublead_loose'] and not HHsel11['SRTT']
        HHsel11['ATTT'] = (not HHsel11['DoubleB_lead_loose']) and HHsel11['DoubleB_sublead_tight']
        HHsel11['ATLL'] = (not HHsel11['DoubleB_lead_loose']) and HHsel11['DoubleB_sublead_loose'] and not HHsel11['DoubleB_sublead_tight']

        preselection_11 = HHsel11['nFatJet'] and HHsel11['eta'] and HHsel11['pt'] and HHsel11['hmass'] and HHsel11['dEta'] and HHsel11['tau21']
        if not isData:
            if HHsel11['nFatJet']:
                hh11_cutflow.Fill(1)
                if HHsel11['eta']:
                    hh11_cutflow.Fill(2)
                    if HHsel11['pt']:
                        hh11_cutflow.Fill(3)
                        if HHsel11['hmass']:
                            hh11_cutflow.Fill(4)
                            # if HHsel11['reduced_hhmass']:
                                # hh11_cutflow.Fill(5)
                            if HHsel11['dEta']:
                                hh11_cutflow.Fill(5)
                                if HHsel11['tau21']:
                                    hh11_cutflow.Fill(6)
                                    if HHsel11['SRLL']:
                                        hh11_cutflow.Fill(7)
                                        if HHsel11['SRTT']:
                                            hh11_cutflow.Fill(8)

        ###############################
        # Weighting and Uncertainties #
        ###############################

        # Initialize event weight
        weights = { 'PDF':{},
                    'Pileup':{},
                    'Trigger':{},
                    'btagSF':{}
                    }

        
        if not isData:
            # PDF weight
            weights['PDF']['up'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'up')
            weights['PDF']['down'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'down')

            # Pileup reweighting applied
            weights['Pileup']['nom'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['nom'])
            weights['Pileup']['up'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['up'])
            weights['Pileup']['down'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['down'])

            # weights['Trigger']['nom'] = 1#Trigger_Lookup( ht , TrigPlot1 )[0]
            # weights['Trigger']['up'] = 1#Trigger_Lookup( ht , TrigPlot1 )[1]
            # weights['Trigger']['down'] = 1#Trigger_Lookup( ht , TrigPlot1 )[2]

        #########################################
        # Check if 1+1 initial selection passes #
        #########################################
        if preselection_11:
            hh11_doubleB.Fill(getattr(ak8JetsColl[0],doubleB_name))
            hh11_doubleB.Fill(getattr(ak8JetsColl[1],doubleB_name))

            if HHsel11['SRTT']:
                run_21 = False
                #1+1 TT Pass
                MhhvMh11TTPass.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'nominal'))
                if runOthers and 'data' not in options.set:
                    MhhvMh11TTPassPDFup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'PDF_up'))
                    MhhvMh11TTPassPDFdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'PDF_down'))

                    MhhvMh11TTPassPUup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Pileup_up'))
                    MhhvMh11TTPassPUdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Pileup_down'))

                    # MhhvMh11TTPassTrigup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Trigger_up'))
                    # MhhvMh11TTPassTrigdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Trigger_down'))

                    # MhhvMh11TTPassBtagup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'btagSF_up'))
                    # MhhvMh11TTPassBtagdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'btagSF_down'))

            elif HHsel11['SRLL']:
                run_21 = False
                #1+1 LL Pass
                MhhvMh11LLPass.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'nominal'))
                if runOthers and 'data' not in options.set:
                    MhhvMh11LLPassPDFup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'PDF_up'))
                    MhhvMh11LLPassPDFdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'PDF_down'))

                    MhhvMh11LLPassPUup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Pileup_up'))
                    MhhvMh11LLPassPUdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Pileup_down'))

                    # MhhvMh11LLPassTrigup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Trigger_up'))
                    # MhhvMh11LLPassTrigdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Trigger_down'))

                    # MhhvMh11LLPassBtagup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'btagSF_up'))
                    # MhhvMh11LLPassBtagdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'btagSF_down'))
            
            elif HHsel11['ATTT']:
                run_21 = False
                #1+1 TT Fail
                MhhvMh11TTFail.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'nominal'))
                if runOthers and 'data' not in options.set:
                    MhhvMh11TTFailPDFup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'PDF_up'))
                    MhhvMh11TTFailPDFdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'PDF_down'))

                    MhhvMh11TTFailPUup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Pileup_up'))
                    MhhvMh11TTFailPUdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Pileup_down'))

                    # MhhvMh11TTFailTrigup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Trigger_up'))
                    # MhhvMh11TTFailTrigdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Trigger_down'))

                    # MhhvMh11TTFailBtagup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'btagSF_up'))
                    # MhhvMh11TTFailBtagdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'btagSF_down'))

            elif HHsel11['ATLL']:
                run_21 = False
                #1+1 LL Fail
                MhhvMh11LLFail.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'nominal'))
                if runOthers and 'data' not in options.set:
                    MhhvMh11LLFailPDFup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'PDF_up'))
                    MhhvMh11LLFailPDFdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'PDF_down'))

                    MhhvMh11LLFailPUup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Pileup_up'))
                    MhhvMh11LLFailPUdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Pileup_down'))

                    # MhhvMh11LLFailTrigup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Trigger_up'))
                    # MhhvMh11LLFailTrigdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'Trigger_down'))

                    # MhhvMh11LLFailBtagup.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'btagSF_up'))
                    # MhhvMh11LLFailBtagdown.Fill(h_jet0.M(),mhh11,norm_weight*Weightify(weights,'btagSF_down'))

            else:
                run_21 = True

        ##############################
        # Else do the 2+1 checks now #
        ##############################
        if not preselection_11 or run_21:
            candidateAK4s = Hemispherize(ak8JetsColl,ak4JetsColl)
            if candidateAK4s == False or len(ak8JetsColl) == 0:
                continue
            h_jet = TLorentzVector()
            h_jet.SetPtEtaPhiM(ak8JetsColl[0].pt,ak8JetsColl[0].eta,ak8JetsColl[0].phi,ak8JetsColl[0].msoftdrop)

            b_jet0 = TLorentzVector()
            b_jet1 = TLorentzVector()
            b_jet0.SetPtEtaPhiM(candidateAK4s[0].pt,candidateAK4s[0].eta,candidateAK4s[0].phi,candidateAK4s[0].mass)
            b_jet1.SetPtEtaPhiM(candidateAK4s[1].pt,candidateAK4s[1].eta,candidateAK4s[1].phi,candidateAK4s[1].mass)

            mhh21 = (h_jet+b_jet0+b_jet1).M()
            mbb = (b_jet0+b_jet1).M()
            deltaEta = abs(h_jet.Eta() - (b_jet0+b_jet1).Eta())
            mreduced = mhh21 - (h_jet.M() - 125.) - (mbb - 125)

            HHsel21['eta'] = (Cuts['eta'][0]<abs(ak8JetsColl[0].eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(candidateAK4s[0].eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(candidateAK4s[1].eta)<Cuts['eta'][1])
            HHsel21['hpt'] = Cuts['hpt'][0]<ak8JetsColl[0].pt<Cuts['hpt'][1]
            HHsel21['bpt'] = Cuts['bpt'][0]<candidateAK4s[0].pt<Cuts['bpt'][1] and Cuts['bpt'][0]<candidateAK4s[1].pt<Cuts['bpt'][1]
            HHsel21['mbb'] = Cuts['bbmass'][0]<mbb<Cuts['bbmass'][1]
            HHsel21['DeepCSV'] = Cuts['deepbtag'][0]<candidateAK4s[0].btagDeepB<Cuts['deepbtag'][1] and Cuts['deepbtag'][0]<candidateAK4s[1].btagDeepB<Cuts['deepbtag'][1]
            HHsel21['dEta'] = Cuts['dEtaAK4'][0]<deltaEta<Cuts['dEtaAK4'][1]
            HHsel21['doubleB'] = Cuts['doublebtag'][0]<getattr(ak8JetsColl[0],doubleB_name)<Cuts['doublebtag'][1]
            # HHsel21['reduced_hhmass'] = Cuts['mreduced'][0]<mreduced<Cuts['mreduced'][1]

            preselection_21 = HHsel21['eta'] and HHsel21['hpt'] and HHsel21['bpt'] and HHsel21['mbb'] and HHsel21['DeepCSV'] and HHsel21['dEta']
            if not isData:
                hh21_cutflow.Fill(1)
                if HHsel21['eta']:
                    hh21_cutflow.Fill(2)
                    if HHsel21['hpt']:
                        hh21_cutflow.Fill(3)
                        if HHsel21['bpt']:
                            hh21_cutflow.Fill(4)
                            if HHsel21['mbb']:
                                hh21_cutflow.Fill(5)
                                if HHsel21['DeepCSV']:
                                    hh21_cutflow.Fill(6)
                                    if HHsel21['dEta']:
                                        hh21_cutflow.Fill(7)
                                        if HHsel21['doubleB']:
                                            hh21_cutflow.Fill(8)
                                    
            if preselection_21:
                # b tagging scale factor
                if not isData:
                    weights['btagSF']['nom'] = reader.eval_auto_bounds('central', 0, abs(b_jet0.Eta()), b_jet0.Perp())
                    weights['btagSF']['up'] = reader.eval_auto_bounds('up', 0,  abs(b_jet0.Eta()), b_jet0.Perp())
                    weights['btagSF']['down'] = reader.eval_auto_bounds('down', 0,  abs(b_jet0.Eta()), b_jet0.Perp())

                    weights['btagSF']['nom'] *= reader.eval_auto_bounds('central', 0, abs(b_jet1.Eta()), b_jet1.Perp())
                    weights['btagSF']['up'] *= reader.eval_auto_bounds('up', 0,  abs(b_jet1.Eta()), b_jet1.Perp())
                    weights['btagSF']['down'] *= reader.eval_auto_bounds('down', 0,  abs(b_jet1.Eta()), b_jet1.Perp())


                hh21_doubleB.Fill(getattr(ak8JetsColl[0],doubleB_name))
                ##########################
                # Fill 2+1 pass and fail #
                ##########################
                if HHsel21['doubleB']:
                    MhhvMh21Pass.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'nominal'))
                    if runOthers and 'data' not in options.set:
                        #2+1 Pass
                        MhhvMh21PassPDFup.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'PDF_up'))
                        MhhvMh21PassPDFdown.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'PDF_down'))

                        MhhvMh21PassPUup.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'Pileup_up'))
                        MhhvMh21PassPUdown.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'Pileup_down'))

                        # MhhvMh21PassTrigup.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'Trigger_up'))
                        # MhhvMh21PassTrigdown.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'Trigger_down'))

                        MhhvMh21PassBtagup.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'btagSF_up'))
                        MhhvMh21PassBtagdown.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'btagSF_down'))


                else:
                    MhhvMh21Fail.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'nominal'))
                    if runOthers and 'data' not in options.set:
                        #2+1 Fail
                        MhhvMh21FailPDFup.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'PDF_up'))
                        MhhvMh21FailPDFdown.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'PDF_down'))

                        MhhvMh21FailPUup.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'Pileup_up'))
                        MhhvMh21FailPUdown.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'Pileup_down'))

                        # MhhvMh21FailTrigup.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'Trigger_up'))
                        # MhhvMh21FailTrigdown.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'Trigger_down'))

                        MhhvMh21FailBtagup.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'btagSF_up'))
                        MhhvMh21FailBtagdown.Fill(h_jet.M(),mhh21,norm_weight*Weightify(weights,'btagSF_down'))

                            
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'
    f.cd()
    f.Write()
    f.Close()
