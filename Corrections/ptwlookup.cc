#include <cmath>
using namespace ROOT::VecOps;
using rvec_f = const RVec<float> &;
using rvec_i = const RVec<int> &;

namespace analyzer {
    std::vector<std::pair<float, bool>> PTWLookup(rvec_i nGenJet, rvec_i GPpdgId, rvec_i GPstatusFlags, rvec_f GPpt, rvec_f GPeta, rvec_f GPphi, rvec_f GPmass,TLorentzVector* jet0, TLorentzVector* jet1 ){

        std::vector<std::pair<float, bool>> out;

        float genTpt = 0;
        float genTBpt = 0;
        float wTPt, wTbarPt; 
        bool pair_exists = False;

        // For all gen particles
        for (int i =0; i < nGenJet; i++){
            if ((GPpdgId == -6) && (GPstatusFlags & (1 << 13))){ 
                TLorentzVector* antitop_lv = new TLorentzVector();
                antitop_lv->SetPtEtaPhiM(GPpt,GPeta,GPphi,GPmass);
                if ((antitop_lv.DeltaR(jet0) <0.8) || (antitop_lv.DeltaR(jet1) <0.8)){
                    genTBpt = GPpt;
                }
            }elif ((GPpdgId == 6) && (GPstatusFlags & (1 << 13))){ 
                TLorentzVector* top_lv = new TLorentzVector();
                top_lv->SetPtEtaPhiM(GPpt,GPeta,GPphi,GPmass);
                if ((top_lv.DeltaR(jet0) <0.8) || (top_lv.DeltaR(jets1) <0.8)){
                    genTpt = GPpt;
                }
            }
        }

        if (genTpt == 0) || (genTBpt == 0){
            pair_exists = False;
        }else{ 
            pair_exists = True;
        }
        
        if (genTpt == 0){ 
            wTPt = 1.0;
        }else{
            wTPt = exp(0.0615-0.0005*genTpt);
        }

        if (genTBpt == None){ 
            wTbarPt = 1.0;
        }else{
            wTbarPt = exp(0.0615-0.0005*genTBpt);
        }

        out.push_back(std::make_pair(sqrt(wTPt*wTbarPt),pair_exists));
        return out;
}