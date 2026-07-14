#!/usr/bin/env bash
# Two-sided Fisher exact test on a 2x2 table. Self-contained (wraps python), so
# it runs as one allowlisted call.
#
# Usage: fisher.sh a b c d
#   2x2 table [[a, b], [c, d]] — e.g. a=group1 fails, b=group1 passes,
#                                     c=group2 fails, d=group2 passes.
set -u
python3 - "$@" <<'PY'
import sys
from math import comb
a, b, c, d = (int(x) for x in sys.argv[1:5])
def p(a, b, c, d):
    return comb(a + b, a) * comb(c + d, c) / comb(a + b + c + d, a + c)
obs = p(a, b, c, d); tot = 0.0; r1, r2 = a + b, c + d; col1 = a + c
for x in range(0, min(r1, col1) + 1):
    aa, bb, cc = x, r1 - x, col1 - x
    dd = r2 - cc
    if bb < 0 or cc < 0 or dd < 0:
        continue
    pr = p(aa, bb, cc, dd)
    if pr <= obs + 1e-12:
        tot += pr
print(f"Fisher 2-sided p = {tot:.4f}   [[{a},{b}],[{c},{d}]]")
PY
