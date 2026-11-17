# Tủ sách — syllabus proposal

**A proposal for the owner to approve or change.** Nothing is approved; no lesson is drafted. Written by Claude on
18 Nov 2026 from repository commit dcaf84f and `data/build/vi.db`. **Not checked by a native speaker.** The first
word list is `wordlist-1.tsv` (lessons 1–14), with its doubts in `wordlist-1-to-check.md`.

## 1. Shape of the course

- **100 lessons**, as in Tsheh-tû. Every 7th is a review (7, 14 … 98): 14 reviews, 86 new lessons.
- **Second wave from lesson 50**: with lesson N, redo lesson N−49 from English into Vietnamese (as in Tsheh-tû).
- **Story**: Sam, who speaks French and Chinese, spends a year in Hà Nội at chị Lan's guesthouse, with her husband
  anh Minh, her mother and her children. The family gives the pronoun strand real people of every age.
- **A lesson** = title, one line of setting, a dialogue, notes (grammar, pronouns, one bridge note at most, Southern
  or false-friend remarks), new words (English on every card), two exercises (translate, fill the gap), always new
  sentences. Review lessons: a short new dialogue using only the week's words, a recap note, no new words.

**Lines per dialogue** (smooth: one more line about every six lessons, reviews 8):

| Lesson | 1 | 8 | 15 | 22 | 29 | 36 | 43 | 50 | 64 | 78 | 92 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Lines | 7 | 8 | 9 | 10 | 12 | 13 | 14 | 15 | 16 | 18 | 19 | 20 |

Rule: lines(n) = round(7 + 8·(n−1)/49) up to lesson 50, then round(15 + 5·(n−50)/50).

**New words per lesson** (native / Hán-Việt; lessons 1–13 are the real counts of word list 1):

| Lessons | 1–13 | 15–20 | 22–27 | 29–34 | 36–41 | 43–48 | 50–62 | 64–76 | 78–100 |
|---|---|---|---|---|---|---|---|---|---|
| New words | 15–19 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 |
| Hán-Việt | 1–6 | 5 | 6 | 7 | 8 | 9 | 11 | 12 | 13 |

About **1,785 words** in all, **44 % Hán-Việt** (23 % in lessons 1–14, rising to over half from lesson 50). The
frequency list says 38 % of the 500 most frequent words are Hán-Việt and about 50 % beyond: everyday speech first,
his advantage grows with the topics.

## 2. Strands

### 2.1 Pronunciation and the six Northern tones
A reading page before lesson 1 ("Lesson 0", as Tsheh-tû has for Tâi-lô): letters, vowels, the six tones, and the
Hà Nội mergers. Then one sound note per lesson in lessons 1–13.

| Tone | Mark | Hà Nội (Claude's description) |
|---|---|---|
| ngang | a | mid level |
| huyền | à | low falling, breathy |
| sắc | á | high rising |
| hỏi | ả | low falling (dipping); kept apart from ngã in the North |
| ngã | ã | rising, broken by a glottal catch |
| nặng | ạ | low, short, glottal stop |

Hà Nội merges in sound what spelling keeps apart: **d, gi, r → z**; **s, x → s**; **tr, ch → ch**. The bridge
tells the spelling (2.3, I5–I7). Southern speech merges hỏi and ngã: mentioned once, not taught.

**What his Chinese predicts (Hán-Việt words only).** The six tones are the four old tone classes split by the old
initial, exactly the split Cantonese and Taigi made. Native words follow no such rule.

| Old class | Hán-Việt | Cantonese | Taigi lit. | Mandarin | Example (yue / nan / cmn) |
|---|---|---|---|---|---|
| 平, upper | ngang | 1 | 1 | 1 | tâm 心 sam1 / sim / xīn |
| 平, lower | huyền | 4 | 5 | 2 | nam 南 naam4 / lâm / nán |
| 上, upper | hỏi | 2 | 2 | 3 | cảm 感 gam2 / kám / gǎn |
| 上, lower (m n ng l v…) | ngã | 5 | 2 | 3 | mã 馬 maa5 / má / mǎ |
| 去, upper | sắc | 3 | 3 | 4 | quá 過 gwo3 / kò / guò |
| 去, lower (+ 上 with old voiced stop) | nặng | 6 | 7 | 4 | bệnh 病 beng6 / pīng / bìng |
| 入, upper | sắc | 1 / 3 | 4 | any | quốc 國 gwok3 / kok / guó |
| 入, lower | nặng | 6 | 8 | any | học 學 hok6 / ha̍k / xué |

Rule for the learner: **a syllable ending in -p -t -c -ch has only sắc or nặng**. Cantonese tone 6 or Taigi tone
7/8 → nặng is the most useful single rule. Exceptions exist (hỏi/ngã are the least regular); the notes say so.

### 2.2 Grammar, in teaching order
Stage A (1–21), the survival core:
1. là between nouns; không phải là (L1–2).
2. **Modifier after the noun**: người Pháp, cà phê sữa đá, tiếng Việt (L2–3; the opposite of Chinese, and of
   Hán-Việt compounds such as Việt Nam 越南: shown side by side in B0).
3. Yes/no: có … không? (L3); question words gì, ai, đâu, nào, bao giờ (L11).
4. Numbers, mươi; **classifiers** quả (L4), con (L5), cái (L15), quyển, tờ, chiếc (L17).
5. của, often dropped with family (L5).
6. **Time and aspect**: đã / đang / sẽ (L6), often left out when context says it; đã … chưa? rồi, chưa (L10);
   sắp, vừa mới (L13, L31); đã từng (L26).
7. Adjectives as predicates, no là; rất / lắm / quá / hơi (L9).
8. **Negation**: không (L1), chưa (L10), đừng (L18), không được (L62), chẳng (stage B).
9. Modal verbs: nên, phải (L12), có thể, được (L18), cần (L33).
10. **Comparison**: hơn, bằng, nhất (L15); càng … càng (L40).
11. Plurals and quantifiers: các / những, mọi / mỗi (L23).
Stage B (22–49): direction and result complements (L24–25); còn / vẫn / nữa / lại (L27); **passives được
(good) and bị (bad)** (L12 bị with illness, L29–30 with an agent); conditionals nếu … thì (L33); cause vì … nên
(L34); relative mà (L36); purpose để (L37); concession tuy … nhưng (L38); reported speech rằng (L39); causatives
(L43); **final particles** ạ, nhé, nhỉ (L13), à, chứ, mà, đâu (L44), thôi, đi (L59).
Stage C (50–100): written register, nominalisers sự / việc / cuộc (L51), reduplication (L53), four-syllable
idioms (L55), narrative connectors (L64, L72), formal letters and speech (L76, L99).

**Pronouns and kinship** (its own strand): L1 tôi, anh, chị, em; L5 family nouns (bố, mẹ, ông, bà, anh trai…);
L11 bạn between peers; L13 the generation above: cháu ↔ bác, cô, chú; L16 chúng tôi (exclusive) vs chúng ta
(inclusive), like Taigi 阮 / 咱; L19 ông, bà as "you"; L32 in-laws, nội / ngoại; L58 con cháu, họ hàng; L60
anh / em between lovers; mày / tao only to recognise (stage B note).

### 2.3 Bridge notes, one correspondence at a time
Every example is a database row: Hán-Việt word, chữ Hán, Cantonese / Taigi literary / Mandarin.

**Finals first (L2–L8)**
- **B0, L2 — What Hán-Việt is**: Việt Nam 越南 jyut6 naam4 / ua̍t-lâm / Yuènán; Trung Quốc 中國 zung1 gwok3 /
  Tiong-kok / Zhōngguó; Pháp 法 faat3 / huat / fǎ; học 學 hok6 / ha̍k / xué; Hà Nội 河內 ho4 noi6 / hô-luē / Hénèi.
- **B1, L4 — -p -t -c survive** (Mandarin lost them): học tập 學習 hok6 zaap6 / ha̍k-si̍p / xuéxí; pháp luật 法律
  faat3 leot6 / huat-lu̍t / fǎlǜ; độc lập 獨立 duk6 laap6 / to̍k-li̍p / dúlì; phát triển 發展 faat3 zin2 /
  huat-tián / fāzhǎn; quốc gia 國家 gwok3 gaa1 / kok-ka / guójiā.
- **B2, L6 — -m survives** (Mandarin -n): nam 南 naam4 / lâm / nán; tâm 心 sam1 / sim / xīn; cảm 感 gam2 / kám /
  gǎn; điểm 點 dim2 / tiám / diǎn; tham gia 參加 caam1 gaa1 / tsham-ka / cānjiā.
- **B3, L8 — -nh / -ch = -ng / -k after a front vowel**: sinh 生 saang1 / sing / shēng; minh 明 ming4 / bîng /
  míng; bệnh 病 beng6 / pīng / bìng; lịch sử 歷史 lik6 si2 / li̍k-sú / lìshǐ; khách 客 haak3 / khik / kè.

**Tone classes (L10–L15)**: T1 ngang / huyền, T2 hỏi / ngã, T3 sắc / nặng, T4 checked syllables, recap (the
table in 2.1, with 4–6 words each: T1 tâm, đông 冬, kim 金 / nam, minh, hồ 湖, trà 茶; T2 cảm, điểm, thủy 水, chủ 主 /
mã 馬, nữ 女, vũ 雨, lão 老; T3 quá, thế 世, kiếm 劍, ý 意 / bệnh, định 定, điện 電, đại 大; T4 quốc, phát, nhất 一,
bắc 北 / học, thật 實, lực 力, lập 立).

**Initials (L16–L29)**, chosen so his Cantonese or Taigi decides the letter:
- **I1 kh** = Cantonese h-, Taigi kh-: khách 客 haak3 / khik; khí 氣 hei3 / khì; khai 開 hoi1 / khai; khẩu 口
  hau2 / khió; khoa học 科學 fo1 hok6 / kho-ha̍k.
- **I2 ph** = Cantonese f-, Taigi h-: phát 發 faat3 / huat; pháp 法 faat3 / huat; phương 方 fong1 / hong; phi 飛
  fei1 / hui; phụ nữ 婦女 fu5 neoi5 / hū-lú.
- **I3 v** = Cantonese m-, Taigi b-, Mandarin w-: văn hóa 文化 man4 faa3 / bûn-huà / wénhuà; vật 物 mat6 / bu̍t /
  wù; vô 無 mou4 / bû / wú; vạn 萬 maan6 / bān / wàn; vị 味 mei6 / bī / wèi.
- **I4 gi** = old k- before -a- (Mandarin j-): gia đình 家庭 gaa1 ting4 / ka-tîng / jiātíng; giáo 教 gaau3 / kàu /
  jiào; giang 江 gong1 / kang / jiāng; gian 間 gaan1 / kan / jiān; giảm 減 gaam2 / kiám / jiǎn.
- **I5 tr vs ch** (one sound in Hà Nội): Taigi t- → tr: trung 中 tiong, trà 茶 tê, trí 智 tì, Trần 陳 tîn;
  Taigi ts- → ch: chính 正 tsìng, chủ 主 tsú, chân 真 tsin, chiến 戰 tsiàn.
- **I6 s vs x** (one sound in Hà Nội): Mandarin sh- → s: sinh 生 shēng, sơn 山 shān, sự 事 shì, sở 所 suǒ (Taigi
  s-); Mandarin ch- → x: xuất 出 chū, xuân 春 chūn, xa 車 chē (Taigi tsh- for 出, 春).
- **I7 d** = Mandarin y- (and a few old m-): dụng 用 jung6 / iōng / yòng; dương 陽 joeng4 / iông / yáng; du lịch
  遊歷 jau4 lik6 / iû-li̍k / yóulì; dân 民 man4 / bîn / mín; diện 面 min6 / biān / miàn. **r** never starts a
  Hán-Việt word.
- **I8 nh** = Mandarin r-: nhân dân 人民 jan4 man4 / jîn-bîn / rénmín; tự nhiên 自然 zi6 jin4 / tsū-jiân / zìrán;
  nhiệt 熱 jit6 / jia̍t / rè; nhập 入 jap6 / ji̍p / rù; nhật 日 jat6 / ji̍t / rì.
- **I9 ng** = Taigi g-, Mandarin zero: ngôn ngữ 言語 jin4 jyu5 / giân-gú / yányǔ; nghiệp 業 jip6 / gia̍p / yè;
  ngọc 玉 juk6 / gio̍k / yù; ngân 銀 ngan4 / gîn / yín.
- **I10 t** from old s- / ts-: tâm 心 sam1 / sim / xīn; tân 新 san1 / sin / xīn; tiên 先 sin1 / sian / xiān;
  tính 性 sing3 / sìng / xìng.
- **I11 th** = old th- and old ɕ-: thiên 天 tin1 / thian / tiān; thông 通 tung1 / thong / tōng; thư 書 syu1 / su
  / shū; thủy 水 seoi2 / suí / shuǐ; thế 世 sai3 / sè / shì.

**Later (L30–L55)**: rhymes (-ương: 方 phương, 陽 dương; -iên: 天 thiên, 電 điện, 先 tiên); older loans read the
non-Hán-Việt way, from the database's etymons (được 得, biết 別, cũng 共, đọc 讀, đũa 箸, giờ 時); Hán-Việt
compound order versus the native order; Vietnam-made Hán-Việt words; affixes (-viên, -sĩ, -gia, -học, -hóa, bất-,
vô-, phi-); tone exceptions (động 動 dung6 / tōng / dòng, hậu 後 hau6 / hiō / hòu: old voiced 上 → nặng); idioms.

**Not used as bridge examples** (correct as history, useless to a reader): không 空, thì 時, nhưng 仍, cần 懃,
thích 適, đang 當, đường 唐 "road".

### 2.4 False friends
One per bridge slot when a lesson meets it, each added to `course/false_friends.tsv` with its evidence:
thời tiết 時節 (weather, not season; L9), bác sĩ 博士 (physician, not PhD; L12), bản đồ 版圖 (map; L8), thư 書
(letter, not book), học sinh 學生 (pupil) vs sinh viên 生員 (university student; L52), tử tế 仔細 (kind, decent),
lịch sự 歷事 (polite; the database's characters), phương tiện 方便 (means of transport), an ninh 安寧 (security),
tâm sự 心事 (to confide), đồng hồ 銅壺 (clock), khách sạn 客棧 (hotel).

## 3. Lesson by lesson
Grammar and bridge columns as in section 2 (B = finals, T = tones, I = initials, V = rhymes, FF = false friend).
Lines from the rule above. New words: native / Hán-Việt; * = target, to be fixed with each word list.

| # | Situation | Grammar | Bridge | Lines | New (nat/HV) |
|---|---|---|---|---|---|
| 1 | Hello (Chào chị) | là; tôi / anh / chị / em | — | 7 | 15/3 |
| 2 | Where are you from? | người + nationality: modifier after noun; ở đâu | B0 what Hán-Việt is | 7 | 11/5 |
| 3 | At the café | có … không?; muốn; cho tôi | — | 7 | 15/1 |
| 4 | At the market | numbers, mươi; first classifier quả; bao nhiêu | B1 finals -p -t -c | 7 | 14/5 |
| 5 | A family photo | của (often dropped); mấy; kinship nouns | — | 8 | 11/5 |
| 6 | What time is it? | clock time; đã / đang / sẽ | B2 final -m | 8 | 15/1 |
| 7 | **Review 1** | recap | — | 8 | 0 |
| 8 | Around Hoàn Kiếm lake | directions; imperative + đi / nhé | B3 -nh -ch = -ng -k | 8 | 10/6 |
| 9 | What's the weather like? | adjective as predicate (no là); rất / lắm / quá / hơi | FF1 thời tiết 時節 | 8 | 11/5 |
| 10 | A bowl of phở | đã … chưa? / rồi / chưa | T1 ngang / huyền | 8 | 14/1 |
| 11 | Weekend plans | question words; hay vs hoặc; bao giờ | T2 hỏi / ngã | 9 | 11/5 |
| 12 | Not feeling well | bị (illness); nên / phải | T3 sắc / nặng; FF2 bác sĩ | 9 | 10/5 |
| 13 | A phone call | kinship pronouns cháu / bác / cô / chú; dạ; ạ / nhé / nhỉ | T4 checked syllables | 9 | 13/3 |
| 14 | **Review 2** | recap | — | 8 | 0 |
| 15 | Buying clothes | comparison hơn / bằng / nhất | tone table recap | 9 | 12/5* |
| 16 | Dinner with the neighbours | chúng tôi vs chúng ta (阮 / 咱) | I1 kh | 9 | 12/5* |
| 17 | At the bookshop | classifiers 2: quyển, tờ, chiếc | I2 ph | 10 | 12/5* |
| 18 | Can you swim? | có thể; được after the verb; biết + verb | I3 v | 10 | 12/5* |
| 19 | A present for Bà | cho (for, to); tặng | I4 gi | 10 | 12/5* |
| 20 | A day at the office | vừa … vừa; cũng / đều | I5 tr vs ch | 10 | 12/5* |
| 21 | **Review 3** | recap | — | 8 | 0 |
| 22 | At Hà Nội station | thì; khi / lúc | I6 s vs x | 10 | 12/6* |
| 23 | Renting a room | các / những; mọi / mỗi | I7 d | 11 | 12/6* |
| 24 | Learning to ride a motorbike | direction verbs ra / vào / lên / xuống | I8 nh | 11 | 12/6* |
| 25 | Lunch near the office | result: xong, hết, thấy, được | I9 ng | 11 | 12/6* |
| 26 | Hobbies | đã từng; thường / hay / luôn | I10 t (from s, ts) | 11 | 12/6* |
| 27 | Bà's stories | còn, vẫn, nữa, lại | I11 th | 11 | 12/6* |
| 28 | **Review 4** | recap | — | 8 | 0 |
| 29 | At the bank | được (good passive) | initials recap | 12 | 12/7* |
| 30 | A stolen bike | bị vs được with an agent | V1 -ương | 12 | 12/7* |
| 31 | Tết is coming | sắp; wishes | V2 -iên | 12 | 12/7* |
| 32 | Tết in the village | in-laws, nội / ngoại (pronoun strand) | older loans 1: giờ / thời | 12 | 12/7* |
| 33 | The doctor again | nếu … thì; cần | older loans 2: đọc / độc | 12 | 12/7* |
| 34 | A football match | vì … nên; tại vì | word order in Hán-Việt compounds | 12 | 12/7* |
| 35 | **Review 5** | recap | — | 8 | 0 |
| 36 | The Old Quarter | mà (relative) | Vietnam-made Hán-Việt words | 13 | 12/8* |
| 37 | Water puppets | để (purpose) | FF3 | 13 | 12/8* |
| 38 | A wedding | tuy … nhưng; formal greetings | Hán-Việt surnames | 13 | 12/8* |
| 39 | Looking for a job | rằng (reported speech) | suffixes -viên -sĩ -gia | 13 | 12/8* |
| 40 | A trip to Hạ Long | càng … càng; không những … mà còn | suffixes -học -hóa | 13 | 12/8* |
| 41 | Feelings | cảm thấy; emotion words | prefixes bất- vô- phi- | 14 | 12/8* |
| 42 | **Review 6** | recap | — | 8 | 0 |
| 43 | Ordering online | làm cho / khiến | Mandarin words that are not Hán-Việt | 14 | 12/9* |
| 44 | An argument | chứ / mà / đâu (contradiction) | FF4 | 14 | 12/9* |
| 45 | Making up | apologies by register | tone exceptions (動 động) | 14 | 12/9* |
| 46 | At the post office | formal register: quý khách, xin vui lòng | Hán-Việt on signs | 14 | 12/9* |
| 47 | Floods in the rainy season | khi … thì; sudden events | — | 15 | 12/9* |
| 48 | Hà Nội then and now | hồi, ngày xưa: past narration | — | 15 | 12/9* |
| 49 | **Review 7** | recap | — | 8 | 0 |
| 50 | Sam writes an email | written register (second wave starts) | Hán-Việt in writing | 15 | 11/11* |
| 51 | Headlines | sự / việc / cuộc (nominalisers) | reading dense Hán-Việt | 15 | 11/11* |
| 52 | At the university | — | FF: học sinh, sinh viên | 15 | 11/11* |
| 53 | Street food | reduplication (đo đỏ, nho nhỏ) | — | 15 | 11/11* |
| 54 | Mid-Autumn | — | festivals | 15 | 11/11* |
| 55 | The Temple of Literature | four-syllable idioms | 成語 in Vietnamese | 16 | 11/11* |
| 56 | **Review 8** | recap | — | 8 | 0 |
| 57 | The National Assembly (neutral) | formal political words | politics | 16 | 11/11* |
| 58 | Ông in hospital | chăm sóc; con cháu, họ hàng | — | 16 | 11/11* |
| 59 | Bargaining at Đồng Xuân | softeners: thôi, đi, mà | — | 16 | 11/11* |
| 60 | Love songs | anh / em in songs (pronoun strand) | — | 16 | 11/11* |
| 61 | Cooking nem | trước khi / sau khi | — | 16 | 11/11* |
| 62 | Traffic rules | không được / cấm | — | 16 | 11/11* |
| 63 | **Review 9** | recap | — | 8 | 0 |
| 64 | Childhood memories | narrative connectors | — | 16 | 11/12* |
| 65 | Prices and the economy | triệu, tỷ; percentages | economy | 16 | 11/12* |
| 66 | A trip to Huế | Central speech (one note) | imperial Hán-Việt | 17 | 11/12* |
| 67 | A trip to Sài Gòn | Southern words and sounds | Southern readings nhựt, sanh | 17 | 11/12* |
| 68 | Sport and health | — | — | 17 | 11/12* |
| 69 | Money worries | dù … vẫn | — | 17 | 11/12* |
| 70 | **Review 10** | recap | — | 8 | 0 |
| 71 | Scripts of Vietnamese | chữ Hán, chữ Nôm, quốc ngữ | chữ Nôm (one note) | 17 | 11/12* |
| 72 | A folk tale | ngày xửa ngày xưa; narrative | — | 17 | 11/12* |
| 73 | Moving house | — | — | 17 | 11/12* |
| 74 | Pets | — | — | 17 | 11/12* |
| 75 | Thuốc Nam, thuốc Bắc | — | medicine | 18 | 11/12* |
| 76 | A formal letter | kính gửi; letter formulas | — | 18 | 11/12* |
| 77 | **Review 11** | recap | — | 8 | 0 |
| 78 | A typhoon day off | — | — | 18 | 11/13* |
| 79 | Family conflict | phải / cần / nên nuances | — | 18 | 11/13* |
| 80 | Science and technology | — | science | 18 | 11/13* |
| 81 | The environment | — | — | 18 | 11/13* |
| 82 | Law and rights | — | law | 18 | 11/13* |
| 83 | At the pagoda | — | Buddhist words | 18 | 11/13* |
| 84 | **Review 12** | recap | — | 8 | 0 |
| 85 | History: Bạch Đằng | — | history | 18 | 11/13* |
| 86 | Literature: Truyện Kiều | — | literary Hán-Việt | 19 | 11/13* |
| 87 | Proverbs (tục ngữ) | — | native vs Hán-Việt proverbs | 19 | 11/13* |
| 88 | A job interview | — | — | 19 | 11/13* |
| 89 | A TV interview | — | — | 19 | 11/13* |
| 90 | City or countryside? | arguing a point | — | 19 | 11/13* |
| 91 | **Review 13** | recap | — | 8 | 0 |
| 92 | Heritage and tourism | — | — | 19 | 11/13* |
| 93 | A hospital visit | — | medicine 2 | 19 | 11/13* |
| 94 | Việt kiều in France | French loans (ga, ô tô) | — | 19 | 11/13* |
| 95 | Social media | — | — | 20 | 11/13* |
| 96 | Weddings and funerals | — | — | 20 | 11/13* |
| 97 | Sam's year in Hà Nội | — | — | 20 | 11/13* |
| 98 | **Review 14** | recap | — | 8 | 0 |
| 99 | A farewell speech | formal speech | — | 20 | 11/13* |
| 100 | Goodbye, Hà Nội | — | — | 20 | 11/13* |

## 4. Decisions for the owner

| # | Question | Recommendation | Alternative |
|---|---|---|---|
| D1 | How many lessons? | **100**, review every 7th, second wave from 50 (same as Tsheh-tû) | 98 (14 weeks exactly) or 70 with denser lessons |
| D2 | How early does Hán-Việt vocabulary enter? | **From lesson 2, where natural**: about 23 % of new words in 1–14, 35 % in 15–49, over 50 % from 50 | Push it: 40 % from the start. Faster use of his Chinese, but dialogues sound bookish |
| D3 | Pronouns of the first lessons | **tôi + anh / chị / em from lesson 1**, as Sam meets older and younger people; kinship strand at 5, 13, 16, 32 | Neutral tôi / bạn first (textbook style); kinship terms from about lesson 10. Easier, less like Hà Nội speech |
| D4 | chữ Hán on the card from lesson 1? | **Yes**, for every Hán-Việt word (the card already does it); hide them only on the doubtful analyses (to-check list) | Show characters only after the word's bridge note |
| D5 | Older loans (được 得, biết 別, cũng 共) | **Show "older loan of 得 (đắc)" on the card**, readings beside it (tooling) | Leave them out; mention only in the L32–33 notes |
| D6 | How much Southern usage? | **One line in the note when the Southern word differs** (bố / ba, cốc / ly, quả / trái, đắt / mắc, ốm "ill" / "thin"); one lesson in Sài Gòn (L67) | None; or a Southern column on every card |
| D7 | May notes compare with French? | **Yes, briefly**: French loans (cà phê, xe buýt, phim, a lô, ga) and a few sounds; English stays the lesson language | English only |
| D8 | Spelling y or i (lý / lí, Mỹ / Mĩ, kỳ / kì, công ty / công ti) | **y**, as most print does (công ty 277 against công ti 4,186 in the ranks) | i (the school-reform spelling) |
| D9 | The story | **Sam** again (continuity with Tsheh-tû), at chị Lan's guesthouse in Hà Nội | A new learner character |
| D10 | Tea | **trà** in the café (L3), **chè** as the Northern home word at L16 (a native speaker should confirm the split) | chè only |
| D11 | A reading page "Lesson 0" (letters, tones, Hà Nội mergers) | **Yes** | Spread over lessons 1–13 only |
| D12 | Word list 1 | **Approve as a list of 195 rows**, with the to-check items fixed by course English | Change words or counts per lesson |

## 5. Limits, plainly
- **Written by Claude; not checked by a native speaker.** That covers the Vietnamese, the notes on Northern usage,
  the tone descriptions, the English, and the word boundaries. Where Claude is unsure the note column says so.
- **The frequency ranks are biased**: only Wiktionary words can rank; the counts lean to Wikipedia and the web
  (huyện, quận, Nguyễn, names), English leaks in (the, in), and the corpus is small and translated (tiếng Pháp ranks
  high; vâng 3,707 and phở 12,581 are underrated). Ranks guide; the topic decides.
- **The y/i split** (finding below) undercounts Hán-Việt words that are usually spelt with y.
- **Etymologies come from Wiktionary**: some are doubtful (xa 賒, đường 唐, khám 勘) and 69 of the 195 words have no
  recorded origin (marked `native?`).
- **Taigi literary readings** are taken as unmarked MOE readings where the MOE marks none; for some characters that
  is the colloquial reading (冊 tsheh, 院 īnn).

## 6. Tooling needed (not changed in this task)
1. **`syllabus.yaml` fields** per lesson: `grammar`, `bridge` (correspondence id), `strand` (pronouns),
   `lines` (planned), `new_words {native, hv}`; lint warns when a lesson's dialogue length or word count leaves the
   plan by more than one, and when a lesson's Hán-Việt share is far from it.
2. **The approved word list as a file**: `approved.word_list.file` should point to an 11-column TSV like
   `wordlist-1.tsv`; lint should check each lesson's `new_words` against it (missing, extra, other lesson).
   `verify_words.py` reads only 3 columns today.
3. **Alternative spellings**: 69 of the 3,000 most frequent keys are "alternative spelling of X" entries with no
   chữ Hán and no English of their own (lý do, công ty, Mỹ, kỳ, sức khỏe, hy vọng, kỹ thuật…). `build_db.py`
   should give them X's characters and English, and the ranks of both spellings should be pooled.
4. **Older-loan etymon on the card** (origin `nonhv`: được 得 đắc, đọc 讀 độc), if D5 is accepted.
5. **Taigi literary flag**: mark a reading taken as "unmarked" when it is not the literary one (冊 tsheh, 院 īnn,
   外 guē, 場 tshiâng, 房 pông, 醬 tsiùnn), or show it as "unmarked" instead of literary.
6. **Bridge-note examples checked by lint**: a note's examples must be database words with all three readings.
7. **Homograph tags of one etymology** (phải "right" / phải~must): today a tag needs a dictionary tag or a
   `new_words` entry; decide whether a sense tag is allowed when the etymology is the same.
8. **Characters without a word entry**: Sino-Vietnamese numerals (tam 三, thập 十) exist only as character readings,
   so a bridge note on numbers has no card to open.
9. **`make coverage` on a word list** before lessons exist (share of the top 500 / 1,000 that the plan covers).

## 7. Database faults found while querying
- The alternative-spelling gap above (item 3).
- Colloquial readings in the Taigi literary column (item 5).
- trường học is analysed 場學, a Vietnamese-order compound; the bridge then composes a Mandarin "(chǎng/cháng) xué"
  that is not a Chinese word. Such rows should be marked as composed, not shown as the "same word".
- cảm ơn exists only as an alternative form of cám ơn (no English, no characters); the Northern form needs its own.
- tam (三 in Hán-Việt) exists only as "younger sibling"; bận has no "busy" sense; thế nào's first sense is
  "inevitably"; Lan / Minh / Hoa rank as their common-noun keys.
- `vi.db` contains the fixture's 11 entries (source `fixture`); queries must filter them (the tools do).
