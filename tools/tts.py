"""Generate narration audio for every segment in script/narration.json.

Run with the isolated TTS env (its OpenMP runtime conflicts with manim's):
    .venv-tts/bin/python tools/tts.py [--voice af_heart] [--only ch03]

Writes audio/<chapter>/<segment>.wav and audio/durations.json.
Segments are cached by a hash of (voice, speed, spoken text); unchanged
segments are not regenerated.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "script" / "narration.json"
AUDIO = ROOT / "audio"
SR = 24000


# Pronunciation fixes applied to every spoken line (misaki inline-phoneme markup).
LEXICON = {
    "Affleck": "[Affleck](/ˈæflɛk/)",
}


def spoken(seg):
    # "say" overrides the display text when pronunciation needs help.
    text = seg.get("say", seg["text"])
    for word, fix in LEXICON.items():
        text = re.sub(rf"\b{word}\b", fix, text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default=None)
    ap.add_argument("--speed", type=float, default=None)
    ap.add_argument("--only", default=None, help="chapter id to (re)generate")
    args = ap.parse_args()

    script = json.loads(SCRIPT.read_text())
    voice = args.voice or script.get("voice", "af_heart")
    speed = args.speed or script.get("speed", 1.0)

    from kokoro import KPipeline
    pipe = KPipeline(lang_code="a" if voice[0] == "a" else "b")

    dur_path = AUDIO / "durations.json"
    durations = json.loads(dur_path.read_text()) if dur_path.exists() else {}
    hashes_path = AUDIO / "hashes.json"
    hashes = json.loads(hashes_path.read_text()) if hashes_path.exists() else {}

    for ch in script["chapters"]:
        if args.only and ch["id"] != args.only:
            continue
        outdir = AUDIO / ch["id"]
        outdir.mkdir(parents=True, exist_ok=True)
        durations.setdefault(ch["id"], {})
        for seg in ch["segments"]:
            key = f'{ch["id"]}/{seg["id"]}'
            text = spoken(seg)
            h = hashlib.sha1(f"{voice}|{speed}|{text}".encode()).hexdigest()
            wav = outdir / f'{seg["id"]}.wav'
            if hashes.get(key) == h and wav.exists():
                continue
            chunks = [a for _, _, a in pipe(text, voice=voice, speed=speed)]
            audio = np.concatenate([np.asarray(c) for c in chunks]).astype(np.float32)
            sf.write(wav, audio, SR)
            durations[ch["id"]][seg["id"]] = round(len(audio) / SR, 3)
            hashes[key] = h
            print(f"{key}: {durations[ch['id']][seg['id']]:.2f}s")
        # drop segments that no longer exist in the script
        live = {s["id"] for s in ch["segments"]}
        durations[ch["id"]] = {k: v for k, v in durations[ch["id"]].items() if k in live}

    dur_path.write_text(json.dumps(durations, indent=1))
    hashes_path.write_text(json.dumps(hashes, indent=1))
    total = sum(sum(d.values()) for d in durations.values())
    print(f"total narration: {total/60:.1f} min")


if __name__ == "__main__":
    main()
