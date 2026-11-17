# Reference: formats and tools

## Layout
```
course/lessons/NN.yaml   lessons (none yet: the syllabus and word list wait for the owner's approval)
course/syllabus.yaml     the plan and the owner's approvals (lint refuses lessons without them)
course/glosses_en.tsv    English written for words that are not in a lesson's new_words
course/false_friends.tsv hand-curated false friends (word, chữ Hán, note); empty; format in its header
tools/                   build, pipeline, checks (MIT)
tools/fixtures/          TEST FIXTURE: dict.yaml (9 invented entries), lessons/00.yaml (3 lines), raw/ (a kaikki-shaped
                         file for tools/test_db.py); not content
tests/cutter/            reference.tsv: 200 sentences cut by hand, NOT checked by a native speaker
data/fetch.sh            open sources pinned by content (ATTRIBUTION.md); a missing one fails (TUSACH_ALLOW_MISSING)
data/fetch-lib.sh        its functions: fetch (clean git checkout), get (SHA-256), snap (our release), npmpkg
data/snapshot-request.txt  a commit changing it runs .github/workflows/snapshot.yml (tools/pin_snapshot.py TAG)
data/build/              generated, never committed: vi.db, vi-nc.db, cards.json
requirements-build*.txt  build-time packages (wordfreq, underthesea), locked with hashes; CI installs them
app/                     page template, recording page, PWA files, embedded font; app/dist/ is generated
app/published-*.{txt,tsv}  card ids and English ranks of published pages (committed, only ever grow)
```

## Lesson format (`course/lessons/NN.yaml`, file name = id)
```yaml
id: 1
title: {vi: Chào anh, en: Hello}
review: false                      # true on every 7th lesson
setting: One line of scene setting, in English.
native_check: {by: name, date: 2026-12-01}   # omit until a native speaker has checked it; the app then says so
dialogue:
- {n: 1, speaker: Lan, vi: "Chào anh! Tôi là học_sinh.", en: "Hello! I'm a student."}
notes:
- {ref: 1, topic: bridge, text: "học sinh is 學生 …"}      # ref 0 = recap note; topic free (bridge, pronouns, false-friend…)
new_words:
- {w: học_sinh, en: "pupil, student"}                       # optional: tag, chars, label (same | false-friend | native)
- {w: Lan, en: "Lan (a woman's name)", name: true}
exercises:
  translate: [{vi: "Anh là học_sinh.", en: "You are a student."}]
  fill: [{vi: "Chị ___ là học_sinh.", answer: cũng, en: "You are a student too."}]
```
**Word boundaries** (decided 17 Nov 2026): underscores join the syllables of one word (`học_sinh`, `Hà_Nội`); spaces
separate words. Every space-separated piece is one word, so the course never depends on the cutter. A homograph takes
`~tag` (`đường~road`), defined by a dictionary entry's tag or a `new_words` entry with that tag; the tag is not shown.
Numbers are not words. Names are declared once in any lesson's `new_words` with `name: true`.
**Tone-mark placement** (house style, decided 18 Nov 2026): the traditional one, as in most print and in the subtitle
counts (khỏe 5,853 against khoẻ 957 in FrequencyWords): in an open rhyme of two vowels the mark sits on the first
(hòa, khỏe, thủy, mùa), else on the vowel with a diacritic, else on the last vowel before a coda (hoàn), else the middle
of three (ngoái). `vi.key()` writes every syllable this way, so hoà and hòa find the same card; the line keeps its own
spelling on screen; lint asks for the house style (error). quí/quý are different spellings, not placements.
**Syllable table** (`tools/vi.py`, finding 10): built from a stated description of the phonotactics (nuclei with
their codas, the medial /w/, qu and gi), not a word list; checked at each build against every Thiều Chửu reading and
the FrequencyWords syllables seen 200+ times (`build_db.py validate_syllables`, result in HISTORY).
Chữ Hán never appear in `vi` lines or titles; notes may use them (bridge notes).

## Word card (`DATA.dict[id]`, built only by `tools/cards.py`)
Id: the word's key (lower-case NFC, spaces between syllables), `~tag` for a homograph, `name:` + surface for a name.
Fields: `w`, `k`, `en`, `en_src` (course | written | dict:SOURCE | parts), `en_rank` (3/2/1/0), `chars`, `hv`
(Hán-Việt per character, labelled), `yue` (Jyutping), `nan` (Tâi-lô LITERARY reading), `nan_coll` (the MOE word
reading when it is not the literary one: "colloquial / everyday"), `cmn` (pinyin), `by_char`, `label`, `ex {vi, en}`,
`other` (other etymologies of the spelling: en, chars), `parts` (syllable cards), `rank`, `audio`, `name`, `fixture`,
`src`. English, characters, label and example of a card come from ONE etymology (`cards.senses`). Shown top to bottom: word and ▶, English (+ its source, and "not checked by
a native speaker" for course English), chữ Hán with Cantonese / Taigi / Mandarin side by side, the label, the example.

## Database (`tools/schema.sql`, built by `tools/build_db.py`)
`meta` (nc, sources, missing, freq_method), `source`, `entry` (word, key, english, chars, origin sino|vietic|'',
hv_check, label same|native|'', freq per billion, freq_rank), `example` (ref: Tatoeba id and author), `hanviet` (char,
reading, kind hv|nom|hannom|unchecked, source, checked against the other Hán-Việt source), `chinese` (chars, lang
yue|nan|cmn, reading, level word|char, share, note), `bridge` (one row per chữ Hán spelling of the entries).
Loaders (`SOURCES`): wiktionary (kaikki: words, English, `vi-etym-sino` → chars, character readings by tag),
thieuchuu (Hán-Việt per character; `Ð`→`Đ`; heads with a stroke count `đại (5 n)` read), unihan (kVietnamese,
`unchecked`; kMandarin → `mandarin_pref`), rime (Jyutping; chars with rime's %, words), moe (Tâi-lô: characters'
literary 文讀=1 or unmarked 0 readings, words' own readings; accent variants `a/b` split; appendix types skipped),
cedict (pinyin, traditional forms only, numbers → marks with the apostrophe and syllabic m/n/ng; capitalised =
`name`), tatoeba (examples, attached to the words vi.cut() finds, 2 per word), and the
Tatoeba Challenge test set (corpus for the counts only). A missing file: "source X not fetched", `meta.missing`.
- **Bridge join** (`tools/bridge.py join()`, the same for cards, the `bridge` table and coverage): Cantonese and
  Mandarin: the whole word if the source has it, else character by character with every reading in brackets, main
  first (`hok6 (saang1/sang1)`, `by_char` on the card, `*` in the Bridge tab), else missing. Taigi: the column is the
  LITERARY reading (the layer that matches Hán-Việt), composed from the characters' literary readings; it is
  "attested" when the MOE word entry reads the same; a different MOE word reading (生日 senn-ji̍t, 先生 sian-sinn) is
  shown apart as "colloquial / everyday", never as literary. Mandarin order: Unihan kMandarin's reading first, then
  the number of CC-CEDICT words using the reading; surname/place readings dropped when there are others.
- **Hán-Việt** (`tools/hanviet.py`): Northern standard first; Thiều Chửu's Southern forms (sanh, chánh, võ…) come
  after, labelled "Southern variant"; where only the Southern form exists the Northern one is derived by the rule
  table (label "derived"); a character no Hán-Việt source reads gets Unihan's readings of Hán-Việt shape, labelled
  "unchecked, Unihan"; else "— (no Hán-Việt reading)", listed by `make lint` and `make coverage`. A Wiktionary
  analysis whose characters do not match the syllables (`hv_check` differs/length) is not shown as "same word";
  `make lint` lists it.
- **Labels**: `same` = Wiktionary `vi-etym-sino` whose characters match the syllables; `native` = inherited (`inh`) from Proto-Vietic/Mon-Khmer/
  Austroasiatic; `false-friend` only from `course/false_friends.tsv` (cards.py); borrowings and unknown: no label.
- **Frequency** (`tools/freq.py`): each syllable's frequency (wordfreq, else FrequencyWords) is divided among the
  dictionary words containing it in the proportions seen in a corpus cut by underthesea (Tatoeba, Wiktionary
  examples, Tatoeba Challenge), smoothed towards wordfreq's own phrase estimate; a word's frequency is the geometric
  mean over its syllables. Biases in the module docstring.

## Tools
| Command | What |
|---|---|
| `make db` / `make db-nc` | `tools/build_db.py`: vi.db (public) / vi-nc.db (`--nc`, private); refuses a wrong path |
| `make lint` | `tools/lint.py` (rules, see its docstring) + `tools/verify_words.py --lessons` (suspects by class) |
| `make test` | `tools/vi.py` self-test + `tools/test_pipeline.py` (guards, pipeline, partial builds, card check, lint, compare) + `tools/test_db.py` (loaders, missing sources, labels, bridge, frequency, cutter scoring), then the cutter report |
| `make cutter` | `tools/cutter_test.py`: P/R/F1 of vi.cut() and underthesea on `tests/cutter/reference.tsv`, and where they differ (`--known viet74k`: underthesea's word list as vi.cut()'s dictionary) |
| `make app` | `tools/build_app.py`: page + record.html, font coverage check, then `tools/check_cards.py` |
| `make check` | the card check alone |
| `make smoke` | `tools/smoke.py`: phone-sized click-through (Playwright) |
| `make lookup W=…` | `tools/lookup.py`: Vietnamese (tones optional), chữ Hán or `-e` English |
| `tools/compare.py run` | before/after: builds a git ref and the working tree, diffs lines, cuts, ids, card fields |
| `tools/published_ids.py` | after publishing: records card ids and English ranks |
| `tools/verify_words.py FILE.tsv` | checks a word list (word, English, chữ Hán) |
| `make coverage` | `tools/coverage.py [TOP]`: of the TOP (3000) most frequent dictionary words, how many have English, a Hán-Việt analysis, and 3/2/1/0 Chinese readings; then lesson coverage |
| `tools/import_recordings.py` | imports a native speaker's zip from `record.html` into `course/audio/lessons/` |
| `tools/site.py`, `tools/make_icons.py` | installable site (CSP, PWA) for Pages; app icons |

Text helpers for every tool: `tools/vi.py` (NFC, tones 1–6, `key`, `tkey`, syllable checks, `words`, `cut`).

## The private companion (`tusach-private`)
Same contract as Tsheh-tû's: the app's `Exam` loader reads `exam/index.json` (`{"files": {path: sha}}`) through the
GitHub API with the sync token (Contents: Read on the private repo), fetches `exam/app.css` and `exam/app.js`, caches
them by hash, and calls `window.ExamModule.init(loader)`, `.route(hash)` (`#exam…`, `#books`) and `.fill(root)`.
The module may call the page's globals (`openCard`, `closeSheet`, `esc`, `DATA`, `listSet`, `LIST_TITLES`). Its builds
use this repository's `tools/cards.py` with `open_db('private')` and their own `cards.Store`, and end with
`check_cards.check()`. The CSP (`tools/site.py`) allows only `blob:` scripts besides the page's own.
