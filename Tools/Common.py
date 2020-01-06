import json, ROOT
from ROOT import RDataFrame

# Returns OR string of triggers that can be given to a cut group
def GetValidTriggers(self,trigList,DataFrame):
    trigOR = ""
    colnames = DataFrame.GetColumnNames()
    for i,t in enumerate(trigList):
        if t in colnames: 
            if trigOR == '': trigOR = "(("+t+"==1)" 
            else: trigOR += " || ("+t+"==1)"
        else:
            print "Trigger %s does not exist in TTree. Skipping." %(t)   

    if trigOR != "": 
        trigOR += ")" 
        
    return trigOR

def openJSON(f):
    return json.load(open(f,'r'), object_hook=ascii_encode_dict) 

def ascii_encode_dict(data):    
    ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x 
    return dict(map(ascii_encode, pair) for pair in data.items())

# Draws a cutflow histogram using the report feature of RDF. `cutlist` is the corresponding CutGroup to name the bins (so it must match what was given to the RDF!)
def CutflowHist(name,node,cutgroup):
    cutlist = cutgroup.keys()
    ncuts = len(cutlist)
    h = ROOT.TH1F(name,name,ncuts,0,ncuts)
    rdf_report = node.DataFrame.Report()
    for i,c in enumerate(cutlist): 
        h.GetXaxis().SetBinLabel(i+1,c)
        sel = rdf_report.At(c)
        h.SetBinContent(i+1,sel.GetPass())

    return h
