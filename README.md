# nanoaod-trigobj-notes

Knowledge base from the investigation of the dead unseeded-leg photon filter bits in CMS
NanoAOD (diphoton triggers), the NanoAOD v13 production recipe, and the one-line fix.
Second pass of 4 November 2026: every statement re-verified against the code, the release
tags and nineteen HLT menu files; the corrections are listed in section 0 of `NOTES.md`.

- `NOTES.md`: the full notes (corrections of the second pass, versions, recipes,
  trigger-object machinery, HLT path anatomy with per-menu path versions, the bug, affected
  versions and triggers, fix, validation, PR readiness, environment notes, commands, sources).
- `report/`: the issue report as PDF and its HTML source; `scripts/render_pdf.js` renders it.
- `pr/`: the patch against upstream `cms-sw/cmssw` master and the PR title and body.
- `scripts/`: the scanners used for the verification (`bits.py`, `menuscan.py`,
  `menusummary.py`, `pathmatrix.py`, `bitfilters.py`, `wfn.py`, `deadbits.py`); run with
  `python3 -I` and the downloaded files as arguments.
- `scan/`: outputs of `deadbits.py` (every filter bit of every object type resolved against the
  2022 to 2026 menus; see `NOTES.md` section 13).

Fix in one line, `PhysicsTools/NanoAOD/python/triggerObjects_cff.py`, Photon selection:

    type(92) && pt > 15 && (coll('hltEgammaCandidates') || coll('hltEgammaCandidatesUnseeded'))
