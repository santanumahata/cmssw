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
- `results/`: the lxplus measurement on ten NanoAOD files, v9 to v15 (`REPORT.md` and one JSON per
  file): the unseeded photon bits are never set, all controls behave; see `NOTES.md` section 14.
- `results/fix_test/`: NANO re-made from one MiniAOD file without and with the fix
  (CMSSW_13_3_1_patch1 for v13, CMSSW_15_0_15_patch4 for v15) and the central v13 file of the
  same events, one JSON each; see `results/REPORT.md` "Fix test" and `NOTES.md` section 15.
- `results/relval_16_1_3/`: relval workflows in CMSSW_16_1_3 clean vs with commit aebf3eb64
  (TrigObj and DQM comparisons); see `results/REPORT.md` and `NOTES.md` section 16.
- `scripts/measure_trigobj.py`, `scripts/make_fixed_nano.sh`, `scripts/relval_fix_check.sh`,
  `scripts/compare_dqm.py`: the measurement, the fix test and the relval check as run on lxplus.

Fix in one line, `PhysicsTools/NanoAOD/python/triggerObjects_cff.py`, Photon selection:

    type(92) && pt > 15 && (coll('hltEgammaCandidates') || coll('hltEgammaCandidatesUnseeded'))

## Slides

Two decks, built on 4 November 2026 and updated on 5 November with the fix test and the relval (the files below are current; the private Claude artifacts still show the 4 November version):

| Deck | Slides | PDF | Standalone HTML | Source (Slides format) | Claude artifact |
|---|---|---|---|---|---|
| Issue deck (problem, scope, measurement, fix test, fix) | 64 | `slides/issue-deck.pdf` | `slides/issue-deck.html` | `slides/issue-deck-src/project/` | https://claude.ai/artifact/CnPtNgvGdp6PAAh9xfizof |
| Detailed walkthrough (code at every step, breadth scan, measurement, fix test, appendices) | 86 | `slides/detailed-deck.pdf` | `slides/detailed-deck.html` | `slides/detailed-deck-src/project/` | https://claude.ai/artifact/Qx2HzCEjougjAQmaH6P2Qc |

Beamer version (dark CMS style, 108 frames: the main talk plus backup frames with the code at every step, all
tables, history, production recipe and reproducibility): source `slides/beamer/src/trigobj_unseeded.tex` with
`preamble.tex`, PDF `slides/beamer/outputs/trigobj_unseeded.pdf`. Build from `slides/beamer/src/` with
`pdflatex -interaction=nonstopmode -output-directory=../outputs trigobj_unseeded.tex`, twice.

All three decks end with a "Backup: code" section (53 slides in each HTML deck, 60 frames in Beamer): every
script in `scripts/` except the two renderers, and `slides/code/commands_as_run.sh`, the hand-run commands of
5 November 2026 copied verbatim from the session log. `scripts/make_commands_file.py` writes that file;
`scripts/make_code_slides.py <repo root>` writes `slides/beamer/src/code_backup.tex` and the `code-*` slides.

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
