import subprocess

commands = []

base_string = '-s TEMPSET -j IJOB -n NJOB -y TEMPYEAR'#'python CondorHelper.py -r run_bstar.sh -a "-s TEMPSET -j IJOB -n NJOB -y TEMPYEAR"'

for year in ['16','17','18']:
    year_string = base_string.replace("TEMPYEAR",year)

    # QCD
    if year == '16':
        qcd_dict = {'QCDHT700':18,'QCDHT1000':7,'QCDHT1500':6,'QCDHT2000':3,'QCDHT1000ext':15,'QCDHT1500ext':11,'QCDHT2000ext':7}
    elif year == '17':
        qcd_dict = {'QCDHT700':39,'QCDHT1000':15,'QCDHT1500':10,'QCDHT2000':7}
    elif year == '18':
        qcd_dict = {'QCDHT700':273,'QCDHT1000':88,'QCDHT1500':67,'QCDHT2000':40}
    for qcd in qcd_dict.keys():
        qcd_string = year_string.replace('TEMPSET',qcd).replace('NJOB',str(qcd_dict[qcd]))
        for i in range(1,qcd_dict[qcd]+1):
            qcd_job_string = qcd_string.replace('IJOB',str(i))
            commands.append(qcd_job_string)

    # TTbar
    if year == '16':
        ttbar_jobs = 75
    elif year == '17':
        ttbar_jobs = 30
    elif year == '18':
        ttbar_jobs = 133
    ttbar_string = year_string.replace('TEMPSET','ttbar').replace("NJOB",str(ttbar_jobs))
    for i in range(1,ttbar_jobs+1):
        ttbar_job_string = ttbar_string.replace('IJOB',str(i))
        commands.append(ttbar_job_string)

    # ST
    if year == '16':
        st_dict = {'singletop_t':59,'singletop_tB':34,'singletop_tW':3,'singletop_tWB':2}
    elif year == '17':
        st_dict = {'singletop_t':6,'singletop_tB':11,'singletop_tW':13,'singletop_tWB':9}
    elif year == '18':
        st_dict = {'singletop_tW':8,'singletop_tWB':7}
    for st in st_dict.keys():
        st_string = year_string.replace('TEMPSET',st).replace('NJOB',str(st_dict[st]))
        for i in range(1,st_dict[st]+1):
            st_job_string = st_string.replace('IJOB',str(i))
            commands.append(st_job_string)

    # Signal
    if year == '16':
        for hand in ['LH','RH']:
            for mass in range(1200,3200,200):
                sig_name = 'signal'+hand+str(mass)
                signal_string = year_string.replace('TEMPSET',sig_name).replace('NJOB','1').replace('IJOB','1')
                commands.append(signal_string)

    # Data
    if year == '16':
        data_dict = {'dataB2':88,'dataC':31,'dataD':43,'dataE':50,'dataF':31,'dataG':89,'dataH':77}#,'dataH2':1}
        # data_string = year_string.replace('TEMPSET','data').replace('NJOB','301')
        # for i in range(1,302):
        #     data_job_string = data_string.replace('IJOB',str(i))
        #     commands.append(data_job_string)
    elif year == '17':
        data_dict = {'dataB':41,'dataC':57,'dataD':26,'dataE':52,'dataF':67}
    elif year == '18':
        data_dict = {'dataA':135,'dataB':93,'dataC':72, 'dataD':204}
    for data in data_dict.keys():
        data_job_string = year_string.replace('TEMPSET',data).replace('NJOB',str(data_dict[data]))
        for i in range(1,data_dict[data]+1):
            data_subjob_string = data_job_string.replace('IJOB',str(i))
            commands.append(data_subjob_string)


outfile = open('../args/bstar_nano_args.txt','w')

for s in commands:
    outfile.write(s+'\n')

outfile.close()
