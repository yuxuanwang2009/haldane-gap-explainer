"""Full spectra of periodic (optionally twisted) spin-S Heisenberg rings,
parallelised over (S^z sector, momentum) blocks.  Writes
spectra/S{S}_L{L}_th{tag}.npz with arrays E (distinct block eigenvalues,
sorted) and W (multiplicity weights; sum W = (2S+1)^L).

usage: python run_spectra.py JOBSPEC [nworkers]
JOBSPEC like "0.5:4-18:0" or "1:4-12:0,pi,2pi3" (comma lists allowed in L
and twist fields; ranges a-b include every integer)."""
import os
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import sys, time
import numpy as np
from multiprocessing import Pool
import scipy.linalg as sla
from ed import Sector, all_digit_sums, momentum_list

TW = {"0": 0.0, "pi": np.pi, "2pi3": 2 * np.pi / 3}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spectra")
os.makedirs(OUT, exist_ok=True)

_cache = {}


def work(task):
    S, L, tag, Q, mk, wt = task
    d = int(round(2 * S + 1))
    key = (L, d, Q)
    if key not in _cache:
        _cache.clear()
        x, s = all_digit_sums(L, d)
        _cache[key] = Sector(L, d, Q, x, s)
        del x, s
    sec = _cache[key]
    H = sec.block(mk, TW[tag] / L, dense=True)
    if H is None:
        return task, np.zeros(0), 0
    n = H.shape[0]
    e = sla.eigvalsh(H, overwrite_a=True, check_finite=False, driver="evd")
    return task, e, n


def parse_L(f):
    out = []
    for part in f.split(","):
        if "-" in part:
            a, b = map(int, part.split("-"))
            out += list(range(a, b + 1))
        else:
            out.append(int(part))
    return out


def main():
    jobs = []
    for spec in sys.argv[1].split(";"):
        Sf, Lf, Tf = spec.split(":")
        S = float(Sf)
        for L in parse_L(Lf):
            for tag in Tf.split(","):
                if S == 0.5 and L % 2 == 1:
                    continue
                jobs.append((S, L, tag))
    nw = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    tasks = []
    for (S, L, tag) in jobs:
        fn = os.path.join(OUT, f"S{S}_L{L}_th{tag}.npz")
        if os.path.exists(fn):
            print("skip existing", fn)
            continue
        d = int(round(2 * S + 1))
        Qtot = (d - 1) * L
        for Q in range(0, Qtot // 2 + 1):
            wQ = 1 if 2 * Q == Qtot else 2
            for (mk, wk) in momentum_list(L, TW[tag]):
                tasks.append((S, L, tag, Q, mk, wQ * wk))
    # rough cost estimate: sector size ~ multinomial; just put large-L, central-Q first
    def cost(t):
        S, L, tag, Q, mk, wt = t
        d = int(round(2 * S + 1))
        return (L * np.log(d), -abs(Q - (d - 1) * L / 2))
    tasks.sort(key=cost, reverse=True)
    pending = {}
    for t in tasks:
        pending.setdefault(t[:3], []).append(t)
    results = {k: ([], []) for k in pending}
    remaining = {k: len(v) for k, v in pending.items()}
    t0 = time.time()
    with Pool(nw, maxtasksperchild=50) as pool:
        for task, e, n in pool.imap_unordered(work, tasks):
            k = task[:3]
            if n:
                results[k][0].append(e)
                results[k][1].append(np.full(n, task[5], np.int64))
            remaining[k] -= 1
            if remaining[k] == 0:
                S, L, tag = k
                E = np.concatenate(results[k][0])
                W = np.concatenate(results[k][1])
                d = int(round(2 * S + 1))
                assert W.sum() == d ** L, (k, W.sum())
                o = np.argsort(E)
                np.savez(os.path.join(OUT, f"S{S}_L{L}_th{tag}.npz"), E=E[o], W=W[o])
                print(f"[{time.time()-t0:7.1f}s] saved S={S} L={L} twist={tag} "
                      f"E0={E[o][0]:.12f} dim={W.sum()}", flush=True)
                del results[k]


if __name__ == "__main__":
    main()
