"""
# Edit the version and ws_* dir paths

python3 submit_signal_jobs.py -s runYields --exec

python3 submit_signal_jobs.py -s dc --exec
python3 submit_signal_jobs.py -s dc_syst --exec

python3 submit_signal_jobs.py -s dc_cleanup --exec
python3 submit_signal_jobs.py -s dc_syst_cleanup --exec

"""
import glob , os
import argparse
import multiprocessing as mp
import subprocess

NUM_CPUS=12
N=0
taskID=0
completedIdx=0

GLOBAL_FAILURE_LIST=[]
def execute_cmd(cmd):
    #value = rd.random()
    #time.sleep(value*3)
    #print("    >>> PRGRESSING  <<<",flush=True)
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()    
    rc = proc.returncode
    if rc !=0:
        print(err)
        GLOBAL_FAILURE_LIST.append(cmd)
    #os.system(cmd)
    return {'cmd':cmd,"exitCode":rc}

def progress_callback(out):
    global taskID,completedIdx
    completedIdx+=1
    taskID-=1
    stat="sucessfully"
    if out['exitCode']!=0:
        stat=f" with exit code {out['exitCode']}"

    print(f"Fininshed {stat} {completedIdx}/{N}. {taskID} remining!\n > {out['cmd']}" , flush=True)
 
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--step",  help="step",choices=['runYields','dc_syst','dc','dc_syst_cleanup','dc_cleanup'] )
    parser.add_argument("-c","--cfg",  help="cfg" ,default=None)
    parser.add_argument("--procs" , help="Procs" , default=None)
    parser.add_argument("--years" , help="Years" , default=None)
    parser.add_argument("-v","--version" , help="Version" , default=None)
    parser.add_argument("--exec", help="execute the cmd",action='store_true')
    parser.add_argument("--noMP", help="execute the cmd without Multiprocessing",action='store_true',default=False)
    parser.add_argument("-p","--printOnly", help="Do not submit the jobs",action='store_true')
    parser.add_argument("-t","--isTest", help="just process only the one input file",action='store_true')
    args = parser.parse_args()
    
    tag='v32p0'
    files=glob.glob("../Trees2WS/apr3/ws_*/*.root")
    if args.version is None:
        args.version=tag
    CMD_TPL=""
    SED_CMS_TPL=''
    if args.step=='runYields':
        CMD_TPL='python RunYields.py --cats auto --inputWSDirMap YEAR=IWD   --procs  PROC  --batch local --queue longlunch --ext EXT  --sigModelExt SIG_EXT --skipBkg --doSystematics --ignore-warnings '
    elif args.step=='dc_syst':
        CMD_TPL='python makeDatacard.py --years YEAR --ext EXT --output VERDataCards/WithSysts/EXT --doSystematics'
        os.system('mkdir -p VERDataCards/WithSysts/'.replace('VER',args.version))
    elif args.step=='dc':
        CMD_TPL='python makeDatacard.py --years YEAR --ext EXT --output VERDataCards/NoSysts/EXT '
        os.system('mkdir -p VERDataCards/NoSysts/'.replace('VER',args.version))
    elif args.step=='dc_syst_cleanup':
        SED_CMS_TPL="sed  -i '/pdfindex_CAT.*discrete/d' VERDataCards/WithSysts/*".replace("VER",args.version)
        print(SED_CMS_TPL)
        os.system(SED_CMS_TPL)
        exit(0)
    elif args.step=='dc_cleanup':
        SED_CMS_TPL="sed  -i '/pdfindex_CAT.*discrete/d' VERDataCards/NoSysts/*".replace("VER",args.version)
        print(SED_CMS_TPL)
        os.system(SED_CMS_TPL)
        exit(0)
    else:
        print("ENTER VALID MODE ! ")
        exit(1)
    #if args.printOnly:
    #    CMD_TPL+="  --printOnly "
    
    procs=[]
    if args.procs:
        procs=args.procs.split(',')
    years=[]
    if args.years:
        years=args.years.split(',')
    
    if not args.cfg:
        args.cfg=''
    
    print(f"Got {len(files)} ! ")

    pool=None
    if args.exec:
        pool = mp.Pool(NUM_CPUS)
    

    proctSet={}
    for fls in files:
        wsDir='/'.join(fls.split('/')[:-1])+'/'
        wsFile=fls.split('/')[-1]
        mode=wsFile.split("_")[0]
        proc=wsFile.split("_")[1]
        yr=wsFile.split("_")[2]
        if ('c3' in wsFile) and ( 'd4' in wsFile ):
            proc='_'.join(wsFile.split("_")[1:5])
            yr=wsFile.split("_")[5]
        if 'ggHH_kl' in wsFile:
            proc='_'.join(wsFile.split("_")[1:3])
            yr=wsFile.split("_")[3]
                
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
            exit()
        ext=f"trippleH_{tag}_{proc}_{year}"
        sig_ext=ext
        if procs:
            if proc not in procs:
                continue
        if years:
            if year not in years:
                continue
        if proc not in proctSet:
            proctSet[proc]=[]
        proctSet[proc].append(year)
    
        print("wsDir  : ",wsDir)
        print("wsFile : ",wsFile)
        print("proc : ",proc)
        print("year : ",year)   
        print("ext : ",ext)    
        cmd=str(CMD_TPL)
        cmd=cmd.replace("VER",args.version)
        cmd=cmd.replace("IWD",wsDir)
        cmd=cmd.replace("IWF",wsFile)
        cmd=cmd.replace("PROC",proc)
        cmd=cmd.replace("YEAR",year)
        cmd=cmd.replace("SIG_EXT",sig_ext)
        cmd=cmd.replace("EXT",ext)
        print(cmd)
        if args.exec:
            if args.noMP:
                print("  > executing locally ")
                os.system(cmd)
            else:
                taskID+=1
                N+=1
                print(f"  Adding task to the pool ! n-Task {taskID}")
                pool.apply_async(execute_cmd, args=(cmd,),callback=progress_callback)    
        print("= "*20)
        if args.isTest:
            break
    
    for i in proctSet:
        print(i,proctSet[i])        
    if args.exec:    
        pool.close()
        pool.join()
    print("Failed cmds : ",len(GLOBAL_FAILURE_LIST))
    for i in GLOBAL_FAILURE_LIST:
        print(i)
