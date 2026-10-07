"""
Exact diagonalization of the periodic spin-S Heisenberg ring
    H = sum_{j=0}^{L-1} S_j . S_{j+1}      (J = 1, site L == site 0)
optionally with a twist theta (rotation by theta about the z axis on one
seam bond, gauge-spread uniformly as phi = theta/L per bond).  This is the
twisted Hamiltonian H_n(g) of the periodic Haldane-gap paper (model.tex,
eq. (twisted-hamiltonian) and (seam-phase)); g = P is theta = pi, g = C is
theta = 2 pi / 3.

Symmetries used: total S^z (sector Q = sum of local digits), translation
(momentum k = 2 pi m / L, Bloch basis on orbit representatives), the
spectral equality of M and -M sectors, and (untwisted only) of k and -k.

Basis encoding: configuration x = sum_j s_j d^j, s_j in {0..d-1},
m_j = s_j - S.
"""
import numpy as np
import scipy.sparse as sp
import scipy.linalg as sla
import scipy.sparse.linalg as spla
import time


def all_digit_sums(L, d):
    N = d ** L
    x = np.arange(N, dtype=np.int64)
    s = np.zeros(N, dtype=np.int16)
    y = x.copy()
    for _ in range(L):
        s += (y % d).astype(np.int16)
        y //= d
    del y
    return x, s


def rot(x, L, d):
    """Cyclic translation by one site (digit j -> j-1, digit 0 -> L-1)."""
    return (x % d) * (d ** (L - 1)) + x // d


class Sector:
    """Fixed-Q sector: orbit representatives and the hopping structure."""

    def __init__(self, L, d, Q, x=None, s=None, states=None):
        self.L, self.d, self.Q = L, d, Q
        if states is None:
            states = x[s == Q]
        st = states
        rep = st.copy()
        per = np.zeros(len(st), np.int32)
        r = st.copy()
        for j in range(1, L):
            r = rot(r, L, d)
            np.minimum(rep, r, out=rep)
            per[(per == 0) & (r == st)] = j
        per[per == 0] = L
        isrep = rep == st
        self.reps = st[isrep]
        self.per = per[isrep]
        del rep, r, per, st
        nr = len(self.reps)
        S = (d - 1) / 2.0
        dig = np.empty((L, nr), np.int8)
        y = self.reps.copy()
        for j in range(L):
            dig[j] = y % d
            y //= d
        m = dig.astype(np.float64) - S
        self.diag = np.zeros(nr)
        for j in range(L):
            self.diag += m[j] * m[(j + 1) % L]
        cp = np.sqrt(S * (S + 1) - m * (m + 1))
        cm = np.sqrt(S * (S + 1) - m * (m - 1))
        A, BP, AMP, DIR = [], [], [], []
        for j in range(L):
            j1 = (j + 1) % L
            # S^+_j S^-_{j1}
            a = np.nonzero((dig[j] < d - 1) & (dig[j1] > 0))[0]
            A.append(a)
            BP.append(self.reps[a] + d ** j - d ** j1)
            AMP.append(0.5 * cp[j][a] * cm[j1][a])
            DIR.append(np.ones(len(a), np.int8))
            # S^-_j S^+_{j1}
            a = np.nonzero((dig[j] > 0) & (dig[j1] < d - 1))[0]
            A.append(a)
            BP.append(self.reps[a] - d ** j + d ** j1)
            AMP.append(0.5 * cm[j][a] * cp[j1][a])
            DIR.append(-np.ones(len(a), np.int8))
        del dig, m, cp, cm
        self.a = np.concatenate(A)
        bp = np.concatenate(BP)
        self.amp = np.concatenate(AMP)
        self.dir = np.concatenate(DIR)
        best = bp.copy()
        ell = np.zeros(len(bp), np.int16)
        r = bp.copy()
        for t in range(1, L):
            r = rot(r, L, d)
            msk = r < best
            best[msk] = r[msk]
            ell[msk] = t
        self.ell = ell
        self.b = np.searchsorted(self.reps, best)
        assert np.all(self.reps[self.b] == best)

    def block(self, mk, phi=0.0, dense=True):
        L = self.L
        allowed = (mk * self.per) % L == 0
        nk = int(allowed.sum())
        if nk == 0:
            return None
        idx = -np.ones(len(self.reps), np.int64)
        idx[allowed] = np.arange(nk)
        sel = allowed[self.a] & allowed[self.b]
        a, b = self.a[sel], self.b[sel]
        k = 2 * np.pi * mk / L
        realcase = (phi == 0.0) and ((2 * mk) % L == 0)
        ph = self.dir[sel] * phi - k * self.ell[sel]
        if realcase:
            vals = self.amp[sel] * np.round(np.cos(ph))
        else:
            vals = self.amp[sel] * np.exp(1j * ph)
        vals = vals * np.sqrt(self.per[a] / self.per[b])
        H = sp.coo_matrix((vals, (idx[b], idx[a])), shape=(nk, nk)).tocsr()
        H = H + sp.diags(self.diag[allowed])
        if dense:
            return H.toarray()
        return H


def momentum_list(L, theta):
    """(m, weight) pairs; untwisted rings pair k with -k."""
    if theta != 0.0:
        return [(m, 1) for m in range(L)]
    out = []
    for m in range(L // 2 + 1):
        w = 1 if (2 * m) % L == 0 else 2
        out.append((m, w))
    return out


def full_spectrum(L, S, theta=0.0, verbose=True):
    d = int(round(2 * S + 1))
    phi = theta / L
    x, s = all_digit_sums(L, d)
    Qtot = (d - 1) * L
    Es, Ws = [], []
    t0 = time.time()
    for Q in range(0, Qtot // 2 + 1):
        wQ = 1 if 2 * Q == Qtot else 2
        sec = Sector(L, d, Q, x, s)
        for (mk, wk) in momentum_list(L, theta):
            H = sec.block(mk, phi, dense=True)
            if H is None:
                continue
            e = sla.eigvalsh(H, overwrite_a=True, check_finite=False)
            Es.append(e)
            Ws.append(np.full(len(e), wQ * wk, np.int64))
        if verbose:
            print(f"  L={L} S={S} theta={theta:.4f} Q={Q} done ({time.time()-t0:.1f}s)", flush=True)
    E = np.concatenate(Es)
    W = np.concatenate(Ws)
    assert W.sum() == d ** L, (W.sum(), d ** L)
    o = np.argsort(E)
    return E[o], W[o]


def lowest_in_sector(L, S, Q, mk, nev=2, theta=0.0, x=None, s=None, sec=None):
    d = int(round(2 * S + 1))
    if sec is None:
        sec = Sector(L, d, Q, x, s)
    H = sec.block(mk, theta / L, dense=False)
    if H is None:
        return None, sec
    n = H.shape[0]
    if n <= 400:
        e = np.linalg.eigvalsh(H.toarray())[:nev]
    else:
        e = spla.eigsh(H, k=nev, which='SA', tol=1e-12, return_eigenvectors=False)
        e = np.sort(e)
    return e, sec


# ---------------------------------------------------------------- brute force

def brute_force_spectrum(L, S, theta=0.0):
    """Dense kron construction with the twist on the seam bond (n-1,0), as in
    the paper: h_{n-1,0}(g) = sum_a S^a_{n-1} (g S^a g^-1)_0 with g = exp(-i theta S^z)."""
    d = int(round(2 * S + 1))
    ms = np.arange(S, -S - 1, -1)
    Sz = np.diag(ms)
    Sp = np.zeros((d, d))
    for i in range(1, d):
        m = ms[i]
        Sp[i - 1, i] = np.sqrt(S * (S + 1) - m * (m + 1))
    Sm = Sp.T
    I = np.eye(d)

    def op(o, j):
        out = np.array([[1.0]])
        for q in range(L):
            out = np.kron(out, o if q == j else I)
        return out
    H = np.zeros((d ** L, d ** L), complex)
    for j in range(L):
        j1 = (j + 1) % L
        if j1 == 0:
            g = np.diag(np.exp(-1j * theta * ms))
            Spg = g @ Sp @ g.conj().T
            Smg = g @ Sm @ g.conj().T
        else:
            Spg, Smg = Sp, Sm
        H += op(Sz, j) @ op(Sz, j1)
        H += 0.5 * (op(Sp, j) @ op(Smg, j1) + op(Sm, j) @ op(Spg, j1))
    return np.linalg.eigvalsh(H)
