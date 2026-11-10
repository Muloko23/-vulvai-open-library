# Architecture

## Overview

The platform has four AI and data components, each designed so that a girl only ever receives clinician verified information.

| Component | Purpose | Pilot implementation | Production path |
| --- | --- | --- | --- |
| Learning path engine | Selects each girl's next lesson | Transparent rules on quiz scores and prerequisites (`pathway.py`) | Rules informed by VULVAi's clinical categorization work, tuned with pilot outcome data |
| Library retrieval | Answers private questions | BM25 ranking over verified FAQ entries (`retrieval.py`) | Multilingual embeddings for Hindi and local dialects; answers still returned only from verified entries |
| Safety routing | Sends sensitive questions to a human | Keyword baseline across abuse, pregnancy, self harm, serious symptoms, and early marriage (`safety.py`) | Classifier trained on community reviewed examples, with the keyword baseline kept as a fallback |
| Speech and translation | Produces audio and narration | Not in this repository | Translation and speech models draft Hindi and dialect audio; facilitators and clinicians review every file before release |

## Principles

1. **Retrieval, never free generation.** The platform does not run an open ended chatbot. Every answer is a verified library entry. If no entry matches with confidence, the girl is directed to a facilitator.
2. **Human in the loop.** Facilitators receive every flagged question. Clinicians verify every lesson and answer before release.
3. **Review gate in code.** `load_library(min_status="clinically_verified")` is used in production, so unverified content cannot reach learners.
4. **Offline first.** Modules are plain JSON and media files that can be preloaded onto shared phones. Quiz results and questions are queued on the device and synced when a connection is available. Private questions that need retrieval are answered on the device from the bundled index.
5. **Minimal data.** The platform stores a pseudonymous learner ID, quiz scores, module completion, and flagged question records. It does not collect names, phone numbers, or location from girls.

## Data flow

1. A facilitator registers a girl with a pseudonymous ID during a session at a Digital Community School.
2. The girl completes lessons and quizzes on a shared phone or in a group session.
3. Quiz scores update her learning path.
4. Private questions pass through safety routing, then retrieval.
5. Flagged questions create a follow up task for a trained Bindi International facilitator.
6. Anonymized scores feed the outcome measurement toolkit for the study.

## Relationship to VULVAi's proprietary platform

VULVAi's US clinical repository, proprietary clinical algorithm, and diagnostic frameworks are not part of this repository. This open library is a new, separate code base and content set built for community deployment and released under open licenses.
