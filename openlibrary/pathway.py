"""Rules based learning path engine.

Each girl has a quiz score (0 to 100) per completed module. The engine picks
the next module using transparent rules that facilitators can read and audit:

1. A module scored below the mastery threshold is repeated first, so no girl
   moves on without understanding the basics.
2. Otherwise, the next module is the lowest level unlocked module not yet
   completed. A module is unlocked when all its prerequisites are mastered.
3. When everything available is mastered, the path is complete.
"""

from __future__ import annotations

from dataclasses import dataclass

from .content import Module

MASTERY_THRESHOLD = 70


@dataclass
class Recommendation:
    module_id: str | None
    reason: str


def next_module(modules: dict[str, Module], scores: dict[str, int],
                threshold: int = MASTERY_THRESHOLD) -> Recommendation:
    for module_id, score in sorted(scores.items(), key=lambda kv: kv[1]):
        if module_id in modules and score < threshold:
            return Recommendation(module_id, f"Review: scored {score}, below {threshold}")

    mastered = {m for m, s in scores.items() if s >= threshold}
    candidates = [
        m for m in modules.values()
        if m.id not in scores and all(p in mastered for p in m.prerequisites)
    ]
    if candidates:
        choice = min(candidates, key=lambda m: (m.level, m.id))
        return Recommendation(choice.id, f"New: level {choice.level}, prerequisites met")
    return Recommendation(None, "All available modules mastered")


def score_quiz(module: Module, answers: list[int]) -> int:
    """Return a 0 to 100 score for a list of selected option indexes."""
    if not module.quiz:
        return 100
    correct = sum(1 for q, a in zip(module.quiz, answers) if q["answer"] == a)
    return round(100 * correct / len(module.quiz))
