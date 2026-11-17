# History (experiments, superseded methods, decisions and why)

## 2026-11-17 — forked from tsehtu dict-all df02bfe on 2026-11-17
- Source: `tbrapor-arch/tsehtu`, branch `dict-all`, commit df02bfe (after the 17 Nov 2026 dictionary work). The first
  commit here holds the kept files unchanged, so `git diff` from it shows every adaptation.
- Kept and adapted: build_app, build_db (+ schema), cards, english, lint, smoke, verify_words, published_ids, site,
  lookup, coverage, import_recordings, make_icons, the app shell (look, tabs, progress, lists, Leitner cards, sync
  through a gist, the private-module loader), the recording page, the PWA files, the embedded Noto Sans subset (it
  already had every precomposed Vietnamese letter and the mark tables), PORTING.md, PORTING_PROMPT.md, LICENSE.
- Removed (Taigi only, or tied to Taigi data): sandhi, tailo, sutian, taigi_chars, moe_examples, variants, freq_align,
  enrich, tone_drill, bridge (the Taigi reading quiz), zh_words (tappable Mandarin; needs jieba data: port later if
  wanted), podcast + fetch_podcast, fetch_audio (MOE recordings), export, the lesson-writing helpers built on Tâi-lô
  keys (candidates, exercises, extend_lessons, fresh, qc_glosses, qc_readings, taught_later, untaught, wordcheck,
  xrefs), all course content, glosses, docs, themes, podcast/video/music data, published card ids.
- New, from the handover's section 4: `tools/vi.py`, `tools/course.py`, `tools/check_cards.py`, `tools/compare.py`,
  `tools/test_pipeline.py`, `.github/workflows/check.yml`, the shared card file (`cards.Store`), the database guard
  (`cards.open_db`), the syllabus-approval gate in lint.
- Decision: word boundaries written in the lesson source with underscores (`học_sinh`) rather than a separate tokens
  field: one line to write and read, every piece is one word, nothing can drift between two fields.
- Decision: the two database builds go to two files (vi.db, vi-nc.db) and carry `meta.nc`; the public page and the
  private module each refuse the other's.
