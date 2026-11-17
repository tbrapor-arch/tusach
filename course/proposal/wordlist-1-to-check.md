# Word list 1 (lessons 1–14): rows to check

Written by Claude on 18 Nov 2026 from `data/build/vi.db` (built from dcaf84f). Nothing here was fixed by hand: each
item says what the database gives and what looks wrong. **Not checked by a native speaker.**

## Missing from the database (3)
| Lesson | Word | Problem |
|---|---|---|
| 1 | Sam | Not a Vietnamese word (the learner's name in the dialogues); declare it with `name: true`. The key `sam` exists only as "horseshoe crab". |
| 13 | nhắn tin | "to text, send a message": the database has no such word; the list uses nhắn + tin as two words. A native speaker should say whether it is one word (house style would then write nhắn_tin). |
| 1 | cảm ơn (chữ Hán) | In the database only as "alternative form of cám ơn", no chữ Hán and no English of its own. cảm ơn is the Northern form and the one the course should use. 感恩 is the usual analysis (Claude, not from the database): no bridge row is shown. |

## English in the database too poor for the card (5): course English needed in `new_words`
| Lesson | Word | Database English | Suggested |
|---|---|---|---|
| 1 | cảm_ơn | alternative form of cám ơn ("thank you") | thank you; to thank |
| 13 | a_lô | alternative form of a-lô | hello (on the phone). Spelling a lô / a-lô / alô varies: pick one |
| 11 | bận | verb senses only ("to get occupied doing something") | busy |
| 9 | thế_nào | first sense "inevitably, somehow or other" | how?; what … like? |
| 4 | đồng | "copper; dong (currency of Vietnam…)" under 銅 | dong (the currency) |

## Doubtful Sino-Vietnamese analyses (6): the card would show these characters
| Lesson | Word | Database | Doubt |
|---|---|---|---|
| 8 | đường "road" | 唐 tong4 / tông / táng | An old etymology; no Chinese reader sees "road" in 唐. Keep off bridge notes; perhaps hide the characters for this sense. |
| 8 | xa "far" | 賒 se1 / sia / shē ("buy on credit") | Looks wrong or at least opaque. |
| 12 | khám "to examine (a patient)" | 勘 ham3 / kham / kān | Plausible (勘 "to survey") but Claude cannot confirm. |
| 10 | bát "bowl" | 缽 but3 / puat / bō | Plausible; Claude cannot confirm. |
| 8, 12 | phải "right; must" | older loan of 被 (etymon) | Surprising; leave out of bridge notes. |
| 1, 6, 9, 11 | không 空, đang 當, nhưng 仍, thích 適 | sino, all three readings (nhưng: no Taigi) | Correct as history but grammaticalised or opaque: not used as bridge examples. |

## Taigi "literary" column showing a colloquial reading (2 in this list)
The MOE marks no literary reading for some characters, so the database takes the unmarked one, which is the
colloquial reading here. Claude's knowledge, to confirm with the MOE dictionary:
| Lesson | Word | Database Taigi | Literary reading expected |
|---|---|---|---|
| 11 | sách 冊 | tsheh | tshik |
| 12 | bệnh_viện 病院 | pīng-īnn | pīng-uān (院 uān) |

## Ranks to read with care (4)
| Word | Rank | Why |
|---|---|---|
| vâng | 3707 | Everyday spoken "yes"; the written, translated corpus underrates it. Same for dạ (1873). |
| Lan, Minh, Hoa | 1687, 769, 224 | The rank is the key's (lan "orchid", minh 明, hoa "flower"), not the name's. |
| phở | 12581 | Corpus bias; it is in the list for the topic. |
| không, các… | 9, 6 | Fine; listed only because their analysis is opaque (above). |

## Types: 69 rows marked `native?`
The database gives no origin for them (Wiktionary has no `inh` etymology). Claude believes most are native; a few
may be old Chinese loans not recorded. Not checked.

## Homographs needing a tag (2)
năm (five, L4) / năm~year (L5) and phải (right, L8) / phải~must (L12): same spelling, different sense in the course.
For năm the two are different words; for phải the database has one etymology with two senses (see "tooling needed" in
the proposal: a tag that the database does not define).

Total: 26 rows of the 195 are named above (Sam, nhắn, cảm_ơn, a_lô, bận, thế_nào, đồng, đường, xa, khám, bát,
phải, phải~must, không, đang, nhưng, thích, sách, bệnh_viện, vâng, dạ, Lan, Minh, phở, năm, năm~year); the 69
`native?` types are counted apart.
