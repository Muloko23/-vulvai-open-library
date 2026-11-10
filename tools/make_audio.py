"""Generate draft narration for every lesson.

Uses the open Kokoro text to speech model (Apache 2.0) so drafts can be
produced offline. These synthetic voices are placeholders for prototyping.
In the pilot, final audio is recorded by local voices in Hindi and local
dialects and reviewed by facilitators and clinicians.

Usage:
    python tools/make_audio.py --model kokoro-v1.0.int8.onnx --voices voices-v1.0.bin
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = ROOT / "library" / "modules"
MEDIA = ROOT / "library" / "media" / "audio"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--voices", required=True)
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=0.9)
    args = parser.parse_args()

    from kokoro_onnx import Kokoro
    import soundfile as sf

    tts = Kokoro(args.model, args.voices)
    MEDIA.mkdir(parents=True, exist_ok=True)
    for path in sorted(MODULES.glob("*.json")):
        module = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for lesson in module["lessons"]:
            out = MEDIA / f"{lesson['id']}.mp3"
            samples, rate = tts.create(lesson["script"]["en"], voice=args.voice,
                                       speed=args.speed, lang="en-us")
            with tempfile.NamedTemporaryFile(suffix=".wav") as wav:
                sf.write(wav.name, samples, rate)
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav.name,
                                "-ac", "1", "-b:a", "48k", str(out)], check=True)
            rel = f"media/audio/{out.name}"
            if lesson.get("audio") != rel:
                lesson["audio"] = rel
                changed = True
            print(f"{out.name}  {len(samples) / rate:.1f}s")
        if changed:
            path.write_text(json.dumps(module, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
