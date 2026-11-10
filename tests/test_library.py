import copy

import pytest

from openlibrary import safety
from openlibrary.content import ValidationError, load_library, validate
from openlibrary.pathway import next_module, score_quiz
from openlibrary.retrieval import NO_MATCH_MESSAGE, LibraryIndex


@pytest.fixture(scope="module")
def modules():
    return load_library()


def test_library_loads_and_validates(modules):
    assert {"body_basics", "menstruation_basics", "consent_basics"} <= set(modules)


def test_production_mode_serves_only_verified_content(modules):
    verified = load_library(min_status="clinically_verified")
    assert all(m.review_status == "clinically_verified" for m in verified.values())


def test_invalid_quiz_answer_is_rejected(modules):
    data = copy.deepcopy(modules["body_basics"].__dict__)
    data.pop("source")
    data["quiz"][0]["answer"] = 9
    with pytest.raises(ValidationError):
        validate(data)


def test_new_learner_starts_with_basics(modules):
    assert next_module(modules, {}).module_id == "body_basics"


def test_low_score_is_repeated_before_moving_on(modules):
    rec = next_module(modules, {"body_basics": 90, "menstruation_basics": 40})
    assert rec.module_id == "menstruation_basics"


def test_prerequisites_lock_modules(modules):
    rec = next_module(modules, {"body_basics": 50})
    assert rec.module_id == "body_basics"


def test_score_quiz(modules):
    m = modules["menstruation_basics"]
    assert score_quiz(m, [1, 1]) == 100
    assert score_quiz(m, [0, 1]) == 50


def test_answers_come_only_from_library(modules):
    index = LibraryIndex(modules)
    answer = index.ask("Why does my stomach hurt so much on my period?")
    assert answer.source == "menstruation_basics.faq[1]"
    entry_texts = {e["answer"] for e in index.entries}
    assert answer.text in entry_texts


def test_unknown_question_is_not_guessed(modules):
    answer = LibraryIndex(modules).ask("What is the capital of France?")
    assert answer.text == NO_MATCH_MESSAGE
    assert answer.source is None


@pytest.mark.parametrize("question,category", [
    ("I think I might be pregnant", "pregnancy"),
    ("My uncle touched me and said to keep it secret", "abuse"),
    ("I have heavy bleeding and fainted", "serious_symptom"),
])
def test_sensitive_questions_are_routed_to_a_facilitator(modules, question, category):
    answer = LibraryIndex(modules).ask(question)
    assert answer.routed_to_facilitator
    assert category in answer.safety_categories


@pytest.mark.parametrize("question,source", [
    ("It burns when I pee", "care_seeking.faq[0]"),
    ("How do I dry my period cloth?", "menstrual_hygiene.faq[1]"),
    ("Why are my breasts sore?", "puberty_changes.faq[0]"),
    ("My discharge smells and itches", "care_seeking.faq[2]"),
])
def test_common_questions_find_the_right_answer(modules, question, source):
    assert LibraryIndex(modules).ask(question).source == source


def test_every_module_is_reachable(modules):
    scores = {}
    for _ in range(len(modules)):
        rec = next_module(modules, scores)
        if rec.module_id is None:
            break
        scores[rec.module_id] = 100
    assert set(scores) == set(modules)


def test_ordinary_question_is_not_flagged():
    assert not safety.check("Is white discharge normal?").flagged


def test_every_lesson_has_narration_and_media_files_exist():
    from openlibrary.content import MEDIA_KINDS, MEDIA_ROOT

    modules = load_library()
    for m in modules.values():
        for lesson in m.lessons:
            assert lesson.get("audio"), f"{lesson['id']} has no narration"
            for kind in MEDIA_KINDS:
                if lesson.get(kind):
                    assert (MEDIA_ROOT / lesson[kind]).is_file()
        video_lessons = [l for l in m.lessons if l["format"] == "video"]
        assert all(l.get("video") for l in video_lessons)
