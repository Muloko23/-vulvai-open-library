"""Command line demo for the VULVAi Open Library.

Examples:
    python -m openlibrary.cli validate
    python -m openlibrary.cli path --scores body_basics=90 menstruation_basics=40
    python -m openlibrary.cli ask "Why does my stomach hurt during my period?"
    python -m openlibrary.cli lesson menstruation_basics
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, safety
from .content import load_library
from .pathway import MASTERY_THRESHOLD, next_module
from .retrieval import NO_MATCH_MESSAGE, STOPWORDS, LibraryIndex


def _parse_scores(pairs: list[str]) -> dict[str, int]:
    scores = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        scores[key] = int(value)
    return scores


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="openlibrary")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--min-status", default="draft",
                        choices=["draft", "community_reviewed", "clinically_verified"])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    p_path = sub.add_parser("path")
    p_path.add_argument("--scores", nargs="*", default=[])
    p_ask = sub.add_parser("ask")
    p_ask.add_argument("question")
    p_lesson = sub.add_parser("lesson")
    p_lesson.add_argument("module_id")
    p_export = sub.add_parser("export", help="bundle the library for the offline web app")
    p_export.add_argument("--out", default="app/library.json")
    args = parser.parse_args(argv)

    modules = load_library(min_status=args.min_status)

    if args.command == "validate":
        for m in modules.values():
            print(f"ok  {m.id:<22} level {m.level}  {m.review_status}")
        print(f"{len(modules)} modules valid")
    elif args.command == "path":
        rec = next_module(modules, _parse_scores(args.scores))
        print(f"Next: {rec.module_id or 'none'}  ({rec.reason})")
    elif args.command == "ask":
        answer = LibraryIndex(modules, args.lang).ask(args.question)
        print(answer.text)
        if answer.routed_to_facilitator:
            print(f"[routed to facilitator: {', '.join(answer.safety_categories)}]")
        elif answer.source:
            print(f"[source: {answer.source}, score {answer.score}]")
    elif args.command == "export":
        bundle = {
            "version": __version__,
            "min_status": args.min_status,
            "mastery_threshold": MASTERY_THRESHOLD,
            "safety": {"categories": safety.CATEGORIES, "message": safety.FACILITATOR_MESSAGE},
            "no_match_message": NO_MATCH_MESSAGE,
            "stopwords": sorted(STOPWORDS),
            "modules": [{k: v for k, v in vars(m).items() if k != "source"} for m in modules.values()],
        }
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(bundle, ensure_ascii=False, indent=1), encoding="utf-8")
        copied = _copy_media(modules.values(), out.parent)
        print(f"wrote {out} with {len(modules)} modules and {copied} media files")
    elif args.command == "lesson":
        m = modules[args.module_id]
        print(m.text(m.title, args.lang))
        for lesson in m.lessons:
            print(f"\n[{lesson['format']}] {m.text(lesson['script'], args.lang)}")
    return 0


def _copy_media(modules, dest: Path) -> int:
    """Copy every audio, video, and image file a lesson uses next to the app bundle."""
    import shutil

    from .content import MEDIA_KINDS, MEDIA_ROOT

    copied = 0
    for m in modules:
        for lesson in m.lessons:
            for kind in MEDIA_KINDS:
                rel = lesson.get(kind)
                if rel:
                    target = dest / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(MEDIA_ROOT / rel, target)
                    copied += 1
    return copied


if __name__ == "__main__":
    sys.exit(main())
