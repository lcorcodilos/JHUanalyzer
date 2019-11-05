#include <cmath>
#include <stdbool.h>
using namespace ROOT::VecOps;
using rvec_i = const RVec<int>;

namespace analyzer {
    std::vector<std::pair<float, bool>> PTWLookup(int nGenJet, rvec_i GPpdgId, int GPstatusFlags, double GPpt, double GPeta, double GPphi, double GPmass,TLorentzVector* jet0, TLorentzVector* jet1 ){

        std::vector<std::pair<float, bool>> out;

        float genTpt = 0;
        float genTBpt = 0;
        float wTPt, wTbarPt; 
        bool pair_exists = false;

        // For all gen particles
        for (int i =0; i < nGenJet; i++){
            if ((GPpdgId == -6) && (GPstatusFlags & (1 << 13))){ 
                TLorentzVector* antitop_lv = new TLorentzVector();
                antitop_lv->SetPtEtaPhiM(GPpt,GPeta,GPphi,GPmass);
                if ((antitop_lv->DeltaR(*jet0) <0.8) || (antitop_lv->DeltaR(*jet1) <0.8)){
                    genTBpt = GPpt;
                }
            }else if ((GPpdgId == 6) && (GPstatusFlags & (1 << 13))){ 
                TLorentzVector* top_lv = new TLorentzVector();
                top_lv->SetPtEtaPhiM(GPpt,GPeta,GPphi,GPmass);
                if ((top_lv->DeltaR(*jet0) <0.8) || (top_lv->DeltaR(*jet1) <0.8)){
                    genTpt = GPpt;
                }
            }
        }

        if ((genTpt == 0) || (genTBpt == 0)){
            pair_exists = false;
        }else{ 
            pair_exists = true;
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

        out.push_back(std::make_pair(sqrt(wTPt*wTbarPt),pair_exists));
        return out;
    }
}