import re, sys

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
    # sequence/path members in order
    return re.findall(r'(?:fragment|process)\.(\w+)', body)

def describe(mods, name):
    if name not in mods: return "%s: NOT DEFINED" % name
    typ, body = mods[name]
    edtype = re.match(r'\s*"(\w+)"', body)
    edtype = edtype.group(1) if edtype else "?"
    bits = []
    for p in ("saveTags", "l1EGCand", "inputTag", "candTag", "triggerType", "varTag", "lessThan", "useEt", "thrRegularEB", "thrRegularEE", "thrOverEEB", "thrOverEEE", "thrOverE2EB", "thrOverE2EE", "ncandcut", "etcutEB", "etcutEE", "lowerMassCut", "upperMassCut", "minPt", "minMass", "maxMass"):
        v = param(body, p)
        if v is not None: bits.append("%s=%s" % (p, v))
    return "%s [%s] %s" % (name, edtype, " ".join(bits))

def main(path, pathre, maxdepth=2):
    text = open(path).read()
    m = re.search(r'tableName = cms\.string\(\s*"([^"]+)"', text)
    print("#" * 110); print(path, "menu:", m.group(1) if m else "?")
    mods = parse_modules(text)
    names = sorted(n for n, (t, b) in mods.items() if t == "Path" and re.search(pathre, n))
    print("paths:", ", ".join(names))
    for n in names:
        if not re.search(r'Diphoton30_(22|18)', n): continue
        print("-" * 100); print("PATH", n)
        seen = set()
        def walk(name, depth):
            typ, body = mods.get(name, ("?", ""))
            for mem in members(body):
                if mem in seen: continue
                seen.add(mem)
                t2 = mods.get(mem, ("?", ""))[0]
                if t2 == "Sequence" and depth < maxdepth and not mem.startswith(("HLTBeginSequence", "HLTEndSequence", "HLTDoLocalHcal", "HLTDoFull", "HLTPFClustering", "HLTEgamma", "HLTL1", "HLTDoLocalPixel", "HLTRecoPixel", "HLTElePixel", "HLTTrackReco", "HLTPFTrack", "HLTPFRecoSequence", "HLTDo")):
                    print("  " * depth + "SEQ " + mem)
                    walk(mem, depth + 1)
                elif t2 == "EDFilter":
                    print("  " * depth + describe(mods, mem))
                elif t2 == "Sequence":
                    print("  " * depth + "seq " + mem + " (not expanded)")
        walk(n, 1)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else r'HLT_(Diphoton|DoublePhoton)')
