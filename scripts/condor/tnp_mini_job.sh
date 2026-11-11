#!/bin/bash
# One HTCondor job: MINIAOD tag-and-probe reference (tnp_miniaod.py) on one MINIAOD parent, read over xrootd.
# Only the JSON comes back.
# usage (from tnp_mini.sub): tnp_mini_job.sh <index> <MINIAOD LFN> [nanoprec]
set -eo pipefail
INDEX=$1
INPUT=$2
MODE=${3:-}                                     # "nanoprec": NanoAOD eta/phi precision, output tnp_<i>_mini_nanoprec.json
SUFFIX=${MODE:+_$MODE}
TOP=/eos/user/s/smahata/trigobj_check
echo "job $INDEX input $INPUT host $(hostname)"

source /cvmfs/cms.cern.ch/cmsset_default.sh
WORKDIR=$PWD
cd $TOP/cmssw/CMSSW_13_3_1_patch1/src
eval $(scramv1 runtime -sh)
cd $WORKDIR

python3 $TOP/tnp_miniaod.py root://cms-xrd-global.cern.ch/$INPUT v13data_${INDEX}_mini$SUFFIX tnp_${INDEX}_mini$SUFFIX.json $MODE 2>&1 \
    | grep -v "^Warning" | tail -40
echo "job $INDEX done"
