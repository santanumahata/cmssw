Title: NanoAOD: accept unseeded e/gamma trigger objects in the Photon TrigObj selection

#### PR description:

The `Photon` entry of `triggerObjectTable` (`PhysicsTools/NanoAOD/python/triggerObjects_cff.py`) selects only trigger objects from the `hltEgammaCandidates` collection. The sub-leading (unseeded) legs of `HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90` and `_Mass95` run on `hltEgammaCandidatesUnseeded`: their last filters `hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter` and `hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter` (and `hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter` of the `HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId*` paths in the 2018 and 2022 menus) have dedicated `TrigObj_filterBits` (bits 16, 17 and 19 in the current list; 14, 15 and 17 in NanoAOD v12 to v14).

A `coll()` argument without wildcard is compared exactly with the stored collection label (`pat::TriggerObjectStandAlone::hasCollection` falls back to `pat::TriggerObject::hasCollection`), and `TriggerObjectTableProducer` evaluates `sel` before the quality bits, so every object carrying these filter labels is discarded and the bits can never be set. They have been dead since they were introduced in #40711 (NanoAOD v12 onwards; the filter names and collections are unchanged in every HLT menu from 2018 to 2026). #41827 fixed the identical problem for the `Electron` selection only.

This PR adds `hltEgammaCandidatesUnseeded` to the `Photon` selection, mirroring the `Electron` selection. Since `skipObjectsNotPassingQualityBits = True`, only unseeded objects that pass one of the photon filters are stored, and the only photon-bit filters that run on the unseeded collection are the diphoton sub-leading-leg filters listed above. The producer's self-cleaning merges an unseeded object with a seeded one pointing in the same direction. No bit numbers or documentation strings change.

#### PR validation:

Standard workflows that include the NANO step, before and after the change, for example `runTheMatrix.py -l 12452.0,12852.0,141.046` (H125GGgluonfusion_14TeV 2023 and 2024 with RecoNano, which fire the diphoton triggers; RunEGamma2023D with AODNANORUN3). Expected differences are limited to photon trigger objects (`TrigObj_id == 22`) in events firing the diphoton triggers: entries with bits 16 and 17 appear (zero before this change), and `nTrigObj` and the `TrigObj` DQM histograms move accordingly, as for electrons in #41827.

#### If this PR is a backport, please specify the original PR and why you need to backport that PR:

Not a backport. A backport to the NanoAOD production branch (`CMSSW_15_0_X`) is requested if a further NanoAOD production from that branch is planned.
