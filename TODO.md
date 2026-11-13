# NanoAOD photon TrigObj fix — TODO

**Last updated:** 2026-11-13

## Now
- PR ready to open — fix branch `8bb009d9b` and `pr/PR_body.md` final; not opened (Next 1).

## Next
1. Open the PR myself, by hand:
   https://github.com/cms-sw/cmssw/compare/master...santanumahata:cmssw:nano-photon-trigobj-unseeded — title and
   body from `pr/PR_body.md`.
2. After opening: xpog L2 signature (`enibigir`, `ram1123`, `vepadulano`, `battibass`), tests, then an ORP merge
   (`sextonkennedy`, `mandrenguyen`, `ftenchini`); from cms-bot `categories.py`, `categories_map.py`,
   `cmssw_l2/l2.json`, 13 November.
3. Supervisor deck footer still reads "9 November 2026" (`slides/supervisor_10/src/trigobj_short.tex`, local only) —
   decide whether to change the date.
4. Follow-ups kept out of the one-line PR (`NOTES.md` section 8.2): 2023+ names of the Diphoton30_18 filters as
   alternatives in the existing bits; bits for the low-mass and other diphoton paths, to be agreed with EGM and Higgs.

## Blocked
- Runbook update for the PR preparation (new step 12, conventions, changelog line) — **waiting on:** my choice
  between splitting `RUNBOOK.md` into card + `RUNBOOK-DETAIL.md`, or keeping one file and adding step 12.

## Done
- 2026-11-13 — Notes branch updated: short `pr/PR_body.md` (bug, effect, fix, EGM FYI tag), patch regenerated from
  `8bb009d9b`, new hash in `README.md` and `RUNBOOK.md`, `NOTES.md` section 23 appended — commit `a02c7de`,
  `git ls-remote` equals HEAD.
- 2026-11-13 — Fix branch `nano-photon-trigobj-unseeded` rebased onto cms-sw master `43690ddd6`: tip `8bb009d9b`,
  author and committer santanumahata; GitHub compare 1 ahead, 0 behind, `triggerObjects_cff.py +1 -1`; name scan 0.
- 2026-11-13 — EGM tag `@cms-sw/egamma-pog-l2` checked: used in 71 cms-sw/cmssw issues and PRs (GitHub search).
- 2026-11-11 — `RUNBOOK.md` rebuilt and extended (step 7a, MiniAOD convention, gotchas) — commit `6a4618c`.
- 2026-11-10 — MiniAOD vs fixed NanoAOD cut-and-count on the same 40 files: 0.9210 (30_22) and 0.9088 (30_18) in
  both; with NanoAOD rounding 0 / 80 file-family differences (cluster 9773153) — `NOTES.md` section 22, commit
  `910b916`, plots `results/tnp_2022D_v13_40files/mini_vs_nano_30_{22,18}.png`.
- 2026-11-10 — Supervisor deck: two MiniAOD vs NanoAOD slides added, 12 pages, 0 overfull (local only,
  `slides/supervisor_10/outputs/trigobj_short.pdf`).

## Done (archive)
