import re, sys, hashlib

def parse_modules(text):
    mods = {}
    pat = re.compile(r'^(?:fragment|process)\.(\w+) = cms\.(\w+)\(', re.M)
    for m in pat.finditer(text):
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
    return m.group(1).replace('"', '').replace("'", "").replace("\n", " ") if m else None

def members(body):
    return re.findall(r'(?:fragment|process)\.(\w+)', body)

KEY = ["hltDiEG22EtEta2p55UnseededFilter",
       "hltEG22R9Id85b90eHE12R9Id50b80eR9UnseededLastFilter",
       "hltEG22Iso60CaloId15b35eHE12R9Id50b80eTrackIsoUnseededLastFilter",
       "hltEG30LR9Id85b90eHE12R9Id50b80eR9IdLastFilter",
       "hltEG30LIso60CaloId15b35eHE12R9Id50b80eEcalIsoLastFilter",
       "hltEG30Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eEcalIsoFilter",
       "hltEG18TrackIso60Iso60CaloId15b35eR9Id50b90eHE12b10eR9Id50b80eTrackIsoUnseededFilter",
       "hltEG30Iso60b40eCaloId11b32eHE10b9eR9Id50b90eEcalIsoFilter",
       "hltDiEG18TrackIso60Iso60b40eCaloId11b32eHE10b9eR9Id50b90eTrackIsoUnseededFilter",
       "hltDiEG18EtUnseededFilter"]

def leaves(mods, name, seen=None):
    if seen is None: seen = set()
    out = []
    typ, body = mods.get(name, ("?", ""))
    for mem in members(body):
        if mem in seen: continue
        seen.add(mem)
        t2 = mods.get(mem, ("?", ""))[0]
        if t2 in ("Sequence", "Path"):
            out += leaves(mods, mem, seen)
        elif t2 == "EDFilter":
            out.append(mem)
    return out

for path in sys.argv[1:]:
    text = open(path).read()
    m = re.search(r'tableName = cms\.string\(\s*["\']([^"\']+)["\']', text)
    mods = parse_modules(text)
    print("#" * 100)
    print("%s\n  menu: %s" % (path.split("/")[-1], m.group(1) if m else "?"))
    names = sorted(n for n, (t, b) in mods.items() if t == "Path" and re.search(r'HLT_(Diphoton|DoublePhoton)', n))
    print("  paths: " + ", ".join(n.replace("HLT_", "") for n in names))
    for k in KEY:
        if k not in mods:
            print("  KEY %-88s : not defined" % k); continue
        typ, body = mods[k]
        ed = re.match(r'\s*"(\w+)"', body).group(1)
        print("  KEY %-88s : %s saveTags=%s l1EGCand=%s inputTag=%s triggerType=%s" % (k, ed, param(body, "saveTags"), param(body, "l1EGCand"), param(body, "inputTag"), param(body, "triggerType")))
    for n in names:
        if not re.search(r'Diphoton30_(22|18)', n): continue
        lv = [f for f in leaves(mods, n) if f.startswith("hlt") and not f.startswith("hltPre") and mods[f][1].find("HLTL1TSeed") < 0 and not re.search(r'(Trigger|Bool|HLTPrescaler)', mods[f][1][:40])]
        egf = [f for f in lv if re.search(r'EG|Diphoton|DiEG|DiPhoton|Mass|Photon', f)]
        uns = [f for f in egf if "Unseeded" in f]
        sed = [f for f in egf if "Unseeded" not in f and not re.search(r'Comb|Mass', f)]
        comb = [f for f in egf if re.search(r'Comb|Mass', f)]
        st = set(param(mods[f][1], "saveTags") for f in egf)
        h = hashlib.md5(" ".join(egf).encode()).hexdigest()[:8]
        print("  PATH %s: nEgFilters=%d chain=%s saveTags=%s" % (n.replace("HLT_", ""), len(egf), h, "/".join(sorted(x or "None" for x in st))))
        print("       last seeded   : %s" % (sed[-1] if sed else "-"))
        print("       last unseeded : %s" % (uns[-1] if uns else "-"))
        print("       comb/mass     : %s" % ", ".join(comb))
