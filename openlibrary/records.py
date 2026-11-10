"""Pseudonymous learner records with an offline sync queue.

Shared phones in villages are often offline. Every event (lesson completed,
quiz answered, question flagged) is appended to a local queue file and synced
when a connection is available. No names, phone numbers, or locations are
stored. Learner IDs are random codes issued by a facilitator.
"""

from __future__ import annotations

import json
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_EVENTS = {"lesson_completed", "quiz_scored", "question_answered",
                  "question_flagged", "survey_submitted"}
FORBIDDEN_FIELDS = {"name", "phone", "address", "village", "gps", "location", "email"}


def new_learner_id() -> str:
    """Return a short random code a facilitator can write on a card, e.g. 'G7K2QX'."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(6))


@dataclass
class Event:
    learner_id: str
    type: str
    data: dict = field(default_factory=dict)
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


class SyncQueue:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, event: Event) -> None:
        if event.type not in ALLOWED_EVENTS:
            raise ValueError(f"unknown event type '{event.type}'")
        leaked = FORBIDDEN_FIELDS & {k.lower() for k in event.data}
        if leaked:
            raise ValueError(f"personal data not allowed: {sorted(leaked)}")
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def pending(self) -> list[Event]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [Event(**json.loads(line)) for line in lines if line.strip()]

    def flush(self, send) -> int:
        """Send pending events with the given callable and clear them on success.

        send receives a list of event dictionaries and should raise on failure,
        in which case the queue is kept for the next attempt.
        """
        events = self.pending()
        if not events:
            return 0
        send([asdict(e) for e in events])
        self.path.unlink()
        return len(events)
