"""ch02: Haldane's picture, and why it is not a proof.

Segments (script/narration.json):
  s01 timeline: Bethe 1931, des Cloizeaux-Pearson inset (1962), Haldane 1981/83
  s02 Berry phase of one spin: arrow on the sphere sweeps a cap of solid angle
  s03 antiferromagnet: neighbouring solid angles nearly cancel -> theta Q
  s04 O(3) sigma model + topological term; theta = pi phasors interfere
  s05 theta = 0 (mod 2 pi) phasors add; schematic RG flow; Delta ~ e^{-pi S}
  s06 why it is not a proof (three DIM crosses) + objection bubble (b)
  s07 the space-time sheet with glued edges becomes the bare L x beta torus
"""
from motifs import *  # noqa: F401,F403  (also visuals.* and common.*)

# reference clip lengths used to place the phrase cues below (seconds); cues
# are rescaled by d / REF[seg] so they stay in sync if a clip is re-generated
REF = {"s01": 13.025, "s02": 10.25, "s03": 16.175, "s04": 17.275,
       "s05": 11.625, "s06": 16.475, "s07": 9.3}


# ====================================================================== helpers
def Tm(*parts, **kw):
    """Multi-part T() (common.T takes one string)."""
    kw.setdefault("color", FG)
    return Tex(*parts, tex_template=TEX_TEMPLATE, **kw)


def Mm(*parts, **kw):
    """Multi-part M() (common.M takes one string)."""
    kw.setdefault("color", FG)
    return MathTex(*parts, tex_template=TEX_TEMPLATE, **kw)


def short_arrow(start, end, color=FG, stroke=4, tip=0.16):
    """Arrow whose tip keeps a readable size even when the arrow is short."""
    return Arrow(np.array(start, dtype=float), np.array(end, dtype=float), buff=0,
                 color=color, stroke_width=stroke, tip_length=tip,
                 max_tip_length_to_length_ratio=0.6,
                 max_stroke_width_to_length_ratio=40)


# ---------------------------------------------------------------- s01 timeline
TL_Y = -3.0


def year_x(year):
    """Timeline from 1930 (x = -6) to 2030 (x = +6)."""
    return -6.0 + 12.0 * (year - 1930) / 100.0


def timeline():
    line = Line([-6.3, TL_Y, 0], [6.3, TL_Y, 0], color=DIM, stroke_width=2)
    ticks, labels = VGroup(), VGroup()
    for yr in range(1930, 2031, 20):
        x = year_x(yr)
        ticks.add(Line([x, TL_Y - 0.09, 0], [x, TL_Y + 0.09, 0], color=DIM, stroke_width=2))
        labels.add(T(str(yr), font_size=24, color=DIM).move_to([x, TL_Y - 0.36, 0]))
    return VGroup(line, ticks, labels)


def event_dot(year):
    return Dot([year_x(year), TL_Y, 0], radius=0.07, color=FG)


def dispersion_inset():
    """E(k) = (pi/2)|sin k| on [0, pi] (des Cloizeaux-Pearson 1962), HALF."""
    ax = Axes(x_range=[0, PI, PI], y_range=[0, 1.9, 1], x_length=3.2, y_length=1.6,
              tips=False, axis_config={"color": DIM, "stroke_width": 2,
                                       "include_ticks": False})
    curve = ax.plot(lambda k: PI / 2 * abs(np.sin(k)), x_range=[0, PI, 0.02],
                    color=HALF, stroke_width=4)
    xl = M("k", font_size=28, color=DIM).next_to(ax.x_axis, RIGHT, buff=0.12)
    yl = M("E", font_size=28, color=DIM).next_to(ax.y_axis, UP, buff=0.1)
    # buff 0.2: clear of the HALF zero dots (radius 0.07) drawn on top of them
    t0 = M("0", font_size=24, color=DIM).next_to(ax.c2p(0, 0), DOWN, buff=0.2)
    tpi = M(r"\pi", font_size=24, color=DIM).next_to(ax.c2p(PI, 0), DOWN, buff=0.2)
    zeros = VGroup(Dot(ax.c2p(0, 0), radius=0.07, color=HALF),
                   Dot(ax.c2p(PI, 0), radius=0.07, color=HALF))
    cap = T(r"gapless \,(des Cloizeaux--Pearson 1962)", font_size=24, color=DIM)
    cap.next_to(VGroup(ax, t0), DOWN, buff=0.18)
    g = VGroup(ax, curve, xl, yl, t0, tpi, zeros, cap)
    g.ax, g.curve, g.zeros, g.cap = ax, curve, zeros, cap
    g.frame = VGroup(ax, xl, yl, t0, tpi)
    return g


def preprint_card():
    head = T(r"\textit{preprint}", font_size=24, color=DIM)
    title = T("Haldane, 1981", font_size=28)
    claim = T(r"integer spins: gapped", font_size=28, color=INTEGER)
    stack = VGroup(head, title, claim).arrange(DOWN, buff=0.12)
    w = stack.width + 0.6
    lines = VGroup(*[Line(ORIGIN, RIGHT * (w - 0.6 - dl), color=FAINT, stroke_width=4)
                     for dl in (0.0, 0.25, 0.1, 0.55)]).arrange(DOWN, buff=0.17, aligned_edge=LEFT)
    content = VGroup(stack, lines).arrange(DOWN, buff=0.24)
    lines.align_to(stack, LEFT)
    box = RoundedRectangle(width=w, height=content.height + 0.45, corner_radius=0.08,
                           stroke_color=FG, stroke_width=2, fill_color=BG, fill_opacity=1)
    box.move_to(content)
    g = VGroup(box, content)
    g.box, g.lines = box, lines
    return g


def stamp(text="rejected", angle=10 * DEGREES):
    t = T(r"\textbf{" + text + "}", font_size=28, color=DIM)
    box = RoundedRectangle(width=t.width + 0.34, height=t.height + 0.24, corner_radius=0.06,
                           stroke_color=DIM, stroke_width=3, fill_color=BG, fill_opacity=1)
    box.move_to(t)
    return VGroup(box, t).rotate(angle)


# ---------------------------------------------------------------- s02 sphere
ELEV = np.arcsin(0.7 / 3.2)      # viewing elevation: equator ellipse 3.2 x 0.7


def proj(v, center, R):
    """Orthographic view of a unit vector v = (x right, y toward viewer, z up)."""
    x, y, z = v
    return np.array(center) + R * np.array([x, z * np.cos(ELEV) - y * np.sin(ELEV), 0.0])


class BerrySphere(VGroup):
    """Sphere outline, dashed equator, a loop traced by the tip of n, its cap."""

    def __init__(self, center=(-3.3, -0.4, 0), R=1.8, axis=(0.5, 0.45, 0.72), alpha=0.42):
        super().__init__()
        self.c, self.R = np.array(center, dtype=float), R
        a = np.array(axis, dtype=float)
        a /= np.linalg.norm(a)
        u = np.cross(a, [0, 0, 1.0])
        u /= np.linalg.norm(u)
        w = np.cross(a, u)
        self._loop = lambda t: np.cos(alpha) * a + np.sin(alpha) * (
            np.cos(t) * u + np.sin(t) * w)
        self.circle = Circle(radius=R, stroke_color=FG, stroke_width=2.5,
                             fill_color=FG, fill_opacity=0.04).move_to(self.c)
        self.equator = DashedVMobject(
            Ellipse(width=2 * R, height=2 * R * np.sin(ELEV), stroke_color=DIM,
                    stroke_width=2).move_to(self.c), num_dashes=40)
        self.center_dot = Dot(self.c, radius=0.05, color=FG)
        self.path = ParametricFunction(lambda t: self.screen(t), t_range=[0, TAU, TAU / 120],
                                       color=TIME, stroke_width=4)
        pts = [self.screen(t) for t in np.linspace(0, TAU, 121)]
        self.cap = VMobject(stroke_width=0, fill_color=DEFECT, fill_opacity=0.3)
        self.cap.set_points_as_corners(pts)
        self.add(self.circle, self.equator, self.center_dot)

    def screen(self, t):
        return proj(self._loop(t), self.c, self.R)

    def arrow_at(self, t):
        return Arrow(self.c, self.screen(t), buff=0, color=FG, stroke_width=5,
                     max_tip_length_to_length_ratio=0.18)


# ---------------------------------------------------------------- s03 / s07 textures
def field_glyph(n, point, scale=0.32, color=FG):
    """2D picture of a unit vector n at `point`: an in-plane arrow of length
    ~ |n_perp|; a nearly out-of-plane vector is a dot (up) or a circled cross (down)."""
    nx, ny, nz = n
    perp = np.hypot(nx, ny)
    p = np.array(point, dtype=float)
    if perp < 0.28:
        if nz > 0:
            return Dot(p, radius=0.035, color=color)
        r = 0.07
        return VGroup(Circle(radius=r, stroke_color=color, stroke_width=2).move_to(p),
                      Line(p + r * 0.7 * (UL), p + r * 0.7 * DR, color=color, stroke_width=2),
                      Line(p + r * 0.7 * UR, p + r * 0.7 * DL, color=color, stroke_width=2))
    d = np.array([nx, ny, 0.0]) * scale
    return short_arrow(p - d / 2, p + d / 2, color=color, stroke=3, tip=0.1)


def skyrmion_n(x, y, R):
    r = np.hypot(x, y)
    f = PI * (1 - r / R) if r < R else 0.0
    ph = np.arctan2(y, x)
    return np.array([np.sin(f) * np.cos(ph), np.sin(f) * np.sin(ph), np.cos(f)])


def skyrmion_grid(nx=7, ny=7, spacing=0.38, R=1.45, center_off=(0, 0), scale=0.32):
    g = VGroup()
    for i in range(nx):
        for j in range(ny):
            x = spacing * (i - (nx - 1) / 2)
            y = spacing * (j - (ny - 1) / 2)
            n = skyrmion_n(x - center_off[0], y - center_off[1], R)
            g.add(field_glyph(n, [x, y, 0], scale=scale))
    return g


def sheet_axes(box, xlab="x", tlab=r"\tau", buff=0.25, font_size=32):
    """SPACE arrow under `box` (x), TIME arrow left of it (tau)."""
    L, R, B, Tp = box.get_left()[0], box.get_right()[0], box.get_bottom()[1], box.get_top()[1]
    ax_x = Arrow([L, B - buff, 0], [R, B - buff, 0], buff=0, color=SPACE, stroke_width=3,
                 max_tip_length_to_length_ratio=0.08)
    ax_t = Arrow([L - buff, B, 0], [L - buff, Tp, 0], buff=0, color=TIME, stroke_width=3,
                 max_tip_length_to_length_ratio=0.08)
    lx = M(xlab, color=SPACE, font_size=font_size).next_to(ax_x, DOWN, buff=0.1)
    lt = M(tlab, color=TIME, font_size=font_size).next_to(ax_t, LEFT, buff=0.12)
    return VGroup(ax_x, ax_t, lx, lt)


# ---------------------------------------------------------------- s04 / s05 phasors
PHASOR_LENGTHS = (1.0, 0.6, 0.35, 0.2)        # schematic sector weights Z_0..Z_3


class PhasorRow(VGroup):
    """Sector phasors e^{i theta Q} Z_Q laid head to tail (small downward steps
    so that arrows pointing back stay visible), plus the resultant Z below."""

    def __init__(self, signs, color, x0, y0, unit=1.7, dy=0.27):
        super().__init__()
        self.arrows, self.links = VGroup(), VGroup()
        x = x0
        for k, (s, ln) in enumerate(zip(signs, PHASOR_LENGTHS)):
            y = y0 - k * dy
            if k > 0:
                self.links.add(DashedLine([x, y + dy, 0], [x, y, 0], color=DIM,
                                          stroke_width=1.5, dash_length=0.04))
            self.arrows.add(short_arrow([x, y, 0], [x + s * ln * unit, y, 0], color=color,
                                        stroke=4.5, tip=0.17))
            x += s * ln * unit
        yr = y0 - len(signs) * dy - 0.22
        self.drop = DashedLine([x, y0 - (len(signs) - 1) * dy, 0], [x, yr, 0], color=DIM,
                               stroke_width=1.5, dash_length=0.05)
        self.result = short_arrow([x0, yr, 0], [x, yr, 0], color=color, stroke=8, tip=0.22)
        self.zlab = M("Z", color=color, font_size=34).next_to(self.result, RIGHT, buff=0.15)
        self.start_tick = Line([x0, y0 + 0.15, 0], [x0, yr - 0.15, 0], color=DIM,
                               stroke_width=1.5)
        self.add(self.start_tick, self.arrows, self.links, self.drop, self.result, self.zlab)

    def build(self, run_time=1.6):
        anims = []
        for k, a in enumerate(self.arrows):
            if k > 0:
                anims.append(Create(self.links[k - 1], run_time=0.15))
            anims.append(GrowArrow(a, run_time=0.35))
        return Succession(FadeIn(self.start_tick, run_time=0.2), *anims,
                          run_time=run_time)

    def resolve(self, **kw):
        return AnimationGroup(Create(self.drop), GrowArrow(self.result),
                              FadeIn(self.zlab, shift=0.1 * RIGHT), lag_ratio=0.3, **kw)


def hedgehog_icon(r=0.19):
    """Tiny 'one unit of winding' glyph in the s03 skyrmion's own vocabulary:
    a circled cross at the core (n down), a ring of outward arrows, and up-dots
    outside (n up) -- the Q = 1 texture in miniature."""
    rc = 0.045
    p = ORIGIN
    g = VGroup(Circle(radius=rc, stroke_color=FG, stroke_width=1.5).move_to(p),
               Line(p + rc * 0.7 * UL, p + rc * 0.7 * DR, color=FG, stroke_width=1.5),
               Line(p + rc * 0.7 * UR, p + rc * 0.7 * DL, color=FG, stroke_width=1.5))
    for k in range(8):
        u = np.array([np.cos(TAU * k / 8), np.sin(TAU * k / 8), 0.0])
        g.add(short_arrow(u * 0.07, u * (r - 0.02), color=FG, stroke=2, tip=0.055))
    for k in range(4):
        u = np.array([np.cos(TAU * (k + 0.5) / 4), np.sin(TAU * (k + 0.5) / 4), 0.0])
        g.add(Dot(u * (r + 0.02), radius=0.018, color=FG))
    return g


def sector_thumbs(side=1.0):
    """Winding sectors Q = 0..3 as small sheets holding Q hedgehogs (schematic)."""
    spots = {0: [], 1: [(0, 0)], 2: [(-0.22, 0.2), (0.22, -0.2)],
             3: [(-0.24, 0.22), (0.24, 0.18), (0.0, -0.24)]}
    out = VGroup()
    for Q in range(4):
        box = Square(side_length=side, stroke_color=DIM, stroke_width=2,
                     fill_color=FG, fill_opacity=0.04)
        icons = VGroup(*[hedgehog_icon().move_to([x, y, 0]) for x, y in spots[Q]])
        lab = M(f"Q={Q}", font_size=30, color=DIM).next_to(box, DOWN, buff=0.15)
        g = VGroup(box, icons, lab)
        g.sheet, g.lab = (VGroup(box, icons) if Q else VGroup(box)), lab
        out.add(g)
    return out.arrange(RIGHT, buff=0.5)


def row_label(top, bottom, color):
    a = T(top, font_size=28, color=color)
    b = M(bottom, font_size=34, color=color)
    return VGroup(a, b).arrange(DOWN, aligned_edge=LEFT, buff=0.14)


# ---------------------------------------------------------------- s05 RG sketch
def rg_sketch():
    ax = Axes(x_range=[0, 24, 4], y_range=[0, 1.8, 1], x_length=3.8, y_length=2.4,
              tips=True, axis_config={"color": DIM, "stroke_width": 2,
                                      "include_ticks": False,
                                      "tip_width": 0.16, "tip_height": 0.16})
    g0 = 0.25
    lmax = 2 * PI * (1 - g0 / 1.7) / g0
    curve = ax.plot(lambda l: g0 / (1 - g0 * l / (2 * PI)), x_range=[0, lmax, 0.05],
                    color=INTEGER, stroke_width=4)
    lxi = 2 * PI * (1 - g0) / g0
    vline = DashedLine(ax.c2p(lxi, 0), ax.c2p(lxi, 1.75), color=DIM, stroke_width=2)
    hline = DashedLine(ax.c2p(0, 1), ax.c2p(lxi, 1), color=FAINT, stroke_width=2)
    one = M("1", font_size=24, color=DIM).next_to(ax.c2p(0, 1), LEFT, buff=0.12)
    xi = M(r"\ell\sim\xi", font_size=30).next_to(ax.c2p(lxi, 0), DOWN, buff=0.14)
    xl = M(r"\log\ell", font_size=30, color=DIM).next_to(ax.x_axis.get_end(), RIGHT, buff=0.12)
    yl = M("g", font_size=32, color=DIM).next_to(ax.y_axis.get_end(), LEFT, buff=0.14)
    g = VGroup(ax, xl, yl, one, hline, curve, vline, xi)
    g.ax, g.curve, g.vline, g.xi, g.hline, g.one = ax, curve, vline, xi, hline, one
    g.frame = VGroup(ax, xl, yl)
    return g


# ====================================================================== scene
class Ch02(NarratedScene):
    CHAPTER = "ch02"

    # -- cue helpers -------------------------------------------------------
    def _start(self, seg, d):
        self._t0 = self.renderer.time
        self._k = d / REF[seg]

    def at(self, sec):
        """Wait until `sec` (reference seconds into the current clip)."""
        dt = self._t0 + sec * self._k - self.renderer.time
        if dt > 1 / 30:
            self.wait(dt)
        elif dt < -0.15:
            print(f"[ch02] cue {sec:.2f}s is late by {-dt:.2f}s")

    def construct(self):
        self.s01()
        self.s02()
        self.s03()
        self.s04_05()
        self.s06()
        self.s07()

    # ------------------------------------------------------------------ s01
    def s01(self):
        with self.voice("s01") as d:
            self._start("s01", d)
            tl = timeline()
            self.play(Create(tl[0]), FadeIn(tl[1]), FadeIn(tl[2], shift=0.1 * UP),
                      run_time=1.0)

            # "Bethe solved the spin one-half chain exactly"
            dot31 = event_dot(1931)
            bethe = VGroup(T("Bethe, 1931", font_size=28),
                           Tm(r"spin $\tfrac12$", r" solved exactly", font_size=28))
            bethe[1][0].set_color(HALF)
            bethe.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
            bethe.move_to([-6.4, TL_Y + 0.55, 0], aligned_edge=DL)
            stem31 = Line(dot31.get_center(), [year_x(1931), TL_Y + 0.47, 0],
                          color=DIM, stroke_width=2)
            self.at(1.9)
            self.play(GrowFromCenter(dot31), Create(stem31), run_time=0.4)
            self.play(FadeIn(bethe, shift=0.15 * UP), run_time=0.8)

            # "it is gapless."  (inset belongs to 1962, not to the 1931 label)
            inset = dispersion_inset()
            inset.shift(np.array([-3.85, 0.55, 0]) - inset.ax.c2p(0, 0))
            dot62 = event_dot(1962)
            stem62 = Line(dot62.get_center(), [year_x(1962), inset.cap.get_bottom()[1] - 0.08, 0],
                          color=DIM, stroke_width=2)
            self.at(4.4)
            self.play(GrowFromCenter(dot62), Create(stem62), FadeIn(inset.frame),
                      run_time=0.4)
            self.play(Create(inset.curve), FadeIn(inset.cap), run_time=0.75)
            self.play(LaggedStart(*[Flash(z, color=HALF, line_length=0.14, flash_radius=0.16)
                                    for z in inset.zeros], lag_ratio=0.2),
                      FadeIn(inset.zeros), run_time=0.5)

            # "Haldane's claim that integer spins differ"
            dot81 = event_dot(1981)
            card = preprint_card()
            card.move_to([year_x(1981) + 0.2, TL_Y + 0.55, 0], aligned_edge=DOWN)
            stem81 = Line(dot81.get_center(), [year_x(1981), card.get_bottom()[1], 0],
                          color=DIM, stroke_width=2)
            self.at(6.2)
            self.play(GrowFromCenter(dot81), Create(stem81), run_time=0.35)
            self.play(FadeIn(card, shift=0.2 * UP), run_time=0.8)

            # "was rejected by several journals"
            # spread so the two stamps meet only at a corner (no letters hidden)
            lc = card.box.get_center()[0], card.lines.get_center()[1]
            st1 = stamp(angle=9 * DEGREES).move_to([lc[0] - 0.74, lc[1] + 0.14, 0])
            st2 = stamp(angle=-7 * DEGREES).move_to([lc[0] + 0.76, lc[1] - 0.3, 0])
            self.at(8.2)
            self.play(FadeIn(st1, scale=1.8, rate_func=rate_functions.rush_into), run_time=0.35)
            self.wait(0.3)
            self.play(FadeIn(st2, scale=1.8, rate_func=rate_functions.rush_into), run_time=0.35)

            # "and dubbed a conjecture"
            dot83 = event_dot(1983)
            pub = T("published, 1983", font_size=28)
            pub.move_to([2.7, TL_Y + 0.62, 0], aligned_edge=LEFT)
            lead83 = Line(dot83.get_center(), pub.get_left() + LEFT * 0.1 + DOWN * 0.08,
                          color=DIM, stroke_width=2)
            conj = T(r"``conjecture''", font_size=52)
            conj.next_to(pub, UP, buff=0.35).align_to(pub, LEFT).shift(LEFT * 0.1)
            self.at(10.25)
            self.play(GrowFromCenter(dot83), Create(lead83), FadeIn(pub, shift=0.1 * UP),
                      run_time=0.5)
            self.play(Write(conj), run_time=0.8)

            # "the name stuck."  -- the timeline itself brightens from 1983 to today
            # (drawn ON the axis, so it is not a second track and the 1983 leader
            # does not cross it)
            x26 = year_x(2026)
            stuck = Line([year_x(1983), TL_Y, 0], [x26, TL_Y, 0],
                         color=FG, stroke_width=4, stroke_opacity=0.8)
            o26 = open_circle(radius=0.1, color=FG).move_to([x26, TL_Y, 0])
            l26 = T("2026", font_size=24, color=DIM).next_to(o26, UP, buff=0.3)
            self.at(11.7)
            self.add(stuck)
            self.bring_to_front(dot83, lead83)
            self.play(Create(stuck), Indicate(conj, color=FG, scale_factor=1.06),
                      run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
            self.play(Create(o26), FadeIn(l26), run_time=0.35)

    # ------------------------------------------------------------------ s02
    def s02(self):
        with self.voice("s02") as d:
            self._start("s02", d)
            self.play(FadeOut(*self.mobjects), run_time=0.45)

            # "If you learned it from Altland and Simons:"
            src = tag(r"Altland \& Simons, Condensed Matter Field Theory", corner=UL,
                      buff=0.42)     # 0.42: keeps |x| <= 6.7
            self.play(tag_in(src), run_time=0.6)

            # "in the spin path integral,"
            sph = BerrySphere()
            arr = sph.arrow_at(0)
            eq1 = M(r"\mathbf S(\tau)=S\,\mathbf n(\tau)", font_size=48).move_to([3.3, 1.25, 0])
            self.at(1.3)
            self.play(Create(sph.circle), Create(sph.equator), FadeIn(sph.center_dot),
                      run_time=1.2)
            # bold n riding beside the shaft (left side, lower third: clear of the
            # loop traced by the tip, and of the cap that later fills it)
            def n_pos(t):
                v = sph.screen(t) - sph.c
                u = v / np.linalg.norm(v)
                return sph.c + 0.35 * v + 0.36 * np.array([-u[1], u[0], 0.0])

            nlab = M(r"\mathbf n", font_size=34).move_to(n_pos(0))
            self.at(2.9)
            self.play(GrowArrow(arr), FadeIn(nlab), Write(eq1), run_time=0.9)

            # "each spin picks up a Berry phase,"
            tt = ValueTracker(0)
            arr.add_updater(lambda m: m.become(sph.arrow_at(tt.get_value())))
            nlab.add_updater(lambda m: m.move_to(n_pos(tt.get_value())))
            eq2 = M(r"e^{\,iS\,\Omega[\mathbf n]}", font_size=64)
            omega = eq2[0][3]
            omega.set_color(DEFECT)
            eq2.move_to([3.3, -0.45, 0])
            berry = T("Berry phase", font_size=30, color=DIM).next_to(eq2, DOWN, buff=0.3)
            self.at(4.45)
            self.play(tt.animate.set_value(TAU), Create(sph.path), run_time=1.75,
                      rate_func=rate_functions.linear)
            arr.clear_updaters()
            nlab.clear_updaters()
            self.play(FadeIn(eq2, shift=0.15 * UP), FadeIn(berry), run_time=0.5)

            # "S times the solid angle its arrow sweeps on the sphere."
            lab = VGroup(T("solid angle", font_size=30), M(r"\Omega", color=DEFECT, font_size=36))
            lab.arrange(RIGHT, buff=0.15).move_to([-0.3, 2.3, 0])
            cap_c = sph.cap.get_center()
            ptr = Arrow(lab.get_left() + LEFT * 0.08 + DOWN * 0.08, cap_c + np.array([0.16, 0.24, 0]),
                        buff=0.0, color=DIM, stroke_width=2.5,
                        max_tip_length_to_length_ratio=0.12)
            self.at(6.75)
            self.add(sph.cap)
            self.bring_to_front(sph.path, arr, nlab)
            self.play(FadeIn(sph.cap), run_time=0.8)
            self.play(FadeIn(lab, shift=0.1 * LEFT), GrowArrow(ptr), run_time=0.7)
            self.play(Indicate(omega, color=DEFECT, scale_factor=1.3), run_time=0.8)

    # ------------------------------------------------------------------ s03
    def s03(self):
        with self.voice("s03") as d:
            self._start("s03", d)
            self.play(FadeOut(*self.mobjects), run_time=0.4)

            # "In an antiferromagnet,"
            chain = spin_chain(10, spacing=0.9, staggered=True, tilt=0.15)
            chain.move_to([0, 0.75, 0])
            self.play(LaggedStart(*[GrowArrow(a) for a in chain], lag_ratio=0.08),
                      run_time=1.0)

            # "neighbors point opposite ways,"
            f1 = M(r"\mathbf S_j\approx S\big[(-1)^j\,\mathbf n(x_j)+\mathbf L(x_j)\big]",
                   font_size=40).move_to([0, 2.55, 0])
            self.at(1.7)
            self.play(Write(f1), run_time=1.3)

            # "and their Berry phases nearly cancel."
            xs = [a.get_center()[0] for a in chain]
            yd, rd = -0.75, 0.3
            plus = VGroup(*[Circle(radius=rd, stroke_color=DEFECT, stroke_width=2,
                                   fill_color=DEFECT, fill_opacity=0.45).move_to([xs[j], yd, 0])
                            for j in range(0, 10, 2)])
            minus = VGroup(*[Circle(radius=rd, stroke_color=DIM, stroke_width=2,
                                    fill_color=BG, fill_opacity=1).move_to([xs[j], yd, 0])
                             for j in range(1, 10, 2)])
            lp = M(r"+\Omega_j", font_size=30, color=DEFECT).next_to(plus[0], DOWN, buff=0.18)
            lm = M(r"-\Omega_{j+1}", font_size=30, color=DIM).next_to(minus[0], DOWN, buff=0.18)
            self.at(3.6)
            self.play(LaggedStart(*[AnimationGroup(FadeIn(p), FadeIn(m))
                                    for p, m in zip(plus, minus)], lag_ratio=0.1),
                      FadeIn(lp), FadeIn(lm), run_time=0.8)
            eps = 0.1
            slide = xs[1] - xs[0] - eps
            self.play(*[ApplyMethod(m.shift, LEFT * slide) for m in minus],
                      lm.animate.shift(LEFT * slide).set_opacity(0), lp.animate.set_opacity(0),
                      run_time=1.0)
            self.remove(lm, lp)

            # "Nearly."  -> thin leftover slivers
            slivers = VGroup(*[Difference(p, m, fill_color=DEFECT, fill_opacity=0.95,
                                          stroke_width=0) for p, m in zip(plus, minus)])
            left_lab = T("leftover", font_size=28, color=DEFECT)
            left_lab.next_to(slivers[0], DOWN, buff=0.35)
            self.at(6.0)
            self.remove(*plus, *minus)
            self.add(slivers)
            # label lands with the swap (short fade) so it reads before "What survives"
            # (different run_times in one play: rate functions clip at alpha = 1)
            self.play(LaggedStart(*[Indicate(s, color=DEFECT, scale_factor=1.6) for s in slivers],
                                  lag_ratio=0.08, run_time=0.9),
                      FadeIn(left_lab, shift=0.1 * UP, run_time=0.4))

            # "What survives is theta times Q,"
            f2 = Mm(r"S\sum_j(-1)^j\,", r"\Omega_j", r"\ \longrightarrow\ ", r"\theta\,Q",
                   font_size=48)
            f2[1].set_color(DEFECT)
            f2.move_to([0, 2.75, 0])
            # first clear the chain and f1 (f2 takes f1's place), then the leftover
            # crescents fly into the Omega_j glyph only; the rest of f2 is written
            self.at(7.4)
            self.play(FadeOut(chain), FadeOut(f1), FadeOut(left_lab), run_time=0.4)
            omega_c = f2[1].get_center()
            flights = []
            for s in slivers:
                tgt = s.copy().scale(0.2).move_to(omega_c).set_fill(opacity=0.0)
                flights.append(Transform(s, tgt, rate_func=rate_functions.ease_in_out_sine))
            self.play(Write(f2[0], run_time=1.0),
                      AnimationGroup(LaggedStart(*flights, lag_ratio=0.1, run_time=0.8),
                                     FadeIn(f2[1], scale=1.6, run_time=0.4), lag_ratio=0.75))
            self.remove(slivers)
            self.play(Write(f2[2]), Write(f2[3]), run_time=0.6)

            # "where Q counts how often the staggered field wraps the sphere over space time,"
            fq = M(r"Q=\frac1{4\pi}\int dx\,d\tau\ \mathbf n\cdot"
                   r"(\partial_x\mathbf n\times\partial_\tau\mathbf n)\ \in\ \mathbb Z",
                   font_size=40).move_to([0, 1.35, 0])
            sk = skyrmion_grid(spacing=0.42, R=1.6, scale=0.34).move_to([-2.7, -1.4, 0])
            frame = SurroundingRectangle(sk, buff=0.12, stroke_color=FAINT, stroke_width=2)
            axes = sheet_axes(frame, buff=0.22)
            q1 = M("Q=1", font_size=36).next_to(frame, RIGHT, buff=0.45)
            self.at(9.45)
            self.play(Indicate(f2[3], color=FG, scale_factor=1.15), Write(fq), run_time=1.3)
            self.play(Create(frame), FadeIn(axes),
                      LaggedStart(*[FadeIn(g, scale=0.5) for g in sk], lag_ratio=0.02),
                      run_time=1.5)
            self.play(Write(q1), run_time=0.5)

            # "and theta equals two pi S."
            th = M(r"\theta=2\pi S", font_size=56).move_to([3.3, -1.4, 0])
            box = SurroundingRectangle(th, buff=0.2, color=DEFECT, stroke_width=3)
            self.at(13.75)
            self.play(Write(th), run_time=0.8)
            self.play(Create(box), run_time=0.6)

    # ------------------------------------------------------------------ s04 + s05
    def s04_05(self):
        with self.voice("s04") as d:
            self._start("s04", d)
            self.play(FadeOut(*self.mobjects), run_time=0.4)

            # "So the low-energy theory is the O three sigma model"
            seff = Mm(r"S_{\rm eff}[\mathbf n]=",
                     r"\frac1{2g}\int dx\,d\tau\,\Big[\tfrac1v(\partial_\tau\mathbf n)^2"
                     r"+v(\partial_x\mathbf n)^2\Big]",
                     r"\;-\;i\theta Q", font_size=40).move_to([0, 2.75, 0])
            b1 = Brace(seff[1], DOWN, buff=0.1, color=DIM)
            l1 = T(r"O(3) $\sigma$ model", font_size=28, color=DIM).next_to(b1, DOWN, buff=0.1)
            b2 = Brace(seff[2], DOWN, buff=0.1, color=DIM)
            l2 = T("topological term", font_size=28, color=DIM).next_to(b2, DOWN, buff=0.1)
            l2.align_to(l1, DOWN)
            l2.shift(RIGHT * max(0.0, l1.get_right()[0] + 0.4 - l2.get_left()[0]))
            self.play(Write(seff[0]), Write(seff[1]), run_time=1.6)
            self.play(GrowFromCenter(b1), FadeIn(l1), run_time=0.6)

            # "plus a topological term,"
            self.at(3.1)
            self.play(Write(seff[2]), run_time=0.6)
            self.play(GrowFromCenter(b2), FadeIn(l2), run_time=0.5)

            # "weighting each winding sector by e to the i theta Q."
            zf = Mm(r"Z=\sum_{Q\in\mathbb Z}", r"e^{\,i\theta Q}", r"\,Z_Q", font_size=44)
            zf.move_to([0, 0.75, 0])
            thumbs = sector_thumbs().move_to([0, -1.4, 0])     # centred under S_eff and Z
            sch = tag(TAG_SCHEMATIC, buff=0.42)   # sectors, phasors, RG sketch are cartoons
            self.at(4.9)
            self.play(Write(zf), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(t, shift=0.15 * UP) for t in thumbs], lag_ratio=0.25),
                      tag_in(sch), run_time=1.4)
            self.at(7.9)
            self.play(Indicate(zf[1], color=FG, scale_factor=1.2), run_time=0.8)

            # "For half-integer spin, theta is pi, modulo two pi:"
            hl = row_label(r"half-integer $S$", r"\theta=\pi\ (\mathrm{mod}\ 2\pi)", HALF)
            hl.move_to([-6.3, -0.55, 0], aligned_edge=UL)
            self.at(9.65)
            self.play(FadeIn(hl[0], shift=0.1 * RIGHT), run_time=0.5)
            self.at(10.9)
            self.play(Write(hl[1]), Indicate(zf[1], color=HALF, scale_factor=1.2), run_time=0.9)

            # "sectors alternate in sign, interfere,"
            hrow = PhasorRow([1, -1, 1, -1], HALF, x0=-2.6, y0=-0.75)
            sign = M(r"e^{\,i\pi Q}=(-1)^Q", font_size=44, color=HALF).move_to([2.6, -1.25, 0])
            self.at(12.5)
            # each winding sector becomes its phasor
            # (all top level: a FadeOut nested in a group would not remove its mobject)
            self.play(FadeIn(hrow.start_tick),
                      *[FadeOut(t.sheet, target_position=a.get_center(), scale=0.2)
                        for t, a in zip(thumbs, hrow.arrows)],
                      *[GrowFromPoint(a, t.sheet.get_center()) for t, a in zip(thumbs, hrow.arrows)],
                      *[FadeOut(t.lab) for t in thumbs], run_time=1.1)
            self.play(Create(hrow.links), FadeIn(sign, shift=0.1 * LEFT), run_time=0.6)
            self.at(14.3)
            self.play(hrow.resolve(), run_time=0.7)

            # "and the chain stays critical."
            hcap = T("interference: critical", font_size=28, color=DIM)
            hcap.next_to(hl, DOWN, buff=0.3).align_to(hl, LEFT)
            self.at(15.3)
            self.play(FadeIn(hcap, shift=0.1 * UP), run_time=0.6)

        with self.voice("s05") as d:
            self._start("s05", d)
            # make room: S_eff leaves; Z and the HALF row move up
            half = VGroup(hl, hrow, hcap)
            self.play(FadeOut(VGroup(seff, b1, l1, b2, l2, sign)), run_time=0.35)
            self.play(zf.animate.move_to([-3.4, 3.0, 0]), half.animate.shift(UP * 2.5),
                      run_time=0.6)

            # "For integer spin every phase is one,"
            il = row_label(r"integer $S$", r"\theta=0\ (\mathrm{mod}\ 2\pi)", INTEGER)
            il.move_to([-6.3, -0.55, 0], aligned_edge=UL)
            irow = PhasorRow([1, 1, 1, 1], INTEGER, x0=-2.6, y0=-0.75)
            self.play(FadeIn(il, shift=0.1 * RIGHT), Indicate(zf[1], color=INTEGER, scale_factor=1.2),
                      run_time=0.8)
            # Z has done its job: it leaves while the integer phasors line up
            self.play(irow.build(run_time=1.1), FadeOut(zf, run_time=0.6))

            # "leaving the plain O three sigma model,"
            icap = T(r"plain O(3) model", font_size=28, color=DIM)
            icap.next_to(il, DOWN, buff=0.3).align_to(il, LEFT)
            self.at(2.8)
            self.play(irow.resolve(), run_time=0.8)
            # focus on the integer row once its resultant lands
            self.play(FadeIn(icap, shift=0.1 * UP), half.animate.fade(0.5), run_time=0.5)

            # "believed to generate a mass:"
            rg = rg_sketch()
            rg.shift(np.array([2.15, 0.45, 0]) - rg.ax.c2p(0, 0))
            self.at(5.0)
            self.play(FadeIn(rg.frame), run_time=0.4)
            self.play(Create(rg.curve), run_time=1.1, rate_func=rate_functions.ease_in_sine)
            self.play(Create(rg.hline), FadeIn(rg.one), Create(rg.vline), FadeIn(rg.xi),
                      run_time=0.6)

            # "a gap shrinking like e to the minus pi S, up to powers of S."
            gap = M(r"\Delta\ \propto\ e^{-\pi S}", font_size=48, color=GAP)
            pw = M(r"(\text{up to powers of }S)", font_size=36, color=GAP)
            bel = T("believed:", font_size=30, color=DIM)
            row = VGroup(bel, gap, pw).arrange(DOWN, buff=0.25)
            row.move_to([4.05, -1.75, 0])
            self.at(7.1)
            self.play(FadeIn(bel), Write(gap), run_time=1.1)
            self.at(9.9)
            self.play(FadeIn(pw, shift=0.1 * LEFT), run_time=0.6)

    # ------------------------------------------------------------------ s06
    def s06(self):
        with self.voice("s06") as d:
            self._start("s06", d)
            self.play(FadeOut(*self.mobjects), run_time=0.4)

            # "But it is not a proof."
            b = objection_bubble("theta")
            head = T("Haldane's argument", font_size=40).move_to([-6.2, 2.75, 0], aligned_edge=LEFT)
            self.play(bubble_in(b), run_time=0.6)
            self.play(FadeIn(head, shift=0.1 * UP), bubble_indicate(b), run_time=0.9)

            rows_txt = [
                r"large-$S$ expansion, used at $S=1$",
                r"continuum limit, but $\xi\approx6$ sites",
                r"mass gap of the 2D O(3) model: no accepted proof",
            ]
            rows = VGroup()
            for i, s in enumerate(rows_txt):
                txt = T(s, font_size=36)
                cr = cross_mark(size=0.34, color=DIM, stroke=7)
                cr.next_to(txt, LEFT, buff=0.4)
                rows.add(VGroup(cr, txt))
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.75)
            rows.move_to([-5.9, -0.45, 0], aligned_edge=LEFT)
            lit = literature_label(rows[1][1], RIGHT, buff=0.3)

            def show_row(i):
                cr, txt = rows[i]
                self.play(FadeIn(txt, shift=0.15 * RIGHT), run_time=0.6)
                self.play(Create(cr), run_time=0.45)

            # "It expands in large spin, then sets S equal to one."
            self.at(1.8)
            show_row(0)
            # "It takes a continuum limit ... only about six sites."
            self.at(5.95)
            show_row(1)
            self.at(9.6)
            self.play(FadeIn(lit), run_time=0.5)
            # "And even the endpoint, the mass gap of the O three model, has no accepted proof."
            self.at(11.25)
            self.play(FadeIn(rows[2][1], shift=0.15 * RIGHT), run_time=0.7)
            self.at(14.65)
            self.play(Create(rows[2][0]), run_time=0.45)
            # the chapter's verdict: large, centred in the free band under the checklist
            verdict = T("it explains; it does not prove", font_size=44, color=GAP)
            verdict.move_to([0, -2.65, 0])
            b.answer = verdict
            self.play(FadeIn(verdict, shift=0.15 * UP), run_time=0.6)
            # motif badge, centred on the corner (the motif's inset touches "theta-term")
            badge = check_badge()
            badge.move_to(b.shape.get_corner(UR))
            b.badge = badge
            self.play(AnimationGroup(GrowFromCenter(badge[0]), Create(badge[1]), lag_ratio=0.4),
                      run_time=0.5)

    # ------------------------------------------------------------------ s07
    def s07(self):
        with self.voice("s07") as d:
            self._start("s07", d)
            # one FadeOut for everything: two FadeOuts whose groups share members
            # (bubble badge parts) leave the bubble behind in CE 0.20
            self.play(FadeOut(*self.mobjects), run_time=0.45)

            # "Keep one image, though:"
            tor = Torus(5, 3)
            tor.shift(DOWN * 0.1 - tor.rect.get_center())
            tex = skyrmion_grid(nx=10, ny=6, spacing=0.5, R=1.75, center_off=(-0.25, 0.0),
                                scale=0.36).move_to(tor.rect)
            self.play(Create(tor.rect), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(g, scale=0.5) for g in tex], lag_ratio=0.01),
                      run_time=1.0)

            # "a sheet of space and imaginary time,"
            sp = T("space", font_size=32, color=SPACE).next_to(tor.rect, DOWN, buff=0.22)
            # buff 0.45: clear of the SPACE chevron while it pulses at scale 1.7
            im = T("imaginary time", font_size=32, color=TIME).next_to(tor.rect, LEFT, buff=0.45)
            self.at(1.95)
            self.play(FadeIn(sp, shift=0.1 * UP), run_time=0.5)
            self.at(2.9)
            self.play(FadeIn(im, shift=0.1 * RIGHT), run_time=0.5)

            # "edges glued."
            top = Line(tor.rect.get_corner(UL), tor.rect.get_corner(UR), color=TIME, stroke_width=6)
            bot = Line(tor.rect.get_corner(DL), tor.rect.get_corner(DR), color=TIME, stroke_width=6)
            lft = Line(tor.rect.get_corner(DL), tor.rect.get_corner(UL), color=SPACE, stroke_width=6)
            rgt = Line(tor.rect.get_corner(DR), tor.rect.get_corner(UR), color=SPACE, stroke_width=6)
            self.at(4.1)
            self.play(Create(top), Create(bot), FadeIn(tor.chev_time), run_time=0.45)
            self.play(FadeOut(top), FadeOut(bot), Create(lft), Create(rgt),
                      FadeIn(tor.chev_space), run_time=0.45)
            self.play(FadeOut(lft), FadeOut(rgt), tor.pulse_chevrons(), run_time=0.6)

            # "The new proof lives there too, but asks a very different question."
            self.at(5.45)
            self.play(FadeOut(tex, lag_ratio=0.01),
                      FadeTransform(sp, tor.L_label),
                      FadeTransform(im, tor.beta_label), run_time=1.3)
            self.remove(tor.rect, tor.chev_time, tor.chev_space, tor.L_label, tor.beta_label)
            self.add(tor)
        self.play(FadeOut(*self.mobjects), run_time=0.6)
