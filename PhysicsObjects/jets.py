from base import particle

class FatJet(base):
    """docstring for FatJet"""
    def __init__(self):
        super(FatJet, self).__init__()
        self.R = 0.8

class Jet(base):
    """docstring for Jet"""
    def __init__(self):
        super(Jet, self).__init__()
        self.R = 0.4
        
class W(FatJet):
    """docstring for W"""
    def __init__(self):
        super(W, self).__init__()

    def ScaleFactor(self):
        self.mc2dataSF

class Z(FatJet):
    """docstring for Z"""
    def __init__(self):
        super(Z, self).__init__()

    def ScaleFactor(self):
        self.mc2dataSF

class Higgs(FatJet):
    """docstring for Higgs"""
    def __init__(self):
        super(Higgs, self).__init__()

    def ScaleFactor(self):
        self.mc2dataSF

class top(FatJet):
    """docstring for top"""
    def __init__(self):
        super(top, self).__init__()
    
    def ScaleFactor(self):
        self.mc2dataSF

class bottom(Jet):
    """docstring for bottom"""
    def __init__(self):
        super(bottom, self).__init__()
        
    def ScaleFactor(self):
        self.mc2dataSF