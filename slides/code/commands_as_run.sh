# Shell commands I ran by hand for the 5 November 2026 checks, copied verbatim from the session log.
# They ran from my laptop; the work happened on lxplus over ssh. Not a script to execute as a whole.

# ===== 1. DAS lookups

# --- Query DAS for NanoAOD datasets per version pattern
ssh -o BatchMode=yes lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  for p in \
    "/EGamma/Run2018*-UL2018_MiniAODv2_NanoAODv9*/NANOAOD" \
    "/EGamma/Run2022*-PromptNanoAODv10*/NANOAOD" \
    "/EGamma/Run2022*-PromptNanoAODv11*/NANOAOD" \
    "/EGamma/Run2022*-22Sep2023-v*/NANOAOD" \
    "/GluGluHtoGG*/Run3Summer22*NanoAODv12*/NANOAODSIM" \
    "/EGamma/Run2022*-16Dec2023-v*/NANOAOD" \
    "/GluGluHto*G*/Run3Summer23NanoAODv13*/NANOAODSIM" \
    "/EGamma*/Run2024*-PromptReco-v*/NANOAOD" \
    "/GluGluHto*G*/*NanoAODv14*/NANOAODSIM" \
    "/GluGluHto*G*/Run3Summer2*NanoAODv15*/NANOAODSIM" \
    "/EGamma*/Run202*NanoAODv15*/NANOAOD"
  do echo "== $p"; dasgoclient -query="dataset=$p" 2>&1 | head -8; done' 2>&1 | grep -v '^\*'

# --- Query DAS with wider v14/v15 patterns
ssh -o BatchMode=yes lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  for p in \
    "/GluGluH*G*/*NanoAODv14*/NANOAODSIM" \
    "/GluGluH*G*/Run3Summer24*/NANOAODSIM" \
    "/GluGluH*G*/*NanoAODv15*/NANOAODSIM" \
    "/EGamma*/Run2024*NanoAODv15*/NANOAOD"
  do echo "== $p"; dasgoclient -query="dataset=$p" 2>&1 | head -8; done' 2>&1 | grep -v '^\*'

# --- Get first file LFN for each chosen dataset
ssh -o BatchMode=yes lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  for d in \
    /EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD \
    /EGamma/Run2022D-PromptNanoAODv10_v2-v1/NANOAOD \
    /EGamma/Run2022F-PromptNanoAODv11_v1-v2/NANOAOD \
    /GluGluHtoGG_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM \
    /EGamma/Run2022D-22Sep2023-v1/NANOAOD \
    /GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv13-133X_mcRun3_2023_realistic_ForNanov13_v1_ext1-v4/NANOAODSIM \
    /EGamma/Run2022D-16Dec2023-v1/NANOAOD \
    /EGamma0/Run2024D-PromptReco-v1/NANOAOD \
    /GluGluH-Hto2G_Par-M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM \
    /EGamma/Run2022D-NanoAODv15-v1/NANOAOD
  do echo "== $d"; dasgoclient -query="file dataset=$d" 2>&1 | head -1; done' 2>&1 | grep -v '^\*'

# --- Look up DAS datasets needed for tasks A, B, C
ssh -o BatchMode=yes lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  for p in \
    "/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM" \
    "/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4*/MINIAODSIM" \
    "/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv1*/NANOAODSIM" \
    "/GluGluHto*G*/Run3Summer23NanoAODv15*/NANOAODSIM" \
    "/EGamma0/Run2024*-MINIv6NANOv15-v*/NANOAOD" \
    "/GluGluHtoGG*/*Winter24*NanoAOD*/NANOAODSIM"
  do echo "== $p"; dasgoclient -query="dataset=$p" 2>&1 | head -6; done' 2>&1 | grep -v '^\*'

# --- Check MiniAOD dataset status, central-file parent, wider patterns
ssh -o BatchMode=yes lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  for d in /GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM /GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v15_ext1-v4/MINIAODSIM; do
    echo "== $d"; dasgoclient -query="dataset dataset=$d status=*" -json 2>/dev/null | grep -o "\"dataset_access_type\":\"[A-Z]*\"" | head -1; dasgoclient -query="summary dataset=$d" 2>&1 | head -2; done
  echo "== parent of central v13 file"
  dasgoclient -query="parent file=/store/mc/Run3Summer23NanoAODv13/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/133X_mcRun3_2023_realistic_ForNanov13_v1_ext1-v4/2820000/4f45fe87-a958-4c8f-b88f-c322fec857f3.root"
  for p in "/*/Run3Summer23NanoAODv15*/NANOAODSIM" "/GluGluH*/*Winter24*/NANOAODSIM" "/*/RunIII2024Winter24NanoAOD*/NANOAODSIM"; do echo "== $p"; dasgoclient -query="dataset=$p" 2>&1 | head -4; done' 2>&1 | grep -v '^\*'

# --- Get first file of 2024D MINIv6NANOv15 and Winter24 datasets
ssh -o BatchMode=yes -o ConnectTimeout=30 lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  for d in /EGamma0/Run2024D-MINIv6NANOv15-v1/NANOAOD /GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Winter24NanoAOD-133X_mcRun3_2024_realistic_v9-v2/NANOAODSIM; do
    echo "== $d"; dasgoclient -query="file dataset=$d" | head -1; done' 2>&1 | grep -v '^\*'

# --- Check DAS sites and IB EOS cache for the RAW file
timeout 120 ssh -o BatchMode=yes -o ConnectTimeout=30 lxplus.cern.ch 'export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms; F=/store/data/Run2023D/EGamma0/RAW/v1/000/369/978/00000/0068cd83-0af4-4efc-9155-b2521e558ebb.root; echo "== DAS sites"; dasgoclient -query="site file=$F"; echo "== ibeos cache"; ls -la /eos/cms/store/user/cmsbuild$F 2>&1 | head -2; ls /eos/cms/store/user/cmsbuild/store/data/Run2023D/EGamma0/RAW/v1/000/369/978/00000/ 2>&1 | head -3' 2>&1 | grep -v '^\*'

# --- Check which 141.046 input files exist in IB EOS cache
timeout 120 ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ConnectTimeout=30 smahata@lxplus967.cern.ch 'cd /eos/user/s/smahata/trigobj_check/relval_16_1_3/run_clean/141.046_*; wc -l < step1_dasquery.log; cat step1_lumiRanges.log | head -c 300; echo; for f in $(cat step1_dasquery.log); do if [ -f /eos/cms/store/user/cmsbuild$f ]; then echo "cached $f"; else echo "missing $f"; fi; done | sort | uniq -c -w 7 | head; ls /eos/cms/store/user/cmsbuild/store/data/Run2023D/EGamma0/RAW/v1/000/369/978/00000/ | wc -l' 2>&1 | grep -v '^\*'

# ===== 2. Measuring the NanoAOD files

# --- Copy script to lxplus and run v13 smoke test
cd <session folder> && scp -q -o BatchMode=yes measure_trigobj.py lxplus.cern.ch:/eos/user/s/smahata/trigobj_check/ 2>&1 | grep -v '^\*'; ssh -o BatchMode=yes lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
  cd /eos/user/s/smahata/trigobj_check
  mkdir -p nanoaod-trigobj-notes/results
  python3 measure_trigobj.py v13 \
    /GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv13-133X_mcRun3_2023_realistic_ForNanov13_v1_ext1-v4/NANOAODSIM \
    root://cms-xrd-global.cern.ch//store/mc/Run3Summer23NanoAODv13/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/133X_mcRun3_2023_realistic_ForNanov13_v1_ext1-v4/2820000/4f45fe87-a958-4c8f-b88f-c322fec857f3.root \
    nanoaod-trigobj-notes/results/v13_GluGluHto2G_M125_Run3Summer23.json' 2>&1 | grep -v '^\*'

# --- Run measurement on the remaining 9 NanoAOD files
ssh -o BatchMode=yes lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
  cd /eos/user/s/smahata/trigobj_check
  R=root://cms-xrd-global.cern.ch/
  run() { echo "##### $1 $4"; python3 measure_trigobj.py "$1" "$2" "$R$3" "nanoaod-trigobj-notes/results/$4.json" 2>&1 | grep -E "WARNING|Error|error|\"(events_read|filterBits_interpretation|n_photon_bits_documented|fired_Mass90|fired_DoubleEle33_CaloIdL_MW|electron_CaloIdL_MW_unseeded_bit|electrons_with_CaloIdL_MW_unseeded_bit|n_id2_MET|n_id1515_BoostedTau|n_id22_Photon|events_with_unseeded_photon_bit)\""; }
  run v9  /EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD /store/data/Run2018D/EGamma/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v3/250000/566E12C7-CD3E-3F4D-A657-A71FF4CB2637.root v9_EGamma_Run2018D_UL2018NanoAODv9
  run v10 /EGamma/Run2022D-PromptNanoAODv10_v2-v1/NANOAOD /store/data/Run2022D/EGamma/NANOAOD/PromptNanoAODv10_v2-v1/2520000/3f1fe826-1729-4ba9-83b9-d28a2cfd2b88.root v10_EGamma_Run2022D_PromptNanoAODv10
  run v11 /EGamma/Run2022F-PromptNanoAODv11_v1-v2/NANOAOD /store/data/Run2022F/EGamma/NANOAOD/PromptNanoAODv11_v1-v2/80000/6d07f113-b587-45b3-8db6-c2928358ae0b.root v11_EGamma_Run2022F_PromptNanoAODv11
  run v12 /GluGluHtoGG_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM /store/mc/Run3Summer22NanoAODv12/GluGluHtoGG_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/130X_mcRun3_2022_realistic_v5-v2/2530000/fd1a30c4-ac59-4c33-8245-719b82fad9f0.root v12_GluGluHtoGG_M125_Run3Summer22
  run v12 /EGamma/Run2022D-22Sep2023-v1/NANOAOD /store/data/Run2022D/EGamma/NANOAOD/22Sep2023-v1/2530000/e5762711-8726-4523-8891-32efa9ddb381.root v12_EGamma_Run2022D_22Sep2023
  run v13 /EGamma/Run2022D-16Dec2023-v1/NANOAOD /store/data/Run2022D/EGamma/NANOAOD/16Dec2023-v1/2550000/499b6a69-bd7e-4bce-bd6d-4ab4f250ea2d.root v13_EGamma_Run2022D_16Dec2023
  run v14 /EGamma0/Run2024D-PromptReco-v1/NANOAOD /store/data/Run2024D/EGamma0/NANOAOD/PromptReco-v1/000/380/306/00000/9bfae790-c112-48bf-bc54-ef1feaa74a96.root v14_EGamma0_Run2024D_PromptReco
  run v15 /GluGluH-Hto2G_Par-M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM /store/mc/RunIII2024Summer24NanoAODv15/GluGluH-Hto2G_Par-M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/150X_mcRun3_2024_realistic_v2-v2/120000/acebfb52-a25b-48bc-b9f6-80fe54a98d56.root v15_GluGluHHto2G_M125_RunIII2024Summer24
  run v15 /EGamma/Run2022D-NanoAODv15-v1/NANOAOD /store/data/Run2022D/EGamma/NANOAOD/NanoAODv15-v1/2820000/41628bc7-c70f-4bf7-b2a4-e755aea819fd.root v15_EGamma_Run2022D_NanoAODv15
  echo ALLDONE' 2>&1 | grep -v '^\*'

# --- Measure 2024D MINIv6NANOv15 and Winter24 files
ssh -o BatchMode=yes -o ServerAliveInterval=15 lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
  cd /eos/user/s/smahata/trigobj_check
  R=root://cms-xrd-global.cern.ch/
  K="events_read|events_in_file|filterBits_interpretation|n_photon_bits_documented|fired_Mass90|photons_with_bit|R9|TrackIso|EG18|seeded|hltHtEcal|electron_CaloIdL|electrons_with|n_id2|n_id1515|n_id22|events_with_unseeded|nTrigObj_mean|file_size|WARNING|NOTE|Error"
  python3 measure_trigobj.py v15 /EGamma0/Run2024D-MINIv6NANOv15-v1/NANOAOD $R/store/data/Run2024D/EGamma0/NANOAOD/MINIv6NANOv15-v1/110000/9d4e97c7-f23a-4cff-ac72-58488e544076.root nanoaod-trigobj-notes/results/v15_EGamma0_Run2024D_MINIv6NANOv15.json 2>&1 | grep -E "$K" | head -40
  echo "#####"
  python3 measure_trigobj.py Winter24_133X /GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Winter24NanoAOD-133X_mcRun3_2024_realistic_v9-v2/NANOAODSIM $R/store/mc/Run3Winter24NanoAOD/GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8/NANOAODSIM/133X_mcRun3_2024_realistic_v9-v2/80000/68618af9-2d38-4ef7-9aa9-2d0c30a6e3f1.root nanoaod-trigobj-notes/results/Winter24_133X_GluGluHToGG_M125_powheg.json 2>&1 | grep -E "$K" | head -40' 2>&1 | grep -v '^\*'

# ===== 3. Fix test, v13 and v15

# --- Copy scripts and start NANO runs on lxplus967 as smahata
cd <session folder> && O="-o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ServerAliveInterval=15"; scp -q $O make_fixed_nano.sh measure_trigobj.py smahata@lxplus967.cern.ch:/eos/user/s/smahata/trigobj_check/ 2>&1 | grep -v '^\*'; ssh $O smahata@lxplus967.cern.ch 'cd /eos/user/s/smahata/trigobj_check && nohup bash -c "bash make_fixed_nano.sh v13; bash make_fixed_nano.sh v15" > make_fixed_nano.log 2>&1 < /dev/null & sleep 8; hostname; head -5 /eos/user/s/smahata/trigobj_check/make_fixed_nano.log' 2>&1 | grep -v '^\*'

# --- Rerun v13 nano_fix cmsRun on lxplus967 in held-open session
ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ServerAliveInterval=30 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  cd /eos/user/s/smahata/trigobj_check/cmssw/CMSSW_13_3_1_patch1/src && eval $(scramv1 runtime -sh)
  git diff --numstat
  cd /eos/user/s/smahata/trigobj_check/cmssw/v13
  echo "=== v13 nano_fix rerun start $(date)"
  cmsRun nano_fix_cfg.py > nano_fix_rerun.log 2>&1
  echo "=== v13 nano_fix rerun exit $? $(date)"
  ls -l nano_nofix.root nano_fix.root' 2>&1 | grep -v '^\*'

# --- Run v15 fix-test NANO pair on another lxplus node
ssh -o BatchMode=yes -o ServerAliveInterval=30 lxplus.cern.ch 'hostname; cd /eos/user/s/smahata/trigobj_check && bash make_fixed_nano.sh v15 > make_fixed_nano_v15.log 2>&1; echo "v15 exit $? $(date)"; grep -E "^=== |^ERROR:|^[0-9]+: +sel|^[-+] +sel" make_fixed_nano_v15.log' 2>&1 | grep -v '^\*'

# --- Measure central v13 file into fix_test results
ssh -o BatchMode=yes -o ServerAliveInterval=30 lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
  cd /eos/user/s/smahata/trigobj_check && mkdir -p nanoaod-trigobj-notes/results/fix_test
  python3 measure_trigobj.py v13_central /GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv13-133X_mcRun3_2023_realistic_ForNanov13_v1_ext1-v4/NANOAODSIM root://cms-xrd-global.cern.ch//store/mc/Run3Summer23NanoAODv13/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/133X_mcRun3_2023_realistic_ForNanov13_v1_ext1-v4/2820000/4f45fe87-a958-4c8f-b88f-c322fec857f3.root nanoaod-trigobj-notes/results/fix_test/central_v13.json 2>&1 | grep -E "events_read|fired_Mass90|nTrigObj_mean|file_size|events_with_unseeded|fraction|photons_per|Error|WARN"' 2>&1 | grep -v '^\*'

# --- Measure v13 nano_nofix and nano_fix with references
ssh -o BatchMode=yes -o ServerAliveInterval=30 lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
  cd /eos/user/s/smahata/trigobj_check; V=cmssw/v13; O=nanoaod-trigobj-notes/results/fix_test
  CENTRAL=root://cms-xrd-global.cern.ch//store/mc/Run3Summer23NanoAODv13/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/NANOAODSIM/133X_mcRun3_2023_realistic_ForNanov13_v1_ext1-v4/2820000/4f45fe87-a958-4c8f-b88f-c322fec857f3.root
  K="events_read|fired_Mass90|R9|TrackIso|EG18|seeded|hltHtEcal|nTrigObj_mean|file_size|events_with_unseeded|fraction|photons_per|n_id22|\"n\"|min|median|below|reference|events_in|identical|Error|WARN|NOTE"
  python3 measure_trigobj.py v13_nofix MiniAOD-parent-of-central-v13 $V/nano_nofix.root $O/nano_nofix.json $CENTRAL 2>&1 | grep -E "$K"
  echo "#####"
  python3 measure_trigobj.py v13_fix MiniAOD-parent-of-central-v13 $V/nano_fix.root $O/nano_fix.json $V/nano_nofix.root 2>&1 | grep -E "$K"
  python3 -c "import json; a=json.load(open(\"$O/nano_nofix.json\")); b=json.load(open(\"$O/nano_fix.json\")); print(\"objects_per_id nofix\", a[\"objects_per_id\"]); print(\"objects_per_id fix  \", b[\"objects_per_id\"]); print(\"id!=22 bit counts identical:\", a[\"bit_counts_per_id_without_22\"]==b[\"bit_counts_per_id_without_22\"])"' 2>&1 | grep -v '^\*'

# --- Measure v15 nano_nofix and nano_fix
ssh -o BatchMode=yes -o ServerAliveInterval=30 lxplus.cern.ch '
  export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
  cd /eos/user/s/smahata/trigobj_check; V=cmssw/v15; O=nanoaod-trigobj-notes/results/fix_test
  ls -l $V/*.root
  K="events_read|events_in_file|interpretation|n_photon_bits|fired_Mass90|R9|TrackIso|EG18|seeded|hltHtEcal|nTrigObj_mean|file_size|events_with_unseeded|fraction|photons_per|n_id22|\"n\"|min|median|below|events_in|identical|Error|WARN|NOTE"
  python3 measure_trigobj.py v15_nofix MiniAOD-parent-of-central-v13 $V/nano_nofix.root $O/v15_nano_nofix.json 2>&1 | grep -E "$K"
  echo "#####"
  python3 measure_trigobj.py v15_fix MiniAOD-parent-of-central-v13 $V/nano_fix.root $O/v15_nano_fix.json $V/nano_nofix.root 2>&1 | grep -E "$K"
  python3 -c "import json; a=json.load(open(\"$O/v15_nano_nofix.json\")); b=json.load(open(\"$O/v15_nano_fix.json\")); print(\"objects_per_id nofix\", a[\"objects_per_id\"]); print(\"objects_per_id fix  \", b[\"objects_per_id\"]); print(\"id!=22 bit counts identical:\", a[\"bit_counts_per_id_without_22\"]==b[\"bit_counts_per_id_without_22\"])"' 2>&1 | grep -v '^\*'

# ===== 4. Relval in CMSSW_16_1_3

# --- List the five relval workflows in CMSSW_16_1_3
ssh -o BatchMode=yes -o ConnectTimeout=30 -o ServerAliveInterval=15 lxplus.cern.ch 'source /cvmfs/cms.cern.ch/cmsset_default.sh
  cd /cvmfs/cms.cern.ch/el9_amd64_gcc13/cms/cmssw/CMSSW_16_1_3/src && eval $(scramv1 runtime -sh)
  mkdir -p /tmp/smahata_rtm && cd /tmp/smahata_rtm && runTheMatrix.py -n -e -l 12452.0,12852.0,12434.0,12834.0,141.046 2>&1 | grep -v "^$" | cut -c1-400 | head -60' 2>&1 | grep -v '^\*'

# --- List relval workflows with upgrade and default matrices
ssh -o BatchMode=yes -o ConnectTimeout=30 -o ServerAliveInterval=15 lxplus.cern.ch 'source /cvmfs/cms.cern.ch/cmsset_default.sh
  cd /cvmfs/cms.cern.ch/el9_amd64_gcc13/cms/cmssw/CMSSW_16_1_3/src && eval $(scramv1 runtime -sh)
  mkdir -p /tmp/smahata_rtm && cd /tmp/smahata_rtm
  echo "##### upgrade 12452/12852"; runTheMatrix.py -n -e -w upgrade -l 12452.0,12852.0 2>&1 | grep -v "^processing\|^ignoring\|^$" | cut -c1-300 | head -30
  echo "##### default 12434/12834/141.046"; runTheMatrix.py -n -e -l 12434.0,12834.0,141.046 2>&1 | grep -v "^processing\|^ignoring\|^$" | cut -c1-300 | head -40' 2>&1 | grep -v '^\*'

# --- Run relval check with cached RAW file for 141.046
ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ServerAliveInterval=30 smahata@lxplus967.cern.ch 'cd /eos/user/s/smahata/trigobj_check && nohup bash relval_fix_check.sh > relval_fix_check.log 2>&1 < /dev/null; echo "relval exit code $?"; grep -E "^=== |^ERROR:|tests passed|Step[0-9]-|^[0-9]+\s+[0-9]+\s+Phys|exceptions|Fatal" relval_fix_check.log | cut -c1-250' 2>&1 | grep -v '^\*'

# --- Dry-run 141.046 to get full step3/step4 commands
timeout 300 ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ConnectTimeout=30 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh; export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  cd /eos/user/s/smahata/trigobj_check/relval_16_1_3/clean/src && eval $(scramv1 runtime -sh)
  mkdir -p /tmp/smahata_dry && cd /tmp/smahata_dry && rm -rf 141.046_*
  runTheMatrix.py -l 141.046 -i all --ibeos --dryRun > dry.log 2>&1
  grep -E "cmsDriver.py step[34] " 141.046_*/cmdLog' 2>&1 | grep -v '^\*'

# --- Run clean 141.046 steps 3-4 then the rest of relval script
ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ServerAliveInterval=30 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh; export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  cd /eos/user/s/smahata/trigobj_check/relval_16_1_3/clean/src && eval $(scramv1 runtime -sh)
  cd /eos/user/s/smahata/trigobj_check/relval_16_1_3/run_clean/141.046_*
  grep -E "cmsDriver.py step[34] " /tmp/smahata_dry/141.046_*/cmdLog > steps34_from_dryrun.sh
  echo "# steps 3-4 below taken from runTheMatrix --dryRun (aborted run had not written them)" >> cmdLog
  cat steps34_from_dryrun.sh >> cmdLog
  echo "=== clean 141.046 steps 3-4 start $(date)"
  bash steps34_from_dryrun.sh; echo "steps34 exit $?"
  ls -l step3_inNANOEDMAOD.root step3_inDQM.root DQM_V0001*.root
  cd /eos/user/s/smahata/trigobj_check
  bash relval_fix_check.sh > relval_fix_check.log 2>&1; echo "relval exit code $? $(date)"
  grep -E "^=== |^ERROR:|^[0-9]+\s+[0-9]+\s+Phys|exceptions" relval_fix_check.log | cut -c1-250' 2>&1 | grep -v '^\*'

# --- Rerun 141.046 steps 3-4 in the fix area
ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ServerAliveInterval=30 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh; export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  W=/eos/user/s/smahata/trigobj_check/relval_16_1_3
  cd $W/fix/src && eval $(scramv1 runtime -sh) && git diff CMSSW_16_1_3 --numstat
  cd $W/run_fix/141.046_RunEGamma2023D
  cp $W/run_clean/141.046_RunEGamma2023D/steps34_from_dryrun.sh .
  echo "=== fix 141.046 steps 3-4 start $(date)"
  bash steps34_from_dryrun.sh; echo "=== fix 141.046 steps 3-4 exit $? $(date)"
  ls -l step3_inNANOEDMAOD.root DQM_V0001*.root' 2>&1 | grep -v '^\*'

# --- Convert, measure and compare 12452.0 clean vs fix
timeout 900 ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ConnectTimeout=60 -o ServerAliveInterval=30 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh; export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
  W=/eos/user/s/smahata/trigobj_check/relval_16_1_3; T=/eos/user/s/smahata/trigobj_check
  for AREA in clean fix; do
    (cd $W/$AREA/src && eval $(scramv1 runtime -sh) && cd $W/run_$AREA/12452.0_* && \
     cmsDriver.py flat --step NONE --mc --conditions auto:phase1_2023_realistic --era Run3_2023 \
       --filein file:step3_inNANOEDMAODSIM.root --fileout file:step3_flatNANOAODSIM.root \
       --eventcontent NANOAODSIM --datatier NANOAODSIM -n -1 > flat_nano.log 2>&1; echo "$AREA flat exit $?"; ls -l step3_flatNANOAODSIM.root)
  done
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
  O=$T/nanoaod-trigobj-notes/results/relval_16_1_3; mkdir -p $O
  C=$(ls $W/run_clean/12452.0_*/step3_flatNANOAODSIM.root); F=$(ls $W/run_fix/12452.0_*/step3_flatNANOAODSIM.root)
  cd $T
  python3 measure_trigobj.py 16_1_3_clean wf12452.0 $C $O/wf12452_clean.json 2>&1 | grep -E "events_read|fired_Mass90|n_photon_bits|n_id22|events_with_unseeded|fraction|nTrigObj_mean|Error"
  python3 measure_trigobj.py 16_1_3_fix wf12452.0 $F $O/wf12452_fix.json $C 2>&1 | grep -E "events_read|fired_Mass90|R9Unseeded|TrackIsoUnseeded|n_id22|events_with_unseeded|fraction|nTrigObj_mean|min|identical|Error"
  python3 -c "import json; a=json.load(open(\"$O/wf12452_clean.json\")); b=json.load(open(\"$O/wf12452_fix.json\")); print(\"ids clean\", a[\"objects_per_id\"]); print(\"ids fix  \", b[\"objects_per_id\"]); print(\"id!=22 bits identical:\", a[\"bit_counts_per_id_without_22\"]==b[\"bit_counts_per_id_without_22\"]); print(\"photon bits clean\", a[\"photons_with_bit\"]); print(\"photon bits fix  \", b[\"photons_with_bit\"])"
  python3 compare_dqm.py $(ls $W/run_clean/12452.0_*/DQM_V0001*.root) $(ls $W/run_fix/12452.0_*/DQM_V0001*.root) $O/wf12452_dqm_diff.json 2>&1 | head -60
  echo "--- logs"
  for A in clean fix; do L=$(ls $W/run_$A/12452.0_*/step3_*.log); echo "$A step3: Exception lines $(grep -c Exception $L), triggerObjectTable lines $(grep -c triggerObjectTable $L)"; grep triggerObjectTable $L | head -3; done
  L=$(ls $W/run_clean/141.046_*/step3_*.log); echo "clean 141.046 step3: Exception lines $(grep -c Exception $L), triggerObjectTable lines $(grep -c triggerObjectTable $L)"' 2>&1 | grep -v '^\*' | cut -c1-300

# --- Rerun 12452.0 DQM comparison without time limit
ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ServerAliveInterval=30 smahata@lxplus967.cern.ch '
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
  W=/eos/user/s/smahata/trigobj_check/relval_16_1_3; T=/eos/user/s/smahata/trigobj_check
  cd $T && echo "start $(date)"
  python3 compare_dqm.py $(ls $W/run_clean/12452.0_*/DQM_V0001*.root) $(ls $W/run_fix/12452.0_*/DQM_V0001*.root) nanoaod-trigobj-notes/results/relval_16_1_3/wf12452_dqm_diff.json > /dev/null 2>&1; echo "exit $? $(date)"
  python3 -c "import json; d=json.load(open(\"nanoaod-trigobj-notes/results/relval_16_1_3/wf12452_dqm_diff.json\")); print(d[\"n_histograms_clean\"], d[\"n_histograms_fix\"], len(d[\"only_in_clean\"]), len(d[\"only_in_fix\"]), len(d[\"differing\"])); print(\"\n\".join(d[\"differing\"][:40]))"' 2>&1 | grep -v '^\*'

# --- Convert and measure clean 141.046 NANO
timeout 1200 ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ConnectTimeout=60 -o ServerAliveInterval=30 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh; W=/eos/user/s/smahata/trigobj_check/relval_16_1_3; T=/eos/user/s/smahata/trigobj_check
  (cd $W/clean/src && eval $(scramv1 runtime -sh) && cd $W/run_clean/141.046_RunEGamma2023D && \
   cmsDriver.py flat --step NONE --data --conditions auto:run3_data_relval --era Run3_2023 \
     --filein file:step3_inNANOEDMAOD.root --fileout file:step3_flatNANOAOD.root \
     --eventcontent NANOAOD --datatier NANOAOD -n -1 > flat_nano.log 2>&1; echo "flat exit $?"; ls -l step3_flatNANOAOD.root)
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh; cd $T
  python3 measure_trigobj.py 16_1_3_clean wf141.046 $W/run_clean/141.046_RunEGamma2023D/step3_flatNANOAOD.root nanoaod-trigobj-notes/results/relval_16_1_3/wf141046_clean.json 2>&1 | grep -E "events_read|n_photon_bits|fired_Mass90|R9Unseeded|TrackIsoUnseeded|seeded_|n_id22|events_with_unseeded|nTrigObj_mean|Error"' 2>&1 | grep -v '^\*'

# --- Convert, measure, check logs and DQM for 141.046 fix
ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ServerAliveInterval=30 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh; W=/eos/user/s/smahata/trigobj_check/relval_16_1_3; T=/eos/user/s/smahata/trigobj_check; O=$T/nanoaod-trigobj-notes/results/relval_16_1_3
  (cd $W/fix/src && eval $(scramv1 runtime -sh) && cd $W/run_fix/141.046_RunEGamma2023D && \
   cmsDriver.py flat --step NONE --data --conditions auto:run3_data_relval --era Run3_2023 \
     --filein file:step3_inNANOEDMAOD.root --fileout file:step3_flatNANOAOD.root \
     --eventcontent NANOAOD --datatier NANOAOD -n -1 > flat_nano.log 2>&1; echo "flat exit $?")
  L=$W/run_fix/141.046_RunEGamma2023D/step3_RunEGamma2023D.log; echo "fix 141.046 step3: Exception $(grep -c Exception $L), triggerObjectTable $(grep -c triggerObjectTable $L), events $(grep -c "Begin processing" $L)"
  L=$W/run_clean/141.046_RunEGamma2023D/step3_RunEGamma2023D.log; echo "clean 141.046 step3 events $(grep -c "Begin processing" $L)"
  source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh; cd $T
  python3 measure_trigobj.py 16_1_3_fix wf141.046 $W/run_fix/141.046_RunEGamma2023D/step3_flatNANOAOD.root $O/wf141046_fix.json $W/run_clean/141.046_RunEGamma2023D/step3_flatNANOAOD.root 2>&1 | grep -E "events_read|fired_Mass90|n_id22|events_with_unseeded|nTrigObj_mean|events_in|identical|Error"
  python3 compare_dqm.py $W/run_clean/141.046_RunEGamma2023D/DQM_V0001*.root $W/run_fix/141.046_RunEGamma2023D/DQM_V0001*.root $O/wf141046_dqm_diff.json > /dev/null 2>&1; echo "dqm exit $?"
  python3 -c "import json; d=json.load(open(\"$O/wf141046_dqm_diff.json\")); print(d[\"n_histograms_clean\"], d[\"n_histograms_fix\"], len(d[\"only_in_clean\"]), len(d[\"only_in_fix\"]), len(d[\"differing\"])); print(\"\n\".join(x for x in d[\"differing\"] if \"TimerService\" not in x)[:3000])"' 2>&1 | grep -v '^\*'

# --- Inspect trigger products in 141.046 MINIAOD and NANO
timeout 600 ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ConnectTimeout=60 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh; W=/eos/user/s/smahata/trigobj_check/relval_16_1_3
  cd $W/clean/src && eval $(scramv1 runtime -sh) && cd $W/run_clean/141.046_RunEGamma2023D
  echo "== MINIAOD trigger products"; edmEventSize -v step3_inMINIAOD.root 2>/dev/null | grep -iE "trigger|TriggerResults" | head
  echo "== EDM NANO TrigObj"; edmEventSize -v step3_inNANOEDMAOD.root 2>/dev/null | grep -iE "trig" | head
  echo "== cfg"; grep -nE "unpackedPatTrigger|patTrigger\b|triggerResults|hltProcess|slimmedPatTrigger" step3_RAW2DIGI*.py 2>/dev/null | head; ls *.py' 2>&1 | grep -v '^\*' | cut -c1-200

# --- Check HLT trigger summary products in relval outputs
timeout 600 ssh -o BatchMode=yes -o HostKeyAlias=lxplus.cern.ch -o ConnectTimeout=60 smahata@lxplus967.cern.ch '
  source /cvmfs/cms.cern.ch/cmsset_default.sh; W=/eos/user/s/smahata/trigobj_check/relval_16_1_3
  cd $W/clean/src && eval $(scramv1 runtime -sh) && cd $W/run_clean/141.046_RunEGamma2023D
  echo "== step2 (reHLT output) trigger summary products"; edmEventSize -v step2.root 2>/dev/null | grep -iE "TriggerEvent|hltTriggerSummary|TriggerResults" | head
  echo "== step3 AOD"; edmEventSize -v step3.root 2>/dev/null | grep -iE "TriggerEvent|hltTriggerSummary" | head
  cd $W/run_clean/12452.0_*; echo "== 12452 step2"; edmEventSize -v step2.root 2>/dev/null | grep -iE "TriggerEvent|hltTriggerSummary" | head; echo "== 12452 MINIAOD"; edmEventSize -v step3_inMINIAODSIM.root 2>/dev/null | grep -iE "slimmedPatTrigger" | head -3' 2>&1 | grep -v '^\*' | cut -c1-200

# ===== 5. HiggsDNA photon-bit usage

# --- Shallow-clone HiggsDNA repos and grep TrigObj usage
D=<scratch>/higgsdna_src; mkdir -p $D; cd $D; timeout 200 git clone -q --depth 1 https://gitlab.cern.ch/cms-analysis/general/HiggsDNA.git HiggsDNA 2>&1 | tail -2; timeout 200 git clone -q --depth 1 https://github.com/ZhenyuDongLL/HiggsDNA-bbggrun3.git bbgg 2>&1 | tail -2; git -C HiggsDNA log --oneline -1 | cat; git -C bbgg log --oneline -1 | cat; grep -rn --include=*.py --include=*.json -E "trigger_match|TrigObj|filterBits" HiggsDNA | grep -v "^HiggsDNA/tests/data" | cut -c1-220 | head -60

# --- Read HiggsDNA trigger-matching code and search bbgg fork
cd <scratch>/higgsdna_src; sed -n 230,262p HiggsDNA/higgs_dna/workflows/dystudies.py; echo ----; sed -n 300,325p HiggsDNA/higgs_dna/utils/misc_utils.py; echo ----; sed -n 630,645p HiggsDNA/higgs_dna/workflows/lowmass.py; echo ---- bbgg; grep -rn --include=*.py -E "trigger_match|TrigObj|filterBits" bbgg | cut -c1-200 | head -20; echo ---- other trig refs; grep -rln --include=*.py -iE "Diphoton30_22|hltEG22|Unseeded" HiggsDNA bbgg | head

# --- Show diphoton-trigger references in HiggsDNA systematics
cd <scratch>/higgsdna_src; grep -n -iE "Diphoton30_22|hltEG22|Unseeded" HiggsDNA/higgs_dna/systematics/event_weight_systematics.py HiggsDNA/higgs_dna/scripts/pull_files.py | cut -c1-200 | head -12
