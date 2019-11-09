#include <cmath>
#include <stdbool.h>
using namespace ROOT::VecOps;
using rvec_i = const RVec<int>;
using rvec_d = const RVec<double>;

namespace analyzer {
    std::vector<float> PTWLookup(int nGenJet, rvec_i GPpdgId, rvec_i GPstatusFlags, rvec_d GPpt, rvec_d GPeta, rvec_d GPphi, rvec_d GPmass, TLorentzVector* jet0, TLorentzVector* jet1 ){

        std::vector<float> out;

        float genTpt = 0;
        float genTBpt = 0;
        float wTPt, wTbarPt; 
        bool pair_exists = 0.0;

        // For all gen particles
        for (int i =0; i < nGenJet; i++){
            if ((GPpdgId[i] == -6) && (GPstatusFlags[i] & (1 << 13))){ 
                TLorentzVector* antitop_lv = new TLorentzVector();
                antitop_lv->SetPtEtaPhiM(GPpt[i],GPeta[i],GPphi[i],GPmass[i]);
                if ((antitop_lv->DeltaR(*jet0) <0.8) || (antitop_lv->DeltaR(*jet1) <0.8)){
                    genTBpt = GPpt[i];
                }
            }else if ((GPpdgId[i] == 6) && (GPstatusFlags[i] & (1 << 13))){ 
                TLorentzVector* top_lv = new TLorentzVector();
                top_lv->SetPtEtaPhiM(GPpt[i],GPeta[i],GPphi[i],GPmass[i]);
                if ((top_lv->DeltaR(*jet0) <0.8) || (top_lv->DeltaR(*jet1) <0.8)){
                    genTpt = GPpt[i];
                }
            }
        }

        if ((genTpt == 0) || (genTBpt == 0)){
            pair_exists = 0.0;
        }else{ 
            pair_exists = 1.0;
        }
        
        if (genTpt == 0){ 
            wTPt = 1.0;
        }else{
            wTPt = exp(0.0615-0.0005*genTpt);
        }

        if (genTBpt == 0){ 
            wTbarPt = 1.0;
        }else{
            wTbarPt = exp(0.0615-0.0005*genTBpt);
        }

        out.push_back(sqrt(wTPt*wTbarPt));
        out.push_back(1.5*sqrt(wTPt*wTbarPt));
        out.push_back(0.5*sqrt(wTPt*wTbarPt));
	    out.push_back(pair_exists);
        return out;
    }
}
