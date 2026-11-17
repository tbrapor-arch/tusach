# State (one small entry per module; newest facts only)

## Repository (17 Nov 2026)
Forked from Tsheh-tû `dict-all` df02bfe. Builds, lints, tests and click-tests on the test fixture only.
Next steps (handover section 9): 3 verify source licences → 4 build the database and the bridge join, measure
coverage → 5 cutter test (200 hand-cut sentences) → 6 syllabus and first word list, wait for the owner → 7 lessons 1–7.

## Data sources
None. `SOURCES` in `tools/build_db.py` and `data/fetch.sh` are empty on purpose (licences being verified by another
session). The database holds the test fixture only (9 entries).

## Lessons
None. `course/syllabus.yaml`: syllabus and word list not approved. The build uses `tools/fixtures/lessons/00.yaml`.

## Word cards and bridge
Card model in place (word, audio, English, chữ Hán + Jyutping / Tâi-lô / pinyin, label, example). Bridge tab: a table
of the Hán-Việt cards; the sound-correspondence drills are not built (TODO(bridge)).

## Audio
No source of word recordings (TODO(audio)); cards say "No recording yet". The native-speaker recording page
(`record.html`) and `tools/import_recordings.py` are kept; no clip.

## Cutter for texts without boundaries
`vi.cut()`: longest dictionary match, up to 4 syllables. Not measured (TODO(cutter), handover step 5). No module uses it.

## Private companion
`tusach-private` skeleton: loader contract and an empty module; no content. The repository name in the app's
`Exam.REPO` (`tbrapor-arch/tusach-private`) is a guess from Tsheh-tû's owner: confirm (TODO(repo)).

## Publishing
Not on GitHub yet. `app/published-card-ids.txt` and `app/published-english.tsv` are empty (no page published).
