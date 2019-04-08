import ROOT
from ROOT import *

import sys

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim

if len(sys.argv) > 1:
    openfile = sys.argv[1]
else:
    openfile = ''

def fillHist(hist,coll,var,index,cut,absval=False):
    if len(coll)>index:
        if not absval:
            if (getattr(coll[index],var) >= cut[0]) and (getattr(coll[index],var) <= cut[1]):
                hist.Fill(getattr(coll[index],var))
        else:
            if (abs(getattr(coll[index],var)) >= cut[0]) and (abs(getattr(coll[index],var)) <= cut[1]):
                hist.Fill(getattr(coll[index],var))
    
def ratio(hist1,hist2):
    i1 = hist1.Integral()
    i2 = hist2.Integral()

    return i1/i2

f16 = TFile.Open('data16C_sample.root')
f17 = TFile.Open('data17C_sample.root')
files = {'16':TFile.Open('data16C_sample.root'),
         '17':TFile.Open('data17C_sample.root')}

ratios = {}

if openfile == '':
    out = TFile('YearComparisonOut.root','RECREATE')

    for string_f in files.keys():
        f = files[string_f]

        print 'Working on '+string_f

        inTree = f.Get("Events")
        elist,jsonFiter = preSkim(inTree,None,'')
        inTree = InputTree(inTree,elist)
        treeEntries = inTree.entries

        Jet1ptpass = TH1F('Jet1ptpass'+string_f,'Jet1ptpass'+string_f,160,400,2000)
        Jet2ptpass = TH1F('Jet2ptpass'+string_f,'Jet2ptpass'+string_f,160,400,2000)
        Jet1etapass = TH1F('Jet1etapass'+string_f,'Jet1etapass'+string_f,40,-4.0,4.0)
        Jet2etapass = TH1F('Jet2etapass'+string_f,'Jet2etapass'+string_f,40,-4.0,4.0)
        eptpass = TH1F('eptpass'+string_f,'eptpass'+string_f,100,0,200)
        muptpass = TH1F('muptpass'+string_f,'muptpass'+string_f,100,0,200)

        Jet1ptfail = TH1F('Jet1ptfail'+string_f,'Jet1ptfail'+string_f,200,0,2000)
        Jet2ptfail = TH1F('Jet2ptfail'+string_f,'Jet2ptfail'+string_f,200,0,2000)
        Jet1etafail = TH1F('Jet1etafail'+string_f,'Jet1etafail'+string_f,40,-4.0,4.0)
        Jet2etafail = TH1F('Jet2etafail'+string_f,'Jet2etafail'+string_f,40,-4.0,4.0)
        eptfail = TH1F('eptfail'+string_f,'eptfail'+string_f,100,0,200)
        muptfail = TH1F('muptfail'+string_f,'muptfail'+string_f,100,0,200)

        count = 0
        cut_1 = 0
        cut_2 = 0
        cut_3 = 0
        cut_4 = 0
        cut_5 = 0
        cut_6 = 0
        for entry in range(0,treeEntries):
            count = count + 1
            sys.stdout.write("%i / %i ... %.2f \r" % (count,treeEntries,100*float(count)/float(treeEntries)))
            sys.stdout.flush()

            event = Event(inTree, entry)

            fatJetsColl = Collection(event, "FatJet")
            eColl = Collection(event, "Electron")
            muColl = Collection(event, "Muon")
            subJetsColl = Collection(event, 'SubJet')

            fillHist(Jet1ptpass,fatJetsColl,'pt',0,[400,2000])
            fillHist(Jet2ptpass,fatJetsColl,'pt',1,[400,2000])
            fillHist(Jet1etapass,fatJetsColl,'eta',0,[0.0,2.4],absval=True)
            fillHist(Jet2etapass,fatJetsColl,'eta',1,[0.0,2.4],absval=True)

            fillHist(eptpass,eColl,'pt',0,[0,53])
            fillHist(muptpass,muColl,'pt',0,[0,53])

            fillHist(Jet1ptfail,fatJetsColl,'pt',0,[0,400])
            fillHist(Jet2ptfail,fatJetsColl,'pt',1,[0,400])
            fillHist(Jet1etafail,fatJetsColl,'eta',0,[2.4,4.0],absval=True)
            fillHist(Jet2etafail,fatJetsColl,'eta',1,[2.4,4.0],absval=True)
            fillHist(eptfail,eColl,'pt',0,[53,200])
            fillHist(muptfail,muColl,'pt',0,[53,200])


            if len(eColl) < 1 or eColl[0].pt < 53:
                cut_1 += 1
                if len(muColl) < 1 or muColl[0].pt < 53:
                    cut_2 += 1
                    if len(fatJetsColl) > 0 and fatJetsColl[0].pt > 400:
                        cut_3 += 1
                        if len(fatJetsColl) > 1 and fatJetsColl[1].pt > 400:
                            cut_4 += 1
                            if abs(fatJetsColl[0].eta) < 2.4:
                                cut_5 += 1
                                if abs(fatJetsColl[1].eta) < 2.4:
                                    cut_6 += 1
                
        print 'Electron cut:        '+str(cut_1)
        print 'Muon cut:            '+str(cut_2)
        print 'Lead jet pt cut:     '+str(cut_3)
        print 'Sublead jet pt cut:  '+str(cut_4)
        print 'Lead jet eta cut:    '+str(cut_5)
        print 'Sublead jet eta cut: '+str(cut_6)


        out.cd()
        out.Write()

        ratios['Jet1pt'+string_f] = ratio(Jet1ptpass,Jet1ptfail)
        ratios['Jet2pt'+string_f] = ratio(Jet2ptpass,Jet2ptfail)
        ratios['Jet1eta'+string_f] = ratio(Jet1etapass, Jet1etafail)
        ratios['Jet2eta'+string_f] = ratio(Jet2etapass, Jet2etafail)
        ratios['ept'+string_f] = ratio(eptpass,eptfail)
        ratios['mu1pt'+string_f] = ratio(muptpass,muptfail)

else:
    out = TFile.Open('YearComparisonOut.root')

    for string_f in files.keys():
        Jet1ptpass = out.Get('Jet1ptpass'+string_f)
        Jet2ptpass = out.Get('Jet2ptpass'+string_f)
        Jet1etapass = out.Get('Jet1etapass'+string_f)
        Jet2etapass = out.Get('Jet2etapass'+string_f)
        eptpass = out.Get('eptpass'+string_f)
        muptpass = out.Get('muptpass'+string_f)

        Jet1ptfail = out.Get('Jet1ptfail'+string_f)
        Jet2ptfail = out.Get('Jet2ptfail'+string_f)
        Jet1etafail = out.Get('Jet1etafail'+string_f)
        Jet2etafail = out.Get('Jet2etafail'+string_f)
        eptfail = out.Get('eptfail'+string_f)
        muptfail = out.Get('muptfail'+string_f)

        ratios['Jet1pt'+string_f] = ratio(Jet1ptpass,Jet1ptfail)
        ratios['Jet2pt'+string_f] = ratio(Jet2ptpass,Jet2ptfail)
        ratios['Jet1eta'+string_f] = ratio(Jet1etapass, Jet1etafail)
        ratios['Jet2eta'+string_f] = ratio(Jet2etapass, Jet2etafail)
        ratios['ept'+string_f] = ratio(eptpass,eptfail)
        ratios['mu1pt'+string_f] = ratio(muptpass,muptfail)

sorted_ratio_keys = sorted(ratios.keys())
print sorted_ratio_keys
for i in range(0,len(sorted_ratio_keys),2):
    key16 = sorted_ratio_keys[i]
    key17 = sorted_ratio_keys[i+1]
    ratio16 = ratios[key16]
    ratio17 = ratios[key17]

    rofr = ratio16/ratio17

    print key16 + '\t' + str(ratio16)+' / '+str(ratio17) +' = '+str(rofr)

out.Close()

