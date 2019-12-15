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
            ROOT::Math::PtEtaPhiMVector TLvector(float pt,float eta,float phi,float m) {
                ROOT::Math::PtEtaPhiMVector v(pt,eta,phi,m);
                return v;
            }
        }
        '''
        self.invariantMass = '''
        namespace analyzer {
            double invariantMass(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2) {
                return (v1+v2).M();
            }
        }
        '''
        self.invariantMassThree = '''
        namespace analyzer {
            double invariantMassThree(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2, ROOT::Math::PtEtaPhiMVector v3) {
                return (v1+v2+v3).M();
            }
        }
        '''
        self.HT = '''
        namespace analyzer {
            float HT(std::vector<int> v) {
                float ht = 0.0;
                for(int pt : v) {
                    ht = ht + pt
                }
                return ht;
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