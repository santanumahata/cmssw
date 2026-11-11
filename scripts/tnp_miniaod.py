# Z->ee tag-and-probe cut-and-count efficiency of the diphoton leg filters on one MINIAOD file, as the reference
# for scripts/tnp_unseeded.py on the fixed NanoAOD made from the same file. Same tag, probe and pair cuts;
# trigger matching by filter label in slimmedPatTrigger instead of TrigObj filterBits.
# Tag:   RunIIIWinter22-V1 tight electron, pT > 35, |eta_SC| < 2.1, event fires HLT_Ele32_WPTight_Gsf_v*, matched to
#        a trigger object passing the NanoAOD electron TrigObj selection with an hltEle*WPTight*TrackIsoFilter* label,
#        AND to one passing the NanoAOD photon TrigObj selection with a seeded-leg label of that path family.
# Probe: other RunIIIWinter22-V1 loose electron, pT > 15, |eta_SC| < 2.5 outside 1.4442-1.566, opposite charge,
#        70 < m_ee < 110.
# Pass:  probe within dR < 0.1 of a trigger object with an unseeded label of that family ("either" = any of them);
#        "seeded" is the control. Each numerator twice: raw (label only) and "_pt15" (label and trigger object
#        pT > 15, the NanoAOD photon TrigObj cut).
# Electron pT is the MINIAOD pT: NanoAOD applies its energy calibration to Electron_pt only for run2_egamma.
# Optional 4th argument "nanoprec": round electron and trigger-object eta, phi (and deltaEtaSC) to the mantissa bits
# NanoAOD stores (electrons_cff.py, common_cff.py, TriggerObjectTableProducer.cc in CMSSW_13_3_1_patch1) before any cut.
# usage (cmsenv, CMSSW_13_3_1_patch1): python3 tnp_miniaod.py <miniaod file> <label> <output json> [nanoprec]
import fnmatch
import json
import math
import struct
import sys

import ROOT
from DataFormats.FWLite import Events, Handle

PATH_PREFIX = "HLT_Ele32_WPTight_Gsf_v"
LEGS = {                                                      # same filters as LEGS in tnp_unseeded.py
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
ID_LOOSE, ID_TIGHT = "cutBasedElectronID-RunIIIWinter22-V1-loose", "cutBasedElectronID-RunIIIWinter22-V1-tight"
EG_COLLECTIONS = ("hltEgammaCandidates", "hltEgammaCandidatesUnseeded")


def float32(f):
    # Total: time O(1), space O(1)
    return struct.unpack("f", struct.pack("f", f))[0]


def reduce_mantissa(f, bits):
    # Python copy of ReduceMantissaToNbitsRounding (DataFormats/Math/interface/libminifloat.h).
    # Total: time O(1), space O(1)
    shift = 23 - bits
    mask = ((0xFFFFFFFF >> shift) << shift) & 0xFFFFFFFF
    test, maxn = 1 << (shift - 1), (1 << bits) - 2
    i32 = struct.unpack("I", struct.pack("f", f))[0]
    if i32 & test:                                            # - | need to round
        mantissa = (i32 & 0x007FFFFF) >> shift
        if mantissa < maxn:
            mantissa += 1
        i32 = (i32 & 0xFF800000) | (mantissa << shift)
    else:
        i32 &= mask
    return struct.unpack("f", struct.pack("I", i32))[0]


def delta_r(eta1, phi1, eta2, phi2):
    # Total: time O(1), space O(1)
    dphi = (phi1 - phi2 + math.pi) % (2 * math.pi) - math.pi  # - | wrap phi difference into [-pi, pi)
    return math.hypot(eta1 - eta2, dphi)


def pair_mass(e1, e2):
    # Total: time O(1), space O(1)
    def four_vector(e):
        px, py = e["pt"] * math.cos(e["phi"]), e["pt"] * math.sin(e["phi"])
        pz = e["pt"] * math.sinh(e["eta"])
        return math.sqrt(px * px + py * py + pz * pz + ELECTRON_MASS ** 2), px, py, pz
    a, b = four_vector(e1), four_vector(e2)
    m2 = (a[0] + b[0]) ** 2 - sum((a[i] + b[i]) ** 2 for i in (1, 2, 3))
    return math.sqrt(max(m2, 0.0))


def bin_index(value, edges):
    # Total: time O(bins), space O(1)
    for i in range(len(edges) - 1):                           # O(bins) | linear search
        if edges[i] <= value < edges[i + 1]:
            return i
    return None


def unpack_objects(objs, event, results, nanoprec):
    # Trigger objects as plain dicts with the flags the selections need.
    # Total: time O(nObj * labels), space O(nObj * labels)
    rnd = (lambda x: reduce_mantissa(x, 12)) if nanoprec else (lambda x: x)
    out = []
    for obj in objs:                                          # O(nObj) | one unpack per object
        obj.unpackNamesAndLabels(event.object(), results)
        labels = set(str(l) for l in obj.filterLabels())
        eg = obj.type(92) and any(obj.hasCollection(c) for c in EG_COLLECTIONS)
        nano_ele = (eg and obj.pt() > 7 and any(fnmatch.fnmatch(l, "*PixelMatchFilter") or
                                                fnmatch.fnmatch(l, "*PixelMatchUnseededFilter") for l in labels))
        out.append({"eta": rnd(obj.eta()), "phi": rnd(obj.phi()), "pt": obj.pt(), "labels": labels,
                    "wptight": nano_ele and any(fnmatch.fnmatch(l, "hltEle*WPTight*TrackIsoFilter*") for l in labels),
                    "nano_pho": eg and obj.pt() > 15})        # - | fixed NanoAOD photon TrigObj selection
    return out


def matches(e, objects, test):
    # True if any trigger object passing `test` lies within MATCH_DR. Total: time O(nObj), space O(1)
    return any(test(o) and delta_r(e["eta"], e["phi"], o["eta"], o["phi"]) < MATCH_DR for o in objects)


def numerator_tests(leg):
    # {numerator name: test on a trigger object}, raw and _pt15. Total: time O(filters), space O(filters)
    sets = {key: {name} for key, name in leg["unseeded"].items()}
    sets["either"] = set(leg["unseeded"].values())
    sets["seeded"] = set(leg["seeded"])
    tests = {}
    for key, names in sets.items():
        tests[key] = lambda o, names=names: bool(o["labels"] & names)
        tests[key + "_pt15"] = lambda o, names=names: bool(o["labels"] & names) and o["pt"] > 15
    return tests


def is_tag(e, objects, seeded):
    # Total: time O(nObj), space O(1)
    if not e["tight"] or e["pt"] <= 35 or abs(e["eta_sc"]) >= 2.1:
        return False
    return (matches(e, objects, lambda o: o["wptight"]) and
            matches(e, objects, lambda o: o["nano_pho"] and bool(o["labels"] & seeded)))


def is_probe(e):
    # Total: time O(1), space O(1)
    in_gap = 1.4442 <= abs(e["eta_sc"]) <= 1.566
    return e["loose"] and e["pt"] > 15 and abs(e["eta_sc"]) < 2.5 and not in_gap


def empty_counts(tests):
    # Same layout as tnp_unseeded.py, plus the list of probe pairs. Total: time O(tests * bins), space O(same)
    return {"tags": 0, "pairs_os": 0, "pairs_ss": 0,
            "passed": {k: 0 for k in tests},
            "total_pt": [0] * (len(PT_BINS) - 1), "total_eta": [0] * (len(ETA_BINS) - 1),
            "passed_pt": {k: [0] * (len(PT_BINS) - 1) for k in tests},
            "passed_eta": {k: [0] * (len(ETA_BINS) - 1) for k in tests},
            "pairs": []}


def fill_leg(counts, eid, electrons, objects, seeded, tests):
    # Tag-and-probe pairs of one event for one path family. Total: time O(nEle^2 * nObj * tests), space O(1)
    for i, tag in enumerate(electrons):                       # O(nEle) | every tag candidate
        if not is_tag(tag, objects, seeded):
            continue
        counts["tags"] += 1
        for j, probe in enumerate(electrons):                 # O(nEle) | every probe candidate
            if j == i or not is_probe(probe) or not 70 < pair_mass(tag, probe) < 110:
                continue
            if tag["charge"] == probe["charge"]:
                counts["pairs_ss"] += 1                       # - | same-sign: background estimate only
                continue
            counts["pairs_os"] += 1
            ipt, ieta = bin_index(probe["pt"], PT_BINS), bin_index(abs(probe["eta_sc"]), ETA_BINS)
            if ipt is not None:
                counts["total_pt"][ipt] += 1
            if ieta is not None:
                counts["total_eta"][ieta] += 1
            passed = []
            for key, test in tests.items():                   # O(tests) | one match per numerator
                if matches(probe, objects, test):
                    passed.append(key)
                    counts["passed"][key] += 1
                    if ipt is not None:
                        counts["passed_pt"][key][ipt] += 1
                    if ieta is not None:
                        counts["passed_eta"][key][ieta] += 1
            counts["pairs"].append(list(eid) + [round(probe["pt"], 3), round(probe["eta_sc"], 4), passed])


def check_leg(counts):
    # Numerators never exceed denominators; "either" covers each single filter; _pt15 never exceeds raw.
    # Total: time O(tests * bins), space O(1)
    passed = counts["passed"]
    for key, n in passed.items():
        assert n <= counts["pairs_os"], key
        assert all(p <= t for p, t in zip(counts["passed_pt"][key], counts["total_pt"])), key
        assert all(p <= t for p, t in zip(counts["passed_eta"][key], counts["total_eta"])), key
        if key.endswith("_pt15"):
            assert n <= passed[key[:-5]], key
    singles = [n for key, n in passed.items() if key.split("_pt15")[0] not in ("either", "seeded")
               and not key.endswith("_pt15")]
    assert passed["either"] >= max(singles)


def main():
    # Total: time O(events * families * (nObj * labels + nEle^2 * nObj * tests)), space O(pairs)
    mini_file, label, out_json = sys.argv[1:4]
    nanoprec = sys.argv[4:5] == ["nanoprec"]
    events = Events(mini_file)
    h_ele = Handle("std::vector<pat::Electron>")
    h_obj = Handle("std::vector<pat::TriggerObjectStandAlone>")
    h_res = Handle("edm::TriggerResults")
    tests = {family: numerator_tests(leg) for family, leg in LEGS.items()}
    legs = {family: empty_counts(tests[family]) for family in LEGS}

    n_events = events_fired = 0
    for event in events:                                      # O(events) | event loop
        n_events += 1
        event.getByLabel(("TriggerResults", "", "HLT"), h_res)
        results = h_res.product()
        names = event.object().triggerNames(results)
        fired = any(names.triggerName(k).startswith(PATH_PREFIX) and results.accept(k) for k in range(names.size()))
        if not fired:
            continue
        events_fired += 1
        event.getByLabel("slimmedPatTrigger", h_obj)
        objects = unpack_objects(h_obj.product(), event, results, nanoprec)
        event.getByLabel("slimmedElectrons", h_ele)
        electrons = []
        for e in h_ele.product():                             # O(nEle) | one dict per electron
            if nanoprec:                                      # - | as stored in NanoAOD, eta_sc = eta + deltaEtaSC
                eta, deta = reduce_mantissa(e.eta(), 12), reduce_mantissa(e.superCluster().eta() - e.eta(), 10)
                kin = {"pt": float32(e.pt()), "eta": eta, "phi": reduce_mantissa(e.phi(), 12), "eta_sc": eta + deta}
            else:
                kin = {"pt": e.pt(), "eta": e.eta(), "phi": e.phi(), "eta_sc": e.superCluster().eta()}
            kin.update({"charge": e.charge(), "loose": e.electronID(ID_LOOSE) > 0.5,
                        "tight": e.electronID(ID_TIGHT) > 0.5})
            electrons.append(kin)
        aux = event.eventAuxiliary()
        eid = (aux.run(), aux.luminosityBlock(), aux.event())
        for family, leg in LEGS.items():                      # O(families) | each path family separately
            fill_leg(legs[family], eid, electrons, objects, set(leg["seeded"]), tests[family])

    for family in LEGS:
        check_leg(legs[family])
    result = {"label": label, "file": mini_file, "path": PATH_PREFIX + "*", "events": n_events,
              "events_fired_path": events_fired, "pt_bins": PT_BINS, "eta_bins": ETA_BINS, "legs": legs}
    json.dump(result, open(out_json, "w"), indent=1)
    summary = {f: {k: legs[f][k] for k in ("tags", "pairs_os", "pairs_ss", "passed")} for f in LEGS}
    print(json.dumps({"events": n_events, "events_fired_path": events_fired, "legs": summary}, indent=1))


if __name__ == "__main__":
    main()
