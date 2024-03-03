echo
echo        Signal F-Tests
python RunSignalScripts.py --inputConfig config_HHH.py --mode fTest --modeOpts "--doPlots --threshold 2"
echo
echo        Signal Fitting
python RunSignalScripts.py --inputConfig config_HHH.py --mode signalFit --groupSignalFitJobsByCat --modeOpts "--massPoints 125 --replacementThreshold 0 --skipSystematics --doPlots"
echo
echo        Signal Model Packer
python RunPackager.py --cats auto --inputWSDir ../Trees2WS/inputFiles/ws_trippleH/ --exts trippleH_2018 --massPoints 125 --year 2018 --outputExt trippleH_2018
echo


python3 submit_signal_jobs.py -s ftest  -c test_2016.py  --year 2016Pre --exec
python3 submit_signal_jobs.py -s ftest  -c test_2016.py  --year 2016Post --exec
python3 submit_signal_jobs.py -s ftest  -c test_2016.py  --year 2016 --exec
python3 submit_signal_jobs.py -s ftest  -c test_2017.py  --year 2017 --exec
python3 submit_signal_jobs.py -s ftest  -c test_2018.py  --year 2018 --exec

python3 submit_signal_jobs.py -s phoSyst  -c test_2018.py  --year 2018  --exec
python3 submit_signal_jobs.py -s phoSyst  -c test_2017.py  --year 2017  --exec
python3 submit_signal_jobs.py -s phoSyst  -c test_2016.py  --year 2016  --exec
python3 submit_signal_jobs.py -s phoSyst  -c test_2016.py  --year 2016Pre  --exec
python3 submit_signal_jobs.py -s phoSyst  -c test_2016.py  --year 2016Post  --exec

python3 submit_signal_jobs.py -s signalFit -c test_2018.py  --year 2018  --exec
python3 submit_signal_jobs.py -s signalFit -c test_2017.py  --year 2017  --exec
python3 submit_signal_jobs.py -s signalFit -c test_2016.py  --year 2016  --exec
python3 submit_signal_jobs.py -s signalFit -c test_2016.py  --year 2016Pre  --exec
python3 submit_signal_jobs.py -s signalFit -c test_2016.py  --year 2016Post  --exec

python3 submit_signal_jobs.py -s pack -c test_2018.py  --year 2018  --exec
python3 submit_signal_jobs.py -s pack -c test_2017.py  --year 2017  --exec
python3 submit_signal_jobs.py -s pack -c test_2016.py  --year 2016  --exec
python3 submit_signal_jobs.py -s pack -c test_2016.py  --year 2016Pre  --exec
python3 submit_signal_jobs.py -s pack -c test_2016.py  --year 2016Post  --exec


python3 submit_signal_jobs.py -s plotPacked --exec
