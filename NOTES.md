# NanoAOD photon trigger objects: knowledge base

Everything learned in the sessions of 4 November 2026 about NanoAOD v13, the NanoAOD
trigger-object machinery, the dead unseeded-leg photon filter bits of the diphoton
triggers, the fix, and the surrounding CMSSW facts. Written for Santanu Mahata.

This is the **second pass**: every statement of the first version was re-checked against
the source code, the release tags and the HLT menus. Statements marked **verified** were
read directly from source code or from fetched files; statements marked **reported** come
from documents or repositories found on the web and were not independently confirmed.
Section 0 lists what the second pass corrected.

Companion files in this repository:

- `report/NanoAOD_photon_TrigObj_unseeded_bits_issue.pdf`: the issue report (and
  `report/report.html`, its source; `scripts/render_pdf.js` renders it with Chromium).
- `pr/PR_body.md`: pull-request title and description, in the cms-sw template layout.
- `pr/0001-NanoAOD-photon-TrigObj-unseeded-collection.patch`: the fix as a patch on top of
  upstream `cms-sw/cmssw` master `ed35654b1` (4 November 2026).
- `scripts/`: the scanners used for the verification (section 11).

---

## 0. Corrections made in the second pass

The conclusion of the first pass stands: the three unseeded-leg photon bits can never be
set, the one-line fix is correct, and no other change is needed for the Diphoton30_22
paths. The following details of the first version were wrong or imprecise and are fixed
below.

1. **Object type.** `HLTGenericFilter` (and `HLTEgammaGenericQuadraticFilter`) save their
   objects as `trigger::TriggerPhoton` (81) when `saveTags` is true, not as
   `TriggerCluster` (92). Type 92 comes from the first filter of each leg (`HLT1Photon`
   with `triggerType = 92` on the unseeded leg; the L1-match and Et filters on the seeded
   leg). PAT attaches to an object the types of **all** filters that accepted it, so the
   objects carry both 81 and 92 and `type(92)` is satisfied on both legs. Nothing changes
   in the diagnosis, but the first notes described line 143 of `HLTGenericFilter.cc` wrongly.
2. **Wildcards in `coll()`.** `pat::TriggerObjectStandAlone::hasCollection` (an override)
   does support `*` wildcards; it falls back to the exact comparison of
   `pat::TriggerObject::hasCollection` only when the argument has no `*`. The selection
   string `coll('hltEgammaCandidates')` has none, so the comparison is exact. A wildcard
   form `coll('hltEgammaCandidates*')` would also work; the explicit OR was kept because it
   names the two collections and mirrors the Electron selection.
3. **Producer versions.** v12 to v14 (and also `CMSSW_15_0_0`, `CMSSW_15_0_1`): bits are a
   32-bit `int` (`assert(bit < 31)`), `TrigObj_filterBits` is `Int_t`, and the duplicate
   merging requires both |delta pT| < 1e-6 and delta R squared < 1e-6 (the pT condition was
   dropped in `CMSSW_15_0_0`). From `CMSSW_15_0_2` and in master: bits are `uint64_t`
   (`assert(bit < 64)`), the branch is 64-bit unsigned, and the merging tests only
   delta R squared < 1e-6. The first notes quoted the 32-bit assert and the pT condition
   for all versions.
4. **One object, several selections.** Since 13_0_X an object is tested against every
   selection and can be written once per selection it passes (for example as id 11 and
   as id 22). 12_4_X (v10) still had a `break` after the first match.
5. **Mass filter module.** The final pair filter of the Mass90/Mass95 paths is an
   `HLTEgammaAllCombMassFilter`, not `HLTEgammaCombMassFilter`.
6. **Path versions.** The frozen 2024 menu has `_v22` of the Mass90/Mass95 paths (the first
   notes said `_v24` for 2024 and 2025). `_v24` is the development menu of May 2025 in the
   fork; the frozen 2025 menu has `_v26`; the frozen 2026 menu `_v29`; the 16_1_X GRun
   development menu `_v30`. The frozen early-2022 menu (`2022v12`) still has `_v13`.
   Section 6 has the full matrix.
7. **Relval workflow numbers.** `2500.1`, `2500.11`, `2500.2`, `2500.21` do not exist. The
   NanoAOD-only workflows are numbered `2500.1001`, `2500.1101`, `2500.2001`, `2500.2101`
   in 15_1_X of May 2025, and upstream master no longer defines them at all. Section 8.1
   gives workflows that exist today.
8. **`hltEG120EBTightIDTightIsoTrackIsoFilter`** (photon bit 10, bit 12 in v15) exists only
   in the 2018 menu and the frozen early-2022 menu; it is absent from every menu from
   2022 v1.4 on (the first notes said "not in the 2025 menu").
9. **History.** PR 43292 is the 13_3_X backport of PR 43247 (master, November 2023).
   PRs 47594 (master) and 47601 (15_0_X), March 2025, are consistent with the change
   between `CMSSW_15_0_1` and `CMSSW_15_0_2` that added the `hltEG45/50EBTightID` bits and
   the VBF wildcard bit and moved the bits to 64 bits; the v15 numbering 16/17/19 therefore
   holds from `CMSSW_15_0_2`.
10. **Line numbers.** `PATTriggerProducer.cc`: `setCollection` at line 699 in the fork,
    line 700 in upstream master. `HLTGenericFilter.cc`: `addCollectionTag` at line 139
    (fork) / 141 (upstream); the type logic at lines 143 to 145 (fork) / 145 to 147
    (upstream).
11. **Photon pT threshold.** `CMSSW_13_0_0` still had `pt > 20`; `pt > 15` is in
    `CMSSW_13_0_1` and every later 13_0_X tag, so the v12 production release
    `CMSSW_13_0_13` has 15.
12. **Electron precedent.** The Electron selection accepts the unseeded collection since
    PR 41827 (June 2023); the first NanoAOD production version with it is v13, not v12
    (13_0_13 still has the seeded-only Electron selection).
13. **Validation snippet** parenthesised (operator precedence) and extended to 64-bit bits.
14. **Environment.** `api.github.com` and `patch-diff.githubusercontent.com` are blocked
    for repositories not attached to the session; `raw.githubusercontent.com` works for
    branches and tags.

---

## 1. One-paragraph summary

The `Photon` selection of `triggerObjectTable` in
`PhysicsTools/NanoAOD/python/triggerObjects_cff.py` accepts only trigger objects whose HLT
collection is `hltEgammaCandidates`. The sub-leading legs of the H to gamma gamma triggers
`HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90` and `_Mass95` (and, in the 2018 and
2022 menus, of `HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId` and `_Mass55`) are built on
`hltEgammaCandidatesUnseeded`. The collection test, written without a wildcard, is an exact
label comparison and is applied before the quality bits are evaluated, so every object
carrying the unseeded filter labels is discarded and the corresponding `TrigObj_filterBits`
can never be set. This has been true since the bits were added in February 2023 (PR 40711):
NanoAOD v12, v13, v14, v15 and upstream master are affected; v10 and v11 are not, because
the bits did not exist yet. The same defect was fixed for electrons in June 2023 (PR 41827)
and missed for photons. The fix is one line: accept both collections in the photon
selection.

---

## 2. Repository and session state

- Working checkout: fork `santanumahata/cmssw`, shallow clone, branch
  `claude/fervent-lamport-3oiuh6`, based on fork master `f99356577`
  ("Merge pull request #47943 from ftorrresd/nano_comparison_report", 2025-05-06). This is
  code of the 15_1_X cycle (its GRun menu is `/dev/CMSSW_15_0_0/GRun/V62`, its FULL menu
  `/dev/CMSSW_15_0_0/HLT/V78`, and it ships the frozen menu `HLT_2025v10_cff.py`).
- Upstream references fetched into that checkout (remote `upstream` =
  `https://github.com/cms-sw/cmssw`, read-only through the session proxy):
  - `upstream/CMSSW_13_3_X` = `f78d7d4ed` (2026-01-05, "Merge pull request #49602 from
    stahlleiton/MC_CMSSW_13_3_X").
  - tag `CMSSW_13_3_1_patch1` = `0a2662153` (2023-12-12, "Merge pull request #43539 from
    jordan-martins/my-backport2"). **Verified**: `PhysicsTools/NanoAOD` and
    `Configuration/PyReleaseValidation/python/relval_nano.py` are byte-identical between
    this tag and the `CMSSW_13_3_X` tip.
  - `upstream/master` = `ed35654b1` (2026-11-04 07:07 +0100, "Merge pull request #52130
    from stefduponcheel/BadComponentsPayloads"). This is the 16_1_X cycle: its GRun menu is
    `/dev/CMSSW_16_1_0/GRun/V16` and it ships the frozen 2026 menu `HLT_2026v13_cff.py`
    (`/frozen/2026/2e34/v1.3/HLT/V1`).
- 13_3_X release tags: `CMSSW_13_3_0_pre1` to `_pre5`, `CMSSW_13_3_0`, `CMSSW_13_3_1`,
  `CMSSW_13_3_1_patch1`, `CMSSW_13_3_2`, `CMSSW_13_3_2_patch1`, `CMSSW_13_3_3`.
- Commits made (nothing pushed):
  - `1699a39f7` on `claude/fervent-lamport-3oiuh6`: the fix on the fork's May 2025 master.
    Author santanumahata, committer Claude (amended on request of a repository hook).
  - `aebf3eb64` on `nano-photon-trigobj-unseeded`: the same change cherry-picked onto
    upstream master `ed35654b1`; applied cleanly; checked out in a git worktree in the
    session scratchpad. Same author and committer.
- Files fetched from `raw.githubusercontent.com` for the verification (all **verified**
  by reading):
  - `PhysicsTools/NanoAOD/python/triggerObjects_cff.py` at the branch tips `CMSSW_12_4_X`,
    `CMSSW_12_6_X`, `CMSSW_13_0_X`, `CMSSW_14_0_X`, `CMSSW_15_0_X`, and at the tags
    `CMSSW_13_0_0`, `CMSSW_13_0_1` to `CMSSW_13_0_17`, `CMSSW_13_3_0`, `CMSSW_14_0_0`,
    `CMSSW_14_1_0`, `CMSSW_15_0_0`, `CMSSW_15_0_2`, `CMSSW_15_0_15_patch4`, `CMSSW_15_1_0`
    (plus `CMSSW_13_3_1_patch1`, fork master and upstream master from git).
  - `PhysicsTools/NanoAOD/plugins/TriggerObjectTableProducer.cc` at `CMSSW_12_4_X`,
    `CMSSW_13_0_X`, `CMSSW_14_0_X`, `CMSSW_15_0_X`, `CMSSW_14_1_0`, `CMSSW_14_2_0`,
    `CMSSW_15_0_0`, `CMSSW_15_0_1`, `CMSSW_15_0_2`, `CMSSW_15_0_5`, `CMSSW_15_0_10`,
    `CMSSW_15_0_13`, `CMSSW_15_0_15`, `CMSSW_15_0_15_patch4`, `CMSSW_15_1_0`, `CMSSW_16_0_0`.
  - `HLTrigger/Egamma/plugins/HLTGenericFilter.cc` at `CMSSW_10_6_X`, `CMSSW_12_4_X`,
    `CMSSW_12_6_X`, `CMSSW_13_0_X`, `CMSSW_13_3_X`, `CMSSW_14_0_X`, `CMSSW_15_0_X`, master.
  - HLT menus (`HLTrigger/Configuration/python/`): `HLT_GRun_cff.py` of `CMSSW_10_6_X`
    (`/dev/CMSSW_10_6_0/GRun/V3`), `CMSSW_12_4_X` (`/dev/CMSSW_12_4_0/GRun/V171`),
    `CMSSW_12_6_X` (`/dev/CMSSW_12_6_0/GRun/V16`), `CMSSW_13_0_X` (`/dev/CMSSW_13_0_0/GRun/V153`),
    `CMSSW_14_0_X` (`/dev/CMSSW_14_0_0/GRun/V182`), `CMSSW_15_0_X` (`/dev/CMSSW_15_0_0/GRun/V120`);
    the frozen menus `HLT_2022v12_cff.py` (`/frozen/2022/2e34/v1.2/HLT/V1`) and
    `HLT_2022v14_cff.py` (`/frozen/2022/2e34/v1.4/HLT/V1`) of `CMSSW_12_4_X`,
    `HLT_2022v15_cff.py` (`/frozen/2022/2e34/v1.5/CMSSW_12_6_X/HLT/V2`) of `CMSSW_12_6_X`,
    `HLT_2023v12_cff.py` of `CMSSW_13_0_X` (`/frozen/2023/2e34/v1.2/HLT/V2`) and of
    `CMSSW_13_3_1_patch1` (`/frozen/2023/2e34/v1.2/CMSSW_13_3_X/HLT/V3`),
    `HLT_2024v14_cff.py` of `CMSSW_14_0_X` (`/frozen/2024/2e34/v1.4/HLT/V1`),
    `HLT_2025v13_cff.py` of `CMSSW_15_0_X` (`/frozen/2025/2e34/v1.3/HLT/V4`), and from git
    the GRun (`/dev/CMSSW_13_3_0/GRun/V11`) and FULL (`/dev/CMSSW_13_3_0/HLT/V19`) menus of
    `CMSSW_13_3_1_patch1`, the fork's GRun and FULL menus, and upstream master's GRun and
    `HLT_2026v13_cff.py`. Other frozen menu names probed and absent: `2018v32/33` in
    10_6_X, `2022v13/15` in 12_4_X, `2023v10/11` in 13_0_X, `2024v10` to `v13` in 14_0_X,
    `2025v10` to `v12` and `v14` in 15_0_X.

---

## 3. NanoAOD versions, releases and campaigns

### 3.1 Version to release map (as established in this session)

| NanoAOD | Release | Evidence |
|---|---|---|
| v9 | CMSSW_10_6_X | relval inputs `RunIISummer20UL*MiniAODv2`, era modifier `run2_nanoAOD_106Xv2` (**verified** in code) |
| v10 | CMSSW_12_4_X | era modifier `run3_nanoAOD_124` in 13_3_X (**verified**); PR 40711 bits absent in 12_4_X (**verified**) |
| v11, v11_1 | CMSSW_12_6_X | reported; PR 40711 bits absent in 12_6_X (**verified**) |
| v12 | CMSSW_13_0_X, production 13_0_13 | reported (Purdue AF guide, user's notes); bits present from `CMSSW_13_0_0` (**verified**) |
| v13 | CMSSW_13_3_X, production CMSSW_13_3_1_patch1 | dataset strings `NanoAODv13-133X_*_ForNanov13_*` (**verified** in public configs); 13_3_1_patch1 named by choij1589/CustomNanoAOD and by the user's 2022 skim notes (reported; a GitHub code search for `CMSSW_13_3_1_patch1` with `NanoAODv13` finds only these two sources) |
| v14 | CMSSW_14_0_X | reported; bits present in `CMSSW_14_0_0` and the 14_0_X tip (**verified**) |
| v15 | CMSSW_15_0_X (>= 15_0_2 for 2024; 15_0_15_patch4 for 2022/2023 inputs with `run3_nanoAOD_pre142X`) | reported (CustomNanoAOD, WMass production repo); relval comments "re-MINI/NANOv15 in 15_0_X" (**verified**); the 21-bit photon list and the 64-bit `filterBits` start at `CMSSW_15_0_2` (**verified**) |

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

### 3.5 Frozen HLT menus shipped with the releases (verified file names; campaign use reported)

| Year | Frozen menu file | Table name | Release |
|---|---|---|---|
| 2022 | `HLT_2022v12_cff.py` | `/frozen/2022/2e34/v1.2/HLT/V1` | 12_4_X (reported: Run3Summer22 MC) |
| 2022 | `HLT_2022v14_cff.py` | `/frozen/2022/2e34/v1.4/HLT/V1` | 12_4_X (reported: Run3Summer22EE MC) |
| 2022 | `HLT_2022v15_cff.py` | `/frozen/2022/2e34/v1.5/CMSSW_12_6_X/HLT/V2` | 12_6_X |
| 2023 | `HLT_2023v12_cff.py` | `/frozen/2023/2e34/v1.2/HLT/V2` (`.../CMSSW_13_3_X/HLT/V3` in 13_3_X) | 13_0_X, 13_3_X (reported: Run3Summer23 and Summer23BPix MC) |
| 2024 | `HLT_2024v14_cff.py` | `/frozen/2024/2e34/v1.4/HLT/V1` | 14_0_X (reported: Run3Summer24 MC) |
| 2025 | `HLT_2025v13_cff.py` | `/frozen/2025/2e34/v1.3/HLT/V4` | 15_0_X |
| 2026 | `HLT_2026v13_cff.py` | `/frozen/2026/2e34/v1.3/HLT/V1` | master (16_1_X) |

Online data-taking menus evolve during the year; the path versions in the frozen files are
representative, and the e/gamma filter names of the diphoton paths are the same in all of
them (section 6).

### 3.6 Other NanoAOD v12 issues met while searching (reported, not verified here)

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
  `process.unpackedPatTrigger.triggerResults` (upstream master lines 1975 to 1976; the PAT
  step rewires `patTrigger.processName`, `slimmedPatTrigger.triggerResults` and
  `patMuons.triggerResults` at lines 1904 to 1907).
- `PhysicsTools/NanoAOD/python/nano_cff.py` (13_3_X): `nanoTableTaskCommon` holds the object
  tasks and tables; `nanoSequenceCommon`, `nanoSequenceOnlyFullSim` (= `triggerObjectTablesTask`,
  line 77 in 13_3_X, line 87 in upstream master), `nanoSequenceOnlyData` (proton tables +
  `lhcInfoTable`), `nanoSequence` (data), `nanoSequenceFS`, `nanoSequenceMC`.
  `nanoAOD_customizeCommon` activates VID electron and photon IDs, runs the AK4 and AK8 deep
  taggers through the `nanoAOD_addDeepInfo*` switches, adds tau IDs and ParticleNet
  information to taus (`nanoAOD_addPNetToTaus`), and boosted-tau IDs for Run 2. Run 2 uses
  AK4 CHS jets (`run2_nanoAOD_ANY`), Run 3 AK4 Puppi.
- `autoNANO` keys (**verified**): 13_3_X: PHYS, L1, L1FULL, Prompt. Fork master (15_1_X,
  May 2025): PHYS, L1, L1FULL, Scout, ScoutMonitor, ScoutFromMini, JME, JMErePuppi, L1DPG,
  Phase2L1DPG, Phase2L1DPGwithGen, MUPOG, MUDPG, MUDPGBKG, MUHLT, HCAL, HCALCalib, HCALMC, EGM,
  Prompt (= PHYS + L1), LepTrackInfo, BTV, GEN, GENFromMini. Upstream master additionally:
  L1Scout, L1ScoutSelect, BPH, Phase2HLT, Phase2HLTVal, Phase2HLTPixelOnly, NGTScouting,
  NGTScoutingVal, EXO, GENMinimal, TauEmbedding, HGCAL, HGCALVal.
- Relval definitions, `Configuration/PyReleaseValidation/python/relval_nano.py`:
  `_NANO_mc` = `-s NANO,DQM:@nanoAODDQM --process NANO --mc --eventcontent NANOAODSIM,DQM
  --datatier NANOAODSIM,DQMIO -n 10000 --customise Configuration/DataProcessing/Utils.addMonitoring`;
  `_NANO_data` the same with `--data` and NANOAOD. The workflow numbers come from a counter
  class `WFN(2500)` that produces four-decimal numbers (`2500.0001`, `2500.1001`, ...).
  - Fork master (May 2025, **verified** by emulating the counter): `2500.0001` to `.0003`
    NANOmc106Xul16v2/17v2/18v2, `2500.0101` to `.0103` the UL data, `2500.02xx/03xx`
    re-MINI + NANO of UL, `2500.1001` NANOmc130X (`TTbarMINIAOD13.0`, era
    `Run3,run3_nanoAOD_pre142X`), `2500.1101` NANOdata130Xrun3 (`MuonEG2023MINIAOD13.0`),
    `2500.1102` the same with `NANO:@Prompt`, `2500.2001` NANOmc140X, `2500.2101`
    NANOdata140Xrun3 (`MuonEG2024MINIAOD14.0`), `2500.22xx/23xx/24xx` POG and DPG flavours,
    `2500.3001` NANOmc2024reMINI (Summer24 AOD), `2500.3101` NANOdata2024reMINI (Run2024H AOD),
    `2500.9001/9002` NANOGEN from MiniAOD, `2500.9101` to `.9103` NANOGEN from GEN.
  - Upstream master (November 2026): the standard NANO-only workflows have been removed from
    `relval_nano.py` (only the comments and `_wfn.subnext()` placeholders remain); the file
    now defines only the scouting, L1-scouting, DPG, NANOGEN and Phase-2 HLT-NANO workflows
    (`2500.1501` to `.1504`, `2500.2301` to `.2304`, `2500.2401` to `.2403`, `2500.3301`
    to `.3303`, `2500.4301`, `2500.4302`, `2500.9101` to `.9103`, `3000.0001` to `.0007`).
    The steps `NANO_mc13.0`, `NANO_mc14.0`, `NANO_mc15.0`, `NANO_data13.0/14.0/15.0/16.0`
    still exist and are used by the POG steps.
  - The NANO step now runs inside the standard matrix instead: the data workflows
    `140.xxx` (2022) and `141.xxx` (2023) use the steps `AODNANORUN3_reHLT_2022/2023/2023B`
    (`-s RAW2DIGI,L1Reco,RECO,PAT,NANO,DQM:...+@nanoAODDQM`), for example `140.048`
    RunEGamma2022C, `141.011` RunEGamma2023B, `141.036` RunEGamma2023C, `141.046`
    RunEGamma2023D, `141.038`/`141.048` RunMuonEG2023C/D. The steps
    `RECONANORUN3_reHLT_2024/2025` and `AODNANORUN3_reHLT_2024` are defined but no EGamma,
    MuonEG or JetMET data workflow in `relval_standard.py` uses them today. The MC upgrade
    matrix (`relval_upgrade.py`, `upgradeWorkflowComponents.py`) numbers workflows as
    block start + fragment index, with the block starts 10000 + 200 x key index (shifted
    past the reserved ranges): `2023` starts at 12400, `2024` at 12800, `2025` at 16800,
    `2026` at 18400; the fragment `TTbar_14TeV_TuneCP5_cfi` is index 34 and
    `H125GGgluonfusion_14TeV_TuneCP5_cfi` index 52, so TTbar 2023/2024/2025 = `12434.0`,
    `12834.0`, `16834.0` and H to gamma gamma 2023/2024/2025 = `12452.0`, `12852.0`,
    `16852.0` (`12434.0` is confirmed by its presence in `relval_2017.py`; the others follow
    from the same arithmetic and should be confirmed with `runTheMatrix.py -n -e -l <wf>`).
    The Run 3 scenarios run NANO inside their `RecoNano`/`HARVESTNano` steps.

---

## 5. Trigger-object machinery, end to end (verified in code)

### 5.1 HLT side

- The leg filters are `HLTEgammaGenericFilter` and `HLTEgammaGenericQuadraticFilter`
  (`HLTrigger/Egamma/plugins/HLTGenericFilter.cc`, a template, and
  `HLTEgammaGenericQuadraticFilter.cc`). Both read the candidate collection from the
  parameter `l1EGCand` (line 30 / line 51), and when `saveTags` is true they call
  `filterproduct.addCollectionTag(l1EGTag_)` (fork lines 139 / 118, upstream 141 / 118) and
  save the accepted objects with type `trigger::TriggerPhoton` (81) (fork lines 143 to 145 /
  125 to 127, upstream 145 to 147); `TriggerCluster` (92) is used only when `saveTags` is
  false, which never produces stored objects. The same logic is in 10_6_X through master.
- The first filter of a leg saves type 92: on the unseeded leg `hltDiEG22EtEta2p55UnseededFilter`
  is an `HLT1Photon` (`HLTSinglet<reco::RecoEcalCandidate>`,
  `HLTrigger/HLTfilters/plugins/HLTSinglet.cc`) with `inputTag = hltEgammaCandidatesUnseeded`,
  `triggerType = 92`, `saveTags = True`; `getObjectType<T>` returns 0 for a
  `RecoEcalCandidate`, so the configured `triggerType` is stored (lines 151 to 154) and the
  collection tag is `inputTag_` (line 133). On the seeded leg `HLTEgammaL1TMatchFilterRegional`
  (lines 125, 150) and `HLTEgammaEtFilter` (line 85) save `TriggerCluster`.
- `DataFormats/HLTReco/interface/TriggerTypeDefs.h`: `TriggerL1EG = -98` (line 47),
  `TriggerPhoton = 81` (line 84), `TriggerCluster = 92` (line 95).
- `hltTriggerSummaryAOD` (`TriggerSummaryProducerAOD`, `moduleLabelPatternsToMatch = 'hlt*'`,
  no skip pattern) collects the objects of every filter with `saveTags`, keyed by collection
  tag, and keeps for each filter the per-object type id it was saved with.
- Every e/gamma filter in the diphoton sequences has `saveTags = True` (checked in all
  menus of section 2).
- The pair filter of the Mass90/Mass95 paths is an `HLTEgammaAllCombMassFilter`
  (`minMass = 90` or `95`), `saveTags = True`, in every menu from 2018 to 2026.

### 5.2 PAT and MiniAOD

- `PhysicsTools/PatAlgos/plugins/PATTriggerProducer.cc` (fork line 699, upstream line 700):
  `triggerObject.setCollection(handleTriggerEvent->collectionTagEncoded(iC))`, so an object
  made from the unseeded collection carries `hltEgammaCandidatesUnseeded::HLT`. Just after
  (upstream lines 703 to 706) it calls `addTriggerObjectType` for the type id of **every**
  filter that referenced the object (a multimap built at lines 680 to 683), so the e/gamma
  objects carry both 92 and 81. Then it attaches the filter labels (`addFilterLabel`, line
  725) and path names (`addPathName`, line 731). `patTrigger` has `onlyStandAlone = False`
  and no `exludeCollections` (the parameter is commented out in
  `triggerLayer1/triggerProducer_cfi.py`, in 13_3_X and in master).
- `selectedPatTrigger` (`PATTriggerObjectStandAloneSelector`, cut `!filterLabels.empty()`)
  keeps every object that was accepted by at least one filter with `saveTags`.
- `PhysicsTools/PatAlgos/python/slimming/slimmedPatTrigger_cfi.py`: `slimmedPatTrigger` is a
  `PATTriggerObjectStandAloneSlimmer` with `src = selectedPatTrigger`, `triggerResults =
  TriggerResults::HLT`, `packFilterLabels = True`, `packP4 = True`. The collection string and
  the type list are kept.

### 5.3 NanoAOD

- `PhysicsTools/NanoAOD/python/triggerObjects_cff.py`: `unpackedPatTrigger`
  (`PATTriggerObjectStandAloneUnpacker`, line 8) restores the labels; `triggerObjectTable =
  triggerObjectTableProducer.clone(src = "unpackedPatTrigger", ...)` (line 45 in v13 and the
  fork, 49 in upstream master) defines one `selections` entry per object type;
  `triggerObjectTablesTask = cms.Task(unpackedPatTrigger, triggerObjectTable, l1bits)`
  (line 420 / 447 / 451).
- `mksel(selection, doc=None, bit=None)` builds one quality-bit entry; a list of filter
  names is turned into an OR of `filter('name')` tests, a tuple into an AND. Bit i is the
  0-based position in `qualityBits` unless `bit=` is given (no photon entry uses it).
- `PhysicsTools/NanoAOD/plugins/TriggerObjectTableProducer.cc`: `SelectedObject` holds the
  `sel` cut (`StringCutObjectSelector`), the L1 and L2 seed cuts and cone sizes, the
  `skipObjectsNotPassingQualityBits` flag, and a `StringObjectFunction` built as the sum of
  `2^bit * (selection)` over the entries (asserts: a bit is not inserted twice; `bit < 31`
  up to `CMSSW_15_0_1`, `bit < 64` from `CMSSW_15_0_2`). `match(obj)` is `cut(obj)` (line 139).
  In `produce` (lines 151 to 160, same in 13_0_X, v13, 14_0_X, 15_0_X, the fork and master)
  each object is tested against **every** selection with `sel.match(obj)`; only for a
  passing selection are the bits computed; with the skip flag an object with no bit is
  dropped; an object can therefore be written once per selection it passes (Electron and
  Photon are independent). In 12_4_X (v10) a `break` after the first match assigned an
  object to one selection only.
- Self-cleaning (lines 162 to 176): a later object of the same selection id is merged into
  an earlier one, OR-ing the bits, when the two coincide. Up to `CMSSW_14_1_X` (v12 to v14)
  "coincide" means |delta pT| < 1e-6 and delta R squared < 1e-6; from `CMSSW_15_0_0`
  (so in v15 and master) only delta R squared < 1e-6 is tested.
- Output: `filterBits` is `int` (`Int_t`) up to `CMSSW_15_0_1`, `uint64_t` from
  `CMSSW_15_0_2` (PRs 47594 / 47601). `nanoDQM_cfi.py` books `TrigObj` plots per id
  (`Photon = id == 22`) of `_size`, `pt`, `eta`, `phi`, `id`, `filterBits` (bit set, 64 bins),
  `l1pt`, `l1iso`, `l1charge`, `l1pt_2`, `l2pt`.
- Collection matching: in the string cut, `coll(name)` resolves to
  `pat::TriggerObjectStandAlone::coll`, which calls the override
  `TriggerObjectStandAlone::hasCollection` (`DataFormats/PatCandidates/src/TriggerObjectStandAlone.cc`).
  If `name` contains `*`, the wildcard parser `hasAnyName` is used (this is how the Run 2
  muon selection writes `coll('hlt*L3MuonCandidates')`); otherwise it falls back to
  `pat::TriggerObject::hasCollection` (`src/TriggerObject.cc` lines 54 to 71, identical in
  v13, the fork and upstream master): exact string equality, otherwise the stored tag is
  split into label, instance and process, and with no process in the request the instance
  must match and the label must be **equal**. `hltEgammaCandidates` therefore does not
  match `hltEgammaCandidatesUnseeded::HLT`. `filter(name)` works the same way
  (`hasFilterOrCondition`: wildcard parser if `*` present, exact match otherwise; it throws
  if the labels are still packed, hence `unpackedPatTrigger`).

### 5.4 Selections per object type (fork master and upstream master)

- Electron (id 11): `type(92) && pt > 7 && (coll('hltEgammaCandidates') ||
  coll('hltEgammaCandidatesUnseeded')) && (filter('*PixelMatchFilter*') ||
  filter('*PixelMatchUnseededFilter'))`. In 13_0_X (every tag up to 13_0_17) the electron
  selection was still `coll('hltEgammaCandidates') && filter('*PixelMatchFilter')`; the
  unseeded collection was added by PR 41827 (June 2023) and is in `CMSSW_13_3_0` and later.
- Photon (id 22): `type(92) && pt > 15 && coll('hltEgammaCandidates')` (`pt > 20` in 12_4_X,
  12_6_X and `CMSSW_13_0_0`; `pt > 15` from `CMSSW_13_0_1`). `skipObjectsNotPassingQualityBits
  = True`. No era modifier touches the photon block (the modifiers in the file act on the
  Muon, Tau and Jet selections and on the prefiring producer only).
- Muon (id 13): `type(83) && pt > 5 && (coll('hltIterL3MuonCandidates') || (pt > 45 &&
  coll('hltHighPtTkMuonCands')) || (pt > 95 && coll('hltOldL3MuonCandidates')))`.
- Tau (id 15), BoostedTau (1515), Jet, FatJet, MET and others follow.

### 5.5 Photon quality bits by version (verified from the tag and branch files)

12_4_X and 12_6_X (12 bits, old `qualityBits = cms.string("... + 2048*filter(...)")` layout,
no diphoton bits): hltEG33L1EG26HEFilter, hltEG50HEFilter, hltEG75HEFilter, hltEG90HEFilter,
hltEG120HEFilter, hltEG150HEFilter, hltEG175HEFilter, hltEG200HEFilter, hltHtEcal800,
hltEG110EBTightIDTightIsoTrackIsoFilter, hltEG120EBTightIDTightIsoTrackIsoFilter,
hltMu17Photon30IsoCaloIdPhotonlegTrackIsoFilter.

13_0_0 to 13_0_17, 13_3_0, 13_3_1_patch1, 14_0_0, 14_0_X, 14_1_0, 15_0_0, 15_0_1 (18 bits):

| Bit | Filter | Runs on |
|---|---|---|
| 0 to 7 | hltEG33L1EG26HEFilter, hltEG50/75/90/120/150/175/200HEFilter | hltEgammaCandidates |
| 8 | hltHtEcal800 | HT object |
| 9 | hltEG110EBTightIDTightIsoTrackIsoFilter | hltEgammaCandidates |
| 10 | hltEG120EBTightIDTightIsoTrackIsoFilter | hltEgammaCandidates; present only in the 2018 menu and the frozen early-2022 (v1.2) menu |
| 11 | hltMu17Photon30IsoCaloIdPhotonlegTrackIsoFilter ("1mu-1photon") | hltEgammaCandidates |
| 12 | hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter | hltEgammaCandidates |
| 13 | hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter | hltEgammaCandidates |
| 14 | hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter | **hltEgammaCandidatesUnseeded, dead** |
| 15 | hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter | **hltEgammaCandidatesUnseeded, dead** |
| 16 | hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter | hltEgammaCandidates; 2018 and 2022 menu names |
| 17 | hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter | **hltEgammaCandidatesUnseeded, dead**; 2018 and 2022 names |

15_0_2, 15_0_15_patch4, 15_1_0, fork master, upstream master (21 bits): bits 9 and 10
become hltEG45EBTightIDTightIsoTrackIsoFilter (filter exists from the 2024 menu) and
hltEG50EBTightIDTightIsoTrackIsoFilter (from the 2023 menu), the old 9 to 17 shift to 11 to
19, and bit 20 is the wildcard `hltEG*L1VBFLooseIsoEGHEFilter` (the only matching module,
`hltEG22L1VBFLooseIsoEGHEFilter`, exists from the 2023 menu and runs on
`hltEgammaCandidates`). The dead bits are 16, 17 and 19. Decimal values of the dead bits:
16384, 32768, 131072 (v12 to v14); 65536, 131072, 524288 (v15, master).

All non-diphoton photon-bit filters were checked in nine menus from 2018 to 2026: each one
that exists runs on `hltEgammaCandidates` (including the Mu17_Photon30 photon leg and the
VBF filter). No unseeded filter name matches any photon bit other than the three diphoton
unseeded bits, so the fix cannot admit unseeded objects through another bit.

### 5.6 Changes to `triggerObjects_cff.py` between v13 and the fork master (verified diff)

Electron: `*PixelMatchFilter*` wildcard; new bits "1e-1tau PNet", `hltEle30WPTightGsfTrackIsoFilter`,
`hltEle*erWPTightGsfTrackIsoFilterNoRhoCorrectionForVBF`. Photon: bits for hltEG45/50EBTightID,
and the VBF wildcard (these, with the 64-bit `filterBits`, entered 15_0_X between
`CMSSW_15_0_1` and `CMSSW_15_0_2`, consistent with PR 47594 "[NANOAOD] Add missing trigger
filter bits" and its 15_0_X backport PR 47601, merged 18 March 2025). Muon: "1mu-1tau PNet".
Tau: selection and bits reorganised around PNet filters (30 bits). BoostedTau: new selection
and three PNet/ParticleNet bits. Jet: bits 31 to 45 (QuadPFJet PNet, VBF categories, VBF+gamma,
VBF+e, SinglePFJetX, DiPFJetAveX). FatJet: PNetBB bit. Run 2 2017 muon filter
`hltIterL3MuonCandidates` bit. The photon `sel` line is unchanged throughout. Upstream master
(November 2026) differs from the fork only by a `tau_embedding_merging` modifier on
`unpackedPatTrigger` and four extra lines before the table (Photon block at line 88 instead
of 84).

---

## 6. The HLT paths

### 6.1 HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90 / Mass95

Path definition (13_3_1_patch1 `HLT_FULL_cff.py` line 119468): `HLTBeginSequence +
hltL1sSingleAndDoubleEGor + hltPreDiphoton3022R9IdORIsoCaloIdANDHER9IdMass90 +
HLTDiphoton30L22R9Id85b90eORIso60CaloId15b35eANDHE12R9Id50b80eSequence +
hltDiEG22R9Id85b90eORIso60CaloId15b35eANDHE12R9Id50b80eMass90CombMassLastFilter + HLTEndSequence`.
Mass95 uses the same sequence and `hltDiEG22R9Id85b95eORIso60CaloId15b35eANDHE12R9Id50b80eMass95CombMassLastFilter`.

Path version per menu (**verified**, section 2 files):

| Menu | Mass90 / Mass95 version |
|---|---|
| 2018, `/dev/CMSSW_10_6_0/GRun/V3` | v13 |
| 2022, frozen v1.2 (`HLT_2022v12`) | v13 |
| 2022, frozen v1.4, v1.5, GRun 12_4 V171, GRun 12_6 V16 | v15 |
| 2023, frozen v1.2 (13_0_X and 13_3_X), GRun 13_0 V153 | v17 |
| 2023 development, 13_3 GRun V11 and HLT V19 | v19 |
| 2024, frozen v1.4, GRun 14_0 V182 | v22 |
| 2025 development (fork, May 2025), GRun 15_0 V62 and HLT V78 | v24 |
| 2025, frozen v1.3, GRun 15_0 V120 | v26 |
| 2026, frozen v1.3 | v29 |
| 2026 development, GRun 16_1 V16 | v30 |

The e/gamma filter chain of the sequence is identical in all these menus (16 filter
modules, same names in the same order; the MD5 of the name list is the same everywhere).

Sequence (`HLTDiphoton30L22R9Id85b90eORIso60CaloId15b35eANDHE12R9Id50b80eSequence`, 13_3_1_patch1
`HLT_FULL_cff.py` line 118801), filters in order, all `saveTags = True`:

Seeded leading leg on `hltEgammaCandidates`: hltEGL1SingleAndDoubleEGOrFilter
(HLTEgammaL1TMatchFilterRegional, type 92), hltEG30L1SingleAndDoubleEGOrEtFilter
(HLTEgammaEtFilter, Et > 30, type 92), hltEG30LR9Id50b80eR9IdFilter (HLTEgammaGenericFilter,
R9 > 0.5 EB / 0.8 EE), hltEG30LHE12R9Id50b80eHEFilter (HLTEgammaGenericQuadraticFilter, H/E),
[ignore] hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter (R9 > 0.85 EB / 0.9 EE, bit 12),
[ignore] hltEG30LCaloId15b35eHE12R9Id50b80eClusterShapeFilter, [ignore]
hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter (bit 13),
hltEG30LRId85ORIso60CaloId15b35eANDHE12R9Id50b80eLegCombLastFilter (HLTEgammaDoubleLegCombFilter).

Unseeded sub-leading leg on `hltEgammaCandidatesUnseeded`: hltDiEG22EtEta2p55UnseededFilter
(HLT1Photon, `triggerType = 92`), hltDiEG22R9Id50b80eR9IdUnseededFilter,
hltDiEG22HE12R9Id50b80eHEUnseededFilter, [ignore] hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter
(bit 15), [ignore] hltEG22CaloId15b35eHE12R9Id50b80eClusterShapeUnseededFilter, [ignore]
hltEG22Iso60CaloId15b35eHE12R9Id50b80eEcalIsoUnseededFilter, [ignore]
hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter (bit 14).

Pair: hltDiEG22R9Id85b90eORIso60CaloId15b35eANDHE12R9Id50b80eMass90CombMassLastFilter
(HLTEgammaAllCombMassFilter, `minMass = 90`), no NanoAOD bit.

Parameters of the two unseeded last filters (fork GRun lines 47281 to 47302 and 47362 to 47383;
same values in every menu checked):
R9UnseededLastFilter: candTag hltDiEG22HE12R9Id50b80eHEUnseededFilter, varTag
hltEgammaR9IDUnseeded:r95x5, thresholds EB 0.85, EE 0.9 (greater than), l1EGCand
hltEgammaCandidatesUnseeded. TrackIsoUnseededLastFilter: candTag
hltEG22Iso60CaloId15b35eHE12R9Id50b80eEcalIsoUnseededFilter, varTag hltEgammaHollowTrackIsoUnseeded,
lessThan, useEt, thrRegular 6.0 GeV, thrOverE 0.002, l1EGCand hltEgammaCandidatesUnseeded.

### 6.2 HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId (and _Mass55)

Versions per menu (**verified**): 2018 `_NoPixelVeto_v2` and `_NoPixelVeto_Mass55_v2`;
2022 frozen v1.2: `_v2` / `_Mass55_v2`; 2022 frozen v1.4, v1.5 and GRun 12_4/12_6: `_v3`;
2023 frozen and GRun 13_0: `_v5`; 13_3 development: `_v7`; 2024: `_v10`; fork development
May 2025: `_v12`; 2025 frozen: `_v14`; 2026 frozen: `_v17`; GRun 16_1: `_v18`.

2018 and 2022 menus, sequences `HLTDiphoton3018R9Idb50e90ANDIso60CaloId15b35eANDHE12b10eSequence`
and `...Mass55Sequence` (2018: `...NoPixelVetoSequence` and `...Mass55NoPixelVetoSequence`),
same filter names in all four:

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
(NanoAOD bit 17 / 19, dead). Mass55 variant: hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eMass55CombMassLastFilter.

The 2018 menu also has `HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_NoPixelVeto_Mass55_v13`
and `_PixelVeto_Mass55_v15`; the frozen early-2022 menu still has
`HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_Mass55_v13`; later menus have none of them.

2023 and later menus (2023 frozen, 13_3, 2024, 2025, 2026): one sequence for both variants,
`HLTDiphoton3018R9Id50b90eANDHE10b9eANDCaloId11b32eANDIso60b40eSequence`, re-tuned thresholds
and renamed filters:
Seeded: hltEGL1SingleAndDoubleEGOrFilter, hltEG30L1SingleAndDoubleEGOrEtFilter,
hltEG30R9Id50b90eR9IdFilter, hltEG30HE10b9eR9Id50b90eHEFilter,
hltEG30CaloId11b32eHE10b9eR9Id50b90eClusterShapeFilter,
hltEG30Iso60b40eCaloId11b32eHE10b9eR9Id50b90eEcalIsoFilter (no NanoAOD bit).
Unseeded: hltDiEG18EtUnseededFilter, hltDiEG18R9Id50b90eR9IdUnseededFilter,
hltDiEG18HE10b9eR9Id50b90eHEUnseededFilter, hltDiEG18CaloId11b32eHE10b9eR9Id50b90eClusterShapeUnseededFilter,
hltDiEG18Iso60b40eCaloId11b32eHE10b9eR9Id50b90eEcalIsoUnseededFilter,
hltDiEG18TrackIso60Iso60b40eCaloId11b32eHE10b9eR9Id50b90eTrackIsoUnseededFilter (no NanoAOD bit).
Mass55: hltDiEG18TrackIso60Iso60b40eCaloId11b32eHE10b9eR9Id50b90eMass55CombMassLastFilter.
Consequence: for 2023 to 2026 data and MC, NanoAOD bits 16/17 (18/19) match nothing on either leg
of the 30_18 paths. This is a stale-name problem, separate from the collection problem.

### 6.3 Diphoton and DoublePhoton paths per menu (verified matrix)

Columns: 2018 GRun | 2022 v1.2 | 2022 v1.4 | 2022 v1.5 and GRun 12_4 | 2023 v1.2 and GRun 13_0 |
13_3 dev | 2024 v1.4 and GRun 14_0 | fork dev May 2025 | 2025 v1.3 and GRun 15_0 | 2026 v1.3 | GRun 16_1.

| Path | versions |
|---|---|
| Diphoton20_14_eta1p5_R9IdL_AND_HE(T)_AND_IsoTCaloIdT, Diphoton22_14_... | - , 1, 2, 2, 4, 6, 9, 11, 13, 16, 17 |
| Diphoton24_14_eta1p5_R9IdL_AND_HET_AND_IsoTCaloIdT, Diphoton24_16_... | from 2023: 4, 6, 9, 11, 13, 16, 17 |
| Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId (and _Mass55) | 2 (NoPixelVeto), 2, 3, 3, 5, 7, 10, 12, 14, 17, 18 |
| Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90 / Mass95 | 13, 13, 15, 15, 17, 19, 22, 24, 26, 29, 30 |
| Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_(NoPixelVeto/PixelVeto)_Mass55 | 2018: 13 / 15; 2022 v1.2: `_Mass55_v13`; then gone |
| DiphotonMVA14p25_Mass90, DiphotonMVA14p25_Tight_Mass90 | 2024 only: v2 |
| DiphotonMVA14p25_{High,Low,Medium,TightHigh,TightLow,TightMedium}_Mass60 | fork dev and 2025: v1; 2026: v2 |
| Diphoton15_10_EBEB_TightID_ECALTrackIsoDr0p2(to0p4), Diphoton15_12_... | 2025: v3; 2026 frozen: v6; GRun 16_1: v7 |
| DoublePhoton33_CaloIdL, DoublePhoton70 | 6, 6, 8, 9, 11, 13, 16, 18, 18, 19, 19 |
| DoublePhoton85 | 14, 14, 16, 17, 19, 21, 24, 26, 26, 27, 27 |

NanoAOD has no photon bits for the low-mass eta1p5 paths, the DiphotonMVA paths, the
Diphoton15_1x EBEB paths or the DoublePhoton paths. The HLT XGBoost photon MVA and the
diphoton combination filter were added by PRs 44473 (master) and 44500 (14_0_X) in March 2024.

---

## 7. The bug, precisely

1. The unseeded leg's filters save objects referenced through `hltEgammaCandidatesUnseeded`,
   with the filter labels attached; the leg's first filter saves them with type 92, the later
   ones with type 81 (section 5.1).
2. PAT stores the collection name and all types on the object; MiniAOD keeps them (section 5.2).
3. NanoAOD's photon selection requires `coll('hltEgammaCandidates')`, an exact label match
   because the argument has no wildcard (section 5.3), so the unseeded objects fail the
   selection although they pass `type(92)` and `pt > 15`.
4. The selection runs before the quality bits; a rejected object never reaches the bit
   evaluation; the later self-cleaning only sees accepted objects.
5. Therefore photon bits 14, 15, 17 (v12 to v14) or 16, 17, 19 (v15, master) are documented in
   `TrigObj_filterBits` but can never be set. The matching leading-leg bits 12/13 (14/15) work.

Observation that prompted the investigation: in NanoAOD v13 the last unseeded filter bit of the
Diphoton30_22 path is present in the documentation but no photon trigger object ever has it.

### 7.1 Ruled out

- Wrong filter names: all four 30_22 names exist with `saveTags = True` in every menu from 2018
  to 2026 (nineteen menu files, section 2), always on the expected collection.
- Objects missing from MiniAOD: `patTrigger` excludes no collection; the electron selection has
  relied on `coll('hltEgammaCandidatesUnseeded')` since June 2023 and PR 41827 observed the
  extra objects.
- Wrong object type: the unseeded objects carry type 92 from `hltDiEG22EtEta2p55UnseededFilter`
  (`triggerType = 92`), next to the type 81 of the later filters.
- pT threshold: the unseeded leg requires Et > 22 GeV (18 GeV for the 30_18 paths), above the
  15 GeV of the selection.
- Era overrides: none for the photon block.
- v13-specific code: the v13 tag equals the 13_3_X tip; all later branches have the same line.

### 7.2 Affected NanoAOD versions (verified per tag and branch)

| Version | Release | Photon sel | Diphoton unseeded bits | `filterBits` | Affected |
|---|---|---|---|---|---|
| v10 | 12_4_X | seeded only, pt > 20 | absent | Int_t | no |
| v11, v11_1 | 12_6_X | seeded only, pt > 20 | absent | Int_t | no |
| v12 | 13_0_X (13_0_0: pt > 20; 13_0_1 to 13_0_17: pt > 15) | seeded only | 14, 15, 17 | Int_t | yes |
| v13 | 13_3_0, 13_3_1_patch1, 13_3_X tip | seeded only | 14, 15, 17 | Int_t | yes |
| v14 | 14_0_0, 14_0_X tip (also 14_1_0) | seeded only | 14, 15, 17 | Int_t | yes |
| (pre-v15) | 15_0_0, 15_0_1 | seeded only | 14, 15, 17 | Int_t | yes |
| v15 | 15_0_2 to 15_0_15_patch4, 15_1_0 | seeded only | 16, 17, 19 | 64-bit unsigned | yes |
| master (fork May 2025; upstream Nov 2026) | 15_1_X / 16_1_X | seeded only | 16, 17, 19 | 64-bit unsigned | yes |

### 7.3 Affected triggers per menu era

| Era (menus) | Paths with a dead unseeded photon bit | Dead bits (v12 to v14 / v15+) |
|---|---|---|
| 2018 (GRun 10_6) | Diphoton30_22 Mass90_v13, Mass95_v13; Diphoton30_18 NoPixelVeto_v2, NoPixelVeto_Mass55_v2 | 14, 15 / 16, 17; 17 / 19 |
| 2022 (frozen v1.2) | Diphoton30_22 Mass90_v13, Mass95_v13; Diphoton30_18_v2, Mass55_v2 | 14, 15 / 16, 17; 17 / 19 |
| 2022 (frozen v1.4, v1.5; GRun 12_4, 12_6) | Diphoton30_22 Mass90_v15, Mass95_v15; Diphoton30_18_v3, Mass55_v3 | 14, 15 / 16, 17; 17 / 19 |
| 2023 (frozen v1.2; 13_3 dev v19) | Diphoton30_22 Mass90_v17 (v19), Mass95_v17 (v19) | 14, 15 / 16, 17 |
| 2024 (frozen v1.4) | Diphoton30_22 Mass90_v22, Mass95_v22 | 16, 17 (14, 15 if made with 14_0_X) |
| 2025 (frozen v1.3; fork dev v24) | Diphoton30_22 Mass90_v26, Mass95_v26 | 16, 17 |
| 2026 (frozen v1.3; GRun 16_1 v30) | Diphoton30_22 Mass90_v29, Mass95_v29 | 16, 17 |

Mass90 and Mass95 share filters, so one fix restores both; likewise the 30_18 pair in the
2018 and 2022 menus. For 2023 and later the 30_18 bits need the renamed filters (section 8.2).

### 7.4 History (dates from the GitHub search API, verified)

- PR 40711 "diphoton_hlt_filters_added" (Soumyatifr), created 7 Feb 2023, merged 8 Feb 2023
  into master during the 13_0_X pre-release cycle (the bits are in `CMSSW_13_0_0`): added the
  six diphoton photon bits "needed for the next iteration of the NANOAOD production";
  reviewer swertz asked about OR-grouping; the author kept separate bits after consulting
  lfinco. Photon selection untouched (reported from the PR page, first session).
- Between `CMSSW_13_0_0` and `CMSSW_13_0_1` the photon threshold went from `pt > 20` to
  `pt > 15` (the PR was not identified).
- PR 41827 "Add CaloIdL_MW unseeded filter to nanoAOD filterBits" (RSalvatico), created
  31 May 2023, merged 8 Jun 2023 (master, 13_2_X cycle; in `CMSSW_13_3_0`, never in 13_0_X):
  added `hltDiEle*CaloIdLMWPMS2UnseededFilter`, allowed `*PixelMatchUnseededFilter`, and
  "added the collection hltEgammaCandidatesUnseeded, which are the objects on which the
  selection of the unseeded trigger leg is made" to the Electron selection; noted "we are
  effectively allowing more trigger objects by adding one input collection" (reported from
  the PR page, first session).
- PR 43247 "Add CaloIdL_MW seeded filter and split the legs of CaloIdL_TrackIdL_IsoVL filter
  on nanoAOD filterBits" (ikrommyd), created 10 Nov 2023, merged 17 Nov 2023 (master), and its
  13_3_X backport PR 43292, created 15 Nov, merged 17 Nov 2023 (the backport text says it
  "is required for the production of NanoAODv13 from CMSSW_13").
- Other 13_3_X backports for v13 (Nov to Dec 2023): 43209 (photon superclusterEta), 43254
  (revert precision decrease), 43286 (electron NonIso MVA ID for EB), 43383 (tau decay
  products in NanoDQM), 43387 (L1 unprefirable event info and Final OR in BX-1/-2), 43470
  (tau trigger filter bit fixes), 43513 (photon variable precision 10).
- PR 44473 "HLT XGBoost Photon MVA and Diphoton combination filter", created 19 Mar 2024,
  merged 22 Mar 2024, and its 14_0_X backport 44500 (DiphotonMVA paths).
- PR 47594 "[NANOAOD] Add missing trigger filter bits", created 13 Mar 2025, merged 18 Mar
  2025 (master), and its 15_0_X backport PR 47601, merged 18 Mar 2025: consistent with the
  new photon bits 9, 10 and 20 and the 64-bit `filterBits` that appear in `CMSSW_15_0_2`.
- No upstream issue or PR on photon unseeded trigger objects was found (searches on
  `hltEgammaCandidatesUnseeded`, `R9UnseededLastFilter`, `Diphoton30_22 filterBits`, both
  in the first and the second session).

---

## 8. The fix

```diff
-            sel = cms.string("type(92) && pt > 15 && coll('hltEgammaCandidates')"),
+            sel = cms.string("type(92) && pt > 15 && (coll('hltEgammaCandidates') || coll('hltEgammaCandidatesUnseeded'))"),
```

- Why this form: it names exactly the two collections and mirrors the Electron selection
  (in production since NanoAOD v13). A wildcard `coll('hltEgammaCandidates*')` would also
  match, because `TriggerObjectStandAlone::hasCollection` parses `*`, but it would silently
  include any future collection with that prefix.
- Effect: unseeded objects enter the photon branch; with `skipObjectsNotPassingQualityBits`
  only those that pass one of the photon filters are written, and the only photon-bit filters
  that run on the unseeded collection are the three diphoton sub-leading-leg filters
  (section 5.5). A seeded and an unseeded object pointing in the same direction (delta R
  squared < 1e-6; up to 14_1_X also the same pT) are merged by the self-cleaning with OR-ed
  bits, keeping the one that comes first in the input list; otherwise a second photon entry
  appears, as already happens for electrons. Bit numbers, documentation strings and event
  content are unchanged.
- Not changed by the fix: the 2023+ names of the 30_18 path (needs new entries), and the paths
  without any photon bits (low-mass eta1p5, DiphotonMVA, Diphoton15_1x EBEB, DoublePhoton).

### 8.1 Validation plan (not executable here: no CMSSW runtime in the session container)

1. Run standard workflows that include the NANO step before and after the change. In upstream
   master today: MC `runTheMatrix.py -l 12452.0,12852.0` (H125GGgluonfusion_14TeV, 2023 and
   2024 scenarios, which fire the diphoton triggers), `12434.0,12834.0` (TTbar 2023, 2024),
   and data `141.046` (RunEGamma2023D, `AODNANORUN3_reHLT_2023`) or `140.048` (RunEGamma2022C).
   Confirm the numbers with `runTheMatrix.py -n -e -l <wf>` first; the arithmetic is in
   section 4. In a 15_1_X area of May 2025 the NanoAOD-only workflows were `2500.1001`
   (NANOmc130X), `2500.1101` (NANOdata130Xrun3), `2500.2001` (NANOmc140X), `2500.2101`
   (NANOdata140Xrun3).
2. Count photon TrigObj with the unseeded bits in events firing the diphoton path: zero before,
   non-zero and of the order of the number of triggered events after.
3. Compare `nTrigObj`, the `TrigObj` DQM histograms (`_size`, `filterBits` per id) and the file
   size; only diphoton-triggered events should move.

```python
import uproot, awkward as ak, numpy as np
t = uproot.open("nano.root")["Events"]
path = "HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"
a = t.arrays(["TrigObj_id", "TrigObj_filterBits", path])
ph    = a["TrigObj_id"] == 22
bits  = ak.values_astype(a["TrigObj_filterBits"][ph], np.uint64)
fired = a[path]
for bit in (16, 17):                      # 14, 15 for NanoAOD v12 to v14
    hasbit = ak.any(((bits >> np.uint64(bit)) & np.uint64(1)) == 1, axis=1)
    print(bit, int(np.sum(hasbit & fired)), "of", int(np.sum(fired)))
```

### 8.2 Pull request readiness

- Branch `nano-photon-trigobj-unseeded` = upstream master `ed35654b1` + `aebf3eb64`; the patch is
  `pr/0001-NanoAOD-photon-TrigObj-unseeded-collection.patch`; title and body in `pr/PR_body.md`.
- Publish: `git push -u origin nano-photon-trigobj-unseeded`, then open the PR from
  `santanumahata:nano-photon-trigobj-unseeded` to `cms-sw:master`. Needs the xpog signature.
  The bot's RelVal comparison will show the expected `nTrigObj` and DQM differences. Cite PR 40711
  and PR 41827. Nothing has been pushed and no PR exists (state on 4 November 2026).
- Backport: request `CMSSW_15_0_X` if another NanoAOD production from that branch is planned.
- Follow-ups, separate from the one-line fix:
  1. Add the 2023+ names of the 30_18 path as alternatives inside the existing two entries so bit
     numbers stay stable, e.g. `mksel(["hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter",
     "hltEG30Iso60b40eCaloId11b32eHE10b9eR9Id50b90eEcalIsoFilter"], ...)` and
     `mksel(["hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter",
     "hltDiEG18TrackIso60Iso60b40eCaloId11b32eHE10b9eR9Id50b90eTrackIsoUnseededFilter"], ...)`.
     The unseeded entry only works together with the collection fix.
  2. Bits for the low-mass eta1p5 diphoton paths, the DiphotonMVA14p25 paths, the
     Diphoton15_1x EBEB paths and the DoublePhoton paths, to be agreed with the EGM POG and
     the Higgs PAG.

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
- In v15 files `TrigObj_filterBits` is a 64-bit unsigned branch; code that assumed `Int_t`
  (v12 to v14) must be adapted when the bit test is written by hand.

---

## 10. Environment notes for future sessions

- Not reachable from the cloud session: `twiki.cern.ch`, `cms-nanoaod-integration.web.cern.ch`
  (McM and other cern.ch hosts presumably the same), `web.archive.org`,
  `patch-diff.githubusercontent.com`, and `api.github.com` for any repository not attached to
  the session (the proxy answers with a "GitHub access to this repository is not enabled"
  message).
- Reachable: `github.com`, `raw.githubusercontent.com` for branches **and tags** (curl works
  through the proxy; a missing path returns the text `404: Not Found`), GitHub search through
  `gh api -X GET search/issues|code|commits`. Issue search requires `is:issue` or `is:pr` in
  the query. Code search returns text fragments with
  `-H "Accept: application/vnd.github.text-match+json"` and only indexes default branches.
- Upstream `cms-sw/cmssw` can be fetched read-only (add a remote, `git fetch --depth 1 upstream
  <branch|tag>`); GitHub API tools are scoped to the attached fork; repository creation is not
  allowed from the session.
- No CMSSW runtime (no scram, cmsRun or ROOT) in the container; code can only be read.
- PDF generation: Node `playwright` 1.63.0 with the pre-installed Chromium (HTML to PDF);
  `reportlab`, `pypdf`, `pdftotext`, `pdftoppm` present; the Python `playwright` module is not.
- Downloaded files were kept in a separate directory and parsed with `python3 -I` scripts
  that take the paths as arguments.

---

## 11. Key commands and scripts used (reproducibility)

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

# any branch or tag without a full fetch
curl -sS -L -o trig_13_0_13.py \
  https://raw.githubusercontent.com/cms-sw/cmssw/CMSSW_13_0_13/PhysicsTools/NanoAOD/python/triggerObjects_cff.py
curl -sS -L -o menu_2024v14.py \
  https://raw.githubusercontent.com/cms-sw/cmssw/CMSSW_14_0_X/HLTrigger/Configuration/python/HLT_2024v14_cff.py

# matcher and producer
sed -n '/bool TriggerObjectStandAlone::hasCollection/,/^}/p' DataFormats/PatCandidates/src/TriggerObjectStandAlone.cc
sed -n '/bool TriggerObject::hasCollection/,/^}/p' DataFormats/PatCandidates/src/TriggerObject.cc
grep -n "if (sel.match(obj))" PhysicsTools/NanoAOD/plugins/TriggerObjectTableProducer.cc

# scripts in this repository (run with python3 -I, files given as arguments)
python3 -I scripts/bits.py        trig_*.py        # photon/electron selection and the numbered photon bits per file
python3 -I scripts/menuscan.py    menu.py          # diphoton paths with their expanded filter sequences
python3 -I scripts/menusummary.py menu_*.py        # per menu: key filters, collection, last seeded/unseeded filters
python3 -I scripts/pathmatrix.py  menu_*.py        # path-version matrix of Diphoton/DoublePhoton paths
python3 -I scripts/bitfilters.py  menu_*.py        # presence and collection of every photon-bit filter
python3 -I scripts/wfn.py         relval_nano.py   # NanoAOD relval workflow numbers (WFN counter emulation)
node scripts/render_pdf.js report                  # HTML report to PDF

# GitHub searches
gh api -X GET search/issues -f q='repo:cms-sw/cmssw is:pr base:CMSSW_13_3_X nanoAOD' --jq '.items[].html_url'
gh api -X GET search/issues -f q='repo:cms-sw/cmssw is:pr "CaloIdL_MW unseeded filter"' \
  --jq '.items[] | {number, title, created_at, merged_at: .pull_request.merged_at}'
gh api -H "Accept: application/vnd.github.text-match+json" -X GET search/code \
  -f q='"ForNanov13" cmsDriver' --jq '.items[] | .text_matches[].fragment'
```

---

## 12. Sources

- cms-sw/cmssw PR 40711: https://github.com/cms-sw/cmssw/pull/40711
- cms-sw/cmssw PR 41827: https://github.com/cms-sw/cmssw/pull/41827
- cms-sw/cmssw PR 43247 (master) and 43292 (13_3_X backport "for the production of NanoAODv13"):
  https://github.com/cms-sw/cmssw/pull/43247, https://github.com/cms-sw/cmssw/pull/43292
- cms-sw/cmssw PR 43286, 43470, 43209, 43254, 43383, 43387, 43513 (13_3_X NanoAOD backports)
- cms-sw/cmssw PR 47594 and 47601 (missing trigger filter bits, March 2025):
  https://github.com/cms-sw/cmssw/pull/47594, https://github.com/cms-sw/cmssw/pull/47601
- cms-sw/cmssw PR 44473 and 44500 (HLT photon MVA and diphoton combination filter, March 2024)
- uhh-cms/cmsdb v13 campaigns: https://github.com/uhh-cms/cmsdb (campaigns/run3_2023_preBPix_nano_v13 and siblings)
- bhbam/MCProduction_run3 (v13 NANO config): https://github.com/bhbam/MCProduction_run3
- maxgalli/SBI-Htt-EFT (v13 cmsDriver in README): https://github.com/maxgalli/SBI-Htt-EFT
- choij1589/CustomNanoAOD (release and era tables; "Run3 Nano v13 (legacy)" = CMSSW_13_3_1_patch1): https://github.com/choij1589/CustomNanoAOD
- choij1589/SKNanoAnalyzer docs (v12 electron MVA NoIso bug; custom Run 3 JetID): https://github.com/choij1589/SKNanoAnalyzer
- LPC-HH/HH4b PR 368 (NanoAODv12 jetId numbers, ECAL bad-calib veto): https://github.com/LPC-HH/HH4b/pull/368
- WMass/WMassNanoProduction (v15 production notes): https://github.com/WMass/WMassNanoProduction
- Purdue AF private MC guide (MiniAODv4/NanoAODv12 with CMSSW_13_0_13): https://analysis-facility.physics.purdue.edu/en/latest/guide-mc-gen.html
- santanumahata/2023_lowmass_analysis (2022 skim notes: 22Sep2023 = 13_0_13, 16Dec2023 = 13_3_1_patch1, 19Dec2023 = 13_0_17)
