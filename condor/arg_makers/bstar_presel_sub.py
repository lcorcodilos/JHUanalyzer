import subprocess

commands = []

base_string = '-s TEMPSET -r TEMPREG -d TEMPDEEP -t TEMPTAU32 -j NJOB -n IJOB -y TEMPYEAR'# -j -r -a -b

for year in ['16','17','18']:
    for deep in ['off']:
        for tau32 in ['loose','medium']:
            for reg in ['ttbar','default','sideband']:
                year_string = base_string.replace("TEMPYEAR",year).replace('TEMPREG',reg).replace('TEMPDEEP',deep).replace('TEMPTAU32',tau32)
                # QCD
                if year == '16':
                    qcd_dict = {'QCDHT700':1,'QCDHT1000':5,'QCDHT1500':1,'QCDHT2000':1,'QCDHT1000ext':5,'QCDHT1500ext':1,'QCDHT2000ext':1}
                elif year == '17' or year == '18':
                    qcd_dict = {'QCDHT700':1,'QCDHT1000':1,'QCDHT1500':1,'QCDHT2000':1}
                for qcd in qcd_dict.keys():
                    qcd_string = year_string.replace('TEMPSET',qcd).replace('NJOB',str(qcd_dict[qcd]))
                    for i in range(1,qcd_dict[qcd]+1):
                        qcd_job_string = qcd_string.replace('IJOB',str(i))
                        commands.append(qcd_job_string)

                # TTbar
                ttbar_jobs = 1
                ttbar_string = year_string.replace('TEMPSET','ttbar').replace("NJOB",str(ttbar_jobs))
                for i in range(1,ttbar_jobs+1):
                    commands.append(ttbar_string.replace('IJOB',str(i)))
                for k in [' up',' down']:
                    for j in [' -J', ' -R', ' -a', ' -b']:
                        for i in range(1,ttbar_jobs+1):
                            ttbar_job_string = ttbar_string.replace('IJOB',str(i))
                            ttbar_job_string+=j+k
                            commands.append(ttbar_job_string)

                # ST
                st_dict = {'singletop_t':1,'singletop_tB':1,'singletop_tW':1,'singletop_tWB':1}
                for st in st_dict.keys():
                    if year == '18' and (st == 'singletop_t' or st == 'singletop_tB'):
                        continue
                    st_string = year_string.replace('TEMPSET',st).replace('NJOB',str(st_dict[st]))
                    for i in range(1,st_dict[st]+1):
                        commands.append(st_string.replace('IJOB',str(i)))
                    
                    for k in [' up',' down']:
                        for j in [' -J', ' -R', ' -a', ' -b']:
                            for i in range(1,st_dict[st]+1):
                                st_job_string = st_string.replace('IJOB',str(i))
                                st_job_string+=j+k
                                commands.append(st_job_string)

                # Signal
                if year == '16':
                    for hand in ['LH','RH']:
                        for mass in range(1200,3200,200):
                            sig_name = 'signal'+hand+str(mass)
                            commands.append(year_string.replace('TEMPSET',sig_name).replace('NJOB','1').replace('IJOB','1'))
                            for k in [' up',' down']:
                                for j in [' -J', ' -R', ' -a', ' -b']:
                                    signal_string = year_string.replace('TEMPSET',sig_name).replace('NJOB','1').replace('IJOB','1')
                                    signal_string+=j+k
                                    commands.append(signal_string)

                # Data
                # if year == '16':
                #     data_dict = {'dataB':1,'dataB2':100,'dataC':25,'dataD':50,'dataE':50,'dataF':50,'dataG':50,'dataH':50,'dataH2':1}
                # elif year == '17':
                #     data_dict = {'dataA':50,'dataB':50,'dataC':50,'dataD':50,'dataE':50,'dataF':50}

                # for data in data_dict.keys():

                data_string = year_string.replace('TEMPSET','data').replace('NJOB','20')
                for i in range(1,21):
                    data_job_string = data_string.replace('IJOB',str(i))
                    commands.append(data_job_string)

outfile = open('../args/bstar_presel_args.txt','w')

for s in commands:
    outfile.write(s+'\n')

outfile.close()
