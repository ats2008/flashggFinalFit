import glob , os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--step",  help="step",choices=['ftest','phoSyst','signalFit','pack','plotPacked'] )
parser.add_argument("-c","--cfg",  help="cfg" ,default=None)
parser.add_argument("--procs" , help="Procs" , default=None)
parser.add_argument("--years" , help="Years" , default=None)
parser.add_argument("--exec", help="execute the cmd",action='store_true')
parser.add_argument("-p","--printOnly", help="Do not submit the jobs",action='store_true')
parser.add_argument("-t","--isTest", help="just process only the one input file",action='store_true')
args = parser.parse_args()

CMD_TPL=""
if args.step=='ftest':
    CMD_TPL='python RunSignalScripts.py --inputConfig  ICFG  --mode fTest --groupSignalFitJobsByCat --modeOpts "--threshold 2 --doPlots  " --inputWSDir IWD --inputWSFile IWF  --procs PROC --ext EXT --year YEAR '
elif args.step=='phoSyst' :
    CMD_TPL='python RunSignalScripts.py --inputConfig ICFG --mode calcPhotonSyst --inputWSDir IWD --inputWSFile IWF  --procs PROC --ext EXT --year YEAR  '
elif args.step=='signalFit' :
    CMD_TPL='python RunSignalScripts.py --inputConfig ICFG --mode signalFit --groupSignalFitJobsByCat --modeOpts "--massPoints 125 --replacementThreshold 0 --doPlots " --inputWSDir IWD --inputWSFile IWF  --procs PROC --ext EXT --year YEAR '
elif args.step=='pack' :
    CMD_TPL='python RunPackager.py --cats auto --inputWSDir IWD --exts EXT --massPoints 125 --year YEAR --outputExt  EXT --batch condor '
elif args.step=='plotPacked':
    CMD_TPL=' python RunPlotter.py --procs PROC --cats all  --ext EXT --year YEAR'
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

tag='v30p1'
files=glob.glob("../Trees2WS/mar9/ws_*/*.root")
print(f"Got {len(files)} ! ")
procSet={}
for fls in files:
    print(fls)
    wsDir='/'.join(fls.split('/')[:-1])+'/'
    wsFile=fls.split('/')[-1]
    collection=wsFile.split("_")[0]
    proc=wsFile.split("_")[1]
    yr=wsFile.split("_")[2]
    if collection=='kappaScan':
        proc='_'.join(wsFile.split("_")[1:5])
        yr=wsFile.split("_")[5]
        print(proc,yr)
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
        print("YEAR NOT FOUND")
        print("fl : ",fls)
        exit(1)

    ext=f"trippleH_{tag}_{proc}_{year}"
    if procs:
        if proc not in procs:
            continue
    if years:
        if year not in years:
            continue
    if proc not in procSet:
        procSet[proc]=[]
    procSet[proc].append(year)


    print("wsDir  : ",wsDir)
    print("wsFile : ",wsFile)
    print("proc : ",proc)
    print("year : ",year)   
    print("ext : ",ext)    
    cmd=CMD_TPL.replace("ICFG",args.cfg)
    cmd=cmd.replace("IWD",wsDir)
    cmd=cmd.replace("IWF",wsFile)
    cmd=cmd.replace("PROC",proc)
    cmd=cmd.replace("YEAR",year)
    cmd=cmd.replace("EXT",ext)
    print(cmd)
    if args.exec:
        os.system(cmd)
    print("= "*20)
    if args.isTest:
        break


for i,prc in enumerate(procSet):
    print(i+1,"  : ",prc ,"  : ",procSet[prc])
