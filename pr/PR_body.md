Title: NanoAOD: accept unseeded e/gamma trigger objects in the Photon TrigObj selection

#### PR description:

The `Photon` selection of `triggerObjectTable` (`PhysicsTools/NanoAOD/python/triggerObjects_cff.py`) accepts only `coll('hltEgammaCandidates')`. The sub-leading legs of the `HLT_Diphoton30_22` (and 2018/2022 `HLT_Diphoton30_18`) paths run on `hltEgammaCandidatesUnseeded`, so their objects are rejected before the filter bits are evaluated, and their dedicated `TrigObj_filterBits` (16, 17, 19; 14, 15, 17 in v12 to v14) can never be set. As a result, these bits are 0 for every photon in central NanoAOD from v12 on, and the sub-leading diphoton leg cannot be matched to its HLT object.

This PR adds `hltEgammaCandidatesUnseeded` to the `Photon` selection. No bit numbers or documentation strings change.

@cms-sw/egamma-pog-l2 FYI
