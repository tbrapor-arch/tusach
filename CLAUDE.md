# Tủ sách — rules in force

A Vietnamese course app for one learner (English lessons; Cantonese, Mandarin and Taigi as a bridge). Forked from
Tsheh-tû. State: `docs/STATE.md`. Formats and tools: `docs/REFERENCE.md`. Past methods: `docs/HISTORY.md`.

## Fixed decisions
- Northern (Hà Nội) pronunciation. Lesson language: English.
- Lessons are written from scratch by Claude. A course book the owner owns goes to the private repository only.
- The owner approves the syllabus and the first word list before any lesson is drafted: `tools/lint.py` refuses
  any file in `course/lessons/` until both approvals are recorded in `course/syllabus.yaml`.
- Text is quốc ngữ in Unicode NFC. Word boundaries are written in the source (`học_sinh`), never guessed.
- Chữ Hán appear on word cards and in the bridge, never in lesson lines.

## The owner's standing preferences
- English on every word card.
- No display setting based on his Mandarin level.
- Complete, automatic solutions rather than partial manual ones.
- Exercise sentences are new, never taken from the lesson's own dialogue.
- A smooth growth in lines per lesson.
- Everything not checked by a native speaker is labelled so (lessons, course English).

## Rules enforced by code (do not work around them)
1. One word pipeline: every module (lessons, books, podcast, lists, private or public) cuts text and gets cards
   through `tools/cards.py`. No second cutter, no hand-built cards.
2. `make lint` runs `tools/lint.py` (0 errors) and `tools/verify_words.py` (read its suspect list).
3. Two databases: `make db` → `vi.db` for the public page, `make db-nc` → `vi-nc.db` for the private module.
   `cards.open_db()` refuses the wrong one. A non-commercial source has `commercial_ok: False`.
4. A partial build adds to the shared card file (`cards.Store.replace_module`). Never restore generated files.
5. The card check ends every build and runs on every push: no word without a card, no card lost, no card
   with poorer English. After publishing: `python3 tools/published_ids.py`, commit both `app/published-*` files.
6. Any change to the dictionary, the cutter or the pipeline: `python3 -I tools/compare.py run` before publishing.
   For anything risky, a second agent that did not do the work checks the result.
7. Data sources: pinned in `data/fetch.sh`, licence row in `ATTRIBUTION.md`, loader in `tools/build_db.py`
   (`SOURCES`), licence checked on its own page first. Never edit the database by hand.
8. The test fixture (`tools/fixtures/`) is not course content; a real lesson may not use a fixture-only word.

## Repository rules
- Public repo: code and Claude's own lessons. Copyrighted material (books, transcripts, recordings he owns) lives
  in the private companion `tusach-private`, loaded by the app with a token.
- Never commit `data/raw`, `data/build`, `app/dist`, `*.db`, or anything in `reference/`.
- Fixes shared with the other apps: `PORTING.md` (Tsheh-tû is the lead app).

## Working
- Parallel sessions collide: `git fetch` and merge before building, and say which commit your work includes.
- Run heavy steps one at a time; commit as you go.
- Four documents, kept apart and short: this file (under 60 lines), `docs/REFERENCE.md`, `docs/STATE.md` (one small
  entry per module), `docs/HISTORY.md`. The repository is the source of truth; the claude.ai project points here.
- Before a commit: `make lint`, `make test`, `make app`. After app or template changes: `make smoke`.
