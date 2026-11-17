# State (one small entry per module; newest facts only)

## Repository (18 Nov 2026)
First real build (18 Nov 2026): every source pinned and fetched, `make db db-nc lint test app check` passes
from a clean clone with nothing missing (cold fetch 28 s, build and checks 1 min 38 s in the sandbox). Not pushed yet
at the time of writing. Next steps: a native speaker checks the cutter sets → syllabus and first word list, wait for
the owner → lessons 1–7.

## Data sources (18 Nov 2026)
`data/fetch.sh` pins every source by content (ATTRIBUTION.md). kaikki (Wiktionary) and Tatoeba come from our snapshot
release `data-2026-11-17` (NOTES.md: upstream URLs, workflow run). Unihan adds kSemanticVariant/kZVariant (same commit).

## Database
Wiktionary: 35,526 entries (29,349 keys; 3,025 names), 10,793 keys with chữ Hán (10,674 matching their syllables),
905 older borrowings read the non-Hán-Việt way (origin nonhv). Hán-Việt readings for 10,618 characters (2,099 tagged by
Wiktionary). Suspects in `make lint`: 115 analyses not matching the syllables, 16 characters with no reading. Tatoeba:
22,181 sentence pairs used, 10,040 examples on 6,138 words.

## Bridge and labels
Join on characters in `tools/bridge.py`: Taigi literary reading (literary MOE readings only when a character has one)
with the colloquial word reading apart; Hán-Việt readings by use, Northern first; Unihan variants (120 rows). 11,046
spellings: 3 readings 10,509, 2 518, 1 6, 0 13. False friends: `course/false_friends.tsv`, empty. Sound-correspondence
drills: TODO(bridge).

## Word frequency and coverage
Ranks: `tools/freq.py` (vi.cut() over Tatoeba + Wiktionary examples, wordfreq prior); known junk: the, in (English
in the counts), names, Wikipedia words. `make coverage`, top 3,000: Hán-Việt analysis on the card 1,453 (48.4 %), all
three Chinese readings 98.6 % of them; Sino-Vietnamese share 38 % in ranks 1–500, about 50 % from 1,000 on.

## Cutter
F1 with the Wiktionary keys: reference (200, rules tuned on it) vi.cut() 0.955, underthesea 0.930; held-out (100 Tatoeba
sentences, `tests/cutter/heldout.tsv`) vi.cut() 0.955, underthesea 0.928. Both sets cut by Claude, **not checked by a
native speaker**.

## Lessons
None. `course/syllabus.yaml`: syllabus and word list not approved. The build uses `tools/fixtures/lessons/00.yaml`.

## Audio
No source of word recordings (TODO(audio)); cards say "No recording yet". The native-speaker recording page
(`record.html`) and `tools/import_recordings.py` are kept; no clip.

## Private companion
`tusach-private`: loader contract with neutral names (module/, window.PrivateModule, `#private`), merge rule (no
poorer card over a public one), cards built with the course words; no content. Repository `tbrapor-arch/tusach-private`.

## Publishing
Not on GitHub yet. `app/published-card-ids.txt` and `app/published-english.tsv` are empty (no page published).
