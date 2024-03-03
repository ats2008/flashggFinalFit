# Config file: options for signal fitting
_version ='v29p5'
_year = '2018'
tag = 'yr18std'
signalScriptCfg = {
  
  # Setup
  'inputWSDir':'/grid_mnt/t3storage3/athachay/trippleHiggs/hhhTo4b2g/flashggFinalFits/CMSSW_10_2_13/src/flashggFinalFit/Trees2WS/jan16_xSecUpdated/ws_2018/',
  'inputWSFile': ['doubleH_2018_M125_13TeV_doubleH.root','singleH_UL18_M125_13TeV_singleH.root','sig_ggHHH_UL18_13TeV_ggHHH.root'], #['singleH_125_13TeV_singleH.root']
  #'procs':'c3_4_d4_9', # if auto: inferred automatically from filenames
  'procs':'doubleH,singleH,ggHHH', # if auto: inferred automatically from filenames
  'cats':'CAT0,CAT1,CAT2', # if auto: inferred automatically from (0) workspace
  #'ext':'trippleHMultiPeak_%s_%s' %(_version,_year),
  'ext':'trippleH_%s_%s_%s' %(_version,_year,tag),
  'analysis':'trippleH_v2', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'year':'%s'%_year, # Use 'combined' if merging all years: not recommended
  'massPoints':'120,125,130',

  #Photon shape systematics  
  #'systematics' : ['JEC','FNUFEB','FNUFEE'],
  
  'scales': 'HighR9EB,HighR9EE,LowR9EB,LowR9EE,Gain1EB,Gain6EB', # separate nuisance per year
  'scalesCorr': 'ShowerShapeHighR9EB,ShowerShapeHighR9EE,ShowerShapeLowR9EB,ShowerShapeLowR9EE,SigmaEOverEShift,FNUFEE,FNUFEB,MaterialCentralBarrel,MaterialForward,MaterialOuterBarrel', # correlated across years
  'scalesGlobal':'NonLinearity,Geant4', # affect all processes equally, correlated across years
  'smears':'HighR9EBPhi,HighR9EBRho,HighR9EEPhi,HighR9EERho,LowR9EBPhi,LowR9EBRho,LowR9EEPhi,LowR9EERho', # separate nuisance per year

  # Job submission options
  'queue':'hep.q',
  'batch':'local',
  'batch':'condor', # ['condor','SGE','IC','local']
  #'queue':'espresso',

}
