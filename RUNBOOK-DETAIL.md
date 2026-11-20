# NanoAOD photon TrigObj fix: measurement, fix test and tag-and-probe — Runbook (detail)

**Last updated:** 2026-11-20
**Card:** `RUNBOOK.md` — commands only.
**Where it runs:** lxplus (EL9), work area `/eos/user/s/smahata/trigobj_check/`, HTCondor submit directory
`/afs/cern.ch/user/s/smahata/tnp_condor_v13data/`; 2023 closure in `/eos/user/s/smahata/nano3018_test/`, submit
directory `~/closure_2023_condor/` on lxplus9108; notes, decks and git on the local machine.

## Overview
I re-make NanoAOD from MINIAOD without and with the one-line Photon-selection fix
(`scripts/make_fixed_nano.sh`), count the photon TrigObj bits on central and re-made files
(`scripts/measure_trigobj.py`), and measure the Diphoton30_22 and Diphoton30_18 leg efficiencies with Z->ee
tag-and-probe (`scripts/tnp_unseeded.py`): one file locally, or all 40 MINIAOD parents of one central v13
NanoAOD file on HTCondor (`scripts/condor/`), then merge (`scripts/merge_tnp.py`) and overlay
(`scripts/plot_tnp_compare.py`); the same tag-and-probe directly on those MINIAOD files is the reference
(`scripts/tnp_miniaod.py`, `scripts/plot_mini_vs_nano.py`). Results go to `results/` and `NOTES.md` (append-only sections), then into
the three decks, then to the fork `santanumahata/cmssw`, branch `nanoaod-trigobj-notes` only. Before the pull
request, the fix branch is moved onto current upstream master and the PR text is kept ready (step 12); I open
the PR myself. For 2023 data from run 367661 a second change on the fork ORs the old and new Diphoton30_18 filter
names (step 13); steps 14-17 check the names in MINIAOD, re-make 2023 NANO in three CMSSW_16_1_3 areas and run the
cumulative closure (stock, then +#52514, then both changes).

## Steps

### 1. Log in and get a proxy (by me, by hand)
I run `kinit` locally and `voms-proxy-init` on lxplus myself. The proxy file is
`/afs/cern.ch/user/s/smahata/private/x509up_cms` (on 6 November it was valid for about 162 h).
**Expect:** `voms-proxy-info --all` shows time left. Every xrootd or DAS command afterwards runs with
`export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms`.

### 2. Re-make NANO without and with the fix
**Known-good command (on lxplus):**
```bash
bash scripts/make_fixed_nano.sh v13data     # or v13 | v15 | v16
```
**Expect:** `$WORK/<case>/nano_nofix.root` and `nano_fix.root` in `/eos/user/s/smahata/trigobj_check/cmssw/`;
the script stops unless exactly one line of `triggerObjects_cff.py` changed. Cases (release, era, GT, input):
- `v13data`: CMSSW_13_3_1_patch1, `Run3`, `133X_dataRun3_v3` (autoCond `run3_data`; the 16Dec2023 GT was not
  found), one 2022D EGamma 22Sep2023 MINIAOD parent, all events.
- `v16`: CMSSW_16_0_4_patch2, `Run3_2026`, `160X_dataRun3_Prompt_frozen260223_v1`, Run2026C MINIAOD of run 402536,
  20000 events.
- `v13`, `v15`: GluGluHto2G MC (see the script).

The release area is left **with the fix applied** after the script.

### 3. Count bits; check the no-fix NANO against the central file
**Known-good command (on lxplus):**
```bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
cd /eos/user/s/smahata/trigobj_check
python3 measure_trigobj.py v13data_nofix /EGamma/Run2022D-22Sep2023-v1/MINIAOD \
  cmssw/v13data/nano_nofix.root nanoaod-trigobj-notes/results/fix_test/v13data_nano_nofix.json \
  root://cms-xrd-global.cern.ch//store/data/Run2022D/EGamma/NANOAOD/16Dec2023-v1/2550000/499b6a69-bd7e-4bce-bd6d-4ab4f250ea2d.root
```
**Expect:** `reference_comparison` reports TrigObj (id, filterBits, pt) identical in all shared events
(19539 / 19539 on 6 November). The reference is matched by (run, lumi, event) over the whole central file.

### 4. Tag-and-probe on one NANO file (local check)
**Known-good command (LCG view, not cmsenv):**
```bash
python3 tnp_unseeded.py <nano file> <label> <output json> <output png prefix>
python3 plot_tnp_compare.py <nofix json> <fix json> 30_22 "<title>" <output png>
```
**Expect:** the script prints the bit masks it parsed, e.g. 30_22 seeded 12288 (bits 12, 13), unseeded 16384 / 32768
(bits 14, 15); 30_18 seeded 65536 (bit 16), unseeded 131072 (bit 17); electron WPTight 2 (bit 1) on 2022 v13 data.
`plot_tnp_compare.py` asserts that tags, pairs and probe counts are identical in the no-fix and fix files.

### 5. Dump the two NANO configurations for HTCondor
**Known-good command (on lxplus, right after step 2, while the area still has the fix):**
```bash
T=/eos/user/s/smahata/trigobj_check; C=$T/condor_v13data; V=$T/cmssw/v13data
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd $T/cmssw/CMSSW_13_3_1_patch1/src && eval $(scramv1 runtime -sh)
mkdir -p $C
edmConfigDump $V/nano_fix_cfg.py > $C/nano_fix_dump.py
git checkout -- PhysicsTools/NanoAOD/python/triggerObjects_cff.py
scram b -j 8 > /dev/null 2>&1
git diff --numstat                      # empty = clean
edmConfigDump $V/nano_nofix_cfg.py > $C/nano_nofix_dump.py
diff $C/nano_nofix_dump.py $C/nano_fix_dump.py
```
**Expect:** two dumps of equal length (28883 lines for v13data) that differ only in the Photon `sel` line, the
annotation and the output file name. Anything else differing → stop. The area ends clean (no fix).

### 6. Submit one job per MINIAOD parent
**Known-good command:** copy `scripts/condor/tnp_job.sh` and `tnp.sub` to the submit directory, copy
`tnp_unseeded.py` to `/eos/user/s/smahata/trigobj_check/`, then on lxplus:
```bash
export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
D=/afs/cern.ch/user/s/smahata/tnp_condor_v13data
mkdir -p $D/logs && cd $D && chmod +x tnp_job.sh
dasgoclient -query='parent file=/store/data/Run2022D/EGamma/NANOAOD/16Dec2023-v1/2550000/499b6a69-bd7e-4bce-bd6d-4ab4f250ea2d.root' \
  | awk '{print NR-1, $1}' > inputs.txt
wc -l < inputs.txt                      # 40
md5sum tnp_job.sh tnp.sub               # compare with the local copies
condor_submit tnp.sub
```
**Expect:** 40 jobs (`longlunch`, 4 CPUs). Each job runs cmsRun on both dumps over its whole file, runs
`tnp_unseeded.py` on both NANOs in a clean LCG environment, and returns only `tnp_<i>_nofix.json` and
`tnp_<i>_fix.json`. Cluster 9771223: all 40 jobs return value 0, queue empty at 02:14 on 7 November.

### 7. Check the jobs, merge, plot
**Known-good command (on lxplus):**
```bash
cd /afs/cern.ch/user/s/smahata/tnp_condor_v13data
ls tnp_*_nofix.json | wc -l; ls tnp_*_fix.json | wc -l          # 40 and 40
grep "return value" logs/condor.log | sort | uniq -c              # 40 Normal termination (return value 0)
grep -h "^bits" logs/job_*.out | sort | uniq -c                   # one distinct line, 80 times
source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
S=/eos/user/s/smahata/trigobj_check
python3 $S/merge_tnp.py v13data_40files_nofix merged_nofix.json tnp_*_nofix.json
python3 $S/merge_tnp.py v13data_40files_fix merged_fix.json tnp_*_fix.json
python3 $S/plot_tnp_compare.py merged_nofix.json merged_fix.json 30_22 "Run2022D EGamma (40 files), Diphoton30_22 legs (Mass90/Mass95)" tnp_compare_30_22.png
python3 $S/plot_tnp_compare.py merged_nofix.json merged_fix.json 30_18 "Run2022D EGamma (40 files), Diphoton30_18 legs (low mass)" tnp_compare_30_18.png
```
**Expect:** `40 files, 3125939 events` (the DAS total of `inputs.txt`); 59863 opposite-sign pairs for 30_22 and
57727 for 30_18; unseeded leg 0 without the fix; seeded counts equal without and with the fix.

### 7a. MiniAOD reference on the same 40 files
Same cuts on the MINIAOD parents themselves (`scripts/tnp_miniaod.py`, FWLite in cmsenv): stored RunIIIWinter22-V1
IDs, `slimmedPatTrigger` filter labels, each numerator raw and `_pt15`. Second run `nanoprec`: electron and TrigObj
eta/phi rounded as NanoAOD stores them. No cmsRun; one CPU per job.
**Known-good command (on lxplus; copy `tnp_miniaod.py`, `merge_tnp.py`, `plot_mini_vs_nano.py` to
`/eos/user/s/smahata/trigobj_check/` and `scripts/condor/tnp_mini*` plus `inputs.txt` to the submit directory):**
```bash
export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms
D=/afs/cern.ch/user/s/smahata/tnp_condor_mini; S=/eos/user/s/smahata/trigobj_check
mkdir -p $D/logs && cd $D && chmod +x tnp_mini_job.sh
md5sum inputs.txt ../tnp_condor_v13data/inputs.txt                 # equal
condor_submit tnp_mini.sub; condor_submit tnp_mini_nanoprec.sub
# after both clusters are empty:
grep "return value" logs/condor.log logs/condor_nanoprec.log | sort | uniq -c   # 40 + 40 return value 0
source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc13-opt/setup.sh
python3 $S/merge_tnp.py v13data_40files_mini merged_mini.json tnp_*_mini.json
python3 $S/merge_tnp.py v13data_40files_mini_nanoprec merged_mini_nanoprec.json tnp_*_mini_nanoprec.json
N=/afs/cern.ch/user/s/smahata/tnp_condor_v13data/merged_fix.json
python3 $S/plot_mini_vs_nano.py $N merged_mini.json 30_22 "Run2022D EGamma (40 files), Diphoton30_22 legs: MiniAOD vs fixed NanoAOD" mini_vs_nano_30_22.png
python3 $S/plot_mini_vs_nano.py $N merged_mini.json 30_18 "Run2022D EGamma (40 files), Diphoton30_18 legs: MiniAOD vs fixed NanoAOD" mini_vs_nano_30_18.png
```
Per-file check: compare `tags`, `pairs_os`, `pairs_ss`, `total_*` and every `passed*` of `tnp_<i>_mini_nanoprec.json`
with `../tnp_condor_v13data/tnp_<i>_fix.json` for all 40 files.
**Expect (clusters 9773146, 9773153 on 10 November):** about 2 min per file. Raw: 30_22 55132 / 59861 = 0.9210,
30_18 52458 / 57725 = 0.9088, 1-3 tags or pairs off the fixed NanoAOD in 25 files; `_pt15` = raw. `nanoprec`: 0 / 80
file-family differences. Before committing, drop `legs.*.pairs` from the merged JSONs (23.6 MB → 11 KB); the full
files stay in `$D`.

### 8. Fetch results to the local clone
**Known-good command (local), per file:**
```bash
F=/afs/cern.ch/user/s/smahata/tnp_condor_v13data/merged_fix.json
remote=$(ssh smahata@lxplus.cern.ch "md5sum $F" | cut -d" " -f1)
ssh smahata@lxplus.cern.ch "cat $F" > results/tnp_2022D_v13_40files/merged_fix.json
md5sum results/tnp_2022D_v13_40files/merged_fix.json             # must equal $remote; else retry
```
Upload goes the other way: `ssh smahata@lxplus.cern.ch "cat > <remote path>" < <local file>`, then compare md5.

### 9. Rebuild the decks
**Known-good command (local, from the notes clone):**
```bash
cd slides/beamer/src
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../outputs trigobj_unseeded.tex
pdflatex -interaction=nonstopmode -output-directory=../outputs trigobj_unseeded.tex
grep -c Overfull ../outputs/trigobj_unseeded.log                  # 0
cd ../../..
export NODE_PATH=$MAMBA_ENV/lib/node_playwright/node_modules   # MAMBA_ENV: the micromamba env with Playwright
/usr/bin/node scripts/render_deck.js slides/issue-deck-src slides/issue-deck
/usr/bin/node scripts/render_deck.js slides/detailed-deck-src slides/detailed-deck
/usr/bin/node scripts/render_pdf.js $PWD/report    # absolute path: the script builds a file:// URL from it
```
**Expect:** Beamer 49 pages, issue deck 14 slides, detailed deck 36 slides, report 10 pages (9 November). In an overflow check
(any element bottom > 1016 px of a 1080 px slide) only `cover` (both decks) and the issue-deck `trigger` slide
are flagged; they were flagged before the November changes too. HTML slides embed figures as base64 data URIs;
a new slide is a file in `project/slides/` plus its id in `project/deck.json` `order`.
The supervisor deck (local only, not in this repository) is built the same way as the Beamer one, from
`<session folder>/slides/supervisor_10/src/Missing_unseeded_photon_filter_bits_in_NanoAOD_identification_and_fix_Santanu_Mahata.tex`
(file name = talk title plus my name; was `trigobj_short.tex`): 19 pages, 0 overfull (20 November); title page
"EGM General Meeting" with `plots/logo_tifr.png` and `plots/logo_cms.png`; the last page, after `\appendix`, is backup
(the efficiency-plot captions).

### 10. Commit and push to the fork only
**Known-good command:**
```bash
export NAME_PATTERN='<regex of the forbidden tool and vendor names; kept outside the repository>'
git add <files>
git grep -ciIE "$NAME_PATTERN"; for f in $(git ls-files '*.pdf'); do (pdftotext $f -; pdfinfo $f) | grep -ciE "$NAME_PATTERN"; done   # all 0
git -c user.name=santanumahata -c user.email=santanuedu.m@gmail.com commit -m "<message, no attribution lines>"
git -c credential.helper='!f() { echo username=x-access-token; echo "password=$GH_TOKEN"; }; f' \
  push -q https://github.com/santanumahata/cmssw.git HEAD:refs/heads/nanoaod-trigobj-notes
git ls-remote https://github.com/santanumahata/cmssw.git refs/heads/nanoaod-trigobj-notes   # equals HEAD
```

### 11. Rewrite commit metadata to my identity (only if forbidden names got in)
**Known-good command (run 9 November; backup first, then rewrite, then push with lease):**
```bash
git bundle create <session folder>/backup/notes_before_scrub.bundle nanoaod-trigobj-notes
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --env-filter '
echo "$GIT_AUTHOR_NAME $GIT_AUTHOR_EMAIL" | grep -qiE "$NAME_PATTERN" && { GIT_AUTHOR_NAME=santanumahata; GIT_AUTHOR_EMAIL=santanuedu.m@gmail.com; }
echo "$GIT_COMMITTER_NAME $GIT_COMMITTER_EMAIL" | grep -qiE "$NAME_PATTERN" && { GIT_COMMITTER_NAME=santanumahata; GIT_COMMITTER_EMAIL=santanuedu.m@gmail.com; }
export GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL' \
 --msg-filter 'grep -viE "^[A-Za-z-]+:.*($NAME_PATTERN)|^($NAME_PATTERN)" | sed -e :a -e "/^\n*\$/{\$d;N;ba" -e "}"' nanoaod-trigobj-notes
# a single fix commit C on a cmssw branch (fetched with --depth 2): same tree, same parent, same dates
N=$(GIT_AUTHOR_NAME=santanumahata GIT_AUTHOR_EMAIL=santanuedu.m@gmail.com GIT_AUTHOR_DATE="$(git log -1 --format=%aD $C)" \
    GIT_COMMITTER_NAME=santanumahata GIT_COMMITTER_EMAIL=santanuedu.m@gmail.com GIT_COMMITTER_DATE="$(git log -1 --format=%cD $C)" \
    git commit-tree $C^{tree} -p $C^ -m "<message without the trailer lines>")
git push https://github.com/santanumahata/cmssw.git --force-with-lease=refs/heads/<branch>:<old sha> $N:refs/heads/<branch>
```
**Expect:** `git diff --stat <old> <new>` empty (trees identical); `git log --format='%an%ae%cn%ce%n%B' | grep -ciE "$NAME_PATTERN"`
is 0 on a fresh clone. Hashes cited in files then need updating (`git grep` the old short hashes).

### 12. Prepare the PR: fix branch on current upstream master
**Known-good command (local, run 13 November; `SESSION_SCRATCH` is the session scratchpad):**
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
git diff --stat HEAD~1 HEAD                     # triggerObjects_cff.py | 2 +-
git -c credential.helper='!f(){ echo username=santanumahata; echo password=$GH_TOKEN; }; f' \
  push --force-with-lease=nano-photon-trigobj-unseeded:<old full sha> \
  https://github.com/santanumahata/cmssw.git HEAD:refs/heads/nano-photon-trigobj-unseeded
git ls-remote https://github.com/santanumahata/cmssw.git refs/heads/nano-photon-trigobj-unseeded   # equals HEAD
curl -s "https://api.github.com/repos/cms-sw/cmssw/compare/master...santanumahata:cmssw:nano-photon-trigobj-unseeded" \
 | python3 -c 'import json,sys; d=json.load(sys.stdin); print("status", d.get("status"), "ahead", d.get("ahead_by"), "behind", d.get("behind_by")); [print(f["filename"], "+%d -%d" % (f["additions"], f["deletions"])) for f in d.get("files", [])]'
git format-patch -1 HEAD --stdout > $N/pr/0001-NanoAOD-photon-TrigObj-unseeded-collection.patch
```
Then in the notes clone: new hash in `README.md` and in the fork-branch line of the Conventions below
(`git grep` the old short hash; mentions in earlier `NOTES.md` sections and `results/` stay as they were), a new
`NOTES.md` section, and step 10.
**Expect (13 November):** cherry-pick clean; tip `8bb009d9b` on master `43690ddd6`, author and committer
santanumahata; compare `ahead 1 behind 0`, `PhysicsTools/NanoAOD/python/triggerObjects_cff.py +1 -1`; name check of
commit, diff and `pr/PR_body.md` 0. I then open the PR by hand from
`https://github.com/cms-sw/cmssw/compare/master...santanumahata:cmssw:nano-photon-trigobj-unseeded`, title and
body from `pr/PR_body.md`.

### 13. Second change: Diphoton30_18 bits accept old and new filter names (fork branch on master, PR-ready)
**Known-good command (local cmssw clone, run 20 November; remotes `origin` = cms-sw, `my-cmssw` = my fork):**
```bash
# the change is commit 8983610a713 (made 19 November on top of 8bb009d9b); the two Diphoton30_18 mksel lines become
#   # Diphoton30_18 legs: HLT renamed both filters during Run2023C-v3, keep old and new names
#   mksel(["hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter","hltEG30Iso60b40eCaloId11b32eHE10b9eR9Id50b90eEcalIsoFilter"]),
#   mksel(["hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter","hltDiEG18TrackIso60Iso60b40eCaloId11b32eHE10b9eR9Id50b90eTrackIsoUnseededFilter"]),
cd /home/santanu/Videos/cmssw
F=PhysicsTools/NanoAOD/python/triggerObjects_cff.py
git fetch origin master
git log --oneline 5cc01a5cbb4..origin/master -- $F         # empty: file unchanged upstream since my May fetch
git grep -n -e 'Iso60CaloId15b35e' -e 'Iso60b40eCaloId11b32e' origin/master -- $F
git branch -m nano-photon-diphoton3018-2023names nano-photon-diphoton3018-2023names-on52514   # keeps 8983610a713
git switch -c nano-photon-diphoton3018-2023names origin/master
git cherry-pick 8983610a713
git -c user.name=santanumahata -c user.email=santanuedu.m@gmail.com commit --amend --no-edit \
  --author="santanumahata <santanuedu.m@gmail.com>"           # my GitHub identity; author date kept
git log --oneline origin/master..HEAD
git diff --stat origin/master..HEAD
python3 -m py_compile $F
git push --force-with-lease=nano-photon-diphoton3018-2023names:8983610a713 \
  "https://santanumahata:${GH_TOKEN}@github.com/santanumahata/cmssw.git" nano-photon-diphoton3018-2023names
git fetch -q my-cmssw nano-photon-diphoton3018-2023names
git rev-list --left-right --count origin/master...FETCH_HEAD
```
**Expect (20 November):** master `7167add78d2`; the Diphoton30_18 lines 113-114 carry the old names only (the grep also
matches the Diphoton30_22 lines 110-111); `mksel` takes a list on master (`triggerObjects_cff.py:24`). Cherry-pick clean; one commit `e830f534b11`
(first pushed as `68fc08904d9` with `smahata <santanu.mahata@cern.ch>`, then amended, same tree), author and committer
`santanumahata <santanuedu.m@gmail.com>`; `triggerObjects_cff.py | 5 +++--`; parse OK. Pushes
`8983610a713...68fc08904d9`, `68fc08904d9...e830f534b11` (forced update); rev-list `0 1`. Name check of commit, diff, branch name and PR text 0.
The code is independent of #52514 (different line); the unseeded bit needs both. Upstream diff, without opening a PR:
`https://github.com/cms-sw/cmssw/compare/master...santanumahata:cmssw:nano-photon-diphoton3018-2023names`. The
cms-sw PR template is `pull_request_template.md` at the cmssw root: PR description, PR validation, a backport
section, a checklist. Not yet a PR: I open it only after I confirm.

### 14. MiniAOD check: which Diphoton30_18 filter names fire in which 2023 era
Analyzer area `/eos/user/s/smahata/edanalyzer/CMSSW_13_0_13` (an EL7 release, so `cmssw-el7`); configs
`cfg_Cv1v2_oldString.py` (old names) and `cfg_Dv1v2_newString.py` (new names) in `MyAnalysis/DiphotonTnPAnalyzer/python/`.
**Known-good command (lxplus9108, run 19 November):**
```bash
A=/eos/user/s/smahata/edanalyzer/CMSSW_13_0_13/src/MyAnalysis/DiphotonTnPAnalyzer
OUT=$A/demo_filter_rename
CV2=root://cms-xrd-global.cern.ch//store/data/Run2023C/EGamma0/MINIAOD/22Sep2023_v2-v1/40000/b6b896c4-5d8b-43cf-84f7-c8e7ded6abdc.root
DV1=root://cms-xrd-global.cern.ch//store/data/Run2023D/EGamma0/MINIAOD/22Sep2023_v1-v1/2530000/664b05d0-e4ac-48d8-83b9-1ccf889a27c3.root
mkdir -p $OUT
cmssw-el7 --command-to-run "cd $A/../.. && eval \`scram runtime -sh\` && \
 cmsRun $A/python/cfg_Cv1v2_oldString.py inputFiles=$CV2 maxEvents=20000 outputFile=$OUT/Cv2_old.root > $OUT/Cv2_old.log 2>&1 && \
 cmsRun $A/python/cfg_Dv1v2_newString.py inputFiles=$CV2 maxEvents=20000 outputFile=$OUT/Cv2_new.root > $OUT/Cv2_new.log 2>&1 && \
 cmsRun $A/python/cfg_Cv1v2_oldString.py inputFiles=$DV1 maxEvents=20000 outputFile=$OUT/Dv1_old.root > $OUT/Dv1_old.log 2>&1 && \
 cmsRun $A/python/cfg_Dv1v2_newString.py inputFiles=$DV1 maxEvents=20000 outputFile=$OUT/Dv1_new.root > $OUT/Dv1_new.log 2>&1"
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /cvmfs/cms.cern.ch/el9_amd64_gcc12/cms/cmssw/CMSSW_13_3_0/src && eval `scram runtime -sh` && cd $OUT
for f in Cv2_old Cv2_new Dv1_old Dv1_new; do
  root -l -b -q -e "TTree*t=(TTree*)TFile::Open(\"${f}_numEvent20000.root\")->Get(\"diphotonTnP/tnpPhoHLT\"); \
   printf(\"$f pairs=%lld seed=%lld unseed=%lld\n\", t->GetEntries(), t->GetEntries(\"probe_passSeed==1\"), t->GetEntries(\"probe_passUnseed==1\"));"
done
```
**Expect (19 November):** `Cv2_old pairs=1225 seed=460 unseed=550`, `Cv2_new 1225 / 0 / 0`, `Dv1_old 1240 / 0 / 0`,
`Dv1_new 1240 / 413 / 496`: each name set finds objects only in its own era (C-v2 run 367615, D-v1 run 370175).

### 15. Build three CMSSW_16_1_3 areas on EOS: plain, pr52514, fixed
**Known-good command (lxplus9108, run 19-20 November):**
```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc13
W=/eos/user/s/smahata/nano3018_test
mkdir -p $W/plain $W/pr52514 $W/fixed
cd $W/plain && scram project CMSSW CMSSW_16_1_3
cd $W/pr52514 && scram project CMSSW CMSSW_16_1_3 && cd CMSSW_16_1_3/src && eval `scram runtime -sh`
git cms-init --upstream-only
git cms-addpkg PhysicsTools/NanoAOD
git fetch https://github.com/santanumahata/cmssw.git nano-photon-trigobj-unseeded
git checkout FETCH_HEAD -- PhysicsTools/NanoAOD/python/triggerObjects_cff.py
git diff --stat HEAD
scram b -j 8 > $W/pr52514/build.log 2>&1; echo "build exit $?"
# the same six lines in $W/fixed with branch nano-photon-diphoton3018-2023names, log $W/fixed/build.log
```
**Expect:** pr52514 `1 file changed, 1 insertion(+), 1 deletion(-)`, fixed `1 file changed, 4 insertions(+), 3 deletions(-)`;
build exit 0 for both. `python3 -c "import PhysicsTools.NanoAOD.triggerObjects_cff as m; print(m.__file__)"` gives
the cvmfs release file in plain and `<area>/CMSSW_16_1_3/src/...` in the other two.

### 16. Re-make 2023 NANO (20000 events) and count bits 18, 19
**Known-good command (lxplus9108, run 19 November; one ssh session per cmsDriver, for area in plain, fixed and
file in Cv2, Dv1 of step 14):**
```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh; export SCRAM_ARCH=el9_amd64_gcc13
W=/eos/user/s/smahata/nano3018_test; area=fixed
CV2=root://cms-xrd-global.cern.ch//store/data/Run2023C/EGamma0/MINIAOD/22Sep2023_v2-v1/40000/b6b896c4-5d8b-43cf-84f7-c8e7ded6abdc.root
cd $W/$area/CMSSW_16_1_3/src && eval `scram runtime -sh` && cd $W/$area
cmsDriver.py nano_Cv2 -s NANO --data --era Run3_2023,run3_nanoAOD_pre142X --conditions auto:run3_data \
  --datatier NANOAOD --eventcontent NANOAOD --filein $CV2 --fileout file:Cv2_nano.root -n 20000 \
  --python_filename nano_Cv2_cfg.py > nano_Cv2.log 2>&1; echo "$area Cv2 exit $?"
# count, in any 16_1_3 cmsenv:
for area in fixed plain; do for f in Cv2 Dv1; do
  root -l -b -q -e "TTree*t=(TTree*)TFile::Open(\"$W/$area/${f}_nano.root\")->Get(\"Events\"); \
   printf(\"$area $f events=%lld bit18=%lld bit19=%lld\n\", t->GetEntries(), \
   t->GetEntries(\"Sum\$(TrigObj_id==22 && ((TrigObj_filterBits>>18)&1))>0\"), \
   t->GetEntries(\"Sum\$(TrigObj_id==22 && ((TrigObj_filterBits>>19)&1))>0\"));"
done; done
root -l -b -q -e "TTree*t=(TTree*)TFile::Open(\"$W/fixed/Dv1_nano.root\")->Get(\"Events\"); \
 cout<<t->GetBranch(\"TrigObj_filterBits\")->GetTitle()<<endl;" | tr ';' '\n' | grep -n "Diphoton\|hltEG30Iso60\|hltEG18\|hltDiEG18"
```
**Expect (19-20 November):** all four cmsDriver exit 0. Events with >= 1 photon TrigObj carrying the bit, bit18 / bit19:
fixed Cv2 14630 / 2602, fixed Dv1 13753 / 1781, plain Cv2 14630 / 0, plain Dv1 0 / 0. Fixed bits 18, 19 read
"old OR new"; plain shows the old names only; bit 20 unchanged.

### 17. Closure: 2023 trigger efficiency, cumulative steps (submitted 20 November; outputs not yet checked)
Job files `scripts/condor/closure_2023/nano_job.sh` and `closure.sub`, copied to `~/closure_2023_condor/` on lxplus9108
(md5 `0bc1720e…`, `c216decd…` on both sides). One job = one MINIAOD file, all events, in one area.
**Known-good command (lxplus9108, run 20 November):**
```bash
cd ~/closure_2023_condor && mkdir -p logs
cp /tmp/x509up_u170597 ~/private/x509_proxy          # the proxy file named in closure.sub
source /cvmfs/cms.cern.ch/cmsset_default.sh
W=/eos/user/s/smahata/nano3018_test
rm -f inputs.txt inputs_more.txt
for T in Cv2:Run2023C-22Sep2023_v2-v1 Cv4:Run2023C-22Sep2023_v4-v1 Dv1:Run2023D-22Sep2023_v1-v1; do
  i=0
  for LFN in $(dasgoclient -query="file dataset=/EGamma0/${T#*:}/MINIAOD" | sort | head -40); do
    L=inputs.txt; [ $i -ge 10 ] && L=inputs_more.txt   # run on 20 Nov as two loops (files 0-9, 10-39); same lines
    echo "${T%%:*} stock   $W/plain   $LFN $i" >> $L
    echo "${T%%:*} pr52514 $W/pr52514 $LFN $i" >> $L
    echo "${T%%:*} both    $W/fixed   $LFN $i" >> $L
    i=$((i+1))
  done
done
wc -l inputs.txt inputs_more.txt                      # 90, 270
for T in Cv2 Cv4 Dv1; do for S in stock pr52514 both; do mkdir -p $W/closure_2023/$T/$S; done; done
sed 's/from inputs.txt/from inputs_more.txt/' closure.sub > closure_more.sub
condor_submit closure.sub
condor_submit closure_more.sub
```
Quick check that does not wait for condor: file 0 of each dataset in each area under `nohup` on lxplus9108,
output on node-local `/tmp/smahata_closure/<step>/nano_<tag>_0.{log,root}`:
```bash
mkdir -p /tmp/smahata_closure
cp /tmp/x509up_u170597 /tmp/smahata_closure/x509_proxy
cd /tmp/smahata_closure
for S in stock:plain pr52514:pr52514 both:fixed; do
  STEP=${S%%:*}
  AREA=/eos/user/s/smahata/nano3018_test/${S#*:}
  mkdir -p $STEP
  for T in Cv2 Cv4 Dv1; do
    LFN=$(awk -v t=$T -v s=$STEP '$1==t && $2==s && $5==0 {print $4}' ~/closure_2023_condor/inputs.txt)
    nohup bash -c "source /cvmfs/cms.cern.ch/cmsset_default.sh; export SCRAM_ARCH=el9_amd64_gcc13; \
      export X509_USER_PROXY=/tmp/smahata_closure/x509_proxy; \
      cd $AREA/CMSSW_16_1_3/src && eval \`scram runtime -sh\` && cd /tmp/smahata_closure/$STEP && \
      python3 -c 'import PhysicsTools.NanoAOD.triggerObjects_cff as m; print(m.__file__)' > nano_${T}_0.log && \
      cmsDriver.py nano_${T} -s NANO --data --era Run3_2023,run3_nanoAOD_pre142X --conditions auto:run3_data \
        --datatier NANOAOD --eventcontent NANOAOD --filein root://cms-xrd-global.cern.ch/$LFN \
        --fileout file:nano_${T}_0.root -n -1 --python_filename nano_${T}_cfg.py >> nano_${T}_0.log 2>&1; \
      echo \"cmsDriver exit \$?\" >> nano_${T}_0.log" > /dev/null 2>&1 &
  done
done
sleep 240; pgrep -u smahata -c cmsRun; grep -c "Begin processing" /tmp/smahata_closure/*/nano_*_0.log
```
**Expect (20 November):** `90 job(s) submitted to cluster 9803546`, `270 job(s) submitted to cluster 9803547`;
outputs `$W/closure_2023/<tag>/<step>/nano_<idx>.{log,root}`, each log ending `cmsDriver exit 0`. Quick check:
9 `cmsRun`, about 2000 events processed per run after 4 minutes, each log's first line the area's own
`triggerObjects_cff.py`. NOT YET VERIFIED: job exits, outputs, and the tag-and-probe (`tnp_unseeded.py` per file,
`merge_tnp.py` per dataset and step; a three-series plot is still to be written). The tag needs a seeded-leg bit,
so stock and pr52514 on new-name files (C-v4, D-v1) are expected to give no tags.

## Conventions
- Never push to `cms-sw/cmssw`, never open a PR or issue. Data access is read-only; only small test files.
- The PR to `cms-sw/cmssw` is opened by me, by hand (step 12); nothing here opens or comments on it.
- `pr/PR_body.md` is paste-ready: title, the bug, its effect in one sentence, the fix, then
  `@cms-sw/egamma-pog-l2 FYI`. No validation or backport section, no follow-up notes, no references to other PRs.
- Who signs: `PhysicsTools/NanoAOD` maps to xpog (cms-bot `categories_map.py`); xpog L2 signs, tests run, ORP
  merges (`categories.py:13`). EGM is not a signing category for this file; it is tagged for information only.
- `NOTES.md`: never change earlier sections; append a new numbered, dated section. Exception made on request on
  9 November: section 2 (repository state) edited in place for the branch rename and new hashes.
- No forbidden tool or vendor name anywhere (the names are in `NAME_PATTERN`, outside the repository): file contents, PDFs, commit author, committer and
  trailers, branch names. Commits are authored and committed as `santanumahata <santanuedu.m@gmail.com>`; local paths
  containing such a name become placeholders (`$MAMBA_ENV`, `SESSION_WORKDIR`, `SESSION_SCRATCH`).
- Fork branches: `nanoaod-trigobj-notes` (this repository), `nano-photon-trigobj-unseeded` (fix `8bb009d9b` on
  upstream master), `nano-photon-trigobj-unseeded-forkmaster` (fix `42555a463` on the fork's May 2025 master),
  `nano-photon-diphoton3018-2023names` (second change `e830f534b11` on upstream master `7167add78d2`; not yet a PR;
  the earlier `8983610a713` on `8bb009d9b` is kept only in the local branch `nano-photon-diphoton3018-2023names-on52514`).
- A fix for upstream goes to my fork first; the upstream PR is opened only after I confirm the fork branch.
- Each upstream PR branch sits on current cms-sw master and carries only its own lines
  (`git diff --stat origin/master..HEAD`), also when its effect needs another open PR (step 13).
- The 2023 closure is cumulative, one change at a time: `stock` (area plain, neither change), `pr52514` (#52514 only),
  `both` (area fixed, the rename on top of #52514). Same MINIAOD files in all three.
- The closure runs in CMSSW_16_1_3, not on master: master cannot read 2023 MINIAOD (Gotchas), and
  `triggerObjects_cff.py` is the same blob (`2691ff0e80b`) in CMSSW_16_1_3 and master.
- Tag-and-probe: tag tight electron, pT > 35, |eta_SC| < 2.1, `HLT_Ele32_WPTight_Gsf`, matched (dR < 0.1) to the
  WPTight electron object and to a seeded-leg photon object of the family measured; probe cutBased >= 2, pT > 15,
  |eta_SC| < 2.5 outside 1.4442-1.566, opposite sign, 70 < m_ee < 110 GeV. Counting only, no fit; same-sign pairs
  reported; 68% Clopper-Pearson. The no-fix file is the control.
- The MiniAOD reference (step 7a) reads the MINIAOD parents of the same NANO files, never a different sample, and
  copies the NanoAOD electron and photon TrigObj selections for the tag.
- Bit numbers are always parsed from the file's `TrigObj_filterBits` documentation, never hard-coded.
- Results: `results/tnp_<era>_<version>[_<variant>]/`; scripts in `scripts/`, HTCondor files in `scripts/condor/`.
- The local clone lives in the session scratchpad and is not durable: commit and push before stopping.
- The LCG view and the CMSSW environment are never set up in the same shell; inside a job the LCG part runs
  under `env -i HOME="$HOME" PATH=/usr/bin:/bin bash -c "source <LCG setup> && ..."` (`tnp_job.sh`).
- The release area must be clean (no fix) after the configuration dumps; `make_fixed_nano.sh` leaves the fix in,
  so step 5 dumps the fix configuration first, then restores and dumps the no-fix one.

## Gotchas
- **Symptom:** `ssh` to lxplus gives `Permission denied`.
  **Cause:** Kerberos ticket expired.
  **Fix:** I run `kinit` (and `voms-proxy-init` if the proxy is also gone) by hand.
- **Symptom:** the reference comparison of `measure_trigobj.py` (xrootd read of the central file) failed.
  **Cause:** `X509_USER_PROXY` not exported in that ssh shell.
  **Fix:** `export X509_USER_PROXY=/afs/cern.ch/user/s/smahata/private/x509up_cms` first.
- **Symptom:** `Could not chdir to home directory /afs/cern.ch/user/s/smahata: Connection timed out`, `.bashrc`
  timeouts, `cd` into the AFS submit directory fails.
  **Cause:** AFS unreachable from that lxplus node.
  **Fix:** reconnect to `lxplus.cern.ch` (a new node), in a retry loop. Do not ssh to a fixed node name such as
  `lxplus955.cern.ch` or `lxplus921.cern.ch`: both failed with `Host key verification failed` (EOS and AFS are the
  same from any node).
- **Symptom:** `scp` ends with `Connection closed`.
  **Fix:** copy with `ssh ... "cat > file" < file` or `ssh ... "cat file" > file` and compare md5 on both sides;
  never send the fetch's stderr to /dev/null without the md5 check (a failed fetch then passes silently).
- **Symptom:** all HTCondor jobs held right after `condor_submit`, before running.
  **Cause:** queue variable named `INPUT`; submit commands are case-insensitive, so it set the job's `input`
  (stdin) file and condor tried to transfer the LFN as a local file.
  **Fix:** the variable is `LFN` (`queue INDEX, LFN from inputs.txt`); `condor_rm <cluster>` and resubmit.
- **Symptom:** the DAS parent of a PromptReco NANOAOD file is a RAW file.
  **Fix:** use a MINIAOD file of the same run and dataset as input.
- **Symptom:** `dasgoclient` prints a Python error with the LCG view set up.
  **Cause:** LCG Python vs dasgoclient. Harmless; the query output is still correct.
- **Symptom:** the Diphoton30_18 bits (18, 19 in master; 16, 17 in v12-v14) stay 0 on 2023 input from run 367661
  (Run2023C-v3 on), even with #52514; on 2023D-v1 the seeded bit is 0 too.
  **Cause:** the HLT renamed both 30_18 filters from run 367661; the bit list has only the old names (step 14;
  `NOTES.md` sections 7, 8, 15).
  **Fix:** branch `nano-photon-diphoton3018-2023names` (step 13) ORs old and new names; on 20000 D-v1 events bit 18 / 19
  go from 0 / 0 to 13753 / 1781 (step 16).
- **Symptom:** `node: No such file` for `$MAMBA_ENV/bin/node`.
  **Fix:** use `/usr/bin/node` with `NODE_PATH` set to the Playwright modules of `$MAMBA_ENV` (step 9).
- **Symptom:** the local notes clone is gone after a session restart.
  **Cause:** the session scratchpad is wiped.
  **Fix:** `git clone --single-branch -b nanoaod-trigobj-notes https://github.com/santanumahata/cmssw.git notes_repo`.
  Uncommitted work is lost, which is why every step ends with a push. Happened on 9 November with RUNBOOK.md and
  README.md uncommitted; recovered by replaying, in order, the file writes and edits recorded in the session
  transcript (`<transcript folder>/<session id>.jsonl`) onto the fresh clone, each edit checked to match once.
  Happened again on 10 November (RUNBOOK.md): replay also the shell commands that edited the file (Python
  string-replacement heredocs), in timestamp order; transcript entries without a timestamp are duplicates.
- **Symptom:** `gh: command not found`; a `gh ... | grep` check then reports "clean" because it greps the error.
  **Fix:** query the REST API with `curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/santanumahata/cmssw/...`.
- **Symptom:** after a force-push, `https://api.github.com/repos/santanumahata/cmssw/commits/<old sha>` still returns
  HTTP 200.
  **Cause:** GitHub keeps commits that are on no branch reachable by SHA (observed on 9 November for 3 commits).
  **Fix:** none from git. UNVERIFIED: GitHub Support can purge them on request (I file that myself).
- **Symptom:** `ModuleNotFoundError: No module named 'scipy'` with the LCG view set up.
  **Cause:** `python3 -I` ignores `PYTHONPATH`, through which the LCG view provides its packages.
  **Fix:** run LCG Python without `-I`.
- **Symptom:** the MINIAOD and fixed NanoAOD counts differ by 1-3 tags or pairs in some files.
  **Cause:** NanoAOD stores eta, phi with 12 mantissa bits (deltaEtaSC 10); objects at a cut or bin edge move across.
  **Fix:** none needed; `tnp_miniaod.py ... nanoprec` reproduces the NanoAOD counts exactly (NOTES.md section 22).
- **Symptom:** `cmsDriver.py: error: unrecognized arguments: --eras Run3_2023,run3_nanoAOD_pre142X` (exit 2).
  **Fix:** the option is `--era`, with the comma-separated list.
- **Symptom:** reading `Cv2_old.root` after `cmsRun <cfg> maxEvents=20000 outputFile=$OUT/Cv2_old.root` gives
  "file ... does not exist" and a ROOT segmentation violation.
  **Cause:** VarParsing appends `_numEvent<maxEvents>` to `outputFile`.
  **Fix:** open `Cv2_old_numEvent20000.root` (step 14).
- **Symptom:** `/afs/cern.ch/work/s/smahata: Read-only file system` or `No such file or directory` when creating a
  release area.
  **Cause:** no AFS work area for this account.
  **Fix:** release areas on EOS, `/eos/user/s/smahata/nano3018_test/`.
- **Symptom:** after `kill -TERM` of the parent bash of a loop of cmsDriver calls, the cmsRun it was running ended too.
  **Fix:** one ssh session per cmsDriver (step 16), or one `nohup` per run (step 17).
- **Symptom:** on the master IB `CMSSW_20_1_X_2026-11-19-2300` (= cms-sw/cmssw master `7167add78d2`) every 2023 MINIAOD
  job stops while opening the input, stock included: `FileOpenError`, `Fatal Root Error: @SUB=TStreamerInfo::BuildCheck`,
  "The StreamerInfo of class reco::PixelClusterTagInfo ... has the same version (=3) as the active class but a
  different checksum"; cmsDriver exit 84 (HTCondor cluster 9802761, 3 / 3 jobs, 20 November).
  **Cause:** per the ROOT message, the class changed on master without a version bump; not investigated further.
  **Fix:** none on master; the closure runs in CMSSW_16_1_3 (Conventions). Reported on the backup page of the
  supervisor deck.
- **Symptom:** `ls -l` on the EOS mount shows `-?????????` and "No such file or directory" for a log a condor job
  just wrote with `xrdcp`.
  **Fix:** read it with `xrdcp -f root://eosuser.cern.ch/<path> <local file>`; cause not investigated.
- **Symptom:** pushing the rebuilt second-change branch: `! [rejected] ... (non-fast-forward)`.
  **Cause:** the fork already had `nano-photon-diphoton3018-2023names` at the old commit `8983610a713` (on #52514).
  **Fix:** `git push --force-with-lease=<branch>:<old sha>` (step 13); the old commit stays in a local backup branch.
- **Symptom:** a raw-byte grep of a PDF for `NAME_PATTERN` reports one hit; `pdftotext` and `pdfinfo` show none.
  **Cause:** a short name in the pattern matches random bytes inside a compressed stream (`strings <pdf> | grep`
  shows the byte run). **Fix:** none needed; the name check of a PDF is `pdftotext` plus `pdfinfo` (step 10).

## Changelog
- 2026-11-09 — Runbook created from the 5–9 November work: 16_0_X and v13 data NANO, recipe check, local and
  HTCondor tag-and-probe for both diphoton families, deck rebuild and push.
- 2026-11-09 — Report render and /usr/bin/node in step 9; identity and name check in step 10; new step 11 (history
  scrub); conventions for names, identity, branches; gotchas for missing gh, old SHAs, transcript recovery.
- 2026-11-11 — New step 7a (MiniAOD reference T&P, raw and nanoprec); supervisor deck build line in step 9; MiniAOD
  convention; gotchas for `python3 -I` with LCG and NanoAOD rounding; fixed-node and scratchpad-wipe entries tightened.
- 2026-11-13 — Split into card `RUNBOOK.md` and this detail; new step 12 (fix branch onto upstream master by sparse
  clone and cherry-pick, compare API check, patch, PR text); conventions for the PR body, the EGM tag and signing.
- 2026-11-20 — New steps 13-17 (2023 Diphoton30_18 rename change on the fork, MiniAOD name check, three 16_1_3 areas,
  20k re-Nano bit count, cumulative closure submitted but unverified); Diphoton30_18 gotcha now points at the fix;
  gotchas for `--era`, VarParsing output name, AFS work area, killed cmsDriver loop, master PixelClusterTagInfo,
  EOS `?????????`; conventions for branches, fork-first, cumulative closure, 16_1_3 not master; deck line 15 pages.
- 2026-11-20 — Step 13 redone: second change cherry-picked onto cms-sw master `7167add78d2` as `68fc08904d9` (only
  its 3 lines), fork branch replaced by a lease push, old commit kept locally; convention one PR branch = own lines on
  master; gotchas for the rejected push and the raw-byte PDF grep; deck line 19 pages, EGM title page and logos.
- 2026-11-20 — Supervisor deck source and outputs renamed to the talk title plus my name (step 9).
- 2026-11-20 — Step 13: second change re-authored as `santanumahata <santanuedu.m@gmail.com>`, now `e830f534b11`.
