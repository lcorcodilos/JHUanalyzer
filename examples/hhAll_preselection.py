import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser

from JHUanalyzer.Preselections.analyzer import analyzer,openJSON
from JHUanalyzer.Preselections.Cscripts import CommonCscripts, CustomCscripts
commonc = CommonCscripts()
customc = CustomCscripts()

parser = OptionParser()

parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-c', '--config', metavar='FILE', type='string', action='store',
                default   =   'config.json',
                dest      =   'config',
                help      =   'Configuration file in json format that is interpreted as a python dictionary')


(options, args) = parser.parse_args()

start_time = time.time()

a = analyzer(options.input)
if '_loc.txt' in options.input: setname = options.input.split('/')[-1].split('_loc.txt')[0]
else: setname = ''

if os.path.exists(options.config):
    print 'JSON config imported'
    c = openJSON(options.config)
    if setname != '' and not a.isData: 
        xsec = c['XSECS'][setname]
        lumi = c['lumi']
    else: 
        xsec = 1.
        lumi = 1.

# a.SetCFunc("deltaPhi",commonc.deltaPhi)
a.SetCFunc("TLvector",commonc.vector)
a.SetCFunc("invariantMass",commonc.invariantMass)


a.SetTriggers(["HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30","HLT_PFHT650_WideJetMJJ900DEtaJJ1p5","HLT_AK8PFHT650_TrimR0p1PT0p03Mass50","HLT_AK8PFHT700_TrimR0p1PT0p03Mass50","HLT_AK8DiPFJet280_200_TrimMass30_BTagCSV_p20"])
#a.SetTriggers(["HLT_PFHT1050","HLT_AK8PFJet360_TrimMass30"])
a.SetCut("nFatJets","nFatJet > 1")
a.SetCut("pt0","FatJet_pt[0] > 300")
a.SetCut("pt1","FatJet_pt[1] > 300")
a.SetCut("eta0","abs(FatJet_eta[0]) < 2.4")
a.SetCut("eta1","abs(FatJet_eta[1]) < 2.4")
a.SetCut("jetID","((FatJet_jetId[0] & 2) == 2) && ((FatJet_jetId[1] & 2) == 2)")
a.SetCut("PV","PV_npvsGood > 0")
a.SetCut("deltaEta","abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
a.SetVar("lead_vect","analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])")
a.SetVar("sublead_vect","analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])")
a.SetVar("mhh","analyzer::invariantMass(lead_vect,sublead_vect)")
a.SetVar("mreduced","mhh - (FatJet_msoftdrop[0]-125.0) - (FatJet_msoftdrop[1]-125.0)")
a.SetCut("mreduced","mreduced > 1000.")
a.SetCut("tau21","(FatJet_tau2[0]/FatJet_tau1[0] < 0.55) && (FatJet_tau2[1]/FatJet_tau1[1] < 0.55)")
a.SetCut("msoftdrop_1","105 < FatJet_msoftdrop[1] && FatJet_msoftdrop[1] < 135")


a.SetVar("mh","FatJet_msoftdrop[0]")
a.SetVar("SRTT","FatJet_btagHbb[0] > 0.8 && FatJet_btagHbb[1] > 0.8")
a.SetVar("SRLL","FatJet_btagHbb[0] > 0.3 && FatJet_btagHbb[1] > 0.3 && (!SRTT)")
a.SetVar("ATTT","(FatJet_btagHbb[0] > 0.8 && FatJet_btagHbb[1] < 0.3) || (FatJet_btagHbb[1] > 0.8 && FatJet_btagHbb[0] < 0.3)")
a.SetVar("ATLL","(FatJet_btagHbb[0] > 0.3 && FatJet_btagHbb[0] < 0.8 && FatJet_btagHbb[1] < 0.3) || (FatJet_btagHbb[1] > 0.3 && FatJet_btagHbb[1] < 0.8 && FatJet_btagHbb[0] < 0.3)")

a.SetVar("11presel")

if not a.isData: norm = (xsec*lumi)/a.genEventCount
else: norm = 1.

11_presel = a.Filter("11presel == 1")

#21_candidate = a.Filter("presel=1")

##a nunch of setvars and set cuts
#21_candidate.SetVar("21presel", )

#21_presel = 21_candidate.Filter("21presel == 1")

SRTT = a.Cut({"SRTT":"SRTT"},11_presel)
ATTT = a.Cut({"ATTT":"ATTT"},11_presel)
SRLL = a.Cut({"SRLL":"SRLL"},11_presel)
ATLL = a.Cut({"ATLL":"ATLL"},11_presel)

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()

hSRTT = SRTT.Histo2D(("SRTT","SRTT",9 ,40 ,220 ,20 ,700 ,2700),'mh','mhh')
hATTT = ATTT.Histo2D(("ATTT","ATTT",9 ,40 ,220 ,20 ,700 ,2700),"mh","mhh")
hSRLL = SRLL.Histo2D(("SRLL","SRLL",9 ,40 ,220 ,20 ,700 ,2700),"mh","mhh")
hATLL = ATLL.Histo2D(("ATLL","ATLL",9 ,40 ,220 ,20 ,700 ,2700),"mh","mhh")

for h in [hSRTT,hATTT,hSRLL,hATLL]: h.Scale(norm)

norm_hist = ROOT.TH1F('norm','norm',1,0,1)
norm_hist.SetBinContent(1,norm)
norm_hist.Write()

hSRTT.Write()
hATTT.Write()
hSRLL.Write()
hATLL.Write()

out_f.Close()

print "Total time: "+str((time.time()-start_time)/60.) + ' min'
