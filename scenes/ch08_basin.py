"""ch08: Getting into the basin.

Isn't this just numerics?  What the computer actually does: low moments of the
spatial transfer operator from small rings, seams as symmetry sectors,
polynomial walls (upper jaw), one integer trial state (lower jaw), the pinch,
the seed bounds, six exact leapfrogs and the payoff numbers; then the weaker
60-site seed and two flagged physicist's readings.

Every seed and update number on screen is a certified UPPER BOUND on a defect.
The gauges show them rounded UP to four decimals (0.0480 for p0 < 0.047916), so
a displayed bound is never smaller than the certified one.

Timing: each voice block is cued to the pauses of its clip (ffmpeg silencedetect
on audio/ch08/*.wav).  Cue times are seconds of the reference clip (REF) and
are rescaled by d / REF[seg].
"""
import csv
import math
from contextlib import contextmanager

import numpy as np

from motifs import *  # noqa: F401,F403
from ch03_why_hard import aklt_cartoon          # the ch03 valence-bond cartoon
from ch04_torus_knives import seam_glyph        # the ch04 SEAM glyph (circular arrow, P)

# clip durations the cue sheets were measured on
REF = {"s01": 18.425, "s02": 12.825, "s03": 15.225, "s04": 16.05, "s05": 14.6,
       "s06": 19.7, "s07": 19.8, "s08": 24.725, "s09": 14.575, "s10": 16.475,
       "s11": 25.025, "s12": 16.9, "s13": 17.95}


# =================================================================== data
def _csv(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


ZTAB = {}                                    # n -> {"1": centre, "P": centre} at beta = 49/4
for _r in _csv("paper_thermal_table_check.csv"):
    if _r["b"] == "12.25":
        ZTAB.setdefault(int(_r["n"]), {})[_r["g"]] = _r["paper_center"]

_SIX = _csv("bootstrap_six_updates.csv")     # the paper's rounded update table
SIX_N = [int(r["n_spatial"]) for r in _SIX]
SIX_B = [r["b"] for r in _SIX]
SIX_P = [float(r["p"]) for r in _SIX]
SIX_Q = [float(r["q"]) for r in _SIX]
P_TXT = ["0.047916"] + [r["p"] for r in _SIX[1:]]   # seed printed as p0 < 0.047916
Q_TXT = ["0.181521"] + [r["q"] for r in _SIX[1:]]   # and q0 < 0.181521
B_TXT = ["12.25", "24.5", "49", "98", "196", "392", "784"]

U60 = [float(r["u_j"]) for r in _csv("bootstrap_dyadic.csv") if r["row"] == "n0=60"]
C60 = 7.9                                    # u_{j+1} = (79/10) u_j^2 for the 60-site seed


def MM(*parts, **kw):
    """Multi-part MathTex (parts can be coloured / revealed separately)."""
    kw.setdefault("color", FG)
    return MathTex(*parts, tex_template=TEX_TEMPLATE, **kw)


def ind_each(group, **kw):
    """Indicate every member in place (a group Indicate would spread them apart)."""
    return AnimationGroup(*[Indicate(m, **kw) for m in group])


def up4(v):
    """Round an upper bound UP to 4 decimals (display never understates a bound)."""
    return math.ceil(v * 1e4 - 1e-9) / 1e4


def appear(mob, **kw):
    """Fade in and STAY (safe inside a Succession: invisible until its turn)."""
    mob.set_opacity(0)

    def upd(m, a):
        m.set_opacity(min(1.0, 2.5 * a))
    return UpdateFromAlphaFunc(mob, upd, **kw)


def knife_walk(vk, bonds, labels):
    """Step the space knife bond by bond; each step leaves a persistent label
    (None = no label) above the site it crossed."""
    steps = []
    for b, lab in zip(bonds, labels):
        mv = vk.to_bond(b, run_time=1.0)
        steps.append(AnimationGroup(mv, appear(lab, run_time=1.0)) if lab is not None else mv)
    return Succession(*steps)


def site_labels(tor, sites, tex="X", font_size=28, color=DIM, dy=0.42):
    """Faint labels above the crossed site columns of a torus."""
    return VGroup(*[M(tex, font_size=font_size, color=color).move_to(
        [tor.site_x(k), tor.top + dy, 0]) for k in sites])


def FN(x):
    """The paper's threefold-sector filter F_N(x) = x^4 (12 - 394 x^2 + 1000 x^4)^2."""
    return x ** 4 * (12 - 394 * x ** 2 + 1000 * x ** 4) ** 2


B_N = 48169.88                               # its budget


# =================================================================== eigenvalue rows
RX0, RX1 = -3.0, 6.0                         # screen x of the rows
YJ, YN = 0.3, -1.0                           # symmetric row, threefold row
YM = (YJ + YN) / 2
FULL = (-1.05, 1.05)
ZOOM = (0.70, 1.01)
J_A = [0.82, 0.55, 0.2, -0.35, -0.7]         # schematic eigenvalues (s03)
N_A = [0.74, 0.4, -0.15, -0.5, -0.8]
J_B = [0.82, 0.47, 0.1, -0.43, -0.76]        # after the shuffle (s05)
N_B = [0.78, 0.31, -0.24, -0.56, -0.79]
QMARK = 0.96                                 # the hollow "is any eigenvalue near 1?" dot


def lx(lam, rng=FULL):
    lo, hi = rng
    return RX0 + (lam - lo) / (hi - lo) * (RX1 - RX0)


def row_line(y):
    return Line([RX0, y, 0], [RX1, y, 0], color=DIM, stroke_width=2)


def jdot(lam, rng=FULL, y=YJ):
    return Dot([lx(lam, rng), y, 0], radius=0.075, color=FG)


def triple(lam, rng=FULL, y=YN, color=SPACE):
    x = lx(lam, rng)
    return VGroup(*[Dot([x, y + dy, 0], radius=0.058, color=color) for dy in (-0.15, 0, 0.15)])


def wall(lam, y, color, rng=FULL, h=0.66, stroke=6):
    x = lx(lam, rng)
    return Line([x, y - h / 2, 0], [x, y + h / 2, 0], color=color, stroke_width=stroke)


def row_ticks(vals, rng, labels=None, y_lab=YN, ys=(YJ, YN)):
    marks = VGroup(*[Line([lx(v, rng), y - 0.07, 0], [lx(v, rng), y + 0.07, 0], color=DIM,
                          stroke_width=2) for v in vals for y in ys])
    labs = VGroup(*[M(s, font_size=24, color=DIM).next_to([lx(v, rng), y_lab - 0.24, 0], DOWN,
                                                          buff=0.04)
                    for v, s in zip(vals, labels or [str(v) for v in vals])])
    return marks, labs


def row_label(text, y, color):
    return T(text, font_size=28, color=color).move_to([RX0 - 0.35, y, 0], aligned_edge=RIGHT)


# =================================================================== small builders
def small_ring(n, radius=0.33):
    circ = Circle(radius=radius, stroke_color=DIM, stroke_width=2)
    dots = VGroup(*[Dot(radius * np.array([np.cos(TAU * k / n + PI / 2),
                                           np.sin(TAU * k / n + PI / 2), 0]),
                        radius=0.042, color=FG) for k in range(n)])
    return VGroup(circ, dots)


def badge(text):
    ck = check_mark(size=0.3, color=GAP, stroke=5)
    t = T(text, font_size=28, color=FG)
    row = VGroup(ck, t).arrange(RIGHT, buff=0.22)
    box = RoundedRectangle(width=row.width + 0.5, height=row.height + 0.34, corner_radius=0.12,
                           stroke_color=GAP, stroke_width=2, fill_color=GAP,
                           fill_opacity=0.05).move_to(row)
    return VGroup(box, row)


def color_tag(text, color, font_size=26):
    """A small rounded tag in a semantic colour ('trial state', 'upper wall')."""
    lab = T(text, font_size=font_size, color=color)
    box = RoundedRectangle(width=lab.width + 0.3, height=lab.height + 0.22, corner_radius=0.1,
                           stroke_color=color, stroke_width=1.5, fill_color=BG,
                           fill_opacity=0.85).move_to(lab)
    return VGroup(box, lab)


def make_stair():
    st = Staircase("real", x_length=5.4, y_length=3.3)
    st.shift(np.array([-5.85, -3.0, 0]) - st.ax.c2p(0, 0))
    return st


def make_gauges():
    """Both gauges start EMPTY (at the 1e-3 floor, number hidden) and rise to their bound."""
    gg = DefectGauges(p=1e-3, q=1e-3, bound=True, one_percent=True)
    gg.shift(np.array([2.55, -1.45, 0]) - gg.p.frame.get_center())
    for g in (gg.p, gg.q):
        g.number.set_opacity(0)
    return gg


def gauge_rise(g, v, **kw):
    """Fill rises from empty to v while the reading fades in and counts up."""
    def upd(m, a):
        m.set_opacity(min(1.0, 4 * a))
    # suspend_mobject_updating=False: the number's own updater must keep counting
    return AnimationGroup(g.set_defect(v), UpdateFromAlphaFunc(g.number, upd),
                          suspend_mobject_updating=False, **kw)


def mps_ring(center, n=18, R=1.3, r=0.095):
    c = np.array(center, dtype=float)
    angs = [PI / 2 - TAU * k / n for k in range(n)]
    pos = [c + R * np.array([np.cos(a), np.sin(a), 0]) for a in angs]
    tens = VGroup(*[Circle(radius=r, stroke_color=FG, stroke_width=2.5, fill_color=BG,
                           fill_opacity=1).move_to(p) for p in pos])
    legs = VGroup(*[Line(c + (R + r) * np.array([np.cos(a), np.sin(a), 0]),
                         c + (R + r + 0.17) * np.array([np.cos(a), np.sin(a), 0]),
                         color=FG, stroke_width=2) for a in angs])
    dth = r / R * 1.05
    bonds = VGroup(*[Arc(radius=R, start_angle=angs[k] - dth, angle=-(TAU / n - 2 * dth),
                         arc_center=c, stroke_color=VIRTUAL, stroke_width=6)
                     for k in range(n)])
    return VGroup(bonds, legs, tens)


# =================================================================== the chapter
class Ch08(NarratedScene):
    CHAPTER = "ch08"

    # ---------------------------------------------------------------- cueing
    @contextmanager
    def seg(self, sid):
        with self.voice(sid) as d:
            self._sid, self._t0, self._k = sid, self.renderer.time, d / REF[sid]
            yield d

    def at(self, t):
        """Wait until t seconds (reference-clip time) into the current clip."""
        target = self._t0 + t * self._k
        now = self.renderer.time
        if target - now > 1e-3:
            self.wait(target - now)
        elif now - target > 0.25:
            print(f"[cue] {self._sid}: {now - target:.2f}s late for cue {t}")

    def rt(self, s):
        return s * self._k

    def present(self, *mobs):
        """The given mobjects (or, for groups not on screen, their members) that are
        currently in the scene; fading anything else would make it flash back."""
        fam = set(self.get_mobject_family_members())
        out = []

        def walk(m):
            if m in fam:
                out.append(m)
            else:
                for sm in m.submobjects:
                    walk(sm)
        for m in mobs:
            walk(m)
        return out

    def construct(self):
        for s in ("s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10",
                  "s11", "s12", "s13"):
            getattr(self, s)()
        self.play(FadeOut(*self.mobjects), run_time=0.8)

    # ---------------------------------------------------------------- s01
    def s01(self):
        st = make_stair()
        seed = st.tromino_at(36, 12.25)
        self.st, self.seed = st, seed
        sites = M(r"36\ \text{and}\ 72\ \text{sites}", font_size=38, color=SPACE)
        beta = M(r"\beta=49/4=12.25", font_size=38, color=TIME)
        top = VGroup(sites, beta).arrange(RIGHT, buff=1.2).move_to([0, 2.7, 0])
        dim = M(r"\dim=3^{72}\approx2.3\times10^{34}", font_size=38, color=DIM)
        dim.move_to([3.2, -1.2, 0])
        cr = cross_mark(size=0.42).next_to(dim, RIGHT, buff=0.35)

        tor = Torus(3.6, 2.0, nx=8, ny=4)
        tor.shift(np.array([-1.5, 0.25, 0]) - tor.rect.get_center())
        vk = space_knife(tor, bond=0)
        xl = site_labels(tor, range(1, 8))
        eq = MM(r"Z_n=\operatorname{Tr}X^n=\sum_i\lambda_i^{\,n}", r",\qquad n=4,\dots,12",
               font_size=42).move_to([-0.6, -2.55, 0])
        eq[1].set_color(DIM)

        box = VGroup(RoundedRectangle(width=1.9, height=1.0, corner_radius=0.14,
                                      stroke_color=SPACE, stroke_width=3, fill_color=SPACE,
                                      fill_opacity=0.12),
                     M(r"X_{49/4}", font_size=42, color=SPACE)).move_to([-1.5, 0.25, 0])
        rings = VGroup(*[small_ring(n) for n in range(4, 13)]).arrange(RIGHT, buff=0.36)
        rings.move_to([-1.5, 2.75, 0])
        rlabs = VGroup(*[M(str(n), font_size=28).next_to(r, DOWN, buff=0.14)
                         for n, r in zip(range(4, 13), rings)])
        top_y = box.get_top()[1] + 0.06
        arrows = VGroup(*[Arrow([r.get_x(), rlabs.get_bottom()[1] - 0.08, 0],
                                [-1.5 + (r.get_x() + 1.5) * 0.16, top_y, 0], buff=0,
                                color=DIM, stroke_width=2.5, tip_length=0.14,
                                max_tip_length_to_length_ratio=0.2) for r in rings])
        tgt = M(r"\operatorname{Tr}X^{36},\ \ \operatorname{Tr}X^{72}\ ?", font_size=42)
        tgt.move_to([4.25, 0.25, 0])
        long = Arrow(box.get_right(), tgt.get_left(), buff=0.25, color=SPACE, stroke_width=4)

        with self.seg("s01"):
            self.play(FadeIn(st), run_time=self.rt(0.5))
            self.play(Create(seed.S), Create(seed.T), FadeIn(seed.dots), run_time=self.rt(0.5))
            self.play(seed.pulse(), run_time=self.rt(0.7))
            self.at(1.6)
            self.play(FadeIn(sites, shift=0.1 * DOWN), run_time=self.rt(0.6))
            self.at(3.44)
            self.play(FadeIn(beta, shift=0.1 * DOWN), run_time=self.rt(0.6))
            self.at(5.49)
            self.play(FadeIn(dim), run_time=self.rt(0.6))
            self.play(Create(cr), run_time=self.rt(0.5))
            # "The rescue is the vertical knife again"
            self.at(7.9)
            self.play(FadeOut(st, seed, top, dim, cr), run_time=self.rt(0.4))
            self.play(FadeIn(tor), run_time=self.rt(0.5))
            self.play(vk.cut_in(), run_time=self.rt(0.6))
            self.play(vk.glow_on(), run_time=self.rt(0.25))
            # "Z of n is the trace of X to the n"
            self.at(10.2)
            self.play(knife_walk(vk, [1, 2, 3, 4, 5, 6, 7], list(xl)),
                      Write(eq[0], run_time=self.rt(1.3)), run_time=self.rt(2.6))
            # "so small rings are low moments ..."
            self.at(13.3)
            self.play(FadeOut(VGroup(tor, vk, xl), scale=0.4, target_position=box.get_center()),
                      FadeIn(box, scale=1.9), run_time=self.rt(0.7))
            self.play(LaggedStart(*[FadeIn(VGroup(r, l), shift=0.15 * DOWN)
                                    for r, l in zip(rings, rlabs)], lag_ratio=0.08),
                      run_time=self.rt(1.1))
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.04),
                      FadeIn(eq[1]), run_time=self.rt(0.7))
            # "... of the very operator whose high moments we need"
            self.at(15.9)
            self.play(GrowArrow(long), run_time=self.rt(0.6))
            self.play(Write(tgt), run_time=self.rt(0.8))
        self.o1 = dict(box=box, rings=rings, rlabs=rlabs, arrows=arrows, tgt=tgt, long=long,
                       eq=eq)

    # ---------------------------------------------------------------- s02
    def s02(self):
        o = self.o1
        b = objection_bubble("numerics")
        ns = list(range(4, 13))
        y0, dy = 1.75, 0.44
        xn, xz, xp = -5.5, -2.75, -0.55
        title = T(r"$\beta=49/4$\quad each value $\pm3\times10^{-5}$", font_size=28,
                  color=DIM).move_to([-3.0, 3.05, 0])
        hdr = VGroup(M("n", font_size=32, color=DIM).move_to([xn, y0 + 0.62, 0]),
                     M(r"Z_n", font_size=32).move_to([xz, y0 + 0.62, 0], aligned_edge=RIGHT),
                     M(r"Z_n(P)", font_size=32).move_to([xp, y0 + 0.62, 0],
                                                        aligned_edge=RIGHT))
        rule = Line([xn - 0.45, y0 + 0.3, 0], [xp + 0.1, y0 + 0.3, 0], color=DIM,
                    stroke_width=1.5)
        nl = VGroup(*[M(str(n), font_size=28).move_to([xn, y0 - i * dy, 0])
                      for i, n in enumerate(ns)])
        vals = VGroup(*[VGroup(M(ZTAB[n]["1"], font_size=28).move_to([xz, y0 - i * dy, 0],
                                                                     aligned_edge=RIGHT),
                               M(ZTAB[n]["P"], font_size=28).move_to([xp, y0 - i * dy, 0],
                                                                     aligned_edge=RIGHT))
                        for i, n in enumerate(ns)])
        badges = VGroup(badge("integer arithmetic"), badge("explicit error bounds"),
                        badge("no floating-point premise")).arrange(DOWN, buff=0.38,
                                                                     aligned_edge=LEFT)
        badges.move_to([3.55, 0.05, 0])
        foot = T(r"27 enclosures: 18 at $\beta=49/4$, 9 at $\beta=21/2$",
                 font_size=26, color=DIM).move_to([3.55, -2.35, 0])

        with self.seg("s02"):
            self.play(FadeOut(o["arrows"], o["box"], o["long"], o["tgt"], o["eq"], o["rings"]),
                      bubble_in(b), ReplacementTransform(o["rlabs"], nl), run_time=self.rt(0.7))
            self.play(bubble_indicate(b), run_time=self.rt(0.8))
            # "Not in the usual sense"
            self.at(1.85)
            self.play(FadeIn(title), FadeIn(hdr), Create(rule), run_time=self.rt(0.7))
            # "rings of four to twelve sites are enclosed ..."
            self.at(3.6)
            self.play(LaggedStart(*[FadeIn(v, shift=0.1 * LEFT) for v in vals], lag_ratio=0.25),
                      run_time=self.rt(2.2))
            self.at(6.0)
            self.play(FadeIn(badges[0], shift=0.15 * UP), run_time=self.rt(0.5))
            self.at(7.65)
            self.play(FadeIn(badges[1], shift=0.15 * UP), run_time=self.rt(0.5))
            self.at(9.5)
            self.play(FadeIn(badges[2], shift=0.15 * UP), run_time=self.rt(0.5))
            self.at(10.6)
            self.play(FadeIn(foot), run_time=self.rt(0.5))
            self.play(bubble_check(b), run_time=self.rt(0.6))
        self.o2 = VGroup(title, hdr, rule, nl, vals, badges, foot)
        self.bub = b

    # ---------------------------------------------------------------- s03
    def s03(self):
        # a ring of 8 sites with a seam at one bond
        rc, R = np.array([-4.5, 1.35, 0]), 1.0
        angs = [TAU * k / 8 + PI / 8 for k in range(8)]
        ring = VGroup(Circle(radius=R, stroke_color=DIM, stroke_width=2).move_to(rc),
                      VGroup(*[Dot(rc + R * np.array([np.cos(a), np.sin(a), 0]), radius=0.075,
                                   color=FG) for a in angs]))
        cut = Line(rc + RIGHT * (R - 0.2), rc + RIGHT * (R + 0.2), color=FG, stroke_width=5)
        sg = seam_glyph().move_to(rc + RIGHT * (R + 0.62))
        ht = T("half turn", font_size=26, color=DIM).next_to(sg, DOWN, buff=0.12)

        tor = Torus(4.2, 2.2, nx=8, ny=4)
        tor.shift(np.array([2.6, 1.3, 0]) - tor.rect.get_center())
        xs = tor.bond_x(6)
        tseam = DashedLine([xs, tor.bottom, 0], [xs, tor.top, 0], color=FG, stroke_width=3,
                           dash_length=0.1)
        tsg = seam_glyph().scale(0.85).next_to([xs, tor.bottom, 0], DOWN, buff=0.12)
        vk = space_knife(tor, bond=1)
        xl = site_labels(tor, range(2, 6))                   # X X X X, persistent
        uplab = M(r"U_P", font_size=36).move_to([xs, tor.top + 0.5, 0])
        zp = MM(r"Z_n(P)=\operatorname{Tr}\big(X^n\,", r"U_P", r"\big)", font_size=40)
        zp.move_to([2.6, -0.85, 0])
        top = MM(r"Z_n=\operatorname{Tr}X^n", r",\qquad", r"Z_n(P)=\operatorname{Tr}\big(X^n\,",
                 r"U_P", r"\big)", font_size=38).move_to([0, 3.05, 0])

        # rows: merged line first, then the split
        mline = row_line(YM)
        mlab = T(r"eigenvalues of $X$", font_size=28).move_to([RX0 - 0.35, YM, 0],
                                                            aligned_edge=RIGHT)
        mJ = VGroup(*[jdot(l, y=YM) for l in J_A])
        mN = VGroup(*[triple(l, y=YM, color=FG) for l in N_A])
        lineJ, lineN = row_line(YJ), row_line(YN)
        dJ = VGroup(*[jdot(l) for l in J_A])
        dN = VGroup(*[triple(l) for l in N_A])
        tmarks, tlabs = row_ticks([-1, 0, 1], FULL, ["-1", "0", "1"])
        labJ = row_label(r"symmetric sector $J$", YJ, FG)
        labN = row_label(r"threefold sector $N$", YN, SPACE)
        sect = MM(r"Z=J+3N,\qquad Z(P)=J-N", r"\qquad(J=I+2O)", font_size=38)
        sect[1].set_color(DIM)
        sect.move_to([0.4, -2.75, 0])
        schem = inline_tag(TAG_SCHEMATIC, Dot([6.3, -1.95, 0]), LEFT, buff=0)
        schem.move_to([5.55, -1.95, 0])

        with self.seg("s03"):
            self.play(FadeOut(self.o2), bubble_out(self.bub), run_time=self.rt(0.5))
            self.play(FadeIn(ring), run_time=self.rt(0.6))
            # "a half-turn spin rotation inserted at one bond"
            self.at(2.05)
            self.play(Create(cut), FadeIn(sg, scale=0.6), run_time=self.rt(0.7))
            self.play(FadeIn(ht), run_time=self.rt(0.4))
            self.at(3.6)
            self.play(Indicate(VGroup(cut, sg), color=FG, scale_factor=1.25), run_time=self.rt(0.8))
            # "Through the vertical knife"
            self.at(5.6)
            self.play(FadeIn(tor), Create(tseam), FadeIn(tsg), run_time=self.rt(0.6))
            self.play(vk.cut_in(), vk.glow_on(), run_time=self.rt(0.5))
            # "the seam becomes a symmetry operator inside the trace"
            self.at(6.95)
            self.play(knife_walk(vk, [2, 3, 4, 5], list(xl)), run_time=self.rt(1.2))
            # the knife reaches the seam: it reads U_P there
            self.play(vk.to_bond(6), FadeIn(uplab, shift=0.15 * DOWN), run_time=self.rt(0.6))
            self.play(Indicate(uplab, color=FG, scale_factor=1.3), Indicate(tsg, color=FG),
                      run_time=self.rt(0.6))
            self.play(Write(zp[0]), Write(zp[2]), TransformFromCopy(uplab, zp[1]),
                      run_time=self.rt(1.0))
            # "splitting the eigenvalues into a symmetric sector"
            self.at(10.5)
            self.play(FadeOut(ring, cut, sg, ht, tor, tseam, tsg, vk, xl, uplab),
                      run_time=self.rt(0.35))
            self.play(ReplacementTransform(zp, VGroup(*top[2:])), FadeIn(top[0]), FadeIn(top[1]),
                      run_time=self.rt(0.5))
            self.play(Create(mline), FadeIn(mJ), FadeIn(mN), FadeIn(mlab), run_time=self.rt(0.5))
            self.play(ReplacementTransform(mline.copy(), lineJ), ReplacementTransform(mline, lineN),
                      ReplacementTransform(mJ, dJ), ReplacementTransform(mN, dN),
                      FadeOut(mlab), FadeIn(labJ), FadeIn(tmarks), FadeIn(tlabs),
                      run_time=self.rt(0.9))
            # "and a sector of triples"
            self.at(13.5)
            self.play(FadeIn(labN), ind_each(dN, color=SPACE, scale_factor=1.25),
                      run_time=self.rt(0.6))
            self.play(Write(sect), FadeIn(schem), run_time=self.rt(0.9))
        self.rows = dict(lineJ=lineJ, lineN=lineN, J=dJ, N=dN, tmarks=tmarks, tlabs=tlabs,
                         labJ=labJ, labN=labN)
        self.o3 = dict(top=top, sect=sect, schem=schem)

    # ---------------------------------------------------------------- s04
    def s04(self):
        r, o = self.rows, self.o3
        yax, PH, FMAX = -2.5, 4.15, 12.0          # plot: F in units of 1e4, y in [0, 12]

        def ys(F):
            return yax + F / 1e4 / FMAX * PH

        nrow = VGroup(r["lineN"], r["N"], r["labN"], r["tlabs"])
        nmarks = VGroup(*[m for i, m in enumerate(r["tmarks"]) if i % 2 == 1])
        jmarks = VGroup(*[m for i, m in enumerate(r["tmarks"]) if i % 2 == 0])
        shift = UP * (yax - YN)
        yaxis = Line([RX0, yax, 0], [RX0, yax + PH + 0.1, 0], color=DIM, stroke_width=2)
        yt = VGroup(*[VGroup(Line([RX0 - 0.07, ys(v * 1e4), 0], [RX0 + 0.07, ys(v * 1e4), 0],
                                  color=DIM, stroke_width=2),
                             M(str(v), font_size=24, color=DIM).next_to(
                                 [RX0 - 0.07, ys(v * 1e4), 0], LEFT, buff=0.12))
                      for v in (4, 8, 12)])
        ylab = M(r"F_N\ \,(10^4)", font_size=28, color=SPACE).move_to(
            [RX0 + 0.15, yax + PH + 0.42, 0], aligned_edge=RIGHT)
        xc = 0.9245
        curve = ParametricFunction(lambda t: np.array([lx(t), ys(min(FN(t), 1.2e5)), 0]),
                                   t_range=[-xc, xc, 0.0025], color=SPACE, stroke_width=4)
        form = M(r"F_N(x)=x^4\big(12-394x^2+1000x^4\big)^2", font_size=34, color=SPACE)
        form.move_to([1.15, 1.15, 0])
        # only the eigenvalues are schematic (F_N and B_N are the paper's): tag the row
        schem4 = tag_box("eigenvalues: schematic").move_to([-0.65, yax - 0.8, 0])
        lams = list(N_A)
        bars = VGroup(*[Line([lx(l), yax, 0], [lx(l), max(ys(FN(l)), yax + 1e-3), 0],
                             color=SPACE, stroke_width=6) for l in lams])
        eq = MM(r"\sum_{\lambda\in N}F_N(\lambda)", r"=\sum_{k=4}^{12}f_k\,N_k", r"\ \le\ B_N",
               r",\qquad N_k=\frac14\big(Z_k-Z_k(P)\big)", font_size=34).move_to([0.2, 3.1, 0])
        eq[3].set_color(DIM)
        budget = DashedLine([RX0, ys(B_N), 0], [RX1, ys(B_N), 0], color=DEFECT, stroke_width=3,
                            dash_length=0.12)
        blab = T(r"budget $B_N$", font_size=28, color=DEFECT).next_to(
            [2.6, ys(B_N), 0], UP, buff=0.12)
        shade = VGroup(*[Rectangle(width=RX1 - lx(0.872), height=PH, stroke_width=0,
                                   fill_color=SX, fill_opacity=0.2)
                         .move_to([(lx(0.872) + RX1) / 2 * s + (1 - s) * (RX0 + lx(-0.872)) / 2,
                                   yax + PH / 2, 0], ) for s in (1, 0)])
        flab = T("forbidden", font_size=28, color=SX).move_to([lx(0.872) + 0.1, yax + PH + 0.28, 0],
                                                            aligned_edge=RIGHT)
        flab.align_to([RX1 + 0.3, 0, 0], RIGHT)
        w872 = M("0.872", font_size=28, color=SPACE).next_to([lx(0.872), yax, 0], DOWN, buff=0.3)
        w872.shift(LEFT * 0.12)

        with self.seg("s04"):
            self.play(FadeOut(r["lineJ"], r["J"], r["labJ"], jmarks, o["top"], o["sect"]),
                      nrow.animate.shift(shift), nmarks.animate.shift(shift),
                      FadeOut(o["schem"]), FadeIn(schem4), run_time=self.rt(0.8))
            schem = schem4
            self.play(Create(yaxis), FadeIn(yt), FadeIn(ylab), run_time=self.rt(0.5))
            # "Next, a polynomial filter"
            self.play(Create(curve), run_time=self.rt(1.3))
            self.play(FadeIn(form, shift=0.1 * UP), run_time=self.rt(0.5))
            # "never negative, and huge beyond some wall"
            self.at(3.7)
            self.play(Indicate(curve, color=FG, scale_factor=1.0), run_time=self.rt(1.0))
            # "Its sum over one sector's eigenvalues ..."
            self.at(5.71)
            self.play(LaggedStart(*[Create(b) for b in bars], lag_ratio=0.15),
                      ind_each(r["N"], color=FG, scale_factor=1.25), run_time=self.rt(0.8))
            self.play(Write(eq[0]), run_time=self.rt(0.8))
            self.at(7.6)
            self.play(Write(eq[1]), FadeIn(eq[3]), run_time=self.rt(1.3))
            # "a fixed budget"
            self.at(10.24)
            self.play(Create(budget), FadeIn(blab), Write(eq[2]), run_time=self.rt(0.8))
            # "If one eigenvalue stood beyond the wall"
            self.at(11.66)
            lt = ValueTracker(lams[0])
            tri, bar0 = r["N"][0], bars[0]
            tri.add_updater(lambda m: m.move_to([lx(lt.get_value()), yax, 0]))

            def upd_bar(m):
                v = lt.get_value()
                F = FN(v)
                m.put_start_and_end_on([lx(v), yax, 0], [lx(v), max(ys(min(F, 1.2e5)), yax + 1e-3), 0])
                m.set_color(interpolate_color(ManimColor(SPACE), ManimColor(SX),
                                              float(np.clip((F - 0.8 * B_N) / (0.4 * B_N), 0, 1))))
            bar0.add_updater(upd_bar)
            self.play(lt.animate.set_value(0.91), run_time=self.rt(1.4),
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(Indicate(budget, color=SX, scale_factor=1.0),
                      Flash([lx(0.91), ys(FN(0.91)), 0], color=SX, line_length=0.25),
                      run_time=self.rt(0.6))
            # "it alone would exceed the budget"
            self.at(14.0)
            self.play(lt.animate.set_value(lams[0]), run_time=self.rt(0.7),
                      rate_func=rate_functions.ease_out_back)
            tri.clear_updaters()
            bar0.clear_updaters()
            self.play(FadeIn(shade), FadeIn(flab), FadeIn(w872), run_time=self.rt(0.6))
        self.o4 = dict(yaxis=yaxis, yt=yt, ylab=ylab, curve=curve, form=form, bars=bars, eq=eq,
                       budget=budget, blab=blab, shade=shade, flab=flab, w872=w872,
                       nrow=nrow, nmarks=nmarks, jmarks=jmarks, schem=schem, shift=shift)

    # ---------------------------------------------------------------- s05
    def s05(self):
        r, o = self.rows, self.o4
        wJ = VGroup(wall(-1.00139, YJ, FG), wall(1.00139, YJ, FG))
        wN = VGroup(wall(-0.872, YN, SPACE), wall(0.872, YN, SPACE))
        lJ = M("1.00139", font_size=28, color=FG).next_to(wJ[1], UP, buff=0.1)
        lN = M("0.872", font_size=28, color=SPACE).next_to(wN[1], UP, buff=0.1)
        yb = lJ.get_top()[1] + 0.1                # the brace clears the 1.00139 label
        brace = Brace(Line([lx(-1.00139), yb, 0], [lx(1.00139), yb, 0]), UP,
                      buff=0.0, color=FG)
        blab = T(r"upper jaw: thermal data of rings $\le12$", font_size=30).next_to(
            brace, UP, buff=0.12)
        qdot = open_circle(radius=0.1, color=FG, stroke=3).move_to([lx(QMARK), YJ, 0])
        qm = M("?", font_size=44, color=DEFECT).move_to([lx(QMARK), YJ + 1.3, 0])
        qtxt = T("is any eigenvalue near 1?", font_size=30).next_to(qm, LEFT, buff=0.3)
        qln = DashedLine(qm.get_bottom() + DOWN * 0.08, qdot.get_top() + UP * 0.06, color=DEFECT,
                         stroke_width=2, dash_length=0.06)
        old_schem = o["schem"]
        schem = tag_box(TAG_SCHEMATIC).move_to([5.55, -1.95, 0])
        self.o4["schem"] = schem

        with self.seg("s05"):
            self.play(FadeOut(o["yaxis"], o["yt"], o["ylab"], o["curve"], o["form"], o["bars"],
                              o["eq"], o["budget"], o["blab"], o["shade"], o["flab"], o["w872"]),
                      o["nrow"].animate.shift(-o["shift"]), o["nmarks"].animate.shift(-o["shift"]),
                      FadeOut(old_schem), run_time=self.rt(0.8))
            self.play(FadeIn(r["lineJ"]), FadeIn(r["J"]), FadeIn(r["labJ"]), FadeIn(o["jmarks"]),
                      FadeIn(schem), run_time=self.rt(0.5))
            # "symmetric eigenvalues below 1.00139 in size"
            self.at(1.8)
            self.play(GrowFromCenter(wJ[0]), GrowFromCenter(wJ[1]), run_time=self.rt(0.7))
            self.at(3.3)
            self.play(FadeIn(lJ, shift=0.1 * DOWN), ind_each(wJ, color=FG, scale_factor=1.3),
                      run_time=self.rt(0.7))
            # "threefold ones below 0.872"
            self.at(6.54)
            self.play(GrowFromCenter(wN[0]), GrowFromCenter(wN[1]), run_time=self.rt(0.7))
            self.play(FadeIn(lN, shift=0.1 * DOWN), run_time=self.rt(0.4))
            # dots shuffle inside their walls
            self.play(*[d.animate.move_to([lx(l), YJ, 0]) for d, l in zip(r["J"], J_B)],
                      *[t.animate.move_to([lx(l), YN, 0]) for t, l in zip(r["N"], N_B)],
                      run_time=self.rt(1.2), rate_func=rate_functions.ease_in_out_sine)
            # "That is the upper jaw."
            self.at(9.82)
            self.play(GrowFromCenter(brace), FadeIn(blab, shift=0.1 * DOWN), run_time=self.rt(0.7))
            # "But purity also needs one eigenvalue to be big."
            self.at(11.44)
            self.play(FadeOut(brace, blab, lJ), run_time=self.rt(0.3))
            self.play(Create(qdot), FadeIn(qm, shift=0.1 * DOWN), Create(qln), run_time=self.rt(0.5))
            self.play(FadeIn(qtxt), run_time=self.rt(0.5))
        self.walls = dict(wJ=wJ, wN=wN, lJ=lJ, lN=lN)
        self.o5 = dict(qdot=qdot, qm=qm, qtxt=qtxt, qln=qln)

    # ---------------------------------------------------------------- s06
    def s06(self):
        r, w, o5 = self.rows, self.walls, self.o5
        rowsall = VGroup(r["lineJ"], r["lineN"], r["J"], r["N"], r["tmarks"], r["tlabs"],
                         r["labJ"], r["labN"], w["wJ"], w["wN"], w["lN"], self.o4["schem"])
        self.rowsall = rowsall
        jaw = T("lower jaw", font_size=36, color=VIRTUAL).move_to([-4.6, 3.25, 0])
        rc = np.array([-3.2, 1.25, 0])
        mps = mps_ring(rc)
        center = VGroup(T("72 sites", font_size=28, color=DIM),
                        T("(18 drawn)", font_size=24, color=DIM)).arrange(DOWN, buff=0.1).move_to(rc)
        mlab = T("matrix product state", font_size=30).move_to([1.6, 2.15, 0], aligned_edge=LEFT)
        dlab = M(r"D=26", font_size=38, color=VIRTUAL).move_to([1.6, 1.4, 0], aligned_edge=LEFT)
        ilab = T("integer entries", font_size=30, color=DIM).move_to([1.6, 0.7, 0],
                                                                    aligned_edge=LEFT)
        hb = mps[0][4].copy().set_stroke(width=12)          # the bond D=26 points at
        darr = Arrow(dlab.get_left() + LEFT * 0.1, hb.get_center() + RIGHT * 0.12, buff=0.05,
                     color=VIRTUAL, stroke_width=3, tip_length=0.16,
                     max_tip_length_to_length_ratio=0.15)

        # zoomed energy-per-bond line
        ELO, EHI, YE = -1.4014845, -1.4014815, -1.35

        def ex(e):
            return -6.0 + (e - ELO) / (EHI - ELO) * 12.0
        eline = Line([-6.0, YE, 0], [6.0, YE, 0], color=DIM, stroke_width=2)
        eticks = VGroup(*[Line([ex(-1.401484 + 1e-6 * k), YE - 0.06, 0],
                               [ex(-1.401484 + 1e-6 * k), YE + 0.06, 0], color=DIM,
                               stroke_width=2) for k in range(3)])
        ecap = T("energy per bond", font_size=28, color=DIM).move_to([-6.0, YE + 0.42, 0],
                                                                    aligned_edge=LEFT)

        def mark(e, color, h=0.44, stroke=5):
            return Line([ex(e), YE - h / 2, 0], [ex(e), YE + h / 2, 0], color=color,
                        stroke_width=stroke)
        E0, ET, EA = -1.401484039, -1.4014821126, -1.401482
        m0, mt, ma = mark(E0, DIM), mark(ET, VIRTUAL), mark(EA, FG)
        v0 = M("-1.401484039", font_size=28, color=DIM).next_to(m0, DOWN, buff=0.15)
        d0 = T(r"true $e_0$ (DMRG)", font_size=26, color=DIM).next_to(v0, DOWN, buff=0.12)
        lit0 = literature_label(d0, RIGHT, buff=0.15)
        vt = M("-1.4014821126", font_size=28, color=VIRTUAL)
        vt.next_to(mt, DOWN, buff=0.15).align_to(mt, RIGHT).shift(LEFT * 0.12)
        dt = T(r"trial state, certified, $L=72$", font_size=26, color=VIRTUAL)
        dt.next_to(vt, DOWN, buff=0.12).align_to(vt, RIGHT)
        va = M("-1.401482", font_size=28).next_to(ma, DOWN, buff=0.15).align_to(ma, LEFT)
        va.shift(RIGHT * 0.12)
        gb = Brace(Line([ex(ET), YE + 0.3, 0], [ex(EA), YE + 0.3, 0]), UP, buff=0.02, color=GAP)
        gl = M(r"\text{below by }1.1\times10^{-7}", font_size=28, color=GAP)
        gl.next_to(gb, UP, buff=0.1).align_to([ex(EA) + 0.6, 0, 0], RIGHT)

        with self.seg("s06"):
            self.play(FadeOut(rowsall, o5["qdot"], o5["qm"], o5["qtxt"], o5["qln"]),
                      run_time=self.rt(0.5))
            self.play(FadeIn(jaw, shift=0.1 * DOWN), run_time=self.rt(0.4))
            self.play(LaggedStart(Create(mps[0]), FadeIn(mps[1]), FadeIn(mps[2]), lag_ratio=0.3),
                      FadeIn(center), run_time=self.rt(1.6))
            # "a matrix product state with bond dimension 26"
            self.at(3.25)
            self.play(FadeIn(mlab, shift=0.1 * LEFT), run_time=self.rt(0.5))
            self.at(5.0)
            self.play(FadeIn(dlab, shift=0.1 * LEFT), GrowArrow(darr), FadeIn(hb),
                      run_time=self.rt(0.6))
            # "and integer entries"
            self.at(6.5)
            self.play(FadeIn(ilab, shift=0.1 * LEFT), run_time=self.rt(0.5))
            # "On 72 sites, its energy per bond"
            self.at(8.19)
            self.play(Create(eline), FadeIn(eticks), FadeIn(ecap), run_time=self.rt(0.8))
            # "is certified below minus 1.401482"
            self.at(9.9)
            self.play(GrowFromCenter(mt), FadeIn(vt), FadeIn(dt), run_time=self.rt(0.7))
            self.at(12.0)
            self.play(GrowFromCenter(ma), FadeIn(va), run_time=self.rt(0.7))
            self.at(13.4)
            self.play(GrowFromCenter(gb), FadeIn(gl), run_time=self.rt(0.7))
            # "just above the true value near minus 1.401484"
            self.at(15.0)
            self.play(GrowFromCenter(m0), FadeIn(v0), FadeIn(d0), run_time=self.rt(0.7))
            self.play(FadeIn(lit0), run_time=self.rt(0.4))
        self.o6 = dict(jaw=jaw, mps=mps, center=center, mlab=mlab, dlab=dlab, ilab=ilab, hb=hb,
                       darr=darr,
                       eline=VGroup(eline, eticks, ecap, m0, mt, ma, v0, d0, lit0, vt, dt, va,
                                    gb, gl),
                       ma=ma, mt=mt, va=va, gb=gb, gl=gl)

    # ---------------------------------------------------------------- s07
    def s07(self):
        o = self.o6
        e1 = MM(r"H_n", r"\ \text{includes}\ ", r"+\tfrac{700741}{500000}\,n=+1.401482\,n",
               font_size=38)
        note = T(r"cancels from $S$, $T$ and the gap", font_size=28, color=DIM)
        e2 = MM(r"E_0(72)<0", r"\ \Longrightarrow\ ", r"Z_{72}(\beta)>1",
               r"\ \text{ for every }\beta", font_size=38)
        e3 = MM(r"\text{all }|\lambda_J|\le0.999", r"\ \Longrightarrow\ ",
               r"Z_{72}(49/4)<1", r"\quad(\text{margin}>0.069)", font_size=38)
        e3[3].set_color(DIM)
        e1.move_to([0, -0.25, 0])
        note.next_to(e1, DOWN, buff=0.3)
        e2.move_to([0, -2.35, 0])
        zero = T("zero of energy, after the constant", font_size=26).next_to(o["ma"], UP, buff=0.95)
        zarr = Arrow(zero.get_bottom(), o["ma"].get_top(), buff=0.1, color=FG,
                     stroke_width=3, tip_length=0.18, max_tip_length_to_length_ratio=0.3)
        up = 3.2
        contra = T("contradiction", font_size=34, color=SX)

        with self.seg("s07"):
            # clear the ring (and the brace) first, then lift the energy line
            self.play(FadeOut(o["jaw"], o["mps"], o["center"], o["mlab"], o["dlab"], o["ilab"],
                              o["hb"], o["darr"], o["gb"], o["gl"]), run_time=self.rt(0.4))
            rest = VGroup(*[m for m in o["eline"] if m is not o["gb"] and m is not o["gl"]])
            self.play(rest.animate.shift(UP * up), run_time=self.rt(0.6))
            zero.shift(UP * up)
            zarr.shift(UP * up)
            # "The constant added to H is exactly 1.401482 per site"
            self.at(1.0)
            self.play(Indicate(o["ma"], color=FG, scale_factor=1.3),
                      FadeIn(zero), GrowArrow(zarr), run_time=self.rt(0.8))
            self.at(2.2)
            self.play(Write(e1), run_time=self.rt(1.8))
            self.play(FadeIn(note, shift=0.1 * UP), run_time=self.rt(0.6))
            # "the trial state's energy is negative"
            self.at(6.42)
            self.play(Indicate(o["mt"], color=VIRTUAL, scale_factor=1.3), Write(e2[0]),
                      run_time=self.rt(1.0))
            # "so Z of 72 exceeds one at every temperature"
            self.at(8.79)
            self.play(Write(e2[1:]), run_time=self.rt(1.1))
            self.play(Indicate(e2[2], color=GAP), run_time=self.rt(0.6))
            # "Yet if every symmetric eigenvalue were at most 0.999"
            self.at(12.66)
            self.play(FadeOut(*self.present(o["eline"], zero, zarr)),
                      VGroup(e1, note).animate.shift(UP * 2.6),
                      e2.animate.shift(UP * 2.0), run_time=self.rt(0.7))
            e3.move_to([0, -1.75, 0])
            self.play(Write(e3[0]), run_time=self.rt(1.0))
            # "the small-ring moments would force it below one"
            self.at(16.97)
            self.play(Write(e3[1:]), run_time=self.rt(1.0))
            contra.move_to([0, -2.85, 0])
            ln = VGroup(SurroundingRectangle(e2[2], color=SX, buff=0.1, corner_radius=0.06),
                        SurroundingRectangle(e3[2], color=SX, buff=0.1, corner_radius=0.06))
            self.play(Create(ln), FadeIn(contra, scale=1.3), run_time=self.rt(0.7))
            self.play(Flash(contra, color=SX, line_length=0.3, flash_radius=1.4),
                      run_time=self.rt(0.6))
        self.o7 = VGroup(e1, note, e2, e3, contra, ln)

    # ---------------------------------------------------------------- s08
    def s08(self):
        r, w = self.rows, self.walls
        # the s05 rows come back, then zoom to [0.70, 1.01]
        qdot = self.o5["qdot"]
        items = ([(d, l) for d, l in zip(r["J"], J_B)] + [(t, l) for t, l in zip(r["N"], N_B)] +
                 [(w["wJ"][0], -1.00139), (w["wJ"][1], 1.00139), (w["wN"][0], -0.872),
                  (w["wN"][1], 0.872), (qdot, QMARK)])
        zmarks, zlabs = row_ticks([0.7, 0.8, 0.9, 1.0], ZOOM, ["0.7", "0.8", "0.9", "1"])
        back = VGroup(r["lineJ"], r["lineN"], r["J"], r["N"], r["tmarks"], r["tlabs"], r["labJ"],
                      r["labN"], w["wJ"], w["wN"], w["lN"], qdot, self.o4["schem"])
        shortJ = M("J", font_size=34).move_to([RX0 - 0.45, YJ, 0])
        shortN = M("N", font_size=34, color=SPACE).move_to([RX0 - 0.45, YN, 0])

        # inset (vise) above the rows
        IL = (0.9965, 1.0035)
        IX0, IX1, IY = 0.75, 6.15, 2.55

        def ix(v):
            return IX0 + (v - IL[0]) / (IL[1] - IL[0]) * (IX1 - IX0)
        frame = RoundedRectangle(width=IX1 - IX0 + 0.4, height=1.65, corner_radius=0.12,
                                 stroke_color=DIM, stroke_width=1.5).move_to(
            [(IX0 + IX1) / 2, IY + 0.05, 0])
        zb = Rectangle(width=lx(IL[1], ZOOM) - lx(IL[0], ZOOM), height=0.5, stroke_color=DIM,
                       stroke_width=1.5).move_to([(lx(IL[0], ZOOM) + lx(IL[1], ZOOM)) / 2, YJ, 0])
        con = VGroup(Line(zb.get_corner(UL), frame.get_corner(DL), color=DIM, stroke_width=1),
                     Line(zb.get_corner(UR), frame.get_corner(DR), color=DIM, stroke_width=1))
        iline = Line([IX0, IY - 0.2, 0], [IX1, IY - 0.2, 0], color=DIM, stroke_width=2)
        jh = 0.42
        ljaw = Rectangle(width=ix(0.999) - IX0, height=jh, stroke_width=0, fill_color=VIRTUAL,
                         fill_opacity=0.85).move_to([(IX0 + ix(0.999)) / 2, IY - 0.2 + jh / 2, 0])
        ujaw = Rectangle(width=IX1 - ix(1.00139), height=jh, stroke_color=FG, stroke_width=2,
                         fill_color=FG, fill_opacity=0.25).move_to(
            [(ix(1.00139) + IX1) / 2, IY - 0.2 + jh / 2, 0])
        lj_t = T("trial state", font_size=26, color=VIRTUAL).next_to(ljaw, UP, buff=0.1).align_to(
            ljaw, RIGHT)
        uj_t = T("filters", font_size=26).next_to(ujaw, UP, buff=0.1).align_to(ujaw, LEFT)
        lj_v = M("0.999", font_size=28, color=VIRTUAL).next_to([ix(0.999), IY - 0.2, 0], DOWN,
                                                              buff=0.1)
        uj_v = M("1.00139", font_size=28).next_to([ix(1.00139), IY - 0.2, 0], DOWN, buff=0.1)
        L0 = 1.0003
        idot = Dot([ix(L0), IY - 0.2 + jh / 2, 0], radius=0.11, color=FG)
        iglow = Dot([ix(L0), IY - 0.2 + jh / 2, 0], radius=0.19, color=FG, fill_opacity=0.12)
        ilab = M(r"\lambda_0", font_size=30).next_to(idot, UP, buff=0.16)
        mtick = Line([lx(0.999, ZOOM), YJ - 0.25, 0], [lx(0.999, ZOOM), YJ + 0.25, 0],
                     color=VIRTUAL, stroke_width=4)

        # twelfth-moment budget mark
        xb = lx(0.808, ZOOM)
        bmark = DashedLine([xb, YJ - 0.35, 0], [xb, YJ + 0.35, 0], color=DIM, stroke_width=3,
                           dash_length=0.06)
        bform = M(r"\big(m_J-0.999^{12}\big)^{1/12}\approx0.81", font_size=34).next_to(
            [xb, YJ + 0.35, 0], UP, buff=0.12)
        bcap = T(r"twelfth-moment budget, after removing $\lambda_0$", font_size=26, color=DIM)
        bcap.move_to([xb + 0.3, YJ - 0.62, 0])

        # 0.872^n crushes the threefold sector
        YB = -2.45
        nt = ValueTracker(1.0)
        bar = Rectangle(width=9 * 0.872, height=0.26, stroke_width=0, fill_color=SPACE,
                        fill_opacity=0.85).move_to([RX0, YB, 0], aligned_edge=LEFT)
        bar.add_updater(lambda m: m.stretch_to_fit_width(max(9 * 0.872 ** nt.get_value(), 1e-3))
                        .move_to([RX0, YB, 0], aligned_edge=LEFT))
        base = M("0.872", font_size=34, color=SPACE)
        expo = Integer(1, font_size=26, color=SPACE)
        powlab = VGroup(base, expo)
        base.move_to([RX0 - 1.25, YB - 0.04, 0])
        expo.next_to(base, UR, buff=0.03).shift(DOWN * 0.12)
        expo.add_updater(lambda m: m.set_value(int(round(nt.get_value()))).next_to(
            base, UR, buff=0.03).shift(DOWN * 0.12))
        crushed = M(r"0.872^{72}\approx5\times10^{-5}", font_size=36, color=SPACE)
        crushed.move_to([RX0, YB, 0], aligned_edge=LEFT).shift(LEFT * 1.75)

        # the seed on the staircase
        st, seed = self.st, self.seed
        gg = make_gauges()
        self.gg = gg
        sform = M(r"1-S(36,49/4)\ \le\ p_0\ <\ 0.047916", font_size=38, color=SPACE)
        sform.move_to([0, 2.75, 0])
        ptmp = T("basin edge", font_size=24, color=DEFECT).next_to(gg.p.basin, RIGHT, buff=0.12)

        with self.seg("s08"):
            self.play(FadeOut(self.o7), run_time=self.rt(0.4))
            self.play(FadeIn(back), run_time=self.rt(0.5))
            # zoom the rows to [0.70, 1.01]
            anims = []
            for mob, lam in items:
                x0, x1 = lx(lam, FULL), lx(lam, ZOOM)
                if RX0 - 1e-6 <= x1 <= RX1 + 0.3:
                    anims.append(mob.animate.shift(RIGHT * (x1 - x0)))
                else:
                    anims.append(FadeOut(mob, shift=RIGHT * (RX0 - 0.3 - x0)))
            self.play(*anims, FadeOut(r["tmarks"], r["tlabs"], w["lN"]),
                      FadeIn(zmarks), FadeIn(zlabs),
                      FadeOut(r["labJ"]), FadeOut(r["labN"]), FadeIn(shortJ), FadeIn(shortN),
                      run_time=self.rt(1.0))
            self.play(Create(zb), Create(con), FadeIn(frame), Create(iline), FadeIn(mtick),
                      run_time=self.rt(0.6))
            # "pinched between 0.999"
            self.play(FadeIn(ljaw, shift=RIGHT * 0.8), FadeIn(lj_t), FadeIn(lj_v),
                      run_time=self.rt(0.6))
            # "and 1.00139"
            self.at(4.02)
            self.play(FadeIn(ujaw, shift=LEFT * 0.8), FadeIn(uj_t), FadeIn(uj_v),
                      run_time=self.rt(0.6))
            solid = Dot([lx(L0, ZOOM), YJ, 0], radius=0.09, color=FG)
            self.play(ReplacementTransform(qdot, solid), FadeIn(iglow), GrowFromCenter(idot),
                      FadeIn(ilab), run_time=self.rt(0.7))
            # "the twelfth-moment budget leaves no room for a second symmetric one near one"
            self.at(6.46)
            self.play(Create(bmark), FadeIn(bform, shift=0.1 * DOWN), run_time=self.rt(0.8))
            self.play(FadeIn(bcap), run_time=self.rt(0.5))
            self.at(8.6)
            self.play(r["J"][0].animate.move_to([lx(0.755, ZOOM), YJ, 0]), run_time=self.rt(1.0),
                      rate_func=rate_functions.ease_in_out_sine)
            # "The threefold ones are crushed"
            self.at(11.12)
            self.play(Indicate(w["wN"][1], color=SPACE, scale_factor=1.3),
                      Indicate(r["N"][0], color=FG, scale_factor=1.2), run_time=self.rt(0.7))
            # "0.872 to the 72nd power"
            self.at(12.91)
            self.add(bar, powlab)
            self.play(FadeIn(bar), FadeIn(powlab), run_time=self.rt(0.3))
            self.play(nt.animate.set_value(72), run_time=self.rt(2.5),
                      rate_func=rate_functions.ease_in_out_sine)
            # "is about five in a hundred thousand"
            self.at(16.0)
            bar.clear_updaters()
            expo.clear_updaters()
            self.play(FadeOut(powlab), FadeOut(bar), FadeIn(crushed), run_time=self.rt(0.6))
            # "The seed:"
            self.at(18.0)
            self.play(FadeOut(*self.present(
                r["lineJ"], r["lineN"], r["J"], r["N"], w["wJ"], w["wN"], zmarks, zlabs, shortJ,
                shortN, frame, zb, con, iline, ljaw, ujaw, lj_t, uj_t, lj_v, uj_v, idot, iglow,
                ilab, mtick, solid, bmark, bform, bcap, crushed, self.o4["schem"])),
                run_time=self.rt(0.5))
            self.play(FadeIn(st), FadeIn(seed), run_time=self.rt(0.6))
            # "a spatial defect certified below 0.048 at 36 sites"
            self.at(19.56)
            self.play(Write(sform), Indicate(seed.S, color=SPACE, scale_factor=1.15),
                      run_time=self.rt(1.0))
            self.play(FadeIn(gg.p), FadeIn(ptmp), run_time=self.rt(0.5))
            self.play(gauge_rise(gg.p, up4(SIX_P[0])), run_time=self.rt(1.3),
                      rate_func=rate_functions.ease_in_out_sine)
        self.o8 = dict(sform=sform, ptmp=ptmp)

    # ---------------------------------------------------------------- s09
    def s09(self):
        o, gg, seed = self.o8, self.gg, self.seed
        frac = M(r"T(72,\beta)=\frac{Z_{72}(2\beta)}{Z_{72}(\beta)^2}", font_size=38,
                 color=TIME).move_to([-4.35, 2.75, 0])
        a1 = M(r"Z_{72}(2\beta)>1", font_size=34).move_to([-2.0, 3.2, 0], aligned_edge=LEFT)
        t1 = color_tag("trial state", VIRTUAL).next_to(a1, RIGHT, buff=0.3)
        a2 = M(r"Z_{72}(\beta)\le1.00139^{72}+\text{tail}\approx1.105", font_size=34)
        a2.move_to([-2.0, 2.3, 0], aligned_edge=LEFT)
        t2 = color_tag("upper wall", FG).next_to(a2, RIGHT, buff=0.3)
        r1 = M(r"\Rightarrow\ T(72,\beta)\ \ge\ \frac{1}{1.105^2}\approx0.82", font_size=34,
               color=TIME)
        r2 = M(r"\Rightarrow\ \ 1-T(72,49/4)\ \le\ q_0\ <\ 0.181521", font_size=34,
               color=TIME)
        VGroup(r1, r2).arrange(RIGHT, buff=0.6).move_to([0.1, 1.35, 0])

        with self.seg("s09"):
            self.play(FadeOut(o["sform"]), run_time=self.rt(0.4))
            self.play(Write(frac), run_time=self.rt(1.0))
            # "Z of 72 is above one at doubled beta"
            self.at(2.34)
            self.play(FadeIn(a1, shift=0.1 * LEFT), run_time=self.rt(0.6))
            self.play(FadeIn(t1), run_time=self.rt(0.4))
            # "but the wall caps it only near 1.1 at beta"
            self.at(5.63)
            self.play(FadeIn(a2, shift=0.1 * LEFT), run_time=self.rt(0.8))
            self.play(FadeIn(t2), run_time=self.rt(0.4))
            # "so the thermal defect at 72 sites"
            self.at(8.9)
            self.play(Write(r1), run_time=self.rt(1.0))
            self.play(Write(r2), Indicate(seed.T, color=TIME, scale_factor=1.15),
                      run_time=self.rt(1.0))
            # "is bounded only by about 0.18"
            self.at(12.15)
            self.play(FadeOut(o["ptmp"]), FadeIn(gg.q), run_time=self.rt(0.4))
            self.play(gauge_rise(gg.q, up4(SIX_Q[0])), run_time=self.rt(0.9),
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(pulse(gg.q.fill), Indicate(gg.q.basin, color=DEFECT), run_time=self.rt(0.6))
        self.o9 = VGroup(frac, a1, t1, a2, t2, r1, r2)

    # ---------------------------------------------------------------- update table
    def table(self):
        x0, dx = -2.95, 1.42
        ys = [3.3, 2.8, 2.15, 1.6]
        heads = VGroup(M("n", font_size=30, color=SPACE), M(r"\beta", font_size=30, color=TIME),
                       M(r"1-S(n,\beta)\le", font_size=30, color=SPACE),
                       M(r"1-T(2n,\beta)\le", font_size=30, color=TIME))
        for h, y in zip(heads, ys):
            h.move_to([x0 - 0.8, y, 0], aligned_edge=RIGHT)
        cols = VGroup()
        for j in range(7):
            x = x0 + j * dx
            cols.add(VGroup(M(str(SIX_N[j]), font_size=28).move_to([x, ys[0], 0]),
                            M(B_TXT[j], font_size=28).move_to([x, ys[1], 0]),
                            M(P_TXT[j], font_size=28, color=SPACE).move_to([x, ys[2], 0]),
                            M(Q_TXT[j], font_size=28, color=TIME).move_to([x, ys[3], 0])))
        rule = Line([-6.3, 2.48, 0], [6.3, 2.48, 0], color=FAINT, stroke_width=1.5)
        return heads, cols, rule

    def climb_step(self, j, cols, worse_lab=None):
        """One leapfrog of the seed tromino + column j of the table + gauges."""
        gg = self.gg
        anims = [self.seed.step(), FadeIn(cols[j], shift=0.12 * DOWN),
                 gg.set_defects(p=up4(SIX_P[j]), q=up4(SIX_Q[j]))]
        return anims

    # ---------------------------------------------------------------- s10
    def s10(self):
        gg = self.gg
        heads, cols, rule = self.table()
        self.tab = (heads, cols, rule)
        exact = T(r"\textit{exact rational arithmetic}", font_size=26, color=DIM)
        exact.move_to([6.35, 0.98, 0], aligned_edge=RIGHT)
        worse = VGroup(Arrow(DOWN * 0.3, UP * 0.3, buff=0, color=DEFECT, stroke_width=4,
                             tip_length=0.15, max_tip_length_to_length_ratio=0.35),
                       T("bound worse", font_size=26, color=DEFECT)).arrange(RIGHT, buff=0.1)

        with self.seg("s10"):
            # "That is too big for the clean recursion"
            self.play(pulse(gg.q.fill), Indicate(gg.q.basin, color=DEFECT),
                      Indicate(gg.q.number, color=DEFECT), run_time=self.rt(0.9))
            # "so the paper first runs the leapfrog six times"
            self.at(2.55)
            self.play(FadeOut(self.o9), run_time=self.rt(0.5))
            self.play(FadeIn(heads), Create(rule), FadeIn(cols[0]), run_time=self.rt(0.8))
            # "in exact arithmetic"
            self.at(5.61)
            self.play(FadeIn(exact), run_time=self.rt(0.5))
            # three updates; the spatial bound gets worse
            for j, t in ((1, 6.3), (2, 9.9), (3, 11.8)):
                self.at(t)
                self.play(*self.climb_step(j, cols), run_time=self.rt(1.3))
                worse.next_to(gg.p.frame, LEFT, buff=0.15).set_y(
                    gg.p._y(defect_frac(gg.p.value)))
                self.play(Indicate(cols[j][2], color=DEFECT, scale_factor=1.2),
                          FadeIn(worse, shift=0.15 * UP), run_time=self.rt(0.45))
                self.play(FadeOut(worse), run_time=self.rt(0.15))
            # "as the loose thermal bound leaks into it"
            self.at(13.86)
            self.play(Indicate(VGroup(*[c[3] for c in cols[:4]]), color=TIME, scale_factor=1.1),
                      Indicate(gg.q.fill, color=TIME), run_time=self.rt(0.8))
            self.play(Indicate(VGroup(*[c[2] for c in cols[:4]]), color=DEFECT, scale_factor=1.1),
                      run_time=self.rt(0.7))
        self.exact = exact

    # ---------------------------------------------------------------- s11
    def s11(self):
        gg = self.gg
        heads, cols, rule = self.tab
        last = cols[6]
        inp = MM(r"(n_0,\beta_0)=(2304,\,784)", r",\qquad u_0=1/100,\qquad C=5,\qquad "
                 r"r=Cu_0=1/20", font_size=34).move_to([0, 3.3, 0])
        # (n_0, beta_0) is the recursion's new starting point, not the seed's beta = 49/4
        inote = T("new start for the recursion", font_size=26, color=DIM).next_to(
            inp[0], DOWN, buff=0.16)
        thm = MM(r"\text{every even }L\ge2304{:}", r"\quad\gamma_L>\frac{\log20}{784}",
                r"\approx3.82\times10^{-3}", font_size=40, color=GAP).move_to([0, 1.7, 0])
        thm[0].set_color(FG)
        tbox = SurroundingRectangle(thm, color=GAP, buff=0.22, corner_radius=0.1)

        with self.seg("s11"):
            # "Then both bounds collapse."
            for j in (4, 5, 6):
                self.play(*self.climb_step(j, cols), run_time=self.rt(0.95))
            # "At beta 784"
            self.at(3.0)
            self.play(Indicate(last[1], color=TIME, scale_factor=1.25), run_time=self.rt(0.7))
            # "the spatial defect at 2304 sites is below 0.0085"
            self.at(5.4)
            self.play(Indicate(last[0], color=SPACE, scale_factor=1.25), run_time=self.rt(0.7))
            self.at(7.9)
            bp = SurroundingRectangle(last[2], color=SPACE, buff=0.08, corner_radius=0.06)
            self.play(Create(bp), Indicate(gg.p.number, color=SPACE), run_time=self.rt(0.7))
            # "and the thermal one, on the doubled ring, below 0.0055"
            self.at(12.6)
            bq = SurroundingRectangle(last[3], color=TIME, buff=0.08, corner_radius=0.06)
            self.play(Create(bq), Indicate(gg.q.number, color=TIME), run_time=self.rt(0.7))
            # "under one percent"
            self.at(15.04)
            self.play(Indicate(gg.p.pct, color=GAP, scale_factor=1.2),
                      Indicate(gg.q.pct, color=GAP, scale_factor=1.2), run_time=self.rt(0.6))
            self.play(gg.p.recolor(GAP), gg.q.recolor(GAP), run_time=self.rt(0.7))
            # "the one in a hundred we started from" (u0 = 1/100 of ch06)
            self.at(16.3)
            self.play(Indicate(gg.p.pct[1], color=GAP, scale_factor=1.5),
                      Indicate(gg.q.pct[1], color=GAP, scale_factor=1.5), run_time=self.rt(0.9))
            # "With r one twentieth"
            self.at(18.4)
            self.play(FadeOut(heads, cols, rule, bp, bq, self.exact), run_time=self.rt(0.5))
            self.play(FadeIn(inp, shift=0.1 * DOWN), FadeIn(inote, shift=0.1 * DOWN),
                      run_time=self.rt(0.7))
            # "every even ring from there on has a gap above log 20 over 784"
            self.at(20.08)
            self.play(Write(thm), run_time=self.rt(1.8))
            self.play(Create(tbox), run_time=self.rt(0.6))
        self.o11 = dict(inp=VGroup(inp, inote), thm=thm, tbox=tbox)

    # ---------------------------------------------------------------- s12
    def s12(self):
        o, gg, st, seed = self.o11, self.gg, self.st, self.seed
        alt = st.tromino_at(60, 26.25, style="alt")
        alab = VGroup(T("second seed", font_size=28, color=DEFECT),
                      T(r"rings 6, 8, 10; trial state on 120 sites", font_size=26, color=DIM))
        alab.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        alab.next_to(alt, RIGHT, buff=0.3).align_to(alt.S, DOWN).shift(DOWN * 0.05)
        thm = o["thm"]
        th60 = MM(r"\text{every even }L\ge60{:}", r"\quad\gamma_L>\tfrac{4}{105}\log\tfrac{80}{79}",
                  r"\approx4.79\times10^{-4}", font_size=40, color=GAP)
        th60[0].set_color(FG)
        uniq = T(r"unique ground state on every even ring (Marshall--Lieb--Mattis)",
                 font_size=28)

        # cobweb inset: u_{j+1} = (79/10) u_j^2, start 1/8, basin edge 0.127 (equal x/y scales)
        sc = 3.0 / 0.14
        ax = Axes(x_range=[0, 0.15, 0.05], y_range=[0, 0.14, 0.05], x_length=0.15 * sc,
                  y_length=3.0, tips=False,
                  axis_config={"color": DIM, "stroke_width": 2, "include_ticks": True,
                               "tick_size": 0.05})
        ax.shift(np.array([1.75, -2.85, 0]) - ax.c2p(0, 0))
        xl = M(r"u_j", font_size=28, color=DIM).next_to(ax.x_axis.get_end(), RIGHT, buff=0.12)
        yl = M(r"u_{j+1}", font_size=28, color=DIM).next_to(ax.y_axis.get_end(), UP, buff=0.1)
        tk = VGroup(M("0.05", font_size=24, color=DIM).next_to(ax.c2p(0.05, 0), DOWN, buff=0.12),
                    M("0.1", font_size=24, color=DIM).next_to(ax.c2p(0.10, 0), DOWN, buff=0.12))
        diag = Line(ax.c2p(0, 0), ax.c2p(0.14, 0.14), color=DIM, stroke_width=2)
        cmax = math.sqrt(0.14 / C60)
        cur = ax.plot(lambda u: C60 * u * u, x_range=[0, cmax], color=DEFECT, stroke_width=4)
        edge = DashedLine(ax.c2p(0.127, 0), ax.c2p(0.127, 0.14), color=DEFECT, stroke_width=3,
                          dash_length=0.08)
        elab = T(r"basin edge $\approx0.127$", font_size=24, color=DEFECT).next_to(
            ax.c2p(0.127, 0.14), UP, buff=0.1)
        u0d = Dot(ax.c2p(U60[0], 0), radius=0.075, color=DEFECT)
        u0d.set_stroke(DIM, width=3, background=True)
        # label below-right of the dot (clear of the 0.1 tick label), with a short leader
        u0l = M(r"u_0=1/8", font_size=28, color=DEFECT)
        u0l.next_to(ax.c2p(U60[0], 0) + DOWN * 0.42, DOWN, buff=0).align_to(
            ax.c2p(U60[0], 0) + LEFT * 0.3, LEFT)
        u0ln = Line(ax.c2p(U60[0], 0) + DOWN * 0.09, [ax.c2p(U60[0], 0)[0], u0l.get_top()[1] + 0.04, 0],
                    color=DEFECT, stroke_width=1.5)
        # cobweb: the first rise (at 0.125, next to the 0.127 edge) is drawn thin
        p0 = ax.c2p(U60[0], 0)
        rise = Line(p0, ax.c2p(U60[0], U60[1]), color=GAP, stroke_width=2)
        cob = VGroup(Line(ax.c2p(U60[0], U60[1]), ax.c2p(U60[1], U60[1]), color=GAP,
                          stroke_width=3))
        pts = [ax.c2p(U60[1], U60[1])]
        for a, b in zip(U60[1:-1], U60[2:]):
            seg = VMobject(stroke_color=GAP, stroke_width=3)
            seg.set_points_as_corners([pts[-1], ax.c2p(a, b), ax.c2p(b, b)])
            pts.append(ax.c2p(b, b))
            cob.add(seg)
        inset = VGroup(ax, xl, yl, tk, diag, cur, edge, elab)

        with self.seg("s12"):
            # the first seed's bounds leave with it: the new tromino has its own (1/8)
            self.play(FadeOut(o["inp"], gg.p, gg.q), seed.animate.fade(0.65),
                      run_time=self.rt(0.4))
            # "A second seed"
            self.play(Create(alt.S), Create(alt.T), FadeIn(alt.dots), run_time=self.rt(0.7))
            self.play(alt.pulse(), FadeIn(alab[0]), run_time=self.rt(0.6))
            # "from rings of six to ten sites and the trial state on 120 sites"
            self.at(1.6)
            self.play(FadeIn(alab[1]), run_time=self.rt(0.6))
            # "starts with bounds of one eighth"
            self.at(5.97)
            self.play(FadeIn(ax), FadeIn(xl), FadeIn(yl), FadeIn(tk), Create(diag), Create(cur),
                      run_time=self.rt(0.8))
            self.play(GrowFromCenter(u0d), Create(u0ln), FadeIn(u0l), run_time=self.rt(0.5))
            # "barely inside the basin"
            self.at(7.74)
            self.play(Create(edge), FadeIn(elab), run_time=self.rt(0.6))
            self.play(edge.animate.set_stroke(opacity=0.45), Create(rise), run_time=self.rt(0.3),
                      rate_func=linear)
            for k, sgm in enumerate(cob):
                self.play(Create(sgm), run_time=self.rt(0.15 if k == 0 else
                                                        (0.2 if k < 6 else 0.3)),
                          rate_func=linear)
            # "a weaker floor of 0.000479"
            self.at(10.2)
            th60.move_to([0, 3.0, 0])
            colon_x = thm[0].get_right()[0]
            th60.shift(RIGHT * (colon_x - th60[0].get_right()[0]))
            dx = -VGroup(th60, thm).get_center()[0]
            th60.shift(RIGHT * dx)
            sh = RIGHT * dx + UP * (1.95 - thm.get_y())
            uniq.move_to([0, 1.12, 0])
            thm_to = thm.copy().shift(sh)
            nbox = SurroundingRectangle(VGroup(th60, thm_to), color=GAP, buff=0.22,
                                        corner_radius=0.1)
            nbox2 = SurroundingRectangle(VGroup(th60, thm_to, uniq), color=GAP, buff=0.22,
                                         corner_radius=0.1)
            self.play(thm.animate.shift(sh), Transform(o["tbox"], nbox), run_time=self.rt(0.5))
            self.play(Write(th60), run_time=self.rt(1.4))
            # uniqueness on even rings is classical (Marshall-Lieb-Mattis); listed, not new
            self.play(Transform(o["tbox"], nbox2), FadeIn(uniq, shift=0.1 * UP),
                      run_time=self.rt(0.6))
            # "but for every even ring from 60 sites on"
            self.at(13.96)
            self.play(Indicate(th60[0], color=GAP, scale_factor=1.1), run_time=self.rt(0.9))
        self.o12 = VGroup(alt, alab, th60, thm, o["tbox"], uniq, inset, u0d, u0l, u0ln, rise, cob)

    # ---------------------------------------------------------------- s13
    def s13(self):
        tg = tag(TAG_READING)
        # left: the 0.872 wall vs the true correlation length
        LO, HI, X0, X1, Y = 0.80, 0.90, -6.1, -1.1, 0.55

        def zx(v):
            return X0 + (v - LO) / (HI - LO) * (X1 - X0)
        head = T("threefold sector", font_size=30, color=SPACE).move_to([-3.6, 2.6, 0])
        line = Line([X0, Y, 0], [X1, Y, 0], color=DIM, stroke_width=2)
        ticks = VGroup(*[VGroup(Line([zx(v), Y - 0.07, 0], [zx(v), Y + 0.07, 0], color=DIM,
                                     stroke_width=2),
                                M(s, font_size=24, color=DIM).next_to([zx(v), Y, 0], DOWN,
                                                                     buff=0.18))
                         for v, s in ((0.8, "0.80"), (0.9, "0.90"))])
        w = Line([zx(0.872), Y - 0.4, 0], [zx(0.872), Y + 0.4, 0], color=SPACE, stroke_width=6)
        wl = VGroup(M("0.872", font_size=28, color=SPACE),
                    T("certified wall", font_size=26, color=SPACE)).arrange(DOWN, buff=0.08,
                                                                           aligned_edge=LEFT)
        wl.next_to(w, RIGHT, buff=0.15).align_to(w, UP).shift(UP * 0.45)
        lt = Line([zx(0.847), Y, 0], [zx(0.847), Y + 0.32, 0], color=DIM, stroke_width=4)
        ll = M(r"e^{-1/\xi},\ \xi\approx6", font_size=28, color=DIM).next_to(lt, UP, buff=0.12)
        ll.shift(LEFT * 0.35)
        lit = literature_label(ll, UP, buff=0.08)
        cap = MM(r"e^{-1/\xi(T)}\lesssim0.872", r"\ \ \Rightarrow\ \ \xi(T)\lesssim7\ \text{sites}",
                 font_size=34).move_to([-3.6, -0.75, 0])
        sub = T(r"(at $\beta=49/4$; threefold sector $\leftrightarrow$ spin correlations)",
                font_size=26, color=DIM).move_to([-3.6, -1.45, 0])

        # right: the trial state's bond opens into half-integer spin blocks
        ta = Circle(radius=0.16, stroke_color=FG, stroke_width=2.5, fill_color=BG,
                    fill_opacity=1).move_to([1.4, 2.35, 0])
        tb = ta.copy().move_to([3.8, 2.35, 0])
        bond = Line(ta.get_right(), tb.get_left(), color=VIRTUAL, stroke_width=8)
        legs = VGroup(*[Line(t.get_bottom(), t.get_bottom() + DOWN * 0.25, color=FG,
                             stroke_width=2) for t in (ta, tb)])
        dl = M(r"D=26", font_size=32, color=VIRTUAL).next_to(bond, UP, buff=0.12)
        dims = [2, 2, 2, 2, 4, 4, 4, 6]
        u, gap = 0.12, 0.06
        blocks = VGroup()
        y = 1.55
        for k, dm in enumerate(dims):
            h = dm * u
            op = 0.85 if dm == 2 else (0.55 if dm == 4 else 0.3)
            blk = Rectangle(width=0.75, height=h, stroke_color=VIRTUAL, stroke_width=1.5,
                            fill_color=VIRTUAL, fill_opacity=op).move_to([2.6, y - h / 2, 0])
            blocks.add(blk)
            y -= h + gap
        groups = [VGroup(*blocks[0:4]), VGroup(*blocks[4:7]), VGroup(blocks[7])]
        glabs = VGroup()
        for g, tex, wt in zip(groups, [r"4\times\ j=\tfrac12", r"3\times\ j=\tfrac32",
                                       r"1\times\ j=\tfrac52"],
                              [r"97\%", r"3\%", r"\sim0.001\%"]):
            br = Brace(g, RIGHT, buff=0.1, color=DIM)
            lab = M(tex, font_size=30, color=VIRTUAL).next_to(br, RIGHT, buff=0.12)
            wtl = M(wt, font_size=28, color=DIM).next_to(lab, RIGHT, buff=0.35)
            glabs.add(VGroup(br, lab, wtl))
        eq = M(r"26=4\cdot2+3\cdot4+1\cdot6", font_size=34).move_to([3.7, -2.55, 0])
        cart = aklt_cartoon(8)
        cart.scale(0.55).move_to([0.0, -3.3, 0])
        cart.fade(0.65)

        with self.seg("s13"):
            self.play(FadeOut(*self.mobjects), run_time=self.rt(0.6))
            self.play(tag_in(tg), run_time=self.rt(0.5))
            # "the 0.872 wall caps the correlation length here near seven sites"
            self.at(2.92)
            self.play(FadeIn(head), Create(line), FadeIn(ticks), run_time=self.rt(0.6))
            self.play(GrowFromCenter(w), FadeIn(wl), run_time=self.rt(0.6))
            self.at(5.0)
            self.play(Write(cap), FadeIn(sub), run_time=self.rt(1.0))
            # "against a true value near six"
            self.at(7.97)
            self.play(GrowFromCenter(lt), FadeIn(ll), FadeIn(lit), run_time=self.rt(0.8))
            # "and the trial state's bonds carry only half-integer spins"
            self.at(10.09)
            self.play(FadeIn(ta), FadeIn(tb), FadeIn(legs), Create(bond), FadeIn(dl),
                      run_time=self.rt(0.6))
            self.play(LaggedStart(*[GrowFromPoint(b, bond.get_center()) for b in blocks],
                                  lag_ratio=0.08), run_time=self.rt(1.0))
            self.play(LaggedStart(*[FadeIn(VGroup(g[0], g[1])) for g in glabs], lag_ratio=0.3),
                      run_time=self.rt(0.8))
            self.play(LaggedStart(*[FadeIn(g[2]) for g in glabs], lag_ratio=0.3),
                      run_time=self.rt(0.6))
            # "valence-bond physics, smuggled in through an energy bound"
            self.at(13.79)
            self.play(Write(eq), FadeIn(cart), run_time=self.rt(1.0))
