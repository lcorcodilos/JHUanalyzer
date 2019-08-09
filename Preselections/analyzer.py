import ROOT
ROOT.ROOT.EnableImplicitMT()
import pprint, time
pp = pprint.PrettyPrinter(indent=4)
from collections import OrderedDict

class analyzer(object):
    """docstring for analyzer"""
    def __init__(self,fileName):
        super(analyzer, self).__init__()
        self.fileName = fileName
        self.cuts = OrderedDict()
        self.Cfuncs = {}
        self.DataFrame = ROOT.RDataFrame("Events", self.fileName)
       
    def Cut(self, selection=None,node=None):
        # If a starting point (node) isn't already input, use the base data frame
        if node == None: this_entries = self.DataFrame
        # Else, use the input starting point
        else: this_entries = node

        # If no other selection given, use self.cuts
        if selection == None: this_selection = self.cuts
        else: this_selection = selection

        # Loop over the selection (ordered keys) and apply filter from selection
        for k in this_selection.keys():
            s = this_selection[k]
            this_entries = this_entries.Filter(s,k)
        final_selection = this_entries
        
        return final_selection

    # def SetCuts(self,orderedCuts): # orderedCuts must be of type OrderedDict
    #     self.cuts = orderedCuts
    def SetCut(self,name,cut):
        self.cuts[name] = cut

    def GetCuts(self):
        return self.cuts
    def SetCFunc(self,funcname,blockcode):
        self.Cfuncs[funcname] = blockcode
        ROOT.gInterpreter.Declare(self.Cfuncs[funcname])

    def SetVar(self,varname,vardef,node=None):
        if node == None: this_entries = self.DataFrame
        else: this_entries = node
        return this_entries.Define(varname,vardef)

    def Discriminate(self,preselection,discriminator):
        pass_sel = preselection
        fail_sel = preselection
        passfail = {
            "pass":pass_sel.Filter("pass",discriminator),
            "fail":fail_sel.Filter("fail","!("+discriminator+")")
        }
        return passfail


preselection_cuts = OrderedDict()
preselection_cuts["pt0"] = "FatJet_pt[0] > 400"
preselection_cuts["pt1"] = "FatJet_pt[1] > 400"
preselection_cuts["eta0"] = "abs(FatJet_eta[0]) < 2.4"
preselection_cuts["eta1"] = "abs(FatJet_eta[1]) < 2.4"
preselection_cuts["d_phi"] = "abs(analyzer::deltaPhi(FatJet_phi[0],FatJet_phi[1])) > TMath::Pi()/2"
# preselection_cuts["tau32_0"] = "FatJet_tau3[0]/FatJet_tau2[0] < 0.65"
preselection_cuts["tau32_1"] = "FatJet_tau3[1]/FatJet_tau2[1] < 0.65"
preselection_cuts["sjbtag1"] = "FatJet_btagDeepB[1] > 0.1522"
# preselection_cuts["sjbtag0"] = "FatJet_btagDeepB[0] > 0.1522"
# preselection_cuts["mass0"] = "105 < FatJet_msoftdrop[0] && FatJet_msoftdrop[0] < 220"
preselection_cuts["mass1"] = "105 < FatJet_msoftdrop[1] && FatJet_msoftdrop[1] < 220"

deltaPhi_code ='''
namespace analyzer {
  double deltaPhi(double phi1,double phi2) {
    double result = phi1 - phi2;
    while (result > TMath::Pi()) result -= 2*TMath::Pi();
    while (result <= -TMath::Pi()) result += 2*TMath::Pi();
    return result;
  }
}
'''
vector_code = '''
namespace analyzer {
    TLorentzVector* TLvector(float pt,float eta,float phi,float m) {
        TLorentzVector* v = new TLorentzVector();
        v->SetPtEtaPhiM(pt,eta,phi,m);
        return v;
    }
}
'''
invariantMass_code = '''
namespace analyzer {
    double invariantMass(TLorentzVector* v1, TLorentzVector* v2) {
        return (*v1+*v2).M();
    }
}
'''

toptag = "(FatJet_btagDeepB[1] > 0.1522 && FatJet_tau3[0]/FatJet_tau2[0] < 0.65)"

a = analyzer("~/CMS/temp/ttbar_bstar17.root")
a.SetCFunc("deltaPhi",deltaPhi_code)
a.SetCFunc("TLvector",vector_code)
a.SetCFunc("invariantMass",invariantMass_code)
a.SetVar("lead_vect","analyzer::TLvector(FatJet_pt[0],FatJet_eta[0],FatJet_phi[0],FatJet_msoftdrop[0])")
a.SetVar("sublead_vect","analyzer::TLvector(FatJet_pt[1],FatJet_eta[1],FatJet_phi[1],FatJet_msoftdrop[1])")
a.SetVar("mtt","analyzer::invariantMass(lead_vect,sublead_vect)")
a.SetVar("mt","FatJet_msoftdrop[0]")
a.SetCuts(preselection_cuts)
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