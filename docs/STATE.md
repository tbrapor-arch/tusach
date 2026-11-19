# State (one small entry per module; newest facts only)

## Numbers (printed by `tools/state.py --write`; `make test` fails when they drift)
<!-- state:numbers -->
- Course lexicon: 669 rows (doubt 16, likely 116, sure 537; 53 with an override; 463 with an example written by Claude); golden cards: 685.
- Top 1,000 cards, labels: same 385, gram 7, hv-vn 13, doubtful 12, opaque 18, older-loan 111, loan 9, native 200, compound 111, false-friend 10, unknown 124.
- Cards showing chữ Hán (Hán-Việt analysis) among the top 1,000 / 3,000 / 5,000: 433 / 1499 / 2570.
- Taigi: 180 characters with a reading found colloquial (coda class or 麻 rhyme).
- Word list 2 (L1–13): 207 words + 3 names (L1 16, L2 16, L3 18, L4 18, L5 17, L6 17, L8 16, L9 17, L10 18, L11 18, L12 18, L13 18); Hán-Việt 38 (18 %), older Chinese loans 28 (6 with a doubtful etymon, characters hidden), other loans (French and others) 2, the rest native, compounds and 41 with no etymology recorded. Word list 3 (L15–27): 221 words + 0 names (L15 18, L16 18, L17 18, L18 18, L19 18, L20 18, L22 18, L23 19, L24 19, L25 19, L26 19, L27 19); Hán-Việt 65 (29 %), older Chinese loans 32 (3 with a doubtful etymon, characters hidden), other loans (French and others) 6, the rest native, compounds and 34 with no etymology recorded.
- Sound rules: 993 syllables (character + Hán-Việt reading) of 1499 Hán-Việt cards of rank <= 3000. 132 measured: 91 rules, 14 tendencies, 16 that narrow the choice, 2 facts of spelling, 9 dropped. Every tone from Cantonese: main 910 / 993, 92 %, strict 797 / 993, 80 %; from Taigi: main 878 / 959, 92 %, strict 853 / 959, 89 %.
<!-- /state -->

## Repository (19 Nov 2026)
`main` has the owner's approvals, reviews 3–6 (HISTORY) and lessons 0–14 (branches `lessons-01-07`, merged after
review 5, and `lessons-08-14`, merged after review 6). From a clean
clone with nothing missing, `make data db db-nc lint test app check` and `tools/smoke.py` (with TUSACH_PRIVATE)
pass; `make lint` also checks the plan, the draft word list and the proposal. Word list 3 (L15–27, 221 words) is
APPROVED by the owner on 19 Nov 2026 (`course/proposal/wordlist-3.tsv`, listed with list 2 in approved.word_list.file;
notes in `wordlist-3-NOTES.md`, doubts in `wordlist-3-to-check.md`). Next steps: lessons 15–28 (branch
`lessons-15-28`); a native speaker, when one is found, reads NOTES-for-native-speaker.md (the two lists of eight first),
wordlist-2-to-check.md (18 points), the lexicon's examples and the cutter sets.

## Data sources (18 Nov 2026)
`data/fetch.sh` pins every source by content (ATTRIBUTION.md). kaikki (Wiktionary), Tatoeba and the English
Wiktionary's translation tables (`en-translations.tsv.gz`, derived on the runner) come from our snapshot release
`data-2026-11-18.2` (NOTES.md: upstream URLs, workflow run). The Vietnamese Wiktionary extract is no longer fetched or
snapshotted (the old release still carries it, licence unverified: the owner may delete the asset). Unihan adds kSemanticVariant/kZVariant (same commit).

## Database
Wiktionary: 35,526 entries (29,349 keys; 3,025 names), 10,793 keys with chữ Hán, 905 older borrowings read the
non-Hán-Việt way (origin nonhv) and 38 Sino-Vietnamese analyses read with a Nôm reading, now older loans. Hán-Việt readings for 10,618 characters (2,099 tagged by
Wiktionary). Suspects in `make lint` (verify_words): 350. Tatoeba: 22,181 sentence pairs used; 45,475 example candidates on 6,093 words (flagged:
unsuitable, Southern, misaligned, unknown word…), the card chooses by sense; a lexicon example wins.

## Cards (branch data-quality, 18 Nov 2026)
Three layers (REFERENCE): the course lexicon `course/lexicon.tsv` (Claude's, NOT native-checked; English, sense,
origin, characters, notes, and an example for every word of word list 2 and 44 frequent cards), the dictionary for
other words, the golden snapshot of everything a card shows (550 cards) and the real-card compare. Counts: the
generated block above. Against 16c8b24 (Claude's reading of the word-list and top-300 cards): examples 175 better,
84 neutral, 0 worse; readings better on 行 數 適 錢 轉 現 屬, worse on 句 câu, 省 tỉnh, 襖 áo (irregular). Review 4 (against 55607b8, `compare.py` now also reads origins and readings): 60 origin lines
with their form or a correct kind (lăm an alteration of năm; ancestors never cognates), 襖 no longer read via 澳
(`bridge.same_sound`); Cantonese ou3 before ou2 on áo kept (the measured fit; the HV tone is irregular).

## Bridge and labels
Join on characters in `tools/bridge.py`: Taigi literary reading with the colloquial word reading apart (coda rule
and 麻 rhyme; "layer not marked by the MOE" where no rule decides); Hán-Việt readings by use, Northern first, never a
Nôm-only reading (38 Nôm-read analyses are older loans); a card orders a polyphonic character's readings by
measured fit with its syllable and the source's preference (tools/soundfit.py: 93 of the first 100 polyphonic
one-character cards right in both languages, Claude's judgement). False friends: the lexicon's false_friend column.
Sound rules: `tools/bridge_rules.py` (main / strict / lenient rates; numbers above and in the proposal). Drills:
TODO(bridge).

## Word frequency and coverage
Ranks: `tools/freq.py` (vi.cut() over Tatoeba + Wiktionary examples, wordfreq prior less English leakage; names
sharing a key with a lower-case word unranked; common word + name and 4+-syllable keys unranked); spoken particles and
food words under-ranked (vâng 3663, ạ 1257, nhỉ 2207, phở 12139): the syllabus decides what is taught. `make coverage`: Hán-Việt characters on
the card top 1,000 / 3,000 / 5,000: 439 / 1,510 / 2,584; "same word" 387 / 1,263 / 2,087.

## Cutter
F1 with the Wiktionary keys: reference (200, rules tuned on it) vi.cut() 0.955, underthesea 0.929; held-out (100 Tatoeba
sentences, `tests/cutter/heldout.tsv`) vi.cut() 0.953, underthesea 0.928. Both sets cut by Claude, **not checked by a
native speaker**.

## Lessons (19 Nov 2026; 1–7 after review 5, 8–14 after review 6, in main)
Lesson 0 "Reading Vietnamese" (`course/lesson0.yaml`, page `#reading`): alphabet, IPA and nearest sounds, Hà Nội
mergers, finals (-nh/-ch, the lip rule), six tones in one line each, checked syllables; no audio (the page says so);
its sound-table examples are checked against their row. Lessons 1–7 (`course/lessons/01–07.yaml`, 7 a review):
lines 7 7 7 7 8 8 9, notes 9 each, new words 16 16 18 18 17 17 0 + names Sacha, Lan, Thảo, Minh, Bin, Na; all from
word list 2, each word (lines, exercises, notes, glosses) taught before use (lint). NOT checked by a native speaker
(labelled in the app); open questions, the reviewer's eight first: `course/lessons/NOTES-for-native-speaker.md`.
Lessons 8–14 (19 Nov 2026, after review 6; 14 a review): lines 8 8 8 9 9 9 10, notes 9
each (one false-friend clause in L11 and L12), new words 16 17 18 18 18 18 0 + name Mai, exactly word list 2's; the week after lesson 7 (Tuesday walk to Hoàn
Kiếm with Thảo … Sunday birthday of Lan's mother); their points for a native speaker in the same file.
`course/syllabus.yaml`: the one plan source (100 lessons, cast, particle strand), syllabus and word list 2 APPROVED
by the owner on 19 Nov 2026. Proposal: `course/proposal/syllabus-proposal.md`; `wordlist-2.tsv` and its to-check list.

## Audio
No source of word recordings (TODO(audio)); cards say "No recording yet". The native-speaker recording page
(`record.html`) and `tools/import_recordings.py` are kept; no clip.

## Private companion
`tusach-private`: loader contract with neutral names (module/, window.PrivateModule, `#private`), merge rule (no
poorer card over a public one), cards built with the course words; no content. Repository `tbrapor-arch/tusach-private`.

## Publishing
Not deployed yet: GitHub Pages is not enabled for the repository (the "Build and publish the app" workflow builds,
then fails at deploy-pages). `app/published-card-ids.txt` and `app/published-english.tsv` are empty and are to be
written (`python3 tools/published_ids.py`, both files committed) after the first successful deploy, not before.
