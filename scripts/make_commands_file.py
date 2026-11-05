# Copy the result-producing shell commands of this session, verbatim, into one file grouped by step.
import re, sys
calls_file, out_file = sys.argv[1], sys.argv[2]
LOCAL = '/home/santanu/.config/Claude/scratch-workspaces/bcb56660-0fde-4131-be70-35a637089569/a7237d23-a55d-46d8-8df5-151d815d0978/scratch-2026-11-04-d4f5dc'
SCRATCH = re.compile(r'/tmp/claude-1000/[^ ;]*?/scratchpad')
GROUPS = [
    ('1. DAS lookups', [11, 13, 14, 37, 38, 61, 86, 90]),
    ('2. Measuring the NanoAOD files', [16, 17, 63]),
    ('3. Fix test, v13 and v15', [52, 96, 97, 99, 103, 105]),
    ('4. Relval in CMSSW_16_1_3', [56, 57, 93, 101, 102, 127, 116, 131, 128, 133, 129, 130]),
    ('5. HiggsDNA photon-bit usage', [65, 66, 67]),
]

calls = {}                                                     # dict: call number -> (description, command)
current = None
for line in open(calls_file):                                  # O(lines) | split the dump at '##### N [desc]'
    m = re.match(r'^##### (\d+) \[(.*)\]$', line.rstrip('\n'))
    if m:
        current = int(m.group(1))
        calls[current] = [m.group(2), '']
    elif current is not None:
        calls[current][1] += line

with open(out_file, 'w') as out:
    out.write('# Shell commands I ran by hand for the 5 November 2026 checks, copied verbatim from the session log.\n')
    out.write('# They ran from my laptop; the work happened on lxplus over ssh. Not a script to execute as a whole.\n')
    for title, numbers in GROUPS:
        out.write(f'\n# ===== {title}\n')
        for n in numbers:
            desc, cmd = calls[n]
            cmd = cmd.replace(LOCAL, '<session folder>')       # O(len) | hide local machine paths
            cmd = SCRATCH.sub('<scratch>', cmd)
            out.write(f'\n# --- {desc}\n{cmd.rstrip()}\n')
