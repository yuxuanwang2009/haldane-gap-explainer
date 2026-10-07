"""Independent floating-point (NOT certified) cross-check of the thermal tables in
Lemma thermal-inputs, by exact diagonalisation of the twisted spin-1 Heisenberg ring.

H_n(theta) = sum_j S_j.S_{j+1}, with the seam bond (n-1,0) twisted by exp(-i theta S^z) on site 0:
   S^+_{n-1} S^-_0 picks up a phase.  We use the paper's matrix convention (model.tex eq. seam-phase):
   H_{x,y} = exp(i theta (y_0 - x_0)) for a seam hop from column y to row x.
Z_n(b,theta) = sum_k exp(-b (E_k + a n)),  a = 700741/500000.
Also reports E_0 and the gap of the untwisted ring for orientation.
"""
import itertools, sys, time
import numpy as np

a = 700741/500000

def sector_H(n, M, theta):
    words = [w for w in itertools.product((-1, 0, 1), repeat=n) if sum(w) == M]
    idx = {w: i for i, w in enumerate(words)}
    d = len(words)
    H = np.zeros((d, d), dtype=complex if theta not in (0.0,) else float)
    for i, x in enumerate(words):
        H[i, i] = sum(x[j-1]*x[j] for j in range(n))
        for j in range(n):
            k = (j+1) % n
            for delta in (-1, 1):
                y = list(x); y[j] -= delta; y[k] += delta   # column y, row x  <-> x = y with (j,k) changed by (+delta,-delta)
                if abs(y[j]) > 1 or abs(y[k]) > 1:
                    continue
                y = tuple(y); c = idx[y]
                amp = 1.0  # (S^+ S^- + S^- S^+)/2 with ladder sqrt2 * sqrt2 / 2 = 1
                if k == 0 and theta != 0.0:
                    amp = np.exp(1j*theta*(y[0]-x[0]))
                H[i, c] += amp
    return H

def spectrum(n, theta):
    ev = []
    for M in range(-n, n+1):
        H = sector_H(n, M, theta)
        assert np.allclose(H, H.conj().T)
        ev.append(np.linalg.eigvalsh(H))
    return np.sort(np.concatenate(ev))

def Z(ev, n, b):
    return float(np.sum(np.exp(-b*(ev + a*n))))

tab49 = {4: (124885379, 65757), 5: (2925, 2960742), 6: (12870614, 286599), 7: (54069, 1920414),
         8: (4639283, 510140), 9: (195455, 1514846), 10: (2654823, 675419), 11: (377629, 1314544),
         12: (1900547, 787405)}
tab21 = {6: (8945303, 346734, 939987), 8: (3741281, 567167, 984108), 10: (2327547, 721090, 1002613)}

nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 10
print("n  twist   b      Z_ED            table centre   |diff|      E0(n)/n      gap(n) (untwisted)")
nmin = int(sys.argv[2]) if len(sys.argv) > 2 else 4
for n in range(nmin, nmax+1):
    t0 = time.time()
    specs = {th: spectrum(n, th) for th in (0.0, np.pi) + ((2*np.pi/3,) if n in tab21 else ())}
    e = specs[0.0]
    gap = e[np.argmax(e > e[0] + 1e-9)] - e[0]
    for th, lab in ((0.0, "1"), (np.pi, "P")):
        z = Z(specs[th], n, 49/4); c = tab49[n][0 if th == 0.0 else 1]*1e-6
        print(f"{n:2d}  {lab:5s} 49/4  {z:14.8f}  {c:14.6f}  {abs(z-c):.2e}   {e[0]/n:+.6f}   {gap:.5f}")
    if n in tab21:
        for k, (th, lab) in enumerate(((0.0, "1"), (np.pi, "P"), (2*np.pi/3, "C"))):
            z = Z(specs[th], n, 21/2); c = tab21[n][k]*1e-6
            print(f"{n:2d}  {lab:5s} 21/2  {z:14.8f}  {c:14.6f}  {abs(z-c):.2e}")
    print(f"    [n={n}: {time.time()-t0:.1f}s; Hilbert dim {3**n}]", flush=True)
