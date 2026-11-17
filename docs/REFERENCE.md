# Reference: formats and tools

## Layout
```
course/lessons/NN.yaml   lessons (none yet: the syllabus and word list wait for the owner's approval)
course/syllabus.yaml     the plan and the owner's approvals (lint refuses lessons without them)
course/glosses_en.tsv    English written for words that are not in a lesson's new_words
tools/                   build, pipeline, checks (MIT)
tools/fixtures/          TEST FIXTURE: dict.yaml (9 invented entries) and lessons/00.yaml (3 lines); not content
data/fetch.sh            open sources at pinned versions (none yet: TODO(sources))
data/build/              generated, never committed: vi.db, vi-nc.db, cards.json
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
Chữ Hán never appear in `vi` lines or titles; notes may use them (bridge notes).

## Word card (`DATA.dict[id]`, built only by `tools/cards.py`)
Id: the word's key (lower-case NFC, spaces between syllables), `~tag` for a homograph, `name:` + surface for a name.
Fields: `w`, `k`, `en`, `en_src` (course | written | dict:SOURCE | parts), `en_rank` (3/2/1/0), `chars`, `yue`
(Jyutping), `nan` (Tâi-lô, literary reading), `cmn` (pinyin), `label`, `ex {vi, en}`, `parts` (syllable cards),
`rank`, `audio`, `name`, `fixture`, `src`. Shown top to bottom: word and ▶, English (+ its source, and "not checked by
a native speaker" for course English), chữ Hán with Cantonese / Taigi / Mandarin side by side, the label, the example.

## Database (`tools/schema.sql`)
`meta` (nc = 0 public / 1 non-commercial), `source` (licence, commercial_ok, fixture), `entry` (word, key, tkey,
toneless, tag, english, chars, label, freq), `example`, `hanviet` (char → reading), `chinese` (chars, lang yue|nan|cmn,
reading). Bridge data is joined on the characters (handover section 5): Hán-Việt + Jyutping (the Cantonese app's
rime-cantonese data) + Tâi-lô literary (Tsheh-tû's `taigi.db`, `wenbai = literary`) + pinyin (CC-CEDICT). TODO(sources).

## Tools
| Command | What |
|---|---|
| `make db` / `make db-nc` | `tools/build_db.py`: vi.db (public) / vi-nc.db (`--nc`, private); refuses a wrong path |
| `make lint` | `tools/lint.py` (rules, see its docstring) + `tools/verify_words.py --lessons` (suspects by class) |
| `make test` | `tools/vi.py` self-test + `tools/test_pipeline.py` (guards, pipeline, partial builds, card check, lint, compare) |
| `make app` | `tools/build_app.py`: page + record.html, font coverage check, then `tools/check_cards.py` |
| `make check` | the card check alone |
| `make smoke` | `tools/smoke.py`: phone-sized click-through (Playwright) |
| `make lookup W=…` | `tools/lookup.py`: Vietnamese (tones optional), chữ Hán or `-e` English |
| `tools/compare.py run` | before/after: builds a git ref and the working tree, diffs lines, cuts, ids, card fields |
| `tools/published_ids.py` | after publishing: records card ids and English ranks |
| `tools/verify_words.py FILE.tsv` | checks a word list (word, English, chữ Hán) |
| `tools/coverage.py` | lesson coverage of the frequent words (needs a frequency source) |
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
