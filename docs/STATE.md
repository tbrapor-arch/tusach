# State (one small entry per module; newest facts only)

## Repository (18 Nov 2026)
First real build (18 Nov 2026): every source pinned and fetched, `make db db-nc lint test app check` passes
from a clean clone with nothing missing (cold fetch 28 s, build and checks 1 min 38 s in the sandbox). Not pushed yet
at the time of writing. Next steps: a native speaker checks the cutter sets → syllabus and first word list, wait for
the owner → lessons 1–7.

## Data sources (18 Nov 2026)
`data/fetch.sh` pins every source by content (ATTRIBUTION.md). kaikki (Wiktionary), Tatoeba and the English
Wiktionary's translation tables (`en-translations.tsv.gz`, derived on the runner) come from our snapshot release
`data-2026-11-18.2` (NOTES.md: upstream URLs, workflow run). The Vietnamese Wiktionary extract is fetched for evaluation
only (licence unverified on a primary page). Unihan adds kSemanticVariant/kZVariant (same commit).

## Database
Wiktionary: 35,526 entries (29,349 keys; 3,025 names), 10,793 keys with chữ Hán (10,674 matching their syllables),
905 older borrowings read the non-Hán-Việt way (origin nonhv). Hán-Việt readings for 10,618 characters (2,099 tagged by
Wiktionary). Suspects in `make lint`: 115 analyses not matching the syllables, 16 characters with no reading. Tatoeba:
22,181 sentence pairs used, 10,040 examples on 6,138 words.

## Data quality (branch data-quality, 18 Nov 2026)
Spelling groups 688 (379 i/y; house spelling y in 344); card English composed from Wiktionary senses + translation
evidence: unusable English (tools/english.py) top 1,000 225 -> 49, word list 1 34 -> 5; labels on the top 1,000 cards:
same 372, hv-vn 10, opaque 47, doubtful 6, older-loan 110, loan 12, native 229, compound 55, unknown 157 (was 416).
Taigi: 187 unmarked MOE readings found colloquial (163 characters colloquial only). Details: REFERENCE, HISTORY.

## Bridge and labels
Join on characters in `tools/bridge.py`: Taigi literary reading (literary MOE readings only when a character has one)
with the colloquial word reading apart; Hán-Việt readings by use, Northern first; Unihan variants (120 rows). 11,046
spellings: 3 readings 10,509, 2 518, 1 6, 0 13. False friends: `course/false_friends.tsv`, empty. Sound-correspondence
drills: TODO(bridge).

## Word frequency and coverage
Ranks: `tools/freq.py` (vi.cut() over Tatoeba + Wiktionary examples, wordfreq prior less English leakage: the 247 ->
6732, in 240 -> 335; names sharing a key unranked); known junk: Wikipedia words. `make coverage`: Hán-Việt characters on
the card top 1,000 / 3,000 / 5,000: 435 / 1,487 / 2,539 (was 436 / 1,453 / 2,470); "same word" 372 / 1,221 / 2,012.

## Cutter
F1 with the Wiktionary keys: reference (200, rules tuned on it) vi.cut() 0.955, underthesea 0.930; held-out (100 Tatoeba
sentences, `tests/cutter/heldout.tsv`) vi.cut() 0.955, underthesea 0.928. Both sets cut by Claude, **not checked by a
native speaker**.

## Lessons
None. `course/syllabus.yaml`: syllabus and word list not approved. Proposal in course/proposal/ (word list 1
regenerated from the cards; glosses-proposed.tsv not in force). The build uses `tools/fixtures/lessons/00.yaml`.

## Audio
No source of word recordings (TODO(audio)); cards say "No recording yet". The native-speaker recording page
(`record.html`) and `tools/import_recordings.py` are kept; no clip.

## Private companion
`tusach-private`: loader contract with neutral names (module/, window.PrivateModule, `#private`), merge rule (no
poorer card over a public one), cards built with the course words; no content. Repository `tbrapor-arch/tusach-private`.

## Publishing
Not on GitHub yet. `app/published-card-ids.txt` and `app/published-english.tsv` are empty (no page published).
