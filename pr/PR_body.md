Title: NanoAOD: accept unseeded e/gamma trigger objects in the Photon TrigObj selection

#### PR description:

The `Photon` entry of `triggerObjectTable` (`PhysicsTools/NanoAOD/python/triggerObjects_cff.py`) selects only trigger objects from the `hltEgammaCandidates` collection. The sub-leading (unseeded) legs of `HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90` and `_Mass95` run on `hltEgammaCandidatesUnseeded`: their last filters `hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter` and `hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter` (and `hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter` of the 2022-menu `HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId*` paths) have dedicated `TrigObj_filterBits` (bits 16, 17 and 19 in the current list; 14, 15 and 17 in NanoAOD v12 to v14).

`coll()` compares the collection label exactly (`pat::TriggerObject::hasCollection`), and `TriggerObjectTableProducer` evaluates `sel` before the quality bits, so every object carrying these filter labels is discarded and the bits can never be set. They have been dead since they were introduced in #40711 (NanoAOD v12 onwards). #41827 fixed the identical problem for the `Electron` selection only.

This PR adds `hltEgammaCandidatesUnseeded` to the `Photon` selection, mirroring the `Electron` selection. Since `skipObjectsNotPassingQualityBits = True`, only unseeded objects that pass one of the photon filters are stored, and the only photon bits whose filters run on the unseeded collection are the diphoton sub-leading-leg bits listed above. The producer's self-cleaning merges an unseeded object with a coincident seeded one. No bit numbers or documentation strings change.

#### PR validation:

NanoAOD relval workflows reading 2023 and 2024 MiniAOD (`runTheMatrix.py -l 2500.1,2500.11,2500.2,2500.21`). Expected changes are limited to the photon trigger-object multiplicity in events firing the diphoton triggers: photon `TrigObj` with bits 16 and 17 appear (zero before this change), and `nTrigObj` and the trigger-object DQM histograms move accordingly, as for electrons in #41827.

#### If this PR is a backport, please specify the original PR and why you need to backport that PR:

Not a backport. A backport to the NanoAOD production branch (`CMSSW_15_0_X`) is requested if a further NanoAOD production from that branch is planned.
