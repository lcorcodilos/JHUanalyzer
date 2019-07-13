import subprocess, sys, glob
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-i', '--ignore', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'ignore',
                help      =   'Comma separated list of what to ignore when building argument list')
parser.add_option('-n', '--name', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'name',
                help      =   'A custom name for this argument list (hh_nano_<name>_args.txt)')

(options, args) = parser.parse_args()

# Any arguments in command line are used to ignore certain sets or years when building the argument list
ignore = options.ignore.split(',')
name_string = '_'+options.name if options.name != '' else ''

# Initialize output file
outfile = open('../args/hh_nano'+name_string'_args.txt','w')

base_string = '-s TEMPSET -j IJOB -n NJOB -y TEMPYEAR'#'python CondorHelper.py -r run_bstar.sh -a "-s TEMPSET -j IJOB -n NJOB -y TEMPYEAR"'

for year in ['16','17','18'] and year not in ignore:
    year_string = base_string.replace("TEMPYEAR",year)

    for file in glob.glob('../../hhTrees/NanoAOD'+year+'_lists/*_loc.txt'):
        setname = file.split('/')[-1].split('_loc')[0]
        if setname not in ignore:
            set_njobs = len(open(file,'r').readlines())
            job_base_string = year_string.replace('TEMPSET',setname).replace('NJOB',str(set_njobs))
            for i in range(1,set_njobs+1):
                job_string = job_base_string.replace('IJOB',str(i))
                outfile.write(job_string+'\n')

outfile.close()
