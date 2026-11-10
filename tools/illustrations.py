"""Draft illustrations for story cards, case scenarios, and group activities.

Flat vector scenes set in a Rajasthani village. These are prototype
illustrations. In the pilot, the youth advisory group reviews every image,
and local illustrators adapt characters, clothing, and settings.

Usage:
    python tools/illustrations.py
"""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "library" / "media" / "images"

SKIN = ["#8d5a3b", "#a86b47", "#7a4a30", "#9b6240", "#6e4128"]
HAIR = "#1f1414"
SKY_TOP, SKY_BOTTOM = "#fde9d8", "#fbd3c2"
SAND, WALL, WALL_SHADE = "#f2c98b", "#e9a86b", "#d98f57"


def scene(body: str, sky=(SKY_TOP, SKY_BOTTOM), ground=SAND, wall=True, sun=True) -> str:
    sky_grad = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{sky[0]}"/><stop offset="1" stop-color="{sky[1]}"/></linearGradient>')
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600"><defs>{sky_grad}</defs>',
             '<rect width="600" height="600" fill="url(#sky)"/>']
    if sun:
        parts.append('<circle cx="500" cy="95" r="48" fill="#f7b538" opacity=".9"/>')
    if wall:
        parts.append(f'<rect x="0" y="210" width="600" height="230" fill="{WALL}"/>'
                     f'<path d="M210 440 V320 a60 60 0 0 1 120 0 V440 Z" fill="{WALL_SHADE}"/>'
                     f'<rect x="0" y="200" width="600" height="14" fill="{WALL_SHADE}"/>'
                     '<g fill="#fff" opacity=".35"><circle cx="70" cy="260" r="6"/><circle cx="100" cy="260" r="6"/>'
                     '<circle cx="130" cy="260" r="6"/><circle cx="470" cy="260" r="6"/><circle cx="500" cy="260" r="6"/>'
                     '<circle cx="530" cy="260" r="6"/></g>')
    parts.append(f'<rect x="0" y="440" width="600" height="160" fill="{ground}"/>')
    parts.append(body)
    parts.append("</svg>")
    return "".join(parts)


def girl(x, y, s=1.0, skin=0, kurta="#9c2d63", dupatta="#f2786d", pants="#5b1f4f", mood="smile",
         arm="down", hair="braid") -> str:
    k = SKIN[skin % len(SKIN)]
    face = {"smile": '<path d="M-9 8 q9 9 18 0" stroke="#3a1d14" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "worried": '<path d="M-8 12 q8 -6 16 0" stroke="#3a1d14" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "talk": '<ellipse cx="0" cy="10" rx="5" ry="4" fill="#3a1d14"/>'}[mood]
    arms = {"down": f'<path d="M-30 50 q-12 40 -8 70" stroke="{k}" stroke-width="12" fill="none" stroke-linecap="round"/>'
                    f'<path d="M30 50 q12 40 8 70" stroke="{k}" stroke-width="12" fill="none" stroke-linecap="round"/>',
            "up": f'<path d="M-30 50 q-12 40 -8 70" stroke="{k}" stroke-width="12" fill="none" stroke-linecap="round"/>'
                  f'<path d="M30 50 q30 -10 40 -50" stroke="{k}" stroke-width="12" fill="none" stroke-linecap="round"/>'
                  f'<circle cx="72" cy="-6" r="13" fill="{k}"/>',
            "reach": f'<path d="M-30 50 q-12 40 -8 70" stroke="{k}" stroke-width="12" fill="none" stroke-linecap="round"/>'
                     f'<path d="M30 50 q30 0 60 -20" stroke="{k}" stroke-width="12" fill="none" stroke-linecap="round"/>'}[arm]
    hair_svg = (f'<path d="M-30 -8 q0 -40 30 -40 q30 0 30 40 q-8 -18 -30 -20 q-22 2 -30 20z" fill="{HAIR}"/>'
                + (f'<path d="M24 0 q14 40 4 90" stroke="{HAIR}" stroke-width="10" fill="none" stroke-linecap="round"/>'
                   if hair == "braid" else f'<circle cx="0" cy="-48" r="15" fill="{HAIR}"/>'))
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<rect x="-22" y="125" width="18" height="70" rx="8" fill="{pants}"/>'
            f'<rect x="4" y="125" width="18" height="70" rx="8" fill="{pants}"/>'
            f'<path d="M-34 40 q34 -16 68 0 l14 100 h-96z" fill="{kurta}"/>'
            f'<path d="M-30 42 q40 30 64 100" stroke="{dupatta}" stroke-width="16" fill="none" stroke-linecap="round"/>'
            f'{arms}<rect x="-8" y="24" width="16" height="18" fill="{k}"/>'
            f'<circle cx="0" cy="0" r="30" fill="{k}"/>{hair_svg}'
            f'<circle cx="-10" cy="-2" r="3.5" fill="#1f1414"/><circle cx="10" cy="-2" r="3.5" fill="#1f1414"/>'
            f'{face}<circle cx="0" cy="-16" r="3" fill="#c2185b"/></g>')


def woman(x, y, s=1.0, skin=1, saree="#e0b04b", border="#9c2d63", mood="smile", arm="down", badge=None) -> str:
    k = SKIN[skin % len(SKIN)]
    face = {"smile": '<path d="M-10 9 q10 9 20 0" stroke="#3a1d14" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "talk": '<ellipse cx="0" cy="11" rx="6" ry="4.5" fill="#3a1d14"/>',
            "stern": '<path d="M-9 12 h18" stroke="#3a1d14" stroke-width="3" stroke-linecap="round"/>'}[mood]
    arm_svg = {"down": f'<path d="M34 55 q14 45 6 80" stroke="{k}" stroke-width="13" fill="none" stroke-linecap="round"/>',
               "reach": f'<path d="M34 55 q-10 40 -50 50" stroke="{k}" stroke-width="13" fill="none" stroke-linecap="round"/>',
               "point": f'<path d="M34 55 q30 0 55 -30" stroke="{k}" stroke-width="13" fill="none" stroke-linecap="round"/>'}[arm]
    badge_svg = (f'<g transform="translate(-22 70)"><rect x="-26" y="-12" width="52" height="24" rx="6" fill="#fff"/>'
                 f'<text x="0" y="6" font-family="Arial" font-weight="700" font-size="15" text-anchor="middle" fill="#2d7a46">{badge}</text></g>'
                 if badge else "")
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-40 45 q40 -18 80 0 l22 180 h-124z" fill="{saree}"/>'
            f'<path d="M-62 225 h124" stroke="{border}" stroke-width="12"/>'
            f'<path d="M-38 48 q50 10 60 177" stroke="{border}" stroke-width="10" fill="none"/>'
            f'<path d="M-40 -10 q0 -48 40 -48 q40 0 40 48 l8 70 q-48 -40 -96 0z" fill="{saree}" opacity=".95"/>'
            f'{arm_svg}<rect x="-9" y="28" width="18" height="20" fill="{k}"/>'
            f'<circle cx="0" cy="0" r="32" fill="{k}"/>'
            f'<path d="M-32 -6 q0 -36 32 -36 q32 0 32 36 q-12 -20 -32 -20 q-20 0 -32 20z" fill="{HAIR}"/>'
            f'<circle cx="-11" cy="-2" r="3.5" fill="#1f1414"/><circle cx="11" cy="-2" r="3.5" fill="#1f1414"/>'
            f'{face}<circle cx="0" cy="-17" r="3.5" fill="#c2185b"/>{badge_svg}</g>')


def bubble(x, y, w, h, text, tail="left", fill="#fff", color="#5b1f4f", size=24) -> str:
    tx = x + 30 if tail == "left" else x + w - 30
    lines = text.split("\n")
    texts = "".join(f'<text x="{x + w / 2}" y="{y + h / 2 + (i - (len(lines) - 1) / 2) * (size + 6) + size / 3}" '
                    f'font-family="Arial, sans-serif" font-weight="700" font-size="{size}" text-anchor="middle" fill="{color}">{line}</text>'
                    for i, line in enumerate(lines))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="#f0d9e1" stroke-width="3"/>'
            f'<path d="M{tx - 12} {y + h - 2} l{-10 if tail == "left" else 10} 26 l26 -26z" fill="{fill}"/>{texts}')


def scenes() -> dict[str, str]:
    return {
        "body_basics_2": scene(
            woman(200, 250, 1.0, skin=1, saree="#e0b04b", mood="talk", arm="reach")
            + girl(390, 285, 0.95, skin=0, kurta="#9c2d63", mood="worried")
            + bubble(40, 70, 250, 90, "This is normal.\nYour body is healthy.", size=21)),
        "puberty_changes_2": scene(
            girl(160, 300, 0.85, skin=2, kurta="#2f8f83", dupatta="#e0b04b", mood="worried")
            + girl(300, 270, 1.0, skin=0, kurta="#9c2d63", mood="smile")
            + woman(460, 240, 1.0, skin=3, saree="#5b1f4f", border="#e0b04b", mood="talk", arm="point")
            + bubble(300, 60, 270, 90, "Every body has its\nown timetable.", tail="right", size=21)),
        "menstruation_basics_2": scene(
            '<rect x="225" y="330" width="90" height="110" fill="#7a4a30"/>'
            + girl(140, 290, 0.95, skin=4, kurta="#f2786d", dupatta="#5b1f4f", mood="worried")
            + woman(440, 245, 1.0, skin=1, saree="#2f8f83", border="#e0b04b", mood="stern")
            + bubble(30, 70, 230, 90, "Am I unclean?", size=26)
            + bubble(330, 70, 240, 90, "What would\nyou tell her?", tail="right", fill="#fff8e8", size=22)),
        "menstrual_hygiene_2": scene(
            '<path d="M330 190 V430 M560 190 V430" stroke="#7a4a30" stroke-width="8"/>'
            '<path d="M330 210 Q445 235 560 210" stroke="#3a1d14" stroke-width="3" fill="none"/>'
            '<rect x="370" y="216" width="56" height="80" rx="6" fill="#fff"/><rect x="450" y="220" width="56" height="80" rx="6" fill="#f6d6dc"/>'
            '<g stroke="#f7b538" stroke-width="5" stroke-linecap="round"><path d="M500 30 v-18"/><path d="M560 60 l14 -10"/><path d="M440 60 l-14 -10"/></g>'
            + girl(200, 280, 1.0, skin=2, kurta="#9c2d63", dupatta="#e0b04b", mood="smile", arm="up")
            + bubble(30, 60, 260, 90, "Dry it in the sun!", size=24)),
        "care_seeking_2": scene(
            girl(190, 285, 0.95, skin=0, kurta="#5b1f4f", dupatta="#f2786d", mood="talk")
            + woman(410, 245, 1.0, skin=3, saree="#ffffff", border="#2f8f83", mood="smile", badge="ASHA")
            + '<rect x="470" y="380" width="60" height="44" rx="8" fill="#2f8f83"/><path d="M500 392 v20 M490 402 h20" stroke="#fff" stroke-width="5"/>'
            + bubble(30, 60, 300, 100, "It burns when I pass\nurine. It started\nthree days ago.", size=19)),
        "consent_basics_2": scene(
            girl(200, 285, 1.0, skin=1, kurta="#2f8f83", dupatta="#e0b04b", mood="talk", arm="up")
            + girl(400, 285, 1.0, skin=3, kurta="#9c2d63", mood="smile")
            + bubble(40, 70, 220, 90, "No. Please stop.", size=24)
            + bubble(330, 70, 230, 90, "I hear you.", tail="right", fill="#fff8e8", size=24)),
        "emotions_selfworth_2": scene(
            "".join(girl(x, 300, 0.8, skin=i, kurta=c, mood="smile")
                    for i, (x, c) in enumerate([(110, "#9c2d63"), (230, "#2f8f83"), (370, "#f2786d"), (490, "#5b1f4f")]))
            + "".join(f'<path d="M{x} {y} c-10 -14 -30 -4 -20 12 l20 18 l20 -18 c10 -16 -10 -26 -20 -12z" fill="#e8435a"/>'
                      for x, y in [(170, 150), (300, 120), (430, 150)]),
            wall=True),
        "safety_trusted_adults_2": scene(
            '<g transform="translate(300 330)">'
            '<path d="M-110 120 q-20 -90 10 -140 v-110 a22 22 0 0 1 44 0 v90 v-130 a22 22 0 0 1 44 0 v130 v-120 a22 22 0 0 1 44 0 v120 v-90 '
            'a22 22 0 0 1 44 0 v150 l40 -50 a22 22 0 0 1 34 28 l-60 100 q-40 70 -110 70 z" fill="#fff" stroke="#5b1f4f" stroke-width="6"/>'
            + "".join(f'<g transform="translate({fx} {fy})"><circle r="11" fill="{c}"/><path d="M-14 26 q14 -22 28 0" fill="{c}"/></g>'
                      for fx, fy, c in [(-88, -205, "#9c2d63"), (-44, -245, "#2f8f83"), (0, -235, "#e0b04b"),
                                    (44, -205, "#f2786d"), (102, -80, "#5b1f4f")])
            + '</g>', wall=False, ground="#fbeaee"),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, svg in scenes().items():
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"{name}.svg")


if __name__ == "__main__":
    main()
