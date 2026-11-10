"""Safety routing for private questions.

Questions that may signal abuse, pregnancy, self harm, or a serious symptom
are never answered automatically. They are routed to a trained facilitator.

This keyword router is the transparent baseline. During the pilot it will be
extended with a classifier trained and evaluated on community reviewed
examples in Hindi and local dialects. The baseline stays in place as a
fallback, and any question flagged by either method is routed to a human.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

CATEGORIES: dict[str, list[str]] = {
    "abuse": ["forced", "force me", "hurt me", "touched me", "touches me", "secret",
              "hit me", "beat", "rape", "made me", "threaten"],
    "pregnancy": ["pregnant", "pregnancy", "baby", "had sex"],
    "self_harm": ["kill myself", "hurt myself", "end my life", "want to die", "suicide"],
    "serious_symptom": ["heavy bleeding", "bleeding a lot", "fainted", "faint",
                        "fever", "severe pain", "very bad pain", "lump", "blood in urine"],
    "marriage": ["marry me", "getting married", "my marriage", "married off"],
}

FACILITATOR_MESSAGE = (
    "Thank you for asking. This is important, and a trusted facilitator will talk "
    "with you privately and help you. You are not in trouble."
)


@dataclass
class SafetyResult:
    flagged: bool
    categories: list[str]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def check(question: str) -> SafetyResult:
    text = _normalize(question)
    hits = [cat for cat, phrases in CATEGORIES.items()
            if any(re.search(rf"\b{re.escape(p)}\b", text) for p in phrases)]
    return SafetyResult(flagged=bool(hits), categories=hits)
