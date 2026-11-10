"""Answer private questions only from verified library entries.

This is the retrieval step of the retrieval augmented approach. It ranks the
library's FAQ entries with BM25 plus curated keyword matches and returns the
verified answer text unchanged. If no entry is a confident match, it returns
no answer rather than guessing.

In production, the ranking step can be replaced with multilingual embeddings
so questions in Hindi and local dialects match correctly. A language model may
be used only to rephrase a retrieved answer for reading level, never to add
new medical content, and every rephrasing template is clinically reviewed.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from . import safety
from .content import Module

STOPWORDS = {"a", "an", "the", "is", "it", "my", "i", "to", "of", "and", "or",
             "in", "on", "for", "do", "does", "be", "am", "are", "what", "why",
             "how", "can", "me", "this", "that", "when", "during", "normal"}

NO_MATCH_MESSAGE = (
    "I do not have a checked answer for that yet. Please ask your facilitator, "
    "who can help you or find someone who can."
)


@dataclass
class Answer:
    text: str
    source: str | None
    score: float
    routed_to_facilitator: bool = False
    safety_categories: list | None = None


def _stem(token: str) -> str:
    """Light English plural stemming so 'smells' matches 'smell'.

    Hindi and dialect matching will use multilingual embeddings instead.
    """
    if len(token) > 4 and re.search(r"(ch|sh|x)es$", token):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _tokens(text: str) -> list[str]:
    return [_stem(t) for t in re.findall(r"[a-zऀ-ॿ]+", text.lower()) if t not in STOPWORDS]


class LibraryIndex:
    def __init__(self, modules: dict[str, Module], lang: str = "en",
                 k1: float = 1.5, b: float = 0.75):
        self.lang = lang
        self.entries = []
        for module in modules.values():
            for i, item in enumerate(module.faq):
                doc = " ".join([
                    module.text(item["question"], lang),
                    module.text(item["answer"], lang),
                    " ".join(item["keywords"]),
                ])
                self.entries.append({
                    "id": f"{module.id}.faq[{i}]",
                    "answer": module.text(item["answer"], lang),
                    "keywords": {_stem(k.lower()) for k in item["keywords"]},
                    "tokens": Counter(_tokens(doc)),
                })
        self.k1, self.b = k1, b
        n = len(self.entries) or 1
        self.avg_len = sum(sum(e["tokens"].values()) for e in self.entries) / n
        df = Counter(t for e in self.entries for t in e["tokens"])
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def _bm25(self, query: list[str], entry: dict) -> float:
        length = sum(entry["tokens"].values())
        score = 0.0
        for t in query:
            tf = entry["tokens"].get(t, 0)
            if tf:
                score += self.idf[t] * tf * (self.k1 + 1) / (
                    tf + self.k1 * (1 - self.b + self.b * length / self.avg_len))
        return score

    def ask(self, question: str, min_score: float = 1.0) -> Answer:
        result = safety.check(question)
        if result.flagged:
            return Answer(safety.FACILITATOR_MESSAGE, None, 0.0, True, result.categories)

        query = _tokens(question)
        best, best_score = None, 0.0
        for entry in self.entries:
            score = self._bm25(query, entry) + 0.5 * len(entry["keywords"] & set(query))
            if score > best_score:
                best, best_score = entry, score
        if best is None or best_score < min_score:
            return Answer(NO_MATCH_MESSAGE, None, best_score)
        return Answer(best["answer"], best["id"], round(best_score, 2))
