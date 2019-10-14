import os
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-t', '--tagger', metavar='FILE', type='string', action='store',
                default   =   'doubleB',
                dest	  =   'tagger',
                help	  =   'Specific tagger you want to use.')
(options, args) = parser.parse_args()

out = open(options.output,'w')

loc_files = [f for f in os.listdir(options.input) if '_loc' in f]

for f in loc_files:
    setname = f.split('_loc.txt')[0]
    out.write('-i '+options.input+'/'+f+' -o HHpreselection17_'+setname+'_'+options.tagger+'.root -c hh17_config.json \n') 
