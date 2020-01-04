import ROOT
import pprint, time, json, copy
pp = pprint.PrettyPrinter(indent=4)
from collections import OrderedDict

class analyzer(object):
    """Main class for JHUanalyzer package. Works on the basis of nodes, edges, and forks
    where nodes are an RDF instance after an action (or series of actions) is performed, 
    the edges are actions, and forks split the processing of one node into two via a discriminator."""
    def __init__(self,fileName,eventsTreeName="Events",runTreeName="Runs"):
        super(analyzer, self).__init__()
        self.fileName = fileName # Can be single root file txt file with list of ROOT file locations (including xrootd locations)
        self.eventsTreeName = eventsTreeName
        # self.cuts = OrderedDict()
        # self.Cfuncs = {}

        # Setup TChains for multiple or single file
        self.EventsChain = ROOT.TChain(self.eventsTreeName) # Has events to turn into starting RDF
        RunChain = ROOT.TChain(runTreeName) # Has generated event count information - will be deleted after initialization
        if ".root" in self.fileName: 
            self.EventsChain.Add(self.fileName)
            RunChain.Add(self.fileName)
        elif ".txt" in self.fileName: 
            txt_file = open(self.fileName,"r")
            for l in txt_file.readlines():
                self.EventsChain.Add(l.strip())
                RunChain.Add(l.strip())
        else: 
            raise Exception("File name extension not supported. Please provide a single .root file or a .txt file with a line-separated list of .root files to chain together.")

        # Make base RDataFrame
        self.BaseDataFrame = ROOT.RDataFrame(self.EventsChain)
        self.BaseNode = Node('base',self.BaseDataFrame)
        self.DataFrames = {} # All dataframes

        # Check if dealing with data
        if hasattr(RunChain,'genEventCount'): self.isData = False
        else: self.isData = True
 
        # Count number of generated events if not data
        self.genEventCount = 0
        if not self.isData: 
            for i in range(self.RunChain.GetEntries()): 
                self.RunChain.GetEntry(i)
                self.genEventCount+= self.RunChain.genEventCount
        
        # Cleanup
        del RunChain

    ###################
    # Node operations #
    ###################
    def Cut(self,cuts,name='',node=self.BaseNode):
        newnode = node.Clone()

        if isinstance(cuts,CutGroup):
            for c in cuts.keys():
                newnode = newnode.Cut(c,cut)
        elif isinstance(cuts,str):
            newnode = newnode.Cut(name,cut)
        else:
            raise TypeError("ERROR: Second argument to Cut method must be a string of a single cut or of type CutGroup (which provides an OrderedDict)")

        self.DataFrames[name] = newnode
        return newnode 

    def Define(self,var,name='',node=self.BaseNode):
        newnode = node.Clone()

        if isinstance(var,VarGroup):
            for v in var.keys():
                newnode = newnode.Define(v,var)
        elif isinstance(var,str):
            newnode = newnode.Define(name,var)
        else:
            raise TypeError("ERROR: Second argument to Define method must be a string of a single var or of type VarGroup (which provides an OrderedDict)")

        self.DataFrames[name] = newnode
        return newnode  

    # Applies a bunch of action groups (cut or var) in one-shot in the order they are given
    def Apply(self,actiongrouplist,node=self.BaseNode):
        for ag in actiongrouplist:
            if ag.type == 'cut':
                self.Cut(ag,name=ag.name,node=node)
            elif ag.type == 'var':
                self.Define(ag,name=ag.name,node=node)
            else:
                raise TypeError("ERROR: Group %s does not have a defined type. Please initialize with either CutGroup or VarGroup." %ag.name)

    def Discriminate(self,discriminator,name='',node=self.BaseNode):
        newnodes = node.Discriminate(name,cut)
        self.DataFrames[name] = newnodes
        return newnodes


    #############
    # No return #
    #############
    def SetCFunc(self,blockcode):
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

        puWeights = puHist_data.Clone()
        puWeights.Divide(puHist_mc)
        puWeights.Sumw2()

        ROOT.gInterpreter.ProcessLine("auto puWeights = pileup;")

        self.SetCFunc('''using namespace ROOT::VecOps;
                float getWeight(float nvtx)
                {
                    weight *= puWeights->GetBinContent(puWeights->FindBin(nvtx));
                    return weight;
                } ''')

        self.SetVar("puw","getWeight("+nvtx+")")

##############
# Node Class #
##############
class Node(object):
    """Class to represent nodes in the DataFrame processing graph. Can make new nodes via Define, Cut, and Discriminate and setup relations between nodes (done automatically via Define, Cut, Discriminate)"""
    def __init__(self, name, DataFrame, parent=None, children=[],action=''):
        super(Node, self).__init__()
        self.DataFrame = DataFrame
        self.name = name
        self.action = action
        self.parent = parent # None or specified
        self.children = children # list of length 0, 1, or 2
        
    def Clone(self):
        return Node(self.name,self.DataFrame,parent=self.parent,children=self.children,action=self.action)

    # Set parent of type Node
    def SetParent(self,parent): 
        if isinstance(parent,Node): self.parent = parent
        else: raise TypeError('ERROR: Parent is not an instance of Node class for node %s'%self.name)

    # Set one child of type Node
    def SetChild(self,child,overwrite=False,silence=False):
        if overwrite: self.children = []
        # if len(children > 1): raise ValueError("ERROR: More than two children are trying to be added node %s. You may use the overwrite option to erase current children or find your bug."%self.name)
        # if len(children == 1) and silence == False: raw_input('WARNING: One child is already specified for node %s and you are attempting to add another (max 2). Press enter to confirm and continue.'%self.name)

        if isinstance(child,Node): self.children.append(child)
        else: raise TypeError('ERROR: Child is not an instance of Node class for node %s' %self.name)

    # Set children of type Node
    def SetChildren(self,children,overwrite=False):
        if overwrite: self.children = []
        # if len(children > 0): raise ValueError("ERROR: More than two children are trying to be added node %s. You may use the overwrite option to erase current children or find your bug."%self.name)
        
        if isinstance(children,dict) and 'pass' in children.keys() and 'fail' in children.keys() and len(children.keys()) == 2:
            self.SetChild(children['pass'])
            self.SetChild(children['fail'])
        else:
            raise TypeError('ERROR: Attempting to add a dictionary of children of incorrect format. Argument must be a dict of format {"pass":class.Node,"fail":class.Node}')

    # Define a new column to calculate
    def Define(self,name,var):
        newNode = Node(name,self.DataFrame.Define(name,var),parent=self,action=var)
        self.SetChild(newNode)
        return newNode

    # Define a new cut to make
    def Cut(self,name,cut):
        print 'Filtering %s: %s' %(name,cut)
        newNode = Node(name,self.DataFrame.Filter(cut,name),parent=self,action=cut)
        self.SetChild(newNode)
        return newNode

    # Discriminate based on a discriminator
    def Discriminate(self,name,discriminator):
        pass_sel = self.DataFrame
        fail_sel = self.DataFrame
        passfail = {
            "pass":Node(name+"_pass",pass_sel.Filter(name+"_pass",discriminator),parent=self,action=discriminator),
            "fail":Node(name+"_fail",fail_sel.Filter(name+"_fail","!("+discriminator+")"),parent=self,action="!("+discriminator+")")
        }
        self.SetChildren(passfail)
        return passfail
            
    # IMPORTANT: When writing a variable size array through Snapshot, it is required that the column indicating its size is also written out and it appears before the array in the columns list.
    # columns should be an empty string if you'd like to keep everything
    def Snapshot(self,columns,outfilename,treename):
        if columns == '':
            self.DataFrame.Snapshot(treename,outfilename)
        else:
            self.DataFrame.Snapshot(treename,outfilename,set(columns))

##################
# CutGroup Class #
##################
class Group(object):
    """docstring for Group"""
    def __init__(self, name):
        super(Group, self).__init__()
        self.name = name
        self.items = OrderedDict()

    def Add(self,name,item):
        self.items[name] = cut
        
    def Drop(self,name):
        del self.items[name]

    def __add__(self,other):
        added = copy.deepcopy(self.items)
        added.update(other)
        return added

    # Subclass for cuts
    class CutGroup(object):
        """docstring for CutGroup"""
        def __init__(self, name):
            super(Group, self).__init__()
            self.type = 'cut'
        
    # Subclass for vars/columns
    class VarGroup(object):
        """docstring for VarGroup"""
        def __init__(self, name):
            super(Group, self).__init__()
            self.type = 'var'
