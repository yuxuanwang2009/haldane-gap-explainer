"""Recurring motifs of the Haldane-gap explainer (storyboard "Recurring motifs" 1-8).

    from motifs import *        # also brings visuals.* and common.*

Every callback of a motif must be built with these helpers so that it looks
identical in every chapter.  See scenes/MOTIFS.md for the API reference and
the storyboard segments that use each motif.

Conventions
- Constructors return VGroups (or VGroup subclasses with named parts).
- Methods that return animations do NOT play them; play them right away, in
  the order they were created (some methods update the object's bookkeeping,
  e.g. a tromino's position or a thumbnail's multipliers, when called).
- Dim motifs with .fade(), not .set_opacity(): several keep invisible parts
  (off-range plot points, cross-faded ticks, thumbnail seams, knife glow).
- Nothing here changes the signatures in visuals.py.
"""
import csv

import numpy as np

from visuals import *  # noqa: F401,F403

# =================================================================== small glyphs
STROKE_KNIFE = 6


def check_mark(size=0.32, color=GAP, stroke=6):
    """Hand-drawn check mark (animate with Create)."""
    pts = np.array([[-0.50, 0.02, 0], [-0.16, -0.36, 0], [0.50, 0.42, 0]]) * size
    m = VMobject(stroke_color=color, stroke_width=stroke)
    m.set_points_as_corners(pts)
    m.set_fill(opacity=0)
    return m


def cross_mark(size=0.3, color=SX, stroke=6):
    """Two crossing strokes (animate with Create)."""
    a = Line([-size / 2, -size / 2, 0], [size / 2, size / 2, 0], color=color, stroke_width=stroke)
    b = Line([-size / 2, size / 2, 0], [size / 2, -size / 2, 0], color=color, stroke_width=stroke)
    return VGroup(a, b)


def open_circle(radius=0.11, color=DIM, stroke=3):
    """The neutral status bullet (an empty circle)."""
    return Circle(radius=radius, stroke_color=color, stroke_width=stroke, fill_opacity=0)


def check_badge(color=GAP, radius=0.2):
    """Check mark in a BG-filled ring; sits on corners of bubbles and cards."""
    ring = Circle(radius=radius, stroke_color=color, stroke_width=3,
                  fill_color=BG, fill_opacity=1)
    return VGroup(ring, check_mark(size=radius * 1.25, color=color, stroke=5))


def spin1_marker(point=ORIGIN, side=0.13):
    """Spin-one data marker (colour-clash rule): hollow INTEGER square."""
    return Square(side_length=side, stroke_color=INTEGER, stroke_width=3,
                  fill_opacity=0).move_to(point)


def spinhalf_marker(point=ORIGIN, radius=0.065):
    """Spin one-half data marker: filled HALF dot."""
    return Dot(point, radius=radius, color=HALF)


def pulse(mob, color=DEFECT, scale_factor=1.12, **kw):
    """Short emphasis: briefly scale and recolour (for 'pulse DEFECT')."""
    return Indicate(mob, color=color, scale_factor=scale_factor, **kw)


def pay_coin(kind="T", radius=0.24):
    """Coin used for 'T pays' / 'S pays' (ch06 s08, ch10 s09)."""
    c = TIME if kind == "T" else SPACE
    disc = Circle(radius=radius, fill_color=c, fill_opacity=1, stroke_color=FG, stroke_width=2)
    lab = M(kind, color=BG, font_size=30).move_to(disc)
    return VGroup(disc, lab)


# =================================================================== 7. TAGS
TAG_READING = "physicist's reading -- not in the paper"
TAG_READING_NEITHER = "physicist's reading -- in neither paper"
TAG_OURS = "our calculation -- not in the paper"
TAG_HEURISTIC = "heuristic"
TAG_ANALOGY = "analogy"
TAG_SCHEMATIC = "schematic"


def tag_box(text, font_size=26, color=DIM):
    """The tag glyph: italic DIM text in a thin rounded box (no placement)."""
    lab = T(r"\textit{" + text + "}", font_size=font_size, color=color)
    box = RoundedRectangle(width=lab.width + 0.32, height=lab.height + 0.24,
                           corner_radius=0.1, stroke_color=color, stroke_width=1.5,
                           fill_color=BG, fill_opacity=0.85).move_to(lab)
    g = VGroup(box, lab)
    g.box, g.label = box, lab
    return g


def tag(text, corner=UR, buff=0.42, **kw):
    """Corner tag (motif 7): on screen for the whole segment.

    corner: UR (default) or UL.  Use the TAG_* constants for the standard texts.
    Intro/outro: tag_in(t) / tag_out(t).
    """
    return tag_box(text, **kw).to_corner(corner, buff=buff)


def inline_tag(text, mob, direction=RIGHT, buff=0.2, **kw):
    """Same glyph placed next to an object ('schematic', 'even rings', ...)."""
    return tag_box(text, **kw).next_to(mob, direction, buff=buff)


def tag_in(t, **kw):
    return FadeIn(t, shift=0.15 * DOWN, **kw)


def tag_out(t, **kw):
    return FadeOut(t, **kw)


def literature_label(mob, direction=RIGHT, buff=0.15, text="literature", font_size=24):
    """Small DIM 'literature' label next to a literature number."""
    return T(r"\textit{" + text + "}", font_size=font_size, color=DIM).next_to(
        mob, direction, buff=buff)


# =================================================================== 6. OBJECTION BUBBLES
OBJECTIONS = {
    "finite": "every finite chain has a gap",
    "theta": r"doesn't the $\theta$-term\\already explain it?",
    "even": r"why even $L$?",
    "beta": r"why not just double $\beta$?",
    "numerics": "isn't this just numerics?",
    "half": r"why doesn't it prove\\spin $\tfrac12$ gapped?",
}
OBJECTION_ORDER = ["finite", "theta", "even", "beta", "numerics", "half"]   # (a)..(f)
_LETTER = dict(zip("abcdef", OBJECTION_ORDER))


def _bubble_outline(w, h, r=0.22, tail=(0.32, 0.72, 0.16, 0.30)):
    """Rounded rectangle with a speech tail on the bottom-left, as ONE closed path."""
    xa, xb, xt, dt = tail
    L, R, B, Tp = -w / 2, w / 2, -h / 2, h / 2
    k = 0.5523 * r
    m = VMobject(stroke_color=DIM, stroke_width=2, fill_color=BG, fill_opacity=0.92)
    m.start_new_path(np.array([L + xb, B, 0]))
    m.add_line_to(np.array([R - r, B, 0]))
    m.add_cubic_bezier_curve_to(np.array([R - r + k, B, 0]), np.array([R, B + r - k, 0]),
                                np.array([R, B + r, 0]))
    m.add_line_to(np.array([R, Tp - r, 0]))
    m.add_cubic_bezier_curve_to(np.array([R, Tp - r + k, 0]), np.array([R - r + k, Tp, 0]),
                                np.array([R - r, Tp, 0]))
    m.add_line_to(np.array([L + r, Tp, 0]))
    m.add_cubic_bezier_curve_to(np.array([L + r - k, Tp, 0]), np.array([L, Tp - r + k, 0]),
                                np.array([L, Tp - r, 0]))
    m.add_line_to(np.array([L, B + r, 0]))
    m.add_cubic_bezier_curve_to(np.array([L, B + r - k, 0]), np.array([L + r - k, B, 0]),
                                np.array([L + r, B, 0]))
    m.add_line_to(np.array([L + xa, B, 0]))
    m.add_line_to(np.array([L + xt, B - dt, 0]))
    m.add_line_to(np.array([L + xb, B, 0]))
    return m


class ObjectionBubble(VGroup):
    """A skeptic's speech bubble (motif 6).  Parts: .shape, .text.

    key: 'finite' (a), 'theta' (b), 'even' (c), 'beta' (d), 'numerics' (e),
    'half' (f); the letters 'a'..'f' also work.
    """

    def __init__(self, key, font_size=26):
        super().__init__()
        key = _LETTER.get(key, key)
        self.key = key
        self.text = T(OBJECTIONS[key], font_size=font_size, color=FG)
        w, h = self.text.width + 0.5, self.text.height + 0.36
        self.shape = _bubble_outline(w, h, r=min(0.22, h / 2.2))
        self.shape.move_to(self.text.get_center() + DOWN * 0.15)   # 0.15 = half the tail
        self.add(self.shape, self.text)
        self.badge = None
        self.answer = None

    def tip(self):
        """Current position of the tail tip (pop-in grows from here)."""
        return self.shape.get_corner(DL) + RIGHT * 0.16

    def to_corner_slot(self, corner=UR):
        """Standard slot for a returning objection: top-right (or top-left), full
        size (the storyboard's 'scale 0.6' would put the text under the 24-pt
        floor); inset so the check badge stays inside x, y in [-6.7, 6.7] x [-3.7, 3.7]."""
        body_top = self.shape.get_top()[1]
        x = 6.45 if corner is UR else -6.45
        self.shift(np.array([x, 3.45, 0]) - np.array(
            [self.shape.get_right()[0] if corner is UR else self.shape.get_left()[0],
             body_top, 0]))
        return self


def objection_bubble(key, corner=UR):
    """A single bubble already placed in its corner slot (UR default, or UL)."""
    return ObjectionBubble(key).to_corner_slot(corner)


def bubble_in(b, **kw):
    """Pop-in: grows out of its tail with a small overshoot."""
    kw.setdefault("rate_func", rate_functions.ease_out_back)
    return GrowFromPoint(b, b.tip(), **kw)


def bubble_indicate(b, **kw):
    """Indicate without flooding the BG fill: outline brightens, bubble swells."""
    tgt = b.copy()
    tgt.scale(1.08)
    tgt.shape.set_stroke(FG, width=3.5)
    kw.setdefault("rate_func", there_and_back)
    kw.setdefault("run_time", 0.9)
    return Transform(b, tgt, **kw)


def bubble_check(b, **kw):
    """Adds a GAP check badge on the bubble's top-right corner (stored as b.badge)."""
    badge = check_badge()
    badge.move_to(b.shape.get_corner(UR) + RIGHT * 0.03 + UP * 0.03)
    b.badge = badge
    return AnimationGroup(GrowFromCenter(badge[0]), Create(badge[1]), lag_ratio=0.4, **kw)


def bubble_answer(b, text, font_size=26, **kw):
    """Small GAP reply under the bubble (e.g. 'the question is uniformity')."""
    lab = T(text, font_size=font_size, color=GAP)
    lab.next_to(b.shape, DOWN, buff=0.18).align_to(b.shape, RIGHT)
    b.answer = lab
    return FadeIn(lab, shift=0.1 * DOWN, **kw)


def bubble_out(b, **kw):
    """Fade the bubble together with its badge and answer, if any."""
    parts = [b] + [m for m in (b.badge, b.answer) if m is not None]
    return FadeOut(*parts, **kw)


def objection_column(right=6.65, top=3.6, buff=0.16):
    """All six bubbles stacked down the right margin (ch01 s06)."""
    col = VGroup(*[ObjectionBubble(k) for k in OBJECTION_ORDER])
    col.arrange(DOWN, aligned_edge=RIGHT, buff=buff)
    col.move_to([right, top, 0], aligned_edge=UR)
    return col


def objection_column_in(col, **kw):
    kw.setdefault("lag_ratio", 0.18)
    return LaggedStart(*[FadeIn(b, shift=0.3 * LEFT) for b in col], **kw)


def objection_collapse(col, corner=UR, **kw):
    """Collapse the column into a small offset stack at the corner, then fade."""
    anchor = np.array([6.55, 3.55, 0]) if corner is UR else np.array([-6.55, 3.55, 0])
    moves = []
    for i, b in enumerate(col):
        tgt = b.copy().scale(0.3)
        tgt.move_to(anchor + DL * 0.04 * i, aligned_edge=UR if corner is UR else UL)
        moves.append(Transform(b, tgt))
    # remover=True: inside a Succession a FadeOut alone would leave the stack behind
    return Succession(AnimationGroup(*moves, lag_ratio=0.06), FadeOut(col, run_time=0.5),
                      remover=True, **kw)


# =================================================================== 8. STATUS CARD
class StatusCard(VGroup):
    """Plain-text status card (ch01 s07, reprise ch10 s06).

    Parts (animate them in sync with the narration):
      .titles      VGroup(2) the two manuscript titles (font 34)
      .title_tags  VGroup(2) DIM tags "even rings" / "odd open chains, end fields"
      .meta        DIM line: author, dates
      .lines       VGroup(3) status lines, each VGroup(icon, text)
    Helpers: anim_titles(), anim_tag(i), anim_meta(), anim_line(i).
    """

    def __init__(self, center=ORIGIN + UP * 0.2):
        super().__init__()
        t1 = T(r"``The periodic spin-one Haldane gap''", font_size=34)
        t2 = T(r"``A boundary-field gap for the spin-one Heisenberg chain''", font_size=34)
        self.titles = VGroup(t1, t2).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        x_tag = self.titles.get_right()[0] + 0.45
        tags = VGroup()
        for t, s in zip(self.titles, ["even rings", "odd open chains, end fields"]):
            g = tag_box(s)
            g.move_to([x_tag, t.get_center()[1], 0], aligned_edge=LEFT)
            tags.add(g)
        self.title_tags = tags
        self.meta = T(r"author: OpenAI $\cdot$ manuscripts dated 24 Sep 2026 $\cdot$ "
                      r"released 6 Oct 2026", font_size=26, color=DIM)
        self.meta.next_to(self.titles, DOWN, buff=0.38).align_to(self.titles, LEFT)
        rows = [
            (open_circle(), r"claimed proof $\cdot$ preprint $\cdot$ not yet independently refereed"),
            (check_mark(0.34), r"analytic argument: short, checkable by hand"),
            (check_mark(0.34), r"finite computations: published with the paper, re-runnable on a laptop"),
        ]
        lines = VGroup()
        for icon, s in rows:
            txt = T(s, font_size=28)
            icon.next_to(txt, LEFT, buff=0.3)
            lines.add(VGroup(icon, txt))
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        lines.next_to(self.meta, DOWN, buff=0.7).align_to(self.titles, LEFT).shift(RIGHT * 0.2)
        wmax = max(ln[0].width for ln in lines)
        xl = min(ln[0].get_left()[0] for ln in lines)
        for icon, txt in lines:
            icon.set_x(xl + wmax / 2)
            txt.shift(RIGHT * (xl + wmax + 0.3 - txt.get_left()[0]))
        self.lines = lines
        self.add(self.titles, self.title_tags, self.meta, self.lines)
        self.move_to(center)

    def anim_titles(self, **kw):
        return LaggedStart(*[FadeIn(t, shift=0.15 * UP) for t in self.titles], lag_ratio=0.35, **kw)

    def anim_tag(self, i, **kw):
        return FadeIn(self.title_tags[i], shift=0.15 * LEFT, **kw)

    def anim_meta(self, **kw):
        return FadeIn(self.meta, **kw)

    def anim_line(self, i, **kw):
        icon, txt = self.lines[i]
        grow = Create(icon) if i > 0 else GrowFromCenter(icon)
        return AnimationGroup(grow, FadeIn(txt, shift=0.1 * RIGHT), lag_ratio=0.3, **kw)


# =================================================================== 1. GAPPLOT
def load_gaps():
    """(L, gap) lists for spin 1/2 and spin 1 from data/gaps.csv, sorted by L."""
    half, one = [], []
    with open(DATA / "gaps.csv") as f:
        for r in csv.DictReader(f):
            row = (int(r["L"]), float(r["gap_first_excitation"]))
            (half if float(r["S"]) == 0.5 else one).append(row)
    return sorted(half), sorted(one)


class GapPlot(VGroup):
    """The ch01 gap-versus-1/L plot (motif 1); identical object in ch10 s10.

    Structure (fixed, so that zoomed() can transform it):
      .ax, .x_label, .y_label, .lines (VGroup(half_segments, one_segments)),
      .half_pts (Dots, increasing L), .one_pts (hollow squares, increasing L).
    Separate objects (not in the group): .series_labels(), .counter(),
      .half_guide(), .literature_line(), .what_if_curves(), .floor_lines().
    Animations: build_axes(), build_data() (points in L order, counter ticks).
    """
    X_RANGE = (0, 0.27, 0.05)
    Y_RANGE = (0, 1.05, 0.2)

    def __init__(self, x_range=X_RANGE, y_range=Y_RANGE, x_length=8.0, y_length=4.6,
                 center=(0, -0.4, 0)):
        super().__init__()
        self.params = dict(x_range=tuple(x_range), y_range=tuple(y_range),
                           x_length=x_length, y_length=y_length, center=tuple(center))
        x0, x1, dx = x_range
        y0, y1, dy = y_range
        xnums = [round(v, 4) for v in np.arange(dx, x1 + 1e-9, dx)]
        ynums = [round(v, 4) for v in np.arange(dy, y1 + 1e-9, dy)]
        xdec = max(0, int(np.ceil(-np.log10(dx) - 1e-9)))
        ax = Axes(x_range=list(x_range), y_range=list(y_range), x_length=x_length,
                  y_length=y_length, tips=False,
                  axis_config={"color": DIM, "stroke_width": 2, "include_ticks": True,
                               "tick_size": 0.06, "font_size": 24},
                  x_axis_config={"numbers_to_include": xnums,
                                 "decimal_number_config": {"num_decimal_places": xdec,
                                                           "color": DIM}},
                  y_axis_config={"numbers_to_include": ynums,
                                 "decimal_number_config": {"num_decimal_places": 1,
                                                           "color": DIM}})
        mid = (ax.c2p(x0, y0) + ax.c2p(x1, y1)) / 2
        ax.shift(np.array(center, dtype=float) - mid)
        self.ax = ax
        self.x_label = M(r"1/L", font_size=32).next_to(ax.c2p(x1, 0), RIGHT, buff=0.2)
        self.y_label = M(r"\gamma_L=E_1-E_0", font_size=32).next_to(
            ax.c2p(0, y1), UR, buff=0.15)
        self.half_data, self.one_data = load_gaps()
        self.half_pts = VGroup(*[spinhalf_marker(self._pt(L, g)) for L, g in self.half_data])
        self.one_pts = VGroup(*[spin1_marker(self._pt(L, g)) for L, g in self.one_data])
        self.lines = VGroup(self._segments(self.half_data, HALF),
                            self._segments(self.one_data, INTEGER))
        for pts, data in ((self.half_pts, self.half_data), (self.one_pts, self.one_data)):
            for p, (L, g) in zip(pts, data):
                if 1 / L > x1 + 1e-9:
                    p.set_opacity(0)
        self.add(self.ax, self.x_label, self.y_label, self.lines, self.half_pts, self.one_pts)
        self.extras = {}

    # ---------------------------------------------------------------- coordinates
    def c2p(self, x, y):
        return self.ax.c2p(x, y)

    def _pt(self, L, g):
        return self.ax.c2p(1 / L, g)

    def _segments(self, data, color):
        """Thin polyline as separate segments (L ascending).  Segments with an
        end beyond the x-range sit at their true place, invisible (no clipping)."""
        x1 = self.params["x_range"][1]
        segs = VGroup()
        for (La, ga), (Lb, gb) in zip(data[:-1], data[1:]):
            s = VMobject(stroke_color=color, stroke_width=2, stroke_opacity=0.5)
            s.set_points_as_corners([self.ax.c2p(1 / La, ga), self.ax.c2p(1 / Lb, gb)])
            if 1 / La > x1 + 1e-9:
                s.set_stroke(opacity=0)
            segs.add(s)
        return segs

    # ---------------------------------------------------------------- build animations
    def build_axes(self, **kw):
        """Axes and labels only (points stay hidden until build_data)."""
        return AnimationGroup(Create(self.ax), FadeIn(self.x_label), FadeIn(self.y_label),
                              lag_ratio=0.1, **kw)

    def counter(self, font_size=32):
        """'L = 4' counter at the top right of the axes, for build_data()."""
        lab = M("L=", font_size=font_size)
        num = Integer(4, font_size=font_size)
        num.next_to(lab, RIGHT, buff=0.12)
        g = VGroup(lab, num)
        g.next_to(self.ax.c2p(self.params["x_range"][1], self.params["y_range"][1]),
                  DL, buff=0.05).shift(UP * 0.55)
        self._counter = g
        return g

    def build_data(self, lag_ratio=0.15, counter=None, **kw):
        """Points appear in order of increasing L (right to left), the two spins
        alternating; each series' thin polyline grows with it; the optional counter
        (from .counter()) ticks 4 -> 24 in sync.  Start state: all data hidden."""
        order = []
        for L in sorted({L for L, _ in self.half_data + self.one_data}):
            for kind, data in (("h", self.half_data), ("o", self.one_data)):
                for i, (LL, _) in enumerate(data):
                    if LL == L:
                        order.append((kind, i, L))
        K = len(order)
        w = 1.0 / (1 + (K - 1) * lag_ratio)
        starts = [k * lag_ratio * w for k in range(K)]
        pts = {"h": self.half_pts, "o": self.one_pts}
        segs = {"h": self.lines[0], "o": self.lines[1]}
        data = {"h": self.half_data, "o": self.one_data}
        saved = {key: [p.copy() for p in pts[key]] for key in pts}
        ends = {key: [(s.get_start().copy(), s.get_end().copy()) for s in segs[key]] for key in segs}
        seg_on = {key: [s.get_stroke_opacity() > 0 for s in segs[key]] for key in segs}
        num = counter[1] if counter is not None else None

        def upd(group, alpha):
            latest = 4
            for k, (kind, i, L) in enumerate(order):
                t = float(np.clip((alpha - starts[k]) / w, 0, 1))
                if alpha >= starts[k]:
                    latest = max(latest, L)
                p = pts[kind][i]
                p.become(saved[kind][i])
                if t < 1:
                    s = smooth(t)
                    p.scale(max(1e-3, 0.4 + 0.6 * s)).set_opacity(s)
                if i > 0:
                    a, b = ends[kind][i - 1]
                    seg = segs[kind][i - 1]
                    seg.set_points_as_corners([a, a + smooth(t) * (b - a) + 1e-6 * RIGHT])
                    seg.set_stroke(opacity=0.5 if (t > 0 and seg_on[kind][i - 1]) else 0)
            if num is not None:
                old = num.get_left()
                num.set_value(latest)
                num.move_to(old, aligned_edge=LEFT)

        group = VGroup(self.half_pts, self.one_pts, self.lines)
        if counter is not None:
            group.add(counter)
        return UpdateFromAlphaFunc(group, upd, **kw)

    def hide_data(self):
        """Instantly hide points and polylines (to add the plot before build_data)."""
        for p in [*self.half_pts, *self.one_pts]:
            p.set_opacity(0)
        for s in [*self.lines[0], *self.lines[1]]:
            s.set_stroke(opacity=0)
        return self

    # ---------------------------------------------------------------- overlays
    def series_labels(self, font_size=28):
        """Direct labels 'spin 1' (above its curve) and 'spin 1/2' (below its curve)."""
        one = T(r"spin $1$", font_size=font_size, color=INTEGER)
        half = T(r"spin $\tfrac12$", font_size=font_size, color=HALF)
        x1 = self.params["x_range"][1]
        if x1 >= 0.2:            # the full ch01 view
            one.move_to(self.c2p(0.135, 0.76))
            half.move_to(self.c2p(0.125, 0.155))
        else:                    # zoomed views
            one.move_to(self.c2p(0.6 * x1, 0.745))
            half.move_to(self.c2p(0.75 * x1, 0.075))
        g = VGroup(half, one)
        self.extras["series_labels"] = g
        return g

    def half_guide(self):
        """Dashed HALF guide y = 4.385 x from the L = 24 point to the origin, '-> 0'."""
        L, g = self.half_data[-1]
        line = DashedLine(self._pt(L, g), self.c2p(0, 0), color=HALF, stroke_width=3,
                          dash_length=0.1)
        to0 = M(r"\to0", color=HALF, font_size=30).next_to(self.c2p(0, 0), LEFT, buff=0.12)
        grp = VGroup(line, to0)
        self.extras["half_guide"] = grp
        return grp

    def literature_line(self):
        """Dashed INTEGER segment at 0.4105 for x in [0, 1/16] with its DIM label
        (two lines, placed in the empty upper-left and tied by a short leader)."""
        y = 0.4105
        line = DashedLine(self.c2p(0, y), self.c2p(1 / 16, y), color=INTEGER, stroke_width=3,
                          dash_length=0.1)
        lab = VGroup(T(r"0.4105 $\cdot$ literature", font_size=24, color=DIM),
                     T(r"DMRG, White--Huse 1993", font_size=24, color=DIM)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        y0 = self.ax.c2p(0, 0)[1]
        lab.move_to([self.c2p(0, 0)[0] + 0.2, y0 + 2.9, 0], aligned_edge=DL)
        lx = lab.get_left()[0] + 0.55
        leader = Line([lx, lab.get_bottom()[1] - 0.06, 0], [lx, line.get_center()[1] + 0.07, 0],
                      color=DIM, stroke_width=1.5)
        grp = VGroup(line, leader, lab)
        self.extras["literature_line"] = grp
        return grp

    def what_if_curves(self, start=None):
        """Three DIM dashed 'what-if' continuations from the last spin-1 square:
        one stays flat, two bend down to 0 at very small 1/L (ch01 s04)."""
        L, g = self.one_data[-1]
        xs = 1 / L

        def flat(x):
            return g - 0.006 * (1 - x / xs)

        def dive(x0, w):
            def f(x):
                return g * np.tanh((x - x0) / w) / np.tanh((xs - x0) / w)
            return f

        curves = VGroup()
        for f, xa in ((flat, 0.0), (dive(0.016, 0.012), 0.016), (dive(0.004, 0.006), 0.004)):
            c = self.ax.plot(f, x_range=[xa, xs, (xs - xa) / 60], color=DIM, stroke_width=3)
            c.reverse_points()                       # draw from the data point leftwards
            curves.add(DashedVMobject(c, num_dashes=24, dashed_ratio=0.55))
        self.extras["what_if"] = curves
        return curves

    def floor_lines(self, color=GAP, stroke=5):
        """ch10 s10 floor at TRUE height: 4.79e-4 for 1/L <= 1/60, and the short
        3.82e-3 step for 1/L <= 1/2304 (both hug the axis on this scale)."""
        a = Line(self.c2p(0, 4.79e-4), self.c2p(1 / 60, 4.79e-4), color=color, stroke_width=stroke)
        b = Line(self.c2p(0, 3.82e-3), self.c2p(1 / 2304, 3.82e-3), color=color,
                 stroke_width=stroke)
        grp = VGroup(a, b)
        self.extras["floor"] = grp
        return grp

    def with_extras(self):
        """VGroup(plot, *extras) for moving/fading the plot with its overlays
        (e.g. ch01 s05: shrink to the left half at opacity 0.3)."""
        return VGroup(self, *self.extras.values())

    # ---------------------------------------------------------------- zoom
    def zoomed(self, x_max=0.07, x_step=0.01, **kw):
        """Re-range the x axis to [0, x_max] (y unchanged): points slide right,
        those beyond x_max fly out and fade; guides made with this plot follow.

            plot, anim = plot.zoomed(0.07, 0.01)
            self.play(anim)

        Returns (new_plot, animation).  Use new_plot (and new_plot.extras[...])
        from then on.  Extras not in the scene are simply rebuilt.
        """
        p = dict(self.params)
        p["x_range"] = (0, x_max, x_step)
        new = GapPlot(**p)
        # tick marks and numbers cross-fade in place instead of morphing
        for attr in ("ticks", "numbers"):
            og, ng = getattr(self.ax.x_axis, attr), getattr(new.ax.x_axis, attr)
            vis = [m for m in og.submobjects
                   if max(m.get_stroke_opacity(), m.get_fill_opacity()) > 1e-3]
            og.remove(*[m for m in og.submobjects if m not in vis])
            nv = list(ng.submobjects)
            og.add(*[m.copy().scale(0.05).set_opacity(0) for m in nv])
            ng.remove(*nv)
            ng.add(*[m.copy().scale(0.05).set_opacity(0) for m in vis], *nv)
        anims = [ReplacementTransform(self, new)]
        builders = {"series_labels": new.series_labels, "half_guide": new.half_guide,
                    "literature_line": new.literature_line, "what_if": new.what_if_curves,
                    "floor": new.floor_lines}
        for name, old in self.extras.items():
            tgt = builders[name]()
            anims.append(ReplacementTransform(old, tgt))
        # beyond-range markers fly out to the right as they fade
        for pts, data in ((new.half_pts, new.half_data), (new.one_pts, new.one_data)):
            for q, (L, g) in zip(pts, data):
                if 1 / L > x_max + 1e-9:
                    q.move_to(new.ax.c2p(1 / L, g))
        return new, AnimationGroup(*anims, **kw)


# =================================================================== 2. TORUS + TWO KNIVES
class Torus(VGroup):
    """The L x beta torus (motif 2), built on visuals.torus_rect.

    Parts: .rect, .grid, .chev_time (top/bottom, TIME), .chev_space (left/right,
    SPACE), .L_label (below, SPACE), .beta_label (left, TIME).
    Use this rather than torus_rect directly: the beta label sits a little
    further out (buff 0.32) so the time knife's handle never touches it.
    """

    def __init__(self, width=5.0, height=3.0, nx=0, ny=0, labels=True,
                 L_tex="L", beta_tex=r"\beta", label_size=36):
        super().__init__()
        base = torus_rect(width, height, nx=nx, ny=ny, label_L=False, label_beta=False)
        self.dims = dict(width=width, height=height, nx=nx, ny=ny, labels=labels,
                         L_tex=L_tex, beta_tex=beta_tex, label_size=label_size)
        self.rect, self.grid = base[0], base[1]
        self.chev_time = VGroup(base[2], base[3])
        self.chev_space = VGroup(base[4], base[5])
        self.add(self.rect, self.grid, self.chev_time, self.chev_space)
        if labels:
            self.L_label = M(L_tex, color=SPACE, font_size=label_size).next_to(
                self.rect, DOWN, buff=0.2)
            self.beta_label = M(beta_tex, color=TIME, font_size=label_size).next_to(
                self.rect, LEFT, buff=0.32)
            self.add(self.L_label, self.beta_label)

    # geometry --------------------------------------------------------
    @property
    def left(self):
        return self.rect.get_left()[0]

    @property
    def right(self):
        return self.rect.get_right()[0]

    @property
    def top(self):
        return self.rect.get_top()[1]

    @property
    def bottom(self):
        return self.rect.get_bottom()[1]

    def x_at(self, frac):
        return self.left + frac * (self.right - self.left)

    def y_at(self, frac):
        return self.bottom + frac * (self.top - self.bottom)

    def site_x(self, i):
        """x of site world line i (i = 0 is the identified left/right edge)."""
        nx = max(self.dims["nx"], 1)
        return self.left + (i % nx) * (self.right - self.left) / nx

    def bond_x(self, k):
        """x midway between site lines k and k+1 (where the space knife cuts)."""
        nx = max(self.dims["nx"], 1)
        return self.left + ((k % nx) + 0.5) * (self.right - self.left) / nx

    def bond_frac(self, k):
        nx = max(self.dims["nx"], 1)
        return ((k % nx) + 0.5) / nx

    # variants & animations ------------------------------------------
    def resized(self, width=None, height=None, anchor=DL):
        """A fresh Torus of the new size, same style, sharing the `anchor` corner
        of the rectangle.  Animate with Transform(torus, torus.resized(...))."""
        d = dict(self.dims)
        if width is not None:
            d["width"] = width
        if height is not None:
            d["height"] = height
        new = Torus(**d)
        new.shift(self.rect.get_corner(anchor) - new.rect.get_corner(anchor))
        return new

    def periodicity_labels(self, font_size=28):
        """'time is periodic: trace' (above, TIME) and 'space is periodic: ring'
        (right, SPACE).  Returns VGroup(time_label, space_label)."""
        t = T("time is periodic: trace", font_size=font_size, color=TIME)
        t.next_to(self.rect, UP, buff=0.3)
        s = T("space is periodic: ring", font_size=font_size, color=SPACE)
        s.next_to(self.rect, RIGHT, buff=0.35)
        return VGroup(t, s)

    def pulse_chevrons(self, **kw):
        return AnimationGroup(
            *[Indicate(c, color=TIME, scale_factor=1.7) for c in self.chev_time],
            *[Indicate(c, color=SPACE, scale_factor=1.7) for c in self.chev_space], **kw)

    def tiling_overlays(self, inset=0.07, badge_size=30):
        """The four-tori identity on this torus (2n x 2beta), ch06 s06/ch10 s09.

        Returns a list of 4 VGroups, in order: whole (+1), two tall halves
        n x 2beta (-2, split by a SPACE cut), two wide halves 2n x beta (-2, TIME
        cut), four quarters (+4).  Each group is (tiles..., badge) and .badge.
        """
        L, R, B, Tp = self.left, self.right, self.bottom, self.top
        xm, ym = (L + R) / 2, (B + Tp) / 2

        def tile(x0, x1, y0, y1, color):
            r = Rectangle(width=x1 - x0 - 2 * inset, height=y1 - y0 - 2 * inset,
                          stroke_color=color, stroke_width=3, fill_color=color,
                          fill_opacity=0.10)
            return r.move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])

        specs = [
            ([(L, R, B, Tp)], FG, "+1"),
            ([(L, xm, B, Tp), (xm, R, B, Tp)], SPACE, "-2"),
            ([(L, R, B, ym), (L, R, ym, Tp)], TIME, "-2"),
            ([(L, xm, B, ym), (xm, R, B, ym), (L, xm, ym, Tp), (xm, R, ym, Tp)], FG, "+4"),
        ]
        out = []
        for rects, col, w in specs:
            g = VGroup(*[tile(*r, col) for r in rects])
            badge_t = M(w, font_size=badge_size, color=FG)
            box = RoundedRectangle(width=badge_t.width + 0.3, height=badge_t.height + 0.22,
                                   corner_radius=0.1, stroke_color=col, stroke_width=2,
                                   fill_color=BG, fill_opacity=1).move_to(badge_t)
            badge = VGroup(box, badge_t).next_to(self.rect, RIGHT, buff=0.3).align_to(
                self.rect, UP)
            g.add(badge)
            g.badge = badge
            out.append(g)
        return out


class Knife(VGroup):
    """A knife on a Torus (motif 2).

    kind='time'  : horizontal TIME line across the full width, triangular handle
                   at its left end; sweeps upward (thermal reading).
    kind='space' : vertical SPACE line across the full height, handle at the top;
                   sweeps rightward and cuts THROUGH A BOND (use at_bond / bond
                   indices, never site lines).
    `at` is the fraction of the height (time) or width (space); 0 = bottom/left.
    Parts: .blade, .handle, .glow (wide translucent copy, off by default).
    """

    def __init__(self, torus, kind="time", at=0.5, stroke=STROKE_KNIFE, handle=0.2):
        super().__init__()
        self.torus, self.kind, self.frac = torus, kind, at
        c = TIME if kind == "time" else SPACE
        self.color = c
        L, R, B, Tp = torus.left, torus.right, torus.bottom, torus.top
        h = handle
        if kind == "time":
            y = torus.y_at(at)
            self.blade = Line([L - 0.04, y, 0], [R + 0.1, y, 0], color=c, stroke_width=stroke)
            self.handle = Polygon([L - 0.04, y, 0], [L - 0.04 - 0.87 * h, y + h / 2, 0],
                                  [L - 0.04 - 0.87 * h, y - h / 2, 0],
                                  stroke_width=0, fill_color=c, fill_opacity=1)
        else:
            x = torus.x_at(at)
            self.blade = Line([x, Tp + 0.04, 0], [x, B - 0.1, 0], color=c, stroke_width=stroke)
            self.handle = Polygon([x, Tp + 0.04, 0], [x - h / 2, Tp + 0.04 + 0.87 * h, 0],
                                  [x + h / 2, Tp + 0.04 + 0.87 * h, 0],
                                  stroke_width=0, fill_color=c, fill_opacity=1)
        self.glow = self.blade.copy().set_stroke(width=stroke * 3.2, opacity=0)
        self.glow.set_z_index(-1)
        self.add(self.glow, self.blade, self.handle)

    def _shift_to(self, frac):
        if self.kind == "time":
            return UP * (self.torus.y_at(frac) - self.torus.y_at(self.frac))
        return RIGHT * (self.torus.x_at(frac) - self.torus.x_at(self.frac))

    # animations ------------------------------------------------------
    def cut_in(self, **kw):
        """Handle slides in, then the blade is drawn across the torus."""
        d = LEFT if self.kind == "time" else UP
        return AnimationGroup(FadeIn(self.handle, shift=-0.3 * d),
                              Create(self.blade, rate_func=rate_functions.ease_in_out_sine),
                              lag_ratio=0.35, **kw)

    def glow_on(self, opacity=0.3, **kw):
        """'The cut glows'."""
        return self.glow.animate(**kw).set_stroke(opacity=opacity)

    def glow_off(self, **kw):
        return self.glow.animate(**kw).set_stroke(opacity=0)

    def move_to_frac(self, frac, **kw):
        """Lazy move (safe to queue several before playing them in order)."""
        sh = self._shift_to(frac)
        self.frac = frac
        return ApplyMethod(self.shift, sh, **kw)

    def sweep(self, to=None, **kw):
        """Continuous sweep (up for time, right for space) to fraction `to`
        (default: 0.97 of the way)."""
        kw.setdefault("rate_func", rate_functions.ease_in_out_sine)
        return self.move_to_frac(0.97 if to is None else to, **kw)

    def to_bond(self, k, **kw):
        return self.move_to_frac(self.torus.bond_frac(k), **kw)

    def cut_copy(self, color=None):
        """A copy of the cut slice (the torus edge-to-edge line) to lift out."""
        T_ = self.torus
        if self.kind == "time":
            y = T_.y_at(self.frac)
            ln = Line([T_.left, y, 0], [T_.right, y, 0])
        else:
            x = T_.x_at(self.frac)
            ln = Line([x, T_.bottom, 0], [x, T_.top, 0])
        return ln.set_stroke(color or self.color, width=STROKE_KNIFE)

    def steps(self, targets, label_tex=None, label_size=28, step_time=1.0, **kw):
        """Jump through `targets` (fractions; for kind='space' integers are bond
        indices).  A faint transient label (e.g. r"e^{-\\delta\\tau H}" or "X") shows
        during each jump, beside it.  Space-knife jumps past the right edge wrap
        around to the left (space is periodic)."""
        anims = []
        for t in targets:
            frac = self.torus.bond_frac(t) if (self.kind == "space" and isinstance(t, int)) else t
            old = self.frac
            parts = []
            if self.kind == "space" and frac < old:            # wrap around
                parts.append(self._wrap_anim(frac, run_time=step_time))
            else:
                parts.append(self.move_to_frac(frac, run_time=step_time))
            if label_tex is not None:
                lab = M(label_tex, font_size=label_size, color=DIM)
                if self.kind == "time":
                    lab.next_to([self.torus.right, self.torus.y_at((old + frac) / 2), 0], RIGHT,
                                buff=0.3)
                else:
                    xm = self.torus.x_at((old + frac) / 2 if frac > old else frac)
                    lab.move_to([xm, self.torus.top + 0.55, 0])
                parts.append(_transient(lab, run_time=step_time))
            anims.append(AnimationGroup(*parts))
        return Succession(*anims, **kw)

    def _wrap_anim(self, frac, **kw):
        """Exit through the right edge, re-enter through the left (periodic)."""
        T_ = self.torus
        out_dx = T_.right - T_.x_at(self.frac) + 0.25
        in_dx = T_.x_at(frac) - T_.left + 0.25
        sh = self._shift_to(frac)
        self.frac = frac
        state = {}

        def upd(m, a):
            if "saved" not in state:          # captured when the step starts
                state["saved"] = m.copy()
                state["g0"] = m.glow.get_stroke_opacity()
            saved, g0 = state["saved"], state["g0"]
            m.become(saved)
            if a < 0.5:
                o = 1 - smooth(2 * a)
                m.shift(RIGHT * out_dx * smooth(2 * a))
            else:
                o = smooth(2 * a - 1)
                m.shift(sh + LEFT * in_dx * (1 - smooth(2 * a - 1)))
            m.blade.set_stroke(opacity=o)
            m.handle.set_fill(opacity=o)
            m.glow.set_stroke(opacity=g0 * o)
        return UpdateFromAlphaFunc(self, upd, **kw)


def _transient(mob, peak=1.0, **kw):
    """Fade in, hold, fade out within one animation (safe inside Successions:
    the mobject is invisible until its turn and left invisible afterwards)."""
    mob.set_opacity(0)

    def upd(m, a):
        m.set_opacity(peak * min(1.0, 4 * a, 4 * (1 - a)))
    return UpdateFromAlphaFunc(mob, upd, **kw)


def time_knife(torus, at=0.5, **kw):
    return Knife(torus, "time", at=at, **kw)


def space_knife(torus, at=None, bond=1, **kw):
    """Vertical knife; by default at bond 1 (x = -1.75 on the ch04 torus)."""
    if at is None:
        at = torus.bond_frac(bond)
    return Knife(torus, "space", at=at, **kw)


class TorusThumb(VGroup):
    """Small torus pinned top-left from ch05 on (motif 2).  Its width or height
    visibly DOUBLES when L or beta doubles (seams mark the copies), then the
    whole thumbnail re-fits its box; labels read L, 2L, 4L... and beta, 2beta...

    Same part order as Torus (rect, seams, chev_time, chev_space, L_label,
    beta_label), so ReplacementTransform(big_torus, thumb) morphs piece by piece.
    """

    MAX_SEAMS = 15

    def __init__(self, w=1.75, h=1.05, max_w=3.0, max_h=2.0, anchor=None,
                 L_tex="L", beta_tex=r"\beta", label_size=28):
        super().__init__()
        self.w0, self.h0, self.max_w, self.max_h = w, h, max_w, max_h
        self.L_tex, self.beta_tex, self.label_size = L_tex, beta_tex, label_size
        self.anchor = np.array([-6.05, 3.45, 0]) if anchor is None else np.array(anchor, float)
        self.mL, self.mb = 1, 1
        self.s = self._fit_scale(1, 1)
        self.add(*self._build(self.mL, self.mb, self.s))
        self.rect, self.seams, self.chev_time, self.chev_space, self.L_label, self.beta_label = \
            self.submobjects

    def _fit_scale(self, mL, mb):
        return min(1.0, self.max_w / (mL * self.w0), self.max_h / (mb * self.h0))

    def _label(self, m, base):
        return (str(m) if m > 1 else "") + base

    def _build(self, mL, mb, s):
        W, H = mL * self.w0 * s, mb * self.h0 * s
        ul = self.anchor
        rect = Rectangle(width=W, height=H, stroke_color=FG, stroke_width=2, fill_color=FG,
                         fill_opacity=0.03).move_to(ul + np.array([W / 2, -H / 2, 0]))
        L, R, Tp, B = ul[0], ul[0] + W, ul[1], ul[1] - H
        seams = VGroup()
        for k in range(1, self.MAX_SEAMS + 1):        # vertical seams (L copies)
            x = L + min(k, mL) * W / mL
            seams.add(DashedLine([x, B, 0], [x, Tp, 0], color=DIM, stroke_width=1.5,
                                 dash_length=0.06).set_opacity(0.8 if k < mL else 0))
        for k in range(1, self.MAX_SEAMS + 1):        # horizontal seams (beta copies)
            y = Tp - min(k, mb) * H / mb
            seams.add(DashedLine([L, y, 0], [R, y, 0], color=DIM, stroke_width=1.5,
                                 dash_length=0.06).set_opacity(0.8 if k < mb else 0))
        cs = 0.6          # chevrons sit mid-way along the FIRST copy, never on a seam
        cx, cy = L + 0.5 * W / mL, Tp - 0.5 * H / mb
        ct = VGroup(*[M(">", color=TIME, font_size=28).scale(cs).move_to([cx, y, 0])
                      for y in (B, Tp)])
        csp = VGroup(*[M(r"\gg", color=SPACE, font_size=28).scale(cs).rotate(PI / 2)
                     .move_to([x, cy, 0]) for x in (L, R)])
        Ll = M(self._label(mL, self.L_tex), color=SPACE, font_size=self.label_size)
        Ll.next_to(rect, DOWN, buff=0.12)
        bl = M(self._label(mb, self.beta_tex), color=TIME, font_size=self.label_size)
        bl.next_to(rect, LEFT, buff=0.12)
        return [rect, seams, ct, csp, Ll, bl]

    def _anim_to(self, mL, mb, s, **kw):
        tgt = self._build(mL, mb, s)
        return AnimationGroup(*[Transform(a, b) for a, b in zip(self.submobjects, tgt)], **kw)

    def _double(self, dL, db, **kw):
        mL, mb = self.mL * dL, self.mb * db
        grow = self._anim_to(mL, mb, self.s, run_time=1.0)
        s_new = self._fit_scale(mL, mb)
        self.mL, self.mb = mL, mb
        if abs(s_new - self.s) < 1e-9:
            return Succession(grow, **kw)
        fit = self._anim_to(mL, mb, s_new, run_time=0.6)
        self.s = s_new
        return Succession(grow, fit, **kw)

    def double_beta(self, **kw):
        """Height doubles (a second copy appears below the seam), then re-fit."""
        return self._double(1, 2, **kw)

    def double_L(self, **kw):
        """Width doubles, then re-fit."""
        return self._double(2, 1, **kw)

    def reset(self, **kw):
        """Back to L x beta (animated)."""
        self.mL, self.mb = 1, 1
        self.s = self._fit_scale(1, 1)
        return self._anim_to(1, 1, self.s, **kw)


# =================================================================== 3. WEIGHT BARS
class WeightBars(VGroup):
    """visuals.weight_bars with the standard motions (motif 3).

    Parts: .base, .bars.  Probabilities in .probs.  Tallest bar = highlight
    (pass highlight_color=TIME or SPACE; default = color).  Put the tallest bar
    first so the defect brace spans the small bars.

    Standard squaring, ALWAYS in two steps:
        s1, s2 = wb.square()        # s1: heights -> p^2 ; s2: renormalise to sum 1
        self.play(s1); self.play(s2)
    Separate (not in the group, so they can be faded independently):
        wb.defect_brace(label)      # DEFECT brace over the small bars (follows squaring)
        wb.caption(tex)             # e.g. r"e^{-\\beta E_k}" under the bars;
                                    # square(relabel=r"e^{-2\\beta E_k}") rewrites it
    signed=True (ch04 s11): values are drawn as-is (no normalisation), negative
    values hang below the base; morph_to(values) animates to new values.
    """

    def __init__(self, weights, width=5.0, height=2.6, color=FG, highlight_color=None,
                 bar_buff=0.12, signed=False, value_scale=None):
        super().__init__()
        w = np.asarray(weights, dtype=float)
        self.signed = signed
        self.H = height
        self.width_ = width
        self.color = color
        self.hl = int(np.argmax(np.abs(w)))
        self.hl_color = color if highlight_color is None else highlight_color
        if signed:
            self.vals = w
            self.k = height if value_scale is None else value_scale
        else:
            self.vals = w / w.sum()
            self.k = height
        base_g = weight_bars(np.abs(w) + 1e-12, width=width, height=height, color=color,
                             highlight=self.hl, highlight_color=self.hl_color, bar_buff=bar_buff)
        self.base, self.bars = base_g[0], base_g[1]
        self.add(self.base, self.bars)
        for i in range(len(w)):
            self.bars[i].become(self._rect(i, self.vals[i]))
        self.brace = None
        self.cap = None

    @property
    def probs(self):
        return self.vals

    def purity(self):
        return float((self.vals ** 2).sum())

    def y_of(self, p):
        """Screen y of probability level p (e.g. the dashed 1/2 line of ch05 s06)."""
        return self.base.get_center()[1] + p * self.k

    def level_line(self, p, color=DIM, label=None, font_size=28):
        """Dashed horizontal line at probability p across the bars (+ optional label)."""
        y = self.y_of(p)
        ln = DashedLine([self.base.get_left()[0], y, 0], [self.base.get_right()[0], y, 0],
                        color=color, stroke_width=2.5, dash_length=0.1)
        if label is None:
            return ln
        return VGroup(ln, M(label, color=color, font_size=font_size).next_to(ln, RIGHT, 0.15))

    def defect(self):
        return 1.0 - self.purity()

    def _rect(self, i, v):
        b = self.bars[i]
        y0 = self.base.get_center()[1]
        h = max(abs(v) * self.k, 1e-3)
        r = Rectangle(width=b.width, height=h, stroke_width=0,
                      fill_color=self.hl_color if i == self.hl else self.color,
                      fill_opacity=0.9)
        r.move_to([b.get_center()[0], y0, 0], aligned_edge=DOWN if v >= 0 else UP)
        return r

    def morph_to(self, values, **kw):
        """Animate the bars to new (raw) values; no normalisation."""
        v = np.asarray(values, dtype=float)
        anims = [Transform(self.bars[i], self._rect(i, v[i])) for i in range(len(v))]
        self.vals = v
        extra = []
        if self.brace is not None:
            extra.append(Transform(self.brace, self._brace_for(v)))
        return AnimationGroup(*anims, *extra, **kw)

    def square(self, relabel=None, **kw):
        """Two-step squaring.  Returns (step1, step2):
        step1: every bar -> height p_i^2 on the same scale (small bars collapse);
        step2: rescale so the bars sum to 1 again (the tall bar grows).
        relabel: optional new caption tex, rewritten during step 2."""
        p = self.vals
        p2 = p ** 2
        s1 = self.morph_to(p2, **kw)
        q = p2 / p2.sum()
        anims2 = [self.morph_to(q)]
        if relabel is not None and self.cap is not None:
            new = M(relabel, color=self.cap.get_color(), font_size=self._cap_size)
            new.move_to(self.cap, aligned_edge=UP)
            anims2.append(TransformMatchingShapes(self.cap, new))
            self.cap = new
        return s1, AnimationGroup(*anims2, **kw)

    # overlays ----------------------------------------------------------
    def _small(self, vals):
        idx = [i for i in range(len(vals)) if i != self.hl]
        return VGroup(*[self._rect(i, vals[i]) for i in idx])

    def _brace_for(self, vals):
        small = self._small(vals)
        top = max(r.get_top()[1] for r in small)
        ref = Line([small.get_left()[0], top, 0], [small.get_right()[0], top, 0])
        br = Brace(ref, direction=UP, buff=0.12, color=DEFECT)
        lab = self._brace_label.copy().next_to(br, UP, buff=0.1)
        return VGroup(br, lab)

    def defect_brace(self, label="defect", font_size=28):
        """DEFECT brace over the small bars with a label (text or VMobject)."""
        self._brace_label = (T(label, font_size=font_size, color=DEFECT)
                             if isinstance(label, str) else label)
        self.brace = self._brace_for(self.vals)
        return self.brace

    def caption(self, tex, color=None, font_size=34, buff=0.25):
        """Distribution label under the base, e.g. r"e^{-\\beta E_k}"."""
        self._cap_size = font_size
        self.cap = M(tex, color=color or self.color, font_size=font_size)
        self.cap.next_to(self.base, DOWN, buff=buff)
        return self.cap


# =================================================================== 4. DEFECT GAUGES
BASIN_EDGE = 0.127


def defect_frac(v):
    """Gauge fill fraction: log10(defect) mapped [-3, 0] -> [0, 1] (clamped).
    FULL = large defect (impure), EMPTY = pure, everywhere in the film."""
    return float(np.clip((np.log10(max(v, 1e-12)) + 3.0) / 3.0, 0.0, 1.0))


class DefectGauge(VGroup):
    """One vertical defect gauge (motif 4).

    kind: 'p' (SPACE, "p (spatial)"), 'q' (TIME, "q (thermal)") or 'u' (DEFECT).
    bound=True switches the titles to "bound on p" / "bound on q" (ch08 s08 on).
    Parts: .frame, .fill, .basin (dashed DEFECT line at 0.127),
    .basin_label, .pct (optional dashed 1% line + label), .title, .number.
    The level is a ValueTracker holding log10(defect):
        self.play(g.set_defect(0.0479))          # fill and DecimalNumber follow
        self.play(g.recolor(GAP))                # e.g. 'turn GAP' in ch08 s11
    """
    TITLES = {"p": (r"$p$ (spatial)", r"bound on $p$"),
              "q": (r"$q$ (thermal)", r"bound on $q$"),
              "u": (r"defect $u$", r"bound on $u$")}
    COLORS = {"p": SPACE, "q": TIME, "u": DEFECT}

    def __init__(self, value, kind="p", bound=False, title=None, height=2.6, width=0.52,
                 decimals=4, basin=True, basin_label=True, one_percent=False,
                 title_size=28, number_size=30):
        super().__init__()
        self.kind = kind
        self.color = self.COLORS.get(kind, DEFECT)
        self._fill_color = ManimColor(self.color)
        self.H, self.W = height, width
        self.frame = RoundedRectangle(width=width, height=height, corner_radius=0.08,
                                      stroke_color=DIM, stroke_width=2, fill_color=BG,
                                      fill_opacity=0.6)
        self.tracker = ValueTracker(np.log10(max(value, 1e-12)))
        self.fill = Polygon(*[ORIGIN, RIGHT, UP + RIGHT, UP], stroke_width=0,
                            fill_color=self.color, fill_opacity=0.85)
        self.add(self.frame, self.fill)
        self.basin = VGroup()
        self.basin_label = VGroup()
        if basin:
            y = self._y(defect_frac(BASIN_EDGE))
            self.basin = DashedLine([-width / 2 - 0.14, y, 0], [width / 2 + 0.14, y, 0],
                                    color=DEFECT, stroke_width=3, dash_length=0.07)
            self.basin.set_stroke(BG, width=6, background=True)
            self.add(self.basin)
            if basin_label:
                self.basin_label = T("basin edge", font_size=24, color=DEFECT).next_to(
                    self.basin, RIGHT, buff=0.12)
                self.add(self.basin_label)
        self.pct = VGroup()
        if one_percent:
            y = self._y(defect_frac(0.01))
            ln = DashedLine([-width / 2 - 0.14, y, 0], [width / 2 + 0.14, y, 0],
                            color=FG, stroke_width=2, dash_length=0.05, stroke_opacity=0.7)
            lab = T(r"1\%", font_size=24, color=FG).next_to(ln, RIGHT, buff=0.12)
            self.pct = VGroup(ln, lab)
            self.add(self.pct)
        ttl = title if title is not None else self.TITLES.get(kind, ("", ""))[1 if bound else 0]
        self.title = VGroup(T(ttl, font_size=title_size, color=self.color).next_to(
            self.frame, UP, buff=0.25))
        self._title_size = title_size
        self.number = DecimalNumber(value, num_decimal_places=decimals, font_size=number_size,
                                    color=self.color)
        self.number.next_to(self.frame, DOWN, buff=0.22)
        self.add(self.title, self.number)
        self._update_fill(self.fill)
        self.fill.add_updater(self._update_fill)
        self.number.add_updater(self._update_number)

    def _y(self, frac):
        return self.frame.get_bottom()[1] + frac * self.H if hasattr(self, "frame") else \
            -self.H / 2 + frac * self.H

    def _update_fill(self, m):
        f = defect_frac(10 ** self.tracker.get_value())
        pad = 0.045
        bl = self.frame.get_corner(DL) + np.array([pad, pad, 0])
        br = self.frame.get_corner(DR) + np.array([-pad, pad, 0])
        hh = max(f * (self.frame.height - 2 * pad), 1e-4)
        m.set_points_as_corners([bl, br, br + UP * hh, bl + UP * hh, bl])
        m.set_fill(self._fill_color, opacity=0.85 if f > 0 else 0)

    def _update_number(self, m):
        anchor = self.frame.get_bottom() + DOWN * 0.22
        m.set_value(10 ** self.tracker.get_value())
        m.next_to(anchor, DOWN, buff=0)

    @property
    def value(self):
        return 10 ** self.tracker.get_value()

    def set_defect(self, v, **kw):
        """Animate the gauge to defect value v (log-linear in between)."""
        return self.tracker.animate(**kw).set_value(np.log10(max(v, 1e-12)))

    def recolor(self, color, number=True, **kw):
        c0, c1 = ManimColor(self._fill_color), ManimColor(color)
        n0 = self.number.get_color()

        def upd(m, a):
            self._fill_color = interpolate_color(c0, c1, a)
            if number:
                self.number.set_color(interpolate_color(n0, c1, a))
        return UpdateFromAlphaFunc(self, upd, **kw)

    def retitle(self, text, **kw):
        """Cross-fade the title in place (e.g. 'p (spatial)' -> 'bound on p')."""
        old = self.title[-1]
        new = T(text, font_size=self._title_size, color=self.color)
        new.move_to(old, aligned_edge=DOWN).set_opacity(0)
        self.title.add(new)
        return AnimationGroup(old.animate.set_opacity(0), new.animate.set_opacity(1), **kw)


class DefectGauges(VGroup):
    """The pair: blue p (spatial) left, orange q (thermal) right (motif 4).
    Only the right gauge carries the 'basin edge' label.  .p, .q are DefectGauge.
        self.play(gg.set_defects(p=0.06, q=0.17))
        self.play(gg.to_bounds())         # titles -> 'bound on p' / 'bound on q'
    """

    def __init__(self, p=0.3, q=0.3, bound=False, spacing=2.1, **kw):
        super().__init__()
        self.p = DefectGauge(p, "p", bound=bound, basin_label=False, **kw)
        self.q = DefectGauge(q, "q", bound=bound, basin_label=True, **kw)
        self.q.shift(RIGHT * spacing)
        self.add(self.p, self.q)
        self.center()

    def set_defects(self, p=None, q=None, **kw):
        anims = []
        if p is not None:
            anims.append(self.p.set_defect(p))
        if q is not None:
            anims.append(self.q.set_defect(q))
        return AnimationGroup(*anims, **kw)

    def to_bounds(self, **kw):
        return AnimationGroup(self.p.retitle(r"bound on $p$"), self.q.retitle(r"bound on $q$"),
                              **kw)


# =================================================================== 5. STAIRCASE
def _tick_labels(axis_vals, coords_fn, texts, color, direction, font_size=24, buff=0.18):
    g = VGroup()
    for v, s in zip(axis_vals, texts):
        g.add(M(s, color=color, font_size=font_size).next_to(coords_fn(v), direction, buff=buff))
    return g


class Staircase(VGroup):
    """The (log L, log beta) plane of the bootstrap (motif 5).

    kind='bare'     : the lb_plane content (log2 L, log2 beta, unlabelled integer ticks)
                      in the staircase axis style; use instead of visuals.lb_plane.
    kind='symbolic' : ticks n, 2n, 4n, 8n (SPACE) and beta, 2beta, 4beta (TIME)
                      (ch06 s08 on); the origin sits half a doubling below/left of (n, beta) so trominoes never lie on the axes.
    kind='real'     : true log2 scale, x ticks 32..8192, y ticks 8..2048 (ch08).
    Coordinates are always log2 units: pt(x, y); for 'real' use npt(n, beta).
    Parts: .ax, .labels (axis labels), .ticks (tick numbers, may be empty).
    """

    def __init__(self, kind="symbolic", x_length=6.0, y_length=4.0, n_max=6):
        super().__init__()
        self.kind = kind
        self.ox = self.oy = 0.0
        if kind == "bare":
            # same content as visuals.lb_plane, in the staircase's axis style
            self.ax = Axes(x_range=[0, n_max, 1], y_range=[0, n_max - 1, 1], x_length=x_length,
                           y_length=y_length, tips=True,
                           axis_config={"color": DIM, "stroke_width": 2, "include_ticks": True,
                                        "tick_size": 0.06, "tip_width": 0.18,
                                        "tip_height": 0.18})
            xl = M(r"\log_2 L", color=SPACE, font_size=32).next_to(self.ax.x_axis.get_end(),
                                                                   RIGHT, buff=0.15)
            yl = M(r"\log_2 \beta", color=TIME, font_size=32).next_to(self.ax.y_axis.get_end(),
                                                                      UP, buff=0.15)
            self.labels = VGroup(xl, yl)
            self.ticks = VGroup()
        else:
            if kind == "symbolic":
                xs, ys = [0, 1, 2, 3], [0, 1, 2]
                self.ox, self.oy = 0.45, 0.4            # (n, beta) sits inside the plane
                xmax, ymax = 3.8, 2.75
                xt = ["n", "2n", "4n", "8n"]
                yt = [r"\beta", r"2\beta", r"4\beta"]
            else:
                xs, ys = list(range(5, 14)), list(range(3, 12))
                self.ox, self.oy = -4.55, -2.55
                xmax, ymax = 8.8, 8.8
                xt = [str(2 ** k) for k in xs]
                yt = [str(2 ** k) for k in ys]
            self.ax = Axes(x_range=[0, xmax, 1], y_range=[0, ymax, 1], x_length=x_length,
                           y_length=y_length, tips=True,
                           axis_config={"color": DIM, "stroke_width": 2, "include_ticks": False,
                                        "tip_width": 0.18, "tip_height": 0.18})
            marks = VGroup(*[Line(self.pt(v, -self.oy) + DOWN * 0.06,
                                  self.pt(v, -self.oy) + UP * 0.06, color=DIM, stroke_width=2)
                             for v in xs],
                           *[Line(self.pt(-self.ox, v) + LEFT * 0.06,
                                  self.pt(-self.ox, v) + RIGHT * 0.06, color=DIM, stroke_width=2)
                             for v in ys])
            self.ax.add(marks)
            fs = 28 if kind == "symbolic" else 24
            tx = _tick_labels(xs, lambda v: self.pt(v, -self.oy), xt, SPACE, DOWN, font_size=fs)
            ty = _tick_labels(ys, lambda v: self.pt(-self.ox, v), yt, TIME, LEFT, font_size=fs)
            self.ticks = VGroup(tx, ty)
            xl = M("L", color=SPACE, font_size=32).next_to(self.ax.x_axis.get_end(), RIGHT,
                                                           buff=0.15)
            yl = M(r"\beta", color=TIME, font_size=32).next_to(self.ax.y_axis.get_end(), UP,
                                                               buff=0.15)
            self.labels = VGroup(xl, yl)
        self.add(self.ax, self.ticks, self.labels)

    def pt(self, x, y):
        """Screen point of log2 coordinates (x, y).  symbolic: (0, 0) = (n, beta);
        real: x = log2 L, y = log2 beta; bare: lb_plane coordinates."""
        return self.ax.c2p(x + self.ox, y + self.oy)

    def npt(self, n, beta):
        """Point of (L = n, beta) (real kind; log2 taken here)."""
        return self.pt(np.log2(n), np.log2(beta))

    @property
    def unit(self):
        """Screen vector of one doubling in each direction: (+1, +1)."""
        return self.pt(1, 1) - self.pt(0, 0)

    def tromino(self, x0=0.0, y0=0.0, style="main"):
        return Tromino(self, x0, y0, style=style)

    def tromino_at(self, n, beta, style="main"):
        """Tromino with S at (n, beta) -> (2n, beta) (log2 coordinates)."""
        return Tromino(self, np.log2(n), np.log2(beta), style=style)

    def fig1(self, x0=0.0, y0=0.0, k=3, label="interpolate"):
        """The paper's Fig. 1: dots at (x0+j, y0+j), dashed diagonal arrows, thick
        bars from length n_j to 2 n_j at height beta_j, one 'interpolate' label."""
        dots = VGroup(*[Dot(self.pt(x0 + j, y0 + j), radius=0.07, color=FG) for j in range(k)])
        arrows = VGroup(*[DashedLine(self.pt(x0 + j, y0 + j), self.pt(x0 + j + 1, y0 + j + 1),
                                     color=DIM, stroke_width=2.5, dash_length=0.09,
                                     buff=0.12).add_tip(tip_length=0.16, tip_width=0.14)
                          for j in range(k - 1)])
        bars = VGroup(*[Line(self.pt(x0 + j, y0 + j), self.pt(x0 + j + 1, y0 + j),
                             color=FG, stroke_width=9, stroke_opacity=0.75)
                        for j in range(k)])
        lab = T(label, font_size=26, color=DIM).next_to(bars[0], DOWN, buff=0.15)
        return VGroup(bars, arrows, dots, lab)


def _slide_solidify(dashed, solid, shift):
    """Dashed segment slides by `shift`; the solid one fades in on arrival while the
    dashed one fades out (it stays in the scene, invisible)."""
    solid.set_opacity(0)
    state = {}

    def upd_d(m, a):
        if "s" not in state:
            state["s"] = m.copy()
        m.become(state["s"]).shift(shift * smooth(min(1.0, a / 0.75)))
        m.set_opacity(1 - smooth(float(np.clip((a - 0.6) / 0.4, 0, 1))))

    def upd_s(m, a):
        m.set_opacity(smooth(float(np.clip((a - 0.6) / 0.4, 0, 1))))
    return [UpdateFromAlphaFunc(dashed, upd_d), UpdateFromAlphaFunc(solid, upd_s)]


class Tromino(VGroup):
    """The tracked pair (motif 5): an L-shaped tromino.

    .S : SPACE segment (x0, y0) -> (x0+1, y0)     = S(n, beta)
    .T : TIME  segment (x0+1, y0) -> (x0+1, y0+1)  = T(2n, beta)
    .dots : FG dots at the three corners.
    style='main' (default) or 'alt' (DIM-outlined DEFECT, the 60-site seed).
    """
    W = 7

    def __init__(self, stair, x0, y0, style="main", parts=None):
        super().__init__()
        self.stair, self.x0, self.y0, self.style = stair, float(x0), float(y0), style
        if parts is None:
            S, T_, dots = self._make(self.x0, self.y0)
        else:
            S, T_, dots = parts
        self.S, self.T, self.dots = S, T_, dots
        self.add(self.S, self.T, self.dots)

    def _seg(self, a, b, color, dashed=False):
        p = self.stair.pt
        if dashed:
            ln = DashedLine(p(*a), p(*b), color=color, stroke_width=self.W, dash_length=0.1)
        else:
            ln = Line(p(*a), p(*b), color=color, stroke_width=self.W)
        if self.style == "alt":
            ln.set_color(DEFECT).set_stroke(width=5)
            ln.set_stroke(DIM, width=10, background=True)
        return ln

    def _make(self, x0, y0):
        p = self.stair.pt
        S = self._seg((x0, y0), (x0 + 1, y0), SPACE)
        T_ = self._seg((x0 + 1, y0), (x0 + 1, y0 + 1), TIME)
        dots = VGroup(*[Dot(p(*c), radius=0.06, color=FG)
                        for c in ((x0, y0), (x0 + 1, y0), (x0 + 1, y0 + 1))])
        return S, T_, dots

    # labels ------------------------------------------------------------
    def label_S(self, tex, direction=DOWN, font_size=30, buff=0.15):
        return M(tex, color=SPACE, font_size=font_size).next_to(self.S, direction, buff=buff)

    def label_T(self, tex, direction=RIGHT, font_size=30, buff=0.15):
        return M(tex, color=TIME, font_size=font_size).next_to(self.T, direction, buff=buff)

    # motions -----------------------------------------------------------
    def step(self, *riders, **kw):
        """One full update: translate by (+1, +1).  `riders` (labels...) move along."""
        v = self.stair.unit
        self.x0 += 1
        self.y0 += 1
        return AnimationGroup(*[ApplyMethod(m.shift, v) for m in (self, *riders)], **kw)

    def climb(self, n=4, exit=False, trail=False, **kw):
        """n steps up the diagonal; exit=True fades it out on the last step
        (ch01 s08, ch10 s10: '...and exits the top-right').  trail=True leaves
        ghost copies behind."""
        anims = []
        v = self.stair.unit
        for i in range(n):
            last = exit and i == n - 1
            parts = []
            if trail:
                parts.append(FadeIn(self.copy().shift(v * i).set_opacity(0.2), run_time=0.01))
            if last:
                parts.append(FadeOut(self, shift=v))
            else:
                parts.append(ApplyMethod(self.shift, v))
            self.x0 += 1
            self.y0 += 1
            anims.append(Succession(*parts) if len(parts) > 1 else parts[0])
        return Succession(*anims, **kw)

    def ghost(self, opacity=0.22, **kw):
        """Fade to a ghost in place (ch06 s10)."""
        return self.animate(**kw).set_opacity(opacity)

    def ghost_copy(self, opacity=0.22):
        return self.copy().set_opacity(opacity)

    def diag_arrow(self, color=DIM):
        """Dashed arrow from the start corner (x0, y0) to (x0+1, y0+1)."""
        p = self.stair.pt
        return DashedLine(p(self.x0, self.y0), p(self.x0 + 1, self.y0 + 1), color=color,
                          stroke_width=3, dash_length=0.09, buff=0.1).add_tip(
            tip_length=0.18, tip_width=0.16)

    def pulse(self, color=DEFECT, **kw):
        return Indicate(self, color=color, scale_factor=1.06, **kw)

    def leapfrog(self, labels=(None, None, None, None), label_size=30):
        """The four-step update of ch06 s09.  Returns a Leapfrog with
          .steps  [a1, a2, a3, a4] animations (play one per sentence)
          .new    the new Tromino at (x0+1, y0+1) (its S and T are the moved pieces)
          .labels the label mobjects created (None where no tex was given)
        1. dashed copy of S lifts to height y0+1; T flashes (it pays);
        2. it slides to (x0+1 .. x0+2, y0+1) and turns solid (square in space);
        3. a dashed copy of T jumps right to x0+2; the new S flashes (it pays);
        4. it squares upward to (x0+2, y0+1 .. y0+2), solid; corner dots appear.
        The original tromino stays put (ghost it afterwards with .ghost())."""
        x0, y0 = self.x0, self.y0
        p = self.stair.pt
        up = p(0, 1) - p(0, 0)
        right = p(1, 0) - p(0, 0)
        S_lift = self._seg((x0, y0 + 1), (x0 + 1, y0 + 1), SPACE, dashed=True)
        S_new = self._seg((x0 + 1, y0 + 1), (x0 + 2, y0 + 1), SPACE)
        T_jump = self._seg((x0 + 2, y0), (x0 + 2, y0 + 1), TIME, dashed=True)
        T_new = self._seg((x0 + 2, y0 + 1), (x0 + 2, y0 + 2), TIME)
        dots = VGroup(*[Dot(p(*c), radius=0.06, color=FG)
                        for c in ((x0 + 1, y0 + 1), (x0 + 2, y0 + 1), (x0 + 2, y0 + 2))])
        labs = [None] * 4
        if labels[0]:
            labs[0] = M(labels[0], color=SPACE, font_size=label_size).next_to(S_lift, UP, 0.15)
        if labels[1]:
            labs[1] = M(labels[1], color=SPACE, font_size=label_size).next_to(S_new, UP, 0.15)
        if labels[2]:
            labs[2] = M(labels[2], color=TIME, font_size=label_size).next_to(T_jump, RIGHT, 0.15)
        if labels[3]:
            labs[3] = M(labels[3], color=TIME, font_size=label_size).next_to(T_new, RIGHT, 0.15)

        def with_lab(anims, i, prev=None):
            out = list(anims)
            if labs[i] is not None:
                out.append(FadeIn(labs[i], shift=0.1 * UP))
            if prev is not None and labs[prev] is not None:
                out.append(FadeOut(labs[prev]))
            return out

        a1 = AnimationGroup(*with_lab([FadeIn(S_lift, shift=up * 0.999),
                                       Indicate(self.T, color=TIME, scale_factor=1.12)], 0))
        a2 = AnimationGroup(*with_lab(_slide_solidify(S_lift, S_new, right), 1, prev=0))
        a3 = AnimationGroup(*with_lab([FadeIn(T_jump, shift=right * 0.999),
                                       Indicate(S_new, color=SPACE, scale_factor=1.12)], 2))
        a4 = AnimationGroup(*with_lab(_slide_solidify(T_jump, T_new, up) +
                                      [FadeIn(dots, rate_func=squish_rate_func(smooth, 0.6, 1))],
                                      3, prev=2))
        new = Tromino(self.stair, x0 + 1, y0 + 1, style=self.style, parts=(S_new, T_new, dots))

        class Leapfrog:
            pass
        lf = Leapfrog()
        lf.steps, lf.new, lf.labels = [a1, a2, a3, a4], new, labs
        return lf


# =================================================================== icons (recap cards)
def icon_torus(w=1.6, h=1.0):
    """Two-knives torus icon (ch07 s05, ch10 s04, ch10 s08)."""
    r = Rectangle(width=w, height=h, stroke_color=FG, stroke_width=2, fill_color=FG,
                  fill_opacity=0.03)
    hk = Line(r.get_left() + UP * 0.12 * h, r.get_right() + UP * 0.12 * h, color=TIME,
              stroke_width=4)
    vk = Line(r.get_top() + RIGHT * 0.22 * w, r.get_bottom() + RIGHT * 0.22 * w, color=SPACE,
              stroke_width=4)
    return VGroup(r, hk, vk)


def icon_squared_bars(w=1.9, h=0.9):
    """Bars before -> after squaring (renormalised)."""
    p = np.array([0.5, 0.22, 0.16, 0.12])
    q = p ** 2 / (p ** 2).sum()
    a = weight_bars(p, width=0.75, height=h, color=FG, highlight=0, highlight_color=FG,
                    bar_buff=0.05)
    b = weight_bars(q, width=0.75, height=h, color=FG, highlight=0, highlight_color=FG,
                    bar_buff=0.05)
    arr = Arrow(LEFT * 0.2, RIGHT * 0.2, buff=0, color=DIM, stroke_width=3,
                max_tip_length_to_length_ratio=0.4)
    return VGroup(a, arr, b).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)


def icon_tiling(w=1.4, h=1.0):
    """2x2 tiling (the four-tori identity)."""
    r = Rectangle(width=w, height=h, stroke_color=FG, stroke_width=2)
    v = DashedLine(r.get_top(), r.get_bottom(), color=SPACE, stroke_width=2.5, dash_length=0.07)
    hz = DashedLine(r.get_left(), r.get_right(), color=TIME, stroke_width=2.5, dash_length=0.07)
    return VGroup(r, v, hz)


def icon_staircase(steps=3, u=0.42):
    """Three trominoes up a diagonal."""
    g = VGroup()
    for j in range(steps):
        o = np.array([j * u, j * u, 0])
        g.add(Line(o, o + RIGHT * u, color=SPACE, stroke_width=4).set_opacity(0.35 + 0.65 * (j == steps - 1)))
        g.add(Line(o + RIGHT * u, o + RIGHT * u + UP * u, color=TIME, stroke_width=4)
              .set_opacity(0.35 + 0.65 * (j == steps - 1)))
    return g.center()
