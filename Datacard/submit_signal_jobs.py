import glob , os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--step",  help="step",choices=['runYields','dc_syst','dc'] )
parser.add_argument("-c","--cfg",  help="cfg" ,default=None)
parser.add_argument("--procs" , help="Procs" , default=None)
parser.add_argument("--years" , help="Years" , default=None)
parser.add_argument("-v","--version" , help="Version" , default=None)
parser.add_argument("--exec", help="execute the cmd",action='store_true')
parser.add_argument("-p","--printOnly", help="Do not submit the jobs",action='store_true')
parser.add_argument("-t","--isTest", help="just process only the one input file",action='store_true')
args = parser.parse_args()

tag='v30p1'
files=glob.glob("../Trees2WS/mar9/ws_*/*.root")
if args.version is None:
    args.version=tag
CMD_TPL=""
SED_CMS_TPL=''
if args.step=='runYields':
    CMD_TPL='python RunYields.py --cats auto --inputWSDirMap YEAR=IWD   --procs  PROC  --batch local --queue longlunch --ext EXT  --sigModelExt SIG_EXT --skipBkg --doSystematics --ignore-warnings '
elif args.step=='dc_syst':
    CMD_TPL='python makeDatacard.py --years YEAR --ext EXT --output VERDataCards/WithSysts/EXT --doSystematics'
    SED_CMS_TPL="sed  -i '/pdfindex_CAT.*discrete/d' VERDataCards/WithSysts/EXT*"
    os.system('mkdir -p VERDataCards/WithSysts/'.replace('VER',args.version))
elif args.step=='dc':
    CMD_TPL='python makeDatacard.py --years YEAR --ext EXT --output VERDataCards/NoSysts/EXT '
    SED_CMS_TPL="sed  -i '/pdfindex_CAT.*discrete/d' VERDataCards/NoSysts/EXT*"
    os.system('mkdir -p VERDataCards/NoSysts/'.replace('VER',args.version))
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
proctSet={}
for fls in files:
    wsDir='/'.join(fls.split('/')[:-1])+'/'
    wsFile=fls.split('/')[-1]
    mode=wsFile.split("_")[0]
    proc=wsFile.split("_")[1]
    yr=wsFile.split("_")[2]
    if mode=='kappaScan':
        proc='_'.join(wsFile.split("_")[1:5])
        yr=wsFile.split("_")[5]
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
        os.system(cmd)
    print("= "*20)
    if args.isTest:
        break
    sedCMD=SED_CMS_TPL.replace("VER",args.version).replace("EXT",ext)
    os.system(sedCMD)

for i in proctSet:
    print(i,proctSet[i])        
