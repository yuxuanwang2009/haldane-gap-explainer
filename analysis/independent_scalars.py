"""Independent exact-rational recomputation of the scalar layer of
'The periodic spin-one Haldane gap' (OpenAI, 2026), Section 'Two finite initializations'.

Written from the formulas in build/initialization.tex and build/bootstrap.tex only
(not by importing the authors' scripts).  Inputs: the thermal centre tables of
Lemma thermal-inputs and the stated error bars.  All assertions are exact Fractions.
"""
from fractions import Fraction as F
from math import log, floor
import numpy as np

def dec(x, k=12):
    return f"{float(x):.{k}g}"

# ---------------- thermal tables (units 1e-6) ----------------
eps49 = F(30, 10**6)
Z49 = {  # n: (Z_n(1), Z_n(P)) at b = 49/4
    4: (124885379, 65757), 5: (2925, 2960742), 6: (12870614, 286599),
    7: (54069, 1920414), 8: (4639283, 510140), 9: (195455, 1514846),
    10: (2654823, 675419), 11: (377629, 1314544), 12: (1900547, 787405)}
Z49 = {n: (F(a, 10**6), F(b, 10**6)) for n, (a, b) in Z49.items()}
eps21 = F(1, 10**5)
Z21 = {6: (8945303, 346734, 939987), 8: (3741281, 567167, 984108),
       10: (2327547, 721090, 1002613)}
Z21 = {n: tuple(F(v, 10**6) for v in t) for n, t in Z21.items()}

# ---------------- character inversion (tetrahedral group A4 = D2 x| C3) -------------
J = {n: (z + 3*p)/4 for n, (z, p) in Z49.items()}
N = {n: (z - p)/4 for n, (z, p) in Z49.items()}
print("b=49/4 sector-moment centres  n : J_n  N_n")
for n in range(4, 13):
    print(f"  {n:2d}: {dec(J[n],9):>12s} {dec(N[n],9):>12s}")

# ---------------- polynomial filters (Lemma polynomial-filter) ----------------
def square_times_x4(c):
    P = [0]*(4 + 2*(len(c)-1) + 1)
    for i, x in enumerate(c):
        for j, y in enumerate(c):
            P[i+j+4] += x*y
    return P

def peval(P, x):
    return sum(F(a)*x**k for k, a in enumerate(P))

QJ = [7, 17, -280, -185, 1000]
QN = [12, 0, -394, 0, 1000]
PJ, PN = square_times_x4(QJ), square_times_x4(QN)
BJ = sum(F(a)*J[k] + abs(a)*eps49 for k, a in enumerate(PJ) if a)
BN = sum(F(a)*N[k] + abs(a)*eps49 for k, a in enumerate(PN) if a)
print("B_J =", BJ, "=", dec(BJ, 15), "  paper: 318604.54848175")
print("B_N =", BN, "=", dec(BN, 15), "  paper: 48169.880699")
assert BJ == F("318604.54848175") and BN == F("48169.880699")
vJ, vN = F(100139, 100000), F(872, 1000)
mJp, mJm = peval(PJ, vJ) - BJ, peval(PJ, -vJ) - BJ
mNp, mNm = peval(PN, vN) - BN, peval(PN, -vN) - BN
print("F_J(+vJ)-B_J =", dec(mJp), " F_J(-vJ)-B_J =", dec(mJm))
print("F_N(+vN)-B_N =", dec(mNp), " F_N(-vN)-B_N =", dec(mNm))
assert mJp > 180 and mJm > 496888 and mNp > 654 and mNm > 654
# exterior monotonicity: Taylor coefficients of Q about +-1, as in the paper
def shift(c, s):  # coefficients of c(s*(1+y)) in y
    from math import comb
    return [sum(comb(i, j)*a*s**i for i, a in enumerate(c) if i >= j) for j in range(len(c))]
assert shift(QJ, 1) == [559, 2902, 5165, 3815, 1000]
assert shift(QJ, -1) == [895, 3978, 6275, 4185, 1000]
print("roots of Q_J:", np.round(np.roots(QJ[::-1]), 4))
print("roots of Q_N (in x):", np.round(np.roots(QN[::-1]), 4))
# where does the B_J budget go?  contribution of a hypothetical lone eigenvalue at 1:
print("F_J(1) =", dec(peval(PJ, F(1))), "  F_J(0.999) =", dec(peval(PJ, F(999, 1000))),
      "  F_J(1.00139) =", dec(peval(PJ, vJ)))

# ---------------- twelfth-moment masses and capped-mass lemma ----------------
mJ = J[12] + eps49
mN = N[12] + eps49
print("m_J =", dec(mJ, 10), " m_N =", dec(mN, 10))
assert mJ == F("1.0657205") and mN == F("0.2783155")

def capped(m, h, r):  # C(m,h,r) = q h^r + (m - q h)^r,  q = floor(m/h);  r integer here
    q = m // h
    return q*h**r + (m - q*h)**r

ell = F(999, 1000)
hN = vN**12
print("v_N^12 =", dec(hN), " floor(m_N / v_N^12) =", mN // hN)
def Bk(k): return 3*capped(mN, hN, k//12)
def RA(k): return Bk(k) + (mJ - ell**12)**(k//12)
no_dominant = capped(mJ, ell**12, 6) + Bk(72)
print("If all |lambda_J|<=0.999:  Z_72(49/4) <=", dec(no_dominant), " margin to 1:", dec(1 - no_dominant))
assert no_dominant < 1 and 1 - no_dominant > F("0.0693")
assert mJ > ell**12 and 2*ell**12 > mJ   # dominant eigenvalue is unique in J
print("B(36) =", dec(Bk(36)), " R_A(36) =", dec(RA(36)), " B(72) =", dec(Bk(72)), " R_A(72) =", dec(RA(72)))
p0 = 1 - (1 + RA(36)/ell**36)**-2
q0 = 1 - (vJ**72 + RA(72))**-2
print("p0 =", dec(p0, 15), "(<0.047916?)", p0 < F("0.047916"))
print("q0 =", dec(q0, 15), "(<0.181521?)", q0 < F("0.181521"))
print("   v_J^72 =", dec(vJ**72), "  ell^36 =", dec(ell**36))
assert p0 < F("0.047916") and q0 < F("0.181521")

# ---------------- six rounded doubling updates ----------------
def f(u):
    assert 0 <= u < 1
    return u*u/(2*(1-u)**2)
def ceil7(x):
    y = x*10**7
    return F(-((-y.numerator)//y.denominator), 10**7)
paper = [(F(151249, 2500000), F(433453, 2500000)), (F(343303, 5000000), F(1632381, 10000000)),
         (F(44601, 625000), F(361773, 2500000)), (F(632939, 10000000), F(1055161, 10000000)),
         (F(375793, 10000000), F(445941, 10000000)), (F(84513, 10000000), F(27493, 5000000))]
p, q = p0, q0
n, b = 36, F(49, 4)
print(f"j=0  (n={n}, 2n={2*n}, b={b})  p={dec(p,8)}  q={dec(q,8)}")
for j in range(1, 7):
    p_exact = f(1 - (1-p)**2*(1-q)); p = ceil7(p_exact)
    q_exact = f(1 - (1-q)**2*(1-p)); q = ceil7(q_exact)
    n, b = 2*n, 2*b
    ok = (p, q) == paper[j-1]
    print(f"j={j}  (n={n}, 2n={2*n}, b={b})  p={p} ({dec(p,7)})  q={q} ({dec(q,7)})  matches paper: {ok}")
    assert ok
assert (n, b) == (2304, 784) and max(p, q) < F(1, 100)

# un-rounded iteration for comparison (floating point: exact Fractions blow up in size,
# which is precisely why the paper rounds to a 1e-7 grid)
pf, qf = float(p0), float(q0)
ff = lambda u: u*u/(2*(1-u)**2)
for j in range(1, 7):
    pf = ff(1 - (1-pf)**2*(1-qf)); qf = ff(1 - (1-qf)**2*(1-pf))
print("unrounded (float) after 6 steps: p =", pf, " q =", qf)

# ---------------- bootstrap constants ----------------
def G(u):
    v = 1 - u
    return (1/v + 1/v**2 + 1/v**3)**2/2
print("G(1/8) =", G(F(1, 8)), " paper: 913952/117649;", G(F(1, 8)) == F(913952, 117649))
assert G(F(1, 8)) == F(913952, 117649) < F(79, 10)
assert 3/(F(79, 10)*(1 - F(3, 8))) == F(48, 79)
print("G(1/100) =", dec(G(F(1, 100))), " <= 45000/9409 =", dec(F(45000, 9409)), "< 5")
assert G(F(1, 100)) <= F(45000, 9409) < 5
assert 3/(5*(1 - F(3, 100))) == F(60, 97)
# check: f(1-(1-u)^3) == G(u) u^2 symbolically at a few rationals
for u in (F(1, 8), F(1, 100), F(3, 17)):
    assert f(1 - (1-u)**3) == G(u)*u*u
print("gap bound row 1: (4/105) log(80/79) =", (4/105)*log(80/79))
print("gap bound row 2: log(20)/784        =", log(20)/784)
# doubly-exponential defect sequence u_j = C^{-1} r^{2^j}
for name, u0, C in (("row1", F(1, 8), F(79, 10)), ("row2", F(1, 100), F(5))):
    r = C*u0
    print(name, "u_j:", [dec(r**(2**j)/C, 4) for j in range(8)])

# ---------------- the length-60 initialization ----------------
I10 = {n: (z + 3*p + 8*c)/12 for n, (z, p, c) in Z21.items()}
O10 = {n: (z + 3*p - 4*c)/12 for n, (z, p, c) in Z21.items()}
N10 = {n: (z - p)/4 for n, (z, p, c) in Z21.items()}
print("b=21/2 sector centres n: I O N")
for n in (6, 8, 10):
    print(f"  {n:2d}: {dec(I10[n],9)} {dec(O10[n],9)} {dec(N10[n],9)}")
mI, mO, mN2 = F(1042655, 10**6), F(40041, 10**6), F(401625, 10**6)
print("margins m - centre - 1e-5 (x 1e6):", (mI - I10[10] - eps21)*10**6, (mO - O10[10] - eps21)*10**6,
      (mN2 - N10[10] - eps21)*10**6)
assert mI - I10[10] - eps21 == F(19, 12*10**6) and mO - O10[10] - eps21 == F(7, 12*10**6)
assert mN2 - N10[10] - eps21 == F(3, 4*10**6)
U, V = F(100245, 100000), F(88643, 100000)
for lab, mom, c0, c1, v in (("I", I10, -2, 10, U), ("N", N10, -25, 100, V)):
    bound = c0*c0*mom[6] + 2*c0*c1*mom[8] + c1*c1*mom[10] + eps21*(abs(c0) + abs(c1))**2
    val = v**6*(c0 + c1*v*v)**2
    print(f"filter {lab}: bound={dec(bound)}  F(v)={dec(val)}  margin={dec(val-bound)}")
assert U**10 < mI < 2*U**10 and V**10 < mN2 < 2*V**10
def A(k): return U**k + (mI - U**10)**(k//10)
def Bo(k): return mO**(k//10)
def Cn(k): return V**k + (mN2 - V**10)**(k//10)
m = A(30) + 2*Bo(30) + 3*Cn(30); pp = A(30) + 2*Bo(30); qq = A(120) + 2*Bo(120) + 3*Cn(120)
D, E, tau, tau0, Rq = F(1450, 1000), F(1202, 1000), F(1225, 1000), F(1264, 1000), F(684, 10000)
print("m =", dec(m), " p =", dec(pp), " q =", dec(qq))
print("margins: D^2-m^5 =", dec(D**2 - m**5), " E^2-p^5 =", dec(E**2 - pp**5), " Rq^2-(q-1)^5 =", dec(Rq**2 - (qq-1)**5))
assert m**5 < D**2 and pp**5 < E**2 and qq >= 1 and (qq-1)**5 < Rq**2
assert (D + 11*E)/12 <= tau and (D + 3*E)/4 <= tau0
assert D*F(88, 100)**3 < 1 and 2*F(88, 100) > D
def R(t):
    verts = [(0, 0), (tau - t, 0), (tau - t, tau0 - tau), (0, tau0 - t)]
    return max(x*x + y*y/2 + (D - t - x - y)**2/3 for x, y in verts)
for t in (F(88, 100), F(99, 100), F(998, 1000)):
    print("R(", t, ") =", dec(R(t)))
print("1-.99^4-R(.88)^2 =", dec(1 - F(99, 100)**4 - R(F(88, 100))**2, 10),
      " 1-.998^4-R(.99)^2 =", dec(1 - F(998, 1000)**4 - R(F(99, 100))**2, 13))
S60 = (1 + R(F(998, 1000))/F(998, 1000)**2)**-2
T120 = (1 + Rq)**-2
print("S(60,105/4) >=", dec(S60), "  T(120,105/4) >=", dec(T120))
assert S60 > F(8756, 10000) > F(7, 8) and T120 > F(8760, 10000) > F(7, 8)
print("ALL INDEPENDENT SCALAR CHECKS PASSED")
