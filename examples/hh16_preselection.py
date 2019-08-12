import ROOT
ROOT.ROOT.EnableImplicitMT()

import time

from JHUanalyzer.Preselections.analyzer import analyzer
from JHUanalyzer.Preselections.Cscripts import CommonCscripts, CustomCscripts
commonc = CommonCscripts()
customc = CustomCscripts()

a = analyzer("chain_test.txt")

# a.SetCFunc("deltaPhi",commonc.deltaPhi)
a.SetCFunc("TLvector",commonc.vector)
a.SetCFunc("invariantMass",commonc.invariantMass)

a.SetVar("lead_vect","analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])")
a.SetVar("sublead_vect","analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])")
a.SetVar("mhh","analyzer::invariantMass(lead_vect,sublead_vect)")
a.SetVar("mh","FatJet_msoftdrop[0]")
a.SetVar("mreduced","mhh - (FatJet_msoftdrop[0]-125.0) - (FatJet_msoftdrop[1]-125.0)")
a.SetVar("SRTT","FatJet_btagHbb[0] > 0.8 && FatJet_btagHbb[1] > 0.8")
a.SetVar("SRLL","FatJet_btagHbb[0] > 0.3 && FatJet_btagHbb[1] > 0.3 && (!SRTT)")
a.SetVar("ATTT","(FatJet_btagHbb[0] > 0.8 && FatJet_btagHbb[1] < 0.3) || (FatJet_btagHbb[1] > 0.8 && FatJet_btagHbb[0] < 0.3)")
a.SetVar("ATLL","(FatJet_btagHbb[0] > 0.3 && FatJet_btagHbb[0] < 0.8 && FatJet_btagHbb[1] < 0.3) || (FatJet_btagHbb[1] > 0.3 && FatJet_btagHbb[1] < 0.8 && FatJet_btagHbb[0] < 0.3)")

# a.SetTriggers(["HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30"])
a.SetTriggers(["HLT_PFHT1050","HLT_AK8PFJet360_TrimMass30"])
a.SetCut("pt0","FatJet_pt[0] > 300")
a.SetCut("pt1","FatJet_pt[1] > 300")
a.SetCut("eta0","abs(FatJet_eta[0]) < 2.4")
a.SetCut("eta1","abs(FatJet_eta[1]) < 2.4")
a.SetCut("jetID","((FatJet_jetId[0] & 2) == 2) && ((FatJet_jetId[1] & 2) == 2)")
# a.SetCut("PV","PV_npvsGood > 0")
a.SetCut("deltaEta","abs(FatJet_eta[0] - FatJet_eta[1]) < 1.3")
a.SetCut("mreduced","mreduced > 1000.")
a.SetCut("tau21","(FatJet_tau2[0]/FatJet_tau1[0] < 0.55) && (FatJet_tau2[1]/FatJet_tau1[1] < 0.55)")
a.SetCut("msoftdrop_1","105 < FatJet_msoftdrop[1] && FatJet_msoftdrop[1] < 135")

presel = a.Cut()

SRTT = a.Cut({"SRTT":"SRTT"},presel)
ATTT = a.Cut({"ATTT":"ATTT"},presel)
SRLL = a.Cut({"SRLL":"SRLL"},presel)
ATLL = a.Cut({"ATLL":"ATLL"},presel)

# report = presel.Report()
# report.Print()

out_f = ROOT.TFile("hh16_ttbar_test.root","RECREATE")
out_f.cd()

start_time = time.time()

hSRTT = SRTT.Histo2D(("SRTT","SRTT",9 ,40 ,220 ,20 ,1000 ,3000),'mh','mhh')
hATTT = ATTT.Histo2D(("ATTT","ATTT",9 ,40 ,220 ,20 ,1000 ,3000),"mh","mhh")
hSRLL = SRLL.Histo2D(("SRLL","SRLL",9 ,40 ,220 ,20 ,1000 ,3000),"mh","mhh")
hATLL = ATLL.Histo2D(("ATLL","ATLL",9 ,40 ,220 ,20 ,1000 ,3000),"mh","mhh")

hSRTT.Write()
hATTT.Write()
hSRLL.Write()
hATLL.Write()

out_f.Close()

print "Total time: "+str((time.time()-start_time)/60.) + ' min'