"""Load and validate library modules.

Validation is implemented without third party packages so the library can be
checked on low resource machines and offline devices.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

LIBRARY_DIR = Path(__file__).resolve().parent.parent / "library" / "modules"

TOPICS = {"body", "puberty", "menstruation", "hygiene", "consent", "safety",
          "relationships", "emotions", "care_seeking"}
REVIEW_STATUSES = ("draft", "community_reviewed", "clinically_verified")
LESSON_FORMATS = {"audio", "video", "story_card", "case_scenario", "group_activity"}
MEDIA_ROOT = LIBRARY_DIR.parent
MEDIA_DIRS = {"audio": "audio", "video": "video", "image": "images"}
MEDIA_KINDS = tuple(MEDIA_DIRS)
REQUIRED_KEYS = ("id", "title", "topic", "level", "review_status",
                 "prerequisites", "lessons", "quiz", "faq")


@dataclass
class Module:
    id: str
    title: dict
    topic: str
    level: int
    review_status: str
    prerequisites: list
    lessons: list
    quiz: list
    faq: list
    source: Path | None = field(default=None, compare=False)

    def text(self, value: dict, lang: str = "en") -> str:
        """Return localized text, falling back to English."""
        return value.get(lang) or value["en"]


class ValidationError(ValueError):
    pass


def _check_localized(value, where: str) -> None:
    if not isinstance(value, dict) or not isinstance(value.get("en"), str) or not value["en"].strip():
        raise ValidationError(f"{where}: must be an object with a non empty 'en' string")


def validate(data: dict, where: str = "module") -> None:
    """Raise ValidationError if a module does not match the schema."""
    for key in REQUIRED_KEYS:
        if key not in data:
            raise ValidationError(f"{where}: missing '{key}'")
    _check_localized(data["title"], f"{where}.title")
    if data["topic"] not in TOPICS:
        raise ValidationError(f"{where}: unknown topic '{data['topic']}'")
    if not isinstance(data["level"], int) or not 1 <= data["level"] <= 5:
        raise ValidationError(f"{where}: level must be an integer from 1 to 5")
    if data["review_status"] not in REVIEW_STATUSES:
        raise ValidationError(f"{where}: unknown review_status '{data['review_status']}'")
    for i, lesson in enumerate(data["lessons"]):
        if lesson.get("format") not in LESSON_FORMATS:
            raise ValidationError(f"{where}.lessons[{i}]: unknown format")
        _check_localized(lesson.get("script"), f"{where}.lessons[{i}].script")
        for kind in MEDIA_KINDS:
            rel = lesson.get(kind)
            if rel is None:
                continue
            if not str(rel).startswith(f"media/{MEDIA_DIRS[kind]}/") or not (MEDIA_ROOT / rel).is_file():
                raise ValidationError(f"{where}.lessons[{i}].{kind}: missing media file {rel}")
    for i, q in enumerate(data["quiz"]):
        _check_localized(q.get("question"), f"{where}.quiz[{i}].question")
        options = q.get("options", [])
        if len(options) < 2:
            raise ValidationError(f"{where}.quiz[{i}]: needs at least two options")
        for j, opt in enumerate(options):
            _check_localized(opt, f"{where}.quiz[{i}].options[{j}]")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] < len(options):
            raise ValidationError(f"{where}.quiz[{i}]: answer index out of range")
    for i, item in enumerate(data["faq"]):
        _check_localized(item.get("question"), f"{where}.faq[{i}].question")
        _check_localized(item.get("answer"), f"{where}.faq[{i}].answer")
        if not item.get("keywords"):
            raise ValidationError(f"{where}.faq[{i}]: needs keywords")


def load_library(directory: Path = LIBRARY_DIR, min_status: str = "draft") -> dict[str, Module]:
    """Load every module at or above the given review status.

    In production, call with min_status="clinically_verified" so girls only
    ever see verified content.
    """
    threshold = REVIEW_STATUSES.index(min_status)
    modules: dict[str, Module] = {}
    for path in sorted(Path(directory).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        validate(data, where=path.name)
        if REVIEW_STATUSES.index(data["review_status"]) < threshold:
            continue
        modules[data["id"]] = Module(**data, source=path)
    for module in modules.values():
        for prereq in module.prerequisites:
            if prereq not in modules and min_status == "draft":
                raise ValidationError(f"{module.id}: unknown prerequisite '{prereq}'")
    return modules
