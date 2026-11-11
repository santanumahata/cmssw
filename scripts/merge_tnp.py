# Sum tag-and-probe JSONs of several files (same binning) into one JSON with the same layout.
# usage: python3 merge_tnp.py <label> <output json> <input json> [<input json> ...]
import json
import sys

from scipy.stats import beta

SUMMED = ["tags", "pairs_os", "pairs_ss"]
SUMMED_LISTS = ["total_pt", "total_eta"]
SUMMED_DICTS = ["passed"]
SUMMED_DICT_LISTS = ["passed_pt", "passed_eta"]


def clopper_pearson(passed, total):
    # 68.3% central interval. Total: time O(1), space O(1)
    if total == 0:
        return None, None, None
    low = beta.ppf(0.1587, passed, total - passed + 1) if passed > 0 else 0.0
    high = beta.ppf(0.8413, passed + 1, total - passed) if passed < total else 1.0
    return passed / total, low, high


def add_leg(total, leg):
    # Add one file's counts of one path family into the running total. Total: time O(numerators * bins), space O(1)
    for key in SUMMED:
        total[key] += leg[key]
    for key in SUMMED_LISTS:
        total[key] = [a + b for a, b in zip(total[key], leg[key])]
    for key in SUMMED_DICTS:
        for num in total[key]:
            total[key][num] += leg[key][num]
    for key in SUMMED_DICT_LISTS:
        for num in total[key]:
            total[key][num] = [a + b for a, b in zip(total[key][num], leg[key][num])]
    if "pairs" in total:                                      # - | MINIAOD JSONs: per-pair list, concatenated
        total["pairs"] += leg["pairs"]


def main():
    # Total: time O(files * numerators * bins), space O(numerators * bins)
    label, out_json = sys.argv[1:3]
    inputs = [json.load(open(path)) for path in sys.argv[3:]]
    first = inputs[0]
    merged = {"label": label, "files": [r["file"] for r in inputs], "path": first["path"],
              "events": 0, "events_fired_path": 0, "pt_bins": first["pt_bins"], "eta_bins": first["eta_bins"],
              "legs": json.loads(json.dumps(first["legs"]))}  # - | deep copy of the first file as starting point
    for result in inputs:                                     # O(files) | check binning, add events
        assert result["pt_bins"] == first["pt_bins"] and result["eta_bins"] == first["eta_bins"], result["file"]
        merged["events"] += result["events"]
        merged["events_fired_path"] += result["events_fired_path"]
    for result in inputs[1:]:                                 # O(files) | add every further file
        for family, leg in result["legs"].items():
            add_leg(merged["legs"][family], leg)
    for leg in merged["legs"].values():                       # - | efficiencies from the summed counts
        leg["efficiency"] = {k: clopper_pearson(n, leg["pairs_os"]) for k, n in leg["passed"].items()}
    json.dump(merged, open(out_json, "w"), indent=1)
    print(len(inputs), "files,", merged["events"], "events")
    for family, leg in merged["legs"].items():
        print(family, "pairs_os", leg["pairs_os"], "pairs_ss", leg["pairs_ss"], "passed", leg["passed"])


if __name__ == "__main__":
    main()
