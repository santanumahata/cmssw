#!/usr/bin/env python3
"""Count TrigObj filter bits of the Diphoton30_22 photon legs in one NanoAOD file.

Bit numbers are parsed from the TrigObj_filterBits branch documentation, never hardcoded.
Usage: python3 measure_trigobj.py <version> <dataset> <file> <out.json> [<reference file>]
With a reference file, events are matched by (run, lumi, event) and their TrigObj content compared.
"""
import json
import re
import sys

import awkward as ak
import numpy as np
import uproot

MAX_EVENTS = 300000
PATH_MASS90 = "HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90"
PATH_DIELE = "HLT_DoubleEle33_CaloIdL_MW"
PHOTON_FILTERS = {
    "R9UnseededLast": "hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter",
    "TrackIsoUnseededLast": "hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter",
    "EG18Unseeded": "hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter",
    "seeded_R9IdLast": "hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter",
    "seeded_EcalIsoLast": "hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter",
    "hltHtEcal800": "hltHtEcal800",
}
SEEDED = ("seeded_R9IdLast", "seeded_EcalIsoLast")
UNSEEDED = ("R9UnseededLast", "TrackIsoUnseededLast", "EG18Unseeded")
EXPECTED_PHOTON_BIT_COUNTS = (0, 12, 18, 21)
BIT_ENTRY = re.compile(r"(\d+)\s*=>\s*(.*?)(?=,\s*\d+\s*=>|\s+for\s+\w+\s*$)")
EVENT_COLUMNS = ["run", "luminosityBlock", "event", "TrigObj_id", "TrigObj_filterBits", "TrigObj_pt"]


def bits_of(doc, obj):
    # Total: time O(len(doc)), space O(n_bits)
    bits = {}
    for chunk in doc.split("; "):                               # list scan O(len) | each per-object chunk
        if not chunk.strip().endswith(" for " + obj):          # -                | keep only this object's chunk
            continue
        for match in BIT_ENTRY.finditer(chunk):                # regex O(len)     | each "N => description"
            bits[int(match.group(1))] = match.group(2).strip()  # dict insert O(1) | bit -> description
    return bits


def find_bit(bits, name):
    # Total: time O(n_bits), space O(1)
    for bit, description in bits.items():                      # dict scan O(n)   | first bit naming the filter
        if name in description:                                # substring O(len) | description contains name
            return bit
    return None


def has_bit(filter_bits, bit):
    # Total: time O(n_obj), space O(n_obj)
    shifted = filter_bits >> np.uint64(bit)                    # jagged op O(n)   | move bit to position 0
    return (shifted & np.uint64(1)) == 1                       # jagged op O(n)   | per-object bit set?


def count_objects(ids, filter_bits, object_id, bit, event_mask=None):
    # Total: time O(n_obj), space O(n_obj)
    if bit is None:
        return None
    selected = (ids == object_id) & has_bit(filter_bits, bit)  # jagged mask O(n) | objects of this id with bit
    if event_mask is not None:
        selected = selected & event_mask                       # broadcast O(n)   | only in chosen events
    return int(ak.sum(selected))                               # reduction O(n)   | number of objects


def bit_counts_per_id(ids, filter_bits, n_bits, skip_id):
    # Total: time O(n_obj * n_bits), space O(n_obj)
    flat_ids = ak.to_numpy(ak.flatten(ids))                    # array O(n)       | all object ids
    flat_bits = ak.to_numpy(ak.flatten(filter_bits))           # array O(n)       | all object bit words
    counts = {}
    for object_id in np.unique(flat_ids):                      # sort O(n log n)  | each object type
        if object_id == skip_id:
            continue
        words = flat_bits[flat_ids == object_id]               # mask O(n)        | bit words of this type
        per_bit = [int(((words >> np.uint64(b)) & np.uint64(1)).sum()) for b in range(n_bits)]
        counts[str(int(object_id))] = {str(b): c for b, c in enumerate(per_bit) if c > 0}
    return counts


def event_contents(arrays, skip_id=None):
    # Total: time O(n_obj log n_obj), space O(n_obj)
    contents = {}
    rows = zip(arrays["run"], arrays["luminosityBlock"], arrays["event"],
               ak.to_list(arrays["TrigObj_id"]), ak.to_list(arrays["TrigObj_filterBits"]),
               ak.to_list(arrays["TrigObj_pt"]))
    for run, lumi, event, ids, words, pts in rows:             # loop O(n_events) | one event at a time
        objects = [(i, int(w) & 0xFFFFFFFFFFFFFFFF, p) for i, w, p in zip(ids, words, pts) if i != skip_id]
        contents[(int(run), int(lumi), int(event))] = sorted(objects)  # dict O(1)  | key -> sorted objects
    return contents


def compare_with_reference(arrays, reference_url):
    # Total: time O(n_obj log n_obj), space O(n_obj)
    reference = uproot.open(reference_url)["Events"].arrays(EVENT_COLUMNS, entry_stop=MAX_EVENTS)
    this_all, ref_all = event_contents(arrays), event_contents(reference)
    this_other, ref_other = event_contents(arrays, skip_id=22), event_contents(reference, skip_id=22)
    common = set(this_all) & set(ref_all)                      # set join O(n)    | events in both files
    identical_all = sum(1 for k in common if this_all[k] == ref_all[k])
    identical_other = sum(1 for k in common if this_other[k] == ref_other[k])
    return {
        "reference_file": reference_url,
        "events_in_reference": len(ref_all),
        "events_in_common": len(common),
        "events_identical_all_TrigObj": identical_all,
        "events_identical_TrigObj_without_id22": identical_other,
    }


def main():
    # Total: time O(n_events * n_obj), space O(n_events * n_obj)
    version, dataset, url, out_path = sys.argv[1:5]
    reference_url = sys.argv[5] if len(sys.argv) > 5 else None
    root_file = uproot.open(url)
    tree = root_file["Events"]
    branch = tree["TrigObj_filterBits"]
    doc = branch.title
    photon_bits = bits_of(doc, "Photon")                       # dict             | photon bit -> name
    electron_bits = bits_of(doc, "Electron")                   # dict             | electron bit -> name
    bit = {key: find_bit(photon_bits, name) for key, name in PHOTON_FILTERS.items()}
    electron_bit = find_bit(electron_bits, "CaloIdL_MW unseeded")
    n_bits = 64 if "u8" in str(branch.interpretation) else 32

    paths = [p for p in (PATH_MASS90, PATH_DIELE) if p in tree.keys()]
    arrays = tree.arrays(EVENT_COLUMNS + paths, entry_stop=MAX_EVENTS)  # columnar read | up to 300k events
    ids = arrays["TrigObj_id"]
    filter_bits = ak.values_astype(arrays["TrigObj_filterBits"], np.uint64)
    n_events = len(ids)
    assert n_events > 0, "no events read"

    fired = arrays[PATH_MASS90] if PATH_MASS90 in paths else None
    n_fired = int(ak.sum(fired)) if fired is not None else None

    photons_with_bit = {key: count_objects(ids, filter_bits, 22, b) for key, b in bit.items()}
    photons_with_bit_fired = {key: count_objects(ids, filter_bits, 22, b, fired) if fired is not None else None
                              for key, b in bit.items()}

    unseeded_any = ak.zeros_like(ids, dtype=bool)              # jagged bool O(n) | photon has any unseeded bit
    for key in UNSEEDED:
        if bit[key] is not None:
            unseeded_any = unseeded_any | ((ids == 22) & has_bit(filter_bits, bit[key]))
    offending = ak.any(unseeded_any, axis=1)                   # reduction O(n)   | events with such a photon
    offending_events = [[int(r), int(l), int(e)] for r, l, e in zip(arrays["run"][offending][:50],
                        arrays["luminosityBlock"][offending][:50], arrays["event"][offending][:50])]

    unseeded_pt = ak.to_numpy(ak.flatten(arrays["TrigObj_pt"][unseeded_any]))  # array O(n) | pt of those objects
    photons_per_event = ak.sum(ids == 22, axis=1)              # reduction O(n)   | photon objects per event
    n_fired_with_unseeded = int(ak.sum(offending & fired)) if fired is not None else None

    flat_ids = ak.to_numpy(ak.flatten(ids))
    unique_ids, counts = np.unique(flat_ids, return_counts=True)  # sort O(n log n) | objects per id
    objects_per_id = {int(i): int(c) for i, c in zip(unique_ids, counts)}

    result = {
        "version": version,
        "dataset": dataset,
        "file": url,
        "file_size_bytes": getattr(root_file.file.source, "num_bytes", None),
        "events_in_file": int(tree.num_entries),
        "events_read": n_events,
        "filterBits_interpretation": str(branch.interpretation),
        "n_photon_bits_documented": len(photon_bits),
        "n_electron_bits_documented": len(electron_bits),
        "photon_bit_numbers": bit,
        "electron_CaloIdL_MW_unseeded_bit": electron_bit,
        "paths_present": paths,
        "fired_Mass90": n_fired,
        "fired_DoubleEle33_CaloIdL_MW": int(ak.sum(arrays[PATH_DIELE])) if PATH_DIELE in paths else None,
        "photons_with_bit": photons_with_bit,
        "photons_with_bit_in_Mass90_events": photons_with_bit_fired,
        "electrons_with_CaloIdL_MW_unseeded_bit": count_objects(ids, filter_bits, 11, electron_bit),
        "objects_per_id": objects_per_id,
        "n_id2_MET": objects_per_id.get(2, 0),
        "n_id1515_BoostedTau": objects_per_id.get(1515, 0),
        "n_id22_Photon": objects_per_id.get(22, 0),
        "events_with_unseeded_photon_bit": int(ak.sum(offending)),
        "first_offending_run_lumi_event": offending_events,
        "Mass90_events_with_unseeded_photon_bit": n_fired_with_unseeded,
        "fraction_Mass90_events_with_unseeded_photon_bit":
            n_fired_with_unseeded / n_fired if n_fired else None,
        "photons_per_Mass90_event_mean": float(ak.mean(photons_per_event[fired])) if n_fired else None,
        "unseeded_photon_pt": {
            "n": int(len(unseeded_pt)),
            "min": float(unseeded_pt.min()) if len(unseeded_pt) else None,
            "median": float(np.median(unseeded_pt)) if len(unseeded_pt) else None,
            "n_below_22": int((unseeded_pt < 22).sum()),
        },
        "nTrigObj_mean": float(ak.mean(ak.num(ids))),
        "bit_counts_per_id_without_22": bit_counts_per_id(ids, filter_bits, n_bits, skip_id=22),
        "photon_bits_documented": {str(k): v for k, v in sorted(photon_bits.items())},
    }
    if reference_url:
        result["reference_comparison"] = compare_with_reference(arrays, reference_url)

    if len(photon_bits) not in EXPECTED_PHOTON_BIT_COUNTS:
        print("WARNING: unexpected number of documented photon bits:", len(photon_bits))
    if result["events_with_unseeded_photon_bit"] > 0:
        print("NOTE: photon objects WITH an unseeded bit found:", result["events_with_unseeded_photon_bit"], "events")

    with open(out_path, "w") as out:
        json.dump(result, out, indent=1)
    skip = ("photon_bits_documented", "bit_counts_per_id_without_22")
    print(json.dumps({k: v for k, v in result.items() if k not in skip}, indent=1))


if __name__ == "__main__":
    main()
