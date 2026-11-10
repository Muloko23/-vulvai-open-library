# Contributing

We welcome organizations that want to adapt this library for their own communities.

## Adapting content

1. Copy a module in `library/modules/` and edit it, or add new language keys (for example `"hi"` for Hindi) to existing modules.
2. Set `review_status` to `draft` for any new or changed module.
3. Follow `docs/content_guidelines.md`: review with girls and families in your community, then have a qualified clinician verify the medical content before marking it `clinically_verified`.
4. Run `python -m openlibrary.cli validate` to check your changes.

## Changing code

1. Run `python -m pytest` and `node tests/engine_parity.test.js` before opening a pull request.
2. If you change the learning path, retrieval, or safety rules in Python, make the same change in `app/engine.js`. The parity test checks that both agree.
3. Run `python -m openlibrary.cli export` after any library change so the app bundle stays current.

## Safety changes

Changes to `openlibrary/safety.py` need review by a safeguarding lead. Never remove a safety category or phrase without that review.

## Contact

maria@vulvai.co
