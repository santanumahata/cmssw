#!/bin/bash
# Relval check of the photon TrigObj fix in CMSSW_16_1_3: clean area vs area with commit 828ed8b2a.
# Steps 1-2 of each workflow run once (clean area); steps 3-4 run in both areas on the same step-2 output.
# Usage: bash relval_fix_check.sh
set -eo pipefail

export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
source /cvmfs/cms.cern.ch/cmsset_default.sh

RELEASE=CMSSW_16_1_3
WORK=/eos/user/s/smahata/trigobj_check/relval_16_1_3
FIX_COMMIT=828ed8b2a887a758130483d19a27adac8e29c181
CFF=PhysicsTools/NanoAOD/python/triggerObjects_cff.py
mkdir -p $WORK

echo "=== step 1: clean area and full workflows"
cd $WORK
if [ ! -d clean ]; then
    scram project -n clean CMSSW $RELEASE
fi
cd clean/src
eval $(scramv1 runtime -sh)
mkdir -p $WORK/run_clean && cd $WORK/run_clean
# 12452.0 generates its own GEN-SIM: its RelVal GEN-SIM input is not found at T2_CH_CERN (--ibeos)
if ! ls 12452.0_*/step3_inNANOEDMAODSIM.root > /dev/null 2>&1; then
    rm -rf 12452.0_*
    runTheMatrix.py -w upgrade -l 12452.0 -j 4
fi
# 141.046 RAW is on tape only in DAS; the IB EOS cache (--ibeos) has the file
if ! ls 141.046_*/step3_inNANOEDMAOD.root > /dev/null 2>&1; then
    if ! ls -d 141.046_* > /dev/null 2>&1; then
        runTheMatrix.py -l 141.046 -i all --ibeos -j 4 || true
    fi
    cd 141.046_*
    # of the 321 RAW files DAS lists for run 369978 (tape only), only this one is in the IB EOS cache
    echo "root://eoscms.cern.ch//eos/cms/store/user/cmsbuild/store/data/Run2023D/EGamma0/RAW/v1/000/369/978/00000/0068cd83-0af4-4efc-9155-b2521e558ebb.root" > step1_dasquery.log
    grep -E "cmsDriver.py step[234] " cmdLog > steps234.sh
    cat steps234.sh
    bash steps234.sh
    ls -l step3_inNANOEDMAOD.root
    cd $WORK/run_clean
fi

echo "=== step 2: fix area with the cherry-picked commit"
cd $WORK
if [ ! -d fix ]; then
    scram project -n fix CMSSW $RELEASE
fi
cd fix/src
eval $(scramv1 runtime -sh)
if [ ! -d PhysicsTools/NanoAOD ]; then
    git cms-addpkg PhysicsTools/NanoAOD
    git fetch https://github.com/santanumahata/cmssw.git nano-photon-trigobj-unseeded
    git cherry-pick $FIX_COMMIT
fi
git diff $RELEASE --numstat
CHANGED=$(git diff $RELEASE --numstat | awk '{print $1, $2, $3}')
if [ "$CHANGED" != "1 1 $CFF" ]; then
    echo "ERROR: expected exactly one changed line in $CFF, got: $CHANGED"; exit 1
fi
git diff $RELEASE
scram b -j 8

echo "=== step 3: rerun steps 3 and 4 in the fix area on the clean step-2 output"
for CLEAN_DIR in $WORK/run_clean/12452.0_* $WORK/run_clean/141.046_*; do
    FIX_DIR=$WORK/run_fix/$(basename $CLEAN_DIR)
    mkdir -p $FIX_DIR && cd $FIX_DIR
    ln -sf $CLEAN_DIR/step2.root step2.root
    grep -E "cmsDriver.py step[34] " $CLEAN_DIR/cmdLog > steps34.sh
    cat steps34.sh
    if [ ! -s steps34.sh ]; then
        echo "ERROR: no step3/step4 command in $CLEAN_DIR/cmdLog"; exit 1
    fi
    bash steps34.sh
done

echo "=== step 4: flat NANO from the EDM NANO of both workflows (both areas)"
for AREA in clean fix; do
    cd $WORK/$AREA/src && eval $(scramv1 runtime -sh)
    cd $WORK/run_$AREA/12452.0_*
    cmsDriver.py flat --step NONE --mc --conditions auto:phase1_2023_realistic --era Run3_2023 \
        --filein file:step3_inNANOEDMAODSIM.root --fileout file:step3_flatNANOAODSIM.root \
        --eventcontent NANOAODSIM --datatier NANOAODSIM -n -1 > flat_nano.log 2>&1
    cd $WORK/run_$AREA/141.046_*
    cmsDriver.py flat --step NONE --data --conditions auto:run3_data_relval --era Run3_2023 \
        --filein file:step3_inNANOEDMAOD.root --fileout file:step3_flatNANOAOD.root \
        --eventcontent NANOAOD --datatier NANOAOD -n -1 > flat_nano.log 2>&1
done

echo "=== step 5: log check"
for AREA in clean fix; do
    for LOG in $WORK/run_$AREA/*/step3_*.log; do
        echo "$LOG: exceptions $(grep -c "Exception" $LOG || true)," \
             "triggerObjectTable lines $(grep -c "triggerObjectTable" $LOG || true)"
        grep "triggerObjectTable" $LOG | head -5 || true
    done
done
echo "=== done"
