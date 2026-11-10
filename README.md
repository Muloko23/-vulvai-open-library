# VULVAi Open Library

An open source, AI assisted sexual and reproductive health learning platform for adolescent girls and young women, cocreated with the communities it serves.

The first deployment is in rural Rajasthan, India, led by **B.Bindi** (applicant) with **Bindi International** (community and education partner) and **VULVAi** (technology and clinical partner).

## VULVAi's first open source model

VULVAi builds AI powered education and diagnostic tools for vulvovaginal and pelvic health. Its core platform, proprietary clinical algorithm, and research repository were built for clinicians and patients in the United States and remain proprietary.

This repository is VULVAi's first open source model. Content built for the United States does not translate directly to other communities, so this project builds a separate, open library and engine with the community it serves, making it culturally competent as well as medically accurate.

## Built to be reproduced worldwide

Rajasthan is the first site. The model is designed to be repeated by any community organization, anywhere girls lack accurate information about their bodies:

1. **Partner** with a trusted local organization that already works with girls and families.
2. **Listen** to a youth advisory group of local girls and mothers.
3. **Adapt** stories, images, examples, and languages with the community.
4. **Verify** every lesson with clinicians and add local referral information.
5. **Launch** on shared phones with trained local facilitators.
6. **Measure and share** the same six outcomes, and contribute adapted lessons back to the open library.

The medical core is reused everywhere, so each new site adapts how lessons are told rather than rebuilding what they say. Every site adds languages and stories to the library and data to a shared evidence base, making each new launch faster than the last. See `docs/replication_playbook.md`.

## Why this exists

Most girls in rural Rajasthan reach puberty without accurate information about their own bodies. Existing digital health content is rarely available in local languages, is not built for low literacy, and is not designed with the girls who use it. This project builds an open library and learning platform that any community organization can adapt, while keeping every lesson medically accurate.

## What is open and what is not

| Component | Status |
| --- | --- |
| Lesson library (text, scripts, story cards, quizzes, audio, video, illustrations) | Open, CC BY 4.0 |
| Content schema and authoring guidelines | Open, CC BY 4.0 |
| Learning path engine (this repository) | Open, MIT |
| Library retrieval for private questions (this repository) | Open, MIT |
| Safety routing (this repository) | Open, MIT |
| Outcome measurement toolkit (survey and scoring) | Open, CC BY 4.0 and MIT |
| Offline learning app (Know My Body) | Open, MIT |
| VULVAi's US clinical repository, proprietary clinical algorithm, and diagnostic frameworks | Proprietary, not included |

## How it works

```
Girl on shared phone or in a facilitated session
        |
        v
 Learning path engine  ---> selects next lesson from quiz results
        |
        v
 Lesson library (audio, video narration, story cards, quizzes)
        |
 Private question  ---> Safety router ---> flagged: refer to trained facilitator
        |                       |
        |                       v
        |              not flagged: Library retrieval
        |                       |
        v                       v
 Answer drawn only from the clinician verified library, never generated freely
```

Key design rules:

1. **No open ended chatbot.** Answers to private questions come only from verified library entries. If no entry matches, the platform says so and suggests talking to a facilitator.
2. **Safety first.** Questions that signal abuse, pregnancy, self harm, or a serious symptom are never answered automatically. They are routed to a trained facilitator.
3. **Clinical review gate.** Content is marked `draft`, `community_reviewed`, or `clinically_verified`. Only `clinically_verified` content is served to girls in production.
4. **Offline first.** The library is plain JSON so it can be bundled onto shared devices and synced when a connection is available.
5. **Localizable.** Every learner facing string supports multiple languages. Hindi and local dialect versions are produced with community translators and reviewed by facilitators and clinicians.

## Curriculum

Eight starter modules cover the core of body literacy:

| Level | Module | Topic |
| --- | --- | --- |
| 1 | Knowing my body | Anatomy and correct names |
| 2 | How my body changes | Puberty |
| 2 | Understanding my period | Menstruation |
| 2 | My body, my choice | Consent |
| 2 | My feelings matter | Emotions and self worth |
| 3 | Caring for myself during my period | Menstrual hygiene |
| 3 | Staying safe and getting help | Safety and trusted adults |
| 3 | When and where to get care | Warning signs and care seeking |

Each module combines audio, video, story cards, case scenarios, or group activities with a quiz and verified answers for private questions.

## Multimedia lessons

Many girls in the pilot read little or share a phone with a family, so every lesson works by listening and looking, not only reading.

| Media | What it is | Count |
| --- | --- | --- |
| Narration | Every lesson has spoken audio, so girls can listen in a group or alone | 16 lessons |
| Video | Short narrated explainers with one illustrated scene and a caption per sentence | 2 lessons (puberty, periods) |
| Illustrations | Scenes set in a Rajasthani village for every story card, case scenario, and group activity | 8 lessons |

All media ship inside the app and are cached on the phone, so lessons play with no connection. Videos are about 500 KB each.

The media in this repository are **prototype drafts**. Narration for the puberty video, the period video, and Sunita's story is recorded by Dr. Maria Uloko, founder of VULVAi, and lives in `library/media/recordings/` with one file per sentence. The remaining lessons use draft narration from an open text to speech model (Kokoro, Apache 2.0), and illustrations are generated from code in `tools/`. In the pilot, local women record narration in Hindi and local dialects, local illustrators adapt characters and settings, and the youth advisory group approves every image and video before release. Any community replicating the model can regenerate drafts in its own language with the same tools, then replace them with locally made media.

```bash
python tools/illustrations.py                                   # draw story and scenario scenes
python tools/make_audio.py --model kokoro-v1.0.int8.onnx --voices voices-v1.0.bin
python tools/make_video.py                                      # rebuild videos from human recordings
```

## Repository layout

```
app/                     Know My Body offline web app (works on shared phones)
library/
  schema.json            Content schema for lessons
  modules/               Lesson modules (sample content, pending review)
  media/                 Narration (audio), explainer videos (video), illustrations (images)
outcomes/
  survey.json            Pre and post survey for the six study outcomes
openlibrary/
  content.py             Load and validate the library
  pathway.py             Rules based learning path engine
  retrieval.py           Answers questions only from library entries
  safety.py              Safety routing for sensitive questions
  outcomes.py            Outcome scoring and anonymized cohort reports
  records.py             Pseudonymous learner records and offline sync queue
  cli.py                 Command line tools
docs/
  architecture.md        Technical architecture
  content_guidelines.md  Cocreation and clinical review workflow
  facilitator_guide.md   Session guide and referral steps for facilitators
  outcomes.md            Study outcomes and instruments
  replication_playbook.md  How any community can launch its own version
  safety.md              Safeguarding and data protection approach
tools/                   Draft media generators (illustrations, narration, video)
tests/                   Python tests and app engine parity test
```

## Quick start

Requires Python 3.10 or later. The engine has no external dependencies.

```bash
python -m openlibrary.cli validate          # check every lesson against the schema
python -m openlibrary.cli path --scores body_basics=90 menstruation_basics=40
python -m openlibrary.cli ask "Is it normal for my period to be late?"
python -m pytest                            # run the tests (pytest required)
```

Run the offline app:

```bash
python -m openlibrary.cli export            # bundle the library and its media into app/
cd app && python -m http.server 8000        # then open http://localhost:8000
```

Once opened, the app caches itself and keeps working with no connection. Progress is stored only on the device, under a random learner code.

## Status

This is the starting point for the UNICEF Femtech Ventures pilot. Sample lessons are drafts written for demonstration and are **not yet clinically verified**. During months 1 to 4 of the pilot, a youth advisory group, Bindi International facilitators, and VULVAi clinicians will cocreate and verify the full library.

## Partners

* **B.Bindi**: applicant; reaches families through women led self help groups in Rajasthan.
* **Bindi International**: runs Digital Community Schools and trains women facilitators in Rajasthan.
* **VULVAi**: technology and clinical partner; builds the platform and verifies medical accuracy. Contact: maria@vulvai.co

## License

Code is released under the MIT License (see `LICENSE`). Library content and documentation are released under Creative Commons Attribution 4.0 (see `CONTENT_LICENSE.md`).
