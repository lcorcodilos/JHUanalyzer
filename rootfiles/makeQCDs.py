import subprocess
for y in ['18']:
    for r in ['default']:
	for doubleb in ['doubleB','dak8MDHbb','dak8MDZHbb']:
            new_file = 'HHpreselection'+y+'_QCD_'+doubleb+'_'+r+'.root'
            hadd_string = 'hadd '+new_file
            print 'Executing: rm ' + new_file
            subprocess.call(['rm '+new_file],shell=True)
            htlist = ['700','1000','1500','2000']
            for h in htlist:
                hadd_string += ' HHpreselection'+y+'_QCDHT'+h+'_'+doubleb+'_'+r+'.root'
                
            print 'Executing: ' + hadd_string
            subprocess.call([hadd_string],shell=True)
