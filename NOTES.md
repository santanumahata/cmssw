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
selection. Confirmed on twelve NanoAOD files (section 14) and by NANO re-made with the fix
(section 15).

---

## 2. Repository and session state

- Working checkout: fork `santanumahata/cmssw`, shallow clone, branch
  `nano-photon-trigobj-unseeded-forkmaster`, based on fork master `f99356577`
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
- Commits made (both branches pushed to the fork `santanumahata/cmssw` later; nothing pushed to
  `cms-sw/cmssw`):
  - `42555a463` on `nano-photon-trigobj-unseeded-forkmaster`: the fix on the fork's May 2025 master.
    Author and committer santanumahata.
  - `828ed8b2a` on `nano-photon-trigobj-unseeded`: the same change on upstream master `ed35654b1`;
    applied cleanly. Same author and committer.
  - On 9 November 2026 both commits and the notes branch were re-created with author and committer
    santanumahata (same trees and dates). Older hashes cited in this file: `1699a39f7` = `42555a463`,
    `aebf3eb64` = `828ed8b2a`.
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

### 8.1 Validation plan (written on 4 November without a CMSSW runtime; carried out on lxplus on 5 November, sections 15 and 16)

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
- Publish: the branch is on the fork; open the PR from
  `santanumahata:nano-photon-trigobj-unseeded` to `cms-sw:master`. Needs the xpog signature.
  In CMSSW_16_1_3 the relval workflows 12452.0 and 141.046 show no difference (their NANO has no
  TrigObj, section 16). Cite PR 40711 and PR 41827. No PR exists; nothing pushed to
  `cms-sw/cmssw` (state on 5 November 2026).
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
- HiggsDNA (GitLab master `d179305`, 5 Nov 2026; same in the GitHub fork ZhenyuDongLL/HiggsDNA-bbggrun3
  `66d76af`): `trigger_match` (`higgs_dna/utils/misc_utils.py:306`) is called only in
  `workflows/dystudies.py:256`, for electrons (`pdgid=11`, bit 1 or 12); no workflow tests a photon
  `filterBits` bit or a diphoton filter bit (`workflows/lowmass.py:641-642` only counts id 11 and id 22
  objects as `nTrigEle`/`nTrigPho`), and the low-mass unseeded-leg efficiency is read from the
  precomputed `JSONs/TriggerSF_LM/<year>/Lowmass_unseeded_leg_efficinecy.json`
  (`systematics/event_weight_systematics.py:3920`), whose derivation is not in the repository.
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

---

## 13. Third pass (4 November 2026, evening): is it still there, and how widespread is it?

### 13.1 Latest upstream state (verified live)

- `git ls-remote` on `cms-sw/cmssw`: `master` = `ed35654b1` (no newer commit than this morning's),
  `CMSSW_16_1_X` = `8aacfa5da`, `CMSSW_16_0_X` = `de8bdeed9`, `CMSSW_15_1_X` = `e9272496`,
  `CMSSW_15_0_X` = `6db81eb6d`; newest tags `CMSSW_16_1_3`, `CMSSW_16_0_10`.
- `triggerObjects_cff.py` Photon selection is `type(92) && pt > 15 && coll('hltEgammaCandidates')`
  on master, on the tips of `CMSSW_14_1_X`, `14_2_X`, `15_0_X`, `15_1_X`, `16_0_X`, `16_1_X`, and at
  the tags `CMSSW_15_1_0`, `CMSSW_16_0_10`, `CMSSW_16_1_3`. The producer and the matcher are
  unchanged. The fix branch applies cleanly.
- GitHub search: no open pull request or issue mentions `hltEgammaCandidatesUnseeded`,
  `triggerObjects_cff` or photon TrigObj; no PR touched `triggerObjects_cff.py` since June 2026.

### 13.2 Method of the breadth scan

`scripts/deadbits.py <triggerObjects_cff.py> <label=menu.py>...` emulates `mksel` for every
quality-bit entry of every selection, resolves each `filter('pattern')` (NanoAOD wildcard
semantics: `*` only, anchored at both ends unless the pattern starts or ends with `*`) against
the `EDFilter` modules of a menu, reads the collection each matched filter saves its objects from
(`l1EGCand`, `inputTag`, `CandTag`, `inputCandCollection`, `originTagN`, `taus`, `Jets`, ...,
following `inputTagN`/`candTag` chains to the first filter when needed) and compares it with the
`coll()` terms of the selection. Status per bit and menu: OK, COLL (filters exist but the
selection's collection test rejects all of them), STALE (no module matches), UNK (L1 seed
modules, whose objects are L1 objects accepted by type). Configs scanned: master (`ed35654b1`),
`CMSSW_15_0_X` (v15), `CMSSW_13_3_1_patch1` (v13), `CMSSW_13_0_13` (v12). Menus: frozen 2022
v1.2 and v1.4, 2023 v1.2, 2024 v1.4, 2025 v1.3, 2026 v1.3, and the GRun development menus of
13_0_X, 14_0_X, 15_0_X (early and late 2025) and 16_1_X. Raw outputs are in `scan/`.
Limits: the type test of a selection is not emulated (only the collection test), and the Tau
selection's `coll('*Tau*')` is OR-ed with filter terms, so it is treated as non-restrictive.

### 13.3 Findings: same mechanism (object rejected by the selection)

| Where | Bits | Why | Since |
|---|---|---|---|
| Photon | 16, 17, 19 (v15+); 14, 15, 17 (v12 to v14) | unseeded diphoton filters, collection `hltEgammaCandidatesUnseeded` rejected | v12 (PR 40711, Feb 2023) |
| Photon | 8 (`hltHtEcal800`) | `HLTHtMhtFilter` saves `TriggerTHT`/`TriggerMHT` objects from `hltHtMhtEcal` (types 89/90): never type 92, never an e/gamma collection | v10 (12_4_X list; the v9 photon list had no bits at all) |
| BoostedTau (whole table) | all | selection `type(85) && pt > 120 && coll('hltAK8PFJetsCorrected') && filter('hltAK8SinglePFJets*SoftDropMass40*ParticleNetTauTau')`: the pattern is end-anchored, the menus have `...ParticleNetTauTau0p30` (2022) and `...PNetTauTauTag0p03/0p05` (2023+), and the jets come from `hltAK8PFJets230SoftDropMass40`, so no object ever passes | v12, v13, v14 and 15_0_0/15_0_1; relaxed to `type(85) && pt > 120 && filter('*TauTau*')` in `CMSSW_15_0_2` |
| MET (whole table) | none | `skipObjectsNotPassingQualityBits = True` with an empty bit list (`"0"`): no MET object is ever written | every version from 10_6_X (v9) to master |
| Photon (v9) | none | 10_6_X photon selection `type(92) && pt > 20 && coll('hltEgammaCandidates') && !filter('*PixelMatchFilter')` with no bits and the skip flag: no photon TrigObj in Run 2 UL NanoAOD v9 | v9 only |

Electron and Muon have no collection mismatch in any version or menu (the only unacceptable
alternatives, muon-leg filters inside the 2e-1mu and 1e-2mu entries, have an acceptable
electron-leg alternative in the same entry).

### 13.4 Findings: stale filter names (bit defined, no such module in the menu of that year)

Master config against the frozen menus (fine / collection-dead / stale, out of the bit count):

| Object | bits | 2022 v1.4 | 2023 | 2024 | 2025 | 2026 | stale bits in 2025 and why |
|---|---|---|---|---|---|---|---|
| Electron | 20 | 18/0/2 | 18/0/2 | 19/0/1 | 18/0/2 | 18/0/2 | 2 `hltEle*WPLoose*TrackIsoFilter` (gone 2023), 8 triple-electron `DphiLeg` (gone 2025) |
| Photon | 21 | 13/4/4 | 14/3/4 | 15/3/3 | 15/3/3 | 15/3/3 | 12 `hltEG120EBTightID...` (gone 2022 v1.4), 18 and 19 30_18 names (renamed 2023) |
| Muon | 14 | 13/0/1 | 13/0/1 | 14/0/0 | 12/0/2 | 12/0/2 | 2 and 6 `*OverlapFilterIsoMu*PFTau*` (DeepTau mu-tau overlaps, gone 2025; bit 13 PNet replaces them) |
| Tau | 31 | 25/0/6 | 27/0/4 | 31/0/0 | 30/0/1 | 30/0/1 | 3 `*DeepTau*` (gone 2025) |
| BoostedTau | 3 | 1/0/2 | 2/0/1 | 2/0/1 | 2/0/1 | 2/0/1 | 0 `...ParticleNetTauTau0p30` (2022 name) |
| Jet | 46 | 29/0/15 | 38/0/6 | 37/0/7 | 34/0/10 | 34/0/10 | 0, 1, 6, 22, 27 pixel-only HH4b filters (gone 2024), 8 and 9 three-jet pt40/pt45 (gone 2024/2023), 11 DeepCSV, 24 and 25 DeepJet (gone 2025) |
| FatJet | 7 | 6/0/1 | 6/0/1 | 4/0/3 | 4/0/3 | 4/0/3 | 3 ParticleNetBB0p35 names (gone 2023), 4 and 5 `hltAK8DoublePFJetSDModMass30/50` (gone 2024) |
| HT | 6 | 2/0/3 | 3/0/2 | 3/0/2 | 3/0/2 | 3/0/2 | 0 and 1 Run 2 L1 seed names (never in Run 3 menus); bit 2 is an L1 seed that exists |
| MHT | 2 | 2/0/0 | 2/0/0 | 2/0/0 | 2/0/0 | 2/0/0 | none |

(2 Jet bits and 1 HT bit are L1 seed filters counted as fine.) The v12, v13 and v15 configs
give the same picture for their own bit lists (`scan/v12_*.txt`, `scan/v13_*.txt`,
`scan/v15_*.txt`); in v13 the Tau list has 5 stale bits in the 2022 menus and 3 in 2023, and
the BoostedTau list is dead as described above.

### 13.5 Downstream use (GitHub code search, default branches only)

- The unseeded filter names appear outside cms-sw in 16 files: `kevimota/HYgammaRunIII_analysis`
  (`trigger_legend.md`, bits 16 and 17 listed as the legs to match), `cms-flaf/FLAF`
  (`config/Run2_201{6,7,8}/triggers.yaml`, photon bit legends), custom NanoAOD configurations
  (`portalesHEP/higgs-trigger-nano`, `Gianco99/2024_Nano`), and flashgg's MiniAOD-based
  `Validation/test/makeHltTreePhotons.py` (unaffected: flashgg reads the MiniAOD objects).
- 176 files combine `TrigObj_filterBits` with `Diphoton30_22`; most are generic NanoAOD
  readers. HiggsDNA itself is not indexed by code search.

### 13.6 Consequences for the pull request

The one-line fix stays as it is. The scan adds candidates for separate pull requests:
`hltHtEcal800` out of the Photon list (or into HT), the 2023 names of the 30_18 filters, a
per-year statement in the bit documentation, and a note to XPOG about MET (never written) and
BoostedTau (empty in v12 to v14).

---

## 14. Empirical verification on NanoAOD files (lxplus, 4 November 2026)

Done by Santanu's lxplus workflow from the handover prompt (commit `61bb149`, `results/REPORT.md`
and one JSON per file under `results/`): ten files, one per dataset, up to 300000 events each, read
through `root://cms-xrd-global.cern.ch/` with uproot (LCG_107); bit numbers parsed from each file's
own `TrigObj_filterBits` documentation. **Every prediction of sections 7 and 13 holds.**

| NanoAOD | dataset (one file) | events | fired Mass90 | photons with seeded bits | photons with unseeded bits | e unseeded bit | id 2 | id 1515 |
|---|---|---|---|---|---|---|---|---|
| v9 | /EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD | 300000 | 31771 | no id-22 object at all | none defined | n/a | 0 | 0 |
| v10 | /EGamma/Run2022D-PromptNanoAODv10_v2-v1/NANOAOD | 300000 | 46707 | bits not defined (11 photon filters documented) | none defined | n/a | 0 | 0 |
| v11 | /EGamma/Run2022F-PromptNanoAODv11_v1-v2/NANOAOD | 300000 | 41546 | bits not defined (12 photon filters) | none defined | n/a | 0 | 0 |
| v12 | GluGluHtoGG_M-125 Run3Summer22NanoAODv12 | 12979 | 7725 | 12: 15626, 13: 17978 | 14: 0, 15: 0, 17: 0 | not defined | 0 | 0 |
| v12 | /EGamma/Run2022D-22Sep2023-v1/NANOAOD | 300000 | 46407 | 12: 208527, 13: 255099 | 14: 0, 15: 0, 17: 0 | not defined | 0 | 0 |
| v13 | GluGluHto2G_M-125 Run3Summer23NanoAODv13 (ext1-v4) | 17760 | 10453 | 12: 20865, 13: 24170 | 14: 0, 15: 0, 17: 0 | 16: 702 | 0 | 0 |
| v13 | /EGamma/Run2022D-16Dec2023-v1/NANOAOD | 300000 | 46794 | 12: 207844, 13: 252774 | 14: 0, 15: 0, 17: 0 | 16: 29042 | 0 | 0 |
| v14 | /EGamma0/Run2024D-PromptReco-v1/NANOAOD | 300000 | 35892 | 12: 203620, 13: 252039 | 14: 0, 15: 0, 17: 0 | 16: 19444 | 0 | 0 |
| v15 | GluGluH-Hto2G_M-125 RunIII2024Summer24NanoAODv15 | 4180 | 2406 | 14: 4815, 15: 5588 | 16: 0, 17: 0, 19: 0 | 16: 205 | 0 | 22 |
| v15 | /EGamma/Run2022D-NanoAODv15-v1/NANOAOD | 300000 | 48687 | 14: 212270, 15: 258546 | 16: 0, 17: 0, 19: 0 | 16: 30451 | 0 | 430 |

Reading of the table:

- **The claim is confirmed.** Across about 1.2 million events of v12, v13, v14 and v15 (data and MC)
  not one photon object carries an unseeded-leg bit, while the seeded-leg bits of the same paths are
  set on more objects than there are Mass90 events (both leading-leg alternatives, both Mass90 and
  Mass95 contribute). In Mass90-fired events the photons with seeded bits number, for example,
  53153 / 52221 against 46794 fired events in the v13 data file.
- **Controls.** v9 has no photon trigger objects at all (section 13.3); v10 and v11 define no
  diphoton bits; the electron "CaloIdL_MW unseeded" bit is absent in v12 and populated from v13
  (section 0 item 12 and PR 41827), which also proves that unseeded objects reach the table.
- **Side findings confirmed.** No object with id 2 (MET) in any file (section 13.3); no id 1515
  (BoostedTau) in v12 to v14 and 22 / 430 of them in the v15 files (selection relaxed in 15_0_2).
  `hltHtEcal800` (photon bit 8): 0 objects wherever the parser could resolve it (v11 to v15).
- **Documentation curiosities seen in the files.** The v10 file (PromptNanoAODv10, early 12_4_X)
  lists 11 photon filters, without the Mu17_Photon30 leg that the 12_4_X branch tip has as the 12th;
  the v11 file names bits 5 and 6 both `hltEG150HEFilter` (a doc typo in the 12_6_X list). The
  script's bit parser does not read the old `1 = ..., 2 = ...` bitmask-value layout of v9 and v10,
  so the hltHtEcal800 count is missing for v10.
- **Not covered on 4 November** (done on 5 November, section 15): the NANO re-run with the fix,
  and 2024 data at v15 (processing string `MINIv6NANOv15`). Still open: NanoAOD v14 (14_0_X) MC is
  not in DAS; one file per dataset.

Decks: the slide "Measured on real files" was added to both decks (issue deck slide 8, detailed deck
slide 19) and the validation slides were updated.

---

## 15. Fix test and remaining gaps (lxplus, 5 November 2026)

Details and tables: `results/REPORT.md` "Fix test"; JSONs in `results/fix_test/`; commands in
`scripts/make_fixed_nano.sh`; measurement `scripts/measure_trigobj.py`.

- Input: MiniAOD `.../Run3Summer23MiniAODv4/GluGluHto2G_M-125_.../130X_mcRun3_2023_realistic_v15_ext1-v4/2820000/74338d47-0b38-4e0b-83a2-ad85c7f4e533.root`
  (DAS parent of the central v13 file `4f45fe87-...`), 17760 events, NANO made without and with the fix.
- CMSSW_13_3_1_patch1 (v13, line 83 changed): nano_nofix identical to the central v13 file in 17760 / 17760
  events (TrigObj id, filterBits, pt). nano_fix: bits 14 / 15 on 20461 / 18365 photon objects; 10453 / 10453
  Mass90-fired events have a photon with an unseeded bit; those objects have pt >= 22.04 GeV (median 58.30);
  id != 22 identical in 17760 / 17760 events; photon objects 24835 -> 26639; nTrigObj mean 5.287 -> 5.388;
  file 29339920 -> 29363499 bytes.
- CMSSW_15_0_15_patch4 (v15, `Run3_2023,run3_nanoAOD_pre142X`, GT `150X_mcRun3_2023_realistic_v1`; the changed
  line is 86, not 90): bits 16 / 17 on 20461 / 18365 photon objects; 10453 / 10453 Mass90 events; id != 22
  identical in 17760 / 17760 events; photon objects 25188 -> 26807; nTrigObj mean 38.134 -> 38.225.
- Bit 17 (v13) / 19 (v15), Diphoton30_18 unseeded, stays 0 after the fix on this 2023 MC (filter renamed in
  2023, section 13.4).
- New rows of the file measurement: `/EGamma0/Run2024D-MINIv6NANOv15-v1/NANOAOD` (2024 data at v15):
  bits 16/17/19 = 0, seeded 14/15 = 201628/248974, 30945 Mass90 events; `/GluGluHToGG_M-125_..._powheg-pythia8/Run3Winter24NanoAOD-133X_mcRun3_2024_realistic_v9-v2/NANOAODSIM`
  (133X, 18-bit `>i4` layout): bits 14/15/17 = 0, 101598 Mass90 events.
- Remaining gaps: NanoAOD v14 MC (14_0_X) not found in DAS; the MiniAOD dataset
  `.../Run3Summer23MiniAODv4-130X_mcRun3_2023_realistic_v14-v2/MINIAODSIM` has 0 files.
- Decks and report (5 November): slide "Fix test on real input" added (issue deck slide 9, detailed
  deck slide 20); measured, validation, summary, next/pr-plan and fix slides updated; report section 9
  is now "Validation" (9.1 files, 9.2 fix test, 9.3 relval) and section 10 gives the pushed state.

---

## 16. Build and relval check on the synced master (lxplus, 5 November 2026)

CMSSW_16_1_3 with commit `aebf3eb64` cherry-picked (one changed line, `git diff CMSSW_16_1_3 --numstat`) builds
and runs relval 12452.0 (H125GGgluonfusion 2023, upgrade matrix, 10 events) and 141.046 (EGamma 2023D, 100 events,
RAW from the IB EOS cache because DAS has it on tape only) without exceptions; steps 3-4 ran in both areas on the
same `step2.root`. Clean and fix agree in TrigObj (10 / 10 and 100 / 100 events) and in every DQM histogram except
25 `DQM/TimerService` ones per workflow. The NANO TrigObj table is empty in both workflows and areas (the relval
HLT trigger summaries are 1.3-1.4 kB per event, against 34.6 kB for the original 2023 HLT summary in the 141.046
input), so this relval does not exercise the photon selection; the fix test of section 15 does. Details:
`results/REPORT.md` "Relval in CMSSW_16_1_3"; JSONs in `results/relval_16_1_3/`; script
`scripts/relval_fix_check.sh`.

---

## 17. 2026 PromptReco NANOAOD, CMSSW_16_0_X (lxplus, 5 November 2026)

DAS has no dataset named NanoAOD v16 (`*NanoAODv16*`, `*Nanov16*`, `*NANOv16*`, data and MC). The 2026 EGamma0
PromptReco NANOAOD is made in CMSSW_16_0_X (DAS `release`: Run2026A 16_0_2_patch1; Run2026B 16_0_2_patch1, 16_0_4;
Run2026C 16_0_4_patch2, 16_0_5_patch1); it is labelled here "16_0_X PromptReco", not v16. Same procedure as
section 14 (`scripts/measure_trigobj.py`, first DAS file, 300000 events, LCG_107):

| release | dataset (one file) | events | fired Mass90 | photons with seeded bits | photons with unseeded bits | e unseeded bit | id 2 | id 1515 |
|---|---|---|---|---|---|---|---|---|
| 16_0_X | /EGamma0/Run2026C-PromptReco-v1/NANOAOD | 300000 | 1511 | 14: 124972, 15: 145161 | 16: 0, 17: 0, 19: 0 | 16: 1034 | 0 | 42 |

- 21 photon bits documented, same bit numbers as v15. 0 events with an unseeded photon bit; in Mass90-fired events
  1655 / 1579 photons carry seeded bits 14 / 15 and 0 carry unseeded bits.
- Mass90 fired in 1511 of 300000 events, against 31771-48687 in the data files of section 14; not investigated.
- File `/store/data/Run2026C/EGamma0/NANOAOD/PromptReco-v1/000/402/536/00000/38961e9f-be5f-4319-a1b9-bf287597c1fc.root`
  (454912 events). JSON: `results/16_0_X_EGamma0_Run2026C_PromptReco.json`.

---

## 18. Fix test on 2026 data, CMSSW_16_0_4_patch2 (lxplus, 5 November 2026)

`scripts/make_fixed_nano.sh v16`: CMSSW_16_0_4_patch2 (release of the central Run2026C PromptReco NANO file,
`edmProvDump`), `--data`, era `Run3_2026`, GT `160X_dataRun3_Prompt_frozen260223_v1` (`autoCond.py:39`
`run3_data_prompt` of that release; the GT Tier0 used is not in the file provenance and was not checked). Input
`/store/data/Run2026C/EGamma0/MINIAOD/PromptReco-v1/000/402/536/00000/33c652d5-5e17-456b-9b90-6d8e00734855.root`
(run 402536, same run as the section 17 file), first 20000 events, NANO made without and with the fix (line 86
changed, one line). JSONs: `results/fix_test/v16_nano_nofix.json`, `results/fix_test/v16_nano_fix.json`.

| | nano_nofix | nano_fix |
|---|---|---|
| fired Mass90 | 308 | 308 |
| photons with bit 16 / 17 (all events) | 0 / 0 | 671 / 1010 |
| photons with bit 16 / 17 (Mass90 events) | 0 / 0 | 334 / 507 |
| photons with bit 19 | 0 | 0 |
| photons with seeded bit 14 / 15 | 8909 / 10760 | 8909 / 10760 |
| Mass90 events with an unseeded photon bit | 0 / 308 | 308 / 308 |
| unseeded-bit photons: n, min pt, median pt | 0 | 1234, 22.01 GeV, 37.06 GeV |
| photon objects (id 22) | 12744 | 13109 |
| electrons with CaloIdL_MW unseeded bit | 189 | 189 |
| nTrigObj mean | 2.0998 | 2.11805 |

- Same outcome as the v13 and v15 fix tests of section 15: without the fix the unseeded bits are 0, as in the
  central file of section 17; with it every Mass90-fired event has a photon with an unseeded bit, seeded-bit
  counts unchanged.
- Bit 19 (Diphoton30_18 unseeded) stays 0 after the fix, as in section 15; not investigated for 2026.
- Not checked here: event-by-event agreement of nano_nofix with a central file, and the id != 22 comparison.
- Log: `/eos/user/s/smahata/trigobj_check/make_fixed_nano_v16.log`.

---

## 19. Unseeded-leg trigger efficiency, Z->ee tag-and-probe on re-made NANO (lxplus, 6 November 2026)

`scripts/tnp_unseeded.py` (one file) and `scripts/plot_tnp_compare.py` (no fix vs fix overlay). Tag: tight electron
(`Electron_cutBased` 4), pT > 35 GeV, |eta_SC| < 2.1, event fires `HLT_Ele32_WPTight_Gsf`, matched (dR < 0.1) to an
electron TrigObj with the WPTight bit and to a photon TrigObj with a seeded-leg bit. Probe: other electron, cutBased
>= 2, pT > 15 GeV, |eta_SC| < 2.5 outside 1.4442-1.566, opposite charge, 70 < m_ee < 110 GeV; same-sign pairs counted
only. Pass: probe matched to a photon TrigObj with the unseeded TrackIso bit, the R9 bit, either, or (control) either
seeded bit. Bit numbers parsed from each file. 68% Clopper-Pearson intervals; no background subtraction.

v13 data: `scripts/make_fixed_nano.sh v13data`, CMSSW_13_3_1_patch1 (DAS release of
`/EGamma/Run2022D-16Dec2023-v1/NANOAOD`), era `Run3`, GT `133X_dataRun3_v3` (`autoCond.py:41` `run3_data`; the
16Dec2023 GT was not found, section 3.4), input `/store/data/Run2022D/EGamma/MINIAOD/22Sep2023-v1/2520000/05d4c158-d7eb-439d-bf0c-947db0f8d58c.root`
(one of the 40 DAS parents of the central v13 file `499b6a69-...`), all 62007 events. 23299 events fire Ele32, 8978 tags,
1210 opposite-sign and 12 same-sign pairs.

| numerator | no fix | with fix |
|---|---|---|
| unseeded TrackIso (bit 14) | 0 / 1210 | 1118 / 1210 = 0.924 |
| unseeded R9 (bit 15) | 0 / 1210 | 827 / 1210 = 0.683 |
| unseeded leg, bit 14 or 15 | 0 / 1210 | 1125 / 1210 = 0.930 (0.922-0.937) |
| seeded leg, bit 12 or 13 | 979 / 1210 = 0.809 | 979 / 1210 = 0.809 |

- Unseeded leg with fix vs probe pT: 15-20 GeV 0/17, 20-22 1/18, 22-25 25/28, 25-30 103/111, 30-35 136/147,
  35-40 226/237, 40-50 505/522, 50-70 112/113, 70-100 12/12. Vs |eta_SC|: 0-0.8 548/560, 0.8-1.4442 345/368,
  1.566-2.0 124/168, 2.0-2.5 108/114. The 1.566-2.0 bin was not investigated.
- Seeded leg identical without and with the fix in every pT bin (0, 0, 0, 13, 128, 216, 495, 110, 12).
- 2026C data (section 18 files, 20000 events, run before the seeded numerator existed): 739 Ele32 events, 263 tags,
  42 opposite-sign and 2 same-sign pairs; unseeded leg 0 / 42 without and 39 / 42 with the fix.
- Probes are electrons. The nofix file was not compared event by event with the central v13 file.
- Results: `results/tnp_2022D_v13/` (JSON, per-file plots, `tnp_compare.png`), `results/tnp_2026C/`. Slide
  "Trigger efficiency with the fix" added after the fix-test slide in the three decks.

---

## 20. v13 data recipe check: re-made no-fix NANO vs the central 16Dec2023 file (lxplus, 6 November 2026)

`scripts/measure_trigobj.py` with the reference file
`/store/data/Run2022D/EGamma/NANOAOD/16Dec2023-v1/2550000/499b6a69-bd7e-4bce-bd6d-4ab4f250ea2d.root` (964636 events);
the comparison now selects the reference events whose (run, lumi, event) are in the compared file instead of reading
the first 300000 entries. `cmssw/v13data/nano_nofix.root` (section 19, 62007 events): 19539 events in common, TrigObj
(id, filterBits, pt) identical in 19539 / 19539, also with id 22 excluded. The other 42468 events are not in this
central file. JSON: `results/fix_test/v13data_nano_nofix.json`.

---

## 21. Tag-and-probe on all 40 parent files, Diphoton30_22 and Diphoton30_18 legs (lxplus HTCondor, 7 November 2026)

Same tag, probe and pass definitions as section 19, now for two path families. `scripts/tnp_unseeded.py` takes the
seeded and unseeded bits of each family from `LEGS`; the tag must match a seeded bit of the family being measured.
Bits parsed from the files (identical in all 80 job logs): electron WPTight 1; 30_22 seeded 12, 13, unseeded 14
(TrackIso), 15 (R9); 30_18 seeded 16 (EG30 EcalIso), unseeded 17 (EG18 TrackIso, the only unseeded 30_18 bit).

Input: the 40 MINIAOD parents of the central v13 file `499b6a69-...` (DAS), 3125939 events. One HTCondor job per file
(`scripts/condor/`: `tnp.sub`, `tnp_job.sh`) runs the dumped no-fix and fix NANO configurations of
`make_fixed_nano.sh v13data` with cmsRun, then `tnp_unseeded.py` on each NANO; only the JSONs come back. Cluster
9771223, 40 / 40 jobs return value 0. Merged with `scripts/merge_tnp.py`; 1142457 events fire Ele32.

| family | opposite / same sign pairs | unseeded leg, no fix | unseeded leg, with fix | seeded leg (no fix = fix) |
|---|---|---|---|---|
| 30_22 | 59863 / 596 | 0 | 55133 = 0.921 (0.920-0.922) | 48108 = 0.804 |
| 30_18 | 57727 / 537 | 0 | 52460 = 0.909 (0.908-0.910) | 44989 = 0.779 |

- 30_22 with fix: TrackIso 54874 (0.917), R9 40909 (0.683).
- Unseeded leg with fix vs probe pT (bins 15, 17, 18, 20, 22, 25, 30, 35, 40, 50, 70, 100 GeV):
  - 30_22: 0/423, 1/244, 6/581, 109/784, 1246/1605, 3794/4179, 6894/7325, 11601/12201, 24553/25422, 5874/6037, 701/708.
  - 30_18: 8/404, 51/237, 359/560, 626/758, 1343/1556, 3538/4039, 6403/7083, 10760/11788, 22896/24476, 5496/5805,
    647/680.
- Vs |eta_SC| (0-0.8, 0.8-1.4442, 1.566-2.0, 2.0-2.5):
  - 30_22: 26595/27529, 16568/17856, 6256/8258, 5714/6220.
  - 30_18: 26325/26961, 16199/17206, 4613/7790, 5323/5770.
  - The 1.566-2.0 bin is lower also for the seeded leg; not investigated.
- Seeded leg identical without and with the fix in every bin; tags, pairs and probe counts identical in the no-fix and
  fix files (checked by `plot_tnp_compare.py`).
- Results: `results/tnp_2022D_v13_40files/` (`merged_nofix.json`, `merged_fix.json`, `tnp_compare_30_22.png`,
  `tnp_compare_30_18.png`). The efficiency slides in the three decks now show these two plots.

## 22. MiniAOD reference: cut-and-count on the same 40 MINIAOD files vs the fixed NanoAOD (lxplus HTCondor, 10 November 2026)

I measure the same tag-and-probe efficiencies directly on the 40 MINIAOD parents of section 21 (same `inputs.txt`,
same events), as the reference for the fixed NanoAOD. `scripts/tnp_miniaod.py` (FWLite, CMSSW_13_3_1_patch1) applies
the cuts of `tnp_unseeded.py`:
- electron ID from the stored `cutBasedElectronID-RunIIIWinter22-V1-loose` / `-tight` of `slimmedElectrons`, the ID
  NanoAOD re-runs for `Electron_cutBased` (`electrons_cff.py` lines 20-28 in 13_3_1_patch1); pT is the MINIAOD pT,
  since NanoAOD calibrates `Electron_pt` only for `run2_egamma`; eta_SC = `superCluster().eta()`;
- trigger matching by filter label in `slimmedPatTrigger` (dR < 0.1); the tag objects pass the NanoAOD electron and
  photon TrigObj selections (`triggerObjects_cff.py` lines 57, 63, 83);
- every numerator twice: raw (label only) and `_pt15` (label and trigger-object pT > 15, the NanoAOD photon cut).

Content check on 2000 events of `05d4c158-...`: both IDs stored; all seven filter labels present on trigger objects.
One-file check on `05d4c158-...` (62007 events): every count equal to `tnp_unseeded.py` on the fixed NANO of the same
file. Full run: cluster 9773146 (`scripts/condor/tnp_mini.sub`, `tnp_mini_job.sh`), 40 / 40 jobs return value 0,
3125939 events, 1142457 fire Ele32.

| family | | tags | opposite / same sign pairs | unseeded leg (either) | seeded leg |
|---|---|---|---|---|---|
| 30_22 | MiniAOD | 447698 | 59861 / 596 | 55132 = 0.9210 (0.9199-0.9221) | 48107 = 0.8036 (0.8020-0.8053) |
| 30_22 | fixed NanoAOD | 447700 | 59863 / 596 | 55133 = 0.9210 (0.9199-0.9221) | 48108 = 0.8036 (0.8020-0.8053) |
| 30_18 | MiniAOD | 424647 | 57725 / 537 | 52458 = 0.9088 (0.9075-0.9100) | 44988 = 0.7794 (0.7776-0.7811) |
| 30_18 | fixed NanoAOD | 424650 | 57727 / 537 | 52460 = 0.9088 (0.9075-0.9100) | 44989 = 0.7793 (0.7776-0.7811) |

- 30_22 MiniAOD: TrackIso 54873, R9 40908 (fixed NanoAOD 54874, 40909).
- `_pt15` equals raw for every numerator: no MINIAOD trigger-object match below 15 GeV is lost by the NanoAOD cut.
- Per file, 25 of 40 files differ from the fixed NanoAOD by 1-3 tags or pairs, both signs, at cut and bin edges.
  NanoAOD stores electron eta, phi with 12 mantissa bits and deltaEtaSC with 10 (`common_cff.py` lines 41, 44;
  `electrons_cff.py` line 319), TrigObj eta, phi with 12 (`TriggerObjectTableProducer.cc` lines 320-321). With that
  rounding applied to MINIAOD before any cut (`tnp_miniaod.py ... nanoprec`, a copy of
  `ReduceMantissaToNbitsRounding`; cluster 9773153, `tnp_mini_nanoprec.sub`, 40 / 40 return value 0), every count
  equals the fixed NanoAOD in every bin, every numerator, both families, all 40 files (0 / 80 file-family differences).
- 68% Clopper-Pearson intervals.
- Results: `results/tnp_2022D_v13_40files/` (`merged_mini.json`, `merged_mini_nanoprec.json` without the per-pair rows,
  which stay in `/afs/cern.ch/user/s/smahata/tnp_condor_mini/`; `mini_vs_nano_30_22.png`, `mini_vs_nano_30_18.png`
  from `scripts/plot_mini_vs_nano.py`, lower panel MiniAOD / fixed NanoAOD). `scripts/merge_tnp.py` now also
  concatenates per-pair rows when present.

## 23. Fix branch rebased; PR description shortened (13 November 2026)

- `nano-photon-trigobj-unseeded` rebased onto upstream master `43690ddd6` (13 November 2026): cherry-pick of
  `828ed8b2a`, new tip `8bb009d9b`, same author, message and one-line diff. GitHub compare
  `cms-sw:master...santanumahata:nano-photon-trigobj-unseeded`: 1 ahead, 0 behind,
  `triggerObjects_cff.py +1 -1`. `828ed8b2a` is no longer on a branch; the relval records of section 16 and
  `results/CODE.md` refer to it as it was then.
- `pr/0001-NanoAOD-photon-TrigObj-unseeded-collection.patch` regenerated from `8bb009d9b`.
- `pr/PR_body.md` shortened to the bug, its effect (unseeded photon bits 0 in central NanoAOD from v12 on,
  section 14) and the fix, with an FYI to `@cms-sw/egamma-pog-l2`; no validation or backport section.
- No PR opened; nothing pushed to `cms-sw/cmssw`.
