import subprocess
import sys
import pprint 
pp = pprint.PrettyPrinter(indent=4)

year = sys.argv[1]

candidate_files = subprocess.check_output('ls -1 HHpreselection'+year+'_*.root',shell=True).split('\n')

to_remove = [i for i,x in enumerate(candidate_files) if x == '']

for r in to_remove:
    candidate_files.pop(r)

done_files = []

# Just move files that don't need to be hadded
for f in candidate_files:
    if 'job' not in f:
        print 'Executing: mv '+f+'rootfilesXSEC1pb/'
        subprocess.call(['mv '+f+' rootfilesXSEC1pb/'],shell=True)
        done_files.append(f)
        
# Get a dictionary with all processes that need to be hadded
proc_dict = {}
for f in candidate_files:
    if (f not in done_files) and ('_job1of' in f):

        proc = f.split('_')[1]
        #dak8_string = f.split('_')[3]

        if len(f.split('_')) > 5:   # has mod
            mod_string = '_'+f.split('_')[3]+'_'+f.split('_')[4]
            tag_string = '_'+f.split('_')[5]
            reg_string = f.split('_')[6].split('.')[0]
        else:   # doesn't have mod
            mod_string = ''
            tag_string = '_'+f.split('_')[3]
            reg_string = f.split('_')[4].split('.')[0]
        
        
        key_name = proc+'_'+tag_string+'_'+reg_string+'_'+mod_string
        proc_dict[key_name] = {
                                'haddname':f.replace('_'+f.split('_')[2],''),
                                'files_to_add':f.replace('_job1of','_job*of')
                            }

pp.pprint(proc_dict)

for f in proc_dict.keys():
    print 'Executing: rm rootfilesXSEC1pb/'+proc_dict[f]['haddname']
    subprocess.call(['rm rootfilesXSEC1pb/'+proc_dict[f]['haddname']],shell=True)
    print 'Executing: hadd rootfilesXSEC1pb/'+proc_dict[f]['haddname']+' '+proc_dict[f]['files_to_add']
    subprocess.call(['hadd rootfilesXSEC1pb/'+proc_dict[f]['haddname']+' '+proc_dict[f]['files_to_add']], shell=True)
    print 'Executing: rm '+proc_dict[f]['files_to_add']
    subprocess.call(['rm '+proc_dict[f]['files_to_add']],shell=True)
