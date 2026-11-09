# Photon TrigObj unseeded-leg filter bits: measurement on NanoAOD files

Measured 4 November 2026 on lxplus with `measure_trigobj.py` (uproot, LCG_107), files read via
`root://cms-xrd-global.cern.ch/`, up to 300000 events per file. Bit numbers parsed from the
`TrigObj_filterBits` documentation of each file. Per-file numbers: `results/<version>_<dataset>.json`.

Seeded bits = `hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter` / `hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter`.
Unseeded bits = `hltEG22Iso60...TrackIsoUnseededLastFilter` / `hltEG22R9Id85b90e...R9UnseededLastFilter` /
`hltEG18TrackIso60...TrackIsoUnseededFilter`. Counts are photon objects (id 22) with the bit set, all events read.

| version | dataset | file | events | fired Mass90 | photons with seeded bits (bit: count) | photons with unseeded bits (bit: count) | electron unseeded bit (bit: count) | id 2 | id 1515 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| v9 | /EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD | 566E12C7-CD3E-3F4D-A657-A71FF4CB2637.root | 300000 | 31771 | not documented (0 id-22 objects) | not documented | not documented | 0 | 0 | control: no photon TrigObj |
| v10 | /EGamma/Run2022D-PromptNanoAODv10_v2-v1/NANOAOD | 3f1fe826-1729-4ba9-83b9-d28a2cfd2b88.root | 300000 | 46707 | not documented | not documented | not documented | 0 | 0 | control: not affected |
| v11 | /EGamma/Run2022F-PromptNanoAODv11_v1-v2/NANOAOD | 6d07f113-b587-45b3-8db6-c2928358ae0b.root | 300000 | 41546 | not documented | not documented | not documented | 0 | 0 | control: not affected |
| v12 | /GluGluHtoGG_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2/NANOAODSIM | fd1a30c4-ac59-4c33-8245-719b82fad9f0.root | 12979 | 7725 | 12: 15626, 13: 17978 | 14: 0, 15: 0, 17: 0 | not documented | 0 | 0 | claim confirmed |
| v12 | /EGamma/Run2022D-22Sep2023-v1/NANOAOD | e5762711-8726-4523-8891-32efa9ddb381.root | 300000 | 46407 | 12: 208527, 13: 255099 | 14: 0, 15: 0, 17: 0 | not documented | 0 | 0 | claim confirmed |
| v13 | /GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv13-133X_mcRun3_2023_realistic_ForNanov13_v1_ext1-v4/NANOAODSIM | 4f45fe87-a958-4c8f-b88f-c322fec857f3.root | 17760 | 10453 | 12: 20865, 13: 24170 | 14: 0, 15: 0, 17: 0 | 16: 702 | 0 | 0 | claim confirmed |
| v13 | /EGamma/Run2022D-16Dec2023-v1/NANOAOD | 499b6a69-bd7e-4bce-bd6d-4ab4f250ea2d.root | 300000 | 46794 | 12: 207844, 13: 252774 | 14: 0, 15: 0, 17: 0 | 16: 29042 | 0 | 0 | claim confirmed |
| v14 | /EGamma0/Run2024D-PromptReco-v1/NANOAOD | 9bfae790-c112-48bf-bc54-ef1feaa74a96.root | 300000 | 35892 | 12: 203620, 13: 252039 | 14: 0, 15: 0, 17: 0 | 16: 19444 | 0 | 0 | claim confirmed |
| v15 | /GluGluH-Hto2G_Par-M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2/NANOAODSIM | acebfb52-a25b-48bc-b9f6-80fe54a98d56.root | 4180 | 2406 | 14: 4815, 15: 5588 | 16: 0, 17: 0, 19: 0 | 16: 205 | 0 | 22 | claim confirmed |
| v15 | /EGamma/Run2022D-NanoAODv15-v1/NANOAOD | 41628bc7-c70f-4bf7-b2a4-e755aea819fd.root | 300000 | 48687 | 14: 212270, 15: 258546 | 16: 0, 17: 0, 19: 0 | 16: 30451 | 0 | 430 | claim confirmed |
| v15 | /EGamma0/Run2024D-MINIv6NANOv15-v1/NANOAOD | 9d4e97c7-f23a-4cff-ac72-58488e544076.root | 300000 | 30945 | 14: 201628, 15: 248974 | 16: 0, 17: 0, 19: 0 | 16: 22980 | 0 | 254 | claim confirmed |
| Run3Winter24NanoAOD (133X) | /GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8/Run3Winter24NanoAOD-133X_mcRun3_2024_realistic_v9-v2/NANOAODSIM | 68618af9-2d38-4ef7-9aa9-2d0c30a6e3f1.root | 175654 | 101598 | 12: 205090, 13: 239250 | 14: 0, 15: 0, 17: 0 | 16: 9860 | 0 | 0 | claim confirmed |

The last two rows were added on 5 November 2026 (`v15_EGamma0_Run2024D_MINIv6NANOv15.json`,
`Winter24_133X_GluGluHToGG_M125_powheg.json`). The Winter24 dataset carries the processing string `133X`
and its file has the 18-bit, `>i4` layout; it is listed by campaign, not as NanoAOD v14. NanoAOD v14 MC
(14_0_X) is still not covered: no GluGluH*G* dataset matching `*NanoAODv14*` exists in DAS.

Photon objects with an unseeded bit set: 0 in every file (`events_with_unseeded_photon_bit` = 0 in all JSONs).

## Per version: expected vs observed

- **v9** (control). Expected: no id-22 object, no diphoton bits. Observed: 0 id-22 objects; filterBits `>i4`;
  documentation in the bitmask-value layout (`1 = ..., 2 = ...`), not parsed by the script.
- **v10** (control). Expected: 12 photon bits, no diphoton names. Observed: 12476 id-22 objects; documentation in the
  bitmask-value layout, read by hand: **11** photon filters (`hltEG33L1EG26HEFilter` ... `hltEG120EBTightIDTightIsoTrackIsoFilter`;
  `hltMu17Photon30...` absent), no diphoton filter names. The script's bit-number parse returned 0 bits for this file, so
  `hltHtEcal800` (value 256, bit 8) was **not counted** for v10.
- **v11** (control). Expected: 12 photon bits, no diphoton names. Observed: 12 photon bits, no diphoton names;
  bit 8 `hltHtEcal800`: 0 photons. The documentation in this file names bits 5 and 6 both `hltEG150HEFilter`.
- **v12**. Expected: bits 14/15/17 zero, 12/13 of order of fired Mass90, bit 8 zero, id 2 and id 1515 zero.
  Observed: as expected in MC and data; 18 photon bits, `>i4`; electron `CaloIdL_MW unseeded` bit not documented
  (consistent with NOTES §0 item 12).
- **v13**. Expected: as v12, plus electron unseeded bit > 0. Observed: as expected; electron bit 16: 702 (MC), 29042 (data).
- **v14**. Expected: as v13. Observed: as expected (18 photon bits, `>i4`, electron bit 16: 19444). The release of
  this file was not read from the file; 18 bits + `>i4` + electron unseeded bit is the v13/v14 (or 15_0_0/15_0_1) layout.
- **v15**. Expected: bits 16/17/19 zero, 14/15 > 0, `uint64`, id 2 zero, id 1515 possibly > 0. Observed: as expected;
  21 photon bits, `>u8`; id 1515: 22 (MC), 430 (data).

In Mass90-fired events, photons with the seeded bits (12/13 in v12-v14, 14/15 in v15) vs fired events:
v12 MC 12522/14393 vs 7725; v12 data 52464/52006 vs 46407; v13 MC 16614/19213 vs 10453; v13 data 53153/52221 vs 46794;
v14 data 40085/40157 vs 35892; v15 MC 3778/4383 vs 2406; v15 data 55164/54372 vs 48687.

## Not covered (first measurement, 4 November 2026)

- Optional step 7 (re-running NANO with the fix): done on 5 November, see "Fix test" below.
- No v14 MC: no GluGluH*G* dataset matching `*NanoAODv14*` or `Run3Summer24*` NANOAODSIM was found in DAS.
- No 2024 data at v15 under `NanoAODv15`: it exists under the processing string `MINIv6NANOv15` (row added above).
- One file per dataset; v12/v13/v15 MC files contain 12979, 17760 and 4180 events.

## Fix test (5 November 2026)

NANO re-made twice from one MiniAOD file, without and with the one-line fix, with
`scripts/make_fixed_nano.sh` (the exact commands), then measured with `scripts/measure_trigobj.py`.

- Input: `/store/mc/Run3Summer23MiniAODv4/GluGluHto2G_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15_ext1-v4/2820000/74338d47-0b38-4e0b-83a2-ad85c7f4e533.root`,
  the DAS parent of the central v13 file `4f45fe87-a958-4c8f-b88f-c322fec857f3.root`; all 17760 events.
  The MiniAOD dataset named in the request (`...realistic_v14-v2/MINIAODSIM`) has 0 files in DAS.
- v13: CMSSW_13_3_1_patch1, `--era Run3_2023 --conditions 133X_mcRun3_2023_realistic_ForNanov13_v1`;
  changed line 83 of `triggerObjects_cff.py`.
- v15: CMSSW_15_0_15_patch4, `--era Run3_2023,run3_nanoAOD_pre142X --conditions 150X_mcRun3_2023_realistic_v1`
  (processing string of `/DYto2E_MLL-50to120_.../Run3Summer23NanoAODv15-150X_mcRun3_2023_realistic_v1-v3/NANOAODSIM`;
  no GluGluH dataset exists in `Run3Summer23NanoAODv15`); the changed line is line **86** in this release.
- In both releases `git diff --numstat` showed exactly one changed line.

| file | events | fired Mass90 | photons with seeded bits | photons with unseeded bits | Mass90 events with an unseeded bit / fired | photons per Mass90 event | nTrigObj mean | size (bytes) |
|---|---|---|---|---|---|---|---|---|
| central v13 (`central_v13.json`) | 17760 | 10453 | 12: 20865, 13: 24170 | 14: 0, 15: 0, 17: 0 | 0 / 10453 | 1.847 | 5.287 | 29333713 |
| v13 nano_nofix (`nano_nofix.json`) | 17760 | 10453 | 12: 20865, 13: 24170 | 14: 0, 15: 0, 17: 0 | 0 / 10453 | 1.847 | 5.287 | 29339920 |
| v13 nano_fix (`nano_fix.json`) | 17760 | 10453 | 12: 20865, 13: 24170 | 14: 20461, 15: 18365, 17: 0 | 10453 / 10453 | 2.016 | 5.388 | 29363499 |
| v15 nano_nofix (`v15_nano_nofix.json`) | 17760 | 10453 | 14: 20865, 15: 24170 | 16: 0, 17: 0, 19: 0 | 0 / 10453 | 1.867 | 38.134 | 39947152 |
| v15 nano_fix (`v15_nano_fix.json`) | 17760 | 10453 | 14: 20865, 15: 24170 | 16: 20461, 17: 18365, 19: 0 | 10453 / 10453 | 2.019 | 38.225 | 39959608 |

- nano_nofix reproduces the central v13 file: events matched by (run, lumi, event), 17760 / 17760 events
  with identical TrigObj (id, filterBits, pt).
- pt of the photon objects carrying an unseeded bit after the fix: 21254 objects (v13 and v15 alike),
  minimum 22.04 GeV, median 58.30 GeV, 0 below 22 GeV.
- Bit 17 (v13) / 19 (v15), the Diphoton30_18 unseeded filter, stays 0: that filter name is not in the 2023 menu
  (NOTES.md section 13.4).
- id != 22: objects per id and per-bit counts are identical before and after in both releases, and the TrigObj
  content without id 22 is identical in 17760 / 17760 events. Photon objects: 24835 -> 26639 (v13),
  25188 -> 26807 (v15).
- The first `nano_fix` run in CMSSW_13_3_1_patch1 was terminated at 8532 events ("A fatal system signal has
  occurred: external termination request", cause not found in the log); it was rerun with the same
  configuration (`nano_fix_cfg.py`) and completed.

## Relval in CMSSW_16_1_3 (5 November 2026)

Script: `scripts/relval_fix_check.sh`; JSONs in `results/relval_16_1_3/`.

- Areas: `clean` = CMSSW_16_1_3; `fix` = CMSSW_16_1_3 + `git cms-addpkg PhysicsTools/NanoAOD` +
  `git cherry-pick 828ed8b2a` (fetched from `santanumahata/cmssw` branch `nano-photon-trigobj-unseeded`).
  `git diff CMSSW_16_1_3 --numstat`: `1 1 PhysicsTools/NanoAOD/python/triggerObjects_cff.py`.
  The cherry-pick was used instead of `git cms-merge-topic`, because the topic branch is based on master
  `ed35654b1`, not on the 16_1_X release.
- Workflows (`runTheMatrix.py -n -e`): 12452.0 = H125GGgluonfusion_14TeV 2023, GEN-SIM / DIGI+HLT `@relval2023` /
  RECO+PAT+NANO+DQM (`RecoNanoFakeHLT_2023`) / harvesting, 10 events, upgrade matrix (`-w upgrade`; it is not in
  the default matrix of 16_1_3). 141.046 = `/EGamma0/Run2023D-v1/RAW` run 369978 / reHLT `@relval2023` /
  RECO+PAT+NANO+DQM / harvesting, 100 events.
- Steps 1-2 ran once in the clean area; steps 3-4 ran in both areas on the same `step2.root`.
- 12452.0 ran without `-i all`: its GEN-SIM input dataset returned no file at T2_CH_CERN (`--ibeos`), so step 1
  generated the 10 events.
- 141.046: the RAW files of run 369978 are on tape only in DAS (T0_CH_CERN_Tape, T1_US_FNAL_Tape); of the 321
  files listed, one is in the IB EOS cache
  (`/eos/cms/store/user/cmsbuild/store/data/Run2023D/EGamma0/RAW/v1/000/369/978/00000/0068cd83-0af4-4efc-9155-b2521e558ebb.root`)
  and was used as the input of step 2 (100 events). runTheMatrix stopped after the failed first attempt, so the
  step 3 and step 4 commands were taken from `runTheMatrix.py -l 141.046 -i all --ibeos --dryRun` and run by hand.
- The NANO of step 3 is EDM (`NANOEDMAODSIM` / `NANOEDMAOD`); it was converted to flat NANO with
  `cmsDriver.py flat --step NONE ... --eventcontent NANOAODSIM` before measuring.

| workflow | area | events | fired Mass90 | NANO TrigObj objects | photons with bits 16 / 17 | TrigObj vs clean | log: Exception / triggerObjectTable lines | DQM vs clean |
|---|---|---|---|---|---|---|---|---|
| 12452.0 | clean | 10 | no HLT path branches | 0 (nTrigObj mean 0.0) | 0 / 0 | - | 0 / 0 | - |
| 12452.0 | fix | 10 | no HLT path branches | 0 (nTrigObj mean 0.0) | 0 / 0 | identical, 10 / 10 events | 0 / 0 | 116785 histograms each; 25 differ, all `DQM/TimerService` |
| 141.046 | clean | 100 | 10 | 0 (nTrigObj mean 0.0) | 0 / 0 | - | 0 / 0 | - |
| 141.046 | fix | 100 | 10 | 0 (nTrigObj mean 0.0) | 0 / 0 | identical, 100 / 100 events | 0 / 0 | 53846 histograms each; 25 differ, all `DQM/TimerService` |

JSONs: `wf12452_clean.json`, `wf12452_fix.json`, `wf12452_dqm_diff.json`, `wf141046_clean.json`,
`wf141046_fix.json`, `wf141046_dqm_diff.json`.

- The fix area builds and runs both workflows without exceptions; clean and fix outputs agree in TrigObj and in
  every DQM histogram except the 25 `DQM/TimerService` timing and memory histograms.
- The NANO TrigObj table is empty in both workflows and both areas, so this relval does not exercise the photon
  selection. Upstream of NANO, per-event product sizes (`edmEventSize -v`): 141.046 `step2.root`
  `hltTriggerSummaryAOD__reHLT` 1427.78 bytes against `hltTriggerSummaryAOD__HLT` (original 2023 HLT) 34558.6 bytes;
  `step3_inMINIAOD.root` `slimmedPatTrigger__reRECO` 371.96 bytes, with `patTrigger.processName = "reHLT"` in the
  step 3 configuration; 12452.0 `step2.root` `hltTriggerSummaryAOD__HLT` 1313 bytes. Why the relval HLT step stores
  so few objects was not investigated.
- The effect of the fix on real input is shown by the "Fix test" above (13_3_1_patch1 and 15_0_15_patch4).
- 141.046 fix-area steps 3-4: the first attempt (inside `relval_fix_check.sh`) ended during step 3 at about 01:46
  with no error in its log; they were rerun by hand with the same commands (`steps34_from_dryrun.sh`) on the same
  `step2.root` and completed (03:19 to 03:42).
