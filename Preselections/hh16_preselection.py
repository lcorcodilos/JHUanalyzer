import ROOT
ROOT.ROOT.EnableImplicitMT()

import time

from analyzer import analyzer
from Cscripts import CommonCscripts, CustomCscripts
commonc = CommonCscripts()
customc = CustomCscripts()

toptag = "(FatJet_btagDeepB[1] > 0.1522 && FatJet_tau3[0]/FatJet_tau2[0] < 0.65)"

a = analyzer("~/CMS/temp/ttbar_bstar17.root")

a.SetCFunc("deltaPhi",commonc.deltaPhi)
a.SetCFunc("TLvector",commonc.vector)
a.SetCFunc("invariantMass",commonc.invariantMass)

a.SetVar("lead_vect","analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])")
a.SetVar("sublead_vect","analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])")
a.SetVar("mtt","analyzer::invariantMass(lead_vect,sublead_vect)")
a.SetVar("mt","FatJet_msoftdrop[0]")

a.SetCut("pt0","FatJet_pt[0] > 400")
a.SetCut("pt1","FatJet_pt[1] > 400")
a.SetCut("eta0","abs(FatJet_eta[0]) < 2.4")
a.SetCut("eta1","abs(FatJet_eta[1]) < 2.4")
a.SetCut("d_phi","abs(analyzer::deltaPhi(FatJet_phi[0],FatJet_phi[1])) > TMath::Pi()/2")
# a.SetCut("tau32_0","FatJet_tau3[0]/FatJet_tau2[0] < 0.65")
a.SetCut("tau32_1","FatJet_tau3[1]/FatJet_tau2[1] < 0.65")
a.SetCut("sjbtag1","FatJet_btagDeepB[1] > 0.1522")
# a.SetCut("sjbtag0","FatJet_btagDeepB[0] > 0.1522")
# a.SetCut("mass0","105 < FatJet_msoftdrop[0] && FatJet_msoftdrop[0] < 220")
a.SetCut("mass1","105 < FatJet_msoftdrop[1] && FatJet_msoftdrop[1] < 220")

presel = a.Cut()
# report = presel.Report()
# report.Print()
pass_and_fail = a.Discriminate(presel,toptag)
           

pass_report = pass_and_fail["pass"].Report()
fail_report = pass_and_fail["fail"].Report()                 
pass_report.Print()
fail_report.Print()
# hpass = pass_and_fail["pass"].Histo2D(("pass","pass",60,50,350,30,1000,4000),"mt","mtt")
# hfail = pass_and_fail["fail"].Histo2D(("fail","fail",60,50,350,30,1000,4000),"mt","mtt")

# hpass.Draw("lego")
# raw_input('pass')
# hfail.Draw("lego")
# raw_input('fail')