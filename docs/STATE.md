# State (one small entry per module; newest facts only)

## Repository (18 Nov 2026)
Branch `data-quality` (pushed; not merged): from a clean clone with nothing missing, `make data db db-nc lint test app
check coverage cutter` and `tools/smoke.py` (with TUSACH_PRIVATE) pass (data 34 s, each database ~80 s, test 165 s).
Next steps: a native speaker reads the lexicon's doubts (course/proposal/wordlist-1-to-check.md) and the cutter sets
→ syllabus revision and word list → the owner's approval → lessons 1–7.

## Data sources (18 Nov 2026)
`data/fetch.sh` pins every source by content (ATTRIBUTION.md). kaikki (Wiktionary), Tatoeba and the English
Wiktionary's translation tables (`en-translations.tsv.gz`, derived on the runner) come from our snapshot release
`data-2026-11-18.2` (NOTES.md: upstream URLs, workflow run). The Vietnamese Wiktionary extract is no longer fetched or
snapshotted (the old release still carries it, licence unverified: the owner may delete the asset). Unihan adds kSemanticVariant/kZVariant (same commit).

## Database
Wiktionary: 35,526 entries (29,349 keys; 3,025 names), 10,793 keys with chữ Hán (10,674 matching their syllables),
905 older borrowings read the non-Hán-Việt way (origin nonhv). Hán-Việt readings for 10,618 characters (2,099 tagged by
Wiktionary). Suspects in `make lint` (verify_words): 259 (148 analyses whose readings differ, 112 of another length, 20
characters with no reading…). Tatoeba: 22,181 sentence pairs used; 45,475 example candidates on 6,093 words (473
flagged), the card chooses by sense.

## Cards (branch data-quality, 18 Nov 2026)
Three layers (REFERENCE): the course lexicon `course/lexicon.tsv`, 508 rows (doubt 14, likely 86, sure 408; 4
overrides; 0 open conflicts), Claude's, NOT native-checked; the dictionary for other words; the golden check (524
cards) and the real-card compare. Top 1,000 cards: English not usable 33 (was 49 at fa4d343, 225 at dcaf84f); labels
same 387, gram 7, hv-vn 13, doubtful 11, opaque 20, older-loan 111, loan 9, native 200, compound 111, false-friend 8,
unknown 123. Spelling groups: orthographic only. Top 300 read against fa4d343: 118 better, 172 neutral, 10
unchanged, 0 worse; against dcaf84f: 100 better, 193 neutral, 7 unchanged, 0 worse (Claude's reading).

## Bridge and labels
Join on characters in `tools/bridge.py`: Taigi literary reading (literary MOE readings only when a character has one)
with the colloquial word reading apart (167 characters colloquial by the coda rule, 149 colloquial only); Hán-Việt
readings by use, Northern first; Unihan variants (195 rows). 12,347 spellings: 3 readings 11,239, 2 1,024, 1 60, 0 24.
False friends: the lexicon's false_friend column (bác sĩ, thời tiết, bản đồ, trường, quận, đầu tiên…). Sound-correspondence
drills: TODO(bridge).

## Word frequency and coverage
Ranks: `tools/freq.py` (vi.cut() over Tatoeba + Wiktionary examples, wordfreq prior less English leakage; names
sharing a key with a lower-case word unranked; common word + name and 4+-syllable keys unranked); spoken particles and
food words under-ranked (vâng 3663, ạ 1257, nhỉ 2207, phở 12139): the syllabus decides what is taught. `make coverage`: Hán-Việt characters on
the card top 1,000 / 3,000 / 5,000: 439 / 1,510 / 2,584; "same word" 387 / 1,263 / 2,087.

## Cutter
F1 with the Wiktionary keys: reference (200, rules tuned on it) vi.cut() 0.955, underthesea 0.930; held-out (100 Tatoeba
sentences, `tests/cutter/heldout.tsv`) vi.cut() 0.953, underthesea 0.928. Both sets cut by Claude, **not checked by a
native speaker**.

## Lessons
None. `course/syllabus.yaml`: syllabus and word list not approved. Proposal in course/proposal/ (word list 1
regenerated from the cards with sense tags; its to-check list = the lexicon's doubts and overrides; the syllabus
revision, with the essentials review 2 found missing, is the next task). The build uses `tools/fixtures/lessons/00.yaml`.

## Audio
No source of word recordings (TODO(audio)); cards say "No recording yet". The native-speaker recording page
(`record.html`) and `tools/import_recordings.py` are kept; no clip.

## Private companion
`tusach-private`: loader contract with neutral names (module/, window.PrivateModule, `#private`), merge rule (no
poorer card over a public one), cards built with the course words; no content. Repository `tbrapor-arch/tusach-private`.

## Publishing
Not on GitHub yet. `app/published-card-ids.txt` and `app/published-english.tsv` are empty (no page published).
