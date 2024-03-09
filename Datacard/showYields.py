import pickle

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i',"--inputFile", help="Input File",default=None)
args = parser.parse_args()


with open(args.inputFile,'rb') as f:
    data=pickle.load(f)

print(data.keys())    
print()

branchesToPrint=['proc',
            'year',
            #'inputWSFile', 
            'nominalDataName', 
            #'modelWSFile', 
            'model', 
            'rate' , 
            'nominal_yield'
            ]
print(data[branchesToPrint])

