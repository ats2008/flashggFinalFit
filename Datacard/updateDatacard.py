import json,sys,os,argparse

lumi={'2018':58,'2017':41.5,'2016':36.3 , '2016PreVFP':19.5,'2016PostVFP':16.8,'run2':137.61}
lumiMap={ky : f"{lumi[ky]*1000:1f}" for ky in lumi }

doKappaLambda=False

def getProcName(proc):
    if proc=='data_obs':
        return proc
    if doKappaLambda:
        if 'ggHHH' in proc:
            return 'c3_0_d4_0'
    if ('c3' in proc) and ('d4' in proc):
       return '_'.join(proc.split('_')[:4])   
    return proc.split('_')[0]

def getAllProcs(dataS):
    procs=set()
    for ch in dataS:
        for proc in dataS[ch]:
            procs.add(getProcName(proc))
    return list(procs)

def getAllChannels(dataS):   
    return list(dataS.keys())

def getAllNuisanceParams(dataS,systExtra):
    s=[]
    for ch in dataS:
        for proc in dataS[ch]:
            return  list(dataS[ch][proc]['syst']) + list(systExtra)
    return []
def setRate(data,yr,cat,proc,rate):
    for ch in data:
        for proc_ in data[ch]:
            if proc_!=proc:
                continue
            if data[ch][proc]['year']!=yr:
                continue
            if data[ch][proc]['cat']!=cat:
                continue
            print(f"Updating {ch}/{proc} rate {data[ch][proc]['rate']} -> {rate}")
            data[ch][proc]['rate']=str(rate)

def printDset(dataS):
    for ch in dataS:
        print("Channel : ",ch)
        for proc in dataS[ch]:
            ostr="proc : "+proc+ " id : "+str(dataS[ch][proc]['id'])+" | rate "+dataS[ch][proc]['rate']
            if 'cat' in dataS[ch][proc]:
                ostr="cat : "+ dataS[ch][proc]['cat'] + ' | ' +ostr
            if 'year' in dataS[ch][proc]:
                ostr="Year : "+ dataS[ch][proc]['year'] + ' | ' +ostr
            if 'channel' in dataS[ch][proc]:
                ostr="channel : "+ dataS[ch][proc]['channel'] + ' | ' +ostr
                
            print(f"\t{ostr}")
def printShapeData(shapeData):
    for proc in shapeData:
        for ch in shapeData[proc]:
            print(proc,ch,shapeData[proc][ch])

def printObeservations(observationData):
    for ch in observationData:
        print(ch,"  :  ",observationData[ch])

def standardizeData(dataS,shapeData,observationData):
    dataS_updated={}
    shapeData_updated={}
    
    all_procs=getAllProcs(dataS)
    bkg_procs=[i for i in all_procs  if 'ggHHH' not in i ]
    procid_map = { proc : i+1  for i,proc in enumerate(bkg_procs) }
    procid_map['ggHHH'] = 0
    
    for ch in dataS:
        dataS_updated[ch]={}
        for proc in dataS[ch]:
            p_upd=getProcName(proc)
            dataS_updated[ch][p_upd]=dataS[ch][proc]
            dataS_updated[ch][p_upd]['_original_procname']=proc
            dataS_updated[ch][p_upd]['_original_procid']=dataS[ch][proc]['id']
            dataS_updated[ch][p_upd]['_original_rate']=dataS[ch][proc]['rate']
            dataS_updated[ch][p_upd]['id']=procid_map[p_upd]
            dataS_updated[ch][p_upd]['rate']=dataS[ch][proc]['rate']
            dataS_updated[ch][p_upd]['channel']=ch.split('_')[0]
            if len(ch.split('_'))>1:
                dataS_updated[ch][p_upd]['cat']=ch.split('_')[1]
            else:
                dataS_updated[ch][p_upd]['cat']=ch
            if len(ch.split('_'))>2:
                dataS_updated[ch][p_upd]['year']=ch.split('_')[2]
            else:
                dataS_updated[ch][p_upd]['year']=ch
    for proc in shapeData:
        p_upd=getProcName(proc)
        if p_upd not in shapeData_updated:
            shapeData_updated[p_upd]={}
        for ch in shapeData[proc]:
            shapeData_updated[p_upd][ch]=shapeData[proc][ch]

    return dataS_updated,shapeData_updated,observationData

def mergeChannels(dataS,shapeData,observationData):
    dataS_updated={}
    shapeData_updated={}
    observationData_updated={}

    all_procs=getAllProcs(dataS)
    procid_map = { }
    signalIndex=0
    backgroundIndex=1

    for ch in dataS:
        channel_id,cat,yr = ch.split('_')

        if cat not in dataS_updated:
            dataS_updated[cat]={}

        for proc in dataS[ch]:
            p_upd=getProcName(proc)
            #p_upd=p_upd+f'_{yr}_{channel_id}'
            p_upd=p_upd+f'_{yr}'
            if p_upd in dataS_updated[cat]:
                print("PROBLEM !! things are not clean :) ! ",p_upd," Already there in ",cat,"   [ ",proc,"]  ")
                exit(1)
            if p_upd not in procid_map :
                if 'ggHHH' in p_upd:
                    procid_map[p_upd]=signalIndex
                    signalIndex-=1
                else:
                    procid_map[p_upd]=backgroundIndex
                    backgroundIndex+=1

            dataS_updated[cat][p_upd]=dataS[ch][proc]
            dataS_updated[cat][p_upd]['_original_procname']=proc
            dataS_updated[cat][p_upd]['_original_procid']=dataS[ch][proc]['id']
            dataS_updated[cat][p_upd]['_original_rate']=dataS[ch][proc]['rate']
            dataS_updated[cat][p_upd]['id']=procid_map[p_upd]
            dataS_updated[cat][p_upd]['rate']=dataS[ch][proc]['rate']
            dataS_updated[cat][p_upd]['channel']=ch.split('_')[0]
            dataS_updated[cat][p_upd]['cat']=ch.split('_')[1]
            dataS_updated[cat][p_upd]['year']=ch.split('_')[2]
    
    for proc in shapeData:
        for ch in shapeData[proc]:
            channel_id,cat,yr = ch.split('_')
            p_upd=getProcName(proc)
            if p_upd!='data_obs':
                #p_upd=p_upd+f'_{yr}_{channel_id}'
                p_upd=p_upd+f'_{yr}'
                if p_upd in shapeData_updated:
                    if cat in shapeData_updated[p_upd]:
                        print("PROBLEM !! things are not clean :) ! ",p_upd," Already there in shapeData_updated ","   [ ",proc,ch,"]  ")
                        exit(1)
            if p_upd not in shapeData_updated:
                shapeData_updated[p_upd]={}
            shapeData_updated[p_upd][cat]=shapeData[proc][ch]
    
    for ch in observationData:
        cat=ch.split('_')[1]
        observationData_updated[cat]=observationData[ch]

    return dataS_updated,shapeData_updated,observationData_updated


def removeColumn(data,shapeData,proc,isSig=False):
    sucessS=False
    sucessD=False
    if proc in shapeData:
        shapeData.pop(proc)
        sucessS=True
        print(f"  proc {proc} removed from shapes")
    for ch in data:
        pid=1e5
        sucessD=False
        if proc in data[ch]:
            pid=data[ch][proc]['id']
            data[ch].pop(proc)
            sucessD=True
            for proc_ in data[ch]:
                if data[ch][proc_]['id'] > pid :
                    data[ch][proc_]['id'] =  data[ch][proc_]['id'] - 1
            print(f"  proc {proc} removed from {ch}")

    if sucessD and sucessS:
        print(f"{proc} is sucessfully removed !")
    else:
        if not sucessD:
            print(f"{proc} failed to be removed from yield data")
        if not sucessS:
            print(f"{proc} failed to be removed from shapes")

def duplicateColumn(data,shapeData,src_ch,src_proc,dst_ch,dst_proc,lumi=None,isSig=False):
    for ch in data:
        if ch!=src_ch:
            continue
        
        pid=0
        for proc_ in data[ch]:
            if isSig and ('ggHHH' not in proc_):
                continue
            pid=max(abs(data[ch][proc_]['id']),pid)
        pid+=1
        if isSig:
            pid*=-1
        if dst_ch in data:
            if dst_proc in data[dst_ch]:
                pid=data[dst_ch][dst_proc]['id']
        for proc in data[ch]:
            if proc!=src_proc:
                continue
            data[dst_ch][dst_proc]=dict(data[ch][proc])
            if lumi:
                print(f"Duplicating {ch}/{proc}/{data[ch][proc]['id']} --> {dst_ch}/{dst_proc}/{pid} ! rate set as {lumi}")
            else:
                print(f"Duplicating {ch}/{proc}/{data[ch][proc]['id']} --> {dst_ch}/{dst_proc}/{pid} ! ")
            data[dst_ch][dst_proc]['id']=pid
            if lumi:
                data[dst_ch][dst_proc]['rate']=str(lumi)
            if dst_proc not in shapeData:
                shapeData[dst_proc]={}
            shapeData[dst_proc][dst_ch]=shapeData[src_proc][src_ch]
            return


def extractData(fname):
    f=open(fname)
    txt=f.readlines()
    f.close()
    linesOfInterest={'shapes':[],'systs':[]}
    bCount=0
    pCount=0
    gotPDFIndex=False
    gotRate=False
    for l in txt:
        if l.startswith('pdfindex'):
            gotPDFIndex=True
            continue
        if l.startswith('---'):
            continue
        if l.startswith('bin'):
            linesOfInterest[f'bin_{bCount}'] = l[:-1]
            bCount+=1
        if l.startswith('process'):
            linesOfInterest[f'process_{pCount}'] = l[:-1]
            pCount+=1
        if l.startswith('rate'):
            linesOfInterest[f'rate'] = l[:-1]
            gotRate=True
            continue
            
        if l.startswith('observation'):
            linesOfInterest['observation']=l[:-1]
        if l.startswith('shapes'):
            linesOfInterest['shapes'].append(l[:-1])
        if gotRate and  not gotPDFIndex:
            linesOfInterest['systs'].append(l[:-1])

    bin1    =linesOfInterest['bin_1'].split()[1:]
    process0=linesOfInterest['process_0'].split()[1:]
    process1=linesOfInterest['process_1'].split()[1:]
    rate=linesOfInterest['rate'].split()[1:]
    
    N=len(bin1)
    
    systData={}
    systExtra=[]
    for l in linesOfInterest['systs']:
        items=l.split()
        if len(items) <1:
            print("",l,items)
            continue
        systData[items[0]]={'type':items[1],'data':items[2:]}
        if len(items[2:])!=N:
            systExtra.append(l)
    dataS={}
    for i in range(N):
        channel=bin1[i]
        proc=process0[i]
        procID=process1[i]
        rt=rate[i]
        if channel not in dataS:
            dataS[channel]={}
        dataS[channel][proc]={'id' : procID ,'rate' : rt,'syst' : {},'syst_type':{}}
        for syst in systData:
        #    if ( systData[syst]['type']!='param' ):
            if len(systData[syst]['data']) ==N:
                dataS[channel][proc]['syst'][syst]=systData[syst]['data'][i]
                dataS[channel][proc]['syst_type'][syst]=systData[syst]['type']
    shapeData={}
    for l in linesOfInterest['shapes']:
        items=l.split()[1:]
        proc=items[0]
        ch=items[1]
        dest_str=' '.join(items[2:])
        if proc not in shapeData :
            shapeData[proc]={}
        shapeData[proc][ch]=dest_str
        
    
    observationData={}
    
    bin0    =linesOfInterest['bin_0'].split()[1:]
    obs=linesOfInterest['observation'].split()[1:]
    N=len(bin0)
    for i in range(N):
        observationData[bin0[i]] = obs[i]
    
    return txt,dataS,shapeData,observationData,systExtra

def getHeaderStringBlock(dataS,systExtra):
    ostr="imax @@IMAX number of bins\njmax @@JMAX number of processes minus 1\nkmax @@KMAX number of nuisance parameters"
    ostr=ostr.replace("@@IMAX",f"{len(getAllChannels(dataS))}")
    
    procMap=dict()
    for ch in dataS:
        for proc in dataS[ch]:
            if proc not in procMap:
                procMap[proc]=dataS[ch][proc]['id']
            else:
                if procMap[proc]!=dataS[ch][proc]['id']:
                    print(f"ERROR ! duplicate proc ids found !! for {ch}/{proc}")
    
    procList=[i[0] for i in sorted(procMap.items(),key= lambda x : x[1])]
 
    ostr=ostr.replace("@@JMAX",f"{len(procList)-1}")
    ostr=ostr.replace("@@KMAX",f"{len(getAllNuisanceParams(dataS,systExtra))}")
    return ostr

def getShapeStringBlock(shapeData):
    nProcLenMax=0
    nChLenMax =0
    for proc in shapeData:
        nProcLenMax=max(nProcLenMax,len(proc))
        for ch in shapeData[proc]:
            nChLenMax=max(nChLenMax,len(ch))
    nProcLenMax+=3
    nChLenMax+=3
    
    ostr_shapeBlock=""
    k=0
    for proc in shapeData:
        for ch in shapeData[proc]:
            ostr =f"{proc:<{nProcLenMax}}"
            ostr+=f"{ch:<{nChLenMax}}"
            ostr+=shapeData[proc][ch]
            ostr_shapeBlock+= "shapes "+ostr+"\n"
            k+=1
    
    print(f"Number of shapes exported : [{k}] ")

    return ostr_shapeBlock

def getObservationStringBlock(observationData):

    ostr_obschannel ="bin         "
    ostr_obs     ="observation "
    nMax=0
    for ch in observationData:
        nMax=max(len(ch),nMax)
    nMax+=2
    for ch in observationData:
        ostr_obschannel+= f"{ch:<{nMax}}"
        ostr_obs    += f"{observationData[ch]:<{nMax}}"
    return ostr_obschannel+"\n"+ostr_obs

def getProcYieldStringBlock(dataS): 
    nMax=0
    for ch in dataS:
        nMax=max(nMax,len(ch))
        for proc in dataS[ch]:
            nMax=max(nMax,len(proc))
            nMax=max(nMax,len(str(dataS[ch][proc]['id'])))
            nMax=max(nMax,len(str(dataS[ch][proc]['rate'])))
            for syst in dataS[ch][proc]['syst']:
                nMax=max(nMax,len(str(dataS[ch][proc]['syst'][syst])))
    nMax+=2
    nChLenMax=len("process  ")
    systList=[]
    sysType=[]
    for ch in dataS:
        for proc in dataS[ch]:
            for syst in dataS[ch][proc]['syst']:
                nChLenMax=max(nChLenMax,len(syst))
                systList.append(syst)
                sysType.append(dataS[ch][proc]['syst_type'][syst])
    nChLenMax+=2
    ostr_syst    = {syst:f'{syst:<{nChLenMax}}   {sysT:<8} ' for syst,sysT in zip(systList,sysType) }
    nClm0Max=0
    for i in ostr_syst:
        nClm0Max=max(nClm0Max,len(ostr_syst[i]))
    
    ostr_channel =f'{"bin     ":<{nClm0Max}}'
    ostr_proc    =f'{"process ":<{nClm0Max}}'
    ostr_procid  =f'{"process ":<{nClm0Max}}'
    ostr_rate    =f'{"rate    ":<{nClm0Max}}'
    chList       = list(dataS.keys()) ; chList.sort();
    
    procList=[]
    procMap=dict()
    for ch in dataS:
        for proc in dataS[ch]:
            if proc not in procMap:
                procMap[proc]=dataS[ch][proc]['id']
            else:
                if procMap[proc]!=dataS[ch][proc]['id']:
                    print(f"ERROR ! duplicate proc ids found !! for {ch}/{proc}")
    
    procList=[i[0] for i in sorted(procMap.items(),key= lambda x : x[1])]
    procIDList=[i[1] for i in sorted(procMap.items(),key= lambda x : x[1])]
    pstr=""
    for i,j in zip(procList,procIDList):
        pstr+=f", ({i} : {j})"
    print(f"Channels  exported : [{len(chList)}] : {' '.join(chList)}")
    print(f"Processes exported : [{len(procList)}] : {pstr}")
    
    for ch in chList:
        for proc in procList:
            if proc not in dataS[ch]:
                continue
            ostr_channel+= f"{ch:<{nMax}}"
            ostr_proc   += f"{proc:<{nMax}}"
            ostr_procid += f"{dataS[ch][proc]['id']:<{nMax}}"
            ostr_rate   += f"{dataS[ch][proc]['rate']:<{nMax}}"
            for syst in dataS[ch][proc]['syst']:
                ostr_syst[syst]+=f"{dataS[ch][proc]['syst'][syst]:<{nMax}}"
    print(f"Number of nuisance parameters per proc exported : [{len(ostr_syst)}] ")
    return ostr_channel+"\n"+ostr_proc+"\n"+ostr_procid+"\n"+ostr_rate,ostr_syst

def getPDFIndexStringBlock(dataS):
    ostr_pdfindex=""
    for ch in dataS:
        ostr_pdfindex+=f"pdfindex_{ch}_merged_13TeV discrete\n"
    return ostr_pdfindex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',"--inputFile", help="Input File",default=None)
    parser.add_argument("-o","--ofile", help="output filename ", default='ofile_updated.txt' )
    parser.add_argument("--print", help="Print the datasets",default=False,action='store_true')
    parser.add_argument("--noPeaking", help="Remove the peaking processes",default=False,action='store_true')
    parser.add_argument("-p","--onlyPrint", help="Only print the datacard",default=False,action='store_true')    
    parser.add_argument("-k","--doKappaLambda", help="Only print the datacard",default=False,action='store_true')    
    args = parser.parse_args()
    txt,dataS,shapeData,observationData,systExtra=extractData(args.inputFile)
    
    if args.doKappaLambda:
        global doKappaLambda
        doKappaLambda=True
    if args.onlyPrint:
        print("================> Shape info , prior to update ")
        printShapeData(shapeData)
        print()
        print()
        print("================> observation block info , prior to update ")
        printObeservations(observationData)
        print()
        print()
        print("================> proc block info , prior to update ")
        printDset(dataS)
        print()
        print()
        print(f"Number of nuisance parameters (gbl) : [{len(systExtra)}] ")
        i=0
        k=0
        for prc in shapeData:
            i+=1
            for ch in shapeData[prc]:
                k+=1

        print(f"Number of shapes   exported : [{k}] in {i} procs")
        for ch in dataS:
            print("  > ch ",ch," n Procs : ",len(dataS[ch]))
 
        return
  
    #setRate(dataS_updated,'2018','CAT0','ggHHH',rate='137650.0')
    #setRate(dataS_updated,'2018','CAT1','ggHHH',rate='137650.0')
    #setRate(dataS_updated,'2018','CAT2','ggHHH',rate='137650.0')

    #setRate(dataS_updated,'2017','CAT0','vHH',rate='137650.0')
    #setRate(dataS_updated,'2017','CAT1','vHH',rate='137650.0')
    #setRate(dataS_updated,'2017','CAT2','vHH',rate='137650.0')

    #setRate(dataS_updated,'2017','CAT0','ttHH',rate='137650.0')
    #setRate(dataS_updated,'2017','CAT1','ttHH',rate='137650.0')
    #setRate(dataS_updated,'2017','CAT2','ttHH',rate='137650.0')

    dataS_updated,shapeData_updated,observationData_updated=standardizeData(dataS,shapeData,observationData)
    dataS_updated,shapeData_updated,observationData_updated=mergeChannels(
                                                                     dataS_updated,
                                                                     shapeData_updated,
                                                                     observationData_updated
                                                                    )

    for cat in ['CAT0','CAT1','CAT2'] :                                                                    
        #duplicateColumn(dataS_updated,shapeData_updated,cat,'ggHHH_2018_ch4',cat,'ggHHH_2016_ch4',lumi=lumiMap['2016'],isSig=True)
        #duplicateColumn(dataS_updated,shapeData_updated,cat,'ggHHH_2018_ch4',cat,'ggHHH_2017_ch4',lumi=lumiMap['2017'],isSig=True)
        duplicateColumn(dataS_updated,shapeData_updated,cat,'ttHH_2017' ,cat,'ttHH_2018',lumi=lumiMap['2018'],isSig=False)
        duplicateColumn(dataS_updated,shapeData_updated,cat,'ttHH_2017' ,cat,'ttHH_2016',lumi=lumiMap['2016'],isSig=False)
        duplicateColumn(dataS_updated,shapeData_updated,cat,'vHH_2017'  ,cat,'vHH_2018',lumi=lumiMap['2018'],isSig=False)
        duplicateColumn(dataS_updated,shapeData_updated,cat,'vHH_2017'  ,cat,'vHH_2016',lumi=lumiMap['2016'],isSig=False)

    if args.print:
        print("================> Shape info , prior to update ")
        printShapeData(shapeData)
        print()
        print("================> Shape info , post update ")
        printShapeData(shapeData_updated)
        print()
        print()
        print()
        print("================> observation block info , prior to update ")
        printObeservations(observationData)
        print()
        print("================> observation block info , post update ")
        printObeservations(observationData_updated)
        print()
        print()
        print("================> proc block info , prior to update ")
        printDset(dataS)
        print()
        print("================> proc block info , post update ")
        printDset(dataS_updated)
        print()
        print()
    
    if args.noPeaking:
        print("Removing Peaking backgrounds !")
        for proc in list(shapeData_updated.keys()):
            if 'bkg_mer' in proc:
                continue
            if 'data_obs'==proc:
                continue
            if 'ggHHH' in proc:
                continue
            removeColumn(dataS_updated , shapeData_updated , proc  )
    ostr_header        = getHeaderStringBlock(dataS_updated,systExtra)
    ostr_shapeBlock    = getShapeStringBlock(shapeData_updated)
    ostr_obsBlock      = getObservationStringBlock(observationData_updated)
    ostr_pdfindexBlock = getPDFIndexStringBlock(dataS_updated)
    ostr_procYBlock,systBlock = getProcYieldStringBlock(dataS_updated)
    ostr_systBlock=""
    for sy in systBlock:
        ostr_systBlock+=systBlock[sy]+"\n"
    for l in systExtra:
        ostr_systBlock+=l+"\n"
    print(f"Number of nuisance parameters (gbl) exported : [{len(systExtra)}] ")
    outPutTxt=[txt[0][:-1] + f" | Updated from {args.inputFile} \n"]
    hasWrittenUpdate=False
    devider='---'*60+'\n'
    if True:
        outPutTxt.append(ostr_header+"\n")
        outPutTxt.append(devider)
        outPutTxt.append(ostr_shapeBlock+"\n")
        outPutTxt.append(devider)
        outPutTxt.append(ostr_obsBlock+"\n")
        outPutTxt.append(devider)
        outPutTxt.append(ostr_procYBlock+"\n")
        outPutTxt.append(devider)
        if len(ostr_systBlock) > 0:
            outPutTxt.append(ostr_systBlock)
            outPutTxt.append(devider)
        outPutTxt.append(ostr_pdfindexBlock+"\n")
    else:
        for l in txt:
            if l.startswith('--'):
                devider=l
                continue
            if l.startswith('shapes'):
                if not hasWrittenUpdate:
                    outPutTxt.append(devider)
                    outPutTxt.append(ostr_shapeBlock+"\n")
                    outPutTxt.append(devider)
                    outPutTxt.append(ostr_obsBlock+"\n")
                    outPutTxt.append(devider)
                    outPutTxt.append(ostr_procYBlock+"\n")
                    outPutTxt.append(devider)
                    outPutTxt.append(ostr_systBlockp)
                    outPutTxt.append(devider)
                    outPutTxt.append(ostr_pdfindexBlock+"\n")
                    hasWrittenUpdate=True
                break
                continue
            if l.startswith('bin'):
                continue
            if l.startswith('observation'):
                continue
            if l.startswith('process'):
                continue
            if l.startswith('rate'):
                continue
            if l.startswith('pdfindex'):
                continue
            outPutTxt.append(l)
    
 
    with open(args.ofile,'w') as f :
        for l in outPutTxt:
           f.write(l)


if __name__=='__main__':
    main( )
