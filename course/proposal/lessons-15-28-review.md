# Lessons 15–28: independent review (review 7, Claude, 19 Nov 2026)

Branch `lessons-15-28` at 10bbfe6 (merges the approved word list 3, 567a4e9 = main). The reviewer did not write the
lessons. Read: CLAUDE.md, STATE, REFERENCE, SEGMENTATION, HISTORY (reviews 5 and 6 above all), syllabus.yaml (plan,
particle strand, cast), lessons 1–14 (the standard and the story so far), wordlist-3.tsv and its review, the lexicon,
NOTES-for-native-speaker.md (rows L15–L28), every line of lessons 15–28, the sound-rule tables of the proposal
(`tools/bridge_rules.py` output) and the writer's tool change. Words looked up on the built database (`make lookup`,
`data/build/vi.db`). NOT checked by a native speaker: the Northern-usage judgements below are Claude's.

Checks on 10bbfe6 (no db rebuild): `make lint` 0 errors (28 I lines: not native-checked); verify_words 421 suspects
(read with `--all`: the L15–28 ones are free sequences, numerals, names after a title, a sentence boundary (Có. Khi),
and the points below: thế thì, cả nhà, ăn cơm).

Severity: **high** = the learner is taught something false (grammar, usage, pronouns, culture); **medium** = a scene
that does not hold together, a plan point not served, an exercise with two right answers, an unnatural line;
**low** = wording, polish, tools. Each finding: lesson:line, evidence, fix. "Status" is written by the fix pass
(the same reviewer, after the findings were committed).

## High

1. **Bin, 8, studies "môn văn" (L19:7, L21:4 and setting).** In Vietnam the subject of primary school (lớp 1–5) is
   *Tiếng Việt*; *Ngữ văn* / văn begins at lower secondary (lớp 6). Bin is in his second or third year. "Cô ở trường
   cháu cũng dạy văn" and "kiểm tra môn văn" teach a wrong fact about Vietnamese school. Fix: L19:7 Bin's teacher
   teaches tiếng Việt (the note says why it is not văn); L21:4 and the setting: a Vietnamese test (kiểm tra tiếng Việt).
   Status: open.

2. **Pronoun notes that say what no line does (L28 note ref 6, L23 note ref 1).** L28: "The landlady says cô and cháu
   to Thảo and Sacha": she calls herself cô and THEM cháu (line 6: … ăn cơm với cô). L23: "they call her cô … and say
   cháu", but neither Thảo nor Sacha says cô in L23 (lines 3, 5, 7, 11 have no term or cháu alone). Pronoun pairs are
   the class review 5 fixed first. Fix: L28 note rewritten; L23 line 3 Cô ơi, phòng này có bếp không ạ?
   Status: open.

## Medium

3. **L20:3–5, the reports.** Mai: "Chúng ta đều phải gửi báo cáo cho sếp" ("we both have to send", not yet done);
   two lines later, asked by that boss, she answers "Em gửi rồi ạ. Sacha cũng gửi rồi." Fix: line 3 Hôm qua chúng ta
   đều phải gửi báo cáo cho sếp ("yesterday we both had to send"), note ref 3 follows.
   Status: open.

4. **L20:8, lunch at nine.** The meeting starts at nine (lines 2, 4); line 8 is "đi ăn trưa đi!" with no time marker,
   in Tuấn's meeting. Fix: line 8 opens Mười hai giờ rồi! ("twelve o'clock already!").
   Status: open.

5. **L26:7, Mai "always busy at weekends" (Cuối tuần em luôn bận)** four lessons after her weekend trip to Lào Cai
   with Sacha (L22), and in L11 she had a free Sunday for a film. Fix: line 7 Tháng sau em bận lắm, anh ạ. Em không có
   thời gian. (next month); luôn moves to Tuấn, line 10: Anh thì tối thứ bảy luôn xem bóng đá (hay~often stays in
   line 3); note ref 1 follows.
   Status: open.

6. **L19:6, Ông là giáo viên for a retired teacher** ("I am a teacher"; the English says "I was", the lit "be").
   Vietnamese marks no tense, but a bare là + profession is read as the present. Fix: Ông dạy môn văn ở trường kia ba
   mươi năm. Bây giờ ông già rồi, ông là giáo viên nghỉ hưu ("I taught … for thirty years … I'm a retired teacher");
   note ref 6 follows; NOTES L19.4 answered.
   Status: open.

7. **L24:7, Chú ý! Xe máy ở trước! Phanh đi!** A rider shouting a warning says Cẩn thận!; chú ý is "pay attention"
   (signs, teachers), and "Xe máy ở trước" without có is not how one says "there's a motorbike in front". The writer
   rewrote the line round a lint false positive (finding 22). Fix: line 7 Cẩn thận! Có xe máy ở trước! Phanh đi!;
   line 9 Được. Chú ý nhé, đừng ngã!; notes ref 7 / 9 and the bridge ref follow.
   Status: open.

8. **L17:5, sách cho Na, năm tuổi … Na thích mèo** said to a bookseller who does not know Na. Fix: Em cũng muốn mua
   sách cho một cháu năm tuổi. Cháu thích mèo (cháu, a friend's child, lesson 5); note ref 5 follows.
   Status: open.

9. **L17 bridge: "Mandarin and Cantonese lost an old ng-"** is false for Cantonese, which keeps ng- in many words
   (我 ngo5, 牙 ngaa4, 眼 ngaan5; only 語 jyu5 here lost it). Fix: "Mandarin lost an old ng- that Taigi keeps as g-".
   Status: open.

10. **L20 bridge, plan ID "đ, th, n, l": th is missing.** The proposal's rule: th ← Mandarin t- in tones 1 3 4 (84 %).
    No Hán-Việt th word with Mandarin t- is taught by L20 (giao thông is L24), so the rule is stated without an
    example. Status: open.

11. **L27 bridge, plan Z "d / gi / r, tr / ch, s / x": s / x is missing**, and L25 promised x "a later lesson".
    Fix: one clause from the measured rows (s → Mandarin sh- or ch-, sh 45 %; x → Mandarin ch-, 67 %, a tendency):
    "for s or x, a Mandarin sh- points to s (sinh 生), a ch- more often to x"; the note shortened to stay near two lines.
    Status: open.

12. **Exercises with two right answers.** L22 fill 2 "___ nào anh về Pháp?" (lúc nào and khi nào, khi taught in the
    same lesson); L18 fill 2 "Phở ở đây ngon ___?" (chứ, không, nhỉ all fit "isn't it?"); L20 fill 3 "Đây là lần ___
    em ăn phở" (đầu, taught in L18: lần đầu, fits as well as đầu tiên); L19 fill 1 "___, cháu đi rồi ạ" (vâng fits
    as well as dạ; "Have you been to school yet?" is also odd English for Cháu đi học chưa?). Fix: L22 Na đi ngủ ___
    tám giờ tối (lúc); L18 Anh nói tiếng Việt được ___! "Of course I can …" (chứ); L20 Bin là học sinh ___ đến trường
    (đầu tiên); L19 Bin ơi! – ___, bà gọi cháu ạ? (dạ answers a call; vâng does not).
    Status: open.

13. **"Bà Lan" = "Mrs Lan" in exercises (L19 translate 1, L22 translate 3).** Lan is chị Lan, 35; the family's bà
    (Lan's mother) has no name in the course. The learner meets a second Lan, or thinks Lan is old. Fix: L19 Bà sống
    với chị Lan và anh Minh ("Grandma lives with Lan and Minh"); L22 Bà ngủ sớm ….
    Status: open.

## Low

14. **L18 setting vs line 4.** "Thảo has never learnt to swim, and Sacha has offered to teach her", then Sacha asks
    "Em biết bơi không?" and she asks him to teach her (line 7). Fix: setting: Sacha has asked Thảo to come swimming.
    Status: open.

15. **L16:2, Mời cả nhà ăn cơm! from the grandmother.** mời goes up or to guests; the eldest answers the children's
    invitation by starting the meal: Cả nhà ăn cơm đi! Fix done; note ref 2 follows (mời stays in line 1).
    Status: open.

16. **L16:7, Hôm qua kiểm tra, con được mười điểm** (the writer's doubt L16.5): a bare "kiểm tra" as a time phrase
    is telegraphic. Fix: Hôm qua con kiểm tra được mười điểm! (verb + được + the mark); note ref 7 follows.
    Status: open.

17. **L17:6, Quyển này về một con mèo** (doubt L17.4): about-phrases want a verb: Quyển này nói về một con mèo.
    Status: open.

18. **L27:6, bà đến thành phố học** – going from the village to the city is lên (lên thành phố, lên Hà Nội), a use
    of the direction verbs of L24. L27:10 Bác không quên đâu just after line 8 Bà quên rồi reads as a contradiction:
    she forgot telling the story, not the past. Fix: lên thành phố; line 10 Chuyện ngày đó bác không quên đâu, cháu ạ.
    Bây giờ bác hạnh phúc lắm. Notes follow. Status: open.

19. **L28:6, 9 and translate 2.** "Khi các cháu xong" (xong with no verb, doubt L28.3) → Khi các cháu làm xong thì …;
    line 9 jumps to after dinner with no marker → Cơm ngon quá! … and the setting says they stay for dinner;
    "bơi khoảng một giờ" (doubt L28.7: Hà Nội says một tiếng for a duration, một giờ is also "one o'clock") →
    khoảng ba mươi phút. Status: open.

20. **Smaller exercise points.** L18 translate 2: Lan teaches Bin, 8, to read, but Bin reads Vietnamese better than
    Sacha (L21) → Na; L26 translate 4: Thảo swims "with Minh" → with Sacha (L18); fills whose particle is told apart
    only by register (L16 fills 2–3 hả / à, nhá / nhé; L21 fills 3–4 với / đi, hả / à): the English now names the
    register. L19:3 English "Coming!" → "Yes, here I am!" (cháu đây). Status: open.

21. **Two notes.** L27 note ref 2 "lớn is more formal": lớn is the general and Southern word, not formal; now "lớn is
    the general word, and the South's". L23 note ref 1 named chủ nhà without the lines using it (kept: the speaker
    label says it). Status: open.

22. **Lint: the person-term check read chú in chú_ý as the kin term chú.** `kin_mismatch` split the line after
    `vi.display()`, which turns underscores into spaces, so every compound starting with a kin syllable (chú_ý, cô_giáo,
    con_trai, anh_trai…) counted as a person term: "Em chú_ý nhé, anh ngồi sau" was a warning. Fix: split the raw line
    (words keep their underscores; tags are read by `vi.words`); test in tools/test_review5.py.
    Status: open.

23. **Segmentation points of the writer.** (a) *thế thì*: the dictionary has it ("so, then, in that case"), but it
    is thế (pro-form "so, like that") + thì (the main-clause marker of L22) used freely (nếu thế thì, thế thì sao?):
    two words, as written; SEGMENTATION gets one sentence. (b) *buổi sáng*: SEGMENTATION's time word, one word, is
    right; the lessons are right to avoid it until a word list teaches buổi_sáng (NOTES L18.7 kept, a word-list
    point). (c) *chú in chú_ý*: finding 22. (d) Found here: the cutter joins cả_nhà and ăn_cơm (dictionary entries),
    while the lessons write cả nhà (quantifier + noun, like mọi người) and ăn cơm (as L10, L14 and the cutter
    reference line 109): only external texts and examples are cut by the cutter, the lessons keep their boundaries;
    left for a cutter pass (NOTES). Status: open.

24. **The writer's tool change (plan.py EN_MORE + "run")** is right and minimal: the gloss "to run" of chạy made the
    plan check read the English word as Vietnamese run "to tremble"; the set already holds such words (ten, can, ban).
    No change. Status: open.

25. **Line counts** 9 9 10 10 10 10 10 10 11 11 11 11 11 11 are exactly the plan's; L14 (a review) has 10 and L15 9,
    a dip the plan made (L14 planned 9). Notes 9 a lesson. No change. Status: open.

## Doubts the writer flagged (decided)
- **máy for the phone** (L15): the shop's and everyday word (máy này, máy cũ, đổi máy): keep.
- **Thôi, anh lấy máy trắng này** (L15:9): Thôi closing a choice is ordinary: keep.
- **Giúp em với! to a bookseller** (L17:1): a little pleading, heard in shops when one cannot find something: keep;
  still a native point.
- **Dạ, cháu đây ạ** (L19:3) answering a call from the door: the planned use; keep, English fixed (finding 20).
- **cô ở trường cháu** (L19:7) for "my teacher": understandable, cô giáo cháu more usual (not taught): keep, native.
- **Tôi cũng thế after a negative** (L20:3): cũng thế / cũng vậy agree with a negative as well: keep.
- **Ngày đó** "in those days" (L27): natural (ngày đó / ngày ấy); hồi đó waits for L48: keep.
- **một giờ vs một tiếng** for a duration (L28): changed (finding 19).
- **bà / bác in one scene** (L27): right: the grandmother is bà to her grandchildren and bác to Sacha: keep.
