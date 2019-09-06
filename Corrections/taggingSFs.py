def LoadDoubleBSF(year, wp):
    if year == 17: filename = 'JHUanalyzer/SFs/doubleb_dummy_94x.root'

    ROOT.gInterpreter.ProcessLine('auto doublebsf_hist = hist')

    loop_code = '''
    namespace analyzer {
        std::vector<float> GetDoubleBSF(float pt) {
            int this_bin = doublebsf_hist->FindBin(pt);
            float nom = doublebsf_hist->GetBinContent(this_bin);
            float up = doublebsf_hist->GetBinContent(this_bin) + doublebsf_hist->GetBinErrorUp(this_bin);
            float down = doublebsf_hist->GetBinContent(this_bin) + doublebsf_hist->GetBinErrorLow(this_bin);

            std::vector<float> out = {nom,up,down};
            return out;
        };
    }
    '''

    GetHist(filename,wp,'doublebsf_hist',loopcode)

#------------Helper functions--------------------

def GetHist(filename,histname,outname,loopcode):
    file = TFile.Open(filename)
    hist = file.Get(histname)
    ROOT.gInterpreter.ProcessLine('auto '+outname+' = hist')
    ROOT.gInterpreter.Declare(loopcode)