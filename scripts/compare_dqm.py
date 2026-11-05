#!/usr/bin/env python3
"""List the histograms that differ between two harvested DQM files.

Usage: python3 compare_dqm.py <clean DQM_V0001_*.root> <fix DQM_V0001_*.root> <out.json>
"""
import json
import sys

import numpy as np
import uproot


def histograms(path):
    # Total: time O(n_hist * n_bins), space O(n_hist * n_bins)
    found = {}
    with uproot.open(path) as root_file:
        for name, classname in root_file.classnames().items():  # dict scan O(n)   | every stored object
            if not classname.startswith(("TH1", "TH2", "TH3", "TProfile")):
                continue
            found[name.split(";")[0]] = root_file[name].values(flow=True)  # array O(bins) | bin contents
    return found


def main():
    # Total: time O(n_hist * n_bins), space O(n_hist * n_bins)
    clean_path, fix_path, out_path = sys.argv[1:4]
    clean, fix = histograms(clean_path), histograms(fix_path)
    only_clean = sorted(set(clean) - set(fix))                 # set diff O(n)    | histograms lost by the fix
    only_fix = sorted(set(fix) - set(clean))                   # set diff O(n)    | histograms added by the fix
    differing = sorted(name for name in set(clean) & set(fix)  # set join O(n)    | same name, different bins
                       if clean[name].shape != fix[name].shape or not np.array_equal(clean[name], fix[name]))
    result = {
        "clean": clean_path,
        "fix": fix_path,
        "n_histograms_clean": len(clean),
        "n_histograms_fix": len(fix),
        "only_in_clean": only_clean,
        "only_in_fix": only_fix,
        "differing": differing,
    }
    with open(out_path, "w") as out:
        json.dump(result, out, indent=1)
    print(json.dumps({k: v for k, v in result.items()}, indent=1)[:6000])


if __name__ == "__main__":
    main()
