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

## 6. Grammar, in teaching order

Lessons in brackets; L1–13 agree with word list 2 (each word's lesson is the list's).

**Stage A (1–21), the survival core**
1. **là** between nouns (L1); **không** + verb (L2); **không phải là** (L3); adjectives need no là (L9).
2. **The modifier follows the noun**: người Pháp, cà phê sữa đá, quán này (L2–3), the opposite of Chinese, and of
   the Hán-Việt words themselves (Việt Nam 越南): B0 shows both orders side by side.
3. **Questions**: có … không? (L3); gì (L1), nào (L2), ở đâu (L2), ai, mấy (L5), bao nhiêu (L4), bao giờ, hay
   "or" (L11); **final particles** ạ (L1, politeness), nhé (L3, "OK?"), nhỉ (L9, "isn't it?"); ơi to call (L3).
4. **Numbers** and mươi, nghìn (L4); **classifiers** quả (L4), cái (L13), quyển, tờ, chiếc, con (L17).
5. **của**, dropped with family and close ties (L5); person term + ấy = he / she (L5); đây là (L5).
6. **Time and aspect**: đang / sẽ (L6), usually left out when the context says it; **đã … chưa? / rồi / chưa**
   (L10); rồi "then" (L8); sắp (L31); vừa mới (L47); đã từng (L26).
7. **Degree**: rất (L1), lắm, quá, hơi (L9); comparison hơn / bằng / nhất (L15); càng … càng (L40).
8. **Modals**: muốn (L3), định (L11), nên / phải (L12), có thể, verb + được, biết + verb (L18), cần (L33).
9. **bị** for something bad (L12); **cho** "give, let, for" (L3, L19); tặng (L13); với "with", và "and" (L3, L11).
10. Plural and quantity: các / những, mọi / mỗi (L23); cũng / đều, vừa … vừa (L20).

**Stage B (22–49)**: thì, khi / lúc (L22); direction verbs (L24) and result complements (L25); thường / hay / luôn
(L26); còn / vẫn / nữa / lại (L27); **passives được (good) and bị (bad)** with an agent (L29–30); nếu … thì (L33);
vì … nên (L34); relative **mà** (L36); purpose **để** (L37); tuy … nhưng (L38); reported speech rằng (L39);
không những … mà còn (L40); causatives làm cho / khiến (L43); particles chứ / mà / đâu / à (L44); register:
apologies, quý khách, xin vui lòng (L45–46); khi … thì, bỗng (L47); past narration hồi, ngày xưa (L48).

**Stage C (50–100)**: written register (L50); nominalisers sự / việc / cuộc (L51); reduplication (L53); four-syllable
idioms (L55); softeners thôi / đi / mà (L59); trước khi / sau khi (L61); không được / cấm (L62); narrative
connectors (L64, L72); dù … vẫn (L69); letter formulas (L76); nuances of phải / cần / nên (L79); argument and
reporting (L89–90); formal speech (L99).

**Pronouns and kinship** (its own strand; the cast's ages decide each choice):
- L1 **tôi, anh, chị, em**: Sacha starts with tôi; chị Lan calls him em and says chị, and he switches to em.
- L3 **em** to a young waiter; L5 **anh ấy, chị ấy**, family nouns (bố, mẹ, ông, bà, chồng, con, em gái).
- L11 **bạn**, the neutral "you" between peers (Mai) and in writing (signs, forms, messages).
- L12 **bác / cháu** with chị Lan's mother; L16 **chúng tôi** (without you) and **chúng ta** (with you), the
  Taigi 阮 / 咱 split; anh trai, chị gái.
- L19 **ông / bà** as "you" (ông Hùng); **cô, chú**: Bin and Na call Sacha chú, he calls them cháu.
- L32 in-laws, nội / ngoại; L44 **mình** "I" among friends, **cậu / tớ**, and **mày / tao** only to recognise;
  L58 con cháu, họ hàng; L60 anh / em between lovers; L100 the whole cast, each with the right term.

## 7. Other strands

**Older Chinese loans** (decision 5: on the card as an older layer with the etymon, apart from Hán-Việt). O1 (L10):
giờ "hour" is an older reading of 時, whose Hán-Việt reading is thời; O2 (L33): biết (別 biệt), cũng (共 cộng),
được (得 đắc), đọc (讀 độc). Word list 2 has 24 older loans (6 with a doubtful etymon, characters hidden).
The etymons are not "same word" examples; the Hán-Việt words beside them are:
<!-- bridge-examples -->
- O1–O2: 時間 thời gian, 特別 đặc biệt, 共 cộng
- C4–C6: 員 viên, 會員 hội viên, 士 sĩ, 化 hóa, 現代化 hiện đại hóa, 無 vô, 無數 vô số, 非 phi, 不同 bất đồng
<!-- /bridge-examples -->

**Word-building notes** (C1–C24, one per lesson from L34; table in section 8): Hán-Việt order inside a word, native
order outside; words made in Vietnam (hv-vn); surnames; suffixes -viên, -sĩ, -gia, -học, -hóa; prefixes bất-,
vô-, phi-; Vietnamese words that are not the Mandarin ones; native and Hán-Việt pairs (nhà / gia, nước / quốc);
idioms; then the vocabulary of institutions, medicine, science, law, Buddhism, history and literature.

**False friends** (the `false_friend` column of `course/lexicon.tsv`; one line in the lesson that meets the word):
thời tiết 時節 "weather", not a season (L9); tuần 旬 "week", not ten days (L11); bác sĩ 博士 "physician", not a PhD
(L12); đầu tiên 頭先 "first" (Cantonese only, "just now") (L20); bản đồ 版圖 "map", not territory (L22); quận 郡
"urban district" (L23); chương trình 章程 "programme", not statutes (L37); thông cảm 通感 "to sympathise" (L44);
thực sự 實事 "really" (L45); trường 場 "school" (L52); triệu 兆 "million" (L59); lạm phát 濫發 "inflation" (L65);
nôm 南 the Vietnamese script (L71); nghĩa trang 義莊 "cemetery" (L96). Candidates from the first proposal (thư
"letter", sinh viên, tử tế, phương tiện, an ninh, tâm sự, khách sạn) get a lexicon row with evidence before use.

**Southern usage** (decision 6): one line where the word differs: bố / ba, cốc / ly, quả / trái, đắt / mắc, nghìn
/ ngàn, rẽ / quẹo, bát / tô, ốm "ill" / "thin", nhỉ / nhể, ha; vâng / dạ. L67 is set in Sài Gòn (sounds, words,
the readings nhựt 日, sanh 生, chánh 正).

**French** (decision 7): a line where it helps: loans (cà phê, phim, ga, ô tô, xà phòng: L3, L11, L94), and
sounds in Lesson 0 (nh = gn, ê = é, ô = eau).

## 8. Lesson by lesson

Bridge ids as in sections 3–7 (B finals, V rhymes, T tones, I initials, Z spelling, O older loans, C word-building,
FF false friend). Lines from the rule in section 1. New words: native / Hán-Việt / other (older and Western loans);
L1–13 are word list 2, later lessons are targets for each word list. The same plan is in `course/syllabus.yaml`.

| # | Situation | Grammar | Bridge / false friend | Lines | New: nat / HV / oth |
|---|---|---|---|---|---|
| 1 | Hello (Sacha meets chị Lan) | là; tôi / anh / chị / em; ạ, vâng; rất + adjective | — | 7 | 12 / 0 / 3 |
| 2 | Where are you from? | người + nationality (modifier after the noun); ở đâu; nào; không + verb; cũng | B0 what Hán-Việt is | 7 | 8 / 5 / 2 |
| 3 | At the café | có … không?; không phải là; muốn; cho tôi …; noun + này; ơi; nhé; và | — | 7 | 10 / 2 / 3 |
| 4 | At the market | numbers, mươi, nghìn; first classifier quả; bao nhiêu | B1 -p -t -c survive | 7 | 13 / 2 / 1 |
| 5 | A family photo | của (dropped with family); ai; person term + ấy; mấy … tuổi; đây là | — | 8 | 11 / 4 / 1 |
| 6 | What time is it? | clock time, rưỡi; đang / sẽ; time words first | B2 -m survives | 8 | 13 / 2 / 1 |
| 7 | **Review 1** | recap 1–6 | — | 8 | — |
| 8 | Around Hoàn Kiếm lake | directions; imperatives; rồi "then"; đó; khoảng | B3 -nh / -ch = -ng / -k | 8 | 9 / 5 / 2 |
| 9 | What is the weather like? | adjective as predicate (no là); rất / lắm / quá / hơi; nhỉ; nhưng | T1 level tones: ngang / huyền; FF thời tiết | 8 | 9 / 4 / 3 |
| 10 | A bowl of phở | đã … chưa? / rồi / chưa; thêm; nhiều | O1 two layers: giờ and thời | 8 | 13 / 1 / 3 |
| 11 | Free at the weekend? | days and weeks; bao giờ; hay "or"; với; định + verb; thích | T2 rising tones: hỏi / ngã / nặng; FF tuần | 9 | 10 / 5 / 2 |
| 12 | Sacha has a cold | bị (something bad); nên / phải; có khỏe không? | T3 departing tones: sắc / nặng; FF bác sĩ | 9 | 9 / 4 / 4 |
| 13 | A birthday present | classifier cái; colours; vừa "to fit"; lấy; tặng | T4 checked syllables: sắc / nặng only | 9 | 13 / 3 / 2 |
| 14 | **Review 2** | recap 8–13 | — | 9 | — |
| 15 | Which phone is cheaper? | comparison hơn / bằng / nhất | T5 tones heard → Chinese tone | 9 | 11 / 5 / 2 |
| 16 | Dinner with the family | chúng tôi (exclusive) / chúng ta (inclusive); anh trai, chị gái | IK c / k / q, kh, gi | 9 | 11 / 5 / 2 |
| 17 | At the bookshop | classifiers quyển, tờ, chiếc, con | IH h and IG ng | 10 | 11 / 5 / 2 |
| 18 | At the swimming pool | có thể; verb + được; biết + verb | IP b, ph | 10 | 11 / 5 / 2 |
| 19 | Tea with ông Hùng | ông / bà as "you"; cho "for, to" | IM m, v | 10 | 11 / 5 / 2 |
| 20 | A day at the office | vừa … vừa; cũng / đều | ID đ, th, n, l; FF đầu tiên | 10 | 11 / 5 / 2 |
| 21 | **Review 3** | recap 15–20 | — | 10 | — |
| 22 | At Hà Nội station | thì; khi / lúc | IA aspiration and the old voiced tones; FF bản đồ | 10 | 11 / 5 / 2 |
| 23 | A room for Thảo | các / những; mọi / mỗi | IS t, th from the old ts- s- series; FF quận | 11 | 11 / 6 / 2 |
| 24 | Learning to ride a motorbike | direction verbs ra / vào / lên / xuống / về / sang | IR tr, ch | 11 | 11 / 6 / 2 |
| 25 | Lunch near the office | result complements xong, hết, thấy, được | IR th, s, x | 11 | 11 / 6 / 2 |
| 26 | Hobbies | đã từng; thường / hay / luôn | IY nh, d, no initial | 11 | 11 / 6 / 2 |
| 27 | Bà's stories | còn, vẫn, nữa, lại | Z spelling what Hà Nội merges: d / gi / r, tr / ch, s / x | 11 | 11 / 6 / 2 |
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
| 44 | An argument with Mai | chứ / mà / đâu (contradiction); à | FF thông cảm | 14 | 10 / 8 / 2 |
| 45 | Making up | apologies by register | FF thực sự | 14 | 10 / 8 / 2 |
| 46 | At the post office | formal register: quý khách, xin vui lòng | C8 Hán-Việt on signs | 14 | 10 / 8 / 2 |
| 47 | Floods in the rainy season | khi … thì; sudden events (bỗng, tự nhiên) | — | 15 | 10 / 8 / 2 |
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
| 59 | Bargaining at Đồng Xuân market | softeners thôi, đi, mà | FF triệu | 16 | 10 / 10 / 1 |
| 60 | Love songs | pronouns in songs | — | 16 | 10 / 10 / 1 |
| 61 | Cooking nem | trước khi / sau khi | — | 16 | 10 / 10 / 1 |
| 62 | Traffic rules | không được / cấm | — | 16 | 10 / 10 / 1 |
| 63 | **Review 9** | recap 57–62 | — | 16 | — |
| 64 | Childhood memories | narrative connectors (rồi, sau đó, cuối cùng) | — | 16 | 10 / 10 / 1 |
| 65 | Prices and the economy | triệu, tỷ; percentages | FF lạm phát | 16 | 10 / 11 / 1 |
| 66 | A trip to Huế | Central speech (one note) | C13 the court's Hán-Việt | 17 | 10 / 11 / 1 |
| 67 | A trip to Sài Gòn | Southern words and sounds | C14 Southern readings nhựt, sanh, chánh | 17 | 10 / 11 / 1 |
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

## 9. Limits, plainly

- **Written by Claude, not checked by a native speaker**: the Vietnamese (titles, examples), the Northern usage
  notes, the tone descriptions, the course English, the word boundaries and the course lexicon. The choices a
  lesson repeats most (tôi → em with chị Lan, bác for her mother, chú for the children, vâng or dạ, trà, nhỏ / lớn,
  rảnh) are in `wordlist-2-to-check.md` for a native speaker, most important first.
- **Frequency is biased**: a small, partly translated corpus (Tatoeba, Wiktionary examples); spoken particles,
  numbers and food words rank low (vâng 3,663, nhỉ 2,207, phở 12,139); some ranks are junk. Ranks guide; the
  situation decides, and every low-ranked word of the list says why it is there.
- **The sound rules are measured, not proven**: 994 syllables of the top-3,000 Hán-Việt cards, whose labels the
  review found partly wrong (opaque or Vietnam-made by mistake); Taigi literary readings are the MOE's, a few of
  them colloquial; a syllable whose readings disagree is left out; some classes are small (nh ← Taigi j-: 4;
  Cantonese 5 with an obstruent: 7). A rate is a guide for the learner, not a law.
- **Etymologies are Wiktionary's**: 24 older loans in word list 2 (6 doubtful, characters hidden), 36 words with
  no recorded origin. Tone descriptions in Lesson 0 come from published accounts, not from listening.

## 10. Questions for the owner

| # | Question | Recommendation |
|---|---|---|
| Q1 | Can a Hà Nội speaker read `wordlist-2-to-check.md` (its first four points) before lessons 1–7 are drafted? | **Yes, if at all possible**: those choices are repeated in every early dialogue; otherwise Claude drafts with its choices, labelled unchecked. |
| Q2 | Teach the tendencies (60–80 %: ch, th, x, s, d, ngã → Chinese) or only the rules? | **Teach them, marked "tendency"**, each with its exception list: they still beat guessing for a reader of Chinese. |
| Q3 | Initials take 12 bridge notes in L16–29: keep them together or spread to L50? | **Keep together**: the classes explain each other; reviews 21 and 28 recap them, and the second wave revisits them. |
