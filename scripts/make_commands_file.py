# Write results/CODE.md: every analysis script in full, then the hand-run shell commands of this session verbatim.
# usage: SESSION_WORKDIR=<local work folder> SESSION_SCRATCH=<scratch folder> python3 make_commands_file.py <dump of the session's shell calls> <repo root>
import os
import re
import sys

calls_file, root = sys.argv[1], sys.argv[2]
LOCAL = os.environ['SESSION_WORKDIR']
SCRATCH = re.compile(re.escape(os.environ['SESSION_SCRATCH']))
SCRIPTS = [                                                   # (path in repo, fence language)
    ('scripts/verify_nanoaod_files.py', 'python'),
    ('scripts/deadbits.py', 'python'),
    ('scripts/menuscan.py', 'python'),
    ('scripts/menusummary.py', 'python'),
    ('scripts/pathmatrix.py', 'python'),
    ('scripts/bits.py', 'python'),
    ('scripts/bitfilters.py', 'python'),
    ('scripts/wfn.py', 'python'),
    ('scripts/measure_trigobj.py', 'python'),
    ('scripts/make_fixed_nano.sh', 'bash'),
    ('scripts/relval_fix_check.sh', 'bash'),
    ('scripts/compare_dqm.py', 'python'),
]
GROUPS = [                                                    # (group title, call numbers in the session dump)
    ('DAS lookups', [11, 13, 14, 37, 38, 61, 86, 90]),
    ('Measuring the NanoAOD files', [16, 17, 63]),
    ('Fix test, v13 and v15', [52, 96, 97, 99, 103, 105]),
    ('Relval in CMSSW_16_1_3', [56, 57, 93, 101, 102, 127, 116, 131, 128, 133, 129, 130]),
    ('HiggsDNA photon-bit usage', [65, 66, 67]),
]


def read_calls(path):
    # Split the dump at '##### N [description]' headers.
    # Total: time O(lines), space O(lines)
    calls, current = {}, None                                 # dict | call number -> [description, command]
    for line in open(path):                                   # O(lines) | one pass
        m = re.match(r'^##### (\d+) \[(.*)\]$', line.rstrip('\n'))
        if m:
            current = int(m.group(1))
            calls[current] = [m.group(2), '']
        elif current is not None:
            calls[current][1] += line
    return calls


def clean(cmd):
    # Total: time O(len), space O(len)
    cmd = cmd.replace(LOCAL, '<session folder>')              # - | hide local machine paths
    return SCRATCH.sub('<scratch>', cmd).rstrip()


calls = read_calls(calls_file)
out = ['# Code used for the NanoAOD photon TrigObj checks', '',
       'Part 1: every analysis script in `scripts/`, in full. '
       'Part 2: the shell commands I ran by hand on 5 November 2026, copied verbatim from the session log, '
       'in the order they ran. They ran from my laptop; the work happened on lxplus over ssh.', '',
       '## Part 1: scripts', '']
for rel, lang in SCRIPTS:                                     # O(files) | one section per script
    out += [f'### `{rel}`', '', f'```{lang}', open(os.path.join(root, rel)).read().rstrip(), '```', '']
out += ['## Part 2: commands as run', '']
for g, (title, numbers) in enumerate(GROUPS, 1):              # O(commands) | one section per group
    out += [f'### {g}. {title}', '']
    for n in numbers:
        desc, cmd = calls[n]
        out += [f'**{desc}**', '', '```bash', clean(cmd), '```', '']
os.makedirs(os.path.join(root, 'results'), exist_ok=True)
open(os.path.join(root, 'results/CODE.md'), 'w').write('\n'.join(out))
print('scripts', len(SCRIPTS), '| commands', sum(len(n) for _, n in GROUPS))
