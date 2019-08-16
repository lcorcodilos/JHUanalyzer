import sys, subprocess, os, fnmatch
import os.path

setname = sys.argv[1]
year = sys.argv[2]

execute = []
eosrmer = open('removers/eosRmer_'+setname+year+'.csh','w')

for filename in os.listdir('/eos/uscms/store/user/mbrugman/TriBoson_nano'):
    if fnmatch.fnmatch(filename,'TriBosonTrees'+year+'_'+setname+'_1-*.root'):
        njobs = int(filename.split(setname+'_1-')[1].rstrip('.root'))
        sjobs = str(njobs)

eosdir = 'root://cmseos.fnal.gov//store/user/mbrugman/TriBoson_nano/'
threeDayLifetime = '/uscmst1b_scratch/lpc1/3DayLifetime/mbrugman/'

# Segment so never hadd more than 100 files at once
if njobs > 100:
    if njobs%100 != 0:
        segments = int(njobs/100) + 1
    else:
        segments = int(njobs/100)

    segment_walls = []
    for s in range(segments):
        lower_wall = s*100+1
        upper_wall = min((s+1)*100,njobs)+1

        list_of_files = ''
        # Copy all files in the segment locally
        for i in range(lower_wall, upper_wall):
            list_of_files+= ' '+eosdir+'TriBosonTrees'+year+'_'+setname+'_'+str(i)+'-'+sjobs+'.root'
            eosrmer.write('eosrm '+eosdir.replace('root://cmseos.fnal.gov/','')+'TriBosonTrees'+year+'_'+setname+'_'+str(i)+'-'+sjobs+'.root\n')

        # Hadd the jobs into a segment
        execute.append('python haddnano.py '+threeDayLifetime+'temp_wall_'+str(lower_wall)+'-'+str(upper_wall)+'.root '+list_of_files)


    # Hadd the segments
    execute.append('python haddnano.py '+threeDayLifetime+setname+'_WWW'+year+'.root '+threeDayLifetime+'temp_wall_*.root')
    # Remove the segments
    execute.append('rm '+threeDayLifetime+'temp_wall_*.root')

    # Copy to eos and delete locally
    execute.append('xrdcp -f '+threeDayLifetime+setname+'_WWW'+year+'.root root://cmseos.fnal.gov//store/user/mbrugman/TriBoson_nano/rootfiles/')
    execute.append('rm '+threeDayLifetime+setname+'_WWW'+year+'.root')

else:
    list_of_files = ''
    for i in range(1,njobs+1):
        list_of_files+= ' '+eosdir+'TriBosonTrees'+year+'_'+setname+'_'+str(i)+'-'+sjobs+'.root'
        eosrmer.write('eosrm ' +eosdir.replace('root://cmseos.fnal.gov/','')+'TriBosonTrees'+year+'_'+setname+'_'+str(i)+'-'+sjobs+'.root\n')

    execute.append('python haddnano.py '+setname+'_WWW'+year+'.root '+list_of_files)

    execute.append('xrdcp -f '+setname+'_WWW'+year+'.root root://cmseos.fnal.gov//store/user/mbrugman/TriBoson_nano/rootfiles/'+setname+'_WWW'+year+'.root')
    execute.append('rm '+setname+'_WWW'+year+'.root')

for s in execute:
    print "Executing: %s" %s 
    subprocess.call([s],shell=True)
