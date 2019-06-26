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
        f = TFile( "HHpreselection"+options.year+"_"+options.set+"_job"+options.job+"of"+options.njobs+mod+'_'+options.region+".root", "recreate" )
    else:
        f = TFile( "HHpreselection"+options.year+"_"+options.set+mod+'_'+options.region+".root", "recreate" )
    f.cd()

    # print("New rootfile made")
    ###################
    # Book histograms #
    ###################
    hh11_cutflow = ROOT.TH1D('hh11_cutflow', 'hh11_cutflow', 10, 0.5, 10.5)
    hh11_cutflow.GetXaxis().SetBinLabel(1, "no cuts")
    hh11_cutflow.GetXaxis().SetBinLabel(2, "eta")
    hh11_cutflow.GetXaxis().SetBinLabel(3, "p_{T}(H)")
    hh11_cutflow.GetXaxis().SetBinLabel(4, "p_{T}(b)")
    hh11_cutflow.GetXaxis().SetBinLabel(5, "m_{bb}")
    hh11_cutflow.GetXaxis().SetBinLabel(6, "DeepCSV")
    hh11_cutflow.GetXaxis().SetBinLabel(7, "|\Delta \eta|")
    hh11_cutflow.GetXaxis().SetBinLabel(8,"LL")
    hh11_cutflow.GetXaxis().SetBinLabel(9,"TT")

    hh21_cutflow = TH1F("hh21_cutflow","hh21_cutflow",8,0.5,8.5)
    hh21_cutflow.GetXaxis().SetBinLabel(1, "no cuts")
    hh21_cutflow.GetXaxis().SetBinLabel(2, "eta")
    hh21_cutflow.GetXaxis().SetBinLabel(3, "p_{T}(H)")
    hh21_cutflow.GetXaxis().SetBinLabel(4, "p_{T}(b)")
    hh21_cutflow.GetXaxis().SetBinLabel(5, "m_{bb}")
    hh21_cutflow.GetXaxis().SetBinLabel(6, "DeepCSV")
    hh21_cutflow.GetXaxis().SetBinLabel(7, "|\Delta \eta|")
    hh21_cutflow.GetXaxis().SetBinLabel(8, "DeepDoubleB")


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
            MhhvMh21PassPDFup   = TH2F("MhhvMh21PassPDFup", "mass of HH vs mass of AK8 jet H PDF up - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassPDFdown = TH2F("MhhvMh21PassPDFdown",   "mass of HH vs mass of AK8 jet H PDF down - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassPDFup.Sumw2()
            MhhvMh21PassPDFdown.Sumw2()

            MhhvMh21PassPUup   = TH2F("MhhvMh21PassPUup", "mass of HH vs mass of AK8 jet H PU up - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassPUdown = TH2F("MhhvMh21PassPUdown",   "mass of HH vs mass of AK8 jet H PU down - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassPUup.Sumw2()
            MhhvMh21PassPUdown.Sumw2()

            MhhvMh21PassBtagup   = TH2F("MhhvMh21PassBtagup", "mass of HH vs mass of AK8 jet H Btag up - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassBtagdown = TH2F("MhhvMh21PassBtagdown",   "mass of HH vs mass of AK8 jet H Btag down - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassBtagup.Sumw2()
            MhhvMh21PassBtagdown.Sumw2()

            MhhvMh21PassTrigup   = TH2F("MhhvMh21PassTrigup", "mass of HH vs mass of AK8 jet H trig up - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassTrigdown = TH2F("MhhvMh21PassTrigdown",   "mass of HH vs mass of AK8 jet H trig down - Pass", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21PassTrigup.Sumw2()
            MhhvMh21PassTrigdown.Sumw2()

            # Fail - 2+1 
            MhhvMh21FailPDFup   = TH2F("MhhvMh21FailPDFup", "mass of HH vs mass of AK8 jet H PDF up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailPDFdown = TH2F("MhhvMh21FailPDFdown",   "mass of HH vs mass of AK8 jet H PDF up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailPDFup.Sumw2()
            MhhvMh21FailPDFdown.Sumw2()

            MhhvMh21FailPUup   = TH2F("MhhvMh21FailPUup", "mass of HH vs mass of AK8 jet H PU up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailPUdown = TH2F("MhhvMh21FailPUdown",   "mass of HH vs mass of AK8 jet H PU up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailPUup.Sumw2()
            MhhvMh21FailPUdown.Sumw2()

            MhhvMh21FailBtagup   = TH2F("MhhvMh21FailBtagup", "mass of HH vs mass of AK8 jet H Btag up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailBtagdown = TH2F("MhhvMh21FailBtagdown",   "mass of HH vs mass of AK8 jet H Btag up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailBtagup.Sumw2()
            MhhvMh21FailBtagdown.Sumw2()

            MhhvMh21FailTrigup   = TH2F("MhhvMh21FailTrigup", "mass of HH vs mass of AK8 jet H trig up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailTrigdown = TH2F("MhhvMh21FailTrigdown",   "mass of HH vs mass of AK8 jet H trig up - Fail", 9, 40, 220, 13, 700, 2000 )
            MhhvMh21FailTrigup.Sumw2()
            MhhvMh21FailTrigdown.Sumw2()

            # Pass - 1+1 TT
            MhhvMh11TTPassPDFup   = TH2F("MhhvMh11TTPassPDFup", "mass of HH vs mass of AK8 jet H PDF up - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassPDFdown = TH2F("MhhvMh11TTPassPDFdown",   "mass of HH vs mass of AK8 jet H PDF down - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassPDFup.Sumw2()
            MhhvMh11TTPassPDFdown.Sumw2()

            MhhvMh11TTPassPUup   = TH2F("MhhvMh11TTPassPUup", "mass of HH vs mass of AK8 jet H PU up - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassPUdown = TH2F("MhhvMh11TTPassPUdown",   "mass of HH vs mass of AK8 jet H PU down - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassPUup.Sumw2()
            MhhvMh11TTPassPUdown.Sumw2()

            MhhvMh11TTPassBtagup   = TH2F("MhhvMh11TTPassBtagup", "mass of HH vs mass of AK8 jet H Btag up - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassBtagdown = TH2F("MhhvMh11TTPassBtagdown",   "mass of HH vs mass of AK8 jet H Btag down - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassBtagup.Sumw2()
            MhhvMh11TTPassBtagdown.Sumw2()

            MhhvMh11TTPassTrigup   = TH2F("MhhvMh11TTPassTrigup", "mass of HH vs mass of AK8 jet H trig up - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassTrigdown = TH2F("MhhvMh11TTPassTrigdown",   "mass of HH vs mass of AK8 jet H trig down - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTPassTrigup.Sumw2()
            MhhvMh11TTPassTrigdown.Sumw2()

            # Fail - 1+1 TT
            MhhvMh11TTFailPDFup   = TH2F("MhhvMh11TTFailPDFup", "mass of HH vs mass of AK8 jet H PDF up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailPDFdown = TH2F("MhhvMh11TTFailPDFdown",   "mass of HH vs mass of AK8 jet H PDF up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailPDFup.Sumw2()
            MhhvMh11TTFailPDFdown.Sumw2()

            MhhvMh11TTFailPUup   = TH2F("MhhvMh11TTFailPUup", "mass of HH vs mass of AK8 jet H PU up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailPUdown = TH2F("MhhvMh11TTFailPUdown",   "mass of HH vs mass of AK8 jet H PU up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailPUup.Sumw2()
            MhhvMh11TTFailPUdown.Sumw2()

            MhhvMh11TTFailBtagup   = TH2F("MhhvMh11TTFailBtagup", "mass of HH vs mass of AK8 jet H Btag up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailBtagdown = TH2F("MhhvMh11TTFailBtagdown",   "mass of HH vs mass of AK8 jet H Btag up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailBtagup.Sumw2()
            MhhvMh11TTFailBtagdown.Sumw2()

            MhhvMh11TTFailTrigup   = TH2F("MhhvMh11TTFailTrigup", "mass of HH vs mass of AK8 jet H trig up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailTrigdown = TH2F("MhhvMh11TTFailTrigdown",   "mass of HH vs mass of AK8 jet H trig up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11TTFailTrigup.Sumw2()
            MhhvMh11TTFailTrigdown.Sumw2()

            # Pass - 1+1 LL 
            MhhvMh11LLPassPDFup   = TH2F("MhhvMh11LLPassPDFup", "mass of HH vs mass of AK8 jet H PDF up - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassPDFdown = TH2F("MhhvMh11LLPassPDFdown",   "mass of HH vs mass of AK8 jet H PDF down - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassPDFup.Sumw2()
            MhhvMh11LLPassPDFdown.Sumw2()

            MhhvMh11LLPassPUup   = TH2F("MhhvMh11LLPassPUup", "mass of HH vs mass of AK8 jet H PU up - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassPUdown = TH2F("MhhvMh11LLPassPUdown",   "mass of HH vs mass of AK8 jet H PU down - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassPUup.Sumw2()
            MhhvMh11LLPassPUdown.Sumw2()

            MhhvMh11LLPassBtagup   = TH2F("MhhvMh11LLPassBtagup", "mass of HH vs mass of AK8 jet H Btag up - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassBtagdown = TH2F("MhhvMh11LLPassBtagdown",   "mass of HH vs mass of AK8 jet H Btag down - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassBtagup.Sumw2()
            MhhvMh11LLPassBtagdown.Sumw2()

            MhhvMh11LLPassTrigup   = TH2F("MhhvMh11LLPassTrigup", "mass of HH vs mass of AK8 jet H trig up - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassTrigdown = TH2F("MhhvMh11LLPassTrigdown",   "mass of HH vs mass of AK8 jet H trig down - Pass", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLPassTrigup.Sumw2()
            MhhvMh11LLPassTrigdown.Sumw2()

            # Fail - 1+1 LL 
            MhhvMh11LLFailPDFup   = TH2F("MhhvMh11LLFailPDFup", "mass of HH vs mass of AK8 jet H PDF up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailPDFdown = TH2F("MhhvMh11LLFailPDFdown",   "mass of HH vs mass of AK8 jet H PDF up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailPDFup.Sumw2()
            MhhvMh11LLFailPDFdown.Sumw2()

            MhhvMh11LLFailPUup   = TH2F("MhhvMh11LLFailPUup", "mass of HH vs mass of AK8 jet H PU up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailPUdown = TH2F("MhhvMh11LLFailPUdown",   "mass of HH vs mass of AK8 jet H PU up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailPUup.Sumw2()
            MhhvMh11LLFailPUdown.Sumw2()

            MhhvMh11LLFailBtagup   = TH2F("MhhvMh11LLFailBtagup", "mass of HH vs mass of AK8 jet H Btag up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailBtagdown = TH2F("MhhvMh11LLFailBtagdown",   "mass of HH vs mass of AK8 jet H Btag up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailBtagup.Sumw2()
            MhhvMh11LLFailBtagdown.Sumw2()

            MhhvMh11LLFailTrigup   = TH2F("MhhvMh11LLFailTrigup", "mass of HH vs mass of AK8 jet H trig up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailTrigdown = TH2F("MhhvMh11LLFailTrigdown",   "mass of HH vs mass of AK8 jet H trig up - Fail", 9, 40, 220, 20, 1000, 3000 )
            MhhvMh11LLFailTrigup.Sumw2()
            MhhvMh11LLFailTrigdown.Sumw2()


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
        hh21_cutflow.Fill(1)
        hh11_cutflow.Fill(1)
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
        if (ak8JetsColl[0].jetId & 1 == 0) or (ak8JetsColl[0].jetId & 2 == 0):
            HHsel21['jetIds'] = True
            if ((ak8JetsColl[1].jetId & 1 == 0) or (ak8JetsColl[1].jetId & 2 == 0)):    
                HHsel11['jetIds'] = True
            else:
                HHsel11['jetIds'] = False
        else:
            # HHsel11['jetIds'] = False
            # HHsel21['jetIds'] = False
            continue

        # check if we have enough jets
        if len(ak8JetsColl) >= 2:
            HHsel11['nFatJet'] = True
            HHsel21['nFatJet'] = True
        elif len(ak8JetsColl) == 1:
            HHsel11['nFatJet'] = False
            HHsel21['nFatJet'] = True
        if len(ak4JetsColl) < 1:
            # HHsel11['nFatJet'] = False
            # HHsel21['nFatJet'] = False
            continue

        # Start 1+1 stuff
        HHsel11['eta'] = (Cuts['eta'][0]<abs(ak8JetsColl[0].eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(ak8JetsColl[1].eta)<Cuts['eta'][1])
        HHsel11['dEta'] = Cuts['dEtaAK8'][0] < abs(ak8JetsColl[0].eta - ak8JetsColl[1].eta) < Cuts['dEtaAK8'][1]
        HHsel11['pt'] = Cuts['hpt'][0] < ak8JetsColl[0].pt < Cuts['hpt'][1] and Cuts['hpt'][0] < ak8JetsColl[1].pt < Cuts['hpt'][1]
        HHsel11['hmass'] = Cuts['hmass'][0] < ak8JetsColl[1].msoftdrop < Cuts['hmass'][1]
        if ak8JetsColl[0].tau1 > 0 and ak8JetsColl[1].tau1 > 0:
            HHsel11['tau21'] = (Cuts['tau21'][0] < ak8JetsColl[0].tau2/ak8JetsColl[0].tau1 < Cuts['tau21'][1]) and (Cuts['tau21'][0] < ak8JetsColl[1].tau2/ak8JetsColl[1].tau1 < Cuts['tau21'][1])            
        else:
            continue
        p4_jet0, p4_jet1 = ROOT.TLorentzVector(), ROOT.TLorentzVector()
        p4_jet0.SetPtEtaPhiM(ak8JetsColl[0].pt, ak8JetsColl[0].eta, ak8JetsColl[0].phi, ak8JetsColl[0].msoftdrop)
        p4_jet1.SetPtEtaPhiM(ak8JetsColl[1].pt, ak8JetsColl[1].eta, ak8JetsColl[1].phi, ak8JetsColl[1].msoftdrop)
        mjj = (p4_jet0 + p4_jet1).M()
        mjjred = mjj - p4_jet0.M() - p4_jet1.M() + 250
        isAK8Mjj = mjjred > 750. 
        HHsel11['reduced_hhmass'] = Cuts['mreduced'][0] < mjjred < Cuts['mreduced'][1]

        HHsel11['SRTT'] = (Cuts['doublebtagTight'][0] < ak8JetsColl[0].btagHbb < Cuts['doublebtagTight'][1]) and (Cuts['doublebtagTight'][0] < ak8JetsColl[1].btagHbb < Cuts['doublebtagTight'][1])
        HHsel11['SRLL'] = (Cuts['doublebtagLoose'][0] < ak8JetsColl[0].btagHbb < Cuts['doublebtagLoose'][1]) and (Cuts['doublebtagLoose'][0] < ak8JetsColl[1].btagHbb < Cuts['doublebtagLoose'][1]) and not HHsel11['SRTT']
        HHsel11['ATTT'] = (0.0 < ak8JetsColl[0].btagHbb < Cuts['doublebtagLoose'][0]) and (Cuts['doublebtagTight'][0] < ak8JetsColl[1].btagHbb < Cuts['doublebtagTight'][1])
        HHsel11['ATLL'] = (0.0 < ak8JetsColl[0].btagHbb < Cuts['doublebtagLoose'][0]) and (Cuts['doublebtagLoose'][0] < ak8JetsColl[1].btagHbb < Cuts['doublebtagTight'][0])

        # Separate into hemispheres the leading and subleading jets
        candidateAK4s = Hemispherize(ak8JetsColl,ak4JetsColl)

        # If Hemispherize failed
        if not candidateAK4s:
            continue

        # Start 2+1 stuff
        HHsel21['eta'] = (Cuts['eta'][0]<abs(ak8JetsColl[0].eta)<Cuts['eta'][1])

        leadingFatJet = ak8JetsColl[0]
        leadingJet = ak4JetsColl[candidateAK4s[0]]
        subleadingJet = ak4JetsColl[candidateAK4s[1]]

        eta_cut = (Cuts['eta'][0]<abs(leadingJet.eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(subleadingJet.eta)<Cuts['eta'][1])
        #print("start eta cut")
        if eta_cut:
            hh21_cutflow.Fill(2)
            hh11_cutflow.Fill(2)
            # Make the lorentz vectors
            hjet = TLorentzVector()
            hjet.SetPtEtaPhiM(leadingFatJet.pt,leadingFatJet.eta,leadingFatJet.phi,leadingFatJet.msoftdrop)

            bjet1 = TLorentzVector()
            bjet2 = TLorentzVector()
            bjet1.SetPtEtaPhiM(leadingJet.pt,leadingJet.eta,leadingJet.phi,leadingJet.mass)
            bjet2.SetPtEtaPhiM(subleadingJet.pt,subleadingJet.eta,subleadingJet.phi,subleadingJet.mass)

            ht = hjet.Perp() + bjet1.Perp() + bjet2.Perp()
            Mhh = (hjet+bjet1+bjet2).M()
            Mbb = (bjet1+bjet2).M()
            deltaEta = abs(hjet.Eta() - (bjet1+bjet2).Eta())
            mreduced = Mhh - (hjet.M() - 125.) - (Mbb - 125)
            
            # Make and get all cuts
            hpt_cut = Cuts['hpt'][0]<hjet.Perp()<Cuts['hpt'][1]
            bpt_cut = Cuts['bpt'][0]<bjet1.Perp()<Cuts['bpt'][1] and Cuts['bpt'][0]<bjet2.Perp()<Cuts['bpt'][1]
            
            bbmass_cut = Cuts['bbmass'][0]<Mbb<Cuts['bbmass'][1]
            deepbtag_cut = Cuts['deepbtag'][0]<leadingJet.btagDeepB<Cuts['deepbtag'][1] and Cuts['deepbtag'][0]<subleadingJet.btagDeepB<Cuts['deepbtag'][1]
            deltaEta_cut = Cuts['deltaEta'][0]<deltaEta<Cuts['deltaEta'][1]
            mreduced_cut = Cuts['mreduced'][0]<mreduced<Cuts['mreduced'][1]

            preselection = hpt_cut and bpt_cut and bbmass_cut and deepbtag_cut and deltaEta_cut # and mreduced_cut 

            if hpt_cut:
                hh21_cutflow.Fill(3)
                hh11_cutflow.Fill(3)
                if bpt_cut:
                    hh21_cutflow.Fill(4)
                    hh11_cutflow.Fill(4)
                    if bbmass_cut:
                        hh21_cutflow.Fill(5)
                        hh11_cutflow.Fill(5)
                        if deepbtag_cut:
                            hh21_cutflow.Fill(6)
                            hh11_cutflow.Fill(6)
                            if deltaEta_cut:
                                hh21_cutflow.Fill(7)
                                hh11_cutflow.Fill(7)

            if preselection: 
                doubleB_cut = Cuts['doublebtag'][0]<leadingFatJet.btagHbb<Cuts['doublebtag'][1]
                hmass_cut = Cuts['hmass'][0]<hjet.M()<Cuts['hmass'][1]


                # Get GenParticles for use below
                # if options.set != 'data':
                #     GenParticles = Collection(event,'GenPart')

                ###############################
                # Weighting and Uncertainties #
                ###############################

                # Initialize event weight
                weights = { 'PDF':{},
                            'Pileup':{},
                            'Trigger':{},
                            'btagSF':{}
                            }

                
                if 'data' not in options.set:
                    # PDF weight
                    weights['PDF']['up'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'up')
                    weights['PDF']['down'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'down')

                    # Pileup reweighting applied
                    weights['Pileup']['nom'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['nom'])
                    weights['Pileup']['up'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['up'])
                    weights['Pileup']['down'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['down'])

                    # b tagging scale factor
                    weights['btagSF']['nom'] = reader.eval_auto_bounds('central', 0, abs(bjet1.Eta()), bjet1.Perp())
                    weights['btagSF']['up'] = reader.eval_auto_bounds('up', 0,  abs(bjet1.Eta()), bjet1.Perp())
                    weights['btagSF']['down'] = reader.eval_auto_bounds('down', 0,  abs(bjet1.Eta()), bjet1.Perp())

                    weights['btagSF']['nom'] *= reader.eval_auto_bounds('central', 0, abs(bjet2.Eta()), bjet2.Perp())
                    weights['btagSF']['up'] *= reader.eval_auto_bounds('up', 0,  abs(bjet2.Eta()), bjet2.Perp())
                    weights['btagSF']['down'] *= reader.eval_auto_bounds('down', 0,  abs(bjet2.Eta()), bjet2.Perp())

                    weights['Trigger']['nom'] = 1#Trigger_Lookup( ht , TrigPlot1 )[0]
                    weights['Trigger']['up'] = 1#Trigger_Lookup( ht , TrigPlot1 )[1]
                    weights['Trigger']['down'] = 1#Trigger_Lookup( ht , TrigPlot1 )[2]
 

                ####################################
                # Split into top tag pass and fail #
                ####################################
                
                if doubleB_cut:
                    hh21_cutflow.Fill(8)
                    MhhvMh21Pass.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal')) 

                    if runOthers and 'data' not in options.set:
                            MhhvMh21PassPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                            MhhvMh21PassPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                            MhhvMh21PassPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                            MhhvMh21PassPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                            MhhvMh21PassTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                            MhhvMh21PassTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                            MhhvMh21PassBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                            MhhvMh21PassBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))



                else:
                    MhhvMh21Fail.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal')) 

                    if runOthers and 'data' not in options.set:
                        MhhvMh21FailPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                        MhhvMh21FailPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                        MhhvMh21FailPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                        MhhvMh21FailPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                        MhhvMh21FailTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                        MhhvMh21FailTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                        MhhvMh21FailBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                        MhhvMh21FailBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))

                    doubleBTight_cut = Cuts['doublebtagTight'][0]<leadingFatJet.btagHbb<Cuts['doublebtagTight'][1]
                    doubleBLoose_cut = Cuts['doublebtagLoose'][0]<leadingFatJet.btagHbb<Cuts['doublebtagLoose'][1]
                    
                    if doubleBTight_cut:
                        hh11_cutflow.Fill(9)
                        MhhvMh11TTPass.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal'))

                        if runOthers and 'data' not in options.set:
                            #1+1 TT Pass
                            MhhvMh11TTPassPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                            MhhvMh11TTPassPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                            MhhvMh11TTPassPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                            MhhvMh11TTPassPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                            MhhvMh11TTPassTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                            MhhvMh11TTPassTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                            MhhvMh11TTPassBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                            MhhvMh11TTPassBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))

                    elif doubleBLoose_cut:
                        hh11_cutflow.Fill(8)
                        
                        MhhvMh11LLPass.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal'))
                        MhhvMh11TTFail.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal'))

                        if runOthers and 'data' not in options.set:
                            #1+1 TT Fail
                            MhhvMh11TTFailPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                            MhhvMh11TTFailPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                            MhhvMh11TTFailPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                            MhhvMh11TTFailPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                            MhhvMh11TTFailTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                            MhhvMh11TTFailTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                            MhhvMh11TTFailBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                            MhhvMh11TTFailBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))
                            #1+1 LL Pass
                            MhhvMh11LLPassPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                            MhhvMh11LLPassPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                            MhhvMh11LLPassPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                            MhhvMh11LLPassPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                            MhhvMh11LLPassTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                            MhhvMh11LLPassTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                            MhhvMh11LLPassBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                            MhhvMh11LLPassBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))

                    else:
                        MhhvMh11TTFail.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal'))
                        MhhvMh11LLFail.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal'))

                        if runOthers and 'data' not in options.set:
                            #1+1 TT Fail
                            MhhvMh11TTFailPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                            MhhvMh11TTFailPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                            MhhvMh11TTFailPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                            MhhvMh11TTFailPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                            MhhvMh11TTFailTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                            MhhvMh11TTFailTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                            MhhvMh11TTFailBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                            MhhvMh11TTFailBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))
                            #1+1 LL Fail
                            MhhvMh11LLFailPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                            MhhvMh11LLFailPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                            MhhvMh11LLFailPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                            MhhvMh11LLFailPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                            MhhvMh11LLFailTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                            MhhvMh11LLFailTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                            MhhvMh11LLFailBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                            MhhvMh11LLFailBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))     
                            
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'
    f.cd()
    f.Write()
    f.Close()
