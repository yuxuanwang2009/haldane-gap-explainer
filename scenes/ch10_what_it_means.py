"""ch10: What it means.

Scope (claimed / not claimed), why the bound is small, what is new,
certification vs explanation, status and the computer's part, the AI angle,
a recap on the torus, and the closing callback: a floor under the ch01 plot.

Sentence cues inside each segment come from pauses in the narration clips
(ffmpeg silencedetect on audio/ch10/sNN.wav), so reveals land on the words.
"""
import os
import sys
from contextlib import contextmanager

from motifs import *  # noqa: F401,F403  (also visuals.*, common.*)
import ch02_haldane_picture as ch02   # PhasorRow / row_label (module import: no Ch02 scene here)

# Chapters are rendered in parallel into one media dir; manim's LaTeX cleanup in one
# process can delete another's in-flight .dvi.  A private Tex dir avoids that race.
config.tex_dir = str(Path(config.media_dir) / "Tex_ch10")


# =================================================================== small helpers
def color_glyphs(m, mapping):
    """Colour single glyphs of a one-string MathTex by index: {index: color}."""
    g = m[0]
    for i, c in mapping.items():
        g[i].set_color(c)
    return m


def item_rows(rows, line_buff=0.15):
    """rows: list of (tex, color, font_size).  Left-aligned stack."""
    g = VGroup(*[T(s, font_size=fs, color=c) for s, c, fs in rows])
    g.arrange(DOWN, aligned_edge=LEFT, buff=line_buff)
    return g


def bullet(icon, rows, x_icon, top):
    """Icon at x_icon, text block to its right, first line's centre level with the icon."""
    rows.move_to([x_icon + 0.42, top, 0], aligned_edge=UL)
    icon.move_to([x_icon, rows[0].get_center()[1], 0])
    return VGroup(icon, rows)


def pbox(lines, width, color=FG, fs=28, min_h=0.0, fill=0.06):
    """Pipeline box: rounded rectangle with centred text lines [(tex, color)];
    DIM lines are set 2 pt smaller."""
    txt = VGroup(*[T(s, font_size=fs - (2 if c == DIM else 0), color=c) for s, c in lines]
                 ).arrange(DOWN, buff=0.1)
    h = max(min_h, txt.height + 0.32)
    box = RoundedRectangle(width=width, height=h, corner_radius=0.12, stroke_color=color,
                           stroke_width=2, fill_color=color, fill_opacity=fill)
    txt.move_to(box)
    g = VGroup(box, txt)
    g.box, g.txt = box, txt
    return g


def term_line(cols, xs, fs=28, color=FG, right=(2,)):
    """One terminal line: texttt columns at fixed x offsets.  Columns in `right`
    are right-aligned at their x (so '18 traces' and '9 traces' line up)."""
    g = VGroup()
    for k, (s, x) in enumerate(zip(cols, xs)):
        if not s:
            continue
        c = GAP if s == "PASS" else color
        m = T(r"\texttt{" + s + "}" if "$" not in s else s, font_size=fs, color=c)
        m.move_to([x, 0, 0], aligned_edge=RIGHT if k in right else LEFT)
        g.add(m)
    return g


def highlight_bar(mob, pad_x=0.25, pad_y=0.1):
    """Soft FAINT bar behind a line of text (focus marker)."""
    r = RoundedRectangle(width=mob.width + 2 * pad_x, height=mob.height + 2 * pad_y,
                         corner_radius=0.08, stroke_width=0, fill_color=FAINT, fill_opacity=0.7)
    r.move_to(mob)
    r.set_z_index(-2)
    return r


# =================================================================== the chapter
class Ch10(NarratedScene):
    CHAPTER = "ch10"

    # ---------------------------------------------------------- sync helpers
    @contextmanager
    def seg(self, sid, breath=None):
        with self.voice(sid, breath=breath) as d:
            self._t0 = self.renderer.time
            yield d
            if os.environ.get("CH10_CHECK"):
                self._check_safe_area(sid)

    def _check_safe_area(self, sid, xmax=6.7, ymax=3.7):
        """Debug aid (CH10_CHECK=1): report visible parts outside the safe area."""
        for top in self.mobjects:
            for m in top.get_family():
                if not m.has_points():
                    continue
                if max(m.get_stroke_opacity(), m.get_fill_opacity()) < 0.05:
                    continue
                l, r = m.get_left()[0], m.get_right()[0]
                b, t = m.get_bottom()[1], m.get_top()[1]
                if l < -xmax - 1e-3 or r > xmax + 1e-3 or b < -ymax - 1e-3 or t > ymax + 1e-3:
                    print(f"[safe-area] {sid}: {type(m).__name__} x[{l:.2f},{r:.2f}] "
                          f"y[{b:.2f},{t:.2f}]", file=sys.stderr)

    def cue(self, t):
        """Wait until t seconds after the start of the current segment."""
        dt = self._t0 + t - self.renderer.time
        if dt > 0.04:
            self.wait(dt)

    def fade_all(self, run_time=0.6, keep=()):
        mobs = [m for m in self.mobjects if m not in keep]
        if mobs:
            self.play(FadeOut(*mobs), run_time=run_time)

    # ---------------------------------------------------------- construct
    def construct(self):
        self.s01_s02_scope()
        self.s03_why_small()
        self.s04_tool()
        self.s05_not_explanation()
        self.s06_status()
        self.s07_computations()
        self.s08_ai()
        self.s09_recap()
        self.s10_floor()

    # ================================================================ s01 + s02
    def s01_s02_scope(self):
        xL, xR = -6.2, 0.6
        sub = T(r"spin-1 Heisenberg chain", font_size=30, color=DIM).move_to([0, 3.3, 0])
        hL = T("claimed", font_size=40, color=GAP).move_to([-3.35, 2.55, 0])
        hR = T("not claimed", font_size=40, color=DIM).move_to([3.45, 2.55, 0])
        rule = Line([-6.4, 2.1, 0], [6.4, 2.1, 0], color=FAINT, stroke_width=2)
        divider = Line([0.15, 1.9, 0], [0.15, -3.35, 0], color=FAINT, stroke_width=2)

        # left column: claimed
        L1 = bullet(check_mark(0.34), item_rows([
            (r"even rings, $L\ge60$", FG, 30),
            (r"uniform gap $>4.79\times10^{-4}$", FG, 30),
            (r"($>3.82\times10^{-3}$ for $L\ge2304$)", FG, 30),
            (r"unique ground state: classical", DIM, 26),
        ]), xL, 1.6)
        L2 = bullet(check_mark(0.34), item_rows([
            (r"odd open chains, $\ge1921$ sites,", FG, 30),
            (r"end fields $h=\tfrac35$", FG, 30),
            (r"uniform gap $>5.87\times10^{-3}$", FG, 30),
            (r"index $-1$ for every", FG, 30),
            (r"boundary-selected subsequential limit", FG, 30),
        ]), xL, L1.get_bottom()[1] - 0.6)

        # right column: not claimed
        gapR = 0.5
        R1 = bullet(open_circle(), item_rows([
            (r"the value of the gap", FG, 30),
            (r"bounds $\gtrsim\!100\times$ below $0.41$ \textit{(literature)}", DIM, 26),
        ]), xR, 1.6)
        R2 = bullet(open_circle(), item_rows([(r"odd periodic rings", FG, 30)]),
                    xR, R1.get_bottom()[1] - gapR)
        R3 = bullet(open_circle(), item_rows([(r"unique infinite-volume ground state", FG, 30)]),
                    xR, R2.get_bottom()[1] - gapR)
        R4 = bullet(open_circle(), item_rows([
            (r"spin $\ge2$", FG, 30),
            (r"spin 2: $\xi\approx49.5$ sites \textit{(literature)}", DIM, 26),
        ]), xR, R3.get_bottom()[1] - gapR)
        guess = tag_box("difficulty: our guess").next_to(R4[1], DOWN, buff=0.25).align_to(
            R4[1], LEFT)

        def show_rows(it, idx, rt):
            icon, rows = it
            anims = [FadeIn(rows[i], shift=0.12 * RIGHT) for i in idx]
            if 0 in idx:
                anims.insert(0, GrowFromCenter(icon) if isinstance(icon, Circle) else Create(icon))
            self.play(LaggedStart(*anims, lag_ratio=0.25), run_time=rt)

        # ---------------- s01
        with self.seg("s01"):
            self.play(FadeIn(hL, shift=0.15 * DOWN), Create(rule), Create(divider),
                      run_time=1.0)
            self.cue(2.5)                                     # "...the spin one Heisenberg chain"
            self.play(FadeIn(sub), run_time=0.8)
            self.cue(4.4)                                     # "on even rings from 60 sites on"
            show_rows(L1, [0], 0.8)
            self.play(LaggedStart(*[FadeIn(L1[1][i], shift=0.12 * RIGHT) for i in (1, 2, 3)],
                                  lag_ratio=0.35), run_time=1.3)
            self.cue(7.15)                                    # "and for long odd open chains..."
            show_rows(L2, [0, 1], 1.2)
            self.cue(11.05)                                   # "a uniform gap"
            show_rows(L2, [2], 0.6)
            self.cue(12.3)                                    # "and index minus one for every limit"
            show_rows(L2, [3, 4], 1.1)

        # ---------------- s02
        with self.seg("s02"):
            self.play(FadeIn(hR, shift=0.15 * DOWN), run_time=0.6)
            self.cue(1.45)                                    # "the gap's value"
            show_rows(R1, [0, 1], 0.9)
            self.cue(2.55)                                    # "odd periodic rings"
            show_rows(R2, [0], 0.6)
            self.cue(4.15)                                    # "uniqueness of the infinite-volume state"
            show_rows(R3, [0], 0.7)
            self.cue(6.5)                                     # "or spin two and beyond"
            show_rows(R4, [0], 0.6)
            self.cue(8.4)                                     # "where we suspect ... out of reach"
            self.play(FadeIn(R4[1][1], shift=0.12 * RIGHT), run_time=0.7)
            self.play(tag_in(guess), run_time=0.6)

        self._card = dict(R1=R1)

    # ================================================================ s03
    def s03_why_small(self):
        R1 = self._card["R1"]
        src = R1[1][1]                                       # "bounds >~100x below 0.41 (literature)"
        header = T(r"bounds $\gtrsim\!100\times$ below $0.41$ \textit{(literature)}",
                   font_size=34, color=FG).move_to([0, 3.2, 0])

        rowA = M(r"u\;\longrightarrow\;u^{2},\qquad \beta\;\longrightarrow\;2\beta", font_size=44)
        # glyphs: u | --> (2 glyphs) | u 2 , | beta | --> (2) | 2 beta
        color_glyphs(rowA, {0: DEFECT, 3: DEFECT, 4: DEFECT, 6: TIME, 9: TIME, 10: TIME})
        rowA.move_to([0.35, 1.85, 0])
        labA = T("one doubling", font_size=28, color=DIM)
        labA.next_to(rowA, LEFT, buff=0.6)

        rowB = M(r"\frac{-\log u}{\beta}\;\longrightarrow\;\frac{-\log u^{2}}{2\beta}"
                 r"\;=\;\frac{-\log u}{\beta}", font_size=44)
        color_glyphs(rowB, {4: DEFECT, 6: TIME, 13: DEFECT, 14: DEFECT, 16: TIME, 17: TIME,
                            23: DEFECT, 25: TIME})
        rowB.move_to([0.35, 0.55, 0])
        rate_lab = T("rate", font_size=28, color=DIM)
        rate_lab.next_to(rowB, LEFT, buff=0.6)
        labA.align_to(rate_lab, RIGHT)
        never = T(r"kept by doubling, never improved", font_size=28, color=DIM)
        never.next_to(rowB, DOWN, buff=0.3).set_x(rowB.get_x())

        beta_h = M(r"\beta=784", font_size=40, color=TIME).move_to([0, -1.25, 0])
        cert_t = T("certified", font_size=30, color=GAP).move_to([-2.7, -2.0, 0])
        cert_v = M(r"u<10^{-2}", font_size=48, color=GAP)
        cert_v[0][0].set_color(DEFECT)
        est_t = T("free-magnon estimate", font_size=30, color=DIM).move_to([2.7, -2.0, 0])
        est_v = M(r"u\sim e^{-300}", font_size=48, color=DIM)
        est_v[0][0].set_color(DEFECT)
        cert_v.move_to([-2.7, -2.85, 0])
        est_v.move_to([2.7, -2.85, 0])
        # common baseline for both values
        est_v.shift(UP * (cert_v[0][0].get_bottom()[1] - est_v[0][0].get_bottom()[1]))
        vs = T("vs", font_size=30, color=DIM)
        vs.move_to([0, 0, 0]).shift(UP * (cert_v[0][0].get_bottom()[1] - vs.get_bottom()[1]))
        cert = VGroup(cert_t, cert_v)
        est = VGroup(est_t, est_v)
        heur = tag(TAG_HEURISTIC, buff=0.42)          # keeps the box inside x <= 6.7

        with self.seg("s03"):
            others = [m for m in self.mobjects]
            src_copy = src.copy()
            self.add(src_copy)
            self.play(FadeOut(*others), ReplacementTransform(src_copy, header), run_time=1.2)
            self.cue(3.15)                                    # "Doubling preserves the rate..."
            self.play(Write(rowA), FadeIn(labA), run_time=1.0)
            self.play(FadeIn(rowB, shift=0.1 * DOWN), FadeIn(rate_lab), run_time=1.0)
            self.cue(6.1)                                     # "but never improves it"
            self.play(FadeIn(never, shift=0.1 * UP), run_time=0.7)
            self.cue(7.75)                                    # "a certified one percent at beta 784"
            self.play(FadeIn(beta_h), FadeIn(cert, shift=0.15 * UP), run_time=0.9)
            self.cue(11.3)                                    # "where a rough free-magnon estimate"
            self.play(FadeIn(vs), FadeIn(est, shift=0.15 * UP), tag_in(heur), run_time=0.9)
            self.cue(13.3)                                    # "...near e to the minus 300"
            self.play(Indicate(est_v, color=FG, scale_factor=1.1), run_time=1.0)

    # ================================================================ s04
    def s04_tool(self):
        new = T("what's new:", font_size=32, color=DIM)
        head = T("a finite-size gap criterion", font_size=42)
        hdr = VGroup(new, head).arrange(RIGHT, buff=0.3, aligned_edge=DOWN).move_to([0, 2.5, 0])

        y_icon, y_txt = 0.55, -0.3                     # icon centres / text tops (shared)
        it = icon_torus().scale(1.15)
        t1 = VGroup(T("two nonnegative", font_size=30), T(r"readings of $Z$", font_size=30)
                    ).arrange(DOWN, buff=0.1)
        ist = icon_staircase().scale(1.1)
        t2 = VGroup(T("a certified seed", font_size=30), T("in the basin", font_size=30)
                    ).arrange(DOWN, buff=0.1)
        cm = check_mark(0.5)
        t3 = VGroup(T("uniform", font_size=34, color=GAP), T("gap", font_size=34, color=GAP)
                    ).arrange(DOWN, buff=0.1)
        plus = M("+", font_size=48)
        imp = M(r"\Longrightarrow", font_size=48)
        xs = [-3.7, -1.85, 0.25, 2.25, 3.95]
        for (ic, tx), x in zip([(it, t1), (ist, t2), (cm, t3)], [xs[0], xs[2], xs[4]]):
            ic.move_to([x, y_icon, 0])
            tx.move_to([x, y_txt, 0], aligned_edge=UP)
        plus.move_to([xs[1], y_icon, 0])
        imp.move_to([xs[3], y_icon, 0])
        c1, c2, c3 = VGroup(it, t1), VGroup(ist, t2), VGroup(cm, t3)
        row = VGroup(c1, plus, c2, imp, c3)
        box = RoundedRectangle(width=row.width + 1.0, height=row.height + 0.75, corner_radius=0.2,
                               stroke_color=DIM, stroke_width=2).move_to(row)
        ff = VGroup(check_mark(0.3), T("frustration-freeness not required", font_size=30,
                                       color=DIM)).arrange(RIGHT, buff=0.22)
        ff.next_to(box, DOWN, buff=0.4)
        reuse = T(r"offered as reusable: other models with the same two readings",
                  font_size=28, color=DIM).next_to(ff, DOWN, buff=0.35)

        with self.seg("s04"):
            self.fade_all(0.6)
            self.play(FadeIn(new, shift=0.1 * DOWN), run_time=0.6)
            self.cue(1.95)                                    # "a finite-size gap criterion"
            self.play(FadeIn(head, shift=0.1 * DOWN), Create(box), run_time=0.8)
            self.play(LaggedStart(FadeIn(c1), FadeIn(plus), FadeIn(c2), FadeIn(imp),
                                  AnimationGroup(Create(cm), FadeIn(t3)), lag_ratio=0.3),
                      run_time=1.3)
            self.cue(4.1)                                     # "that does not need frustration-freeness"
            self.play(Create(ff[0]), FadeIn(ff[1], shift=0.1 * UP), run_time=0.7)
            self.cue(6.35)                                    # "offers as reusable ... same two readings"
            self.play(FadeIn(reuse, shift=0.1 * UP), run_time=0.8)
            self.cue(8.6)                                     # "...the same two readings"
            self.play(Circumscribe(c1, color=FG, buff=0.15, time_width=0.6), run_time=1.4)

    # ================================================================ s05
    def s05_not_explanation(self):
        div = Line([0, 1.2, 0], [0, -3.4, 0], color=FAINT, stroke_width=2)
        # left: certifies THAT (staircase climbs)
        hl = T(r"certifies \textit{that}", font_size=40, color=GAP).move_to([-3.4, 1.5, 0])
        cap = VGroup(check_mark(0.3), T(r"spin 1 is gapped", font_size=30),
                     T(r"\textit{(claimed)}", font_size=26, color=DIM))
        cap.arrange(RIGHT, buff=0.2)
        cap[2].shift(RIGHT * 0.05).align_to(cap[1], DOWN)
        cap.move_to([-3.4, 0.75, 0])
        st = Staircase("symbolic", x_length=4.4, y_length=2.7).move_to([-3.35, -1.45, 0])
        tr = st.tromino(0, 0)
        # right: explains WHY (theta term) -- the ch02 phasor rows, same helper
        hr = T(r"explains \textit{why}", font_size=40, color=FG).move_to([3.4, 1.5, 0])
        f = M(r"Z=\sum_{Q}e^{\,i\theta Q}\,Z_Q,\qquad \theta=2\pi S", font_size=36)
        f.move_to([3.4, 0.55, 0])
        x_lab, x_row, unit, dy = 0.5, 3.5, 1.25, 0.24
        y_half, y_int = -0.4, -2.05
        hrow = ch02.PhasorRow([1, -1, 1, -1], HALF, x0=x_row, y0=y_half, unit=unit, dy=dy)
        irow = ch02.PhasorRow([1, 1, 1, 1], INTEGER, x0=x_row, y0=y_int, unit=unit, dy=dy)
        hlab = ch02.row_label(r"half-integer $S$", r"\theta=\pi\ (\mathrm{mod}\ 2\pi)", HALF)
        ilab = ch02.row_label(r"integer $S$", r"\theta=0\ (\mathrm{mod}\ 2\pi)", INTEGER)
        hlab.move_to([x_lab, hrow.start_tick.get_top()[1], 0], aligned_edge=UL)
        ilab.move_to([x_lab, irow.start_tick.get_top()[1], 0], aligned_edge=UL)
        crit = T("cancel: critical", font_size=26, color=DIM)
        crit.next_to(hlab, DOWN, buff=0.18).align_to(hlab, LEFT)
        gapd = T("add up: gapped", font_size=26, color=DIM)
        gapd.next_to(ilab, DOWN, buff=0.18).align_to(ilab, LEFT)
        b = objection_bubble("theta")
        # phasors and sector weights are cartoons (as in ch02): tag the right panel
        sch = tag_box(TAG_SCHEMATIC).move_to([x_lab, b.shape.get_top()[1], 0], aligned_edge=UL)

        with self.seg("s05", breath=1.1):
            self.fade_all(0.6)
            self.play(bubble_in(b), run_time=0.7)
            self.cue(2.5)                                     # "It claims to certify that..."
            self.play(FadeIn(hl, shift=0.1 * DOWN), Create(div), FadeIn(st), run_time=0.6)
            self.play(FadeIn(tr), Create(cap[0]), FadeIn(cap[1]), FadeIn(cap[2]), run_time=0.5)
            self.play(tr.climb(1, trail=True), run_time=0.8)
            self.cue(5.1)                                     # "never why"
            self.play(FadeIn(hr, shift=0.1 * DOWN), bubble_indicate(b), Write(f), tag_in(sch),
                      run_time=0.9)
            self.cue(6.1)                                     # "the theta term is still the explanation"
            self.play(AnimationGroup(
                AnimationGroup(FadeIn(hlab, shift=0.1 * RIGHT, run_time=0.4),
                               hrow.build(run_time=1.0)),
                AnimationGroup(FadeIn(ilab, shift=0.1 * RIGHT, run_time=0.4),
                               irow.build(run_time=1.0)),
                lag_ratio=0.5), run_time=1.5)
            self.play(hrow.resolve(), irow.resolve(), FadeIn(crit), FadeIn(gapd), run_time=0.7)
            self.play(bubble_check(b), run_time=0.5)
        self._bubble = b
        self._s05_tag = sch

    # ================================================================ s06
    def s06_status(self):
        card = StatusCard()
        bar0 = highlight_bar(card.lines[0])
        bar_meta = highlight_bar(card.meta)
        bar1 = highlight_bar(card.lines[1])
        # pipeline -------------------------------------------------------
        xin, xbh, xcl = -4.45, 0.9, 4.88              # column centres
        w_in, w_bh, w_cl = 4.1, 2.9, 3.55
        r1_in = VGroup(
            pbox([(r"27 thermal traces", FG), (r"rings, $\le12$ sites", DIM)], w_in),
            pbox([(r"integer trial state", FG), (r"$L=72,\ 120$", DIM)], w_in),
        ).arrange(DOWN, buff=0.14)
        r2_in = VGroup(
            pbox([(r"15 thermal traces", FG), (r"open chains, 2--6 sites", DIM)], w_in),
            pbox([(r"integer trial states", FG), (r"same tensor, new end vectors", DIM)], w_in),
        ).arrange(DOWN, buff=0.14)
        r1_in.move_to([xin, 1.3, 0], aligned_edge=UP)
        r2_in.move_to([xin, r1_in.get_bottom()[1] - 0.6, 0], aligned_edge=UP)
        r1_bh = pbox([(r"analytic bootstrap", FG), (r"a few pages", DIM)], w_bh,
                     min_h=1.0).move_to([xbh, r1_in.get_center()[1], 0])
        r2_bh = pbox([(r"second bootstrap", FG)], w_bh,
                     min_h=1.0).move_to([xbh, r2_in.get_center()[1], 0])
        r1_cl = pbox([(r"every even $L\ge60$", FG), (r"uniform gap", GAP)], w_cl, color=GAP,
                     min_h=1.0).move_to([xcl, r1_in.get_center()[1], 0])
        r2_cl = pbox([(r"odd chains, $\ge1921$ sites,", FG), (r"$h=\tfrac35$: uniform gap", GAP)],
                     w_cl, color=GAP, min_h=1.0).move_to([xcl, r2_in.get_center()[1], 0])

        def arrow(a, b):
            return Arrow(a.get_right(), b.get_left(), buff=0.12, color=DIM, stroke_width=3,
                         tip_length=0.18, max_tip_length_to_length_ratio=0.5,
                         max_stroke_width_to_length_ratio=20)

        ar1a, ar2a = arrow(r1_in, r1_bh), arrow(r2_in, r2_bh)
        ar1b, ar2b = arrow(r1_bh, r1_cl), arrow(r2_bh, r2_cl)
        fin = VGroup(T("finitely many", font_size=24, color=DIM),
                     T("inequalities", font_size=24, color=DIM)).arrange(DOWN, buff=0.06)
        fin.move_to([(r1_in.get_right()[0] + r1_bh.get_left()[0]) / 2,
                     (r1_in.get_bottom()[1] + r2_in.get_top()[1]) / 2, 0])
        h_y = 1.85
        h_in = T("computer", font_size=30, color=DIM).move_to([xin, h_y, 0])
        h_bh = T("by hand", font_size=30, color=DIM).move_to([xbh, h_y, 0])
        h_cl = T("claim", font_size=30, color=GAP).move_to([xcl, h_y, 0])
        nb = objection_bubble("numerics")

        with self.seg("s06"):
            b = self._bubble
            self.play(bubble_out(b), run_time=0.4)
            self.fade_all(0.5)
            self.play(FadeIn(card), run_time=1.0)            # reprise: the whole card at once
            self.cue(1.5)                                     # "this is OpenAI's claimed proof"
            self.play(FadeIn(bar0), run_time=0.5)
            self.cue(3.85)                                    # "a preprint released on October 6, 2026"
            self.play(Transform(bar0, bar_meta), run_time=0.6)
            self.cue(7.3)                                     # "not yet independently refereed"
            self.play(Transform(bar0, highlight_bar(card.lines[0])), run_time=0.6)
            self.cue(9.65)                                    # "The analytic argument ... by hand"
            self.play(Transform(bar0, bar1), run_time=0.6)
            self.cue(11.9)
            self.play(FadeOut(card), FadeOut(bar0), run_time=0.6)
            self.play(FadeIn(h_bh), FadeIn(h_cl), FadeIn(r1_bh), FadeIn(r2_bh), GrowArrow(ar1b),
                      GrowArrow(ar2b), FadeIn(r1_cl), FadeIn(r2_cl), run_time=0.8)
            self.cue(13.0)                                    # "the computer only proves..."
            self.play(FadeIn(h_in), bubble_in(nb), run_time=0.7)
            self.cue(14.0)                                    # "finitely many inequalities"
            self.play(FadeIn(fin, shift=0.1 * RIGHT), run_time=0.6)
            self.cue(16.3)                                    # "about thermal traces of rings and chains"
            self.play(LaggedStart(
                AnimationGroup(FadeIn(r1_in[0], shift=0.15 * RIGHT),
                               GrowArrow(ar1a, rate_func=squish_rate_func(smooth, 0.4, 1.0))),
                AnimationGroup(FadeIn(r2_in[0], shift=0.15 * RIGHT),
                               GrowArrow(ar2a, rate_func=squish_rate_func(smooth, 0.4, 1.0))),
                lag_ratio=0.45), run_time=1.4)
            self.cue(20.1)                                    # "and a few integer trial states"
            self.play(LaggedStart(FadeIn(r1_in[1], shift=0.15 * RIGHT),
                                  FadeIn(r2_in[1], shift=0.15 * RIGHT), lag_ratio=0.5),
                      run_time=1.0)
            self.play(bubble_check(nb), run_time=0.6)
        self._bubble = nb

    # ================================================================ s07
    def s07_computations(self):
        # left: what was published
        pub = VGroup(T("published", font_size=32), T("with the paper", font_size=32)
                     ).arrange(DOWN, buff=0.1)
        cpu_n = M(r"\approx40", font_size=56)
        cpu_t = T("CPU-minutes", font_size=30)
        cpu = VGroup(cpu_n, cpu_t).arrange(DOWN, buff=0.15)
        blk = VGroup(T("matrices up to", font_size=26, color=DIM),
                     T(r"dimension 73{,}789", font_size=26, color=DIM)).arrange(DOWN, buff=0.08)
        left = VGroup(pub, cpu, blk).arrange(DOWN, buff=0.55).move_to([-4.55, 0.3, 0])

        # right: terminal-style replay box (plain monospace, no brand UI)
        x0 = -2.2
        w18 = T(r"\texttt{18 traces}", font_size=28).width
        xs = [x0 + 0.35, x0 + 3.65, x0 + 5.35 + w18, x0 + 7.4]   # col 2: right edge
        rows = [
            ["thermal", r"$\beta=49/4$", "18 traces", "PASS"],
            ["thermal", r"$\beta=21/2$", "9 traces", "PASS"],
            ["trial state", r"$L=72$", "", "PASS"],
            ["trial state", r"$L=120$", "", "PASS"],
            ["boundary thermal", "", "15 traces", "PASS"],
            ["boundary trials", "", "4 states", "PASS"],
        ]
        pitch, y_top = 0.52, 1.95
        lines = VGroup()
        for i, r in enumerate(rows):
            ln = term_line(r, xs)
            ln.shift(UP * (y_top - i * pitch - ln[0].get_top()[1]))   # fixed pitch, cap-aligned
            lines.add(ln)
        head = T(r"\texttt{re-run for this video}", font_size=26, color=DIM)
        head.move_to([xs[0], y_top + 0.62, 0], aligned_edge=LEFT)
        sep = Line([x0 + 0.3, 0, 0], [x0 + 8.4, 0, 0], color=FAINT, stroke_width=2)
        sep.set_y(lines.get_bottom()[1] - 0.3)
        wall = T(r"\texttt{about 20 min wall clock, laptop}", font_size=28, color=FG)
        wall.next_to(sep, DOWN, buff=0.3).align_to(lines, LEFT)
        frame = RoundedRectangle(width=8.75, height=VGroup(head, wall).height + 0.75,
                                 corner_radius=0.15, stroke_color=DIM, stroke_width=2,
                                 fill_color=FAINT, fill_opacity=0.25)
        frame.move_to(VGroup(head, wall)).set_x(x0 + 8.75 / 2)
        match = VGroup(check_mark(0.36), T("every certified number matched", font_size=30,
                                           color=GAP)).arrange(RIGHT, buff=0.25)
        match.next_to(frame, DOWN, buff=0.4)

        with self.seg("s07"):
            self.play(bubble_out(self._bubble), run_time=0.4)
            self.fade_all(0.5)
            self.play(FadeIn(pub, shift=0.1 * UP), run_time=0.7)
            self.cue(3.05)                                    # "about forty minutes of processor time"
            self.play(FadeIn(cpu, shift=0.1 * UP), run_time=0.7)
            self.play(FadeIn(blk), run_time=0.6)
            self.cue(5.7)                                     # "For this video we re-ran them..."
            self.play(FadeIn(frame), FadeIn(head), run_time=0.5)
            for ln in lines:
                self.play(FadeIn(ln[:-1], shift=0.08 * RIGHT), run_time=0.22)
                self.play(FadeIn(ln[-1]), run_time=0.15)
            self.cue(8.5)                                     # "in about twenty minutes"
            self.play(Create(sep), FadeIn(wall), run_time=0.6)
            self.cue(9.85)                                    # "and every certified number matched"
            self.play(Create(match[0]), FadeIn(match[1], shift=0.1 * RIGHT), run_time=0.8)

    # ================================================================ s08
    def s08_ai(self):
        au = T(r"author: OpenAI", font_size=48).move_to([0, 0.55, 0])
        no = T(r"no human author named", font_size=32, color=DIM).next_to(au, DOWN, buff=0.35)
        top = T(r"author: OpenAI $\cdot$ no human author named", font_size=28, color=DIM)
        top.move_to([0, 3.25, 0])

        tor = Torus(4.6, 2.8, nx=10, ny=6)
        tor.shift(np.array([-3.1, -0.35, 0]) - tor.rect.get_center())
        hk = time_knife(tor, at=0.15)
        vk = space_knife(tor, bond=0)
        ck1 = VGroup(check_mark(0.38), T("checkable", font_size=36)).arrange(RIGHT, buff=0.3)
        ck2 = VGroup(check_mark(0.38), T("fits in your head", font_size=36)).arrange(RIGHT,
                                                                                   buff=0.3)
        cks = VGroup(ck1, ck2).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to([3.3, -0.35, 0])

        with self.seg("s08"):
            self.fade_all(0.5)                                # "As for the AI:"
            self.play(FadeIn(au, shift=0.1 * UP), run_time=0.8)
            self.cue(4.3)                                     # "with no human author named"
            self.play(FadeIn(no), run_time=0.8)
            self.cue(6.5)                                     # "For a skeptic"
            self.play(ReplacementTransform(VGroup(au, no), top), run_time=1.0)
            self.cue(9.2)                                     # "...the argument is checkable"
            self.play(Create(ck1[0]), FadeIn(ck1[1], shift=0.1 * RIGHT), run_time=0.7)
            self.cue(10.25)                                   # "and its central idea fits in your head"
            self.play(FadeIn(tor), FadeIn(hk), FadeIn(vk), Create(ck2[0]),
                      FadeIn(ck2[1], shift=0.1 * RIGHT), run_time=1.2)
        self._s08 = dict(tor=tor, hk=hk, vk=vk, top=top, cks=cks)

    # ================================================================ s09
    def s09_recap(self):
        S = self._s08
        tor, hk, vk = S["tor"], S["hk"], S["vk"]
        xb = 3.55
        gb = WeightBars([0.6, 0.15, 0.1, 0.08, 0.07], width=3.0, height=1.6, color=TIME,
                        highlight_color=TIME)
        gb.shift(np.array([xb, 1.0, 0]) - gb.base.get_center())
        gcap = gb.caption(r"e^{-\beta E_k}", font_size=34, buff=0.2)
        glab = T("Gibbs weights", font_size=30, color=TIME).move_to([xb, 2.95, 0])
        sb = WeightBars([0.55, 0.17, 0.12, 0.09, 0.07], width=3.0, height=1.6, color=SPACE,
                        highlight_color=SPACE)
        sb.shift(np.array([xb, -2.55, 0]) - sb.base.get_center())
        scap = sb.caption(r"|\lambda_i|^{L}", font_size=34, buff=0.2)
        slab = T("spatial weights", font_size=30, color=SPACE).move_to([xb, -0.55, 0])
        cT = pay_coin("T").move_to([5.65, 1.55, 0])
        cS = pay_coin("S").move_to([5.65, -2.0, 0])
        tiles = tor.tiling_overlays()

        with self.seg("s09"):
            self.play(FadeOut(S["top"]), FadeOut(S["cks"]), tor.pulse_chevrons(), run_time=0.9)
            self.cue(1.5)                                     # "A horizontal knife gives Gibbs weights"
            self.play(hk.glow_on(), run_time=0.3)
            self.play(hk.sweep(to=0.88), FadeIn(glab), run_time=1.2)
            self.play(FadeIn(gb), FadeIn(gcap), run_time=0.6)
            self.cue(3.9)                                     # "a vertical knife gives spatial weights"
            self.play(vk.glow_on(), run_time=0.3)
            self.play(vk.to_bond(8, rate_func=rate_functions.ease_in_out_sine), FadeIn(slab),
                      run_time=1.2)
            self.play(FadeIn(sb), FadeIn(scap), run_time=0.6)
            self.cue(6.45)                                    # "Squaring one doubles beta"
            s1, s2 = gb.square(relabel=r"e^{-2\beta E_k}")
            self.play(s1, run_time=0.5)
            self.play(s2, run_time=0.6)
            self.cue(8.15)                                    # "squaring the other doubles L"
            s1, s2 = sb.square(relabel=r"|\lambda_i|^{2L}")
            self.play(s1, run_time=0.5)
            self.play(s2, run_time=0.6)
            self.cue(9.85)                                    # "and an exact identity..."
            self.play(FadeOut(hk), FadeOut(vk), FadeIn(tiles[0]), run_time=0.35)
            for a, b in zip(tiles[:-1], tiles[1:]):
                self.wait(0.25)                               # each overlay holds ~0.6 s
                self.play(FadeOut(a), FadeIn(b), run_time=0.35)
            self.wait(0.15)
            self.play(FadeIn(cT, scale=0.5), FadeIn(cS, scale=0.5), FadeOut(tiles[-1]),
                      FadeIn(hk), FadeIn(vk), run_time=0.4)
            # "...lets each pay for the other's doubling": the coins swap
            self.play(cT.animate.move_to(cS.get_center()), cS.animate.move_to(cT.get_center()),
                      run_time=0.8, path_arc=PI / 3)      # arcs bulge <= 0.48: stays in frame

    # ================================================================ s10
    def s10_floor(self):
        real = Staircase("real", x_length=7.0, y_length=5.0).move_to([0.2, -0.25, 0])
        seed = real.tromino_at(36, 12.25)
        lab_in = T(r"small rings $+$ one trial state", font_size=28, color=DIM)
        lab_in.next_to(seed, RIGHT, buff=0.55).shift(DOWN * 0.15)
        arr_in = Arrow(lab_in.get_left() + LEFT * 0.05, seed.get_right() + RIGHT * 0.05, buff=0.1,
                       color=DIM, stroke_width=3, max_tip_length_to_length_ratio=0.3)
        basin = T("in the basin", font_size=28, color=GAP).next_to(lab_in, DOWN, buff=0.2).align_to(
            lab_in, LEFT)
        # well below the climbing trail, near the tip of the L axis (L ~ 6000, beta ~ 400)
        inf = M(r"L\to\infty", font_size=36, color=SPACE).move_to(real.npt(5800, 400))

        # the ch01 plot, same object and overlays as in ch01
        plot = GapPlot()
        labels = plot.series_labels()
        guide = plot.half_guide()
        lit = plot.literature_line()
        fl = plot.floor_lines()
        cf = T("claimed floor", font_size=28, color=GAP).move_to(plot.c2p(0.085, 0.075))
        cf_arr = Arrow(cf.get_left() + LEFT * 0.05, plot.c2p(0.012, 0.006), buff=0.1, color=GAP,
                       stroke_width=3, max_tip_length_to_length_ratio=0.18)

        # the shrunk plot: top-left, scale 1/2, numbers and axis labels gone
        sc = 0.5
        O_old = plot.c2p(0, 0)
        O_new = np.array([-6.3, 1.0, 0])

        def fade_along(m):
            """FadeOut that follows the shrink (lands where tf would put it)."""
            c = O_new + sc * (m.get_center() - O_old)
            return FadeOut(m, target_position=c, scale=sc)

        mag = RoundedRectangle(width=0.4, height=0.24, corner_radius=0.04, stroke_color=FG,
                               stroke_width=2.5, fill_opacity=0)
        mag.move_to(O_new + DL * 0.07, aligned_edge=DL)
        inset = self.build_inset()
        frame = inset["frame"]
        con = VGroup(Line(mag.get_corner(UR), frame.get_corner(UL)),
                     Line(mag.get_corner(DR), frame.get_corner(DL)))
        con.set_stroke(DIM, width=2, opacity=0.45)

        with self.seg("s10", breath=3.4):
            self.play(FadeOut(*self.mobjects), run_time=0.5)
            self.play(FadeIn(real), FadeIn(seed), run_time=0.8)
            self.play(FadeIn(lab_in), GrowArrow(arr_in), run_time=0.7)
            self.cue(2.6)                                     # "...put the pair inside the basin"
            self.play(seed.pulse(), FadeIn(basin, shift=0.1 * UP), run_time=1.0)
            self.cue(4.25)                                    # "and the staircase climbs..."
            self.play(FadeOut(lab_in), FadeOut(arr_in), FadeOut(basin), run_time=0.3)
            self.play(seed.climb(8, exit=True, trail=True), FadeIn(inf, rate_func=squish_rate_func(
                smooth, 0.65, 1.0)), run_time=2.2)
            # "Under the curve we started with": zoom out -- the staircase recedes into
            # 1/L -> 0 while the ch01 plot comes back (no black gap)
            stair_all = Group(*self.mobjects)
            # camera-style zoom out: both shrink, the plot settling at its ch01 size
            self.play(FadeOut(stair_all, scale=0.12, target_position=O_old + UR * 0.05,
                              rate_func=squish_rate_func(smooth, 0.0, 0.7)),
                      FadeIn(VGroup(plot, labels, guide, lit), scale=1.6,
                             rate_func=squish_rate_func(smooth, 0.12, 1.0)), run_time=1.1)
            self.cue(8.95)                                    # "there is now a claimed floor"
            self.play(Create(fl), run_time=0.5)
            self.play(FadeIn(cf, shift=0.1 * LEFT), GrowArrow(cf_arr), run_time=0.5)
            self.cue(10.9)                                    # "Low,"
            # ---- shrink the plot to the top-left; drop everything too small to read
            ax = plot.ax
            nums = VGroup(ax.x_axis.numbers, ax.y_axis.numbers)
            ax.x_axis.remove(ax.x_axis.numbers)
            ax.y_axis.remove(ax.y_axis.numbers)
            plot.remove(plot.x_label, plot.y_label)
            self.add(nums, plot.x_label, plot.y_label)
            gone = [nums[0], nums[1], plot.x_label, plot.y_label, labels, lit[1], lit[2],
                    guide, cf, cf_arr]
            self.play(VGroup(plot, lit[0]).animate.scale(sc, about_point=O_old)
                      .shift(O_new - O_old).fade(0.45),
                      fl.animate.scale(sc, about_point=O_old).shift(O_new - O_old),
                      *[fade_along(m) for m in gone],
                      Create(mag, rate_func=squish_rate_func(smooth, 0.55, 1.0)),
                      run_time=0.7)
            # ---- the magnifier opens into the inset (frame first, then its axes)
            self.play(Succession(ReplacementTransform(mag.copy(), frame, run_time=0.45),
                                 AnimationGroup(FadeIn(inset["axes"]), Create(con),
                                                run_time=0.35)))
            self.play(Create(inset["floor"]), run_time=0.6)  # "...but a floor"
            self.play(FadeIn(inset["data"]), Create(inset["lit"][0]), FadeIn(inset["lit"][1]),
                      FadeIn(inset["spin"]), run_time=0.5)
            # labels and the emphasis use the first part of the breath
            self.play(FadeIn(inset["labels"]), run_time=0.6)
            self.play(Indicate(inset["floor"][1], color=GAP, scale_factor=1.6), run_time=0.7)
        self.play(FadeOut(*self.mobjects), run_time=1.5)
        self.wait(0.3)

    def build_inset(self):
        """Log-log magnifier: L from ~2.8 to 1e5, gap from 1e-4 to ~1.6.
        Built in place; then shifted so its frame sits in the right part of the screen."""
        X0, X1, Y0, Y1 = 0.45, 5.0, -4.0, 0.2
        ax = Axes(x_range=[X0, X1, 1], y_range=[Y0, Y1, 1], x_length=6.3, y_length=4.75,
                  tips=False, axis_config={"include_ticks": False})
        xa = Line(ax.c2p(X0, Y0), ax.c2p(X1, Y0), color=DIM, stroke_width=2)
        ya = Line(ax.c2p(X0, Y0), ax.c2p(X0, Y1), color=DIM, stroke_width=2)
        ticks = VGroup()
        for k in range(1, 6):
            p = ax.c2p(k, Y0)
            ticks.add(Line(p + DOWN * 0.06, p + UP * 0.06, color=DIM, stroke_width=2))
            lab = "10" if k == 1 else f"10^{k}"
            ticks.add(M(lab, font_size=26, color=DIM).next_to(p, DOWN, buff=0.15))
        for k in range(-4, 1):
            p = ax.c2p(X0, k)
            ticks.add(Line(p + LEFT * 0.06, p + RIGHT * 0.06, color=DIM, stroke_width=2))
            lab = "1" if k == 0 else f"10^{{{k}}}"
            ticks.add(M(lab, font_size=26, color=DIM).next_to(p, LEFT, buff=0.12))
        xl = M("L", font_size=32).next_to(ax.c2p(X1, Y0), RIGHT, buff=0.15)
        yl = M(r"\gamma_L", font_size=32).next_to(ax.c2p(X0, Y1), UP, buff=0.12)
        axes = VGroup(xa, ya, ticks, xl, yl)

        _, one = load_gaps()
        data = VGroup(*[spin1_marker(ax.c2p(np.log10(L), np.log10(g)), side=0.12)
                        for L, g in one])
        spin = T(r"spin $1$", font_size=28, color=INTEGER)
        spin.next_to(data[0], RIGHT, buff=0.2).shift(UP * 0.12)
        ylit = np.log10(0.4105)
        lit_line = DashedLine(ax.c2p(X0, ylit), ax.c2p(X1, ylit), color=INTEGER, stroke_width=2.5,
                              dash_length=0.09)
        lit_lab = T(r"0.4105 \textit{(literature)}", font_size=26, color=DIM)
        lit_lab.next_to(ax.c2p(X1, ylit), DOWN, buff=0.14).align_to(ax.c2p(X1, 0), RIGHT)
        lit = VGroup(lit_line, lit_lab)

        y1, y2 = np.log10(4.79e-4), np.log10(3.82e-3)
        x60, x2304, xend = np.log10(60), np.log10(2304), 4.9
        floor = VMobject(stroke_color=GAP, stroke_width=5)
        floor.set_points_as_corners([ax.c2p(x60, y1), ax.c2p(x2304, y1), ax.c2p(x2304, y2),
                                     ax.c2p(xend, y2)])
        tip = Triangle(fill_color=GAP, fill_opacity=1, stroke_width=0).scale(0.1).rotate(-PI / 2)
        tip.move_to(ax.c2p(xend, y2) + RIGHT * 0.06)
        floor_g = VGroup(floor, tip)
        l1 = VGroup(M(r"\frac{4}{105}\log\frac{80}{79}", font_size=34, color=GAP),
                    T(r"even $L\ge60$", font_size=28, color=GAP)).arrange(DOWN, buff=0.12)
        l1.next_to(ax.c2p((x60 + x2304) / 2, y1), UP, buff=0.2)
        l1.shift(RIGHT * min(0, ax.c2p(x2304, 0)[0] - 0.25 - l1.get_right()[0]))
        l2 = VGroup(M(r"\frac{\log 20}{784}", font_size=34, color=GAP),
                    T(r"even $L\ge2304$", font_size=28, color=GAP)).arrange(DOWN, buff=0.12)
        l2.next_to(ax.c2p((x2304 + xend) / 2, y2), UP, buff=0.25)
        cl = T(r"\textit{claimed}", font_size=26, color=DIM).next_to(ax.c2p(xend, y2), DOWN,
                                                                     buff=0.22).align_to(
            ax.c2p(xend, 0), RIGHT)
        labels = VGroup(l1, l2, cl)
        content = VGroup(axes, data, spin, lit, floor_g, labels)
        frame = RoundedRectangle(width=content.width + 0.55, height=content.height + 0.45,
                                 corner_radius=0.18, stroke_color=DIM, stroke_width=2,
                                 fill_opacity=0).move_to(content)
        everything = VGroup(frame, content)
        everything.shift(np.array([6.6, -3.55, 0]) - frame.get_corner(DR))
        return dict(frame=frame, axes=axes, data=data, spin=spin, lit=lit, floor=floor_g,
                    labels=labels)
