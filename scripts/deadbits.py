"""Resolve every trigger-object filter bit of a NanoAOD triggerObjects_cff.py against HLT menus.
usage: deadbits.py <triggerObjects_cff.py> <label=menu.py> [<label=menu.py> ...]
Status per bit and menu: OK (a matching filter whose objects the selection's coll() accepts),
COLL (matching filters exist but none passes the selection's coll()), STALE (no module matches),
UNK (matching filter, collection could not be determined)."""
import re, sys, ast

# ---------- menu ----------
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

CAND_PARAMS = ["l1EGCand", "inputTag", "CandTag", "inputCandCollection", "candIsolatedTag",
               "candNonIsolatedTag", "inputTag1", "inputTag2", "firstLegLastFilter", "secondLegLastFilter",
               "JetSrc", "src", "htLabels", "mhtLabels", "inputJetTag", "originalTag", "TauSrc", "jetSrc",
               "Jets", "JetTags", "inputJets", "candTag", "PreviousCandTag", "previousCandTag", "metLabels",
               "mhtLabel", "inputMet", "L1TauTrigger", "TriggerSrc", "JetTag", "MuonTag", "ElectronTag",
               "PhotonTag", "muonTag", "electronTag", "photonTag", "tauTag", "jetTag", "taus", "originTag1", "originTag2", "originTag3", "originTag", "jets"]

def tag_labels(body, name):
    m = re.search(r'\b%s = cms\.(VInputTag|InputTag)\(\s*(.*?)\s*\)' % re.escape(name), body, re.S)
    if not m: return None
    kind, inner = m.group(1), m.group(2)
    toks = [t.strip().strip('"\'') for t in inner.replace("\n", " ").split(",") if t.strip()]
    if kind == "InputTag":
        return [toks[0].split(":")[0]] if toks else []
    return [t.split(":")[0] for t in toks]

def collections_of(mods, name, depth=0, seen=None):
    """Collections (EDProducer labels) whose objects a filter saves."""
    if seen is None: seen = set()
    if name in seen or depth > 8 or name not in mods: return set()
    seen.add(name)
    typ, body = mods[name]
    direct, follow = set(), []
    for p in CAND_PARAMS:
        labs = tag_labels(body, p)
        if not labs: continue
        for lab in labs:
            t2 = mods.get(lab, ("?", ""))[0]
            if t2 == "EDProducer": direct.add(lab)
            elif t2 == "EDFilter": follow.append(lab)
    if direct: return direct
    out = set()
    for f in follow: out |= collections_of(mods, f, depth + 1, seen)
    return out

def glob_re(pat):
    parts = pat.split("*")
    return re.compile("^" + ".*".join(re.escape(p) for p in parts) + "$")

# ---------- config ----------
def block(text, name):
    lines = text.splitlines(); start = None
    for i, l in enumerate(lines):
        if re.match(r'^\s*%s\s*=\s*cms\.PSet\(' % name, l): start = i; break
    if start is None: return None
    indent = len(lines[start]) - len(lines[start].lstrip()); out = [lines[start]]
    for l in lines[start+1:]:
        ind = len(l) - len(l.lstrip())
        if l.strip() and ind <= indent: break
        out.append(l)
    return "\n".join(out)

def split_args(s):
    args, depth, q, cur = [], 0, None, ""
    for c in s:
        if q:
            cur += c
            if c == q: q = None
            continue
        if c in "\"'": q = c; cur += c; continue
        if c in "([{": depth += 1
        if c in ")]}": depth -= 1
        if c == "," and depth == 0: args.append(cur); cur = ""; continue
        cur += c
    if cur.strip(): args.append(cur)
    return [a.strip() for a in args]

def calls(blk, fname="mksel("):
    res, i = [], 0
    while True:
        j = blk.find(fname, i)
        if j < 0: break
        k = j + len(fname); depth = 1; q = None
        while k < len(blk) and depth:
            c = blk[k]
            if q:
                if c == q: q = None
            elif c in "\"'": q = c
            elif c == "(": depth += 1
            elif c == ")": depth -= 1
            k += 1
        res.append(blk[j+len(fname):k-1]); i = k
    return res

def chaintoken(tokens, op):
    if not isinstance(tokens, (list, tuple)):
        tokens = [t.strip() for t in tokens.split(op)]
    return tokens

def alternatives(sel0):
    """Emulate mksel: return list of alternatives; each alternative = list of (kind, pattern) all required."""
    s = sel0
    if isinstance(s, str) and "OR" in s: s = chaintoken(s, "OR")
    if isinstance(s, str) and "AND" in s: s = ("AND",) + tuple(chaintoken(s, "AND"))
    if isinstance(s, tuple) and s and s[0] == "AND": return [[("filter", t) for t in s[1:]]]
    if isinstance(s, list): return [[("filter", t)] for t in s]
    if isinstance(s, tuple): return [[("filter", t) for t in s]]
    toks = re.findall(r"(filter|path|coll)\('([^']*)'\)", s)
    if not toks: return [[("raw", s)]]
    if "min(" in s or "&&" in s:   # treat as AND of all tokens (approximation)
        return [toks]
    return [[t] for t in toks]

def parse_config(text):
    sels = {}
    for name in ("Electron", "Photon", "Muon", "Tau", "BoostedTau", "Jet", "FatJet", "MET", "HT", "MHT"):
        blk = block(text, name)
        if blk is None: continue
        sel = re.search(r'sel\s*=\s*cms\.string\((["\'])(.*?)\1\)', blk)
        skip = re.search(r'skipObjectsNotPassingQualityBits\s*=\s*cms\.bool\((\w+)\)', blk)
        colls = re.findall(r"coll\('([^']*)'\)", sel.group(2)) if sel else []
        if sel and re.search(r"coll\('[^']*'\)\s*\|\|\s*filter\(", sel.group(2)): colls = []  # coll OR-ed with filters: not restrictive
        bits = []
        qb = blk[blk.find("qualityBits"):] if "qualityBits" in blk else ""
        if "cms.VPSet" in qb:
            for n, c in enumerate(calls(qb)):
                args = split_args(c)
                try: a0 = ast.literal_eval(args[0])
                except Exception: a0 = args[0].strip('"')
                doc = ""
                if len(args) > 1 and not args[1].startswith("bit"):
                    try: doc = ast.literal_eval(args[1])
                    except Exception: doc = args[1]
                b = re.search(r'bit\s*=\s*(\d+)', c)
                bits.append((int(b.group(1)) if b else n, a0, doc))
        else:  # old string layout: "a*filter('x') + ..."
            m = re.search(r'qualityBits\s*=\s*cms\.string\(\s*(.*?)\)\s*,\s*\n', blk, re.S)
            if m:
                expr = "".join(ast.literal_eval(p) for p in re.findall(r'"(?:[^"\\]|\\.)*"', m.group(1)))
                for term in expr.split("+"):
                    w = re.match(r'\s*(\d+)\*', term)
                    bitno = int(w.group(1)).bit_length() - 1 if w else 0
                    pats = re.findall(r"filter\('([^']*)'\)", term)
                    bits.append((bitno, pats if len(pats) > 1 else (pats[0] if pats else term.strip()), ""))
        sels[name] = dict(sel=sel.group(2) if sel else "", skip=skip.group(1) if skip else "?", colls=colls, bits=bits)
    return sels

# ---------- evaluation ----------
def accepts(colls, label):
    if not colls: return True
    return any(glob_re(c).match(label) for c in colls)

def token_status(mods, filters, paths, producers, kind, pat, colls):
    if kind == "path":
        return "OK" if any(glob_re(pat).match(p) for p in paths) else "STALE"
    if kind == "coll":
        return "OK" if any(glob_re(pat).match(p) for p in producers) else "STALE"
    if kind == "raw":
        return "UNK"
    rx = glob_re(pat)
    matched = [f for f in filters if rx.match(f)]
    if not matched: return "STALE"
    best, info = "COLL", []
    for f in matched:
        cs = collections_of(mods, f)
        if not cs: best = "UNK" if best != "OK" else best; info.append("%s[%s:?]" % (f, mods[f][0])); continue
        if any(accepts(colls, c) for c in cs): return "OK"
        info.append("%s[%s:%s]" % (f, mods[f][0], ",".join(sorted(cs))))
    return best + "{" + "; ".join(info[:3]) + "}"

RANK = {"OK": 0, "UNK": 1, "COLL": 2, "STALE": 3}
def bit_status(mods, filters, paths, producers, alts, colls):
    results = []
    for alt in alts:
        sts = [token_status(mods, filters, paths, producers, k, p, colls) for k, p in alt]
        worst = max(sts, key=lambda s: RANK[s.split("{")[0]])
        results.append(worst)
    return min(results, key=lambda s: RANK[s.split("{")[0]])

def main():
    cfg = open(sys.argv[1]).read()
    sels = parse_config(cfg)
    menus = []
    for arg in sys.argv[2:]:
        label, path = arg.split("=", 1)
        mods = parse_modules(open(path).read())
        filters = [n for n, (t, b) in mods.items() if t == "EDFilter"]
        paths = [n for n, (t, b) in mods.items() if t == "Path"]
        producers = [n for n, (t, b) in mods.items() if t == "EDProducer"]
        menus.append((label, mods, filters, paths, producers))
    print("config:", sys.argv[1]); print("menus:", " ".join(l for l, *_ in menus))
    for name, s in sels.items():
        print("\n== %s (sel colls: %s; skip=%s; %d bits)" % (name, s["colls"] or "any", s["skip"], len(s["bits"])))
        if not s["bits"] and s["skip"] == "True":
            print("   !! no quality bits and skipObjectsNotPassingQualityBits=True: this object type is never written")
        counts = {l: {"OK": 0, "UNK": 0, "COLL": 0, "STALE": 0} for l, *_ in menus}
        for bitno, a0, doc in s["bits"]:
            alts = alternatives(a0)
            row = []
            for label, mods, filters, paths, producers in menus:
                st = bit_status(mods, filters, paths, producers, alts, s["colls"])
                counts[label][st.split("{")[0]] += 1
                row.append((label, st))
            if any(st.split("{")[0] != "OK" for l, st in row):
                desc = a0 if isinstance(a0, str) else "|".join(a0)
                print("   bit %2d %-70s %s" % (bitno, (desc[:68] + (".." if len(desc) > 68 else "")), " ".join("%s:%s" % (l, st.split("{")[0]) for l, st in row)))
                extra = [st for l, st in row if "{" in st]
                if extra: print("          detail: " + extra[0][extra[0].find("{"):][:260])
        print("   summary: " + " | ".join("%s OK=%d COLL=%d STALE=%d UNK=%d" % (l, c["OK"], c["COLL"], c["STALE"], c["UNK"]) for l, c in counts.items()))

main()
