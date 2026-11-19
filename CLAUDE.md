# Tủ sách — rules in force

A Vietnamese course app for one learner (English lessons; Mandarin, Cantonese and Taigi as a bridge). Forked from
Tsheh-tû. State: `docs/STATE.md`. Formats and tools: `docs/REFERENCE.md`. Past methods: `docs/HISTORY.md`.
**Priority (owner, 19 Nov 2026): Vietnamese first.** The Chinese bridge is a bounded help: Mandarin first; a bridge
remark is one or two lines on a word he knows; no more Cantonese / Taigi reading passes unless a card is plainly wrong.

## Fixed decisions
- Northern (Hà Nội) pronunciation. Lesson language: English.
- Lessons are written from scratch by Claude. A course book the owner owns goes to the private repository only.
- Syllabus, word lists 2 and 3 approved by the owner (19 Nov 2026, `course/syllabus.yaml`; lint refuses lessons without).
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
5. The card check ends every build and runs on every push: no word without a card, no card lost, no poorer English
   (lower rank; a gloss dropping senses needs `app/english-changes.tsv`); private beats public only if strictly better.
   After publishing: `python3 tools/published_ids.py`, commit both `app/published-*` files.
6. Any change to the dictionary, the cutter or the pipeline: `python3 -I tools/compare.py run` (pages and the real
   cards of the top 3,000 and all course words) before publishing; read the changed cards. For anything risky, a
   second agent that did not do the work checks the result.
7. Data sources: pinned by content in `data/fetch.sh` (unversioned ones through our snapshot release), licence row
   in `ATTRIBUTION.md`, loader in `tools/build_db.py` (`SOURCES`), licence checked on its own page first. A missing
   source fails `make db`; `TUSACH_ALLOW_MISSING=id,…` is for sandboxes only and makes the page unpublishable.
8. The test fixture (`tools/fixtures/`) is not course content; a real lesson may not use a fixture-only word;
   `fixture: true` counts only there; only test databases load it (`build_db --fixture`). Only `NN.yaml` in lessons.
9. Word boundaries follow `docs/SEGMENTATION.md`; tone marks and spellings (lý do, not lí do) follow the house style (lint).
10. The course lexicon `course/lexicon.tsv` (Claude's, not native-checked; honest `doubt`) decides a word's English,
   sense, origin, characters, notes and example; readings come from the database. Lint refuses a conflict with the
   data (each English item, characters vs etymology, "X only") unless overridden with a reason.
11. `make test` checks the cards against `tests/golden/cards.tsv` (reviewed snapshot of what the learner sees);
   after a deliberate change, `tools/test_golden.py --write` and read the diff.
12. One plan source: `course/syllabus.yaml` + word list, `tools/plan.py --write` makes the rest; notes and planned
   grammar use taught words or a `{preview}`; rule numbers only from `tools/bridge_rules.py --write`.

## Repository rules
- Public repo: code and Claude's own lessons; what he owns (books, transcripts, recordings) goes to `tusach-private`.
- Never commit `data/raw`, `data/build`, `app/dist`, `*.db`, `reference/`. Shared fixes: `PORTING.md` (Tsheh-tû leads).

## Working
- Parallel sessions collide: `git fetch` and merge before building; say which commit your work includes; run heavy
  steps one at a time; commit as you go.
- Four documents, kept apart and short: this file (under 60 lines), `docs/REFERENCE.md`, `docs/STATE.md` (one small
  entry per module), `docs/HISTORY.md`. The repository is the source of truth.
- Before a commit: `make lint`, `make test`, `make app`. After app or template changes: `make smoke`.
