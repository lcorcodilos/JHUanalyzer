'''@docstring Analyzer.py

Home of main class for HAMMER.

'''

import ROOT
import pprint, time, json, copy, os,sys
from collections import OrderedDict
pp = pprint.PrettyPrinter(indent=4)
sys.path.append('../')
from Tools.Common import GetHistBinningTuple, CompileCpp
from Node import *
from Correction import *
from Group import *

class analyzer(object):
    """Main class for HAMMER. 

    Implements an interface with ROOT's RDataFrame (RDF). The default values assume the data is in
    NanoAOD format. However, any TTree can be used. The class works on the basis of nodes and actions
    where nodes are an RDF instance and an action (or series of actions) can transform the RDF to create a new node(s).

    When using class functions to perform actions, an active node will always be tracked so that the next action uses 
    the active node and assigns the output node as the new active node"""
    def __init__(self,fileName,eventsTreeName="Events",runTreeName="Runs"):
        '''
        Constructor

        Args:
            fileName (str): A ROOT file path or the path to a txt file which contains several ROOT file paths separated by 
                new line characters.

            eventsTreeName (str): Name of TTree in fileName where events are stored. Defaults to "Events" (for NanoAOD)
            
            runTreeName (str): NAme of TTree in fileName where run information is stored (for generated event info in 
                simulation). Defaults to "Runs" (for NanoAOD) 
        '''

        super(analyzer, self).__init__()
        self.fileName = fileName 
        self.eventsTreeName = eventsTreeName

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
        self.BaseDataFrame = ROOT.RDataFrame(self.EventsChain) #: ROOT.RDataFrame: Initial RDataFrame - no modifications
        self.BaseNode = Node('base',self.BaseDataFrame) #: Node: Initial Node - no modifications
        self.DataFrames = {} #: dict: All data frames
        self.Corrections = {} #: dict: All corrections added to track

        # Check if dealing with data
        if hasattr(RunChain,'genEventCount'): 
            self.isData = False #: bool: Is data (true) or simulation (false) based on existence of _genEventCount branch
            self.preV6 = True #: bool: Is pre-NanoAODv6 (true) or not (false) based on existence of _genEventCount branch
        elif hasattr(RunChain,'genEventCount_'): 
            self.isData = False
            self.preV6 = False
        else: self.isData = True
 
        # Count number of generated events if not data
        self.genEventCount = 0 #: int: Number of generated events in imported simulation files. Zero if data.
        if not self.isData: 
            for i in range(RunChain.GetEntries()): 
                RunChain.GetEntry(i)
                if self.preV6: self.genEventCount+= RunChain.genEventCount
                else: self.genEventCount+= RunChain.genEventCount_
        
        # Cleanup
        del RunChain
        self.ActiveNode = self.BaseNode #: Mode: Active node. Access via GetActiveNode(). Set via SetActiveNode().
 
    def SetActiveNode(self,node):
        '''Sets the active node (#ActiveNode)'''
        if not isinstance(node,Node): raise ValueError('ERROR: SetActiveNode() does not support argument of type %s. Please provide a Node.'%(type(node)))
        else: self.ActiveNode = node

    def GetActiveNode(self):
        '''Return the active node (#ActiveNode)'''
        return self.ActiveNode

    def GetBaseNode(self):
        '''Return the base node (#BaseNode)'''
        return self.BaseNode

    def TrackNode(self,node):
        '''Add a node to track. 

        Will add the node to #DataFrames dictionary with key node.name.

        Raise exception if node.name already exists as a key.'''
        if isinstance(node,Node):
            if node.Name in self.DataFrames.keys():
                raise ValueError('ERROR: Attempting to track a node with the same name as one that is already being tracked (%s). Please provide a unique node.'%(node.name))
            self.DataFrames[node.name] = node
        else:
            raise TypeError('ERROR: TrackNode() does not support arguments of type %s. Please provide a Node.'%(type(node)))

    def GetCorrectionNames(self):
        '''Return names of all corrections being tracked.

        Names are stored as keys in #Corrections dictionary.'''
        return self.Corrections.keys()

    #-----------------------------------------------------------#
    # Node operations - degenerate with Node class methods but  #
    # have benefit of keeping track of an Active Node (reset by #
    # each action and used by default).                         #
    #-----------------------------------------------------------#
    def Cut(self,name='',cuts='',node=self.ActiveNode):
        newNode = node.Clone()

        if isinstance(cuts,CutGroup):
            for c in cuts.keys():
                cut = cuts[c]
                newNode = newNode.Cut(c,cut)
        elif isinstance(cuts,str):
            newNode = newNode.Cut(name,cuts)
        else:
            raise TypeError("ERROR: Second argument to Cut method must be a string of a single cut or of type CutGroup (which provides an OrderedDict).")

        self.TrackNode(newNode)
        self.SetActiveNode(newNode)
        return newNode 

    def Define(self,name='',variables='',node=self.ActiveNode):
        newNode = node.Clone()

        if isinstance(variables,VarGroup):
            for v in variables.keys():
                var = variables[v]
                newNode = newNode.Define(v,var)
        elif isinstance(variables,str):
            newNode = newNode.Define(name,variables)
        else:
            raise TypeError("ERROR: Second argument to Define method must be a string of a single var or of type VarGroup (which provides an OrderedDict).")

        self.TrackNode(newNode)
        self.SetActiveNode(newNode)
        return newNode  

    # Applies a bunch of action groups (cut or var) in one-shot in the order they are given
    def Apply(self,actiongrouplist,node=self.ActiveNode):
        if type(actiongrouplist) != list: actiongrouplist = [actiongrouplist]
        for ag in actiongrouplist:
            if ag.type == 'cut':
                newNode = self.Cut(name=ag.name,cuts=ag,node=node)
            elif ag.type == 'var':
                newNode = self.Define(name=ag.name,variables=ag,node=node)
            else:
                raise TypeError("ERROR: Apply() group %s does not have a defined type. Please initialize with either CutGroup or VarGroup." %ag.name)

        self.TrackNode(newNode)
        self.SetActiveNode(newNode)
        return newNode

    def Discriminate(self,discriminator,name='',node=self.ActiveNode,passAsActiveNode=None):
        newNodes = node.Discriminate(name,cut)

        self.TrackNode(newNodes['pass'])
        self.TrackNode(newNodes['fail'])

        if passAsActiveNode == True: self.SetActiveNode(newNodes['pass'])
        elif passAsActiveNode == False: self.SetActiveNode(newNodes['fail'])

        return newNodes

    #######################
    # Corrections/Weights #
    #######################
    # Want to correct with analyzer class so we can track what corrections have been made for final weights and if we want to save them out in a group when snapshotting
    def AddCorrection(self,correction,node=self.ActiveNode):
        # Quick type checking
        if not isinstance(node,Node): raise TypeError('ERROR: AddCorrection() does not support argument of type %s for node. Please provide a Node.'%(type(node)))
        elif not isinstance(correction,Correction): raise TypeError('ERROR: AddCorrection() does not support argument type %s for correction. Please provide a Correction.'%(type(correction)))

        # Add correction to track
        self.Corrections[correction.name] = correction

        # Make new node
        newNode = node.Define(correction.name+'__vec',correction.GetCall())
        if correction.type == 'weight':
            returnNode = newNode.Define(correction.name+'__nom',correction.name+'__vec[0]').Define(correction.name+'__up',correction.name+'__vec[1]').Define(correction.name+'__down',correction.name+'__vec[2]')
        elif correction.type == 'uncert':
            returnNode = newNode.Define(correction.name+'__up',correction.name+'__vec[0]').Define(correction.name+'__down',correction.name+'__vec[1]')

        self.TrackNode(returnNode)
        self.SetActiveNode(returnNode)
        return returnNode

    def AddCorrections(self,node=self.ActiveNode,correctionList=[]):
        newNode = node
        for c in correctionList:
            newNode = self.AddCorrection(newNode,c)

        self.TrackNode(newNode)
        self.SetActiveNode(newNode)
        return newNode

    def MakeWeightCols(self,node=self.ActiveNode,CorrectionNames=None,dropList=[]):
        correctionsToApply = _checkCorrections(CorrectionNames,dropList)
        
        # Build nominal weight first (only "weight", no "uncert")
        weights = {'nominal':''}
        for corrname in correctionsToApply:
            corr = self.Corrections[corrname] # MIGHT BE ABLE TO REMOVE THIS LINE AND THE STORING OF Correction INSTANCES ENTIRELY (ie just store names)
            if corr.GetType() == 'weight':
                weights['nominal']+=corrname+'__nom * '
            weights['nominal'] = weights['nominal'][:-3]

        # Vary nominal weight for each correction ("weight" and "uncert")
        for corrname in correctionsToApply:
            corr = self.Corrections[corrname]
            if corr.GetType() == 'weight':
                weights[corrname+'_up'] = weights['nominal'].replace(corrname+'__nom',corrname+'__up')
                weights[corrname+'_down'] = weights['nominal'].replace(corrname+'__nom',corrname+'__down')
            elif corr.GetType() == 'uncert':
                weights[corrname+'_up'] = weights['nominal']+' * '+corrname+'__up'
                weights[corrname+'_down'] = weights['nominal']+' * '+corrname+'__down'
            else:
                raise TypeError('ERROR: Correction "%s" not identified as either "weight" or "uncert"'%(corrname))

        # Make a node with all weights calculated
        returnNode = node
        for weight in weights.keys():
            returnNode = returnNode.Define('weight__'+weight,weights[weight])
        
        self.TrackNode(returnNode)
        self.SetActiveNode(returnNode)
        return returnNode 

    def MakeTemplateHistos(self,templateHist,variables,node=self.ActiveNode,CorrectionNames=None,dropList=[]):
        out = HistGroup('Templates')

        weight_cols = [cname for cname in node.GetColumnNames() if 'weight__' in cname]
        baseName = templateHist.GetName()
        baseTitle = templateHist.GetTitle()
        binningTuple,dimension = GetHistBinningTuple(templateHist)

        for c in weight_cols:
            histname = '%s__%s'%(baseName,cname.replace('weight__',''))
            histtitle = '%s__%s'%(baseTitle,cname.replace('weight__',''))

            # Build the tuple to give as argument for template
            template_attr = (histname,histtitle) + binningTuple

            if dimension == 1: thishist = node.DataFrame.Histo1D(template_attr,variables[0],cname)
            elif dimension == 2: thishist = node.DataFrame.Histo2D(template_attr,variables[0],variables[1],cname)
            elif dimension == 3: thishist = node.DataFrame.Histo3D(template_attr,variables[0],variables[1],variables[2],cname)
           
            out.Add(histname,thishist)

        return out

    ##################################################################
    # Draw templates together to see up/down effects against nominal #
    ##################################################################
    def DrawTemplates(hGroup,saveLocation,projection='X',projectionArgs=(),fileType='pdf'):
        canvas = TCanvas('c','',800,700)

        # Initial setup
        baseName = list(hGroup.keys())[0].split('__')[0]

        if isinstance(hGroup[baseName+'__nominal'],ROOT.TH2) or isinstance(hGroup[baseName+'__nominal'],ROOT.TH3): 
            projectedGroup = hGroup.Do("Projection"+projection,projectionArgs)
        else:
            projectedGroup = hGroup

        nominal = projectedGroup[baseName+'__nominal']
        nominal.SetLineColor(kBlack)
        nominal.SetFillColor(kYellow-2)
        corrections = []
        for name in projectedGroup.keys():
            corr = name.split('__')[1].split('_')[0]
            if corr not in corrections:
                corrections.append(corr)

        # Loop over corrections
        for corr in corrections:
            nominal.Draw('hist')

            up = projectedGroup[baseName+'__'+corr+'_up']
            down = projectedGroup[baseName+'__'+corr+'_down']

            up.SetLineColor(kRed)
            down.SetLineColor(kBlue)

            leg = TLegend(0.8,0.8,0.9,0.9)
            leg.AddEntry('Nominal',nominal,'lf')
            leg.AddEntry('Up',up,'l')
            leg.AddEntry('Down',down,'l')

            up.Draw('same hist')
            down.Draw('same hist')
            leg.Draw()

            canvas.Print('%s/%s_%s.%s'%(saveLocation,baseName,corr,fileType),fileType)

    #####################
    # Private functions #
    #####################
    def _checkCorrections(self,CorrectionNames,dropList):
        # Quick type checking
        if CorrectionNames == None: correctionsToApply = self.Corrections.keys()
        elif not isinstance(CorrectionNames,list):
            raise ValueError('ERROR: MakeWeights() does not support CorrectionNames argument of type %s. Please provide a list.'%(type(CorrectionNames)))
        else: correctionsToApply = CorrectionNames

        # Drop specified weights from consideration
        if not isinstance(dropList,list):
            raise ValueError('ERROR: MakeWeights() does not support dropList argument of type %s. Please provide a list.'%(type(dropList)))
        else: 
            newCorrsToApply = []
            for corr in correctionsToApply:
                if corr not in dropList: newCorrsToApply.append(corr)
            correctionsToApply = newCorrsToApply

        return correctionsToApply

