"""ch04: One torus, two knives.

Z(L, beta) read along time (Gibbs weights) and along space (a self-adjoint
spatial transfer operator on bond histories); why the theorem is about even rings.

Sync: every voice block calls self.begin(seg, d) and then self.at(t) with t the
phrase onsets (seconds) measured from the ch04 clips (silence detection).  They are
rescaled by d / D_REF[seg], so a re-generated clip keeps the cues proportional.
"""
import json

from motifs import *  # noqa: F401,F403

# clip lengths when the cue times below were measured
D_REF = {"s01": 15.875, "s02": 15.5, "s03": 19.35, "s04": 19.025, "s11": 9.825, "s12": 12.375, "s13": 8.25, "s14": 22.425,
         "s15": 14.65, "s16": 14.65}

XYZ = {"x": SX, "y": SY, "z": SZ}
NARR = {c["id"]: {g["id"]: g["text"] for g in c["segments"]}
        for c in json.loads((ROOT / "script" / "narration.json").read_text())["chapters"]}

# schematic spatial eigenvalues (NOT data: no eigenvalue of X is known numerically)
LAMS = np.array([0.99, -0.88, 0.57, -0.52, 0.33, -0.26, 0.14])

# schematic Gibbs weights: levels E = 0, 0.6 (x3), 1.1, 1.3 (x2) at beta = 2.5,
# one bar per eigenstate (multiplicity counted)
LEVELS = [0.0, 0.6, 0.6, 0.6, 1.1, 1.3, 1.3]
GIBBS = np.exp(-2.5 * np.array(LEVELS))
GIBBS = GIBBS / GIBBS.sum()

# hand-placed bond histories for the 7-site picture (times in [0, beta = 3])
EVENTS = {0: [(0.45, "x"), (1.60, "z"), (2.55, "y")],
          1: [(0.95, "y"), (2.10, "x")],
          2: [(0.30, "z"), (1.25, "x"), (2.35, "y")],
          3: [(0.70, "y"), (1.85, "z"), (2.75, "x")],
          4: [(0.20, "x"), (1.45, "y"), (2.30, "z")],
          5: [(1.00, "z"), (2.00, "x")]}
EXTRA_BEADS = [[(0.25, "y"), (0.70, "z")], [(0.50, "x")],
               [(0.20, "z"), (0.55, "y"), (0.85, "x")], [(0.40, "x"), (0.75, "y")]]

TOR_C = np.array([0.0, -0.4, 0.0])      # s01 torus centre
TOR_L = np.array([-3.3, -0.4, 0.0])     # torus centre while the right panel is in use
DIAG_C = np.array([-2.2, -0.55, 0.0])   # 7-site bond-history picture
RING_C = np.array([-3.0, -0.6, 0.0])    # chain of beads


# ------------------------------------------------------------------ helpers
def MT(*parts, **kw):
    """Multi-part MathTex in the film's template (M() takes one string)."""
    kw.setdefault("color", FG)
    return MathTex(*parts, tex_template=TEX_TEMPLATE, **kw)


def TX(*parts, **kw):
    kw.setdefault("color", FG)
    return Tex(*parts, tex_template=TEX_TEMPLATE, **kw)


def place_torus(tor, centre):
    return tor.shift(np.array(centre) - tor.rect.get_center())


def history_capsule(events, height=3.0, width=0.36, tick_w=0.24, color=SPACE,
                    tick_stroke=5, frac=False, t_max=3.0, fill=0.0):
    """A bond history: SPACE-outlined capsule with x/y/z ticks at its event times.
    events: list of (time, label); times in [0, t_max] (or fractions if frac)."""
    box = RoundedRectangle(width=width, height=height, corner_radius=min(width / 2, 0.14),
                           stroke_color=color, stroke_width=2.5, fill_color=BG,
                           fill_opacity=fill)
    ticks = VGroup()
    for t, lab in events:
        f = t if frac else t / t_max
        y = -height / 2 + f * height
        ticks.add(Line([-tick_w / 2, y, 0], [tick_w / 2, y, 0], color=XYZ[lab],
                       stroke_width=tick_stroke))
    g = VGroup(box, ticks)
    g.box, g.ticks = box, ticks
    return g


class EigLine(VGroup):
    """Schematic eigenvalue number line from -1.1 to 1.1 (ticks at -1, 0, 1)."""

    def __init__(self, lams, width=4.2, dot_r=0.075, font_size=26, color=SPACE, xr=1.1):
        super().__init__()
        self.xr = xr
        self.line = Line(LEFT * width / 2, RIGHT * width / 2, color=DIM, stroke_width=2)
        self.ticks, self.labels = VGroup(), VGroup()
        for v, s in ((-1, "-1"), (0, "0"), (1, "1")):
            p = RIGHT * v * width / (2 * xr)
            self.ticks.add(Line(p + DOWN * 0.09, p + UP * 0.09, color=DIM, stroke_width=2))
            self.labels.add(M(s, font_size=font_size, color=DIM).next_to(p + DOWN * 0.09, DOWN,
                                                                          buff=0.1))
        self.dots = VGroup(*[Dot(RIGHT * v * width / (2 * xr), radius=dot_r, color=color)
                             for v in lams])
        self.add(self.line, self.ticks, self.labels, self.dots)

    def n2p(self, v):
        a, b = self.line.get_start(), self.line.get_end()
        return a + (v + self.xr) / (2 * self.xr) * (b - a)

    def build(self, **kw):
        return AnimationGroup(Create(self.line), FadeIn(self.ticks), FadeIn(self.labels),
                              LaggedStart(*[GrowFromCenter(d) for d in self.dots],
                                          lag_ratio=0.12), lag_ratio=0.25, **kw)


def level_ticks(levels, tick_w=0.4, gap=0.1, yscale=1.8, color=TIME, stroke=4):
    """Level diagram with degenerate levels drawn as side-by-side ticks (one tick per
    eigenstate).  Ticks are returned in the order of `levels`; y = E * yscale."""
    out = VGroup()
    seen = {}
    for E in levels:
        seen[E] = seen.get(E, 0) + 1
    placed = {}
    for E in levels:
        cnt = seen[E]
        i = placed.get(E, 0)
        placed[E] = i + 1
        total = cnt * tick_w + (cnt - 1) * gap
        x = -total / 2 + tick_w / 2 + i * (tick_w + gap)
        out.add(Line([x - tick_w / 2, E * yscale, 0], [x + tick_w / 2, E * yscale, 0],
                     color=color, stroke_width=stroke))
    return out


def seam_glyph(color=FG, radius=0.17):
    """The SEAM (ch04 s10, ch08 s03): a small circular arrow labelled P."""
    arc = Arc(radius=radius, start_angle=-0.35 * PI, angle=1.55 * PI, color=color,
              stroke_width=3)
    arc.add_tip(tip_length=0.11, tip_width=0.11)
    lab = M("P", font_size=30, color=color).next_to(arc, RIGHT, buff=0.08)
    return VGroup(arc, lab)


def pause_glyph(h=0.5, w=0.13, gap=0.15, color=DIM):
    bars = VGroup(*[RoundedRectangle(width=w, height=h, corner_radius=0.04, stroke_width=0,
                                     fill_color=color, fill_opacity=1) for _ in range(2)])
    bars.arrange(RIGHT, buff=gap)
    return bars


def fg_ring(n, radius=0.75, length=0.38):
    r = spin_ring(n, radius=radius, color=FG, length=length)
    r[0].set_stroke(DIM, width=2)
    return r


# ------------------------------------------------------------------ the chapter
class Ch04(NarratedScene):
    CHAPTER = "ch04"

    # cue helpers -------------------------------------------------------
    def begin(self, seg, d):
        self._t0 = self.renderer.time
        self._k = d / D_REF[seg] if seg in D_REF else 1.0
        self._seg = seg
        self._d = d

    def at_words(self, phrase):
        """Wait until the narration reaches `phrase` (word-proportional estimate,
        plus Kokoro's ~0.35 s lead-in).  Used by segments without measured cues."""
        text = NARR["ch04"][self._seg]
        i = text.find(phrase)
        assert i >= 0, (self._seg, phrase)
        frac = len(text[:i].split()) / max(1, len(text.split()))
        self.at(0.35 + frac * (self._d - 0.35))

    def at(self, t):
        dt = self._t0 + t * self._k - self.renderer.time
        if dt > 0.05:
            self.wait(dt)
        elif dt < -0.15:
            print(f"[cue] {self.CHAPTER} {self._seg} t={t}: late by {-dt:.2f}s")

    def left(self, t, floor=0.4):
        """Seconds from now until cue t (at least `floor`)."""
        return max(floor, self._t0 + t * self._k - self.renderer.time)

    # -------------------------------------------------------------------
    def construct(self):
        self.s01()
        self.s02()
        self.s03()
        self.s04()
        for k in range(5, 17):
            getattr(self, "s%02d" % k)()

    # ================================================================ s01
    def s01(self):
        with self.voice("s01") as d:
            self.begin("s01", d)
            eq = MT(r"Z(", "L", ",", r"\beta", r")=\operatorname{Tr}\,e^{-", r"\beta", "H_{", "L",
                    "}}", font_size=52)
            eq[1].set_color(SPACE)
            eq[3].set_color(TIME)
            eq[5].set_color(TIME)
            eq[7].set_color(SPACE)
            eq.move_to([2.7, 0.3, 0])
            zpart = VGroup(eq[0], eq[1], eq[2], eq[3], eq[4][0])
            rest = VGroup(eq[4][1:], eq[5], eq[6], eq[7], eq[8])
            self.at(0.32)
            self.play(Write(zpart), run_time=1.3)
            self.at(3.52)
            self.play(Write(rest), run_time=1.4)

            ring = fg_ring(10, radius=1.4, length=0.42).move_to([-3.6, -0.1, 0])
            circ, sites, arrows = ring
            lab = VGroup(M("L", color=SPACE, font_size=34), T("spins", font_size=30)).arrange(
                RIGHT, buff=0.12).next_to(ring, DOWN, buff=0.35)
            self.at(5.4)
            self.play(Create(circ), FadeIn(sites),
                      LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.08),
                      FadeIn(lab, shift=0.1 * UP), run_time=1.5)

            # ---- the ring stacked in imaginary time -> cylinder -> torus
            tor = place_torus(Torus(5, 3, nx=10, ny=6), TOR_C)
            W, H = 5.0, 3.0
            y0 = TOR_C[1] - H / 2
            ell_w, ell_h = 4.0, 0.62

            def ell_pts(y):
                return [np.array([TOR_C[0] + ell_w / 2 * np.cos(TAU * j / 10 + PI / 2),
                                  y + ell_h / 2 * np.sin(TAU * j / 10 + PI / 2), 0])
                        for j in range(10)]

            ell0 = Ellipse(width=ell_w, height=ell_h, color=DIM, stroke_width=2).move_to(
                [TOR_C[0], y0, 0])
            self.at(7.45)
            self.play(eq.animate.scale(0.75).move_to([0, 3.15, 0]), FadeOut(arrows), FadeOut(lab),
                      Transform(circ, ell0),
                      *[s.animate.move_to(p) for s, p in zip(sites, ell_pts(y0))],
                      run_time=0.75)
            # unroll geometry: the ellipse is a circle of radius R0 seen at a slant
            # (depth Z squashed by ell_h / ell_w).  The ring is cut at the back (site 0)
            # and opened about its front point: an arc of half-angle th = pi (1 - a)
            # whose half-width grows from R0 to W/2, so it never crosses itself and
            # site j slides along the arc to world line j.
            R0, sq = ell_w / 2, ell_h / ell_w

            def arc_pt(u, a, y):
                th = PI * (1 - a)
                hw = (1 - a) * R0 + a * W / 2
                if th < 1e-4:
                    X, Z = u * hw, -R0
                else:
                    rho = hw if th >= PI / 2 else hw / np.sin(th)
                    X = rho * np.sin(u * th)
                    Z = -R0 + rho * (1 - np.cos(u * th))
                return np.array([TOR_C[0] + X, y + sq * Z + ell_h / 2 * a, 0])

            us = np.linspace(-1, 1, 61)
            curve0 = VMobject().set_points_smoothly([arc_pt(u, 0, y0) for u in us])
            curve0.set_stroke(DIM, width=2)
            self.remove(circ)
            self.add(curve0)
            rows = [VGroup(curve0, sites)]
            for k in range(1, 7):
                c = VGroup(curve0.copy().set_stroke(opacity=0.75), sites.copy().set_opacity(0.75))
                rows.append(c)
            self.add(*rows[1:])
            sides = VGroup(Line([TOR_C[0] - ell_w / 2, y0, 0], [TOR_C[0] - ell_w / 2, y0 + H, 0]),
                           Line([TOR_C[0] + ell_w / 2, y0, 0], [TOR_C[0] + ell_w / 2, y0 + H, 0])
                           ).set_stroke(DIM, width=2)
            self.play(LaggedStart(*[ApplyMethod(rows[k].shift, UP * H * k / 6)
                                    for k in range(1, 7)], lag_ratio=0.12),
                      Create(sides), run_time=0.75)

            # unroll: every ring opens into one row of the rectangle; site j -> world line j
            def unroll(row, y):
                def upd(m, a):
                    m[0].set_points_smoothly([arc_pt(u, a, y) for u in us])
                    for j, s in enumerate(m[1]):
                        s.move_to(arc_pt((j - 5) / 5, a, y))
                return UpdateFromAlphaFunc(row, upd)

            self.play(*[unroll(row, y0 + H * k / 6) for k, row in enumerate(rows)],
                      sides[0].animate.set_x(TOR_C[0] - W / 2),
                      sides[1].animate.set_x(TOR_C[0] + W / 2),
                      run_time=1.1, rate_func=smooth)
            self.play(FadeIn(tor), FadeOut(VGroup(*rows), sides), run_time=0.4)

            pl = tor.periodicity_labels()
            self.at(10.38)
            self.play(FadeIn(pl[1], shift=0.2 * LEFT),
                      *[Indicate(c, color=SPACE, scale_factor=1.8) for c in tor.chev_space],
                      run_time=1.3)
            self.at(13.29)
            self.play(FadeIn(pl[0], shift=0.2 * DOWN),
                      *[Indicate(c, color=TIME, scale_factor=1.8) for c in tor.chev_time],
                      run_time=1.3)
        self.tor, self.eq, self.pl = tor, eq, pl

    # ================================================================ s02
    def s02(self):
        tor, eq = self.tor, self.eq
        with self.voice("s02") as d:
            self.begin("s02", d)
            self.play(FadeOut(self.pl), tor.animate.shift(TOR_L - TOR_C),
                      eq.animate.move_to([TOR_L[0], 3.15, 0]), run_time=0.8)
            hk = time_knife(tor, at=0.25)
            self.play(hk.cut_in(), run_time=1.0)
            self.play(hk.glow_on(), run_time=0.4)

            # the cut is the whole ring at one instant
            self.at(2.44)
            cut = hk.cut_copy()
            ring_c = np.array([2.0, tor.y_at(0.25) + 0.15, 0])
            sr = fg_ring(10, radius=0.85, length=0.32).move_to(ring_c)
            sr[0].set_stroke(TIME, width=3)
            self.add(cut)
            self.play(ReplacementTransform(cut, sr[0]), run_time=1.0)
            self.play(FadeIn(sr[1]), LaggedStart(*[GrowArrow(a) for a in sr[2]], lag_ratio=0.06),
                      run_time=0.7)

            self.at(5.2)
            self.play(hk.steps([0.417, 0.583, 0.75, 0.917], label_tex=r"e^{-\delta\tau H}",
                               label_size=34, run_time=self.left(8.1, 2.0)))

            # Gibbs reading: levels and weights (schematic)
            therm = MT(r"Z=\sum_k e^{-\beta E_k}", r",\qquad w_k=\frac{e^{-\beta E_k}}{Z}",
                       color=TIME, font_size=36)
            therm.move_to([1.0, 2.32, 0], aligned_edge=LEFT)
            base_y = -2.0
            lv = level_ticks(LEVELS, yscale=1.8).move_to([1.75, 0, 0])
            lv.shift(UP * (base_y - lv[0].get_y()))
            e_ax = Arrow([0.55, base_y - 0.1, 0], [0.55, base_y + 2.6, 0], buff=0, color=DIM,
                         stroke_width=2, max_tip_length_to_length_ratio=0.08)
            e_lab = M("E", color=DIM, font_size=30).next_to(e_ax.get_end(), LEFT, buff=0.12)
            wb = WeightBars(GIBBS, width=3.0, height=2.6, color=TIME, highlight_color=TIME)
            wb.shift(np.array([4.75, base_y, 0]) - wb.base.get_center())
            self.at(8.3)
            self.play(FadeOut(sr), Write(therm[0]), run_time=1.0)
            self.play(Create(e_ax), FadeIn(e_lab),
                      LaggedStart(*[Create(t) for t in lv], lag_ratio=0.12), run_time=1.3)
            self.at(12.73)
            self.play(Create(wb.base),
                      LaggedStart(*[GrowFromEdge(b, DOWN) for b in wb.bars], lag_ratio=0.12),
                      run_time=1.0)
            gibbs = T("Gibbs distribution", font_size=28, color=TIME).next_to(
                wb.bars, UP, buff=0.3)
            sch = inline_tag(TAG_SCHEMATIC, VGroup(lv, wb), DOWN, buff=0.3)
            self.at(13.84)
            self.play(Write(therm[1]), FadeIn(gibbs, shift=0.1 * UP), FadeIn(sch), run_time=1.0)
        self.hk, self.therm = hk, therm
        self.s02_extra = VGroup(lv, e_ax, e_lab, wb, gibbs, sch)

    # ================================================================ s03
    def s03(self):
        tor, hk = self.tor, self.hk
        with self.voice("s03") as d:
            self.begin("s03", d)
            self.play(hk.glow_off(), run_time=0.2)
            self.play(FadeOut(hk), FadeOut(self.s02_extra), run_time=0.5)
            vk = space_knife(tor, bond=1)
            self.play(vk.cut_in(), run_time=0.8)

            self.at(1.5)
            self.play(*[l.animate(rate_func=there_and_back).set_stroke(FG, width=4)
                        for l in (tor.grid[0], tor.grid[1])], run_time=1.2)

            # lift out one bond's history
            self.at(2.86)
            self.play(vk.glow_on(), run_time=0.4)
            cut = vk.cut_copy()
            self.add(cut)
            cap = history_capsule([(0.12, "x"), (0.31, "z"), (0.52, "y"), (0.70, "x"), (0.88, "z")],
                                  height=3.0, frac=True).move_to([0.35, TOR_L[1], 0])
            self.play(cut.animate.move_to([0.35, TOR_L[1], 0]), run_time=0.9)
            self.play(ReplacementTransform(cut, cap.box),
                      LaggedStart(*[GrowFromCenter(t) for t in cap.ticks], lag_ratio=0.15),
                      run_time=0.9)
            cap_lab = T("a bond's history", font_size=28, color=SPACE).next_to(cap, DOWN, buff=0.3)
            self.play(FadeIn(cap_lab, shift=0.1 * UP), run_time=0.5)

            self.at(6.58)
            self.play(vk.steps(list(range(2, 10)), label_tex="X", run_time=self.left(10.48, 3.0)))
            stag = tag("in the spirit of Suzuki's quantum transfer matrix", buff=0.42)
            self.play(vk.steps([10, 11], label_tex="X", run_time=1.0), tag_in(stag, run_time=0.8))

            spat = MT(r"Z=\operatorname{Tr}\,X_\beta^{\,L}", r"=\sum_i\lambda_i(\beta)^{L}",
                      color=SPACE, font_size=36)
            spat.move_to([1.0, 1.05, 0], aligned_edge=LEFT)
            el = EigLine(LAMS, width=4.2).move_to([3.95, -0.55, 0])
            sch = inline_tag(TAG_SCHEMATIC, el, DOWN, buff=0.25)
            self.at(13.64)
            # the lifted-out history has done its job: clear it (and the s01 title)
            self.play(Write(spat[0]), FadeOut(VGroup(cap, cap_lab), shift=0.1 * DOWN),
                      FadeOut(self.eq), run_time=1.1)
            self.at(16.37)
            self.play(Write(spat[1]), run_time=1.0)
            self.play(el.build(), FadeIn(sch), run_time=1.2)
        self.s03_all = VGroup(vk, stag, spat, el, sch, self.therm)

    # ================================================================ s04
    def s04(self):
        tor = self.tor
        with self.voice("s04") as d:
            self.begin("s04", d)
            self.play(FadeOut(self.s03_all), run_time=0.35)

            body = VGroup(tor.rect, tor.grid, tor.chev_time, tor.chev_space)
            c = tor.rect.get_center()
            L0, b0 = tor.L_label.get_center(), tor.beta_label.get_center()
            L1 = c + LEFT * (1.5 + 0.35)
            b1 = c + DOWN * (2.5 + 0.35)
            cap1 = T("continuum: rotate the torus", font_size=32).move_to([3.4, 0.55, 0])
            cap2 = TX(r"lattice: build ", r"$X$", font_size=32).move_to([3.4, -0.35, 0])
            cap2[1].set_color(SPACE)
            cap2.align_to(cap1, LEFT)
            labs = VGroup(tor.L_label, tor.beta_label)
            self.at(0.34)
            # labels step aside while the body turns, then reappear upright (L now vertical)
            self.play(Rotate(body, -PI / 2, about_point=c, run_time=1.1),
                      FadeOut(labs, run_time=0.35), FadeIn(cap1, shift=0.1 * UP, run_time=1.1))
            tor.L_label.move_to(L1)
            tor.beta_label.move_to(b1)
            self.play(FadeIn(labs), run_time=0.35)
            self.wait(0.3)
            self.play(Rotate(body, PI / 2, about_point=c, run_time=1.1),
                      FadeOut(labs, run_time=0.35))
            tor.L_label.move_to(L0)
            tor.beta_label.move_to(b0)
            self.play(FadeIn(labs), run_time=0.35)
            self.at(3.96)
            self.play(FadeIn(cap2, shift=0.1 * UP),
                      tor.grid.animate(rate_func=there_and_back).set_stroke(DIM, width=2.5),
                      run_time=1.2)

            # the Cartesian spin-one matrices
            gdef = MT(r"G_\alpha=iS^\alpha", r",\qquad (G_\alpha)_{jk}=\varepsilon_{\alpha jk}",
                      font_size=36).move_to([1.0, 2.5, 0], aligned_edge=LEFT)
            self.at(6.58)
            self.play(FadeOut(cap1), FadeOut(cap2), Write(gdef[0]), run_time=1.0)
            self.at(9.28)
            self.play(Write(gdef[1]), run_time=1.0)

            ent = [["0", "1", "0"], ["-1", "0", "0"], ["0", "0", "0"]]
            mat = Matrix(ent, left_bracket="(", right_bracket=")", h_buff=0.75, v_buff=0.62,
                         element_to_mobject=lambda s: MathTex(s, tex_template=TEX_TEMPLATE,
                                                              font_size=36))
            for e in mat.get_entries():
                e.set_color(FG if e.get_tex_string() == "0" else SZ)
            mat.get_brackets().set_color(FG)
            glab = MT("G_{", "z", "}=", font_size=36)
            glab[1].set_color(SZ)
            gz = VGroup(glab, mat).arrange(RIGHT, buff=0.15).move_to([3.4, 0.8, 0])
            gtag = inline_tag("real, antisymmetric, norm 1", gz, DOWN, buff=0.3)
            self.at(10.94)
            self.play(FadeIn(gz, shift=0.1 * UP), run_time=0.8)
            self.play(FadeIn(gtag), run_time=0.6)
            self.at(13.47)
            self.play(Indicate(gdef[0][0:2], color=FG, scale_factor=1.25), run_time=0.8)

            # the bond, one coloured term per label (x red, y green, z blue)
            b_lhs = MT(r"\mathbf S_j\cdot\mathbf S_{j+1}", font_size=36)
            b_rhs = MT(r"=-\big(", r"G_x\otimes G_x", "+", r"G_y\otimes G_y", "+",
                       r"G_z\otimes G_z", r"\big)", font_size=36)
            b_rhs[1].set_color(SX)
            b_rhs[3].set_color(SY)
            b_rhs[5].set_color(SZ)
            b_rhs.next_to(b_lhs, DOWN, buff=0.22).align_to(b_lhs, LEFT).shift(RIGHT * 0.45)
            bond = VGroup(b_lhs, b_rhs)
            bond.move_to([3.15, -1.95, 0])
            self.at(14.61)
            self.play(Succession(Write(b_lhs, run_time=0.6), Write(b_rhs, run_time=1.2)))
        self.s04_all = VGroup(gdef, gz, gtag)
        self.bond = bond

    # ================================================================ s05
    def rungs_for(self, sites, events):
        """Event rungs between neighbouring world lines for {bond k: [(t, label)]}, t in [0, 3]."""
        ybot = sites[0].get_start()[1]
        ytop = sites[0].get_end()[1]
        g = VGroup()
        for k in sorted(events):
            x0, x1 = sites[k].get_x(), sites[k + 1].get_x()
            bg = VGroup()
            for t, lab in events[k]:
                y = ybot + t / 3.0 * (ytop - ybot)
                bg.add(Line([x0, y, 0], [x1, y, 0], color=XYZ[lab], stroke_width=5))
            g.add(bg)
        return g

    def s05(self):
        """What an event is: one bond term, one moment, one label, G_alpha on both ends."""
        tor = self.tor
        with self.voice("s05") as d:
            self.begin("s05", d)
            hd = bond_history_diagram(n_sites=7, beta=3.0, spacing=0.9,
                                      events=[[t for t, _ in EVENTS[k]] for k in range(6)])
            hd.shift(DIAG_C - hd.get_center())
            sites, ev = hd
            for k in range(6):
                for r, (_, lab) in zip(ev[k], EVENTS[k]):
                    r.set_color(XYZ[lab])
            ybot = sites[0].get_start()[1]
            expf = MT(r"e^{-\beta H}=\exp\Big(\beta\sum_{\langle jk\rangle}\sum_\alpha "
                      r"G_\alpha^{(j)}G_\alpha^{(k)}\Big)", font_size=36).move_to([-1.3, 3.0, 0])
            tau_ax = Arrow([-5.45, ybot, 0], [-5.45, ybot + 3.35, 0], buff=0, color=TIME,
                           stroke_width=3, max_tip_length_to_length_ratio=0.07)
            tau_lab = M(r"\tau", color=TIME, font_size=34).next_to(tau_ax.get_end(), LEFT,
                                                                   buff=0.15)
            rest = [m for m in [tor.rect, tor.grid[0], tor.grid[8], *tor.grid[9:], tor.chev_time,
                                tor.chev_space, tor.L_label, tor.beta_label]]
            self.play(FadeOut(self.s04_all), FadeOut(self.bond, shift=0.3 * UP), run_time=0.4)
            self.play(Write(expf),
                      ReplacementTransform(VGroup(*tor.grid[1:8]), sites),
                      *[FadeOut(m) for m in rest], run_time=1.4)
            self.remove(tor)
            self.add(sites)
            self.at_words("Each term switches on")
            rungs = sorted([r for g in ev for r in g], key=lambda r: r.get_y())
            self.play(Create(tau_ax), FadeIn(tau_lab),
                      LaggedStart(*[GrowFromCenter(r) for r in rungs], lag_ratio=0.15),
                      run_time=2.4)
            self.add(ev)

            # one event: a bond, a moment, a label -- and G_alpha on BOTH ends
            e_star = ev[5][0]                      # bond (5,6), label z
            ys = e_star.get_y()
            self.at_words("Call each one an event")
            self.play(Indicate(e_star, color=SZ, scale_factor=1.4), run_time=0.8)
            self.at_words("a bond,")
            br = Brace(Line(sites[5].get_start(), sites[6].get_start()), DOWN, buff=0.12,
                       color=FG)
            br_lab = T("bond", font_size=28).next_to(br, DOWN, buff=0.1)
            self.play(GrowFromCenter(br), FadeIn(br_lab), run_time=0.6)
            self.at_words("a moment,")
            dl = DashedLine([sites[6].get_x() + 0.08, ys, 0], [sites[6].get_x() + 0.75, ys, 0],
                            color=DIM, stroke_width=2, dash_length=0.08)
            tl = M(r"\tau", color=TIME, font_size=34).next_to(dl, RIGHT, buff=0.12)
            self.play(Create(dl), FadeIn(tl), run_time=0.6)
            self.at_words("and a label")
            leg = VGroup()
            for s_ in "xyz":
                leg.add(VGroup(Line(LEFT * 0.2, RIGHT * 0.2, color=XYZ[s_], stroke_width=5),
                               M(s_, color=XYZ[s_], font_size=32)).arrange(DOWN, buff=0.12))
            leg.arrange(RIGHT, buff=0.35).move_to([4.3, 1.55, 0])
            leg_lab = T("label", font_size=28, color=DIM).next_to(leg, UP, buff=0.2)
            self.play(LaggedStart(*[FadeIn(g, shift=0.1 * UP) for g in leg], lag_ratio=0.25),
                      FadeIn(leg_lab), run_time=0.9)
            self.play(Indicate(leg[2], color=SZ, scale_factor=1.3), run_time=0.6)
            self.at_words("acts with that same")
            # one G_z on each end of the bond, right where it acts
            a1 = M("G_z", color=SZ, font_size=28).next_to([sites[5].get_x(), ys, 0], LEFT, buff=0.08)
            a2 = M("G_z", color=SZ, font_size=28).next_to([sites[6].get_x(), ys, 0], RIGHT, buff=0.08)
            acts = MT(r"G_z", r"\otimes", r"G_z", font_size=40)
            acts[0].set_color(SZ)
            acts[2].set_color(SZ)
            acts.move_to([4.3, -0.15, 0])
            note = T(r"the same $G_z$ on both ends", font_size=28, color=DIM).next_to(
                acts, DOWN, buff=0.3)
            self.play(FadeOut(VGroup(dl, tl)), FadeIn(a1, shift=0.1 * RIGHT),
                      FadeIn(a2, shift=0.1 * LEFT), Indicate(e_star, color=SZ), run_time=0.9)
            self.play(Write(acts), FadeIn(note), run_time=0.9)
        self.hd, self.expf, self.tau = hd, expf, VGroup(tau_ax, tau_lab)
        self.s05_extra = VGroup(br, br_lab, leg, leg_lab, acts, note, a1, a2)

    # ================================================================ s06
    def s06(self):
        """The picture is ONE term: placement is free, so nothing lines up."""
        sites, ev = self.hd
        with self.voice("s06") as d:
            self.begin("s06", d)
            self.play(FadeOut(self.s05_extra), run_time=0.4)
            tag1 = tag_box("one configuration = one term of the sum").to_corner(UR, buff=0.42)
            self.play(FadeIn(tag1, shift=0.1 * DOWN), Indicate(ev, scale_factor=1.04), run_time=0.9)
            self.at_words("any number of them")
            free = TX(r"any number", r" $\cdot$ any bond", r" $\cdot$ any moment",
                      r" $\cdot$ any label", font_size=30).move_to([0, -3.05, 0])
            self.play(LaggedStart(*[FadeIn(p, shift=0.1 * UP) for p in free], lag_ratio=0.5),
                      run_time=2.2)
            self.at_words("each with a positive coefficient")
            pos = T("all coefficients positive", font_size=28, color=GAP).next_to(
                self.expf, DOWN, buff=0.15)
            self.play(FadeIn(pos, shift=0.1 * UP), run_time=0.6)
            self.at_words("That is why nothing lines up")
            # sweep across the bonds: their events sit at unrelated heights
            self.play(LaggedStart(*[Indicate(g, scale_factor=1.08, color=FG) for g in ev],
                                  lag_ratio=0.25), run_time=1.6)
            # other terms of the sum (random placements), then back to the first one
            rng = np.random.default_rng(7)
            alt = []
            for _ in range(2):
                cfg = {}
                for k in range(6):
                    n = int(rng.integers(0, 5))
                    cfg[k] = sorted((float(rng.uniform(0.1, 2.9)), "xyz"[int(rng.integers(3))])
                                    for _ in range(n))
                alt.append(self.rungs_for(sites, cfg))
            counter = TX(r"term 1", font_size=28, color=DIM).next_to(tag1, DOWN, buff=0.25).align_to(tag1, RIGHT)
            self.add(counter)
            self.at_words("Here is another term")
            cur = ev
            for i, g in enumerate(alt):
                new_c = TX(r"term %d" % (i + 2), font_size=28, color=DIM).move_to(counter)
                self.play(FadeOut(cur, run_time=0.5), FadeIn(g, run_time=0.5),
                          Transform(counter, new_c, run_time=0.5))
                self.remove(cur)
                cur = g
                if i == 0:
                    self.at_words("and another")
            self.wait(0.8)
            back = TX(r"term 1", font_size=28, color=DIM).move_to(counter)
            self.play(FadeOut(cur), FadeIn(ev), Transform(counter, back), run_time=0.6)
        self.pos = pos
        self.s06_extra = VGroup(free, counter)
        self.tag_conf = tag1

    # ================================================================ s07
    def s07(self):
        """Free placement does not mean independence: the weight is computed site by site."""
        sites, ev = self.hd
        with self.voice("s07") as d:
            self.begin("s07", d)
            self.play(FadeOut(self.s06_extra), run_time=0.4)
            self.at_words("Each configuration carries a weight")
            wq = MT(r"\text{weight}(", r"\text{this term}", r")\;=\;?", font_size=34)
            wq.move_to([3.6, 1.6, 0])
            self.play(Write(wq), run_time=0.9)
            self.at_words("computed site by site")
            self.play(LaggedStart(*[Indicate(s_, color=FG, scale_factor=1.0) for s_ in sites],
                                  lag_ratio=0.1),
                      *[s_.animate.set_stroke(width=3) for s_ in sites], run_time=1.2)
            self.at_words("Watch one site")
            site = sites[3]
            dimmed = VGroup(*[r for k in (0, 1, 4, 5) for r in ev[k]])
            self.play(dimmed.animate.set_stroke(opacity=0.2),
                      *[s_.animate.set_stroke(opacity=0.35) for i, s_ in enumerate(sites) if i != 3],
                      site.animate.set_stroke(FG, width=5), run_time=0.9)
            self.at_words("every event on its left bond")
            self.play(*[r.animate.set_stroke(width=9) for r in ev[2]], run_time=0.6)
            self.play(Indicate(ev[2], scale_factor=1.06, color=FG), run_time=0.6)
            self.at_words("every event on its right bond")
            self.play(*[r.animate.set_stroke(width=9) for r in ev[3]], run_time=0.6)
            self.play(Indicate(ev[3], scale_factor=1.06, color=FG), run_time=0.6)
            self.at_words("acts on this same")
            spin = T(r"one shared spin (3 states)", font_size=28).next_to(site, UP, buff=0.22)
            self.play(FadeIn(spin, shift=0.1 * DOWN), Indicate(site, color=FG), run_time=0.9)
        self.s07_extra = VGroup(wq, spin)
        self.dimmed = dimmed

    # ================================================================ s08
    def s08(self):
        """Merge, multiply, trace -- and the interleaving matters (G's do not commute)."""
        sites, ev = self.hd
        site = sites[3]
        with self.voice("s08") as d:
            self.begin("s08", d)
            wq, spin = self.s07_extra
            pair = sorted([(r, lab) for k in (2, 3) for r, (_, lab) in zip(ev[k], EVENTS[k])],
                          key=lambda p: p[0].get_y())
            ticks = VGroup(*[Line([site.get_x() - 0.17, r.get_y(), 0],
                                  [site.get_x() + 0.17, r.get_y(), 0], color=XYZ[lab],
                                  stroke_width=7) for r, lab in pair])
            self.play(FadeOut(wq), run_time=0.3)
            self.play(*[ReplacementTransform(r.copy(), t) for (r, _), t in zip(pair, ticks)],
                      *[r.animate.set_stroke(opacity=0.35, width=5) for k in (2, 3) for r in ev[k]],
                      run_time=1.5)
            self.at_words("multiply the matrices")
            prod = MT(r"\operatorname{tr}\big[", *[r"G_{%s}" % lab for _, lab in pair], r"\big]",
                      font_size=38)
            for i, (_, lab) in enumerate(pair):
                prod[i + 1].set_color(XYZ[lab])
            prod.move_to([3.6, 1.6, 0])
            self.play(FadeIn(prod[0]), FadeIn(prod[-1]),
                      LaggedStart(*[ReplacementTransform(t, prod[i + 1])
                                    for i, t in enumerate(ticks)], lag_ratio=0.12),
                      run_time=1.3)
            contrib = T("= this site's factor", font_size=28, color=DIM).next_to(prod, DOWN,
                                                                               buff=0.25)
            self.at_words("that number is")
            self.play(FadeIn(contrib), run_time=0.5)

            # the order matters: a three-line zoom
            self.at_words("And the order matters")
            nc = MT(r"G_xG_y\neq G_yG_x", font_size=34).move_to([3.6, 2.55, 0])
            xs = [2.4, 3.6, 4.8]
            yb, yt = -2.05, 0.75
            zl = VGroup(*[Line([x, yb, 0], [x, yt, 0], color=DIM, stroke_width=2) for x in xs])
            zl[1].set_stroke(FG, width=4)
            def rung(b, y, lab):
                return Line([xs[b], y, 0], [xs[b + 1], y, 0], color=XYZ[lab], stroke_width=6)
            rx, rz, ry = rung(0, -1.35, "x"), rung(0, 0.25, "z"), rung(1, -0.55, "y")
            hl = VGroup(*[M(m, color=XYZ[m], font_size=28) for m in "xzy"])
            hl[0].next_to(rx, LEFT, buff=0.1)
            hl[1].next_to(rz, LEFT, buff=0.1)
            hl[2].next_to(ry, RIGHT, buff=0.1)
            side = VGroup(T("left bond", font_size=24, color=DIM).next_to(VGroup(zl[0], zl[1]), DOWN, buff=0.12),
                          T("right bond", font_size=24, color=DIM).next_to(VGroup(zl[1], zl[2]), DOWN, buff=0.12))
            self.play(FadeOut(VGroup(prod, contrib)), FadeIn(nc), run_time=0.6)
            self.play(FadeIn(zl), FadeIn(side), run_time=0.6)
            self.at_words("Here an x event on the left")
            self.play(GrowFromCenter(rx), GrowFromCenter(rz), FadeIn(hl[0]), FadeIn(hl[1]),
                      run_time=0.6)
            self.play(GrowFromCenter(ry), FadeIn(hl[2]), run_time=0.5)
            f1 = MT(r"\operatorname{tr}[\,", r"G_x", r"G_y", r"G_z", r"\,]=", r"+1", font_size=36)
            for i, c in ((1, SX), (2, SY), (3, SZ)):
                f1[i].set_color(c)
            f1[5].set_color(GAP)
            f1.move_to([3.6, -2.75, 0])
            self.at_words("and the trace is plus one")
            self.play(Write(f1), run_time=0.9)
            self.at_words("Slide the y below the x")
            ry2 = rung(1, -1.8, "y")
            self.play(Transform(ry, ry2), hl[2].animate.next_to(ry2, RIGHT, buff=0.1),
                      run_time=1.1)
            f2 = MT(r"\operatorname{tr}[\,", r"G_y", r"G_x", r"G_z", r"\,]=", r"-1", font_size=36)
            for i, c in ((1, SY), (2, SX), (3, SZ)):
                f2[i].set_color(c)
            f2[5].set_color(SX)
            f2.move_to(f1)
            self.at_words("and it becomes minus one")
            self.play(TransformMatchingTex(f1, f2), run_time=0.9)
            self.play(Indicate(f2[5], color=SX, scale_factor=1.3), run_time=0.5)
        self.s08_extra = VGroup(nc, zl, side, rx, rz, ry, hl, f2, spin)

    # ================================================================ s09
    def s09(self):
        """Only shared sites couple bonds: the weight is a product of site factors."""
        sites, ev = self.hd
        with self.voice("s09") as d:
            self.begin("s09", d)
            self.play(FadeOut(self.s08_extra),
                      *[r.animate.set_stroke(opacity=1, width=5) for g in ev for r in g],
                      *[s_.animate.set_stroke(DIM, width=2, opacity=1) for s_ in sites],
                      run_time=0.4)
            # bonds 0 and 3 share no site: slide an event of bond 0 past one of bond 3
            self.at_words("Events on bonds that share no site")
            others = VGroup(*[r for k in (1, 2, 4, 5) for r in ev[k]])
            self.play(others.animate.set_stroke(opacity=0.2),
                      *[r.animate.set_stroke(width=8) for k in (0, 3) for r in ev[k]],
                      run_time=0.7)
            # two events adjacent in time, on bonds (0,1) and (3,4): they act on different spins
            ea, eb = ev[0][1], ev[3][1]          # (1.60, z) and (1.85, z)
            self.play(Indicate(ea, color=SZ, scale_factor=1.3), Indicate(eb, color=SZ, scale_factor=1.3),
                      run_time=0.7)
            self.at_words("so their order never matters")
            same = MT(r"G_z^{(0)}G_z^{(1)}\;G_z^{(3)}G_z^{(4)}", r"=", r"G_z^{(3)}G_z^{(4)}\;G_z^{(0)}G_z^{(1)}",
                      font_size=30).move_to([3.6, 1.6, 0])
            ok = check_mark(0.3).next_to(same, RIGHT, buff=0.2)
            dif = T("spins 0, 1 vs spins 3, 4: they commute", font_size=26, color=DIM).next_to(
                same, DOWN, buff=0.2)
            self.play(FadeIn(same), Create(ok), FadeIn(dif), run_time=0.8)
            self.at_words("Only interleavings at a shared site count")
            self.play(others.animate.set_stroke(opacity=1),
                      *[r.animate.set_stroke(width=5) for k in (0, 3) for r in ev[k]],
                      LaggedStart(*[Indicate(s_, color=FG, scale_factor=1.0) for s_ in sites[1:6]],
                                  lag_ratio=0.1), run_time=1.2)
            # one bracket per site, spanning its two bonds
            self.at_words("So the weight of a whole configuration")
            ybot = sites[0].get_start()[1]
            brs = VGroup()
            for j in range(1, 6):
                x0, x1 = (sites[j - 1].get_x() + sites[j].get_x()) / 2, (sites[j].get_x() + sites[j + 1].get_x()) / 2
                yy = ybot - 0.3 - 0.28 * (j % 2)
                brs.add(VGroup(Line([x0, yy, 0], [x1, yy, 0], color=FG, stroke_width=2.5),
                               Line([x0, yy, 0], [x0, yy + 0.1, 0], color=FG, stroke_width=2.5),
                               Line([x1, yy, 0], [x1, yy + 0.1, 0], color=FG, stroke_width=2.5),
                               Dot([sites[j].get_x(), yy, 0], radius=0.04, color=FG)))
            wf = MT(r"\text{weight}=\prod_{\text{sites }j}\operatorname{tr}_j\big[\cdots\big]",
                    font_size=34).move_to([3.6, 0.55, 0])
            self.play(FadeOut(VGroup(same, ok, dif)), Write(wf), run_time=0.9)
            self.at_words("each factor involves exactly two")
            self.play(LaggedStart(*[Create(b) for b in brs], lag_ratio=0.2), run_time=1.4)
            two = T("each factor: two neighbouring bonds", font_size=28, color=DIM).next_to(
                wf, DOWN, buff=0.3)
            self.play(FadeIn(two), run_time=0.5)
        self.s09_extra = VGroup(brs, wf, two)

    # ================================================================ s10
    def s10(self):
        """Histories, the nearest-neighbour kernel, and the transfer operator."""
        sites, ev = self.hd
        with self.voice("s10") as d:
            self.begin("s10", d)
            self.play(FadeOut(self.s09_extra), FadeOut(self.tag_conf), run_time=0.4)
            # each bond's events -> a capsule (its history)
            caps = VGroup()
            for k in range(6):
                xk = (sites[k].get_x() + sites[k + 1].get_x()) / 2
                caps.add(history_capsule(EVENTS[k], height=3.0, width=0.34).move_to(
                    [xk, DIAG_C[1], 0]))
            xl = VGroup(*[M(r"x_{%d}" % k, color=SPACE, font_size=28).next_to(caps[k], DOWN, buff=0.15)
                          for k in range(6)])
            self.play(*[Create(c.box) for c in caps],
                      *[ReplacementTransform(r, t) for k in range(6)
                        for r, t in zip(ev[k], caps[k].ticks)],
                      FadeOut(self.tau), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(m) for m in xl], lag_ratio=0.1), run_time=0.7)
            self.at_words("The site between bonds j")
            kern = MT(r"k_\beta(x_j,x_{j+1})=\operatorname{tr}\big[\,G_{\alpha_1}G_{\alpha_2}\cdots "
                      r"\big]_{\text{events of }x_j,\,x_{j+1}\text{ merged in time}}",
                      font_size=34).move_to([0, 3.0, 0])
            self.play(FadeOut(self.expf), FadeOut(self.pos), FadeIn(kern, shift=0.1 * DOWN),
                      Indicate(sites[3], color=FG), run_time=0.9)
            # the ring of beads
            self.at_words("and Z sums the product around the ring")
            angles = [np.deg2rad(a) for a in (198, 162, 126, 90, 54, 18, -18, -54, -90, -126)]
            R = 1.75
            beads = VGroup()
            for k, a in enumerate(angles):
                evs = [(t / 3.0, lab) for t, lab in EVENTS[k]] if k < 6 else EXTRA_BEADS[k - 6]
                b = history_capsule(evs, height=0.8, width=0.3, tick_w=0.2, tick_stroke=4,
                                    frac=True, fill=1.0)
                b.move_to(RING_C + R * np.array([np.cos(a), np.sin(a), 0]))
                beads.add(b)
            hoop = Circle(radius=R, color=FAINT, stroke_width=2).move_to(RING_C)
            nodes = VGroup(*[Dot(RING_C + R * np.array([np.cos(a - np.deg2rad(18)),
                                                        np.sin(a - np.deg2rad(18)), 0]),
                                 radius=0.07, color=FG) for a in angles])
            klab = M(r"k_\beta", font_size=32).move_to(
                RING_C + (R + 0.48) * np.array([np.cos(np.deg2rad(72)), np.sin(np.deg2rad(72)), 0]))
            self.play(*[Transform(caps[k], beads[k]) for k in range(6)],
                      FadeOut(sites), FadeOut(xl), run_time=0.9)
            self.remove(*caps)
            self.add(*beads[:6])
            zf1 = MT(r"Z_L(\beta)=\int\prod_j k_\beta(x_j,x_{j+1})\,d\mu(x_j)", font_size=34)
            zf1.move_to([0.9, 0.45, 0], aligned_edge=LEFT)
            self.play(Create(hoop), LaggedStart(*[FadeIn(b) for b in beads[6:]], lag_ratio=0.2),
                      LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.06),
                      FadeIn(klab), Write(zf1), run_time=1.4)
            self.bring_to_front(beads, nodes)
            self.at_words("whose variables are entire histories")
            self.play(LaggedStart(*[Indicate(b, color=SPACE, scale_factor=1.15) for b in beads],
                                  lag_ratio=0.05), run_time=1.0)
            self.at_words("couplings that can even be negative")
            ex = MT(r"\operatorname{tr}(G_xG_x)=", r"-2<0", font_size=34, color=DIM)
            ex[1].set_color(FG)
            ex.move_to([-3.6, 2.15, 0])
            neg = inline_tag("kernel can be negative", ex, RIGHT, buff=0.35)
            self.play(FadeIn(ex, shift=0.1 * DOWN), FadeIn(neg),
                      LaggedStart(*[Indicate(n, color=FG, scale_factor=1.6) for n in nodes],
                                  lag_ratio=0.05), run_time=1.0)
            self.at_words("Summing it bond by bond")
            zf2 = MT(r"=\operatorname{Tr}\,", r"X_\beta^{\,L}", font_size=34)
            zf2[1].set_color(SPACE)
            zf2.next_to(zf1, DOWN, buff=0.35).align_to(zf1, LEFT).shift(RIGHT * 1.15)
            xb = M(r"X_\beta", color=SPACE, font_size=38).move_to(RING_C)
            xbox = SurroundingRectangle(xb, buff=0.14, color=SPACE, stroke_width=2,
                                        corner_radius=0.08)
            self.play(FadeOut(VGroup(kern, ex, neg)), FadeIn(xb), Create(xbox), run_time=0.9)
            self.at_words("around the ring Z is the trace")
            self.play(Write(zf2), run_time=0.9)
            capt = TX(r"bonds = states,", r" sites = transfer", font_size=32)
            capt.move_to([3.55, -1.75, 0])
            capt[0].set_color(SPACE)
            self.at_words("bonds are the states")
            self.play(FadeIn(capt[0], shift=0.1 * UP),
                      LaggedStart(*[Indicate(b, color=SPACE, scale_factor=1.15) for b in beads],
                                  lag_ratio=0.05), run_time=1.0)
            self.at_words("sites do the transferring")
            self.play(FadeIn(capt[1], shift=0.1 * UP),
                      LaggedStart(*[Indicate(n, color=FG, scale_factor=1.6) for n in nodes],
                                  lag_ratio=0.05), run_time=1.0)
        self.beads, self.nodes, self.hoop, self.klab = beads, nodes, hoop, klab
        self.xb, self.xbox = xb, xbox
        self.s06_right = VGroup(zf1, zf2, capt)

    # ================================================================ s11
    def s11(self):
        with self.voice("s11") as d:
            self.begin("s11", d)
            self.play(FadeOut(self.s06_right), run_time=0.35)
            t2 = place_torus(Torus(3.0, 1.8, nx=10, ny=6, label_size=32), [3.4, 0.9, 0])
            self.at(0.29)
            self.play(FadeIn(t2), run_time=0.8)
            flat = t2.resized(height=0.15)
            # a sliver: chevrons and the beta label would pile onto one line, so they fade
            flat.chev_time.set_opacity(0)
            flat.chev_space.set_opacity(0)
            flat.beta_label.set_opacity(0)
            b0 = M(r"\beta\to0", color=TIME, font_size=36).next_to(flat.rect, UP, buff=0.45)
            self.at(1.39)
            self.play(Transform(t2, flat), FadeIn(b0, shift=0.2 * DOWN),
                      *[FadeOut(b.ticks, scale=0.2) for b in self.beads], run_time=1.8)
            for b in self.beads:          # keep the faded ticks from coming back later
                b.remove(b.ticks)
            three = M("3", font_size=44, color=FG).move_to(self.xb)
            self.at(4.14)
            self.play(Transform(self.xb, three),
                      Transform(self.xbox, SurroundingRectangle(three, buff=0.16, color=FG,
                                                                stroke_width=2,
                                                                corner_radius=0.08)),
                      run_time=0.9)
            res = MT(r"\beta\to0:\quad", r"X_\beta\to3", r",\qquad", r"Z\to3^{L}", font_size=36)
            res[0][0].set_color(TIME)
            res.move_to([3.2, -1.45, 0])
            self.at(5.81)
            self.play(Write(res), run_time=1.3)
            ck = check_mark(0.4).next_to(res, RIGHT, buff=0.35)
            self.at(7.6)
            self.play(Create(ck), run_time=0.6)
            self.at(9.02)
            self.play(Indicate(ck, color=GAP, scale_factor=1.3), run_time=0.6)
        self.s11_all = VGroup(self.beads, self.nodes, self.hoop, self.klab, self.xb, self.xbox,
                              t2, b0, res, ck)

    # ================================================================ s12
    def s12(self):
        with self.voice("s12") as d:
            self.begin("s12", d)
            self.play(FadeOut(self.s11_all), run_time=0.35)
            xa, xb_ = -3.6, 3.6
            hx = [(0.15, "x"), (0.50, "z"), (0.82, "y")]
            hy = [(0.30, "y"), (0.66, "x"), (0.92, "z")]

            # two histories named x (left) and y (right); history names in SPACE, as x_2 in s05
            a1 = history_capsule(hx, height=2.4, frac=True).move_to([xa - 0.6, 0.2, 0])
            b1 = history_capsule(hy, height=2.4, frac=True).move_to([xa + 0.6, 0.2, 0])
            la1 = M("x", font_size=36, color=SPACE).next_to(a1, UP, buff=0.2)
            lb1 = M("y", font_size=36, color=SPACE).next_to(b1, UP, buff=0.2)
            self.at(0.33)
            self.play(FadeIn(VGroup(a1, b1)), FadeIn(la1), FadeIn(lb1), run_time=0.7)
            # the same unmerged pair, copied to the right
            a2, b2, la2, lb2 = [m.copy() for m in (a1, b1, la1, lb1)]
            for m in (a2, b2, la2, lb2):
                m.shift(RIGHT * (xb_ - xa))
            self.play(*[TransformFromCopy(m, c) for m, c in zip((a1, b1, la1, lb1),
                                                                (a2, b2, la2, lb2))],
                      run_time=0.6)

            def kb(p, q, xc):
                k = MT(r"k_\beta(", p, ",", q, ")", font_size=34)
                k[1].set_color(SPACE)
                k[3].set_color(SPACE)
                return k.move_to([xc, -1.6, 0])

            def merge(a, b, l_left, l_right, xc, **kw):
                return AnimationGroup(a.animate.move_to([xc, 0.2, 0]),
                                      b.animate.move_to([xc, 0.2, 0]),
                                      l_left.animate.move_to([xc - 0.25, l_left.get_y(), 0]),
                                      l_right.animate.move_to([xc + 0.25, l_right.get_y(), 0]),
                                      **kw)

            k1 = kb("x", "y", xa)
            k2 = kb("y", "x", xb_)
            self.at(1.92)
            self.play(merge(a1, b1, la1, lb1, xa), FadeIn(k1, shift=0.1 * UP), run_time=0.9)
            b1.remove(b1.box)
            # swap which history comes from the left, then merge again
            self.play(Swap(a2, b2), Swap(la2, lb2), run_time=0.8)
            self.play(merge(b2, a2, lb2, la2, xb_), run_time=0.9)
            b2.remove(b2.box)
            eqs = M("=", font_size=60, color=GAP).move_to([0, 0.2, 0])
            greal = MT(r"G_\alpha", r"\ \text{real}", font_size=36).move_to([0, 2.45, 0])
            self.play(FadeIn(k2, shift=0.1 * UP), FadeIn(eqs, scale=0.6),
                      Indicate(VGroup(a1, b1.ticks), color=GAP, scale_factor=1.06),
                      Indicate(VGroup(a2, b2.ticks), color=GAP, scale_factor=1.06), run_time=0.9)
            self.play(FadeIn(greal, shift=0.1 * DOWN), run_time=0.5)

            sym = MT(r"k_\beta(", "x", ",", "y", r")=k_\beta(", "y", ",", "x", r")\in\mathbb R",
                     r"\ \Longrightarrow\ X_\beta=X_\beta^{\dagger}",
                     r"\ \Longrightarrow\ \lambda_i(\beta)\in\mathbb R", font_size=36)
            for i in (1, 3, 5, 7):
                sym[i].set_color(SPACE)
            sym.move_to([0, -2.75, 0])
            box = SurroundingRectangle(sym, buff=0.2, color=GAP, stroke_width=2.5,
                                       corner_radius=0.08)
            self.at(6.51)
            self.play(Write(sym[0:9]), run_time=1.0)
            self.at(8.75)
            self.play(Write(sym[9]), run_time=0.9)
            self.at(10.26)
            self.play(Write(sym[10]), run_time=0.9)
            self.play(Create(box), run_time=0.6)
        self.s12_all = VGroup(a1, b1, la1, lb1, a2, b2, la2, lb2, k1, k2, eqs, greal, sym, box)

    # ================================================================ s13
    def s13(self):
        with self.voice("s13", breath=2.0) as d:
            self.begin("s13", d)
            self.play(FadeOut(self.s12_all), run_time=0.35)
            el = EigLine(LAMS, width=9.0, dot_r=0.1, font_size=30).move_to([0, 0.85, 0])
            lab = M(r"\lambda_i(\beta)", color=SPACE, font_size=36).next_to(el.line, RIGHT,
                                                                            buff=0.3)
            sch = inline_tag(TAG_SCHEMATIC, el.line, DOWN, buff=0.7).align_to(el.line, RIGHT)
            self.at(0.34)
            self.play(el.build(), FadeIn(lab), FadeIn(sch), run_time=1.3)
            negs = VGroup(*[dt for dt, v in zip(el.dots, LAMS) if v < 0])
            nb = Brace(negs, UP, buff=0.2, color=FG)
            nl = M(r"\lambda_i<0", font_size=34).next_to(nb, UP, buff=0.1)
            self.play(GrowFromCenter(nb), FadeIn(nl),
                      LaggedStart(*[Indicate(dt, color=FG, scale_factor=1.6) for dt in negs],
                                  lag_ratio=0.15), run_time=1.0)
            pg = pause_glyph().move_to([-1.6, -1.45, 0])
            self.at(2.92)
            self.play(FadeIn(pg, scale=0.8), run_time=0.6)
            r5 = fg_ring(5, radius=0.55, length=0.3).move_to([-0.2, -1.45, 0])
            q = TX(r"odd $L$\,?", font_size=44).next_to(r5, RIGHT, buff=0.45)
            self.at(4.15)
            self.play(FadeIn(r5), Write(q), run_time=1.0)
            bub = objection_bubble("even")
            self.at(5.4)
            self.play(bubble_in(bub), run_time=0.8)
        self.bub = bub
        self.s13_all = VGroup(el, lab, sch, nb, nl, pg, r5, q)

    # ================================================================ s14
    def s14(self):
        with self.voice("s14") as d:
            self.begin("s14", d)
            self.play(FadeOut(self.s13_all), run_time=0.35)
            hdr = M(r"\beta=\tfrac{49}{4}=12.25", color=TIME, font_size=40).to_corner(UL, buff=0.5)
            ys = 0.75
            r4 = fg_ring(4).move_to([-4.3, ys, 0])
            r5 = fg_ring(5).move_to([0.0, ys, 0])
            r6 = fg_ring(6).move_to([4.3, ys, 0])
            z4 = M(r"Z_4=124.885", font_size=36).next_to(r4, DOWN, buff=0.45)
            # Z_5 stays a question mark until the reveal ("It is 0.003")
            z5q = MT(r"Z_5=", r"\text{?}", font_size=36).next_to(r5, DOWN, buff=0.45)
            z5 = MT(r"Z_5=", r"0.0029", font_size=36, color=DEFECT).next_to(r5, DOWN, buff=0.45)
            z6 = M(r"Z_6=12.871", font_size=36).next_to(r6, DOWN, buff=0.45)
            for z in (z4, z5q, z5, z6):
                z.set_y(ys - 1.35)
            self.at(0.30)
            self.play(FadeIn(hdr, shift=0.1 * DOWN), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(VGroup(r, z), shift=0.15 * UP)
                                    for r, z in ((r4, z4), (r5, z5q), (r6, z6))], lag_ratio=0.25),
                      run_time=1.4)
            note = MT(r"Z_n=\operatorname{Tr}\,e^{-\beta(H_n+an)}", font_size=34, color=DIM)
            note.next_to(hdr, RIGHT, buff=0.7)
            note2 = TX(r"energies measured from $-a$ per site", font_size=26, color=DIM)
            note2.next_to(note, DOWN, buff=0.15).align_to(note, LEFT)
            self.at(3.26)
            self.play(FadeIn(note), FadeIn(note2), run_time=0.8)

            ineq = MT(r"\text{all }\lambda_i\ge0", r"\ \Rightarrow\ Z_5^{1/5}\ge Z_6^{1/6}",
                      r"\ \Rightarrow\ Z_5\ge12.87^{5/6}\approx8.4", font_size=36)
            ineq.move_to([0, -2.05, 0])
            self.at(5.72)
            # Z_4 plays no part in the argument: dim it so the eye compares Z_5 with Z_6
            self.play(Write(ineq[0]), VGroup(r4, z4).animate.fade(0.6), run_time=0.9)
            self.at(8.51)
            self.play(Write(ineq[1]), Indicate(z6, color=FG, scale_factor=1.12), run_time=1.3)
            self.play(Write(ineq[2]), run_time=1.3)

            cx = cross_mark(0.42).next_to(ineq, RIGHT, buff=0.35)
            self.at(13.27)
            self.play(TransformMatchingTex(z5q, z5), Create(cx), ineq.animate.set_opacity(0.45),
                      run_time=0.7)
            self.play(pulse(z5), run_time=0.7)

            # the seam: a half turn at one bond of the odd ring
            ang0, ang4 = PI / 2, TAU * 4 / 5 + PI / 2
            R = 0.75
            fb = Arc(radius=R, start_angle=ang4 - TAU, angle=(ang0 - (ang4 - TAU)), color=FG,
                     stroke_width=6).move_arc_center_to(r5[0].get_center())
            mid = (ang0 + ang4 - TAU) / 2
            seam = seam_glyph().move_to(r5[0].get_center() + (R + 0.55) * np.array(
                [np.cos(mid), np.sin(mid), 0]))
            ht = T("half turn", font_size=26, color=DIM).next_to(seam, RIGHT, buff=0.15)
            self.at(15.89)
            self.play(FadeOut(ineq), FadeOut(cx), Create(fb), run_time=0.8)
            self.play(FadeIn(seam, scale=0.6), FadeIn(ht), Indicate(fb, color=FG), run_time=1.0)

            zp = M(r"Z_5(P)=2.961", font_size=36).move_to([0, -2.55, 0])
            arr = Arrow(z5.get_bottom() + DOWN * 0.05, zp.get_top() + UP * 0.05, buff=0.08,
                        color=DIM, stroke_width=3, max_tip_length_to_length_ratio=0.25)
            x1000 = M(r"\times1400", font_size=32, color=FG).next_to(arr, RIGHT, buff=0.2)
            self.at(20.54)
            self.play(GrowArrow(arr), FadeIn(zp, shift=0.2 * DOWN), FadeIn(x1000), run_time=1.0)
        self.s14_all = VGroup(hdr, r4, r5, r6, z4, z5, z6, note, note2, fb, seam, ht, zp, arr,
                              x1000)

    # ================================================================ s15
    def s15(self):
        bub = self.bub
        with self.voice("s15") as d:
            self.begin("s15", d)
            self.play(FadeOut(self.s14_all), run_time=0.35)
            base_y = -0.6
            sb = WeightBars(LAMS ** 5, width=3.6, height=2.6, color=SPACE, signed=True,
                            value_scale=1.6)
            sb.shift(np.array([-3.3, base_y, 0]) - sb.base.get_center())
            l5 = M(r"\lambda_i^{\,5}", color=SPACE, font_size=38).next_to(sb.base, LEFT, buff=0.3)
            sch = inline_tag(TAG_SCHEMATIC, sb.base, DOWN, buff=1.15)
            self.at(0.30)
            self.play(Create(sb.base), LaggedStart(*[GrowFromEdge(
                b, DOWN if v >= 0 else UP) for b, v in zip(sb.bars, LAMS ** 5)], lag_ratio=0.1),
                FadeIn(l5), FadeIn(sch), run_time=1.3)
            ev = MT(r"L\ \text{even}:\quad", r"\lambda_i^{L}=|\lambda_i|^{L}\ge0",
                    r",\qquad p_i=\frac{|\lambda_i|^{L}}{Z}", font_size=36)
            ev[2].set_color(SPACE)
            ev.to_corner(UL, buff=0.5)
            l6 = M(r"\lambda_i^{\,6}", color=SPACE, font_size=38).move_to(l5)
            self.at(2.76)
            self.play(sb.morph_to(LAMS ** 6), Transform(l5, l6), run_time=1.3)
            self.play(Write(ev[0:2]), run_time=1.0)

            # a second probability distribution for the same Z
            p = LAMS ** 6 / (LAMS ** 6).sum()
            gb = WeightBars(GIBBS, width=3.6, height=2.6, color=TIME, highlight_color=TIME)
            gb.shift(np.array([3.3, base_y, 0]) - gb.base.get_center())
            pl_ = MT(r"p_i", r"\ \text{(spatial)}", color=SPACE, font_size=34)
            wl_ = MT(r"w_k", r"\ \text{(thermal)}", color=TIME, font_size=34)
            pl_.next_to(sb.base, DOWN, buff=0.3)
            wl_.next_to(gb.base, DOWN, buff=0.3)
            self.at(7.35)
            self.play(Write(ev[2]), sb.morph_to(p * 2.6 / 1.6), FadeOut(l5), run_time=1.2)
            self.play(FadeIn(pl_), Create(gb.base),
                      LaggedStart(*[GrowFromEdge(b, DOWN) for b in gb.bars], lag_ratio=0.1),
                      FadeIn(wl_), run_time=1.2)
            both = VGroup(sb.base, gb.base, pl_, wl_)
            br = Brace(both, DOWN, buff=0.2, color=FG)
            same = TX(r"same $Z$", font_size=32).next_to(br, DOWN, buff=0.12)
            self.play(GrowFromCenter(br), FadeIn(same),
                      sch.animate.next_to(same, DOWN, buff=0.3), run_time=0.7)

            self.at(11.77)
            self.play(bubble_indicate(bub), run_time=0.8)
            self.play(bubble_check(bub), run_time=0.6)
            self.at(13.9)
            self.play(bubble_out(bub), run_time=0.5)
        self.s15_all = VGroup(sb, gb, ev, pl_, wl_, br, same, sch)

    # ================================================================ s16
    def s16(self):
        with self.voice("s16") as d:
            self.begin("s16", d)
            tor = place_torus(Torus(5, 3, nx=10, ny=6), TOR_L)
            rt = tag(TAG_READING, buff=0.42)
            self.play(FadeOut(self.s15_all), run_time=0.35)
            self.at(0.31)
            self.play(FadeIn(tor), tag_in(rt), run_time=0.9)

            # the top eigenvalue lambda_0 encodes the free energy (schematic line: no
            # eigenvalue of X is known numerically)
            el = EigLine(LAMS, width=3.8, font_size=26).move_to([4.5, 1.5, 0])
            el.dots[0].scale(1.5)
            sch12 = inline_tag(TAG_SCHEMATIC, el, DOWN, buff=0.25).align_to(el.line, RIGHT)
            fe = TX(r"$\lambda_0$: free energy per site", font_size=28, color=SPACE)
            fe.next_to(el.dots[0], UP, buff=0.5).align_to(el.line, RIGHT).shift(RIGHT * 0.1)
            fe_arr = Arrow(ORIGIN, UP, buff=0, color=SPACE, stroke_width=2.5,
                           max_tip_length_to_length_ratio=0.3)
            fe_arr.put_start_and_end_on(
                np.array([el.dots[0].get_x(), fe.get_bottom()[1] - 0.04, 0]),
                el.dots[0].get_top() + UP * 0.04)
            self.at(2.94)
            self.play(el.build(), FadeIn(sch12), run_time=1.2)
            self.play(FadeIn(fe, shift=0.1 * DOWN), GrowArrow(fe_arr),
                      Indicate(el.dots[0], color=SPACE, scale_factor=1.4), run_time=0.9)
            ratio = MT(r"\lambda_i/\lambda_0", r"\ \leftrightarrow\ ", r"e^{-1/\xi(T)}",
                       font_size=36)
            ratio[0].set_color(SPACE)
            ratio.move_to([4.5, -0.4, 0])
            self.at(5.66)
            self.play(LaggedStart(*[Indicate(dt, color=SPACE, scale_factor=1.5)
                                    for dt in el.dots[1:]], lag_ratio=0.08),
                      Write(ratio), run_time=1.3)

            # two faces of one mass: the correlation time 1/Delta and the length xi
            xv = tor.x_at(0.12)
            va = DoubleArrow([xv, tor.y_at(0.12), 0], [xv, tor.y_at(0.88), 0], buff=0,
                             color=TIME, stroke_width=4, tip_length=0.18)
            vl = TX(r"correlation time $1/\Delta$", font_size=28, color=TIME)
            vl.next_to(va, RIGHT, buff=0.2).set_y(tor.y_at(0.72))
            yh = tor.y_at(0.3)
            ha = DoubleArrow([tor.x_at(0.3), yh, 0], [tor.x_at(0.94), yh, 0], buff=0,
                             color=SPACE, stroke_width=4, tip_length=0.18)
            hl = TX(r"correlation length $\xi$", font_size=28, color=SPACE)
            hl.next_to(ha, UP, buff=0.15).align_to(ha, RIGHT)
            for lab_ in (vl, hl):
                lab_.set_stroke(BG, width=6, background=True)
            dxv = MT(r"\Delta\cdot\xi\approx v", font_size=36, color=DIM).move_to([4.5, -1.7, 0])
            self.at(7.73)
            self.play(Create(va), FadeIn(vl), run_time=0.9)
            self.play(Create(ha), FadeIn(hl), run_time=0.9)
            self.at(10.55)
            self.play(FadeIn(dxv, shift=0.1 * UP), Indicate(va, color=TIME, scale_factor=1.05),
                      Indicate(ha, color=SPACE, scale_factor=1.05), run_time=0.8)

            # yet spatial eigenvalues are not energies (the paper: 'distinct objects')
            lv = level_ticks(LEVELS, tick_w=0.4, gap=0.1, yscale=0.8, stroke=4)
            lv.move_to([0.6, 1.5, 0])
            ne = M(r"\neq", font_size=52).move_to([1.95, 1.5, 0])
            ne_l = T("not energies", font_size=28, color=DIM).move_to([1.95, 0.7, 0])
            self.at(11.45)
            self.play(LaggedStart(*[Create(t) for t in lv], lag_ratio=0.08), FadeIn(ne),
                      FadeIn(ne_l, shift=0.1 * UP), run_time=1.0)

            # the proof needs none of this: the reading fades, both knives return
            self.at(12.8)
            # the comparison stays and settles level with the torus
            cmp = VGroup(lv, ne, ne_l, el, sch12)
            self.play(FadeOut(VGroup(rt, fe, fe_arr, ratio, va, vl, ha, hl, dxv)),
                      cmp.animate.shift(UP * (tor.rect.get_y() - cmp.get_y())), run_time=0.7)
            hk = time_knife(tor, at=0.25)
            vk = space_knife(tor, bond=6)
            self.play(hk.cut_in(), vk.cut_in(), run_time=0.8)
            self.play(hk.glow_on(), vk.glow_on(), run_time=0.3)
        self.wait(0.6)
        self.play(FadeOut(*self.mobjects), run_time=1.0)
