"""ch03: Why a proof was hard.

What rigor could and could not do: LSM leaves integer spin unconstrained; AKLT
shows the 'finite check' template but only for frustration-free chains; the
Heisenberg chain is not frustration-free; the evidence; Tasaki's conditional
theorem; and finally the exact claim.

Reusable pieces defined here (import them, do not copy them):
    from ch03_why_hard import aklt_cartoon, AKLTChain, FiniteCheckRow
The valence-bond cartoon returns in ch08 s13 and ch09 s01.

Timing: every voice block is cued to the pauses of its narration clip
(measured with ffmpeg silencedetect on audio/ch03/*.wav).  Cue times are in
seconds of the reference clip (REF) and are rescaled by d / REF[seg], so the
choreography follows the speech even if a clip is regenerated.
"""
from motifs import *  # noqa: F401,F403

# clip durations the cue sheets below were measured on
REF = {"s01": 14.25, "s02": 15.025, "s03": 22.5, "s04": 21.025,
       "s05": 12.5, "s06": 14.575, "s07": 19.175, "s08": 15.575}


# =================================================================== reusable pieces
def panel(width, height, color, stroke=3, fill_opacity=0.05, corner_radius=0.25):
    """Rounded card with a faint tint of its border colour."""
    return RoundedRectangle(width=width, height=height, corner_radius=corner_radius,
                            stroke_color=color, stroke_width=stroke,
                            fill_color=color, fill_opacity=fill_opacity)


class AKLTChain(VGroup):
    """Valence-bond (AKLT) cartoon (ch03 s03; reused in ch08 s13 and ch09 s01).

    n spin-one sites (INTEGER circles), each split into two VIRTUAL spin-1/2 dots;
    a VIRTUAL valence bond (singlet) binds the right dot of site j to the left dot of
    site j+1 (bond_style="line", the textbook picture; "ellipse" draws ovals instead);
    the two outermost dots stay unpaired, with a soft VIRTUAL glow.

    Parts: .sites, .dots (VGroup of (left, right) pairs), .bonds, .free (the two
    unpaired end dots), .glows.  Animations: sites_in(), split_in(), bonds_in(),
    glows_in().  bond_center(k) is the midpoint of bond k (between sites k, k+1).
    """

    def __init__(self, n=8, spacing=1.3, radius=0.36, dot_r=0.08, dot_dx=0.16,
                 bond_style="line", bond_stroke=5):
        super().__init__()
        self.n, self.spacing, self.dot_dx = n, spacing, dot_dx
        xs = [spacing * (j - (n - 1) / 2) for j in range(n)]
        self.sites = VGroup(*[Circle(radius=radius, stroke_color=INTEGER, stroke_width=3)
                              .move_to([x, 0, 0]) for x in xs])
        self.dots = VGroup(*[VGroup(Dot([x - dot_dx, 0, 0], radius=dot_r, color=VIRTUAL),
                                    Dot([x + dot_dx, 0, 0], radius=dot_r, color=VIRTUAL))
                             for x in xs])
        if bond_style == "line":
            self.bonds = VGroup(*[Line([a + dot_dx, 0, 0], [b - dot_dx, 0, 0], color=VIRTUAL,
                                       stroke_width=bond_stroke)
                                  for a, b in zip(xs[:-1], xs[1:])])
        else:
            self.bonds = VGroup(*[Ellipse(width=spacing - 2 * dot_dx + 0.3, height=0.4,
                                          stroke_color=VIRTUAL, stroke_width=2.5)
                                  .move_to([(a + b) / 2, 0, 0])
                                  for a, b in zip(xs[:-1], xs[1:])])
        self.free = VGroup(self.dots[0][0], self.dots[-1][1])
        self.glows = VGroup(*[
            VGroup(Circle(radius=0.27, stroke_width=0, fill_color=VIRTUAL, fill_opacity=0.12),
                   Circle(radius=0.17, stroke_width=0, fill_color=VIRTUAL, fill_opacity=0.22)
                   ).move_to(d) for d in self.free])
        self.add(self.glows, self.sites, self.bonds, self.dots)

    def bond_center(self, k):
        return (self.sites[k].get_center() + self.sites[k + 1].get_center()) / 2

    def sites_in(self, **kw):
        kw.setdefault("lag_ratio", 0.08)
        return LaggedStart(*[GrowFromCenter(s) for s in self.sites], **kw)

    def split_in(self, **kw):
        """Each spin one splits into two spin one-halves (dots slide out of the centre)."""
        kw.setdefault("lag_ratio", 0.08)
        dx = self.dot_dx
        return LaggedStart(*[AnimationGroup(FadeIn(p[0], shift=LEFT * dx),
                                            FadeIn(p[1], shift=RIGHT * dx))
                             for p in self.dots], **kw)

    def bonds_in(self, **kw):
        kw.setdefault("lag_ratio", 0.12)
        return LaggedStart(*[Create(b) for b in self.bonds], **kw)

    def glows_in(self, **kw):
        return FadeIn(self.glows, scale=0.5, **kw)


def aklt_cartoon(n=8, **kw):
    """The ch03 valence-bond cartoon (see AKLTChain)."""
    return AKLTChain(n, **kw)


def mini_chain(n, spacing=0.26, r=0.06, color=INTEGER):
    pts = [RIGHT * spacing * i for i in range(n)]
    links = VGroup(*[Line(pts[i], pts[i + 1], color=DIM, stroke_width=2) for i in range(n - 1)])
    dots = VGroup(*[Dot(p, radius=r, color=color) for p in pts])
    return VGroup(links, dots)


class FiniteCheckRow(VGroup):
    """The frustration-free 'finite check': a boxed short chain => longer chains gapped.

    Parts: .left (GAP box + 4-site chain), .arrow (=>), .chains (6, 9, 12 sites),
    .checks (GAP checks), .right (chains + checks).
    """

    def __init__(self):
        super().__init__()
        self.small = mini_chain(4)
        self.box = RoundedRectangle(width=self.small.width + 0.55, height=0.8,
                                    corner_radius=0.12, stroke_color=GAP,
                                    stroke_width=3).move_to(self.small)
        self.left = VGroup(self.box, self.small)
        self.arrow = M(r"\Longrightarrow", font_size=48)
        self.chains = VGroup(*[mini_chain(k) for k in (6, 9, 12)]).arrange(
            DOWN, aligned_edge=LEFT, buff=0.32)
        xr = self.chains.get_right()[0] + 0.38
        self.checks = VGroup(*[check_mark(size=0.26).move_to([xr, c.get_y(), 0])
                               for c in self.chains])
        self.right = VGroup(self.chains, self.checks)
        VGroup(self.left, self.arrow, self.right).arrange(RIGHT, buff=0.45)
        self.add(self.left, self.arrow, self.right)


def gapless_icon(w=1.1, color=HALF):
    """Levels crowding down onto the ground state."""
    ys = [0, 0.05, 0.12, 0.22, 0.35, 0.51, 0.70]
    return VGroup(*[Line(LEFT * w / 2, RIGHT * w / 2, color=color, stroke_width=3).shift(UP * y)
                    for y in ys])


def degenerate_icon(w=1.1, color=HALF):
    """Two ground states side by side, a gap, then a band."""
    half = (w - 0.14) / 2
    g = VGroup(Line(LEFT * w / 2, LEFT * w / 2 + RIGHT * half, color=color, stroke_width=3),
               Line(RIGHT * w / 2 + LEFT * half, RIGHT * w / 2, color=color, stroke_width=3))
    for y in (0.46, 0.58, 0.70):
        g.add(Line(LEFT * w / 2, RIGHT * w / 2, color=color, stroke_width=3).shift(UP * y))
    return g


def singlet_oval(chain, j, color=VIRTUAL, opacity=1.0):
    """Oval around arrows j, j+1 of a spin_chain (a two-site singlet)."""
    a, b = chain[j].get_center(), chain[j + 1].get_center()
    w = np.linalg.norm(b - a) + 0.52
    return Ellipse(width=w, height=1.0, stroke_color=color, stroke_width=3,
                   stroke_opacity=opacity, fill_color=color,
                   fill_opacity=0.08 * opacity).move_to((a + b) / 2)


# =================================================================== the chapter
class Ch03(NarratedScene):
    CHAPTER = "ch03"

    # ---------------------------------------------------------------- cueing
    def cues(self, sid, d):
        """Return (at, rt): at(t) waits until t s into the clip; rt(s) scales a duration."""
        t0 = self.renderer.time
        k = d / REF[sid]

        def at(t):
            target = t * k
            now = self.renderer.time - t0
            if target - now > 1e-3:
                self.wait(target - now)
            elif now - target > 0.2:
                print(f"[cue] {sid}: {now - target:.2f}s late for cue {t}")

        return at, (lambda s: s * k)

    def construct(self):
        self.s01()
        self.s02()
        self.s03()
        self.s04()
        self.s05()
        self.s06()
        self.s07()
        self.s08()
        self.play(FadeOut(*self.mobjects), run_time=0.8)
        self.wait(0.3)

    # ---------------------------------------------------------------- s01
    def s01(self):
        lc, rc = np.array([-3.35, -0.15, 0]), np.array([3.35, -0.15, 0])
        lcard, rcard = panel(6.1, 6.3, HALF).move_to(lc), panel(6.1, 6.3, INTEGER).move_to(rc)
        lhead = T("half-integer spin", font_size=42, color=HALF).move_to(lc + UP * 2.5)
        rhead = T("integer spin", font_size=42, color=INTEGER).move_to(rc + UP * 2.5)
        # display-style fractions: \tfrac at 34 would put the numerals under the size floor
        lsub = M(r"S=\frac12,\ \frac32,\ \dots", font_size=34, color=DIM).next_to(
            lhead, DOWN, buff=0.18)
        rsub = M(r"S=1,\ 2,\ \dots", font_size=34, color=DIM).set_x(rhead.get_x())
        rsub.shift(UP * (lsub[0][0].get_y() - rsub[0][0].get_y()))   # same "S=" line

        names = VGroup(T(r"Lieb--Schultz--Mattis 1961", font_size=32),
                       T(r"Affleck--Lieb 1986", font_size=32)).arrange(DOWN, buff=0.2)
        names.move_to(lc + UP * 0.6)
        claim = T(r"no unique gapped ground state", font_size=36).move_to(lc + DOWN * 0.55)

        gl, dg = gapless_icon(), degenerate_icon()
        gl.move_to(lc + LEFT * 1.45 + DOWN * 1.75)
        dg.move_to(lc + RIGHT * 1.45 + DOWN * 1.75)
        orw = T("or", font_size=32, color=DIM).move_to(lc + DOWN * 1.75)
        gl_l = T("gapless", font_size=30).next_to(gl, DOWN, buff=0.22)
        dg_l = T("degenerate", font_size=30).next_to(dg, DOWN, buff=0.22)
        gl_l.align_to(dg_l, DOWN)

        self.s01_body = VGroup(names, claim, gl, dg, orw, gl_l, dg_l)
        self.lcard, self.rcard = lcard, rcard
        self.lhead, self.rhead, self.lsub, self.rsub = lhead, rhead, lsub, rsub

        with self.voice("s01") as d:
            at, rt = self.cues("s01", d)
            # "What could mathematics prove?"
            at(0.1)
            self.play(Create(lcard), Create(rcard), run_time=rt(0.8))
            self.play(LaggedStart(FadeIn(lhead, shift=0.15 * DOWN), FadeIn(lsub),
                                  FadeIn(rhead, shift=0.15 * DOWN), FadeIn(rsub),
                                  lag_ratio=0.25), run_time=rt(0.9))
            # "On the half-integer side, a lot."
            at(2.2)
            self.play(lcard.animate.set_fill(opacity=0.10), rcard.animate.set_stroke(opacity=0.5),
                      Indicate(lhead, color=HALF, scale_factor=1.08), run_time=rt(0.9))
            # "Lieb, Schultz and Mattis, and later Affleck and Lieb,"
            at(4.45)
            self.play(FadeIn(names[0], shift=0.15 * UP), run_time=rt(0.7))
            at(6.2)
            self.play(FadeIn(names[1], shift=0.15 * UP), run_time=rt(0.7))
            # "showed that a half-integer chain cannot have a unique ground state with a gap:"
            at(7.8)
            self.play(Write(claim), run_time=rt(1.8))
            # "it is gapless, or degenerate."
            at(12.0)
            self.play(LaggedStart(Create(gl, lag_ratio=0.15), FadeIn(gl_l), lag_ratio=0.3),
                      run_time=rt(0.7))
            self.play(FadeIn(orw), run_time=rt(0.3))
            self.play(LaggedStart(Create(dg, lag_ratio=0.15), FadeIn(dg_l), lag_ratio=0.3),
                      run_time=rt(0.7))

    # ---------------------------------------------------------------- s02
    def s02(self):
        # The cards shrink into two header panels at the top.  The spiral is drawn on
        # the ring cut open and laid flat (the dashed arc closes it): drawn on a flat
        # circle, an in-plane twist of 2*pi*j/L turns with the circle itself and just
        # looks like a radial pattern.
        lc2, rc2 = np.array([-3.35, 2.2, 0]), np.array([3.35, 2.2, 0])
        lcard2 = panel(6.1, 2.7, HALF).move_to(lc2).set_fill(opacity=0.10)
        rcard2 = panel(6.1, 2.7, INTEGER).move_to(rc2).set_stroke(opacity=0.5)
        lhead2 = self.lhead.copy().move_to(lc2 + UP * 0.82)
        rhead2 = self.rhead.copy().move_to(rc2 + UP * 0.82)
        lsub2 = self.lsub.copy().next_to(lhead2, DOWN, buff=0.12)
        rsub2 = self.rsub.copy().set_x(rhead2.get_x())
        rsub2.shift(UP * (lsub2[0][0].get_y() - rsub2[0][0].get_y()))

        N = 16
        chain = spin_chain(N, spacing=0.63, staggered=True, color=FG, length=0.52)
        chain.move_to(DOWN * 0.45)
        xL, xR = chain[0].get_x(), chain[-1].get_x()
        y0 = chain.get_bottom()[1] - 0.15
        arc = DashedVMobject(ArcBetweenPoints([xR, y0, 0], [xL, y0, 0], angle=-0.45),
                             num_dashes=48, dashed_ratio=0.55).set_stroke(DIM, 2)
        lab = VGroup(T("slow spiral", font_size=32),
                     T("(a variational state)", font_size=28, color=DIM)).arrange(
            RIGHT, buff=0.2, aligned_edge=DOWN).move_to([-2.45, -2.05, 0])
        de = M(r"\Delta E=O(1/L)", font_size=40).move_to([3.55, -2.05, 0])

        ortho_t = T("orthogonal to the ground state", font_size=30)
        ortho_b = RoundedRectangle(width=ortho_t.width + 0.4, height=ortho_t.height + 0.32,
                                   corner_radius=0.15, stroke_color=HALF, stroke_width=3,
                                   fill_color=BG, fill_opacity=0.6)
        ortho = VGroup(ortho_b, ortho_t).move_to(lc2 + DOWN * 0.74)
        ortho_t.move_to(ortho_b)

        noob = T("no obstruction", font_size=30, color=DIM)
        qm = T("?", font_size=84, color=DEFECT)    # open-question marks are DEFECT in ch03

        # The spiral turns site j by 2*pi*j/N about its Neel orientation, so neighbours
        # still differ by ~180 deg.  The odd sublattice recedes to DIM while it turns,
        # leaving the even sites to show the slow 2*pi/(N/2)-per-step helix.
        def turn(a, ang, recede):
            if not recede:
                return Rotate(a, angle=ang, about_point=a.get_center())
            start, c = a.copy(), a.get_center()

            def upd(m, t):
                m.become(start.copy().rotate(t * ang, about_point=c)
                         .set_color(interpolate_color(ManimColor(FG), ManimColor(DIM), t))
                         .set_opacity(1 - 0.5 * t))
            return UpdateFromAlphaFunc(a, upd)
        VGroup(noob, qm).arrange(RIGHT, buff=0.45).move_to(rc2 + DOWN * 0.68)
        cap = T(r"escaping a no-go $\neq$ having a gap", font_size=36).move_to(DOWN * 3.2)

        with self.voice("s02") as d:
            at, rt = self.cues("s02", d)
            self.play(FadeOut(self.s01_body), run_time=rt(0.35))
            self.play(Transform(self.lcard, lcard2), Transform(self.rcard, rcard2),
                      Transform(self.lhead, lhead2), Transform(self.rhead, rhead2),
                      Transform(self.lsub, lsub2), Transform(self.rsub, rsub2),
                      run_time=rt(0.6))
            # "Their trick, a slow spiral of the spins around the ring,"
            self.play(LaggedStart(*[FadeIn(a) for a in chain], lag_ratio=0.05),
                      Create(arc), run_time=rt(0.6))
            at(1.6)
            self.play(*[turn(a, TAU * j / N, j % 2 == 1) for j, a in enumerate(chain)],
                      run_time=rt(1.4))
            self.play(FadeIn(lab, shift=0.1 * UP), run_time=rt(0.45))
            # "costs energy of order one over L and,"
            at(3.5)
            self.play(Write(de), run_time=rt(1.1))
            # "for half-integer spin,"
            at(5.9)
            self.play(Indicate(self.lhead, color=HALF, scale_factor=1.08), run_time=rt(0.8))
            # "is orthogonal to the ground state."
            at(7.8)
            self.play(FadeIn(ortho, scale=0.9), run_time=rt(0.7))
            # "Integer spin escapes,"
            at(10.15)
            self.play(self.rcard.animate.set_stroke(opacity=1).set_fill(opacity=0.10),
                      FadeIn(noob), run_time=rt(0.6))
            self.play(FadeIn(qm, scale=0.6), run_time=rt(0.5))
            # "but escaping a no-go theorem is not having a gap."
            at(11.8)
            self.play(Write(cap), run_time=rt(1.6))
        self.s02_all = VGroup(self.lcard, self.rcard, self.lhead, self.rhead, self.lsub,
                              self.rsub, chain, arc, lab, de, ortho, noob, qm, cap)

    # ---------------------------------------------------------------- s03
    def s03(self):
        hdr = T(r"Affleck--Kennedy--Lieb--Tasaki, 1987", font_size=34).move_to(UP * 3.3)
        eq = M(r"h_{\rm AKLT}=\mathbf S_j\cdot\mathbf S_{j+1}"
               r"+\frac13\big(\mathbf S_j\cdot\mathbf S_{j+1}\big)^2",
               font_size=38).move_to(UP * 2.35)
        ch = AKLTChain().move_to(UP * 0.75)
        checks = VGroup(*[check_mark(size=0.28).move_to(ch.bond_center(k) + UP * 0.62)
                          for k in range(ch.n - 1)])
        blab = T("every bond term at its minimum", font_size=30, color=GAP).move_to(DOWN * 0.02)

        row = FiniteCheckRow()
        fftag = tag_box("frustration-free only")
        grp = VGroup(row, fftag).arrange(RIGHT, buff=0.6).move_to(DOWN * 1.6)
        cap = T(r"gap on one finite chain large enough $\Rightarrow$ gap for all longer chains",
                font_size=30).move_to(DOWN * 2.85)

        with self.voice("s03") as d:
            at, rt = self.cues("s03", d)
            self.play(FadeOut(self.s02_all), run_time=rt(0.4))
            # "In 1987, Affleck, Kennedy, Lieb and Tasaki"
            at(0.45)
            self.play(Write(hdr), run_time=rt(2.2))
            # "found a cousin with a provable gap:"
            at(3.6)
            self.play(ch.sites_in(), run_time=rt(1.2))
            # "split each spin one into two spin one-halves,"
            at(6.45)
            self.play(ch.split_in(), run_time=rt(1.6))
            # "bound into singlets across every bond."
            at(9.5)
            self.play(ch.bonds_in(), run_time=rt(1.4))
            self.play(ch.glows_in(), run_time=rt(0.6))
            # "That A-K-L-T state minimizes every bond term at once,"
            at(12.3)
            self.play(Write(eq), run_time=rt(1.3))
            self.play(LaggedStart(*[Create(c) for c in checks], lag_ratio=0.15),
                      run_time=rt(1.3))
            self.play(FadeIn(blab, shift=0.1 * UP), run_time=rt(0.5))
            # "and for such frustration-free chains,"
            at(16.1)
            self.play(FadeIn(fftag, shift=0.1 * DOWN), run_time=rt(0.6))
            # "a large enough gap on one finite chain settles all longer ones."
            at(18.2)
            self.play(FadeIn(row.left, scale=0.9), FadeIn(cap), run_time=rt(0.7))
            self.play(Write(row.arrow), run_time=rt(0.5))
            self.play(LaggedStart(*[FadeIn(c, shift=0.2 * RIGHT) for c in row.chains],
                                  lag_ratio=0.25), run_time=rt(0.9))
            self.play(LaggedStart(*[Create(c) for c in row.checks], lag_ratio=0.2),
                      run_time=rt(0.7))
        self.s03_all = VGroup(hdr, eq, ch, checks, blab, row, fftag, cap)

    # ---------------------------------------------------------------- s04
    def s04(self):
        h1 = M(r"\text{Heisenberg:}\quad h=\mathbf S_j\cdot\mathbf S_{j+1}", font_size=38)
        h2 = T(r"not frustration-free", font_size=34, color=DEFECT)
        sep = Line(UP * 0.22, DOWN * 0.22, color=DIM, stroke_width=2)
        header = VGroup(h1, sep, h2).arrange(RIGHT, buff=0.4).move_to(UP * 3.25)

        chain = spin_chain(8, spacing=1.15, staggered=True, color=FG, length=0.72)
        chain.move_to(UP * 1.6)
        A, B, C = (singlet_oval(chain, j) for j in (2, 3, 4))
        slab = T("singlet", font_size=30, color=VIRTUAL).next_to(A, DOWN, buff=0.12)
        settled = VGroup(*[singlet_oval(chain, j, opacity=0.4) for j in range(7)])

        y_nl = -0.55
        nl = NumberLine(x_range=[-2.1, -1.2, 0.1], length=9.0, color=DIM, stroke_width=2,
                        include_tip=False, tick_size=0.06).move_to(UP * y_nl)
        nums = VGroup(*[M(f"{v:.1f}", font_size=28, color=DIM).next_to(nl.n2p(v), DOWN,
                                                                         buff=0.18)
                        for v in (-2.0, -1.8, -1.6, -1.4, -1.2)])
        m2 = Dot(nl.n2p(-2.0), radius=0.1, color=VIRTUAL)
        m2_lab = VGroup(T("singlet:", font_size=30, color=VIRTUAL),
                        T("one bond's minimum", font_size=30)).arrange(DOWN, buff=0.1)
        m2_lab.next_to(nums, DOWN, buff=0.25).set_x(nl.n2p(-2.0)[0])
        e0 = -1.4015
        mh = Dot(nl.n2p(e0), radius=0.1, color=FG)
        mh_val = M(r"-1.4015", font_size=34).next_to(mh, UP, buff=0.2)
        mh_lit = literature_label(mh_val, RIGHT, buff=0.18)
        mh_lab = VGroup(T("Heisenberg ground state,", font_size=30),
                        T("per bond", font_size=30)).arrange(DOWN, buff=0.1)
        mh_lab.next_to(nums, DOWN, buff=0.25).set_x(nl.n2p(e0)[0])
        pct = T(r"$\approx 70\%$ of a singlet's energy", font_size=36, color=DEFECT)
        pct.next_to(mh_lab, DOWN, buff=0.35).set_x(nl.n2p(e0)[0])
        phaseA = VGroup(header, chain, settled, nl, nums, m2, m2_lab, mh, mh_val, mh_lit,
                        mh_lab, pct)

        # phase B: the finite check fails; perturbation theory stops short
        row = FiniteCheckRow()
        fftag = tag_box("frustration-free only")
        rowg = VGroup(row, fftag).arrange(RIGHT, buff=0.6).move_to(UP * 2.3)
        cross = cross_mark(size=0.6, stroke=8).move_to(row.arrow)

        y_p = -1.25
        xH, xA = -2.3, 3.3
        pline = Line([-4.2, y_p, 0], [6.1, y_p, 0], color=DIM, stroke_width=2)
        fam = M(r"h+c\,h^2", font_size=38).next_to(pline, LEFT, buff=0.3)
        dH = Dot([xH, y_p, 0], radius=0.1, color=FG)
        dA = Dot([xA, y_p, 0], radius=0.1, color=FG)
        lH = VGroup(T("Heisenberg", font_size=30), M(r"c=0", font_size=34)).arrange(
            DOWN, buff=0.12).next_to(dH, UP, buff=0.6)
        # c = 1/3 written inline: full-size numerals, and both "c=" sit on one line
        lA = VGroup(T("AKLT", font_size=30), M(r"c=1/3", font_size=34)).arrange(
            DOWN, buff=0.12).next_to(dA, UP, buff=0.6)
        lA.align_to(lH, DOWN)
        disk = Ellipse(width=3.0, height=0.95, stroke_color=GAP, stroke_width=2.5,
                       fill_color=GAP, fill_opacity=0.18).move_to(dA)
        disk_l = T("proved gapped neighbourhood", font_size=30, color=GAP).next_to(
            disk, DOWN, buff=0.25)
        qH = T("?", font_size=64, color=DEFECT).next_to(dH, DOWN, buff=0.35)
        schem = inline_tag(TAG_SCHEMATIC, fam, DOWN, buff=0.45)
        # when the check is crossed out, its conclusion is no longer proved: the green
        # checks on the longer chains become open-question marks and the chains dim
        row_q = VGroup(*[T("?", font_size=40, color=DEFECT).move_to(c)
                         for c in row.checks])

        with self.voice("s04") as d:
            at, rt = self.cues("s04", d)
            self.play(FadeOut(self.s03_all), run_time=rt(0.4))
            # "The Heisenberg chain is not frustration-free:"
            self.play(Write(h1), FadeIn(chain, lag_ratio=0.1), run_time=rt(1.1))
            at(1.7)
            self.play(Create(sep), FadeIn(h2, shift=0.1 * LEFT), run_time=rt(0.6))
            # "each bond would love to be a singlet,"
            at(3.25)
            self.play(GrowFromCenter(A, rate_func=rate_functions.ease_out_back),
                      run_time=rt(0.45))
            self.play(FadeIn(slab, shift=0.1 * UP), run_time=rt(0.4))
            # "at energy minus two,"
            at(5.0)
            self.play(Create(nl), FadeIn(nums), run_time=rt(0.6))
            self.play(GrowFromCenter(m2), FadeIn(m2_lab[0], shift=0.2 * DOWN),
                      FadeIn(m2_lab[1], shift=0.2 * DOWN), run_time=rt(0.7))
            # "but a spin cannot be in a singlet with both neighbors,"
            for new, old, shared, t in ((B, A, 3, 7.15), (C, B, 4, 8.45)):
                at(t)
                self.play(GrowFromCenter(new, rate_func=rate_functions.ease_out_back),
                          Indicate(chain[shared], color=DEFECT, scale_factor=1.25),
                          run_time=rt(0.45))
                fade = [FadeOut(old, scale=1.15)]
                if old is A:
                    fade.append(FadeOut(slab))
                self.play(*fade, run_time=rt(0.4))
            # "so the ground state settles near minus 1.40 per bond."
            at(10.2)
            self.play(FadeOut(C), FadeIn(settled, lag_ratio=0.08), run_time=rt(0.7))
            self.play(GrowFromCenter(mh), FadeIn(mh_val, shift=0.1 * DOWN), FadeIn(mh_lit),
                      FadeIn(mh_lab, shift=0.1 * UP), run_time=rt(0.7))
            at(11.7)
            self.play(FadeIn(pct, scale=0.9), run_time=rt(0.5))
            # "That kills the finite check,"
            at(13.9)
            self.play(FadeOut(phaseA), run_time=rt(0.4))
            self.play(FadeIn(rowg), run_time=rt(0.4))
            self.play(Create(cross), ReplacementTransform(row.checks, row_q),
                      row.chains.animate.set_opacity(0.4), run_time=rt(0.5))
            # "and perturbation theory around A-K-L-T"
            at(16.2)
            self.play(Create(pline), FadeIn(fam), FadeIn(schem), run_time=rt(0.5))
            self.play(GrowFromCenter(dH), GrowFromCenter(dA), FadeIn(lH), FadeIn(lA),
                      run_time=rt(0.6))
            at(17.6)
            self.play(GrowFromCenter(disk, rate_func=rate_functions.ease_out_cubic),
                      run_time=rt(1.4))
            # "stops short of the Heisenberg point."
            self.play(FadeIn(disk_l, shift=0.1 * UP), run_time=rt(0.5))
            at(19.6)
            self.play(FadeIn(qH, scale=0.6), run_time=rt(0.4))
        # (row.checks were replaced by row_q; list the row's live parts explicitly)
        self.s04_all = VGroup(row.left, row.arrow, row.chains, row_q, fftag, cross, pline,
                              fam, schem, dH, dA, lH, lA, disk, disk_l, qH)

    # ---------------------------------------------------------------- s05
    def s05(self):
        head = T("the evidence", font_size=38, color=DIM).move_to(UP * 2.55)

        def evidence_card(year, line1, line2, icon, y):
            fr = panel(11.6, 1.95, DIM, stroke=2, fill_opacity=0.04)
            yr = M(year, font_size=54)
            txt = VGroup(line1, line2).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            yr.move_to(fr.get_left() + RIGHT * 1.15)
            txt.next_to(yr, RIGHT, buff=0.6)
            icon.move_to(fr.get_right() + LEFT * 1.35)
            return VGroup(fr, yr, txt, icon).move_to(UP * y)

        # icon 1: neutrons scattering off a chain (schematic)
        ch = mini_chain(6, spacing=0.3, r=0.07)
        n_in = Arrow([-0.95, 0.75, 0], [-0.1, 0.12, 0], buff=0, color=DIM, stroke_width=3,
                     max_tip_length_to_length_ratio=0.25)
        n_out = Arrow([0.25, 0.12, 0], [1.05, 0.7, 0], buff=0, color=DIM, stroke_width=3,
                      max_tip_length_to_length_ratio=0.25)
        nl = M("n", font_size=30, color=DIM).next_to(n_in.get_start(), LEFT, buff=0.08)
        ch.move_to([0.05, -0.05, 0])
        icon1 = VGroup(ch, n_in, n_out, nl)
        l1a = T(r"neutron scattering on CsNiCl$_3$", font_size=34)
        l1b = T(r"Buyers \textit{et al.}", font_size=30, color=DIM)
        card1 = evidence_card("1986", l1a, l1b, icon1, 0.65)

        # icon 2: a gapped level diagram
        lv = level_diagram([0, 0.75, 0.88, 1.0], width=1.0, color=FG)
        br = gap_brace(lv[0], lv[1], label=r"\Delta")
        icon2 = VGroup(lv, br)
        l2a = M(r"\text{DMRG:}\quad \Delta=0.41050(2)", font_size=36)
        l2b = T(r"White--Huse", font_size=30, color=DIM)
        card2 = evidence_card("1993", l2a, l2b, icon2, -1.75)
        lit = literature_label(l2a, RIGHT, buff=0.25)
        val = l2a[0][-10:]   # "0.41050(2)"

        with self.voice("s05") as d:
            at, rt = self.cues("s05", d)
            self.play(FadeOut(self.s04_all), run_time=rt(0.4))
            # "Physicists, meanwhile, stopped doubting."
            self.play(FadeIn(head, shift=0.1 * DOWN), run_time=rt(0.7))
            # "Neutrons saw the gap in cesium nickel chloride in 1986,"
            at(3.1)
            self.play(FadeIn(card1, shift=2.5 * LEFT), run_time=rt(0.8))
            # "and in 1993,"
            at(7.27)
            self.play(FadeIn(card2, shift=2.5 * LEFT), run_time=rt(0.8))
            # "D-M-R-G pinned it at 0.4105."
            at(9.0)
            self.play(FadeIn(lit), run_time=rt(0.5))
            at(10.3)
            self.play(Circumscribe(val, color=GAP, buff=0.08), run_time=rt(1.2))
        self.s05_all = VGroup(head, card1, card2, lit)

    # ---------------------------------------------------------------- s06
    def s06(self):
        card = panel(12.6, 5.5, DIM, stroke=2, fill_opacity=0.04).move_to(UP * 0.15)
        head = T(r"Tasaki 2024 (PRL 2025)", font_size=40).move_to(UP * 2.4)

        n = 7
        xs = [0.95 * (j - (n - 1) / 2) for j in range(n)]
        y_c = 1.0
        sites = VGroup(*[Circle(radius=0.2, stroke_color=INTEGER, stroke_width=3)
                         .move_to([x, y_c, 0]) for x in xs])
        links = VGroup(*[Line([a + 0.2, y_c, 0], [b - 0.2, y_c, 0], color=DIM, stroke_width=2)
                         for a, b in zip(xs[:-1], xs[1:])])
        fields = VGroup()
        for x in (xs[0], xs[-1]):
            ar = Arrow([x, y_c + 0.3, 0], [x, y_c + 0.98, 0], buff=0, color=FG, stroke_width=4,
                       max_tip_length_to_length_ratio=0.3)
            lab = M("h", font_size=34).next_to(ar, RIGHT if x > 0 else LEFT, buff=0.12)
            fields.add(VGroup(ar, lab))
        chain_l = T(r"odd open chain, field $h$ on both end spins", font_size=30, color=DIM)
        chain_l.next_to(sites, DOWN, buff=0.3)

        imp = MathTex(r"\text{uniform gap}", r"\ \Longrightarrow\ ",
                      r"\text{topologically nontrivial (index }{-1}\text{)}", font_size=38,
                      color=FG, tex_template=TEX_TEMPLATE).move_to(DOWN * 0.8)
        ul = Line(imp[0].get_corner(DL) + DOWN * 0.12, imp[0].get_corner(DR) + DOWN * 0.12,
                  color=DEFECT, stroke_width=4)
        qm = T("?", font_size=48, color=DEFECT).next_to(imp[0], UP, buff=0.12)
        chal = VGroup(T("challenge:", font_size=34, color=DIM),
                      T("a computer-aided proof of the gap", font_size=34)).arrange(
            RIGHT, buff=0.25).move_to(DOWN * 1.85)

        with self.voice("s06") as d:
            at, rt = self.cues("s06", d)
            self.play(FadeOut(self.s05_all), run_time=rt(0.4))
            # "In 2024,"
            self.play(Create(card), FadeIn(head, shift=0.1 * DOWN), run_time=rt(0.8))
            # "Hal Tasaki proved that if odd open chains"
            at(2.6)
            self.play(LaggedStart(*[GrowFromCenter(s) for s in sites], lag_ratio=0.1),
                      Create(links), run_time=rt(0.9))
            self.play(FadeIn(chain_l), run_time=rt(0.5))
            # "with a field on their end spins"
            at(4.4)
            self.play(*[GrowArrow(f[0]) for f in fields], *[FadeIn(f[1]) for f in fields],
                      run_time=rt(0.7))
            # "have a uniform gap,"
            at(6.3)
            self.play(Write(imp[0]), run_time=rt(0.8))
            # "the ground state is topologically nontrivial."
            at(7.8)
            self.play(Write(imp[1]), run_time=rt(0.4))
            self.play(Write(imp[2]), run_time=rt(1.6))
            at(10.3)
            self.play(Create(ul), FadeIn(qm, scale=0.6), run_time=rt(0.6))
            # "He named a computer-aided proof of that gap as the challenge."
            at(11.05)
            self.play(FadeIn(chal[0]), run_time=rt(0.4))
            self.play(Write(chal[1]), run_time=rt(1.5))
        self.s06_all = VGroup(card, head, sites, links, fields, chain_l, imp, ul, qm, chal)

    # ---------------------------------------------------------------- s07
    def s07(self):
        card = panel(12.0, 5.4, GAP, stroke=3, fill_opacity=0.04).move_to(DOWN * 0.05)
        head = T(r"Claimed theorem (periodic manuscript, Thm.~1.1)", font_size=38, color=GAP)
        head.move_to(UP * 1.95)
        line1 = M(r"\text{spin }1,\quad H_L=\sum_j\mathbf S_j\cdot\mathbf S_{j+1},"
                  r"\quad L\ \text{even}", font_size=40).move_to(UP * 0.85)
        lab2 = M(r"L\ge60{:}", font_size=40)
        # display-style \frac: \tfrac numerals at 40 fall under the 34-pt equation floor
        in2 = M(r"\gamma_L>\frac{4}{105}\log\frac{80}{79}", font_size=40)
        ap2 = M(r"\approx4.79\times10^{-4}", font_size=40, color=GAP)
        lab3 = M(r"L\ge2304{:}", font_size=40)
        in3 = M(r"\gamma_L>\frac{\log20}{784}", font_size=40)
        ap3 = M(r"\approx3.82\times10^{-3}", font_size=40, color=GAP)
        x_col = -1.75
        for lab, ineq, ap, y in ((lab2, in2, ap2, -0.42), (lab3, in3, ap3, -1.72)):
            lab.move_to([0, y, 0]).align_to([x_col - 0.45, 0, 0], RIGHT)
            ineq.move_to([0, y, 0]).align_to([x_col, 0, 0], LEFT)
            ap.next_to(ineq, RIGHT, buff=0.3)
        # vertically centre each row on its gamma
        for lab, ineq, ap in ((lab2, in2, ap2), (lab3, in3, ap3)):
            lab.set_y(ineq.get_y())
            ap.set_y(ineq.get_y())
        body = VGroup(line1, lab2, in2, ap2, lab3, in3, ap3)
        VGroup(body).set_x(0)
        self.s07_parts = dict(card=card, head=head, line1=line1, lab2=lab2, in2=in2, ap2=ap2,
                              lab3=lab3, in3=in3, ap3=ap3)

        with self.voice("s07") as d:
            at, rt = self.cues("s07", d)
            self.play(FadeOut(self.s06_all), run_time=rt(0.4))
            # "Here, precisely, is the claim."
            self.play(Create(card), Write(head), run_time=rt(1.3))
            # "For the spin one ring of every even length"
            at(2.8)
            self.play(Write(line1), run_time=rt(1.8))
            # "from 60 sites on,"
            at(5.0)
            self.play(FadeIn(lab2, shift=0.1 * RIGHT), run_time=rt(0.6))
            # "the gap exceeds 0.000479."
            at(6.4)
            self.play(Write(in2), run_time=rt(1.4))
            at(8.1)
            self.play(Write(ap2), run_time=rt(1.2))
            # "From two thousand three hundred and four sites on,"
            at(11.4)
            self.play(FadeIn(lab3, shift=0.1 * RIGHT), run_time=rt(0.6))
            # "it exceeds log 20 over 784,"
            at(13.4)
            self.play(Write(in3), run_time=rt(1.5))
            # "about 0.0038."
            at(16.5)
            self.play(Write(ap3), run_time=rt(1.1))

    # ---------------------------------------------------------------- s08
    def s08(self):
        p = self.s07_parts
        # pinned copy of the claim (top-left), legible size
        pin_head = T(r"Claimed theorem (periodic manuscript, Thm.~1.1)", font_size=28,
                     color=GAP)
        pin_box = panel(pin_head.width + 0.45, pin_head.height + 0.35, GAP, stroke=2.5,
                        fill_opacity=0.04, corner_radius=0.15)
        pin_head.move_to(pin_box)
        pin = VGroup(pin_box, pin_head).to_corner(UL, buff=0.45)   # inside x >= -6.7

        # horizontal log-scale bars, 10^-4 .. 10^0
        x0, dec = -2.9, 2.0
        X = lambda v: x0 + (np.log10(v) + 4) * dec
        y_ax, rows = -0.85, {"true": 1.45, "2304": 0.55, "60": -0.35}
        bh = 0.34
        axis = Line([x0 - 0.1, y_ax, 0], [X(1) + 0.15, y_ax, 0], color=DIM, stroke_width=2)
        ticks = VGroup(*[Line([X(10.0 ** k), y_ax - 0.07, 0], [X(10.0 ** k), y_ax + 0.07, 0],
                              color=DIM, stroke_width=2) for k in range(-4, 1)])
        tlabs = VGroup(*[M(f"10^{{{k}}}", font_size=30, color=DIM).next_to(
            [X(10.0 ** k), y_ax, 0], DOWN, buff=0.2) for k in range(-4, 1)])
        xlab = T("gap", font_size=30, color=DIM).next_to(axis, RIGHT, buff=0.25)

        def bar(v, y, hollow=False):
            w = X(v) - x0
            r = Rectangle(width=w, height=bh)
            if hollow:
                r.set_stroke(INTEGER, 3).set_fill(opacity=0)
            else:
                r.set_stroke(width=0).set_fill(GAP, 0.85)
            return r.move_to([x0 + w / 2, y, 0])

        v60, v2304, vtrue = 4 / 105 * np.log(80 / 79), np.log(20) / 784, 0.4105
        b60, b2304, btrue = bar(v60, rows["60"]), bar(v2304, rows["2304"]), \
            bar(vtrue, rows["true"], hollow=True)
        val60 = M(r"4.79\times10^{-4}", font_size=32, color=GAP).next_to(
            [X(v60), rows["60"] + bh / 2, 0], UP, buff=0.12)
        val2304 = M(r"3.82\times10^{-3}", font_size=32, color=GAP).next_to(
            [X(v2304), rows["2304"] + bh / 2, 0], UP, buff=0.12)
        valtrue = M(r"0.4105", font_size=32).next_to([X(vtrue), rows["true"] + bh / 2, 0], UP,
                                                     buff=0.12)
        littrue = literature_label(valtrue, RIGHT, buff=0.15)
        rl = lambda s, y: T(s, font_size=30).move_to([0, y, 0]).align_to([x0 - 0.35, 0, 0], RIGHT)
        rlab = VGroup(rl("true gap", rows["true"]), rl(r"bound, $L\ge2304$", rows["2304"]),
                      rl(r"bound, $L\ge60$", rows["60"]))
        guide = DashedLine([X(vtrue), rows["true"] - bh / 2, 0], [X(vtrue), y_ax, 0],
                           color=DIM, stroke_width=2, dash_length=0.08)

        def gap_arrow(v, y, txt):
            a = DoubleArrow([X(v) + 0.05, y, 0], [X(vtrue) - 0.05, y, 0], buff=0, color=FG,
                            stroke_width=2.5, tip_length=0.16)
            t = M(txt, font_size=34).next_to(a, UP, buff=0.12)
            return VGroup(a, t)

        ar2304 = gap_arrow(v2304, rows["2304"], r"\times107")
        ar60 = gap_arrow(v60, rows["60"], r"\times857")
        uniq = T(r"unique ground state on even rings: classical (Marshall--Lieb--Mattis)",
                 font_size=30, color=DIM).move_to(DOWN * 2.15)
        unif = T(r"uniformity in $L$", font_size=54, color=GAP).move_to(DOWN * 3.05)
        bub = objection_bubble("finite")

        with self.voice("s08") as d:
            at, rt = self.cues("s08", d)
            # clear the theorem body first, then shrink the card into the pinned copy
            # (the two bounds reappear as the bars' labels)
            self.play(FadeOut(VGroup(p["line1"], p["lab2"], p["in2"], p["ap2"], p["lab3"],
                                     p["in3"], p["ap3"])), run_time=rt(0.25))
            self.play(ReplacementTransform(p["card"], pin_box),
                      ReplacementTransform(p["head"], pin_head), run_time=rt(0.45))
            # "That is about a hundred times below the true 0.41:"
            self.play(Create(axis), FadeIn(ticks), FadeIn(tlabs), FadeIn(xlab), FadeIn(rlab),
                      run_time=rt(0.4))
            self.play(GrowFromEdge(b60, LEFT), GrowFromEdge(b2304, LEFT),
                      GrowFromEdge(btrue, LEFT), FadeIn(val60), FadeIn(val2304),
                      FadeIn(valtrue), FadeIn(littrue), Create(guide), run_time=rt(0.5))
            self.play(LaggedStart(AnimationGroup(GrowFromCenter(ar2304[0]), FadeIn(ar2304[1])),
                                  AnimationGroup(GrowFromCenter(ar60[0]), FadeIn(ar60[1])),
                                  lag_ratio=0.5), run_time=rt(0.6))
            # "... the true 0.41"
            at(2.75)
            self.play(Indicate(valtrue, color=FG, scale_factor=1.1),
                      Indicate(ar2304[1], color=FG, scale_factor=1.2), run_time=rt(0.8))
            # "the claim is that a gap exists,"
            at(4.3)
            self.play(Indicate(b60, color=GAP, scale_factor=1.06),
                      Indicate(b2304, color=GAP, scale_factor=1.06), run_time=rt(0.9))
            # "not its size."
            at(6.0)
            self.play(Indicate(ar2304[1], color=FG, scale_factor=1.2),
                      Indicate(ar60[1], color=FG, scale_factor=1.2), run_time=rt(0.8))
            # "Uniqueness of the ground state on even rings is classical,
            #  from Marshall, Lieb and Mattis."
            at(7.4)
            self.play(Write(uniq), run_time=rt(2.0))
            # the objection pops in on the pause before "The new content is uniformity."
            at(12.9)
            self.play(bubble_in(bub), run_time=rt(0.5))
            at(13.45)
            self.play(Write(unif), bubble_indicate(bub), run_time=rt(0.9))
            self.play(bubble_check(bub), run_time=rt(0.5))
