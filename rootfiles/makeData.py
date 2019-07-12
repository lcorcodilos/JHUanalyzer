import subprocess

datas = ['dataA','dataB','dataC1','dataC2','dataD']

for y in ['18']:
    for r in ['default']:
	for doubleb in ['doubleB','dak8MDHbb','dak8MDZHbb','DeepDB']:
       	    new_file = 'HHpreselection'+y+'_data_'+doubleb+'_'+r+'.root'
            hadd_string = 'hadd '+new_file
            print 'Executing: rm ' + new_file
            subprocess.call(['rm '+new_file],shell=True) 
            for d in datas:
                hadd_string += ' HHpreselection'+y+'_'+d+'_'+doubleb+'_'+r+'.root'
                
            print 'Executing: ' + hadd_string
            subprocess.call([hadd_string],shell=True)
