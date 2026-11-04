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

## Slides

Two decks, built on 4 November 2026 (private Claude artifacts; the files below are viewable without them):

| Deck | Slides | PDF | Standalone HTML | Source (Slides format) | Claude artifact |
|---|---|---|---|---|---|
| Issue deck (problem, scope, fix) | 9 | `slides/issue-deck.pdf` | `slides/issue-deck.html` | `slides/issue-deck-src/project/` | https://claude.ai/artifact/CnPtNgvGdp6PAAh9xfizof |
| Detailed walkthrough (code at every step, breadth scan, appendices) | 31 | `slides/detailed-deck.pdf` | `slides/detailed-deck.html` | `slides/detailed-deck-src/project/` | https://claude.ai/artifact/Qx2HzCEjougjAQmaH6P2Qc |

`scripts/render_deck.js <deck root> <output base>` turns a deck's `project/` folder into the standalone HTML
and the PDF (Node + Playwright with Chromium; Google Fonts are used when reachable, otherwise the
basic faces).

## Where this lives on GitHub

Everything is in the fork `santanumahata/cmssw` only; nothing was pushed to `cms-sw/cmssw` and no pull
request has been opened.

- Notes, scripts, scan outputs, report and slides (this repository, as a branch of the fork):
  https://github.com/santanumahata/cmssw/tree/nanoaod-trigobj-notes
- The fix on top of upstream master (branch for the future pull request, commit aebf3eb64):
  https://github.com/santanumahata/cmssw/tree/nano-photon-trigobj-unseeded
- The same fix on the fork's own master (session working branch, commit 1699a39f7):
  https://github.com/santanumahata/cmssw/tree/claude/fervent-lamport-3oiuh6
- To open the pull request later (creates nothing by itself):
  https://github.com/cms-sw/cmssw/compare/master...santanumahata:cmssw:nano-photon-trigobj-unseeded
