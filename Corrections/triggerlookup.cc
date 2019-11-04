#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<float> TriggerLookup(float var, TH1D* TRP ){
        float Weight;
        float Weightup;
        float Weightdown;

        std::vector<float> out;

        if (var < 2000.0){
            int bin0 = TRP->FindBin(var); 
            float jetTriggerWeight = TRP->GetBinContent(bin0);
            // Check that we're not in an empty bin in the fully efficient region
            if (jetTriggerWeight == 0){
                if ((TRP->GetBinContent(bin0-1) == 1.0) && (TRP->GetBinContent(bin0+1) == 1.0)){
                    jetTriggerWeight = 1.0;
                }else if (((TRP->GetBinContent(bin0-1) > 0) || (TRP->GetBinContent(bin0+1) > 0))){
                    jetTriggerWeight = (TRP->GetBinContent(bin0-1)+TRP->GetBinContent(bin0+1))/2.0;
                }

            Weight = jetTriggerWeight;
            float deltaTriggerEff  = 0.5*(1.0-jetTriggerWeight);
            Weightup = std::min(1.0,(jetTriggerWeight + deltaTriggerEff));
            Weightdown = std::max(0.0,(jetTriggerWeight - deltaTriggerEff));
            }
        }    
        out.push_back(Weight);
        out.push_back(Weightup);
        out.push_back(Weightdown);
        return out;
    }
}