# Word list 1 (lessons 1–14): rows to check

Rewritten by Claude on 18 Nov 2026 after the data-quality work (branch `data-quality`), from `data/build/vi.db` and
the cards (`tools/wordlist.py` regenerated every database column of `wordlist-1.tsv`; the words did not change).
Nothing was fixed by hand in the database. **Not checked by a native speaker.**

## Summary
Of the 26 rows named in the first version, **18 are now resolved by data and code**, 2 by a reviewed judgement of
Claude's (`course/etymology-review.tsv`), and **6 remain** (below). Of the 69 rows typed `native?`, **31 now have an
origin from evidence** (20 native, 9 compound, 1 loan, 1 older Chinese loan) and **38 remain unknown**: Wiktionary has
no etymology for them, and the Vietnamese Wiktionary would not help (tools/eval_viwikt.py).
English usable on a card (tools/english.py problems): 34 rows unusable before, 5 by the same measure now (lan, mươi,
đang, mùa, thịt: description or no attested English word); `glosses-proposed.tsv` (56 rows, not in force) proposes
course English for these and for other rows whose dictionary English is long or ordered for a dictionary, not a lesson.

## Resolved by data (18)
| Word | Before | Now (database, card) |
|---|---|---|
| cảm_ơn | "alternative form of cám ơn", no chữ Hán | "to thank"; older Chinese loan of 感恩 with its readings (gam2 jan1 / kám-un / gǎn'ēn): Wiktionary's "nativisation of Chinese 感恩" read from the etymology text. "thank you" is proposed as course English. |
| a_lô | "alternative form of a-lô" | "hello (when answering the telephone)…"; loan from French allô (as a-lô). |
| bận | verb senses only | "busy" first (English Wiktionary translation table of "busy"). |
| thế_nào | "inevitably" first | "how; what; in what manner" (a Northern-tagged sense is not dialectal for this course; senses with attested English first). |
| đồng | "copper; dong (currency…)" | "copper; dong; a currency; a thousand dongs" (long senses shortened). |
| đường | 唐 shown as the same word | label **doubtful**: Wiktionary's own etymology says "alternatively, possibly"; lint refuses it as a bridge example. đường~sugar (糖) is "same". |
| xa | 賒 shown as the same word | label **opaque**: "far" is in neither CC-CEDICT's English of 賒 nor a translation table with 賒. |
| khám | 勘 | label **doubtful**: Wiktionary says "possibly contaminated by khán 看". |
| phải~must | no tag possible | the sense tag `phải~must` names the verb entry (cards.sense_tag); English "must, have to, should". |
| đang | 當 "same" | **opaque**: grammaticalised particle, its English is not among 當's senses. |
| nhưng | 仍 "same", no Taigi | **opaque**: conjunction "but", not 仍's sense. |
| thích | 適 "same" | **opaque**: "to like" is not among 適's senses. |
| sách | Taigi literary tsheh | tsheh is now **colloquial only** (its -h does not match sách's -ch): literary column empty, the card says so. |
| bệnh_viện | Taigi literary pīng-īnn | 院 īnn is colloquial only (-nn against viện's -n): literary column empty, colloquial pēnn-īnn shown as such. |
| năm, năm~year | needed a tag the database did not define | `năm~year` resolves by sense tag; năm alone is "five". |
| Lan, Minh | ranked as the common words lan, minh | a name sharing a key with a common word has no rank; the list shows none. |

## Resolved by Claude's reviewed judgement (2), `course/etymology-review.tsv`
- **không 空**: opaque (the negator is a grammaticalisation). The data alone says "same": the card's first entry by
  attested English is the number "zero", whose sense matches 空.
- **phải 被**: older loan, opaque (no sense of 被 a reader of Chinese would see in "must; right").

## Still to check (6)
| Word | Why it remains |
|---|---|
| Sam | Not a Vietnamese word: declare it with `name: true` in the lesson (decision D9). |
| nhắn (tin) | nhắn tin "to text" is not in the database; whether it is one word (nhắn_tin) needs a native speaker. |
| a_lô (spelling) | a lô / a-lô / alô: the database pools no spelling here (a lô is an "alternative form"); a native speaker should choose. |
| bát | 缽 stays "same": no evidence of doubt in the data, and Claude cannot confirm it either. |
| vâng, dạ | Ranks 3650 and 1820: the written, translated corpus underrates spoken politeness words (corpus bias, not corrected). |
| phở | Rank 12422 (corpus bias); in the list for the topic. Its older-loan etymon 牛肉粉 is marked doubtful (Wiktionary: "folk etymology"). |

## Types still `unknown` (38)
tên, vâng, ạ, rất, nào, đâu, nói, đây, nhé, mươi, rẻ, của, phút, rưỡi, hôm_nay, ngày_mai, chiều, làm, đã, rẽ, thẳng,
lắm, hơi, hôm_qua, món, chưa, rồi, gọi, rảnh, hay, mệt, sốt, nghỉ, nhắn, chờ, lát, dạ, vừa. Wiktionary gives these no
etymology (or one that names no source language); compounds such as hôm_nay stay unknown when one syllable is. Claude
believes most are native; that is not evidence and is not recorded.

## Sense tags the lessons should write
The regenerated list names a sense tag in the note where the card's main sense is not the one drafted: `từ~from`,
`trà~tea`, `sẽ~marks` (a poor tag: the course should write sẽ~future once glosses are in force). Homographs: `đường~road` / `đường~sugar`,
`năm~year`, `phải~must`.
