import subprocess, sys, glob, os
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-r', '--regions', metavar='FILE', type='string', action='store',
                default   =   'default',
                dest      =   'regions',
                help      =   'Regions to consider (comma separated list). Default is signal region ("default")')
parser.add_option('-y', '--years', metavar='FILE', type='string', action='store',
                default   =   '16,17,18',
                dest      =   'years',
                help      =   'Years to consider (comma separated list). Default is 16,17,18.')
parser.add_option('-t', '--taggers', metavar='FILE', type='string', action='store',
                default   =   'btagHbb,deepTagMD_HbbvsQCD,deepTagMD_ZHbbvsQCD,btagDDBvL',
                dest      =   'taggers',
                help      =   'Taggers to consider (comma separated list) as named in the NanoAOD. Default is btagHbb,deepTagMD_HbbvsQCD,deepTagMD_ZHbbvsQCD,btagDDBvL.')
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
regions = options.regions.split(',')
years = options.years.split(',')
taggers = options.taggers.split(',')
ignore = options.ignoreset.split(',')
name_string = '_'+options.name if options.name != '' else ''

# Initialize output file
outfile = open('../args/hh_presel'+name_string+'_args.txt','w')

base_string = '-s TEMPSET -r TEMPREG -n NJOB -j IJOB -y TEMPYEAR -d TEMPTAGGER'

for year in years:
    for reg in regions:
        for tagger in taggers:
            job_base_string = base_string.replace("TEMPYEAR",year).replace('TEMPREG',reg).replace('TEMPTAGGER',tagger)

            for loc_file in glob.glob('../../hhTrees/NanoAOD'+year+'_lists/*_loc.txt'):
                setname = loc_file.split('/')[-1].split('_loc')[0]

                if setname not in ignore:
                    # Get njobs by counting how many GB in each file (1 job if file size < 1 GB)
                    bitsize = os.path.getsize('/eos/uscms/store/user/dbrehm/data18andTTbarSignalMC/rootfiles/'+setname+'_hh'+year+'.root')
                    if bitsize/float(10**9) < 1:  set_njobs = 1
                    else: set_njobs = int(round(bitsize/float(10**9)))

                    njob_string = job_base_string.replace('TEMPSET',setname).replace('NJOB',str(set_njobs))               
                    for i in range(1,set_njobs+1):
                        job_string = njob_string.replace('IJOB',str(i))
                        outfile.write(job_string+'\n')

                        # Will eventually use this but not setup in make_preselection.py yet
                        # if 'data' not in setname and 'QCD' not in setname:
                        #     for j in [' -J', ' -R', ' -a', ' -b']:
                        #         for v in [' up',' down']:
                        #             jec_job_string = job_string + j + v


outfile.close()
