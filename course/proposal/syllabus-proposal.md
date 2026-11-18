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
