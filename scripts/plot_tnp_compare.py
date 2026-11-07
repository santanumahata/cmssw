# Overlay the tag-and-probe efficiencies without and with the fix for one diphoton path family:
# unseeded leg (either unseeded bit) and seeded leg (control).
# usage: python3 plot_tnp_compare.py <nofix json> <fix json> <family, e.g. 30_22> <title> <output png>
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import beta

SERIES = [                                                    # (json, numerator, legend, marker, colour)
    ("nofix", "either", "unseeded leg, no fix", "o", "#C2410C"),
    ("fix", "either", "unseeded leg, with fix", "s", "#176B7B"),
    ("nofix", "seeded", "seeded leg, no fix", "^", "#7A7A7A"),
    ("fix", "seeded", "seeded leg, with fix", "x", "#16213A"),
]


def clopper_pearson(passed, total):
    # 68.3% central interval. Total: time O(1), space O(1)
    low = beta.ppf(0.1587, passed, total - passed + 1) if passed > 0 else 0.0
    high = beta.ppf(0.8413, passed + 1, total - passed) if passed < total else 1.0
    return passed / total, low, high


def curve(result, family, numerator, variable):
    # Points (bin centre, efficiency, lower error, upper error) for bins with probes.
    # Total: time O(bins), space O(bins)
    edges = result[f"{variable}_bins"]
    leg = result["legs"][family]
    totals = leg[f"total_{variable}"]
    passes = leg[f"passed_{variable}"][numerator]
    points = []                                               # list | one tuple per non-empty bin
    for k in range(len(edges) - 1):                           # O(bins) | bin loop
        if totals[k] == 0:
            continue
        eff, low, high = clopper_pearson(passes[k], totals[k])
        points.append((0.5 * (edges[k] + edges[k + 1]), eff, eff - low, high - eff))
    return points


def main():
    # Total: time O(series * bins), space O(bins)
    nofix_file, fix_file, family, title, out_png = sys.argv[1:6]
    results = {"nofix": json.load(open(nofix_file)), "fix": json.load(open(fix_file))}
    for key in ("tags", "pairs_os", "pairs_ss", "total_pt", "total_eta"):
        assert results["nofix"]["legs"][family][key] == results["fix"]["legs"][family][key], \
            f"nofix and fix differ in {key}: they must have the same tags and probes"

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, variable, xlabel in ((axes[0], "pt", "probe electron $p_T$ [GeV]"), (axes[1], "eta", "probe electron $|\\eta_{SC}|$")):
        for which, numerator, legend, marker, colour in SERIES:   # O(4) | one curve per series
            points = curve(results[which], family, numerator, variable)
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            errors = [[p[2] for p in points], [p[3] for p in points]]
            ax.errorbar(x, y, yerr=errors, fmt=marker, color=colour, label=legend, markersize=5, capsize=2)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("efficiency")
        ax.set_ylim(-0.03, 1.1)
        ax.grid(alpha=0.3)
    axes[0].legend(loc="center right", fontsize=8)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    print("wrote", out_png)


if __name__ == "__main__":
    main()
