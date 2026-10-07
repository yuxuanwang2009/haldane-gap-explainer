"""Turns the full ED spectra (spectra/*.npz) and the Lanczos data
(gaps_lanczos_S*.csv) into plot-ready tables.  All energies in units J = 1,
H = sum_j S_j.S_{j+1} on a periodic ring; beta = inverse temperature = the
paper's b.  Partition functions use the paper's shift Z_L(b) = Tr exp[-b(H_L + aL)]
(a = 700741/500000 for spin 1; a = ln2 - 1/4 for spin 1/2); the shift cancels in
every purity.  Since the spectra are complete, there is NO truncation error:
Z is an exact finite sum over all (2S+1)^L eigenvalues (floating point only)."""
import os, csv, json, math, glob
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
SP = os.path.join(here, "spectra")
A_SHIFT = {1.0: 700741 / 500000, 0.5: math.log(2) - 0.25}
E0_INF = {1.0: -1.401484038971, 0.5: 0.25 - math.log(2)}   # White-Huse 1993; Bethe/Hulthen
V_LIT = {1.0: 2.49, 0.5: math.pi / 2}                       # spin-wave velocities (literature)
DELTA_LIT = 0.41048                                         # Haldane gap (literature)

_cache = {}


def spec(S, L, tag="0"):
    key = (S, L, tag)
    if key not in _cache:
        fn = os.path.join(SP, f"S{S}_L{L}_th{tag}.npz")
        if not os.path.exists(fn):
            return None
        z = np.load(fn)
        _cache[key] = (z["E"], z["W"].astype(np.float64))
    return _cache[key]


def available(S, tag="0"):
    out = []
    for fn in glob.glob(os.path.join(SP, f"S{S}_L*_th{tag}.npz")):
        out.append(int(os.path.basename(fn).split("_L")[1].split("_")[0]))
    return sorted(out)


def logZ(S, L, b, tag="0"):
    E, W = spec(S, L, tag)
    e0 = E[0]
    return -b * (e0 + A_SHIFT[S] * L) + math.log(np.sum(W * np.exp(-b * (E - e0))))


def thermal_defect(S, L, b):
    """1 - T(L,b), T = Z_L(2b)/Z_L(b)^2, computed without cancellation."""
    E, W = spec(S, L)
    dE = E - E[0]
    gs = dE < 1e-9
    g0 = W[gs].sum()
    a1 = np.sum(W[~gs] * np.exp(-b * dE[~gs]))
    b1 = np.sum(W[~gs] * np.exp(-2 * b * dE[~gs]))
    A = g0 + a1
    return (g0 * g0 - g0 + 2 * g0 * a1 + a1 * a1 - b1) / (A * A)


def thermal_purity(S, L, b):
    return 1.0 - thermal_defect(S, L, b)


def log_spatial(S, n, b):
    return logZ(S, 2 * n, b) - 2 * logZ(S, n, b)


def spatial_purity(S, n, b):
    return math.exp(log_spatial(S, n, b))


def wcsv(name, header, rows):
    with open(os.path.join(here, name), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


summary = {}

# ------------------------------------------------------------------ (a) gaps
gap_rows, disp_rows = [], []
for S in (1.0, 0.5):
    fn = os.path.join(here, f"gaps_lanczos_S{S}.csv")
    rows = list(csv.DictReader(open(fn)))
    Ls = sorted(set(int(r["L"]) for r in rows))
    for L in Ls:
        rr = [r for r in rows if int(r["L"]) == L]
        rr = {int(r["m"]): r for r in rr}  # de-duplicate
        ms = sorted(rr)
        a1 = np.array([float(rr[m]["Sz0_level1"]) for m in ms])
        a2 = np.array([float(rr[m]["Sz0_level2"]) for m in ms])
        b1 = np.array([float(rr[m]["Sz1_level1"]) for m in ms])
        i0 = int(np.nanargmin(a1))
        E0 = a1[i0]
        cand = np.concatenate([np.delete(a1, i0), [a2[i0]], b1])
        gap = float(np.nanmin(cand) - E0)
        it = int(np.nanargmin(b1))
        trip = float(b1[it] - E0)
        # cross-check against full spectrum if present
        fs = spec(S, L)
        if fs is not None:
            E, W = fs
            fgap = E[np.argmax(E > E[0] + 1e-9)] - E[0]
            xdiff = abs(fgap - gap) + abs(E[0] - E0)
        else:
            xdiff = None
        gap_rows.append([S, L, f"{E0:.10f}", f"{E0/L:.10f}", f"{E0_INF[S]:.10f}", f"{E0/L - E0_INF[S]:.3e}",
                         f"{gap:.10f}", f"{gap*L:.6f}", f"{2*ms[i0]/L:.3f}", f"{2*ms[it]/L:.3f}", f"{trip:.10f}",
                         "" if xdiff is None else f"{xdiff:.1e}"])
        for j, m in enumerate(ms):
            disp_rows.append([S, L, f"{2*m/L:.6f}", f"{b1[j]-E0:.10f}"])
wcsv("gaps.csv", ["S", "L", "E0", "E0_per_site", "e0_infinite_literature", "E0/L-e0", "gap_first_excitation",
                  "gap_times_L", "GS_k_over_pi", "lowest_Sz1_k_over_pi", "lowest_Sz1_minus_E0",
                  "abs_diff_vs_full_spectrum"], gap_rows)
wcsv("dispersion_lowest_Sz1.csv", ["S", "L", "k_over_pi", "E_lowest(Sz=1,k)-E0"], disp_rows)

# --------------------------------------------- (b) thermal purity along beta = c L
LS1 = [L for L in available(1.0) if L % 2 == 0]
LS2 = [L for L in available(0.5) if L % 2 == 0]
ray_rows = []
for S, Ls in ((1.0, LS1), (0.5, LS2)):
    for c in (0.25, 0.5, 1.0, 2.0):
        for L in Ls:
            b = c * L
            dT = thermal_defect(S, L, b)
            ray_rows.append([S, c, L, b, f"{1-dT:.12f}", f"{dT:.6e}"])
wcsv("thermal_purity_ray.csv", ["S", "c", "L", "beta=cL", "T(L,beta)", "1-T"], ray_rows)

# ------------------------------------------- (f) thermal purity vs beta at fixed L
grid = np.round(np.concatenate([np.arange(0.0, 2.0, 0.05), np.arange(2.0, 40.0001, 0.25)]), 4)
tb_rows = []
for S, Ls in ((1.0, LS1), (0.5, LS2)):
    for L in Ls:
        for b in grid:
            dT = thermal_defect(S, L, b) if b > 0 else 1 - 1 / ( (2*S+1) ** L )
            tb_rows.append([S, L, b, f"{1-dT:.12f}", f"{dT:.6e}"])
wcsv("thermal_purity_vs_beta.csv", ["S", "L", "beta", "T(L,beta)", "1-T"], tb_rows)


def beta_star(S, L, target):
    lo, hi = 0.0, 1.0
    while thermal_defect(S, L, hi) > target:
        hi *= 2
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if thermal_defect(S, L, mid) > target:
            lo = mid
        else:
            hi = mid
    return hi


bs_rows = []
for S, Ls in ((1.0, LS1), (0.5, LS2)):
    for L in Ls:
        bs_rows.append([S, L, f"{beta_star(S, L, 1/8):.6f}", f"{beta_star(S, L, 1/100):.6f}",
                        f"{beta_star(S, L, 1e-6):.6f}"])
wcsv("beta_star_thermal.csv", ["S", "L", "beta: 1-T=1/8", "beta: 1-T=1/100", "beta: 1-T=1e-6"], bs_rows)

# ------------------------------------------------ (c) spatial purity S(n,beta)
BETAS = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 10.5, 12.25, 16.0, 24.5]
sp_rows = []
for S, Ls in ((1.0, available(1.0)), (0.5, LS2)):
    for n in range(4, 13):
        if 2 * n not in Ls or n not in Ls:
            continue
        for b in BETAS:
            ls = log_spatial(S, n, b)
            sp_rows.append([S, n, 2 * n, b, "even" if n % 2 == 0 else "ODD(not a purity)",
                            f"{math.exp(ls):.12f}", f"{-math.expm1(ls):.6e}"])
wcsv("spatial_purity.csv", ["S", "n", "2n", "beta", "n_parity", "S(n,beta)", "1-S"], sp_rows)

spb_rows = []
gridS = np.round(np.concatenate([np.arange(0.05, 2.0, 0.05), np.arange(2.0, 40.0001, 0.25)]), 4)
for S, Ls in ((1.0, LS1), (0.5, LS2)):
    for n in range(4, 13, 2):
        if 2 * n not in Ls:
            continue
        for b in gridS:
            ls = log_spatial(S, n, b)
            spb_rows.append([S, n, b, f"{math.exp(ls):.12f}", f"{-math.expm1(ls):.6e}"])
wcsv("spatial_purity_vs_beta.csv", ["S", "n", "beta", "S(n,beta)", "1-S"], spb_rows)

# spatial purity along the ray beta = c n  (CFT check for spin 1/2)
spr_rows = []
for S, Ls in ((1.0, LS1), (0.5, LS2)):
    for c in (0.25, 0.5, 2 / math.pi, 1.0, 2.0):
        for n in range(4, 13, 2):
            if 2 * n not in Ls:
                continue
            ls = log_spatial(S, n, c * n)
            spr_rows.append([S, f"{c:.6f}", n, c * n, f"{math.exp(ls):.12f}", f"{-math.expm1(ls):.6e}"])
wcsv("spatial_purity_ray.csv", ["S", "c", "n", "beta=cn", "S(n,beta)", "1-S"], spr_rows)

# finite-size energy inequality implied by S <= 1 as b -> infinity: E0(2n) >= 2 E0(n)
ineq_rows = []
for S, Ls in ((1.0, LS1), (0.5, LS2)):
    for n in range(2, 13):
        if n in Ls and 2 * n in Ls:
            e_n, e_2n = spec(S, n)[0][0], spec(S, 2 * n)[0][0]
            ineq_rows.append([S, n, f"{e_n:.10f}", f"{e_2n:.10f}", f"{e_2n - 2*e_n:.10f}"])
wcsv("energy_superadditivity.csv", ["S", "n", "E0(n)", "E0(2n)", "E0(2n)-2E0(n) (>=0 required by S<=1)"],
     ineq_rows)

# ------------------------------------------- (d) cancellation identities
cid_rows = []
maxrel = 0.0
for S, Ls in ((1.0, available(1.0)), (0.5, LS2)):
    for n in range(2, 13):
        for b in (0.5, 1.0, 3.0, 7.0, 12.25):
            if n in Ls and 2 * n in Ls and n >= 2:
                lhs = log_spatial(S, n, 2 * b)
                rhs = 2 * log_spatial(S, n, b) + (logZ(S, 2 * n, 2 * b) - 2 * logZ(S, 2 * n, b)) \
                    - 2 * (logZ(S, n, 2 * b) - 2 * logZ(S, n, b))
                cid_rows.append([S, "S(n,2b)=S(n,b)^2 T(2n,b)/T(n,b)^2", n, b, f"{lhs:.15e}", f"{rhs:.15e}",
                                 f"{abs(lhs-rhs):.2e}"])
                maxrel = max(maxrel, abs(lhs - rhs))
            if n in Ls and 2 * n in Ls and 4 * n in Ls:
                lhs = logZ(S, 4 * n, 2 * b) - 2 * logZ(S, 4 * n, b)
                T2n = logZ(S, 2 * n, 2 * b) - 2 * logZ(S, 2 * n, b)
                rhs = 2 * T2n + log_spatial(S, 2 * n, 2 * b) - 2 * log_spatial(S, 2 * n, b)
                cid_rows.append([S, "T(4n,b)=T(2n,b)^2 S(2n,2b)/S(2n,b)^2", n, b, f"{lhs:.15e}", f"{rhs:.15e}",
                                 f"{abs(lhs-rhs):.2e}"])
                maxrel = max(maxrel, abs(lhs - rhs))
wcsv("cancellation_identity_check.csv", ["S", "identity", "n", "b", "log LHS", "log RHS", "abs diff (logs)"],
     cid_rows)
summary["cancellation_max_abs_log_diff"] = maxrel

# ----------------------------- paper's certified thermal table (Lemma thermal-inputs)
paper_tab = {  # (n, b, g): center in units 1e-6
    (6, 10.5, "0"): 8945303, (6, 10.5, "pi"): 346734, (6, 10.5, "2pi3"): 939987,
    (8, 10.5, "0"): 3741281, (8, 10.5, "pi"): 567167, (8, 10.5, "2pi3"): 984108,
    (10, 10.5, "0"): 2327547, (10, 10.5, "pi"): 721090, (10, 10.5, "2pi3"): 1002613,
    (4, 12.25, "0"): 124885379, (4, 12.25, "pi"): 65757, (5, 12.25, "0"): 2925, (5, 12.25, "pi"): 2960742,
    (6, 12.25, "0"): 12870614, (6, 12.25, "pi"): 286599, (7, 12.25, "0"): 54069, (7, 12.25, "pi"): 1920414,
    (8, 12.25, "0"): 4639283, (8, 12.25, "pi"): 510140, (9, 12.25, "0"): 195455, (9, 12.25, "pi"): 1514846,
    (10, 12.25, "0"): 2654823, (10, 12.25, "pi"): 675419, (11, 12.25, "0"): 377629, (11, 12.25, "pi"): 1314544,
    (12, 12.25, "0"): 1900547, (12, 12.25, "pi"): 787405,
}
pt_rows = []
worst = 0.0
for (n, b, g), c in sorted(paper_tab.items()):
    if spec(1.0, n, g) is None:
        pt_rows.append([n, b, g, "", c * 1e-6, "", "not computed"])
        continue
    z = math.exp(logZ(1.0, n, b, g))
    tol = 1e-5 if b == 10.5 else 30e-6
    diff = z - c * 1e-6
    worst = max(worst, abs(diff))
    pt_rows.append([n, b, {"0": "1", "pi": "P", "2pi3": "C"}[g], f"{z:.9f}", f"{c*1e-6:.6f}", f"{diff:.2e}",
                    "OK" if abs(diff) < tol else "MISMATCH"])
wcsv("paper_thermal_table_check.csv", ["n", "b", "g", "Z_ED", "paper_center", "ED-center", "within paper error?"],
     pt_rows)
summary["paper_table_worst_abs_diff"] = worst

# sector moments (sector-inversion eq.) at b = 21/2, n = 10 and b = 49/4, n = 12, from ED
sec_rows = []
for (n, b) in ((10, 10.5), (12, 12.25), (6, 10.5), (8, 10.5)):
    try:
        Z1 = math.exp(logZ(1.0, n, b, "0"))
        ZP = math.exp(logZ(1.0, n, b, "pi"))
    except TypeError:
        continue
    J = (Z1 + 3 * ZP) / 4
    N = (Z1 - ZP) / 4
    row = [n, b, f"{Z1:.8f}", f"{ZP:.8f}", f"{J:.8f}", f"{N:.8f}"]
    if spec(1.0, n, "2pi3") is not None:
        ZC = math.exp(logZ(1.0, n, b, "2pi3"))
        I = (Z1 + 3 * ZP + 8 * ZC) / 12
        O = (Z1 + 3 * ZP - 4 * ZC) / 12
        row += [f"{ZC:.8f}", f"{I:.8f}", f"{O:.8f}"]
    else:
        row += ["", "", ""]
    sec_rows.append(row)
wcsv("sector_moments.csv", ["n", "b", "Z", "Z(P)", "J_n", "N_n", "Z(C)", "I_n", "O_n"], sec_rows)

# ------------------------------------------ dilute-magnon estimate (APPROXIMATE)
def magnon_log_ratio(L, b, Delta=DELTA_LIT, v=V_LIT[1.0]):
    k = 2 * np.pi * np.arange(L) / L
    q = np.angle(np.exp(1j * (k - np.pi)))
    eps = np.sqrt(Delta ** 2 + (v * q) ** 2)
    return 3 * np.sum(np.exp(-b * eps))


def magnon_thermal_defect(L, b):
    return -math.expm1(magnon_log_ratio(L, 2 * b) - 2 * magnon_log_ratio(L, b))


est_rows = []
for (L, b, label) in [(8, 8, "ED compare"), (10, 10, "ED compare"), (12, 12, "ED compare"), (12, 6, "ED compare"),
                      (72, 12.25, "paper seed q0 bounds 1-T(72,49/4) by 0.181521"),
                      (120, 26.25, "paper seed bounds 1-T(120,105/4) by 1/8"),
                      (144, 24.5, "paper j=1 q bounds 1-T(144,49/2) by 0.1733812"),
                      (4608, 784, "paper j=6 q bounds 1-T(4608,784) by 0.0054986")]:
    est = magnon_thermal_defect(L, b)
    exact = thermal_defect(1.0, L, b) if spec(1.0, L) is not None else None
    est_rows.append([L, b, f"{est:.4e}", "" if exact is None else f"{exact:.4e}", label])
wcsv("magnon_gas_estimate.csv", ["L", "b", "1-T dilute-magnon ESTIMATE (Delta=0.41048,v=2.49)", "1-T exact ED",
                                 "context"], est_rows)


# HEURISTIC spatial counterpart: Euclidean rotation of the relativistic (O(3) sigma-model)
# magnon gas, S(n,b) ~ T(L'=v b, b'=n/v), continuum momentum integral (L' non-integer).
def magnon_cont_a(Lp, bp, Delta=DELTA_LIT, v=V_LIT[1.0]):
    q = np.linspace(-np.pi, np.pi, 20001)
    eps = np.sqrt(Delta ** 2 + (v * q) ** 2)
    return 3 * Lp / (2 * np.pi) * np.trapezoid(np.exp(-bp * eps), q)


sest = []
for (n, b, label) in [(36, 12.25, "paper seed p0 bounds 1-S(36,49/4) by 0.047916"),
                      (60, 26.25, "paper seed bounds 1-S(60,105/4) by 1/8 (proved >0.8756)"),
                      (72, 24.5, "paper j=1 p bounds 1-S(72,49/2) by 0.0604996"),
                      (2304, 784, "paper j=6 p bounds 1-S(2304,784) by 0.0084513")]:
    v = V_LIT[1.0]
    Lp, bp = v * b, n / v
    est = -math.expm1(magnon_cont_a(Lp, 2 * bp) - 2 * magnon_cont_a(Lp, bp))
    sest.append([n, b, f"{Lp:.2f}", f"{bp:.2f}", f"{est:.3e}", label])
wcsv("magnon_spatial_heuristic.csv", ["n", "b", "rotated L'=v b", "rotated b'=n/v",
                                      "1-S HEURISTIC (rotated magnon gas)", "context"], sest)

# -------------------------------- Euclidean-rotation duality check (spin 1/2, CFT)
# S(n, b) should approximately equal T(L', b') with L' = v b, b' = n / v (v = pi/2), i.e.
# S along beta = c n  <->  T along beta' = c' L' with c' = 1/(v^2 c).
dual_rows = []
v = math.pi / 2
for c in (0.4, 2 / math.pi, 1.0):
    cp = 1 / (v * v * c)
    for n in (6, 8):
        if 2 * n in LS2:
            Sval = spatial_purity(0.5, n, c * n)
            for L in (16, 18):
                if L in LS2:
                    dual_rows.append([f"{c:.4f}", n, f"{c*n:.4f}", f"{Sval:.6f}", f"{cp:.4f}", L, f"{cp*L:.4f}",
                                      f"{thermal_purity(0.5, L, cp*L):.6f}"])
wcsv("rotation_duality_spinhalf.csv", ["c (spatial ray beta=c n)", "n", "beta", "S(n,beta)",
                                       "c'=1/(v^2 c)", "L", "beta'=c'L", "T(L,beta')"], dual_rows)

with open(os.path.join(here, "analysis_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=1)
print(json.dumps(summary, indent=1))
print("available S=1:", available(1.0), "pi:", available(1.0, "pi"), "C:", available(1.0, "2pi3"))
print("available S=1/2:", available(0.5))


# ------------------------- SU(2)_1 WZW (spin-1/2 continuum limit) universal purities
# Normalised torus sum Zt(q) = [(sum_n q^{n^2})^2 + (sum_n q^{(n+1/2)^2})^2] / prod_k (1-q^k)^2,
# q = exp(-2 pi v beta / L), v = pi/2.  T_inf(c) = Zt(q^2)/Zt(q)^2 with q = exp(-pi^2 c) on beta = cL;
# S_inf(c) = T_inf(1/(v^2 c)) on beta = c n (Euclidean rotation / modular S).  Log corrections
# from the marginal operator make lattice convergence slow; this is the L -> infinity target.
def Zt(q):
    ns = np.arange(-40, 41)
    a = np.sum(q ** (ns ** 2.0))
    b = np.sum(q ** ((ns + 0.5) ** 2))
    k = np.arange(1, 400)
    return (a * a + b * b) / np.prod(1 - q ** k) ** 2


def T_cft(c):
    q = math.exp(-math.pi ** 2 * c)
    return Zt(q * q) / Zt(q) ** 2


cft_rows = []
for c in (0.25, 0.5, 2 / math.pi, 1.0, 2.0):
    Tl = {L: thermal_purity(0.5, L, c * L) for L in (12, 18)}
    Sl = {n: spatial_purity(0.5, n, c * n) for n in (4, 8)}
    cft_rows.append([f"{c:.6f}", f"{1-T_cft(c):.4e}", f"{1-Tl[12]:.4e}", f"{1-Tl[18]:.4e}",
                     f"{1-T_cft(1/((math.pi/2)**2*c)):.4e}", f"{1-Sl[4]:.4e}", f"{1-Sl[8]:.4e}"])
wcsv("cft_spinhalf_universal.csv", ["c", "1-T CFT (beta=cL, L->inf)", "1-T lattice L=12", "1-T lattice L=18",
                                    "1-S CFT (beta=cn, n->inf)", "1-S lattice n=4", "1-S lattice n=8"], cft_rows)
