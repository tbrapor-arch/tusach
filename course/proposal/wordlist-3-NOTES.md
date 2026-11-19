# Word list 3 (lessons 15–28): drafter's notes

Working notes of the drafting session (Claude, 19 Nov 2026, branch `wordlist-3` from main ac5ae29). NOT approved by the
owner; NOT checked by a native speaker. Kept short; the list itself is `wordlist-3.tsv`, its doubts and overrides
`wordlist-3-to-check.md`.

## Method
- One scene per lesson (syllabus.yaml title), words chosen for that scene's natural dialogue, the lesson's grammar
  points and particle (thôi L15, hả / nhá L16, với L17, chứ L18, dạ L19, mà L27), and its bridge topic (bridge
  examples are Hán-Việt words of this list or list 2, same word in Chinese, not false friends).
- Counts aimed at the plan as it stood before `tools/plan.py --write`: L15–20 and L22 13 native (2 of them older or
  Western loans) + 5 Hán-Việt; L23–27 13 + 6. Reviews L21, L28: no word.
- No word of word list 2 (lint checks both lists together, see "Tool change"). Northern forms (bể bơi, thìa, ngõ,
  hiệu sách, đỗ…); spelling and tone placement as lint asks.
- Candidates read on the real cards (`tools/cards.py` through a scratch script outside the repository) before choosing.

## Status
- [ ] wordlist-3.tsv (lesson, word, note) and database columns (tools/wordlist.py)
- [ ] lexicon rows for every new word (example with words taught by that lesson)
- [ ] syllabus draft pointer + tool change (plan reads approved lists + draft)
- [ ] plan --write, to-check, golden, state
- [ ] make lint / test / app

## Decisions and doubts
(filled in as the work goes)
