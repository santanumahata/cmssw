# NanoAOD photon TrigObj fix — TODO

**Last updated:** 2026-11-14

## Now
- PR open: https://github.com/cms-sw/cmssw/pull/52514 — waiting for cms-bot, xpog L2 signature, tests, ORP merge.

## Next
1. On PR 52514: xpog L2 signature (`enibigir`, `ram1123`, `vepadulano`, `battibass`), tests, then an ORP merge
   (`sextonkennedy`, `mandrenguyen`, `ftenchini`); from cms-bot `categories.py`, `categories_map.py`,
   `cmssw_l2/l2.json`, 13 November.
2. Supervisor deck footer still reads "9 November 2026" (`slides/supervisor_10/src/trigobj_short.tex`, local only) —
   decide whether to change the date.
3. Follow-ups kept out of the one-line PR (`NOTES.md` section 8.2): 2023+ names of the Diphoton30_18 filters as
   alternatives in the existing bits; bits for the low-mass and other diphoton paths, to be agreed with EGM and Higgs.

## Blocked
- Nothing blocked.

## Done
- 2026-11-14 — PR https://github.com/cms-sw/cmssw/pull/52514 opened on `master` from `8bb009d9b`: 1 file, +1 -1,
  author santanumahata; name scan of commit, patch, title and body 0.
- 2026-11-13 — Runbook split into card `RUNBOOK.md` (7.4 KB) and `RUNBOOK-DETAIL.md` (23.7 KB); new step 12 (PR
  preparation), conventions for the PR body, EGM tag and signing — commit `4e57cd9`, `git ls-remote` equals HEAD.
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
