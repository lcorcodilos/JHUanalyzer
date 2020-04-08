'''@docstring Group.py

Home of Group classes for organizing cuts, new variables, and histograms

'''

from collections import OrderedDict
#################
# Group Classes #
#################
class Group(object):
    """docstring for Group"""
    def __init__(self, name):
        super(Group, self).__init__()
        self.name = name
        self.items = OrderedDict()
        self.type = None

    def Add(self,name,item):
        self.items[name] = item 
        
    def Drop(self,name):
        dropped = copy.deepcopy(self.items)
        del dropped[name]
        if self.type == None: newGroup = Group(self.name+'-'+name)
        elif self.type == 'var': newGroup = VarGroup(self.name+'-'+name)
        elif self.type == 'cut': newGroup = CutGroup(self.name+'-'+name)
        newGroup.items = dropped
        return newGroup

    def __add__(self,other):
        added = copy.deepcopy(self.items)
        added.update(other.items)
        if self.type == 'var' and self.type == 'var': newGroup = VarGroup(self.name+"+"+other.name)
        elif self.type == 'cut' and self.type == 'cut': newGroup = CutGroup(self.name+"+"+other.name)
        else: newGroup = Group(self.name+"+"+other.name)
        newGroup.items = added
        return newGroup

    def keys(self):
        return self.items.keys()

    def __getitem__(self,key):
        return self.items[key]

# Subclass for cuts
class CutGroup(Group):
    """docstring for CutGroup"""
    def __init__(self, name):
        super(CutGroup,self).__init__(name)
        self.type = 'cut'
        
# Subclass for vars/columns
class VarGroup(Group):
    """docstring for VarGroup"""
    def __init__(self, name):
        super(VarGroup,self).__init__(name)
        self.type = 'var'

# Subclass for histograms
class HistGroup(Group):
    """docstring for VarGroup"""
    def __init__(self, name):
        super(HistGroup,self).__init__(name)
        self.type = 'hist'

    # Batch act on histograms - THmethod is a string and argsTuple is a tuple of arguments to pass the THmethod
    def Do(THmethod,argsTuple):
        # Book new group in case THmethod returns something
        newGroup = Group(self.name+'_%s%s'%(THmethod,argsTuple))
        # Initialize check for None return type
        returnNone = False
        # Loop over hists
        for name,hist in self.items.items():
            out = getattr(hist,THmethod)(*argsTuple)
            # If None type, set returnNone = True
            if out == None and returnNone == False: returnNone = True
            # If return is not None, add 
            if not returnNone:
                newGroup.Add(name+'_%s%s'%(THmethod,argsTuple),out)

        if returnNone: del newGroup
        else: return newGroup