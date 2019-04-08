import sys
files = sys.argv[1:]

writeout = False
if '--write' in files:
    writeout = True

jobsToReRun = []
log = []
for f in files:
    if f == '--write':
        continue
    thisF = open(f,'r')
    hasError = False
    for line in thisF:
        if 'error' in line.lower():
            if 'SetBranchStatus' not in line:
                hasError = True
                print f+': '+line
                log.append(f+': '+line)

    if hasError:
        stdoutFile = open(f.replace('notneeded/','').replace('.stderr','.stdout'),'r')
        for l in stdoutFile:
            if 'make_preselection.py ' in l:
                jobsToReRun.append(l.replace('make_preselection.py ',''))
                break 

with open('jobsToReRun.txt', 'w') as f:
    for job in jobsToReRun:
        print job
        if writeout:
            f.write("%s" % job)

with open('jobsToReRun.log', 'w') as f:
    for job in log:
        f.write("%s" % job)     
