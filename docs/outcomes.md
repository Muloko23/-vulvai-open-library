# Outcome Measurement

The study asks one question: when girls learn about their bodies, what changes?

## Six outcomes

| Outcome | How it is measured | Validated instrument to align with during adaptation |
| --- | --- | --- |
| Comfort with body and period | Survey domain `comfort` | Menstrual Practice Needs Scale (MPNS) |
| Confidence and self worth | Survey domain `confidence` | Rosenberg Self Esteem Scale (validated Hindi version) |
| Feeling safe | Survey domain `safety` | Global Early Adolescent Study agency and safety measures |
| Self advocacy | Survey domain `self_advocacy` | Global Early Adolescent Study voice measures |
| Ability to act on health information | Survey domain `health_action` | Health Literacy Assessment Scale for Adolescents (HAS A) |
| Body knowledge | Percent correct on curriculum quiz items | Curriculum specific knowledge test |

The draft items in `outcomes/survey.json` are written for cognitive testing with the youth advisory group. During months 1 to 2 of the pilot, each domain will be aligned with or supplemented by the validated instrument listed above, translated into Hindi and local dialects, back translated, and pilot tested, subject to each instrument's license.

## Administration

* Facilitators read each item aloud or play it as audio. Girls answer on a four point picture scale.
* The survey is given at enrollment and at the end of the program.
* Quiz answers collected during lessons feed the body knowledge score.

## Scoring

`openlibrary/outcomes.py` scores each domain from 0 to 100, flips reverse scored items, never treats missing answers as zero, and computes individual change from pre to post.

## Reporting and privacy

Cohort summaries report mean pre, post, and change scores for each outcome. Results are suppressed for any group smaller than ten girls so no individual can be identified.
