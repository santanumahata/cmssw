#!/usr/bin/env python3
"""Empirical check of the dead unseeded-leg photon TrigObj bits in CMS NanoAOD files.

usage:
  python3 verify_nanoaod_files.py --label v13 --files root://cms-xrd-global.cern.ch//store/... [more files]
                                  [--max-events 300000] [--out results_v13.json]

For every file it reads the TrigObj_filterBits documentation (branch title) to find the bit numbers
of the relevant filters in THAT file (so v12 to v14 and v15 numbering are both handled), then counts:
  - events firing the diphoton paths (and the DoubleEle CaloIdL_MW paths, electron control),
  - photon trigger objects (id 22) with the seeded last-filter bits (expected > 0),
  - photon trigger objects with the unseeded last-filter bits (the claim: always 0 before the fix),
  - photon objects with the hltHtEcal800 bit (claim: always 0),
  - electron objects (id 11) with the "CaloIdL_MW unseeded" bit (control: > 0 from v13 on),
  - trigger objects per id (MET id 2 expected 0 in every version; BoostedTau id 1515 expected 0 in v12 to v14).
Needs python3 with uproot, awkward, numpy (LCG view or a CMSSW environment) and xrootd access for root:// files.
"""
import argparse, json, re, sys, time
import numpy as np
import awkward as ak
import uproot

UNSEEDED = {
    "TrackIsoUnseededLast": "hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter",
    "R9UnseededLast": "hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter",
    "EG18TrackIsoUnseeded": "hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter",
}
SEEDED = {
    "R9IdLast": "hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter",
    "EcalIsoLast": "hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter",
    "EG30EcalIso3018": "hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter",
}
HT_BIT = "hltHtEcal800"
ELE_UNSEEDED_DOC = "CaloIdL_MW unseeded"
PATHS = [
    "HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90",
    "HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass95",
    "HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId",
    "HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55",
    "HLT_DoubleEle33_CaloIdL_MW",
    "HLT_DoubleEle25_CaloIdL_MW",
]
IDS = {2: "MET", 11: "Electron", 22: "Photon", 13: "Muon", 15: "Tau", 1515: "BoostedTau", 1: "Jet", 6: "FatJet", 3: "HT", 4: "MHT"}


def parse_bitdoc(title):
    """'extra bits ...: 0 => a, 1 => b for Electron; 0 => c for Photon; ...' -> {object: {bit: doc}}"""
    out = {}
    body = title.split(":", 1)[1] if ":" in title else title
    for chunk in body.split("; "):
        m = re.search(r"\s+for\s+(\w+)\s*$", chunk.strip())
        if not m:
            continue
        obj, entries = m.group(1), chunk.strip()[: m.start()]
        d = {}
        for e in re.finditer(r"(\d+)\s*=>\s*(.*?)(?=,\s*\d+\s*=>|$)", entries):
            d[int(e.group(1))] = e.group(2).strip()
        out[obj] = d
    return out


def find_bit(docs, needle):
    for bit, doc in docs.items():
        if needle in doc:
            return bit
    return None


def has_bit(bits, bit):
    return ((bits >> np.uint64(bit)) & np.uint64(1)) == 1


def check_file(path, max_events):
    t0 = time.time()
    f = uproot.open(path)
    t = f["Events"]
    keys = set(t.keys())
    title = t["TrigObj_filterBits"].title
    dtype = str(t["TrigObj_filterBits"].interpretation)
    docs = parse_bitdoc(title)
    pho, ele = docs.get("Photon", {}), docs.get("Electron", {})
    bits_unseeded = {k: find_bit(pho, v) for k, v in UNSEEDED.items()}
    bits_seeded = {k: find_bit(pho, v) for k, v in SEEDED.items()}
    bit_ht = find_bit(pho, HT_BIT)
    bit_ele_unseeded = find_bit(ele, ELE_UNSEEDED_DOC)
    paths = [p for p in PATHS if p in keys]
    branches = ["TrigObj_id", "TrigObj_filterBits"] + paths
    res = {
        "file": path, "events": 0, "filterBits_dtype": dtype, "n_photon_bits_documented": len(pho),
        "bits_unseeded": bits_unseeded, "bits_seeded": bits_seeded, "bit_hltHtEcal800": bit_ht,
        "bit_electron_caloIdL_MW_unseeded": bit_ele_unseeded,
        "paths_present": paths, "fired": {p: 0 for p in paths},
        "objects_per_id": {}, "photon_objects_with_bit": {}, "events_fired_mass90_with_photon_bit": {},
        "electron_objects_with_unseeded_bit": 0,
    }
    allbits = {**{"unseeded:" + k: v for k, v in bits_unseeded.items()}, **{"seeded:" + k: v for k, v in bits_seeded.items()}, "hltHtEcal800": bit_ht}
    for name in allbits:
        res["photon_objects_with_bit"][name] = 0
        res["events_fired_mass90_with_photon_bit"][name] = 0
    main = "HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"
    nread = 0
    for arrays in t.iterate(branches, step_size="100 MB", entry_stop=max_events):
        n = len(arrays["TrigObj_id"])
        nread += n
        ids = arrays["TrigObj_id"]
        bits = ak.values_astype(arrays["TrigObj_filterBits"], np.uint64)
        flat_ids = ak.to_numpy(ak.flatten(ids))
        u, c = np.unique(flat_ids, return_counts=True)
        for i, k in zip(u.tolist(), c.tolist()):
            res["objects_per_id"][str(i)] = res["objects_per_id"].get(str(i), 0) + k
        for p in paths:
            res["fired"][p] += int(ak.sum(arrays[p]))
        isph = ids == 22
        fired_main = arrays[main] if main in keys else ak.zeros_like(arrays["TrigObj_id"][:, 0:0], dtype=bool)
        for name, bit in allbits.items():
            if bit is None:
                continue
            sel = isph & has_bit(bits, bit)
            res["photon_objects_with_bit"][name] += int(ak.sum(sel))
            if main in keys:
                res["events_fired_mass90_with_photon_bit"][name] += int(ak.sum(ak.any(sel, axis=1) & arrays[main]))
        if bit_ele_unseeded is not None:
            res["electron_objects_with_unseeded_bit"] += int(ak.sum((ids == 11) & has_bit(bits, bit_ele_unseeded)))
    res["events"] = nread
    res["seconds"] = round(time.time() - t0, 1)
    # verdict
    uns = [v for k, v in res["photon_objects_with_bit"].items() if k.startswith("unseeded:") and allbits[k] is not None]
    sed = [v for k, v in res["photon_objects_with_bit"].items() if k.startswith("seeded:") and allbits[k] is not None]
    if not any(b is not None for b in bits_unseeded.values()):
        res["verdict"] = "diphoton unseeded bits not documented in this file (NanoAOD v11 or older): not affected"
    elif sum(sed) > 0 and sum(uns) == 0:
        res["verdict"] = "BUG REPRODUCED: seeded last-filter bits set %d times, unseeded last-filter bits never set" % sum(sed)
    elif sum(uns) > 0:
        res["verdict"] = "UNEXPECTED: unseeded bits set %d times (fixed file, or claim wrong: report this)" % sum(uns)
    else:
        res["verdict"] = "INCONCLUSIVE: no object with the seeded diphoton bits either (too few diphoton-triggered events?)"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="NanoAOD version label, e.g. v13")
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--max-events", type=int, default=300000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    results = []
    for p in a.files:
        print("==", a.label, p, flush=True)
        try:
            r = check_file(p, a.max_events)
        except Exception as e:  # keep going, record the failure
            r = {"file": p, "error": repr(e)}
        results.append(r)
        print(json.dumps({k: v for k, v in r.items() if k not in ("file",)}, indent=1), flush=True)
    out = a.out or "results_%s.json" % a.label
    json.dump({"label": a.label, "results": results}, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
