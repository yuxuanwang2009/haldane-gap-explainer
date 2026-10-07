"""Render chapters and assemble the final video.

    python tools/build.py render ch03 [--draft]
    python tools/build.py render all [--draft]
    python tools/build.py assemble [--draft]
    python tools/build.py frames ch03 [--every 4]

(run with the manim environment's python; see README).

Chapter files are scenes/chNN_*.py, each defining class ChNN(NarratedScene).
Render caches live in MEDIA; finished chapter videos are
copied to output/chapters/.  --draft renders 480p15 for fast checks.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENES = ROOT / "scenes"
OUT = ROOT / "output"
# manim's render cache; override with HALDANE_MEDIA to keep it off synced folders
MEDIA = Path(os.environ.get("HALDANE_MEDIA", ROOT / "media"))
PY = Path(sys.executable)   # run this script with the manim environment's python


def chapter_files():
    return sorted(SCENES.glob("ch[0-9][0-9]_*.py"))


def find(ch):
    hits = [f for f in chapter_files() if f.name.startswith(ch + "_")]
    if not hits:
        sys.exit(f"no scene file for {ch}")
    return hits[0]


def render(ch, draft):
    f = find(ch)
    cls = ch.capitalize()
    q = ["-ql"] if draft else ["-qh", "--frame_rate", "30"]
    cmd = [str(PY), "-m", "manim", *q, "--media_dir", str(MEDIA), "--disable_caching",
           str(f), cls]
    print(" ".join(cmd))
    r = subprocess.run(cmd, cwd=SCENES)
    if r.returncode:
        sys.exit(r.returncode)
    sub = "480p15" if draft else "1080p30"
    vid = MEDIA / "videos" / f.stem / sub / f"{cls}.mp4"
    dest = OUT / ("chapters_draft" if draft else "chapters")
    dest.mkdir(parents=True, exist_ok=True)
    # pad audio to the video length so concatenated chapters cannot drift
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vid), "-af", "apad",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", str(dest / f"{ch}.mp4")], check=True)
    # partial movie files are large and only needed during the render
    shutil.rmtree(MEDIA / "videos" / f.stem / sub / "partial_movie_files", ignore_errors=True)
    print("->", dest / f"{ch}.mp4")


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def assemble(draft):
    src = OUT / ("chapters_draft" if draft else "chapters")
    script = json.loads((ROOT / "script" / "narration.json").read_text())
    order = [c["id"] for c in script["chapters"]]
    vids = [src / f"{c}.mp4" for c in order if (src / f"{c}.mp4").exists()]
    missing = [c for c in order if not (src / f"{c}.mp4").exists()]
    if missing:
        print("WARNING missing chapters:", missing)
    lst = src / "concat.txt"
    lst.write_text("".join(f"file '{v}'\n" for v in vids))
    name = "haldane_gap_explainer" + ("_draft" if draft else "")
    final = OUT / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(final)], check=True)
    print(f"-> {final}  ({duration(final)/60:.1f} min)")


def frames(ch, every, draft):
    src = OUT / ("chapters_draft" if draft else "chapters") / f"{ch}.mp4"
    dest = OUT / "frames" / ch
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vf",
                    f"fps=1/{every},scale=960:-1", str(dest / "f%03d.png")], check=True)
    print("->", dest)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["render", "assemble", "frames"])
    ap.add_argument("chapter", nargs="?")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--every", type=float, default=4.0)
    a = ap.parse_args()
    if a.cmd == "render":
        chs = [f.name[:4] for f in chapter_files()] if a.chapter == "all" else [a.chapter]
        for c in chs:
            render(c, a.draft)
    elif a.cmd == "assemble":
        assemble(a.draft)
    else:
        frames(a.chapter, a.every, a.draft)
