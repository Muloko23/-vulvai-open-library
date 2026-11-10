"""Outcome measurement for the study.

Scores the pre and post survey across six outcomes:
comfort, confidence, safety, self advocacy, ability to act on health
information, and body knowledge. Produces individual change scores and an
anonymized cohort summary.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from .content import Module
from .pathway import score_quiz

SURVEY_PATH = Path(__file__).resolve().parent.parent / "outcomes" / "survey.json"


def load_survey(path: Path = SURVEY_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def domain_scores(survey: dict, responses: dict[str, int]) -> dict[str, float]:
    """Return each Likert domain score on a 0 to 100 scale.

    responses maps item id to the selected point, 0 to (points - 1).
    Reverse scored items are flipped. Domains with no answered items are
    returned as None so missing data is never treated as a zero.
    """
    top = survey["scale"]["points"] - 1
    scores = {}
    for domain in survey["domains"]:
        values = []
        for item in domain["items"]:
            if item["id"] not in responses:
                continue
            value = responses[item["id"]]
            if not 0 <= value <= top:
                raise ValueError(f"{item['id']}: response {value} outside 0 to {top}")
            values.append(top - value if item.get("reverse") else value)
        scores[domain["id"]] = round(100 * statistics.mean(values) / top, 1) if values else None
    return scores


def knowledge_score(modules: dict[str, Module], answers: dict[str, list[int]]) -> float | None:
    """Percent correct across the knowledge test modules a girl answered."""
    scored = [score_quiz(modules[m], a) for m, a in answers.items() if m in modules]
    return round(statistics.mean(scored), 1) if scored else None


@dataclass
class Assessment:
    learner_id: str
    scores: dict[str, float | None]


def assess(survey: dict, modules: dict[str, Module], learner_id: str,
           responses: dict[str, int], quiz_answers: dict[str, list[int]]) -> Assessment:
    scores = domain_scores(survey, responses)
    scores[survey["knowledge_test"]["id"]] = knowledge_score(modules, quiz_answers)
    return Assessment(learner_id, scores)


def change(pre: Assessment, post: Assessment) -> dict[str, float | None]:
    if pre.learner_id != post.learner_id:
        raise ValueError("pre and post assessments belong to different learners")
    return {
        k: (round(post.scores[k] - pre.scores[k], 1)
            if pre.scores.get(k) is not None and post.scores.get(k) is not None else None)
        for k in pre.scores
    }


def cohort_summary(pairs: list[tuple[Assessment, Assessment]], min_cohort: int = 10) -> dict:
    """Mean pre, post, and change per outcome across learners.

    Results are suppressed for cohorts smaller than min_cohort so no
    individual girl can be identified from a report.
    """
    if len(pairs) < min_cohort:
        return {"n": len(pairs), "suppressed": True}
    summary = {"n": len(pairs), "suppressed": False, "outcomes": {}}
    for outcome in pairs[0][0].scores:
        pre = [p.scores[outcome] for p, q in pairs if p.scores[outcome] is not None and q.scores[outcome] is not None]
        post = [q.scores[outcome] for p, q in pairs if p.scores[outcome] is not None and q.scores[outcome] is not None]
        if not pre:
            continue
        summary["outcomes"][outcome] = {
            "n": len(pre),
            "mean_pre": round(statistics.mean(pre), 1),
            "mean_post": round(statistics.mean(post), 1),
            "mean_change": round(statistics.mean(b - a for a, b in zip(pre, post)), 1),
        }
    return summary
