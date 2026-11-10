# NanoAOD photon TrigObj fix: measurement, fix test and tag-and-probe — Runbook

**Last updated:** 2026-11-09
**Where it runs:** lxplus (EL9), work area `/eos/user/s/smahata/trigobj_check/`, HTCondor submit directory
`/afs/cern.ch/user/s/smahata/tnp_condor_v13data/`; notes, decks and git on the local machine.

## Overview
I re-make NanoAOD from MINIAOD without and with the one-line Photon-selection fix
(`scripts/make_fixed_nano.sh`), count the photon TrigObj bits on central and re-made files
(`scripts/measure_trigobj.py`), and measure the Diphoton30_22 and Diphoton30_18 leg efficiencies with Z->ee
tag-and-probe (`scripts/tnp_unseeded.py`): one file locally, or all 40 MINIAOD parents of one central v13
NanoAOD file on HTCondor (`scripts/condor/`), then merge (`scripts/merge_tnp.py`) and overlay
(`scripts/plot_tnp_compare.py`). Results go to `results/` and `NOTES.md` (append-only sections), then into
the three decks, then to the fork `santanumahata/cmssw`, branch `nanoaod-trigobj-notes` only.

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

## Conventions
- Never push to `cms-sw/cmssw`, never open a PR or issue. Data access is read-only; only small test files.
- `NOTES.md`: never change earlier sections; append a new numbered, dated section. Exception made on request on
  9 November: section 2 (repository state) edited in place for the branch rename and new hashes.
- No forbidden tool or vendor name anywhere (the names are in `NAME_PATTERN`, outside the repository): file contents, PDFs, commit author, committer and
  trailers, branch names. Commits are authored and committed as `santanumahata <santanuedu.m@gmail.com>`; local paths
  containing such a name become placeholders (`$MAMBA_ENV`, `SESSION_WORKDIR`, `SESSION_SCRATCH`).
- Fork branches: `nanoaod-trigobj-notes` (this repository), `nano-photon-trigobj-unseeded` (fix `828ed8b2a` on
  upstream master), `nano-photon-trigobj-unseeded-forkmaster` (fix `42555a463` on the fork's May 2025 master).
- Tag-and-probe: tag tight electron, pT > 35, |eta_SC| < 2.1, `HLT_Ele32_WPTight_Gsf`, matched (dR < 0.1) to the
  WPTight electron object and to a seeded-leg photon object of the family measured; probe cutBased >= 2, pT > 15,
  |eta_SC| < 2.5 outside 1.4442-1.566, opposite sign, 70 < m_ee < 110 GeV. Counting only, no fit; same-sign pairs
  reported; 68% Clopper-Pearson. The no-fix file is the control.
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
  `lxplus955.cern.ch`: it failed with `Host key verification failed`.
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
- **Symptom:** the Diphoton30_18 unseeded bit stays 0 even with the fix on 2023 or later input.
  **Cause:** the 30_18 filters were renamed in 2023; the bit list has only the 2018 and 2022 names
  (`NOTES.md` sections 7, 8, 15).
  **Fix:** none in the one-line fix; measure the 30_18 leg on 2022 data.
- **Symptom:** `node: No such file` for `$MAMBA_ENV/bin/node`.
  **Fix:** use `/usr/bin/node` with `NODE_PATH` set to the Playwright modules of `$MAMBA_ENV` (step 9).
- **Symptom:** the local notes clone is gone after a session restart.
  **Cause:** the session scratchpad is wiped.
  **Fix:** `git clone --single-branch -b nanoaod-trigobj-notes https://github.com/santanumahata/cmssw.git notes_repo`.
  Uncommitted work is lost, which is why every step ends with a push. Happened on 9 November with RUNBOOK.md and
  README.md uncommitted; recovered by replaying, in order, the file writes and edits recorded in the session
  transcript (`<transcript folder>/<session id>.jsonl`) onto the fresh clone, each edit checked to match once.
- **Symptom:** `gh: command not found`; a `gh ... | grep` check then reports "clean" because it greps the error.
  **Fix:** query the REST API with `curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/santanumahata/cmssw/...`.
- **Symptom:** after a force-push, `https://api.github.com/repos/santanumahata/cmssw/commits/<old sha>` still returns
  HTTP 200.
  **Cause:** GitHub keeps commits that are on no branch reachable by SHA (observed on 9 November for 3 commits).
  **Fix:** none from git. UNVERIFIED: GitHub Support can purge them on request (I file that myself).

## Changelog
- 2026-11-09 — Runbook created from the 5–9 November work: 16_0_X and v13 data NANO, recipe check, local and
  HTCondor tag-and-probe for both diphoton families, deck rebuild and push.
- 2026-11-09 — Report render and /usr/bin/node in step 9; identity and name check in step 10; new step 11 (history
  scrub); conventions for names, identity, branches; gotchas for missing gh, old SHAs, transcript recovery.
