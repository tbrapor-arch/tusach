# State (one small entry per module; newest facts only)

## Repository (17 Nov 2026)
Forked from Tsheh-tû `dict-all` df02bfe. Builds, lints, tests and click-tests on the test fixture only.
Next steps (handover section 9): 4 first full build with kaikki on the owner's machine, then `make coverage` →
5 a native speaker checks the cutter reference → 6 syllabus and first word list, wait for the owner → 7 lessons 1–7.

## Data sources (17 Nov 2026)
`data/fetch.sh` pins all of them (ATTRIBUTION.md). Fetched in the build sandbox: Thiều Chửu, Unihan kVietnamese,
rime-cantonese, MOE (moedict-data-twblg), CC-CEDICT, Tatoeba Challenge eng-vie test, FrequencyWords. **Not fetched**
(host refused from the sandbox): Wiktionary/kaikki and Tatoeba; the owner's machine and GitHub Actions fetch them.
kaikki's pin is a third-party hash (file of 2026-10-30); Tatoeba is unpinned until the first download.

## Database
`make db` works with any subset of sources and lists what is missing. Without kaikki it has no Vietnamese words but
the fixture: 11,787 Thiều Chửu readings (9,884 characters), rime/MOE/CEDICT readings, 3 bridge rows (fixture words). The Wiktionary
loader is tested only on a kaikki-shaped test file: check its counts on the first real build (it warns if no
`han-viet-reading` is found).

## Bridge and labels
Join on characters in `tools/bridge.py`, wired into the card and the Bridge tab (`*` = built by character).
False friends: `course/false_friends.tsv`, empty. Sound-correspondence drills: TODO(bridge).

## Word frequency and coverage
`tools/freq.py` ranks words (syllable frequencies divided by a segmented corpus). Coverage of the 3,000 most frequent
words (`make coverage`): NOT MEASURED yet, it needs the Wiktionary word list.

## Cutter
`tests/cutter/reference.tsv`: 200 sentences cut by Claude, **not checked by a native speaker**. F1 on it: underthesea
0.947; vi.cut() 0.920 with underthesea's Viet74K list as dictionary, 0.768 with the fixture database. To re-measure
with the Wiktionary keys once fetched. No module uses vi.cut() yet.

## Lessons
None. `course/syllabus.yaml`: syllabus and word list not approved. The build uses `tools/fixtures/lessons/00.yaml`.

## Audio
No source of word recordings (TODO(audio)); cards say "No recording yet". The native-speaker recording page
(`record.html`) and `tools/import_recordings.py` are kept; no clip.

## Private companion
`tusach-private` skeleton: loader contract and an empty module; no content. The repository name in the app's
`Exam.REPO` (`tbrapor-arch/tusach-private`) is a guess from Tsheh-tû's owner: confirm (TODO(repo)).

## Publishing
Not on GitHub yet. `app/published-card-ids.txt` and `app/published-english.tsv` are empty (no page published).
