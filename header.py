import ROOT
from ROOT import *
from contextlib import contextmanager
import os, pickle, subprocess
import math
from math import sqrt
import array
import json

# Function stolen from https://stackoverflow.com/questions/9590382/forcing-python-json-module-to-work-with-ascii
def openJSON(f):
    with open(f) as fInput_config:
        input_config = json.load(fInput_config, object_hook=ascii_encode_dict)  # Converts most of the unicode to ascii

        for process in [proc for proc in input_config['PROCESS'].keys() if proc != 'HELP']:
            for index,item in enumerate(input_config['PROCESS'][process]['SYSTEMATICS']):           # There's one list that also
                input_config['PROCESS'][process]['SYSTEMATICS'][index] = item.encode('ascii')  

    return input_config

def ascii_encode_dict(data):    
    ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x 
    return dict(map(ascii_encode, pair) for pair in data.items())

def copyHistWithNewXbins(thisHist,newXbins,copyName):
    # Make a copy with the same Y bins but new X bins
    ybins = []
    for iy in range(1,thisHist.GetNbinsY()+1):
        ybins.append(thisHist.GetYaxis().GetBinLowEdge(iy))
    ybins.append(thisHist.GetYaxis().GetXmax())

    ybins_array = array.array('f',ybins)
    ynbins = len(ybins_array)-1

    xbins_array = array.array('f',newXbins)
    xnbins = len(xbins_array)-1 

    # Use copyName with _temp to avoid overwriting if thisHist has the same name
    # We can do this at the end but not before we're finished with thisHist
    hist_copy = TH2F(copyName+'_temp',copyName+'_temp',xnbins,xbins_array,ynbins,ybins_array)
    hist_copy.Sumw2()
    
    hist_copy.GetXaxis().SetName(thisHist.GetXaxis().GetName())
    hist_copy.GetYaxis().SetName(thisHist.GetYaxis().GetName())

    # Loop through the old bins
    for ybin in range(1,ynbins+1):
        # print 'Bin y: ' + str(binY)
        for xbin in range(1,xnbins+1):
            new_bin_content = 0
            new_bin_errorsq = 0
            new_bin_min = hist_copy.GetXaxis().GetBinLowEdge(xbin)
            new_bin_max = hist_copy.GetXaxis().GetBinUpEdge(xbin)

            # print '\t New bin x: ' + str(newBinX) + ', ' + str(newBinXlow) + ', ' + str(newBinXhigh)
            bins_added = 0
            for old_xbin in range(1,thisHist.GetNbinsX()+1):
                if thisHist.GetXaxis().GetBinLowEdge(old_xbin) >= new_bin_min and thisHist.GetXaxis().GetBinUpEdge(old_xbin) <= new_bin_max:
                    # print '\t \t Old bin x: ' + str(oldBinX) + ', ' + str(thisHist.GetXaxis().GetBinLowEdge(oldBinX)) + ', ' + str(thisHist.GetXaxis().GetBinUpEdge(oldBinX))
                    # print '\t \t Adding content ' + str(thisHist.GetBinContent(oldBinX,binY))
                    bins_added +=1
                    if thisHist.GetBinContent(old_xbin,ybin) >= 0.0:
                        new_bin_content += thisHist.GetBinContent(old_xbin,ybin)
                        new_bin_errorsq += thisHist.GetBinError(old_xbin,ybin)**2

            # new_bin_content /= bins_added
            # new_bin_errorsq /= bins_added

            # print '\t Setting content ' + str(newBinContent) + '+/-' + str(sqrt(newBinErrorSq))
            if new_bin_content > 0:
                # new_bin_content = new_bin_content/(hist_copy.GetXaxis().GetBinWidth(xbin)/oldBinWidth)
                # new_bin_errorsq = new_bin_errorsq/(hist_copy.GetXaxis().GetBinWidth(xbin)/oldBinWidth)
                hist_copy.SetBinContent(xbin,ybin,new_bin_content)
                hist_copy.SetBinError(xbin,ybin,sqrt(new_bin_errorsq))

    # Will now set the copyName which will overwrite thisHist if it has the same name
    hist_copy.SetName(copyName)
    hist_copy.SetTitle(copyName)

    return hist_copy

def copyHistWithNewYbins(thisHist,newYbins,copyName):
    # Make a copy with the same X bins but new Y bins
    xbins = []
    for ix in range(1,thisHist.GetNbinsX()+1):
        xbins.append(thisHist.GetXaxis().GetBinLowEdge(ix))
    xbins.append(thisHist.GetXaxis().GetXmax())

    xbins_array = array.array('f',xbins)
    xnbins = len(xbins_array)-1

    ybins_array = array.array('f',newYbins)
    ynbins = len(ybins_array)-1

    # Use copyName with _temp to avoid overwriting if thisHist has the same name
    # We can do this at the end but not before we're finished with thisHist
    hist_copy = TH2F(copyName+'_temp',copyName+'_temp',xnbins,xbins_array,ynbins,ybins_array)
    hist_copy.Sumw2()
    
    hist_copy.GetXaxis().SetName(thisHist.GetXaxis().GetName())
    hist_copy.GetYaxis().SetName(thisHist.GetYaxis().GetName())

    # Loop through the old bins
    for xbin in range(1,xnbins+1):
        # print 'Bin y: ' + str(binY)
        for ybin in range(1,ynbins+1):
            new_bin_content = 0
            new_bin_errorsq = 0
            new_bin_min = hist_copy.GetYaxis().GetBinLowEdge(ybin)
            new_bin_max = hist_copy.GetYaxis().GetBinUpEdge(ybin)

            # print '\t New bin x: ' + str(newBinX) + ', ' + str(newBinXlow) + ', ' + str(newBinXhigh)
            bins_added = 0
            for old_ybin in range(1,thisHist.GetNbinsY()+1):
                if thisHist.GetYaxis().GetBinLowEdge(old_ybin) >= new_bin_min and thisHist.GetYaxis().GetBinUpEdge(old_ybin) <= new_bin_max:
                    # print '\t \t Old bin x: ' + str(oldBinX) + ', ' + str(thisHist.GetXaxis().GetBinLowEdge(oldBinX)) + ', ' + str(thisHist.GetXaxis().GetBinUpEdge(oldBinX))
                    # print '\t \t Adding content ' + str(thisHist.GetBinContent(oldBinX,binY))
                    bins_added += 1
                    if thisHist.GetBinContent(xbin,old_ybin) >= 0.0:
                        new_bin_content += thisHist.GetBinContent(xbin,old_ybin)
                        new_bin_errorsq += thisHist.GetBinError(xbin,old_ybin)**2

            # new_bin_content /= bins_added
            # new_bin_errorsq /= bins_added

            # print '\t Setting content ' + str(newBinContent) + '+/-' + str(sqrt(newBinErrorSq))
            if new_bin_content > 0:
                # new_bin_content = new_bin_content/(hist_copy.GetXaxis().GetBinWidth(xbin)/oldBinWidth)
                # new_bin_errorsq = new_bin_errorsq/(hist_copy.GetXaxis().GetBinWidth(xbin)/oldBinWidth)
                hist_copy.SetBinContent(xbin,ybin,new_bin_content)
                hist_copy.SetBinError(xbin,ybin,sqrt(new_bin_errorsq))

    # Will now set the copyName which will overwrite thisHist if it has the same name
    hist_copy.SetName(copyName)
    hist_copy.SetTitle(copyName)

    return hist_copy

def stitchHistsInX(name,xbins,ybins,thisHistList,blinded=[]):
    # Required that thisHistList be in order of desired stitching
    # `blinded` is a list of the index of regions you wish to skip/blind
    axbins = array.array('d',xbins)
    aybins = array.array('d',ybins)
    stitched_hist = TH2F(name,name,len(xbins)-1,axbins,len(ybins)-1,aybins)

    bin_jump = 0
    for i,h in enumerate(thisHistList):
        if i in blinded:
            bin_jump += thisHistList[i].GetNbinsX()
            continue
        
        for ybin in range(1,h.GetNbinsY()+1):
            for xbin in range(1,h.GetNbinsX()+1):
                stitched_xindex = xbin + bin_jump

                stitched_hist.SetBinContent(stitched_xindex,ybin,h.GetBinContent(xbin,ybin))
                stitched_hist.SetBinError(stitched_xindex,ybin,h.GetBinError(xbin,ybin))

        bin_jump += thisHistList[i].GetNbinsX()

    return stitched_hist

def rebinY(thisHist,name,tag,new_y_bins_array):
    xnbins = thisHist.GetNbinsX()
    xmin = thisHist.GetXaxis().GetXmin()
    xmax = thisHist.GetXaxis().GetXmax()

    rebinned = TH2F(name,name,xnbins,xmin,xmax,len(new_y_bins_array)-1,new_y_bins_array)
    # print new_y_bins_array
    # print rebinned.GetYaxis().GetBinUpEdge(len(new_y_bins_array)-1)
    rebinned.Sumw2()

    for xbin in range(1,xnbins+1):
        newBinContent = 0
        newBinErrorSq = 0
        rebinHistYBin = 1
        nybins = 0
        for ybin in range(1,thisHist.GetNbinsY()+1):
            # If upper edge of old Rpf ybin is < upper edge of rebinHistYBin then add the Rpf bin to the count
            if thisHist.GetYaxis().GetBinUpEdge(ybin) < rebinned.GetYaxis().GetBinUpEdge(rebinHistYBin):
                newBinContent += thisHist.GetBinContent(xbin,ybin)
                newBinErrorSq += thisHist.GetBinError(xbin,ybin)**2
                nybins+=1
            # If ==, add to newBinContent, assign newBinContent to current rebinHistYBin, move to the next rebinHistYBin, and restart newBinContent at 0
            elif thisHist.GetYaxis().GetBinUpEdge(ybin) == rebinned.GetYaxis().GetBinUpEdge(rebinHistYBin):
                newBinContent += thisHist.GetBinContent(xbin,ybin)
                newBinErrorSq += thisHist.GetBinError(xbin,ybin)**2
                nybins+=1
                rebinned.SetBinContent(xbin, rebinHistYBin, newBinContent/float(nybins))
                rebinned.SetBinError(xbin, rebinHistYBin, sqrt(newBinErrorSq)/float(nybins))# NEED TO SET BIN ERRORS
                rebinHistYBin += 1
                newBinContent = 0
                newBinErrorSq = 0
                nybins = 0
            else:
                print 'ERROR when doing psuedo-2D y rebin approximation. Slices do not line up on y bin edges'
                print 'Input bin upper edge = '+str(thisHist.GetYaxis().GetBinUpEdge(ybin))
                print 'Rebin upper edge = '+str(rebinned.GetYaxis().GetBinUpEdge(rebinHistYBin))
                quit()

    makeCan(name+'_rebin_compare',tag,[rebinned,thisHist])
    return rebinned

def splitBins(binList, sigLow, sigHigh):
    return_bins = {'LOW':[],'SIG':[],'HIGH':[]}
    for b in binList:
        if b <= sigLow:
            return_bins['LOW'].append(b)
        if b >= sigLow and b <= sigHigh:
            return_bins['SIG'].append(b)
        if b >= sigHigh:
            return_bins['HIGH'].append(b)

    return return_bins 

def remapToUnity(hist):

    ybins = array.array('d',[(hist.GetYaxis().GetBinLowEdge(b)-hist.GetYaxis().GetXmin())/(hist.GetYaxis().GetXmax()-hist.GetYaxis().GetXmin()) for b in range(1,hist.GetNbinsY()+1)]+[1])
    xbins = array.array('d',[(hist.GetXaxis().GetBinLowEdge(b)-hist.GetXaxis().GetXmin())/(hist.GetXaxis().GetXmax()-hist.GetXaxis().GetXmin()) for b in range(1,hist.GetNbinsX()+1)]+[1])

    remap = TH2F(hist.GetName()+'_unit',hist.GetName()+'_unit',hist.GetNbinsX(),xbins,hist.GetNbinsY(),ybins)
    remap.Sumw2()

    for xbin in range(hist.GetNbinsX()+1):
        for ybin in range(hist.GetNbinsY()+1):
            remap.SetBinContent(xbin,ybin,hist.GetBinContent(xbin,ybin))
            remap.SetBinError(xbin,ybin,hist.GetBinError(xbin,ybin))

    return remap

def makeBlindedHist(nomHist,sigregion):
    # Grab stuff to make it easier to read
    xlow = nomHist.GetXaxis().GetXmin()
    xhigh = nomHist.GetXaxis().GetXmax()
    xnbins = nomHist.GetNbinsX()
    ylow = nomHist.GetYaxis().GetXmin()
    yhigh = nomHist.GetYaxis().GetXmax()
    ynbins = nomHist.GetNbinsY()
    blindName = nomHist.GetName()

    # Need to change nominal hist name or we'll get a memory leak
    nomHist.SetName(blindName+'_unblinded')

    blindedHist = TH2F(blindName,blindName,xnbins,xlow,xhigh,ynbins,ylow,yhigh)
    blindedHist.Sumw2()

    for binY in range(1,ynbins+1):
        # Fill only those bins outside the signal region
        for binX in range(1,xnbins+1):
            if nomHist.GetXaxis().GetBinUpEdge(binX) <= sigregion[0] or nomHist.GetXaxis().GetBinLowEdge(binX) >= sigregion[1]:
                if nomHist.GetBinContent(binX,binY) > 0:
                    blindedHist.SetBinContent(binX,binY,nomHist.GetBinContent(binX,binY))
                    blindedHist.SetBinError(binX,binY,nomHist.GetBinError(binX,binY))

    return blindedHist

def colliMate(myString,width=18):
    sub_strings = myString.split(' ')
    new_string = ''
    for i,sub_string in enumerate(sub_strings):
        string_length = len(sub_string)
        n_spaces = width - string_length
        if i != len(sub_strings)-1:
            if n_spaces <= 0:
                n_spaces = 2
            new_string += sub_string + ' '*n_spaces
        else:
            new_string += sub_string
    return new_string

def dictStructureCopy(inDict):
    newDict = {}
    for k1,v1 in inDict.items():
        if type(v1) == dict:
            newDict[k1] = dictStructureCopy(v1)
        else:
            newDict[k1] = 0
    return newDict

def dictCopy(inDict):
    newDict = {}
    for k1,v1 in inDict.items():
        if type(v1) == dict:
            newDict[k1] = dictCopy(v1)
        else:
            newDict[k1] = v1
    return newDict

def executeCmd(cmd,dryrun=False):
    print 'Executing: '+cmd
    if not dryrun:
        subprocess.call([cmd],shell=True)

def dictToLatexTable(dict2convert,outfilename,roworder=[],columnorder=[]):
    # First set of keys are row, second are column
    if len(roworder) == 0:
        rows = sorted(dict2convert.keys())
    else:
        rows = roworder
    if len(columnorder) == 0:
        columns = []
        for r in rows:
            thesecolumns = dict2convert[r].keys()
            for c in thesecolumns:
                if c not in columns:
                    columns.append(c)
        columns.sort()
    else:
        columns = columnorder

    latexout = open(outfilename,'w')
    latexout.write('\\begin{table}[] \n')
    latexout.write('\\begin{tabular}{|c|'+len(columns)*'c'+'|} \n')
    latexout.write('\\hline \n')

    column_string = ' &'
    for c in columns:
        column_string += str(c)+'\t& '
    column_string = column_string[:-2]+'\\\ \n'
    latexout.write(column_string)

    latexout.write('\\hline \n')
    for r in rows:
        row_string = '\t'+r+'\t& '
        for c in columns:
            if c in dict2convert[r].keys():
                row_string += str(dict2convert[r][c])+'\t& '
            else:
                row_string += '- \t& '
        row_string = row_string[:-2]+'\\\ \n'
        latexout.write(row_string)

    latexout.write('\\hline \n')
    latexout.write('\\end{tabular} \n')
    latexout.write('\\end{table}')
    latexout.close()


def makeCan(name, tag, histlist, bkglist=[],signals=[],colors=[],titles=[],logy=False,rootfile=False,xtitle='',ytitle='',dataOff=False,datastyle='pe'):  
    # histlist is just the generic list but if bkglist is specified (non-empty)
    # then this function will stack the backgrounds and compare against histlist as if 
    # it is data. The imporant bit is that bkglist is a list of lists. The first index
    # of bkglist corresponds to the index in histlist (the corresponding data). 
    # For example you could have:
    #   histlist = [data1, data2]
    #   bkglist = [[bkg1_1,bkg2_1],[bkg1_2,bkg2_2]]

    if len(histlist) == 1:
        width = 800
        height = 700
        padx = 1
        pady = 1
    elif len(histlist) == 2:
        width = 1200
        height = 700
        padx = 2
        pady = 1
    elif len(histlist) == 3:
        width = 1600
        height = 700
        padx = 3
        pady = 1
    elif len(histlist) == 4:
        width = 1200
        height = 1000
        padx = 2
        pady = 2
    elif len(histlist) == 6 or len(histlist) == 5:
        width = 1600
        height = 1000
        padx = 3
        pady = 2
    else:
        print 'histlist of size ' + str(len(histlist)) + ' not currently supported'
        return 0

    myCan = TCanvas(name,name,width,height)
    myCan.Divide(padx,pady)

    # Just some colors that I think work well together and a bunch of empty lists for storage if needed
    default_colors = [kRed,kMagenta,kGreen,kCyan,kBlue]
    if len(colors) == 0:   
        colors = default_colors
    stacks = []
    tot_hists = []
    legends = []
    mains = []
    subs = []
    pulls = []
    logString = ''

    # For each hist/data distribution
    for hist_index, hist in enumerate(histlist):
        # Grab the pad we want to draw in
        myCan.cd(hist_index+1)
        if len(histlist) > 1:
            thisPad = myCan.GetPrimitive(name+'_'+str(hist_index+1))
            thisPad.cd()
        
        

        # If this is a TH2, just draw the lego
        if hist.ClassName().find('TH2') != -1:
            if logy == True:
                gPad.SetLogy()
            gPad.SetLeftMargin(0.2)
            hist.GetXaxis().SetTitle(xtitle)
            hist.GetYaxis().SetTitle(ytitle)
            hist.GetXaxis().SetTitleOffset(1.5)
            hist.GetYaxis().SetTitleOffset(2.3)
            hist.GetZaxis().SetTitleOffset(1.8)
            if len(titles) > 0:
                hist.SetTitle(titles[hist_index])

            hist.Draw('lego')
            if len(bkglist) > 0:
                print 'ERROR: It seems you are trying to plot backgrounds with data on a 2D plot. This is not supported since there is no good way to view this type of distribution.'
        
        # Otherwise it's a TH1 hopefully
        else:
            alpha = 1
            if dataOff:
                alpha = 0
            hist.SetLineColorAlpha(kBlack,alpha)
            if 'pe' in datastyle.lower():
                hist.SetMarkerColorAlpha(kBlack,alpha)
                hist.SetMarkerStyle(8)
            if 'hist' in datastyle.lower():
                hist.SetFillColorAlpha(0,0)
            
            # If there are no backgrounds, only plot the data (semilog if desired)
            if len(bkglist) == 0:
                hist.GetXaxis().SetTitle(xtitle)
                hist.GetYaxis().SetTitle(ytitle)
                if len(titles) > 0:
                    hist.SetTitle(titles[hist_index])
                hist.Draw(datastyle)
            
            # Otherwise...
            else:
                # Create some subpads, a legend, a stack, and a total bkg hist that we'll use for the error bars
                if not dataOff:
                    mains.append(TPad(hist.GetName()+'_main',hist.GetName()+'_main',0, 0.3, 1, 1))
                    subs.append(TPad(hist.GetName()+'_sub',hist.GetName()+'_sub',0, 0, 1, 0.3))

                else:
                    mains.append(TPad(hist.GetName()+'_main',hist.GetName()+'_main',0, 0.1, 1, 1))
                    subs.append(TPad(hist.GetName()+'_sub',hist.GetName()+'_sub',0, 0, 0, 0))

                legends.append(TLegend(0.65,0.6,0.95,0.93))
                stacks.append(THStack(hist.GetName()+'_stack',hist.GetName()+'_stack'))
                tot_hist = hist.Clone(hist.GetName()+'_tot')
                tot_hist.Reset()
                tot_hist.SetTitle(hist.GetName()+'_tot')
                tot_hist.SetMarkerStyle(0)
                tot_hists.append(tot_hist)


                # Set margins and make these two pads primitives of the division, thisPad
                mains[hist_index].SetBottomMargin(0.0)
                mains[hist_index].SetLeftMargin(0.16)
                mains[hist_index].SetRightMargin(0.05)
                mains[hist_index].SetTopMargin(0.1)

                subs[hist_index].SetLeftMargin(0.16)
                subs[hist_index].SetRightMargin(0.05)
                subs[hist_index].SetTopMargin(0)
                subs[hist_index].SetBottomMargin(0.3)
                mains[hist_index].Draw()
                subs[hist_index].Draw()

                # Build the stack
                for bkg_index,bkg in enumerate(bkglist[hist_index]):     # Won't loop if bkglist is empty
                    # bkg.Sumw2()
                    tot_hists[hist_index].Add(bkg)
                    bkg.SetLineColor(kBlack)
                    if logy:
                        bkg.SetMinimum(1e-3)

                    if bkg.GetName().find('qcd') != -1:
                        bkg.SetFillColor(kYellow)

                    else:
                        if colors[bkg_index] != None:
                            bkg.SetFillColor(colors[bkg_index])
                        else:
                            bkg.SetFillColor(default_colors[bkg_index])

                    stacks[hist_index].Add(bkg)

                    legends[hist_index].AddEntry(bkg,bkg.GetName().split('_')[0],'f')
                    
                # Go to main pad, set logy if needed
                mains[hist_index].cd()

                # Set y max of all hists to be the same to accomodate the tallest
                histList = [stacks[hist_index],tot_hists[hist_index],hist]

                yMax = histList[0].GetMaximum()
                maxHist = histList[0]
                for h in range(1,len(histList)):
                    if histList[h].GetMaximum() > yMax:
                        yMax = histList[h].GetMaximum()
                        maxHist = histList[h]
                for h in histList:
                    h.SetMaximum(yMax*1.1)
                    if logy == True:
                        h.SetMaximum(yMax*10)

                
                mLS = 0.06
                # Now draw the main pad
                data_leg_title = hist.GetTitle()
                if len(titles) > 0:
                    hist.SetTitle(titles[hist_index])
                hist.SetTitleOffset(1.5,"xy")
                hist.GetYaxis().SetTitle('Events')
                hist.GetYaxis().SetLabelSize(mLS)
                hist.GetYaxis().SetTitleSize(mLS)
                if logy == True:
                    hist.SetMinimum(1e-3)
                hist.Draw(datastyle)

                stacks[hist_index].Draw('same hist')

                # Do the signals
                if len(signals) > 0: 
                    signals[hist_index].SetLineColor(kBlue)
                    signals[hist_index].SetLineWidth(2)
                    if logy == True:
                        signals[hist_index].SetMinimum(1e-3)
                    legends[hist_index].AddEntry(signals[hist_index],signals[hist_index].GetName().split('_')[0],'L')
                    signals[hist_index].Draw('hist same')

                tot_hists[hist_index].SetFillColor(kBlack)
                tot_hists[hist_index].SetFillStyle(3354)

                tot_hists[hist_index].Draw('e2 same')
                # legends[hist_index].Draw()

                if not dataOff:
                    legends[hist_index].AddEntry(hist,'data',datastyle)
                    hist.Draw(datastyle+' same')

                gPad.RedrawAxis()

                # Draw the pull
                subs[hist_index].cd()
                # Build the pull
                pulls.append(Make_Pull_plot(hist,tot_hists[hist_index]))
                pulls[hist_index].SetFillColor(kBlue)
                pulls[hist_index].SetTitle(";"+hist.GetXaxis().GetTitle()+";(Data-Bkg)/#sigma")
                pulls[hist_index].SetStats(0)

                LS = .13

                pulls[hist_index].GetYaxis().SetRangeUser(-2.9,2.9)
                pulls[hist_index].GetYaxis().SetTitleOffset(0.4)
                pulls[hist_index].GetXaxis().SetTitleOffset(0.9)
                             
                pulls[hist_index].GetYaxis().SetLabelSize(LS)
                pulls[hist_index].GetYaxis().SetTitleSize(LS)
                pulls[hist_index].GetYaxis().SetNdivisions(306)
                pulls[hist_index].GetXaxis().SetLabelSize(LS)
                pulls[hist_index].GetXaxis().SetTitleSize(LS)

                pulls[hist_index].GetXaxis().SetTitle(xtitle)
                pulls[hist_index].GetYaxis().SetTitle("(Data-Bkg)/#sigma")
                pulls[hist_index].Draw('hist')

                if logy == True:
                    mains[hist_index].SetLogy()

    if rootfile:
        myCan.Print(tag+'plots/'+name+'.root','root')
    else:
        myCan.Print(tag+'plots/'+name+'.png','png')

def FindCommonString(string_list):
    to_match = ''   # initialize the string we're looking for/building
    for s in string_list[0]:    # for each character in the first string
        passed = True
        for istring in range(1,len(string_list)):   # compare to_match+s against strings in string_list
            string = string_list[istring]
            if to_match not in string:                  # if in the string, add more
                passed = False
            
        if passed == True:
            to_match+=s

    if to_match[-2] == '_':
        return to_match[:-2] 
    else:
        return to_match[:-1]                # if not, return to_match minus final character

    return to_match[:-2]
        
def Make_Pull_plot( DATA,BKG):
    BKGUP, BKGDOWN = Make_up_down(BKG)
    pull = DATA.Clone(DATA.GetName()+"_pull")
    pull.Add(BKG,-1)
    sigma = 0.0
    FScont = 0.0
    BKGcont = 0.0
    for ibin in range(1,pull.GetNbinsX()+1):
        FScont = DATA.GetBinContent(ibin)
        BKGcont = BKG.GetBinContent(ibin)
        if FScont>=BKGcont:
            FSerr = DATA.GetBinErrorLow(ibin)
            BKGerr = abs(BKGUP.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        if FScont<BKGcont:
            FSerr = DATA.GetBinErrorUp(ibin)
            BKGerr = abs(BKGDOWN.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        if FSerr != None:
            sigma = sqrt(FSerr*FSerr + BKGerr*BKGerr)
        else:
            sigma = sqrt(BKGerr*BKGerr)
        if FScont == 0.0:
            pull.SetBinContent(ibin, 0.0 )  
        else:
            if sigma != 0 :
                pullcont = (pull.GetBinContent(ibin))/sigma
                pull.SetBinContent(ibin, pullcont)
            else :
                pull.SetBinContent(ibin, 0.0 )
    return pull

def Make_up_down(hist):
    hist_up = hist.Clone(hist.GetName()+'_up')
    hist_down = hist.Clone(hist.GetName()+'_down')

    for xbin in range(1,hist.GetNbinsX()+1):
        errup = hist.GetBinErrorUp(xbin)
        errdown = hist.GetBinErrorLow(xbin)
        nom = hist.GetBinContent(xbin)

        hist_up.SetBinContent(xbin,nom+errup)
        hist_down.SetBinContent(xbin,nom-errdown)

    return hist_up,hist_down

# Taken from Kevin's limit_plot_shape.py
def make_smooth_graph(h2,h3):
    h2 = TGraph(h2)
    h3 = TGraph(h3)
    npoints = h3.GetN()
    h3.Set(2*npoints+2)
    for b in range(npoints+2):
        x1, y1 = (ROOT.Double(), ROOT.Double())
        if b == 0:
            h3.GetPoint(npoints-1, x1, y1)
        elif b == 1:
            h2.GetPoint(npoints-b, x1, y1)
        else:
            h2.GetPoint(npoints-b+1, x1, y1)
        h3.SetPoint(npoints+b, x1, y1)
    return h3

# Built to wait for condor jobs to finish and then check that they didn't fail
# The script that calls this function will quit if there are any job failures
# listOfJobs input should be whatever comes before '.listOfJobs' for the set of jobs you submitted
def WaitForJobs( listOfJobs ):
    # Runs grep to count the number of jobs - output will have non-digit characters b/c of wc
    preNumberOfJobs = subprocess.check_output('grep "python" '+listOfJobs+' | wc -l', shell=True)
    commentedNumberOfJobs = subprocess.check_output('grep "# python" '+listOfJobs+'.listOfJobs | wc -l', shell=True)

    # Get rid of non-digits and convert to an int
    preNumberOfJobs = int(filter(lambda x: x.isdigit(), preNumberOfJobs))
    commentedNumberOfJobs = int(filter(lambda x: x.isdigit(), commentedNumberOfJobs))
    numberOfJobs = preNumberOfJobs - commentedNumberOfJobs

    finishedJobs = 0
    # Rudementary progress bar
    while finishedJobs < numberOfJobs:
        # Count how many output files there are to see how many jobs finished
        # the `2> null.txt` writes the stderr to null.txt instead of printing it which means
        # you don't have to look at `ls: output_*.log: No such file or directory`
        finishedJobs = subprocess.check_output('ls output_*.log 2> null.txt | wc -l', shell=True)
        finishedJobs = int(filter(lambda x: x.isdigit(), finishedJobs))
        sys.stdout.write('\rProcessing ' + str(listOfJobs) + ' - ')
        # Print the count out as a 'progress bar' that refreshes (via \r)
        sys.stdout.write("%i / %i of jobs finished..." % (finishedJobs,numberOfJobs))
        # Clear the buffer
        sys.stdout.flush()
        # Sleep for one second
        time.sleep(1)


    print 'Jobs completed. Checking for errors...'
    numberOfTracebacks = subprocess.check_output('grep -i "Traceback" output*.log | wc -l', shell=True)
    numberOfSyntax = subprocess.check_output('grep -i "Syntax" output*.log | wc -l', shell=True)

    numberOfTracebacks = int(filter(lambda x: x.isdigit(), numberOfTracebacks))
    numberOfSyntax = int(filter(lambda x: x.isdigit(), numberOfSyntax))

    # Check there are no syntax or traceback errors
    # Future idea - check output file sizes
    if numberOfTracebacks > 0:
        print str(numberOfTracebacks) + ' job(s) failed with traceback error'
        quit()
    elif numberOfSyntax > 0:
        print str(numberOfSyntax) + ' job(s) failed with syntax error'
        quit()
    else:
        print 'No errors!'

def Inter(g1,g2):
    xaxisrange = g1.GetXaxis().GetXmax()-g1.GetXaxis().GetXmin()
    xaxismin = g1.GetXaxis().GetXmin()
    inters = []
    for x in range(0,10000):
        xpoint = xaxismin + (float(x)/1000.0)*xaxisrange
        xpoint1 = xaxismin + (float(x+1)/1000.0)*xaxisrange
        Pr1 = g1.Eval(xpoint)
        Pr2 = g2.Eval(xpoint)
        Po1 = g1.Eval(xpoint1)
        Po2 = g2.Eval(xpoint1)
        if (Pr1-Pr2)*(Po1-Po2)<0:
            inters.append(0.5*(xpoint+xpoint1))
        
    return inters

# Right after I wrote this I realized it's obsolete... It's cool parentheses parsing though so I'm keeping it
def separateXandYfromFitString(fitForm):
    # Look for all opening and closing parentheses
    openIndexes = []
    closedIndexes = []
    for index,char in enumerate(fitForm):
        if char == '(': # start looking for ")" after this "("
            openIndexes.append(index)
        if char == ')':
            closedIndexes.append(index)


    # Now pair them by looking at the first in closedIndexes and finding the closest opening one (to the left)
    # Remove the pair from the index lists and repeat
    innerContent = []
    for iclose in closedIndexes:
        diff = len(fitForm)     # max length to start because we want to minimize
        for iopen in openIndexes:
            if iclose > iopen:
                this_diff = iclose - iopen
                if this_diff < diff:
                    diff = this_diff
                    candidateOpen = iopen
        openIndexes.remove(candidateOpen)
        innerContent.append(fitForm[iclose-diff+1:iclose])


    outerContent = []
    for c in innerContent:
        keep_c = True
        for d in innerContent:
            if '('+c+')' in d and c != d:
                keep_c = False
                break
        if keep_c:
            outerContent.append(c)

    if len(outerContent) != 2:
        print 'ERROR: Form of the fit did not factorize correctly. Please make sure it is in (x part)(y part) form. Quitting...'
        quit()
    else:
        for c in outerContent:
            if 'x' in c and 'y' not in c:
                xPart = c
            elif 'x' not in c and 'y' in c:
                yPart = c
            else:
                print 'ERROR: Form of the fit did not factorize correctly. Please make sure it is in (x part)(y part) form. Quitting...'
                quit()

    return xPart,yPart

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
