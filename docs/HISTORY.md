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

## 2026-11-17 — database step (sources, bridge, frequency, cutter test)
- Hán-Việt source: the sources report proposed Wiktionary first. A third-party census of the kaikki file
  (arvicco/nabu README) counts only 2,881 `han-viet-reading` relations against 8,418 `nom-reading` and 9,698 older
  `Hán-Nôm` forms that do not tell the two apart. So both are loaded side by side (kind hv), Wiktionary first, Thiều
  Chửu (11,787 readings of 9,884 characters) as cross-check and fallback; the older forms are kept as kind `hannom`.
- Word frequency: the report suggested wordfreq's own phrase estimate (or the minimum of the syllables). Tried on a
  stand-in word list (underthesea's Viet74K, not kept): alone, it ranks junk compounds of frequent syllables high
  (2,139 multi-syllable keys in the top 3,000, e.g. "là là", "một và"); with the corpus shares of `tools/freq.py`
  (2,500 sentences) 1,503, led by có thể, không thể, làm việc, tất cả. học sinh went from #3565 to #240, thể (bound
  in có thể) from #129 to #2848. Kept: the corpus shares, smoothed towards the phrase estimate.
- The cutter report first listed every differing word of vi.cut() (a joined word counted twice); replaced by
  stretches of syllables cut differently.
- Tatoeba and kaikki are refused from the sandbox. Tatoeba sentences were found on GitHub in Helsinki-NLP's Tatoeba
  Challenge (licence conflict noted in ATTRIBUTION.md): used for the cutter reference and corpus counts only.
