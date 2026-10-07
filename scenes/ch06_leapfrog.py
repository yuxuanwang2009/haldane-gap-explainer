"""ch06: The leapfrog.

Two failed attempts (double only beta / only L), the exchange-rate question,
the exact cancellation identity and its four-tori reading, the linear loss,
the mirror identity, the four-step leapfrog on the staircase, linear loss vs
quadratic gain (cobweb, basin edge 0.127), and the collapse of the defect.

Beats inside each segment are given in seconds of the narration clip as it was
measured (pauses found with ffmpeg silencedetect); they are rescaled by
d / D0[seg] so they follow the audio if a clip is regenerated.
"""
import csv
import sys
from contextlib import contextmanager

import numpy as np

from motifs import *  # noqa: F401,F403

# clip lengths at the time the beats below were measured
D0 = {"s01": 11.3, "s02": 16.85, "s03": 10.125, "s04": 10.975, "s05": 19.75,
      "s06": 14.05, "s07": 12.475, "s08": 14.125, "s09": 15.175, "s10": 7.825,
      "s11": 18.075, "s12": 12.425}


# ======================================================================= helpers
def MT(*s, **kw):
    """MathTex with explicit substrings (each one addressable as m[i])."""
    kw.setdefault("color", FG)
    return MathTex(*s, tex_template=TEX_TEMPLATE, **kw)


def TT(*s, colors=None, **kw):
    """Tex with explicit substrings; colors = {index: color}."""
    kw.setdefault("color", FG)
    m = Tex(*s, tex_template=TEX_TEMPLATE, **kw)
    for i, c in (colors or {}).items():
        m[i].set_color(c)
    return m


def _rows(name):
    with open(DATA / name) as f:
        return list(csv.DictReader(f))


def thermal_bars_beta8():
    """spin 1, beta = 8: (L, 1-T) for L = 4..12 (data/thermal_purity_vs_beta.csv)."""
    out = {}
    for r in _rows("thermal_purity_vs_beta.csv"):
        if float(r["S"]) == 1.0 and float(r["beta"]) == 8.0 and int(r["L"]) in (4, 6, 8, 10, 12):
            out[int(r["L"])] = float(r["1-T"])
    return sorted(out.items())


def spatial_defect_curve(n=4):
    """spin 1, ring n: beta -> 1 - S(n, beta) (data/spatial_purity_vs_beta.csv, deduplicated)."""
    seen = {}
    for r in _rows("spatial_purity_vs_beta.csv"):
        if float(r["S"]) == 1.0 and int(r["n"]) == n:
            seen[float(r["beta"])] = 1.0 - float(r["S(n,beta)"])
    b = np.array(sorted(seen))
    return b, np.array([seen[x] for x in b])


def thermal_defect_curve(L=8):
    """spin 1, ring L: beta -> 1 - T(L, beta) (data/thermal_purity_vs_beta.csv)."""
    seen = {}
    for r in _rows("thermal_purity_vs_beta.csv"):
        if float(r["S"]) == 1.0 and int(r["L"]) == L:
            seen[float(r["beta"])] = 1.0 - float(r["T(L,beta)"])
    b = np.array(sorted(seen))
    return b, np.array([seen[x] for x in b])


def identity_check():
    """(number of cases, max |log LHS - log RHS|) from data/cancellation_identity_check.csv."""
    v = [float(r["abs diff (logs)"]) for r in _rows("cancellation_identity_check.csv")]
    return len(v), max(v)


def dyadic_row(row="n0=2304", jmax=3):
    """u_j for j = 0..jmax from data/bootstrap_dyadic.csv."""
    out = []
    for r in _rows("bootstrap_dyadic.csv"):
        if r["row"] == row and int(r["j"]) <= jmax:
            out.append((int(r["j"]), float(r["u_j"]), -float(r["log10_u_j"])))
    return sorted(out)


def G(u):
    """Paper (4.9): f(1-(1-u)^3) = G(u) u^2."""
    return 0.5 * ((1 - u) ** -1 + (1 - u) ** -2 + (1 - u) ** -3) ** 2


U_STAR = 0.127311   # solves u G(u) = 1 (critic computation; not printed in the paper)


def strike(mob, color=DEFECT):
    return Line(mob.get_corner(DL) + LEFT * 0.04 + DOWN * 0.02,
                mob.get_corner(UR) + RIGHT * 0.04 + UP * 0.02,
                color=color, stroke_width=4)


def pause_glyph(h=0.8, color=DIM):
    bars = VGroup(*[RoundedRectangle(width=0.22, height=h, corner_radius=0.06, stroke_width=0,
                                     fill_color=color, fill_opacity=1) for _ in range(2)])
    bars.arrange(RIGHT, buff=0.2)
    ring = Circle(radius=0.75 * h, stroke_color=color, stroke_width=3).move_to(bars)
    return VGroup(ring, bars)


def place_gauges(gg, p_x, y):
    """Put the gauge pair so that the p frame is centred at (p_x, y)."""
    gg.shift(np.array([p_x, y, 0]) - gg.p.frame.get_center())
    return gg


def fill_top(g, v):
    """Screen y of the top of gauge g's fill for defect v."""
    pad = 0.045
    return g.frame.get_bottom()[1] + pad + defect_frac(v) * (g.frame.height - 2 * pad)


def ch06_gauges(p, q):
    """The gauge pair without the 'basin edge' text: the basin is only named in s11,
    so in this chapter the dashed line stays unlabelled."""
    gg = DefectGauges(p=p, q=q)
    gg.q.remove(gg.q.basin_label)
    return gg


def gauges_freeze(gg):
    """Detach the fill updaters before a FadeIn/FadeOut of the gauges.
    DefectGauge._update_fill re-applies fill opacity 0.85 every frame, also on the
    copies a Fade animation interpolates between, so the fills would ignore the fade."""
    for g in (gg.p, gg.q):
        g.fill.clear_updaters()


def gauges_thaw(gg):
    """Re-attach the fill updaters (after a fade-in) so set_defects moves the fills."""
    for g in (gg.p, gg.q):
        g.fill.clear_updaters()
        g.fill.add_updater(g._update_fill)


def gauge_pulse(g, color=DEFECT, scale=1.08):
    """'Pulse DEFECT' on a gauge: the fill and number flash to `color` and back while
    the frame swells (the fill follows the frame).  Indicate on the fill itself does
    nothing visible, because the fill updater overwrites its colour and shape.
    Returns a list to unpack into play(): wrapping these in an AnimationGroup would make
    the scene re-add the frame on top of the fill, whose BG fill then dims the bar."""
    base, hot = ManimColor(g.color), ManimColor(color)

    def upd(m, a):
        c = interpolate_color(base, hot, there_and_back(a))
        g._fill_color = c
        g.number.set_color(c)
    return [UpdateFromAlphaFunc(g.number, upd),
            g.frame.animate(rate_func=there_and_back).scale(scale).set_stroke(color)]


def thermal_chart(x0, dx, bw, base_y, H, ymax=0.12, fs_tick=28, fs_title=32, fs_val=24,
                  fs_L=30, title_lift=0.35):
    """Bar chart of 1-T(L, beta=8) (spin 1, real ED data) with value labels on the
    first and last bars.  Returns (bars, VGroup(baseline, ticks, Llab, ttl, vals))."""
    data = thermal_bars_beta8()
    bars, ticks = VGroup(), VGroup()
    for i, (L, v) in enumerate(data):
        r = Rectangle(width=bw, height=max(v / ymax * H, 0.02), stroke_width=0,
                      fill_color=TIME, fill_opacity=0.9)
        r.move_to([x0 + i * dx, base_y, 0], aligned_edge=DOWN)
        bars.add(r)
        ticks.add(M(str(L), font_size=fs_tick, color=DIM).next_to([x0 + i * dx, base_y, 0],
                                                                    DOWN, buff=0.15))
    pad = 0.45 * dx / 0.95
    baseline = Line([x0 - pad, base_y, 0], [x0 + 4 * dx + pad, base_y, 0], color=DIM,
                    stroke_width=2)
    Llab = M("L", color=SPACE, font_size=fs_L).next_to(baseline, RIGHT, buff=0.2)
    vals = VGroup(*[M(f"{data[i][1]:.4f}", font_size=fs_val, color=DIM).next_to(
        bars[i], UP, buff=0.1) for i in (0, len(data) - 1)])
    ttl = M(r"1-T(L,\,\beta{=}8)", color=TIME, font_size=fs_title)
    ttl.next_to(baseline, UP, buff=H + title_lift).align_to(baseline, LEFT).shift(RIGHT * 0.1)
    return bars, VGroup(baseline, ticks, Llab, ttl, vals)


# ======================================================================= scene
class Ch06(NarratedScene):
    CHAPTER = "ch06"

    # ---------------------------------------------------------- beat timing
    @contextmanager
    def seg(self, sid, breath=None):
        with self.voice(sid, breath=breath) as d:
            self._t0 = self.renderer.time
            self._k = d / D0[sid]
            self._sid = sid
            yield d
            over = (self.renderer.time - self._t0) - d
            if over > 0.3:
                print(f"[ch06] {sid}: animations overrun the clip by {over:.2f}s", file=sys.stderr)

    def t(self):
        """Seconds into the current clip (in measured-clip units)."""
        return (self.renderer.time - self._t0) / self._k

    def at(self, ts):
        """Wait until ts seconds into the clip."""
        dt = (ts - self.t()) * self._k
        if dt > 0.04:
            self.wait(dt)
        elif dt < -0.35:
            print(f"[ch06] {self._sid}: late by {-dt:.2f}s for beat {ts}", file=sys.stderr)

    def go(self, *anims, until, at=None, min_rt=0.3, **kw):
        """Play anims (optionally starting at beat `at`) so that they end at beat `until`."""
        if at is not None:
            self.at(at)
        rt = max(min_rt, (until - self.t()) * self._k)
        self.play(*anims, run_time=rt, **kw)

    # ---------------------------------------------------------- construct
    def construct(self):
        self.s01()
        self.s02()
        self.s03()
        self.s04()
        self.s05()
        self.s06()
        self.s07()
        self.s08()
        self.s09()
        self.s10()
        self.s11()
        self.s12()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        self.wait(0.2)

    # ================================================================ s01
    def s01(self):
        """Attempt one: double only beta.  Thumb grows vertically x3, q squares,
        the point on the plane climbs straight up; 'fixed L: already known'."""
        self.thumb = TorusThumb()
        gg = ch06_gauges(p=0.3, q=0.4)
        # clear of the thumbnail, which briefly grows to twice its box while beta doubles
        place_gauges(gg, -3.55, -0.65)
        self.gg = gg
        bub = objection_bubble("beta")
        head = TT(r"attempt 1: double only ", r"$\beta$", colors={1: TIME}, font_size=36)
        head.move_to([0.35, 3.2, 0])
        self.head = head

        pl = Staircase("bare", x_length=4.6, y_length=3.6)
        pl.move_to([3.2, -0.75, 0])
        start = pl.pt(2, 1)
        dot = Dot(start, radius=0.08, color=FG)
        arrows = VGroup(*[Arrow(pl.pt(2, k), pl.pt(2, k + 1), buff=0.06, color=TIME,
                                stroke_width=5, max_tip_length_to_length_ratio=0.28)
                          for k in (1, 2, 3)])
        stamp = T(r"fixed $L$: already known", font_size=28, color=DIM)
        stamp.next_to(arrows, RIGHT, buff=0.3).shift(UP * 0.2)
        xmark = Line(pl.pt(2, 0) + DOWN * 0.13, pl.pt(2, 0) + UP * 0.13, color=SPACE,
                     stroke_width=5)
        xguide = DashedLine(pl.pt(2, 0), start, color=SPACE, stroke_width=2.5, dash_length=0.08)

        qv = [0.4, 0.16, 0.0256, 0.000655]
        qlabs = [M(t, color=TIME, font_size=30) for t in ("q", "q^2", "q^4", "q^8")]
        for lab, v in zip(qlabs, qv):
            lab.move_to([gg.q.frame.get_left()[0] - 0.42, max(fill_top(gg.q, v), gg.q.frame.get_bottom()[1] + 0.2), 0])

        with self.seg("s01") as d:
            gauges_freeze(gg)
            self.go(FadeIn(self.thumb), FadeIn(gg), bubble_in(bub), until=1.0)
            gauges_thaw(gg)
            self.go(Write(head), at=1.25, until=2.2)
            self.go(Create(pl.ax), FadeIn(pl.labels), FadeIn(dot, scale=0.5),
                    FadeIn(qlabs[0]), until=3.6)
            # three doublings of beta: thermal defect squares each time
            for k in range(3):
                t0 = 3.81 + 0.75 * k
                self.at(t0)
                self.play(self.thumb.double_beta(run_time=0.72), gg.set_defects(q=qv[k + 1]),
                          GrowArrow(arrows[k]), dot.animate.move_to(pl.pt(2, k + 2)),
                          ReplacementTransform(qlabs[k], qlabs[k + 1]), run_time=0.72)
            # ... but the ring never grew
            self.go(Indicate(self.thumb.L_label, color=SPACE, scale_factor=1.5),
                    Create(xguide), GrowFromCenter(xmark), at=6.33, until=7.4)
            self.go(FadeIn(stamp, shift=0.1 * LEFT), at=7.85, until=8.6)
            self.go(bubble_check(bub), until=9.5)
            self.go(Indicate(stamp, color=FG, scale_factor=1.05), at=9.8, until=10.7)
        self.s01_left = VGroup(pl.ax, pl.labels, dot, arrows, stamp, xmark, xguide, qlabs[3])
        self.bub = bub

    # ================================================================ s02
    def s02(self):
        gg, thumb = self.gg, self.thumb
        head2 = TT(r"attempt 2: double only ", r"$L$", colors={1: SPACE}, font_size=36)
        head2.move_to(self.head)

        # inset: spin-1 thermal defect at beta = 8 grows with L (real ED data);
        # it stays on screen (smaller, lower right) while the heuristic explains it
        bars, chart = thermal_chart(x0=1.05, dx=0.95, bw=0.55, base_y=-1.75, H=2.8)
        bars_c, chart_c = thermal_chart(x0=1.75, dx=0.68, bw=0.4, base_y=-3.05, H=1.5,
                                        fs_tick=24, fs_title=28, fs_L=28, title_lift=0.05)
        cap = T(r"spin 1 $\cdot$ same $\beta$, longer ring", font_size=28, color=DIM)
        cap.next_to(chart[1], DOWN, buff=0.3).match_x(chart[0])

        # heuristic: thermal magnons on a time slice; more places on a longer ring
        tor = Torus(2.6, 1.6)
        tor.shift(np.array([0.7, 0.75, 0]) - tor.rect.get_corner(DL))
        tor2 = Torus(5.2, 1.6, L_tex="2L")
        tor2.shift(tor.rect.get_corner(DL) - tor2.rect.get_corner(DL))
        ys = tor.y_at(0.66)

        def slots_for(t, n):
            return VGroup(*[Circle(radius=0.075, stroke_color=DIM, stroke_width=2)
                            .move_to([t.left + (i + 0.5) * (t.right - t.left) / n, ys, 0])
                            for i in range(n)])
        slots = slots_for(tor, 6)
        slots2 = slots_for(tor2, 12)
        slice_ = DashedLine([tor.left, ys, 0], [tor.right, ys, 0], color=TIME, stroke_width=1.5,
                            dash_length=0.06, stroke_opacity=0.6)
        slice2 = DashedLine([tor2.left, ys, 0], [tor2.right, ys, 0], color=TIME, stroke_width=1.5,
                            dash_length=0.06, stroke_opacity=0.6)
        occ = [1, 3, 4]

        def blob(p):
            return VGroup(Dot(p, radius=0.17, color=TIME, fill_opacity=0.25),
                          Dot(p, radius=0.1, color=TIME))
        blobs = VGroup(*[blob(slots[i].get_center()) for i in occ])
        blobs2 = VGroup(*[blob(slots2[i + 6].get_center()) for i in occ])
        rule = T(r"defect $\approx$ (places) $\times$ (Boltzmann cost)", font_size=30)
        rule.move_to([3.3, -0.35, 0])
        htag = tag(TAG_HEURISTIC, buff=0.42)

        plab = [M(t, color=SPACE, font_size=30) for t in ("p", "p^2")]
        for lab, v in zip(plab, (0.3, 0.09)):
            lab.move_to([gg.p.frame.get_left()[0] - 0.42, fill_top(gg.p, v), 0])

        with self.seg("s02") as d:
            self.go(bubble_out(self.bub), FadeOut(self.s01_left), until=0.6)
            self.go(ReplacementTransform(self.head, head2), thumb.reset(),
                    gg.set_defects(p=0.3, q=0.1), at=0.31, until=1.5)
            self.go(FadeIn(plab[0]), until=2.0)
            # the spatial defect squares
            self.go(thumb.double_L(), gg.set_defects(p=0.09),
                    ReplacementTransform(plab[0], plab[1]), at=2.8, until=4.2)
            # ... but the thermal defect of the longer ring gets worse
            self.go(gg.set_defects(q=0.2), at=4.3, until=5.1)
            self.play(*gauge_pulse(gg.q), FadeIn(chart[0]), FadeIn(chart[2]), FadeIn(chart[3]),
                      run_time=0.7)
            self.go(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.25),
                    LaggedStart(*[FadeIn(t) for t in chart[1]], lag_ratio=0.25),
                    until=7.3)
            self.go(FadeIn(chart[4], shift=0.1 * UP), FadeIn(cap), until=7.9)
            # heuristic: the chart moves aside (kept: the heuristic explains it)
            self.go(ReplacementTransform(bars, bars_c), ReplacementTransform(chart, chart_c),
                    FadeOut(cap), tag_in(htag), at=8.4, until=9.3)
            self.go(FadeIn(tor), Create(slice_), until=10.6)
            self.go(LaggedStart(*[GrowFromCenter(s) for s in slots], lag_ratio=0.12),
                    until=11.4)
            self.go(LaggedStart(*[FadeIn(b, scale=0.4) for b in blobs], lag_ratio=0.3),
                    until=12.3)
            self.go(Write(rule), at=12.65, until=14.0)
            # ... and a longer ring has more places
            self.go(ReplacementTransform(tor, tor2), ReplacementTransform(slice_, slice2),
                    *[ReplacementTransform(slots[i], slots2[i]) for i in range(6)],
                    blobs.animate.shift(np.array([slots2[occ[0]].get_center()[0]
                                                  - slots[occ[0]].get_center()[0], 0, 0])),
                    at=14.36, until=15.2)
            self.go(LaggedStart(*[GrowFromCenter(slots2[i]) for i in range(6, 12)],
                                lag_ratio=0.1),
                    LaggedStart(*[FadeIn(b, scale=0.4) for b in blobs2], lag_ratio=0.3),
                    until=16.3)
        self.s02_right = VGroup(tor2, slice2, slots2, blobs, blobs2, rule, bars_c, chart_c)
        self.htag, self.head2, self.plab = htag, head2, plab[1]

    # ================================================================ s03
    def s03(self):
        gg, thumb = self.gg, self.thumb
        bS, pS = spatial_defect_curve(4)
        bT, qT = thermal_defect_curve(8)
        bmax = 24.5
        ax = Axes(x_range=[0, bmax, 4], y_range=[0, 1.0, 0.5], x_length=5.0, y_length=2.9,
                  tips=False,
                  axis_config={"color": DIM, "stroke_width": 2, "tick_size": 0.06,
                               "font_size": 24},
                  x_axis_config={"numbers_to_include": [4, 8, 12, 16, 20, 24],
                                 "decimal_number_config": {"num_decimal_places": 0,
                                                           "color": DIM}},
                  y_axis_config={"numbers_to_include": [0.5, 1.0],
                                 "decimal_number_config": {"num_decimal_places": 1,
                                                           "color": DIM}})
        ax.move_to([3.45, -0.6, 0])
        xl = M(r"\beta", color=TIME, font_size=32).next_to(ax.x_axis.get_end(), RIGHT, buff=0.15)
        yl = M(r"1-S(4,\beta)", color=SPACE, font_size=30).next_to(ax.c2p(0, 1.0), UP, buff=0.2)
        yl.align_to(ax.c2p(0, 0), LEFT)
        note = T(r"spin 1, $n=4$: small ring, qualitative", font_size=24, color=DIM)
        note.next_to(ax, DOWN, buff=0.25).align_to(ax, RIGHT)
        anchor = M(r"\beta\to0:\ \ X\to3,\ \ S\to1,\ \ T\to3^{-L}", color=DIM, font_size=28)
        anchor.next_to(yl, UP, buff=0.3).align_to(yl, LEFT)
        mask = bS <= bmax
        full = VMobject(stroke_color=SPACE, stroke_width=4)
        bb = np.concatenate([[0.0], bS[mask]])
        pp = np.concatenate([[0.0], pS[mask]])
        full.set_points_as_corners([ax.c2p(b, p) for b, p in zip(bb, pp)])
        curve = full.copy()
        beta = ValueTracker(0.0)

        def p_of(b):
            return float(np.interp(b, bb, pp))

        def q_of(b):
            return float(np.interp(b, bT, qT))
        curve.add_updater(lambda m: m.pointwise_become_partial(
            full, 0, max(1e-3, np.searchsorted(bb, beta.get_value()) / (len(bb) - 1))))
        marker = Dot(ax.c2p(0, 0), radius=0.08, color=SPACE)
        marker.add_updater(lambda m: m.move_to(ax.c2p(beta.get_value(), p_of(beta.get_value()))))

        # 2x2 table
        def cell(good):
            arr = M(r"\downarrow" if good else r"\uparrow", font_size=38,
                    color=GAP if good else DEFECT)
            word = T("improves" if good else "degrades", font_size=30,
                     color=GAP if good else DEFECT)
            return VGroup(arr, word).arrange(RIGHT, buff=0.15)
        ch_b = T(r"double $\beta$", font_size=32, color=TIME)
        ch_L = T(r"double $L$", font_size=32, color=SPACE)
        rh_T = M(r"T(L,\beta)", font_size=38, color=TIME)
        rh_S = M(r"S(L,\beta)", font_size=38, color=SPACE)
        cells = [[cell(True), cell(False)], [cell(False), cell(True)]]
        xs, ys = [2.9, 5.35], [0.35, -0.95]
        x_row = 0.75
        ch_b.move_to([xs[0], 1.55, 0])
        ch_L.move_to([xs[1], 1.55, 0])
        rh_T.move_to([x_row, ys[0], 0])
        rh_S.move_to([x_row, ys[1], 0])
        for i in range(2):
            for j in range(2):
                cells[i][j].move_to([xs[j], ys[i], 0])
        hline = Line([-0.1, 1.05, 0], [6.5, 1.05, 0], color=FAINT, stroke_width=2)
        vline = Line([1.7, 1.95, 0], [1.7, -1.6, 0], color=FAINT, stroke_width=2)
        legend = T(r"arrows show the defect", font_size=26, color=DIM).move_to([4.1, -2.1, 0])
        table = VGroup(ch_b, ch_L, rh_T, rh_S, hline, vline, legend)

        with self.seg("s03") as d:
            self.go(FadeOut(self.s02_right), FadeOut(self.htag), FadeOut(self.head2),
                    FadeOut(self.plab), thumb.reset(), until=0.3)
            self.go(Create(ax), FadeIn(xl), FadeIn(yl), gg.set_defects(p=p_of(0.0) + 7.5e-6,
                                                                       q=q_of(0.0)),
                    until=1.4)
            self.go(FadeIn(anchor), FadeIn(marker), FadeIn(note), until=2.1)
            self.add(curve)
            gg.p.tracker.add_updater(lambda m: m.set_value(
                np.log10(max(p_of(max(beta.get_value(), 0.05)), 1e-12))))
            gg.q.tracker.add_updater(lambda m: m.set_value(np.log10(max(q_of(beta.get_value()),
                                                                        1e-12))))
            self.add(gg.p.tracker, gg.q.tracker)
            self.go(beta.animate.set_value(bmax), at=2.19, until=5.3,
                    rate_func=rate_functions.ease_in_out_sine)
            gg.p.tracker.clear_updaters()
            gg.q.tracker.clear_updaters()
            curve.clear_updaters()
            marker.clear_updaters()
            self.remove(gg.p.tracker, gg.q.tracker)
            # table: each purity improves in its own direction, degrades in the other
            self.go(Succession(FadeOut(VGroup(ax, xl, yl, note, anchor, curve, marker)),
                               FadeIn(table)),
                    gg.set_defects(p=0.09, q=0.2), at=5.6, until=6.7)
            self.go(FadeIn(cells[0][0], shift=0.1 * DOWN), FadeIn(cells[1][1], shift=0.1 * DOWN),
                    until=8.0)
            self.go(FadeIn(cells[0][1], shift=0.1 * UP), FadeIn(cells[1][0], shift=0.1 * UP),
                    at=8.56, until=9.4)
        self.table = VGroup(table, *[c for row in cells for c in row])

    # ================================================================ s04
    def s04(self):
        gg, thumb = self.gg, self.thumb
        # seesaw: plank on a fulcrum, the gauges stand on its ends
        px, qx = -1.05, 1.05         # gauge frame centres (spacing fixed at 2.1)
        fx = (px + qx) / 2
        y_frame = 0.25
        dy = y_frame - gg.p.frame.get_center()[1]
        dx = px - gg.p.frame.get_center()[0]
        plank_y = y_frame - 1.3 - 0.22 - 0.3 - 0.14
        plank = RoundedRectangle(width=3.9, height=0.1, corner_radius=0.05, stroke_width=0,
                                 fill_color=DIM, fill_opacity=1).move_to([fx, plank_y, 0])
        fulcrum = Triangle(stroke_width=0, fill_color=DIM, fill_opacity=1).stretch_to_fit_width(
            0.75).stretch_to_fit_height(0.6)
        fulcrum.next_to(plank, DOWN, buff=0)
        pivot = plank.get_center()
        rate = TT(r"exchange rate?", font_size=40).move_to([fx, 2.9, 0])
        qm = M("?", color=DEFECT, font_size=48)
        pg = pause_glyph().move_to([4.7, 0.3, 0])
        ang = 6 * DEGREES
        lift = (qx - fx) * np.sin(ang)

        with self.seg("s04", breath=2.0) as d:
            self.go(FadeOut(self.table), until=0.5)
            self.go(thumb.double_L(), at=0.3, until=1.0)
            self.go(thumb.double_beta(), until=1.7)
            # the seesaw rises with the gauges, so the numbers never cross the plank
            self.go(ApplyMethod(gg.shift, np.array([dx, dy, 0]), suspend_mobject_updating=False),
                    FadeIn(VGroup(plank, fulcrum), shift=np.array([dx, dy, 0])),
                    at=1.7, until=2.7)
            self.go(Write(rate), until=3.8)
            # when we double beta: thermal defect squares, spatial defect grows by ... ?
            self.go(gg.set_defects(q=0.04), at=4.4, until=5.4)
            qm.move_to([gg.p.frame.get_left()[0] - 0.45, fill_top(gg.p, 0.3) - lift, 0])
            self.go(gg.set_defects(p=0.3), until=6.4)
            self.go(Rotate(plank, ang, about_point=pivot),
                    ApplyMethod(gg.p.shift, DOWN * lift), ApplyMethod(gg.q.shift, UP * lift),
                    FadeIn(qm, scale=0.5), until=7.4)
            # pause here
            self.go(FadeIn(pg, scale=0.7), at=7.83, until=8.5)
            self.go(Circumscribe(rate, color=DEFECT, buff=0.15), at=8.82, until=10.4)
        self.s04_stage = VGroup(gg, plank, fulcrum, qm, pg, thumb)
        self.rate = rate

    # ================================================================ s05
    def s05(self):
        hdr = TT(r"the exchange rate: ", r"an exact identity", font_size=30, color=DIM)
        hdr.move_to([0, 3.25, 0])
        L1 = MT(r"S(n,2\beta)", r"=", r"S(n,\beta)^2", r"\,\frac{", r"T(2n,\beta)", r"}{",
                r"T(n,\beta)^2", r"}", font_size=46)
        for i in (0, 2):
            L1[i].set_color(SPACE)
        for i in (4, 5, 6):
            L1[i].set_color(TIME)
        L1.move_to([0, 1.35, 0])
        L2 = MT(r"\frac{", r"Z(2n,2\beta)", r"}{", r"Z(n,2\beta)^2", r"}", r"=",
                r"\frac{", r"Z(2n,\beta)^2", r"}{", r"Z(n,\beta)^4", r"}", r"\cdot",
                r"\frac{", r"Z(2n,2\beta)", r"}{", r"Z(2n,\beta)^2", r"}", r"\cdot",
                r"\frac{", r"Z(n,\beta)^4", r"}{", r"Z(n,2\beta)^2", r"}", font_size=40)
        A, B = VGroup(L2[1], L2[2], L2[3]), VGroup(L2[7], L2[8], L2[9])
        C, Dg = VGroup(L2[13], L2[14], L2[15]), VGroup(L2[19], L2[20], L2[21])
        A.set_color(SPACE)
        B.set_color(SPACE)
        C.set_color(TIME)
        Dg.set_color(TIME)
        L2.move_to([0, -0.85, 0])
        # final collapsed right-hand side; the line 'A = R' ends centred under L1
        R = MT(r"\frac{", r"Z(2n,2\beta)", r"}{", r"Z(n,2\beta)^2", r"}", font_size=40)
        R.set_color(SPACE)
        R.next_to(L2[5], RIGHT, buff=0.25)
        R.shift(UP * (A.get_center()[1] - R.get_center()[1]))
        x_shift = L1.get_center()[0] - VGroup(A, L2[5], R).get_center()[0]
        R.shift(RIGHT * x_shift)
        n, mx = identity_check()
        assert n == 35 and mx < 4e-15
        foot = T(r"ED check, 35 cases: $|\Delta\log|<4\times10^{-15}$", font_size=24, color=DIM)
        foot.to_edge(DOWN, buff=0.4)

        with self.seg("s05") as d:
            big = T(r"an exact identity", font_size=52).move_to([0, 0.4, 0])
            gauges_freeze(self.gg)
            self.go(FadeOut(self.s04_stage), FadeOut(self.rate, shift=0.25 * UP), until=0.6)
            self.go(FadeIn(big, shift=0.25 * UP), until=1.3)
            self.go(Indicate(big, color=FG, scale_factor=1.06), at=2.0, until=3.4)
            # big[0] and hdr[1] hold the same 15 glyphs: a clean move-and-shrink
            self.go(ReplacementTransform(big[0], hdr[1]), FadeIn(hdr[0]), at=3.6, until=4.4)
            self.go(Write(L1[0]), at=4.42, until=5.9)
            self.go(Write(L1[1]), Write(L1[2]), at=6.2, until=7.6)
            self.go(Write(L1[4]), Create(L1[5]), at=8.14, until=9.6)
            self.go(Write(L1[6]), at=10.69, until=11.9)
            # expand into partition functions: each Z fraction drops out of its parent term
            def drop(parent, frac):
                return AnimationGroup(Indicate(parent, color=FG, scale_factor=1.1),
                                      FadeIn(frac, shift=0.3 * DOWN))
            self.go(LaggedStart(drop(L1[0], A), FadeIn(L2[5]), drop(L1[2], B), FadeIn(L2[11]),
                                drop(L1[4], C), FadeIn(L2[17]), drop(L1[6], Dg),
                                lag_ratio=0.18),
                    at=13.21, until=14.9)
            # everything cancels: strike the pairs, clear them, then close up the survivors
            s1 = VGroup(strike(L2[7]), strike(L2[15]))
            s2 = VGroup(strike(L2[9]), strike(L2[19]))
            self.go(Create(s1), until=15.5)
            self.go(Create(s2), until=16.1)
            dead = VGroup(L2[7], L2[15], L2[9], L2[19], s1, s2, L2[8], L2[11], L2[17], L2[20])
            self.go(FadeOut(dead), until=16.6)
            self.go(A.animate.shift(RIGHT * x_shift), L2[5].animate.shift(RIGHT * x_shift),
                    ReplacementTransform(L2[13], R[1]), ReplacementTransform(L2[14], R[2]),
                    ReplacementTransform(L2[21], R[3]), until=17.4)
            ck = check_mark(0.45).next_to(L1, RIGHT, buff=0.45)
            self.go(Indicate(A, color=GAP, scale_factor=1.08), Indicate(R, color=GAP,
                                                                        scale_factor=1.08),
                    Create(ck), until=18.2)
            self.go(FadeIn(foot), at=18.23, until=19.0)
        self.L1, self.s05_rest = L1, VGroup(hdr, A, L2[5], R, ck, foot)

    # ================================================================ s06
    def s06(self):
        t1 = tag("one way to see it", buff=0.42)
        Q = MT(r"\frac{", r"S(n,2\beta)", r"}{", r"S(n,\beta)^2", r"}", r"=", r"Q", r"=",
               r"\frac{", r"T(2n,\beta)", r"}{", r"T(n,\beta)^2", r"}", font_size=40)
        VGroup(Q[1], Q[2], Q[3]).set_color(SPACE)
        VGroup(Q[9], Q[10], Q[11]).set_color(TIME)
        Q.move_to([3.55, 1.15, 0])
        tor = Torus(4.2, 2.4, L_tex="2n", beta_tex=r"2\beta")
        tor.shift(np.array([-2.85, 1.25, 0]) - tor.rect.get_center())
        ov = tor.tiling_overlays()
        F = MT(r"\log Q", r"=", r"F(2n,2\beta)", r"-2F(n,2\beta)", r"-2F(2n,\beta)",
               r"+4F(n,\beta)", font_size=36)
        F.move_to([-0.6, -1.0, 0])
        Fnote = MT(r"F=\log Z", font_size=34, color=DIM).next_to(F, RIGHT, buff=0.7)
        y2 = -2.5           # second line: the same four terms, grouped the other way
        area = MT(r"\text{area:}\quad", r"4", r"-2\cdot2", r"-2\cdot2", r"+4\cdot1", r"=0",
                  font_size=36)
        area.move_to([-0.6, y2, 0])
        dy2 = DOWN * (F.get_center()[1] - y2)
        dx34 = RIGHT * (F[4].get_center()[0] - F[3].get_center()[0])
        G2 = VGroup(F[1].copy().shift(dy2), F[2].copy().shift(dy2),
                    F[4].copy().shift(dy2 - dx34),          # -2F(2n,beta) moves left
                    F[3].copy().shift(dy2 + dx34),          # -2F(n,2beta) moves right
                    F[5].copy().shift(dy2))

        def braces(g1, g2, color, tex1, tex2):
            b1 = Brace(g1, DOWN, buff=0.1, color=color)
            b2 = Brace(g2, DOWN, buff=0.1, color=color)
            l1 = M(tex1, color=color, font_size=30).next_to(b1, DOWN, buff=0.1)
            l2 = M(tex2, color=color, font_size=30).next_to(b2, DOWN, buff=0.1)
            return VGroup(b1, b2, l1, l2)

        with self.seg("s06") as d:
            self.go(FadeOut(self.s05_rest), until=0.3)
            # divide by S(n,beta)^2: it swings under S(n,2beta); the '=' signs and Q
            # fade out/in at the ends so nothing passes through anything
            L1 = self.L1
            early, late = squish_rate_func(smooth, 0, 0.3), squish_rate_func(smooth, 0.7, 1)
            self.go(tag_in(t1), ReplacementTransform(L1[0], Q[1], path_arc=-PI / 6),
                    ReplacementTransform(L1[2], Q[3], path_arc=PI / 2),
                    ReplacementTransform(L1[4], Q[9]), ReplacementTransform(L1[5], Q[10]),
                    ReplacementTransform(L1[6], Q[11]), FadeOut(L1[1], rate_func=early),
                    FadeIn(VGroup(Q[2], Q[5], Q[6], Q[7]), rate_func=late),
                    at=0.3, until=1.5)
            self.go(FadeIn(tor), at=1.75, until=2.8)
            self.go(Write(VGroup(F[0], F[1])), FadeIn(Fnote), until=4.0)
            self.go(Indicate(Q[6], color=FG, scale_factor=1.4), until=5.2)
            # a big one, its halves and its quarters
            terms = [F[2], F[3], F[4], F[5]]
            self.go(FadeIn(ov[0]), FadeIn(terms[0], shift=0.1 * UP), at=5.77, until=6.35)
            self.go(FadeOut(ov[0]), FadeIn(ov[1]), FadeIn(terms[1], shift=0.1 * UP),
                    at=6.6, until=7.05)
            self.go(FadeOut(ov[1]), FadeIn(ov[2]), FadeIn(terms[2], shift=0.1 * UP),
                    until=7.5)
            self.go(FadeOut(ov[2]), FadeIn(ov[3]), FadeIn(terms[3], shift=0.1 * UP),
                    until=8.2)
            # area terms cancel
            self.go(LaggedStart(*[FadeIn(a, shift=0.1 * UP) for a in area], lag_ratio=0.15),
                    at=8.88, until=10.0)
            # mixed second difference: L first or beta first
            bS = braces(VGroup(F[2], F[3]), VGroup(F[4], F[5]), SPACE, r"\log S(n,2\beta)",
                        r"-2\log S(n,\beta)")
            self.go(FadeOut(ov[3]), FadeIn(bS), at=10.39, until=11.0)
            # ... doesn't care which direction comes first: same terms, other grouping
            self.go(FadeOut(area), at=11.2, until=11.5)
            self.go(TransformFromCopy(F[1], G2[0]), TransformFromCopy(F[2], G2[1]),
                    TransformFromCopy(F[4], G2[2], path_arc=-PI / 3),
                    TransformFromCopy(F[3], G2[3], path_arc=PI / 3),
                    TransformFromCopy(F[5], G2[4]), until=12.45)
            bT = braces(VGroup(G2[1], G2[2]), VGroup(G2[3], G2[4]), TIME, r"\log T(2n,\beta)",
                        r"-2\log T(n,\beta)")
            self.go(FadeIn(bT), until=13.15)
            self.go(Indicate(Q[6], color=FG, scale_factor=1.4), until=13.9)
        self.s06_all = VGroup(t1, tor, F, Fnote, bS, G2, bT)
        self.Q = Q

    # ================================================================ s07
    def s07(self):
        I1 = MT(r"S(n,2\beta)", r"=", r"S(n,\beta)^2", r"\,\frac{", r"T(2n,\beta)", r"}{",
                r"T(n,\beta)^2", r"}", font_size=42)
        for i in (0, 2):
            I1[i].set_color(SPACE)
        for i in (4, 5, 6):
            I1[i].set_color(TIME)
        I1.move_to([-2.6, 2.15, 0])
        le1 = M(r"\le 1", font_size=36, color=FG).next_to(I1[6], DOWN, buff=0.3)
        I2 = MT(r"S(n,2\beta)", r"\ge", r"S(n,\beta)^2", r"\,", r"T(2n,\beta)", font_size=42)
        I2[0].set_color(SPACE)
        I2[2].set_color(SPACE)
        I2[4].set_color(TIME)
        I2.move_to(I1, aligned_edge=LEFT).match_y(I1[0])
        legend = MT(r"p", r"=1-S(n,\beta),\qquad", r"q", r"=1-T(2n,\beta)", font_size=34)
        legend[0].set_color(SPACE)
        legend[1].set_color(SPACE)
        legend[2].set_color(TIME)
        legend[3].set_color(TIME)
        legend.next_to(I2, DOWN, buff=0.75).align_to(I2, LEFT)
        D1 = MT(r"1-S(n,2\beta)", r"\le", r"1-(1-", r"p", r")^2(1-", r"q", r")", font_size=40)
        D1[3].set_color(SPACE)
        D1[5].set_color(TIME)
        D1.next_to(legend, DOWN, buff=0.85).align_to(I2, LEFT)
        D2 = MT(r"\approx", r"2p", r"+", r"q", font_size=40)
        D2[1].set_color(SPACE)
        D2[3].set_color(TIME)
        D2.next_to(D1, DOWN, buff=0.5)
        D2.shift(RIGHT * (D1[1].get_left()[0] - D2[0].get_left()[0]))
        br = Brace(VGroup(D2[1], D2[2], D2[3]), DOWN, buff=0.12, color=DEFECT)
        loss = T("linear loss", font_size=30, color=DEFECT).next_to(br, DOWN, buff=0.12)

        # illustrative values inside the basin: 1-(1-p)^2(1-q) = 0.0967 < 0.127
        p, q = 0.03, 0.04
        gg = ch06_gauges(p=p, q=q)
        place_gauges(gg, 2.8, -0.2)
        newp = 1 - (1 - p) ** 2 * (1 - q)

        with self.seg("s07") as d:
            Q = self.Q
            self.go(FadeOut(self.s06_all), FadeOut(VGroup(Q[2], Q[5], Q[6], Q[7])), until=0.5)
            self.go(ReplacementTransform(Q[1], I1[0], path_arc=PI / 8),
                    ReplacementTransform(Q[3], I1[2], path_arc=-PI / 3),
                    ReplacementTransform(Q[9], I1[4]), ReplacementTransform(Q[10], I1[5]),
                    ReplacementTransform(Q[11], I1[6]),
                    FadeIn(I1[1], rate_func=squish_rate_func(smooth, 0.7, 1)), until=1.4)
            gauges_freeze(gg)
            self.go(FadeIn(gg), until=2.1)
            gauges_thaw(gg)
            self.go(Write(le1), Indicate(I1[6], color=TIME, scale_factor=1.15), at=2.17,
                    until=3.5)
            # drop the denominator
            self.go(FadeOut(VGroup(I1[5], I1[6], le1), shift=0.3 * DOWN),
                    ReplacementTransform(I1[0], I2[0]), ReplacementTransform(I1[1], I2[1]),
                    ReplacementTransform(I1[2], I2[2]), ReplacementTransform(I1[4], I2[4]),
                    at=3.75, until=4.9)
            self.go(FadeIn(legend), at=5.0, until=5.9)
            self.go(Write(D1), until=7.3)
            # about twice itself ...
            self.go(Write(D2[0]), Write(D2[1]), gg.set_defects(p=2 * p), at=7.4, until=8.9)
            # ... plus the thermal defect
            self.go(Write(D2[2]), Write(D2[3]), gg.set_defects(p=newp), at=9.32, until=10.3)
            self.play(*gauge_pulse(gg.p), run_time=0.6)
            self.go(GrowFromCenter(br), FadeIn(loss), at=11.0, until=11.9)
        self.I2 = I2
        self.s07_rest = VGroup(legend, D1, D2, br, loss, gg)
        self.s07_gg = gg

    # ================================================================ s08
    def s08(self):
        I2 = self.I2
        M1 = MT(r"T(4n,\beta)", r"=", r"T(2n,\beta)^2", r"\,\frac{", r"S(2n,2\beta)", r"}{",
                r"S(2n,\beta)^2", r"}", font_size=42)
        M1[0].set_color(TIME)
        M1[2].set_color(TIME)
        for i in (4, 5, 6):
            M1[i].set_color(SPACE)
        M2 = MT(r"T(4n,\beta)", r"\ge", r"T(2n,\beta)^2", r"\,", r"S(2n,2\beta)", font_size=42)
        M2[0].set_color(TIME)
        M2[2].set_color(TIME)
        M2[4].set_color(SPACE)
        # centre stage: I2 on top, the mirror below
        I2_tgt = I2.copy().move_to([0, 1.45, 0])
        M1.move_to([0, -0.6, 0]).align_to(I2_tgt, LEFT)
        M2.move_to(M1, aligned_edge=LEFT).match_y(M1[0])

        def coin_trip(kind, src, dst):
            c = pay_coin(kind).move_to(src.get_top() + UP * 0.38)
            end = dst.get_top() + UP * 0.38
            lab = TT(r"$" + kind + r"$", r" pays", font_size=35,   # ~28.7 pt after scale 0.82
                     colors={0: TIME if kind == "T" else SPACE})
            lab.next_to(end, LEFT, buff=0.42)
            return c, end, lab

        with self.seg("s08") as d:
            gauges_freeze(self.s07_gg)
            self.go(FadeOut(self.s07_rest), I2.animate.move_to(I2_tgt), until=0.9)
            cT, eT, lT = coin_trip("T", I2[4], I2[0])
            self.go(GrowFromCenter(cT), until=1.3)
            self.go(cT.animate(path_arc=PI / 2).move_to(eT), FadeIn(lT), until=2.2)
            # the mirror identity
            self.go(Write(M1), at=2.2, until=4.0)
            self.go(FadeOut(VGroup(M1[5], M1[6]), shift=0.3 * DOWN),
                    ReplacementTransform(M1[0], M2[0]), ReplacementTransform(M1[1], M2[1]),
                    ReplacementTransform(M1[2], M2[2]), ReplacementTransform(M1[4], M2[4]),
                    at=4.0, until=4.9)
            cS, eS, lS_ = coin_trip("S", M2[4], M2[0])
            self.go(GrowFromCenter(cS), until=5.3)
            self.go(cS.animate(path_arc=PI / 2).move_to(eS), FadeIn(lS_), until=6.1)
            # now chain them
            panel = VGroup(I2, cT, lT, M2, cS, lS_)
            st = Staircase("symbolic", x_length=6.6, y_length=4.7).to_edge(LEFT, buff=0.5)
            st.shift(DOWN * 0.25)
            tr = st.tromino(0, 0)
            lS = tr.label_S(r"S(n,\beta)\!:\ p")
            lT = tr.label_T(r"T(2n,\beta)\!:\ q", direction=LEFT, buff=0.12)
            self.go(panel.animate.scale(0.82).to_corner(UR, buff=0.5), at=6.9, until=7.8)
            self.go(FadeIn(st), until=8.6)
            self.go(Create(tr.S), FadeIn(tr.dots[0]), FadeIn(tr.dots[1]), FadeIn(lS),
                    at=8.98, until=10.2)
            self.go(Create(tr.T), FadeIn(tr.dots[2]), FadeIn(lT), at=10.96, until=12.2)
            beta_line = DashedLine(st.pt(-0.45, 0), st.pt(0, 0), color=TIME, stroke_width=2.5,
                                   dash_length=0.08)
            self.go(Create(beta_line), Indicate(st.ticks[1][0], color=TIME, scale_factor=1.4),
                    Indicate(VGroup(tr.dots[0], tr.dots[1]), color=TIME, scale_factor=1.6),
                    at=12.9, until=13.7)
        self.st, self.tr, self.lS, self.lT = st, tr, lS, lT
        self.panel, self.beta_line = panel, beta_line

    # ================================================================ s09
    def s09(self):
        st, tr = self.st, self.tr
        lf = tr.leapfrog(labels=[r"\approx2p+q", r"p_+", r"\approx2q+p_+", r"q_+"])
        it1 = TT(r"1.\ double ", r"$\beta$", r" for ", r"$S$", r" (paid by ", r"$T$", r")",
                 colors={1: TIME, 3: SPACE, 5: TIME}, font_size=30)
        it2 = TT(r"2.\ square in space", font_size=30)
        f2 = MT(r"p_+", r"=f\big(1-(1-", r"p", r")^2(1-", r"q", r")\big)", font_size=34)
        f2[0].set_color(SPACE)
        f2[2].set_color(SPACE)
        f2[4].set_color(TIME)
        it3 = TT(r"3.\ double ", r"$L$", r" for ", r"$T$", r" (paid by ", r"$S$", r")",
                 colors={1: SPACE, 3: TIME, 5: SPACE}, font_size=30)
        it4 = TT(r"4.\ square in time", font_size=30)
        f4 = MT(r"q_+", r"=f\big(1-(1-", r"q", r")^2(1-", r"p_+", r")\big)", font_size=34)
        f4[0].set_color(TIME)
        f4[2].set_color(TIME)
        f4[4].set_color(SPACE)
        fdef = MT(r"f(u)=\frac{u^2}{2(1-u)^2}", font_size=34, color=DIM)
        col = VGroup(it1, it2, f2, it3, it4, f4).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        f2.shift(RIGHT * 0.45)
        f4.shift(RIGHT * 0.45)
        it3.shift(DOWN * 0.1)
        col.to_edge(RIGHT, buff=0.5).shift(UP * (0.55 - col.get_center()[1]))
        fdef.next_to(col, DOWN, buff=0.45).align_to(col, LEFT).shift(RIGHT * 0.45)
        sq_tag = T(r"squaring:", font_size=28, color=DIM).next_to(fdef, LEFT, buff=0.2)
        fgroup = VGroup(sq_tag, fdef)
        fgroup.align_to(col, LEFT)

        with self.seg("s09") as d:
            self.go(FadeOut(self.panel), FadeOut(self.beta_line), until=0.6)
            self.go(FadeIn(it1, shift=0.1 * LEFT), at=0.6, until=1.4)
            self.go(lf.steps[0], at=1.3, until=3.6)
            # step two
            self.go(FadeIn(it2, shift=0.1 * LEFT), at=4.52, until=5.2)
            self.go(lf.steps[1], at=5.2, until=6.9)
            self.remove(lf.labels[0])
            self.go(FadeIn(f2), FadeIn(fgroup), until=7.6)
            # step three
            self.go(FadeIn(it3, shift=0.1 * LEFT), at=7.99, until=8.7)
            self.go(lf.steps[2], at=8.9, until=11.4)
            # step four
            self.go(FadeIn(it4, shift=0.1 * LEFT), at=12.77, until=13.4)
            self.go(lf.steps[3], FadeIn(f4), until=14.8)
            self.remove(lf.labels[2])
        self.lf = lf
        self.s09_col = VGroup(col, fgroup)

    # ================================================================ s10
    def s10(self):
        st, tr, lf = self.st, self.tr, self.lf
        new = lf.new
        arrow = tr.diag_arrow()
        labs = VGroup(self.lS, self.lT, lf.labels[1], lf.labels[3])
        tx, ty = st.ticks
        slider = VGroup(tr.S.copy(), tr.T.copy(), tr.dots.copy())

        # zoomed-out plane: same frame, four doublings in each direction visible
        bare = Staircase("bare", x_length=7.2, y_length=6.0)
        bare.move_to([-0.3, -0.25, 0])
        g0 = bare.tromino(0.5, 0.5).set_opacity(0.3)      # where we were: solid ghost
        n1 = bare.tromino(1.5, 1.5)                          # where we are
        a1 = DashedLine(bare.pt(0.5, 0.5), bare.pt(1.5, 1.5), color=DIM, stroke_width=3,
                        dash_length=0.09, buff=0.1).add_tip(tip_length=0.18, tip_width=0.16)

        def future(x0, y0):
            """Where we go next: dashed outline, no corner dots."""
            pp = bare.pt
            return VGroup(DashedLine(pp(x0, y0), pp(x0 + 1, y0), color=SPACE, stroke_width=4,
                                     dash_length=0.1),
                          DashedLine(pp(x0 + 1, y0), pp(x0 + 1, y0 + 1), color=TIME,
                                     stroke_width=4, dash_length=0.1)).set_stroke(opacity=0.55)
        ghosts = VGroup(*[future(1.5 + k, 1.5 + k) for k in (1, 2)])
        more = VGroup(*[DashedLine(bare.pt(0.5 + k, 0.5 + k), bare.pt(1.5 + k, 1.5 + k),
                                   color=DIM, stroke_width=3, dash_length=0.09, buff=0.1)
                        .add_tip(tip_length=0.18, tip_width=0.16).set_opacity(0.6)
                        for k in (1, 2)])
        c_old = M(r"(n,\beta)", font_size=28, color=DIM).next_to(bare.pt(0.5, 0.5), DOWN,
                                                                  buff=0.18)
        c_new = M(r"(2n,2\beta)", font_size=28, color=DIM).next_to(bare.pt(1.5, 1.5), UL,
                                                                    buff=0.12)

        with self.seg("s10") as d:
            self.go(self.s09_col.animate.set_opacity(0.35), FadeOut(labs), until=0.5)
            self.go(tr.ghost(), Indicate(tx[0], color=SPACE, scale_factor=1.5),
                    Indicate(ty[0], color=TIME, scale_factor=1.5), at=0.4, until=1.5)
            self.go(Create(arrow), at=1.7, until=2.6)
            self.go(Indicate(tx[1], color=SPACE, scale_factor=1.5),
                    Indicate(ty[1], color=TIME, scale_factor=1.5), until=3.5)
            # same shape: the old pair slides onto the new one
            self.at(4.1)
            self.add(slider)
            self.go(slider.animate.shift(st.unit), until=4.85)
            self.remove(slider)
            self.go(Indicate(new, color=FG, scale_factor=1.12), at=5.0, until=5.85)
            # one step up a staircase: zoom out
            # (the two planes are built differently: cross-fade them, move only the pieces)
            self.go(FadeOut(VGroup(st.ax, st.labels, st.ticks)), FadeOut(self.s09_col),
                    FadeIn(VGroup(bare.ax, bare.labels)),
                    Transform(tr, g0), Transform(new, n1), Transform(arrow, a1),
                    at=6.0, until=6.9)
            self.go(LaggedStart(*[AnimationGroup(Create(m), Create(g))
                                  for m, g in zip(more, ghosts)], lag_ratio=0.5),
                    FadeIn(c_old), FadeIn(c_new), until=7.7)
        self.s10_all = VGroup(bare.ax, bare.labels, tr, new, arrow, ghosts, more, c_old, c_new)

    # ================================================================ s11
    def s11(self):
        # left: the cost count
        hd = MT(r"p\approx q\approx u", font_size=34, color=DIM)
        La = MT(r"1-(1-u)^3", r"\approx", r"3u", font_size=40)
        Lb = MT(r"f(3u)", r"\approx", r"\frac{(3u)^2}{2}", r"=", r"\tfrac92\,u^2", font_size=40)
        Lc = MT(r"f\big(1-(1-u)^3\big)", r"=", r"G(u)\,u^2", font_size=40)
        Gd = MT(r"G(u)=\tfrac12\big[(1-u)^{-1}+(1-u)^{-2}+(1-u)^{-3}\big]^2", font_size=34,
                color=FG)
        Ln = MT(r"G(0)=\tfrac92,\qquad G(0.127)\approx7.8", font_size=34)
        grow = T("corrections grow", font_size=28, color=DIM)
        left = VGroup(hd, La, Lb, Lc, Gd, Ln).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        left.to_edge(LEFT, buff=0.45).shift(UP * 0.1)
        Lc.shift(DOWN * 0.15)
        Gd.shift(DOWN * 0.15)
        Ln.shift(DOWN * 0.2)
        grow.next_to(Ln, DOWN, buff=0.15).align_to(Ln, LEFT)
        Lb[4].set_color(DEFECT)

        # right: cobweb
        ax = Axes(x_range=[0, 0.16, 0.05], y_range=[0, 0.16, 0.05], x_length=4.5, y_length=4.5,
                  tips=False,
                  axis_config={"color": DIM, "stroke_width": 2, "tick_size": 0.06,
                               "font_size": 24, "decimal_number_config":
                                   {"num_decimal_places": 2, "color": DIM}},
                  x_axis_config={"numbers_to_include": [0.05, 0.10, 0.15]},
                  y_axis_config={"numbers_to_include": [0.05, 0.10, 0.15]})
        ax.move_to([3.85, -0.15, 0])
        xl = M("u", color=DEFECT, font_size=34).next_to(ax.x_axis.get_end(), RIGHT, buff=0.15)
        yl = M(r"u_{\rm next}", color=DEFECT, font_size=32).next_to(ax.y_axis.get_end(), UP,
                                                                    buff=0.15)
        diag = ax.plot(lambda u: u, x_range=[0, 0.16], color=DIM, stroke_width=3)
        u_cap = 0.138811
        curve = ax.plot(lambda u: G(u) * u * u, x_range=[0, u_cap, u_cap / 80], color=DEFECT,
                        stroke_width=4)
        def key(color, tex, w=4):
            return VGroup(Line(ORIGIN, RIGHT * 0.45, color=color, stroke_width=w),
                          M(tex, color=color, font_size=28)).arrange(RIGHT, buff=0.15)
        clab = key(DEFECT, r"u_{\rm next}=G(u)\,u^2")
        dlab = key(DIM, r"u_{\rm next}=u", w=3)
        VGroup(clab, dlab).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(
            ax.c2p(0.006, 0.158), aligned_edge=UL)
        edge = DashedLine(ax.c2p(U_STAR, 0), ax.c2p(U_STAR, 0.16) + UP * 0.3, color=DEFECT,
                          stroke_width=3, dash_length=0.08)
        elab = T(r"basin edge $\approx0.127$ (computed)", font_size=26, color=DEFECT)
        elab.next_to(edge.get_end(), UP, buff=0.08)
        elab.shift(RIGHT * min(0, 6.55 - elab.get_right()[0]))
        tick8 = Line(ax.c2p(0.125, 0) + DOWN * 0.12, ax.c2p(0.125, 0) + UP * 0.12, color=DIM,
                     stroke_width=3)
        lab8 = M(r"1/8", color=DIM, font_size=26).next_to(tick8, DOWN, buff=0.42)

        def cobweb(u0, n, color, cap=0.16):
            pts = [ax.c2p(u0, 0)]
            u = u0
            for _ in range(n):
                v = G(u) * u * u
                if v > cap:
                    pts.append(ax.c2p(u, cap))
                    break
                pts.append(ax.c2p(u, v))
                pts.append(ax.c2p(v, v))
                u = v
            m = VMobject(stroke_color=color, stroke_width=3.5)
            m.set_points_as_corners(pts)
            return m
        good = cobweb(0.100, 4, GAP)
        bad = cobweb(0.135, 3, SX)
        bad_tip = Triangle(fill_color=SX, fill_opacity=1, stroke_width=0).scale(0.09).move_to(
            bad.get_end() + DOWN * 0.04)
        d_good = Dot(ax.c2p(0.1, 0), radius=0.07, color=GAP)
        d_bad = Dot(ax.c2p(0.135, 0), radius=0.07, color=SX)
        basin = Rectangle(width=ax.c2p(U_STAR, 0)[0] - ax.c2p(0, 0)[0],
                          height=ax.c2p(0, 0.16)[1] - ax.c2p(0, 0)[1], stroke_width=0,
                          fill_color=GAP, fill_opacity=0.15)
        basin.move_to(ax.c2p(0, 0), aligned_edge=DL)
        blab = T("basin", font_size=36, color=GAP).move_to(ax.c2p(0.045, 0.098))

        with self.seg("s11") as d:
            self.go(FadeOut(self.s10_all), until=0.6)
            self.go(FadeIn(hd), until=1.3)
            self.go(Write(La), at=1.53, until=2.8)
            self.go(Write(VGroup(Lb[0], Lb[1], Lb[2])), at=2.9, until=4.4)
            self.go(Write(VGroup(Lb[3], Lb[4])), at=4.87, until=5.8)
            self.play(Indicate(Lb[4], color=DEFECT, scale_factor=1.25), run_time=0.8)
            # exact correction factors
            self.go(VGroup(hd, La, Lb).animate.set_opacity(0.45), Write(Lc), at=7.41, until=8.4)
            self.go(FadeIn(Gd, shift=0.1 * UP), until=9.25)
            # quadratic gain beats linear loss below about 0.127
            self.go(Create(ax), FadeIn(xl), FadeIn(yl), Create(diag), FadeIn(dlab), at=9.4,
                    until=10.3)
            self.go(Create(curve), FadeIn(clab), until=11.2)
            # gain beats loss: below the edge the defect falls to zero ...
            self.go(Create(edge), until=11.9)
            self.go(FadeIn(d_good), Create(good), until=13.2)
            # ... below about 0.127
            self.go(FadeIn(elab), FadeIn(Ln), FadeIn(grow), at=13.3, until=14.1)
            # just above one eighth
            self.go(Create(tick8), FadeIn(lab8), at=14.5, until=15.2)
            # above the edge it escapes
            self.go(FadeIn(d_bad), Create(bad), until=16.1)
            self.add(bad_tip)
            # the basin
            self.go(FadeIn(basin), Write(blab), at=16.15, until=17.3)
        self.s11_all = VGroup(hd, La, Lb, Lc, Gd, Ln, grow, ax, xl, yl, diag, curve, clab, dlab,
                              edge, elab, tick8, lab8, good, bad, bad_tip, d_good, d_bad, basin,
                              blab)

    # ================================================================ s12
    def s12(self):
        rows = dyadic_row()
        assert np.allclose([u for _, u, _ in rows], [0.01, 0.0005, 1.25e-06, 7.8125e-12], rtol=1e-9)
        vals = [r"1\times10^{-2}", r"5\times10^{-4}", r"1.25\times10^{-6}",
                r"7.8125\times10^{-12}"]
        st = Staircase("bare", x_length=4.3, y_length=5.0).to_edge(LEFT, buff=0.45)
        st.shift(UP * (-0.3 - st.get_center()[1]))
        tr = st.tromino(0.5, 0.5)
        # table: scale (symbolic), defect u_j, number of zeros
        x_sc, x_u, x_bar, y0, dy = -1.05, -0.25, 3.3, 1.15, 1.0
        k = 2.65 / rows[-1][2]
        scs, texts, bars, nums = VGroup(), VGroup(), VGroup(), VGroup()
        for j, (jj, u, z) in enumerate(rows):
            y = y0 - j * dy
            scs.add(M(["n_0", "2n_0", "4n_0", "8n_0"][j], font_size=34, color=FG).move_to(
                [x_sc, y, 0]))
            t = MT(r"u_{%d}" % j, r"=", vals[j], font_size=34)
            t[0].set_color(DEFECT)
            t.move_to([x_u, y, 0], aligned_edge=LEFT)
            texts.add(t)
            b = Rectangle(width=z * k, height=0.34, stroke_width=0, fill_color=DEFECT,
                          fill_opacity=0.75)
            b.move_to([x_bar, y, 0], aligned_edge=LEFT)
            bars.add(b)
            nums.add(M(f"{z:.1f}", font_size=26, color=DIM).next_to(b, RIGHT, buff=0.12))
        h_y = y0 + 1.0
        zeros = T("number of zeros", font_size=28, color=DIM).move_to([x_bar, h_y, 0],
                                                                       aligned_edge=LEFT)
        zsub = MT(r"(-\log_{10}u)", font_size=26, color=DIM).next_to(zeros, DOWN, buff=0.12)
        zsub.align_to(zeros, LEFT)
        hdr = VGroup(T("scale", font_size=28, color=DIM).move_to([x_sc, h_y, 0]),
                     T("defect", font_size=28, color=DIM).move_to([x_u, h_y, 0],
                                                                  aligned_edge=LEFT),
                     zeros, zsub)
        sc_note = MT(r"\text{scale } 2^j:\ \ (2^j n_0,\,2^j\beta_0)", font_size=28, color=DIM)
        sc_note.next_to(texts, DOWN, buff=0.5).align_to(texts, LEFT)

        with self.seg("s12") as d:
            self.go(FadeOut(self.s11_all), until=0.45)
            self.go(FadeIn(st), FadeIn(tr), until=1.0)
            self.go(FadeIn(hdr), FadeIn(sc_note), until=1.6)
            self.go(FadeIn(scs[0]), Write(texts[0]), GrowFromEdge(bars[0], LEFT),
                    FadeIn(nums[0]), at=1.65, until=2.9)
            beats = [(3.34, 5.6), (6.02, 7.4), (7.82, 9.1)]
            for j, (a, b) in enumerate(beats, start=1):
                ghost = tr.copy().set_opacity(0.22)
                self.add(ghost)
                self.go(tr.step(), FadeIn(scs[j]), at=a, until=a + 0.7)
                self.go(Write(texts[j]), GrowFromEdge(bars[j], LEFT), FadeIn(nums[j]),
                        until=b)
            # the number of zeros doubles every step
            self.go(LaggedStart(*[Indicate(b, color=DEFECT, scale_factor=1.06) for b in bars],
                                lag_ratio=0.35),
                    LaggedStart(*[Indicate(n, color=FG, scale_factor=1.3) for n in nums],
                                lag_ratio=0.35),
                    at=9.84, until=11.9)
