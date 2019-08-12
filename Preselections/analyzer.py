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

    def SetTriggers(self,trigList):
        trigOR = ""
        for i,t in enumerate(trigList):
            if i < len(trigList)-1: trigOR += "("+t+"==1) || "
            else: trigOR += "("+t+"==1)"
        
        self.cuts["triggers"] = trigOR
