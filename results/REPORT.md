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

## Not covered

- Optional step 7 (re-running NANO with the fix) was not done.
- No v14 MC: no GluGluH*G* dataset matching `*NanoAODv14*` or `Run3Summer24*` NANOAODSIM was found in DAS.
- No 2024 data at v15 (`/EGamma*/Run2024*NanoAODv15*/NANOAOD` returned nothing).
- One file per dataset; v12/v13/v15 MC files contain 12979, 17760 and 4180 events.
