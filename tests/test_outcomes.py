import pytest

from openlibrary.content import load_library
from openlibrary.outcomes import assess, change, cohort_summary, domain_scores, load_survey
from openlibrary.records import Event, SyncQueue, new_learner_id


@pytest.fixture(scope="module")
def survey():
    return load_survey()


@pytest.fixture(scope="module")
def modules():
    return load_library()


def test_survey_covers_six_outcomes(survey):
    ids = {d["id"] for d in survey["domains"]} | {survey["knowledge_test"]["id"]}
    assert ids == {"comfort", "confidence", "safety", "self_advocacy", "health_action", "body_knowledge"}


def test_knowledge_test_modules_exist(survey, modules):
    assert set(survey["knowledge_test"]["source_modules"]) <= set(modules)


def test_reverse_items_are_flipped(survey):
    scores = domain_scores(survey, {"comfort_1": 3, "comfort_2": 3, "comfort_3": 0})
    assert scores["comfort"] == 100.0


def test_missing_domain_is_none_not_zero(survey):
    assert domain_scores(survey, {})["safety"] is None


def test_out_of_range_response_rejected(survey):
    with pytest.raises(ValueError):
        domain_scores(survey, {"safety_1": 7})


def test_change_from_pre_to_post(survey, modules):
    pre = assess(survey, modules, "AB12CD", {"safety_1": 0, "safety_2": 1}, {"body_basics": [1, 0]})
    post = assess(survey, modules, "AB12CD", {"safety_1": 3, "safety_2": 3}, {"body_basics": [0, 1]})
    delta = change(pre, post)
    assert delta["safety"] > 0
    assert delta["body_knowledge"] == 100.0


def test_small_cohorts_are_suppressed(survey, modules):
    a = assess(survey, modules, "X", {"safety_1": 1}, {})
    assert cohort_summary([(a, a)] * 3)["suppressed"] is True
    assert cohort_summary([(a, a)] * 10)["suppressed"] is False


def test_learner_ids_are_random_codes():
    ids = {new_learner_id() for _ in range(100)}
    assert len(ids) == 100 and all(len(i) == 6 for i in ids)


def test_queue_rejects_personal_data(tmp_path):
    queue = SyncQueue(tmp_path / "queue.jsonl")
    with pytest.raises(ValueError):
        queue.add(Event("AB12CD", "quiz_scored", {"name": "Meera"}))


def test_queue_syncs_and_clears(tmp_path):
    queue = SyncQueue(tmp_path / "queue.jsonl")
    queue.add(Event("AB12CD", "quiz_scored", {"module": "body_basics", "score": 100}))
    sent = []
    assert queue.flush(sent.extend) == 1
    assert sent[0]["data"]["score"] == 100
    assert queue.pending() == []


def test_failed_sync_keeps_events(tmp_path):
    queue = SyncQueue(tmp_path / "queue.jsonl")
    queue.add(Event("AB12CD", "lesson_completed", {"lesson": "body_basics_1"}))

    def offline(_):
        raise ConnectionError

    with pytest.raises(ConnectionError):
        queue.flush(offline)
    assert len(queue.pending()) == 1
