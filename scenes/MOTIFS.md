# Recurring motifs: `scenes/motifs.py`

```python
from motifs import *     # brings visuals.* and common.* too
```

Build every callback of a recurring motif with these helpers, so it looks the same in every
chapter. Do not rebuild a motif by hand from `visuals.py`. In particular, use `Torus` and
not `torus_rect`, and use `Staircase("bare")` and not `lb_plane`.

These helpers are exercised by `scenes/motif_gallery.py`,
which renders every motif and every motion listed here. It doubles as a set of working
examples.

## General rules

- Methods that return animations do not play them. Play each one right after you create it,
  in the order you created them. Some of them update bookkeeping when called (a tromino's
  position, a thumbnail's multipliers, a knife's fraction).
- Size `run_time` as a fraction of `d`, for example `self.play(x, run_time=0.4 * d)`.
- Pitfalls in CE 0.20:
  - A `FadeOut(x)` nested inside a `Succession` or `AnimationGroup` does not remove `x`. The
    group stays in the scene and `x` comes back. Play `FadeOut` at top level, or use the
    helpers here, which already work around this.
  - `.animate` targets are fixed when you create them. To queue several moves of one object,
    use `ApplyMethod(m.shift, v)`. The motif methods already do this.
  - To dim a motif, use `.fade(0.7)`, never `.set_opacity(0.3)`. Several motifs keep
    invisible parts: off-range plot points and cross-faded ticks after a zoom, thumbnail
    seams, a knife's glow, retitled gauge titles. `set_opacity` would bring them back;
    `fade` scales each part's own opacity.
- Shared glyphs:
  - `check_mark()`, `cross_mark()` (`SX` red), `open_circle()`, `check_badge()`.
  - `pulse(mob, color=DEFECT)` is the "pulse DEFECT" emphasis.
  - `pay_coin("T" | "S")` gives the coins of ch06 s08 and ch10 s09.
  - Recap icons: `icon_torus()`, `icon_squared_bars()`, `icon_tiling()`, `icon_staircase()`.
    Used in ch07 s05 and ch10 s04/s05/s08.
  - Data markers (colour-clash rule): `spin1_marker(pt)` is a hollow `INTEGER` square;
    `spinhalf_marker(pt)` is a filled `HALF` dot. Use them in every plot that has spin series.

---

## 1. GAPPLOT

Segments: ch01 s02–s05, ch10 s10.

The plot is an `Axes` with x = 1/L in [0, 0.27] and y in [0, 1.05], 8 × 4.6, centred at
(0, −0.4). Data come from `data/gaps.csv`:
- spin ½: `HALF` dots, L = 4..24.
- spin 1: hollow `INTEGER` squares, L = 4..16.
- Each series has a thin polyline.

```python
plot = GapPlot()                        # same object in ch01 and ch10
ctr = plot.counter()                    # "L = 4" counter, top right of the axes
self.play(plot.build_axes(), run_time=0.3 * d)          # axes only (s02)
self.add(ctr)
self.play(plot.build_data(counter=ctr, run_time=0.6 * d))  # L order, spins alternating, lag 0.15
self.play(FadeIn(plot.series_labels()))                 # "spin 1" / "spin 1/2" direct labels
hg = plot.half_guide()                  # dashed HALF y = 4.385x to the origin + "→0"   (s03)
self.play(Create(hg[0]), FadeIn(hg[1]))
lit = plot.literature_line()            # dashed INTEGER 0.4105 for x ≤ 1/16, DIM 2-line label + leader
self.play(Create(lit[0]), Create(lit[1]), FadeIn(lit[2]))
plot, anim = plot.zoomed(0.07, 0.01)    # s04: re-range x to [0, 0.07]; extras follow; returns NEW plot
self.play(anim, run_time=0.25 * d)
wi = plot.what_if_curves()              # 3 DIM dashed continuations from (1/16, 0.443)
self.play(LaggedStart(*map(Create, wi), lag_ratio=0.3))
self.play(plot.with_extras().animate.scale(0.55).to_edge(LEFT).fade(0.7))  # s05 (opacity 0.3)
# ch10 s10:
plot = GapPlot(); fl = plot.floor_lines()   # GAP floor at true height: 4.79e-4 (1/L ≤ 1/60), 3.82e-3 step
```

- `plot.c2p(x, y)` maps data to screen.
- `.half_pts` and `.one_pts` are in L order.
- `.extras` holds the overlays you have created.
- `hide_data()` hides the points if you want to `add` the plot before `build_data`.
- `zoomed()` cross-fades the ticks. Points past `x_max` fly out to the right as they fade.
  After it, use the returned plot.

## 2. TORUS + TWO KNIVES

Segments: ch01 s08, ch02 s07, ch04 s01–s12, ch05 s01–s03 (thumbnail), ch06 s01–s02 and s06,
ch07 s05–s07, ch08 s01 and s03, ch09 s03, ch10 s04 and s08–s09.

Colours are fixed:
- L runs along the bottom in `SPACE`; β runs up the left in `TIME`.
- The top and bottom chevrons are `TIME` (time is periodic). The left and right chevrons are
  `SPACE` (space is periodic).
- `torus_rect` already draws them this way. The storyboard's recolour step is a no-op.

```python
tor = Torus(5, 3, nx=10, ny=6)          # parts: rect, grid, chev_time, chev_space, L_label, beta_label
pl = tor.periodicity_labels()           # "time is periodic: trace" (above), "space is periodic: ring" (right)
self.play(FadeIn(pl), tor.pulse_chevrons())
hk = time_knife(tor, at=0.58)           # TIME line, stroke 6, triangle handle at the left
self.play(hk.cut_in()); self.play(hk.glow_on())          # "the cut glows"
self.play(hk.steps([0.25, 0.42, 0.58, 0.75, 0.92], label_tex=r"e^{-\delta\tau H}", run_time=0.5 * d))
vk = space_knife(tor, bond=1)           # SPACE line cutting THROUGH bond 1 (x = −1.75 when centred)
self.play(vk.cut_in(), vk.glow_on())
cut = vk.cut_copy()                     # the cut slice, to lift out ("a bond's history")
self.play(vk.steps(list(range(2, 12)), label_tex="X", run_time=0.6 * d))  # wraps past the right edge
self.play(hk.sweep())                   # continuous sweep (up / right); also move_to_frac(f), to_bond(k)
self.play(Transform(tor, tor.resized(height=0.05)))      # ch04 s07 (anchor DL by default)
tiles = tor.tiling_overlays()           # [whole +1, tall halves −2 (SPACE cut), wide halves −2 (TIME cut), quarters +4]
```

Knife details:
- Avoid `at=0.5` for the time knife. At exactly mid-height the blade crosses the `SPACE`
  chevron; use 0.42 or 0.58.
- Integers passed to `steps()` are bond indices; floats are fractions.
- Step labels are transient: each one fades in and out during its own jump.

Thumbnail (ch05 on). It sits top-left. Its width or height visibly doubles, seams mark the
copies, and then it re-fits its box. The labels read L, 2L, 4L… and β, 2β, 8β.

```python
thumb = TorusThumb()                    # same part order as Torus
self.play(ReplacementTransform(tor, thumb))   # ch05 s01: the big torus becomes the thumbnail
self.play(thumb.double_beta())          # ch05 s02 / ch06 s01 (×3)
self.play(thumb.double_L())             # ch05 s03 / ch06 s02
self.play(thumb.reset())
```

## 3. WEIGHT BARS (squaring always in two steps)

Segments: ch01 s08, ch04 s02 and s11, ch05 s01–s03 and s05–s06, ch07 s05, ch10 s09.

```python
wb = WeightBars([0.6, 0.15, 0.1, 0.08, 0.07], color=TIME, highlight_color=TIME)  # tallest bar FIRST
cap = wb.caption(r"e^{-\beta E_k}")     # separate mobject under the base
br = wb.defect_brace("defect")          # DEFECT brace over the small bars (or a MathTex, e.g. M("u", color=DEFECT))
self.play(FadeIn(wb), FadeIn(cap), FadeIn(br))
s1, s2 = wb.square(relabel=r"e^{-2\beta E_k}")   # s1: heights → p²; s2: renormalise to sum 1
self.play(s1, run_time=0.25 * d); self.play(s2, run_time=0.25 * d)  # the brace follows both steps
half = wb.level_line(0.5, label=r"\tfrac12")     # ch05 s06 dashed line at probability 1/2
sb = WeightBars(lam**5, color=SPACE, signed=True, value_scale=2.0)  # ch04 s11: negative bars hang down
self.play(sb.morph_to(lam**6))
```

- `wb.probs`, `wb.purity()` and `wb.defect()` drive `DecimalNumber` readouts (ch05 s05).
- `wb.y_of(p)` gives the screen y of probability p.
- Colours: `TIME` for Gibbs bars, `SPACE` for spatial bars, `FG` for neutral bars.

## 4. DEFECT GAUGES

Segments: ch05 s01, ch06 s01–s04 and s07, ch07 s06–s07, ch08 s08–s11.

Fill = log10(defect) mapped from [−3, 0] to [0, 1], so a FULL gauge means a large defect,
everywhere in the film. Never fill a gauge with purity.

Each gauge has:
- a dashed `DEFECT` "basin edge" line at 0.127;
- an optional 1% line;
- a live `DecimalNumber` underneath.

```python
u = DefectGauge(0.479, kind="u", decimals=3)       # single gauge, ch05 s01 (DEFECT fill)
gg = DefectGauges(p=0.3, q=0.3)                    # blue "p (spatial)" left, orange "q (thermal)" right
self.play(gg.set_defects(q=0.09)); self.play(gg.set_defects(q=0.0081))   # log-linear motion
self.play(pulse(gg.q.fill))                        # "orange gauge RISES (pulse DEFECT)"
gg = DefectGauges(p=0.0479, q=0.1815, bound=True, one_percent=True)   # ch08 s08+: "bound on p / q"
self.play(gg.to_bounds())                          # or switch titles later (cross-fade)
self.play(gg.set_defects(p=0.0084513, q=0.0054986), run_time=0.4 * d)
self.play(gg.p.recolor(GAP), gg.q.recolor(GAP))    # ch08 s11 "turn GAP"
```

- `g.tracker` is a `ValueTracker` holding log10(defect). Drive it from your own updater, for
  example the sliding marker of ch06 s03.
- Default `decimals=4` (0.0479, 0.1815). Use `decimals=3` for 0.479.

## 5. STAIRCASE

Segments: ch01 s08, ch05 s08, ch06 s01 and s08–s12, ch07 s02, ch08 s01 and s08–s12,
ch10 s04–s05 and s10.

There are three kinds of plane. All coordinates are log2 units (+1 means one doubling).

- `Staircase("bare")`: unlabelled log2 L / log2 β axes, the lb_plane content in the
  staircase style.
- `Staircase("symbolic")`: ticks n, 2n, 4n, 8n and β, 2β, 4β. `pt(0, 0)` is (n, β), set half
  a doubling inside the plane so trominoes never lie on the axes.
- `Staircase("real")`: true scale. Ticks run 32…8192 and 8…2048. `npt(36, 12.25)` gives
  the point.

```python
st = Staircase("symbolic").to_edge(LEFT)
tr = st.tromino(0, 0)                    # SPACE S (n,β)→(2n,β), TIME T (2n,β)→(2n,2β), FG corner dots
lS, lT = tr.label_S(r"S\!:\,p"), tr.label_T(r"T\!:\,q")
lf = tr.leapfrog(labels=[r"\approx2p+q", r"p_+=f\big(1-(1-p)^2(1-q)\big)", None,
                         r"q_+=f\big(1-(1-q)^2(1-p_+)\big)"])
for a in lf.steps: self.play(a, run_time=0.22 * d)       # ch06 s09, one step per sentence
self.play(tr.ghost(), Create(tr.diag_arrow()))           # ch06 s10; lf.new is the new tromino
ghosts = [lf.new.ghost_copy().shift(st.unit * k) for k in (1, 2)]
self.play(lf.new.step(lS2, lT2))                         # one full update (+1, +1); riders move along
real = Staircase("real", x_length=6.4, y_length=4.8)
seed = real.tromino_at(36, 12.25); self.play(seed.pulse())             # ch08 s01 (pulses DEFECT)
seed60 = real.tromino_at(60, 26.25, style="alt")         # ch08 s12 DIM-outlined DEFECT
self.play(seed.climb(6, run_time=...))                   # ch08 s10–s11
self.play(t.climb(4, exit=True, trail=True))             # ch01 s08 / ch10 s10: climbs and exits top-right
fig = st.fig1(0, 0, k=3)                                 # ch07 s02: dots, dashed arrows, "interpolate" bars
```

The storyboard's long update formulas are wide. If a label passes the frame, place it with
`label_S(..., direction=UP)` or move it to a side panel.

## 6. OBJECTION BUBBLES

The six bubbles, by key (letters `"a"`..`"f"` also work):

| key | bubble | segments |
|---|---|---|
| `"finite"` (a) | every finite chain has a gap | ch01 s04, ch03 s08, ch05 s07 |
| `"theta"` (b) | doesn't the θ-term already explain it? | ch02 s06, ch10 s05 |
| `"even"` (c) | why even L? | ch04 s09 → s11 |
| `"beta"` (d) | why not just double β? | ch05 s07 → ch06 s01 |
| `"numerics"` (e) | isn't this just numerics? | ch08 s02, ch10 s06 |
| `"half"` (f) | why doesn't it prove spin ½ gapped? | ch07 s05 → s08 |

All six appear together in ch01 s06.

```python
b = objection_bubble("finite")          # placed in the top-right slot (corner=UL also works)
self.play(bubble_in(b))                 # grows out of its tail
self.play(bubble_indicate(b))           # outline brightens, bubble swells (fill never floods)
self.play(bubble_check(b))              # GAP check badge on its corner
self.play(bubble_answer(b, "the question is uniformity"))   # GAP reply under it
self.play(bubble_out(b))                # fades bubble + badge + answer
col = objection_column()                # ch01 s06: all six down the right margin
self.play(objection_column_in(col)); self.wait(1.5)
self.play(objection_collapse(col))      # small stack top-right, then gone
```

Bubbles keep full size (font 26) in the corner slot. The storyboard's "scale 0.6" would put
the text below the 24-pt minimum.

## 7. TAGS

These are DIM italic tags in a thin rounded box. A tag stays on screen for the whole segment.

```python
t = tag(TAG_READING)                    # top-right; tag(TAG_HEURISTIC, corner=UL)
self.play(tag_in(t)) ... self.play(tag_out(t))
inline_tag(TAG_SCHEMATIC, numberline, RIGHT)            # same glyph beside an object
literature_label(num_mob)               # small DIM "literature" next to a literature number
```

Standard texts:
- `TAG_READING`: "physicist's reading – not in the paper". Used in ch04 s12, ch07 s06–s07,
  ch08 s13.
- `TAG_READING_NEITHER`: used in ch09 s06.
- `TAG_OURS`: used in ch07 s08.
- `TAG_HEURISTIC`: used in ch06 s02 and ch10 s03.
- `TAG_ANALOGY`.
- `TAG_SCHEMATIC`: used in ch04 s02/s03/s09/s11 and ch02 s05.
- Free text works too, e.g. `tag("in the spirit of Suzuki's quantum transfer matrix")`.

Tags and objection bubbles share the top-right corner. If both are on screen together, put
the tag at UL.

## 8. STATUS CARD

Segments: ch01 s07, reprised in ch10 s06. Plain text only: no logos, no screenshots.

```python
card = StatusCard()                     # .titles, .title_tags, .meta, .lines (3 × (icon, text))
self.play(card.anim_titles(), run_time=0.25 * d)
self.play(card.anim_tag(0)); self.play(card.anim_tag(1))     # "even rings", "odd open chains, end fields"
self.play(card.anim_meta())             # author: OpenAI · manuscripts dated 24 Sep 2026 · released 6 Oct 2026
for i in range(3): self.play(card.anim_line(i), run_time=0.12 * d)
```

The three status lines are:
1. DIM circle: claimed proof · preprint · not yet independently refereed
2. GAP check: analytic argument: short, checkable by hand
3. GAP check: finite computations: published with the paper, re-runnable on a laptop
