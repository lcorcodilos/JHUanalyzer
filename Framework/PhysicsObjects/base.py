class particle(object):
    """docstring for particle"""
    def __init__(self):
        super(particle, self).__init__()
        
        self.pt = None
        self.eta = None
        self.phi = None
        self.mass = None
        self.E = None
        self.vector = TLorentzVector()
        self.weight = 1.0
        self.mc2dataSF = 

        self.

    def SetPtEtaPhiM(pt, eta, phi, m):
        self.pt = pt
        self.eta = eta
        self.phi = phi
        self.mass = m
        self.vector.SetPtEtaPhiM(pt, eta, phi, m)

    def SetPtEtaPhiE(pt, eta, phi, E):
        self.pt = pt
        self.eta = eta
        self.phi = phi
        self.E = E
        self.vector.SetPtEtaPhiM(pt, eta, phi, E)

    def ApplySF(sf):
        self.weight *= sf