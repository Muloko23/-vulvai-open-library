"""Build short narrated, captioned explainer videos for video lessons.

Each sentence of the lesson script becomes one illustrated scene with its
own narration and an on screen caption, so girls with low literacy can
listen and girls who cannot play sound can read. Scenes are joined with
crossfades into a 720x720 MP4 that plays offline on low cost phones.

These are prototype videos. In the pilot, local voices narrate in Hindi
and dialects, and the youth advisory group reviews every scene.

Usage:
    python tools/make_video.py                      # use human recordings only
    python tools/make_video.py --model kokoro-v1.0.int8.onnx --voices voices-v1.0.bin
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from illustrations import bubble, girl, scene, woman  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MODULES = ROOT / "library" / "modules"
OUT = ROOT / "library" / "media" / "video"

ACCENT = "#9c2d63"


def icon_row(items: list[tuple[str, str]], y=110) -> str:
    """Small labelled icon chips across the top of a scene."""
    n = len(items)
    w = 560 / n
    out = []
    for i, (glyph, label) in enumerate(items):
        cx = 20 + w * i + w / 2
        out.append(f'<g transform="translate({cx} {y})"><circle r="44" fill="#fff" stroke="#f0d9e1" stroke-width="3"/>'
                   f'<text y="14" font-size="40" text-anchor="middle" font-family="Arial">{glyph}</text>'
                   f'<text y="72" font-size="18" font-weight="700" text-anchor="middle" fill="{ACCENT}" '
                   f'font-family="Arial">{label}</text></g>')
    return "".join(out)


def growth_chart() -> str:
    bars = []
    for i, (h, skin, kurta) in enumerate([(0.62, 0, "#2f8f83"), (0.78, 2, "#f2786d"), (0.92, 4, "#9c2d63")]):
        bars.append(girl(140 + i * 160, 440 - 230 * h, h, skin=skin, kurta=kurta, mood="smile"))
    return "".join(bars) + '<path d="M70 120 h460" stroke="#d98f57" stroke-width="3" stroke-dasharray="8 8"/>'


def calendar(days_marked: list[int], label: str) -> str:
    cells = []
    for i in range(28):
        x, y = 120 + (i % 7) * 52, 140 + (i // 7) * 52
        on = i in days_marked
        cells.append(f'<rect x="{x}" y="{y}" width="44" height="44" rx="8" fill="{"#e8435a" if on else "#fff"}" '
                     f'stroke="#f0d9e1" stroke-width="2"/>')
    return (f'<rect x="100" y="80" width="400" height="290" rx="20" fill="#fff8e8" stroke="#e0b04b" stroke-width="4"/>'
            f'<text x="300" y="120" font-family="Arial" font-weight="700" font-size="24" text-anchor="middle" fill="{ACCENT}">{label}</text>'
            + "".join(cells))


def uterus() -> str:
    return ('<g transform="translate(300 220)">'
            '<path d="M-120 -70 q-40 -10 -50 30 q-5 30 30 30 M120 -70 q40 -10 50 30 q5 30 -30 30" stroke="#c2185b" stroke-width="10" fill="none" stroke-linecap="round"/>'
            '<circle cx="-150" cy="-5" r="20" fill="#f6b3c4"/><circle cx="150" cy="-5" r="20" fill="#f6b3c4"/>'
            '<path d="M-110 -80 q110 -30 220 0 q0 120 -70 150 v60 h-80 v-60 q-70 -30 -70 -150z" fill="#f48fb1" stroke="#c2185b" stroke-width="6"/>'
            '<path d="M-80 -60 q80 -20 160 0 q-5 90 -55 120 h-50 q-50 -30 -55 -120z" fill="#e8435a" opacity=".55"/>'
            '<g fill="#e8435a"><circle cx="0" cy="150" r="7"/><circle cx="-6" cy="175" r="6"/><circle cx="5" cy="195" r="5"/></g>'
            '</g>')


SCENES: dict[str, list[str]] = {
    "puberty_changes_1": [
        scene(girl(170, 300, 0.75, skin=0, kurta="#2f8f83", mood="smile")
              + '<path d="M245 380 h80" stroke="#9c2d63" stroke-width="8" stroke-linecap="round"/><path d="M315 365 l20 15 l-20 15" fill="#9c2d63"/>'
              + woman(430, 240, 1.0, skin=0, saree="#9c2d63", border="#e0b04b", mood="smile")),
        scene(icon_row([("8", "age 8"), ("➜", ""), ("13", "age 13")]) + girl(300, 290, 0.95, skin=2, kurta="#f2786d", mood="smile"),
              wall=False, sun=False),
        scene(icon_row([("🌱", "breasts"), ("〰", "body hair"), ("⬌", "hips"), ("⬆", "taller")])
              + girl(300, 290, 0.95, skin=1, kurta="#9c2d63", mood="smile"), wall=False, sun=False),
        scene(girl(220, 290, 0.95, skin=3, kurta="#5b1f4f", dupatta="#e0b04b", mood="worried")
              + woman(430, 245, 1.0, skin=1, saree="#2f8f83", border="#e0b04b", mood="talk", arm="point")
              + bubble(300, 60, 270, 90, "Discharge is a\nhealthy sign.", tail="right", size=22)),
        scene(growth_chart(), wall=False, ground="#fbeaee"),
    ],
    "menstruation_basics_1": [
        scene(uterus(), wall=False, sun=False, ground="#fbeaee", sky=("#fff6f8", "#fde4ea")),
        scene(girl(300, 280, 1.0, skin=0, kurta="#9c2d63", mood="smile", arm="up")
              + bubble(330, 60, 240, 90, "Healthy and\nnormal.", tail="right", size=24)),
        scene(icon_row([("10", "age 10"), ("➜", ""), ("15", "age 15")])
              + girl(200, 290, 0.85, skin=2, kurta="#2f8f83", mood="smile")
              + girl(400, 280, 0.95, skin=4, kurta="#f2786d", mood="smile"), wall=False, sun=False),
        scene(calendar([2, 3, 4, 5, 6, 23, 24, 25], "2 to 7 days, irregular at first"), wall=False, sun=False,
              ground="#fbeaee"),
    ],
}


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def wrap(text: str, width=40) -> list[str]:
    words, lines, line = text.split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > width:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    return lines + [line]


def with_caption(svg: str, caption: str) -> str:
    lines = wrap(caption)
    h = 40 + 34 * len(lines)
    y0 = 600 - h - 16
    text = "".join(f'<text x="300" y="{y0 + 42 + i * 34}" font-family="Arial, sans-serif" font-size="25" '
                   f'font-weight="700" text-anchor="middle" fill="#fff">{line}</text>' for i, line in enumerate(lines))
    box = f'<rect x="16" y="{y0}" width="568" height="{h}" rx="16" fill="#3b1530" opacity=".88"/>{text}'
    return svg.replace("</svg>", box + "</svg>")


def render_png(svg_paths: list[Path]) -> None:
    js = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 720, height: 720 } });
  for (const f of process.argv.slice(1)) {
    await p.goto('file://' + f);
    await p.screenshot({ path: f.replace(/\\.svg$/, '.png') });
  }
  await b.close();
})();
"""
    subprocess.run(["node", "-e", js, *map(str, svg_paths)], check=True)


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


RECORDINGS = ROOT / "library" / "media" / "recordings"


def build(lesson_id: str, script: str, tts, voice: str, speed: float) -> Path:
    """Human recordings in library/media/recordings/<lesson_id>/<n>.wav take
    priority. A sentence with no recording stays on screen with its caption
    and no narration until one is added."""
    import shutil

    parts = sentences(script)
    art = SCENES[lesson_id]
    assert len(parts) == len(art), f"{lesson_id}: {len(parts)} sentences, {len(art)} scenes"
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{lesson_id}.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        svgs = []
        for i, (sentence, svg) in enumerate(zip(parts, art)):
            p = tmp / f"s{i}.svg"
            p.write_text(with_caption(svg, sentence).replace(
                "<svg ", '<svg width="720" height="720" ', 1), encoding="utf-8")
            svgs.append(p)
            human = RECORDINGS / lesson_id / f"{i}.wav"
            if human.is_file():
                shutil.copy(human, tmp / f"s{i}.wav")
            elif tts is None:
                secs = max(3.0, len(sentence.split()) * 0.38)
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                                "anullsrc=r=24000:cl=mono", "-t", f"{secs:.2f}", str(tmp / f"s{i}.wav")], check=True)
            else:
                import soundfile as sf
                samples, rate = tts.create(sentence, voice=voice, speed=speed, lang="en-us")
                sf.write(tmp / f"s{i}.wav", samples, rate)
        render_png(svgs)
        clips = []
        for i in range(len(parts)):
            d = duration(tmp / f"s{i}.wav") + 0.7
            clip = tmp / f"c{i}.mp4"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", str(tmp / f"s{i}.png"),
                            "-i", str(tmp / f"s{i}.wav"), "-t", f"{d:.2f}",
                            "-vf", f"scale=720:720,zoompan=z='min(zoom+0.0006,1.06)':d={int(d * 25) + 1}:s=720x720:fps=25,"
                                   f"fade=t=in:st=0:d=0.3,fade=t=out:st={d - 0.3:.2f}:d=0.3",
                            "-af", "apad=pad_dur=1", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "64k", "-ar", "24000", "-ac", "1", "-shortest", str(clip)], check=True)
            clips.append(clip)
        listing = tmp / "list.txt"
        listing.write_text("".join(f"file '{c}'\n" for c in clips))
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", str(out)], check=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Kokoro model, for draft narration where no recording exists")
    parser.add_argument("--voices")
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=0.9)
    args = parser.parse_args()

    tts = None
    if args.model:
        from kokoro_onnx import Kokoro

        tts = Kokoro(args.model, args.voices)
    for path in sorted(MODULES.glob("*.json")):
        module = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for lesson in module["lessons"]:
            if lesson["id"] not in SCENES:
                continue
            out = build(lesson["id"], lesson["script"]["en"], tts, args.voice, args.speed)
            rel = f"media/video/{out.name}"
            if lesson.get("video") != rel:
                lesson["video"] = rel
                changed = True
            print(f"{out.name}  {duration(out):.1f}s  {out.stat().st_size // 1024} KB")
        if changed:
            path.write_text(json.dumps(module, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
