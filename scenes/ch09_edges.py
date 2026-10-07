"""ch09: The edges remember.

Open chains, Tasaki's end fields, the boundary theorem (h = 3/5), the exact
scope of the index statement, where the sign -1 comes from (Tasaki's gentle
local twist), and the theta-term reading (tagged).

The valence-bond cartoon is the ch03 AKLTChain and the theta = 2 pi phasors are
the ch02 PhasorRow (imported, not copied); other recurring motifs come from
motifs.py.  Cue times inside each voice block are fractions of the clip, read
off the pauses in the narration audio.
"""
from motifs import *  # noqa: F401,F403
from ch02_haldane_picture import PhasorRow    # ch02 s05 phasor row (callback in s06)
from ch03_why_hard import AKLTChain           # ch03 s03 valence-bond cartoon

# ------------------------------------------------------------------ geometry
N_START = 9             # the ring opens into a 9-site chain; s01 lengthens it to 13
N_SITES = 13            # odd open chain at the end of s01 and in s02 (2L+1 sites, L = 6)
SP = 0.68               # site spacing in s01-s02 (ch03 proportions: radius ~ 0.38 spacing)
RAD = 0.26              # site circle radius
DDX = 0.12              # offset of the two virtual dots from the site centre
DOTR = 0.07             # virtual dot radius
CHAIN_X = -2.15         # chain centre in s01-s02 (left column)
EDGE_LEN = 0.8          # edge-spin arrows (VIRTUAL), drawn just above the free end dots


def MM(*parts, font_size=36, color=FG, colors=None):
    """Multi-part MathTex (for colouring / TransformMatchingTex)."""
    m = MathTex(*parts, tex_template=TEX_TEMPLATE, font_size=font_size, color=color)
    for i, c in (colors or {}).items():
        m[i].set_color(c)
    return m


# ------------------------------------------------------------------ ring -> chain
def _arc_point(s, kappa, anchor):
    """Point at arc length s on a circle of curvature kappa whose lowest point is
    `anchor` (kappa -> 0: the straight line through anchor)."""
    if kappa < 1e-6:
        return anchor + np.array([s, 0.0, 0.0])
    return anchor + np.array([np.sin(kappa * s) / kappa, (1 - np.cos(kappa * s)) / kappa, 0.0])


class RingToChain(VGroup):
    """An INTEGER spin ring that is cut at its top bond and unrolls into an open chain.

    Site j sits at arc length s_j = (j - (n-1)/2) SP from the lowest point, so the
    cut bond (between sites n-1 and 0) passes through the top of the ring.  With
    an odd number of sites and a staggered pattern both ends point up.
    """

    def __init__(self, chain_center, ring_center, n=N_START, spacing=SP):
        super().__init__()
        self.n, self.sp = n, spacing
        self.k0 = TAU / (n * spacing)
        self.anchor0 = np.array(ring_center, dtype=float) + DOWN / self.k0
        self.anchor1 = np.array(chain_center, dtype=float)
        self.half = (n - 1) / 2 * spacing
        self.arrows = VGroup(*[spin_arrow(UP * (-1) ** j, length=0.5, color=INTEGER, stroke=5)
                               for j in range(n)])
        self.backbone = VMobject(stroke_color=FAINT, stroke_width=2.5)
        self.closing = VMobject(stroke_color=FAINT, stroke_width=2.5)
        self.set_state(0.0)
        self.add(self.backbone, self.closing, self.arrows)

    def _pts(self, s0, s1, kappa, anchor, k=70):
        return [_arc_point(s, kappa, anchor) for s in np.linspace(s0, s1, k)]

    def set_state(self, a):
        kappa = self.k0 * (1 - a)
        anchor = self.anchor0 + (self.anchor1 - self.anchor0) * a
        for j, ar in enumerate(self.arrows):
            ar.move_to(_arc_point((j - (self.n - 1) / 2) * self.sp, kappa, anchor))
        self.backbone.set_points_as_corners(self._pts(-self.half, self.half, kappa, anchor))
        top = self.half + self.sp / 2          # the closing bond, through the top
        pts = self._pts(self.half, top, kappa, anchor, 12) + \
            self._pts(-top, -self.half, kappa, anchor, 12)
        self.closing.set_points_as_corners(pts)


# ------------------------------------------------------------------ valence-bond chain
def vb_chain(n, center, spacing=SP, radius=RAD, dot_dx=DDX, dot_r=DOTR):
    """The ch03 valence-bond cartoon (AKLTChain, straight singlet lines) centred at
    `center`.  The chain is left-right symmetric, so its bounding-box centre is the
    centre of the middle site."""
    ch = AKLTChain(n, spacing=spacing, radius=radius, dot_r=dot_r,
                   dot_dx=dot_dx).move_to(center)
    ch.glows.set_z_index(-1)        # glows stay under the dots whatever the add order
    return ch


def edge_arrow(chain, side, direction=UP, length=EDGE_LEN):
    """VIRTUAL spin arrow of a free end spin, centred just above its dot and clear
    of the site circle (side = 0 left end, 1 right end).  Rotate it about
    arrow_center(arrow)."""
    d = chain.free[side].get_center()
    r = chain.sites[0].width / 2
    c = d + UP * (r + 0.07 + length / 2)
    return spin_arrow(direction, length=length, color=VIRTUAL, stroke=6).shift(c)


def arrow_center(ar):
    return (ar.get_start() + ar.get_end()) / 2


def turn_up(ar):
    """Angle that rotates arrow `ar` to point straight up."""
    ang = angle_of_vector(ar.get_end() - ar.get_start())
    return (PI / 2 - ang + PI) % TAU - PI


def grow_chain(old, arrows, center):
    """Lengthen the open chain by one site at each end: the end sites slide outward
    (carrying their free spins, glows and edge arrows) and a new site with its
    singlet appears in each gap.  Returns (new_chain, animation, leftovers); after
    playing, remove `leftovers` and add the new chain and the arrows."""
    new = vb_chain(old.n + 2, center)
    shL = new.sites[0].get_center() - old.sites[0].get_center()
    shR = new.sites[-1].get_center() - old.sites[-1].get_center()
    movL = VGroup(old.sites[0], old.dots[0], old.glows[0], arrows[0])
    movR = VGroup(old.sites[-1], old.dots[-1], old.glows[1], arrows[1])
    fresh = [new.sites[1], new.dots[1], new.bonds[0], new.sites[-2], new.dots[-2], new.bonds[-1]]
    anim = AnimationGroup(
        ApplyMethod(movL.shift, shL), ApplyMethod(movR.shift, shR),
        GrowFromCenter(new.sites[1]), GrowFromCenter(new.sites[-2]),
        FadeIn(new.dots[1], scale=0.5), FadeIn(new.dots[-2], scale=0.5),
        Create(new.bonds[0]), Create(new.bonds[-1]))
    return new, anim, [old, movL, movR, *fresh]


# ------------------------------------------------------------------ level diagram
ED_SPLIT = {9: 0.2127, 11: 0.1418, 13: 0.0967}     # h = 0, triplet -> singlet (our ED)
ED_BULK = {9: 0.922, 11: 0.799, 13: 0.714}         # lowest bulk-like level (our ED)
ED_FIELD_GAP = 0.519                               # 13 sites, h = 3/5: first excitation (our ED)


class EdgeLevels(VGroup):
    """Low-lying levels of the odd open chain: a triplet (three dashes at 0), a
    singlet just above, and a bulk band higher up (ED, h = 0)."""

    YS = 3.2
    DW = 0.42

    def __init__(self, origin, n=9):
        super().__init__()
        self.o = np.array(origin, dtype=float)
        self.xs = [-0.55, 0.0, 0.55]
        self.trip = VGroup(*[self._dash(x, 0.0) for x in self.xs])
        self.sing = self._dash(0.0, ED_SPLIT[n])
        self.band = self._band(ED_BULK[n])
        self.split = self._split(ED_SPLIT[n])
        self.num = self._num(ED_SPLIT[n])
        self.size_lab = self._size(n)
        self.bulk_lab = T("bulk", font_size=28, color=DIM)
        self.bulk_lab.next_to(self.band, RIGHT, buff=0.18)
        # num and size_lab are kept OUT of the group (they are cross-faded, not morphed)
        self.add(self.band, self.trip, self.sing, self.split, self.bulk_lab)

    def shift_origin(self, v):
        self.o = self.o + v

    def y(self, e):
        return self.o[1] + e * self.YS

    def _dash(self, x, e, w=None, color=FG):
        w = w or self.DW
        return Line(LEFT * w / 2, RIGHT * w / 2, color=color, stroke_width=5).move_to(
            [self.o[0] + x, self.y(e), 0])

    def _band(self, e):
        g = VGroup()
        for i in range(7):
            g.add(Line(LEFT * 0.95, RIGHT * 0.95, color=FG, stroke_width=2.5)
                  .set_stroke(opacity=0.85 - 0.11 * i)
                  .move_to([self.o[0], self.y(e) + 0.075 * i, 0]))
        return g

    def _split(self, e):
        x = self.o[0] + 0.98
        return DoubleArrow([x, self.y(0), 0], [x, self.y(e), 0], buff=0, color=FG,
                           stroke_width=3, tip_length=0.1, max_tip_length_to_length_ratio=0.4,
                           max_stroke_width_to_length_ratio=20)

    def _num(self, e):
        return T(f"{e:.3f}", font_size=30).next_to([self.o[0] + 1.05, self.y(e / 2), 0],
                                                   RIGHT, buff=0.12)

    def _size(self, n):
        return T(f"{n} sites", font_size=28).next_to(
            [self.o[0] - 0.85, self.y(0.0), 0], LEFT, buff=0.22)

    def to_length(self, n, **kw):
        """Animate to another chain length (splitting, band and labels move)."""
        new_band = self._band(ED_BULK[n])
        new_bulk = self.bulk_lab.copy().next_to(new_band, RIGHT, buff=0.18)
        old_num, old_size = self.num, self.size_lab
        self.num, self.size_lab = self._num(ED_SPLIT[n]), self._size(n)
        return AnimationGroup(Transform(self.sing, self._dash(0.0, ED_SPLIT[n])),
                              Transform(self.band, new_band),
                              Transform(self.split, self._split(ED_SPLIT[n])),
                              FadeOut(old_num), FadeIn(self.num),
                              FadeOut(old_size), FadeIn(self.size_lab),
                              Transform(self.bulk_lab, new_bulk), **kw)


# ------------------------------------------------------------------ cards
def _dashed_box(w, h, color=DIM):
    r = RoundedRectangle(width=w, height=h, corner_radius=0.14, stroke_color=color,
                         stroke_width=2.5)
    return DashedVMobject(r, num_dashes=46, dashed_ratio=0.55)


class ImplicationCard(VGroup):
    """Tasaki 2024/25:  [uniform gap (Assumption 2) ?]  ==>  [Ind = -1 (Theorem 3)]."""

    def __init__(self, center=np.array([0, -2.45, 0])):
        super().__init__()
        lt = T("uniform gap", font_size=34)
        ls = T("(Assumption 2)", font_size=26, color=DIM)
        left_txt = VGroup(lt, ls).arrange(DOWN, buff=0.14)
        self.q = M("?", font_size=52, color=DEFECT)
        left_in = VGroup(left_txt, self.q).arrange(RIGHT, buff=0.35)
        rt = M(r"\mathrm{Ind}=-1", font_size=38)
        rs = T("(Theorem 3)", font_size=26, color=DIM)
        right_in = VGroup(rt, rs).arrange(DOWN, buff=0.14)
        w = max(left_in.width, right_in.width) + 0.6
        h = max(left_in.height, right_in.height) + 0.4
        self.left_box = _dashed_box(w, h)
        self.left_box.move_to(left_in)
        self.right_box = RoundedRectangle(width=w, height=h, corner_radius=0.14,
                                          stroke_color=FG, stroke_width=2.5).move_to(right_in)
        self.left = VGroup(self.left_box, left_in)
        self.right = VGroup(self.right_box, right_in)
        self.arrow = M(r"\Longrightarrow", font_size=50)
        row = VGroup(self.left, self.arrow, self.right).arrange(RIGHT, buff=0.45)
        row.move_to(center)
        self.header = T("Tasaki 2024/25", font_size=26, color=DIM)
        self.header.next_to(self.left_box, UP, buff=0.12).align_to(self.left_box, LEFT)
        self.spt = T("nontrivial SPT phase", font_size=28, color=FG)
        self.spt.next_to(self.right_box, DOWN, buff=0.16)
        self.left_in = left_in
        self.add(self.header, self.left, self.arrow, self.right)

    def anim_in(self, **kw):
        return LaggedStart(FadeIn(self.header), Create(self.left_box), FadeIn(self.left_in),
                           Write(self.arrow), FadeIn(self.right, shift=0.15 * LEFT),
                           lag_ratio=0.3, **kw)

    def filled_left_box(self):
        b = self.left_box
        return RoundedRectangle(width=b.width, height=b.height, corner_radius=0.14,
                                stroke_color=GAP, stroke_width=3, fill_color=GAP,
                                fill_opacity=0.12).move_to(b)


def theorem_card():
    head = T(r"claimed theorem (boundary manuscript, Thm.~1.1)", font_size=28)
    l1a = M(r"h=\tfrac35:", font_size=38)
    l1b = M(r"E_1-E_0>\frac{\log 10}{392}\approx5.87\times10^{-3}", font_size=38)
    l1 = VGroup(l1a, l1b).arrange(RIGHT, buff=0.45)
    l2 = M(r"L\ge960\qquad(2L+1\ge1921\ \text{sites})", font_size=34)
    body = VGroup(head, l1, l2).arrange(DOWN, buff=0.26)
    box = RoundedRectangle(width=body.width + 0.8, height=body.height + 0.5, corner_radius=0.16,
                           stroke_color=GAP, stroke_width=3, fill_color=BG, fill_opacity=1)
    box.move_to(body)
    g = VGroup(box, head, l1, l2)
    g.box, g.head, g.l1a, g.l1b, g.l2 = box, head, l1a, l1b, l2
    return g


# ------------------------------------------------------------------ s04: subsequences
class Subsequences(VGroup):
    """Ground states omega_L of longer and longer chains, drawn as a sequence that
    accumulates at two points (schematic): every subsequential limit has Ind = -1;
    convergence of the full sequence is not claimed."""

    def __init__(self, start=np.array([-4.9, 0.35, 0]), A=np.array([1.3, 1.25, 0]),
                 B=np.array([1.3, -0.55, 0]), n=10, q=0.62):
        super().__init__()
        self.A, self.B = A, B
        pts = [start]
        for k in range(1, n + 1):
            tgt = A if k % 2 else B
            pts.append(tgt + (start - tgt) * q ** k)
        # the order of the sequence, fading as the points crowd into the limits
        self.path = VGroup(*[Line(pts[k], pts[k + 1], color=DIM, stroke_width=1.8)
                             .set_stroke(opacity=0.55 * 0.72 ** k) for k in range(n)])
        self.dots = VGroup(*[Dot(p, radius=0.075 - 0.003 * k, color=FG)
                             for k, p in enumerate(pts)])
        self.lab = M(r"\omega_L", font_size=34).next_to(pts[0], UP, buff=0.18)
        self.limA = Circle(radius=0.17, stroke_color=GAP, stroke_width=3).move_to(A)
        self.limB = Circle(radius=0.17, stroke_color=GAP, stroke_width=3).move_to(B)
        self.labA = M(r"\omega", font_size=38).next_to(self.limA, RIGHT, buff=0.18)
        self.labB = M(r"\omega'", font_size=38).next_to(self.limB, RIGHT, buff=0.18)
        self.indA = M(r"\mathrm{Ind}=-1", font_size=36, color=GAP).next_to(
            self.limA, RIGHT, buff=0.95)
        self.indB = M(r"\mathrm{Ind}=-1", font_size=36, color=GAP).next_to(
            self.limB, RIGHT, buff=0.95)
        self.odd = VGroup(*[self.dots[k] for k in range(1, n + 1, 2)])
        self.even = VGroup(*[self.dots[k] for k in range(2, n + 1, 2)])
        arr_y = B[1] - 0.75
        self.Larrow = Arrow([start[0], arr_y, 0], [A[0] - 0.2, arr_y, 0], buff=0, color=DIM,
                            stroke_width=3, max_tip_length_to_length_ratio=0.04)
        self.Llab = M(r"L\to\infty", font_size=30, color=DIM).next_to(self.Larrow, RIGHT,
                                                                       buff=0.15)
        self.add(self.path, self.dots, self.lab)


# ------------------------------------------------------------------ s05: dial + twist
class Dial(VGroup):
    """Unit disc for an expectation value omega(U).  A bead marks the value; in
    the first beat a thin hand joins it to the centre (a phase dial)."""

    def __init__(self, center=np.array([4.45, 0.25, 0]), R=1.3):
        super().__init__()
        self.c, self.R = np.array(center, dtype=float), R
        self.disc = Circle(radius=R, stroke_color=DIM, stroke_width=2.5).move_to(center)
        self.re = Line(self.c + LEFT * (R + 0.15), self.c + RIGHT * (R + 0.15), color=FAINT,
                       stroke_width=2)
        self.im = Line(self.c + DOWN * (R + 0.15), self.c + UP * (R + 0.15), color=FAINT,
                       stroke_width=2)
        self.one = M("1", font_size=30, color=DIM).next_to(self.c + RIGHT * (R + 0.15), RIGHT,
                                                           buff=0.12)
        self.mone = M("-1", font_size=30, color=DIM).next_to(self.c + LEFT * (R + 0.15), LEFT,
                                                             buff=0.12)
        self.phi = ValueTracker(0.0)
        self.rad = ValueTracker(1.0)
        self.bead = Dot(radius=0.12, color=FG).set_z_index(3)
        self.bead.add_updater(lambda m: m.move_to(self.point()))
        self.bead.move_to(self.point())
        self.hand = always_redraw(lambda: Line(self.c, self.point(), color=FG, stroke_width=3))
        self.add(self.disc, self.re, self.im, self.one, self.mone)

    def point(self):
        r = self.rad.get_value() * self.R
        ph = self.phi.get_value()
        return self.c + r * np.array([np.cos(ph), np.sin(ph), 0])


def forbidden_band(dial, c, n=40):
    """The excluded interval |Re omega| < c drawn as a vertical strip of the dial's
    disc: neutral translucent fill with GAP edges (the gap is what keeps the value
    out of it)."""
    R, cx, cy = dial.R, dial.c[0], dial.c[1]
    c = float(np.clip(c, 1e-3, 0.999))
    th = np.arccos(c)
    top = [[cx + R * np.cos(t), cy + R * np.sin(t), 0] for t in np.linspace(th, PI - th, n)]
    bot = [[cx + R * np.cos(t), cy + R * np.sin(t), 0] for t in np.linspace(PI + th, TAU - th, n)]
    fill = VMobject(stroke_width=0, fill_color=DIM, fill_opacity=0.3)
    fill.set_points_as_corners(top + bot + [top[0]])
    h = R * np.sin(th)
    edges = VGroup(*[Line([cx + sx * c * R, cy - h, 0], [cx + sx * c * R, cy + h, 0], color=GAP,
                          stroke_width=3) for sx in (-1, 1)])
    g = VGroup(fill, edges)
    g.set_z_index(-1)
    return g


class TwistPlot(VGroup):
    """Rotation angle theta_j against site j: uniform pi -> Tasaki's ramp
    clip(pi + eps j, 0, 2 pi).  `m` morphs flat -> ramp, `eps` sets the window."""

    def __init__(self, center=np.array([-2.35, -0.25, 0]), W=7.2, H=2.9, J=10.0):
        super().__init__()
        self.W, self.H, self.J = W, H, J
        x0, y0 = center[0] - W / 2, center[1] - H / 2
        self.x0, self.y0 = x0, y0
        self.xaxis = Arrow([x0 - 0.05, y0, 0], [x0 + W + 0.3, y0, 0], buff=0, color=DIM,
                           stroke_width=2.5, max_tip_length_to_length_ratio=0.03)
        self.yaxis = Line([x0, y0, 0], [x0, y0 + H + 0.25, 0], color=DIM, stroke_width=2.5)
        self.grid = VGroup(*[DashedLine([x0, self.yv(v), 0], [x0 + W, self.yv(v), 0],
                                        color=FAINT, stroke_width=1.5, dash_length=0.08)
                             for v in (PI, TAU)])
        self.yticks = VGroup()
        for v, s in ((0, "0"), (PI, r"\pi"), (TAU, r"2\pi")):
            self.yticks.add(M(s, font_size=32, color=DIM).next_to([x0, self.yv(v), 0], LEFT,
                                                                   buff=0.15))
        self.xlab = M("j", font_size=34, color=DIM).next_to(self.xaxis, RIGHT, buff=0.1)
        self.ylab = M(r"\theta_j", font_size=34).next_to(self.yaxis, UP, buff=0.1)
        self.m = ValueTracker(0.0)
        self.eps = ValueTracker(PI / 3.4)
        self.curve = always_redraw(self._make_curve)
        self.add(self.grid, self.xaxis, self.yaxis, self.yticks, self.xlab, self.ylab)

    def xv(self, j):
        return self.x0 + (j + self.J) / (2 * self.J) * self.W

    def yv(self, th):
        return self.y0 + th / TAU * self.H

    def theta(self, j):
        e, m = self.eps.get_value(), self.m.get_value()
        ramp = np.clip(PI + e * j, 0, TAU)
        return (1 - m) * PI + m * ramp

    def _make_curve(self):
        js = np.linspace(-self.J, self.J, 241)
        c = VMobject(stroke_color=FG, stroke_width=5)
        c.set_points_as_corners([[self.xv(j), self.yv(self.theta(j)), 0] for j in js])
        return c

    def window_marks(self):
        """DIM ticks and labels at j = -pi/eps and +pi/eps (they follow eps)."""
        g = VGroup()
        for sgn, s in ((-1, r"-\pi/\varepsilon"), (1, r"\pi/\varepsilon")):
            pair = VGroup(Line(UP * 0.09, DOWN * 0.09, color=DIM, stroke_width=2.5),
                          M(s, font_size=30, color=DIM))

            def upd(mob, sgn=sgn):
                x = self.xv(sgn * PI / self.eps.get_value())
                mob[0].move_to([x, self.y0, 0])
                mob[1].next_to([x, self.y0, 0], DOWN, buff=0.18)
            upd(pair)
            pair.add_updater(upd)
            g.add(pair)
        return g


# ================================================================== the chapter
class Ch09(NarratedScene):
    CHAPTER = "ch09"

    # local clock inside a voice block -----------------------------------
    def _mark(self):
        self._t0 = self.renderer.time

    def until(self, t):
        dt = self._t0 + t - self.renderer.time
        if dt > 0.04:
            self.wait(dt)
        elif dt < -0.15:
            print(f"[ch09 cue late] {self._timeline[-1]['id']} cue {t:.2f}s late by {-dt:.2f}s")

    def purge(self, *mobs):
        """Remove mobjects AND every piece of them that was added on its own
        (Scene.remove only drops top-level entries)."""
        self.remove(*[m for mob in mobs for m in mob.get_family()])

    def construct(self):
        chain_c1 = np.array([CHAIN_X, 0.35, 0])     # s01 chain centre
        lv_o1 = np.array([4.55, -1.25, 0])           # s01 level-diagram origin
        # ============================================================ s01
        with self.voice("s01") as d:
            self._mark()
            rc = RingToChain(chain_center=chain_c1, ring_center=np.array([0, 0.2, 0]))
            self.play(FadeIn(rc), run_time=0.035 * d)
            # "Now cut the ring open."
            snip = rc.closing
            self.play(snip.animate.set_stroke(color=DEFECT, width=6), run_time=0.028 * d)
            self.play(snip.animate.set_stroke(opacity=0), run_time=0.028 * d)
            rc.remove(snip)
            a = ValueTracker(0.0)
            rc.add_updater(lambda m: m.set_state(a.get_value()))
            self.play(a.animate.set_value(1.0), run_time=0.075 * d,
                      rate_func=rate_functions.ease_in_out_sine)
            rc.clear_updaters()
            # "In the valence-bond picture,"  (the ch03 cartoon: each spin one splits
            # into two spin one-halves, neighbouring halves bind into singlets)
            vb = vb_chain(N_START, chain_c1)
            self.play(LaggedStart(*[AnimationGroup(FadeOut(ar, scale=0.4), GrowFromCenter(c))
                                    for ar, c in zip(rc.arrows, vb.sites)], lag_ratio=0.06),
                      FadeOut(rc.backbone), run_time=0.05 * d)
            self.purge(rc)
            self.play(vb.split_in(), run_time=0.033 * d)
            self.play(vb.bonds_in(), run_time=0.033 * d)
            # "each end carries a free spin one-half,"
            self.until(0.31 * d)
            earrows = VGroup(edge_arrow(vb, 0, rotate_vector(UP, 0.7)),
                             edge_arrow(vb, 1, rotate_vector(DOWN, 0.55)))
            self.play(vb.glows_in(),
                      *[Flash(dd, color=VIRTUAL, line_length=0.16, flash_radius=0.3)
                        for dd in vb.free], run_time=0.05 * d)
            self.play(GrowFromCenter(earrows[0]), GrowFromCenter(earrows[1]),
                      run_time=0.045 * d)
            self.play(Rotate(earrows[0], -0.55, about_point=arrow_center(earrows[0])),
                      Rotate(earrows[1], 0.6, about_point=arrow_center(earrows[1])),
                      run_time=0.05 * d, rate_func=there_and_back)
            # "giving four nearly degenerate states:"   (our ED from here on: tag)
            self.until(0.49 * d)
            lv = EdgeLevels(origin=lv_o1, n=N_START)
            ours = tag(TAG_OURS)
            self.play(LaggedStart(FadeIn(lv.trip, shift=0.1 * UP),
                                  FadeIn(lv.sing, shift=0.1 * UP),
                                  FadeIn(lv.band), FadeIn(lv.bulk_lab), lag_ratio=0.25),
                      tag_in(ours), run_time=0.08 * d)
            hlab = M(r"h=0", font_size=30, color=DIM)
            hlab.next_to([lv.o[0], lv.o[1], 0], DOWN, buff=0.38)
            self.play(GrowFromCenter(lv.split), FadeIn(lv.num), FadeIn(lv.size_lab),
                      FadeIn(hlab), run_time=0.04 * d)
            # "an open chain has no uniform gap,"  (the chain itself lengthens 9 -> 11 -> 13)
            self.until(0.675 * d)
            for n_new in (11, 13):
                vb_new, grow, leftovers = grow_chain(vb, earrows, chain_c1)
                self.play(grow, lv.to_length(n_new), run_time=0.065 * d)
                self.purge(*leftovers)
                self.add(vb_new, earrows)
                vb = vb_new
            nug = T("no uniform gap", font_size=34)
            nug.next_to(hlab, DOWN, buff=0.3)
            self.play(Write(nug), run_time=0.055 * d)

        # ============================================================ s02
        with self.voice("s02") as d:
            self._mark()
            # "Tasaki's fix: an odd chain,"
            chain = VGroup(vb, earrows)
            up_c, up_l = UP * 1.45, UP * 0.9
            lv.remove(lv.split)
            self.play(chain.animate.shift(up_c), lv.animate.shift(up_l), hlab.animate.shift(up_l),
                      FadeOut(nug), FadeOut(lv.split), FadeOut(lv.num), FadeOut(lv.size_lab),
                      run_time=0.06 * d)
            lv.shift_origin(up_l)
            # field arrows h sit just below the two end sites, pointing up at them;
            # the site labels -L, 0, L share one row underneath
            fields = VGroup()
            for k, side in ((0, RIGHT), (-1, LEFT)):
                c = vb.sites[k]
                ar = Arrow(c.get_bottom() + DOWN * 0.72, c.get_bottom() + DOWN * 0.1, buff=0,
                           color=FG, stroke_width=5, max_tip_length_to_length_ratio=0.32)
                lab = M("h", font_size=32).next_to(ar, side, buff=0.12)
                fields.add(VGroup(ar, lab))
            row_y = vb.sites[0].get_bottom()[1] - 0.72 - 0.3
            sl = VGroup(*[M(t, font_size=30, color=DIM).move_to([vb.sites[k].get_x(), row_y, 0])
                          for t, k in (("-L", 0), ("0", N_SITES // 2), ("L", -1))])
            nsites = T(r"$2L+1$ sites", font_size=28, color=DIM)
            nsites.next_to(sl[1], DOWN, buff=0.14)
            self.play(FadeIn(sl, lag_ratio=0.3), run_time=0.05 * d)
            self.play(FadeIn(nsites), run_time=0.03 * d)
            # "with the same field on both end spins."
            self.until(0.165 * d)
            self.play(*[GrowArrow(f[0]) for f in fields], *[FadeIn(f[1]) for f in fields],
                      run_time=0.06 * d)
            H = M(r"H_L(h)=\sum_{j=-L}^{L-1}\mathbf S_j\cdot\mathbf S_{j+1}"
                  r"-h\,\big(S^z_{-L}+S^z_{L}\big)", font_size=34)
            H.move_to([CHAIN_X, -0.72, 0])
            self.play(Write(H), run_time=0.11 * d)
            # "The edge spins align,"
            self.until(0.34 * d)
            self.play(*[Rotate(ar, turn_up(ar), about_point=arrow_center(ar)) for ar in earrows],
                      run_time=0.07 * d)
            # "the ground state is unique,"   (levels: our ED, 13 sites, h = 3/5)
            self.until(0.435 * d)
            e1 = ED_FIELD_GAP
            g0 = lv._dash(0.0, 0.0, w=1.5)
            ex_a = lv._dash(-0.3, e1)
            ex_b = lv._dash(0.3, e1)
            ex_c = lv._dash(0.0, ED_BULK[13] + 0.02).set_opacity(0)
            # the level label follows the levels: h = 0 -> h = 3/5 as they split
            hlab2 = M(r"h=\tfrac35", font_size=30, color=DIM).next_to(g0, DOWN, buff=0.3)
            self.play(Transform(lv.trip[1], g0), Transform(lv.trip[0], ex_a),
                      Transform(lv.sing, ex_b), Transform(lv.trip[2], ex_c),
                      FadeOut(hlab, shift=0.15 * UP), FadeIn(hlab2, shift=0.15 * UP),
                      run_time=0.07 * d)
            gx = lv.o[0] + 1.0
            gap_ar = DoubleArrow([gx, lv.y(0), 0], [gx, lv.y(e1), 0], buff=0, color=GAP,
                                 stroke_width=3.5, tip_length=0.14)
            gap_lab = T("gap", font_size=30, color=GAP).next_to(gap_ar, RIGHT, buff=0.12)
            sz = M(r"S^z_{\rm tot}=1", font_size=32).next_to(g0, LEFT, buff=0.22)
            self.play(GrowFromCenter(gap_ar), FadeIn(gap_lab), FadeIn(sz, shift=0.1 * RIGHT),
                      run_time=0.04 * d)
            # "and his theorem turns a uniform gap into a topological index of minus one:"
            # (H has done its job: it leaves so the frame keeps three groups)
            self.until(0.55 * d)
            card = ImplicationCard(center=np.array([0, -1.95, 0]))
            self.play(FadeOut(H), run_time=0.025 * d)
            self.play(card.anim_in(), run_time=0.14 * d)
            self.play(Indicate(card.q, color=DEFECT, scale_factor=1.3), run_time=0.05 * d)
            # "a nontrivial S-P-T phase."
            self.until(0.855 * d)
            self.play(FadeIn(card.spt, shift=0.1 * UP), run_time=0.05 * d)

        # ============================================================ s03
        with self.voice("s03") as d:
            self._mark()
            # "The companion manuscript claims that gap for an end field of three fifths:"
            old = VGroup(chain, sl, nsites, fields, lv, gap_ar, gap_lab, sz, hlab2)
            self.play(FadeOut(old), tag_out(ours), FadeOut(card.spt),
                      card.animate.move_to([0, 2.55, 0]), run_time=0.04 * d)
            th = theorem_card().move_to([0, -0.6, 0])
            link = Arrow(th.box.get_top(), [card.left_box.get_center()[0],
                                            card.left_box.get_bottom()[1], 0],
                         buff=0.12, color=GAP, stroke_width=4,
                         max_tip_length_to_length_ratio=0.15)
            self.play(FadeIn(th.box), FadeIn(th.head, shift=0.1 * UP), run_time=0.04 * d)
            filled = card.filled_left_box()
            chk = check_mark(0.42).move_to(card.q)
            self.play(GrowArrow(link), FadeOut(card.left_box), FadeIn(filled),
                      FadeOut(card.q, scale=0.5), Create(chk), run_time=0.05 * d)
            card.left.remove(card.left_box)
            card.left_in.remove(card.q)
            card.left.add(filled, chk)
            self.until(0.15 * d)
            self.play(Write(th.l1a), run_time=0.04 * d)
            # "above log 10 over 392, about 0.00587,"
            self.until(0.22 * d)
            self.play(Write(th.l1b), run_time=0.13 * d)
            # "on every such chain of at least 1921 sites."
            self.until(0.495 * d)
            self.play(Write(th.l2), run_time=0.1 * d)
            # "It reuses the operator X,"
            self.until(0.685 * d)
            self.play(FadeOut(card), FadeOut(link), th.animate.move_to([0, 2.45, 0]),
                      run_time=0.03 * d)
            tor = Torus(4.2, 2.2, nx=10, ny=4, L_tex="n").move_to([-3.25, -1.55, 0])
            self.play(FadeIn(tor), run_time=0.025 * d)
            vk = space_knife(tor, bond=1)
            self.play(vk.cut_in(), vk.glow_on(), FadeOut(tor.chev_space), run_time=0.03 * d)
            # the chevrons are gone for good: detach them, or a later FadeOut of the torus
            # would bring them back (FadeOut's clean-up restores their opacity)
            tor.remove(tor.chev_space)
            steps = vk.steps([2, 3], label_tex="X", step_time=1.0)
            for grp in steps.animations:          # the transient step labels: X in SPACE
                for an in grp.animations:
                    if isinstance(an, UpdateFromAlphaFunc) and an.mobject is not vk:
                        an.mobject.set_color(SPACE).set_opacity(0)
            self.play(steps, run_time=0.045 * d)
            # "with the end fields as boundary states,"
            self.until(0.815 * d)
            capL = Line([tor.left, tor.bottom, 0], [tor.left, tor.top, 0], color=VIRTUAL,
                        stroke_width=9)
            capR = Line([tor.right, tor.bottom, 0], [tor.right, tor.top, 0], color=VIRTUAL,
                        stroke_width=9)
            vL = M(r"\langle v_\beta|", font_size=36, color=VIRTUAL).next_to(
                [tor.left, tor.bottom, 0], DOWN, buff=0.2)
            vR = M(r"|v_\beta\rangle", font_size=36, color=VIRTUAL).next_to(
                [tor.right, tor.bottom, 0], DOWN, buff=0.2)
            self.play(Create(capL), Create(capR), FadeIn(vL), FadeIn(vR), run_time=0.035 * d)
            f1l = T("same fields (the theorem's chain):", font_size=28)
            f1 = MM(r"\langle", r"v_\beta", r",\,", r"X_\beta^{\,n}", r"\,U_P\,", r"v_\beta",
                    r"\rangle", font_size=40, colors={1: VIRTUAL, 3: SPACE, 5: VIRTUAL})
            f2l = T("opposite fields:", font_size=26, color=DIM)
            f2 = MM(r"\langle", r"v_\beta", r",\,", r"X_\beta^{\,n}", r"\,v_\beta", r"\rangle",
                    font_size=34, color=DIM)
            blk1 = VGroup(f1l, f1).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
            blk2 = VGroup(f2l, f2).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
            fblk = VGroup(blk1, blk2).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
            fblk.move_to([2.9, -0.95, 0]).align_to(np.array([0.55, 0, 0]), LEFT)
            self.play(FadeIn(blk1, shift=0.1 * UP), run_time=0.035 * d)
            self.play(FadeIn(blk2, shift=0.1 * UP), run_time=0.03 * d)
            # "and a second bootstrap."
            self.until(0.925 * d)
            ic = icon_staircase(steps=3, u=0.36)
            icl = T("second bootstrap", font_size=28)
            boot = VGroup(ic, icl).arrange(RIGHT, buff=0.3)
            boot.next_to(fblk, DOWN, buff=0.45).align_to(fblk, LEFT)
            self.play(FadeIn(boot, shift=0.1 * UP), run_time=0.04 * d)

        # ============================================================ s04
        with self.voice("s04") as d:
            self._mark()
            # the sequence drawing is schematic: corner tag for s04 (kept through s05)
            sch = tag(TAG_SCHEMATIC)
            self.play(FadeOut(VGroup(th, tor, vk, capL, capR, vL, vR, fblk, boot)),
                      tag_in(sch), run_time=0.035 * d)
            sub = Subsequences()
            # "So every infinite-chain limit selected by these end fields,"
            self.play(FadeIn(sub.dots[0]), FadeIn(sub.lab), run_time=0.03 * d)
            self.play(LaggedStart(*[Create(seg) for seg in sub.path], lag_ratio=0.25),
                      LaggedStart(*[FadeIn(dt, scale=0.5) for dt in sub.dots[1:]],
                                  lag_ratio=0.25),
                      GrowArrow(sub.Larrow), FadeIn(sub.Llab), run_time=0.16 * d)
            # "along any subsequence of lengths,"
            self.until(0.28 * d)
            self.play(sub.even.animate.set_color(FAINT), sub.dots[0].animate.set_color(FAINT),
                      sub.path.animate.fade(0.4), run_time=0.035 * d)
            self.play(Create(sub.limA), FadeIn(sub.labA), run_time=0.05 * d)
            # "has index minus one."
            self.until(0.43 * d)
            head = T(r"every boundary-selected subsequential limit: $\mathrm{Ind}=-1$",
                     font_size=32)
            hbox = RoundedRectangle(width=head.width + 0.6, height=head.height + 0.4,
                                    corner_radius=0.14, stroke_color=GAP, stroke_width=3)
            hcard = VGroup(hbox, head).move_to([0, 3.0, 0])
            self.play(Write(sub.indA), FadeIn(hcard, shift=0.1 * DOWN), run_time=0.07 * d)
            # "Convergence of the whole sequence,"
            self.until(0.575 * d)
            self.play(sub.odd.animate.set_color(FAINT), sub.even.animate.set_color(FG),
                      run_time=0.03 * d)
            self.play(Create(sub.limB), FadeIn(sub.labB), FadeIn(sub.indB), run_time=0.04 * d)
            neq = M(r"\omega\overset{?}{=}\omega'", font_size=40, color=DIM)
            neq.move_to([5.55, 0.35, 0])
            nc_head = T("not claimed:", font_size=30, color=DIM)
            items = VGroup()
            for s in ("convergence of the full sequence",
                      "uniqueness of the infinite-volume ground state"):
                txt = T(s, font_size=30, color=DIM)
                icon = open_circle().next_to(txt, LEFT, buff=0.25)
                items.add(VGroup(icon, txt))
            items.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            nc = VGroup(nc_head, items).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            items.shift(RIGHT * 0.35)
            nc.move_to([-0.2, -2.8, 0])
            self.play(sub.odd.animate.set_color(FG), FadeIn(neq), FadeIn(nc_head),
                      FadeIn(items[0], shift=0.1 * RIGHT), run_time=0.05 * d)
            # "and uniqueness of the infinite-volume ground state,"
            self.until(0.71 * d)
            self.play(FadeIn(items[1], shift=0.1 * RIGHT), run_time=0.06 * d)
            # "are not claimed."
            self.until(0.905 * d)
            self.play(Indicate(nc_head, color=FG, scale_factor=1.1), run_time=0.07 * d)

        # ============================================================ s05
        with self.voice("s05", breath=0.9) as d:
            self._mark()
            self.play(FadeOut(VGroup(sub, sub.Larrow, sub.Llab, sub.limA, sub.limB, sub.labA,
                                     sub.labB, sub.indA, sub.indB, hcard, neq, nc)),
                      run_time=0.035 * d)
            dial = Dial()
            self.play(FadeIn(dial), FadeIn(dial.hand), FadeIn(dial.bead), run_time=0.04 * d)
            # "The selected ground state has total spin along z equal to one,"
            self.until(0.11 * d)
            sz1 = M(r"S^z_{\rm tot}=1", font_size=44).move_to([-2.4, 1.0, 0])
            self.play(Write(sz1), run_time=0.07 * d)
            # "so a pi rotation about z gives minus one."
            self.until(0.33 * d)
            eq1 = MM(r"e^{-i\pi S^z_{\rm tot}}", "=", r"e^{-i\pi}", "=", "-1", font_size=44)
            eq1.move_to([-2.4, -0.3, 0])
            trail = always_redraw(lambda: Arc(radius=dial.R, start_angle=0,
                                              angle=min(-1e-3, dial.phi.get_value()),
                                              arc_center=dial.c, color=FG, stroke_width=4))
            self.add(trail)
            self.play(Write(eq1[:3]), dial.phi.animate.set_value(-PI), run_time=0.09 * d)
            self.play(Write(eq1[3:]), run_time=0.04 * d)
            self.play(Indicate(eq1[4], color=DEFECT), Indicate(dial.mone, color=DEFECT),
                      Indicate(dial.bead, color=DEFECT, scale_factor=1.5), run_time=0.04 * d)
            # "Deform that rotation into a gentle, local twist in the bulk:"
            self.until(0.51 * d)
            tp = TwistPlot()
            trail.clear_updaters()
            dial.hand.clear_updaters()
            self.play(FadeOut(sz1), FadeOut(trail), FadeOut(dial.hand),
                      eq1.animate.scale(36 / 44).move_to([-2.35, 2.95, 0]),
                      FadeIn(VGroup(tp.grid, tp.xaxis, tp.yaxis, tp.yticks, tp.xlab, tp.ylab)),
                      run_time=0.04 * d)
            self.play(Create(tp.curve), run_time=0.025 * d)
            U = M(r"U_\varepsilon=\exp\Big[-i\!\!\sum_{|j|\le\pi/\varepsilon}"
                  r"\!(\pi+\varepsilon j)\,S^z_j\Big]", font_size=34)
            U.move_to([-2.35, -3.05, 0])
            self.play(tp.m.animate.set_value(1.0), dial.rad.animate.set_value(0.72),
                      Write(U), run_time=0.07 * d)
            wm = tp.window_marks()
            self.play(FadeIn(wm), run_time=0.02 * d)
            self.play(tp.eps.animate.set_value(PI / 6.5), dial.rad.animate.set_value(0.86),
                      run_time=0.06 * d)
            # "reflection keeps its expectation real,"
            self.until(0.735 * d)
            rail = Line(dial.c + LEFT * dial.R, dial.c + RIGHT * dial.R, color=FG,
                        stroke_width=4)
            off = VGroup(*[AnnularSector(inner_radius=0, outer_radius=dial.R, angle=PI,
                                         start_angle=s0, fill_color=FAINT, fill_opacity=0.45,
                                         stroke_width=0).move_arc_center_to(dial.c)
                           for s0 in (0, PI)])
            off.set_z_index(-2)
            real_lab = T("real (reflection)", font_size=28, color=DIM)
            real_lab.next_to(dial.disc, DOWN, buff=0.35)
            self.play(FadeIn(off), Create(rail), FadeIn(real_lab), run_time=0.06 * d)
            # "and the gap keeps it from crossing zero."
            # Forbidden interval (-c, c) on the real axis (neutral band, GAP edges): as
            # epsilon shrinks it widens toward the whole segment and pins the value at -1
            # (Tasaki: -1 <= omega(U_eps) <= -sqrt(1 - 4(pi+eps)eps/gamma)).
            self.until(0.865 * d)
            cw = ValueTracker(0.3)
            band = always_redraw(lambda: forbidden_band(dial, cw.get_value()))
            band_lab = T("kept out by the gap", font_size=28, color=DIM)
            band_lab.next_to(dial.disc, UP, buff=0.38)
            self.play(FadeIn(band), FadeIn(band_lab), run_time=0.025 * d)
            ind = MM(r"\mathrm{Ind}", "=", r"\lim_{\varepsilon\downarrow0}\omega(U_\varepsilon)",
                     "=", "-1", font_size=36, color=GAP)
            ind.move_to(eq1).align_to(eq1, LEFT)
            self.play(tp.eps.animate.set_value(PI / 9.2), cw.animate.set_value(0.87),
                      dial.rad.animate.set_value(1.0), FadeOut(eq1, shift=0.25 * UP),
                      run_time=0.06 * d, rate_func=rate_functions.ease_in_out_sine)
            self.play(FadeIn(ind, shift=0.25 * UP), dial.bead.animate.set_color(GAP),
                      run_time=0.03 * d)

        # ============================================================ s06
        with self.voice("s06") as d:
            self._mark()
            tg = tag(TAG_READING_NEITHER)
            tp.curve.clear_updaters()
            dial.bead.clear_updaters()
            band.clear_updaters()
            for m in wm:
                m.clear_updaters()
            self.play(FadeOut(VGroup(dial, dial.bead, rail, off, band, band_lab, real_lab,
                                     tp, tp.curve, wm, U, ind)),
                      tag_out(sch), tag_in(tg), run_time=0.06 * d)
            # "A physicist's reading, in neither paper:"   (the ch03 cartoon again)
            vb2 = vb_chain(11, np.array([0.0, -0.55, 0]), spacing=0.8, radius=0.3,
                           dot_dx=0.14, dot_r=0.08)
            ea2 = VGroup(edge_arrow(vb2, 0), edge_arrow(vb2, 1))
            self.play(LaggedStart(FadeIn(vb2.sites), FadeIn(vb2.dots), FadeIn(vb2.bonds),
                                  lag_ratio=0.2), run_time=0.07 * d)
            # "theta equals two pi is invisible in the bulk,"   (ch02 s05 phasors: all add)
            self.until(0.245 * d)
            th2 = M(r"\theta=2\pi", font_size=40, color=INTEGER)
            ph = PhasorRow([1, 1, 1, 1], INTEGER, x0=0.0, y0=0.0)
            eq_one = M(r"e^{i\theta Q}=1", font_size=36)
            VGroup(th2, ph, eq_one).arrange(RIGHT, buff=0.6).move_to([0, 2.15, 0])
            self.play(FadeIn(th2), ph.build(run_time=0.09 * d))
            self.play(ph.resolve(), FadeIn(eq_one, shift=0.1 * LEFT), run_time=0.05 * d)
            bulk = VGroup(*vb2.sites[1:-1], *vb2.bonds, *vb2.dots[1:-1], vb2.dots[0][1],
                          vb2.dots[-1][0])
            br = Brace(VGroup(*vb2.sites[1:-1]), UP, buff=0.12, color=DIM)
            br_lab = T("bulk: invisible", font_size=30, color=DIM).next_to(br, UP, buff=0.1)
            self.play(bulk.animate.fade(0.6), GrowFromCenter(br), FadeIn(br_lab),
                      run_time=0.06 * d)
            # "but at an edge it leaves the Berry phase of a free spin one-half,"
            self.until(0.475 * d)
            halfs = VGroup(
                M(r"\tfrac12", font_size=38, color=VIRTUAL).next_to(vb2.sites[0], LEFT,
                                                                    buff=0.2),
                M(r"\tfrac12", font_size=38, color=VIRTUAL).next_to(vb2.sites[-1], RIGHT,
                                                                    buff=0.2))
            self.play(vb2.glows_in(), GrowFromCenter(ea2[0]), GrowFromCenter(ea2[1]),
                      run_time=0.06 * d)
            self.play(FadeIn(halfs, scale=0.6),
                      *[Flash(dd, color=VIRTUAL, line_length=0.16, flash_radius=0.32)
                        for dd in vb2.free], run_time=0.06 * d)
            edge_lab = T(r"edge: Berry phase of a free spin $\tfrac12$", font_size=30,
                         color=VIRTUAL)
            edge_lab.next_to(vb2.sites, DOWN, buff=0.45)
            self.play(FadeIn(edge_lab, shift=0.1 * UP), run_time=0.05 * d)
            # "and the index is a rigorous fingerprint of that."
            self.until(0.785 * d)
            fp = MM(r"\mathrm{Ind}=-1", r"\quad\longleftrightarrow\quad",
                    r"e^{i\theta/2}=e^{i\pi}=-1", font_size=38, colors={0: GAP, 1: DIM})
            fp.move_to([0, -2.75, 0])
            self.play(Write(fp[0]), run_time=0.05 * d)
            self.play(FadeIn(fp[1]), FadeIn(fp[2], shift=0.1 * LEFT), run_time=0.06 * d)

        self.play(FadeOut(*self.mobjects), run_time=1.0)
