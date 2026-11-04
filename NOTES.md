# NanoAOD photon trigger objects: knowledge base

Everything learned in the session of 4 November 2026 about NanoAOD v13, the NanoAOD
trigger-object machinery, the dead unseeded-leg photon filter bits of the diphoton
triggers, the fix, and the surrounding CMSSW facts. Written for Santanu Mahata.
Statements marked **verified** were read directly from source code or from fetched
files; statements marked **reported** come from documents or repositories found on the
web and were not independently confirmed.

Companion files in this repository:

- `report/NanoAOD_photon_TrigObj_unseeded_bits_issue.pdf`: the 8-page issue report (and
  `report/report.html`, its source; `scripts/render_pdf.js` renders it with Chromium).
- `pr/PR_body.md`: pull-request title and description, in the cms-sw template layout.
- `pr/0001-NanoAOD-photon-TrigObj-unseeded-collection.patch`: the fix as a patch on top of
  upstream `cms-sw/cmssw` master `ed35654b1` (4 November 2026).

---

## 1. One-paragraph summary

The `Photon` selection of `triggerObjectTable` in
`PhysicsTools/NanoAOD/python/triggerObjects_cff.py` accepts only trigger objects whose HLT
collection is `hltEgammaCandidates`. The sub-leading legs of the H to gamma gamma triggers
`HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90` and `_Mass95` (and, in the 2018 and
2022 menus, of `HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId` and `_Mass55`) are built on
`hltEgammaCandidatesUnseeded`. The collection test is an exact label comparison and is
applied before the quality bits are evaluated, so every object carrying the unseeded
filter labels is discarded and the corresponding `TrigObj_filterBits` can never be set.
This has been true since the bits were added in February 2023 (PR 40711): NanoAOD v12,
v13, v14, v15 and upstream master are affected; v10 and v11 are not, because the bits did
not exist yet. The same defect was fixed for electrons in June 2023 (PR 41827) and missed
for photons. The fix is one line: accept both collections in the photon selection.

---

## 2. Repository and session state

- Working checkout: fork `santanumahata/cmssw`, shallow clone, branch
  `claude/fervent-lamport-3oiuh6`, based on fork master `f99356577`
  ("Merge pull request #47943 from ftorrresd/nano_comparison_report", 2025-05-06). This is
  code of the 15_1_X cycle.
- Upstream references fetched into that checkout (remote `upstream` =
  `https://github.com/cms-sw/cmssw`, read-only through the session proxy):
  - `upstream/CMSSW_13_3_X` = `f78d7d4ed` (2026-01-05, "Merge pull request #49602 from
    stahlleiton/MC_CMSSW_13_3_X").
  - tag `CMSSW_13_3_1_patch1` = `0a2662153` (2023-12-12, "Merge pull request #43539 from
    jordan-martins/my-backport2"). **Verified**: `PhysicsTools/NanoAOD` and
    `Configuration/PyReleaseValidation/python/relval_nano.py` are byte-identical between
    this tag and the `CMSSW_13_3_X` tip.
  - `upstream/master` = `ed35654b1` (2026-11-04 07:07 +0100, "Merge pull request #52130
    from stefduponcheel/BadComponentsPayloads").
- 13_3_X release tags: `CMSSW_13_3_0_pre1` to `_pre5`, `CMSSW_13_3_0`, `CMSSW_13_3_1`,
  `CMSSW_13_3_1_patch1`, `CMSSW_13_3_2`, `CMSSW_13_3_2_patch1`, `CMSSW_13_3_3`.
- Commits made (nothing pushed):
  - `1699a39f7` on `claude/fervent-lamport-3oiuh6`: the fix on the fork's May 2025 master.
    Author santanumahata, committer Claude (amended on request of a repository hook).
  - `aebf3eb64` on `nano-photon-trigobj-unseeded`: the same change cherry-picked onto
    upstream master `ed35654b1`; applied cleanly; checked out in a git worktree in the
    session scratchpad. Same author and committer.
- Other HLT menu files fetched for comparison (raw GitHub, `HLT_GRun_cff.py` of the
  branch): `CMSSW_10_6_X` (menu `/dev/CMSSW_10_6_0/GRun/V3`), `CMSSW_12_4_X`
  (`/dev/CMSSW_12_4_0/GRun/V171`), `CMSSW_12_6_X` (`/dev/CMSSW_12_6_0/GRun/V16`).
  `triggerObjects_cff.py` was fetched from `CMSSW_12_4_X`, `CMSSW_12_6_X`, `CMSSW_13_0_X`,
  `CMSSW_14_0_X`, `CMSSW_15_0_X` and `master`.

---

## 3. NanoAOD versions, releases and campaigns

### 3.1 Version to release map (as established in this session)

| NanoAOD | Release | Evidence |
|---|---|---|
| v9 | CMSSW_10_6_X | relval inputs `RunIISummer20UL*MiniAODv2`, era modifier `run2_nanoAOD_106Xv2` (**verified** in code) |
| v10 | CMSSW_12_4_X | era modifier `run3_nanoAOD_124` in 13_3_X (**verified**); PR 40711 bits absent in 12_4_X (**verified**) |
| v11, v11_1 | CMSSW_12_6_X | reported; PR 40711 bits absent in 12_6_X (**verified**) |
| v12 | CMSSW_13_0_X, production 13_0_13 | reported (Purdue AF guide, user's notes); bits present in 13_0_X (**verified**) |
| v13 | CMSSW_13_3_X, production CMSSW_13_3_1_patch1 | dataset strings `NanoAODv13-133X_*_ForNanov13_*` (**verified** in public configs); 13_3_1_patch1 named by choij1589/CustomNanoAOD and by the user's 2022 skim notes (reported) |
| v14 | CMSSW_14_0_X | reported; bits present in 14_0_X (**verified**) |
| v15 | CMSSW_15_0_X (15_0_15_patch4 for 2022/2023 inputs with `run3_nanoAOD_pre142X`; >= 15_0_2 for 2024) | reported (CustomNanoAOD, WMass production repo); relval comments "re-MINI/NANOv15 in 15_0_X" (**verified**) |

The fork master only names v15 ("pre v15" comment at `nano_cff.py:257` for the
`run3_nanoAOD_pre142X` path) and the 106Xv2 input. There is no v13-specific switch anywhere
in the code: the version of a NanoAOD file is set by the release it was made in plus the era.

### 3.2 NanoAOD v13 production (MC)

- Input: 13_0_X MiniAODv4 (`Run3Summer22MiniAODv4`, `Run3Summer22EEMiniAODv4`,
  `Run3Summer23MiniAODv4`, `Run3Summer23BPixMiniAODv4`).
- Command shape (from public configs that mirror the McM setup; **verified** text):

```
cmsDriver.py --python_filename <cfg>.py --eventcontent NANOAODSIM \
  --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM \
  --fileout file:nano.root --conditions 133X_mcRun3_2023_realistic_postBPix_ForNanov13_v2 \
  --step NANO --scenario pp --filein file:miniaod.root --era Run3_2023 --no_exec --mc -n -1
```

One private config (maxgalli/SBI-Htt-EFT) used `--era Run3_2023,run3_nanoAOD_124`; the
`run3_nanoAOD_124` modifier is meant for 12_4_X MiniAOD input and is not part of the
central recipe for MiniAODv4 input.

| Campaign | Global tag | Era |
|---|---|---|
| Run3Summer22NanoAODv13 | `133X_mcRun3_2022_realistic_ForNanov13_v1` | `Run3` |
| Run3Summer22EENanoAODv13 | `133X_mcRun3_2022_realistic_postEE_ForNanov13_v1` | `Run3` |
| Run3Summer23NanoAODv13 | `133X_mcRun3_2023_realistic_ForNanov13_v1` | `Run3_2023` |
| Run3Summer23BPixNanoAODv13 | `133X_mcRun3_2023_realistic_postBPix_ForNanov13_v2` | `Run3_2023` |

Example dataset names (**verified** in public repositories):

- `/GluGluHto2G_M-65_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23NanoAODv13-133X_mcRun3_2023_realistic_ForNanov13_v1-v2/NANOAODSIM`
- `/GluGluHto2G_M-70_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer23BPixNanoAODv13-133X_mcRun3_2023_realistic_postBPix_ForNanov13_v2-v2/NANOAODSIM`
- `/GluGluHtoGG_M-65_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22EENanoAODv13-133X_mcRun3_2022_realistic_postEE_ForNanov13_v1-v3/NANOAODSIM`
- `/GJet_PT-20_DoubleEMEnriched_MGG-40to80_TuneCP5_13p6TeV_pythia8/Run3Summer22NanoAODv13-133X_mcRun3_2022_realistic_ForNanov13_v1-v4/NANOAODSIM`
- Some ggHH samples carry a generator-level fix in the processing string:
  `Run3Summer23NanoAODv13-ggHH_powheg_bugfix_133X_mcRun3_2023_realistic_ForNanov13_v1-v2`.
  That "bugfix" is about the powheg ggHH generation, not about the NANO step.

In 13_3_X the era `Run3_2023` is `Run3` plus `run3_egamma_2023`
(`Configuration/Eras/python/Era_Run3_2023_cff.py`, **verified**). The NanoAOD era modifiers
present in 13_3_X are `run2_nanoAOD_106Xv2`, `run3_nanoAOD_122` and `run3_nanoAOD_124`
(`PhysicsTools/NanoAOD/python/nano_eras_cff.py`). In 15_X they are `run2_nanoAOD_106Xv2` and
`run3_nanoAOD_pre142X` (plus the scouting ones `run3_scouting_nanoAOD_2023/2024`).

### 3.3 NanoAOD v13 for data

- 2022 data were re-processed from the 22Sep2023 MiniAOD at NanoAOD v13 under the
  processing string `16Dec2023` (datasets such as `/Muon/Run2022C-16Dec2023-v1/NANOAOD`,
  `/EGamma/Run2022D-16Dec2023-v1/NANOAOD`, `/EGamma/Run2022E-16Dec2023-v1/NANOAOD`,
  `/EGamma/Run2022G-16Dec2023-v1/NANOAOD`; **verified** dataset strings). The user's own
  2022 skim notes record `16Dec2023` as `CMSSW_13_3_1_patch1`, `22Sep2023` as
  `CMSSW_13_0_13`, and `19Dec2023` (eras F, G) as `CMSSW_13_0_17` (reported).
- No v13 processing of 2023 data was found; 2023 data stay at v12 (`22Sep2023_v1` to `_v4`
  for Run2023C/D; `PromptNanoAODv11p9` for Run2023A/B).
- The exact `133X_dataRun3` global tag of the 16Dec2023 processing was not found.

### 3.4 Later versions (reported, from community tables; indicative only)

- v15: CMSSW_15_0_15_patch4 for 2022/2023 inputs (MiniAODv4 / 22Sep2023 MiniAOD) with eras
  `Run3,run3_nanoAOD_pre142X` (2022) and `Run3_2023,run3_nanoAOD_pre142X` (2023); global tags
  `150X_mcRun3_2022_realistic_v1`, `150X_mcRun3_2022_realistic_postEE_v1`,
  `150X_mcRun3_2023_realistic_v1`, `150X_mcRun3_2023_realistic_postBPix_v1`, data
  `150X_dataRun3_v5`. 2024: CMSSW_15_0_2 to 15_0_17, era `Run3_2024`,
  `150X_mcRun3_2024_realistic_v2` (or v4), data `150X_dataRun3_v2`. 2025 data: era `Run3_2025`,
  `150X_dataRun3_Prompt_v1`. 2026 data: CMSSW_16_0_X, era `Run3_2026`, `161X_dataRun3_Prompt_v1`.
- The uhh-cms/cmsdb campaign names `run3_2022_preEE_nano_v13`, `run3_2022_postEE_nano_v13`,
  `run3_2023_preBPix_nano_v13` (id 320231301) and `run3_2023_postBPix_nano_v13` exist with
  `aux["version"] = 13`.

### 3.5 Other NanoAOD v12 issues met while searching (reported, not verified here)

- Electron MVA NoIso ID is wrong in NanoAODv12; v13 carries the fix ("Add Correct EGM Run3
  electron NonIso MVA ID for EB", PR 43286 backport). Source: choij1589/SKNanoAnalyzer docs.
- Run 3 `Jet_jetId` in NanoAODv12 is not usable as stored (JME coordination issue 117; recompute
  from constituents; beyond |eta| = 3 it kept 46 to 57 % of jets instead of 89 to 93 %, per
  LPC-HH/HH4b). JME dropped the JetID branches in v15 and provides a JSON instead.
- `Flag_ecalBadCalibFilter` in 2022/2023 NanoAOD is the Run 2 filter and misses the bad EB
  crystal of runs 362433 to 367144; analyses apply a jet-based veto using PuppiMET.
- PuppiMET Type-1 corrections do not re-apply the latest JECs at NANO time (cms-sw issue 30304,
  2020).

---

## 4. How the NANO step is built (verified in code)

- `Configuration/Applications/python/ConfigBuilder.py`: `NANODefaultCFF =
  "PhysicsTools/NanoAOD/nano_cff"`, `NANODefaultSeq = "nanoSequence"` (data),
  `"nanoSequenceMC"` (MC), `"nanoSequenceFS"` (FastSim); `NANODefaultCustom =
  "nanoAOD_customizeCommon"`. `prepare_NANO` expands `@` mappings through
  `PhysicsTools.NanoAOD.autoNANO.autoNANO` (sequence and customize keys), schedules the sequence
  as `nanoAOD_step`, appends the customisations, and, if `--hltProcess` is set, rewires
  `process.unpackedPatTrigger.triggerResults`.
- `PhysicsTools/NanoAOD/python/nano_cff.py` (13_3_X): `nanoTableTaskCommon` holds the object
  tasks and tables; `nanoSequenceCommon`, `nanoSequenceOnlyFullSim` (= `triggerObjectTablesTask`),
  `nanoSequenceOnlyData` (proton tables + `lhcInfoTable`), `nanoSequence` (data),
  `nanoSequenceFS`, `nanoSequenceMC`. `nanoAOD_customizeCommon` activates VID electron and
  photon IDs, runs the AK4 and AK8 deep taggers through the `nanoAOD_addDeepInfo*` switches, adds
  tau IDs and ParticleNet information to taus (`nanoAOD_addPNetToTaus`), and boosted-tau IDs for
  Run 2. Run 2 uses AK4 CHS jets (`run2_nanoAOD_ANY`), Run 3 AK4 Puppi.
- `autoNANO` keys in 15_1_X: PHYS, L1, L1FULL, Scout, ScoutMonitor, ScoutFromMini, JME,
  JMErePuppi, L1DPG, Phase2L1DPG, Phase2L1DPGwithGen, MUPOG, MUDPG, MUDPGBKG, MUHLT, HCAL,
  HCALCalib, HCALMC, EGM, Prompt (= PHYS + L1), LepTrackInfo, BTV, GEN, GENFromMini. In 13_3_X
  only PHYS, L1, L1FULL and Prompt exist.
- Relval definitions, `Configuration/PyReleaseValidation/python/relval_nano.py` (15_1_X):
  `_NANO_mc` = `-s NANO,DQM:@nanoAODDQM --process NANO --mc --eventcontent NANOAODSIM,DQM
  --datatier NANOAODSIM,DQMIO -n 10000 --customise Configuration/DataProcessing/Utils.addMonitoring`;
  `_NANO_data` the same with `--data` and NANOAOD. Workflow groups: 2500.0xx Run 2 UL (10_6_X
  MiniAODv2 input, and re-MINI + NANO from AOD), 2500.1xx 13_0_X input (TTbar
  `Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2`, MuonEG `Run2023C-22Sep2023_v4-v1`,
  era `Run3,run3_nanoAOD_pre142X`), 2500.2xx 14_0_X input (era `Run3_2024,run3_nanoAOD_pre142X`
  for data, `Run3,run3_nanoAOD_pre142X` for MC, plus POG and DPG flavours), 2500.3xx re-MINI +
  NANO v15 in 15_0_X (Summer24 AOD, Run2024H AOD), 2500.9xx NANOGEN. In 13_3_X the file had
  12.2, 12.4, 13.0, 13.2 and scouting workflows with eras `Run3,run3_nanoAOD_122`,
  `Run3,run3_nanoAOD_124`, `Run3`.

---

## 5. Trigger-object machinery, end to end (verified in code)

### 5.1 HLT side

- E/gamma filters of a leg are `HLTEgammaGenericFilter` and `HLTEgammaGenericQuadraticFilter`,
  both instances of `HLTGenericFilter` (`HLTrigger/Egamma/plugins/HLTGenericFilter.cc`): line 30
  reads the `l1EGCand` parameter, line 139 calls `filterproduct.addCollectionTag(l1EGTag_)`
  when `saveTags` is true, line 143 sets the saved object type to `trigger::TriggerCluster`,
  line 151 reads the previous filter's objects of that type. `HLTEgammaGenericQuadraticFilter.cc`
  does the same at lines 125 and 133.
- `DataFormats/HLTReco/interface/TriggerTypeDefs.h`: `TriggerPhoton = 81` (line 84),
  `TriggerCluster = 92` (line 95). NanoAOD's `type(92)` therefore selects e/gamma HLT objects.
- The first unseeded filter of a leg is an `HLT1Photon` (`HLTSinglet` of RecoEcalCandidate) with
  `inputTag = hltEgammaCandidatesUnseeded`, `triggerType = 92`, `saveTags = True`
  (`hltDiEG22EtEta2p55UnseededFilter`, master `HLT_GRun_cff.py` line 47223).
- Every filter in the diphoton sequences has `saveTags = True`.

### 5.2 PAT and MiniAOD

- `PhysicsTools/PatAlgos/plugins/PATTriggerProducer.cc` line 699:
  `triggerObject.setCollection(handleTriggerEvent->collectionTagEncoded(iC))`, so an object made
  from the unseeded collection carries `hltEgammaCandidatesUnseeded::HLT`. Filter labels of all
  filters that accepted the object are attached.
- `PhysicsTools/PatAlgos/python/slimming/slimmedPatTrigger_cfi.py`: `slimmedPatTrigger` is a
  `PATTriggerObjectStandAloneSlimmer` with `src = selectedPatTrigger`, `triggerResults =
  TriggerResults::HLT`, `packFilterLabels = True`, `packP4 = True`. The collection string is kept.

### 5.3 NanoAOD

- `PhysicsTools/NanoAOD/python/triggerObjects_cff.py`: `unpackedPatTrigger`
  (`PATTriggerObjectStandAloneUnpacker`, line 8) restores the labels; `triggerObjectTable =
  triggerObjectTableProducer.clone(src = "unpackedPatTrigger", ...)` (line 47) defines one
  `selections` entry per object type; `triggerObjectTablesTask = cms.Task(unpackedPatTrigger,
  triggerObjectTable, l1bits)` (line 447).
- `mksel(selection, doc)` builds one quality-bit entry; a list of filter names is turned into
  an OR of `filter('name')` tests. Bit i is the 0-based position in `qualityBits`.
- `PhysicsTools/NanoAOD/plugins/TriggerObjectTableProducer.cc`: `SelectedObject` holds the
  `sel` cut (`StringCutObjectSelector`), the L1 and L2 seed cuts and cone sizes, the
  `skipObjectsNotPassingQualityBits` flag, and a `StringObjectFunction` built as the sum of
  `2^bit * (selection)` over the entries (asserts: a bit is not inserted twice, bit < 31).
  `match(obj)` is `cut(obj)` (line 139). In `produce` (lines 151 to 160) each object is first
  tested with `sel.match(obj)`; only then are the bits computed; with the skip flag an object with
  no bit is dropped. A later self-cleaning (lines 162 to 176) merges objects of the same id whose
  pT differs by less than 1e-6 and whose deltaR squared is below 1e-6, OR-ing their bits.
- `DataFormats/PatCandidates/interface/TriggerObject.h` line 158: `coll(name)` calls
  `hasCollection(name)`. `src/TriggerObject.cc` lines 54 to 71: exact string equality, otherwise
  split into label, instance, process; with no process in the request, the instance must match and
  the label must be equal. No wildcard. `hltEgammaCandidates` therefore does not match
  `hltEgammaCandidatesUnseeded::HLT`. Upstream master differs from the fork only by a `reserve()`
  call in `triggerObjectTypes()`.

### 5.4 Selections per object type (fork master)

- Electron (id 11): `type(92) && pt > 7 && (coll('hltEgammaCandidates') ||
  coll('hltEgammaCandidatesUnseeded')) && (filter('*PixelMatchFilter*') ||
  filter('*PixelMatchUnseededFilter'))`. In 13_0_X the electron selection was still
  `coll('hltEgammaCandidates') && filter('*PixelMatchFilter')`; the unseeded collection was added
  by PR 41827 (June 2023).
- Photon (id 22): `type(92) && pt > 15 && coll('hltEgammaCandidates')` (pt > 20 in 12_4_X and
  12_6_X). `skipObjectsNotPassingQualityBits = True`. No era modifier touches the photon block.
- Muon (id 13): `type(83) && pt > 5 && (coll('hltIterL3MuonCandidates') || (pt > 45 &&
  coll('hltHighPtTkMuonCands')) || (pt > 95 && coll('hltOldL3MuonCandidates')))`.
- Tau (id 15), BoostedTau (1515), Jet, FatJet, MET and others follow.

### 5.5 Photon quality bits by version (verified from the branch files)

12_4_X and 12_6_X (12 bits, no diphoton bits): hltEG33L1EG26HEFilter, hltEG50HEFilter,
hltEG75HEFilter, hltEG90HEFilter, hltEG120HEFilter, hltEG150HEFilter, hltEG175HEFilter,
hltEG200HEFilter, hltHtEcal800, hltEG110EBTightIDTightIsoTrackIsoFilter,
hltEG120EBTightIDTightIsoTrackIsoFilter, hltMu17Photon30IsoCaloIdPhotonlegTrackIsoFilter.

13_0_X, 13_3_1_patch1, 14_0_X (18 bits):

| Bit | Filter | Runs on |
|---|---|---|
| 0 to 7 | hltEG33L1EG26HEFilter, hltEG50/75/90/120/150/175/200HEFilter | hltEgammaCandidates |
| 8 | hltHtEcal800 | HT object |
| 9 | hltEG110EBTightIDTightIsoTrackIsoFilter | hltEgammaCandidates |
| 10 | hltEG120EBTightIDTightIsoTrackIsoFilter | hltEgammaCandidates (not in the 2025 menu) |
| 11 | hltMu17Photon30IsoCaloIdPhotonlegTrackIsoFilter ("1mu-1photon") | hltEgammaCandidates |
| 12 | hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter | hltEgammaCandidates |
| 13 | hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter | hltEgammaCandidates |
| 14 | hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter | **hltEgammaCandidatesUnseeded, dead** |
| 15 | hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter | **hltEgammaCandidatesUnseeded, dead** |
| 16 | hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter | hltEgammaCandidates, 2018 and 2022 menu names |
| 17 | hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter | **hltEgammaCandidatesUnseeded, dead**; 2018 and 2022 names |

15_0_X and master (21 bits): bits 9 and 10 become hltEG45EBTightIDTightIsoTrackIsoFilter and
hltEG50EBTightIDTightIsoTrackIsoFilter, the old 9 to 17 shift to 11 to 19, and bit 20 is the
wildcard `hltEG*L1VBFLooseIsoEGHEFilter`. The dead bits are 16, 17 and 19. Decimal values of the
dead bits: 16384, 32768, 131072 (v12 to v14); 65536, 131072, 524288 (v15, master).

All non-diphoton photon-bit filters were checked in the 2025 menu: each one that exists runs on
`hltEgammaCandidates` (including the Mu17_Photon30 photon leg and `hltEG22L1VBFLooseIsoEGHEFilter`).

### 5.6 Changes to `triggerObjects_cff.py` between v13 and the fork master (verified diff)

Electron: `*PixelMatchFilter*` wildcard; new bits "1e-1tau PNet", `hltEle30WPTightGsfTrackIsoFilter`,
`hltEle*erWPTightGsfTrackIsoFilterNoRhoCorrectionForVBF`. Photon: bits for hltEG45/50EBTightID,
and the VBF wildcard. Muon: "1mu-1tau PNet". Tau: selection and bits reorganised around PNet
filters (30 bits). BoostedTau: new selection and three PNet/ParticleNet bits. Jet: bits 31 to 45
(QuadPFJet PNet, VBF categories, VBF+gamma, VBF+e, SinglePFJetX, DiPFJetAveX). FatJet: PNetBB bit.
Run 2 2017 muon filter `hltIterL3MuonCandidates` bit. The photon `sel` line is unchanged
throughout.

---

## 6. The HLT paths

### 6.1 HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90 / Mass95

Path (13_3_1_patch1 `HLT_FULL_cff.py` line 119468, version `_v19`; `_v17` in `HLT_2023v12`;
`_v15` in the 2022 menus; `_v13` in the 2018 menu; `_v24` in the 2025 menu, master GRun line
86983): `HLTBeginSequence + hltL1sSingleAndDoubleEGor + hltPreDiphoton3022R9IdORIsoCaloIdANDHER9IdMass90
+ HLTDiphoton30L22R9Id85b90eORIso60CaloId15b35eANDHE12R9Id50b80eSequence +
hltDiEG22R9Id85b90eORIso60CaloId15b35eANDHE12R9Id50b80eMass90CombMassLastFilter + HLTEndSequence`.
Mass95 uses the same sequence and `...Mass95CombMassLastFilter`.

Sequence (line 118801), filters in order, all `saveTags = True`:

Seeded leading leg on `hltEgammaCandidates`: hltEGL1SingleAndDoubleEGOrFilter
(HLTEgammaL1TMatchFilterRegional), hltEG30L1SingleAndDoubleEGOrEtFilter (HLTEgammaEtFilter),
hltEG30LR9Id50b80eR9IdFilter (HLTEgammaGenericFilter), hltEG30LHE12R9Id50b80eHEFilter
(HLTEgammaGenericQuadraticFilter), [ignore] hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter
(bit 12), [ignore] hltEG30LCaloId15b35eHE12R9Id50b80eClusterShapeFilter, [ignore]
hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter (bit 13),
hltEG30LRId85ORIso60CaloId15b35eANDHE12R9Id50b80eLegCombLastFilter (HLTEgammaDoubleLegCombFilter).

Unseeded sub-leading leg on `hltEgammaCandidatesUnseeded`: hltDiEG22EtEta2p55UnseededFilter
(HLT1Photon), hltDiEG22R9Id50b80eR9IdUnseededFilter, hltDiEG22HE12R9Id50b80eHEUnseededFilter,
[ignore] hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter (bit 15), [ignore]
hltEG22CaloId15b35eHE12R9Id50b80eClusterShapeUnseededFilter, [ignore]
hltEG22Iso60CaloId15b35eHE12R9Id50b80eEcalIsoUnseededFilter, [ignore]
hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter (bit 14).

Pair: hltDiEG22R9Id85b90eORIso60CaloId15b35eANDHE12R9Id50b80eMass90CombMassLastFilter
(HLTEgammaCombMassFilter), no NanoAOD bit.

Parameters of the two unseeded last filters (master GRun lines 47281 to 47302 and 47362 to 47383):
R9UnseededLastFilter: candTag hltDiEG22HE12R9Id50b80eHEUnseededFilter, varTag
hltEgammaR9IDUnseeded:r95x5, thresholds EB 0.85, EE 0.9 (greater than), l1EGCand
hltEgammaCandidatesUnseeded. TrackIsoUnseededLastFilter: candTag
hltEG22Iso60CaloId15b35eHE12R9Id50b80eEcalIsoUnseededFilter, varTag hltEgammaHollowTrackIsoUnseeded,
lessThan, useEt, thrRegular 6.0 GeV, thrOverE 0.002, l1EGCand hltEgammaCandidatesUnseeded.

### 6.2 HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId (and _Mass55)

2022 menus (12_4_X GRun V171, 12_6_X GRun V16), paths `_v3`, sequence
`HLTDiphoton3018R9Idb50e90ANDIso60CaloId15b35eANDHE12b10eSequence` (+ `Mass55` variant):

Seeded: hltEGL1SingleAndDoubleEGOrFilter, hltEG30L1SingleAndDoubleEGOrEtFilter,
hltEG30R9Id50b80eR9IdFilter, hltEG30HE12b10eR9Id50b80eHEFilter,
hltEG30R9Id50b90eHE12b10eR9Id50b80eR9IdFilter,
hltEG30CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eClusterShapeFilter,
hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter (NanoAOD bit 16 / 18).
Unseeded: hltDiEG18EtUnseededFilter, hltDiEG18R9Id50b80eR9IdUnseededFilter,
hltDiEG18HE12b10eR9Id50b80eHEUnseededFilter, hltEG18R9Id50b90eHE12b10eR9Id50b80eR9IdUnseededFilter,
hltEG18CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eClusterShapeUnseededFilter,
hltEG18Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoUnseededFilter,
hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter
(NanoAOD bit 17 / 19, dead).

2018 menu (10_6_X GRun V3): the same filter names inside
`HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_NoPixelVeto_v2` and `_NoPixelVeto_Mass55_v2`
(sequences `...NoPixelVetoSequence`). The 2018 menu also has
`HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_{NoPixelVeto,PixelVeto}_Mass55`.

2023 and later menus (2023v12 `_v5`, 13_3 FULL `_v7`, 2025 GRun `_v12`), sequence
`HLTDiphoton3018R9Id50b90eANDHE10b9eANDCaloId11b32eANDIso60b40eSequence`, re-tuned thresholds and
renamed filters:
Seeded: hltEGL1SingleAndDoubleEGOrFilter, hltEG30L1SingleAndDoubleEGOrEtFilter,
hltEG30R9Id50b90eR9IdFilter, hltEG30HE10b9eR9Id50b90eHEFilter,
hltEG30CaloId11b32eHE10b9eR9Id50b90eClusterShapeFilter,
hltEG30Iso60b40eCaloId11b32eHE10b9eR9Id50b90eEcalIsoFilter (no NanoAOD bit).
Unseeded: hltDiEG18EtUnseededFilter, hltDiEG18R9Id50b90eR9IdUnseededFilter,
hltDiEG18HE10b9eR9Id50b90eHEUnseededFilter, hltDiEG18CaloId11b32eHE10b9eR9Id50b90eClusterShapeUnseededFilter,
hltDiEG18Iso60b40eCaloId11b32eHE10b9eR9Id50b90eEcalIsoUnseededFilter,
hltDiEG18TrackIso60Iso60b40eCaloId11b32eHE10b9eR9Id50b90eTrackIsoUnseededFilter (no NanoAOD bit).
Consequence: for 2023 to 2025 data and MC, NanoAOD bits 16/17 (18/19) match nothing on either leg
of the 30_18 paths. This is a stale-name problem, separate from the collection problem.

### 6.3 Diphoton and DoublePhoton paths per menu (verified lists)

- 2018 (10_6_X GRun V3): Diphoton30PV_18PV (NoPixelVeto, PixelVeto) Mass55; Diphoton30_18
  NoPixelVeto (and Mass55); Diphoton30_22 Mass90/Mass95 v13.
- 2022 (12_4_X GRun V171, 12_6_X GRun V16): Diphoton20_14 and 22_14 eta1p5 R9IdL AND HE(T) AND
  IsoTCaloIdT (v2); Diphoton30_18 (and Mass55) v3; Diphoton30_22 Mass90/Mass95 v15.
- 2023 (2023v12 / 13_3 FULL): Diphoton20_14, 22_14, 24_14, 24_16 eta1p5 (v4 / v6); Diphoton30_18
  (and Mass55) v5 / v7; Diphoton30_22 Mass90/Mass95 v17 / v19; DoublePhoton33_CaloIdL v11 / v13,
  DoublePhoton70 v11 / v13, DoublePhoton85 v19 / v21.
- 2025 (master GRun and FULL): the same low-mass set at v11; Diphoton30_18 (and Mass55) v12;
  Diphoton30_22 Mass90/Mass95 v24; DiphotonMVA14p25 {High, Low, Medium, TightHigh, TightLow,
  TightMedium} Mass60 v1; DoublePhoton33_CaloIdL v18, DoublePhoton70 v18, DoublePhoton85 v26.
- NanoAOD has no photon bits for the low-mass eta1p5 paths, the DiphotonMVA paths or the
  DoublePhoton paths.

---

## 7. The bug, precisely

1. The unseeded leg's filters save objects referenced through `hltEgammaCandidatesUnseeded`,
   with type 92 and the filter labels attached (section 5.1).
2. PAT stores the collection name on the object; MiniAOD keeps it (section 5.2).
3. NanoAOD's photon selection requires `coll('hltEgammaCandidates')`, an exact label match
   (section 5.3), so the unseeded objects fail the selection.
4. The selection runs before the quality bits; a rejected object never reaches the bit
   evaluation; the later self-cleaning only sees accepted objects.
5. Therefore photon bits 14, 15, 17 (v12 to v14) or 16, 17, 19 (v15, master) are documented in
   `TrigObj_filterBits` but can never be set. The matching leading-leg bits 12/13 (14/15) work.

Observation that prompted the investigation: in NanoAOD v13 the last unseeded filter bit of the
Diphoton30_22 path is present in the documentation but no photon trigger object ever has it.

### 7.1 Ruled out

- Wrong filter names: all four 30_22 names exist with `saveTags = True` in every menu from 2018
  to 2025 (10_6_X, 12_4_X, 12_6_X GRun; 2023v12; 13_3_1_patch1 GRun and FULL; master GRun and FULL).
- Objects missing from MiniAOD: the electron selection has relied on
  `coll('hltEgammaCandidatesUnseeded')` since June 2023 and PR 41827 observed the extra objects.
- Wrong object type: the filters save type 92.
- Era overrides: none for the photon block.
- v13-specific code: the v13 tag equals the 13_3_X tip; all later branches have the same line.

### 7.2 Affected NanoAOD versions (verified per branch)

| Version | Branch | Photon sel | Diphoton unseeded bits | Affected |
|---|---|---|---|---|
| v10 | 12_4_X | seeded only, pt > 20 | absent | no |
| v11, v11_1 | 12_6_X | seeded only, pt > 20 | absent | no |
| v12 | 13_0_X | seeded only | 14, 15, 17 | yes |
| v13 | 13_3_1_patch1 | seeded only | 14, 15, 17 | yes |
| v14 | 14_0_X | seeded only | 14, 15, 17 | yes |
| v15 | 15_0_X | seeded only | 16, 17, 19 | yes |
| master (fork May 2025; upstream Nov 2026) | | seeded only | 16, 17, 19 | yes |

### 7.3 Affected triggers per menu era

| Era | Paths with a dead unseeded photon bit | Dead bits (v12 to v14 / v15+) |
|---|---|---|
| 2018 | Diphoton30_22 Mass90_v13, Mass95_v13; Diphoton30_18 NoPixelVeto_v2, NoPixelVeto_Mass55_v2 | 14, 15 / 16, 17; 17 / 19 |
| 2022 | Diphoton30_22 Mass90_v15, Mass95_v15; Diphoton30_18_v3, Mass55_v3 | 14, 15 / 16, 17; 17 / 19 |
| 2023 | Diphoton30_22 Mass90_v17 (v19), Mass95_v17 (v19) | 14, 15 / 16, 17 |
| 2024, 2025 | Diphoton30_22 Mass90_v24, Mass95_v24 | 16, 17 |

Mass90 and Mass95 share filters, so one fix restores both; likewise the 30_18 pair.

### 7.4 History

- 8 Feb 2023, PR 40711 "diphoton_hlt_filters_added" (Soumyatifr): added the six diphoton photon
  bits "needed for the next iteration of the NANOAOD production"; reviewer swertz asked about
  OR-grouping; the author kept separate bits after consulting lfinco. Photon selection untouched.
- 8 Jun 2023, PR 41827 "Add CaloIdL_MW unseeded filter to nanoAOD filterBits" (RSalvatico):
  added `hltDiEle*CaloIdLMWPMS2UnseededFilter`, allowed `*PixelMatchUnseededFilter`, and "added
  the collection hltEgammaCandidatesUnseeded, which are the objects on which the selection of the
  unseeded trigger leg is made" to the Electron selection; noted "we are effectively allowing more
  trigger objects by adding one input collection".
- Nov to Dec 2023, 13_3_X backports for v13: 43209 (photon superclusterEta), 43254 (revert
  precision decrease), 43286 (electron NonIso MVA ID for EB), 43292 (CaloIdL_MW seeded filter and
  split legs of CaloIdL_TrackIdL_IsoVL on filterBits; the PR text says the backport "is required
  for the production of NanoAODv13 from CMSSW_13"), 43383 (tau decay products in NanoDQM), 43387
  (L1 unprefirable event info and Final OR in BX-1/-2), 43470 (tau trigger filter bit fixes),
  43513 (photon variable precision 10).
- No upstream issue or PR on photon unseeded trigger objects was found (searches on
  `hltEgammaCandidatesUnseeded`, `R9UnseededLastFilter`, `Diphoton30_22 filterBits`).

---

## 8. The fix

```diff
-            sel = cms.string("type(92) && pt > 15 && coll('hltEgammaCandidates')"),
+            sel = cms.string("type(92) && pt > 15 && (coll('hltEgammaCandidates') || coll('hltEgammaCandidatesUnseeded'))"),
```

- Why this form: `hasCollection` has no wildcard; mirrors the Electron selection.
- Effect: unseeded objects enter the photon branch; with `skipObjectsNotPassingQualityBits` only
  those that pass one of the photon filters are written, and only the diphoton sub-leading-leg
  filters run on the unseeded collection. Coincident seeded/unseeded duplicates (same pT and
  direction within 1e-6) are merged by the self-cleaning with OR-ed bits; otherwise a second entry
  appears, as for electrons. Bit numbers, docs and event content unchanged.
- Not changed by the fix: the 2023+ names of the 30_18 path (needs new entries), and the paths
  without any photon bits (low-mass eta1p5, DiphotonMVA, DoublePhoton).

### 8.1 Validation plan (not executable here: no CMSSW runtime in the session container)

1. `runTheMatrix.py -l 2500.1,2500.11,2500.2,2500.21` before and after.
2. Count photon TrigObj with the unseeded bits in events firing the diphoton path: zero before,
   non-zero and of the order of the number of triggered events after.
3. Compare `nTrigObj`, trigger-object DQM histograms and file size; only diphoton-triggered events
   should move.

```python
import uproot, awkward as ak, numpy as np
t = uproot.open("nano.root")["Events"]
a = t.arrays(["TrigObj_id", "TrigObj_filterBits", "HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"])
ph    = a.TrigObj_id == 22
fired = a["HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"]
for bit in (16, 17):           # 14, 15 for NanoAOD v12 to v14
    hasbit = ak.any((a.TrigObj_filterBits[ph] >> bit) & 1 == 1, axis=1)
    print(bit, np.sum(hasbit & fired), "of", np.sum(fired))
```

### 8.2 Pull request readiness

- Branch `nano-photon-trigobj-unseeded` = upstream master `ed35654b1` + `aebf3eb64`; the patch is
  `pr/0001-NanoAOD-photon-TrigObj-unseeded-collection.patch`; title and body in `pr/PR_body.md`.
- Publish: `git push -u origin nano-photon-trigobj-unseeded`, then open the PR from
  `santanumahata:nano-photon-trigobj-unseeded` to `cms-sw:master`. Needs the xpog signature.
  The bot's RelVal comparison will show the expected `nTrigObj` and DQM differences. Cite PR 40711
  and PR 41827.
- Backport: request `CMSSW_15_0_X` if another NanoAOD production from that branch is planned.
- Follow-ups, separate from the one-line fix:
  1. Add the 2023+ names of the 30_18 path as alternatives inside the existing two entries so bit
     numbers stay stable, e.g. `mksel(["hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter",
     "hltEG30Iso60b40eCaloId11b32eHE10b9eR9Id50b90eEcalIsoFilter"], ...)` and
     `mksel(["hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter",
     "hltDiEG18TrackIso60Iso60b40eCaloId11b32eHE10b9eR9Id50b90eTrackIsoUnseededFilter"], ...)`.
     The unseeded entry only works together with the collection fix.
  2. Bits for the low-mass eta1p5 diphoton paths, the DiphotonMVA14p25 paths and the DoublePhoton
     paths, to be agreed with the EGM POG and the Higgs PAG.

---

## 9. Impact on analyses

- Any NanoAOD-based trigger matching of the sub-leading photon to its HLT leg finds no candidate
  in v12 to v15. Leg-by-leg trigger efficiency studies can only use the leading leg. HiggsDNA
  workflows that match to `TrigObj` are affected in the same way.
- Existing files cannot be repaired: the unseeded objects were never written. Only a new NANO
  pass with the fix restores the information.
- For the user's 2023 low-mass diphoton analysis: the M-65 and M-70 `GluGluHto2G` points exist
  only at NanoAODv13 (both 2023 campaigns), the M-5 to M-60 scan at v12; the low-mass eta1p5
  triggers have no photon bits at all in any NanoAOD version.

---

## 10. Environment notes for future sessions

- Not reachable from the cloud session: `twiki.cern.ch`, `cms-nanoaod-integration.web.cern.ch`
  (McM and other cern.ch hosts presumably the same), `web.archive.org`.
- Reachable: `github.com`, `raw.githubusercontent.com` (curl works through the proxy), GitHub
  search through `gh api -X GET search/issues|code|commits`. Issue search requires `is:issue` or
  `is:pr` in the query. Code search returns text fragments with
  `-H "Accept: application/vnd.github.text-match+json"` and only indexes default branches.
- Upstream `cms-sw/cmssw` can be fetched read-only (add a remote, `git fetch --depth 1 upstream
  <branch|tag>`); GitHub API tools are scoped to the attached fork; repository creation is not
  allowed from the session.
- No CMSSW runtime (no scram, cmsRun or ROOT) in the container; code can only be read.
- PDF generation: Node `playwright` 1.63.0 with the pre-installed Chromium (HTML to PDF);
  `reportlab`, `pypdf`, `pdftotext`, `pdftoppm` present; the Python `playwright` module is not.

---

## 11. Key commands used (reproducibility)

```bash
# upstream references
git remote add upstream https://github.com/cms-sw/cmssw
GIT_LFS_SKIP_SMUDGE=1 git fetch --depth 1 upstream CMSSW_13_3_X
GIT_LFS_SKIP_SMUDGE=1 git fetch --depth 1 upstream tag CMSSW_13_3_1_patch1
GIT_LFS_SKIP_SMUDGE=1 git fetch --depth 1 upstream master

# v13 configuration and menu
git show CMSSW_13_3_1_patch1:PhysicsTools/NanoAOD/python/triggerObjects_cff.py | sed -n '76,112p'
git show CMSSW_13_3_1_patch1:HLTrigger/Configuration/python/HLT_FULL_cff.py \
  | grep -n "^fragment.HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"

# which collection a filter runs on
awk '/^fragment.hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter = /{p=1} p{print} p&&/^\)/{exit}' \
  HLTrigger/Configuration/python/HLT_GRun_cff.py

# matcher and producer
sed -n '/bool TriggerObject::hasCollection/,/^}/p' DataFormats/PatCandidates/src/TriggerObject.cc
grep -n "if (sel.match(obj))" PhysicsTools/NanoAOD/plugins/TriggerObjectTableProducer.cc

# other branches' configuration without a full fetch
curl -sS -L -o trig_13_0.py https://raw.githubusercontent.com/cms-sw/cmssw/CMSSW_13_0_X/PhysicsTools/NanoAOD/python/triggerObjects_cff.py

# GitHub searches
gh api -X GET search/issues -f q='repo:cms-sw/cmssw is:pr base:CMSSW_13_3_X nanoAOD' --jq '.items[].html_url'
gh api -H "Accept: application/vnd.github.text-match+json" -X GET search/code \
  -f q='"ForNanov13" cmsDriver' --jq '.items[] | .text_matches[].fragment'
```

---

## 12. Sources

- cms-sw/cmssw PR 40711: https://github.com/cms-sw/cmssw/pull/40711
- cms-sw/cmssw PR 41827: https://github.com/cms-sw/cmssw/pull/41827
- cms-sw/cmssw PR 43292 (13_3_X backport "for the production of NanoAODv13"): https://github.com/cms-sw/cmssw/pull/43292
- cms-sw/cmssw PR 43286, 43470, 43209, 43254, 43383, 43387, 43513 (13_3_X NanoAOD backports)
- uhh-cms/cmsdb v13 campaigns: https://github.com/uhh-cms/cmsdb (campaigns/run3_2023_preBPix_nano_v13 and siblings)
- bhbam/MCProduction_run3 (v13 NANO config): https://github.com/bhbam/MCProduction_run3
- maxgalli/SBI-Htt-EFT (v13 cmsDriver in README): https://github.com/maxgalli/SBI-Htt-EFT
- choij1589/CustomNanoAOD (release and era tables; "Run3 Nano v13 (legacy)" = CMSSW_13_3_1_patch1): https://github.com/choij1589/CustomNanoAOD
- choij1589/SKNanoAnalyzer docs (v12 electron MVA NoIso bug; custom Run 3 JetID): https://github.com/choij1589/SKNanoAnalyzer
- LPC-HH/HH4b PR 368 (NanoAODv12 jetId numbers, ECAL bad-calib veto): https://github.com/LPC-HH/HH4b/pull/368
- WMass/WMassNanoProduction (v15 production notes): https://github.com/WMass/WMassNanoProduction
- Purdue AF private MC guide (MiniAODv4/NanoAODv12 with CMSSW_13_0_13): https://analysis-facility.physics.purdue.edu/en/latest/guide-mc-gen.html
- santanumahata/2023_lowmass_analysis (2022 skim notes: 22Sep2023 = 13_0_13, 16Dec2023 = 13_3_1_patch1, 19Dec2023 = 13_0_17)
