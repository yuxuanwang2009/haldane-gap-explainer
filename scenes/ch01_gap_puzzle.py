"""ch01: A gap that refuses to close.

Hook with real exact-diagonalization data (GAPPLOT motif), the uniformity
question, the 1984 cautionary tale, the puzzle (all six objections), the
status card, and a three-panel preview of the method.

Cue times inside each segment are seconds into its narration clip, read off
the clip's pauses (ffmpeg silencedetect) and rescaled automatically if the
clip is regenerated with a different length (see D0 and Ch01.cue).
"""
from contextlib import contextmanager

from motifs import *  # noqa: F401,F403  (also visuals.*, common.*)

# clip lengths at the time the cue times were measured
D0 = {"s01": 12.675, "s02": 11.95, "s03": 15.65, "s04": 12.5, "s05": 14.95,
      "s06": 6.7, "s07": 22.575, "s08": 11.625}


# ------------------------------------------------------------------ helpers
def MM(*parts, **kw):
    """M() with several substrings (for highlighting parts)."""
    kw.setdefault("color", FG)
    return MathTex(*parts, tex_template=TEX_TEMPLATE, **kw)


def TT(*parts, **kw):
    """T() with several substrings."""
    kw.setdefault("color", FG)
    return Tex(*parts, tex_template=TEX_TEMPLATE, **kw)


def wobble(arrows, amp=12 * DEGREES, **kw):
    """'Quantum wobble': each arrow swings +amp, back, -amp, back about its own
    centre, alternating sign from site to site."""
    saved = [a.copy() for a in arrows]

    def upd(g, alpha):
        f = np.sin(TAU * alpha)
        for j, (a, s) in enumerate(zip(g, saved)):
            a.become(s)
            a.rotate(amp * f * (1 if j % 2 == 0 else -1), about_point=s.get_center())
    return UpdateFromAlphaFunc(arrows, upd, **kw)


def bond_arc(center, radius, n, phase, color=FG, width=8):
    """Bright arc along the ring between two neighbouring sites (bond 0 at
    phase 0, between the top site and the next one counter-clockwise)."""
    return Arc(radius=radius, start_angle=PI / 2 + phase, angle=TAU / n,
               arc_center=np.array(center), stroke_color=color, stroke_width=width)


def mini_ring(n, r, color=INTEGER):
    """Small spin ring of radius r (same look as visuals.spin_ring, scaled)."""
    g = spin_ring(n, radius=1.6, color=color, length=0.55)
    g.scale(r / 1.6)
    g[2].set_stroke(width=max(2.5, 5 * np.sqrt(r / 1.6)))
    return g


def grow_arrows(arrows, lag_ratio=0.12):
    """Arrows grow out of their centres with the tips scaling along with the
    shafts (GrowFromCenter on an Arrow keeps full-size tips: a row of stray
    arrowheads in the first frames)."""
    for a in arrows:
        a.save_state()
        a.scale(0.02, scale_tips=True)
    return LaggedStart(*[Restore(a) for a in arrows], lag_ratio=lag_ratio)


CORNER_SCALE = 0.4


def corner_ring(n, color, center):
    """The s01 ring (radius 1.6) with n sites, shrunk into a corner of s02.
    Arrows get shorter as the sites get denser, so neighbours never touch."""
    sp = TAU * 1.6 / n
    length = min(0.55, 0.7 * sp)
    g = spin_ring(n, radius=1.6, color=color, length=length)
    for a in g[2]:
        a.set_stroke(width=2.75, family=False)
    g.scale(CORNER_SCALE)
    g.shift(np.array(center, dtype=float) - g[0].get_center())
    return g


def ring_tracker(color, center, counter, n_max, n_min=10):
    """Updater for a corner ring: it gains sites as the L counter climbs past
    n_min (stops at n_max, the largest ring diagonalized for that spin).
    Uses become() so the ring stays the same object: the Cairo renderer keeps
    a flat list of a play's moving mobjects, so a swapped-out child would
    still be drawn until the play ends."""
    state = {"n": n_min}

    def upd(m):
        n = int(np.clip(int(round(counter[1].get_value())), n_min, n_max))
        if n != state["n"]:
            state["n"] = n
            m.become(corner_ring(n, color, center))
    return upd


def what_if_curves(plot):
    """Three DIM dashed 'what-if' continuations of the spin-1 data beyond L = 16.
    All three start just left of the L = 16 square and follow one plausible decay
    toward 0.41; one settles there, the other two bend down and reach gamma = 0
    only as 1/L -> 0 (every finite ring keeps a gap)."""
    L, g = plot.one_data[-1]
    xs = 1 / L
    xa = xs - 0.001                    # leave the square marker clean

    def settle(x):
        if x <= 0:
            return 0.4105
        return 0.4105 + (g - 0.4105) * np.exp(-(1 / x - L) / 4.5)

    def dive(w):
        def f(x):
            return settle(x) * np.tanh(x / w) / np.tanh(xs / w)
        return f

    xs_grid = np.unique(np.concatenate([[0.0], np.geomspace(1e-5, xa, 1500),
                                        np.linspace(0, xa, 1500)]))[::-1]   # drawn leftwards
    curves = VGroup()
    for f in (settle, dive(0.012), dive(0.004)):
        pts = np.array([plot.c2p(x, f(x)) for x in xs_grid])
        curves.add(_dashed_path(pts))
    return curves


def _dashed_path(pts, period=0.29, ratio=0.55, color=DIM, width=3):
    """Dashes of one fixed screen length laid along a dense polyline, starting at
    its first point: curves that share a stretch (the what-if fan) then have
    their dashes in phase there instead of a busy double pattern."""
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = cum[-1]
    dashes = VGroup()
    s = 0.0
    while s < total - 0.02:
        e = min(total, s + ratio * period)
        ss = np.linspace(s, e, 10)
        P = np.stack([np.interp(ss, cum, pts[:, i]) for i in range(3)], axis=1)
        d = VMobject(stroke_color=color, stroke_width=width)
        d.set_points_as_corners(P)
        dashes.add(d)
        s += period
    return dashes


def align_status_rows(card):
    """Status-card rows: icons centred in one fixed-width column, all texts
    starting at the same x (the circle and the checks differ in width)."""
    icons = [ln[0] for ln in card.lines]
    txts = [ln[1] for ln in card.lines]
    wmax = max(ic.width for ic in icons)
    xl = min(ic.get_left()[0] for ic in icons)
    for ic, tx in zip(icons, txts):
        ic.set_x(xl + wmax / 2)
        tx.shift(RIGHT * (xl + wmax + 0.3 - tx.get_left()[0]))
    return card


def small_gap_axes(center=(0, -0.45, 0)):
    """s05 panel: gap versus L for L = 4..10."""
    ax = Axes(x_range=[3, 11, 1], y_range=[0, 1.05, 0.2], x_length=6.4, y_length=3.6,
              tips=False,
              axis_config={"color": DIM, "stroke_width": 2, "include_ticks": True,
                           "tick_size": 0.06, "font_size": 24},
              x_axis_config={"numbers_to_include": [4, 6, 8, 10],
                             "decimal_number_config": {"num_decimal_places": 0, "color": DIM}},
              y_axis_config={"numbers_to_include": [0.2, 0.4, 0.6, 0.8, 1.0],
                             "decimal_number_config": {"num_decimal_places": 1, "color": DIM}})
    mid = (ax.c2p(3, 0) + ax.c2p(11, 1.05)) / 2
    ax.shift(np.array(center, dtype=float) - mid)
    xl = M("L", font_size=32).next_to(ax.c2p(11, 0), RIGHT, buff=0.2)
    yl = M(r"\gamma_L", font_size=32).next_to(ax.c2p(3, 1.05), UR, buff=0.12)
    return ax, xl, yl


def series(ax, data, marker, color):
    pts = VGroup(*[marker(ax.c2p(L, g)) for L, g in data])
    line = VMobject(stroke_color=color, stroke_width=2, stroke_opacity=0.5)
    line.set_points_as_corners([ax.c2p(L, g) for L, g in data])
    return pts, line


class Ch01(NarratedScene):
    CHAPTER = "ch01"

    # ---------------------------------------------------------- timing
    @contextmanager
    def seg(self, sid, breath=None):
        with self.voice(sid, breath=breath) as d:
            self._t0 = self.renderer.time
            self._k = d / D0[sid]
            yield d

    def cue(self, t):
        """Wait until t seconds (clip time, measured scale) into the segment."""
        dt = t * self._k - (self.renderer.time - self._t0)
        if dt > 0.04:
            self.wait(dt)

    def rt(self, s):
        return s * self._k

    # ---------------------------------------------------------- scene
    def construct(self):
        rt = self.rt

        # ============================================================ s01
        with self.seg("s01") as d:
            ringL = spin_ring(10, radius=1.6, color=HALF).move_to([-3.6, -0.3, 0])
            ringR = spin_ring(10, radius=1.6, color=INTEGER).move_to([3.6, -0.3, 0])
            labL = T(r"spin $\tfrac12$", color=HALF, font_size=36).next_to(ringL, DOWN, buff=0.35)
            labR = T(r"spin $1$", color=INTEGER, font_size=36).next_to(ringR, DOWN, buff=0.35)
            # common baseline: the fraction makes the left label taller, so next_to
            # (which aligns tops) would drop its "spin" lower; align the "s" glyphs
            labL.shift(UP * (labR[0][0].get_bottom()[1] - labL[0][0].get_bottom()[1]))
            H = MM(r"H_L=\sum_{j=0}^{L-1}", r"\mathbf S_j\cdot\mathbf S_{j+1}", r",\qquad",
                  r"\mathbf S_L=\mathbf S_0", font_size=40).move_to([0, 2.95, 0])

            def build_ring(r):
                return AnimationGroup(
                    Create(r[0]), FadeIn(r[1]), grow_arrows(r[2], lag_ratio=0.12),
                    lag_ratio=0.15)
            # "Here are two rings of quantum spins:"
            self.play(build_ring(ringL), build_ring(ringR), run_time=rt(2.2))
            # "spin one-half on the left, spin one on the right."
            self.cue(2.7)
            self.play(FadeIn(labL, shift=0.15 * UP), run_time=rt(0.6))
            self.cue(4.0)
            self.play(FadeIn(labR, shift=0.15 * UP), run_time=rt(0.6))
            # "Neighbors want to point opposite ways,"
            self.cue(5.8)
            cL, cR = ringL[0].get_center(), ringR[0].get_center()
            arcL, arcR = bond_arc(cL, 1.6, 10, 0), bond_arc(cR, 1.6, 10, 0)
            self.play(Create(arcL), Create(arcR), run_time=rt(0.5))
            self.bring_to_front(ringL[2], ringR[2])
            self.play(wobble(ringL[2]), wobble(ringR[2]), run_time=rt(1.6), rate_func=linear)
            # "and that is the whole Hamiltonian:"
            self.cue(8.0)
            self.play(Write(H), run_time=rt(1.6))
            # "S dot S, summed around the ring."
            self.cue(10.1)
            box = SurroundingRectangle(H[1], buff=0.08, corner_radius=0.08,
                                       stroke_color=FG, stroke_width=2)
            self.play(Create(box), run_time=rt(0.4))
            ph = ValueTracker(0.0)
            arcL.add_updater(lambda m: m.become(bond_arc(cL, 1.6, 10, ph.get_value())))
            arcR.add_updater(lambda m: m.become(bond_arc(cR, 1.6, 10, ph.get_value())))
            self.play(ph.animate.set_value(TAU), run_time=rt(1.5),
                      rate_func=rate_functions.ease_in_out_sine)
            arcL.clear_updaters()
            arcR.clear_updaters()
            self.play(Indicate(H[3], color=FG, scale_factor=1.12), FadeOut(box, arcL, arcR),
                      run_time=rt(0.6))

        # ============================================================ s02
        with self.seg("s02") as d:
            plot = GapPlot()
            ctr = plot.counter()
            cap = caption(r"exact diagonalization, periodic rings").to_edge(DOWN, buff=0.33)
            cornL, cornR = np.array([-5.75, 2.85, 0]), np.array([5.75, 2.85, 0])
            # "Make the rings longer"
            self.play(FadeOut(H, labL, labR),
                      ringL.animate.scale(CORNER_SCALE).move_to(cornL),
                      ringR.animate.scale(CORNER_SCALE).move_to(cornR),
                      run_time=rt(1.4))
            # "and track the gap,"
            self.play(plot.build_axes(), run_time=rt(1.4))
            self.add(ctr)
            # the corner rings gain sites as the L counter climbs (10 -> 24 / 10 -> 16)
            ringL.add_updater(ring_tracker(HALF, cornL, ctr, n_max=24))
            ringR.add_updater(ring_tracker(INTEGER, cornR, ctr, n_max=16))
            # points arrive in L order while the clip runs on:
            # "the energy of the first excited state." (2.73-4.78) -> y label pulses
            # "These are exact diagonalizations,"      (5.42-7.63) -> caption
            # "up to 24 sites for spin one-half"       (7.99-)     -> spin 1/2 label
            t0, T_ = 2.8, 7.4
            self.cue(t0)

            def win(a, b):        # squish window in clip seconds
                return max(0.0, (a - t0) / T_), min(1.0, (b - t0) / T_)
            sl = plot.series_labels()
            self.play(plot.build_data(counter=ctr),
                      Indicate(plot.y_label, color=GAP, scale_factor=1.15,
                               rate_func=squish_rate_func(there_and_back, *win(2.9, 4.6))),
                      FadeIn(cap, shift=0.1 * UP, rate_func=squish_rate_func(smooth, *win(5.4, 6.0))),
                      FadeIn(sl[0], shift=0.1 * DOWN,
                             rate_func=squish_rate_func(smooth, *win(9.5, 10.1))),
                      run_time=rt(T_))
            ringL.clear_updaters()
            ringR.clear_updaters()
            # "and 16 for spin one."
            self.cue(10.4)
            self.play(FadeIn(sl[1], shift=0.1 * UP), run_time=rt(0.6))

        # ============================================================ s03
        with self.seg("s03") as d:
            # "For spin one-half, the gap falls like one over the length,"
            self.cue(0.3)
            self.play(LaggedStart(*[Indicate(p, color=FG, scale_factor=1.6) for p in plot.half_pts],
                                  lag_ratio=0.08), run_time=rt(1.1))
            hg = plot.half_guide()
            self.play(Create(hg[0]), run_time=rt(1.6))
            # "on its way to zero."
            self.cue(3.6)
            self.play(FadeIn(hg[1], shift=0.1 * LEFT), run_time=rt(0.6))
            # "For spin one, it seems to level off,"
            self.cue(5.3)
            self.play(LaggedStart(*[Indicate(p, color=FG, scale_factor=1.6) for p in plot.one_pts],
                                  lag_ratio=0.1), run_time=rt(1.0))
            lit = plot.literature_line()
            self.play(Create(lit[0]), run_time=rt(1.0))
            # "near 0.41."
            self.cue(7.7)
            self.play(Create(lit[1]), FadeIn(lit[2]), run_time=rt(0.7))
            # "Duncan Haldane predicted this difference in 1981, and published it in 1983."
            hal = TT(r"Haldane: 1981 (formulated)", r" $\cdot$ 1983 (published)",
                    font_size=26, color=DIM).move_to([0, 3.3, 0])
            self.cue(9.9)
            self.play(FadeIn(hal[0], shift=0.1 * DOWN), run_time=rt(0.8))
            # "this difference"
            self.cue(11.2)
            self.play(Indicate(ringL, color=HALF, scale_factor=1.15),
                      Indicate(ringR, color=INTEGER, scale_factor=1.15), run_time=rt(1.0))
            self.cue(13.3)
            self.play(FadeIn(hal[1], shift=0.1 * DOWN), run_time=rt(0.6))

        # ============================================================ s04
        with self.seg("s04") as d:
            # "Seems."  -> zoom onto the small-1/L end; drop everything else
            hg_old = plot.extras.pop("half_guide")
            lit_old = plot.extras.pop("literature_line")
            plot, zoom = plot.zoomed(0.07, 0.01)
            half_lab, one_lab = plot.extras["series_labels"]
            half_lab.next_to(plot.half_pts[6], RIGHT, buff=0.18)      # L = 16 dot
            one_lab.next_to(plot.one_pts[6], RIGHT, buff=0.18)        # L = 16 square
            self.play(zoom, FadeOut(hg_old, lit_old, ctr, cap, hal, ringL, ringR),
                      run_time=rt(1.3))
            # "Every finite ring has a gap;"
            bub = objection_bubble("finite")
            self.cue(1.05)
            self.play(bubble_in(bub), run_time=rt(0.6))
            # "that is just linear algebra."
            triv = T(r"each finite $L$: $\gamma_L>0$ (trivial)", font_size=26, color=DIM)
            triv.move_to([6.4, 0.95, 0], aligned_edge=RIGHT)
            self.cue(2.9)
            self.play(bubble_indicate(bub), FadeIn(triv, shift=0.1 * LEFT), run_time=rt(0.9))
            self.play(bubble_check(bub), run_time=rt(0.6))
            # "The real question is whether there is one number,"
            self.cue(5.07)
            self.play(bubble_answer(bub, "the question is uniformity"), run_time=rt(0.6))
            F = M(r"\exists\,\gamma>0:\quad \gamma_L\ge\gamma\ \ \text{for every } L\ ?",
                  font_size=40)
            F.move_to([-6.35, 3.05, 0], aligned_edge=LEFT)
            # the objection has been answered: bubble, reply and the 'trivial' note
            # leave while the real question is written
            self.play(Write(F),
                      bubble_out(bub, rate_func=squish_rate_func(smooth, 0.4, 1.0)),
                      FadeOut(triv, rate_func=squish_rate_func(smooth, 0.4, 1.0)),
                      run_time=rt(1.6))
            # "bigger than zero,"
            floor = DashedLine(plot.c2p(0, 0.1), plot.c2p(0.07, 0.1), color=GAP,
                               stroke_width=3, dash_length=0.12)
            g_lab = M(r"\gamma", color=GAP, font_size=34).next_to(floor, LEFT, buff=0.15)
            self.cue(7.6)
            self.play(Create(floor), FadeIn(g_lab), run_time=rt(0.9))
            # "that the gap never drops below,"
            wi = what_if_curves(plot)
            self.cue(8.85)
            self.play(LaggedStart(*[Create(c) for c in wi], lag_ratio=0.3), run_time=rt(1.7))
            # "no matter how long the ring."
            qm = T("?", font_size=120, color=DEFECT).move_to(plot.c2p(0.022, 0.66))
            self.cue(10.7)
            self.play(GrowFromCenter(qm), run_time=rt(0.6))

        # ============================================================ s05
        with self.seg("s05") as d:
            # "And finite data can fool you."  The hypotheticals go first; the finite
            # data pulse once, then the whole plot clears for the 1984 story.
            self.play(FadeOut(F, qm, floor, g_lab, wi), run_time=rt(0.6))
            x_max = plot.params["x_range"][1]
            shown = [p for pts, data in ((plot.half_pts, plot.half_data),
                                         (plot.one_pts, plot.one_data))
                     for p, (L, _) in zip(pts, data) if 1 / L <= x_max + 1e-9]
            self.cue(0.7)
            self.play(LaggedStart(*[Indicate(p, color=FG, scale_factor=1.6) for p in shown],
                                  lag_ratio=0.12), run_time=rt(1.0))
            self.play(FadeOut(plot.with_extras(), shift=0.3 * LEFT), run_time=rt(0.7))
            # "In 1984, a published comment"
            cite_t = T(r"Comment, Phys.\ Rev.\ B \textbf{29}, 5216 (1984)", font_size=26,
                       color=DIM)
            cite_b = RoundedRectangle(width=cite_t.width + 0.5, height=cite_t.height + 0.4,
                                      corner_radius=0.12, stroke_color=DIM, stroke_width=1.5,
                                      fill_color=BG, fill_opacity=0.9)
            cite = VGroup(cite_b, cite_t.move_to(cite_b)).move_to([0, 2.75, 0])
            self.cue(2.5)
            self.play(FadeIn(cite, shift=0.3 * DOWN), run_time=rt(0.7))
            # "applied the same finite-size scaling"
            ax, xl, yl = small_gap_axes()
            half_d, one_d = load_gaps()
            half_d = [(L, g) for L, g in half_d if L <= 10]
            one_d = [(L, g) for L, g in one_d if L <= 10]
            hp, hl = series(ax, half_d, spinhalf_marker, HALF)
            op, ol = series(ax, one_d, spin1_marker, INTEGER)
            lab1 = T(r"spin $1$", font_size=28, color=INTEGER).next_to(
                ax.c2p(10, one_d[-1][1]), UR, buff=0.12)
            labh = T(r"spin $\tfrac12$", font_size=28, color=HALF).next_to(
                ax.c2p(10, half_d[-1][1]), DR, buff=0.12)
            self.cue(3.9)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=rt(1.5))
            # "that had suggested a spin one gap"
            self.cue(7.4)
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in op], lag_ratio=0.25),
                      Create(ol), FadeIn(lab1), run_time=rt(1.4))
            # "to spin one-half chains,"
            self.cue(9.2)
            self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in hp], lag_ratio=0.25),
                      Create(hl), FadeIn(labh), run_time=rt(1.3))
            # "known to be gapless, and found strikingly similar results."
            hard = caption("small rings: hard to tell apart").set_x(ax.c2p(7, 0)[0])
            self.cue(12.3)
            self.play(LaggedStart(*[Indicate(m, color=FG, scale_factor=1.6)
                                    for pair in zip(op, hp) for m in pair], lag_ratio=0.08),
                      FadeIn(hard, shift=0.1 * UP), run_time=rt(1.2))

        # ============================================================ s06
        with self.seg("s06", breath=2.0) as d:
            # "So here is the puzzle:"
            self.play(FadeOut(*self.mobjects), run_time=rt(0.8))
            q = VGroup(T(r"How can a \emph{finite} computation", font_size=44),
                       T(r"say something certain", font_size=44),
                       T(r"about \emph{every} length $L$?", font_size=44)
                       ).arrange(DOWN, buff=0.3).move_to([0, 1.35, 0])
            # "how can a finite computation" (2.03-3.65)
            self.cue(1.6)
            self.play(Write(q[0]), run_time=rt(1.4))
            # "tell you something certain" (3.87-5.11)
            self.cue(3.85)
            self.play(Write(q[1]), run_time=rt(0.9))
            # "about every length at once?" (5.23-6.25)
            radii, ns = [0.2, 0.3, 0.45, 0.7, 1.0], [4, 6, 8, 10, 12]
            rings = VGroup(*[mini_ring(n, r) for n, r in zip(ns, radii)])
            rings.arrange(RIGHT, buff=0.4)
            dots = M(r"\cdots\ L\to\infty", font_size=40).next_to(rings, RIGHT, buff=0.4)
            row = VGroup(rings, dots).move_to([0, -2.05, 0])
            self.cue(5.0)
            self.play(Write(q[2]),
                      LaggedStart(*[FadeIn(r, scale=0.6) for r in rings], FadeIn(dots),
                                  lag_ratio=0.25), run_time=rt(0.9))
            # the rings march right and off-screen; the question slides left and the
            # six objections line up down the right margin (the lower ones only once
            # the rings have left), then everything hangs through the long breath
            col = objection_column()
            t_march, march = 5.9, 1.5
            t_col, col_rt = 6.3, 1.6
            span = max(march, t_col + col_rt - t_march)

            def wnd(a, b):
                return (a - t_march) / span, min(1.0, (b - t_march) / span)
            self.cue(t_march)
            self.play(row.animate(rate_func=squish_rate_func(smooth, *wnd(t_march, t_march + march)))
                      .shift(RIGHT * 12.5),
                      q.animate(rate_func=squish_rate_func(smooth, *wnd(t_col, t_col + 0.9)))
                      .move_to([-2.35, 1.35, 0]),
                      objection_column_in(col, lag_ratio=0.24,
                                          rate_func=squish_rate_func(linear, *wnd(t_col, t_col + col_rt))),
                      run_time=rt(span))
            self.remove(row)

        # ============================================================ s07
        with self.seg("s07") as d:
            card = align_status_rows(StatusCard())
            # "On October 6, 2026," -- the column hangs a moment longer, then folds away
            self.cue(1.3)
            self.play(objection_collapse(col), FadeOut(q), run_time=rt(1.0))
            # "OpenAI released" (2.44): date and author line
            self.play(card.anim_meta(), run_time=rt(0.7))
            # "two manuscripts,"
            self.cue(3.2)
            self.play(card.anim_titles(), run_time=rt(1.3))
            # "The first claims exactly that:"
            self.cue(7.3)
            self.play(card.titles[1].animate.set_opacity(0.35), run_time=rt(0.6))
            # "on even rings, the spin one gap never closes;"
            self.cue(9.2)
            self.play(card.anim_tag(0), run_time=rt(0.7))
            # "the second, a matching claim for open chains."
            self.cue(12.2)
            self.play(card.titles[1].animate.set_opacity(1),
                      card.titles[0].animate.set_opacity(0.35),
                      card.title_tags[0].animate.set_opacity(0.35), run_time=rt(0.6))
            self.cue(13.0)
            self.play(card.anim_tag(1), run_time=rt(0.7))
            # "They are preprints, not yet independently refereed,"
            self.cue(15.45)
            self.play(card.titles[0].animate.set_opacity(1),
                      card.title_tags[0].animate.set_opacity(1),
                      card.anim_line(0), run_time=rt(0.9))
            # "but the argument is short,"
            self.cue(18.35)
            self.play(card.anim_line(1), run_time=rt(0.8))
            # "and its computer checks re-run on a laptop."
            self.cue(19.8)
            self.play(card.anim_line(2), run_time=rt(0.9))

        # ============================================================ s08
        with self.seg("s08") as d:
            # "And its central idea uses no field theory at all:"
            words = VGroup(T("field theory", font_size=40, color=DIM),
                           T(r"$\theta$-term", font_size=40, color=DIM),
                           T("RG", font_size=40, color=DIM)).arrange(RIGHT, buff=1.0)
            words.move_to([0, 0.3, 0])
            strikes = VGroup(*[Line(w.get_left() + LEFT * 0.12, w.get_right() + RIGHT * 0.12,
                                    color=SX, stroke_width=4) for w in words])
            self.play(FadeOut(card), run_time=rt(0.5))
            self.play(FadeIn(words, lag_ratio=0.2), run_time=rt(0.6))
            self.cue(1.5)
            for s in strikes:
                self.play(Create(s), run_time=rt(0.3))
            self.play(FadeOut(words, strikes, shift=0.2 * DOWN), run_time=rt(0.5))

            # three panels: torus + knives | squared bars | staircase
            tor = Torus(3.4, 2.0, nx=8, ny=5, label_size=32)
            tor.shift(np.array([-4.25, 0.1, 0]) - tor.rect.get_center())
            hk = time_knife(tor, at=0.1)
            vk = space_knife(tor, bond=0)
            wb = WeightBars([0.6, 0.15, 0.1, 0.08, 0.07], width=3.0, height=2.2, color=FG)
            wb.shift(np.array([0.0, -0.95, 0]) - wb.base.get_center())
            st = Staircase("bare", x_length=3.0, y_length=2.4)
            st.shift(np.array([4.15, 0.05, 0]) - st.get_center())
            tr = st.tromino(0.5, 0.5)
            y_lab = -2.45
            labs = VGroup(T(r"one $Z$, two readings", font_size=28, color=DIM),
                          T(r"squaring probabilities", font_size=28, color=DIM),
                          T(r"a staircase to $L=\infty$", font_size=28, color=DIM))
            for lab, x in zip(labs, (tor.rect.get_center()[0], 0.0,
                                     st.ax.c2p(3, 0)[0])):
                lab.move_to([x, y_lab, 0])

            # "one partition function read in two directions,"
            self.cue(3.7)
            self.play(GrowFromCenter(tor), FadeIn(labs[0]), run_time=rt(0.6))
            self.play(hk.cut_in(), run_time=rt(0.35))
            self.play(hk.sweep(0.9), run_time=rt(0.6))
            self.play(vk.cut_in(), run_time=rt(0.35))
            self.play(vk.sweep(0.94), run_time=rt(0.6))
            # "a trick of squaring probabilities,"
            self.cue(6.75)
            self.play(FadeIn(wb, shift=0.2 * UP), FadeIn(labs[1]), run_time=rt(0.45))
            s1, s2 = wb.square()
            self.play(s1, run_time=rt(0.5))
            self.play(s2, run_time=rt(0.5))
            # "and a staircase that climbs to infinite length."
            self.cue(8.88)
            self.play(FadeIn(st), FadeIn(tr), FadeIn(labs[2]), run_time=rt(0.4))
            self.play(tr.climb(4, exit=True, trail=True), run_time=rt(1.8))

            # title card
            self.play(FadeOut(*self.mobjects), run_time=rt(0.6))
            tc = title_card("The Haldane gap", sub="a claimed proof, explained")
            self.play(FadeIn(tc[0], shift=0.15 * UP), run_time=rt(0.8))
            self.play(FadeIn(tc[1]), run_time=rt(0.6))
            self.wait(rt(1.4))

        self.play(FadeOut(*self.mobjects), run_time=0.8)
        self.wait(0.2)
