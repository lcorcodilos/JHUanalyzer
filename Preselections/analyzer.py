import ROOT
# ROOT.ROOT.EnableImplicitMT()
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
        self.Chain = ROOT.TChain("Events")
        if ".root" in self.fileName: 
            self.Chain.Add(self.fileName)
        elif ".txt" in self.fileName: 
            txt_file = open(self.fileName,"r")
            for l in txt_file.readlines():
                self.Chain.Add(l.strip())
        else: 
            raise Exception("File name extension not supported. Please provide a single .root file or a .txt file with a line-separated list of .root files to chain together.")
       
        self.DataFrame = ROOT.RDataFrame(self.Chain)

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

    def SetCut(self,name,cut):
        self.cuts[name] = cut

    def GetCuts(self):
        return self.cuts

    def SetCFunc(self,funcname,blockcode):
        self.Cfuncs[funcname] = blockcode
        ROOT.gInterpreter.Declare(self.Cfuncs[funcname])

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

    def SetTriggers(self,trigList):
        trigOR = ""
        for i,t in enumerate(trigList):
            if i < len(trigList)-1: trigOR += "("+t+"==1) || "
            else: trigOR += "("+t+"==1)"
        
        self.cuts["triggers"] = trigOR
