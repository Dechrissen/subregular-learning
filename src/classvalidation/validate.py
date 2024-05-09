#!/usr/bin/env python3
from collections import defaultdict
import sys

classes = [
    "comm", "lcomm", "tlcomm",
    "sf",
    "da", "lda", "tlda",
    "ltriv", "lltriv", "tlltriv",
    "rtriv", "lrtriv", "tlrtriv",
    "band", "lband", "tlband",
    "pt", "plt", "tplt",
    "acom", "ltt", "tltt",
    "cb", "lt", "tlt",
    "triv", "gd", "tgd",
    "d", "td", "k", "tk", "f", "tf",
    "sl", "tsl",
]

implications = [
    #sideward movements
    ("comm", "lcomm"), ("lcomm", "tlcomm"),
    ("da","lda"), ("lda","tlda"),
    ("ltriv","lltriv"), ("lltriv","tlltriv"),
    ("rtriv","lrtriv"), ("lrtriv","tlrtriv"),
    ("band","lband"), ("lband","tlband"),
    ("pt","plt"), ("plt","tplt"),
    ("acom","ltt"), ("ltt","tltt"),
    ("cb","lt"), ("lt","tlt"),
    ("triv","gd"), ("gd","tgd"),
    ("d","td"), ("k","tk"),("f","tf"),
    ("sl","tsl"),
    # upward movements
    ("f","d"), ("tf","td"),
    ("f","k"), ("tf","tk"),
    ("d","sl"), ("td","tsl"),
    ("k","sl"), ("tk","tsl"),
    ("sl","lt"), ("tsl","tlt"),
    ("lt","ltt"), ("tlt","tltt"),
    ("lt","lband"), ("tlt","tlband"),
    ("ltt","plt"), ("tltt","tplt"),
    ("ltt","lcomm"), ("tltt","tlcomm"),
    ("plt","lltriv"), ("tplt","tlltriv"),
    ("plt","lrtriv"), ("tplt","tlrtriv"),
    ("lltriv","lda"), ("tlltriv","tlda"),
    ("lrtriv","lda"), ("tlrtriv","tlda"),
    ("tlda","sf"),
    ("triv","cb"), ("cb","acom"), ("cb","band"), ("acom","comm"),
    ("acom","pt"), ("pt","ltriv"), ("pt","rtriv"),
    ("ltriv","da"), ("rtriv","da"),
]

lackers = {
    'plt'  : ['pt','tltt'],
    'lt'   : ['tsl','pt'],
    'ltt'  : ['tlt','pt'],
    'pt'   : ['tltt'],
    'reg'  : ['sf'],
    'sl'   : ['pt'],
    'sp'   : ['tltt'],
    'tplt' : ['tltt','plt'],
    'tlt'  : ['tsl','plt'],
    'tltt' : ['tlt','plt'],
    'tsl'  : ['plt'],
    'zp'   : ['sf'],
    'sf'   : ['tplt']
}

txt = filter(lambda x: x in 'YN', sys.stdin.read())
memberships = defaultdict(lambda : False)
for i,v in enumerate(txt):
    memberships[classes[i]] = v == 'Y'

for p,q in implications:
    if memberships[p] and not memberships[q]:
        print(f'Dissatisfied {p} ~ {q}')

# first arg (sys.argv[0]) is the name of the script
# so we want the SECOND to be the name of the class to test
if len(sys.argv) != 2:
    exit(0)

s = sys.argv[1].lower()

if s not in lackers:
    print(f'unknown class {s}')
    exit(1)

memberships['reg'] = True

if not memberships[s] and s not in ['sp','reg','zp']:
    print(f'not a member of {s}')
    exit(1)

bad = 0
for c in lackers[s]:
    if memberships[c]:
        print(f'in {s} but also in {c}')
        bad = 1
if bad:
    exit(1)
