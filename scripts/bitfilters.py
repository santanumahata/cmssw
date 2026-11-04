import re, sys
def parse_modules(text):
    mods = {}
    for m in re.finditer(r'^(?:fragment|process)\.(\w+) = cms\.(\w+)\(', text, re.M):
        k = m.end(); depth = 1; q = None
        while k < len(text) and depth:
            c = text[k]
            if q:
                if c == q: q = None
            elif c in "\"'": q = c
            elif c == "(": depth += 1
            elif c == ")": depth -= 1
            k += 1
        mods[m.group(1)] = (m.group(2), text[m.end():k-1])
    return mods
def param(body, name):
    m = re.search(r'\b%s = cms\.\w+\(\s*(.*?)\s*\)' % re.escape(name), body, re.S)
    return m.group(1).replace('"', '').replace("'", "").strip() if m else None
FILTERS = ["hltEG33L1EG26HEFilter","hltEG50HEFilter","hltEG75HEFilter","hltEG90HEFilter","hltEG120HEFilter","hltEG150HEFilter","hltEG175HEFilter","hltEG200HEFilter","hltHtEcal800","hltEG45EBTightIDTightIsoTrackIsoFilter","hltEG50EBTightIDTightIsoTrackIsoFilter","hltEG110EBTightIDTightIsoTrackIsoFilter","hltEG120EBTightIDTightIsoTrackIsoFilter","hltMu17Photon30IsoCaloIdPhotonlegTrackIsoFilter","hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter","hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter","hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter","hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter","hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter","hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter","hltEG22L1VBFLooseIsoEGHEFilter"]
menus = []
for f in sys.argv[1:]:
    text = open(f).read()
    mods = parse_modules(text)
    row = {}
    for name in FILTERS:
        if name not in mods: row[name] = "-"; continue
        typ, body = mods[name]
        coll = param(body, "l1EGCand") or param(body, "inputTag") or "?"
        if "," in coll: coll = coll.split(",")[0]
        row[name] = {"hltEgammaCandidates": "S", "hltEgammaCandidatesUnseeded": "U"}.get(coll, coll)
    menus.append((f.split("/")[-1].replace("menu_","").replace(".py",""), row))
print("%-82s %s" % ("filter", " ".join("%-3s" % ("c%d" % i) for i in range(len(menus)))))
for i, (n, r) in enumerate(menus): print("  c%-2d %s" % (i, n))
for name in FILTERS:
    print("%-82s %s" % (name, " ".join("%-3s" % r[name] for n, r in menus)))
