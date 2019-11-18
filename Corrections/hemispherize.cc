#define _USE_MATH_DEFINES

#include <cmath>
using namespace ROOT::VecOps;
using rvec_f = const RVec<float> &;
//return two ak4 cnadidates that are properly selected by hemispherize funtion for 2+1
//Compares ak4 jets against leading ak8 and looks for any in opposite hemisphere
//First find the highest pt ak8 jet with mass > 40 geV
namespace analyzer {
     RVec<int> Hemispherize(rvec_f FJpt, rvec_f FJeta, rvec_f FJphi, rvec_f FJmass, int FJnjets, rvec_f Jpt, rvec_f Jeta, rvec_f Jphi, rvec_f Jmass, int Jnjets, rvec_f btagDeepB){
        //First find the highest pt ak8 jet with mass > 40 geV
        RVec<int> fail; //this is used for if the hemispherize fails so we can filter the event
        fail.push_back(0);
        fail.push_back(0);

        auto candidateFatJetIndex = -1;
        for (int i =0; i<FJnjets; i++){

            if (FJmass[i] > 40) {
                candidateFatJetIndex = i;
                break;
            }
        }
        if (candidateFatJetIndex == -1){
            return fail;
        }

        RVec<int> candidateJetIndices;
        //Check the AK4s against the AK8
        for (int ijet = 0; ijet<Jnjets; ijet++){
            if (abs(FJphi[candidateFatJetIndex]-Jphi[ijet]) > M_PI_2 ){
                candidateJetIndices.push_back(std::forward<int>(ijet));
            }
        }

        //If not enough jets, end it
        if (candidateJetIndices.size() < 2){
            return fail;
        }
        //Else compare jets and find those within R of 1.5 (make pairs)

        else{
            //Compare all pairs
            auto pairs_cmb = Combinations(Jpt,2);
            RVec<RVec<int>> passing_pair_indices;
            RVec<int> temp_pair;
            for (size_t i = 0; i<pairs_cmb[0].size(); i++){   // this is providing pairs of indices of the candidateJetIndices list! (not the indices of the jetCollection!)
                const auto i1 = pairs_cmb[0][i];
                const auto i2 = pairs_cmb[1][i];

                TLorentzVector* v1 = new TLorentzVector();
                v1->SetPtEtaPhiM(Jpt[i1],Jeta[i1],Jphi[i1],Jmass[i1]);

                TLorentzVector* v2 = new TLorentzVector();
                v2->SetPtEtaPhiM(Jpt[i2],Jeta[i2],Jphi[i2],Jmass[i2]);

                if (v1->DeltaR(*v2) < 1.5){
                    // Save out collection index of those that pass
                    temp_pair.push_back(i1);
                    temp_pair.push_back(i2);
                    passing_pair_indices.push_back(std::forward<RVec<int>>(temp_pair));
                    temp_pair.clear();
                }
            }

            
            // Check if the ak4 jets are in a larger ak8
            // If they are, pop them out of our two lists for consideration
            for (int i =0; i<FJnjets; i++){
                TLorentzVector* fjetLV = new TLorentzVector();
                fjetLV->SetPtEtaPhiM(FJpt[i],FJeta[i],FJphi[i],FJmass[i]);
                for (int i =0; i < passing_pair_indices[0].size(); i++){
                    const auto i1 = passing_pair_indices[0][i];
                    const auto i2 = passing_pair_indices[1][i];
                        TLorentzVector* v1 = new TLorentzVector();
                        v1->SetPtEtaPhiM(Jpt[i1],Jeta[i1],Jphi[i1],Jmass[i1]);
                        TLorentzVector* v2 = new TLorentzVector();
                        v2->SetPtEtaPhiM(Jpt[i2],Jeta[i2],Jphi[i2],Jmass[i2]);

                        if (fjetLV->DeltaR(*v1) < 0.8){
                            passing_pair_indices.erase(passing_pair_indices.begin()+i);
                            break;
                        }
                        if (fjetLV->DeltaR(*v2) < 0.8){
                            passing_pair_indices.erase(passing_pair_indices.begin()+i);
                        }
                }
            }
            RVec<RVec<int>> candidatePairIdx;
            RVec<int> PairIdx;
            //if STILL greater than 1 pair...
            if (passing_pair_indices.size() > 1){
                // Now pick based on summed btag values
                float btagsum = 0;
                const auto i1 = passing_pair_indices[0][i];
                const auto i2 = passing_pair_indices[1][i];
                for (int i =0; i < passing_pair_indices[0].size(); i++) {
                    float thisbtagsum = btagDeepB[passing_pair_indices[i1]] + btagDeepB[passing_pair_indices[i2]];
                    if (thisbtagsum > btagsum){
                        btagsum = thisbtagsum;
                        candidatePairIdx.push_back(std::forward<RVec<int>>(passing_pair_indices[i]));
                    }
                }
            } else if (passing_pair_indices.size() == 1){
                candidatePairIdx.push_back(std::forward<RVec<int>>(passing_pair_indices[0]));
            } else{
                candidatePairIdx.push_back(fail); 
            }
            
            if (candidatePairIdx.size() == 1){
                PairIdx.push_back(std::forward<int>(candidatePairIdx[0][0]));
                PairIdx.push_back(std::forward<int>(candidatePairIdx[0][1]));
                return PairIdx;
            } else{
                return fail;
            }

        }
    }
}