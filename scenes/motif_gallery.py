"""Gallery that exercises every motif in scenes/motifs.py.

Render (from the scenes/ directory, in the manim environment):
  python -m manim -ql motif_gallery.py GapPlotDemo TorusDemo ...
Each scene writes its checkpoint times to output/motifs_work/marks_<Scene>.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motifs import *  # noqa: E402,F401,F403

WORK = Path(__file__).resolve().parent.parent / "output" / "motifs_work"
WORK.mkdir(parents=True, exist_ok=True)


class Marked(Scene):
    def setup(self):
        self._marks = []

    def mark(self, name):
        self._marks.append((name, round(self.renderer.time, 3)))

    def tear_down(self):
        self.wait(0.5)
        (WORK / f"marks_{type(self).__name__}.json").write_text(json.dumps(self._marks))
        super().tear_down()


class GapPlotDemo(Marked):
    def construct(self):
        plot = GapPlot()
        counter = plot.counter()
        cap = caption(r"exact diagonalization, periodic rings")
        self.play(plot.build_axes(), FadeIn(cap), run_time=1.5)
        self.add(counter)
        self.mark("axes")
        self.play(plot.build_data(counter=counter, run_time=4))
        self.mark("built")
        labs = plot.series_labels()
        self.play(FadeIn(labs))
        self.wait(0.3)
        self.mark("labels")
        hg = plot.half_guide()
        self.play(Create(hg[0]), FadeIn(hg[1]))
        lit = plot.literature_line()
        self.play(Create(lit[0]), Create(lit[1]), FadeIn(lit[2]))
        self.wait(0.3)
        self.mark("guides")
        self.play(FadeOut(counter, cap))
        plot2, anim = plot.zoomed(0.07, 0.01)
        self.mark("zoom_start")
        self.play(anim, run_time=2)
        self.wait(0.3)
        self.mark("zoomed")
        wi = plot2.what_if_curves()
        self.play(LaggedStart(*[Create(c) for c in wi], lag_ratio=0.3), run_time=2)
        self.wait(0.3)
        self.mark("whatif")
        plot3, anim = plot2.zoomed(0.27, 0.05)
        self.play(anim, run_time=2)
        fl = plot3.floor_lines()
        self.play(Create(fl))
        self.wait(0.3)
        self.mark("floor")


class TorusDemo(Marked):
    def construct(self):
        tor = Torus(5, 3, nx=10, ny=6).shift(LEFT * 1.2)
        self.play(FadeIn(tor))
        pl = tor.periodicity_labels()
        self.play(FadeIn(pl), tor.pulse_chevrons())
        self.wait(0.3)
        self.mark("torus")
        self.play(FadeOut(pl))
        hk = time_knife(tor, at=0.08)
        self.play(hk.cut_in(), run_time=1.0)
        self.play(hk.glow_on())
        self.mark("hk_in")
        self.play(hk.steps([0.25, 0.42, 0.58, 0.75, 0.92], label_tex=r"e^{-\delta\tau H}",
                           run_time=5))
        self.mark("hk_steps_done")
        self.play(hk.glow_off(), hk.move_to_frac(0.58))
        vk = space_knife(tor, bond=1)
        self.play(vk.cut_in(), run_time=1.0)
        self.play(vk.glow_on())
        self.wait(0.2)
        self.mark("both_knives")
        self.play(vk.steps(list(range(2, 12)), label_tex="X", run_time=8))
        self.mark("vk_steps_done")
        cut = vk.cut_copy()
        self.play(cut.animate.shift(RIGHT * 4.5), run_time=1)
        self.wait(0.2)
        self.mark("cut_lifted")
        self.play(FadeOut(hk, vk, cut))
        # resize
        self.play(Transform(tor, tor.resized(height=1.5)), run_time=1)
        self.mark("resized")
        self.play(Transform(tor, tor.resized(height=3.0)), run_time=1)
        # tiling
        ov = tor.tiling_overlays()
        for g in ov:
            self.play(FadeIn(g), run_time=0.6)
            self.wait(0.4)
            self.mark(f"tiling_{len(self._marks)}")
            self.play(FadeOut(g), run_time=0.4)
        # thumbnail
        thumb = TorusThumb()
        self.play(ReplacementTransform(tor, thumb), run_time=1.2)
        self.wait(0.2)
        self.mark("thumb")
        for i in range(3):
            self.play(thumb.double_beta())
            self.wait(0.2)
            self.mark(f"thumb_b{i}")
        self.play(thumb.reset())
        for i in range(2):
            self.play(thumb.double_L())
            self.wait(0.2)
            self.mark(f"thumb_L{i}")
        # icons row
        icons = VGroup(icon_torus(), icon_squared_bars(), icon_tiling(), icon_staircase(),
                       pay_coin("T"), pay_coin("S")).arrange(RIGHT, buff=0.6).shift(DOWN * 2.5)
        self.play(FadeIn(icons))
        self.wait(0.3)
        self.mark("icons")


class BarsDemo(Marked):
    def construct(self):
        wb = WeightBars([0.6, 0.15, 0.1, 0.08, 0.07], color=TIME, highlight_color=TIME)
        wb.shift(LEFT * 3 + DOWN * 1.2)
        cap = wb.caption(r"e^{-\beta E_k}")
        br = wb.defect_brace("defect")
        self.play(FadeIn(wb), FadeIn(cap), FadeIn(br))
        self.wait(0.3)
        self.mark("bars")
        s1, s2 = wb.square(relabel=r"e^{-2\beta E_k}")
        self.play(s1, run_time=1.2)
        self.wait(0.3)
        self.mark("sq1")
        self.play(s2, run_time=1.2)
        self.wait(0.3)
        self.mark("sq2")
        lam = np.array([0.95, -0.8, 0.7, -0.6, 0.5, -0.4])
        sb = WeightBars(lam ** 5, width=4, height=2.0, color=SPACE, signed=True, value_scale=2.0)
        sb.shift(RIGHT * 3.4 + DOWN * 0.3)
        self.play(FadeIn(sb))
        self.wait(0.3)
        self.mark("signed5")
        self.play(sb.morph_to(lam ** 6), run_time=1.5)
        self.wait(0.3)
        self.mark("signed6")
        fg = WeightBars([0.70, 0.15, 0.08, 0.04, 0.03], width=4, color=FG).shift(UP * 2 + RIGHT * 3.3)
        self.play(FadeIn(fg))
        self.wait(0.3)
        self.mark("fg")


class GaugesDemo(Marked):
    def construct(self):
        u = DefectGauge(0.479, kind="u", decimals=3).shift(LEFT * 4.5)
        gg = DefectGauges(p=0.3, q=0.3, one_percent=True).shift(RIGHT * 1.5)
        self.play(FadeIn(u), FadeIn(gg))
        self.wait(0.3)
        self.mark("gauges")
        self.play(gg.set_defects(q=0.3 ** 2), run_time=1)
        self.play(gg.set_defects(q=0.3 ** 4), run_time=1)
        self.wait(0.2)
        self.mark("q_drop")
        self.play(gg.set_defects(p=0.0479, q=0.1815), gg.to_bounds(), run_time=1.5)
        self.play(pulse(gg.q.fill))
        self.wait(0.2)
        self.mark("bounds")
        self.play(gg.set_defects(p=0.0084513, q=0.0054986), run_time=2)
        self.play(gg.p.recolor(GAP), gg.q.recolor(GAP))
        self.wait(0.3)
        self.mark("gap")


class StairDemo(Marked):
    def construct(self):
        st = Staircase("symbolic").to_edge(LEFT, buff=0.8)
        tr = st.tromino(0, 0)
        lS, lT = tr.label_S(r"S:\ p"), tr.label_T(r"T:\ q")
        self.play(FadeIn(st), FadeIn(tr), FadeIn(lS), FadeIn(lT))
        self.wait(0.3)
        self.mark("start")
        lf = tr.leapfrog(labels=[r"\approx2p+q", r"p_+", None, r"q_+"])
        for i, a in enumerate(lf.steps):
            self.play(a, run_time=1.2)
            self.wait(0.2)
            self.mark(f"leap{i + 1}")
        self.play(tr.ghost(), FadeOut(lS, lT), *[FadeOut(m) for m in lf.labels if m is not None])
        arr = tr.diag_arrow()
        self.play(Create(arr))
        self.wait(0.2)
        self.mark("ghost")
        self.play(FadeOut(st, tr, arr, lf.new))
        real = Staircase("real", x_length=6.5, y_length=4.8).to_edge(LEFT, buff=0.8)
        seed = real.tromino_at(36, 12.25)
        alt = real.tromino_at(60, 26.25, style="alt")
        self.play(FadeIn(real), FadeIn(seed))
        self.play(seed.pulse())
        self.play(FadeIn(alt))
        self.wait(0.2)
        self.mark("real")
        self.play(seed.climb(6), run_time=4)
        self.wait(0.2)
        self.mark("real_climbed")
        self.play(FadeOut(real, seed, alt))
        sym = Staircase("symbolic").to_edge(LEFT, buff=0.8)
        f1 = sym.fig1(0, 0, k=3)
        bare = Staircase("bare", x_length=5, y_length=3.6).to_edge(RIGHT, buff=0.6)
        t2 = bare.tromino(0.5, 0.5)
        self.play(FadeIn(sym), FadeIn(f1), FadeIn(bare), FadeIn(t2))
        self.wait(0.2)
        self.mark("fig1")
        self.play(t2.climb(5, exit=True, trail=True), run_time=4)
        self.wait(0.2)
        self.mark("exit")


class BubblesDemo(Marked):
    def construct(self):
        col = objection_column()
        self.play(objection_column_in(col), run_time=2)
        self.wait(0.5)
        self.mark("column")
        self.play(objection_collapse(col), run_time=1.5)
        self.mark("collapsed")
        b = objection_bubble("finite")
        self.play(bubble_in(b), run_time=0.8)
        self.wait(0.2)
        self.mark("pop")
        self.play(bubble_indicate(b))
        self.play(bubble_check(b))
        self.play(bubble_answer(b, "the question is uniformity"))
        self.wait(0.3)
        self.mark("answered")
        self.play(bubble_out(b))
        b2 = objection_bubble("half")
        self.play(bubble_in(b2))
        self.play(bubble_check(b2))
        self.wait(0.3)
        self.mark("half")


class TagsStatusDemo(Marked):
    def construct(self):
        t1 = tag(TAG_READING)
        t2 = tag(TAG_HEURISTIC, corner=UL)
        nl = NumberLine(x_range=[-1, 1, 0.5], length=5, color=DIM).shift(DOWN * 2)
        t3 = inline_tag(TAG_SCHEMATIC, nl, RIGHT)
        num = M(r"0.41050(2)", font_size=40).shift(UP * 1)
        lit = literature_label(num)
        self.play(tag_in(t1), tag_in(t2), FadeIn(nl, t3, num, lit))
        self.wait(0.3)
        self.mark("tags")
        self.play(FadeOut(t1, t2, nl, t3, num, lit))
        card = StatusCard()
        self.play(card.anim_titles())
        self.play(card.anim_tag(0))
        self.play(card.anim_tag(1))
        self.play(card.anim_meta())
        for i in range(3):
            self.play(card.anim_line(i))
        self.wait(0.3)
        self.mark("card")


class StillsDemo(Marked):
    """Representative storyboard compositions, to judge the motifs in context."""

    def construct(self):
        # ch01 s03: the gap plot with its guides
        plot = GapPlot()
        cap = caption(r"exact diagonalization, periodic rings")
        self.add(plot, plot.series_labels(), plot.half_guide(), plot.literature_line(), cap)
        self.wait(0.3)
        self.mark("ch01_s03")
        self.clear()
        # ch04 s03: torus, both knives, formula, tag
        tor = Torus(5, 3, nx=10, ny=6).shift(LEFT * 2.6 + DOWN * 0.2)
        hk = time_knife(tor, at=0.58)
        vk = space_knife(tor, bond=1)
        vk.glow.set_stroke(opacity=0.3)
        fz = M(r"Z=\operatorname{Tr}\,X_\beta^{\,L}=\sum_i\lambda_i(\beta)^{L}", color=SPACE,
               font_size=36).move_to(RIGHT * 3.6 + UP * 0.6)
        ft = M(r"Z=\sum_k e^{-\beta E_k}", color=TIME, font_size=36).next_to(fz, UP, buff=0.5)
        tg = tag(r"in the spirit of Suzuki's quantum transfer matrix")
        self.add(tor, hk, vk, fz, ft, tg)
        self.wait(0.3)
        self.mark("ch04_s03")
        self.clear()
        # ch05 s02: thumbnail, orange bars squared, u gauge, formula
        thumb = TorusThumb()
        thumb2 = TorusThumb()
        self.add(thumb)
        self.play(thumb.double_beta(), run_time=0.8)
        wb = WeightBars([0.6, 0.15, 0.1, 0.08, 0.07], width=4.6, color=TIME,
                        highlight_color=TIME).move_to(LEFT * 1.2 + DOWN * 1.0)
        cp = wb.caption(r"e^{-\beta E_k}")
        br = wb.defect_brace(M("u", color=DEFECT, font_size=34))
        half = wb.level_line(0.5, label=r"\tfrac12")
        g = DefectGauge(wb.defect(), kind="u", decimals=3).move_to(RIGHT * 4.6 + DOWN * 0.6)
        fT = M(r"T(L,\beta)=\sum_k w_k^2=\frac{Z(L,2\beta)}{Z(L,\beta)^2}", color=TIME,
               font_size=36).to_edge(UP, buff=0.6).shift(RIGHT * 1.5)
        self.add(wb, cp, br, half, g, fT)
        self.wait(0.3)
        self.mark("ch05_s02")
        s1, s2 = wb.square(relabel=r"e^{-2\beta E_k}")
        self.play(s1)
        self.play(s2, g.set_defect(1 - float((np.array([.6, .15, .1, .08, .07]) ** 2 / (np.array([.6, .15, .1, .08, .07]) ** 2).sum()) @ (np.array([.6, .15, .1, .08, .07]) ** 2 / (np.array([.6, .15, .1, .08, .07]) ** 2).sum()))))
        self.wait(0.3)
        self.mark("ch05_s02_after")
        self.clear()
        # ch06 s09: staircase + running list
        st = Staircase("symbolic").to_edge(LEFT, buff=0.7).shift(DOWN * 0.3)
        tr = st.tromino(0, 0)
        lS, lT = tr.label_S(r"S\!:\,p"), tr.label_T(r"T\!:\,q")
        lf = tr.leapfrog(labels=[r"\approx2p+q", r"p_+", None, r"q_+"])
        lst = VGroup(T(r"1. double $\beta$ for $S$ (paid by $T$)", font_size=28),
                     T(r"2. square in space", font_size=28),
                     T(r"3. double $L$ for $T$ (paid by $S$)", font_size=28),
                     T(r"4. square in time", font_size=28)).arrange(DOWN, aligned_edge=LEFT,
                                                                      buff=0.3)
        lst.to_edge(RIGHT, buff=0.6)
        self.add(st, tr, lS, lT, lst)
        for a in lf.steps:
            self.play(a, run_time=0.6)
        self.wait(0.3)
        self.mark("ch06_s09")
        self.clear()
        # ch08 s11: real staircase + gauges in bound mode
        real = Staircase("real", x_length=6.4, y_length=4.8).to_edge(LEFT, buff=0.8)
        seed = real.tromino_at(2304, 784)
        lS = seed.label_S(r"1-S(2304,784)\le0.0084513", direction=DOWN, font_size=28)
        lT = seed.label_T(r"1-T(4608,784)\le0.0054986", direction=LEFT, font_size=28)
        gg = DefectGauges(p=0.0084513, q=0.0054986, bound=True, one_percent=True)
        gg.move_to(RIGHT * 4.3 + DOWN * 0.2)
        self.add(real, seed, lS, lT, gg)
        self.play(gg.p.recolor(GAP), gg.q.recolor(GAP), run_time=0.5)
        self.wait(0.3)
        self.mark("ch08_s11")
        self.clear()
        # ch01 s07 status card
        self.add(StatusCard())
        self.wait(0.3)
        self.mark("ch01_s07")
        self.clear()
        # bubble + tag together
        b = objection_bubble("even")
        t = tag(TAG_HEURISTIC, corner=UL)
        self.add(b, t)
        self.play(bubble_check(b))
        self.play(bubble_answer(b, "only even rings give a second distribution"))
        self.wait(0.3)
        self.mark("bubble_tag")
