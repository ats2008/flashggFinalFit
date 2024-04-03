"""

python3 submit_signal_jobs.py  -p
python3 submit_signal_jobs.py  --procs ggHHH,c3_0_d4_99,c3_0_d4_m1,c3_19_d4_19,c3_1_d4_0,c3_1_d4_2,c3_2_d4_m1,c3_4_d4_9,c3_m1_d4_0,c3_m1_d4_m1,c3_m1p5_d4_m0p5 --exec -n ggHHH
python3 submit_signal_jobs.py  --procs ggHH,ggHH_kl2p45,ggHH_kl5p0,ggHH_kl0p0,vbfHH,ttHH,wHH,zHH,WToQQHHTo2B2G,ZToBBHHTo2B2G --exec -n doubleH
python3 submit_signal_jobs.py  --procs ggH,ttH,vH,vbfH --exec -n singleH

"""


import glob , os
import argparse
import multiprocessing as mp
import random as rd
import time
import subprocess



NUM_CPUS=12
N=0
taskID=0
completedIdx=0
def execute_cmd(cmd):
    #value = rd.random()
    #time.sleep(value*3)
    #print("    >>> PRGRESSING  <<<",flush=True)
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()    
    rc = proc.returncode
    if rc !=0:
        print(err)
    #os.system(cmd)
    return cmd

def progress_callback(out):
    global taskID,completedIdx
    completedIdx+=1
    taskID-=1
    print(f"Fininshed {completedIdx}/{N}. {taskID} remining!\n > {out}" , flush=True)
    

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--step",  help="step",choices=['tree2WS'],default='tree2WS' )
    parser.add_argument("-c","--cfg",  help="cfg" ,default=None)
    parser.add_argument("--procs" , help="Procs" , default=None)
    parser.add_argument("-n","--treeNameProc" , help="Procs" , default='ggHHH')
    parser.add_argument("--years" , help="Years" , default=None)
    parser.add_argument("--exec", help="execute the cmd",action='store_true')
    parser.add_argument("-p","--printOnly", help="Do not submit the jobs",action='store_true')
    parser.add_argument("-t","--isTest", help="just process only the one input file",action='store_true')
    args = parser.parse_args()



    CMD_TPL=""
    if args.step=='tree2WS':
        CMD_TPL='python trees2ws.py --inputConfig config_trippleH.py --inputTreeFile IWT --productionMode PROC     --doSystematics --year YEAR  --treeNameProc TNP'
    else:
        print("ENTER VALID MODEL ! ")
        exit(1)
    if args.printOnly:
        CMD_TPL+="  --printOnly "
    
    procs=[]
    if args.procs:
        procs=args.procs.split(',')
    years=[]
    if args.years:
        years=args.years.split(',')
    
    if not args.cfg:
        args.cfg=''
    
    tag='v32p0'
    files=glob.glob("apr3/*.root")
    print(f"Got {len(files)} ! ")
    pool=None
    if args.exec:
        pool = mp.Pool(NUM_CPUS)
    
    proctSet={}
    for fls in files:
        isReco=''
        iFile=fls
        wsDir='/'.join(fls.split('/')[:-1])+'/'
        wsFile=fls.split('/')[-1]
        print(wsFile.split('_'))
        # ['kappaScan', 'c3', '0', 'd4', '99', 'UL16Post', '13TeV.root']
        mode=wsFile.split("_")[0]
        proc=wsFile.split("_")[1]
        yr=wsFile.split("_")[2]
        #if mode=='kappaScan':
        if ('c3' in wsFile) and ( 'd4' in wsFile ):
            proc='_'.join(wsFile.split("_")[1:5])
            yr=wsFile.split("_")[5]
        if 'ggHH_kl' in wsFile:
            proc='_'.join(wsFile.split("_")[1:3])
            yr=wsFile.split("_")[3]
            
        print("proc,yr = ",proc,yr)
    
        if '18' in yr:
            year='2018'
        elif '17' in yr:
            year='2017'
        elif '17' in yr:
            year='2017'
        elif '16Pre' in yr:
            year='2016Pre'
        elif '16Post' in yr:
            year='2016Post'
        elif '16' in yr:
            year='2016'
        else:
            print("YEAR NOT FOUND for ",fls)
        if 'RR' in wsFile:
            isReco=' --isRECO'

        ext=f"trippleH_{tag}_{proc}_{year}"
        if procs:
            if proc not in procs:
                continue
        if years:
            if year not in years:
                continue
        if proc not in proctSet:
            proctSet[proc]=[]
        proctSet[proc].append(year)
        print(" fls : ",fls)
        print("wsDir  : ",wsDir)
        print("wsFile : ",wsFile)
        print("proc : ",proc)
        print("year : ",year)   
        print("ext : ",ext)    
        cmd=CMD_TPL.replace("ICFG",args.cfg)
        cmd=cmd.replace("IWT",iFile)
        cmd=cmd.replace("IWD",wsDir)
        cmd=cmd.replace("IWF",wsFile)
        cmd=cmd.replace("PROC",proc)
        cmd=cmd.replace("TNP",args.treeNameProc)
        yearBare=year.replace('Post','').replace('Pre','')
        cmd=cmd.replace("YEAR",yearBare)
        cmd=cmd.replace("EXT",ext) + isReco
        if args.exec:
            taskID+=1
            N+=1
            print(f"  Adding task to the pool ! n-Task {taskID}")
            pool.apply_async(execute_cmd, args=(cmd,),callback=progress_callback)    
            #os.system(cmd)
        else:
            print(cmd)
        print("= "*20)
        if args.isTest:
            break
    
    
    for i in proctSet:
        print(i,proctSet[i])        
    
    if args.exec:    
        pool.close()
        pool.join()


