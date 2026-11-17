# Word segmentation convention

The convention for word boundaries in this repository: lesson lines (`học_sinh`), the cutter reference
(`tests/cutter/reference.tsv`) and the rules of the dictionary cutter (`tools/vi.py cut()`). Written by Claude on
18 Nov 2026, **not checked by a native speaker**. An underscore joins the syllables of one word; a space separates words.

**Principle.** A word is a unit a dictionary lists because its meaning or use is fixed: it is not built freely by the
grammar. Two free words that combine in the ordinary way stay two words, even when a dictionary happens to list the pair.

| Case | Rule | Examples |
|---|---|---|
| Compounds | One word: Sino-Vietnamese and native compounds, coordinative ones with a fixed sense, loans | học_sinh, bệnh_viện, xe_đạp, máy_bay, quần_áo, cà_phê, điện_thoại |
| Reduplication | One word, full or partial | sạch_sẽ, xinh_xắn, từ_từ, nho_nhỏ, ngày_ngày |
| Classifier + noun | Two words, also with a compound noun; only a few lexicalised pairs with a meaning of their own are one word | con chó, căn nhà, cây vợt, quyển sách, chiếc xe_đạp; but con_người, con_cái, cây_cối |
| Verb + direction or result | Two words | đi ra, chạy vào, mang về, đứng lên, làm xong, ăn hết, tìm thấy, nghe thấy |
| Verb + object or verb + verb | Two words when free; one word for a fixed activity or sense | đi học, đi làm, đi chợ, xem phim, đọc báo; ăn_sáng, ăn_tối, đi_bộ, làm_việc, nói_chuyện, hút_thuốc, về_hưu, đánh_rơi, đau_đầu |
| Kin and fixed noun compounds | One word | em_gái, anh_trai, con_trai, anh_em, ông_bà, em_bé, cô_giáo, phòng_ngủ, nhà_ga, bên_ngoài |
| Names | A place name or a person's full name is one word; a title or kinship term before it is not | Việt_Nam, Hà_Nội, Sài_Gòn, Nguyễn_Văn_An; anh Nam, cô Lan |
| tiếng + language | One word (it names the language); người + nationality is two | tiếng_Việt, tiếng_Anh; người Việt |
| Function words | A free sequence of grammatical words is several words; a fixed connective, modal or interrogative is one | không phải, cũng không, rất là, đã từng, làm gì, làm cho, đi đâu, ở đâu; có_thể, không_thể, vì_vậy, cho_nên, bởi_vì, tuy_nhiên, như_vậy, tại_sao, bao_giờ, bao_nhiêu, thế_nào, tất_cả, sau_khi, trước_khi |
| Question words | gì, ai, đâu are always words of their own; nào after a noun too | cái gì, ai đó, lúc nào, người nào |
| Pronouns | Pronouns built with a bound syllable are one word; ấy / ta / này after a pronoun or noun are separate | chúng_tôi, chúng_ta, chúng_nó; anh ấy, cô ta, cái này |
| Numbers and dates | Each numeral syllable is a word; digits are not words; day names are one word | hai mươi lăm, mười một, ngày 5 tháng 3, thứ_hai, chủ_nhật, năm 2024 |

Notes: `mọi người`, `các bạn`, `những người` are a quantifier or plural marker + noun (two words). A generic noun
before a name stays apart (hồ Hoàn_Kiếm, bệnh_viện Bạch_Mai) unless the name needs it (Hồ_Tây, "West Lake").
Productive `bao` + adjective (bao xa, bao lâu) is two words; bao_giờ and bao_nhiêu are one. `người ta`
("one, people") is one word (fixed pronoun). Time words of fixed form are one word (hôm_nay, ngày_mai, bây_giờ,
buổi_sáng); `sáng nay`, `tối qua` (noun + deictic) are two.

How the cutter follows it (`tools/vi.py cut()`): longest dictionary match, except that it never joins (1) a classifier
with what follows unless the pair is in `LEXICALISED`, (2) a sequence made only of free grammatical words unless it is
in `LEXICALISED`, (3) a question word gì / ai / đâu with anything. The lists are in `tools/vi.py`, next to this rule.
