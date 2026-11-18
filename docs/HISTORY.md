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

## 2026-11-18 — first real build (snapshot data-2026-11-17)
- Pinned the snapshot (kaikki Vietnamese JSONL, three Tatoeba exports); `make db` with nothing missing. vi.words() split
  only on spaces and crashed on a newline in a corpus line.
- Wiktionary, read on the real file before trusting the loader (52,167 lines; 9,112 characters): character readings come
  tagged (`han-viet-reading` / `nom-reading`, 2,110 characters, inside `related` or `senses[].related`) or untagged
  (`forms` "Hán-Nôm", 5,308 characters). `vi-etym-sino` has the whole word in argument 1 or characters and glosses
  alternating; with `hv=`/`preMC=` it renders "Non-Sino-Vietnamese reading of Chinese X (SV: …)" (và 和, giấy 紙): a
  borrowing, not a Hán-Việt analysis (origin `nonhv`, `entry.etymon`); these were ~780 of the 950 "differs" suspects.
  pos=romanization entries ("Sino-Vietnamese reading of 衣") are readings, not words. Readings that Wiktionary's own
  Sino-Vietnamese words use are taken as Hán-Việt (實 thực in 36 words: Thiều Chửu has only thật). Suspects 950+110 ->
  69+56.
- Tatoeba: 5 sentences not Vietnamese, 4 without author dropped; examples 4-20 syllables, closest to 8.
- Frequency: hyphenated old spellings (thế-giới, bất-nhân…) were ranked by wordfreq as one phrase with no competitor
  (20 in the top 300): ranked as spaced keys, once. Keys of digits/punctuation and 1-2 letter non-syllables (m, c, l)
  are not ranked. Not corrected (no automatic rule found): English in the syllable counts (the, in near rank 250),
  wordfreq's Wikipedia bias (huyện, quận, Nguyễn), the corpus's topics (tiếng Pháp). Measured ratio of wordfreq's
  prediction to the Tatoeba counts: `the` is overpredicted about 14x, as are administrative words, so no threshold
  separates them.
- Cutter: rules 8 (person term + ấy/ta/này/kia/đó) and 9 (mọi/mỗi + noun) from the top-300 review; reference F1 0.930
  -> 0.955. A held-out set of 100 Tatoeba sentences (tests/cutter/heldout.tsv) cut before any cutter ran: vi.cut()
  0.955, underthesea 0.928. Not tuned on it: rule 5 splits cảm thấy (3 times there); "hầu hết thời gian" crosses.
- Cards: an etymology is (source, number, characters, origin), unnumbered entries after numbered ones; lại "again"
  had taken 賴 from the surname, anh "elder brother" 英. Coverage now measures the card's own characters.
- Bridge, reviewed on 120 sampled rows: MOE unmarked readings beside literary ones were colloquial (共 kā): literary
  only when present; Hán-Việt readings ordered by use in Sino-Vietnamese words (Wiktionary lists them alphabetically);
  日 nhựt, 本 bổn, 義 ngãi labelled Southern; Unihan variants (行爲 -> 行為) find the Chinese readings, 120 rows.
- compare.py: hv/other/via/nan_coll fields; a ref is built with the sources its fetch.sh pinned.

## 2026-11-18 — data quality (branch data-quality)
- Why: the owner judged word list 1 too poor (69 rows of unknown origin, 26 to check, weak English for common words).
  Method: from data and code only; Claude's judgement only in course/etymology-review.tsv (2 rows) and the proposed
  glosses (not in force).
- New source: the English Wiktionary's translation tables, filtered on the snapshot runner (`.github/snapshot-
  translations.py`, release data-2026-11-18.2; the first release of the day had the Vietnamese rows only, superseded
  for the Chinese rows; the workflow now names a second release of a day data-DAY.N). Vietnamese Wiktionary
  (kaikki vi-extract): evaluated, not loaded (licence not readable on a primary page; it would class 4 of 159 unknown
  top-1000 words).
- English: tried ordering senses by the zipf of every attested English word: it promoted English homonyms ("love" =
  tennis zero for không, "why" for lý do, "remote" for xa). Kept: a sense with an attested word before one without;
  an attested word is put first only when no sense of the word has any ("busy"), in one entry; tables defined by
  another English word of the same Vietnamese word are skipped. The first measure of "missing main sense" (best
  zipf word absent) was noisy (uống lacked "take"): replaced by "none of the attested words present". Etymology
  order by evidence fixed là "fine silk", với "to reach", ra "train station", báo "leopard" as main senses.
- Doubt: a token-overlap test with CC-CEDICT on every entry marked 4,552 entries opaque (bạn 伴 "friend" vs
  "companion"); now per etymology, one-character analyses only, with the translation tables' Chinese words as a second
  witness, and a stricter test for function words.
- Taigi: the reported colloquial readings checked on the MOE file: 冊 tsheh, 院 īnn, 醬 tsiùnn are unmarked (0) and
  colloquial; 外 guē, 場 tshiâng, 房 pông are MARKED literary (1) by the MOE and are kept. MOE compound words carry no
  文白 mark, so no literary reading can be read from them; the coda rule (Hán-Việt as witness of the Middle Chinese
  coda) was used, with m/n, p/t, k/t allowed after a first run flagged 凡 huân, 法 huat, 直 ti̍t (229 -> 187 characters).
- Frequency: English leakage removed by k x English frequency (k from English words that cannot be Vietnamese
  syllables); names sharing a key no longer carry the common word's rank; spelling groups ranked once.

## 2026-11-18 — card quality rework after review 2 (branch data-quality, from fa4d343)
- Why: review 2 (independent, from a clean clone) found 48 of the top 200 cards and ~45 of the 195 word-list rows
  faulty after the data-quality pass, which its own measure had scored as an improvement. The architect's decision:
  stop letting heuristics over Wiktionary decide everything; three layers.
- Layer 1, the course lexicon `course/lexicon.tsv` (508 rows: word list 1, the essentials missing from it, the top 300,
  the review's fault words; doubt 14, likely 86, sure 408; 4 overrides), written by Claude, validated by
  `tools/lexicon.py`. First validation: 28 conflicts; resolved by fixing the row (English missing the dictionary's
  wording: tưởng, giống, huyện; origins: xe buýt French, đông "crowded" and thuốc older loans as Wiktionary has
  them; châu Âu formed in Vietnam; kênh's 巠 has no reading: origin left unknown), by fixing the validator (stop words
  that hid "to be", "not", "person"; names as keys; stemming; programme/program), or kept with an override and its
  reason (4). It absorbed glosses_en.tsv, glosses-proposed.tsv, etymology-review.tsv and false_friends.tsv.
- Layer 2, the dictionary: spelling groups pool only orthographic variants (i/y, hyphens, case); pronunciation /
  eye-dialect spellings keep their key (ga, ấy, dậy, nhỉ, biếu, kênh, nôm…). English: translation-table scoring,
  head-word cancellation, the global POS map and the comma cut removed: Wiktionary's order, late senses last, long
  later senses left out, no fragments. Main etymology from Tatoeba translations; first run gave là "to move down"
  (its long gloss had "water", "ground", and "is mounted" counted as "be"): bracketed explanations, "is" inside glosses,
  form-of and late senses are now left out; weak evidence claims no main sense. Opaque test loosened (all senses, all
  CC-CEDICT senses, variants, synonyms, stemming): review 2's sample false opaque 53/73 -> 7/74, false same 0.
  Examples: whole word, the sense's words in the linked translation, numbers and time words kept by the translation
  (a first rule on all nouns refused "giá / costs" paraphrases: narrowed), flags for profanity/sex/drugs, slashes and
  unknown words, and `course/example-block.tsv` (13 sentences). Origins: language names for codes, compounds,
  reduplications and calques from templates, Old Chinese etymons in a following template; doubt only when Wiktionary
  doubts the source itself. Frequency: Trung Quốc ranked again (3254 -> 303), tiếng Pháp and 4+-syllable keys
  unranked. Taigi: nasalised literary and -in/-ng agree (187 -> 167 characters), blind spots listed by coverage.
- Layer 3: `tests/golden/cards.tsv` (524 cards) and the opaque sample in `make test`; `tools/compare.py run` compares
  the real cards of the top 3,000 and every course word, each side built with its own tools.
- Other: smoke fails ("NOT TESTED", exit 2) without the private module; lint checks word-list duplicates and lesson
  numbers; the Vietnamese Wiktionary extract is no longer fetched or snapshotted (release data-2026-11-18.2 still holds
  the old asset, its licence unverified); ATTRIBUTION describes the MOE layers as our own classification.
- Results (clean clone): see STATE. The top 300 read card by card against fa4d343 and dcaf84f; review 2's 134 fault
  rows re-judged (/home/claude/rework-faults-status.tsv in the session): 131 fixed, 1 not fixed (nhưng: no MOE 仍),
  2 disagreements (đá's example is its own sense; phở's "folk etymology" is the French theory).
