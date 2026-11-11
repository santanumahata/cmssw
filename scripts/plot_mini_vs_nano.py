# Overlay the tag-and-probe efficiencies measured on MINIAOD (tnp_miniaod.py, filter labels) and on the fixed
# NanoAOD made from the same files (tnp_unseeded.py, filterBits) for one diphoton path family:
# unseeded leg (either unseeded filter) and seeded leg (control).
# usage: python3 plot_mini_vs_nano.py <fixed nano json> <miniaod json> <family, e.g. 30_22> <title> <output png>
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import beta

SERIES = [                                                    # (json, numerator, legend, marker, colour)
    ("mini", "either", "unseeded leg, MiniAOD", "o", "#C2410C"),
    ("nano", "either", "unseeded leg, fixed NanoAOD", "s", "#176B7B"),
    ("mini", "seeded", "seeded leg, MiniAOD", "^", "#7A7A7A"),
    ("nano", "seeded", "seeded leg, fixed NanoAOD", "x", "#16213A"),
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
    nano_file, mini_file, family, title, out_png = sys.argv[1:6]
    results = {"nano": json.load(open(nano_file)), "mini": json.load(open(mini_file))}
    for key in ("tags", "pairs_os", "pairs_ss", "total_pt", "total_eta"):
        nano, mini = results["nano"]["legs"][family][key], results["mini"]["legs"][family][key]
        print(f"{family} {key}: nano {nano} mini {mini}" + ("" if nano == mini else "  DIFFERENT"))
    for key in ("either", "either_pt15", "seeded", "seeded_pt15"):
        leg = results["mini"]["legs"][family]
        print(f"{family} mini {key}: {leg['passed'][key]} / {leg['pairs_os']}")
    for key in ("either", "seeded"):
        leg = results["nano"]["legs"][family]
        print(f"{family} nano {key}: {leg['passed'][key]} / {leg['pairs_os']}")

    fig, axes = plt.subplots(2, 2, figsize=(11, 5.4), sharex="col", gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05})
    for col, variable, xlabel in ((0, "pt", "probe electron $p_T$ [GeV]"), (1, "eta", "probe electron $|\\eta_{SC}|$")):
        ax, rax = axes[0][col], axes[1][col]
        for which, numerator, legend, marker, colour in SERIES:   # O(4) | one curve per series
            points = curve(results[which], family, numerator, variable)
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            errors = [[p[2] for p in points], [p[3] for p in points]]
            mini = which == "mini"
            ax.errorbar(x, y, yerr=errors, fmt=marker, color=colour, label=legend, markersize=8 if mini else 4,
                        capsize=2, fillstyle="none" if mini else "full", zorder=3 if mini else 2)
        for numerator, colour, marker in (("either", "#C2410C", "o"), ("seeded", "#7A7A7A", "^")):   # O(2) | ratio
            mini = {p[0]: p[1] for p in curve(results["mini"], family, numerator, variable)}
            nano = {p[0]: p[1] for p in curve(results["nano"], family, numerator, variable)}
            x = [c for c in mini if c in nano and nano[c] > 0]
            rax.plot(x, [mini[c] / nano[c] for c in x], marker, color=colour, fillstyle="none", markersize=6)
        rax.axhline(1.0, color="#16213A", linewidth=0.8)
        rax.set_ylim(0.99, 1.01)
        rax.set_ylabel("MiniAOD /\nfixed NanoAOD", fontsize=8)
        rax.set_xlabel(xlabel)
        rax.grid(alpha=0.3)
        ax.set_ylabel("efficiency")
        ax.set_ylim(-0.03, 1.1)
        ax.grid(alpha=0.3)
    axes[0][0].legend(loc="lower right", fontsize=8)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    print("wrote", out_png)


if __name__ == "__main__":
    main()
