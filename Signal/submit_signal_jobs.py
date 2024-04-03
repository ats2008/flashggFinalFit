import glob , os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--step",  help="step",choices=['ftest','phoSyst','signalFit','pack','plotPacked','exportPlots'] )
parser.add_argument("-c","--cfg",  help="cfg" ,default=None)
parser.add_argument("--tagOverride",  help="set tag" ,default=None)
parser.add_argument("--procs" , help="Procs" , default=None)
parser.add_argument("--years" , help="Years" , default=None)
parser.add_argument("--exec", help="execute the cmd",action='store_true')
parser.add_argument("-p","--printOnly", help="Do not submit the jobs",action='store_true')
parser.add_argument("-t","--isTest", help="just process only the one input file",action='store_true')
args = parser.parse_args()
tag='v32p0'
if args.tagOverride:
    tag=args.tagOverride
files=glob.glob("../Trees2WS/apr3/ws_*/*.root")


validationExportScriptTemplate="""
#BASE=v30ValidationPlots/Peaking/
mkdir -p BASE
mkdir -p BASE/PROCESS/
mkdir -p BASE/PROCESS/YEAR
mkdir -p BASE/PROCESS/YEAR/fTest_RV
mkdir -p BASE/PROCESS/YEAR/sigfit_splines
mkdir -p BASE/PROCESS/YEAR/sigfit_vsMH
mkdir -p BASE/PROCESS/YEAR/sigfit_total_shape
mkdir -p BASE/PROCESS/YEAR/sigfit_RV

cp INFOLDER/Plots/smodel* BASE/PROCESS
cp INFOLDER/fTest/Plots/*RV* BASE/PROCESS/YEAR/fTest_RV
cp INFOLDER/signalFit/Plots/*total_shape* BASE/PROCESS/YEAR/sigfit_total_shape
cp INFOLDER/signalFit/Plots/*RV* BASE/PROCESS/YEAR/sigfit_RV
cp INFOLDER/signalFit/Plots/*vs_mH* BASE/PROCESS/YEAR/sigfit_vsMH
cp INFOLDER/signalFit/Plots/*splines* BASE/PROCESS/YEAR/sigfit_splines
"""

def exportPlotsForValidation(INBASE,BASE):
    txt=INBASE.replace(f"outdir_trippleH_{tag}_","")
    PROCESS='_'.join(txt.split('_')[:-1])
    YEAR=txt.split('_')[-1]
    print("     Exporting > Process ",PROCESS,",  Year",YEAR)
    validationExportScript = validationExportScriptTemplate.replace("INFOLDER",INBASE).replace("BASE",BASE).replace("PROCESS",PROCESS).replace("YEAR",YEAR)
    #print(validationExportScript)
    os.system(validationExportScript)


CMD_TPL=""
if args.step=='ftest':
    CMD_TPL='python RunSignalScripts.py --inputConfig  ICFG  --mode fTest --groupSignalFitJobsByCat --modeOpts "--threshold 2 --doPlots  " --inputWSDir IWD --inputWSFile IWF  --procs PROC --ext EXT --year YEAR '
elif args.step=='phoSyst' :
    CMD_TPL='python RunSignalScripts.py --inputConfig ICFG --mode calcPhotonSyst --inputWSDir IWD --inputWSFile IWF  --procs PROC --ext EXT --year YEAR  '
elif args.step=='signalFit' :
    CMD_TPL='python RunSignalScripts.py --inputConfig ICFG --mode signalFit --groupSignalFitJobsByCat --modeOpts "--massPoints 125 --skipVertexScenarioSplit --replacementThreshold 200 --doPlots " --inputWSDir IWD --inputWSFile IWF  --procs PROC --ext EXT --year YEAR '
elif args.step=='pack' :
    CMD_TPL='python RunPackager.py --cats auto --inputWSDir IWD --exts EXT --massPoints 125 --year YEAR --outputExt  EXT --batch condor '
elif args.step=='plotPacked':
    CMD_TPL=' python RunPlotter.py --procs PROC --cats all  --ext EXT --year YEAR'
elif args.step=='exportPlots':
    ibases=glob.glob(f"outdir_trippleH_{tag}_*")
    exportBase=f'exportedPlots_{tag}/Peaking/'
    for ibase in ibases:
        print("Processing ",ibase)
        exportPlotsForValidation(ibase,exportBase)
    print("Setting up the webdirs ")
    for f in os.walk(exportBase):
        os.system('cp tools/index.php '+f[0])
        print("\r  COPYING index.php to "+f[0]+"                                                    ",end="")
    print()
    exit(0)
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

print(f"Got {len(files)} ! ")
procSet={}
for fls in files:
    print(fls)
    wsDir='/'.join(fls.split('/')[:-1])+'/'
    wsFile=fls.split('/')[-1]
    collection=wsFile.split("_")[0]
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



