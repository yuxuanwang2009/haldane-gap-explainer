"""Shared style and narration sync for the Haldane-gap explainer.

Every chapter scene subclasses NarratedScene and sets CHAPTER = "chNN".
Narration is played with

    with self.voice("s03") as d:      # d = clip duration in seconds
        self.play(Create(x), run_time=0.4 * d)
        self.play(Write(y), run_time=0.3 * d)

The block lasts at least the clip duration plus a short breath; if the
animations inside run longer, the next clip simply starts later.
Segment start times are logged to output/timelines/<CHAPTER>.json so the
build script can write subtitles.
"""
import json
from contextlib import contextmanager
from pathlib import Path

from manim import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "audio"
DATA = ROOT / "data"
TIMELINES = ROOT / "output" / "timelines"

# ---------------------------------------------------------------- palette
BG = "#0E0E10"
FG = "#ECECEC"
DIM = "#8A8A8F"
FAINT = "#3A3A40"

SPACE = "#4FC3F7"      # spatial direction, spatial transfer, spatial purity S
TIME = "#FFA94D"       # imaginary time / thermal direction, thermal purity T
DEFECT = "#FFE066"     # purity defects u, p, q
GAP = "#69DB7C"        # the gap, "proved" results
HALF = "#F06595"       # half-integer spin / gapless side
INTEGER = "#74C0FC"    # integer spin / gapped side
SX, SY, SZ = "#FF6B6B", "#51CF66", "#5C7CFA"   # x, y, z labels of G_alpha events
VIRTUAL = "#B197FC"    # virtual spin-1/2s, MPS bonds, edge spins

config.background_color = BG

TEX_TEMPLATE = TexTemplate()
TEX_TEMPLATE.add_to_preamble(r"\usepackage{amsmath,amssymb,bm,dsfont}")


def T(s, **kw):
    """Text in LaTeX roman (Computer Modern), the 3b1b look."""
    kw.setdefault("color", FG)
    return Tex(s, tex_template=TEX_TEMPLATE, **kw)


def M(s, **kw):
    """Display math."""
    kw.setdefault("color", FG)
    return MathTex(s, tex_template=TEX_TEMPLATE, **kw)


def title_card(text, sub=None):
    t = T(text, font_size=56)
    g = VGroup(t)
    if sub:
        s = T(sub, font_size=32, color=DIM).next_to(t, DOWN, buff=0.35)
        g.add(s)
    return g.move_to(ORIGIN)


def caption(text, **kw):
    """Small explanatory line pinned near the bottom edge."""
    kw.setdefault("font_size", 30)
    kw.setdefault("color", DIM)
    return T(text, **kw).to_edge(DOWN, buff=0.45)


class NarratedScene(Scene):
    CHAPTER = None
    BREATH = 0.35   # pause after each clip

    def setup(self):
        dur = json.loads((AUDIO / "durations.json").read_text())
        self._durations = dur.get(self.CHAPTER, {})
        self._timeline = []

    def clip(self, seg_id):
        return self._durations[seg_id]

    @contextmanager
    def voice(self, seg_id, breath=None):
        breath = self.BREATH if breath is None else breath
        d = self._durations[seg_id]
        wav = AUDIO / self.CHAPTER / f"{seg_id}.wav"
        t0 = self.renderer.time
        self.add_sound(str(wav))
        self._timeline.append({"id": seg_id, "start": round(t0, 3), "dur": d})
        yield d
        elapsed = self.renderer.time - t0
        if elapsed < d + breath:
            self.wait(d + breath - elapsed)

    def tear_down(self):
        TIMELINES.mkdir(parents=True, exist_ok=True)
        (TIMELINES / f"{self.CHAPTER}.json").write_text(
            json.dumps({"segments": self._timeline,
                        "total": round(self.renderer.time, 3)}, indent=1))
        super().tear_down()
