# Z->ee tag-and-probe efficiency of the unseeded diphoton leg filters (photon TrigObj bits) on one NanoAOD file.
# Tag:   tight electron, pT > 35, |eta_SC| < 2.1, event fires HLT_Ele32_WPTight_Gsf, matched to the electron
#        WPTight trigger object AND to a photon trigger object with a seeded-leg bit (so the unseeded sequence ran).
# Probe: other loose electron, pT > 15, |eta_SC| < 2.5 outside 1.4442-1.566, opposite charge, 70 < m_ee < 110.
# Pass:  probe matched to a photon trigger object with the TrackIso (16), the R9 (17), or either unseeded bit;
#        "seeded" (either seeded-leg bit on the probe) is the control that the fix must leave unchanged.
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
SEEDED = ["hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter", "hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter"]
UNSEEDED = {"TrackIso": "hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter",
            "R9": "hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter"}
NUMERATORS = ["TrackIso", "R9", "either", "seeded"]
PT_BINS = [15, 20, 22, 25, 30, 35, 40, 50, 70, 100]
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


def main():
    # Total: time O(events * electrons^2 * nTrigObj), space O(events) for the arrays read
    nano_file, label, out_json, out_png = sys.argv[1:5]
    tree = uproot.open(nano_file)["Events"]
    bits = parse_bits(tree["TrigObj_filterBits"].title)
    ele_mask = 1 << bit_number(bits, "Electron", "1e (WPTight")
    seeded_mask = sum(1 << bit_number(bits, "Photon", name) for name in SEEDED)
    unseeded_mask = {key: 1 << bit_number(bits, "Photon", name) for key, name in UNSEEDED.items()}
    unseeded_mask["either"] = unseeded_mask["TrackIso"] | unseeded_mask["R9"]
    unseeded_mask["seeded"] = seeded_mask                     # - | control numerator, same matching
    print("bits: electron WPTight", ele_mask, "| seeded", seeded_mask, "| unseeded", unseeded_mask)

    branches = ["Electron_pt", "Electron_eta", "Electron_phi", "Electron_deltaEtaSC", "Electron_charge",
                "Electron_cutBased", "TrigObj_id", "TrigObj_eta", "TrigObj_phi", "TrigObj_filterBits", PATH]
    arrays = ak.to_list(tree.arrays(branches))                # list of dicts | one dict per event

    counts = {"events": len(arrays), "events_fired_path": 0, "tags": 0, "pairs_os": 0, "pairs_ss": 0}
    total_pt = [0] * (len(PT_BINS) - 1)
    total_eta = [0] * (len(ETA_BINS) - 1)
    passed = {k: 0 for k in NUMERATORS}
    passed_pt = {k: [0] * (len(PT_BINS) - 1) for k in NUMERATORS}
    passed_eta = {k: [0] * (len(ETA_BINS) - 1) for k in NUMERATORS}

    for ev in arrays:                                         # O(events) | event loop
        if not ev[PATH]:
            continue
        counts["events_fired_path"] += 1
        objects = list(zip(ev["TrigObj_id"], ev["TrigObj_eta"], ev["TrigObj_phi"], ev["TrigObj_filterBits"]))
        electrons = [{"pt": pt, "eta": eta, "phi": phi, "eta_sc": eta + deta, "charge": q, "cutBased": cb}
                     for pt, eta, phi, deta, q, cb in zip(ev["Electron_pt"], ev["Electron_eta"], ev["Electron_phi"],
                                                         ev["Electron_deltaEtaSC"], ev["Electron_charge"],
                                                         ev["Electron_cutBased"])]
        for i, tag in enumerate(electrons):                   # O(nEle) | every tag candidate
            if not is_tag(tag, objects, ele_mask, seeded_mask):
                continue
            counts["tags"] += 1
            for j, probe in enumerate(electrons):             # O(nEle) | every probe candidate
                if j == i or not is_probe(probe):
                    continue
                if not 70 < pair_mass(tag, probe) < 110:
                    continue
                if tag["charge"] == probe["charge"]:
                    counts["pairs_ss"] += 1                   # - | same-sign: background estimate only
                    continue
                counts["pairs_os"] += 1
                ipt = bin_index(probe["pt"], PT_BINS)
                ieta = bin_index(abs(probe["eta_sc"]), ETA_BINS)
                if ipt is not None:
                    total_pt[ipt] += 1
                if ieta is not None:
                    total_eta[ieta] += 1
                for key in NUMERATORS:                        # O(3) | three numerators
                    if matches(probe["eta"], probe["phi"], objects, 22, unseeded_mask[key]):
                        passed[key] += 1
                        if ipt is not None:
                            passed_pt[key][ipt] += 1
                        if ieta is not None:
                            passed_eta[key][ieta] += 1

    for key in NUMERATORS:                                    # - | sanity: numerator never exceeds denominator
        assert passed[key] <= counts["pairs_os"]
        assert all(p <= t for p, t in zip(passed_pt[key], total_pt))
    assert passed["either"] >= max(passed["TrackIso"], passed["R9"])

    result = {"label": label, "file": nano_file, "path": PATH, "counts": counts,
              "efficiency": {k: clopper_pearson(passed[k], counts["pairs_os"]) for k in NUMERATORS},
              "passed": passed, "pt_bins": PT_BINS, "eta_bins": ETA_BINS, "total_pt": total_pt, "total_eta": total_eta,
              "passed_pt": passed_pt, "passed_eta": passed_eta}
    json.dump(result, open(out_json, "w"), indent=1)
    print(json.dumps({"counts": counts, "passed": passed, "efficiency": result["efficiency"]}, indent=1))

    for name, edges, totals, passes in (("pt", PT_BINS, total_pt, passed_pt), ("eta", ETA_BINS, total_eta, passed_eta)):
        fig, ax = plt.subplots(figsize=(6, 4.5))
        for key in NUMERATORS:                                # O(bins) | one curve per numerator
            centers, values, low_err, high_err = [], [], [], []
            for k in range(len(edges) - 1):
                eff, low, high = clopper_pearson(passes[key][k], totals[k])
                if eff is None:
                    continue
                centers.append(0.5 * (edges[k] + edges[k + 1]))
                values.append(eff)
                low_err.append(eff - low)
                high_err.append(high - eff)
            ax.errorbar(centers, values, yerr=[low_err, high_err], fmt="o", label=key)
        ax.set_xlabel("probe electron pT [GeV]" if name == "pt" else "probe electron |eta_SC|")
        ax.set_ylabel("efficiency")
        ax.set_ylim(0, 1.1)
        ax.set_title(f"{label}: unseeded leg, Z->ee tag-and-probe")
        ax.legend()
        fig.tight_layout()
        fig.savefig(f"{out_png}_{name}.png", dpi=120)
    print("wrote", out_json, f"{out_png}_pt.png", f"{out_png}_eta.png")


if __name__ == "__main__":
    main()
