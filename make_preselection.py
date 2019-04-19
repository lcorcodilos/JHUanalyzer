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
        # btagtype = 'btagCSVV2'
    # elif options.year == '17' or options.year == '18':
    triggers = [
        'HLT_PFHT780',
        'HLT_AK8PFHT750_TrimMass50',
        'HLT_AK8PFJet360_TrimMass30',
        'HLT_AK8PFJet330_TrimMass30_PFAK8BTagDeepCSV_p17'
    ]
    pretrig_string = 'HLT_IsoMu27'

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
        PileFile = TFile.Open("pileup/PileUp_Ratio_ttbar"+options.year+".root")
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
    MhhvMhPass     = TH2F("MhhvMhPass",     "mass of HH vs mass of AK8 jet H - Pass", 60, 50, 350, 35, 500, 4000 )
    MhhvMhFail     = TH2F("MhhvMhFail",     "mass of HH vs mass of AK8 jet H - Fail", 60, 50, 350, 35, 500, 4000 )
    MhhvMhPass.Sumw2()
    MhhvMhFail.Sumw2()

    nev = TH1F("nev",   "nev",      1, 0, 1 )

    if runOthers == True:
        if options.set != 'data':
            MhhvMhPassPDFup   = TH2F("MhhvMhPassPDFup", "mass of HH vs mass of AK8 jet H PDF up - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassPDFdown = TH2F("MhhvMhPassPDFdown",   "mass of HH vs mass of AK8 jet H PDF down - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassPDFup.Sumw2()
            MhhvMhPassPDFdown.Sumw2()

            MhhvMhPassPUup   = TH2F("MhhvMhPassPUup", "mass of HH vs mass of AK8 jet H PU up - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassPUdown = TH2F("MhhvMhPassPUdown",   "mass of HH vs mass of AK8 jet H PU down - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassPUup.Sumw2()
            MhhvMhPassPUdown.Sumw2()

            MhhvMhPassBtagup   = TH2F("MhhvMhPassBtagup", "mass of HH vs mass of AK8 jet H Btag up - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassBtagdown = TH2F("MhhvMhPassBtagdown",   "mass of HH vs mass of AK8 jet H Btag down - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassBtagup.Sumw2()
            MhhvMhPassBtagdown.Sumw2()

            MhhvMhPassTrigup   = TH2F("MhhvMhPassTrigup", "mass of HH vs mass of AK8 jet H trig up - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassTrigdown = TH2F("MhhvMhPassTrigdown",   "mass of HH vs mass of AK8 jet H trig down - Pass", 60, 50, 350, 35, 500, 4000 )
            MhhvMhPassTrigup.Sumw2()
            MhhvMhPassTrigdown.Sumw2()

            # Fail
            MhhvMhFailPDFup   = TH2F("MhhvMhFailPDFup", "mass of HH vs mass of AK8 jet H PDF up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailPDFdown = TH2F("MhhvMhFailPDFdown",   "mass of HH vs mass of AK8 jet H PDF up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailPDFup.Sumw2()
            MhhvMhFailPDFdown.Sumw2()

            MhhvMhFailPUup   = TH2F("MhhvMhFailPUup", "mass of HH vs mass of AK8 jet H PU up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailPUdown = TH2F("MhhvMhFailPUdown",   "mass of HH vs mass of AK8 jet H PU up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailPUup.Sumw2()
            MhhvMhFailPUdown.Sumw2()

            MhhvMhFailBtagup   = TH2F("MhhvMhFailBtagup", "mass of HH vs mass of AK8 jet H Btag up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailBtagdown = TH2F("MhhvMhFailBtagdown",   "mass of HH vs mass of AK8 jet H Btag up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailBtagup.Sumw2()
            MhhvMhFailBtagdown.Sumw2()

            MhhvMhFailTrigup   = TH2F("MhhvMhFailTrigup", "mass of HH vs mass of AK8 jet H trig up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailTrigdown = TH2F("MhhvMhFailTrigdown",   "mass of HH vs mass of AK8 jet H trig up - Fail", 60, 50, 350, 35, 500, 4000 )
            MhhvMhFailTrigup.Sumw2()
            MhhvMhFailTrigdown.Sumw2()



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
        if count > 1:
            current_event_time = time.time()
            event_time_sum += (current_event_time - last_event_time)
            sys.stdout.write("%i / %i ... \r" % (count,(highBinEdge-lowBinEdge)))
            sys.stdout.write("Avg time = %f " % (event_time_sum/count) )
            sys.stdout.flush()
            last_event_time = current_event_time
        if count % 10000 == 0 :
            print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

        # Grab the event
        event = Event(inTree, entry)

        # Apply triggers first
        if options.set == 'data':
            passt = False
            for t in triggers:
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

        # check if we have enough jets
        if len(ak8JetsColl) < 1:
            continue
        if len(ak4JetsColl) < 2:
            continue

        # Separate into hemispheres the leading and subleading jets
        candidateAK4s = Hemispherize(ak8JetsColl,ak4JetsColl)

        # If Hemispherize failed
        if not candidateAK4s:
            continue

        leadingFatJet = ak8JetsColl[0]
        leadingJet = ak4JetsColl[candidateAK4s]
        subleadingJet = ak4JetsColl[candidateAK4s]

        eta_cut = (Cuts['eta'][0]<abs(leadingJet.eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(subleadingJet.eta)<Cuts['eta'][1])

        if eta_cut:
            # Make the lorentz vectors
            hjet = TLorentzVector()
            hjet.SetPtEtaPhiM(leadingFatJet.pt,leadingFatJet.eta,leadingFatJet.phi,leadingFatJet.msoftdrop)

            bjet1 = TLorentzVector()
            bjet2 = TLorentzVector()
            bjet1.SetPtEtaPhiM(leadingJet.pt,leadingJet.eta,leadingJet.phi,leadingJet.msoftdrop)
            bjet2.SetPtEtaPhiM(subleadingJet.pt,subleadingJet.eta,subleadingJet.phi,subleadingJet.msoftdrop)

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

            preselection = hpt_cut and bpt_cut and bbmass_cut and deepbtag_cut and mreduced_cut and deltaEta_cut

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

                
                if options.set!="data":
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

                    MhhvMhPass.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal')) 

                    if runOthers:
                        if options.set != 'data':
                            MhhvMhPassPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                            MhhvMhPassPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                            MhhvMhPassPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                            MhhvMhPassPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                            MhhvMhPassTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                            MhhvMhPassTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                            MhhvMhPassBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                            MhhvMhPassBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))



                else:
                    MhhvMhFail.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'nominal')) 

                    if runOthers and options.set != 'data':
                        MhhvMhFailPDFup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_up'))
                        MhhvMhFailPDFdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'PDF_down'))

                        MhhvMhFailPUup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_up'))
                        MhhvMhFailPUdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Pileup_down'))

                        MhhvMhFailTrigup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_up'))
                        MhhvMhFailTrigdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'Trigger_down'))

                        MhhvMhFailBtagup.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_up'))
                        MhhvMhFailBtagdown.Fill(hjet.M(),Mhh,norm_weight*Weightify(weights,'btagSF_down'))
                         

                            
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'
    f.cd()
    f.Write()
    f.Close()



    
