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

import Bstar_Functions_local
from Bstar_Functions_local import *


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
    parser.add_option('-n', '--num', metavar='F', type='string', action='store',
                    default   =   'all',
                    dest      =   'num',
                    help      =   'job number')
    parser.add_option('-j', '--jobs', metavar='F', type='string', action='store',
                    default   =   '1',
                    dest      =   'jobs',
                    help      =   'number of jobs')

    (options, args) = parser.parse_args()

    # Prep for deepcsv b-tag if deepak8 is off
    # From https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration
    if options.deepak8 == 'off':
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

    # Trigger
    # if options.year == '16':
    #     tname = 'HLT_PFHT800ORHLT_PFHT900ORHLT_PFJet450'
    #     pretrig_string = 'HLT_Mu50'
    #     # btagtype = 'btagCSVV2'
    # elif options.year == '17' or options.year == '18':
    #     tname = 'HLT_PFHT1050ORHLT_PFJet500'
    #     pretrig_string = 'HLT_IsoMu27'
    
    tname = 
    pretrig_string = 
    btagtype = 'btagDeepB'


    # JECs
    runOthers = True
    if options.set == 'data':
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
    jobs=int(options.jobs)
    if jobs != 1:
        num=int(options.num)
        jobs=int(options.jobs)
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
        
    if options.set != 'data':
        PileFile = TFile.Open("pileup/PileUp_Ratio_ttbar"+tempyear+".root")
        PilePlots = {
            "nom": PileFile.Get("Pileup_Ratio"),
            "up": PileFile.Get("Pileup_Ratio_up"),
            "down": PileFile.Get("Pileup_Ratio_down")}
        
        # ttagsffile = TFile.Open('SFs/20'+tempyear+'TopTaggingScaleFactors.root')

    #############################
    # Make new file for storage #
    #############################
    if jobs!=1:
        f = TFile( "HHpreselection"+options.year+"_"+options.set+"_job"+options.num+"of"+options.jobs+"_"+mod+'_'+options.region+".root", "recreate" )
    else:
        f = TFile( "HHpreselection"+options.year+"_"+options.set+"_"+mod+'_'+options.region+".root", "recreate" )
    f.cd()

    
    ###################
    # Book histograms #
    ###################
    MhhvMhPass     = TH2F("MhhvMhPass",     "mass of tw vs mass of top - Pass", 60, 50, 350, 35, 500, 4000 )
    MhhvMhFail     = TH2F("MhhvMhFail",     "mass of tw vs mass of top - Fail", 60, 50, 350, 35, 500, 4000 )
    MhhvMhPass.Sumw2()
    MhhvMhFail.Sumw2()

    nev = TH1F("nev",   "nev",      1, 0, 1 )

    if runOthers == True:
        if options.set != 'data':
            MhhvMhPassPDFup   = TH2F("MhhvMhPassPDFup", "mass of tw vs mass of top PDF up - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassPDFdown = TH2F("MhhvMhPassPDFdown",   "mass of tw vs mass of top PDF down - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassPDFup.Sumw2()
            MhhvMhPassPDFdown.Sumw2()

            MhhvMhPassPUup   = TH2F("MhhvMhPassPUup", "mass of tw vs mass of top PU up - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassPUdown = TH2F("MhhvMhPassPUdown",   "mass of tw vs mass of top PU down - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassPUup.Sumw2()
            MhhvMhPassPUdown.Sumw2()

            MhhvMhPassScaleup   = TH2F("MhhvMhPassScaleup", "mass of tw vs mass of Q^2 scale up - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassScaledown = TH2F("MhhvMhPassScaledown",   "mass of tw vs mass of Q^2 scale down - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassScaleup.Sumw2()
            MhhvMhPassScaledown.Sumw2()

            MhhvMhPassTrigup   = TH2F("MhhvMhPassTrigup", "mass of tw vs mass of top trig up - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassTrigdown = TH2F("MhhvMhPassTrigdown",   "mass of tw vs mass of top trig down - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassTrigup.Sumw2()
            MhhvMhPassTrigdown.Sumw2()

            # Fail
            MhhvMhFailPDFup   = TH2F("MhhvMhFailPDFup", "mass of tw vs mass of top PDF up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailPDFdown = TH2F("MhhvMhFailPDFdown",   "mass of tw vs mass of top PDF up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailPDFup.Sumw2()
            MhhvMhFailPDFdown.Sumw2()

            MhhvMhFailPUup   = TH2F("MhhvMhFailPUup", "mass of tw vs mass of top PU up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailPUdown = TH2F("MhhvMhFailPUdown",   "mass of tw vs mass of top PU up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailPUup.Sumw2()
            MhhvMhFailPUdown.Sumw2()

            MhhvMhFailScaleup   = TH2F("MhhvMhFailScaleup", "mass of tw vs mass of Q^2 scale up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailScaledown = TH2F("MhhvMhFailScaledown",   "mass of tw vs mass of Q^2 scale down - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailScaleup.Sumw2()
            MhhvMhFailScaledown.Sumw2()

            MhhvMhFailTrigup   = TH2F("MhhvMhFailTrigup", "mass of tw vs mass of top trig up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailTrigdown = TH2F("MhhvMhFailTrigdown",   "mass of tw vs mass of top trig up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailTrigup.Sumw2()
            MhhvMhFailTrigdown.Sumw2()


        MhhvMh_cut1    = TH2F("MhhvMh_cut1",  "mass of tw after pt cuts and dy cuts", 60, 50, 350, 35, 500, 4000)
        MhhvMh_cut2    = TH2F("MhhvMh_cut2",  "mass of tw after tau21 cut", 60, 50, 350, 35, 500, 4000)
        MhhvMh_cut3    = TH2F("MhhvMh_cut3",  "mass of tw after wmass cut", 60, 50, 350, 35, 500, 4000)
        MhhvMh_cut4    = TH2F("MhhvMh_cut4", "mass of tw after tau32 cut", 60, 50, 350, 35, 500, 4000)
        MhhvMh_cut5    = TH2F("MhhvMh_cut5", "mass of tw after sjbtag cut", 60, 50, 350, 35, 500, 4000)
        MhhvMh_cut1.Sumw2()
        MhhvMh_cut2.Sumw2()
        MhhvMh_cut3.Sumw2()
        MhhvMh_cut4.Sumw2()
        MhhvMh_cut5.Sumw2()

        Pt1presel = TH1F("Pt1presel",         "Leading jet pt (GeV)",             46, 350, 1500 )
        Pt2presel = TH1F("Pt2presel",         "Subleading jet pt (GeV)",             46, 350, 1500 )
        deltaRap = TH1F("deltaY",         "Delta Y between leading jets (GeV)",             50, 0, 2.5)
        Pt1presel.Sumw2()
        Pt2presel.Sumw2()
        deltaRap.Sumw2()

        EtaTop      = TH1F("EtaTop",        "Top Candidate eta",                  12, -2.4, 2.4 )
        EtaW   = TH1F("EtaW",     "W Candidate eta",              12, -2.4, 2.4 )
        EtaTop.Sumw2()
        EtaW.Sumw2()

        PtTop       = TH1F("PtTop",         "Top Candidate pt (GeV)",             46, 350, 1500 )
        PtW         = TH1F("PtW",           "W Candidate pt (GeV)",               46, 350, 1500 )
        PtTopW      = TH1F("PtTopW",        "pt of tw system",                35,   0, 700 )
        PtTop.Sumw2()
        PtW.Sumw2()
        PtTopW.Sumw2()

        PhiTop    = TH1F("PhiTop",      "Top Candidate Phi (rad)",                       12, -math.pi, math.pi )
        PhiW      = TH1F("PhiW",    "Top Candidate Phi (rad)",                       12, -math.pi, math.pi )
        dPhi      = TH1F("dPhi",        "delta theat between Top and W Candidates",          12, 2.2, math.pi )
        PhiTop.Sumw2()
        PhiW.Sumw2()
        dPhi.Sumw2()


    ###############################
    # Grab root file that we want #
    ###############################
    file_string = Load_jetNano(options.set,options.year)
    file = TFile.Open(file_string)

    ################################
    # Grab event tree from nanoAOD #
    ################################
    inTree = file.Get("Events")
    elist,jsonFiter = preSkim(inTree,None,'')
    inTree = InputTree(inTree,elist)
    treeEntries = inTree.entries

    #############################
    # Get process normalization #
    #############################
    norm_weight = 1
    if options.set != 'data':
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
        # if count > 1:
            # current_event_time = time.time()
            # event_time_sum += (current_event_time - last_event_time)
        # sys.stdout.write("%i / %i ... \r" % (count,(highBinEdge-lowBinEdge)))
            # sys.stdout.write("Avg time = %f " % (event_time_sum/count) )
        # sys.stdout.flush()
            # last_event_time = current_event_time
        if count % 10000 == 0 :
            print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

        # Grab the event
        event = Event(inTree, entry)

        # Apply triggers first
        if options.set == 'data':
            passt = False
            for t in tname.split('OR'):
                try: 
                    if inTree.readBranch(t):
                        passt = True
                except:
                    continue

            if not passt:
                continue

        # Have to grab Collections for each collection of interest
        # -- collections are for types of objects where there could be multiple values
        #    for a single event
        ak8JetsColl = Collection(event, "FatJet")
        ak4JetsColl = Collection(event, "Jet")

        # Now jetID which (in binary #s) is stored with bit1 as loose, bit2 as tight, and filters (after grabbing jet collections)
        try:
            for i in range(2):
                looseJetID = ak8JetsColl[i].jetId 
                if (ak8JetsColl[i].jetId & 1 == 0):    # if not loose
                    if (ak8JetsColl[i].jetId & 2 == 0): # and if not tight - Need to check here because loose is always false in 2017
                        continue                      # move on
        except:
            # print 'Skipping event ' + str(entry) + ' because fewer than two jets exist - ' + str(len(ak8JetsColl))
            continue

        # Now filters/flags
        # flagColl = Collection(event,'Flag')
        filters = [inTree.readBranch('Flag_goodVertices'),
                   inTree.readBranch('Flag_HBHENoiseFilter'),
                   inTree.readBranch('Flag_HBHENoiseIsoFilter'),
                   inTree.readBranch('Flag_globalTightHalo2016Filter'),
                   inTree.readBranch('Flag_EcalDeadCellTriggerPrimitiveFilter'),
                   inTree.readBranch('Flag_eeBadScFilter')]

        filterFails = 0
        for thisFilter in filters:
            if thisFilter == 0:
                filterFails += 1
        if filterFails > 0:
            continue

        # Separate into hemispheres the leading and subleading jets
        Jetsh0,Jetsh1 = Hemispherize(ak8JetsColl)

        if (len(Jetsh1) < 1):
            # print str(entry)
            # print '\tJetsh0 = ',
            # print Jetsh0
            # print '\tJetsh1 = ',
            # print Jetsh1

            # for i in range(len(Jetsh0)):
            #     for j in range(i,len(Jetsh0)):
            #         if i != j:
            #             sep = deltaPhi(ak8JetsColl[Jetsh0[i]].phi,ak8JetsColl[Jetsh0[j]].phi)
            #             print '\tJet'+str(i)+' vs Jet'+str(j)+': ' + str(sep/3.1415)+'*pi'
            continue

        leadingJet = ak8JetsColl[Jetsh0[0]]
        subleadingJet = ak8JetsColl[Jetsh1[0]]

        # Get and make the DAK8 variables
        if options.year == '16' and ('MD' not in options.deepak8) and options.deepak8 != 'off':
            dak8_qcd_raw_lead = leadingJet.nnQCDb + leadingJet.nnQCDbb + leadingJet.nnQCDc + leadingJet.nnQCDcc + leadingJet.nnQCDothers
            dak8_qcd_raw_sublead = subleadingJet.nnQCDb + subleadingJet.nnQCDbb + subleadingJet.nnQCDc + subleadingJet.nnQCDcc + subleadingJet.nnQCDothers

            dak8_top_raw_lead = leadingJet.nnTbcq + leadingJet.nnTbqq
            dak8_top_raw_sublead = subleadingJet.nnTbcq + subleadingJet.nnTbqq

            dak8_top_lead = dak8_top_raw_lead/(dak8_top_raw_lead+dak8_qcd_raw_lead) if (dak8_top_raw_lead+dak8_qcd_raw_lead) > 0 else 0
            dak8_top_sublead = dak8_top_raw_sublead/(dak8_top_raw_sublead+dak8_qcd_raw_sublead) if (dak8_top_raw_sublead+dak8_qcd_raw_sublead) > 0 else 0

        elif options.year == '16' and ('MD' in options.deepak8) and options.deepak8 != 'off':
            dak8_qcd_raw_lead = leadingJet.nnMDQCDb + leadingJet.nnMDQCDbb + leadingJet.nnMDQCDc + leadingJet.nnMDQCDcc + leadingJet.nnMDQCDothers
            dak8_qcd_raw_sublead = subleadingJet.nnMDQCDb + subleadingJet.nnMDQCDbb + subleadingJet.nnMDQCDc + subleadingJet.nnMDQCDcc + subleadingJet.nnMDQCDothers

            dak8_top_raw_lead = leadingJet.nnMDTbcq + leadingJet.nnMDTbqq
            dak8_top_raw_sublead = subleadingJet.nnMDTbcq + subleadingJet.nnMDTbqq

            dak8_top_lead = dak8_top_raw_lead/(dak8_top_raw_lead+dak8_qcd_raw_lead) if (dak8_top_raw_lead+dak8_qcd_raw_lead) > 0 else 0
            dak8_top_sublead = dak8_top_raw_sublead/(dak8_top_raw_sublead+dak8_qcd_raw_sublead) if (dak8_top_raw_sublead+dak8_qcd_raw_sublead) > 0 else 0
        elif options.year == '17' and ('MD' not in options.deepak8) and options.deepak8 != 'off':
            dak8_top_lead = leadingJet.deepTag_TvsQCD
            dak8_top_sublead = subleadingJet.deepTag_TvsQCD
        elif options.year == '17' and ('MD' in options.deepak8) and options.deepak8 != 'off':
            dak8_top_lead = leadingJet.deepTagMD_TvsQCD
            dak8_top_sublead = subleadingJet.deepTagMD_TvsQCD

        elif options.deepak8 == 'off':
            dak8_top_lead = -10
            dak8_top_sublead = -10

        # if LeptonVeto(Collection(event, "Electron"),Collection(event, "Muon")):
        #     continue

        eta_cut = (Cuts['eta'][0]<abs(leadingJet.eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(subleadingJet.eta)<Cuts['eta'][1])

        if eta_cut:
            doneAlready = False

            for hemis in ['hemis0','hemis1']:
                if hemis == 'hemis0':
                    # Load up the ttree values
                    tVals = {
                        "tau1":leadingJet.tau1,
                        "tau2":leadingJet.tau2,
                        "tau3":leadingJet.tau3,
                        "phi":leadingJet.phi,
                        "mass":getattr(leadingJet,'mass'+mass_name),
                        "pt":leadingJet.pt,
                        "eta":leadingJet.eta,
                        "SDmass":leadingJet.msoftdrop,
                        "dak8_top": dak8_top_lead,
                        "subJetIdx1":leadingJet.subJetIdx1,
                        "subJetIdx2":leadingJet.subJetIdx2
                    }
                    wVals = {
                        "tau1":subleadingJet.tau1,
                        "tau2":subleadingJet.tau2,
                        "tau3":subleadingJet.tau3,
                        "phi":subleadingJet.phi,
                        "mass":getattr(subleadingJet,'mass'+mass_name),
                        "pt":subleadingJet.pt,
                        "eta":subleadingJet.eta,
                        "SDmass":subleadingJet.msoftdrop,
                        "dak8_top": dak8_top_sublead,
                        "subJetIdx1":subleadingJet.subJetIdx1,
                        "subJetIdx2":subleadingJet.subJetIdx2
                    }


                elif hemis == 'hemis1' and doneAlready == False:
                    wVals = {
                        "tau1":leadingJet.tau1,
                        "tau2":leadingJet.tau2,
                        "tau3":leadingJet.tau3,
                        "phi":leadingJet.phi,
                        "mass":getattr(leadingJet,'mass'+mass_name),
                        "pt":leadingJet.pt,
                        "eta":leadingJet.eta,
                        "SDmass":leadingJet.msoftdrop,
                        "dak8_top": dak8_top_lead,
                        "subJetIdx1":leadingJet.subJetIdx1,
                        "subJetIdx2":leadingJet.subJetIdx2
                    }
                    tVals = {
                        "tau1":subleadingJet.tau1,
                        "tau2":subleadingJet.tau2,
                        "tau3":subleadingJet.tau3,
                        "phi":subleadingJet.phi,
                        "mass":getattr(subleadingJet,'mass'+mass_name),
                        "pt":subleadingJet.pt,
                        "eta":subleadingJet.eta,
                        "SDmass":subleadingJet.msoftdrop,
                        "dak8_top": dak8_top_sublead,
                        "subJetIdx1":subleadingJet.subJetIdx1,
                        "subJetIdx2":subleadingJet.subJetIdx2
                    }

                elif hemis == 'hemis1' and doneAlready == True:
                    continue


                # Make the lorentz vectors
                tjet = TLorentzVector()
                tjet.SetPtEtaPhiM(tVals["pt"],tVals["eta"],tVals["phi"],tVals["mass"])

                wjet = TLorentzVector()
                wjet.SetPtEtaPhiM(wVals["pt"],wVals["eta"],wVals["phi"],wVals["mass"])

                ht = tjet.Perp() + wjet.Perp()
                MtopW = (tjet+wjet).M()
                
                # Make and get all cuts
                dy_val = abs(tjet.Rapidity()-wjet.Rapidity())
                wpt_cut = Cuts['wpt'][0]<wjet.Perp()<Cuts['wpt'][1]
                tpt_cut = Cuts['tpt'][0]<tjet.Perp()<Cuts['tpt'][1]
                dy_cut = Cuts['dy'][0]<=dy_val<Cuts['dy'][1]
                
                if runOthers:
                    deltaRap.Fill(dy_val)
                    Pt1presel.Fill(leadingJet.pt)
                    Pt2presel.Fill(subleadingJet.pt)

                # Standard W tag
                if options.region != 'ttbar':
                    if wVals['tau1'] > 0:
                        tau21val = wVals['tau2']/wVals['tau1']
                    else:
                        continue

                    tau21_cut =  Cuts['tau21'][0]<=tau21val<Cuts['tau21'][1]

                    wmass_cut = Cuts['wmass'][0]<=wVals["SDmass"]<Cuts['wmass'][1]

                    preselection = wpt_cut and tpt_cut and dy_cut and wmass_cut and tau21_cut
                
                    if wpt_cut and tpt_cut and dy_cut:
                        if runOthers: MhhvMh_cut1.Fill(tjet.M(),MtopW)
                        if tau21_cut:
                            if runOthers: MhhvMh_cut2.Fill(tjet.M(),MtopW)
                            if wmass_cut:
                                if runOthers: MhhvMh_cut3.Fill(tjet.M(),MtopW)

                # If tagging regular W as a top
                else:
                    wmass_cut = Cuts['tmass'][0]<=wVals["SDmass"]<Cuts['tmass'][1]

                    if options.deepak8 != 'off':
                        if 'MD' in options.deepak8:
                            w_cut = Cuts['DeepAK8_top_'+options.deepak8[2:]][0]<=wVals['dak8_top']<Cuts['DeepAK8_top_'+options.deepak8[2:]][1]
                        else:
                            w_cut = Cuts['DeepAK8_top_'+options.deepak8][0]<=wVals['dak8_top']<Cuts['DeepAK8_top_'+options.deepak8][1]
                        preselection = wpt_cut and tpt_cut and dy_cut and wmass_cut and w_cut

                    else:
                        if wVals['tau2'] > 0:
                            w_tau32val = wVals['tau3']/wVals['tau2']
                        else:
                            continue
                        w_tau32_cut = Cuts['tau32tight'][0]<=w_tau32val<Cuts['tau32tight'][1]

                        if (wVals['subJetIdx1'] < 0) or (wVals['subJetIdx1'] >= len(subJetsColl)):
                            if (wVals['subJetIdx2'] < 0) or (wVals['subJetIdx2'] >= len(subJetsColl)):  # if both negative, throw away event
                                continue
                            else:   # if idx2 not negative or bad index, use that
                                w_btagval = getattr(subJetsColl[wVals['subJetIdx2']],btagtype)

                        else:
                            if (wVals['subJetIdx2'] < 0) or (wVals['subJetIdx2'] >= len(subJetsColl)): # if idx1 not negative, use that
                                w_btagval = getattr(subJetsColl[wVals['subJetIdx1']],btagtype)
                            # if both not negative, use largest
                            else:
                                # print str(wVals['subJetIdx1']) +' '+str(len(subJetsColl))
                                # print str(wVals['subJetIdx2']) +' '+str(len(subJetsColl))
                                w_btagval = max(getattr(subJetsColl[wVals['subJetIdx1']],btagtype), getattr(subJetsColl[wVals['subJetIdx2']],btagtype))
                        
                        # if options.year == '16':
                        #     w_sjbtag_cut = Cuts['sjbtag'][0]<= w_btagval<Cuts['sjbtag'][1]
                        # else:
                        w_sjbtag_cut = Cuts['deepbtag'][0]<= w_btagval<Cuts['deepbtag'][1]

                        preselection = wpt_cut and tpt_cut and dy_cut and wmass_cut and w_sjbtag_cut and w_tau32_cut

                if preselection: 
                    doneAlready = True
                    # Get GenParticles for use below
                    if options.set != 'data':
                        GenParticles = Collection(event,'GenPart')

                    ###############################
                    # Weighting and Uncertainties #
                    ###############################

                    # Initialize event weight
                    weights = { 'PDF':{},
                                'Pileup':{},
                                'Topsf':{},
                                'Q2':{},
                                'sjbsf':{},
                                'Wsf':{},
                                'Trigger':{},
                                'Ptreweight':{},
                                'Extrap':{}}

                    
                    if options.set!="data":
                        # PDF weight
                        weights['PDF']['up'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'up')
                        weights['PDF']['down'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'down')

                        # Q2 Scale
                        weights['Q2']['up'] = inTree.readBranch('LHEScaleWeight')[8]
                        weights['Q2']['down'] = inTree.readBranch('LHEScaleWeight')[0]

                        # Pileup reweighting applied
                        if options.pileup == 'on':
                            weights['Pileup']['nom'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['nom'])
                            weights['Pileup']['up'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['up'])
                            weights['Pileup']['down'] = PU_Lookup(inTree.readBranch('Pileup_nPU'),PilePlots['down'])

                        # Top tagging DAK8 scale factor 
                        if "QCD" not in options.set and options.deepak8 != 'off':
                            sftdeep = SFTdeep_Lookup(tVals['pt'],ttagsfPlots)
                            weights['Topsf']['nom'] = sftdeep[0]
                            weights['Topsf']['up'] = sftdeep[1]
                            weights['Topsf']['down'] = sftdeep[2]
                        # Top tagging tau32+sjbtag scale factor 
                        elif "QCD" not in options.set and options.deepak8 == 'off':
                            sft = SFT_Lookup_MERGEDONLY(tjet,ttagsffile)#(tjet, ttagsffile, GenParticles, options.tau32)#_MERGEDONLY(tjet, ttagsffile)#, GenParticles)
                            weights['Topsf']['nom'] = sft[0]
                            weights['Topsf']['up'] = sft[1]
                            weights['Topsf']['down'] = sft[2]

                            # Subjet b tagging scale factor
                            weights['sjbsf']['nom'] = reader.eval_auto_bounds('central', 0, abs(tVals['eta']), tVals['pt'])
                            weights['sjbsf']['up'] = reader.eval_auto_bounds('up', 0, abs(tVals['eta']), tVals['pt'])
                            weights['sjbsf']['down'] = reader.eval_auto_bounds('down', 0, abs(tVals['eta']), tVals['pt'])


                        if wIsTtagged:
                            # Top tagging DAK8 scale factor 
                            if "QCD" not in options.set and options.deepak8 != 'off':
                                sftdeep = SFTdeep_Lookup(wVals['pt'],ttagsfPlots)
                                weights['Topsf']['nom'] *= sftdeep[0]
                                weights['Topsf']['up'] *= sftdeep[1]
                                weights['Topsf']['down'] *= sftdeep[2]
                            # Top tagging tau32+sjbtag scale factor 
                            elif "QCD" not in options.set and options.deepak8 == 'off':
                                sft = SFT_Lookup_MERGEDONLY(wjet,ttagsffile)#(wjet, ttagsffile, GenParticles, options.tau32)#, GenParticles)
                                weights['Topsf']['nom'] *= sft[0]
                                weights['Topsf']['up'] *= sft[1]
                                weights['Topsf']['down'] *= sft[2]

                                # Subjet b tagging scale factor
                                weights['sjbsf']['nom'] *= reader.eval_auto_bounds('central', 0, abs(wVals['eta']), wVals['pt'])
                                weights['sjbsf']['up'] *= reader.eval_auto_bounds('up', 0, abs(wVals['eta']), wVals['pt'])
                                weights['sjbsf']['down'] *= reader.eval_auto_bounds('down', 0, abs(wVals['eta']), wVals['pt'])

                    

                    if not wIsTtagged:
                        # Determine purity for scale factor
                        if options.region == 'default':
                            Wpurity = 'HP'
                        elif options.region == 'sideband':
                            if options.year == '16':
                                Wpurity = 'LP'
                            elif options.year != '16' and (Cuts['tau21LP'][0] < tau21val < Cuts['tau21LP'][1]):
                                Wpurity = 'LP'
                            else:
                                Wpurity = False
                        else:
                            Wpurity = False

                        # W matching
                        WJetMatchingRequirement = 0
                        if (options.set.find('tW') != -1 or options.set.find('signal') != -1) and not wIsTtagged:
                            if WJetMatching(GenParticles) == 1 and Wpurity != False:
                                wtagsf = Cons['wtagsf_'+Wpurity]
                                wtagsfsig = Cons['wtagsfsig_'+Wpurity]

                                weights['Wsf']['nom'] = wtagsf
                                weights['Wsf']['up'] = (wtagsf + wtagsfsig)
                                weights['Wsf']['down'] = (wtagsf - wtagsfsig)

                        # Get the extrapolation uncertainty
                        extrap = ExtrapUncert_Lookup(wjet.Perp(),Wpurity,options.year)
                        weights['Extrap']['up'] = 1+extrap
                        weights['Extrap']['down'] = 1-extrap

                    # Trigger weight applied
                    if tname != 'none' and options.set!='data' :
                        weights['Trigger']['nom'] = Trigger_Lookup( ht , TrigPlot1 )[0]
                        weights['Trigger']['up'] = Trigger_Lookup( ht , TrigPlot1 )[1]
                        weights['Trigger']['down'] = Trigger_Lookup( ht , TrigPlot1 )[2]

                    # Top pt reweighting
                    if options.ptreweight == "on" and options.set.find('ttbar') != -1:
                        weights['Ptreweight']['nom'] = PTW_Lookup(GenParticles)
                        weights['Ptreweight']['up'] = 1.5*PTW_Lookup(GenParticles)
                        weights['Ptreweight']['down'] = 0.5*PTW_Lookup(GenParticles)
       

                    

                    ####################################
                    # Split into top tag pass and fail #
                    ####################################
                    if options.deepak8 == 'off':
                        if tVals['tau2'] > 0:
                            tau32val = tVals['tau3']/tVals['tau2']
                        else:
                            continue
                        tau32_cut = Cuts['tau32'+options.tau32][0]<=tau32val<Cuts['tau32'+options.tau32][1]

                        if (tVals['subJetIdx1'] < 0) or (tVals['subJetIdx1'] >= len(subJetsColl)):
                            if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)):  # if both negative, throw away event
                                continue
                            else:   # if idx2 not negative or bad index, use that
                                btagval = getattr(subJetsColl[tVals['subJetIdx2']],btagtype)

                        else:
                            if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)): # if idx1 not negative, use that
                                btagval = getattr(subJetsColl[tVals['subJetIdx1']],btagtype)
                            # if both not negative, use largest
                            else:
                                btagval = max(getattr(subJetsColl[tVals['subJetIdx1']],btagtype), getattr(subJetsColl[tVals['subJetIdx2']],btagtype))
                            
                        # if options.year == '16':
                        #     sjbtag_cut = Cuts['sjbtag'][0]<= btagval<Cuts['sjbtag'][1]
                        # else:
                        sjbtag_cut = Cuts['deepbtag'][0]<= btagval<Cuts['deepbtag'][1]
                            

                        top_tag = sjbtag_cut and tau32_cut

                        if tau32_cut:
                            if runOthers: MhhvMh_cut4.Fill(tjet.M(),MtopW)
                            if sjbtag_cut:
                                if runOthers: MhhvMh_cut5.Fill(tjet.M(),MtopW)

                    else:
                        if 'MD' in options.deepak8:
                            top_tag = Cuts['DeepAK8_top_'+options.deepak8[2:]][0]<tVals['dak8_top']<Cuts['DeepAK8_top_'+options.deepak8[2:]][1]
                        else:
                            top_tag = Cuts['DeepAK8_top_'+options.deepak8][0]<tVals['dak8_top']<Cuts['DeepAK8_top_'+options.deepak8][1]
    
                    if runOthers:
                        if options.deepak8 != 'off':
                            dak8Top.Fill(tVals['dak8_top'],norm_weight*Weightify(weights, 'nominal'))
                            dak8Top_vs_mt.Fill(tjet.M(),tVals['dak8_top'],norm_weight*Weightify(weights,'nominal'))
                            if MtopW > 900 and MtopW < 1100:
                                dak8Top_vs_mt_slice1.Fill(tjet.M(),tVals['dak8_top'],norm_weight*Weightify(weights,'nominal'))
                            elif MtopW > 1100 and MtopW < 2400:
                                dak8Top_vs_mt_slice2.Fill(tjet.M(),tVals['dak8_top'],norm_weight*Weightify(weights,'nominal'))
                            elif MtopW > 2400:
                                dak8Top_vs_mt_slice3.Fill(tjet.M(),tVals['dak8_top'],norm_weight*Weightify(weights,'nominal'))

                        else:
                            Tau32.Fill(tau32val,norm_weight*Weightify(weights, 'nominal'))
                            SJbtag.Fill(btagval,norm_weight*Weightify(weights, 'nominal'))

                    if top_tag:

                        MhhvMhPass.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 

                        if runOthers:
                            if options.set != 'data':
                                MhhvMhPassPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up'))
                                MhhvMhPassPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down'))

                                MhhvMhPassPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up'))
                                MhhvMhPassPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down'))

                                MhhvMhPassTopup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_up'))
                                MhhvMhPassTopdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_down'))

                                MhhvMhPassScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up'))
                                MhhvMhPassScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down'))

                                MhhvMhPassSjbtagup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_up'))
                                MhhvMhPassSjbtagdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_down'))

                                MhhvMhPassTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up'))
                                MhhvMhPassTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down'))

                                if not wIsTtagged:
                                    MhhvMhPassWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up')) 
                                    MhhvMhPassWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down'))

                                    MhhvMhPassExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up'))
                                    MhhvMhPassExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down'))

                                MhhvMhPassTptup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_up'))
                                MhhvMhPassTptdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_down')) 

                            EtaTop.Fill(tjet.Eta(),norm_weight*Weightify(weights,'nominal'))
                            EtaW.Fill(wjet.Eta(),norm_weight*Weightify(weights,'nominal'))
                            
                            PtTop.Fill(tjet.Perp(),norm_weight*Weightify(weights,'nominal'))
                            PtW.Fill(wjet.Perp(),norm_weight*Weightify(weights,'nominal'))
                            PtTopW.Fill((tjet+wjet).Perp(),norm_weight*Weightify(weights,'nominal'))
                            
                            PhiTop.Fill(tjet.Phi(),norm_weight*Weightify(weights,'nominal'))
                            PhiW.Fill(wjet.Phi(),norm_weight*Weightify(weights,'nominal'))
                            dPhi.Fill(abs(tjet.Phi()-wjet.Phi()),norm_weight*Weightify(weights,'nominal'))


                    else:
                        MhhvMhFail.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 

                        if flatTag() < 0.1:
                            dumbTagPass.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 
                        else:
                            dumbTagFail.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 

                        if runOthers and options.set != 'data':
                            MhhvMhFailPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up'))
                            MhhvMhFailPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down'))

                            MhhvMhFailPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up'))
                            MhhvMhFailPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down'))

                            MhhvMhFailTopup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_up'))
                            MhhvMhFailTopdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_down'))

                            MhhvMhFailScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up'))
                            MhhvMhFailScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down'))

                            MhhvMhFailSjbtagup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_up'))
                            MhhvMhFailSjbtagdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_down'))

                            MhhvMhFailTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up'))
                            MhhvMhFailTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down'))
                            
                            if not wIsTtagged:
                                MhhvMhFailWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up')) 
                                MhhvMhFailWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down'))

                                MhhvMhFailExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up'))
                                MhhvMhFailExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down'))

                            MhhvMhFailTptup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_up'))
                            MhhvMhFailTptdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_down')) 

                            
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'
    f.cd()
    f.Write()
    f.Close()



    
