# Z->ee tag-and-probe efficiency of the unseeded diphoton leg filters (photon TrigObj bits) on one NanoAOD file,
# for each diphoton path family in LEGS (Diphoton30_22 Mass90/Mass95, Diphoton30_18 low mass).
# Tag:   tight electron, pT > 35, |eta_SC| < 2.1, event fires HLT_Ele32_WPTight_Gsf, matched to the electron
#        WPTight trigger object AND to a photon trigger object with a seeded-leg bit of that path family
#        (so its unseeded sequence ran).
# Probe: other loose electron, pT > 15, |eta_SC| < 2.5 outside 1.4442-1.566, opposite charge, 70 < m_ee < 110.
# Pass:  probe matched to a photon trigger object with an unseeded bit of that family ("either" = any of them);
#        "seeded" (a seeded bit of that family on the probe) is the control that the fix must leave unchanged.
# usage: python3 tnp_unseeded.py <nano file> <label> <output json> <output png prefix>
import json
import math
import re
import sys

import awkward as ak
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import uproot
from scipy.stats import beta

PATH = "HLT_Ele32_WPTight_Gsf"
LEGS = {                                                      # family -> seeded filters, unseeded filters by short name
    "30_22": {"seeded": ["hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter",
                         "hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter"],
              "unseeded": {"TrackIso": "hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter",
                           "R9": "hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter"}},
    "30_18": {"seeded": ["hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter"],
              "unseeded": {"TrackIso": "hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter"}},
}
PT_BINS = [15, 17, 18, 20, 22, 25, 30, 35, 40, 50, 70, 100]
ETA_BINS = [0.0, 0.8, 1.4442, 1.566, 2.0, 2.5]
MATCH_DR = 0.1
ELECTRON_MASS = 0.000511
CUTBASED_LOOSE, CUTBASED_TIGHT = 2, 4                         # Electron_cutBased: 0 fail, 1 veto, 2 loose, 3 medium, 4 tight


def parse_bits(title):
    # Map {object: {filter label: bit}} from the TrigObj_filterBits documentation string.
    # Total: time O(len(title)), space O(number of bits)
    bits = {}                                                 # dict of dicts | object -> label -> bit
    for block in re.findall(r"(.*?) for (\w+);", title):      # O(len) | one block per object type
        text, obj = block
        bits[obj] = {}
        for number, label in re.findall(r"(\d+) => ([^,]*?)(?=, \d+ => |$)", text):
            bits[obj][label.strip()] = int(number)
    return bits


def bit_number(bits, obj, prefix):
    # Total: time O(bits of obj), space O(1)
    found = [n for label, n in bits[obj].items() if label.startswith(prefix)]
    assert len(found) == 1, f"{obj} bit '{prefix}' found {len(found)} times"
    return found[0]


def leg_masks(bits, leg):
    # Bit masks of one path family: the seeded mask, and one mask per numerator.
    # Total: time O(bits), space O(1)
    seeded = sum(1 << bit_number(bits, "Photon", name) for name in leg["seeded"])
    numerators = {key: 1 << bit_number(bits, "Photon", name) for key, name in leg["unseeded"].items()}
    numerators["either"] = sum(numerators.values())
    numerators["seeded"] = seeded                             # - | control numerator, same matching
    return seeded, numerators


def delta_r(eta1, phi1, eta2, phi2):
    # Total: time O(1), space O(1)
    dphi = (phi1 - phi2 + math.pi) % (2 * math.pi) - math.pi  # - | wrap phi difference into [-pi, pi)
    return math.hypot(eta1 - eta2, dphi)


def matches(eta, phi, objects, obj_id, mask):
    # True if any trigger object of this id with any bit of `mask` lies within MATCH_DR.
    # Total: time O(trigger objects), space O(1)
    for o_id, o_eta, o_phi, o_bits in objects:                # O(nTrigObj) | linear scan
        if o_id == obj_id and (o_bits & mask) and delta_r(eta, phi, o_eta, o_phi) < MATCH_DR:
            return True
    return False


def pair_mass(e1, e2):
    # Total: time O(1), space O(1)
    def four_vector(e):
        px, py = e["pt"] * math.cos(e["phi"]), e["pt"] * math.sin(e["phi"])
        pz = e["pt"] * math.sinh(e["eta"])
        return math.sqrt(px * px + py * py + pz * pz + ELECTRON_MASS ** 2), px, py, pz
    a, b = four_vector(e1), four_vector(e2)
    m2 = (a[0] + b[0]) ** 2 - sum((a[i] + b[i]) ** 2 for i in (1, 2, 3))
    return math.sqrt(max(m2, 0.0))


def clopper_pearson(passed, total):
    # 68.3% central interval. Total: time O(1), space O(1)
    if total == 0:
        return None, None, None
    low = beta.ppf(0.1587, passed, total - passed + 1) if passed > 0 else 0.0
    high = beta.ppf(0.8413, passed + 1, total - passed) if passed < total else 1.0
    return passed / total, low, high


def bin_index(value, edges):
    # Total: time O(bins), space O(1)
    for i in range(len(edges) - 1):                           # O(bins) | linear search
        if edges[i] <= value < edges[i + 1]:
            return i
    return None


def is_tag(e, objects, ele_mask, seeded_mask):
    # Total: time O(nTrigObj), space O(1)
    if e["cutBased"] < CUTBASED_TIGHT or e["pt"] <= 35 or abs(e["eta_sc"]) >= 2.1:
        return False
    return matches(e["eta"], e["phi"], objects, 11, ele_mask) and matches(e["eta"], e["phi"], objects, 22, seeded_mask)


def is_probe(e):
    # Total: time O(1), space O(1)
    in_gap = 1.4442 <= abs(e["eta_sc"]) <= 1.566
    return e["cutBased"] >= CUTBASED_LOOSE and e["pt"] > 15 and abs(e["eta_sc"]) < 2.5 and not in_gap


def empty_counts(numerators):
    # Total: time O(numerators * bins), space O(numerators * bins)
    return {"tags": 0, "pairs_os": 0, "pairs_ss": 0,
            "passed": {k: 0 for k in numerators},
            "total_pt": [0] * (len(PT_BINS) - 1), "total_eta": [0] * (len(ETA_BINS) - 1),
            "passed_pt": {k: [0] * (len(PT_BINS) - 1) for k in numerators},
            "passed_eta": {k: [0] * (len(ETA_BINS) - 1) for k in numerators}}


def fill_leg(counts, electrons, objects, ele_mask, seeded_mask, numerators):
    # Tag-and-probe pairs of one event for one path family.
    # Total: time O(nEle^2 * nTrigObj), space O(1)
    for i, tag in enumerate(electrons):                       # O(nEle) | every tag candidate
        if not is_tag(tag, objects, ele_mask, seeded_mask):
            continue
        counts["tags"] += 1
        for j, probe in enumerate(electrons):                 # O(nEle) | every probe candidate
            if j == i or not is_probe(probe) or not 70 < pair_mass(tag, probe) < 110:
                continue
            if tag["charge"] == probe["charge"]:
                counts["pairs_ss"] += 1                       # - | same-sign: background estimate only
                continue
            counts["pairs_os"] += 1
            ipt = bin_index(probe["pt"], PT_BINS)
            ieta = bin_index(abs(probe["eta_sc"]), ETA_BINS)
            if ipt is not None:
                counts["total_pt"][ipt] += 1
            if ieta is not None:
                counts["total_eta"][ieta] += 1
            for key, mask in numerators.items():              # O(numerators) | one test per numerator
                if matches(probe["eta"], probe["phi"], objects, 22, mask):
                    counts["passed"][key] += 1
                    if ipt is not None:
                        counts["passed_pt"][key][ipt] += 1
                    if ieta is not None:
                        counts["passed_eta"][key][ieta] += 1


def check_leg(counts):
    # Sanity: numerators never exceed denominators; "either" covers each single bit.
    # Total: time O(numerators * bins), space O(1)
    for key, n in counts["passed"].items():
        assert n <= counts["pairs_os"], key
        assert all(p <= t for p, t in zip(counts["passed_pt"][key], counts["total_pt"])), key
        assert all(p <= t for p, t in zip(counts["passed_eta"][key], counts["total_eta"])), key
    singles = [n for key, n in counts["passed"].items() if key not in ("either", "seeded")]
    assert counts["passed"]["either"] >= max(singles)


def plot_leg(family, counts, label, out_png):
    # Per-file efficiency vs pT and |eta_SC| for one path family. Total: time O(numerators * bins), space O(bins)
    for name, edges in (("pt", PT_BINS), ("eta", ETA_BINS)):
        fig, ax = plt.subplots(figsize=(6, 4.5))
        for key in counts["passed"]:                          # O(numerators) | one curve per numerator
            points = [(0.5 * (edges[k] + edges[k + 1]),) + clopper_pearson(counts[f"passed_{name}"][key][k],
                                                                           counts[f"total_{name}"][k])
                      for k in range(len(edges) - 1) if counts[f"total_{name}"][k] > 0]
            ax.errorbar([p[0] for p in points], [p[1] for p in points],
                        yerr=[[p[1] - p[2] for p in points], [p[3] - p[1] for p in points]], fmt="o", label=key)
        ax.set_xlabel("probe electron pT [GeV]" if name == "pt" else "probe electron |eta_SC|")
        ax.set_ylabel("efficiency")
        ax.set_ylim(0, 1.1)
        ax.set_title(f"{label}: Diphoton{family} legs, Z->ee tag-and-probe")
        ax.legend()
        fig.tight_layout()
        fig.savefig(f"{out_png}_{family}_{name}.png", dpi=120)
        plt.close(fig)


def main():
    # Total: time O(events * families * electrons^2 * nTrigObj), space O(events) for the arrays read
    nano_file, label, out_json, out_png = sys.argv[1:5]
    tree = uproot.open(nano_file)["Events"]
    bits = parse_bits(tree["TrigObj_filterBits"].title)
    ele_mask = 1 << bit_number(bits, "Electron", "1e (WPTight")
    masks = {family: leg_masks(bits, leg) for family, leg in LEGS.items()}
    print("bits: electron WPTight", ele_mask, "| per family (seeded, numerators):", masks)

    branches = ["Electron_pt", "Electron_eta", "Electron_phi", "Electron_deltaEtaSC", "Electron_charge",
                "Electron_cutBased", "TrigObj_id", "TrigObj_eta", "TrigObj_phi", "TrigObj_filterBits", PATH]
    arrays = ak.to_list(tree.arrays(branches))                # list of dicts | one dict per event

    events_fired = 0
    legs = {family: empty_counts(masks[family][1]) for family in LEGS}
    for ev in arrays:                                         # O(events) | event loop
        if not ev[PATH]:
            continue
        events_fired += 1
        objects = list(zip(ev["TrigObj_id"], ev["TrigObj_eta"], ev["TrigObj_phi"], ev["TrigObj_filterBits"]))
        electrons = [{"pt": pt, "eta": eta, "phi": phi, "eta_sc": eta + deta, "charge": q, "cutBased": cb}
                     for pt, eta, phi, deta, q, cb in zip(ev["Electron_pt"], ev["Electron_eta"], ev["Electron_phi"],
                                                         ev["Electron_deltaEtaSC"], ev["Electron_charge"],
                                                         ev["Electron_cutBased"])]
        for family in LEGS:                                   # O(families) | each path family separately
            seeded_mask, numerators = masks[family]
            fill_leg(legs[family], electrons, objects, ele_mask, seeded_mask, numerators)

    for family in LEGS:
        check_leg(legs[family])
        legs[family]["efficiency"] = {k: clopper_pearson(n, legs[family]["pairs_os"])
                                      for k, n in legs[family]["passed"].items()}
        plot_leg(family, legs[family], label, out_png)

    result = {"label": label, "file": nano_file, "path": PATH, "events": len(arrays), "events_fired_path": events_fired,
              "pt_bins": PT_BINS, "eta_bins": ETA_BINS, "legs": legs}
    json.dump(result, open(out_json, "w"), indent=1)
    summary = {f: {k: legs[f][k] for k in ("tags", "pairs_os", "pairs_ss", "passed")} for f in LEGS}
    print(json.dumps({"events": len(arrays), "events_fired_path": events_fired, "legs": summary}, indent=1))


if __name__ == "__main__":
    main()
