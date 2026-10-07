"""Exact-rational re-derivation of the scalar bootstrap in the periodic paper
(bootstrap.tex, initialization.tex).  Nothing here touches the quantum
problem: it only recomputes the paper's scalar recursions from the paper's
stated inputs, to check transcription and to produce plot-ready tables.
Outputs bootstrap_dyadic.csv, bootstrap_six_updates.csv, bootstrap_checks.json."""
import json, math, os
from fractions import Fraction as F

here = os.path.dirname(os.path.abspath(__file__))


def f(u):
    return u * u / (2 * (1 - u) ** 2)


def G(u):
    return F(1, 2) * ((1 - u) ** -1 + (1 - u) ** -2 + (1 - u) ** -3) ** 2


def ceil7(x):
    return F(math.ceil(x * 10 ** 7), 10 ** 7)


def capped(m, h, r):
    q = math.floor(m / h)
    return q * h ** r + (m - q * h) ** r


checks = {}
# --- scalar hypotheses of Prop. bootstrap (bootstrap.tex, eq. bootstrap-parameters)
checks["G(1/8)"] = str(G(F(1, 8)))
checks["G(1/8) == 913952/117649"] = G(F(1, 8)) == F(913952, 117649)
checks["G(1/8) < 79/10"] = G(F(1, 8)) < F(79, 10)
checks["3/(C(1-3u0)) row1"] = str(F(3) / (F(79, 10) * (1 - 3 * F(1, 8))))
checks["G(1/100) < 5"] = G(F(1, 100)) < 5
checks["G(1/100) float"] = float(G(F(1, 100)))
checks["3/(C(1-3u0)) row2"] = str(F(3) / (5 * (1 - 3 * F(1, 100))))
checks["f(1-(1-u)^3) == G(u) u^2 at u=1/8"] = f(1 - (1 - F(1, 8)) ** 3) == G(F(1, 8)) * F(1, 8) ** 2
checks["gap bound row1 (4/105)log(80/79)"] = (4 / 105) * math.log(80 / 79)
checks["gap bound row2 log(20)/784"] = math.log(20) / 784

# --- dyadic iteration u_{j+1} = C u_j^2 for both rows
rows = []
for (n0, b0, u0, C) in [(60, F(105, 4), F(1, 8), F(79, 10)), (2304, F(784), F(1, 100), F(5))]:
    r = C * u0
    u = u0
    for j in range(0, 8):
        closed = r ** (2 ** j) / C
        assert closed == u
        bound_ratio = 3 * u / (1 - 3 * u)  # e^{-b_j gamma} <= this
        rows.append(dict(row=f"n0={n0}", j=j, n_j=n0 * 2 ** j, b_j=float(b0 * 2 ** j),
                         u_j=float(u), log10_u_j=math.log10(u) if u > 0 else None,
                         gap_bound_from_this_scale=float(-math.log(float(bound_ratio)) / float(b0 * 2 ** j)),
                         uniform_gap_bound=float(math.log(1 / r) / b0)))
        u = C * u * u
with open(os.path.join(here, "bootstrap_dyadic.csv"), "w") as fh:
    keys = list(rows[0].keys())
    fh.write(",".join(keys) + "\n")
    for rw in rows:
        fh.write(",".join(str(rw[k]) for k in keys) + "\n")

# --- seed at (36, 49/4) and six rounded updates (initialization.tex, Prop. seed2304)
mJ = F(10657205, 10 ** 7)
mN = F(2783155, 10 ** 7)
ell = F(999, 1000)
vN = F(872, 1000)
vJ = F(100139, 100000)


def B(k):
    return 3 * capped(mN, vN ** 12, k // 12)


def RA(k):
    return B(k) + (mJ - ell ** 12) ** (k // 12)


checks["mJ > ell^12"] = mJ > ell ** 12
z72_upper_if_no_dominant = capped(mJ, ell ** 12, 6) + B(72)
checks["C(mJ,ell^12,6)+B(72) (must be <1, margin >0.0693)"] = float(z72_upper_if_no_dominant)
checks["margin 1 - that"] = float(1 - z72_upper_if_no_dominant)
p0 = 1 - (1 + RA(36) / ell ** 36) ** -2
q0 = 1 - (vJ ** 72 + RA(72)) ** -2
checks["p0 float (paper: < 0.047916)"] = float(p0)
checks["q0 float (paper: < 0.181521)"] = float(q0)

paper = [(F(151249, 2500000), F(433453, 2500000)),
         (F(343303, 5000000), F(1632381, 10000000)),
         (F(44601, 625000), F(361773, 2500000)),
         (F(632939, 10000000), F(1055161, 10000000)),
         (F(375793, 10000000), F(445941, 10000000)),
         (F(84513, 10000000), F(27493, 5000000))]
tab = [dict(j=0, n_spatial=36, n_thermal=72, b=12.25, p=float(p0), q=float(q0),
            p_exact="exact-rational-see-script", q_exact="exact-rational-see-script",
            matches_paper="seed")]
p, q = p0, q0
allmatch = True
for j in range(1, 7):
    p = ceil7(f(1 - (1 - p) ** 2 * (1 - q)))
    q = ceil7(f(1 - (1 - q) ** 2 * (1 - p)))
    ok = (p, q) == paper[j - 1]
    allmatch &= ok
    tab.append(dict(j=j, n_spatial=36 * 2 ** j, n_thermal=72 * 2 ** j, b=float(F(49, 4) * 2 ** j),
                    p=float(p), q=float(q), p_exact=str(p), q_exact=str(q), matches_paper=ok))
checks["six-update table reproduced exactly"] = allmatch

# float (unrounded) version of the same recursion, to show the effect of rounding
p, q = float(p0), float(q0)
for j in range(1, 7):
    p = f(1 - (1 - p) ** 2 * (1 - q))
    q = f(1 - (1 - q) ** 2 * (1 - p))
    tab[j]["p_float_unrounded"] = p
    tab[j]["q_float_unrounded"] = q
tab[0]["p_float_unrounded"] = float(p0)
tab[0]["q_float_unrounded"] = float(q0)

with open(os.path.join(here, "bootstrap_six_updates.csv"), "w") as fh:
    keys = ["j", "n_spatial", "n_thermal", "b", "p", "q", "p_float_unrounded", "q_float_unrounded",
            "p_exact", "q_exact", "matches_paper"]
    fh.write(",".join(keys) + "\n")
    for rw in tab:
        fh.write(",".join(str(rw[k]) for k in keys) + "\n")

# continue the paper's recursion beyond j=6 using u -> C u^2 with (u0, C) = (1/100, 5)
with open(os.path.join(here, "bootstrap_checks.json"), "w") as fh:
    json.dump({k: (v if isinstance(v, (bool, float, int, str)) else str(v)) for k, v in checks.items()},
              fh, indent=1)
for k, v in checks.items():
    print(k, "=", v)
for rw in tab:
    print(rw["j"], rw["n_spatial"], rw["n_thermal"], rw["b"], f"{rw['p']:.7f}", f"{rw['q']:.7f}",
          f"{rw['p_float_unrounded']:.7f}", f"{rw['q_float_unrounded']:.7f}", rw["matches_paper"])
for rw in rows:
    print(rw)
