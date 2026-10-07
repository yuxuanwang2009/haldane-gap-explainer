"""ch05: Purity.

Both readings of Z become distributions; purity and the defect; T and S as ratios of
partition functions; the squaring lemma; purity -> unique ground state and a gap; the
skeptic's 'purity -> 1 at fixed L' objection and the real target (L and beta doubling
together).

Sync: each voice block places its animations on cue times measured from the clip
(pauses found with ffmpeg silencedetect).  Cue times are stored in seconds for the
reference clip length REF[seg] and rescaled to the actual clip length d, so a slightly
different TTS take still lines up.
"""
import csv

import numpy as np

from motifs import *  # noqa: F401,F403

# clip lengths the cue times below were measured on
REF = {"s01": 16.95, "s02": 12.325, "s03": 13.375, "s04": 10.15, "s05": 10.225,
       "s06": 20.275, "s07": 10.275, "s08": 15.1}


def MM(*parts, **kw):
    """Multi-part MathTex (parts can be coloured / transformed separately)."""
    kw.setdefault("color", FG)
    return MathTex(*parts, tex_template=TEX_TEMPLATE, **kw)


def base_to(wb, point):
    """Shift a WeightBars so that the centre of its base line sits at `point`."""
    wb.shift(np.array(point, dtype=float) - wb.base.get_center())
    return wb


def grow_bars(wb, **kw):
    kw.setdefault("lag_ratio", 0.08)
    return AnimationGroup(Create(wb.base),
                          LaggedStart(*[GrowFromEdge(b, DOWN) for b in wb.bars],
                                      lag_ratio=kw.pop("lag_ratio")), **kw)


def draw_marker(hollow=False, size=0.4):
    t = Triangle().rotate(PI).scale_to_fit_width(size)
    if hollow:
        t.set_fill(BG, opacity=1).set_stroke(FG, width=3.5)
    else:
        t.set_fill(FG, opacity=1).set_stroke(FG, width=1)
    return t


def ghost_outlines(wb, color=DIM, opacity=0.75, width=2.0):
    """Outlines of the bars at their current heights (left behind while squaring)."""
    return VGroup(*[Rectangle(width=b.width, height=b.height, stroke_color=color,
                              stroke_width=width, stroke_opacity=opacity, fill_opacity=0)
                    .move_to(b) for b in wb.bars]).set_z_index(2)


def reveal_markers(mk, fracs, hollow, lead=0.03):
    """Markers appear as the curve being drawn reaches them (fracs = drawing progress)."""
    for m in mk:
        (m.set_stroke(opacity=0) if hollow else m.set_fill(opacity=0))

    def upd(g, a):
        for m, f in zip(g, fracs):
            o = float(np.clip((a - f + lead) / lead, 0.0, 1.0))
            (m.set_stroke(opacity=o) if hollow else m.set_fill(opacity=o))
    return UpdateFromAlphaFunc(mk, upd)


def load_thermal(S, L, beta_max=40.0, floor=1e-14):
    rows = []
    with open(DATA / "thermal_purity_vs_beta.csv") as fh:
        for r in csv.DictReader(fh):
            if abs(float(r["S"]) - S) < 1e-9 and int(r["L"]) == L:
                b, v = float(r["beta"]), float(r["1-T"])
                if b <= beta_max + 1e-9 and v >= floor:
                    rows.append((b, v))
    rows.sort()
    return rows


class Ch05(NarratedScene):
    CHAPTER = "ch05"

    # ------------------------------------------------------------ cue helpers
    def begin(self, seg, d):
        self._t0 = self.renderer.time
        self._k = d / REF[seg]

    def at(self, t):
        """Wait until cue t (reference seconds after the clip start)."""
        dt = self._t0 + t * self._k - self.renderer.time
        if dt > 0.04:
            self.wait(dt)

    def until(self, t, frac=1.0, lo=0.3):
        """Run time that ends at cue t (times frac)."""
        return max(lo, (self._t0 + t * self._k - self.renderer.time) * frac)

    # ------------------------------------------------------------ chapter
    def construct(self):
        # ============================================================ s01
        with self.voice("s01") as d:
            self.begin("s01", d)
            tor = Torus(5, 3, nx=10, ny=6).shift(UP * 0.35)
            hk = time_knife(tor, at=0.58)
            vk = space_knife(tor, bond=1)
            self.play(FadeIn(tor), run_time=0.5)
            self.play(hk.cut_in(), vk.cut_in(), run_time=0.55)
            self.play(hk.glow_on(), vk.glow_on(), run_time=0.25)

            # "two distributions"
            self.at(1.12)
            gib = base_to(WeightBars([0.55, 0.12, 0.12, 0.12, 0.04, 0.03, 0.02], width=2.6,
                                     height=2.2, color=TIME), (-4.75, -0.55, 0))
            gcap = gib.caption(r"e^{-\beta E_k}", font_size=34)
            spa = base_to(WeightBars([0.62, 0.16, 0.09, 0.07, 0.06], width=2.6, height=2.2,
                                     color=SPACE), (4.75, -0.55, 0))
            scap = spa.caption(r"|\lambda_i|^{L}", font_size=34)
            # schematic weights (not data): one tag for the pair of charts
            sch0 = tag_box(TAG_SCHEMATIC).move_to(DOWN * 3.3)
            self.play(FadeIn(gib, shift=LEFT * 0.6), FadeIn(gcap, shift=LEFT * 0.6),
                      FadeIn(spa, shift=RIGHT * 0.6), FadeIn(scap, shift=RIGHT * 0.6),
                      FadeIn(sch0), run_time=self.until(2.35))

            # "one Z"
            self.at(2.41)
            zlab = M(r"Z(L,\beta)", font_size=44).move_to(DOWN * 2.55)
            a1 = Arrow(gcap.get_bottom() + DOWN * 0.05, zlab.get_left() + LEFT * 0.1,
                       color=DIM, stroke_width=3, buff=0.1, max_tip_length_to_length_ratio=0.08)
            a2 = Arrow(scap.get_bottom() + DOWN * 0.05, zlab.get_right() + RIGHT * 0.1,
                       color=DIM, stroke_width=3, buff=0.1, max_tip_length_to_length_ratio=0.08)
            self.play(Write(zlab), GrowArrow(a1), GrowArrow(a2), run_time=0.7)

            # "To measure how much one term dominates": hold the recap, then the torus
            # becomes the thumbnail
            self.at(4.7)
            thumb = TorusThumb()
            self.play(FadeOut(hk, vk), tor.grid.animate.set_stroke(opacity=0),
                      FadeOut(gib, gcap, shift=RIGHT * 0.8), FadeOut(spa, scap, shift=LEFT * 0.8),
                      FadeOut(zlab, a1, a2, sch0), run_time=0.35)

            # "use purity: the sum of squared probabilities": thumbnail, neutral bars, P
            wb = base_to(WeightBars([0.70, 0.15, 0.08, 0.04, 0.03], width=4.4, height=2.6,
                                    color=FG), (-1.9, -2.0, 0))
            sch1 = inline_tag(TAG_SCHEMATIC, wb.base, DOWN, buff=0.3)
            f1 = MM(r"P=\sum_i p_i^{\,2}", r",\qquad", r"u", r"=1-P",
                    r"\ \approx\ 2\,(1-p_{\max})", font_size=40)
            f1[2].set_color(DEFECT)
            f1.move_to(UP * 2.75 + RIGHT * 0.9)
            t_in = self.until(6.45, lo=1.2)
            self.play(AnimationGroup(
                ReplacementTransform(tor, thumb, run_time=0.65),
                Succession(Wait(0.3), AnimationGroup(grow_bars(wb), FadeIn(sch1)),
                           run_time=t_in),
                Succession(Wait(0.35), Write(f1[0]), run_time=t_in)))
            self.play(Indicate(f1[0], color=FG, scale_factor=1.12),
                      LaggedStart(*[Indicate(b, color=FG, scale_factor=1.06) for b in wb.bars],
                                  lag_ratio=0.2), run_time=self.until(7.9, lo=1.0))

            # "the chance that two independent draws agree": two misses, then a match
            self.at(8.34)

            def spot(i, dx=0.0):
                return wb.bars[i].get_top() + UP * 0.32 + RIGHT * dx

            for (i1, x1), (i2, x2), match in (((0, 0.0), (2, 0.0), False),
                                              ((1, 0.0), (0, 0.0), False),
                                              ((0, -0.22), (0, 0.22), True)):
                m1 = draw_marker(False).move_to(spot(i1, x1))
                m2 = draw_marker(True).move_to(spot(i2, x2))
                self.play(FadeIn(m1, shift=DOWN * 0.55), FadeIn(m2, shift=DOWN * 0.55),
                          run_time=0.35)
                if match:
                    self.play(Indicate(wb.bars[0], color=GAP, scale_factor=1.04),
                              Flash(VGroup(m1, m2).get_top() + UP * 0.12, color=GAP,
                                    line_length=0.2, flash_radius=0.38), run_time=0.6)
                    self.play(FadeOut(m1, m2), run_time=self.until(11.25, lo=0.25))
                else:
                    self.wait(0.12)
                    self.play(FadeOut(m1, m2, shift=UP * 0.25), run_time=0.25)

            # "One minus the purity is the defect": the gauge measures the fixed bars
            # (fill sweeps up, the number appears when it lands)
            self.at(11.31)
            gauge = DefectGauge(0.479, kind="u", decimals=3, basin=False)
            gauge.move_to(RIGHT * 3.4 + DOWN * 0.75)
            gnum = gauge.number
            gnum.clear_updaters()
            gauge.remove(gnum)
            gauge.tracker.set_value(-3.0)
            gauge.fill.update()
            self.play(Write(f1[1:4]), FadeIn(gauge), run_time=0.9)
            self.play(gauge.set_defect(0.479), run_time=1.0)
            gauge.add(gnum)
            self.play(FadeIn(gnum, shift=UP * 0.1), run_time=0.35)

            # "roughly twice the chance of missing the dominant outcome"
            self.at(13.71)
            br = wb.defect_brace(M(r"1-p_{\max}", color=DEFECT, font_size=34))
            self.play(Write(f1[4]), GrowFromCenter(br[0]), FadeIn(br[1], shift=UP * 0.1),
                      run_time=1.2)
            self.play(Indicate(f1[4], color=DEFECT, scale_factor=1.08), run_time=1.0)

        # ============================================================ s02
        with self.voice("s02") as d:
            self.begin("s02", d)
            wb.brace = None                       # the brace leaves with s01
            gauge.fill.clear_updaters()           # else the fill updater undoes the fade
            wb.generate_target()
            wb.target.shift(np.array([-3.0, -2.0, 0]) - wb.base.get_center())
            wb.target.bars.set_fill(TIME)
            # the schematic tag drops under the caption that is about to appear
            cap_slot = M(r"e^{-\beta E_k}", font_size=36).next_to(wb.target.base, DOWN,
                                                                  buff=0.25)
            sch1_tgt = sch1.copy().next_to(cap_slot, DOWN, buff=0.25)
            self.play(FadeOut(f1, gauge, br), MoveToTarget(wb), sch1.animate.move_to(sch1_tgt),
                      run_time=1.0)
            wb.color = wb.hl_color = TIME

            self.at(1.61)
            cap = wb.caption(r"e^{-\beta E_k}", font_size=36)
            self.play(Write(cap), run_time=0.9)

            self.at(3.54)
            sqT = MM(r"\big(e^{-\beta E_k}\big)^2", "=", r"e^{-2\beta E_k}", font_size=40,
                     color=TIME).move_to(RIGHT * 3.3 + UP * 1.25)
            s1, s2 = wb.square(relabel=r"e^{-2\beta E_k}")
            self.play(s1, Write(sqT), run_time=1.0)
            self.play(s2, thumb.double_beta(), run_time=1.3)

            # "So the thermal purity T is Z at doubled beta over Z squared"
            self.at(6.08)
            tl1 = MM(r"T(L,\beta)", "=", r"\sum_k w_k^{\,2}", "=", r"{Z(L,2\beta)", r"\over",
                     r"Z(L,\beta)^2}", font_size=40, color=TIME)
            tl1.move_to(RIGHT * 3.3 + DOWN * 0.45)
            tl2 = MM("=", r"\operatorname{Tr}\,\rho_\beta^{\,2}", font_size=40, color=TIME)
            tl2.next_to(tl1, DOWN, buff=0.45)
            tl2.shift(RIGHT * (tl1[3].get_center()[0] - tl2[0].get_center()[0]))
            self.play(Write(tl1[0:3]), run_time=0.9)
            self.at(7.3)
            self.play(Write(tl1[3:]), run_time=1.1)
            self.at(10.0)
            self.play(Write(tl2), run_time=0.9)

        # ============================================================ s03
        with self.voice("s03") as d:
            self.begin("s03", d)
            Tc = MM(r"T(L,\beta)", "=", r"{Z(L,2\beta)", r"\over", r"Z(L,\beta)^2}",
                    font_size=36, color=TIME)
            Tc.to_corner(UR, buff=0.4)
            wb2 = base_to(WeightBars([0.62, 0.14, 0.10, 0.08, 0.06], width=4.4, height=2.6,
                                     color=SPACE), (-3.0, -2.0, 0))
            self.play(*[ReplacementTransform(tl1[i], Tc[j]) for i, j in
                        ((0, 0), (1, 1), (4, 2), (5, 3), (6, 4))],
                      FadeOut(tl1[2], tl1[3], tl2, sqT),
                      FadeOut(wb, wb.cap, shift=DOWN * 0.3), thumb.reset(), run_time=1.0)
            self.play(grow_bars(wb2), run_time=self.until(1.6))

            self.at(1.66)
            cap2 = wb2.caption(r"|\lambda_i|^{L}", font_size=36)
            self.play(Write(cap2), run_time=0.8)

            self.at(2.96)
            sqS = MM(r"\big(|\lambda_i|^{L}\big)^2", "=", r"|\lambda_i|^{2L}", font_size=40,
                     color=SPACE).move_to(RIGHT * 3.3 + UP * 1.0)
            s1, s2 = wb2.square(relabel=r"|\lambda_i|^{2L}")
            self.play(s1, Write(sqS), run_time=0.9)
            self.play(s2, thumb.double_L(), run_time=1.2)

            # "So the spatial purity S is Z at doubled length over Z squared"
            self.at(5.15)
            sl1 = MM(r"S(L,\beta)", "=", r"\sum_i p_i^{\,2}", "=", r"{Z(2L,\beta)", r"\over",
                     r"Z(L,\beta)^2}", font_size=40, color=SPACE)
            sl1.move_to(RIGHT * 3.3 + DOWN * 0.45)
            ev = T(r"($L$ even)", font_size=30, color=DIM)
            ev.next_to(sl1, DOWN, buff=0.35).align_to(sl1, RIGHT)
            self.play(Write(sl1[0:3]), run_time=0.8)
            self.play(Write(sl1[3:]), run_time=1.0)
            self.play(FadeIn(ev), run_time=0.5)

            # "Doubling beta squares one distribution;" the thumbnail doubles in beta
            self.at(9.17)
            r_b = thumb.reset(run_time=0.4)
            d_b = thumb.double_beta()
            self.play(AnimationGroup(Succession(r_b, d_b, run_time=self.until(11.4, lo=1.4)),
                                     Indicate(Tc, color=TIME, scale_factor=1.1, run_time=1.1)))

            # "doubling L squares the other." the thumbnail doubles in L
            self.at(11.52)
            Sc = MM(r"S(L,\beta)", "=", r"{Z(2L,\beta)", r"\over", r"Z(L,\beta)^2}",
                    font_size=36, color=SPACE)
            Sc.next_to(Tc, DOWN, buff=0.4).align_to(Tc, LEFT)
            evc = T(r"($L$ even)", font_size=28, color=DIM).next_to(Sc, DOWN, buff=0.15)
            evc.align_to(Sc, RIGHT)
            r_L = thumb.reset(run_time=0.4)
            d_L = thumb.double_L()
            self.play(AnimationGroup(
                *[ReplacementTransform(sl1[i], Sc[j], run_time=1.1) for i, j in
                  ((0, 0), (1, 1), (4, 2), (5, 3), (6, 4))],
                FadeOut(sl1[2], sl1[3], sqS, run_time=1.1),
                ReplacementTransform(ev, evc, run_time=1.1),
                Succession(r_L, d_L, run_time=1.7)))

        # ============================================================ s04
        with self.voice("s04") as d:
            self.begin("s04", d)
            pair = VGroup(Tc.copy(), Sc.copy())
            pair.scale(1.3).arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(UP * 1.0)
            evt = evc.copy().scale(1.0).next_to(pair[1], RIGHT, buff=0.4).align_to(
                pair[1][0], DOWN)
            self.play(FadeOut(wb2, wb2.cap, shift=DOWN * 0.3), FadeOut(sch1), thumb.reset(),
                      Tc.animate.scale(1.3).move_to(pair[0]),
                      Sc.animate.scale(1.3).move_to(pair[1]),
                      evc.animate.move_to(evt), run_time=1.0)

            # "both purities are ratios of partition functions"
            self.at(1.17)
            zs = [Tc[2], Tc[4], Sc[2], Sc[4]]
            self.play(LaggedStart(*[Indicate(z, color=FG, scale_factor=1.15) for z in zs],
                                  lag_ratio=0.25), run_time=1.6)
            self.play(*[z.animate.set_color(FG) for z in zs], run_time=0.6)

            # "No single energy or eigenvalue is needed"
            self.at(4.47)
            t1 = T(r"no energy, no eigenvalue: only partition functions", font_size=34)
            t1.move_to(DOWN * 1.15)
            self.play(FadeIn(t1, shift=UP * 0.15), run_time=0.9)

            # "and that is what will make the argument checkable"
            self.at(7.54)
            t2 = T(r"$\Rightarrow$ exact identities and certified numbers", font_size=34,
                   color=GAP)
            t2.next_to(t1, DOWN, buff=0.55)
            self.play(FadeIn(t2, shift=DOWN * 0.15), run_time=0.9)

        # ============================================================ s05
        with self.voice("s05") as d:
            self.begin("s05", d)
            A = base_to(WeightBars([0.80, 0.06, 0.05, 0.04, 0.03, 0.02], width=3.9, height=2.4,
                                   color=FG), (-2.4, -1.25, 0))
            B = base_to(WeightBars([0.9, 0.1], width=1.7, height=2.4, color=FG),
                        (3.1, -1.25, 0))
            ro = []
            for wbx in (A, B):
                u0 = 1.0 - purity(wbx.probs)                 # 0.351, 0.180
                u1 = 1.0 - purity(squared(wbx.probs))        # 0.0275, 0.0241
                lab = MM(r"u=", font_size=36, color=DEFECT)
                n0 = DecimalNumber(u0, num_decimal_places=3, font_size=36, color=FG)
                arr = MM(r"\to", font_size=36, color=DIM)
                lab1 = MM(r"u'=", font_size=36, color=DEFECT)
                n1 = DecimalNumber(u0, num_decimal_places=3, font_size=36, color=DEFECT)
                g = VGroup(lab, n0, arr, lab1, n1).arrange(RIGHT, buff=0.15)
                g[3].shift(RIGHT * 0.05)
                g[4].next_to(g[3], RIGHT, buff=0.15)
                g.next_to(wbx.base, DOWN, buff=0.35).set_x(wbx.base.get_center()[0])
                dx = wbx.base.get_center()[0] - VGroup(lab, n0).get_center()[0]
                lab.shift(RIGHT * dx)
                n0.shift(RIGHT * dx)
                g.dx = dx
                ro.append((g, u1))
            # the bars grow while the s04 text leaves, then hold a beat
            self.play(FadeOut(Tc, Sc, evc, t1, t2, shift=UP * 0.3, run_time=0.35),
                      Succession(Wait(0.3), AnimationGroup(grow_bars(A), grow_bars(B)),
                                 run_time=1.05),
                      Succession(Wait(0.45), FadeIn(VGroup(*ro[0][0][0:2], *ro[1][0][0:2])),
                                 run_time=1.05))

            # squaring, step 1 (heights -> p^2), leaving outlines of the original bars
            self.at(1.6)
            ghA, ghB = ghost_outlines(A), ghost_outlines(B)
            tall_gh = VGroup(ghA[0], ghB[0])
            short_gh = VGroup(*ghA[1:], *ghB[1:])
            self.add(tall_gh, short_gh)
            sa1, sa2 = A.square()
            sb1, sb2 = B.square()
            self.play(sa1, sb1, run_time=self.until(2.35, lo=0.6))

            # "the tall bar grows" (above its outline)
            self.at(2.42)
            self.play(sa2, sb2, run_time=0.85)
            self.play(Indicate(A.bars[0], color=FG, scale_factor=1.06),
                      Indicate(B.bars[0], color=FG, scale_factor=1.06),
                      run_time=self.until(3.68, lo=0.35))

            # "the short ones collapse": their outlines fall onto the base, readouts drop
            self.at(3.72)
            flat = VGroup(*[g.copy().stretch_to_fit_height(0.02, about_edge=DOWN)
                            .set_stroke(DEFECT, opacity=1) for g in short_gh])
            self.play(*[FadeIn(g[2:], shift=LEFT * g.dx) for g, _ in ro],
                      *[ApplyMethod(m.shift, LEFT * g.dx) for g, _ in ro for m in g[0:2]],
                      short_gh.animate.set_stroke(DEFECT, opacity=1), run_time=0.35)
            self.play(*[ChangeDecimalToValue(g[4], u1) for g, u1 in ro],
                      Transform(short_gh, flat), run_time=self.until(4.95, lo=0.5))

            # "and a defect becomes at most roughly half its own square"
            self.at(5.11)
            lem = MM(r"u'", r"\ \le\ ", r"f(u)", r"=\frac{u^2}{2(1-u)^2}",
                     r"\ \approx\ \frac{u^2}{2}", font_size=40)
            lem[0].set_color(DEFECT)
            lem[2].set_color(DEFECT)
            lem.move_to(UP * 2.65 + RIGHT * 1.0)
            self.play(Write(lem[0:3]), FadeOut(short_gh), run_time=1.0)
            self.play(Write(lem[3:]), run_time=1.3)

            # "however many bars there are"
            self.at(8.4)
            anyn = T(r"\textit{any number of bars}", font_size=28, color=DIM)
            anyn.next_to(lem, DOWN, buff=0.25)
            eq = T(r"two bars: equality", font_size=28, color=DIM)
            eq.next_to(ro[1][0], DOWN, buff=0.3)
            self.play(FadeIn(anyn, shift=UP * 0.1), FadeIn(eq), run_time=0.8)

        # ============================================================ s06
        with self.voice("s06") as d:
            self.begin("s06", d)
            self.play(FadeOut(A, B, tall_gh, *[g for g, _ in ro], lem, anyn, eq), run_time=0.5)
            # schematic Gibbs weights, one bar per eigenstate: E0, the threefold E1 (three
            # equal bars), then a higher level.  T = 0.513 > 1/2, max = 0.70 > 1/2.
            W = base_to(WeightBars([0.70, 0.08, 0.08, 0.08, 0.06], width=4.4, height=2.6,
                                   color=TIME), (-3.4, -1.25, 0))
            sch6 = inline_tag(TAG_SCHEMATIC, W.base, RIGHT, buff=0.3)
            self.play(grow_bars(W), FadeIn(sch6), run_time=0.9)

            # "If the thermal purity is above one half"
            self.at(1.65)
            half = W.level_line(0.5, label=r"\tfrac{1}{2}", font_size=44)
            fa = MM(r"\max_k w_k", r"\ \ge\ ", r"\sum_k w_k^{\,2}=T", r">\tfrac12",
                    font_size=40)
            fa[2].set_color(TIME)
            fa.move_to([-3.4, -2.6, 0])
            self.play(Create(half[0]), FadeIn(half[1]), Write(fa[2:]), run_time=1.3)

            # "so is the largest Gibbs weight"
            self.at(3.93)
            self.play(Write(fa[0:2]), Indicate(W.bars[0], color=FG, scale_factor=1.05),
                      run_time=1.2)

            # "and the ground state is unique"
            self.at(5.76)
            uq = T("unique ground state", font_size=30, color=GAP)
            uq.next_to(W.bars[0], UP, buff=0.2).align_to(W.bars[0], LEFT).shift(LEFT * 0.1)
            self.play(FadeIn(uq, shift=UP * 0.1), run_time=0.7)

            # "two copies would each need more than half"
            self.at(7.65)
            ghost = W.bars[0].copy().set_z_index(1)
            self.add(ghost)
            self.play(ghost.animate.move_to(W.bars[1], aligned_edge=DOWN).set_fill(DEFECT),
                      W.bars[0].animate.set_fill(DEFECT),
                      *[b.animate.set_fill(opacity=0.15) for b in W.bars[1:]], run_time=0.9)
            cx = cross_mark(size=0.45).move_to(ghost.get_center() + UP * 0.25).set_z_index(2)
            tot = T(r"total $>1$", font_size=30, color=SX).next_to(ghost, RIGHT, buff=0.25)
            tot.align_to(ghost, UP)
            self.play(Create(cx), FadeIn(tot), run_time=0.7)

            # "The excited level's relative weight"
            self.at(10.21)
            lv = level_diagram([0, 1.0], width=1.7, color=TIME, yscale=1.5)
            lv.move_to([2.6, -0.45, 0])
            e0 = M("E_0", font_size=34).next_to(lv[0], LEFT, buff=0.2)
            e1 = M("E_1", font_size=34).next_to(lv[1], LEFT, buff=0.2)
            x3 = M(r"\times3", font_size=28, color=DIM).next_to(lv[1], UP, buff=0.12)
            w0 = M("w_0", font_size=34, color=TIME).next_to(W.base, DOWN, buff=0.15)
            w0.set_x(W.bars[0].get_center()[0])
            w1 = M("w_1", font_size=34, color=TIME).next_to(W.base, DOWN, buff=0.15)
            w1.set_x(W.bars[1].get_center()[0])
            fb = MM(r"{w_1", r"\over", r"w_0}", r"=e^{-\beta\gamma_L}", r"\ \le\ ",
                    r"{1-w_0", r"\over", r"w_0}", font_size=40)
            fb.move_to([2.95, -2.6, 0])
            self.play(FadeOut(ghost, cx, tot), W.bars[0].animate.set_fill(TIME),
                      *[b.animate.set_fill(opacity=0.9) for b in W.bars[1:]], run_time=0.4)
            self.play(Create(lv), FadeIn(e0, e1, x3), FadeIn(w0, w1), Write(fb[0:3]),
                      run_time=1.3)

            # "e to the minus beta times the gap"
            self.at(12.18)
            gb = gap_brace(lv[0], lv[1], label=r"\gamma_L")
            self.play(GrowFromCenter(gb[0]), Write(gb[1]), Write(fb[3]), run_time=1.2)

            # "is at most the leftover over the ground weight"
            self.at(14.24)
            br6 = W.defect_brace(M(r"1-w_0", color=DEFECT, font_size=34))
            self.play(Write(fb[4:]), GrowFromCenter(br6[0]), FadeIn(br6[1], shift=UP * 0.1),
                      run_time=1.4)

            # "Small defect, small ratio: a gap."
            self.at(17.04)
            self.play(Indicate(br6[1], color=DEFECT, scale_factor=1.25),
                      Indicate(fb[5:], color=DEFECT, scale_factor=1.15), run_time=1.0)
            self.play(Indicate(fb[0:4], color=FG, scale_factor=1.1), run_time=0.9)
            self.at(19.35)
            self.play(Indicate(gb, color=GAP, scale_factor=1.25), run_time=0.8)

        # ============================================================ s07
        with self.voice("s07") as d:
            self.begin("s07", d)
            W.brace = None
            self.play(FadeOut(W, half, fa, uq, lv, e0, e1, x3, w0, w1, fb, gb, br6, sch6),
                      run_time=0.45)

            # "Here a skeptic jumps in"
            bA = objection_bubble("finite")
            self.play(bubble_in(bA), run_time=0.8)

            # "at any fixed length"
            self.at(2.02)
            Y0 = 14.5                                  # plotted y = log10(1-T) + Y0
            ax = Axes(x_range=[0, 40, 10], y_range=[0, Y0, 1], x_length=7.6, y_length=4.3,
                      tips=False,
                      axis_config={"color": DIM, "stroke_width": 2, "include_ticks": False})
            ax.shift(np.array([-3.85, -2.55, 0]) - ax.c2p(0, 0))

            def lp(b, v):
                return ax.c2p(b, np.log10(v) + Y0)

            xt = VGroup()
            for v in (0, 10, 20, 30, 40):
                p = ax.c2p(v, 0)
                xt.add(Line(p + DOWN * 0.06, p + UP * 0.06, color=DIM, stroke_width=2))
                xt.add(M(str(v), font_size=24, color=DIM).next_to(p, DOWN, buff=0.15))
            yt = VGroup()
            for k in (0, -4, -8, -12):
                p = ax.c2p(0, k + Y0)
                yt.add(Line(p + LEFT * 0.06, p + RIGHT * 0.06, color=DIM, stroke_width=2))
                yt.add(M(r"10^{%d}" % k, font_size=24, color=DIM).next_to(p, LEFT, buff=0.15))
            xl = M(r"\beta", font_size=36, color=TIME).next_to(ax.c2p(40, 0), RIGHT, buff=0.2)
            yl = M(r"1-T(L,\beta)", font_size=32, color=TIME).rotate(PI / 2)
            yl.move_to([yt.get_left()[0] - 0.4, ax.c2p(0, Y0 / 2)[1], 0])
            self.play(Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xl), FadeIn(yl),
                      run_time=self.until(3.1, lo=0.6))

            def curve(S, L, dashed):
                data = load_thermal(S, L)
                col = INTEGER if S == 1.0 else HALF
                pts = [lp(b, v) for b, v in data]
                ln = VMobject(stroke_color=col, stroke_width=3.5)
                ln.set_points_as_corners(pts)
                if dashed:
                    ln = DashedVMobject(ln, num_dashes=40, dashed_ratio=0.55)
                seg = np.linalg.norm(np.diff(np.array(pts), axis=0), axis=1)
                arc = np.concatenate([[0.0], np.cumsum(seg)]) / seg.sum()
                mk, fr = VGroup(), []
                for i, (b, v) in enumerate(data):
                    if b > 0 and abs(b / 4 - round(b / 4)) < 1e-9:
                        p = lp(b, v)
                        mk.add(spin1_marker(p) if S == 1.0 else spinhalf_marker(p))
                        fr.append(arc[i] if dashed else i / (len(pts) - 1))
                end = pts[-1]
                return ln, mk, end, data, reveal_markers(mk, fr, hollow=(S == 1.0))

            c1 = curve(1.0, 4, False)
            c2 = curve(1.0, 12, True)
            c3 = curve(0.5, 8, False)
            c4 = curve(0.5, 18, True)
            b26 = min(c1[3], key=lambda r: abs(r[0] - 26.0))
            lab_c1 = T(r"spin 1, $L=4$", font_size=28, color=INTEGER).next_to(
                lp(*b26), RIGHT, buff=0.3).shift(UP * 0.2)
            lab_c2 = T(r"spin 1, $L=12$", font_size=28, color=INTEGER).next_to(
                c2[2], RIGHT, buff=0.2).shift(UP * 0.14)
            lab_c3 = T(r"spin $\tfrac12$, $L=8$", font_size=28, color=HALF).next_to(
                c3[2], RIGHT, buff=0.2).shift(DOWN * 0.14)
            lab_c4 = T(r"spin $\tfrac12$, $L=18$", font_size=28, color=HALF).next_to(
                c4[2], RIGHT, buff=0.2)

            # "purity goes to one as beta grows"
            self.at(3.15)
            self.play(Create(c1[0]), Create(c2[0]),
                      c1[4], c2[4],
                      run_time=1.5, rate_func=linear)
            self.play(FadeIn(lab_c1), FadeIn(lab_c2), run_time=0.4)

            # "for spin one and spin one-half alike"
            self.at(5.19)
            self.play(Create(c3[0]), Create(c4[0]),
                      c3[4], c4[4],
                      run_time=1.4, rate_func=linear)
            cap7 = caption(r"fixed $L$: purity $\to1$, gapped or not")
            self.play(FadeIn(lab_c3), FadeIn(lab_c4), FadeIn(cap7, shift=UP * 0.1),
                      run_time=self.until(7.6, lo=0.4))

            # "The first objection, in a new costume."
            self.at(7.79)
            self.play(bubble_indicate(bA), run_time=0.8)
            bD = objection_bubble("beta")
            self.play(bubble_out(bA), run_time=0.35)
            self.play(bubble_in(bD), run_time=self.until(9.75, lo=0.5))

        # ============================================================ s08
        with self.voice("s08") as d:
            self.begin("s08", d)
            plot7 = VGroup(ax, xt, yt, xl, yl, *c1[:2], *c2[:2], *c3[:2], *c4[:2],
                           lab_c1, lab_c2, lab_c3, lab_c4, cap7)
            self.play(FadeOut(plot7), run_time=0.5)
            st = Staircase("bare", x_length=4.9, y_length=2.85)
            st.shift(np.array([-5.45, -2.5, 0]) - st.pt(0, 0))
            self.play(FadeIn(st), run_time=0.5)

            # "But suppose beta doubles each step while the defect squares."
            dots = VGroup(*[Dot(st.pt(k, k), radius=0.08, color=DEFECT) for k in range(1, 5)])
            texs = ["u", "u^2", "u^4", "u^8"]
            dl = VGroup(*[M(t, font_size=34, color=DEFECT).next_to(dt, DR, buff=0.08)
                          for t, dt in zip(texs, dots)])
            self.play(LaggedStart(*[AnimationGroup(GrowFromCenter(dt), FadeIn(lb))
                                    for dt, lb in zip(dots, dl)], lag_ratio=0.55),
                      run_time=self.until(3.4, lo=1.0))

            # "Then the defect falls exponentially in beta"
            self.at(4.06)
            ia = Axes(x_range=[0, 8.8, 1], y_range=[-8.8, 0, 1], x_length=4.2, y_length=3.2,
                      tips=False,
                      axis_config={"color": DIM, "stroke_width": 2, "include_ticks": False})
            ia.shift(np.array([1.55, 1.3, 0]) - ia.c2p(0, 0))
            itx = VGroup()
            for v, s in zip((1, 2, 4, 8), (r"\beta", r"2\beta", r"4\beta", r"8\beta")):
                p = ia.c2p(v, 0)
                itx.add(Line(p + DOWN * 0.06, p + UP * 0.06, color=DIM, stroke_width=2))
                itx.add(M(s, font_size=28, color=TIME).next_to(p, UP, buff=0.12))
            ity = VGroup()
            for v, s in zip((1, 2, 4, 8), texs):
                p = ia.c2p(0, -v)
                ity.add(Line(p + LEFT * 0.06, p + RIGHT * 0.06, color=DIM, stroke_width=2))
                ity.add(M(s, font_size=28, color=DEFECT).next_to(p, LEFT, buff=0.12))
            iyl = T(r"defect (log scale)", font_size=28, color=DEFECT)
            iyl.next_to(ia.c2p(0, -8.8), RIGHT, buff=0.2)
            ipts = VGroup(*[Dot(ia.c2p(v, -v), radius=0.07, color=DEFECT) for v in (1, 2, 4, 8)])
            self.play(Create(ia), FadeIn(itx), FadeIn(ity), FadeIn(iyl), run_time=0.8)
            self.play(LaggedStart(*[TransformFromCopy(a, b) for a, b in zip(dots, ipts)],
                                  lag_ratio=0.2), run_time=1.3)

            # "at a fixed rate"
            self.at(6.86)
            iline = DashedLine(ia.c2p(0, 0), ia.c2p(8.7, -8.7), color=FG, stroke_width=2.5,
                               dash_length=0.1)
            # label laid along the dashed line, just above it
            dvec = ia.c2p(1, -1) - ia.c2p(0, 0)
            dvec = dvec / np.linalg.norm(dvec)
            nvec = np.array([-dvec[1], dvec[0], 0.0])           # normal, pointing up-right
            rate = T("fixed rate", font_size=28, color=FG)
            rate.rotate(np.arctan2(dvec[1], dvec[0]))
            rate.move_to(ia.c2p(5.7, -5.7) + nvec * 0.3)
            self.play(Create(iline), FadeIn(rate), run_time=0.9)

            # "and that rate is a gap at every length along the way"
            self.at(8.06)
            gtx = M(r"\gamma_L\ \ge\ \text{rate}", font_size=36, color=GAP)
            gtx.next_to(ia.c2p(8.8, -8.8), DOWN, buff=0.4).align_to(iline, RIGHT)
            self.play(Write(gtx), run_time=0.8)
            self.play(LaggedStart(*[Indicate(dt, color=GAP, scale_factor=1.8) for dt in dots],
                                  lag_ratio=0.3), run_time=self.until(10.7, lo=0.8))

            # "So that is the target: length and beta doubling together."
            self.at(11.27)
            tgt = T(r"target: $L$ and $\beta$ double together;\ \ $u\to\ \sim u^2$",
                    font_size=34)
            box = SurroundingRectangle(tgt, color=FG, stroke_width=2, buff=0.2,
                                       corner_radius=0.1)
            tg = VGroup(box, tgt).move_to(DOWN * 3.28 + RIGHT * 0.9)
            self.play(FadeIn(tgt), Create(box), run_time=0.9)
            self.at(12.77)
            ray = Arrow(st.pt(0.4, 0.4), st.pt(4.8, 4.8), buff=0, color=FG, stroke_width=4,
                        max_tip_length_to_length_ratio=0.06)
            ray.set_z_index(-1)
            self.play(GrowArrow(ray), thumb._double(2, 2), run_time=1.4)

        self.play(FadeOut(*self.mobjects), run_time=0.8)
