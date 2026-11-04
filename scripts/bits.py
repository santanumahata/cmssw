import re, sys

def block(text, name):
    lines = text.splitlines()
    start = None
    for i, l in enumerate(lines):
        if re.match(r'^\s*%s\s*=\s*cms\.PSet\(' % name, l):
            start = i; break
    if start is None:
        return None
    indent = len(lines[start]) - len(lines[start].lstrip())
    out = [lines[start]]
    for l in lines[start+1:]:
        ind = len(l) - len(l.lstrip())
        if l.strip() and ind <= indent:
            break
        out.append(l)
    return "\n".join(out)

def calls(blk, fname="mksel("):
    res = []
    i = 0
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
        res.append(blk[j+len(fname):k-1])
        i = k
    return res

for path in sys.argv[1:]:
    text = open(path).read()
    print("=" * 100); print(path)
    for name in ("Photon", "Electron"):
        blk = block(text, name)
        if blk is None:
            print("  %s: block not found" % name); continue
        sel = re.search(r'sel\s*=\s*cms\.string\((["\'])(.*?)\1\)', blk)
        print("  %s sel: %s" % (name, sel.group(2) if sel else "?"))
        skip = re.search(r'skipObjectsNotPassingQualityBits\s*=\s*cms\.bool\((\w+)\)', blk)
        print("  %s skip: %s" % (name, skip.group(1) if skip else "?"))
        if name == "Electron":
            continue
        cs = calls(blk)
        if not cs:
            qb = re.search(r'qualityBits\s*=\s*cms\.string\((["\'])(.*?)\1', blk, re.S)
            print("  old layout qualityBits string:", qb.group(2)[:2000] if qb else "none")
            continue
        for n, c in enumerate(cs):
            b = re.search(r'bit\s*=\s*(\d+)', c)
            flag = ""
            if "Unseeded" in c: flag = "  <-- unseeded"
            print("   %2d%s %s%s" % (n, (" (bit=%s)" % b.group(1)) if b else "", c.strip()[:150], flag))
