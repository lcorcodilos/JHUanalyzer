import subprocess, sys, glob, os
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-t', '--taggers', metavar='FILE', type='string', action='store',
                default   =   'btagHbb,deepTagMD_HbbvsQCD,deepTagMD_ZHbbvsQCD,btagDDBvL',
                dest      =   'taggers',
                help      =   'Taggers to consider (comma separated list) as named in the NanoAOD. Default is btagHbb,deepTagMD_HbbvsQCD,deepTagMD_ZHbbvsQCD,btagDDBvL.')
parser.add_option('-y', '--years', metavar='FILE', type='string', action='store',
                default   =   '16,17,18',
                dest      =   'years',
                help      =   'Years to consider (comma separated list). Default is 16,17,18.')
parser.add_option('-i', '--ignoreset', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'ignoreset',
                help      =   'Setnames from *_loc.txt files to IGNORE (comma separated list). Default is empty.')
parser.add_option('-n', '--name', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'name',
                help      =   'A custom name for this argument list (hh_presel_<name>_args.txt)')

(options, args) = parser.parse_args()

# Options to customize run
years = options.years.split(',')
taggers = options.taggers.split(',')
ignore = options.ignoreset.split(',')
name_string = '_'+options.name if options.name != '' else ''

# Initialize output file
outfile = open('../args/hhAll'+name_string+'_args.txt','w')

base_string = '-i TEMPFILE -o TEMPNAME -c TEMPCONFIG -y TEMPYEAR -d TEMPTAGGER'

for year in years:
    for tagger in taggers:
	loc_files = [f for f in glob.glob('../../../NanoAOD'+year+'_lists/*_loc.txt')  if '_loc' in f]
	for f in loc_files:
    	    setname = f.split('/')[-1].split('_loc')[0]
	    if setname not in ignore:
                outname='HHpreselection'+year+'_'+setname+'_'+tagger+'.root'
                job_string=base_string.replace("TEMPYEAR",year).replace('TEMPTAGGER',tagger).replace('TEMPNAME',outname).replace('TEMPFILE','NanoAOD'+year+'_lists/'+setname+'_loc.txt').replace('TEMPCONFIG','hh'+year+'_config.json')
	        outfile.write(job_string+'\n')

outfile.close()
