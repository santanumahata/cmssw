#!/bin/bash
# One HTCondor job: NANO without and with the fix from one MINIAOD file (dumped configurations, so jobs share no
# editable CMSSW area), then tag-and-probe on both. The NANO files stay on the node; only the two JSONs come back.
# usage (from tnp.sub): tnp_job.sh <index> <MINIAOD LFN>
set -eo pipefail
INDEX=$1
INPUT=$2
TOP=/eos/user/s/smahata/trigobj_check
CONFIGS=$TOP/condor_v13data
LCG=/cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
echo "job $INDEX input $INPUT host $(hostname)"

source /cvmfs/cms.cern.ch/cmsset_default.sh
WORKDIR=$PWD
cd $TOP/cmssw/CMSSW_13_3_1_patch1/src
eval $(scramv1 runtime -sh)
cd $WORKDIR

for t in nofix fix; do
    cat > run_$t.py <<EOF
import sys
sys.path.insert(0, "$CONFIGS")
from nano_${t}_dump import process
process.source.fileNames = ["root://cms-xrd-global.cern.ch/$INPUT"]
process.NANOAODoutput.fileName = "file:nano_$t.root"
process.maxEvents.input = -1
EOF
    cmsRun run_$t.py > cmsrun_$t.log 2>&1 || { tail -40 cmsrun_$t.log; exit 1; }
    echo "cmsRun $t done: $(ls -l nano_$t.root)"
done

# tag-and-probe in a clean environment: the LCG view and the CMSSW environment do not mix
for t in nofix fix; do
    env -i HOME="$HOME" PATH=/usr/bin:/bin bash -c \
        "source $LCG && python3 $TOP/tnp_unseeded.py nano_$t.root v13data_${INDEX}_$t tnp_${INDEX}_$t.json tnp_${INDEX}_$t" \
        | tail -40
done
echo "job $INDEX done"
