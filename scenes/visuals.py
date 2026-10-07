"""Reusable visual vocabulary shared by all chapters.

Keep chapters consistent: the same object should look the same everywhere
(spins, level diagrams, the L x beta torus, weight bars, bond histories).
"""
import numpy as np

from common import *  # noqa: F401,F403


# ------------------------------------------------------------------ spins
def spin_arrow(direction=UP, length=0.7, color=FG, stroke=5):
    d = np.array(direction, dtype=float)
    d = d / np.linalg.norm(d)
    return Arrow(-d * length / 2, d * length / 2, buff=0, color=color,
                 stroke_width=stroke, max_tip_length_to_length_ratio=0.3)


def spin_chain(n, spacing=0.8, staggered=True, color=FG, length=0.7, tilt=0.0):
    """Open chain of n spins on a line; staggered = Neel-like up/down."""
    g = VGroup()
    for j in range(n):
        ang = tilt * (1 if j % 2 == 0 else -1)
        d = rotate_vector(UP, ang) * ((-1) ** j if staggered else 1)
        a = spin_arrow(d, length, color)
        a.move_to(RIGHT * spacing * (j - (n - 1) / 2))
        g.add(a)
    return g


def spin_ring(n, radius=2.0, staggered=True, color=FG, length=0.55):
    """Spins on a periodic ring, arrows radial-ish (up/down out of plane drawn as in/out)."""
    sites = VGroup()
    arrows = VGroup()
    for j in range(n):
        ang = TAU * j / n + PI / 2
        p = radius * np.array([np.cos(ang), np.sin(ang), 0])
        sites.add(Dot(p, radius=0.05, color=DIM))
        s = (-1) ** j if staggered else 1
        arrows.add(spin_arrow(UP * s, length, color).move_to(p))
    circ = Circle(radius=radius, color=FAINT, stroke_width=2)
    return VGroup(circ, sites, arrows)


# ------------------------------------------------------------------ spectra
def level_diagram(levels, width=1.6, color=FG, ymin=0.0, yscale=1.0, stroke=3,
                  ground_color=None):
    """Horizontal ticks at energies `levels` (already shifted so ground = 0)."""
    g = VGroup()
    for i, e in enumerate(levels):
        c = ground_color if (i == 0 and ground_color) else color
        g.add(Line(LEFT * width / 2, RIGHT * width / 2, color=c, stroke_width=stroke)
              .shift(UP * (e - ymin) * yscale))
    return g


def gap_brace(lower, upper, label=r"\Delta", color=GAP, side=RIGHT):
    """Double arrow between two level lines with a label."""
    x = (lower.get_right() if side is RIGHT else lower.get_left())[0] + 0.25 * side[0]
    a = DoubleArrow([x, lower.get_y(), 0], [x, upper.get_y(), 0], buff=0, color=color,
                    stroke_width=3, tip_length=0.15)
    t = M(label, color=color, font_size=34).next_to(a, side, buff=0.1)
    return VGroup(a, t)


# ------------------------------------------------------------------ torus
def torus_rect(width=5.0, height=3.0, nx=0, ny=0, label_L=True, label_beta=True):
    """The L x beta Euclidean torus drawn as a rectangle with periodic edges.

    Space runs horizontally (SPACE color), imaginary time vertically (TIME color).
    Opposite edges carry matching tick marks to indicate identification.
    """
    r = Rectangle(width=width, height=height, stroke_color=FG, stroke_width=2,
                  fill_color=FG, fill_opacity=0.03)
    g = VGroup(r)
    grid = VGroup()
    for i in range(1, nx):
        x = -width / 2 + width * i / nx
        grid.add(Line([x, -height / 2, 0], [x, height / 2, 0], color=FAINT, stroke_width=1))
    for i in range(1, ny):
        y = -height / 2 + height * i / ny
        grid.add(Line([-width / 2, y, 0], [width / 2, y, 0], color=FAINT, stroke_width=1))
    g.add(grid)
    # identification marks: top/bottom edges are glued (time periodic -> TIME),
    # left/right edges are glued (space periodic -> SPACE)
    for y in (-height / 2, height / 2):
        g.add(M(r">", color=TIME, font_size=28).move_to([0, y, 0]))
    for x in (-width / 2, width / 2):
        g.add(M(r"\gg", color=SPACE, font_size=28).rotate(PI / 2).move_to([x, 0, 0]))
    if label_L:
        g.add(M("L", color=SPACE, font_size=36).next_to(r, DOWN, buff=0.2))
    if label_beta:
        g.add(M(r"\beta", color=TIME, font_size=36).next_to(r, LEFT, buff=0.2))
    return g


# ------------------------------------------------------------------ weights
def weight_bars(weights, width=5.0, height=2.6, color=FG, highlight=0,
                highlight_color=DEFECT, bar_buff=0.12):
    """Bar chart of a probability distribution (normalized to sum 1).

    The tallest admissible bar height is `height` (prob 1).
    """
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    n = len(w)
    bw = (width - bar_buff * (n - 1)) / n
    bars = VGroup()
    for i, p in enumerate(w):
        b = Rectangle(width=bw, height=max(p * height, 1e-3), stroke_width=0,
                      fill_color=highlight_color if i == highlight else color,
                      fill_opacity=0.9)
        b.move_to([-width / 2 + bw / 2 + i * (bw + bar_buff), 0, 0], aligned_edge=DOWN)
        bars.add(b)
    base = Line([-width / 2 - 0.1, 0, 0], [width / 2 + 0.1, 0, 0], color=DIM, stroke_width=2)
    return VGroup(base, bars)


def purity(weights):
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    return float((w ** 2).sum())


def squared(weights):
    w = np.asarray(weights, dtype=float) ** 2
    return w / w.sum()


# ------------------------------------------------------------------ bond histories
def bond_history_diagram(n_sites=6, beta=3.0, spacing=1.0, events=None, seed=3,
                         rate=2.0):
    """Sites as vertical world lines (time up); events as short horizontal bars
    on bonds at random imaginary times, colored by label x/y/z.

    Returns VGroup(sites, events) with events[k] the VGroup of bond k (bond k joins
    site k and k+1; the last bond wraps around when drawn as a ring elsewhere).
    """
    rng = np.random.default_rng(seed)
    cols = [SX, SY, SZ]
    sites = VGroup(*[Line([spacing * (j - (n_sites - 1) / 2), 0, 0],
                          [spacing * (j - (n_sites - 1) / 2), beta, 0],
                          color=DIM, stroke_width=2) for j in range(n_sites)])
    ev = VGroup()
    for k in range(n_sites - 1):
        x0 = spacing * (k - (n_sites - 1) / 2)
        g = VGroup()
        times = events[k] if events else sorted(rng.uniform(0, beta, rng.poisson(rate * beta)))
        for t in times:
            lab = rng.integers(3)
            g.add(Line([x0, t, 0], [x0 + spacing, t, 0], color=cols[lab], stroke_width=5))
        ev.add(g)
    out = VGroup(sites, ev)
    out.move_to(ORIGIN)
    return out


# ------------------------------------------------------------------ (L, beta) plane
def lb_plane(n_max=6, x_len=8.0, y_len=4.5):
    """Log2 axes for the (length, inverse temperature) plane used in the bootstrap."""
    ax = Axes(x_range=[0, n_max, 1], y_range=[0, n_max - 1, 1], x_length=x_len,
              y_length=y_len, tips=True,
              axis_config={"color": DIM, "stroke_width": 2, "include_ticks": True})
    xl = M(r"\log_2 L", color=SPACE, font_size=32).next_to(ax.x_axis, RIGHT, buff=0.15)
    yl = M(r"\log_2 \beta", color=TIME, font_size=32).next_to(ax.y_axis, UP, buff=0.15)
    return VGroup(ax, xl, yl)
