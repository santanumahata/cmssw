import re, sys
def paths(path):
    text = open(path).read()
    m = re.search(r'tableName = cms\.string\(\s*["\']([^"\']+)["\']', text)
    res = {}
    for pm in re.finditer(r'^(?:fragment|process)\.(HLT_(?:Diphoton|DoublePhoton|DiphotonMVA)\w*?)_v(\d+) = cms\.Path\(', text, re.M):
        res[pm.group(1)] = int(pm.group(2))
    return (m.group(1) if m else "?"), res
cols = []
allp = set()
for f in sys.argv[1:]:
    name, res = paths(f)
    cols.append((f.split("/")[-1].replace("menu_", "").replace(".py", ""), name, res))
    allp |= set(res)
print("columns:")
for i, (f, n, r) in enumerate(cols):
    print("  c%-2d %-32s %s" % (i, f, n))
print()
print("%-78s %s" % ("path", " ".join("c%-2d" % i for i in range(len(cols)))))
for p in sorted(allp):
    print("%-78s %s" % (p.replace("HLT_", ""), " ".join("%-3s" % (r.get(p, "-")) for f, n, r in cols)))
