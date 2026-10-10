# Final synthesized script: generates narration.json and storyboard.md for the
# Haldane-gap explainer. Each segment carries (text, visual, note[, say]).
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "script"

CH = []


def chapter(cid, title, purpose):
    CH.append({"id": cid, "title": title, "purpose": purpose, "segments": []})


def seg(text, visual, note="", say=None, pause=None):
    c = CH[-1]
    sid = "s%02d" % (len(c["segments"]) + 1)
    d = {"id": sid, "text": " ".join(text.split()), "visual": visual.strip("\n"),
         "note": " ".join(note.split()), "pause": pause}
    if say:
        d["say"] = " ".join(say.split())
    c["segments"].append(d)


# =====================================================================
chapter("ch01", "A gap that refuses to close",
        "Hook with real exact-diagonalization data. Make the viewer feel the puzzle: every finite ring has a gap, "
        "the question is uniformity, and finite data has fooled people before. State the claim and its status in one "
        "breath (AI angle, first of two mentions), and promise the one picture.")

seg("""Here are two rings of quantum spins: spin one-half on the left, spin one on the right. Neighbors want to
point opposite ways, and that is the whole Hamiltonian: S dot S, summed around the ring.""",
r"""
- Two `spin_ring(10, radius=1.6, staggered=True)` at (-3.6, -0.3) and (+3.6, -0.3); left arrows `HALF`, right arrows `INTEGER` (pass `color=`).
- Labels 0.35 below each ring, font 36: `T(r"spin $\tfrac12$", color=HALF)` and `T(r"spin $1$", color=INTEGER)`.
- Top centre (y = 3.0), font 40: `M(r"H_L=\sum_{j=0}^{L-1}\mathbf S_j\cdot\mathbf S_{j+1},\qquad \mathbf S_L=\mathbf S_0")`.
- Timing: Create both rings (0.35 d), Write H (0.3 d), then a "quantum wobble": every arrow rotates +/-12 degrees and back, alternating sign by site, `rate_func=there_and_back` (0.25 d).
""",
"Up/down arrows are a classical cartoon. The even-ring ground state is a singlet, not Neel order; never label the cartoon 'ground state'.")

seg("""Make the rings longer and track the gap, the energy of the first excited state. These are exact
diagonalizations, up to 24 sites for spin one-half and 16 for spin one.""",
r"""
- Rings scale to 0.4 and move to the top-left / top-right corners.
- Build the **GAPPLOT** motif (global conventions) centred at (0, -0.4), axes only at first. Caption via `caption(r"exact diagonalization, periodic rings")`.
- Data `data/gaps.csv` (columns `S`, `L`, `gap_first_excitation`), x = 1/`L`. Points appear in order of increasing L (right to left), the two spins alternating, `lag_ratio=0.15`, total 0.6 d: spin 1/2 = filled `HALF` dots (L = 4..24), spin 1 = hollow `INTEGER` squares (L = 4..16). Thin polylines join each series.
- Small counter at the top-right of the axes, `M(r"L=")` + `Integer`, ticking 4 -> 24 in sync.
""",
"ED stops at L = 16 for spin 1 (gap 0.4428) and L = 24 for spin 1/2 (0.1827). L = 4 is exact by hand (gap 1).")

seg("""For spin one-half, the gap falls like one over the length, on its way to zero. For spin one, it seems to
level off, near 0.41. Duncan Haldane predicted this difference in 1981, and published it in 1983.""",
r"""
- Sentence 1: dashed `HALF` guide y = 4.385 x from the L = 24 point down to the origin; small `M(r"\to0", color=HALF)` at the origin.
- Sentence 2: dashed `INTEGER` horizontal segment at y = 0.4105 from x = 0 to x = 1/16. Label, font 24, `DIM`: `T(r"0.4105 \;\cdot\; DMRG, White--Huse 1993 \;\cdot\; literature")`.
- Sentence 3: small `DIM` tag at the top-left: `T(r"Haldane: 1981 (formulated) $\cdot$ 1983 (published)", font_size=26)`.
""",
"0.41050(2) is a literature value (quoted in the periodic manuscript's introduction). No spin-1 point lies on the dashed line; the last one is 0.4428 at L = 16. Haldane: formulated 1981, published 1983.")

seg("""Seems. Every finite ring has a gap; that is just linear algebra. The real question is whether there is one
number, bigger than zero, that the gap never drops below, no matter how long the ring.""",
r"""
- On "Seems": zoom the GAPPLOT (scale the plot group 2.4x about the point (0,0) of the axes, or a `MovingCameraScene` zoom) onto x in [0, 0.07].
- Three `DIM` dashed "what-if" curves leave the last spin-1 square (1/16, 0.443): one stays flat, two bend down to 0 at very small 1/L. A large `DEFECT` `?` between the data and the y axis.
- Top, font 40: `M(r"\exists\,\gamma>0:\quad \gamma_L\ge\gamma\ \ \text{for every } L\ ?")`. Small `DIM` text near the data: `T(r"each finite $L$: $\gamma_L>0$ (trivial)", font_size=26)`.
- OBJECTION BUBBLE "every finite chain has a gap" pops in at the top-right, gets `Indicate`, and a small `GAP` label under it: "the question is uniformity".
""")

seg("""And finite data can fool you. In 1984, a published comment applied the same finite-size scaling that had
suggested a spin one gap to spin one-half chains, known to be gapless, and found strikingly similar results.""",
r"""
- The GAPPLOT shrinks to the left half (scale 0.55, opacity 0.3).
- Right half: small axes x = L in [3, 11] (ticks 4, 6, 8, 10), y = gap in [0, 1.05]. From `data/gaps.csv`, L = 4..10 only: spin 1 squares 1.00, 0.72, 0.59, 0.52; spin 1/2 dots 1.00, 0.68, 0.52, 0.42. The two series nearly overlap.
- Citation card slides in (rounded rectangle, `DIM` text, font 26): `T(r"Comment, Phys.\ Rev.\ B \textbf{29}, 5216 (1984)")`. Caption: `T("small rings: hard to tell apart")`.
""",
"History digest (Bonner and Mueller): they ran the scaling used for spin 1 on spin 1/2 and found similar 'gapped' results, and called the spin-1 question open. Do NOT say they claimed spin 1 is gapless.")

seg("""So here is the puzzle: how can a finite computation tell you something certain about every length at once?""",
r"""
- Fade everything. Centre, font 44, two lines: `T(r"How can a \emph{finite} computation say something certain")` / `T(r"about \emph{every} length $L$?")`.
- Below: a row of `INTEGER` rings of radius 0.2, 0.3, 0.45, 0.7, 1.0 marching right and off-screen, followed by `M(r"\cdots\ L\to\infty")`.
- Then the full OBJECTION BUBBLES set fades in down the right margin (all six), holds ~1.5 s, and collapses to a small stack at the top-right before fading out. They return one at a time later.
""",
"Use breath=1.5 after this clip (the question should hang).", pause=1.5)

seg("""On October 6, 2026, OpenAI released two manuscripts, produced by one of its AI models. The first claims
exactly that: on even rings, the spin one gap never closes; the second, a matching claim for open chains.
They are preprints, not yet independently refereed, but the argument is short, and its computer checks re-run on
a laptop.""",
r"""
- STATUS CARD (first appearance; plain text, no logos, no screenshots). Two title lines, font 34:
  `T(r"``The periodic spin-one Haldane gap''")` and `T(r"``A boundary-field gap for the spin-one Heisenberg chain''")`.
- Sentence 2: a small `DIM` tag appears beside each title in turn: "even rings" next to the first, "odd open chains, end fields" next to the second.
- Under them, `DIM`, font 26: `T(r"author: OpenAI $\cdot$ manuscripts dated 24 Sep 2026 $\cdot$ released 6 Oct 2026")`.
- Three status lines appear in sync with sentence 3:
  1. `DIM` circle: "claimed proof $\cdot$ preprint $\cdot$ not yet independently refereed"
  2. `GAP` check: "analytic argument: short, checkable by hand"
  3. `GAP` check: "finite computations: published with the paper, re-runnable on a laptop"
""",
"Status facts are limited to this allowed list (also ch10 s07-s08). No reactions, no other releases, no repository screenshots, no company branding. Only the periodic manuscript claims the even-ring gap; the boundary manuscript claims a gap for odd open chains with end fields. Keep 'even' visible if the claim is paraphrased on screen.")

seg("""And its central idea uses no field theory at all: one partition function read in two directions, a trick of
squaring probabilities, and a staircase that climbs to infinite length.""",
r"""
- First clause: three `DIM` words "field theory", `$\theta$-term`, "RG" are struck through one by one and fade.
- Montage, about d/3 each, in sync with the three items:
  1. TORUS + TWO KNIVES: `torus_rect(5, 3)` grows at centre; the orange knife sweeps up, the blue knife sweeps right.
  2. WEIGHT BARS: `weight_bars([0.6,0.15,0.1,0.08,0.07])` squares once (two-step squaring).
  3. STAIRCASE: the tromino climbs four steps on a bare `lb_plane` and exits the top-right.
- End on `title_card("The Haldane gap", sub="a claimed proof, explained")`, then fade out.
""")

# =====================================================================
chapter("ch02", "Haldane's picture, and why it is not a proof",
        "Reactivate the viewer's Altland-Simons memory quickly, be precise about why it is not a theorem, and plant "
        "the space-time sheet that the proof will reuse.")

seg("""In 1931, Bethe solved the spin one-half chain exactly; it is
gapless. Haldane's claim that integer spins differ was rejected by several journals and dubbed a conjecture; the name stuck.""",
r"""
- Timeline along y = -3.0 from x = -6 (1930) to x = 6 (2030), `DIM`.
- Tick 1931: `T(r"Bethe: spin $\tfrac12$ solved exactly", font_size=26)`. Above it a small `HALF` dispersion plot E(k) = (pi/2)|sin k| for k in [0, pi], touching zero at both ends, captioned `DIM` font 24 `T(r"gapless (des Cloizeaux--Pearson 1962)")`.
- Tick 1981: a small "preprint" card; two `DIM` "rejected" stamps land on it (no journal names). Tick 1983: "published", and `T(r"``conjecture''")` writes above it.
""",
"Rejections and the 'conjecture' label: Haldane's Nobel lecture (history digest). Do not name journals. The dispersion (pi/2)|sin k| is des Cloizeaux-Pearson 1962, not Bethe 1931 (Hulthen's ground energy is 1938): keep the 1962 label on the inset and do not attach the curve to the 1931 tick text. The 'say' field fixes the pronunciation of Bethe.",
say="""In 1931, Bayta solved the spin one-half chain exactly; it is
gapless. Haldane's claim that integer spins differ was rejected by several journals and dubbed a conjecture; the name stuck.""")

seg("""If you learned it from Altland and Simons: in the spin path integral, each spin picks up a Berry phase, S
times the solid angle its arrow sweeps on the sphere.""",
r"""
- Left: 2D sphere = `Circle(radius=1.6)` + dashed equator `Ellipse(width=3.2, height=0.7)`. A unit arrow n from the centre; its tip traces a closed loop on the front of the sphere (`ParametricFunction`), the enclosed cap fills `TIME` at opacity 0.25.
- Right: `M(r"\mathbf S(\tau)=S\,\mathbf n(\tau),\qquad e^{\,iS\,\Omega[\mathbf n]}")` with `\Omega` in `DEFECT`, and a small label "solid angle" pointing at the cap.
- Corner `DIM` tag: "Altland \& Simons, $\theta$-term section".
""",
"Do not cite an Altland-Simons section or equation number (unverified).")

seg("""In an antiferromagnet, neighbors point opposite ways, and their Berry phases nearly cancel. Nearly. What
survives is theta times Q, where Q counts how often the staggered field wraps the sphere over space time, and
theta equals two pi S.""",
r"""
- `spin_chain(10, spacing=0.9, staggered=True, tilt=0.15)` across the middle; above it `M(r"\mathbf S_j\approx S\big[(-1)^j\,\mathbf n(x_j)+\mathbf L(x_j)\big]")`.
- Under each adjacent pair, small labels `+\Omega_j` / `-\Omega_{j+1}`; brackets merge into a tiny `DEFECT` sliver labelled "leftover" on "Nearly".
- Then centre: `M(r"S\sum_j(-1)^j\,\Omega_j\ \longrightarrow\ \theta\,Q,\qquad Q=\frac1{4\pi}\int dx\,d\tau\ \mathbf n\cdot(\partial_x\mathbf n\times\partial_\tau\mathbf n)\in\mathbb Z,\qquad \theta=2\pi S")`; `\theta=2\pi S` gets a `DEFECT` `SurroundingRectangle`.
- Below: a 7x7 grid of small arrows forming a 2D projection of a skyrmion (radial, length shrinking toward centre and rim), caption `M("Q=1")`.
""",
"Sign and factor conventions vary between textbooks; everything is mod 2 pi.")

seg("""So the low-energy theory is the O three sigma model plus a topological term, weighting each winding sector by e to the i theta Q.
For half-integer spin, theta is pi, modulo two pi: sectors alternate in sign, interfere, and the chain stays
critical.""",
r"""
- `M(r"S_{\rm eff}[\mathbf n]=\frac1{2g}\int dx\,d\tau\,\Big[\tfrac1v(\partial_\tau\mathbf n)^2+v(\partial_x\mathbf n)^2\Big]\;-\;i\theta Q")` then below `M(r"Z=\sum_{Q\in\mathbb Z}e^{\,i\theta Q}\,Z_Q")`.
- Phasor row, `HALF`, label `M(r"\theta=\pi\ (\mathrm{mod}\ 2\pi)", color=HALF)`: arrows of length 1, 0.6, 0.35, 0.2 laid head to tail with alternating direction; the resultant arrow shrinks. Caption "interference: critical".
""",
"The instanton-gas cartoon is qualitative only.")

seg("""For integer spin every phase is one, leaving the plain O three sigma model, believed to generate a mass: a
gap shrinking like e to the minus pi S, up to powers of S.""",
r"""
- Second phasor row under the first, `INTEGER`, label `M(r"\theta=2\pi", color=INTEGER)`: same lengths, all pointing right; long resultant. Caption "plain O(3) model".
- Right: small schematic axes x = log(length scale), y = g, a curve rising slowly then sharply; a dashed vertical where g ~ 1 labelled `M(r"\xi")`; corner tag "schematic".
- `M(r"\Delta\ \propto\ e^{-\pi S}\quad(\text{up to powers of }S)", color=GAP)`.
""",
"Do not quote a prefactor (it depends on loop order). Curve is schematic, not data.")

seg("""But it is not a proof. It expands in large spin, then sets S equal to one. It takes a continuum limit of a
lattice whose correlation length is only about six sites. And even the endpoint, the mass gap of the O three model,
has no accepted proof.""",
r"""
- Checklist with three `DIM` crosses, one per sentence 2-4:
  1. "large-$S$ expansion, used at $S=1$"
  2. "continuum limit, but $\xi\approx6$ sites" + small `DIM` "literature"
  3. "mass gap of the 2D O(3) model: no accepted proof"
- OBJECTION BUBBLE "doesn't the $\theta$-term already explain it?" appears top-right; `Indicate`; label under it: "it explains; it does not prove".
""",
"xi ~ 6 is a literature value (bulk QMC 6.0153; the White-Huse 6.03 is the end-spin length). Write only 'about 6'. Item 3 says 'no accepted proof', not 'not a theorem' (unrefereed claims exist; do not mention them).")

seg("""Keep one image, though: a sheet of space and imaginary time, edges glued. The new proof lives there too, but
asks a very different question.""",
r"""
- A skyrmion-like arrow texture fills a rectangle; the rectangle becomes `torus_rect(5, 3)` with L (`SPACE`) below and beta (`TIME`) at left and the identification chevrons (recoloured by periodic direction, see TORUS motif). The arrows fade, leaving the bare torus; hold 1 s.
""")

# =====================================================================
chapter("ch03", "Why a proof was hard",
        "What rigor could and could not do: LSM leaves integer spin unconstrained; AKLT shows the 'finite check' "
        "template but only for frustration-free chains; Heisenberg is not frustration-free; the evidence; Tasaki's conditional "
        "theorem. End by stating exactly what is claimed, so the viewer knows the target.")

seg("""What could mathematics prove? On the half-integer side, a lot. Lieb, Schultz and Mattis, and later Affleck
and Lieb, showed that a half-integer chain cannot have a unique ground state with a gap: it is gapless, or
degenerate.""",
r"""
- Two columns. Left card, `HALF` border: header "half-integer $S$"; body `T(r"Lieb--Schultz--Mattis 1961 $\cdot$ Affleck--Lieb 1986")` and `T(r"no unique gapped ground state")`; two small icons below: "gapless" OR "degenerate".
- Right card, `INTEGER` border: header "integer $S$", empty body.
""",
"Affleck-Lieb is an obstruction, not a proof of gaplessness: keep the 'or degenerate'.")

seg("""Their trick, a slow spiral of the spins around the ring, costs energy of order one over L and, for half-integer
spin, is orthogonal to the ground state. Integer spin escapes, but escaping a no-go theorem is not having a gap.""",
r"""
- `spin_ring(12, radius=1.4)` (FG) in the centre: arrow j rotates in the plane by 2 pi j / 12 relative to its staggered base orientation, forming a helix. `DIM` label "slow spiral (a variational state)".
- Meter: `M(r"\Delta E=O(1/L)")`.
- `HALF` badge "orthogonal to the ground state"; then the `INTEGER` card gets a large `?` and the caption `T(r"escaping a no-go $\neq$ having a gap")`.
""",
"TWIST RULE: this 'slow spiral' is unrelated to the seams of ch04/ch08 and to Tasaki's twist of ch09. Never reuse this visual there.")

seg("""In 1987, Affleck, Kennedy, Lieb and Tasaki found a cousin with a provable gap: split each spin one into two
spin one-halves, bound into singlets across every bond. That A-K-L-T state minimizes every bond term at once, and
for such frustration-free chains, a large enough gap on one finite chain settles all longer ones.""",
r"""
- Valence-bond cartoon: 8 large circles (`INTEGER` outline, radius 0.35, spacing 1.3), each holding two small `VIRTUAL` dots; `VIRTUAL` ellipses join the right dot of site j to the left dot of site j+1. The two outermost dots stay unpaired with a soft glow (they return in ch09).
- Above: `M(r"h_{\rm AKLT}=\mathbf S_j\cdot\mathbf S_{j+1}+\tfrac13\big(\mathbf S_j\cdot\mathbf S_{j+1}\big)^2")`.
- Sentence 2: a small `GAP` check over every bond ("each bond at its minimum"), then a boxed mini-chain with the arrow `T(r"gap on one finite chain large enough $\Rightarrow$ gap for all longer chains")` and a `DIM` tag "frustration-free only".
""",
"Finite-size criteria of this kind (Knabe-type) apply only to frustration-free chains. Save this cartoon as a reusable function (needed in ch08 s13 and ch09 s01).")

seg("""The Heisenberg chain is not frustration-free: each bond would love to be a singlet, at energy minus two, but a spin
cannot be in a singlet with both neighbors, so the ground state settles near minus 1.40 per bond. That kills the finite check, and perturbation theory around A-K-L-T stops short of the Heisenberg point.""",
r"""
- Number line from -2.1 to -1.2: marker at -2 "singlet: one bond's minimum"; marker at -1.4015 "Heisenberg ground state, per bond (literature)". Above it, a `spin_chain(8)` whose bonds try to snap into singlets one at a time; each snap breaks its neighbour (flicker). Big `DEFECT` text "about 70\%".
- Sentence 2: a horizontal parameter line labelled `M(r"h+c\,h^2")`: points "Heisenberg, $c=0$" and "AKLT, $c=\tfrac13$". A shaded `GAP` disk around AKLT, "proved gapped neighbourhood", visibly not reaching c = 0; a `?` at Heisenberg.
""",
"Bond spectrum {-2, -1, 1} is in the paper; -1.4015 per bond is the literature e0. Yarotsky's result covers a neighbourhood of AKLT only, not a gapped path to the bilinear point; draw no path. Wording: 'not frustration-free' (the paper's term: no state minimizes every bond). Never write 'frustrated' for the even ring on screen: the bipartite even ring is the textbook UNfrustrated magnet (Marshall sign rule). Plain 'frustration' is reserved for odd rings.")

seg("""Physicists, meanwhile, stopped doubting. Neutrons saw the gap in cesium nickel chloride in 1986, and in
1993, D-M-R-G pinned it at 0.4105.""",
r"""
- Two evidence cards slide in from the right: `T(r"1986: neutron scattering on CsNiCl$_3$ (Buyers et al.)")` and `T(r"1993: DMRG, $\Delta=0.41050(2)$ (White--Huse)")`, the second with a `DIM` "literature" tag.
""",
"Buyers et al. 1986 is CsNiCl3 (not NENP).")

seg("""In 2024, Hal Tasaki proved that if odd open chains with a field on their end spins have a uniform gap, the
ground state is topologically nontrivial. He named a computer-aided proof of that gap as the challenge.""",
r"""
- Card: `T(r"Tasaki 2024 (PRL 2025)")`. Body: a tiny odd open chain with two small field arrows h on the end spins; `M(r"\text{uniform gap}\ \Longrightarrow\ \text{topologically nontrivial (index }-1)")`; a `DEFECT` underline and `?` on "uniform gap".
- Second line (paraphrase, not a quotation): `T(r"challenge: a computer-aided proof of the gap")`.
""",
"Tasaki's theorem is conditional on a uniform gap of the ODD OPEN chain with end fields (his Assumption 2). arXiv July 2024, PRL 134, 076602 (2025). The card is a paraphrase.")

seg("""Here, precisely, is the claim. For the spin one ring of every even length from 60 sites on, the gap exceeds
0.000479. From two thousand three hundred and four sites on, it exceeds log 20 over 784, about 0.0038.""",
r"""
- Theorem card, `GAP` border, header `T(r"Claimed theorem (periodic manuscript, Thm.~1.1)")`:
  - `M(r"\text{spin }1,\quad H_L=\sum_j\mathbf S_j\cdot\mathbf S_{j+1},\quad L\ \text{even}")`
  - `M(r"L\ge60:\qquad \gamma_L>\tfrac{4}{105}\log\tfrac{80}{79}\approx4.79\times10^{-4}")`
  - `M(r"L\ge2304:\qquad \gamma_L>\tfrac{\log20}{784}\approx3.82\times10^{-3}")`
- Keep a small copy of this card pinned top-right (scale 0.45) until the end of the chapter.
""",
"Thm 1.1 (1.3)-(1.4). Even rings only. (4/105) log(80/79) = 4.7919e-4 is BELOW 0.00048: never print or say '> 4.8e-4' or 'exceeds 0.00048'; use 4.79e-4 / 0.000479. log 20/784 = 3.8211e-3, so '> 3.82e-3' and 'about 0.0038' are safe. The '784' and '1/20' are explained in ch07-ch08 (payoff: 'that is where log 20 over 784 comes from').")

seg("""That is about a hundred times below the true 0.41: the claim is that a gap exists, not its size. Uniqueness
of the ground state on even rings is classical, from Marshall, Lieb and Mattis. The new content is uniformity.""",
r"""
- Horizontal log-scale bar chart, x from 1e-4 to 1 (ticks `10^{-4}` ... `10^0`): `GAP` bars at 0.000479 and 0.00382; hollow `INTEGER`-outline bar at 0.4105 labelled "literature". Braces "x107" and "x857".
- `DIM` line: `T(r"unique ground state on even rings: classical (Marshall--Lieb--Mattis)")`.
- Big `GAP` text: "uniformity in $L$". The bubble "every finite chain has a gap" `Indicate`s once more.
""",
"Ratios (critic): 0.4105/0.003821 = 107.4 and 0.4105/0.000479 = 856.7. Never present uniqueness on even rings as new.")

# =====================================================================
chapter("ch04", "One torus, two knives",
        "Build the one object of the proof: Z(L, beta) read along time (Gibbs weights) and along space (a "
        "self-adjoint spatial transfer operator on bond histories). Make the symmetric real kernel feel inevitable; "
        "answer 'why even L?' with the paper's own numbers.")

seg("""Everything revolves around Z of L and beta, the trace of e to the minus beta H for a ring of L spins. As a
path integral it lives on a torus: space wraps because the ring is periodic, imaginary time because of the trace.""",
r"""
- `spin_ring(10, color=FG)` at left; `M(r"Z(L,\beta)=\operatorname{Tr}\,e^{-\beta H_L}")` at right.
- The ring is copied upward 6 times (faint, offset in y) to suggest a cylinder; the stack collapses into `torus_rect(width=5, height=3, nx=10, ny=6)` at centre.
- Identification chevrons pulse, coloured by the direction that is periodic: `TIME` chevrons on top/bottom with orange label "time is periodic: trace", `SPACE` double chevrons on left/right with blue label "space is periodic: ring". (`torus_rect` builds them the other way round; recolour after construction: submobjects 2-3, the top/bottom chevrons, -> `TIME`; submobjects 4-5, the left/right chevrons, -> `SPACE`.) L label (`SPACE`) below, beta (`TIME`) left.
""",
"Colour code fixed from here on: horizontal extent L = SPACE blue; vertical extent beta = TIME orange; identification marks take the colour of the periodic direction. From ch08 s02 on, H carries the paper's added constant per site (said aloud once there; its value 1.401482 is given in ch08 s07). No separate symbol for it, and no e^{-a beta}.")

seg("""Slice it with a horizontal knife, and you cut the whole ring at one instant. Stepping upward is imaginary-time
evolution, so Z is a sum of e to the minus beta E over all eigenstates: positive weights, the Gibbs distribution.""",
r"""
- The orange horizontal knife (TORUS + TWO KNIVES motif) enters and cuts at mid-height; the cut glows; a copy of `spin_ring(10, radius=0.6)` pops out to the right.
- The knife steps upward in 6 small jumps, each labelled faintly `M(r"e^{-\delta\tau H}")`.
- Right: schematic `level_diagram([0,0.6,0.6,0.6,1.1,1.3,1.3], color=TIME)` and orange `weight_bars([0.55,0.12,0.12,0.12,0.04,0.03,0.02], color=TIME, highlight=0, highlight_color=TIME)`; `M(r"Z=\sum_k e^{-\beta E_k},\qquad w_k=\frac{e^{-\beta E_k}}{Z}", color=TIME)`.
""",
"Level diagram and bars are schematic (small DIM 'schematic' tag). One bar per EIGENSTATE, counted with multiplicity: the threefold level gets three separate bars (the uniqueness argument of ch05 s06 depends on this).")

seg("""Slice vertically, between two sites, and you cut one bond's whole history in imaginary time. Stepping it around the ring
takes a spatial transfer operator X, in the spirit of Suzuki's quantum transfer matrix, and Z becomes the trace of X to the L, a sum of its eigenvalues lambda to the L.""",
r"""
- Treat the torus's faint vertical grid lines (`nx=10`, width 5: x = -2.0, -1.5, ..., 2.0) as site world lines. The blue vertical knife enters and cuts at x = -1.75, MIDWAY between two site lines (on a bond, never on a site); the full-height cut glows and is lifted out to the right as a vertical line carrying 5 short ticks in `SX`/`SY`/`SZ` at random heights, labelled "a bond's history".
- The knife steps right in 10 jumps of 0.5 (bond to bond), each labelled faintly `M("X")`.
- Right, below the thermal formula: `M(r"Z=\operatorname{Tr}\,X_\beta^{\,L}=\sum_i\lambda_i(\beta)^{L}", color=SPACE)`; a small number line with a few blue dots, one near 1, and a DIM "schematic" tag.
- Small `DIM` tag: "in the spirit of Suzuki's quantum transfer matrix".
""",
"Say and show only 'in the spirit of'. X is not claimed to equal Suzuki's QTM (finite-Trotter QTMs are different operators). In the paper the states of X are BOND histories and each site is the kernel between its two incident bond histories (s06), so the cut goes through a bond, not along a site world line (unlike Suzuki's QTM). No eigenvalues of X are known numerically: every eigenvalue number line in ch04 is schematic.")

seg("""In a relativistic continuum you could just rotate the torus; on a lattice, the spatial operator has to be built.
Recall how that works for a classical Ising ring: one variable per site, and a weight that is a product of factors,
each coupling two neighbors. Put those factors in a matrix T, indexed by the variable, and Z is the trace of T to the L.
So we need two things: a variable for each slot of the ring, and a weight that is a product of nearest-neighbor
factors.""",
r"""
- Torus rotates and back ("continuum: rotate the torus" / "lattice: build X").
- Right panel: a classical Ising ring of +/- spins; `M(r"Z=\sum_{\{s\}}\prod_j e^{Ks_js_{j+1}}")`, `M(r"T(s,s')=e^{Kss'}")`, `M(r"Z=\operatorname{Tr}T^L")`.
- Checklist: "1. a variable for each slot"; "2. weight = product of nearest-neighbour factors".
""",
"Classical anchor only; standard 1D transfer matrix.")

seg("""For the quantum ring, rewrite the Hamiltonian first. Multiply the spin one matrices by i, in a Cartesian basis,
and they become real antisymmetric matrices, G alpha. Each bond term is then exactly minus the sum of G alpha tensor G
alpha, so minus H is a sum of terms with plus signs, one for each bond and each label.""",
r"""
- `M(r"G_\alpha=iS^\alpha,\qquad (G_\alpha)_{jk}=\varepsilon_{\alpha jk}")`, the matrix G_z, tag "real, antisymmetric, norm 1".
- `M(r"\mathbf S_j\cdot\mathbf S_{j+1}=-\big(G_x\otimes G_x+G_y\otimes G_y+G_z\otimes G_z\big)")`, then `M(r"-H=\sum_{\text{bonds}}\sum_\alpha G_\alpha\otimes G_\alpha")`.
""",
"Paper eq. (2.2). Bond eigenvalues -2, -1, 1.")

seg("""Now expand e to the minus beta H in powers of minus H, ordered along imaginary time. A term in this expansion is a
list of events. Each event picks a bond, a label x, y or z, and a moment, and inserts G alpha at both ends of that bond.
Its coefficient is just d t per event, so every term enters with a positive sign. The picture shows one term.""",
r"""
- `M(r"e^{-\beta H}=\sum_{k\ge0}\int_{0<t_1<\cdots<t_k<\beta}dt_1\cdots dt_k\;(-H)^k")`.
- The torus zooms to 7 site world lines (time up); events (rungs, x/y/z colours) appear in time order.
- One event: brace "bond", label legend, tau marker, a small G_z at each end. Corner tag "one term of the expansion".
""",
"Ordered bond expansion (paper Prop. 3.1; Aizenman-Nachtergaele).")

seg("""Now take the trace. Each event acts on two sites, so the trace of the whole ring splits into one three by three
trace per site. A site sees only the events on its two bonds. Merge them in time order and multiply: that is the site's
factor. The matrices do not commute, so the factor depends on how the two lists interleave: x, then y, then z gives plus
one; move the y below the x and it gives minus one.""",
r"""
- `M(r"\operatorname{Tr}\big[\cdots\big]=\prod_{\text{sites }j}\operatorname{tr}_j\big[\text{its }G\text{'s in time order}\big]")`.
- Site 3 and its two bonds highlighted; their events slide onto the site; `tr[G G G ...]`.
- Zoom: x (left, low), z (left, high), y (right, middle): `tr[G_xG_yG_z]=+1`; y slides below x: `tr[G_yG_xG_z]=-1`.
""",
"Computed: tr(GxGyGz)=+1, tr(GyGxGz)=-1, product in increasing time.")

seg("""This is the structure a transfer matrix needs, with the roles of sites and bonds exchanged. The variable lives on
a bond: its history, a list of increasing times between zero and beta, each with a label. Summing over all terms means
integrating over every bond's history, weighted by d t one up to d t k, and by one for the empty history. And each site
supplies a factor coupling its two neighboring histories, k of x j and x j plus one.""",
r"""
- Comparison: "classical Ising: variable on a site, factor on a bond" vs "here: variable on a bond (its history), factor on a site (a trace)".
- Each bond's events become a capsule labelled x_j; `M(r"d\mu(x)=dt_1\cdots dt_k,\quad\mu(\varnothing)=1")`.
- `M(r"Z_L=\int\prod_j d\mu(x_j)\;\prod_j k_\beta(x_j,x_{j+1})")`, `M(r"k_\beta(x,y)=\operatorname{tr}\big[\text{merged }G\text{'s}\big]")`.
""",
"Paper: interleavings of bond histories partition the global time simplex; mu(Omega_b)=e^{3b}.")

seg("""So the spatial operator X is the integral operator with that kernel, acting on functions of one history: X f at x
is the integral of k of x and y, times f of y, d mu of y. Composing two of them integrates over the history in between,
so around the ring the trace of X to the L is the partition function.""",
r"""
- Capsules become beads on a ring with k nodes between them; `X_beta` box in the centre.
- `M(r"(X_\beta f)(x)=\int k_\beta(x,y)\,f(y)\,d\mu(y)")`, `M(r"\operatorname{Tr}X_\beta^{\,L}=\operatorname{Tr}e^{-\beta H_L}")`.
""",
"Paper: X_b = e^{-ab}K_b with Tr X^n = Tr e^{-b(H_n+an)}. The film folds the constant a into H (stated once, ch08 s02) and calls the operator X throughout.")

seg("""Unlike a classical transfer matrix, the entries can be negative: two x events give a trace of minus two. Still,
the kernel is bounded by three, and all histories together weigh e to the three beta, so X is a compact operator with a
discrete list of eigenvalues, and Z is a sum of lambda to the L. Bonds are the states; sites do the transferring.""",
r"""
- `M(r"\operatorname{tr}(G_xG_x)=-2")` tagged "entries can be negative".
- `M(r"|k_\beta|\le3,\ \mu(\text{all})=e^{3\beta}\Rightarrow X_\beta\text{ compact}")`, `M(r"Z_L=\sum_i\lambda_i(\beta)^L")`.
- Caption "bonds = states, sites = transfer".
""",
"Paper: Hilbert-Schmidt norm <= 9 e^{6b}; real, square-summable eigenvalues.")

seg("""Sanity check: at infinite temperature every history is empty, X is just the number three, and Z is three to
the L. Three states per site. Good.""",
r"""
- The torus height animates 3 -> 0.05; all event ticks vanish; the `X_\beta` box `Transform`s into the digit 3.
- `M(r"\beta\to0:\quad X_\beta\to3,\qquad Z\to3^{L}")` with a `GAP` check.
""",
"Empty-history kernel is tr(I_3) = 3 (paper, proof of Prop. 3.1). This anchor returns in ch06 s03.")

seg("""Now the key property. Merging two lists doesn't care which came from the left, and the matrices are real.
So the kernel is real and symmetric, X is self-adjoint, and its eigenvalues are real.""",
r"""
- Two history columns x (left) and y (right) merge into one time-ordered column; then `Swap` x and y and merge again: identical column (flash `GAP`).
- `M(r"k_\beta(x,y)=k_\beta(y,x)\in\mathbb R\ \Longrightarrow\ X_\beta=X_\beta^{\dagger}\ \Longrightarrow\ \lambda_i(\beta)\in\mathbb R")`, boxed `GAP`.
""",
"Paper: 'no reversal of the matrix product occurs'. X is compact, self-adjoint, Hilbert-Schmidt.")

seg("""Real, but not necessarily positive: the paper notes that X does have negative eigenvalues.""",
r"""
- `NumberLine` from -1.1 to 1.1 with blue dots at visibly generic positions, one near 1, a few small positive ones, and a few on the negative side; `DIM` tag "schematic" on the number line; brace over the negative ones, `M(r"\lambda_i<0")`.
- OBJECTION BUBBLE "why even $L$?" appears top-right.
""",
"The paper states explicitly that X is not positive, but gives no eigenvalues: do not use the free-boson 'Matsubara tower' numbers (-0.848, -0.768, -0.641) from the physics digest; they are a model, not data.")

seg("""On an even ring that does no harm: lambda to an even power is never negative, so every term of Z is
nonnegative. Divided by Z, these terms form a second probability distribution for the same Z. On an odd ring, a
negative eigenvalue would add a negative term, and there is no distribution. That is why the theorem is about even
rings.""",
r"""
- Signed bars of lambda_i^6, all pointing up (`DIM` tag "schematic": generic eigenvalues, not data). `M(r"L\ \text{even}:\quad \lambda_i^{L}=|\lambda_i|^{L}\ge0")`.
- Sentence 2: bars become `p_i` (`, p_i=\frac{|\lambda_i|^{L}}{Z}`); orange Gibbs bars beside them, a brace under both: "same $Z$".
- Sentence 3: the blue bars briefly become lambda_i^5 (negative ones hang below the base), labelled "odd $L$".
- Sentence 4: back to `p_i`; the bubble "why even $L$?" `Indicate`s and gets a `GAP` check.
""",
"Evenness is essential in the paper (eq. 3.8). Nothing is claimed about odd periodic rings. No odd-ring data and no seam here: the seam is introduced in ch08 s03, where the proof uses it.")

seg("""A physicist's reading, not the paper's: the top eigenvalue encodes the free energy and the others set
correlation lengths, so gap in time and correlation length in space are two faces of one mass. The proof needs none
of this.""",
r"""
- READING TAG "physicist's reading -- not in the paper" (top-right).
- Number line (schematic): tall blue dot `\lambda_0` near 1 -> "free energy per site"; `M(r"\lambda_i/\lambda_0\ \leftrightarrow\ e^{-1/\xi(T)}")`.
- Inside the torus: a vertical `TIME` arrow "gap $\Delta$ (time)" and a horizontal `SPACE` arrow "correlation length $\xi$ (space)"; `M(r"\Delta\cdot\xi\approx v", color=DIM)`.
- Then the orange level diagram and blue number line side by side with a large "$\neq$" ("not energies"); the tag and arrows fade and both knives return to flank the torus.
""",
"Interpretation. Paper quote for reference: spatial eigenvalues are 'distinct objects from the physical energies'.")

# =====================================================================
chapter("ch05", "Purity",
        "Turn both readings into distributions; define purity; show T and S are ratios of Z's (and why that matters); "
        "the squaring lemma; why purity gives uniqueness and a gap; pre-empt 'purity -> 1 as beta -> infinity is "
        "trivial' by stating the real target.")

seg("""Two knives, two distributions, one Z. To measure how much one term dominates, use purity: the sum of squared
probabilities, the chance that two independent draws agree. One minus the purity is the defect, roughly twice the
chance of missing the dominant outcome.""",
r"""
- Torus thumbnail moves to the top-left (scale 0.35) and stays for the chapter (its width/height double when L/beta double).
- Centre: neutral `weight_bars([0.70,0.15,0.08,0.04,0.03], color=FG)`. Two small "draw" markers drop onto bars a few times; a match flashes.
- `M(r"P=\sum_i p_i^{\,2},\qquad u=1-P\ \approx\ 2\,(1-p_{\max})")` with u in `DEFECT`. Beside the bars, a DEFECT GAUGE (the global motif, same semantics everywhere: fill = log10 of the defect, so a nearly pure distribution shows an almost EMPTY gauge) reading u = 0.479 for these bars.
""",
"The 'about twice' holds when one outcome dominates and the rest is spread out. The letter u appears on screen only; the narration never speaks it (TTS reads it as 'you'). Gauge semantics are global: a FULL gauge always means a LARGE defect.")

seg("""Square a Gibbs weight, e to the minus beta E, and you get e to the minus two beta E.
So the thermal purity T is Z at doubled beta over Z squared: the familiar trace of rho squared.""",
r"""
- Orange bars; label `M(r"e^{-\beta E_k}")` -> `M(r"e^{-2\beta E_k}")`; two-step squaring animation (heights to p^2, then renormalise). The thumbnail's height doubles.
- `M(r"T(L,\beta)=\sum_k w_k^2=\frac{Z(L,2\beta)}{Z(L,\beta)^2}=\operatorname{Tr}\rho_\beta^{\,2}", color=TIME)`.
""")

seg("""Square a spatial weight, lambda to the L, and you get lambda to the two L. So the spatial purity S is Z at
doubled length over Z squared. Doubling beta squares one distribution; doubling L squares the other.""",
r"""
- Blue bars; label `M(r"|\lambda_i|^{L}")` -> `M(r"|\lambda_i|^{2L}")`; squaring animation. The thumbnail's width doubles.
- `M(r"S(L,\beta)=\sum_i p_i^2=\frac{Z(2L,\beta)}{Z(L,\beta)^2}\quad(L\ \text{even})", color=SPACE)`.
- Both definitions are then pinned top-right at scale 0.6 for the rest of the chapter.
""",
"Paper eq. (4.1): S(n,b) = Z_2n(b)/Z_n(b)^2, T(n,b) = Z_n(2b)/Z_n(b)^2.")

seg("""Notice: both purities are ratios of partition functions. No single energy or eigenvalue is needed, and that is
what will make the argument checkable.""",
r"""
- The pinned S and T formulas move to centre; every `Z(\cdot,\cdot)` in them glows FG while the bars fade to 20%.
- Text, font 34: `T(r"no energy, no eigenvalue: only partition functions")`. Small arrow to `T(r"$\Rightarrow$ exact identities and certified numbers")` in `GAP`.
""",
"This is the reason purity is the right quantity: the cancellation identity of ch06 is bookkeeping of Z's, and the seed of ch08 is certified from moments Z_n.")

seg("""And squaring is good for purity: the tall bar grows, the short ones collapse, and a defect becomes at most roughly half its own square, however many bars there are.""",
r"""
- Two demos side by side, each with live `DecimalNumber`s for u before/after (use `purity()` and `squared()`):
  - many bars `[0.80,0.06,0.05,0.04,0.03,0.02]` (u = 0.351 -> 0.028);
  - two bars `[0.9,0.1]` (u = 0.180 -> 0.024, the worst case: equality).
- `M(r"1-P'\ \le\ f(u)=\frac{u^2}{2(1-u)^2}\ \approx\ \frac{u^2}{2}")`, f in `DEFECT`; tag "any number of bars".
""",
"Paper Lemma 4.1. Equality only for two-outcome distributions. Dimension-free: 3^L levels or infinitely many spatial eigenvalues.")

seg("""Why chase purity? If the thermal purity is above one half, so is the largest Gibbs weight, and the ground
state is unique: two copies would each need more than half. The excited level's relative weight, e to the minus
beta times the gap, is at most the leftover over the ground weight. Small defect, small ratio: a gap.""",
r"""
- Orange bars with a dashed line at height 1/2; the tallest bar crosses it. A second equal bar is attempted beside it; both turn `DEFECT` and a cross appears ("total $>1$").
- `M(r"\max_k w_k\ \ge\ \sum_k w_k^2=T>\tfrac12")`.
- Sentence 2: `level_diagram([0, 0.6])` with `gap_brace` (`GAP`, label `\gamma_L`); `M(r"\frac{w_1}{w_0}=e^{-\beta\gamma_L}\ \le\ \frac{1-w_0}{w_0}")`.
""",
"Largest weight >= purity (proof of Prop. 4.3). The per-site energy shift cancels from w1/w0 (eq. 4.17).")

seg("""Here a skeptic jumps in: at any fixed length, purity goes to one as beta grows, for spin one and spin one-half
alike. The first objection, in a new costume.""",
r"""
- Plot from `data/thermal_purity_vs_beta.csv` (columns `S`, `L`, `beta`, `1-T`): x = `beta` in [0, 40], y = log10(`1-T`) in [-14, 0] (linear axis, ticks labelled `10^{k}`). Curves: (S=1.0, L=4) `INTEGER` solid with square markers every 4 units, (S=1.0, L=12) `INTEGER` dashed, (S=0.5, L=8) `HALF` solid, (S=0.5, L=18) `HALF` dashed. All dive. Clip points with `1-T` < 1e-14. Text labels at curve ends ("spin 1, L=4", ...).
- Caption: "fixed $L$: purity $\to1$, gapped or not". The bubble "every finite chain has a gap" `Indicate`s; the bubble "why not just double $\beta$?" appears.
""",
"Real ED data (numerics digest).")

seg("""But suppose beta doubles each step while the defect squares. Then the defect falls exponentially in beta, at a
fixed rate, and that rate is a gap at every length along the way. So that is the target: length and beta doubling
together.""",
r"""
- `lb_plane(n_max=6)`: a diagonal ray of dots at (k, k), k = 1..4, labelled u, u^2, u^4, u^8 (`DEFECT`).
- Inset: log u vs beta for those points: a straight line.
- Text box: `T(r"target: $L$ and $\beta$ double together; $u\to\sim u^2$")`.
""")

# =====================================================================
chapter("ch06", "The leapfrog",
        "The key idea, rediscovered: two failed attempts, the exchange-rate question, the exact cancellation identity, "
        "the four-step leapfrog on the staircase, linear loss vs quadratic gain, and the collapse of the defect.")

seg("""Two gauges track the two defects: p, one minus the spatial purity, and q, one minus the thermal purity. Let's try. Attempt one: double only beta. The thermal defect squares, again and again, but the ring never grew: we have
proved that one fixed ring has a gap, which we knew.""",
r"""
- DEFECT GAUGES appear (blue p "spatial", orange q "thermal"); under them `M(r"p=1-S")` (`SPACE`) and `M(r"q=1-T")` (`TIME`), on screen until attempt two. The torus thumbnail grows only vertically, three doublings; the orange gauge drops u -> u^2 -> u^4.
- On a small `lb_plane`, an arrow goes straight up from the start point; `DIM` stamp "fixed $L$: already known". The bubble "why not just double $\beta$?" gets a `GAP` check.
""")

seg("""Attempt two: double only the length. The spatial defect squares, but the longer ring's thermal purity, at
the same beta, gets worse. A rough heuristic: a defect counts places for an excitation, times its Boltzmann cost, and a longer ring has more places.""",
r"""
- The thumbnail grows only horizontally; the blue gauge drops but the orange gauge RISES (pulse `DEFECT`).
- Inset bar chart from `data/thermal_purity_vs_beta.csv`, rows `S == 1.0`, `beta == 8.0`, L = 4, 6, 8, 10, 12, column `1-T`: 0.0020, 0.0185, 0.0498, 0.0838, 0.1132 (orange bars rising). Caption "same $\beta$, longer ring".
- Sentence 2: torus with three small `TIME` blobs ("thermal magnons") on a time slice; the width doubles and the number of blob slots doubles. Caption `T(r"defect $\approx$ (places) $\times$ (Boltzmann cost)")` with tag "heuristic".
""",
"Dilute-magnon heuristic; not in the paper. Keep the tag.")

seg("""The mirror image holds too: a longer imaginary time degrades the spatial purity. Each purity improves in its own direction and degrades in the other.""",
r"""
- Sentence 1: inset from `data/spatial_purity_vs_beta.csv`, rows `S == 1.0`, `n == 4`: x = `beta` in [0, 24.5], y = `1-S`: a blue curve rising toward 1 (`DIM` note "small ring, qualitative"), with a small `DIM` callback label at beta = 0: `M(r"\beta\to0:\ X\to3,\ S\to1")`. Beside it the two DEFECT GAUGES (defect semantics, as everywhere: full = large defect): at beta -> 0 the blue spatial-defect gauge is EMPTY ("$S\to1$") and the orange thermal-defect gauge FULL ("$T\to3^{-L}$"); as a marker slides along the inset to large beta they swap (blue fills, orange drains).
- Sentence 2: 2x2 table: rows T, S; columns "double $\beta$", "double $L$": T improves / degrades, S degrades / improves (arrows down = improves in `GAP`, up = degrades in `DEFECT`).
""",
"n = 4 is below xi ~ 6, so the inset is qualitative only. The beta -> 0 anchor (visual only; the narration sentence was cut for length): X -> 3 gives S -> 1 and T -> 3^{-n} (critic). Gauges use DEFECT semantics: never draw a full gauge for a pure distribution.")

seg("""So we must double both, and everything hinges on the exchange rate: doubling beta squares the thermal defect q,
but how much does it cost the spatial defect p? Pause here. This is where the proof is decided.""",
r"""
- The two gauges sit on a balance-scale icon; `T(r"exchange rate?")`; pause glyph.
""",
"breath=2.0 after this clip.", pause=2.0)

seg("""The answer starts from an identity, almost embarrassingly simple. The spatial purity at doubled beta equals the old
one squared, times the thermal purity of the doubled ring, over the old thermal purity squared. To check it, write each
purity in partition functions: S is Z of the doubled ring over Z squared, and T is Z at doubled beta over Z squared.
Substitute, and everything cancels: an exact equality, by pure algebra.""",
r"""
- Write `M(r"S(n,2\beta)=S(n,\beta)^2\,\frac{T(2n,\beta)}{T(n,\beta)^2}")`, S terms `SPACE`, T terms `TIME`.
- Sentence 3: reminder line `M(r"S(n,\beta)=\frac{Z(2n,\beta)}{Z(n,\beta)^2},\qquad T(n,\beta)=\frac{Z(n,2\beta)}{Z(n,\beta)^2}")`, S `SPACE`, T `TIME`.
- Expand with `TransformMatchingTex`: LHS `\frac{Z(2n,2\beta)}{Z(n,2\beta)^2}`; RHS `\frac{Z(2n,\beta)^2}{Z(n,\beta)^4}\cdot\frac{Z(2n,2\beta)}{Z(2n,\beta)^2}\cdot\frac{Z(n,\beta)^4}{Z(n,2\beta)^2}`. Strike the `Z(2n,\beta)^2` pair, then the `Z(n,\beta)^4` pair (`DEFECT` lines, fade); what remains equals the LHS (flash `GAP`, check mark).
- Footnote (`DIM`, font 24): "ED check, 35 cases: $|\Delta\log|<4\times10^{-15}$" (`data/cancellation_identity_check.csv`, column `abs diff (logs)`).
""",
"Paper eq. (4.5). Pure algebra, valid for any positive Z; the numerical check only confirms code.")

seg("""One way to see it: both sides are one signed combination of log Z on four tori, a big one, its halves and its quarters. Area terms cancel, and a mixed second difference doesn't care which direction comes first.""",
r"""
- Big torus 2n x 2beta (width 5, height 3). Overlay in sequence, each with a weight badge: whole `+1`; two tall halves (n x 2beta) `-2`; two wide halves (2n x beta) `-2`; four quarters `+4`.
- `M(r"\log Q=F(2n,2\beta)-2F(n,2\beta)-2F(2n,\beta)+4F(n,\beta),\qquad F=\log Z")`; area check `M(r"\text{area: }4-2\cdot2-2\cdot2+4\cdot1=0")`.
- `M(r"\frac{S(n,2\beta)}{S(n,\beta)^2}\;=\;Q\;=\;\frac{T(2n,\beta)}{T(n,\beta)^2}")`. Small `DIM` tag "one way to see it".
""",
"Reformulation from the logic audit; algebraically identical to the paper's identity (the paper just says 'direct cancellation'). Do not add a winding-loop picture here.")

seg("""Now the answer. A purity is at most one, so dropping the denominator can only make the right side smaller: the new
spatial purity is at least the old one squared, times the thermal purity of the doubled ring. In defects, with p for this
ring and q for the doubled ring, that bound comes to about 2p plus q. So doubling beta costs only a linear amount: the
spatial defect roughly doubles, and picks up the thermal one. That is the exchange rate, and it is cheap: squaring gains
quadratically, so once both defects are small, the gain wins.""",
r"""
- In the identity, `T(n,\beta)^2` gets an arrow "$\le1$" and fades: `M(r"S(n,2\beta)\ \ge\ S(n,\beta)^2\,T(2n,\beta)")`.
- Defect form: `M(r"1-S(n,2\beta)\ \le\ 1-(1-p)^2(1-q)\ \approx\ 2p+q")` with p `SPACE`, q `TIME`; the blue gauge pulses up; brace "linear loss".
- Last sentence: `M(r"\text{squaring: }\ u\ \to\ \approx u^2/2")` with "quadratic gain" (`GAP`); `M(r"2p+q\ \ll\ \text{gain once small}")` is NOT shown (the basin edge is quantified in s11).
""",
"'Both denominators are at most one' is the only inequality in the coupling step (paper).")

seg("""A mirror identity, with space and time swapped, lets spatial purity pay for doubling the length of the
thermal one. Now chain them, tracking a pair: spatial purity at length n, thermal purity at length two n, same beta.""",
r"""
- `M(r"T(4n,\beta)=T(2n,\beta)^2\,\frac{S(2n,2\beta)}{S(2n,\beta)^2}\ \ \Longrightarrow\ \ T(4n,\beta)\ \ge\ T(2n,\beta)^2\,S(2n,2\beta)")`. Two coins: an orange coin moves onto the blue term ("T pays"), a blue coin onto the orange term ("S pays").
- Sentence 2: STAIRCASE axes `Axes(x_range=[0,3.2,1], y_range=[0,2.2,1], x_length=6, y_length=4)` at left; x ticks `n, 2n, 4n, 8n` (`SPACE`), y ticks `\beta, 2\beta, 4\beta` (`TIME`). Initial tromino: `SPACE` segment (n,beta)-(2n,beta) labelled `S:\ p`; `TIME` segment (2n,beta)-(2n,2beta) labelled `T:\ q`; dots at the three corners.
""",
"Paper eq. (4.6) is a separate identity with the roles of S and T swapped (not the same identity 'one corner over'). Tracked pair = (S at n, T at 2n), Lemma 4.2. Never draw S and T at the same length.")

seg("""Step one: pay with thermal purity to double beta for the spatial one. Step two: square in space, which
doubles the length. Step three: pay with the new spatial purity to double the length for the thermal one. Step four:
square in time.""",
r"""
- One animation per sentence on the tromino, with a running list in a right panel:
  1. The `SPACE` segment lifts (dashed copy) to (n,2beta)-(2n,2beta), label `\approx2p+q`; the `TIME` segment flashes (it pays). List: "1. double $\beta$ for $S$ (paid by $T$)".
  2. The lifted segment slides/stretches to (2n,2beta)-(4n,2beta), label `p_+=f\big(1-(1-p)^2(1-q)\big)`. List: "2. square in space".
  3. The `TIME` segment (2n,beta)-(2n,2beta) jumps right to (4n,beta)-(4n,2beta) (dashed) while the new `SPACE` segment flashes. List: "3. double $L$ for $T$ (paid by $S$)".
  4. It squares upward to (4n,2beta)-(4n,4beta), label `q_+=f\big(1-(1-q)^2(1-p_+)\big)`. List: "4. square in time".
""",
"Paper Lemma 4.2; p_+ (rounded up) enters the q_+ update. The corner (n, 2beta) enters only through a denominator bounded by 1.")

seg("""The pair that sat at n and beta now sits at two n and two beta: same shape, twice the size, one step up a
staircase.""",
r"""
- Ghost the original tromino; highlight the new one (2n,2beta)-(4n,2beta)-(4n,4beta); dashed diagonal arrow from (n,beta) to (2n,2beta).
- Zoom out: two more ghost trominoes further up the diagonal.
""")

seg("""Count the cost. About three defects go in, and squaring halves their square: about nine halves of the defect squared. Keep the exact correction factors, and this quadratic gain beats the linear loss below about
0.127, just above one eighth. Call that region the basin.""",
r"""
- Sentence 2: `M(r"f\big(1-(1-u)^3\big)=G(u)\,u^2\approx\frac{(3u)^2}{2}=\tfrac92u^2,\qquad G(u)=\tfrac12\big[(1-u)^{-1}+(1-u)^{-2}+(1-u)^{-3}\big]^2")`.
- Sentence 3: small note `M(r"G(0)=\tfrac92,\qquad G(0.127)\approx7.8")` ("corrections grow"). Cobweb plot: axes u in [0, 0.16] both ways; curve y = G(u) u^2 (`DEFECT`), diagonal y = u (`DIM`). Dashed vertical at u* = 0.127 labelled `T(r"basin edge $\approx0.127$ (computed)")`; a tiny `DIM` tick at 1/8 = 0.125 just left of it. Cobweb from u = 0.100: 0.100 -> 0.069 -> 0.029 -> 0.004 (`GAP`), falling to 0. Second cobweb from 0.135 escaping: 0.135 -> 0.149 -> 0.192 (`SX` red, clipped).
- Sentence 4: the region u < 0.127 shades `GAP` (opacity 0.15), labelled "basin".
""",
"u* = 0.127311 solves u G(u) = 1 (critic computation, not printed in the paper). Do NOT show 2/9 (where (9/2)u^2 = u) as the edge: the edge needs the exact G(u), which is about 7.8 there, not 4.5. Use 'about 0.127, just above one eighth' consistently (ch07 s08, ch08 s12). Paper hypotheses for the clean recursion: 0 < u0 < 1/6, G(u0) <= C, r = C u0 < 1, C(1 - 3u0) > 3. Cobweb values verified.")

seg("""Iterate. If both defects start at one in a hundred, the next round gives five in ten thousand, then about one
in a million, then about eight in a trillion. The number of zeros doubles every step.""",
r"""
- Column from `data/bootstrap_dyadic.csv`, rows `row == "n0=2304"`, j = 0..3, column `u_j`: 1e-2, 5e-4, 1.25e-6, 7.8e-12, one per beat, each with a bar of length proportional to -`log10_u_j`. Show j and u_j only; label the scales symbolically ($n_0$, $2n_0$, $4n_0$, ...), not with numbers yet (the values 2304 and 784 are revealed in ch08 s11).
- On the left the tromino keeps climbing the diagonal in sync.
""",
"This is the paper's row 2 (u0 = 1/100, C = 5, r = 1/20): u_j = C^{-1} r^{2^j}. The callback 'the one in a hundred we started from' comes in ch08 s11.")

# =====================================================================
chapter("ch07", "From purity to a gap",
        "Doubly exponential in steps = exponential in beta = a gap; interpolation; gap extraction. Then the sharpest "
        "skeptical question: the machine is spin-blind, so why doesn't it prove spin one-half gapped? Answer with "
        "real ED data and a flagged CFT calculation; conclude that everything hinges on the start.")

seg("""That is doubly exponential in the number of steps. But beta doubles each step too, so against beta the
defect falls like a plain exponential, at a fixed rate: Boltzmann suppression, which is exactly what a gap looks
like.""",
r"""
- Plot A: x = j (0..5), y = `log10_u_j` from `data/bootstrap_dyadic.csv` (row n0=2304, j = 0..5): the points curve steeply downward.
- Morph the x-axis from j to beta_j = 2^j beta_0 (ticks labelled symbolically $\beta_0, 2\beta_0, 4\beta_0, \dots$, spaced proportionally): the same points now sit on a straight line. Draw it; caption `M(r"u_j\approx e^{-\beta_j\cdot\text{rate}}")`.
""",
"Narration rule: doubly exponential in the number of doublings = plain exponential in beta. u_j = C^{-1} r^{2^j} with b_j = 2^j b0 is exactly linear in b_j on a log axis.")

seg("""Doubling only reaches special lengths. For those in between, the spatial reading helps again: Z to the power one over L is a norm of the spatial eigenvalue list, shrinking as even L grows, covering every even length in between, at the cost of a factor of three in the defect.""",
r"""
- Staircase axes: reproduce the paper's Figure 1: dots at (n0,b0), (2n0,2b0), (4n0,4b0) joined by dashed diagonal arrows; thick solid horizontal bars from n_j to 2n_j at height b_j labelled "interpolate".
- `M(r"Z_L^{1/L}=\Big(\sum_i|\lambda_i|^{L}\Big)^{1/L}\ \text{ decreases in even }L")`.
- `M(r"T(L,\beta)\ \ge\ \big[T(2n,\beta)\,S(n,\beta)^2\big]^{L/2n}\ \ge\ (1-u)^3\ \ge\ 1-3u\qquad(n\le L\le2n,\ L\ \text{even})")`.
""",
"Paper eqs. (4.15)-(4.16). Even L only. The norm inequality is introduced here.")

seg("""Now cash it in. At step j, e to the minus beta j times the gap is at most about three times the defect. The
defect squares each step, so this bound falls like a fixed number below one, raised to the power two to the j: in the
paper's run, one twentieth. Meanwhile beta j is two to the j times beta zero.""",
r"""
- `M(r"e^{-\beta_j\gamma_L}\ \le\ \frac{3u_j}{1-3u_j}\ <\ (1/20)^{2^j}")` with a `DIM` tag "paper's run" under the last term; then `M(r"\beta_j=2^j\beta_0")` below it. No new letter for the base (the user asked for no extra notation such as r).
""",
"Paper eq. (4.17) and Prop. 4.3: 3u/(1-3u) < r^{2^j} with r = C u0 = 1/20 (C = 5, u0 = 1/100) for the n0 = 2304 run. The film never names r or C.")

seg("""Take logs, and the powers of two cancel. The gap exceeds log 20, divided by beta zero, at every
even length from the start on. One rate, certified at the starting scale, bounds the gap forever.""",
r"""
- Take log of both sides; strike `2^j` in `DEFECT`; result boxed `GAP`: `M(r"\gamma_L\ >\ \frac{\log 20}{\beta_0}\qquad\text{for every even }L\ge n_0", color=GAP)`.
- The straight line from s01 returns small beside it, its slope labelled with the same expression.
""")

seg("""Notice what this machine never used: spin. Two nonnegative readings of one partition function, a squaring
inequality, an algebraic identity. So why doesn't it prove spin one-half gapped, which Lieb, Schultz and Mattis
forbid?""",
r"""
- Recap card "doubling machine": three icons, two-knives torus "two nonnegative readings", squared bars "squaring inequality", 2x2 tiling "algebraic identity". A struck `DIM` tag "spin".
- Left input: `INTEGER` ring -> "gap". Right input: `HALF` ring -> "gap?!" with `SX`-red "contradicts Lieb--Schultz--Mattis". OBJECTION BUBBLE "why doesn't it prove spin $\tfrac12$ gapped?" appears.
""",
"Critic's safe line: the doubling argument does not care about spin; spin one enters through the construction of X (Prop. 3.1, spin one only) and the finite certificates.")

seg("""First, the paper builds its spatial operator only for spin one. But even granting one, the recursion needs
both defects small at the same scale. A physicist's argument: at a critical point, both purities depend only on
the torus's shape, so doubling both sides changes nothing.""",
r"""
- Sentence 1: the machine box gets a `DIM` tag "spatial operator constructed for spin 1 only (Prop. 3.1)"; the `HALF` input arrow turns dashed, labelled "suppose one existed".
- Sentences 2-3: READING TAG "physicist's reading -- not in the paper". A torus with aspect label `M(r"\rho=v\beta/L")`; the doubled torus is an exact scaled copy; two gauges (S blue, T orange) stay at the same level before and after.
""",
"Never claim a spin-1/2 spatial transfer operator exists. The CFT statements are interpretation. The aspect ratio is called rho (never r: r is the paper's contraction rate C u0, on screen in ch07 s03-s04 and ch08).")

seg("""And they seesaw: long in space means spatially pure but thermally mixed, and the reverse. Along beta
equals L, exact diagonalization shows spin one's thermal defect falling while spin one-half's stalls. Spatial defects are large for both at these tiny sizes; on such tori, spin one's should fall once the ring spans many correlation lengths, spin one-half's never will.""",
r"""
- Sentence 1: a seesaw glyph with the two gauges: a WIDE torus tilts it to "S pure, T mixed"; a TALL torus tilts it to "T pure, S mixed".
- Sentence 2: two-panel plot, both y axes log10(defect) in [-2, 0] (ticks 0.01, 0.1, 1), dashed `DEFECT` line at 0.127 labelled "basin edge" in both panels.
  - Panel A, title `T("thermal defect $1-T(L,\beta{=}L)$", color=TIME)`: `data/thermal_purity_ray.csv`, rows `c == 1.0`, x = `L`, y = `1-T`. Spin 1 (`S == 1.0`, L = 4..12): hollow `INTEGER` squares, 0.101 -> 0.018, label "spin 1". Spin 1/2 (`S == 0.5`, L = 4..18): `HALF` dots 0.105 -> 0.075, label "spin 1/2"; dashed `HALF` asymptote 0.0555 from `data/cft_spinhalf_universal.csv` (row `c == 1.0`, column `1-T CFT (beta=cL, L->inf)`), label "CFT limit".
- Sentence 3: Panel B, title `T("spatial defect $1-S(n,\beta{=}n)$", color=SPACE)`: `data/spatial_purity_ray.csv`, rows `c == 1.0`, x = `n`, y = `1-S`. BOTH spins: spin 1/2 (`S == 0.5`, n = 4, 6, 8): `HALF` dots 0.675, 0.648, 0.638, with a dashed `HALF` line at 0.618 (column `1-S CFT (beta=cn, n->inf)`, row c = 1.0) labelled "CFT: stays"; spin 1 (`S == 1.0`, n = 4, 6): hollow `INTEGER` squares 0.918, 0.879, labelled "spin 1: $n<\xi\approx6$ (literature), too short to tell". A `DIM` dashed arrow from the spin-1 squares toward the lower right, labelled "expected to fall for $n\gg\xi$ (reading)".
- Both spins' spatial points sit ABOVE the basin line at these sizes; say so visually (no `Indicate` that singles out spin 1/2). The spin-1/2 thermal points are already BELOW the line: what fails for spin 1/2 is the spatial side, and only the scale-invariance argument (s06, s08) shows it never improves.
""",
"Real ED data (numerics digest). Honesty rule: at accessible sizes the spin-1 spatial defect on these tori is LARGER than spin 1/2's (0.92, 0.88 vs 0.67, 0.65), so the ED alone does not separate the spins on the spatial side; show both, label the spin-1 points as below xi, and let the flagged CFT argument carry the spin-1/2 no-go. 'Should fall' for spin 1 is a physicist's reading (keep the tag from s06). Seesaw direction (CFT asymptotics): long in space (n >> v beta) -> S near 1, T small; long in time -> the reverse. Colour-clash rule: spin-1 series are hollow INTEGER squares with a 'spin 1' text label, and panel B's title carries 'spatial'.")

seg("""Our calculation, not the paper's: for the spin one-half chain's conformal field theory, the best balance
leaves a defect of about 0.55, far outside the basin. The physics lives in the starting data,
and for spin one, everything hinges on getting in.""",
r"""
- READING TAG "our calculation -- not in the paper".
- Plot, x = rho = v beta / n on a log axis [0.25, 4] (axis label `M(r"\rho=v\beta/n")`), y = defect [0, 1]. Curves from the SU(2)_1 torus function (compute in numpy):
  `Zc(q) = (theta3(q)^2 + theta2(q)^2) / eta(q)^2`, `theta3 = sum_n q^(n^2)`, `theta2 = sum_n q^((n+1/2)^2)`, `eta = q^(1/24) prod_k (1-q^k)`, `q = exp(-2 pi rho)`;
  `1-S(rho) = 1 - Zc(q^(1/2))/Zc(q)^2` (`SPACE`, rising); `1-T(rho) = 1 - Zc(q^2)/Zc(q)^2`; the bootstrap pairs S at n with T at 2n, i.e. `1-T(rho/2)` (`TIME` dashed, falling).
  Thick `DEFECT` curve m(rho) = max of the two; dot at its minimum 0.545 (rho = sqrt 2) labelled "best balance $\approx0.55$". `GAP` band below 0.127 labelled "basin ($<0.127$)".
- Final text: `T(r"the physics lives in the starting data")`.
""",
"Verified: at rho = pi/2 (beta = n), 1-S = 0.618 and 1-T = 0.0555; minimum of the pairing curve 0.5450 at rho = sqrt 2; the two curves 1-S(rho), 1-T(rho) cross at 0.282 at rho = 1. The aspect ratio is rho, never r (r is the paper's contraction rate). The related no-go 'no scale-invariant Z enters the basin' is also ours.")

# =====================================================================
chapter("ch08", "Getting into the basin",
        "Isn't this just numerics? Show exactly what the computer does: low moments of the same operator, seams as "
        "symmetry sectors, polynomial walls (upper jaw), one integer trial state (lower jaw), the pinch, the seed "
        "bounds (and why the thermal one is loose), six exact leapfrogs whose bounds get worse before better, and the "
        "payoff number. Then the weaker 60-site seed and two flagged physicist's checks. Every seed and update number "
        "is a certified UPPER BOUND on a defect, never the defect itself.")

seg("""The paper starts at 36 and 72 sites, at beta 12.25, far beyond any diagonalization. The rescue is the vertical knife again: Z of n is the trace of X to the n, so small rings are low moments of the very operator whose high moments we need.""",
r"""
- Staircase with real log2 scale: `Axes(x_range=[5,13,1], y_range=[3,11,1])`, x ticks 32..8192 (`SPACE`), y ticks 8..2048 (`TIME`). Seed tromino at (36, 12.25)-(72, 12.25)-(72, 24.5) pulses `DEFECT`. `M(r"\dim=3^{72}\approx2.3\times10^{34}", color=DIM)` with an `SX` cross.
- Sentence 2: a row of small FG rings n = 4..12 (`spin_ring(n, radius=0.35)`), each with an arrow converging into one blue box `M(r"X_{49/4}")`; from the box a long arrow to `M(r"\operatorname{Tr}X^{36},\ \operatorname{Tr}X^{72}\,?")`. `M(r"Z_n=\operatorname{Tr}X^n=\sum_i\lambda_i^{\,n},\qquad n=4,\dots,12")`.
""",
"Seeds sit at beta0 = 49/4; the paper gives no rationale for 36, 72, 49/4 (do not invent one).")

seg("""Is this just numerics? Not in the usual sense: rings of four to twelve sites are enclosed in integer
arithmetic, with explicit error bounds, and no floating-point eigenvalue is ever a premise. These values are for H plus a
constant per site, which cancels from every purity and the gap.""",
r"""
- The bubble "isn't this just numerics?" `Indicate`s.
- Table from `data/paper_thermal_table_check.csv`, rows `b == 12.25`, n = 4..12, two columns g = 1 and g = P, column `paper_center`; header "$\pm3\times10^{-5}$".
- Badges: "integer arithmetic", "explicit error bounds", "no floating-point premise". `DIM` footnote: "27 enclosures: 18 at $\beta=49/4$, 9 at $\beta=21/2$". The bubble gets a `GAP` check.
- Last sentence: `DIM` note under the table header, `M(r"Z_n=\operatorname{Tr}\,e^{-\beta H_n}")` "$H_n$ includes a constant per site (value in s07)".
""",
"Lemma 5.1: errors < 3e-5 at beta = 49/4 and < 1e-5 at 21/2. Our ED reproduces all 27 centres within 1e-6.")

seg("""Some rings get a seam: a half-turn spin rotation inserted at one bond. Through the vertical knife, the seam
becomes a symmetry operator inside the trace, splitting the eigenvalues into a symmetric sector and a sector of triples.""",
r"""
- A ring with one bond marked by the SEAM glyph (small circular arrow, label `M("P")`, "half turn"). Seen through the blue knife it becomes `M(r"Z_n(P)=\operatorname{Tr}\big(X^nU_P\big)")`.
- Eigenvalue number line splits into two rows: "symmetric sector $J$" (single FG dots) and "threefold sector $N$" (blue dots drawn as stacked triples, several negative).
- `M(r"Z=J+3N,\qquad Z(P)=J-N\qquad(J=I+2O)")`.
""",
"Paper Lemma 3.2: Z = I + 2O + 3N, Z(P) = I + 2O - N, Z(C) = I - O. The beta = 49/4 seed uses only twists 1 and P; the third-turn twist C is used only by the 60-site seed. Do not say the periodic paper's symmetry group has 12 elements. TWIST RULE: 'seam', no topology.")

seg("""Next, a polynomial filter: never negative, and huge beyond some wall. Its sum over one sector's eigenvalues is a
combination of known moments, a fixed budget. If one eigenvalue stood beyond the wall, it alone would exceed the
budget.""",
r"""
- Axes x in [-1.05, 1.05], y in [0, 1.2e5] (linear, labels in units of 10^4). Plot `F_N(x)=x^4(12-394x^2+1000x^4)^2` (`SPACE`), clipped at the top (it reaches about 7.6e5 at |x| = 1.05; zeros near |x| = 0.18 and 0.60).
- Dashed `DEFECT` line at `B_N = 48169.88` labelled "budget". Shade |x| >= 0.872 (`SX` red, opacity 0.2) "forbidden".
- `M(r"\sum_{\lambda\in N}F_N(\lambda)=\sum_{k=4}^{12}f_k\,N_k\ \le\ B_N,\qquad N_k=\tfrac14\big(Z_k-Z_k(P)\big)")` (the sector moments N_k come from the untwisted and seam-twisted ring tables). A blue dot tries to slide past 0.872; its F-value bar shoots above the budget and it bounces back.
""",
"Paper Prop. 5.5 and eq. (5.1): each filter acts on ONE sector's eigenvalue list (the paper's polynomial-filter lemma is stated for 'a real eigenvalue list with moments M_j'), with sector moments J_n = (Z_n + 3Z_n(P))/4, N_n = (Z_n - Z_n(P))/4. F_N(+/-0.872) - B_N > 654 (recomputed 654.29). F_N has only even powers (k = 4, 6, ..., 12). The J filter F_J = x^4(7+17x-280x^2-185x^3+1000x^4)^2 with B_J = 318604.548 gives the 1.00139 wall the same way on the J list.")

seg("""The walls land here: symmetric eigenvalues below 1.00139 in size, threefold ones below 0.872. That is the upper
jaw. But purity also needs one eigenvalue to be big.""",
r"""
- Number line [-1.05, 1.05]: FG walls at +/-1.00139 "symmetric sector $J$"; blue walls at +/-0.872 "threefold sector $N$". Dots shuffle inside their walls.
- Bracket above: "upper jaw: thermal data of rings $\le12$". A `?` above 1: "is any eigenvalue near 1?"
""",
"Bounds are on |lambda| at beta = 49/4: v_J = 1.00139, v_N = 0.872.")

seg("""The lower jaw is one explicit trial state, a matrix product state with bond dimension 26 and integer entries.
On 72 sites, its energy per bond is certified below minus 1.401482, just above the true value near minus 1.401484.""",
r"""
- Ring of 24 small tensor circles (stand-in for 72) with thick `VIRTUAL` bonds labelled `M("D=26")`, "integer entries".
- Zoomed energy number line from -1.401485 to -1.401481 with three marks, left to right: `-1.401484039` "true $e_0$ (DMRG, literature)" (`DIM`); `-1.4014821126` "trial state, certified, $L=72$" (`VIRTUAL`); `-1.401482` (FG, unlabelled until s07). `GAP` brace "below by $1.1\times10^{-7}$".
""",
"Order must be e0 < e_MPS < -1.401482 (critic row 1). The trial is 1.9e-6 above e0; -a is 2.0e-6 above e0. The paper never quotes e0: label it literature.")

seg("""The constant added to H is exactly 1.401482 per site. With it, the trial state's energy is negative, so Z of 72
exceeds one at every temperature. Yet if every symmetric eigenvalue were at most 0.999,
the small-ring moments would force it below one.""",
r"""
- Arrow "zero of energy after the constant" onto the -1.401482 mark; `M(r"H_n\ \text{includes}\ +\tfrac{700741}{500000}\,n=+1.401482\,n")`.
- `M(r"E_0(72)<0\ \Longrightarrow\ Z_{72}(\beta)>1\ \text{ for every }\beta")`.
- Sentence 2: `M(r"\text{all }|\lambda_J|\le0.999\ \Longrightarrow\ Z_{72}(\tfrac{49}{4})<1\quad(\text{margin}>0.069)")` with an `SX`-red "contradiction" flash.
""",
"Paper (2.4), Lemma C.2, Prop. 5.5 (capped-mass margin > 0.0693). Sign: the paper ADDS 1.401482 per site to H; never say 'subtracts 1.401482'. This is the constant mentioned in ch08 s02.")

seg("""So one eigenvalue is pinched between 0.999 and 1.00139, and the twelfth-moment budget leaves no room for a second
symmetric one near one. The threefold ones are crushed: 0.872 to the 72nd power is about five in a hundred thousand.
The seed: a spatial defect certified below 0.048 at 36 sites.""",
r"""
- Vise on a number line [0.70, 1.01]: lower jaw (`VIRTUAL`, "trial state") slides in to 0.999; upper wall (FG, "filters") at 1.00139; a bright dot `\lambda_0` is squeezed between them.
- On "no room for a second": the other symmetric dots slide left and stay below a `DIM` dashed mark at 0.808, labelled `M(r"\big(m_J-0.999^{12}\big)^{1/12}\approx0.81")` "twelfth-moment budget, after removing $\lambda_0$".
- Sentence 2: threefold dots stay below 0.872; a shrinking bar `M(r"0.872^{72}\approx5\times10^{-5}")`.
- Sentence 3: seed tromino label `M(r"1-S(36,\tfrac{49}{4})\le p_0<0.047916")` on the `SPACE` segment; the blue DEFECT GAUGE reads 0.0479 (label "bound on $p$"), well below the dashed basin line at 0.127.
""",
"0.872 bounds only the threefold sector; the remaining symmetric eigenvalues are controlled by the twelfth-moment budget: removing lambda_0 leaves J-mass at most m_J - 0.999^12 = 0.0777, so every other J eigenvalue has modulus at most 0.808 (paper, proof of Prop. 5.5). Show 0.808 only with that label. p0 is an upper bound on the spatial defect. Data: `data/bootstrap_six_updates.csv` row j = 0.")

seg("""The thermal side is looser: Z of 72 is above one at doubled beta, but the wall caps it only near 1.1 at beta, so the thermal defect at 72 sites is bounded only by about 0.18.""",
r"""
- `M(r"T(72,\beta_0)=\frac{Z_{72}(2\beta_0)}{Z_{72}(\beta_0)^2}")` (`TIME`). Under the numerator: `M(r">1")` with a `VIRTUAL` "trial state" tag. Under the denominator: `M(r"Z_{72}(\beta_0)\le1.00139^{72}+\text{tail}\approx1.105")` with an FG "upper wall" tag.
- Result: `M(r"T(72,\beta_0)\ge\frac1{1.105^2}\approx0.82\quad\Rightarrow\quad 1-T(72,\tfrac{49}{4})\le q_0<0.181521")`. The seed tromino's `TIME` segment gets the label; the orange DEFECT GAUGE (label "bound on $q$") reads 0.1815 and pokes ABOVE the dashed basin line at 0.127 (pulse `DEFECT`).
""",
"Paper (proof of Prop. 5.5): q0 = 1 - (v_J^72 + R_A(72))^{-2}, using Z_72(2 b0) > 1 and Z_72(b0) <= v_J^72 + R_A(72); v_J^72 = 1.1052 (critic: 'the amplification v_J^72 is why q0 ~ 0.18'). The large q0 reflects the looseness of the upper wall raised to the 72nd power, not a large true thermal defect. Recomputed: 1 - 1.00139^-144 = 0.1813; with the tail, 0.181520.")

seg("""That is too big for the clean recursion, so the paper first runs the leapfrog six times, in exact arithmetic.
The spatial bound gets worse first, from 0.048 up to 0.071, as the loose thermal bound leaks into it.""",
r"""
- Left: the tromino climbs rows j = 1..3 on the log2 axes (n = 72, 144, 288; beta = 24.5, 49, 98).
- Right: plot from `data/bootstrap_six_updates.csv`: x = `j` (0..6), y = `p` (`SPACE` line + dots, legend "certified bound on $p$ (spatial, length $n$)") and `q` (`TIME` line + dots, legend "certified bound on $q$ (thermal, length $2n$)"), linear y in [0, 0.2], dashed line at 0.01 labelled "1\%". Points appear in sync: p = .0479, .0605, .0687, .0714 (each rise flashes "bound worse" in `DEFECT`); q = .1815, .1734, .1632, .1447.
""",
"q0 = 0.1815 > 1/6, so Prop. 4.3 cannot start here; Lemma 4.2 needs no smallness. Every number in this table is an upper bound, rounded up to a multiple of 1e-7 (paper's rounded update table), not a value of 1-S or 1-T. The early rise of p is an artifact of worst-case bounds, not physics: never label it as the defect itself getting worse.")

seg("""Then both bounds collapse. At beta 784, the spatial defect at two thousand three hundred and four sites is below 0.0085, and the thermal one, on the doubled ring, below 0.0055: under one percent, the one in a hundred we started from. So every even ring from there on has a gap above log 20 over 784.""",
r"""
- Rows j = 4..6: p = .0633, .0376, .0085; q = .1055, .0446, .0055 (same "certified bound" legends). The tromino reaches (2304, 784)-(4608, 784)-(4608, 1568); its `SPACE` segment is labelled `M(r"1-S(2304,784)\le0.0084513")`, its `TIME` segment `M(r"1-T(4608,784)\le0.0054986")`. Both gauges drop under the 1% line and turn `GAP`.
- Callback: the ch06 s12 column returns with its first row now labelled `(n_0,\beta_0)=(2304,\,784)`, and the ch07 straight line gets real tick values 784, 1568, 3136, ...
- Theorem line, `GAP` box: `M(r"\gamma_L>\frac{\log20}{784}\approx3.82\times10^{-3}\quad\text{for every even }L\ge2304")`. A small arrow back to the ch03 claim card: "this is where it comes from".
""",
"Final row: 1 - S(2304, 784) <= 0.0084513 and 1 - T(4608, 784) <= 0.0054986. Then Prop. 4.3 with n0 = 2304, b0 = 784, u0 = 1/100, C = 5, r = 1/20 (r and C are never named on screen; the input line shows only (n0, b0) and 'both defects < 1/100').")

seg("""A second seed, from rings of six to ten sites and the trial state on 120 sites, starts with bounds of one
eighth, barely inside the basin: a weaker floor of 0.000479, but for every even ring from 60 sites on.""",
r"""
- Staircase: a second tromino at (60, 26.25)-(120, 26.25)-(120, 52.5), `DIM`-outlined `DEFECT`.
- Small cobweb inset: start u0 = 0.125 just left of the 0.127 edge, creeping down slowly (`data/bootstrap_dyadic.csv`, rows `row == "n0=60"`: 0.125, 0.1234, 0.1204, 0.1145, 0.1035, 0.0846, 0.0566, 0.0253).
- Theorem line: `M(r"\text{unique ground state and }\ \gamma_L>\tfrac4{105}\log\tfrac{80}{79}\approx4.79\times10^{-4}\quad\text{for every even }L\ge60")`.
""",
"Prop. 5.4: thermal data at beta = 21/2 for n = 6, 8, 10 with twists 1, P, C; a Hoelder step raises beta to 105/4; S(60) > 0.8756 and T(120) > 0.8760, both above 7/8, i.e. defect bounds below 1/8. u* - 1/8 is only 1.8% of u*. The floor (4/105) log(80/79) = 4.7919e-4 is below 0.00048: never round it up on screen or in speech.")

seg("""Two readings of ours, not the paper's: the 0.872 wall caps the correlation length here near seven sites, against a true value near six, and the trial state's bonds carry only half-integer spins: valence-bond physics, smuggled in through an energy bound.""",
r"""
- READING TAG "physicist's reading -- not in the paper".
- Left: eigenvalue line zoom [0.8, 0.9]: blue wall at 0.872 "certified"; `DIM` tick at 0.847 `M(r"e^{-1/\xi},\ \xi\approx6")` "(literature)"; caption `M(r"\Rightarrow\ \xi(T)\lesssim7\ \text{sites}")`.
- Right: the `VIRTUAL` bond of the trial state opens into stacked blocks: four blocks "$j=\tfrac12$" (dim 2), three "$j=\tfrac32$" (dim 4), one "$j=\tfrac52$" (dim 6); `M(r"26=4\cdot2+3\cdot4+1\cdot6")`; weights "97\% / 3\% / $\sim$0.001\%". The ch03 valence-bond cartoon fades in faintly behind.
""",
"Both are interpretations (critic 2b): the paper never says SU(2), virtual spin or correlation length for these objects; N sector <-> spin correlations and xi(T) <= ~7.35 are our reading. The proof uses only the energy number.")

# =====================================================================
chapter("ch09", "The edges remember",
        "The boundary companion: why open chains need end fields, Tasaki's conditional theorem, what is proved "
        "(h = 3/5), the exact scope of the index statement, and where the sign comes from. Close the theta loop "
        "as a flagged reading.")

seg("""Now cut the ring open. In the valence-bond picture, each end carries a free spin one-half, giving four nearly
degenerate states: an open chain has no uniform gap, for a boring reason.""",
r"""
- `spin_ring(11)` opens (one bond dissolves) and straightens into `spin_chain(11)`; the ch03 valence-bond cartoon overlays it and the two dangling `VIRTUAL` end dots glow and grow small arrows.
- Level diagram to the right: four lines bunched near 0 (triplet + singlet) and a `GAP`-separated band above. As the odd chain lengthens, the bunch splitting shrinks: labels 0.213, 0.142, 0.097 for 9, 11, 13 sites (ED, h = 0). Caption "no uniform gap".
""",
"Edge spins: valence-bond (AKLT) picture; seen numerically by White-Huse. ED splittings from the nlsm digest (odd chains: triplet ground state, singlet above).")

seg("""Tasaki's fix: an odd chain, with the same field on both end spins. The edge spins align, the ground state is
unique, and his theorem turns a uniform gap into a topological index of minus one: a nontrivial S-P-T phase.""",
r"""
- `spin_chain(11)` with sites labelled -L..L; small FG field arrows `h` on the two end sites, both pointing up. `M(r"H_L(h)=\sum_{j=-L}^{L-1}\mathbf S_j\cdot\mathbf S_{j+1}-h\,\big(S^z_{-L}+S^z_{L}\big)")` and `M(r"S^z_{\rm tot}=1")`. The four levels split into one ground level and a gap.
- Implication card: dashed box "uniform gap (Assumption 2)" $\Longrightarrow$ "Ind $=-1$ (Theorem 3)", labelled "Tasaki 2024/25"; the left box shows `?`.
""",
"Uniqueness holds for every h > 0 (Tasaki Lemma 1); the field is not 'small'. Never show 0.41 as this model's gap: its true L -> infinity gap is unknown.")

seg("""The companion manuscript claims that gap for an end field of three fifths: above log 10 over 392, about
0.00587, on every such chain of at least one thousand nine hundred and twenty-one sites. It reuses the operator X,
with the end fields as boundary states, and a second bootstrap.""",
r"""
- The dashed box fills `GAP`: `M(r"h=\tfrac35:\quad E_1-E_0>\frac{\log10}{392}\approx5.87\times10^{-3}\qquad L\ge960\ \ (2L+1\ge1921\ \text{sites})")`, header "claimed theorem (boundary manuscript, Thm.~1.1)".
- Sentence 2: the torus loses its left/right identification (chevrons fade) and becomes a cylinder open in space; `VIRTUAL` caps `\langle v_\beta|` and `|v_\beta\rangle` at its ends. Two labelled formulas, X in `SPACE`: `M(r"\text{same fields (the theorem's chain):}\quad \langle v_\beta,\,X_\beta^{\,n}\,U_P\,v_\beta\rangle")` in FG, and below it, smaller and `DIM`, `M(r"\text{opposite fields:}\quad \langle v_\beta,\,X_\beta^{\,n}\,v_\beta\rangle")`.
""",
"E0 <= E1 counted with multiplicity, so the theorem includes uniqueness. Per BND Prop. 2.1, <v, X^n v> is the OPPOSITE-field chain (used in the initialization) and the same-field chain of the theorem is <v, X^n U_P v>, P = diag(1,-1,-1): an identity between transfer representations, not a unitary equivalence of Hamiltonians. log 10/392 = 5.874e-3: say 'about 0.00587' (0.0059 would round a lower bound up). Do not compare this gap with 0.41.")

seg("""So every infinite-chain limit selected by these end fields, along any subsequence of lengths, has index
minus one. Convergence of the whole sequence, and uniqueness of the infinite-volume ground state, are not
claimed.""",
r"""
- Card (`GAP`): `T(r"every boundary-selected subsequential limit: $\mathrm{Ind}=-1$")`. Below in `DIM`: `T(r"not claimed: convergence of the full sequence $\cdot$ uniqueness of the infinite-volume ground state")`.
""",
"BND Cor. 7.1 and the paragraph after it.")

seg("""Where does the sign come from? The selected ground state has total spin along z equal to one, so a pi
rotation about z gives minus one. Deform that rotation into a gentle, local twist in the bulk: reflection keeps its
expectation real, and the gap keeps it from crossing zero.""",
r"""
- `M(r"e^{-i\pi S^z_{\rm tot}}=e^{-i\pi}=-1")`; a dial (unit circle) with its needle at -1.
- Sentence 2: plot of rotation angle theta_j vs site j: first flat at pi (uniform rotation), then morph into Tasaki's ramp: 0 on the far left, rising linearly through pi at the centre to 2 pi on the far right (window |j| <= pi/epsilon), getting gentler. `M(r"U_\varepsilon=\exp\Big[-i\!\!\sum_{|j|\le\pi/\varepsilon}\!(\pi+\varepsilon j)\,S^z_j\Big]")`.
- The dial needle is confined to the real axis and stays left of a shaded forbidden band around 0; `M(r"\mathrm{Ind}=\lim_{\varepsilon\downarrow0}\omega(U_\varepsilon)=-1", color=GAP)`.
""",
"Mechanism per BND topology section: -1 <= omega_L(U_eps) <= -sqrt(1 - 4(pi+eps)eps/gamma*). TWIST RULE: this 'gentle local twist' is the only twist that carries topology; keep its ramp visual distinct from the ch03 spiral and the ch08 seam.")

seg("""A physicist's reading, in neither paper: theta equals two pi is invisible in the bulk, but at an edge it leaves
the Berry phase of a free spin one-half, and the index is a rigorous fingerprint of that.""",
r"""
- READING TAG "physicist's reading -- in neither paper".
- Call back the ch02 phasor/theta dial: `M(r"\theta=2\pi")` with the bulk label "invisible"; at the chain's end a `VIRTUAL` arrow labelled `M(r"\tfrac12")`.
""",
"Interpretation (Ind = (-1)^S = e^{i theta/2}); neither manuscript mentions a theta term or sigma model.")

# =====================================================================
chapter("ch10", "What it means",
        "Exact scope (claimed vs not), why the bound is small, what is new, explanation vs certification, the "
        "status and the computer's role (second and last status mention), the AI angle, and a closing callback: a "
        "floor under the opening plot.")

seg("""So what is claimed? A uniform gap for the spin one Heisenberg chain on even rings from 60 sites on; and for
long odd open chains with end fields of three fifths, a uniform gap, and index minus one for every limit they select.""",
r"""
- Two-column card; this segment fills the left column, "Claimed" (`GAP` checks):
  - "even periodic rings, $L\ge60$: uniform gap ($>4.79\times10^{-4}$; $>3.82\times10^{-3}$ for $L\ge2304$)", with a `DIM` sub-line "unique ground state: classical";
  - "odd open chains, $h=\tfrac35$, $\ge1921$ sites: gap $>5.87\times10^{-3}$; index $-1$ for every boundary-selected subsequential limit".
""",
"Even rings only; boundary index statement is subsequential and concerns the boundary-selected infinite-chain limits, not the finite open chains. Printed bounds must not exceed the proved constants: 4.7919e-4, 3.8211e-3, 5.8739e-3.")

seg("""Not claimed: the gap's value, odd periodic rings, uniqueness of the infinite-volume state, or spin two and beyond, where we suspect a correlation length near 50 sites puts seeds out of reach.""",
r"""
- Right column, "Not claimed" (`DIM` circles), one item per clause: "the value of the gap ($\sim$100x below 0.41)"; "odd periodic rings"; "unique infinite-volume ground state"; "spin $\ge2$" with a `DIM` aside "$\xi\approx49.5$ at $S=2$ (literature)" and the tag "difficulty: our guess".
""",
"Spin-2 values: Delta = 0.08917, xi = 49.49 (Todo-Kato, literature). The paper says nothing about S >= 2; the 'out of reach' remark is our guess and must carry its tag.")

seg("""Why is the bound a hundred times too small? Doubling preserves the rate the seed certifies, but never improves it: a certified one percent at beta 784, where a rough free-magnon estimate puts the true defect near e to the minus
300.""",
r"""
- Two numbers side by side at beta = 784: `T(r"certified: $u<10^{-2}$")` (`GAP`) vs `T(r"free-magnon estimate: $u\sim e^{-300}$")` (`DIM`, tag "heuristic").
- `M(r"\frac{-\log u_j}{\beta_j}\ \text{ is invariant under doubling}")`.
""",
"Free-boson estimates at (2304, 784): about e^-376 (spatial) and e^-317 (thermal) (physics_intuition 1.3). Heuristic; keep the tag.")

seg("""What's new is a tool: a finite-size gap criterion that does not need frustration-freeness, which the paper
offers as reusable for other models with the same two readings.""",
r"""
- Box: `T(r"two nonnegative readings of $Z$ $+$ a certified seed in the basin $\Rightarrow$ uniform gap")` with tag "frustration-free not required". Icons: two-knives torus, staircase.
""",
"Paper: Prop. 4.3 is 'a reusable criterion ... positivity of the spatial transfer is not required'. Do not claim such representations exist for other spins.")

seg("""And it is not an explanation. The analytic part never mentions spin; spin one enters only through the numbers
in the seed. So it claims to certify that spin one is gapped, never why; the theta term is still the explanation.""",
r"""
- Split screen: left, the staircase labelled "certifies that", with `DIM` line "spin enters only through the seed"; right, the ch02 theta phasors labelled "explains why".
""",
"The integer/half-integer distinction appears nowhere in the analytic argument; it enters only through the construction of X (spin one) and the certified seed numbers.")

seg("""A physicist's reading, not the paper's: doubling L and beta together is a change of scale, so the leapfrog is a
renormalization flow for the two defects. At a critical point they never flow. In a massive phase they flow to zero,
and the basin is that phase's domain of attraction. The seed certifies that by 72 sites, about a dozen correlation
lengths, spin one is already inside. That is also why spin two, with a correlation length near 50 sites, is out of
reach.""",
r"""
- Tag "physicist's reading -- not in the paper" and "schematic". Axes: x "scale: $L$ and $\beta$ doubled together" (log scale, ticks 6, 72, 2304), y "defect".
- Sentence 2: `HALF` flat line near 0.55, label "spin $\tfrac12$: critical, never flows".
- Sentence 3: `GAP` band under 0.127 labelled "basin"; `INTEGER` curve falling into it and plunging to zero, label "spin 1".
- Sentence 4: a dot on the spin-1 curve at $L=72$, label "certified seed"; `INTEGER` tick "$\xi\approx6$".
- Sentence 5: dashed `DIM` spin-2 curve that reaches the basin only far to the right, tick "$\xi\approx50$".
""",
"Reading only: the paper never speaks of RG. Curves are schematic; the only hard numbers are 0.127 (basin edge), 72 (trial state), xi ~ 6 and ~ 50 (literature), 0.55 (our spin-1/2 CFT estimate, ch07 s08). The seed defects (< 0.048 at L = 36-72) are inside the basin.")

seg("""On status: this is OpenAI's claimed proof, a preprint released on October 6, 2026, not yet independently refereed. The analytic argument is short enough to check by hand; the computer only proves finitely many inequalities, about thermal traces of rings and chains of at most twelve sites, and a few integer trial states.""",
r"""
- STATUS CARD reprise (same layout as ch01 s07).
- Then the pipeline, two rows. Ring theorem: box "27 certified thermal traces (rings $\le12$)" + box "one integer trial tensor ($L=72,\,120$)" -> arrow "finite inequalities" -> box "analytic bootstrap (a few pages)" -> `GAP` box "every even $L\ge60$". Boundary theorem (second row, same style): box "15 thermal traces (open chains, 2 to 6 sites)" + box "same bulk tensor, new end vectors ($m=34,78,142,240$)" -> "finite inequalities" -> "second bootstrap" -> `GAP` box "odd chains $\ge1921$ sites, $h=\tfrac35$".
""",
"Only the allowed status facts. No reactions, letters, other releases or verification claims beyond these. Boundary certificates: BND thermal section (fifteen traces, matrices of order at most 3^6 = 729) and BND trials (E_0^opp(m) + am < alpha for m in {34, 78, 142, 240}, same bulk matrices, new endpoint vectors).")

seg("""Those computations are published with the paper, about forty minutes of processor time. For this video we
re-ran them on a laptop, in about twenty minutes, and every certified number matched.""",
r"""
- Monospace terminal-style box (no brand UI): lines "thermal  $\beta$=49/4  18 traces  PASS", "thermal  $\beta$=21/2  9 traces  PASS", "trial state  L=72  PASS", "trial state  L=120  PASS", "boundary thermal  15 traces  PASS", "boundary trials  m=34,78,142,240  PASS", "~20 min wall clock, laptop". Stats beside: "~40 CPU-min", "largest block 73,789".
""",
"certified_numerics: all 27 thermal integers and both trial contractions bit-identical; the boundary paper's 15 thermal traces were also replayed (15/15, critic) and its four trial certificates passed with byte-identical output (boundary digest). No machine names.")

seg("""As for the AI: the manuscripts are credited to OpenAI, with no human author named. For a skeptic, what matters
is that the argument is checkable, and its central idea fits in your head.""",
r"""
- Plain text "author: OpenAI" fades to `DIM`; the two-knives torus fades in behind it.
""",
"Second and last mention of the AI angle.")

seg("""One torus. A horizontal knife gives Gibbs weights; a vertical knife gives spatial weights. Squaring one doubles
beta, squaring the other doubles L, and an exact identity lets each pay for the other's doubling.""",
r"""
- Full recap on the TORUS + TWO KNIVES motif: orange knife sweeps and orange bars square; blue knife sweeps and blue bars square; the four-tori tiling with weights flashes; the two coins swap ("each pays for the other").
""")

seg("""Small rings and one good trial state put the pair inside the basin, and the staircase climbs from there to
infinite length. Under the curve we started with, there is now a claimed floor. Low, but a floor, and it never
moves.""",
r"""
- The staircase tromino climbs and exits the top-right.
- Zoom out to the ch01 GAPPLOT (identical object). On the main axes, a thin `GAP` line at y = 0.000479 from x = 0 to x = 1/60 (it hugs the axis, true height), with a short step at y = 0.0038 for x <= 1/2304.
- Magnifier inset (log-log): x = L from 4 to 1e5 (log), y = gap from 1e-4 to 1 (log). Spin-1 ED squares (L = 4..16), dashed literature line 0.4105, and the `GAP` floor as a step function: nothing for L < 60, 4.79e-4 for 60 <= L < 2304, 3.82e-3 for L >= 2304. Labels "$\frac{4}{105}\log\frac{80}{79}$, even $L\ge60$" and "$\frac{\log20}{784}$, even $L\ge2304$". Small `DIM` "claimed".
- Hold 3 s, fade to BG.
""",
"Never draw a proved floor under the L <= 16 ED points or for L < 60. Floors hold for even L only. Draw at true height; the inset makes it visible.")


# =====================================================================
BAD_WORDS = ["spin-1", "spin-one-half", "O(3)", "AKLT", "DMRG", "MPS", "SPT", "Nachtergaele",
             "revolutionary", "mind-blowing", "3/5", "1/2"]  # excluded status topics are checked separately


def spoken_check(t):
    bad = []
    if re.search(r"[()/\\$\[\]{}=<>+*^_%&#@|~]", t):
        bad.append("symbol:" + "".join(sorted(set(re.findall(r"[()/\\$\[\]{}=<>+*^_%&#@|~]", t)))))
    for m in re.finditer(r"\d[\d,]*(?:\.\d+)?", t):
        s = m.group(0).rstrip(",")
        if "." in s:
            continue
        v = int(s.replace(",", ""))
        if v >= 1000 and not (1900 <= v <= 2100):
            bad.append("bigint:" + s)
    for w in BAD_WORDS:
        if re.search(r"(?<![A-Za-z])" + re.escape(w.lower()) + r"(?![a-z])", t.lower()):
            bad.append("word:" + w)
    n_sent = len(re.findall(r"[.?!](?:\s|$)", t))
    if n_sent > 4:
        bad.append("sentences:%d" % n_sent)
    return bad


GLOBAL = r"""
## Global conventions (read once; they apply to every chapter)

### Palette (`scenes/common.py`) and semantics
- `SPACE` #4FC3F7: spatial direction, vertical knife, spatial transfer X, spatial purity S, spatial defect p.
- `TIME` #FFA94D: imaginary time, horizontal knife, Gibbs weights, thermal purity T, thermal defect q.
- `DEFECT` #FFE066: defects u, p, q (gauge fills, highlighted numbers), the basin-edge line.
- `GAP` #69DB7C: gaps, gap braces, theorem boxes, check marks.
- `HALF` #F06595: spin one-half, half-integer spin. `INTEGER` #74C0FC: spin one, integer spin.
- `SX`/`SY`/`SZ` (red/green/blue): x/y/z event labels. `VIRTUAL` #B197FC: virtual spin-1/2s, valence bonds, MPS bonds, edge spins, boundary vectors.
- `FG`, `DIM`, `FAINT`: neutrals.

**Colour-clash rule (SPACE and INTEGER are nearly the same blue).**
1. Every spin-one DATA series is drawn with hollow square markers (`Square(side_length=0.13)`, stroke `INTEGER`, width 3) and carries a text label "spin 1"; spin one-half series use filled `HALF` dots labelled "spin 1/2".
2. Never put a spatial-purity object and a spin-one series in one panel distinguished by colour alone; spatial-purity objects always carry S, p or "spatial" in text.
3. Rings that only illustrate the method (ch04-ch06, ch08 s01) are drawn in FG; `INTEGER`/`HALF` rings appear only where the spin value is the point (ch01-ch03, ch07 s05, ch09).

**The letter S** means both spin and spatial purity. On screen, spatial purity is always written with arguments, `S(n,\beta)`, in `SPACE`; spin is written "spin 1" or S in FG.

### Recurring motifs (build each once in a new shared module, e.g. `scenes/motifs.py`; callbacks must look identical)
1. **GAPPLOT** (ch01 s02-s05, ch10 s11). `Axes(x_range=[0,0.27,0.05], y_range=[0,1.05,0.2], x_length=8, y_length=4.6)`; x label `M(r"1/L")`, y label `M(r"\gamma_L=E_1-E_0")`. Data `data/gaps.csv`: spin 1/2 rows (L = 4..24) as `HALF` dots, spin 1 rows (L = 4..16) as hollow `INTEGER` squares, x = 1/`L`, y = `gap_first_excitation`. Dashed `HALF` guide y = 4.385 x to the origin; dashed `INTEGER` segment at y = 0.4105 from x = 0 to 1/16, labelled `DIM` "0.4105 - DMRG, White-Huse 1993 - literature".
2. **TORUS + TWO KNIVES** (ch01 s08, ch04 onward, ch10). `torus_rect(width=5, height=3)`; L along the bottom (`SPACE`), beta up the left (`TIME`). Horizontal knife: an orange (`TIME`) `Line` across the full width, stroke 6, small triangular handle at its left end; it sweeps upward (thermal reading). Vertical knife: a blue (`SPACE`) `Line` across the full height with a handle at the top; it sweeps rightward (spatial reading) and always cuts THROUGH A BOND, midway between two site world lines (the states of X are bond histories). Identification chevrons take the colour of the periodic direction: top/bottom chevrons `TIME` ("time is periodic: trace"), left/right chevrons `SPACE` ("space is periodic: ring"); `torus_rect` draws them the other way round, so recolour after construction (submobjects 2-3 -> `TIME`, 4-5 -> `SPACE`). From ch05 a thumbnail (scale 0.35) sits top-left; its width or height visibly doubles whenever L or beta doubles.
3. **WEIGHT BARS**: `weight_bars(...)`; squaring is always animated in two steps: Transform each bar to height proportional to p^2, then rescale the group so it sums to 1 again. Tallest bar uses `highlight_color` `TIME` or `SPACE`; the defect is a `DEFECT` brace over the small bars.
4. **DEFECT GAUGES**: two vertical gauges (height 2.6), blue "p (spatial)" and orange "q (thermal)". Fill height = log10(defect) mapped [-3, 0] -> [0, 1], so FULL = large defect (impure) and EMPTY = pure; this semantics holds everywhere in the film (never fill a gauge with purity). A `DecimalNumber` under each; dashed `DEFECT` line at 0.127 "basin edge". From ch08 s08 on, the gauges show certified UPPER BOUNDS and are labelled "bound on p", "bound on q".
5. **STAIRCASE**: `lb_plane` (x = log2 L, `SPACE`; y = log2 beta, `TIME`). The tracked pair is an L-shaped tromino: a `SPACE` segment (n, beta) -> (2n, beta) standing for S(n, beta), and a `TIME` segment (2n, beta) -> (2n, 2beta) standing for T(2n, beta). Each full update translates it by (+1, +1). Interpolation bars as in the paper's Fig. 1.
6. **OBJECTION BUBBLES**: six small rounded speech bubbles, `DIM` outline, font 26: (a) "every finite chain has a gap", (b) "doesn't the $\theta$-term already explain it?", (c) "why even $L$?", (d) "why not just double $\beta$?", (e) "isn't this just numerics?", (f) "why doesn't it prove spin $\tfrac12$ gapped?". Bubble (a) first appears alone in ch01 s04; all six appear together in ch01 s06. Later, when the narration raises/answers one, that bubble alone fades in at the top-right (scale 0.6), gets `Indicate`, then a small `GAP` check, then fades: (a) ch01 s04, ch03 s08, ch05 s07; (b) ch02 s06 (answered again ch10 s05); (c) ch04 s13 -> s14; (d) ch05 s07 -> ch06 s01; (e) ch08 s02 (again ch10 s07); (f) ch07 s05 -> s08.
7. **TAGS**: a small `DIM` rounded box with italic text in a top corner, on screen for the whole segment whenever the narration offers material that is not in the papers: "physicist's reading -- not in the paper", "our calculation -- not in the paper", "heuristic", "analogy". Literature values carry a small `DIM` "literature" label next to the number.
8. **STATUS CARD** (ch01 s07, ch10 s07): plain text only (see ch01 s07).

### Three different "twists": keep them visually and verbally distinct
- ch03 s02, the Lieb-Schultz-Mattis **slow spiral**: every arrow of a ring rotated progressively (a helix). Variational state. Never reuse.
- ch08 s03, the **seam**: a symmetry rotation inserted at ONE bond of a periodic ring (twisted boundary condition), glyph = small circular arrow labelled P. In the spatial reading it is an operator U_g inside the trace; it sorts eigenvalues into sectors. No topology.
- ch09 s05, Tasaki's **gentle local twist**: a ramp of rotation angles (0 -> pi -> 2 pi) on the open chain. The only one that carries topology.

### Accuracy rules for everything on screen
- Status: only the allowed facts (claimed proof; manuscripts dated 24 Sep 2026; preprint released 6 Oct 2026; not yet independently refereed; analytic argument short enough to check by hand; finite computations published with the paper, re-run and reproduced for this video). Nothing else about verification status; no reactions, letters, other releases, logos or repository screenshots.
- Periodic theorem: EVEN rings only; unique ground state and gamma_L > (4/105) log(80/79) ~ 4.79e-4 for even L >= 60; gamma_L > log 20/784 ~ 3.82e-3 for even L >= 2304. Uniqueness on even rings is classical (Marshall-Lieb-Mattis); the new content is the uniform gap.
- Boundary theorem: odd open chain of 2L+1 sites, field h = 3/5 on both end spins; gap > log 10/392 ~ 5.87e-3 for L >= 960 (>= 1921 sites); index -1 for every boundary-selected SUBSEQUENTIAL limit; full-sequence convergence and infinite-volume uniqueness not claimed. Never compare this gap with 0.41.
- Never round a proved lower bound up: 4.79e-4 (not 4.8e-4 or 0.00048 after 'exceeds'), 3.82e-3, 5.87e-3 (not 5.9e-3).
- Spoken symbols: the letter u is never spoken (TTS says 'you'); the narration says 'the defect'. The torus aspect ratio is rho on screen. Never introduce r (or C) for the contraction rate; write the number (1/20) instead.
- Literature values, labelled "literature": 0.41050(2), e0 = -1.401484039, xi ~ 6, v ~ 2.49, spin-2 values (Delta 0.08917, xi 49.5).
- Energy number line order: e0 (-1.401484039) < trial (-1.4014821126) < -1.401482.
- X is a spatial transfer operator "in the spirit of" Suzuki's quantum transfer matrix; never "a QTM". Never imply a spin-1/2 spatial transfer operator exists.
- Do not invent reasons for the paper's design constants (beta0 = 49/4 and 21/2, seeds 36 and 60, D = 26, h = 3/5, the filter polynomials).
- Do not say the periodic paper's symmetry group has 12 elements.
- Numbers to keep exactly (all are certified UPPER BOUNDS on defects, never the defects themselves; label plots and gauges "certified bound"): p0 < 0.047916 at (36, 49/4); q0 < 0.181521 at (72, 49/4); six-update rows p = .0604996, .0686606, .0713616, .0632939, .0375793, .0084513 and q = .1733812, .1632381, .1447092, .1055161, .0445941, .0054986; walls 1.00139 and 0.872; pinch window (0.999, 1.00139); ratios 107x and 857x.

### Data
All CSVs are in `haldane-gap/data/`; column names are quoted exactly. Never invent data; schematic objects are marked "schematic".

### Timing
`with self.voice("sNN", breath=...)`: segments marked PAUSE use the breath given in their NOTE.
"""


def main():
    narr = {"voice": "af_heart", "speed": 1.0, "chapters": []}
    md = []
    total = 0
    problems = 0
    summary = []
    for c in CH:
        segs = []
        md.append("---")
        md.append("")
        md.append("## %s: %s" % (c["id"], c["title"]))
        md.append("")
        cw = sum(len(s["text"].split()) for s in c["segments"])
        md.append("**Purpose.** " + c["purpose"] + "  *(%d words, about %.1f min)*" % (cw, cw / 165))
        md.append("")
        for s in c["segments"]:
            js = {"id": s["id"], "text": s["text"]}
            if "say" in s:
                js["say"] = s["say"]
            segs.append(js)
            w = len(s["text"].split())
            for field in ("text", "say"):
                if field in s:
                    bad = spoken_check(s[field])
                    if bad:
                        problems += 1
                        print("CHECK", c["id"], s["id"], field, bad, file=sys.stderr)
            md.append("### %s.%s  (%d words, ~%.0f s)" % (c["id"], s["id"], w, w / 165 * 60))
            md.append("")
            md.append("> " + s["text"])
            md.append("")
            if "say" in s:
                md.append("TTS `say` override: " + s["say"])
                md.append("")
            md.append("VISUAL:")
            md.append(s["visual"])
            md.append("")
            if s["note"]:
                md.append("NOTE: " + s["note"])
                md.append("")
            if s["pause"]:
                md.append("PAUSE: `breath=%.1f`" % s["pause"])
                md.append("")
        total += cw
        summary.append((c["id"], c["title"], cw, len(c["segments"])))
        narr["chapters"].append({"id": c["id"], "title": c["title"], "segments": segs})
    head = ["# Storyboard: \"The Haldane gap, proved?\" (final synthesis)", "",
            "Narration voice `af_heart`, speed 1.0. Total narration: %d words (about %.1f min at 165 wpm), %d chapters." % (total, total / 165, len(CH)),
            "",
            "Source of truth for wording and segment ids: `script/narration.json`. Every narration line below is copied verbatim from it.",
            "",
            "Chapter word counts: " + "; ".join("%s %d" % (a, w) for a, _, w, _ in summary) + "."]
    out_md = "\n".join(head) + "\n" + GLOBAL + "\n" + "\n".join(md) + "\n"
    for c, t, w, n in summary:
        print("%s  %-48s %4d words  %2d segs  %.1f min" % (c, t, w, n, w / 165))
    print("TOTAL", total, "words", "%.1f min" % (total / 165), "problems:", problems)
    if "--write" in sys.argv:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "narration.json").write_text(json.dumps(narr, indent=1, ensure_ascii=False) + "\n")
        (OUT / "storyboard.md").write_text(out_md)
        print("wrote", OUT / "narration.json", "and", OUT / "storyboard.md")


if __name__ == "__main__":
    main()
