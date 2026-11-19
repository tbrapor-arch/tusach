# Word list 3 (lessons 15–28): drafter's notes

Working notes of the drafting session (Claude, 19 Nov 2026, branch `wordlist-3` from main ac5ae29). NOT approved by the
owner; NOT checked by a native speaker. The list is `wordlist-3.tsv`, its doubts and overrides `wordlist-3-to-check.md`.

## Method
- One scene per lesson (syllabus.yaml title), words chosen for that scene's natural dialogue, the lesson's grammar
  points and particle (thôi L15, hả / nhá L16, với L17, chứ L18, dạ L19, mà L27), and its bridge topic. Bridge words
  named in the notes are Hán-Việt words of list 2 or 3, the same word in Chinese, never a false friend.
- Counts: native / Hán-Việt exactly the plan's (L15–20, L22: 13 + 5; L23–27: 13 + 6; L21, L28 none). The plan's guess
  of 2 older or other loans per lesson is not kept: the list has 1–5 (L15 5, L16 1, L17 5, L18 3, L19 2, L20 4,
  L22 4, L23 4, L24 2, L25 3, L26 2, L27 3): many basic words are older loans (kia, cũ, tìm, đọc, tầng, thuê, muộn…).
  `tools/plan.py --write` wrote these into syllabus.yaml.
- No word of word list 2 (the plan check now refuses one). Northern forms: bể bơi, thìa, ngõ, hiệu sách, muộn, quyển,
  chén; the Southern ones only as {previews} in notes.
- Every candidate was read on its real card first (a scratch script calling tools/cards.py, outside the repository).
- Lexicon: 127 new rows; 75 existing rows got an example. Every example uses only words taught by its lesson
  (`tools/plan.py --check --verbose`: no I-line on a list-3 word).

## Tool change (tested, documented)
`approved.word_list.file` may be a list. `course.plan_word_lists()` = the approved lists, then the draft; plan.py, lint
(lessons against the union of approved lists; compound check), wordlist.py --to-check and state.py read them together.
A word already in an earlier list is an error. When the owner approves list 3:
`word_list: {by: owner, date: …, file: [course/proposal/wordlist-2.tsv, course/proposal/wordlist-3.tsv]}`.
Tests: tools/test_plan.py (6 new cases).

## Decisions
- L15 triệu taught now (phone prices); its false-friend note stays on the card; the syllabus's FF remark is L59.
- L16 em gái rather than em trai (Thảo is Lan's younger sister); em trai later.
- After the review (`wordlist-3-review.md`): ngồi (L16), hiểu (L18), từ~from (L22), trong (L23), trước (L24) taken in
  for ngọt, an toàn, toa, chật, tay; mèo (L17) for túi, so the classifier con has a noun; môn 門 (L19) for vị, an m-
  word for the labial bridge; học sinh moved to L16 (cam out), hòa bình at L27. kỷ niệm and suất are false friends
  on their cards (suất is no longer a bridge word).
- L17 truyện, bút, giấy, vở left out to keep 5 Hán-Việt; truyện can come at L26/L27 later lists.
- L18 nông "shallow" left out (homograph with 農 and others); sâu alone.
- L19 trường (false friend 場) taught for "Ông dạy văn ở trường"; the syllabus's FF remark is L52.
- L24 bình tĩnh and kinh nghiệm instead of kỹ (opaque 技).
- L25 tính tiền (compound) rather than thanh toán (清算 is "to liquidate" in Chinese).
- L27 mà: the card example shows "but" (main sense, Rẻ mà ngon); the insisting particle is in its usage note.

## Doubts (for the owner / a native speaker)
- máy for "the phone" in a shop (Máy này bao nhiêu tiền?): Claude's reading of shop talk.
- tờ 詞 and vé 貨: Wiktionary's etymons, marked doubt.
- kỷ niệm 紀念: Chinese "commemorate, souvenir"; "memories" is the Vietnamese sense (false-friend note on the card).
  verify_words flags 紀 as read kỉ, not kỷ: the i/y spelling of the same syllable (the lexicon check accepts it).
- văn phòng, sở thích, thực đơn are Hán-Việt formed in Vietnam (counted Hán-Việt, not bridge words).
- toa: origin unknown in the data (not claimed French).
- Hà Nội usage to confirm: suất (một suất bún chả), chén for tea, nghỉ hưu / về hưu, chờ / đợi, rạp alone for a cinema
  (the reviewer judged them right; đợi is at least as common as chờ in Hà Nội speech).

## Status
- [x] wordlist-3.tsv, database columns from tools/wordlist.py
- [x] lexicon rows and examples
- [x] syllabus draft pointer (approved untouched) + tool change, test, REFERENCE
- [x] plan --write, to-check, golden (diff read: only examples and three usage notes of existing cards), state
- [x] make lint 0 errors (verify_words: 350 suspects, the same as main: none from this work); the tests of `make
  test` run one by one without the db rebuild (all pass); make app: card check 0 errors

## Left
- Review: `wordlist-3-review.md` (25 findings; 17 fixed, the rest with the reason).
- The owner's approval (then `approved.word_list.file` as a list, above). Lessons 15–27 are not written.
