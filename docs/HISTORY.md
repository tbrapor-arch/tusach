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

## 2026-11-18 — review fixes
- Syllable table rebuilt from a description of the phonotactics (tools/vi.py): it rejected quýt, huýt, khuâng, ừm,
  quỳnh, yểng and accepted quu, quô, cuơ, gii, giiêng. Validation at build time: all 2,069 distinct Thiều Chửu
  readings accepted (two needed it: quí, quĩ, Thiều Chửu's spelling of quý, quỹ: qu + i accepted as the i/y variant);
  of the 3,588 FrequencyWords syllables seen 200+ times, 2,768 accepted, 809 rejects are plain ASCII or carry digits
  or punctuation (English words, names, ko, subtitle markup, cà-phê with a hyphen), and the 11 with Vietnamese letters
  were read one by one: abbreviations (đc, đm, đ), loans written as one syllable (alô, đôla), typos (đươc, kông,
  téi), junk (àh, ă, ǵ). None is a Vietnamese syllable; nothing was whitelisted. quên showed that uên was missing.
  quốc is the one spelling of qu + a rounded vowel, kept as such.
- Tone-mark placement: one house style (traditional); keys normalise it (see REFERENCE).
- Tatoeba Challenge copy: its licence is in conflict, so it is now `commercial_ok: False` (private build only). The
  cutter reference of 17 Nov 2026 (200 of its sentences, commit 67249d0) was removed from the repository going
  forward; history is not rewritten. New reference: docs/SEGMENTATION.md first, then 200 sentences written by Claude
  and cut by hand by that convention before any cutter ran on them (not checked by a native speaker).
- One cutter: the frequency counts now use vi.cut(), not underthesea (which stays in the cutter report only). vi.cut()
  got the rules of docs/SEGMENTATION.md. On the new reference, with underthesea's Viet74K list as the dictionary
  (stand-in, Wiktionary not fetched): F1 0.893 before the rules, 0.942 after; underthesea 0.930. Caveat: the rules
  were chosen by the convention but tuned while reading the differences on this same reference: no held-out set, so
  0.942 is optimistic; and the reference is one non-native model's judgement.
- Private module: the page used to `Object.assign` the module's cards over its own, so a private card with poorer
  English replaced a public one (reviewer: "Tôi là học sinh."). Now one merge rule (`Priv.mergeCards`), the private
  build uses the course words, and its card check compares with the public published English. The internal names
  Exam/exam (inherited from Tsheh-tû's exam-preparation module) became neutral in both repositories: `Priv`,
  `window.PrivateModule`, `module/`, `#private`.
- Lint: `fixture: true` only under tools/fixtures/; only NN.yaml in course/lessons/ (the template moved to
  course/lesson_template.yaml); exercise copies caught by normalised containment; flow mappings cut at a comma
  (the fixture's "pupil, student" and "I, me" had been read as "pupil" and "I"). The card check compares the English
  text, not only its rank. compare.py run builds both databases.
