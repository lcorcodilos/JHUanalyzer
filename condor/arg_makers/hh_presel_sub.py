import subprocess

commands = []

base_string = '-s TEMPSET -r TEMPREG -n NJOB -j IJOB -y TEMPYEAR -b TEMPDOUBLEB'# -j -r -a -b

for year in ['18']:
    for reg in ['default']:
        for doubleb in ['btagHbb','deepTagMD_HbbvsQCD','deepTagMD_ZHbbvsQCD','btagDDBvL']:
            year_string = base_string.replace("TEMPYEAR",year).replace('TEMPREG',reg).replace('TEMPDOUBLEB',doubleb)
            # QCD
            qcd_dict = {'QCDHT700':57,'QCDHT1000':21,'QCDHT1500':16,'QCDHT2000':8}
            for qcd in qcd_dict.keys():
                qcd_string = year_string.replace('TEMPSET',qcd).replace('NJOB',str(qcd_dict[qcd]))
                for i in range(1,qcd_dict[qcd]+1):
                    qcd_job_string = qcd_string.replace('IJOB',str(i))
                    commands.append(qcd_job_string)

            # TTbar
            ttbar_dict = {'ttbar': 16,'ttbar-semilep': 8}
            for ttbartype in ttbar_dict.keys():
                ttbar_jobs = ttbar_dict[ttbartype]
                ttbar_string = year_string.replace('TEMPSET',ttbartype).replace("NJOB",str(ttbar_jobs))
                for i in range(1,ttbar_jobs+1):
                    commands.append(ttbar_string.replace('IJOB',str(i)))
                for k in [' up',' down']:
                    for j in [' -J', ' -R', ' -a', ' -b']:
                        for i in range(1,ttbar_jobs+1):
                            ttbar_job_string = ttbar_string.replace('IJOB',str(i))
                            ttbar_job_string+=j+k
                            commands.append(ttbar_job_string)


            # Signal
            if year == '18':
                siglist = [
                    #'RadNar_1000',
                    #'RadNar_1500',
                    #'RadNar_2000',
                    #'RadNar_2500',
                    #'RadNar_3000',
                    #'RadWid05_1000',
                    #'RadWid05_1500',
                    #'RadWid05_2000',
                    #'RadWid05_2400',
                    #'RadWid05_3000',
                    #'RadWid10_1500',
                    #'RadWid10_2000',
                    #'RadWid10_2400',
                    #'RadWid10_3000',
                    'GravNar-1000',
                    'GravNar-1500',
                    'GravNar-2000',
                    'GravNar-2500',
                    'GravNar-3000',
                    #'GravWid05_1000',
                    #'GravWid05_1500',
                    #'GravWid05_2000',
                    #'GravWid05_2400',
                    #'GravWid05_3000',
                    #'GravWid10_1000',
                    #'GravWid10_1500',
                    #'GravWid10_2000',
                    #'GravWid10_2400',
                    #'GravWid10_3000'
                ]
                for sig_name in siglist:
                    commands.append(year_string.replace('TEMPSET',sig_name).replace('NJOB','1').replace('IJOB','1'))
                    for k in [' up',' down']:
                        for j in [' -J', ' -R', ' -a', ' -b']:
                            signal_string = year_string.replace('TEMPSET',sig_name).replace('NJOB','1').replace('IJOB','1')
                            signal_string+=j+k
                            commands.append(signal_string)

            # Data
            data_dict = {'dataA':45,'dataB':20,'dataC':20,'dataD':100}
            for data in data_dict.keys():
                data_string = year_string.replace('TEMPSET',data).replace('NJOB',str(data_dict[data]))
                for i in range(1,data_dict[data]+1):
                    data_job_string = data_string.replace('IJOB',str(i))
                    commands.append(data_job_string)

outfile = open('../args/hh_presel_args.txt','w')

for s in commands:
    outfile.write(s+'\n')

outfile.close()
