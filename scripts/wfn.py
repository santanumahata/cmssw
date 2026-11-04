import re, sys
class WFN:
    def __init__(self, offset):
        self.offset = offset; self.index = 1; self.thousands = 0; self.hundreds = 0
    def __call__(self):
        v = float(f"{self.offset}.{self.thousands}{self.hundreds}{self.index:02d}"); self.index += 1; return v
    def subnext(self):
        self.hundreds += 1; self.index = 1
    def next(self, index=None):
        if index is None: self.thousands += 1; self.hundreds = 0
        else: self.thousands = index; self.hundreds = 0
        self.index = 1
src = open(sys.argv[1]).read()
m = re.search(r'_wfn\s*=\s*WFN\((\d+)\)', src)
w = WFN(int(m.group(1))) if m else None
print("counter init:", m.group(0) if m else "none (old scheme?)")
for i, line in enumerate(src.splitlines(), 1):
    s = line.strip()
    if s.startswith("#"): continue
    if re.match(r'_wfn\.next\(\s*\)', s): w.next()
    elif re.match(r'_wfn\.next\((\d+)\)', s): w.next(int(re.match(r'_wfn\.next\((\d+)\)', s).group(1)))
    elif re.match(r'_wfn\.subnext\(\)', s): w.subnext()
    elif "workflows[_wfn()]" in s:
        print("%-10s %s" % (w(), s.split("=", 1)[1].strip()[:110]))
    elif re.match(r'workflows\[([\d.]+)\]', s):
        print("%-10s %s" % (re.match(r'workflows\[([\d.]+)\]', s).group(1), s.split("=", 1)[1].strip()[:110]))
