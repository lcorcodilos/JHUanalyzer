// with CMSSW:
#include "CondFormats/BTauObjects/interface/BTagCalibration.h"
#include "CondTools/BTau/interface/BTagCalibrationReader.h"

// without CMSSW / standalone:
//#include "BTagCalibrationStandalone.h"
//#include "BTagCalibrationStandalone.cpp"

#include <cmath>
using namespace ROOT::VecOps;

namespace analyzer {
    std::vector<float> btagSF(string year, TLorentzVector* b_jet0,TLorentzVector* b_jet1) {
    	std::vector<float> v;
	    if (year == '16'){
            BTagCalibration calib('DeepCSV', 'SFs/DeepCSV_2016LegacySF_V1.csv');
        }elif (year == '17'){
            BTagCalibration calib('DeepCSV', 'SFs/DeepCSV_94XSF_V4_B_F.csv');
        }elif (year == '18'){
            BTagCalibration calib('DeepCSV', 'SFs/DeepCSV_102XSF_V1.csv');
        }

		BTagCalibrationReader reader(BTagEntry::OP_LOOSE,  // operating point
                             "central",             // central sys type
                             {"up", "down"});      // other sys types

		reader.load(calib,                // calibration instance
            BTagEntry::FLAV_B,    // btag flavour
            "incl")               // measurement type


      // Note: this is for b jets, for c jets (light jets) use FLAV_C (FLAV_UDSG)
      double jet_scalefactor = reader.eval_auto_bounds("central", BTagEntry::FLAV_B, b_jet0.eta(),b_jet0.pt()); 
      double jet_scalefactor_up = reader.eval_auto_bounds("up", BTagEntry::FLAV_B, b_jet0.eta(), b_jet0.pt());
      double jet_scalefactor_do = reader.eval_auto_bounds("down", BTagEntry::FLAV_B, b_jet0.eta(), b_jet0.pt());

      jet_scalefactor *= reader.eval_auto_bounds("central", BTagEntry::FLAV_B, b_jet1.eta(),b_jet1.pt()); 
      jet_scalefactor_up *= reader.eval_auto_bounds("up", BTagEntry::FLAV_B, b_jet1.eta(), b_jet1.pt());
      jet_scalefactor_do *= reader.eval_auto_bounds("down", BTagEntry::FLAV_B, b_jet1.eta(), b_jet1.pt());


      v.push_back(jet_scalefactor);
      v.push_back(jet_scalefactor_up);
      v.push_back(jet_scalefactor_do);

      return v;
}