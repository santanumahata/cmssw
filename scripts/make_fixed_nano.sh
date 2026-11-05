#!/bin/bash
# Reproduce NanoAOD from one MiniAOD file twice, without and with the photon TrigObj fix.
# Usage: bash make_fixed_nano.sh v13|v15
set -eo pipefail

export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
source /cvmfs/cms.cern.ch/cmsset_default.sh

WORK=/eos/user/s/smahata/trigobj_check/cmssw
# parent MiniAOD of the central v13 file 4f45fe87-a958-4c8f-b88f-c322fec857f3.root
INPUT=root://cms-xrd-global.cern.ch//store/mc/Run3Summer23MiniAODv4/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15_ext1-v4/2820000/74338d47-0b38-4e0b-83a2-ad85c7f4e533.root
CFF=PhysicsTools/NanoAOD/python/triggerObjects_cff.py

case "$1" in
    v13)
        RELEASE=CMSSW_13_3_1_patch1
        ERA=Run3_2023
        GT=133X_mcRun3_2023_realistic_ForNanov13_v1
        ;;
    v15)
        RELEASE=CMSSW_15_0_15_patch4
        ERA=Run3_2023,run3_nanoAOD_pre142X
        GT=150X_mcRun3_2023_realistic_v1    # processing string of Run3Summer23NanoAODv15 in DAS
        ;;
    *)
        echo "usage: $0 v13|v15"; exit 1
        ;;
esac
OUT=$WORK/$1
mkdir -p "$OUT"

run_nano() {
    local label=$1
    cmsDriver.py nano_$label --step NANO --mc --scenario pp --nThreads 4 \
        --eventcontent NANOAODSIM --datatier NANOAODSIM \
        --conditions $GT --era $ERA \
        --filein $INPUT --fileout file:$OUT/nano_$label.root \
        --python_filename $OUT/nano_${label}_cfg.py -n -1
}

echo "=== step 1: release area $RELEASE"
cd $WORK
if [ ! -d $RELEASE ]; then
    scram project CMSSW $RELEASE
fi
cd $RELEASE/src
eval $(scramv1 runtime -sh)

echo "=== step 2: check out PhysicsTools/NanoAOD and build"
if [ ! -d PhysicsTools/NanoAOD ]; then
    git cms-addpkg PhysicsTools/NanoAOD
fi
git checkout -- $CFF
scram b -j 8

echo "=== step 3: NANO without the fix"
grep -n "coll('hltEgammaCandidates')\"" $CFF
cd $OUT
run_nano nofix
cd $CMSSW_BASE/src

echo "=== step 4: apply the one-line fix"
sed -i "s#type(92) && pt > 15 && coll('hltEgammaCandidates')\"#type(92) \&\& pt > 15 \&\& (coll('hltEgammaCandidates') || coll('hltEgammaCandidatesUnseeded'))\"#" $CFF
git diff $CFF
CHANGED=$(git diff --numstat | awk '{print $1, $2}')
if [ "$CHANGED" != "1 1" ]; then
    echo "ERROR: expected exactly one changed line, got: $CHANGED"; exit 1
fi
scram b -j 8

echo "=== step 5: NANO with the fix"
cd $OUT
run_nano fix
ls -l $OUT/nano_nofix.root $OUT/nano_fix.root
echo "=== done $1"
