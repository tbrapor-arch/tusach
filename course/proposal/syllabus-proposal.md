# Tủ sách — syllabus proposal (second version)

**Approved by the owner on 19 Nov 2026** (with word list 2; `course/syllabus.yaml` records both). His answers to
section 10: no native speaker is available, so lessons are drafted and labelled unchecked (Q1); tendencies are taught,
labelled as such (Q2). Priority: Vietnamese first; the Chinese bridge helps, bounded (CLAUDE.md). Written by Claude,
18 Nov 2026, branch `data-quality`; **not checked by a native speaker**. Word list: `wordlist-2.tsv` (lessons 1–13), its doubts in
`wordlist-2-to-check.md`. Sound rules measured with `tools/bridge_rules.py` (numbers below are its output).

**What changed since the first proposal**
1. The owner's twelve decisions are applied (below); the story is now Sacha's, with a cast whose ages drive the pronouns.
2. Word list 2 replaces word list 1, with the essentials review 2 found missing; ạ (L1), nhé (L3), nhỉ (L9) agree with the grammar plan.
3. Every sound rule is measured on 994 Hán-Việt syllables (1,502 cards of the top 3,000), with its direction and exceptions.
4. Tones corrected: a level-tone syllable with m n nh ng l v d is ngang (nam 南), not huyền; 動 động, 後 hậu are regular.
5. Initials rebuilt by old (Middle Chinese) class; five old rules dropped; Lesson 0 outlined; all 100 lessons planned.

## Decided (the owner, 18 Nov 2026)

1. **100 lessons**, then a second course, *Perfectionnement*: written and formal Vietnamese (press, essays, literature,
   administration) and the denser Hán-Việt vocabulary. Not planned here.
2. **Hán-Việt words from lesson 2**, where a Hà Nội speaker would use them.
3. **Pronouns**: tôi with anh / chị / em from lesson 1; **bạn** early (L11) as the neutral or written "you".
4. **chữ Hán on the card from lesson 1**; hidden when the etymology is doubtful (`doubt_chars`).
5. **Older Chinese loans** (được 得, giấy 紙) shown on the card as an older layer, apart from Hán-Việt.
6. **Southern usage**: one line when a word differs; one lesson set in Sài Gòn (L67).
7. **Brief comparisons with French** allowed; the course is in English.
8. **House spelling**, enforced by lint: công ty, kỹ thuật, lý do.
9. **Main character Sacha**, with a small recurring cast (below).
10. **Tea: trà** in the dialogues; the card notes chè (see below).
11. **Lesson 0**: reading quốc ngữ and the six Hà Nội tones (outline below).
12. **Word list 2 replaces word list 1.**

**Sacha.** 27, from Lyon. He studied Chinese at university and spent a year in Taipei, so he reads characters
and knows some Taiwanese. His company, a small French engineering firm, sends him to its Hà Nội office for one year;
he lands with no Vietnamese and rents a room in chị Lan's family house near the Old Quarter.

**The cast** (ages decide the pronouns; "he says / they say" is what Sacha says for "you" and what they call him):

| Person | Age | To Sacha | Sacha says / they say |
|---|---|---|---|
| chị Lan, the landlady | 35 | 8 years older | chị / em |
| anh Minh, her husband | 38 | older | anh / em |
| her mother (bà to the children) | 62 | his parents' generation | bác / cháu |
| Bin and Na, her children | 8, 5 | children | cháu / chú |
| Thảo, Lan's younger sister, a student | 24 | 3 years younger | em / anh |
| anh Tuấn, his manager | 41 | older | anh / em |
| Mai, a colleague | 27 | same age | bạn / bạn (and tôi, later mình, for "I") |
| ông Hùng, the old neighbour | 78 | grandparents' generation | ông / cháu |

**trà or chè.** The previous session's lexicon row (trà~tea, kept): trà is the usual word, Hà Nội included (trà đá,
trà chanh, trà sữa at every café and stall), and is more frequent: <!-- plan:tra-che -->trà 60,092 against chè 2,989 per billion words (course ranks 1345 and 11197; tools/freq.py, chè counting the dessert too)<!-- /plan -->. The card adds: in the North chè is also tea, at home and for the leaf
(nước chè, chè xanh), and everywhere chè is a sweet dessert soup. Who still says chè at home in Hà Nội is not
checked (to-check list, item 1).

## 1. Shape of the course

- **100 lessons**; every 7th is a review (7, 14 … 98): 14 reviews, 86 new lessons.
- **Second wave from lesson 50**: with lesson N, redo lesson N−49 from English into Vietnamese (as the app does).
- **A lesson**: title, one line of setting, a dialogue, notes (grammar, pronouns, at most one bridge note, a Southern
  or false-friend line when due), new words (English on every card), two exercises (translate, fill the gap) in new
  sentences, never the dialogue's. **A review**: a new dialogue on the week's words, a recap note, no new words.

**Lines per dialogue**, reviews included (smooth, about one more line every six lessons):
lines(n) = round(7 + 8(n−1)/49) up to lesson 50, then round(15 + 5(n−50)/50).

| Lesson | 1 | 8 | 15 | 22 | 29 | 36 | 43 | 50 | 61 | 71 | 81 | 91 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Lines | 7 | 8 | 9 | 10 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |

**New words per lesson** (names apart). Lessons 1–13 are word list 2's real counts (tools/plan.py); from 15, total(n) =
round(18 + 6(n−15)/85) and the Hán-Việt share grows from a quarter to over half. "Other" = older Chinese loans and
Western loans; lint counts them with the native words.

| Lessons | 1–6 | 8–13 | 15–20 | 22–34 | 36–48 | 50–62 | 64–76 | 78–90 | 92–100 |
|---|---|---|---|---|---|---|---|---|---|
| New words | 16–18 | 16–18 | 18 | 18–19 | 19–20 | 20–21 | 21–22 | 22–23 | 23–24 |
| of which Hán-Việt | 0–5 | 2–6 | 5 | 5–7 | 7–8 | 9–10 | 10–11 | 11–12 | 12–13 |

<!-- plan:counts -->Word list 2 (L1–13): 207 words + 3 names (L1 16, L2 16, L3 18, L4 18, L5 17, L6 17, L8 16, L9 17, L10 18, L11 18, L12 18, L13 18); Hán-Việt 38 (18 %), older Chinese loans 28 (6 with a doubtful etymon, characters hidden), Western loans 2, the rest native, compounds and 41 with no etymology recorded.<!-- /plan -->
The whole course: about 1,750 words (native 893, Hán-Việt 724 = 41 %, other 131).

## 2. Lesson 0 — reading quốc ngữ (outline only)

For a reader of English, French and Chinese who knows phonetics; IPA throughout; each sound beside the nearest one in
French, English, Mandarin, Cantonese or Taigi. Not the text, which is to be written after approval.

1. **The syllable**: initial + (glide) + vowel + final + tone; one written syllable = one morpheme, like a character.
   Spelling is close to phonemic, with Hà Nội mergers (6).
2. **Vowels**: a [aː] / ă [a] — the Cantonese aa / a contrast (saam1 / sam1); â [ə] short, ơ [əː];
   e [ɛ] French è, ê [e] French é; o [ɔ] French *or*, ô [o] French *eau*; i / y [i]; u [u]; ư [ɨ] (Quanzhou-type
   Taigi *ir*; no French or Mandarin match). Diphthongs ia/iê [iə], ưa/ươ [ɨə], ua/uô [uə].
3. **Initials**: b [ɓ], đ [ɗ] (implosive, voiced: not Mandarin b, d); t [t] = Mandarin d, Taigi t; th [tʰ];
   c/k/q [k] = Mandarin g; kh [x] = Mandarin h; ph [f]; g/gh [ɣ]; ng/ngh [ŋ] = Cantonese ng-, Taigi ng; nh [ɲ] =
   French gn; v [v]; h, l, m, n. The spelling rules c/k/q, g/gh, ng/ngh (k, gh, ngh before i e ê).
4. **Finals**: -p -t -c unreleased, as in Cantonese and Taigi; -m -n -ng; after o ô u, -ng and -c close the lips
   (học [hawk͡p]); Hà Nội -nh [ajŋ] and -ch [ajk] after a.
5. **The six Hà Nội tones**, with pitch numbers from published descriptions (Claude's summary, to be checked by ear):
   ngang 33 mid level; huyền 21 low falling, breathy; sắc 35 rising; hỏi 31(2) low falling, kept apart from ngã;
   ngã 3ʔ5 rising, broken by a glottal catch; nặng 21ʔ low, short, glottal. Nearest Chinese tones (Cantonese 3, 4,
   2, Mandarin 3 …) as anchors only. A syllable in -p -t -c -ch has sắc or nặng only.
6. **What Hà Nội merges**: d, gi, r → [z]; ch, tr → [c]; s, x → [s]. The spelling of native words is learnt by
   heart; for Hán-Việt words the Chinese decides (section 5, rules Z1–Z3). The South keeps tr, s, r apart and
   merges hỏi / ngã and d / v: one line.
7. **House spelling**: y in lý, kỹ, công ty; tone marks placed the house way (lint).
8. **Drills**: ma má mà mả mã mạ; tone pairs; place names (Hà Nội, Hải Phòng, Đà Nẵng).

## 3. The tone strand (Hán-Việt words only)

**How the rules are measured** (`tools/bridge_rules.py`; every number in sections 3–5 is its output, written into
this file by `tools/bridge_rules.py --write`, and `make lint` fails when they differ). The data: the Hán-Việt
syllables of the top 3,000 cards; native words and older loans follow none of this.
<!-- rules:summary -->
993 syllables (character + Hán-Việt reading) of 1499 Hán-Việt cards of rank <= 3000. 132 measured: 91 rules, 14 tendencies, 16 that narrow the choice, 2 facts of spelling, 9 dropped. Every tone from Cantonese: main 910 / 993, 92 %, strict 797 / 993, 80 %; from Taigi: main 878 / 959, 92 %, strict 853 / 959, 89 %.
<!-- /rules -->
- **The reading he would use.** For each character, the word's own reading when the source has the word (rime,
  CC-CEDICT, the MOE); else the character's most frequent reading in the source's own order (rime's share; the MOE's
  literary reading; Unihan's customary Mandarin reading). A Cantonese **changed tone** (變音: 錢 cin2, 社會 se5 wui2,
  where the source also has cin4, wui6) is counted with its base tone, as Hán-Việt is: the learner is told that a
  tone-2 word he also knows in a low tone is a changed tone.
- **Main, strict, lenient.** "Main" uses that reading; "strict" requires every reading the item could have (all the
  character's readings when the word is not in the source) to fit; "lenient" (from the Vietnamese side only) one of
  them. The thresholds apply to the **main** rate: a **rule** at 80 % or more, a **tendency** from 60 %, else
  dropped. A rule whose outcome is a set of letters is also given its **best single guess** (the most frequent
  letter's share): under 60 % it is taught as **"narrows it to these letters"**, not as a prediction.
- **Only what he has.** A zh→vi rule uses only the Chinese side: "sonorant initial" is the Cantonese initial
  (m n ng l j w or none), the Taigi one (m n ng l j b g or none) or the Mandarin one (m n l r y w or none), and
  "not -p -t -k" is the Cantonese final. The second proposal's "Cantonese 4 with a sonorant initial → ngang" used
  the Vietnamese initial (circular: 100 %); with the Cantonese initial it misses the 匣 words (形 hình, 黃 hoàng,
  和 hòa), whose Cantonese initial is h- or w- but whose old initial was a voiced fricative. A vi→zh rule uses only
  the Vietnamese he hears.

**The old classes.** Hán-Việt splits each of the four old tones by the old initial, but **not the way Cantonese and
Taigi do** (the first proposal said "exactly the split Cantonese and Taigi made": false). Two differences matter:
- **Level tone, sonorant initial → ngang**, with the voiceless ones (nam 南, minh 明, dân 民), where Cantonese
  (4), Taigi (5) and Mandarin (2) put them with the voiced obstruents.
- **Rising tone**: Hán-Việt has three outcomes (hỏi voiceless, ngã sonorant, nặng voiced obstruent). Cantonese
  keeps 2 / 5 / 6 (some old voiced obstruents are 5); Taigi has one rising tone (2) for the first two and moved the
  third to 7; Mandarin has 3 / 3 / 4. So **động 動 and hậu 後 are regular** (old voiced obstruent, rising → nặng).

| Old class | Hán-Việt | Cantonese | Taigi lit. | Mandarin |
|---|---|---|---|---|
| level, voiceless | ngang | 1 | 1 | 1 |
| level, voiced obstruent | huyền | 4 | 5 | 2 |
| level, sonorant | **ngang** | 4 | 5 | 2 |
| rising, voiceless | hỏi | 2 | 2 | 3 |
| rising, sonorant | ngã | 5 | 2 | 3 |
| rising, voiced obstruent | nặng | 6 (some 5) | 7 | 4 |
| departing, voiceless | sắc | 3 | 3 | 4 |
| departing, voiced | nặng | 6 | 7 | 4 |
| entering (-p -t -c), voiceless | sắc | 1 / 3 | 4 | any |
| entering, voiced | nặng | 6 | 8 | any |

Each of Cantonese and Taigi needs the Chinese initial for two tones (Cantonese 4 and 5, Taigi 5 and 2), Mandarin
for 2 and 3; Mandarin 4 does not tell sắc from nặng, and Mandarin has no checked syllables: there Cantonese or
Taigi decides.

**From Cantonese (zh→vi)**
<!-- rules:tones-yue -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| T1 | Cantonese 1, not -p -t -k → ngang | zh→vi | 183 / 195, 94 % | 188 / 224, 84 % |  |  | **rule** | 分 phần 當 đáng 監 giám 坊 phường 將 tướng 擔 đảm 分 phận 胞 bào |
| T1 | Cantonese 4, initial m n ng l j w or none → ngang | zh→vi | 78 / 90, 87 % | 81 / 97, 84 % |  |  | **rule** | 形 hình 完 hoàn 壺 hồ 回 hồi 和 hòa 黃 hoàng 型 hình 湖 hồ |
| T1 | Cantonese 4, other initial → huyền | zh→vi | 85 / 89, 96 % | 88 / 105, 84 % |  |  | **rule** | 重 trọng 查 tra 長 trưởng 傳 truyện |
| T2 | Cantonese 2 → hỏi | zh→vi | 106 / 117, 91 % | 113 / 168, 67 % |  |  | **rule** | 數 số 統 thống 少 thiếu 襖 áo 館 quán 許 hứa 棗 táo 使 sứ |
| T2 | Cantonese 5, initial m n ng l j w or none → ngã | zh→vi | 35 / 42, 83 % | 35 / 43, 81 % |  |  | **rule** | 會 hội 理 lý 與 dự 議 nghị 濫 lạm 李 lý 里 lý |
| T2 | Cantonese 5, other initial → nặng (old voiced 上) | zh→vi | 6 / 8, 75 % | 11 / 18, 61 % |  |  | **tendency** | 社 xã 妥 thỏa |
| T3 | Cantonese 3, not -p -t -k → sắc | zh→vi | 122 / 137, 89 % | 139 / 180, 77 % |  |  | **rule** | 過 qua 間 gian 轉 chuyển 句 câu 處 xử 載 tải 計 kê 撰 soạn |
| T3 | Cantonese 6, not -p -t -k → nặng | zh→vi | 134 / 149, 90 % | 144 / 180, 80 % |  |  | **rule** | 問 vấn 士 sĩ 義 nghĩa 互 hỗ 調 điều 靜 tĩnh 技 kỹ 彈 đàn |
| T4 | Cantonese -p -t -k in tone 1 or 3 → sắc | zh→vi | 83 / 85, 98 % | 88 / 99, 89 % |  |  | **rule** | 絡 lạc 協 hiệp |
| T4 | Cantonese -p -t -k in tone 6 → nặng | zh→vi | 78 / 81, 96 % | 83 / 88, 94 % |  |  | **rule** | 隰 thấp 率 suất 摘 trích |
| T* | every tone from Cantonese (the rules above together) | zh→vi | 910 / 993, 92 % | 797 / 993, 80 % |  |  | **rule** | 數 số 分 phần 過 qua 間 gian 問 vấn 重 trọng 轉 chuyển 社 xã |
| T1x | Cantonese 4 → huyền, whatever the initial (first proposal) | dropped | 97 / 179, 54 % | 100 / 200, 50 % |  |  | **drop** | 如 như 仍 nhưng 南 nam 由 do 重 trọng 民 dân 員 viên 查 tra |
| T1x | Cantonese 4 → ngang when the VIETNAMESE initial is m n nh ng l v d (proposal 2: circular) | dropped | 76 / 76, 100 % | 77 / 79, 97 % |  |  | **drop** | — |

Changed tones: 18 items of the Cantonese total have a changed tone (變音: 錢 cin2, 社會 se5 wui2) in the word; the main rate uses the base tone (cin4, wui6), as the tones of Hán-Việt do; the strict rate counts the changed tone too.
<!-- /rules -->

**From Taigi (zh→vi)**
<!-- rules:tones-nan -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| T1 | Taigi 1 → ngang | zh→vi | 180 / 195, 92 % | 182 / 201, 91 % |  |  | **rule** | 分 phần 組 tổ 當 đáng 勝 thắng 技 kỹ 坊 phường 將 tướng 擔 đảm |
| T1 | Taigi 5, initial m n ng l j b g or none → ngang | zh→vi | 71 / 74, 96 % | 71 / 74, 96 % |  |  | **rule** | 條 điều 完 hoàn 湖 hồ |
| T1 | Taigi 5, other initial → huyền | zh→vi | 90 / 95, 95 % | 92 / 99, 93 % |  |  | **rule** | 重 trọng 查 tra 傳 truyện 彈 đạn 降 giáng |
| T2 | Taigi 2, initial m n ng l j b g or none → ngã | zh→vi | 33 / 44, 75 % | 33 / 44, 75 % |  |  | **tendency** | 影 ảnh 理 lý 研 nghiên 與 dự 穩 ổn 擁 ủng 委 ủy 隱 ẩn |
| T2 | Taigi 2, other initial → hỏi | zh→vi | 97 / 110, 88 % | 99 / 114, 87 % |  |  | **rule** | 統 thống 少 thiếu 轉 chuyến 輔 phụ 館 quán 處 xứ 許 hứa 棗 táo |
| T3 | Taigi 3 → sắc | zh→vi | 114 / 129, 88 % | 124 / 152, 82 % |  |  | **rule** | 過 qua 現 hiện 句 câu 棧 sạn 附 phụ 弊 tệ 卷 quyển 載 tải |
| T3 | Taigi 7 → nặng | zh→vi | 137 / 151, 91 % | 141 / 161, 88 % |  |  | **rule** | 問 vấn 社 xã 士 sĩ 義 nghĩa 互 hỗ 靜 tĩnh 態 thái 俱 câu |
| T4 | Taigi 4 → sắc | zh→vi | 79 / 80, 99 % | 79 / 81, 98 % |  |  | **rule** | 屬 thuộc |
| T4 | Taigi 8 → nặng | zh→vi | 77 / 81, 95 % | 79 / 83, 95 % |  |  | **rule** | 的 đích 複 phức 築 trúc 洩 tiết |
| T* | every tone from Taigi (the rules above together) | zh→vi | 878 / 959, 92 % | 853 / 959, 89 % |  |  | **rule** | 條 điều 分 phần 過 qua 組 tổ 問 vấn 屬 thuộc 現 hiện 重 trọng |
<!-- /rules -->

**From Mandarin (zh→vi)**
<!-- rules:tones-cmn -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| T1 | Mandarin 1 → ngang | zh→vi | 179 / 216, 83 % | 185 / 237, 78 % |  |  | **rule** | 一 nhất 分 phần 織 chức 發 phát 接 tiếp 究 cứu 當 đáng 出 xuất |
| T1 | Mandarin 1, not -p -t -k in Cantonese → ngang | zh→vi | 179 / 196, 91 % | 185 / 217, 85 % |  |  | **rule** | 分 phần 究 cứu 當 đáng 期 kỳ 監 giám 擁 ủng 坊 phường 將 tướng |
| T1 | Mandarin 2, initial m n l r y w or none → ngang | zh→vi | 74 / 75, 99 % | 75 / 78, 96 % |  |  | **rule** | 完 hoàn |
| T1 | Mandarin 2, other initial → huyền | zh→vi | 91 / 94, 97 % | 96 / 112, 86 % |  |  | **rule** | 查 tra 傳 truyện 華 hoa |
| T2 | Mandarin 3, initial m n l r y w or none → ngã | zh→vi | 35 / 43, 81 % | 35 / 45, 78 % |  |  | **rule** | 影 ảnh 理 lý 襖 áo 穩 ổn 委 ủy 隱 ẩn 飲 ẩm 里 lý |
| T2 | Mandarin 3, other initial → hỏi | zh→vi | 102 / 127, 80 % | 104 / 134, 78 % |  |  | **rule** | 場 trường 屬 thuộc 統 thống 少 thiếu 導 đạo 北 bắc 轉 chuyến 給 cấp |
| T3 | Mandarin 4, not -p -t -k in Cantonese → sắc or nặng | zh→vi | 264 / 290, 91 % | 282 / 330, 85 % |  | nặng 50 % | **narrows** | 過 qua 社 xã 句 câu 士 sĩ 差 sai 義 nghĩa 互 hỗ 調 điều |
<!-- /rules -->

**From the Vietnamese tone heard (vi→zh)**: here the lenient rate is the fair one (any of his readings will do).
A syllable in -p -t -c -ch takes only sắc or nặng: a fact of Vietnamese spelling, not a correspondence; which of
the two is told by Cantonese (1 / 3 or 6) or Taigi (4 or 8), above.
<!-- rules:tones-vi -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| T5 | huyền → Cantonese 4 | vi→zh | 97 / 102, 95 % | 81 / 102, 79 % | 100 / 102, 98 % |  | **rule** | 分 phần 調 điều 彈 đàn 坊 phường 胞 bào |
| T5 | ngang → Cantonese 1, or 4 after m n nh ng l v d | vi→zh | 259 / 268, 97 % | 235 / 268, 88 % | 262 / 268, 98 % |  | **rule** | 過 qua 間 gian 句 câu 查 tra 計 kê 郵 bưu 華 hoa 醬 tương |
| T5 | hỏi → Cantonese 2 | vi→zh | 106 / 116, 91 % | 95 / 116, 82 % | 113 / 116, 97 % |  | **rule** | 轉 chuyển 長 trưởng 比 tỷ 處 xử 擔 đảm 載 tải 妥 thỏa 汰 thải |
| T5 | ngã → Cantonese 5 | vi→zh | 36 / 47, 77 % | 28 / 47, 60 % | 36 / 47, 77 % |  | **tendency** | 士 sĩ 義 nghĩa 互 hỗ 靜 tĩnh 技 kỹ 纇 lỗi 櫃 quỹ 浪 lãng |
| T5 | ngã → Mandarin 3 | vi→zh | 37 / 47, 79 % | 35 / 47, 74 % | 37 / 47, 79 % |  | **tendency** | 社 xã 士 sĩ 義 nghĩa 互 hỗ 靜 tĩnh 技 kỹ 纇 lỗi 櫃 quỹ |
| T5 | sắc, open syllable → Cantonese 3 | vi→zh | 121 / 142, 85 % | 103 / 142, 73 % | 129 / 142, 91 % |  | **rule** | 數 số 問 vấn 統 thống 理 lý 當 đáng 少 thiếu 襖 áo 監 giám |
| T5 | nặng, open syllable → Cantonese 6 | vi→zh | 135 / 152, 89 % | 109 / 152, 72 % | 141 / 152, 93 % |  | **rule** | 重 trọng 會 hội 婦 phụ 市 thị 與 dự 傳 truyện 議 nghị 旱 hạn |
| T5 | nặng, open syllable → Mandarin 4 | vi→zh | 144 / 152, 95 % | 135 / 152, 89 % | 146 / 152, 96 % |  | **rule** | 係 hệ 量 lượng 導 đạo 值 trị 傳 truyện 輔 phụ 分 phận 儉 kiệm |
| T4f | a syllable in -p -t -c -ch has sắc or nặng (a fact of Vietnamese spelling) | fact | 166 / 166, 100 % | 166 / 166, 100 % |  |  | **fact** | — |
<!-- /rules -->

**Teaching order**: T1 level tones (L9), T2 rising (L11), T3 departing (L12), T4 checked (L13), T5 heard → Chinese
(L15). Examples, each the same word in Chinese with all four readings in the database:
<!-- bridge-examples -->
- T1 ngang: 心 tâm, 東 đông, 中 trung, 音 âm · ngang after a sonorant: 南 nam, 民 dân, 文明 văn minh, 門 môn, 陽 dương
  · huyền: 湖 hồ, 頭 đầu, 平 bình, 情 tình, 和平 hòa bình
- T2 hỏi: 感 cảm, 點 điểm, 水 thủy, 主 chủ, 口 khẩu · ngã: 馬 mã, 女 nữ, 美 mỹ · nặng: 動 động, 後 hậu, 部 bộ, 道 đạo
- T3 sắc: 過 quá, 世界 thế giới, 意 ý, 信 tín · nặng: 病 bệnh, 定 định, 電 điện, 大 đại
- T4 sắc: 法 pháp, 發 phát, 一 nhất, 北 bắc, 客 khách · nặng: 學 học, 實 thực, 力 lực, 立 lập, 物 vật
<!-- /bridge-examples -->

## 4. Finals and rhymes

All zh→vi unless marked; same data and tool. Mandarin lost -p -t -k and merged -m into -n; Cantonese and Taigi kept
them, and so did Hán-Việt. Lessons: B0 (what Hán-Việt is: one syllable per character, Chinese order inside the
word) L2, B1 L4, B2 L6, B3 L8, B4 L32, V1 L30, V2 L31.
<!-- rules:finals -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| B1 | Cantonese -p → -p | zh→vi | 22 / 22, 100 % | 22 / 22, 100 % |  |  | **rule** | — |
| B1 | Cantonese -t → -t | zh→vi | 41 / 44, 93 % | 41 / 46, 89 % |  |  | **rule** | 實 thực 法 pháp 壓 áp |
| B1 | Cantonese -k → -c / -ch | zh→vi | 99 / 100, 99 % | 100 / 108, 93 % |  | c 70 % | **rule** (one guess: c 70 %) | 值 trị |
| B2 | Cantonese -m → -m | zh→vi | 42 / 43, 98 % | 43 / 46, 93 % |  |  | **rule** | 禪 thiền |
| B2 | Taigi -m → -m | zh→vi | 40 / 42, 95 % | 40 / 42, 95 % |  |  | **rule** | 填 điền 忍 nhẫn |
| B3 | Hán-Việt -nh / -ch → Cantonese -ng / -k | vi→zh | 95 / 95, 100 % | 94 / 95, 99 % | 95 / 95, 100 % |  | **rule** | — |
| B4 | Mandarin -ing → -nh | zh→vi | 46 / 54, 85 % | 47 / 56, 84 % |  |  | **rule** | 憑 bằng 行 hàng 命 mạng 興 hưng 冰 băng 應 ứng 興 hứng 凝 ngưng |
| B3x | Cantonese -ing / -ik → -nh / -ch | dropped | 72 / 102, 71 % | 75 / 106, 71 % |  |  | **drop** | 仍 nhưng 認 nhận 織 chức 域 vực 勝 thắng 力 lực 食 thực 直 trực |
| V1 | Cantonese -oeng / -oek → -ương / -ươc | zh→vi | 33 / 35, 94 % | 33 / 35, 94 % |  |  | **rule** | 樣 dạng 雙 song |
| V2 | Cantonese -in / -it → -iên / -iêt | zh→vi | 40 / 43, 93 % | 41 / 45, 91 % |  |  | **rule** | 結 kết 言 ngôn 必 tất |
<!-- /rules -->

"Cantonese -ing / -ik → -nh / -ch" is dropped: the reverse (B3) is the useful direction; going forward the learner
is told only that -nh / -ch need a Cantonese -ng / -k. B1's 法 pháp, 壓 áp kept an old -p that Cantonese turned to -t.
<!-- bridge-examples -->
- B0: 越南 Việt Nam, 中國 Trung Quốc, 法 Pháp, 學 học, 河內 Hà Nội
- B1: 學習 học tập, 法律 pháp luật, 獨立 độc lập, 發展 phát triển, 國家 quốc gia
- B2: 南 nam, 心 tâm, 感 cảm, 點 điểm, 音 âm, 參加 tham gia
- B3: 生 sinh, 病 bệnh, 明白 minh bạch, 歷史 lịch sử, 客 khách
- B4: 情 tình, 定 định, 平 bình, 影 ảnh, 經濟 kinh tế
- V1: 想 tưởng, 洋 dương, 香 hương, 影響 ảnh hưởng, 戰略 chiến lược
- V2: 電 điện, 先 tiên, 年 niên, 研究 nghiên cứu, 節 tiết, 熱 nhiệt
<!-- /bridge-examples -->

## 5. Initials, by old class

Grouped by the Middle Chinese initial behind each Hán-Việt letter; each rule keyed to whichever of Cantonese, Taigi
or Mandarin predicts best, measured in its direction (**zh→vi**: from the Chinese he knows to a guess of the
Vietnamese; **vi→zh**: from a Vietnamese word heard or read to the Chinese; **spell**: which letter to write for a
sound Hà Nội merges, he hears the sound). Where a rule only narrows the choice, a second condition from another of
his languages is measured beside it (zh- with Taigi t- → tr, with Taigi ts- → ch; Mandarin j q with Cantonese g- →
c, or gi before Cantonese aa / o).

**Labials** (old p ph b; f-series; m)
<!-- rules:labials -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| IP | ph ← Mandarin f- | zh→vi | 41 / 42, 98 % | 41 / 42, 98 % |  |  | **rule** | 幅 bức |
| IP | b ← Mandarin b- | zh→vi | 38 / 42, 90 % | 39 / 43, 91 % |  |  | **rule** | 標 tiêu 比 tỷ 弊 tệ 必 tất |
| IP | b ← Taigi p- | zh→vi | 42 / 47, 89 % | 42 / 47, 89 % |  |  | **rule** | 房 phòng 標 tiêu 比 tỷ 弊 tệ 必 tất |
| IP | ph → Mandarin f- or p- | vi→zh | 50 / 50, 100 % | 50 / 50, 100 % | 50 / 50, 100 % | f 82 % | **rule** | — |
| IP | b → Mandarin b- or p- | vi→zh | 44 / 48, 92 % | 44 / 48, 92 % | 45 / 48, 94 % | b 79 % | **rule** (one guess: b 79 %) | 幅 bức 祕 bí 秘 bí 郵 bưu |
| IM | m ← Mandarin m- | zh→vi | 31 / 37, 84 % | 31 / 37, 84 % |  |  | **rule** | 民 dân 祕 bí 面 diện 名 danh 滅 diệt 秘 bí |
| IM | m → Mandarin m- | vi→zh | 31 / 31, 100 % | 30 / 31, 97 % | 31 / 31, 100 % |  | **rule** | — |
| IM | v ← Cantonese m- with Mandarin w- | zh→vi | 11 / 11, 100 % | 11 / 12, 92 % |  |  | **rule** | — |
| IM | v ← Mandarin w- (alone) | zh→vi | 15 / 24, 62 % | 15 / 26, 58 % |  |  | **tendency** | 翁 ông 完 hoàn 唯 duy 危 nguy 穩 ổn 委 ủy 外 ngoại 維 duy |
| IM | v → Mandarin w- or y- | vi→zh | 26 / 27, 96 % | 26 / 27, 96 % | 26 / 27, 96 % | w 56 % | **narrows** | 榮 vinh |
<!-- /rules -->

**Dentals** (old t th d; n l)
<!-- rules:dentals -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| ID | đ ← Mandarin d- | zh→vi | 46 / 46, 100 % | 46 / 47, 98 % |  |  | **rule** | — |
| ID | đ ← Mandarin t- in tone 2 | zh→vi | 18 / 18, 100 % | 22 / 22, 100 % |  |  | **rule** | — |
| ID | th ← Mandarin t- in tones 1 3 4 | zh→vi | 16 / 19, 84 % | 16 / 19, 84 % |  |  | **rule** | 特 đặc 突 đột 推 suy |
| ID | đ ← Taigi t- with Mandarin d- / t- | zh→vi | 58 / 58, 100 % | 59 / 60, 98 % |  |  | **rule** | — |
| ID | đ → Mandarin d- or t- | vi→zh | 66 / 66, 100 % | 65 / 66, 98 % | 66 / 66, 100 % | d 70 % | **rule** (one guess: d 70 %) | — |
| ID | n ← Mandarin n- | zh→vi | 14 / 15, 93 % | 14 / 15, 93 % |  |  | **rule** | 凝 ngưng |
| ID | l ← Mandarin l- | zh→vi | 50 / 52, 96 % | 50 / 52, 96 % |  |  | **rule** | 樂 nhạc 率 suất |
| ID | n → Mandarin n- | vi→zh | 14 / 14, 100 % | 14 / 14, 100 % | 14 / 14, 100 % |  | **rule** | — |
| ID | l → Mandarin l- | vi→zh | 50 / 50, 100 % | 50 / 50, 100 % | 50 / 50, 100 % |  | **rule** | — |
| ID | Taigi l- → l or n (Mandarin decides) | zh→vi | 59 / 61, 97 % | 59 / 70, 84 % |  | l 74 % | **rule** (one guess: l 74 %) | 條 điều 冗 nhũng |
<!-- /rules -->

**Retroflex series** (old ʈ- and tʂ- / tɕ- series: Mandarin zh ch sh)
<!-- rules:retroflex -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| IR | ch or tr ← Mandarin zh- | zh→vi | 70 / 74, 95 % | 73 / 79, 92 % |  | tr 49 % | **narrows** | 棧 sạn 者 giả 殖 thực 撰 soạn |
| IR | tr ← Mandarin zh- / ch- with Taigi t- / th- | zh→vi | 37 / 37, 100 % | 37 / 38, 97 % |  |  | **rule** | — |
| IR | ch ← Mandarin zh- with Taigi ts- | zh→vi | 34 / 47, 72 % | 34 / 50, 68 % |  |  | **tendency** | 陣 trận 爭 tranh 助 trợ 棧 sạn 狀 trạng 妝 trang 者 giả 站 trạm |
| IR | ch → Mandarin zh- | vi→zh | 34 / 34, 100 % | 34 / 34, 100 % | 34 / 34, 100 % |  | **rule** | — |
| IR | tr → Mandarin zh- or ch- | vi→zh | 51 / 52, 98 % | 50 / 52, 96 % | 51 / 52, 98 % | zh 69 % | **rule** (one guess: zh 69 %) | 責 trách |
| IR | th or s ← Mandarin sh- | zh→vi | 68 / 71, 96 % | 70 / 73, 96 % |  | th 76 % | **rule** (one guess: th 76 %) | 省 tỉnh 社 xã 賒 xa |
| IR | x or s ← Mandarin ch- in tones 1 3 4 | zh→vi | 17 / 18, 94 % | 17 / 18, 94 % |  | x 56 % | **narrows** | 場 trường |
| IR | x ← Mandarin ch- in tones 1 3 4 with Taigi tsh- | zh→vi | 9 / 16, 56 % | 9 / 16, 56 % |  |  | **drop** | 場 trường 銃 súng 差 sai 超 siêu 礎 sở 充 sung 創 sáng |
| IR | tr or th ← Mandarin ch- in tone 2 | zh→vi | 22 / 23, 96 % | 26 / 28, 93 % |  | tr 61 % | **rule** (one guess: tr 61 %) | 察 sát |
| IR | tr ← Mandarin ch- in tone 2 with Taigi t- | zh→vi | 6 / 6, 100 % | 9 / 10, 90 % |  |  | **rule** | — |
| IR | th ← Mandarin ch- in tone 2 with Taigi s- / tsh- | zh→vi | 7 / 10, 70 % | 7 / 13, 54 % |  |  | **tendency** | 查 tra 察 sát 持 trì |
| IR | x → Mandarin ch- | vi→zh | 10 / 15, 67 % | 10 / 15, 67 % | 10 / 15, 67 % |  | **tendency** | 社 xã 確 xác 賒 xa 殼 xác 侵 xâm |
| IR | s → Mandarin sh- or ch- | vi→zh | 22 / 31, 71 % | 21 / 31, 68 % | 23 / 31, 74 % | sh 45 % | **narrows** | 冊 sách 所 sở 色 sắc 策 sách 棧 sạn 率 suất 撰 soạn 推 suy |
<!-- /rules -->

The exceptions to "ch" and "th" are mostly one old group, the 莊 series (爭 助 狀 莊 → tr; 事 生 史 使 士 → s).
Mandarin marks part of it: where the other series have zh ch sh, some 莊 words have z c s (所 suǒ sở, 色 sè sắc,
策 cè sách, 冊 cè sách, 責 zé trách), and these go with the dental sibilants' exceptions below; the rest of the
group is marked by none of his three varieties and is taught as a list.

**Dental sibilants** (old ts tsh dz s z: Mandarin z c s, or j q x before i / ü)
<!-- rules:sibilants -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| IS | t ← Mandarin z- | zh→vi | 28 / 29, 97 % | 29 / 30, 97 % |  |  | **rule** | 責 trách |
| IS | t or th ← Mandarin j q x with Cantonese z c s | zh→vi | 69 / 71, 97 % | 70 / 72, 97 % |  | t 85 % | **rule** | 需 nhu 侵 xâm |
| IS | t ← Mandarin z c s j q x with Cantonese z c s and Taigi ts- / s- | zh→vi | 103 / 108, 95 % | 104 / 109, 95 % |  |  | **rule** | 所 sở 責 trách 色 sắc 需 nhu 搜 sưu |
| IS | th ← Mandarin z c s j q x with Cantonese z c s and Taigi tsh- | zh→vi | 14 / 17, 82 % | 14 / 19, 74 % |  |  | **rule** | 策 sách 侵 xâm 縱 tung |
| IS | t → Mandarin z c s j q x | vi→zh | 110 / 116, 95 % | 110 / 116, 95 % | 111 / 116, 96 % | x 29 % | **narrows** | 省 tỉnh 標 tiêu 比 tỷ 弊 tệ 必 tất 慧 tuệ |
| IS | t + i y ê iê ư ươ → Mandarin j q x | vi→zh | 37 / 52, 71 % | 37 / 52, 71 % | 38 / 52, 73 % | x 35 % | **narrows** | 自 tự 省 tỉnh 司 ty 秭 tỷ 標 tiêu 比 tỷ 資 tư 詞 từ |
| IS | t + other vowels → Mandarin z c s | vi→zh | 39 / 64, 61 % | 39 / 64, 61 % | 40 / 64, 62 % | z 36 % | **narrows** | 續 tục 旬 tuần 全 toàn 心 tâm 進 tấn 集 tập 絕 tuyệt 宣 tuyên |
| IS | t → Cantonese z c s | vi→zh | 111 / 116, 96 % | 110 / 116, 95 % | 111 / 116, 96 % | z 48 % | **narrows** | 標 tiêu 比 tỷ 弊 tệ 必 tất 慧 tuệ |
<!-- /rules -->

**Velars and h** (old k kh g; ŋ; x ɣ)
<!-- rules:velars -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| IK | c / k / q ← Mandarin g- | zh→vi | 45 / 46, 98 % | 46 / 50, 92 % |  |  | **rule** | 概 khái |
| IK | c / k / q or gi ← Taigi k- | zh→vi | 119 / 124, 96 % | 120 / 126, 95 % |  | c 81 % | **rule** | 縣 huyện 枯 khô 緊 khẩn 概 khái 券 khoán |
| IK | c, kh, h or gi ← Mandarin j q x with Cantonese g k h | zh→vi | 125 / 126, 99 % | 125 / 127, 98 % |  | c 51 % | **narrows** | 確 xác |
| IK | gi ← Mandarin j- with Cantonese g- + aa / o | zh→vi | 19 / 19, 100 % | 19 / 19, 100 % |  |  | **rule** | — |
| IK | c ← Mandarin j- / q- with Cantonese g- / k- (not + aa / o) | zh→vi | 64 / 69, 93 % | 64 / 69, 93 % |  |  | **rule** | 區 khu 曲 khúc 緊 khẩn 頃 khoảnh 券 khoán |
| IK | kh ← Cantonese h- / f- with Mandarin k- / q- | zh→vi | 23 / 25, 92 % | 23 / 25, 92 % |  |  | **rule** | 殼 xác 況 huống |
| IK | kh ← Taigi kh- | zh→vi | 25 / 34, 74 % | 25 / 34, 74 % |  |  | **tendency** | 權 quyền 確 xác 擒 cầm 殼 xác 吸 hấp 俱 câu 儉 kiệm 昆 côn |
| IK | c / k / q → Mandarin g j k q | vi→zh | 110 / 110, 100 % | 110 / 110, 100 % | 110 / 110, 100 % | j 49 % | **narrows** | — |
| IK | c / k / q + i y ê iê ư ươ → Mandarin j q | vi→zh | 34 / 35, 97 % | 34 / 35, 97 % | 34 / 35, 97 % | j 89 % | **rule** | 剛 cương |
| IK | c / k / q + other vowels → Mandarin g k | vi→zh | 45 / 75, 60 % | 45 / 75, 60 % | 46 / 75, 61 % | g 59 % | **narrows** | 權 quyền 決 quyết 郡 quận 句 câu 級 cấp 警 cảnh 軍 quân 機 cơ |
| IK | c / k / q → Taigi k- | vi→zh | 101 / 107, 94 % | 101 / 107, 94 % | 101 / 107, 94 % |  | **rule** | 權 quyền 擒 cầm 俱 câu 儉 kiệm 昆 côn 琴 cầm |
| IK | kh → Mandarin k- or q- | vi→zh | 28 / 30, 93 % | 28 / 30, 93 % | 28 / 30, 93 % | k 60 % | **rule** (one guess: k 60 %) | 緊 khẩn 概 khái |
| IK | kh → Taigi kh- | vi→zh | 25 / 29, 86 % | 25 / 29, 86 % | 25 / 29, 86 % |  | **rule** | 枯 khô 緊 khẩn 概 khái 券 khoán |
| IK | gi → Mandarin j- with Cantonese g- | vi→zh | 19 / 20, 95 % | 18 / 20, 90 % | 19 / 20, 95 % |  | **rule** | 者 giả |
| IG | ng / ngh ← Taigi g- | zh→vi | 23 / 25, 92 % | 23 / 25, 92 % |  |  | **rule** | 樂 nhạc 牙 nha |
| IG | ng / ngh → Taigi g- | vi→zh | 23 / 25, 92 % | 23 / 25, 92 % | 23 / 25, 92 % |  | **rule** | 伍 ngũ 偶 ngẫu |
| IH | h ← Mandarin h- / x- with Cantonese h- / f- / w- / j- | zh→vi | 81 / 83, 98 % | 81 / 84, 96 % |  |  | **rule** | 話 thoại 慧 tuệ |
| IH | Taigi h- → h, but ph when Mandarin has f- | zh→vi | 116 / 119, 97 % | 116 / 119, 97 % |  |  | **rule** | 幅 bức 降 giáng 慧 tuệ |
| IH | h → Mandarin h- or x- | vi→zh | 82 / 86, 95 % | 80 / 86, 93 % | 82 / 86, 95 % | h 53 % | **narrows** | 完 hoàn 有 hữu 況 huống 友 hữu |
| IH | h → Taigi h- | vi→zh | 77 / 86, 90 % | 76 / 86, 88 % | 77 / 86, 90 % |  | **rule** | 縣 huyện 完 hoàn 畫 hoạch 有 hữu 吸 hấp 湖 hồ 畫 họa 友 hữu |
<!-- /rules -->

So Mandarin j q x, which Mandarin merged, split again by Cantonese: g k h → c kh h gi; z c s → t th.

**No initial, v, d, nh** (old ʔ, the glides, ɲ)
<!-- rules:glides -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| IY | nh ← Mandarin r- | zh→vi | 13 / 16, 81 % | 13 / 16, 81 % |  |  | **rule** | 阮 nguyễn 容 dung 榮 vinh |
| IY | nh → Mandarin r-, y- or none | vi→zh | 19 / 21, 90 % | 19 / 21, 90 % | 20 / 21, 95 % | r 62 % | **rule** (one guess: r 62 %) | 樂 nhạc 需 nhu |
| IY | nh ← Taigi j- | zh→vi | 12 / 12, 100 % | 12 / 12, 100 % |  |  | **rule** | — |
| IY | d ← Mandarin y- with Cantonese j- in tone 4 5 6, Taigi no initial | zh→vi | 25 / 33, 76 % | 25 / 33, 76 % |  |  | **tendency** | 越 việt 員 viên 有 hữu 園 viên 宇 vũ 羽 vũ 郵 bưu 友 hữu |
| IY | d → Mandarin y- | vi→zh | 27 / 34, 79 % | 27 / 34, 79 % | 27 / 34, 79 % |  | **tendency** | 民 dân 唯 duy 面 diện 容 dung 名 danh 滅 diệt 維 duy |
| IY | d → Cantonese j- | vi→zh | 27 / 34, 79 % | 26 / 34, 76 % | 27 / 34, 79 % |  | **tendency** | 民 dân 唯 duy 面 diện 名 danh 滅 diệt 遺 di 維 duy |
| IY | no initial ← Mandarin y- / w- / none with Cantonese j- / w- / none in tone 1 2 3 | zh→vi | 32 / 35, 91 % | 32 / 41, 78 % |  |  | **rule** | 一 nhất 因 nhân 姻 nhân |
| IY | no initial → Mandarin y-, w- or none | vi→zh | 32 / 32, 100 % | 32 / 32, 100 % | 32 / 32, 100 % | y 62 % | **rule** (one guess: y 62 %) | — |
| IY | no Hán-Việt syllable starts with r | fact | 993 / 993, 100 % | 993 / 993, 100 % |  |  | **fact** | — |
<!-- /rules -->

**Aspiration across the classes** (the old voiced stops lost their voice; Cantonese and Mandarin aspirate some):
these only narrow the letter to a set; the class rules above choose within it.
<!-- rules:aspiration -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| IA | Cantonese p t k kw c in tone 4 / 5 → b đ c t tr ch gi (old voiced) | zh→vi | 69 / 70, 99 % | 82 / 89, 92 % |  | tr 27 % | **narrows** | 妥 thỏa |
| IA | Mandarin p t k q c ch in tone 2 → b đ c t tr ch gi (old voiced) | zh→vi | 59 / 69, 86 % | 69 / 79, 87 % |  | đ 26 % | **narrows** | 常 thường 城 thành 成 thành 察 sát 殼 xác 船 thuyền 承 thừa 誠 thành |
| IA | Mandarin p t k q c ch in tones 1 3 4 → ph th kh x s | zh→vi | 90 / 96, 94 % | 91 / 98, 93 % |  | th 32 % | **narrows** | 場 trường 特 đặc 期 kỳ 突 đột 況 huống 昆 côn |
<!-- /rules -->

**Spelling what Hà Nội merges** (the Chinese decides the letter; native words are learnt by heart)
<!-- rules:spelling -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| Z1 | d or gi: gi when Cantonese has g- | spell | 53 / 54, 98 % | 53 / 54, 98 % |  |  | **rule** | 者 giả |
| Z1 | d or gi: gi when Mandarin has j- | spell | 53 / 54, 98 % | 52 / 54, 96 % |  |  | **rule** | 者 giả |
| Z2 | tr or ch: ch when Taigi has ts- | spell | 74 / 85, 87 % | 72 / 85, 85 % |  |  | **rule** | 陣 trận 爭 tranh 責 trách 助 trợ 狀 trạng 妝 trang 站 trạm 莊 trang |
| Z3 | s or x: x when Mandarin has ch- | spell | 33 / 46, 72 % | 33 / 46, 72 % |  |  | **tendency** | 社 xã 察 sát 產 sản 確 xác 賒 xa 銃 súng 差 sai 殼 xác |
| Z3 | s or x: x when Taigi has tsh- | spell | 32 / 44, 73 % | 31 / 44, 70 % |  |  | **tendency** | 社 xã 察 sát 確 xác 賒 xa 銃 súng 差 sai 殼 xác 超 siêu |
<!-- /rules -->

**Dropped from the first proposal** (measured, zh→vi; "v ← Mandarin w- alone", a tendency, is now among the
labials; "s / x by Mandarin sh / ch" and "tr / ch by Taigi t / ts" became Z3 and Z2)
<!-- rules:dropped -->
| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |
|---|---|---|---|---|---|---|---|---|
| I1x | kh ← Cantonese h- | dropped | 18 / 63, 29 % | 18 / 63, 29 % |  |  | **drop** | 學 học 曉 hiểu 行 hàng 河 hà 系 hệ 行 hành 係 hệ 向 hướng |
| I2x | ph ← Cantonese f- (replaced by ph ← Mandarin f-, which misses one) | dropped | 42 / 61, 69 % | 42 / 66, 64 % |  |  | **drop** | 花 hoa 化 hóa 科 khoa 幅 bức 婚 hôn 塊 khối 枯 khô 款 khoản |
| I3x | v ← Cantonese m- (replaced by v ← Cantonese m- with Mandarin w-) | dropped | 11 / 46, 24 % | 11 / 46, 24 % |  |  | **drop** | 每 mỗi 民 dân 明 minh 門 môn 目 mục 密 mật 媒 môi 命 mạng |
| I4x | gi ← Mandarin j- | dropped | 19 / 96, 20 % | 19 / 96, 20 % |  |  | **drop** | 決 quyết 郡 quận 句 câu 檢 kiểm 接 tiếp 級 cấp 究 cứu 經 kinh |
| I7x | d ← Mandarin y- | dropped | 27 / 83, 33 % | 27 / 84, 32 % |  |  | **drop** | 一 nhất 越 việt 影 ảnh 域 vực 員 viên 研 nghiên 藝 nghệ 意 ý |
<!-- /rules -->

**Teaching order**: IK velars (L16), IH h and IG ng (L17), IP labials (L18), IM m, v (L19), ID dentals (L20),
IA aspiration (L22), IS sibilants (L23), IR tr, ch (L24), IR th, s, x (L25), IY nh, d, none (L26), Z spelling
(L27), recap from the Vietnamese side (L29).
<!-- bridge-examples -->
- IK: 公司 công ty, 國家 quốc gia, 金 kim, 經濟 kinh tế · kh: 客 khách, 開 khai, 口 khẩu, 氣 khí, 起 khởi · gi: 家庭 gia đình, 教 giáo, 間 gian, 江山 giang sơn, 交通 giao thông
- IH: 學 học, 花 hoa, 海外 hải ngoại, 香 hương, 現在 hiện tại · IG: 言語 ngôn ngữ, 業 nghiệp, 外 ngoại, 研究 nghiên cứu, 月 nguyệt
- IP: 法 pháp, 方 phương, 發 phát, 飛機 phi cơ, 破 phá, 片 phiến · b: 北 bắc, 部 bộ, 病 bệnh, 平 bình, 盤 bàn
- IM: 馬 mã, 美 mỹ, 門 môn, 明白 minh bạch · v: 文化 văn hóa, 物 vật, 萬 vạn, 味 vị, 問題 vấn đề, 運 vận, 越 việt, 王 vương
- ID: 東 đông, 大學 đại học, 點 điểm, 電 điện · 頭 đầu, 題 đề, 同意 đồng ý · th: 通 thông, 體 thể, 天然 thiên nhiên, 太陽 thái dương · 南 nam, 女 nữ, 年 niên, 力 lực, 法律 pháp luật
- IR: 中國 Trung Quốc, 政治 chính trị, 傳 truyền, 知識 tri thức · ch: 正 chính, 主 chủ, 真 chân, 戰 chiến · th: 書 thư, 水 thủy, 世界 thế giới, 常 thường, 成 thành · s: 生 sinh, 事 sự, 史 sử, 產品 sản phẩm · x: 出 xuất, 春 xuân
- IS: 自 tự, 作品 tác phẩm, 現在 hiện tại, 心 tâm, 新 tân, 先 tiên, 錢 tiền, 節 tiết, 情 tình, 想 tưởng · th: 清 thanh, 參加 tham gia
- IY: 人民 nhân dân, 日 nhật, 熱 nhiệt, 自然 tự nhiên · d: 陽 dương, 洋 dương, 由 do, 使用 sử dụng · none: 意 ý, 音 âm, 安 an, 影 ảnh, 印象 ấn tượng, 醫 y
- IA: 平 bình, 頭 đầu, 情 tình, 全 toàn, 強 cường · 通 thông, 體 thể, 開 khai, 口 khẩu, 破 phá, 清 thanh, 出 xuất
- Z: gi 家庭 gia đình, 教 giáo / d 陽 dương, 由 do · ch 正 chính, 主 chủ / tr 中國 Trung Quốc · x 出 xuất, 春 xuân / s 生 sinh, 事 sự
<!-- /bridge-examples -->

## 6. Grammar, in teaching order

Lessons in brackets; L1–13 agree with word list 2 (each word's lesson is the list's).

**Stage A (1–21), the survival core**
1. **là** between nouns (L1); **không** + verb (L2); **không phải là** "is not" and **… phải không?** "…, right?"
   (L3); adjectives need no là (L9).
2. **The modifier follows the noun**: người Pháp, cà phê sữa đá, quán này (L2–3), the opposite of Chinese, and of
   the Hán-Việt words themselves (Việt Nam 越南): B0 shows both orders side by side.
3. **Questions**: có … không? (L3); gì (L1), nào, ở đâu, à (L2), ai, mấy (L5), bao nhiêu (L4), bao giờ, hay
   "or" (L11), sao / tại sao "why" with vì "because" (L12); **final particles**: the strand below.
4. **Numbers**: mười, mươi, lăm / mốt / tư after mươi, trăm, nghìn (L4; một, hai, ba at L3); **classifiers** quả
   (L10), cái (L13), quyển, tờ, chiếc, con (L17).
5. **của**, dropped with family and close ties (L5); person term + ấy = he / she (L5); đây là (L5).
6. **Time and aspect**: đang / sẽ (L6), usually left out when the context says it; **đã … chưa? / rồi / chưa**
   with hôm qua (L10); rồi "then" (L8); sắp (L31); vừa mới (L47); đã từng (L26).
7. **Degree**: rất (L1), quá (L4: Đắt quá!), lắm, hơi, thế "so" (L9); comparison hơn / bằng / nhất (L15);
   càng … càng (L40).
8. **Modals and imperatives**: muốn (L3), verb + đi and đừng + verb (L8), định (L11), nên / phải (L12), có thể,
   verb + được, biết + verb (L18), cần (L33).
9. **bị** for something bad (L12); **cho** "give, let, for" (L3, L19); tặng (L13); với "with", và "and" (L3, L11).
10. Plural and quantity: các / những, mọi / mỗi (L23); cũng / đều, vừa … vừa (L20).

**The Northern particle strand** (course/syllabus.yaml `particles`; each lesson's grammar names its particle, and
`make lint` checks that the word list teaches it by then). Hà Nội speech uses them all the time, so they come
early; the Southern counterparts get one line where they differ and L67.
<!-- plan:particles -->
| Particle | Lesson | Use |
|---|---|---|
| ạ | L1 | polite, to someone older: Chào chị ạ. |
| à | L2 | checking what one has just heard, or surprise: Anh là người Pháp à? |
| ơi | L3 | calling someone: Em ơi! |
| nhé | L3 | friendly "OK?" on a suggestion or promise: Hai cà phê sữa đá nhé! |
| phải không | L3 | "…, right?": Anh là người Pháp, phải không? |
| đấy | L6 | a friendly question: Anh đi đâu đấy? |
| đi | L8 | urging or suggesting, after the verb: Đi thẳng đi! |
| nào | L8 | urging, "let's": Đi nào! |
| nhỉ | L9 | seeking agreement: Nóng nhỉ! |
| thế | L9 | "so" (Nóng thế!), and in questions "then" (Sao thế? at L12); the South says vậy |
| đâu | L12 | emphatic "not at all": Không sao đâu! (first met at L2 in ở đâu "where") |
| thôi | L15 | "only, that's all": Hai mươi nghìn thôi. |
| hả | L16 | a blunt, familiar question, to equals or younger people: Con no rồi hả? |
| nhá | L16 | the familiar Northern nhé, to children and close friends: Ăn đi nhá! |
| với | L17 | softening a request for help, at the end: Giúp em với! |
| chứ | L18 | "of course", "surely": Được chứ! |
| dạ | L19 | the deferential "yes" and answer to a call, to elders: Dạ, cháu đây ạ. |
| mà | L27 | insisting, "I told you": Em biết mà! |
| cơ | L44 | insisting on the right one: Em muốn cái kia cơ! |
| nha | L67 | the Southern nhé |
| vậy | L67 | as a final particle, the Southern counterpart of thế (Sao vậy?); in vì vậy, như vậy it is general |
<!-- /plan -->

**Stage B (22–49)**: thì, khi / lúc (L22); direction verbs (L24) and result complements (L25); thường / hay / luôn
(L26); còn / vẫn / nữa / lại, mà insisting (L27); **passives được (good) and bị (bad)** with an agent (L29–30); nếu
… thì (L33); vì … nên (L34); relative **mà** (L36); purpose **để** (L37); tuy … nhưng (L38); reported speech rằng
(L39); không những … mà còn (L40); causatives làm cho / khiến (L43); insisting and contradicting cơ, đâu, hả
(L44); register: apologies, quý khách, xin vui lòng (L45–46); khi … thì, bỗng (L47); past narration hồi, ngày xưa
(L48).

**Stage C (50–100)**: written register (L50); nominalisers sự / việc / cuộc (L51); reduplication (L53); four-syllable
idioms (L55); softeners thôi / đi / mà in requests (L59); trước khi / sau khi (L61); không được / cấm (L62);
narrative connectors (L64, L72); dù … vẫn (L69); letter formulas (L76); nuances of phải / cần / nên (L79); argument
and reporting (L89–90); formal speech (L99).

**Pronouns and kinship** (its own strand; the cast's ages decide each choice):
- L1 **tôi, anh, chị, em**: Sacha starts with tôi; chị Lan calls him em and says chị, and he switches to em.
- L3 **em** to a young waiter; L5 **anh ấy, chị ấy**, family nouns (bố, mẹ, ông, bà, chồng, vợ, con), and **bác /
  cháu**: Sacha greets chị Lan's mother (Cháu chào bác ạ) and asks Bin and Na Cháu mấy tuổi?
- L11 **bạn**, the neutral "you" between peers (Mai) and in writing (signs, forms, messages).
- L12 bác / cháu again (bác looks after Sacha when he is ill); L16 **chúng tôi** (without you) and **chúng ta**
  (with you), the Taigi 阮 / 咱 split; anh trai, chị gái, em gái.
- L19 **ông / bà** as "you" (ông Hùng); **cô, chú**: Bin and Na call Sacha chú, he calls them cháu.
- L32 in-laws, nội / ngoại; L44 **mình** "I" among friends, **cậu / tớ**, and **mày / tao** only to recognise;
  L58 con cháu, họ hàng; L60 anh / em between lovers; L100 the whole cast, each with the right term.

## 7. Other strands

**Older Chinese loans** (decision 5: on the card as an older layer with the etymon, apart from Hán-Việt). O1 (L10):
giờ "hour" is an older reading of 時, whose Hán-Việt reading is thời; O2 (L33): biết (別 biệt), cũng (共 cộng),
được (得 đắc), đọc (讀 độc); also nôm (南, Hán-Việt nam: L71) and bằng "equal" (平, Hán-Việt bình: L15), which the
second proposal wrongly gave as Hán-Việt. Word list 2's older loans are counted in section 1.
The etymons are not "same word" examples; the Hán-Việt words beside them are:
<!-- bridge-examples -->
- O1–O2: 時間 thời gian, 特別 đặc biệt, 共 cộng
- C4–C6: 員 viên, 會員 hội viên, 士 sĩ, 化 hóa, 現代化 hiện đại hóa, 無數 vô số, 非 phi, 不同 bất đồng
<!-- /bridge-examples -->

**Word-building notes** (C1–C24, one per lesson from L34; table in section 8): Hán-Việt order inside a word, native
order outside; words made in Vietnam (hv-vn); surnames; suffixes -viên, -sĩ, -gia, -học, -hóa; prefixes bất-,
vô-, phi-; Vietnamese words that are not the Mandarin ones; native and Hán-Việt pairs (nhà / gia, nước / quốc);
idioms; then the vocabulary of institutions, medicine, science, law, Buddhism, history and literature.

**False friends** (the `false_friend` column of `course/lexicon.tsv`; one line in the lesson that meets the word):
thời tiết 時節 "weather", not a season (L9); tuần 旬 "week", not ten days (L11); bác sĩ 博士 "physician", not a PhD
(L12); sinh viên 生員 "university student", not an examination licentiate (L8); đầu tiên 頭先 "first", where
Cantonese and Taigi 頭先 is "just now" (L20); bản đồ 版圖 "map", not territory (L22); quận 郡
"urban district" (L23); chương trình 章程 "programme", not statutes (L37); thông cảm 通感 "to sympathise" (L44);
thực sự 實事 "really" (L45); trường 場 "school" (L52); triệu 兆 "million" (L59); lạm phát 濫發 "inflation" (L65);
nghĩa trang 義莊 "cemetery" (L96). Candidates from the first proposal (thư "letter", tử tế, phương tiện, an ninh,
tâm sự, khách sạn) get a lexicon row with evidence before use.

**Southern usage** (decision 6): one line where the word differs: bố / ba, cốc / ly, quả / trái, đắt / mắc, nghìn
/ ngàn, rẽ / quẹo, bát / tô, ốm "ill" / "thin", nhỉ / nhể, ha; vâng / dạ. L67 is set in Sài Gòn (sounds, words,
the readings nhựt 日, sanh 生, chánh 正).

**French** (decision 7): a line where it helps: loans (cà phê, phim, ga, ô tô, xà phòng: L3, L11, L94), and
sounds in Lesson 0 (nh = gn, ê = é, ô = eau).

## 8. Lesson by lesson

Bridge ids as in sections 3–7 (B finals, V rhymes, T tones, I initials, Z spelling, O older loans, C word-building,
FF false friend). Lines from the rule in section 1. New words: native / Hán-Việt / other (older and Western loans);
L1–13 are word list 2, later lessons are targets for each word list. Generated by `tools/plan.py --write` from
`course/syllabus.yaml` and the word list (one source; `make lint` fails when they disagree).

<!-- plan:lessons -->
| # | Situation | Grammar | Bridge / false friend | Lines | New: nat / HV / oth |
|---|---|---|---|---|---|
| 1 | Hello (Sacha meets chị Lan) | là; tôi / anh / chị / em; ạ, vâng; rất + adjective; cảm ơn – không có gì | — | 7 | 13 / 0 / 3 |
| 2 | Where are you from? | người + nationality (modifier after the noun); ở đâu; nào; không + verb; cũng; à (checking: Anh là người Pháp à?) | B0 what Hán-Việt is | 7 | 9 / 5 / 2 |
| 3 | At the café | có … không?; không phải là; … phải không?; muốn; cho tôi …; noun + này; ơi; nhé; và; một, hai, ba | — | 7 | 13 / 2 / 3 |
| 4 | Paying at the tea stall | numbers to the thousands: mười, mươi; lăm / mốt / tư after mươi; trăm, nghìn; bao nhiêu; cốc as a counter (hai cốc trà đá); Đắt quá! – Rẻ quá! | B1 -p -t -c survive | 7 | 15 / 2 / 1 |
| 5 | A family photo | của (dropped with family); ai; person term + ấy; mấy … tuổi; đây là | — | 8 | 12 / 4 / 1 |
| 6 | What time is it? | clock time: giờ, rưỡi, phút; đang / sẽ; time words first; đấy (Anh đi đâu đấy?) | B2 -m survives | 8 | 14 / 2 / 1 |
| 7 | **Review 1** | recap 1–6 | — | 8 | — |
| 8 | Around Hoàn Kiếm lake | directions; imperatives: verb + đi (Đi thẳng đi!), đừng + verb; nào (Đi nào!); rồi "then"; đó; khoảng | B3 -nh / -ch = -ng / -k | 8 | 8 / 6 / 2 |
| 9 | What is the weather like? | adjective as predicate (no là); rất / lắm / quá / hơi; thế "so" (Nóng thế!); nhỉ; nhưng | T1 level tones: ngang / huyền; FF thời tiết | 8 | 10 / 3 / 4 |
| 10 | A bowl of phở | đã … chưa? / rồi / chưa; hôm qua; thêm; classifier quả (một quả trứng) | O1 two layers: giờ and thời | 8 | 14 / 2 / 2 |
| 11 | Free at the weekend? | days, weeks and dates; bao giờ; hay "or"; với; định + verb; thích | T2 rising tones: hỏi / ngã / nặng; FF tuần | 9 | 11 / 5 / 2 |
| 12 | Sacha has a cold | bị (something bad); nên / phải; có khỏe không?; sao / tại sao …? – vì …; Sao thế?; đâu (Không sao đâu!) | T3 departing tones: sắc / nặng; FF bác sĩ | 9 | 9 / 4 / 5 |
| 13 | A birthday present | classifier cái; colours; to / nhỏ for size; vừa "to fit"; mua, lấy; tặng; ở chợ | T4 checked syllables: sắc / nặng only | 9 | 11 / 3 / 4 |
| 14 | **Review 2** | recap 8–13 | — | 9 | — |
| 15 | Which phone is cheaper? | comparison hơn / bằng / nhất; thôi "only, that's all" | T5 tones heard → Chinese tone | 9 | 11 / 5 / 2 |
| 16 | Dinner with the family | chúng tôi (exclusive) / chúng ta (inclusive); anh trai, chị gái; hả (Con no rồi hả?); nhá (Ăn đi nhá!) | IK c / k / q, kh, gi | 9 | 11 / 5 / 2 |
| 17 | At the bookshop | classifiers quyển, tờ, chiếc, con; với softening a request (Giúp em với!) | IH h and IG ng | 10 | 11 / 5 / 2 |
| 18 | At the swimming pool | có thể; verb + được; biết + verb; chứ (Được chứ!) | IP b, ph | 10 | 11 / 5 / 2 |
| 19 | Tea with ông Hùng | ông / bà as "you"; cho "for, to"; dạ (answering an elder: Dạ, cháu đây ạ.) | IM m, v | 10 | 11 / 5 / 2 |
| 20 | A day at the office | vừa … vừa; cũng / đều | ID đ, th, n, l; FF đầu tiên | 10 | 11 / 5 / 2 |
| 21 | **Review 3** | recap 15–20 | — | 10 | — |
| 22 | At Hà Nội station | thì; khi / lúc | IA aspiration and the old voiced tones; FF bản đồ | 10 | 11 / 5 / 2 |
| 23 | A room for Thảo | các / những; mọi / mỗi | IS t, th from the old ts- s- series; FF quận | 11 | 11 / 6 / 2 |
| 24 | Learning to ride a motorbike | direction verbs ra / vào / lên / xuống / về / sang | IR tr, ch | 11 | 11 / 6 / 2 |
| 25 | Lunch near the office | result complements xong, hết, thấy, được | IR th, s, x | 11 | 11 / 6 / 2 |
| 26 | Hobbies | đã từng; thường / hay / luôn | IY nh, d, no initial | 11 | 11 / 6 / 2 |
| 27 | Bà's stories | còn, vẫn, nữa, lại; mà (insisting: Em biết mà!) | Z spelling what Hà Nội merges: d / gi / r, tr / ch, s / x | 11 | 11 / 6 / 2 |
| 28 | **Review 4** | recap 22–27 | — | 11 | — |
| 29 | At the bank | được (good passive) | initials heard → Chinese (recap) | 12 | 11 / 6 / 2 |
| 30 | A stolen bike | bị and được with an agent | V1 -ương | 12 | 11 / 6 / 2 |
| 31 | Tết is coming | sắp; wishes with chúc | V2 -iên | 12 | 11 / 6 / 2 |
| 32 | Tết in anh Minh's village | kinship: nội / ngoại, in-laws | B4 Mandarin -ing → -nh (-ưng, -ăng) | 12 | 11 / 6 / 2 |
| 33 | The doctor again | nếu … thì; cần | O2 older loans: đọc, được, biết | 12 | 11 / 6 / 2 |
| 34 | A football match | vì … nên; tại vì | C1 Hán-Việt order inside a word, native order outside | 12 | 10 / 7 / 2 |
| 35 | **Review 5** | recap 29–34 | — | 13 | — |
| 36 | The Old Quarter | mà (relative) | C2 Hán-Việt words made in Vietnam | 13 | 10 / 7 / 2 |
| 37 | Water puppets | để (purpose) | FF chương trình | 13 | 11 / 7 / 2 |
| 38 | A wedding | tuy … nhưng; formal greetings | C3 surnames: Nguyễn, Trần, Lê, Phạm | 13 | 11 / 7 / 2 |
| 39 | Looking for a job | rằng (reported speech) | C4 suffixes -viên, -sĩ, -gia | 13 | 11 / 7 / 2 |
| 40 | A trip to Hạ Long | càng … càng; không những … mà còn | C5 suffixes -học, -hóa | 13 | 11 / 7 / 2 |
| 41 | Feelings | cảm thấy; emotion words | C6 prefixes bất-, vô-, phi- | 14 | 11 / 7 / 2 |
| 42 | **Review 6** | recap 36–41 | — | 14 | — |
| 43 | Ordering online | làm cho / khiến | C7 when the Vietnamese word is not the Mandarin one | 14 | 10 / 8 / 2 |
| 44 | An argument with Mai | cơ, đâu, hả (insisting, contradicting: Không phải đâu!) | FF thông cảm | 14 | 10 / 8 / 2 |
| 45 | Making up | apologies by register | FF thực sự | 14 | 10 / 8 / 2 |
| 46 | At the post office | formal register: quý khách, xin vui lòng | C8 Hán-Việt on signs | 14 | 10 / 8 / 2 |
| 47 | Floods in the rainy season | khi … thì; vừa mới; sudden events (bỗng, tự nhiên) | — | 15 | 10 / 8 / 2 |
| 48 | Hà Nội then and now | hồi, ngày xưa: past narration | — | 15 | 10 / 8 / 2 |
| 49 | **Review 7** | recap 43–48 | — | 15 | — |
| 50 | Sacha writes an email | written register (second wave starts) | C9 native and Hán-Việt pairs: nhà / gia, nước / quốc | 15 | 10 / 9 / 1 |
| 51 | Headlines | nominalisers sự / việc / cuộc | C10 reading dense Hán-Việt | 15 | 11 / 9 / 1 |
| 52 | At Thảo's university | giving reasons: bởi vì, do | FF học sinh / sinh viên, trường | 15 | 10 / 10 / 1 |
| 53 | Street food | reduplication (đo đỏ, nho nhỏ) | — | 15 | 10 / 10 / 1 |
| 54 | Mid-Autumn | trong khi; festival words | — | 15 | 10 / 10 / 1 |
| 55 | The Temple of Literature | four-syllable idioms | C11 thành ngữ from Chinese idioms | 16 | 10 / 10 / 1 |
| 56 | **Review 8** | recap 50–55 | — | 16 | — |
| 57 | The news on TV (neutral) | formal political words | C12 the vocabulary of institutions | 16 | 10 / 10 / 1 |
| 58 | Bác in hospital | chăm sóc; giving care | — | 16 | 10 / 10 / 1 |
| 59 | Bargaining at Đồng Xuân market | softeners in requests: thôi, đi, mà | FF triệu | 16 | 10 / 10 / 1 |
| 60 | Love songs | pronouns in songs | — | 16 | 10 / 10 / 1 |
| 61 | Cooking nem | trước khi / sau khi | — | 16 | 10 / 10 / 1 |
| 62 | Traffic rules | không được / cấm | — | 16 | 10 / 10 / 1 |
| 63 | **Review 9** | recap 57–62 | — | 16 | — |
| 64 | Childhood memories | narrative connectors (rồi, sau đó, cuối cùng) | — | 16 | 10 / 10 / 1 |
| 65 | Prices and the economy | triệu, tỷ; percentages | FF lạm phát | 16 | 10 / 11 / 1 |
| 66 | A trip to Huế | Central speech (one note) | C13 the court's Hán-Việt | 17 | 10 / 11 / 1 |
| 67 | A trip to Sài Gòn | Southern words and sounds; particles vậy, nha, ha | C14 Southern readings nhựt, sanh, chánh | 17 | 10 / 11 / 1 |
| 68 | Sport and health | nên / không nên; advice | — | 17 | 10 / 11 / 1 |
| 69 | Money worries | dù … vẫn | — | 17 | 10 / 11 / 1 |
| 70 | **Review 10** | recap 64–69 | — | 17 | — |
| 71 | The scripts of Vietnamese | chữ Hán, chữ Nôm, quốc ngữ | FF nôm; C15 chữ Nôm (one note) | 17 | 10 / 11 / 1 |
| 72 | A folk tale | ngày xửa ngày xưa; narrative | — | 17 | 10 / 11 / 1 |
| 73 | Moving house | nhờ, giúp: asking for help | — | 17 | 10 / 11 / 1 |
| 74 | Pets | con + noun; animal words | — | 17 | 10 / 11 / 1 |
| 75 | Thuốc Nam, thuốc Bắc | giá mà (wishes) | C16 medicine words | 18 | 10 / 11 / 1 |
| 76 | A formal letter | kính gửi; letter formulas | — | 18 | 10 / 11 / 1 |
| 77 | **Review 11** | recap 71–76 | — | 18 | — |
| 78 | A typhoon day off | bị / được with weather | — | 18 | 10 / 11 / 1 |
| 79 | Family conflict | phải / cần / nên: nuances | — | 18 | 10 / 12 / 1 |
| 80 | Science and technology | definitions: được gọi là | C17 science words | 18 | 10 / 12 / 1 |
| 81 | The environment | cause and effect: do … nên, dẫn đến | — | 18 | 10 / 12 / 1 |
| 82 | Law and rights | theo; conditions in writing | C18 law words | 18 | 10 / 12 / 1 |
| 83 | At the pagoda | respectful speech | C19 Buddhist words | 18 | 10 / 12 / 1 |
| 84 | **Review 12** | recap 78–83 | — | 18 | — |
| 85 | History: Bạch Đằng | dates and narration in writing | C20 history words | 18 | 10 / 12 / 1 |
| 86 | Literature: Truyện Kiều | verse word order | C21 literary Hán-Việt | 19 | 10 / 12 / 1 |
| 87 | Proverbs (tục ngữ) | parallel structures | C22 native and Hán-Việt proverbs | 19 | 10 / 12 / 1 |
| 88 | A job interview | formal self-presentation | — | 19 | 10 / 12 / 1 |
| 89 | A TV interview | reporting: theo …, cho biết | — | 19 | 10 / 12 / 1 |
| 90 | City or countryside? | arguing a point: một mặt … mặt khác | — | 19 | 10 / 12 / 1 |
| 91 | **Review 13** | recap 85–90 | — | 19 | — |
| 92 | Heritage and tourism | được coi là; descriptions | — | 19 | 10 / 12 / 1 |
| 93 | A hospital visit | symptoms and treatment | C23 medicine words 2 | 19 | 10 / 13 / 1 |
| 94 | Việt kiều in France | French loans (ga, ô tô, xà phòng) | C24 French loans beside Hán-Việt | 19 | 10 / 13 / 1 |
| 95 | Social media | colloquial written style | — | 20 | 10 / 13 / 1 |
| 96 | Weddings and funerals | ritual formulas | FF nghĩa trang | 20 | 10 / 13 / 1 |
| 97 | Sacha's year in Hà Nội | looking back: đã từng, chưa bao giờ | — | 20 | 10 / 13 / 1 |
| 98 | **Review 14** | recap 92–97 | — | 20 | — |
| 99 | A farewell speech | formal speech | — | 20 | 10 / 13 / 1 |
| 100 | Goodbye, Hà Nội | everything: a free conversation | — | 20 | 10 / 13 / 1 |
<!-- /plan -->

## 9. Limits, plainly

- **Written by Claude, not checked by a native speaker**: the Vietnamese (titles, examples), the Northern usage
  notes, the tone descriptions, the course English, the word boundaries and the course lexicon. The choices a
  lesson repeats most (tôi → em with chị Lan, bác for her mother, chú for the children, vâng or dạ, trà, to / nhỏ,
  rảnh) are in `wordlist-2-to-check.md` for a native speaker, most important first.
- **Frequency is biased**: a small, partly translated corpus (Tatoeba, Wiktionary examples); spoken particles,
  numbers and food words rank low (vâng 3,663, nhỉ 2,207, phở 12,139); some ranks are junk. Ranks guide; the
  situation decides, and every low-ranked word of the list says why it is there.
- **The sound rules are measured, not proven**: the Hán-Việt syllables of the top-3,000 cards (section 3), whose
  labels reviews found partly wrong; Taigi literary readings are the MOE's, and where the MOE marks no layer the
  app's classification (by the final consonant and the 麻 rhyme) may be wrong; the main rate depends on the stated
  choice of reading, the strict rate shows how much; some classes are small (Cantonese 5 with an obstruent). A rate
  is a guide for the learner, not a law.
- **Etymologies are Wiktionary's**: word list 2's older loans and words with no recorded origin are counted in
  section 1 ("no etymology recorded" says nothing about the origin). Tone descriptions in Lesson 0 come from
  published accounts, not from listening.

## 10. Questions for the owner

| # | Question | Recommendation |
|---|---|---|
| Q1 | Can a Hà Nội speaker read `wordlist-2-to-check.md` (its first four points) before lessons 1–7 are drafted? | **Yes, if at all possible**: those choices are repeated in every early dialogue; otherwise Claude drafts with its choices, labelled unchecked. |
| Q2 | Teach the tendencies (60–80 % on the main rate) and the rules that only narrow the letter to a set (best single guess under 60 %), or only the rules? | **Teach them, marked "tendency" or "narrows it to these letters"**, each with its exception list and its strict rate: they still beat guessing for a reader of Chinese. |
| Q3 | Initials take 12 bridge notes in L16–29: keep them together or spread to L50? | **Keep together**: the classes explain each other; reviews 21 and 28 recap them, and the second wave revisits them. |
