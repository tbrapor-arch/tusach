# Word list 3: independent review (Claude, 19 Nov 2026)

Branch `wordlist-3` at b5a6130 (9 commits on main ac5ae29). The reviewer did not write the list. Read: CLAUDE.md,
STATE, REFERENCE, HISTORY (reviews 3-6), syllabus.yaml, word list 2, lessons 1-14, the draft (`wordlist-3.tsv`,
NOTES, to-check), the lexicon diff and the tool diff. Words were looked up on the built database (`tools/lookup.py`,
`data/build/vi.db`) and the lexicon rows read raw. NOT checked by a native speaker; the Northern-usage judgements
below are Claude's.

Checks run on b5a6130 (no db rebuild): `tools/lint.py` 0 errors (14 I lines: lessons not native-checked);
`tools/verify_words.py --lessons` 350 suspects (the same as main); vi, hanviet, etym, english, test_fetch,
test_pipeline, test_db, test_bridge_rules, test_plan, test_review3-6, test_golden: all 0 failures;
`state.py --check` agrees.

Fix pass: commits after eac98f4 on the same branch.

Severity: **high** = a learner is taught something false, or a scene cannot be written; **medium** = a plan point
or bridge topic not served, a wrong order, a mistranslated example, a misleading count; **low** = wording, notes,
polish. Each finding: evidence, fix. The "Status" line was written by the fix pass (same session, after the owner's
change of method: the reviewer applies the findings).

## High

1. **Core words missing although the lexicon already has their rows: từ~from, trong, trước, ngồi, hiểu.**
   Evidence: frequency ranks (vi.db) trong 8, từ 28, trước 80, hiểu 173, ngồi 389; `course/lexicon.tsv` has rows
   `từ~from` (older-loan 自), `trong`, `trước`, `ngồi`, `hiểu` (hv 曉), but neither list 2 nor list 3 teaches them.
   The scenes need them: L22 at the station (tàu từ Hà Nội đi …, "from"), L23 the room (Trong phòng có …), L24 the
   motorbike (ngồi sau, nhìn trước, đi trước), L16 dinner (Ngồi đi! / cả nhà ngồi ăn cơm), L18 the swimming lesson
   (Em hiểu không?). Without từ a train dialogue cannot say where a train comes from; without trong no room can be
   described "inside". Fix (counts kept: same type in, same type out): L16 ngọt → ngồi; L18 an toàn → hiểu (HV for
   HV; nguy hiểm stays); L22 toa → từ~from; L23 chật → trong; L24 tay → trước.
   Status: fixed.

2. **kỷ niệm: the false-friend note sits in the etymon column; the card says "same".** Evidence: the raw row has
   `In Chinese 紀念 is "to commemorate", 紀念品 a souvenir; memories are 回憶` in column 6 (etymon), false_friend empty;
   `tests/golden/cards.tsv` shows label `same`, no false-friend line. NOTES claims "false-friend note on the card".
   A learner reading Chinese is told 紀念 = "memories". Fix: move the text to false_friend (the card then says false
   friend; the word stays Hán-Việt for the counts).
   Status: fixed.

3. **suất 率 is labelled "the same word in Chinese" and used as a bridge word.** Evidence: card `suất 率 [same]
   portion; rate`; Chinese 率 is "rate, ratio; to lead" (lǜ / shuài); a portion of food is 份. The L25 note uses 率 as
   the IR example "s from Mandarin sh-": a bridge note on a word that is not the same word for the sense taught (the
   class review 3 refused). Fix: false-friend note on the row ("In Chinese 率 is a rate, a ratio or 'to lead'; a
   portion is 份"); the L25 note no longer offers it as a bridge word (thiếu 少 and thực đơn 食 carry IR th; s from
   sh- is in sinh 生, list 2).
   Status: fixed.

## Medium

4. **L17 plans the classifier con, but nothing in or before L17 takes it.** Evidence: syllabus L17 grammar
   "classifiers quyển, tờ, chiếc, con"; con's lexicon English "(classifier for animals)", usage `con {mèo}` (a
   preview); no animal noun is taught by L17 (lists 2, 3). Fix: L17 túi → mèo (a picture book for Bin: quyển sách về
   con mèo); chiếc keeps áo (L13) and xe máy (L8): the chiếc example becomes `Em muốn mua chiếc áo kia.`
   Status: fixed.

5. **L19 bridge IM (m, v) has no Hán-Việt m- word by L19.** Evidence: tools/bridge_rules.py IM rules are "m ←
   Mandarin m-" and "v ← Cantonese m- with Mandarin w-"; the Hán-Việt words of lists 2 and 3 up to L19 have no m-
   word (vị 味 and văn 文 are both v). Fix: L19 vị~taste → môn 門 "subject" (same word, mén / mun4 / bûn: Ông dạy môn
   văn), so m (môn) and v (văn, giáo viên's viên) are both on the page; the vị row keeps its card.
   Status: fixed.

6. **học sinh at L27 is late.** Evidence: L16's dinner talks about Bin's school (điểm, kiểm tra, giỏi), L19 brings
   giáo viên and trường; học sinh (rank 313, the word for Bin) waits until L27 "khi bà còn là học sinh". Fix: L16
   cam → học sinh (HV for HV; IK c keeps canh and công ty, kh keeps khách); L27 học sinh → hòa bình 和平 "peace"
   (Bà's war stories, with chiến tranh).
   Status: fixed.

7. **"Western loans 6" is wrong.** Evidence: the plan sentence (STATE, proposal) counts every `loan` type as
   Western; list 3's six are pin, sếp, phanh, ga (French) and ngủ (Kra-Dai, per Wiktionary) and làng (Hmong-Mien).
   Fix: tools/plan.py says "other loans (French and others)". Status: fixed.

8. **Two lexicon examples mean something else than their English.** Evidence: chuyện `Bà kể chuyện cho cháu nhé.`
   / "Tell me a story, Grandma.": with nhé and bà as subject it is Grandma offering ("I'll tell you a story"); a
   child asks `Bà kể chuyện cho cháu nghe đi!`. kể `Ông kể cho cháu về Hà Nội nhé.` / "Tell me about Hanoi, will you?
   (to an old man)": the request needs nghe and, to an elder, ạ. Fix: `Bà ơi, kể chuyện cho cháu nghe đi!` / "Grandma,
   tell me a story!"; `Ông kể cho cháu về Hà Nội đi ạ.` / "Please tell me about Hanoi (to an old man)." (nghe is L20: the kể
   example of L19 does without it.) Status: fixed.

9. **The lint path that reads several approved lists is not tested.** Evidence: tools/test_plan.py tests
   course.approved_word_lists / plan_word_lists and the plan check; lint.main's union of the approved lists (the
   gate that refuses a lesson word not approved) has no test, and the task's question "can an unapproved list count
   as approved?" was answered only by reading. Reading: no: lint fills `listed` from approved.word_list.file alone,
   the draft never enters it, and a lesson's new word outside it is an error. Fix: a test that runs lint on a
   lesson 15 using hơn (list 3): with list 3 a draft it is "not in the approved word list"; with
   `file: [wordlist-2, wordlist-3]` that error is gone. Status: fixed (tools/test_plan.py).

## Low

10. **cô's English contradicts its note.** "you (to a young woman, a female teacher)" against the strand note "a
    woman of one's parents' generation, a teacher" (Bin and Na's cô; a young woman is chị or em). Fix: "you (to a
    woman of one's parents' generation, a female teacher)". Status: fixed.
11. **nhất 一 "most, -est" shown as the same word.** In Chinese the superlative is 最; 一 is "one, first". The T5
    note uses it only for its tone (acceptable). Fix: usage note "in Chinese 一 is 'one, first'; the superlative is
    最". Status: fixed.
12. **đồng nghiệp 同業**: Chinese 同業 is "the same trade, someone in the same line of business"; a colleague is
    同事. Kept as a bridge word (same morpheme, close sense); fix: usage note. Status: fixed.
13. **nhá and vé have no note** in wordlist-3.tsv (empty before `[db: …]`). Fix: notes. Status: fixed.
14. **pin's note says "one of the lesson's two loans"**; L15 has five older or Western loans. Fix: note.
    Status: fixed.
15. **chủ nhà example** `Chủ nhà là một bà rất vui.` / "a very cheerful woman": vui is a mood (cheerful by nature is
    vui tính). Fix: `Chủ nhà là một bà rất tốt.` / "The landlady is a very kind woman." Status: fixed.
16. **STATE says verify_words lists 248 suspects**; it prints 350 on main and on the branch. Fix: 350.
    Status: fixed.
17. **đúng giờ (L22) is taught while đúng is not** (lexicon row đúng, no list). Status: not fixed: đúng ("right,
    exactly"; Đúng rồi!) for a later list; the compound is learnable alone.
18. **IR "x" at L25 has no Hán-Việt x- word** (only xa 賒 of L8, opaque, which lint refuses as a bridge example).
    Status: not fixed: the L25 bridge note should give th / s only; an x- word (出 xuất…) belongs to a later scene.
19. **nhạc (L20) and âm nhạc (L26)** are one sense in two registers; âm nhạc is bookish for a hobby (the hobby is
    nghe nhạc). Status: not fixed: kept as the art / school subject and the IY example (音, no initial); its note
    says so.
20. **Hà Nội usage queried by the drafter**: máy for the phone in a shop, chén for tea, suất, rạp alone, nghỉ hưu
    (về hưu also), tính tiền: judged right for Hà Nội speech. chờ: đợi is at least as common in Hà Nội ("Đợi em
    tí!"); chờ is not wrong; the note names đợi. Status: no change.
21. **nước~water at L18 is late** for a course with a café (L3) and a tea stall (L4): list 2 is approved, nothing
    to move now; noted for the record. Status: not fixed (approved list).
22. **tốc độ example** `Tốc độ này nhanh quá.` is stiff (a speaker says Đi nhanh quá!). Status: not fixed: no
    natural line with the words taught by L24 found that uses tốc độ better; a native speaker's point.
23. **Tool, approval record**: `approved.word_list` keeps one by/date for all its files; approving list 3 as
    `file: [list 2, list 3]` overwrites the record of when list 2 was approved. Status: not fixed: the format is
    the owner's decision (suggestion: one {file, by, date} entry per list).

## Found while fixing

24. **medium. tools/wordlist.py human_note cut a [db: …] part at its first "]".** Evidence: sạch's [db: …] holds
    "Tho [Cuối Chăm] pʰrɛːk⁸"; the regeneration during the fix pass left "pʰrɛːk⁸]" in the human note, once per run
    (the note grows each time). Fix: the [db: …] part is cut to the end of the note; sạch's note restored; test in
    tools/test_plan.py. Status: fixed.
25. **low. Word list 2 (approved) no longer matches its regeneration**: `tools/wordlist.py
    course/proposal/wordlist-2.tsv --check` says 32 of 210 rows would change (database columns drifted since the
    approval; the same before and after the fix above). Status: not fixed: an approved file, the owner's call.

## Tool change (approved.word_list.file as a list): verdict
Correct and small: course.approved_word_lists / plan_word_lists, plan.load reading every list with its file, a word
of an earlier list refused in a later one (same key and tag; a different tag is another word: nước~water,
đông~crowded, hay~good / ~often are right), lint's union of the approved lists, to-check reading every list. An
unapproved list cannot count as approved (finding 9). Tested for the helpers and the plan; lint's path now too.
