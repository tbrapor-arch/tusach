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

## 2026-11-18 — review 3 fixes (branch data-quality, from 16c8b24)
Review 3 (an independent agent) found word list 2 incoherent for spoken Northern Vietnamese in places, rule rates
inflated by left-out items, circular and multi-outcome rules, wrong usage notes and examples, false statements
marked sure, and guards that let them through. What changed (each reproduced case is a test: tools/test_plan.py,
tools/test_review3.py):
- Plan: course/syllabus.yaml is the one source (lessons, cast, the Northern particle strand, the draft word list);
  tools/plan.py writes the derived counts and the proposal's tables and checks, in `make lint`, that no note, lexicon
  usage note or planned grammar uses a word before the list teaches it (`{preview}` marks the exceptions) and that
  reviews have no new words. Word list 2: 206 words + 3 names (à, đấy, thế, đừng, trăm, chợ, lăm / mốt / tư, vợ,
  sinh viên, hôm qua, sao / tại sao / vì added; bác / cháu at L5, phải "right" at L3, quá at L4).
- Sound rules: the reading the learner would use (the word's, else the source's most frequent; Cantonese changed
  tones counted with their base tone), main / strict / lenient rates, conditions on the Chinese side only, best
  single guess and "narrows"; the proposal's tables are generated (bridge_rules.py --write, checked by lint).
- Hán-Việt evidence: a reading Wiktionary gives only as Nôm is never Hán-Việt (平 bằng, 南 nôm, 局 cuộc, 恩 ơn);
  analyses that need such a reading (công bằng, thế cuộc: 38) are older loans with their characters as etymon.
  Taigi: the 麻-rhyme colloquial -e (茶 tê) and "layer not marked by the MOE" on the card. Polyphonic readings
  ordered by measured fit with the card's syllable (tools/soundfit.py): on the first 100 polyphonic one-character
  cards of the top 3,000, 91 with the right reading first in both languages (Claude's judgement).
- Lexicon: example / example_en (250 rows, Claude's, Northern, labelled), per-item English and characters-vs-
  etymology checks, "X only" claims refused, rows with another character's sense fixed (cơ, công, tiêu, thuộc, kinh,
  đàn, đại, bánh), usage notes of năm, bốn, vậy / thế, bát, hay, cốc, xa. Examples: Southern words, self-harm and
  violence, misaligned wh-questions refused. Bridge notes: the word–character pair judged. Golden: a 550-card
  snapshot of everything shown. False opaque 7 -> 2.

## Review 4 (19 Nov 2026, branch data-quality)
- Origin notes (tools/etym.py): what the etymology says about THIS word (lăm: an alteration of năm after mười), a
  cognate only with its form (taken from the text when the template has "-"), Vietnamese's own ancestors never
  cognates (Middle Vietnamese "inherited from", a proto-form under {{cog}} "related to"), an ancestor identical to
  the word no note. Variants (tools/bridge.py same_sound): a Unihan pair whose Cantonese or Mandarin readings share
  nothing lends no reading (襖~澳, 癉~疸, 戧~創, 玟~玫).
- Plan: L4 at a tea stall (no goods or mua needed), trứng for quả at L10, to / nhỏ at L13, particle strand (nào, đâu
  L12, hả, nhá, với, dạ); the order check classifies every token (a lone mua is checked; Mai at a sentence start is
  mai); rule tables show the best single guess beside a multi-outcome rule. Lexicon: examples (mặc, viết, sau),
  notes (chồng, đấy, vậy, mà, to / lớn / nhỏ), rows to, trứng, chứ, hả, nha. Tests: tools/test_review4.py.

## 2026-11-19 — approvals, Mandarin first, Lesson 0 and lessons 1–7 (branch lessons-01-07)
- The owner approved the syllabus and word list 2 (main fast-forwarded to 36f7440). No native speaker: lessons are
  labelled unchecked; tendencies taught as such. Priority: Vietnamese first, the bridge bounded (CLAUDE.md).
- Card order: Mandarin (pinyin), Cantonese (Jyutping), Taigi (Tâi-lô) from one constant, `cards.DISPLAY_LANGS`
  (page, Bridge table, golden columns, lookup); the golden snapshot was rewritten with the same values, columns moved.
- Lesson 0 as data (`course/lesson0.yaml`, `tools/lesson0.py`) rather than Markdown: the `markdown` package is not in
  the locked requirements, and [[…]] spans let every example word go through `cards.tokenize` and lint. Sounds are
  from published descriptions (Kirby 2011, Thompson 1965), not from listening; "exactly"-type claims are refused.
- Lessons: written from word list 2 alone; no change to the plan or the lexicon was needed. Where a natural line
  wanted an unlisted word (cũng in L1, bố mẹ / ông bà in L5, tiếng Pháp in L2, ừ for "yes" to a younger person),
  the line was rewritten with listed words and the choice recorded in `course/lessons/NOTES-for-native-speaker.md`.
- New checks found by writing: a several-syllable course word written without underscores (W; it caught Cảm ơn),
  a lesson word no lesson up to it teaches (E). The copy check refuses an exercise ending in ", phải không?" while
  the dialogue has one (a two-word clause is "contained"): exercises write the tag without the comma (NOTES L3 5).
- Found and fixed: test_fetch's fixture-database build picked up the real course once lessons existed (make test
  failed in CI from 26c5aa7 to 0729180); smoke's "Show English" loop skipped buttons as they removed themselves.

## 2026-11-19 — review 5 of lessons 1–7 (a second agent's per-line list, 25 rows + 19 findings)
- Content: L1 lines 2–5 in order (Chào em! / Chị tên là gì ạ? / Chị tên là Lan. / Vâng. Cảm ơn chị ạ!); a man who
  says chị says em, never anh (L1 fill 3 now Tôi …); the label Bác is what Sacha calls her; ạ = politeness toward
  elders and in service; cà phê sữa đá, each word describes everything before it; ông 翁 / bà 婆 not asserted
  (lexicon likely); đi công ty out; L6/L7 one story (Minh leaves early, comes home late; they meet at the tea stall
  that Monday evening). Load: 7–9 notes per lesson (were 10–14), numbers as a small table + two rules; L7 a true
  review of 9 lines. Lesson 0: nhé was the example of n; uống out of the lip rule; pitch numbers, Voice column,
  glide table, Southern lines and section 8 cut (page 11,676 → 9,958 px at phone width).
- Code: the test fixture had been loaded into every real build (seven real cards said "Source: test fixture", and
  its 學生 / 學 / 生 readings were in the real tables): now only `build_db.py --fixture` (test databases); compare
  reads card sources and blocks a fixture source. The Taigi mark U+030D drew as a dot: Noto Sans's own short stroke
  (tables and anchors were fine; the Taigi app's font is the same file), redrawn at build time (tools/appfont.py),
  and the font check now covers the cards' readings, combining marks and their positioning. Lint: person-term pairs
  (W), copies from earlier lessons and note examples (E), Vietnamese in notes and glosses taught first or {preview}
  (E); Lesson 0's sound-table examples checked against their row; a mistyped TUSACH_LESSON0 fails. Tests:
  tools/test_review5.py, test_pipeline.py.
- Kept, with the reason in NOTES-for-native-speaker.md: L3 line 3 Anh muốn một cà phê sữa đá and L5 line 6 bác này
  (the reviewer left both to a native speaker), L4 prices.

## 2026-11-19 — lessons 8–14 (branch lessons-08-14, from 467c499; not merged, for review)
- Written from scratch to the plan and word list 2 with the lessons of review 5 applied from the start: L8 Hồ Hoàn
  Kiếm (directions, đừng, verb + đi, nào, rồi, đó, khoảng), L9 weather (adjective predicates, rất / lắm / quá / hơi,
  thế, nhỉ, nhưng), L10 phở (đã … chưa? / rồi / chưa, hôm qua, thêm, quả), L11 the weekend with Mai (days, months,
  dates, bao giờ, hay, với, định, thích; bạn / tôi), L12 a cold (bị, nên / phải, sao / tại sao – vì, Sao thế?,
  Không sao đâu), L13 a present at the market (cái, colours, to / nhỏ, vừa, mua / lấy / tặng), L14 Review 2 (the
  birthday dinner, recap notes, updated pronoun summary). One bridge note each (B3, T1, O1, T2, T3, T4, a tone
  recap); the false friends thời tiết, tuần, bác sĩ, sinh viên stay on their cards (lint refuses a false friend as
  a bridge example). No plan change. Hesitations: 40 rows in NOTES-for-native-speaker.md.
- Data: nào's lexicon usage note gives the urging use (Đi nào!; golden snapshot updated); đi's already did.
- Checks: make lint 0 errors 0 warnings; make test, make app, make check, tools/smoke.py (with TUSACH_PRIVATE) pass;
  tools/compare.py against origin/main (same database both sides: build_db and sources unchanged): 120 lines and 118
  cards added, no existing card changed in the compared fields (usage is not one of them), 0 blocking.

## 2026-11-19 — review 6 (lessons 8–14) applied; merged into main
- An independent reading of lessons 8–14 (28 faults, `review6/faults.tsv`, outside the repository); all applied.
  Bridge wording now matches tools/bridge_rules.py: Mandarin tone 2 "usually" huyền / ngang, checked syllables apart
  (節 tiết, L9) and first (L14 recap); Mandarin tone 4 "usually" (L12); Cantonese checked syllables 1 or 3 sắc, 6 nặng
  (L13; rule T4 is now "tone 6", the same 78 / 81: no checked syllable has tone 2, 4 or 5); 時: thì the dictionaries'
  reading, thời a variant (L10). Story: L13 line 1 Thảo ơi, ngày mai là sinh nhật mẹ em, phải không?; L11 line 9 no
  repeated invitation; L14 line 10 recycles a clock time (bảy giờ rưỡi sáng). Lines: L8 Hồ đây à?, L9 trời nóng thế,
  L12 Cháu đau đầu lắm and Sao phải đi?, L14 … cái áo này ạ ({biếu} previewed). L8 9 notes (1,478 characters), L14
  1,534. False friends (decision 6b): one clause, at most one per lesson, topic `false-friend`: L11 tuần 旬, L12 bác sĩ
  博士 / 醫生.
- Segmentation (decision 6a): đau + body part is two words (đau đầu, đau bụng); vi.cut() rule 10; reference line 63
  follows. Reference F1 vi.cut() 0.955 (unchanged), underthesea 0.930 → 0.929; held-out 0.953 (unchanged). Effect on
  the cards (compare.py against origin/main): đau đầu loses its Tatoeba example (the cutter no longer finds the word
  in it); nào's English is the intended change; 0 blocking.
- Lint: an exercise equal to the example a card of its words shows is an error (nine found, also in L1, L2, L7);
  false-friend notes checked against the lexicon; a cast name in an English note is read as the common word only at
  a sentence start (not after : or a quote) and when that word is taught (reverses review 4 C's "Mai gặp nhé" case).
- Lexicon: nào's English has the urging sense; sao~why's usage Không sao (đâu); đau's usage (body part after).
- NOTES-for-native-speaker.md: the 40 rows with the reviewer's judgement, eight first (B1–B8).

## 2026-11-19 — word list 3 drafted (branch wordlist-3, from ac5ae29; not approved)
- 221 words for L15–27 (L21, L28 reviews: none), chosen per scene for the lesson's grammar, particle and bridge,
  read on the real cards first; native / Hán-Việt counts exactly the plan's (13 + 5, 13 + 6); older and Western
  loans 1–5 a lesson where the plan guessed 2 (many basic words are older loans: kia, cũ, tìm, đọc, tầng…).
- Lexicon: 127 new rows and 75 examples on existing rows, each example using only words taught by its lesson.
- Tools: `approved.word_list.file` may be a list; plan, lint and the to-check list read the approved lists, then the
  draft (`course.plan_word_lists`), so list 3's notes may use list 2's words and a word of list 2 is refused in list 3.
- Found by the plan check: pinyin and Jyutping in a note are read as Vietnamese (notes give characters only); "an"
  is read as English, so "an toàn" cannot be quoted in a note (its card example is flagged I, a false positive).

## 2026-11-19 — word list 3 reviewed and fixed (branch wordlist-3; still NOT approved)
- An independent review (`course/proposal/wordlist-3-review.md`, 25 findings: 3 high, 7 medium, 15 low), then, by
  the owner's change of method, the same session applied it. High: core words the lexicon had but no list taught
  (từ~from, trong, trước, ngồi, hiểu: in for ngọt, toa, chật, tay, an toàn); kỷ niệm's false-friend note was in the
  etymon column (card said "same"); suất 率 a false friend, no longer a bridge word. Medium: mèo for con (L17), môn 門
  for the labial bridge (L19), học sinh at L16, hòa bình at L27, "other loans" for ngủ / làng in the counts, two
  examples (kể, chuyện), lint's approved-lists union now tested, and wordlist.py human_note cut a [db: …] part at
  its first "]" (sạch's note grew at each run). Counts on plan (13 + 5 / 13 + 6).
- 19 Nov 2026: the owner approved word list 3 (after review and fix, 8381c89); approved.word_list.file lists
  wordlist-2.tsv and wordlist-3.tsv. test_plan builds its draft / approved syllabi from the real file, whatever it holds.
