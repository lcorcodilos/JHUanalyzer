import ROOT
from ROOT import *

gStyle.SetOptStat(0)

distsDict = {
    'BG1000Nar':TFile.Open('rootfiles/HHpreselection18_GravNar-1000_default.root'),
    'BG1500Nar':TFile.Open('rootfiles/HHpreselection18_GravNar-1500_default.root'),
    'BG2000Nar':TFile.Open('rootfiles/HHpreselection18_GravNar-2000_default.root'),
    'BG2500Nar':TFile.Open('rootfiles/HHpreselection18_GravNar-2500_default.root'),
    'BG3000Nar':TFile.Open('rootfiles/HHpreselection18_GravNar-3000_default.root')
}

c = TCanvas('c','c',800,700)
leg = TLegend(0.7,0.7,0.9,0.9)

color_index = 0
same = False
for k in sorted(distsDict.keys()):
    print k
    dist = distsDict[k].Get('cutflow')
    dist.SetLineColor(kRed+color_index)
    dist.SetTitle('Cutflow - 2+1 HH#rightarrowbbbb')
    dist.SetMinimum(1)
    dist.GetYaxis().SetTitle('Events')
    dist.SetLineWidth(2)
    leg.AddEntry(dist,k,'l')
    if not same:
        print 'Plot first'
        dist.Draw('hist')
    else:
        dist.Draw('hist same')
    color_index+=1
    same = True

leg.Draw()
c.SetLogy()
c.RedrawAxis()
raw_input('waiting')