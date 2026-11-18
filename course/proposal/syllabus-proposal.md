# Tủ sách — syllabus proposal (second version)

**For the owner to approve.** Nothing is approved and no lesson is drafted. Written by Claude, 18 Nov 2026, branch
`data-quality`; **not checked by a native speaker**. Word list: `wordlist-2.tsv` (lessons 1–13), its doubts in
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
| Mai, a colleague | 27 | same age | bạn / tôi, later mình |
| ông Hùng, the old neighbour | 78 | grandparents' generation | ông / cháu |

**trà or chè.** The previous session's lexicon row (trà~tea, kept): trà is the usual word, Hà Nội included (trà đá,
trà chanh, trà sữa at every café and stall), and is 20 times more frequent in the corpus (60,092 against 2,989 per
billion words, chè counting the dessert). The card adds: in the North chè is also tea, at home and for the leaf
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

**New words per lesson** (names apart). Lessons 1–13 are word list 2's real counts; from 15, total(n) =
round(18 + 6(n−15)/85) and the Hán-Việt share grows from a quarter to over half. "Other" = older Chinese loans and
Western loans; lint counts them with the native words.

| Lessons | 1–6 | 8–13 | 15–20 | 22–34 | 36–48 | 50–62 | 64–76 | 78–90 | 92–100 |
|---|---|---|---|---|---|---|---|---|---|
| New words | 15–16 | 16–18 | 18 | 18–19 | 19–20 | 20–21 | 21–22 | 22–23 | 23–24 |
| of which Hán-Việt | 0–5 | 1–5 | 5 | 5–7 | 7–8 | 9–10 | 10–11 | 11–12 | 12–13 |

Word list 2 (L1–13): 194 words + 3 names; native 130 (incl. compounds and unknown origin), Hán-Việt 37 (19 %),
older loans 24, Western loans 3. The whole course: about 1,750 words (native 893, Hán-Việt 724 = 41 %, other 131).

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

Measured on the Hán-Việt syllables of the top 3,000 cards (`tools/bridge_rules.py`, "hits / total"). Native words and
older loans follow none of this. **Direction**: "zh→vi" guesses the Vietnamese tone from the Chinese he knows;
"vi→zh" goes from a tone he hears to the Chinese tone. "Sonorant" means the Vietnamese syllable starts with
m n nh ng l v d (old m n ŋ l ɲ and the glides): he predicts the initial first (section 5), then the tone.

**The old classes.** Hán-Việt splits each of the four old tones by the old initial, but **not the way Cantonese and
Taigi do** (the first proposal said "exactly the split Cantonese and Taigi made": false). Two differences matter:
- **Level tone, sonorant initial → ngang**, with the voiceless ones (nam 南, minh 明, dân 民), where Cantonese
  (4), Taigi (5) and Mandarin (2) put them with the voiced obstruents. The first proposal (and review 2) said
  huyền: wrong for these.
- **Rising tone**: Hán-Việt has three outcomes (hỏi voiceless, ngã sonorant, nặng voiced obstruent). Cantonese
  keeps 2 / 5 / 6; Taigi has one rising tone (2) for the first two and moved the third to 7; Mandarin has 3 / 3 / 4.
  So **động 動 and hậu 後 are regular** (old voiced obstruent, rising → nặng, Cantonese 6, Taigi 7), not
  exceptions as the first proposal said.

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

**From Cantonese (zh→vi)**, all six rules together: **801 / 850 = 94 %**.

| Cantonese tone | Hán-Việt | Hits | Main exceptions |
|---|---|---|---|
| 1 (open) | ngang | 163 / 168, 97 % | 監 giám, 擔 đảm, 胞 bào |
| 4, obstruent initial | huyền | 82 / 85, 96 % | 查 tra, 郵 bưu, 華 hoa |
| 4, sonorant initial | ngang | 72 / 72, 100 % | — |
| 2 | hỏi | 96 / 109, 88 % | 會 hội, 統 thống, 話 thoại, 院 viện, 館 quán |
| 5, sonorant initial | ngã | 26 / 32, 81 % | 理 lý, 李 lý, 里 lý, 與 dự, 議 nghị |
| 5, obstruent initial | nặng | 5 / 7, 71 % (tendency, few) | 社 xã, 有 hữu |
| 3 | sắc | 103 / 109, 94 % | 間 gian, 計 kê, 醬 tương |
| 6 | nặng | 110 / 120, 92 % | 問 vấn, 士 sĩ, 義 nghĩa, 技 kỹ, 靜 tĩnh (→ ngã) |
| checked 1 / 3 | sắc | 74 / 76, 97 % | 絡 lạc, 協 hiệp |
| checked 6 | nặng | 70 / 72, 97 % | 隰 thấp, 摘 trích |

**From Taigi (zh→vi)**, all together: **856 / 915 = 94 %**. Taigi 1 → ngang 95 %; 5 → huyền 97 % (obstruent) or
ngang 100 % (sonorant); 2 → hỏi 89 % (obstruent; 有 hữu, 少 thiếu, 館 quán) or ngã 86 % (sonorant; 理 lý, 研
nghiên); 3 → sắc 90 % (過 qua, 句 câu); 7 → nặng 90 % (問 vấn, 社 xã, 士 sĩ, 義 nghĩa); checked 4 → sắc 100 %,
8 → nặng 95 % (的 đích, 複 phức). Taigi needs the Vietnamese initial twice (5 and 2), Cantonese once (4, 5).

**From Mandarin (zh→vi)**: 1 → ngang 94 %; 2 with an obstruent → huyền 96 %; 3 with a sonorant → ngã 91 %. Tone 4
does not tell sắc from nặng, and entering syllables are scattered: here Cantonese or Taigi decides.

**From the Vietnamese tone heard (vi→zh)**: huyền → Cantonese 4 (99 %); ngang → Cantonese 1, or 4 after a sonorant
(98 %); hỏi → Cantonese 2 (97 %); sắc (open) → Cantonese 3 (89 %); nặng (open) → Cantonese 6 (89 %), Mandarin 4
(96 %); a syllable in -p -t -c -ch is sắc or nặng (166 / 166). **ngã → Cantonese 5 (72 %) or Mandarin 3 (78 %)
is a tendency**: about a quarter of ngã syllables are old voiced departing or rising ones (士 sĩ, 義 nghĩa, 技 kỹ).

**Teaching order**: T1 level tones (L9), T2 rising (L11), T3 departing (L12), T4 checked (L13), T5 heard → Chinese
(L15). Examples, each the same word in Chinese with all four readings in the database:
<!-- bridge-examples -->
- T1 ngang: 心 tâm, 東 đông, 公 công, 音 âm · ngang after a sonorant: 南 nam, 民 dân, 文明 văn minh, 門 môn, 陽 dương
  · huyền: 茶 trà, 湖 hồ, 頭 đầu, 平 bình, 情 tình
- T2 hỏi: 感 cảm, 點 điểm, 水 thủy, 主 chủ, 口 khẩu · ngã: 馬 mã, 女 nữ, 美 mỹ · nặng: 動 động, 後 hậu, 部 bộ, 道 đạo
- T3 sắc: 過 quá, 世 thế, 意 ý, 信 tín · nặng: 病 bệnh, 定 định, 電 điện, 大 đại
- T4 sắc: 法 pháp, 發 phát, 一 nhất, 北 bắc, 客 khách · nặng: 學 học, 實 thực, 力 lực, 立 lập, 物 vật
<!-- /bridge-examples -->

## 4. Finals and rhymes

All zh→vi unless marked; same data and tool. Mandarin lost -p -t -k and merged -m into -n; Cantonese and Taigi kept
them, and so did Hán-Việt.

| Id | Rule | Hits | Main exceptions | Lesson |
|---|---|---|---|---|
| B0 | What Hán-Việt is: one syllable per character, Chinese order inside the word | — | — | L2 |
| B1 | Cantonese -p → -p | 21 / 21, 100 % | — | L4 |
| B1 | Cantonese -t → -t | 34 / 37, 92 % | 法 pháp, 壓 áp (old -p: Hán-Việt kept it, Cantonese and Taigi did not); 實 thực | L4 |
| B1 | Cantonese -k → -c / -ch | 86 / 87, 99 % | 值 trị | L4 |
| B2 | Cantonese -m → -m | 41 / 41, 100 % | — | L6 |
| B2 | Taigi -m → -m | 40 / 42, 95 % | 填 điền, 忍 nhẫn | L6 |
| B3 | vi→zh: Hán-Việt -nh / -ch → Cantonese -ng / -k | 74 / 74, 100 % | — | L8 |
| B4 | Mandarin -ing → -nh | 46 / 54, 85 % | 憑 bằng, 平 bằng, 冰 băng, 興 hưng, 應 ứng, 凝 ngưng, 命 mạng | L32 |
| V1 | Cantonese -oeng / -oek → -ương / -ươc | 31 / 33, 94 % | 樣 dạng, 雙 song | L30 |
| V2 | Cantonese -in / -it → -iên / -iêt | 36 / 39, 92 % | 結 kết, 言 ngôn, 必 tất | L31 |

**Dropped**: "Cantonese -ing / -ik → -nh / -ch" (57 / 85, 67 %: 仍 nhưng, 力 lực, 食 thực, 直 trực, 織 chức):
the reverse (B3) is the useful direction; going forward the learner is told only that -nh / -ch need a Cantonese
-ng / -k.
<!-- bridge-examples -->
- B0: 越南 Việt Nam, 中國 Trung Quốc, 法 Pháp, 學 học, 河內 Hà Nội
- B1: 學習 học tập, 法律 pháp luật, 獨立 độc lập, 發展 phát triển, 國家 quốc gia
- B2: 南 nam, 心 tâm, 感 cảm, 點 điểm, 音 âm, 參加 tham gia
- B3: 生 sinh, 病 bệnh, 明白 minh bạch, 歷史 lịch sử, 客 khách
- B4: 情 tình, 定 định, 平 bình, 影 ảnh, 經濟 kinh tế
- V1: 想 tưởng, 洋 dương, 商 thương, 香 hương, 影響 ảnh hưởng, 戰略 chiến lược
- V2: 電 điện, 先 tiên, 前 tiền, 年 niên, 研究 nghiên cứu, 節 tiết, 熱 nhiệt
<!-- /bridge-examples -->

## 5. Initials, by old class

Grouped by the Middle Chinese initial behind each Hán-Việt letter; each rule keyed to whichever of Cantonese, Taigi
or Mandarin predicts best, measured in its direction (**zh→vi**: from the Chinese he knows to a guess of the
Vietnamese; **vi→zh**: from a Vietnamese word heard or read to the Chinese; **spell**: which letter to write for a
sound Hà Nội merges). Hit rate = matching / all Hán-Việt syllables of the top 3,000 the rule covers (readings that
disagree are left out). **Rule** at 80 % or more, **tendency** 60–80 %, dropped below.

**Labials** (old p ph b; f-series; m)

| Rule | Dir | Hits | Main exceptions |
|---|---|---|---|
| ph ← Mandarin f- | zh→vi | 40 / 41, 98 % | 幅 bức |
| b ← Mandarin b- | zh→vi | 37 / 41, 90 % | 標 tiêu, 比 tỷ, 必 tất, 弊 tệ (→ t) |
| b ← Taigi p- | zh→vi | 42 / 47, 89 % | the same four, 房 phòng |
| ph → Mandarin f- or p- | vi→zh | 50 / 50, 100 % | — |
| b → Mandarin b- or p- | vi→zh | 44 / 47, 94 % | 幅 bức, 祕 bí |
| m ← Mandarin m- | zh→vi | 30 / 35, 86 % | 民 dân, 面 diện, 名 danh, 滅 diệt (→ d) |
| m → Mandarin m- | vi→zh | 30 / 30, 100 % | — |
| v ← Cantonese m- with Mandarin w- | zh→vi | 11 / 11, 100 % | — |
| v → Mandarin w- or y- | vi→zh | 26 / 27, 96 % | 榮 vinh |

Mandarin p- splits by tone (see "Aspiration"): tone 2 → b (平 bình), other tones → ph (破 phá).

**Dentals** (old t th d; n l)

| Rule | Dir | Hits | Main exceptions |
|---|---|---|---|
| đ ← Mandarin d- | zh→vi | 41 / 41, 100 % | — |
| đ ← Mandarin t- in tone 2 | zh→vi | 17 / 17, 100 % | — |
| th ← Mandarin t- in tones 1 3 4 | zh→vi | 16 / 19, 84 % | 特 đặc, 突 đột, 推 suy |
| đ ← Taigi t- with Mandarin d- / t- | zh→vi | 53 / 53, 100 % | — (Taigi t- with zh- / ch- is tr, below) |
| đ → Mandarin d- or t- | vi→zh | 61 / 61, 100 % | — |
| n ← Mandarin n- · l ← Mandarin l- | zh→vi | 14 / 15 · 50 / 50 | 凝 ngưng |
| n → Mandarin n- · l → Mandarin l- | vi→zh | 14 / 14 · 50 / 50 | — |
| Taigi l- → l or n (Mandarin decides) | zh→vi | 58 / 59, 98 % | 冗 nhũng |

**Retroflex series** (old ʈ- and tʂ- / tɕ- series: Mandarin zh ch sh)

| Rule | Dir | Hits | Main exceptions |
|---|---|---|---|
| tr ← Mandarin zh- / ch- with Taigi t- / th- | zh→vi | 31 / 31, 100 % | — |
| ch or tr ← Mandarin zh- | zh→vi | 66 / 70, 94 % | 棧 sạn, 者 giả, 殖 thực, 撰 soạn |
| ch ← Mandarin zh- with Taigi ts- | zh→vi | 34 / 47, 72 %: **tendency** | 爭 tranh, 助 trợ, 狀 trạng, 陣 trận, 站 trạm |
| ch → Mandarin zh- | vi→zh | 34 / 34, 100 % | — |
| tr → Mandarin zh- or ch- | vi→zh | 44 / 45, 98 % | 責 trách |
| th or s ← Mandarin sh- | zh→vi | 66 / 68, 97 % | 社 xã, 賒 xa |
| th ← Mandarin sh- | zh→vi | 52 / 68, 76 %: **tendency** | s in 事 sự, 數 số, 使 sử, 生 sinh, 史 sử, 士 sĩ |
| x or s ← Mandarin ch- in tones 1 3 4 | zh→vi | 13 / 13, 100 % | — |
| tr or th ← Mandarin ch- in tone 2 | zh→vi | 18 / 19, 95 % | 察 sát |
| x → Mandarin ch- | vi→zh | 10 / 14, 71 %: **tendency** | 社 xã, 確 xác, 侵 xâm |
| s → Mandarin sh- or ch- | vi→zh | 21 / 29, 72 %: **tendency** | 冊 sách, 所 sở, 色 sắc, 策 sách |

The exceptions to "ch" and "th" are one old group (the 莊 series: 爭 助 狀 莊 → tr; 事 生 史 使 士 → s). None of
his three varieties marks it, so it is taught as a list, not a rule.

**Dental sibilants** (old ts tsh dz s z: Mandarin z c s, or j q x before i / ü)

| Rule | Dir | Hits | Main exceptions |
|---|---|---|---|
| t ← Mandarin z- | zh→vi | 28 / 29, 97 % | 責 trách |
| Mandarin j q x with Cantonese z c s → t or th | zh→vi | 64 / 66, 97 % | 需 nhu, 侵 xâm |
| … with Taigi ts- / s- → t | zh→vi | 93 / 98, 95 % | 所 sở, 色 sắc, 責 trách |
| … with Taigi tsh- → th | zh→vi | 13 / 16, 81 % | 策 sách, 侵 xâm, 縱 tung |
| t → Mandarin z c s j q x | vi→zh | 107 / 112, 96 % | 標 tiêu, 比 tỷ, 必 tất, 弊 tệ, 慧 tuệ |
| t → Cantonese z c s | vi→zh | 104 / 109, 95 % | the same |

**Velars and h** (old k kh g; ŋ; x ɣ)

| Rule | Dir | Hits | Main exceptions |
|---|---|---|---|
| c / k / q ← Mandarin g- | zh→vi | 45 / 46, 98 % | 概 khái |
| c / k / q or gi ← Taigi k- | zh→vi | 119 / 124, 96 % | 縣 huyện, 枯 khô, 緊 khẩn |
| Mandarin j q x with Cantonese g k h → c, kh, h, gi (never t) | zh→vi | 112 / 113, 99 % | 確 xác |
| gi ← Mandarin j- with Cantonese g- + aa / o | zh→vi | 18 / 18, 100 % | — |
| kh ← Cantonese h- / f- with Mandarin k- / q- | zh→vi | 23 / 24, 96 % | 況 huống |
| kh ← Taigi kh- | zh→vi | 25 / 34, 74 %: **tendency** | 權 quyền, 確 xác, 擒 cầm, 吸 hấp |
| c / k / q → Mandarin g j k q | vi→zh | 109 / 109, 100 % | — |
| kh → Mandarin k- or q- · → Taigi kh- | vi→zh | 27 / 29, 93 % · 25 / 29, 86 % | 緊 khẩn, 概 khái |
| gi → Mandarin j- with Cantonese g- | vi→zh | 18 / 19, 95 % | 者 giả |
| ng / ngh ← Taigi g- | zh→vi | 23 / 24, 96 % | 牙 nha |
| ng / ngh → Taigi g- | vi→zh | 23 / 25, 92 % | 伍 ngũ, 偶 ngẫu |
| h ← Mandarin h- / x- with Cantonese h f w j | zh→vi | 76 / 78, 97 % | 話 thoại, 慧 tuệ |
| Taigi h- → h, but ph when Mandarin has f- | zh→vi | 113 / 115, 98 % | 幅 bức, 慧 tuệ |
| h → Mandarin h- or x- · → Taigi h- | vi→zh | 80 / 84, 95 % · 76 / 85, 89 % | 完 hoàn, 有 hữu |

So Mandarin j q x, which Mandarin merged, split again by Cantonese: g k h → c kh h gi; z c s → t th.

**No initial, v, d, nh** (old ʔ, the glides, ɲ)

| Rule | Dir | Hits | Main exceptions |
|---|---|---|---|
| nh ← Mandarin r- | zh→vi | 13 / 16, 81 % | 阮 nguyễn, 容 dung, 榮 vinh |
| nh → Mandarin r-, y- or none | vi→zh | 19 / 20, 95 % (r- alone 65 %, tendency) | 需 nhu |
| nh ← Taigi j- | zh→vi | 4 / 4 (few: most Taigi readings here have l- or none) | — |
| d ← Mandarin y- with Cantonese j- in tone 4 5 6, Taigi no initial | zh→vi | 21 / 28, 75 %: **tendency** | 越 việt, 員 viên, 宇 vũ (→ v); 有 hữu |
| d → Mandarin y- · → Cantonese j- | vi→zh | 27 / 34 · 26 / 33, 79 %: **tendency** | 民 dân, 面 diện, 名 danh (m-); 唯 duy (w-) |
| no initial ← Mandarin y- / w- / none with Cantonese in tone 1 2 3 | zh→vi | 24 / 28, 86 % | 一 nhất, 因 nhân, 院 viện |
| no initial → Mandarin y-, w- or none | vi→zh | 31 / 31, 100 % | — |
| no Hán-Việt syllable starts with r | vi→zh | 994 / 994 | — |

**Aspiration across the classes** (the old voiced stops lost their voice: Cantonese and Mandarin aspirate some)

| Rule | Dir | Hits | Main exceptions |
|---|---|---|---|
| Cantonese p t k kw c in tone 4 / 5 → b đ c t tr ch gi | zh→vi | 55 / 55, 100 % | — |
| Mandarin p t k q c ch in tone 2 → b đ c t tr ch gi | zh→vi | 56 / 64, 88 % | 常 thường, 城 thành, 成 thành, 船 thuyền (old fricatives) |
| Mandarin p t k q c ch in tones 1 3 4 → ph th kh x s | zh→vi | 79 / 84, 94 % | 特 đặc, 突 đột, 期 kỳ |

**Spelling what Hà Nội merges** (the Chinese decides the letter; native words are learnt by heart)

| Rule | Hits | Main exceptions |
|---|---|---|
| Z1 [z]: gi when Cantonese has g- (= Mandarin j-), else d; never r | 52 / 53, 98 % | 者 giả |
| Z2 [c]: ch when Taigi has ts-, else tr | 73 / 84, 87 % | 陣 trận, 爭 tranh, 責 trách, 助 trợ, 莊 trang |
| Z3 [s]: x when Mandarin has ch-, else s | 32 / 43, 74 %: **tendency** | 社 xã, 察 sát, 產 sản, 確 xác |

**Dropped from the first proposal** (measured, zh→vi): kh ← Cantonese h- 18 / 58, 31 % (學 học, 河 hà: most are
h); ph ← Cantonese f- 37 / 56, 66 % (花 hoa, 化 hóa, 科 khoa), replaced by Mandarin f-; v ← Cantonese m- 11 / 45,
24 %; v ← Mandarin w- alone 15 / 24, 62 %; gi ← Mandarin j- 18 / 91, 20 %; d ← Mandarin y- 27 / 83, 33 %; s / x by
Mandarin sh / ch 24 / 33, 73 % (now Z3, a tendency); tr / ch by Taigi t / ts 65 / 76, 86 % (kept as Z2 in a form
that covers more words).

**Teaching order**: IK velars (L16), IH h and IG ng (L17), IP labials (L18), IM m, v (L19), ID dentals (L20),
IA aspiration (L22), IS sibilants (L23), IR tr, ch (L24), IR th, s, x (L25), IY nh, d, none (L26), Z spelling
(L27), recap from the Vietnamese side (L29).
<!-- bridge-examples -->
- IK: 公 công, 國家 quốc gia, 金 kim, 經濟 kinh tế · kh: 客 khách, 開 khai, 口 khẩu, 氣 khí, 起 khởi · gi: 家庭 gia đình, 教 giáo, 間 gian, 江山 giang sơn, 交通 giao thông
- IH: 學 học, 花 hoa, 海外 hải ngoại, 香 hương, 現在 hiện tại · IG: 言語 ngôn ngữ, 業 nghiệp, 外 ngoại, 研究 nghiên cứu, 月 nguyệt
- IP: 法 pháp, 方 phương, 發 phát, 飛機 phi cơ, 破 phá, 片 phiến · b: 北 bắc, 部 bộ, 病 bệnh, 平 bình, 盤 bàn
- IM: 馬 mã, 美 mỹ, 門 môn, 明白 minh bạch · v: 文化 văn hóa, 物 vật, 萬 vạn, 味 vị, 問題 vấn đề, 運 vận, 越 việt, 王 vương
- ID: 東 đông, 大學 đại học, 點 điểm, 電 điện · 頭 đầu, 題 đề, 同意 đồng ý · th: 通 thông, 體 thể, 天然 thiên nhiên, 太陽 thái dương · 南 nam, 女 nữ, 年 niên, 力 lực, 法律 pháp luật
- IR: 中國 Trung Quốc, 茶 trà, 長 trường, 政治 chính trị, 傳 truyền, 知識 tri thức · ch: 正 chính, 主 chủ, 真 chân, 戰 chiến · th: 書 thư, 水 thủy, 世 thế, 商 thương, 常 thường, 城 thành · s: 生 sinh, 事 sự, 史 sử, 產品 sản phẩm · x: 出 xuất, 春 xuân, 車 xa
- IS: 自 tự, 作品 tác phẩm, 現在 hiện tại, 心 tâm, 新 tân, 先 tiên, 前 tiền, 錢 tiền, 節 tiết, 情 tình, 想 tưởng · th: 清 thanh, 參加 tham gia
- IY: 人民 nhân dân, 日 nhật, 熱 nhiệt, 自然 tự nhiên · d: 陽 dương, 洋 dương, 由 do, 使用 sử dụng · none: 意 ý, 音 âm, 安 an, 影 ảnh, 印象 ấn tượng, 醫 y
- IA: 平 bình, 頭 đầu, 情 tình, 前 tiền, 全 toàn, 茶 trà, 強 cường · 通 thông, 體 thể, 開 khai, 口 khẩu, 破 phá, 清 thanh, 出 xuất
- Z: gi 家庭 gia đình, 教 giáo / d 陽 dương, 由 do · ch 正 chính, 主 chủ / tr 中國 Trung Quốc, 茶 trà · x 出 xuất, 春 xuân / s 生 sinh, 事 sự
<!-- /bridge-examples -->
