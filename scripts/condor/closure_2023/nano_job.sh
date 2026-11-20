#!/bin/bash
# One closure job: re-make NanoAOD from one 2023 MINIAOD file in one CMSSW_16_1_3 area (stock, pr52514 or both fixes).
# args: <dataset tag> <step> <release area dir> <MINIAOD LFN> <file index>
# Total: time O(events in the file), space O(output NANO size)
TAG=$1
STEP=$2
AREA=$3
LFN=$4
IDX=$5
OUT=/eos/user/s/smahata/nano3018_test/closure_2023/$TAG/$STEP

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc13
cd $AREA/CMSSW_16_1_3/src
eval `scram runtime -sh`
cd $_CONDOR_SCRATCH_DIR

echo "area $AREA" > nano_$IDX.log
python3 -c "import PhysicsTools.NanoAOD.triggerObjects_cff as m; print(m.__file__)" >> nano_$IDX.log
cmsDriver.py nano -s NANO --data --era Run3_2023,run3_nanoAOD_pre142X --conditions auto:run3_data \
  --datatier NANOAOD --eventcontent NANOAOD \
  --filein root://cms-xrd-global.cern.ch/$LFN --fileout file:nano_$IDX.root -n -1 \
  --python_filename nano_cfg.py >> nano_$IDX.log 2>&1
STATUS=$?
echo "cmsDriver exit $STATUS" >> nano_$IDX.log

xrdcp -f nano_$IDX.log root://eosuser.cern.ch/$OUT/nano_$IDX.log
if [ $STATUS -eq 0 ]; then
  xrdcp -f nano_$IDX.root root://eosuser.cern.ch/$OUT/nano_$IDX.root
fi
exit $STATUS
