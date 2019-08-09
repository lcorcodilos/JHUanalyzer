class CommonCscripts(object):
    """Common c scripts all in analyzer namespace"""
    def __init__(self):
        super(CommonCscripts, self).__init__()
        self.deltaPhi ='''
        namespace analyzer {
          double deltaPhi(double phi1,double phi2) {
            double result = phi1 - phi2;
            while (result > TMath::Pi()) result -= 2*TMath::Pi();
            while (result <= -TMath::Pi()) result += 2*TMath::Pi();
            return result;
          }
        }
        '''
        self.vector = '''
        namespace analyzer {
            TLorentzVector* TLvector(float pt,float eta,float phi,float m) {
                TLorentzVector* v = new TLorentzVector();
                v->SetPtEtaPhiM(pt,eta,phi,m);
                return v;
            }
        }
        '''
        self.invariantMass = '''
        namespace analyzer {
            double invariantMass(TLorentzVector* v1, TLorentzVector* v2) {
                return (*v1+*v2).M();
            }
        }
        '''
        
class CustomCscripts(object):
    """docstring for CustomCscripts"""
    def __init__(self):
        super(CustomCscripts, self).__init__()
        self.example = '''
        namespace analyzer {
            return 0
        }
        '''
        
    def Import(self,name,textfilename):
        f = open(textfilename,'r')
        setattr(self,name,f.read())