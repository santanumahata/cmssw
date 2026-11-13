# NanoAOD photon TrigObj fix: measurement, fix test and tag-and-probe — Quick Reference

**Detail:** `RUNBOOK-DETAIL.md` — expected output, gotchas, conventions, changelog.
**Where it runs:** lxplus (EL9) for steps 2-7a; locally for steps 1 (`kinit`), 8-12.

### 1. Log in and get a proxy (by me, by hand)
By hand: `kinit` locally, `voms-proxy-init` on lxplus; then
`export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms`.

### 2. Re-make NANO without and with the fix
```bash
bash scripts/make_fixed_nano.sh v13data
```

### 3. Count bits; check the no-fix NANO against the central file
```bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
cd /eos/user/s/smahata/trigobj_check
python3 measure_trigobj.py v13data_nofix /EGamma/Run2022D-22Sep2023-v1/MINIAOD \
  cmssw/v13data/nano_nofix.root nanoaod-trigobj-notes/results/fix_test/v13data_nano_nofix.json \
  root://cms-xrd-global.cern.ch//store/data/Run2022D/EGamma/NANOAOD/16Dec2023-v1/2550000/499b6a69-bd7e-4bce-bd6d-4ab4f250ea2d.root
```

### 4. Tag-and-probe on one NANO file (local check)
```bash
python3 tnp_unseeded.py <nano file> <label> <output json> <output png prefix>
python3 plot_tnp_compare.py <nofix json> <fix json> 30_22 "<title>" <output png>
```

### 5. Dump the two NANO configurations for HTCondor
```bash
T=/eos/user/s/smahata/trigobj_check; C=$T/condor_v13data; V=$T/cmssw/v13data
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd $T/cmssw/CMSSW_13_3_1_patch1/src && eval $(scramv1 runtime -sh)
mkdir -p $C
edmConfigDump $V/nano_fix_cfg.py > $C/nano_fix_dump.py
git checkout -- PhysicsTools/NanoAOD/python/triggerObjects_cff.py
scram b -j 8 > /dev/null 2>&1
git diff --numstat
edmConfigDump $V/nano_nofix_cfg.py > $C/nano_nofix_dump.py
diff $C/nano_nofix_dump.py $C/nano_fix_dump.py
```

### 6. Submit one job per MINIAOD parent
```bash
export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
D=/afs/cern.ch/user/s/smahata/tnp_condor_v13data
mkdir -p $D/logs && cd $D && chmod +x tnp_job.sh
dasgoclient -query='parent file=/store/data/Run2022D/EGamma/NANOAOD/16Dec2023-v1/2550000/499b6a69-bd7e-4bce-bd6d-4ab4f250ea2d.root' \
  | awk '{print NR-1, $1}' > inputs.txt
wc -l < inputs.txt
md5sum tnp_job.sh tnp.sub
condor_submit tnp.sub
```

### 7. Check the jobs, merge, plot
```bash
cd /afs/cern.ch/user/s/smahata/tnp_condor_v13data
ls tnp_*_nofix.json | wc -l; ls tnp_*_fix.json | wc -l
grep "return value" logs/condor.log | sort | uniq -c
grep -h "^bits" logs/job_*.out | sort | uniq -c
source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
S=/eos/user/s/smahata/trigobj_check
python3 $S/merge_tnp.py v13data_40files_nofix merged_nofix.json tnp_*_nofix.json
python3 $S/merge_tnp.py v13data_40files_fix merged_fix.json tnp_*_fix.json
python3 $S/plot_tnp_compare.py merged_nofix.json merged_fix.json 30_22 "Run2022D EGamma (40 files), Diphoton30_22 legs (Mass90/Mass95)" tnp_compare_30_22.png
python3 $S/plot_tnp_compare.py merged_nofix.json merged_fix.json 30_18 "Run2022D EGamma (40 files), Diphoton30_18 legs (low mass)" tnp_compare_30_18.png
```

### 7a. MiniAOD reference on the same 40 files
```bash
export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
D=/afs/cern.ch/user/s/smahata/tnp_condor_mini; S=/eos/user/s/smahata/trigobj_check
mkdir -p $D/logs && cd $D && chmod +x tnp_mini_job.sh
md5sum inputs.txt ../tnp_condor_v13data/inputs.txt
condor_submit tnp_mini.sub; condor_submit tnp_mini_nanoprec.sub
# after both clusters are empty:
grep "return value" logs/condor.log logs/condor_nanoprec.log | sort | uniq -c
source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
python3 $S/merge_tnp.py v13data_40files_mini merged_mini.json tnp_*_mini.json
python3 $S/merge_tnp.py v13data_40files_mini_nanoprec merged_mini_nanoprec.json tnp_*_mini_nanoprec.json
N=/afs/cern.ch/user/s/smahata/tnp_condor_v13data/merged_fix.json
python3 $S/plot_mini_vs_nano.py $N merged_mini.json 30_22 "Run2022D EGamma (40 files), Diphoton30_22 legs: MiniAOD vs fixed NanoAOD" mini_vs_nano_30_22.png
python3 $S/plot_mini_vs_nano.py $N merged_mini.json 30_18 "Run2022D EGamma (40 files), Diphoton30_18 legs: MiniAOD vs fixed NanoAOD" mini_vs_nano_30_18.png
```

### 8. Fetch results to the local clone
```bash
F=/afs/cern.ch/user/s/smahata/tnp_condor_v13data/merged_fix.json
remote=$(ssh smahata@lxplus.cern.ch "md5sum $F" | cut -d" " -f1)
ssh smahata@lxplus.cern.ch "cat $F" > results/tnp_2022D_v13_40files/merged_fix.json
md5sum results/tnp_2022D_v13_40files/merged_fix.json
```

### 9. Rebuild the decks
```bash
cd slides/beamer/src
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../outputs trigobj_unseeded.tex
pdflatex -interaction=nonstopmode -output-directory=../outputs trigobj_unseeded.tex
grep -c Overfull ../outputs/trigobj_unseeded.log
cd ../../..
export NODE_PATH=$MAMBA_ENV/lib/node_playwright/node_modules
/usr/bin/node scripts/render_deck.js slides/issue-deck-src slides/issue-deck
/usr/bin/node scripts/render_deck.js slides/detailed-deck-src slides/detailed-deck
/usr/bin/node scripts/render_pdf.js $PWD/report
```

### 10. Commit and push to the fork only
```bash
export NAME_PATTERN='<regex of the forbidden tool and vendor names; kept outside the repository>'
git add <files>
git grep -ciIE "$NAME_PATTERN"; for f in $(git ls-files '*.pdf'); do (pdftotext $f -; pdfinfo $f) | grep -ciE "$NAME_PATTERN"; done
git -c user.name=santanumahata -c user.email=santanuedu.m@gmail.com commit -m "<message, no attribution lines>"
git -c credential.helper='!f() { echo username=x-access-token; echo "password=$GH_TOKEN"; }; f' \
  push -q https://github.com/santanumahata/cmssw.git HEAD:refs/heads/nanoaod-trigobj-notes
git ls-remote https://github.com/santanumahata/cmssw.git refs/heads/nanoaod-trigobj-notes
```

### 11. Rewrite commit metadata to my identity (only if forbidden names got in)
Rare and destructive (backup bundle, `filter-branch`, lease push): run it from `RUNBOOK-DETAIL.md` step 11.

### 12. Prepare the PR: fix branch on current upstream master
```bash
S=SESSION_SCRATCH; N=$S/notes_repo
cd $S && git clone -q --depth 1 --filter=blob:none --sparse https://github.com/cms-sw/cmssw.git rebase_fix
cd rebase_fix
git sparse-checkout set PhysicsTools/NanoAOD/python
git config user.name santanumahata
git config user.email santanuedu.m@gmail.com
git fetch -q --depth 2 https://github.com/santanumahata/cmssw.git nano-photon-trigobj-unseeded
git cherry-pick FETCH_HEAD
git log -2 --format='%h %an <%ae> | %cn <%ce> | %s'
git diff --stat HEAD~1 HEAD
git -c credential.helper='!f(){ echo username=santanumahata; echo password=$GH_TOKEN; }; f' \
  push --force-with-lease=nano-photon-trigobj-unseeded:<old full sha> \
  https://github.com/santanumahata/cmssw.git HEAD:refs/heads/nano-photon-trigobj-unseeded
git ls-remote https://github.com/santanumahata/cmssw.git refs/heads/nano-photon-trigobj-unseeded
curl -s "https://api.github.com/repos/cms-sw/cmssw/compare/master...santanumahata:cmssw:nano-photon-trigobj-unseeded" \
 | python3 -c 'import json,sys; d=json.load(sys.stdin); print("status", d.get("status"), "ahead", d.get("ahead_by"), "behind", d.get("behind_by")); [print(f["filename"], "+%d -%d" % (f["additions"], f["deletions"])) for f in d.get("files", [])]'
git format-patch -1 HEAD --stdout > $N/pr/0001-NanoAOD-photon-TrigObj-unseeded-collection.patch
```
