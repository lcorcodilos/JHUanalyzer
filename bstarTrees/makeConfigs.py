import subprocess
import pickle
from optparse import OptionParser


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('--submit', action="store_true",
                      default   =   False,
                      dest      =   'submit',
                      help      =   'Runs crab on everything')
    parser.add_option('--status', action="store_true",
                      default   =   False,
                      dest      =   'status',
                      help      =   'Runs crab status for everything')
    parser.add_option('--killall', action="store_true",
                      default   =   False,
                      dest      =   'killall',
                      help      =   'Kills every job')
    parser.add_option('--hadd', action="store_true",
                      default   =   False,
                      dest      =   'hadd',
                      help      =   'Runs haddnano.py on everything')
    parser.add_option('-v', '--version', metavar='F', type='string', action='store',
                    default   =   '',
                    dest      =   'version',
                    help      =   'Version of form v#p$')

    (options, args) = parser.parse_args()

    if options.version == '':
        print 'Version number must be specific by option `-v`'
        quit()

    input_subs = pickle.load(open('JHitos16Info_'+options.version+'.p','rb'))
    
    if options.hadd:
        myEosDir = '/eos/uscms/store/user/lcorcodi/bstar_nano/'
        result_locations = {}

        commands = []
        for set_name in input_subs.keys():
            if 'data' in set_name:
                continue

            firstDir = input_subs[set_name]['das'].split('/')[1]+'/'
            secondDir = 'JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1/' # input_subs[set_name]['requestName']+'/'

            # Pickle dictionary with set names
            result_locations[set_name] = myEosDir+'results/'+set_name+'_bstar.root'

            n_subdirs = subprocess.check_output(["ls -l "+myEosDir+firstDir+secondDir+'| grep -c ^d'],shell=True).rstrip()
            if n_subdirs > 1:
                print "WARNING!!! Crab jobs for " + set_name+ " have been run more than once. Skipping to avoid double couting!"
                continue
            elif n_subdirs == 0:
                print "WARNING!!! The directory for " + set_name+ " is empty. Are you sure you ran crab jobs? Skipping..."
                continue

            commands.append('python ../scripts/haddnano.py '+myEosDir+'results/'+set_name+'_bstar.root '+myEosDir+firstDir+secondDir+'*/*/*.root')

        pickle.dump(result_locations,open('bstarLocations_'+options.version+'.p','wb'))

        for s in commands:
            print 'Executing ' + s
            raw_input('Press enter to execute')
            subprocess.call([s],shell=True)

    elif options.submit:
        commands = []
        for set_name in input_subs.keys():
            if 'data' in set_name:
               continue

            commands.append("sed 's$TEMPNAME$"+input_subs[set_name]['requestName']+"$g' postprocessor_template.py > postprocessor_"+set_name+".py")
            commands.append("sed -i 's$TEMPSHORT$"+set_name+"$g' postprocessor_"+set_name+".py")
            commands.append("sed -i 's$TEMPINPUT$"+input_subs[set_name]['das']+"$g' postprocessor_"+set_name+".py")
            commands.append("crab submit -c postprocessor_"+set_name+".py")
            commands.append("mv postprocessor_"+set_name+".py SubmittedConfigs")

        for s in commands:
            print 'Executing ' + s
            #subprocess.call([s],shell=True)
