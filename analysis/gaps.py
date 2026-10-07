"""Lanczos (scipy eigsh) low-lying levels of periodic spin-S Heisenberg rings,
resolved by momentum k = 2 pi m / L, in the S^z = 0 and S^z = 1 sectors.
Writes gaps_lanczos_S{S}.csv (per-k data) and appends to stdout.
usage: python gaps.py S Lmin Lmax"""
import os, sys, time
import numpy as np
from ed import Sector, all_digit_sums, lowest_in_sector

S = float(sys.argv[1]); Lmin = int(sys.argv[2]); Lmax = int(sys.argv[3])
d = int(round(2 * S + 1))
here = os.path.dirname(os.path.abspath(__file__))
fn = os.path.join(here, f"gaps_lanczos_S{S}.csv")
new = not os.path.exists(fn)
f = open(fn, "a")
if new:
    f.write("S,L,m,k_over_pi,Sz0_level1,Sz0_level2,Sz1_level1\n")
for L in range(Lmin, Lmax + 1, 2):
    t0 = time.time()
    x, s = all_digit_sums(L, d)
    Q0 = (d - 1) * L // 2
    sec0 = Sector(L, d, Q0, x, s)
    sec1 = Sector(L, d, Q0 + 1, x, s)
    del x, s
    for m in range(L // 2 + 1):
        e0, _ = lowest_in_sector(L, S, Q0, m, nev=2, sec=sec0)
        e1, _ = lowest_in_sector(L, S, Q0 + 1, m, nev=1, sec=sec1)
        a1 = e0[0] if e0 is not None else np.nan
        a2 = e0[1] if (e0 is not None and len(e0) > 1) else np.nan
        b1 = e1[0] if e1 is not None else np.nan
        f.write(f"{S},{L},{m},{2*m/L:.6f},{a1:.12f},{a2:.12f},{b1:.12f}\n")
        f.flush()
    print(f"S={S} L={L} done in {time.time()-t0:.1f}s", flush=True)
f.close()
