import ROOT
# ROOT.ROOT.EnableImplicitMT()
import pprint, time, json, os
pp = pprint.PrettyPrinter(indent=4)
from collections import OrderedDict

class analyzer(object):
    """docstring for analyzer"""
    def __init__(self,fileName):
        super(analyzer, self).__init__()
        self.fileName = fileName
        self.cuts = OrderedDict()
        # self.Cfuncs = {}

        self.Chain = ROOT.TChain("Events")
        self.RunChain = ROOT.TChain("Runs")

        if ".root" in self.fileName: 
            self.Chain.Add(self.fileName)
            self.RunChain.Add(self.fileName)
        elif ".txt" in self.fileName: 
            txt_file = open(self.fileName,"r")
            for l in txt_file.readlines():
                self.Chain.Add(l.strip())
                self.RunChain.Add(l.strip())
        else: 
            raise Exception("File name extension not supported. Please provide a single .root file or a .txt file with a line-separated list of .root files to chain together.")

        self.DataFrame = ROOT.RDataFrame(self.Chain)

        if hasattr(self.RunChain,'genEventCount'): self.isData = False
    	else: self.isData = True
 
        self.genEventCount = 0
        if not self.isData: 
            for i in range(self.RunChain.GetEntries()): 
                self.RunChain.GetEntry(i)
                self.genEventCount+= self.RunChain.genEventCount
        
        del self.RunChain

    def Cut(self, selection=None,node=None):
        # If a starting point (node) isn't already input, use the base data frame
        # Else, use the input starting point
        if node == None: this_entries = self.DataFrame
        else: this_entries = node

        # If no other selection given, use self.cuts
        if selection == None: this_selection = self.cuts
        else: this_selection = selection

        # Loop over the selection (ordered keys) and apply filter from selection
        for cutname in this_selection.keys():
            cutdef = this_selection[cutname]
            print 'Filtering %s: %s' %(cutname,cutdef)
            this_entries = this_entries.Filter(cutdef,cutname)

        final_selection = this_entries
        
        return final_selection

    def SetTriggers(self,trigList):
        trigOR = ""
        colnames = self.DataFrame.GetColumnNames()
        for i,t in enumerate(trigList):
            if t in colnames: 
                if not trigOR: trigOR = "(("+t+"==1)" # empty string == False
                else: trigOR += " || ("+t+"==1)"
            else:
                print "Trigger %s does not exist in TTree. Skipping." %(t)   

        if trigOR != "": 
            trigOR += ")" 
            self.cuts["triggers"] = trigOR
            self.SetVar('triggers',trigOR)

    def DefineCut(self,name,cut):
        self.cuts[name] = cut
        self.SetVar(name,cut)

    def GetCuts(self):
        return self.cuts

    def SetVar(self,varname,vardef,node=None):
        if node == None: self.DataFrame = self.DataFrame.Define(varname,vardef)
        else: return node.Define(varname,vardef)

    def Discriminate(self,preselection,discriminator):
        pass_sel = preselection
        fail_sel = preselection
        passfail = {
            "pass":pass_sel.Filter("pass",discriminator),
            "fail":fail_sel.Filter("fail","!("+discriminator+")")
        }
        return passfail

    def SetCFunc(self,blockcode):#funcname,
        # self.Cfuncs[funcname] = blockcode
        # ROOT.gInterpreter.Declare(self.Cfuncs[funcname])
        ROOT.gInterpreter.Declare(blockcode)

    def makePUWeight(self,year,nvtx):
        if year == '16':
            pufile_mc_name="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/pileup_profile_Summer16.root" % os.environ['CMSSW_BASE']
            pufile_data_name="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupData_GoldenJSON_Full2016.root" % os.environ['CMSSW_BASE']
        elif year == '17':
            pufile_data_name="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupHistogram-goldenJSON-13tev-2018-99bins_withVar.root" % os.environ['CMSSW_BASE']
            pufile_mc_name="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileup2017.root" % os.environ['CMSSW_BASE']
        elif year == '18':
            pufile_data_name="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupHistogram-goldenJSON-13tev-2018-100bins_withVar.root" % os.environ['CMSSW_BASE']
            pufile_mc_name="%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/mcPileup2018.root" % os.environ['CMSSW_BASE']

        puFile_data = ROOT.TFile(pufile_data_name,"READ")
        puHist_data = puFile_data.Get('pileup')
        puFile_mc = ROOT.TFile(pufile_mc_name,"READ")
        puHist_mc = puFile_mc.Get('pu_mc')

        puWeights = puHist_data.Clone('clone')
        puWeights.Divide(puHist_mc)
        puWeights.Sumw2()

        ROOT.gInterpreter.ProcessLine("auto puWeight = clone;")

        self.SetCFunc('''using namespace ROOT::VecOps;
                float getWeight(float nvtx)
                {
                    float weight = 1;
                    weight *= puWeight->GetBinContent(puWeight->FindBin(nvtx));
                    return weight;
                } ''')

        self.SetVar("puw","getWeight("+nvtx+")")


def CutflowHist(name,rdf,cutlist):
    ncuts = len(cutlist)
    h = ROOT.TH1F(name,name,ncuts,0,ncuts)
    rdf_report = rdf.Report()
    for i,c in enumerate(cutlist): 
        h.GetXaxis().SetBinLabel(i+1,c)
        sel = rdf_report.At(c)
        h.SetBinContent(i+1,sel.GetPass())

    return h

def openJSON(f):
    return json.load(open(f,'r'), object_hook=ascii_encode_dict) 

def ascii_encode_dict(data):    
    ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x 
    return dict(map(ascii_encode, pair) for pair in data.items())

class CutGroup():
    """docstring for CutGrou"""
    def __init__(self, name, cutlist):
        self.name = name
        self.cutlist = cutlist

        if type(self.cutlist) == list and len(self.cutlist) > 0: self.cut = '('
        else: raise Exception('A list of cuts must be provided')
        
        for i,c in enumerate(self.cutlist):
            if i < len(self.cutlist)-1: self.cut += c+'==1)&&'
            else: self.cut += c+'==1))'

    def GetName(self): return self.name

    def GetCut(self): return self.cut
