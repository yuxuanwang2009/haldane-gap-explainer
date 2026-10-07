"""ch07 -- From purity to a gap.

s01  doubly exponential in steps = plain exponential in beta   (data/bootstrap_dyadic.csv, n0=2304)
s02  interpolation between dyadic lengths (paper Fig. 1, eqs. 4.15-4.16)
s03  the gap step (4.17)
s04  take logs: gamma_L > log(1/r)/beta_0
s05  the doubling machine never used spin; objection (f)
s06  Prop. 3.1 is spin 1 only; scale invariance at a critical point (physicist's reading)
s07  the seesaw; ED along beta = L (thermal_purity_ray.csv, spatial_purity_ray.csv)
s08  SU(2)_1 torus calculation (ours): best balance 0.545, outside the basin
"""
import csv
from contextlib import contextmanager

import numpy as np

from motifs import *  # noqa: F401,F403

# Cue times (seconds into each clip, read off the pauses of the narration audio).
# They are rescaled by d / D_REF so that a regenerated clip keeps the cues in place.
D_REF = {"s01": 14.2, "s02": 18.075, "s03": 14.425, "s04": 14.175, "s05": 15.125,
         "s06": 18.175, "s07": 23.75, "s08": 16.95}


def MM(*parts, **kw):
    """MathTex built from several top-level parts (each must compile on its own)."""
    kw.setdefault("color", FG)
    return MathTex(*parts, tex_template=TEX_TEMPLATE, **kw)


def TT(*parts, **kw):
    """Tex built from several parts (for colouring words separately)."""
    kw.setdefault("color", FG)
    return Tex(*parts, tex_template=TEX_TEMPLATE, **kw)


def read_rows(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------ SU(2)_1 torus function (our calculation)
def _zc(q):
    n = np.arange(-30, 31)
    th3 = np.sum(q ** (n ** 2.0))
    th2 = np.sum(q ** ((n + 0.5) ** 2))
    k = np.arange(1, 400)
    eta = q ** (1 / 24) * np.prod(1 - q ** k)
    return (th3 ** 2 + th2 ** 2) / eta ** 2


def cft_spatial_defect(rho):
    """1 - S(n, beta) at aspect rho = v beta / n."""
    q = np.exp(-2 * np.pi * rho)
    return 1 - _zc(q ** 0.5) / _zc(q) ** 2


def cft_thermal_defect(rho):
    """1 - T(L, beta) at aspect rho = v beta / L."""
    q = np.exp(-2 * np.pi * rho)
    return 1 - _zc(q ** 2) / _zc(q) ** 2


def cft_pair(rho):
    """The bootstrap's pair at (n, beta): spatial at n, thermal at 2n (aspect rho/2)."""
    return cft_spatial_defect(rho), cft_thermal_defect(rho / 2)


# ------------------------------------------------ a plain 2D plot frame
class Plot2D(VGroup):
    """Axes drawn as an L at the lower-left corner of the data box (never through 0).

    x_range / y_range are in mapped coordinates (e.g. log10 values); p(x, y) takes
    data values and applies xmap / ymap.  Positions follow the axes after any move.
    """

    def __init__(self, x_range, y_range, x_length, y_length, xticks=(), yticks=(),
                 xmap=None, ymap=None, tick_size=24, tick_color=FG, color=DIM, stroke=2,
                 xlabel=None, ylabel=None):
        super().__init__()
        self.xr, self.yr = x_range, y_range
        self.xmap = xmap or (lambda v: v)
        self.ymap = ymap or (lambda v: v)
        self.x_axis = Line(ORIGIN, RIGHT * x_length, color=color, stroke_width=stroke)
        self.y_axis = Line(ORIGIN, UP * y_length, color=color, stroke_width=stroke)
        self.axes = VGroup(self.x_axis, self.y_axis)
        self.xtick_marks, self.xtick_labels = VGroup(), VGroup()
        self.ytick_marks, self.ytick_labels = VGroup(), VGroup()
        for v, tex in xticks:
            pt = self.p(v, None)
            self.xtick_marks.add(Line(pt, pt + DOWN * 0.09, color=color, stroke_width=stroke))
            lab = M(tex, font_size=tick_size, color=tick_color) if tex else VMobject()
            self.xtick_labels.add(lab.next_to(pt, DOWN, buff=0.17))
        for v, tex in yticks:
            pt = self.p(None, v)
            self.ytick_marks.add(Line(pt, pt + LEFT * 0.09, color=color, stroke_width=stroke))
            lab = M(tex, font_size=tick_size, color=tick_color) if tex else VMobject()
            self.ytick_labels.add(lab.next_to(pt, LEFT, buff=0.17))
        self.add(self.axes, self.xtick_marks, self.ytick_marks, self.xtick_labels,
                 self.ytick_labels)
        self.xlabel, self.ylabel = xlabel, ylabel
        if xlabel is not None:
            xlabel.next_to(self.x_axis.get_end(), RIGHT, buff=0.2)
            self.add(xlabel)
        if ylabel is not None:
            ylabel.next_to(self.y_axis.get_end(), UP, buff=0.2)
            self.add(ylabel)

    def u(self, X, Y):
        o = self.x_axis.get_start()
        ex = self.x_axis.get_end() - o
        ey = self.y_axis.get_end() - self.y_axis.get_start()
        fx = 0.0 if X is None else (X - self.xr[0]) / (self.xr[1] - self.xr[0])
        fy = 0.0 if Y is None else (Y - self.yr[0]) / (self.yr[1] - self.yr[0])
        return o + fx * ex + fy * ey

    def p(self, x, y):
        return self.u(None if x is None else self.xmap(x), None if y is None else self.ymap(y))

    def curve(self, f, x0, x1, n=240, **kw):
        """Polyline through (X, f(X)) in mapped x coordinates."""
        xs = np.linspace(x0, x1, n)
        m = VMobject(**kw)
        m.set_points_smoothly([self.u(X, f(X)) for X in xs])
        return m

    def move_origin_to(self, pt):
        self.shift(np.array(pt) - self.x_axis.get_start())
        return self


def strike(mob, color=DEFECT, stroke=5):
    """Diagonal strike-through for cancelled factors."""
    return Line(mob.get_corner(DL) + DL * 0.05, mob.get_corner(UR) + UR * 0.05,
                color=color, stroke_width=stroke)


def torus_morph(old, new):
    """Animations turning Torus `old` into Torus `new`: the frame and chevrons morph,
    the grid cross-fades (different line counts would swing diagonally mid-morph), and a
    relabelled side (2L -> L) fades out then in, so the two labels never overlap.
    Afterwards `new` is the torus on screen."""
    anims = [ReplacementTransform(old.rect, new.rect),
             ReplacementTransform(old.chev_time, new.chev_time),
             ReplacementTransform(old.chev_space, new.chev_space),
             FadeTransform(old.grid, new.grid)]
    for a, b, key in ((old.L_label, new.L_label, "L_tex"),
                      (old.beta_label, new.beta_label, "beta_tex")):
        same = old.dims[key] == new.dims[key]
        anims.append(ReplacementTransform(a, b) if same else Succession(FadeOut(a), FadeIn(b)))
    return anims


def lane_arrow(a, b, color, dashed=False):
    if dashed:
        ln = DashedLine(a, b, color=color, stroke_width=4, dash_length=0.1)
        return ln.add_tip(tip_length=0.2, tip_width=0.2)
    return Arrow(a, b, buff=0, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.25,
                 tip_length=0.2)


class Ch07(NarratedScene):
    CHAPTER = "ch07"

    # ------------------------------------------------------------ timing helpers
    @contextmanager
    def seg(self, sid, **kw):
        with self.voice(sid, **kw) as d:
            self._t0 = self.renderer.time
            self._k = d / D_REF[sid]
            yield d

    def until(self, t):
        """Wait until cue t (seconds into the clip, as measured on the reference audio)."""
        dt = self._t0 + t * self._k - self.renderer.time
        if dt > 1 / 30:
            self.wait(dt)

    # ------------------------------------------------------------ chapter
    def construct(self):
        self.s01()
        self.s02()
        self.s03()
        self.s04()
        self.s05()
        self.s06()
        self.s07()
        self.s08()
        self.play(FadeOut(*self.mobjects), run_time=1.0)
        self.wait(0.3)

    # ------------------------------------------------------------ s01
    def s01(self):
        rows = [r for r in read_rows("bootstrap_dyadic.csv")
                if r["row"] == "n0=2304" and int(r["j"]) <= 5]
        J = np.array([int(r["j"]) for r in rows])
        LU = np.array([float(r["log10_u_j"]) for r in rows])
        a0, a1 = np.log10(1 / 5), np.log10(1 / 20)      # u_j = C^-1 r^(2^j), C = 5, r = 1/20
        assert np.allclose(a0 + a1 * 2.0 ** J, LU)
        self.u_line = (a0, a1)

        yt = [(-k, rf"10^{{-{k}}}" if k else r"10^{0}") for k in (0, 10, 20, 30, 40)]
        origin = np.array([-4.7, -2.85, 0])

        def ylab():
            return T(r"defect $u_j$", font_size=32, color=DEFECT)
        fa = Plot2D((0, 5.5), (-45, 0), 9.6, 5.0, xticks=[(j, str(j)) for j in range(6)],
                    yticks=yt, xlabel=T(r"step $j$", font_size=32), ylabel=ylab())
        fa.move_origin_to(origin)
        fb = Plot2D((0, 34), (-45, 0), 9.6, 5.0,
                    xticks=[(k, rf"{k}\beta_0") for k in (8, 16, 24, 32)], yticks=yt,
                    tick_color=TIME, xlabel=M(r"\beta", font_size=40, color=TIME),
                    ylabel=ylab())
        fb.move_origin_to(origin)

        dots = VGroup(*[Dot(fa.p(j, y), radius=0.085, color=DEFECT) for j, y in zip(J, LU)])
        curve_a = ParametricFunction(lambda t: fa.p(t, a0 + a1 * 2 ** t), t_range=[0, 5, 0.02],
                                     color=DEFECT, stroke_width=3, stroke_opacity=0.55)
        curve_b = ParametricFunction(lambda t: fb.p(2 ** t, a0 + a1 * 2 ** t),
                                     t_range=[0, 5, 0.02], color=DEFECT, stroke_width=3,
                                     stroke_opacity=0.55)
        bnote = M(r"\beta_j=2^j\beta_0", font_size=40, color=TIME).move_to(fa.p(0.95, -37))

        with self.seg("s01") as d:
            self.play(Create(fa.axes), FadeIn(fa.xtick_marks, fa.ytick_marks, fa.xtick_labels,
                                              fa.ytick_labels, fa.xlabel, fa.ylabel),
                      run_time=0.9)
            self.play(LaggedStart(*[GrowFromCenter(dt) for dt in dots], lag_ratio=0.25),
                      Create(curve_a), run_time=1.6)
            self.until(3.3)
            self.play(Write(bnote), run_time=1.0)
            self.until(5.4)
            # old tick labels leave in the first half, new ones arrive in the second, so
            # the two sets never sit on top of each other; the axis label cross-fades
            self.play(*[ApplyMethod(dt.move_to, fb.p(2 ** j, y)) for dt, j, y in zip(dots, J, LU)],
                      Transform(curve_a, curve_b),
                      Succession(FadeOut(fa.xtick_labels, shift=0.1 * DOWN),
                                 FadeIn(fb.xtick_labels, shift=0.1 * UP)),
                      Transform(fa.xtick_marks, fb.xtick_marks),
                      Succession(FadeOut(fa.xlabel), FadeIn(fb.xlabel)), run_time=2.2)
            # slope triangle: a fixed rate
            xA, xB = 20, 28
            pA, pB = fb.p(xA, a0 + a1 * xA), fb.p(xB, a0 + a1 * xB)
            corner = np.array([pB[0], pA[1], 0])
            tri = VGroup(DashedLine(pA, corner, color=DIM, stroke_width=2.5, dash_length=0.08),
                         DashedLine(corner, pB, color=DIM, stroke_width=2.5, dash_length=0.08))
            rate_lab = T("fixed rate", font_size=30, color=GAP).next_to(tri[1], RIGHT, buff=0.15)
            self.until(7.7)
            self.play(Create(tri), FadeIn(rate_lab, shift=0.1 * LEFT), run_time=0.8)
            cap = M(r"u_j\approx e^{-\beta_j\cdot\text{rate}}", font_size=46)
            cap[0][0:2].set_color(DEFECT)
            cap[0][5:7].set_color(TIME)
            cap[0][8:12].set_color(GAP)
            cap.move_to(fb.p(24.5, -8.0))
            self.until(8.95)
            self.play(Write(cap), run_time=1.1)
            bz = M(r"\text{Boltzmann:}\ \ e^{-\beta\cdot\text{gap}}", font_size=40)
            bz[0][0:10].set_color(DIM)
            bz[0][12].set_color(TIME)
            bz[0][14:17].set_color(GAP)
            bz.next_to(cap, DOWN, buff=0.45).align_to(cap, RIGHT)
            self.until(10.3)
            self.play(FadeIn(bz, shift=0.1 * UP), run_time=0.9)
            self.until(11.8)
            self.play(Indicate(cap[0][8:12], color=GAP, scale_factor=1.25),
                      Indicate(bz[0][14:17], color=GAP, scale_factor=1.25), run_time=1.1)
        self.s01_mobs = VGroup(fa.axes, fa.xtick_marks, fa.ytick_marks, fa.ytick_labels,
                               fb.xlabel, fa.ylabel, fb.xtick_labels, dots, curve_a, bnote, tri,
                               rate_lab, cap, bz)

    # ------------------------------------------------------------ s02
    def s02(self):
        st = Staircase("symbolic", x_length=5.6, y_length=3.6)
        st.move_to([-3.55, 0.55, 0])
        f1 = st.fig1(0, 0, k=3)
        bars, arrows, dots, ilab = f1
        z = MM(r"Z_L^{1/L}", "=", r"\Big(\sum_i", r"|\lambda_i|^{L}", r"\Big)^{1/L}",
               font_size=44)
        z[3][1:3].set_color(SPACE)
        z.move_to([3.45, 1.75, 0])
        zlab = T(r"decreases as even $L$ grows", font_size=30).next_to(z, DOWN, buff=0.35)
        zsub = T(r"$\lambda_i$: spatial eigenvalues", font_size=28, color=SPACE)
        zsub.next_to(z, UP, buff=0.3)
        # "the spatial reading helps again": a brief callback of the vertical knife
        ktor = Torus(2.6, 1.6, nx=4, labels=False).move_to(z)
        knife = space_knife(ktor, bond=0)
        ineq = MM(r"T(L,\beta)", r"\ \ge\ ", r"\big[T(2n,\beta)\,", r"S(n,\beta)^2",
                  r"\big]^{L/2n}", r"\ \ge\ ", r"(1-u)^3", r"\ \ge\ ", r"1-3u", font_size=40)
        ineq[0].set_color(TIME)
        ineq[2][1:].set_color(TIME)
        ineq[3].set_color(SPACE)
        ineq[6][3].set_color(DEFECT)
        ineq[8][3].set_color(DEFECT)
        ineq.move_to([0, -2.55, 0])
        cond = T(r"$n\le L\le 2n$, \ $L$ even", font_size=28, color=DIM).next_to(ineq, DOWN,
                                                                                 buff=0.25)
        # a marker that hops along the bottom bar (n -> 2n at height beta), exactly the
        # range written under the inequality; its label rides above the bar, clear of
        # 'interpolate' below it (a BG outline keeps it legible over the dashed arrow)
        p0, p1 = st.pt(0, 0), st.pt(1, 0)
        tick = Line(p0 + DOWN * 0.07, p0 + UP * 0.3, color=SPACE, stroke_width=6)
        Lm = M("L", font_size=32, color=SPACE).next_to(tick, UP, buff=0.08)
        Lm.set_stroke(BG, width=6, background=True)
        mark = VGroup(tick, Lm)

        with self.seg("s02") as d:
            self.play(FadeOut(self.s01_mobs), run_time=0.6)
            self.play(FadeIn(st), run_time=0.6)
            self.play(LaggedStart(*[GrowFromCenter(dt) for dt in dots], lag_ratio=0.3),
                      LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.5), run_time=1.1)
            self.until(2.94)
            self.play(LaggedStart(*[Create(b) for b in bars], lag_ratio=0.3),
                      FadeIn(ilab, shift=0.1 * UP), run_time=1.4)
            self.until(4.15)
            self.play(FadeIn(ktor), knife.cut_in(), run_time=0.7)
            self.play(knife.sweep(to=ktor.bond_frac(2)), run_time=0.7)
            self.until(5.72)
            self.play(FadeOut(ktor, knife), run_time=0.45)
            self.until(6.3)
            self.play(Write(z), run_time=1.8)
            self.until(8.85)
            self.play(FadeIn(zsub, shift=0.1 * DOWN), run_time=0.7)
            self.until(10.7)
            self.play(FadeIn(zlab, shift=0.1 * UP), run_time=0.8)
            self.until(12.85)
            hop = (p1 - p0) / 6
            self.play(FadeIn(mark), run_time=0.3)
            self.play(Succession(*[ApplyMethod(mark.shift, hop, run_time=0.3) for _ in range(6)]),
                      Write(ineq, run_time=1.8),
                      bars[0].animate(rate_func=there_and_back).set_stroke(color=SPACE,
                                                                           opacity=1),
                      run_time=1.8)
            self.play(FadeIn(cond, shift=0.1 * UP), run_time=0.5)
            self.until(15.35)
            three = SurroundingRectangle(VGroup(ineq[6], ineq[8]), color=DEFECT, buff=0.1,
                                         stroke_width=2.5)
            x3 = T(r"factor of $3$", font_size=28, color=DEFECT).next_to(three, UP, buff=0.12)
            self.play(Create(three), FadeIn(x3, shift=0.1 * DOWN), run_time=0.9)
        self.s02_mobs = VGroup(st, f1, z, zlab, zsub, cond, mark, three, x3)
        self.s02_ineq = ineq

    # ------------------------------------------------------------ s03
    def s03(self):
        eq = MM(r"e^{-\beta_j\gamma_L}", r"\ \le\ ", r"\frac{3u_j}{1-3u_j}", r"\ <\ ", r"r^{2^j}",
                font_size=56)
        eq[0][2:4].set_color(TIME)
        eq[0][4:6].set_color(GAP)
        eq[2][1:3].set_color(DEFECT)
        eq[2][7:9].set_color(DEFECT)
        eq.move_to(UP * 0.85)
        gl = T("gap", font_size=28, color=GAP).next_to(eq[0][4:6], UP, buff=0.12)
        br = Brace(eq[2], DOWN, buff=0.12, color=DIM)
        br_lab = T(r"$\approx 3\times$ defect", font_size=30, color=DIM).next_to(br, DOWN, 0.1)
        ujn = M(r"u_j=C^{-1}\,r^{2^j}", font_size=36)
        ujn[0][0:2].set_color(DEFECT)
        ujn.next_to(eq[4], DOWN, buff=0.75).shift(RIGHT * 0.35)
        bj = MM(r"\beta_j", "=", r"2^j", r"\beta_0", font_size=56)
        bj[0].set_color(TIME)
        bj[3].set_color(TIME)
        bj.move_to(DOWN * 2.25)
        prem = MM(r"T(L,\beta_j)", r"\ \ge\ ", r"1-3u_j", font_size=44)
        prem[0].set_color(TIME)
        prem[2][3:5].set_color(DEFECT)
        prem.move_to(UP * 2.85)
        imp = M(r"\Downarrow", font_size=40, color=DIM).move_to(UP * 2.2)

        ineq = self.s02_ineq
        prem0 = MM(r"T(L,\beta)", r"\ \ge\ ", r"1-3u", font_size=44)
        prem0[0].set_color(TIME)
        prem0[2][3].set_color(DEFECT)
        prem0.move_to(prem)
        with self.seg("s03") as d:
            # clear the staircase and the unused middle of the inequality first, then
            # carry only the matching pieces T(L,beta) >= 1-3u up to the top ...
            self.play(FadeOut(self.s02_mobs), FadeOut(*[ineq[i] for i in range(2, 8)]),
                      run_time=0.55)
            self.play(ReplacementTransform(ineq[0], prem0[0]),
                      ReplacementTransform(ineq[1], prem0[1]),
                      ReplacementTransform(ineq[8], prem0[2]), run_time=0.8)
            # ... and on "At step j" they pick up their subscripts
            self.until(1.72)
            self.play(TransformMatchingShapes(prem0, prem), run_time=0.5)
            self.play(FadeIn(imp, shift=0.15 * DOWN), run_time=0.35)
            self.until(2.6)
            self.play(Write(eq[0]), run_time=0.9)
            self.play(FadeIn(gl, shift=0.1 * DOWN), run_time=0.5)
            self.until(4.5)
            self.play(Write(eq[1]), Write(eq[2]), run_time=1.1)
            self.until(6.0)
            self.play(GrowFromCenter(br), FadeIn(br_lab, shift=0.1 * UP), run_time=0.8)
            self.until(7.7)
            self.play(Write(eq[3]), Write(eq[4]), run_time=1.0)
            self.until(9.3)
            self.play(FadeIn(ujn, shift=0.1 * UP), run_time=0.8)
            self.until(11.45)
            self.play(Write(bj), run_time=1.4)
        self.s03_eq, self.s03_bj = eq, bj
        self.s03_extra = VGroup(gl, br, br_lab, ujn, prem, imp)

    # ------------------------------------------------------------ s04
    def s04(self):
        eq, bj = self.s03_eq, self.s03_bj
        # the chain with its middle removed: e^{-beta_j gamma_L} < r^{2^j}
        eqC = MM(r"e^{-\beta_j\gamma_L}", r"\ <\ ", r"r^{2^j}", font_size=56)
        eqC[0][2:4].set_color(TIME)
        eqC[0][4:6].set_color(GAP)
        eqC.move_to(UP * 0.85)
        eqL = MM(r"\beta_j", r"\gamma_L", r"\ >\ ", r"2^j", r"\log(1/r)", font_size=56)
        eqL[0].set_color(TIME)
        eqL[1].set_color(GAP)
        eqL.move_to(UP * 0.85)
        eqS = MM(r"2^j\,", r"\beta_0", r"\gamma_L", r"\ >\ ", r"2^j", r"\log(1/r)", font_size=56)
        eqS[1].set_color(TIME)
        eqS[2].set_color(GAP)
        eqS.move_to(UP * 0.85)
        eqR = MM(r"\gamma_L", r"\ >\ ", r"\frac{\log(1/r)}{\beta_0}", font_size=60, color=GAP)
        eqR.move_to(UP * 0.85)
        ev = T(r"for every even $L\ge n_0$", font_size=36, color=GAP)
        ev.next_to(eqR, DOWN, buff=0.4)
        res = VGroup(eqR, ev)
        box = SurroundingRectangle(res, color=GAP, buff=0.3, corner_radius=0.12, stroke_width=3)

        # the straight line from s01, back as a small sketch: log u_j against beta
        a0, a1 = np.log(1 / 5), np.log(1 / 20)
        mp = Plot2D((0, 46), (-140, 0), 3.9, 2.6,
                    xlabel=M(r"\beta", font_size=36, color=TIME),
                    ylabel=M(r"\log u_j", font_size=34, color=DEFECT))
        mp.move_origin_to([2.05, -1.75, 0])
        mdots = VGroup(*[Dot(mp.p(2 ** j, a0 + a1 * 2 ** j), radius=0.06, color=DEFECT)
                         for j in range(6)])
        mline = Line(mp.p(0, a0), mp.p(32, a0 + a1 * 32), color=DEFECT, stroke_width=3,
                     stroke_opacity=0.7)
        mfwd = DashedLine(mp.p(32, a0 + a1 * 32), mp.p(45, a0 + a1 * 45), color=DEFECT,
                          stroke_width=3, dash_length=0.07).add_tip(tip_length=0.16,
                                                                     tip_width=0.14)
        slope = MM(r"\text{slope}=-", r"\frac{\log(1/r)}{\beta_0}", font_size=34)
        slope[1].set_color(GAP)
        slope.move_to([5.05, 0.6, 0])

        with self.seg("s04") as d:
            # 1. drop the middle term (and the s03 annotations), then close the gap:
            #    e^{-beta_j gamma_L} < r^{2^j}
            self.play(FadeOut(self.s03_extra), FadeOut(eq[1], eq[2]), run_time=0.4)
            self.play(ReplacementTransform(eq[0], eqC[0]), ReplacementTransform(eq[3], eqC[1]),
                      ReplacementTransform(eq[4], eqC[2]), run_time=0.45)
            # 2. take logs, one piece after another: the exponent beta_j gamma_L comes down
            #    to the left and the inequality flips; the 2^j exponent comes down; r becomes
            #    log(1/r)
            lt = eqC[1].copy().rotate(PI, axis=UP).move_to(eqL[2])
            self.until(1.1)
            self.play(LaggedStart(
                AnimationGroup(FadeOut(eqC[0][0:2], shift=0.25 * UP, run_time=0.45),
                               ReplacementTransform(eqC[0][2:4], eqL[0]),
                               ReplacementTransform(eqC[0][4:6], eqL[1]),
                               Transform(eqC[1], lt)),
                ReplacementTransform(eqC[2][1:3], eqL[3]),
                AnimationGroup(ReplacementTransform(eqC[2][0], eqL[4][6]),
                               FadeIn(eqL[4][0:6], eqL[4][7])),
                lag_ratio=0.45), run_time=1.15)
            self.remove(eqC[1])
            self.add(eqL[2])
            # 3. hold beta_j gamma_L > 2^j log(1/r), then substitute beta_j = 2^j beta_0
            self.until(2.85)
            self.play(FadeOut(eqL[0], shift=0.25 * UP),
                      TransformFromCopy(VGroup(bj[2], bj[3]), VGroup(eqS[0], eqS[1])),
                      ReplacementTransform(eqL[1], eqS[2]), ReplacementTransform(eqL[2], eqS[3]),
                      ReplacementTransform(eqL[3], eqS[4]), ReplacementTransform(eqL[4], eqS[5]),
                      run_time=0.5)
            # 4. the powers of two cancel
            s1, s2 = strike(eqS[0]), strike(eqS[4])
            self.play(Create(s1), Create(s2), run_time=0.35)
            self.play(FadeOut(eqS[0], eqS[4], s1, s2), run_time=0.25)
            # beta_0 dips under the line into the denominator
            self.play(FadeOut(bj),
                      ReplacementTransform(eqS[2], eqR[0]), ReplacementTransform(eqS[3], eqR[1]),
                      ReplacementTransform(eqS[5], eqR[2][0:8]),
                      ReplacementTransform(eqS[1], eqR[2][9:11], path_arc=0.9),
                      FadeIn(eqR[2][8]), run_time=0.9)
            self.until(5.75)
            self.play(FadeIn(ev, shift=0.1 * UP), Create(box), run_time=0.9)
            # 4. "One rate, certified at the starting scale, bounds the gap forever."
            self.until(9.25)
            grp = VGroup(res, box)
            self.play(grp.animate.move_to([-3.0, 0.1, 0]), run_time=0.5)
            self.play(Create(mp.axes), FadeIn(mp.xlabel, mp.ylabel),
                      LaggedStart(*[GrowFromCenter(m) for m in mdots], lag_ratio=0.15),
                      Create(mline), Indicate(eqR[2], color=FG, scale_factor=1.08),
                      run_time=0.8)
            # the slope label is the same expression, carried over from the box
            self.play(FadeIn(slope[0], shift=0.1 * LEFT),
                      TransformFromCopy(eqR[2], slope[1], path_arc=1.2), run_time=0.7)
            self.until(12.4)
            self.play(Create(mfwd), box.animate(rate_func=there_and_back).set_stroke(width=8),
                      run_time=1.0)
        self.s04_mobs = VGroup(grp, mp.axes, mp.xlabel, mp.ylabel, mdots, mline, mfwd, slope)

    # ------------------------------------------------------------ s05
    def s05(self):
        box = RoundedRectangle(width=8.0, height=3.2, corner_radius=0.2, stroke_color=FG,
                               stroke_width=2.5, fill_color=FG, fill_opacity=0.03)
        box.move_to([-0.2, -0.45, 0])
        title = T("doubling machine", font_size=36).next_to(box, UP, buff=0.22).align_to(box,
                                                                                         LEFT)
        spin_tag = tag_box("spin", font_size=32).next_to(title, RIGHT, buff=0.45)
        # a thin red strike, drawn a beat after the word has been read
        spin_strike = Line(spin_tag.label.get_left() + LEFT * 0.08,
                           spin_tag.label.get_right() + RIGHT * 0.08, color=SX, stroke_width=2.5)
        icons = VGroup(icon_torus(), icon_squared_bars(), icon_tiling())
        caps = VGroup(T(r"two nonnegative\\readings", font_size=28),
                      T(r"squaring\\inequality", font_size=28),
                      T(r"algebraic\\identity", font_size=28))
        for i, (ic, cp) in enumerate(zip(icons, caps)):
            ic.move_to([box.get_x() + (i - 1) * 2.45, box.get_y() + 0.6, 0])
            cp.next_to(ic, DOWN, buff=0.3)
            cp.move_to([ic.get_x(), box.get_y() - 0.75, 0])
        y_top, y_bot = box.get_y() + 0.95, box.get_y() - 0.95
        xl, xr = box.get_left()[0], box.get_right()[0]
        ring1 = spin_ring(8, radius=0.48, staggered=True, color=INTEGER, length=0.3)
        ring2 = spin_ring(8, radius=0.48, staggered=True, color=HALF, length=0.3)
        ring1.move_to([-6.0, y_top, 0])
        ring2.move_to([-6.0, y_bot, 0])
        r1l = T("spin 1", font_size=28, color=INTEGER).next_to(ring1, UP, buff=0.15)
        r2l = T(r"spin $\tfrac12$", font_size=28, color=HALF).next_to(ring2, UP, buff=0.15)
        in1 = lane_arrow([ring1.get_right()[0] + 0.12, y_top, 0], [xl - 0.08, y_top, 0], INTEGER)
        in2 = lane_arrow([ring2.get_right()[0] + 0.12, y_bot, 0], [xl - 0.08, y_bot, 0], HALF)
        out1 = lane_arrow([xr + 0.08, y_top, 0], [xr + 0.85, y_top, 0], INTEGER)
        out2 = lane_arrow([xr + 0.08, y_bot, 0], [xr + 0.85, y_bot, 0], HALF)
        g1 = T("gap", font_size=36, color=GAP).next_to(out1, RIGHT, buff=0.15)
        ck = check_mark(size=0.34).next_to(g1, RIGHT, buff=0.15)
        g2 = TT("gap", "?!", font_size=36, color=GAP).next_to(out2, RIGHT, buff=0.15)
        g2[1].set_color(SX)
        lsm = T(r"contradicts\\Lieb--Schultz--Mattis", font_size=28, color=SX)
        lsm.next_to(g2, DOWN, buff=0.3)
        lsm.shift(RIGHT * (6.55 - lsm.get_right()[0]))
        bub = objection_bubble("half")

        with self.seg("s05") as d:
            self.play(FadeOut(self.s04_mobs), run_time=0.6)
            self.play(Create(box), FadeIn(title, shift=0.1 * UP), run_time=0.9)
            self.until(2.7)
            self.play(FadeIn(spin_tag, shift=0.1 * DOWN), run_time=0.4)
            self.until(3.4)
            self.play(Create(spin_strike), run_time=0.35)
            self.until(3.8)
            self.play(FadeIn(icons[0], shift=0.1 * UP), FadeIn(caps[0]), run_time=0.9)
            self.until(6.8)
            self.play(FadeIn(icons[1], shift=0.1 * UP), FadeIn(caps[1]), run_time=0.7)
            self.until(8.05)
            self.play(FadeIn(icons[2], shift=0.1 * UP), FadeIn(caps[2]), run_time=0.7)
            self.until(9.6)
            self.play(FadeIn(ring1, r1l), GrowArrow(in1), run_time=0.5)
            self.play(GrowArrow(out1), FadeIn(g1), Create(ck), run_time=0.5)
            self.until(10.3)
            self.play(FadeIn(ring2, r2l), GrowArrow(in2), run_time=0.5)
            self.play(GrowArrow(out2), FadeIn(g2), run_time=0.5)
            self.until(12.4)
            self.play(FadeIn(lsm, shift=0.1 * UP), run_time=0.7)
            self.play(bubble_in(bub), run_time=0.7)
        self.m = dict(box=box, title=title, spin_tag=spin_tag, spin_strike=spin_strike,
                      icons=icons, caps=caps, ring1=ring1, ring2=ring2, r1l=r1l, r2l=r2l,
                      in1=in1, in2=in2, out1=out1, out2=out2, g1=g1, ck=ck, g2=g2, lsm=lsm)
        self.bub = bub

    # ------------------------------------------------------------ s06
    def s06(self):
        m = self.m
        ptag = tag_box(r"spatial operator constructed\\for spin 1 only (Prop.~3.1)")
        ptag.next_to(m["box"], DOWN, buff=0.3).align_to(m["box"], LEFT).shift(RIGHT * 0.3)
        in2d = lane_arrow(m["in2"].get_start(), m["in2"].get_end(), HALF, dashed=True)
        sup = T("suppose one existed", font_size=28, color=DIM)
        sup.next_to(m["ring2"], DOWN, buff=0.2).align_to(m["ring2"], LEFT).shift(LEFT * 0.15)

        # torus + gauges (the bootstrap pair from the SU(2)_1 torus function, beta = n)
        rho0 = np.pi / 2                      # v beta / n with v = pi/2 and beta = n: a square
        p0, q0 = cft_pair(rho0)
        corner = np.array([-5.3, -1.9, 0])
        tor = Torus(1.6, 1.6, nx=4, ny=4)
        tor.shift(corner - tor.rect.get_corner(DL))
        tor2 = Torus(3.2, 3.2, nx=8, ny=8, L_tex="2L", beta_tex=r"2\beta")
        tor2.shift(corner - tor2.rect.get_corner(DL))
        gg = DefectGauges(p=1e-4, q=1e-4, spacing=2.8)
        for g in (gg.p, gg.q):
            g.number.clear_updaters()
            g.remove(g.number)
        gg.move_to([2.75, -0.35, 0])
        qm = VGroup(*[M("?", font_size=56, color=DIM).move_to(g.frame) for g in (gg.p, gg.q)])
        need = T(r"needed: both below the basin edge", font_size=28)
        need.next_to(gg, DOWN, buff=0.45)
        rho = M(r"\rho=v\beta/L", font_size=44).move_to([-3.7, 2.15, 0])
        vlab = T(r"$v$: spin-wave velocity", font_size=28, color=DIM)
        vlab.next_to(rho, RIGHT, buff=0.45).align_to(rho, DOWN).shift(DOWN * 0.04)
        crit = T(r"critical chain (spin $\tfrac12$)", font_size=30, color=HALF)
        crit.move_to([-3.7, 2.95, 0])
        unch = T("unchanged", font_size=30, color=FG).move_to(need)
        rtag = tag(TAG_READING)

        with self.seg("s06") as d:
            self.until(0.4)
            self.play(FadeIn(ptag, shift=0.1 * UP), run_time=0.8)
            # "But even granting one,": the spin-1/2 lane turns dashed in one move
            self.until(4.2)
            self.play(FadeOut(m["in2"]), Create(in2d), FadeIn(sup, shift=0.1 * UP),
                      run_time=0.6)
            # hold the machine into "the recursion needs ...", then cross-fade to the
            # torus and gauges (no blank frame in between)
            self.until(6.3)
            olds = [m[k] for k in ("box", "title", "spin_tag", "spin_strike", "icons", "caps",
                                   "ring1", "ring2", "r1l", "r2l", "in1", "out1", "out2", "g1",
                                   "ck", "g2", "lsm")]
            self.play(LaggedStart(AnimationGroup(FadeOut(*olds, ptag, in2d, sup),
                                                 bubble_out(self.bub)),
                                  AnimationGroup(FadeIn(tor), FadeIn(gg), FadeIn(qm)),
                                  lag_ratio=0.35), run_time=1.2)
            self.until(7.6)
            self.play(FadeIn(need, shift=0.1 * UP), pulse(gg.p.basin, scale_factor=1.3),
                      pulse(gg.q.basin, scale_factor=1.3), run_time=0.9)
            self.until(9.6)
            self.play(tag_in(rtag), run_time=0.6)
            self.until(11.2)
            self.play(FadeIn(crit, shift=0.1 * DOWN), Write(rho), run_time=0.9)
            self.play(FadeIn(vlab), run_time=0.4)
            self.until(12.45)
            self.play(FadeOut(qm), FadeOut(need), gg.set_defects(p=p0, q=q0), run_time=1.3)
            self.until(14.0)
            self.play(Indicate(rho, color=FG, scale_factor=1.1), run_time=0.7)
            self.until(15.45)
            self.play(*torus_morph(tor, tor2), run_time=1.2)
            self.add(tor2)
            self.play(FadeIn(unch, shift=0.1 * UP), Indicate(rho, color=FG, scale_factor=1.1),
                      run_time=0.8)
        self.s06 = dict(tor=tor2, gg=gg, rho=rho, vlab=vlab, crit=crit, unch=unch, rtag=rtag)

    # ------------------------------------------------------------ s07
    def s07(self):
        s = self.s06
        tor, gg, rtag = s["tor"], s["gg"], s["rtag"]
        # seesaw under the two gauges
        fb = gg.p.frame.get_bottom()[1]
        pivot = np.array([gg.get_x(), fb - 0.1, 0])
        half = gg.q.frame.get_x() - gg.p.frame.get_x()
        beam = Line(pivot + LEFT * (half / 2 + 0.75), pivot + RIGHT * (half / 2 + 0.75),
                    color=DIM, stroke_width=6)
        fulcrum = Polygon(pivot, pivot + DL * 0.42 + LEFT * 0.05, pivot + DR * 0.42 + RIGHT * 0.05,
                          stroke_color=DIM, stroke_width=2, fill_color=FAINT, fill_opacity=1)
        dx = {"p": -half / 2, "q": half / 2}
        state = {"ang": 0.0}

        def tilt(new):
            old = state["ang"]
            state["ang"] = new
            anims = [Rotate(beam, new - old, about_point=pivot)]
            for k, g in (("p", gg.p), ("q", gg.q)):
                anims.append(ApplyMethod(g.shift, UP * dx[k] * (np.tan(new) - np.tan(old))))
            return anims

        rho_w, rho_t = 0.5, 3.0
        pw, qw = cft_pair(rho_w)          # long in space: spatially pure, thermally mixed
        pt, qt = cft_pair(rho_t)          # long in time: the reverse
        ctr = np.array([-3.7, -0.15, 0])
        wide = Torus(3.6, 3.6 * (rho_w / (np.pi / 2)), nx=8, ny=3).move_to(ctr)
        tall = Torus(1.6, 1.6 * (rho_t / (np.pi / 2)), nx=3, ny=6).move_to(ctr)

        def seesaw_label(a, b, ca, cb):
            lab = TT(a + ", ", b, font_size=30)
            lab[0].set_color(ca)
            lab[1].set_color(cb)
            return lab.move_to([ctr[0], -2.75, 0])
        lw = seesaw_label("spatially pure", "thermally mixed", SPACE, TIME)
        lt = seesaw_label("thermally pure", "spatially mixed", TIME, SPACE)

        # --- ED panels
        th = read_rows("thermal_purity_ray.csv")
        sp = read_rows("spatial_purity_ray.csv")
        cft = [r for r in read_rows("cft_spinhalf_universal.csv") if float(r["c"]) == 1.0][0]
        T_cft = float(cft["1-T CFT (beta=cL, L->inf)"])
        S_cft = float(cft["1-S CFT (beta=cn, n->inf)"])

        def series(rows_, spin, key, xkey):
            rr = [r for r in rows_ if float(r["S"]) == spin and float(r["c"]) == 1.0]
            return [(int(r[xkey]), float(r[key])) for r in rr]
        A1 = series(th, 1.0, "1-T", "L")
        Ah = series(th, 0.5, "1-T", "L")
        B1 = series(sp, 1.0, "1-S", "n")
        Bh = series(sp, 0.5, "1-S", "n")

        yt = [(0.01, "0.01"), (0.1, "0.1"), (1, "1")]

        def panel(origin, xr, xticks, xlab, title):
            pl = Plot2D(xr, (-2, 0.5), 5.0, 4.2, xticks=[(v, str(v)) for v in xticks],
                        yticks=yt, ymap=np.log10, xlabel=M(xlab, font_size=34))
            pl.move_origin_to(origin)
            ttl = title.move_to([pl.x_axis.get_center()[0], pl.y_axis.get_end()[1] + 0.42, 0])
            bl = DashedLine(pl.p(xr[0], 0.127), pl.p(xr[1], 0.127), color=DEFECT,
                            stroke_width=3, dash_length=0.08)
            blab = T("basin edge", font_size=28, color=DEFECT)
            blab.next_to(bl.get_end(), UP, buff=0.08).align_to(bl, RIGHT)
            return pl, ttl, VGroup(bl, blab)

        def markers(pl, data, kind):
            mk = spin1_marker if kind == 1 else spinhalf_marker
            pts = [pl.p(x, y) for x, y in data]
            line = VMobject(stroke_color=INTEGER if kind == 1 else HALF, stroke_width=2,
                            stroke_opacity=0.5).set_points_as_corners(pts)
            return VGroup(*[mk(p) for p in pts]), line

        plA, ttlA, basA = panel([-5.95, -2.35, 0], (2, 22), (4, 8, 12, 16, 20), "L",
                                T(r"thermal defect $1-T(L,\beta{=}L)$", font_size=30, color=TIME))
        plB, ttlB, basB = panel([1.05, -2.35, 0], (2, 12), (4, 6, 8, 10), "n",
                                T(r"spatial defect $1-S(n,\beta{=}n)$", font_size=30,
                                  color=SPACE))
        basB[1].align_to(basB[0], LEFT).shift(RIGHT * 0.15)
        A1m, A1l = markers(plA, A1, 1)
        Ahm, Ahl = markers(plA, Ah, 0)
        B1m, B1l = markers(plB, B1, 1)
        Bhm, Bhl = markers(plB, Bh, 0)
        labA1 = T("spin 1", font_size=28, color=INTEGER).next_to(A1m[-1], RIGHT, buff=0.15)
        # nudged up so the fraction's denominator clears the dashed CFT line below it
        labAh = T(r"spin $\tfrac12$", font_size=28, color=HALF).next_to(Ahm[-1], RIGHT,
                                                                        buff=0.15)
        labAh.shift(UP * 0.09)
        asA = DashedLine(plA.p(2, T_cft), plA.p(22, T_cft), color=HALF, stroke_width=2.5,
                         dash_length=0.1)
        asAl = T("CFT limit", font_size=28, color=HALF)
        asAl.next_to(asA.get_end(), DOWN, buff=0.1).align_to(asA, RIGHT)
        labBh = T(r"spin $\tfrac12$", font_size=28, color=HALF).move_to(plB.p(4.6, 10 ** -0.43))
        l1 = T(r"spin 1: $n\lesssim\xi\approx6$", font_size=28, color=INTEGER)
        l1 = VGroup(l1, literature_label(l1, buff=0.15))
        labB1 = VGroup(l1, T("too short to tell", font_size=28, color=INTEGER))
        labB1.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        labB1.next_to(plB.p(2.3, 10 ** 0.02), UP, buff=0.05, aligned_edge=LEFT)
        # 'expected to fall': leaves the n=6 square on its right, runs out over the n=8
        # dot and only then plunges, so it crosses the spin-1/2 data nowhere and the
        # CFT line once, clear of the 'CFT: stays' label
        way = [(6.3, 0.90), (7.3, 0.97), (8.1, 0.93), (8.55, 0.72), (8.8, 0.30),
               (8.97, 0.09), (9.08, 0.033)]
        arc = VMobject(stroke_color=DIM, stroke_width=2.5)
        arc.set_points_smoothly([plB.p(n, v) for n, v in way])
        tl = Line(plB.p(9.02, 0.05), plB.p(9.1, 0.03), color=DIM)
        tl.add_tip(tip_length=0.18, tip_width=0.16)
        ftip = tl.pop_tips()[0]
        fall = VGroup(DashedVMobject(arc, num_dashes=26), ftip)
        fall_l = T(r"expected to fall\\for $n\gg\xi$ \textit{(reading)}", font_size=28,
                   color=DIM)
        fall_l.next_to(ftip, LEFT, buff=0.25).shift(UP * 0.15)
        asB = DashedLine(plB.p(2, S_cft), plB.p(12, S_cft), color=HALF, stroke_width=2.5,
                         dash_length=0.1)
        asBl = T("CFT: stays", font_size=28, color=HALF)
        asBl.next_to(asB.get_end(), UP, buff=0.1).align_to(asB, RIGHT)

        with self.seg("s07") as d:
            # 'critical chain (spin 1/2)' and rho stay up through the seesaw: the seesaw
            # is a statement about the scale-invariant chain, not a universal one
            self.play(FadeOut(s["unch"]), run_time=0.4)
            self.play(FadeIn(fulcrum), Create(beam), run_time=0.6)
            self.until(1.43)
            self.play(*torus_morph(tor, wide), gg.set_defects(p=pw, q=qw), *tilt(-0.2),
                      run_time=1.4)
            self.add(wide)
            self.play(FadeIn(lw, shift=0.1 * UP), run_time=0.6)
            self.until(4.55)
            self.play(*torus_morph(wide, tall), gg.set_defects(p=pt, q=qt), *tilt(0.2),
                      Succession(FadeOut(lw, shift=0.1 * UP), FadeIn(lt, shift=0.1 * UP)),
                      run_time=1.1)
            self.add(tall)
            self.until(6.15)
            self.play(FadeOut(tall, gg, beam, fulcrum, lt, s["crit"], s["rho"], s["vlab"]),
                      run_time=0.5)
            self.play(Create(plA.axes), FadeIn(plA.xtick_marks, plA.ytick_marks,
                                               plA.xtick_labels, plA.ytick_labels, plA.xlabel),
                      FadeIn(ttlA, shift=0.1 * DOWN), Create(basA[0]), FadeIn(basA[1]),
                      run_time=0.9)
            self.until(7.45)
            self.play(LaggedStart(*[FadeIn(q, scale=0.5) for q in A1m], lag_ratio=0.3),
                      Create(A1l), run_time=1.6)
            self.play(FadeIn(labA1, shift=0.1 * LEFT), run_time=0.5)
            self.until(11.0)
            self.play(LaggedStart(*[FadeIn(q, scale=0.5) for q in Ahm], lag_ratio=0.2),
                      Create(Ahl), run_time=1.0)
            self.play(FadeIn(labAh, shift=0.1 * LEFT), Create(asA), FadeIn(asAl), run_time=0.7)
            self.until(13.4)
            self.play(Create(plB.axes), FadeIn(plB.xtick_marks, plB.ytick_marks,
                                               plB.xtick_labels, plB.ytick_labels, plB.xlabel),
                      FadeIn(ttlB, shift=0.1 * DOWN), Create(basB[0]), FadeIn(basB[1]),
                      run_time=0.8)
            self.play(LaggedStart(*[FadeIn(q, scale=0.5) for q in [*B1m, *Bhm]], lag_ratio=0.2),
                      Create(B1l), Create(Bhl), run_time=1.2)
            self.play(FadeIn(labBh), FadeIn(labB1[0]), run_time=0.5)
            self.until(16.95)
            self.play(FadeIn(labB1[1], shift=0.1 * UP), run_time=0.6)
            self.until(18.05)
            self.play(Create(fall), run_time=1.0)
            self.play(FadeIn(fall_l, shift=0.1 * UP), run_time=0.6)
            self.until(21.7)
            self.play(Create(asB), FadeIn(asBl), run_time=1.0)
        self.s07_mobs = VGroup(plA, ttlA, basA, plB, ttlB, basB, A1m, A1l, Ahm, Ahl, B1m, B1l,
                               Bhm, Bhl, labA1, labAh, asA, asAl, labBh, labB1, fall, fall_l, asB,
                               asBl)
        self.rtag = rtag

    # ------------------------------------------------------------ s08
    def s08(self):
        lo, hi = np.log10(0.25), np.log10(4)
        pl = Plot2D((lo, hi), (0, 1), 7.4, 3.6, xmap=np.log10,
                    xticks=[(0.25, "1/4"), (0.5, "1/2"), (1, "1"), (2, "2"), (4, "4")],
                    yticks=[(0, "0"), (0.5, "0.5"), (1, "1")],
                    xlabel=M(r"\rho=v\beta/n", font_size=34),
                    ylabel=T("defect", font_size=28))
        pl.move_origin_to([-4.2, -2.0, 0])
        cS = pl.curve(lambda X: cft_spatial_defect(10 ** X), lo, hi, color=SPACE,
                      stroke_width=4)
        cT = DashedVMobject(pl.curve(lambda X: cft_thermal_defect(10 ** X / 2), lo, hi,
                                     color=TIME, stroke_width=4), num_dashes=60)
        env = pl.curve(lambda X: max(cft_pair(10 ** X)), lo, hi, n=400, color=DEFECT,
                       stroke_width=12, stroke_opacity=0.45)
        rs = np.exp(np.linspace(np.log(0.25), np.log(4), 4001))
        mv = np.array([max(cft_pair(r)) for r in rs])
        rmin, vmin = rs[mv.argmin()], mv.min()          # sqrt 2, 0.545
        assert abs(rmin - np.sqrt(2)) < 2e-3 and abs(vmin - 0.545) < 1e-3
        dot = Dot(pl.p(rmin, vmin), radius=0.09, color=DEFECT)
        dlab = T(r"best balance\\$\approx0.55$", font_size=30, color=DEFECT)
        dlab.move_to([dot.get_x(), pl.p(1, 0.87)[1], 0])
        lS = T(r"spatial $1-S(n,\beta)$", font_size=28, color=SPACE)
        lS.next_to(pl.p(4, cft_spatial_defect(4)), RIGHT, buff=0.2)
        lT = T(r"thermal $1-T(2n,\beta)$", font_size=28, color=TIME)
        lT.move_to(pl.p(2.0, 0.45), aligned_edge=LEFT).shift(RIGHT * 0.3)
        sub = T(r"spin $\tfrac12$ chain: conformal field theory", font_size=30, color=HALF)
        sub.move_to([-1.0, 2.55, 0])
        band = Rectangle(width=pl.x_axis.get_length(),
                         height=pl.p(1, 0.127)[1] - pl.p(1, 0)[1], stroke_width=0,
                         fill_color=GAP, fill_opacity=0.2)
        band.move_to(pl.x_axis.get_start(), aligned_edge=DL)
        blab = T(r"basin ($<0.127$)", font_size=28, color=GAP)
        blab.move_to(band).align_to(band, LEFT).shift(RIGHT * 0.2)
        final = T("the physics lives in the starting data", font_size=38).move_to([0, -3.3, 0])
        otag = tag(TAG_OURS, corner=UL)
        bub = objection_bubble("half")

        with self.seg("s08") as d:
            self.play(FadeOut(self.s07_mobs), tag_out(self.rtag), run_time=0.6)
            self.play(tag_in(otag), run_time=0.5)
            self.play(Create(pl.axes), FadeIn(pl.xtick_marks, pl.ytick_marks, pl.xtick_labels,
                                              pl.ytick_labels, pl.xlabel, pl.ylabel),
                      run_time=0.9)
            self.until(2.7)
            self.play(FadeIn(sub, shift=0.1 * DOWN), run_time=0.6)
            self.play(Create(cS), FadeIn(lS), run_time=1.0)
            self.play(Create(cT), FadeIn(lT), run_time=1.0)
            self.until(5.6)
            self.bring_to_back(env)
            self.play(Create(env), run_time=1.3)
            self.play(GrowFromCenter(dot), FadeIn(dlab, shift=0.1 * DOWN), run_time=0.8)
            self.until(9.5)
            self.play(FadeIn(band), FadeIn(blab), run_time=0.8)
            self.play(bubble_in(bub), run_time=0.6)
            self.play(bubble_check(bub), run_time=0.6)
            self.until(11.45)
            self.play(Write(final), run_time=1.3)
            self.until(14.7)
            self.play(Indicate(VGroup(band, blab), color=GAP, scale_factor=1.04), run_time=1.2)
