# nanoaod-trigobj-notes

Knowledge base from the investigation of the dead unseeded-leg photon filter bits in CMS
NanoAOD (diphoton triggers), the NanoAOD v13 production recipe, and the one-line fix.

- `NOTES.md`: the full notes (versions, recipes, trigger-object machinery, HLT path anatomy,
  the bug, affected versions and triggers, fix, validation, PR readiness, environment notes,
  commands, sources).
- `report/`: the issue report as PDF and its HTML source; `scripts/render_pdf.js` renders it.
- `pr/`: the patch against upstream `cms-sw/cmssw` master and the PR title and body.

Fix in one line, `PhysicsTools/NanoAOD/python/triggerObjects_cff.py`, Photon selection:

    type(92) && pt > 15 && (coll('hltEgammaCandidates') || coll('hltEgammaCandidatesUnseeded'))
