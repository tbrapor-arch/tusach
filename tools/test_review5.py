"""Tests of the review 5 code faults (run by `make test`; needs data/build/vi.db).

6   the Taigi vertical-line mark (U+030D: ha̍k, o̍) draws as a vertical stroke in the embedded font, and the build
    checks that every letter and mark on the page and on the cards is in the font and positioned on its letter.
4   Lesson 0: the example word of a sound-table row shows that sound (nhé is not an example of n).
1   lint: a first-person and a second-person kin term in one sentence must be a pair (anh–em, chị–em, bác–cháu…).
14  lint: an exercise may not copy an earlier lesson's dialogue line or a note example of its own lesson.
15  lint: Vietnamese in lesson notes and in new_words glosses is taught at or before the lesson, or marked {preview}.
(5 and 18, the fixture and TUSACH_LESSON0, are in tools/test_pipeline.py.)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import appfont  # noqa: E402

failures = []


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


# 6. the font
patched = appfont.font_bytes()
upstream = open(appfont.FONT, 'rb').read()
p, _ = appfont.font_problems(['ha̍k', 'o̍', 'a̍', 'ế ự ỗ', 'Tâi-lô', 'xuéshēng', 'hok6'], patched)
ok(p == [], f'the page font draws a̍ o̍ ha̍k and the Vietnamese marks, positioned {p}')
p, _ = appfont.font_problems(['ha̍k'], upstream)
ok(any('draws as a dot' in x for x in p), 'the upstream subset is caught: its U+030D is a dot-sized stroke')
from fontTools.ttLib import TTFont  # noqa: E402
import io  # noqa: E402
g = TTFont(io.BytesIO(patched))['glyf']['uni030D']
ok(g.yMax - g.yMin >= appfont.MIN_STROKE_RATIO * (g.xMax - g.xMin) and g.yMin > 536,
   'U+030D is a vertical stroke above the mark anchor (y 536)')
p, _ = appfont.font_problems(['a᪰'], patched)
ok(any('lacks U+1AB0' in x for x in p), 'a mark the font lacks is an error')
p, _ = appfont.font_problems(['µ̍'], patched)
ok(any('no mark positioning' in x for x in p), 'a mark with no positioning on its letter is an error')

# 1. person terms in pairs
import lint  # noqa: E402
ok(lint.kin_mismatch('Anh rất vui được gặp chị.') == [('anh', 'chị')], 'lint: "Anh … gặp chị" is not a pair')
ok(not lint.kin_mismatch('Em rất vui được gặp chị ạ.') and not lint.kin_mismatch('Cháu chào bác ạ!')
   and not lint.kin_mismatch('Tôi rất vui được gặp chị Lan.') and not lint.kin_mismatch('Chị ơi! Cho em hai cốc trà.'),
   'lint: em–chị, cháu–bác, tôi with any are pairs')
ok(not lint.kin_mismatch('Ông và bà ở Hà_Nội.') and not lint.kin_mismatch('Mẹ chị đây!')
   and not lint.kin_mismatch('Anh ấy là chồng chị.') and not lint.kin_mismatch('Bác này là bố chị à?'),
   'lint: ông và bà, mẹ chị, anh ấy, bác này are third persons, not counted')

# 14, 15. copies from earlier lessons and from note examples; Vietnamese in notes and glosses taught first
lint.D = lint.DB_(lint.DB)
L1 = {'id': 1, 'dialogue': [{'n': 1, 'vi': 'Cháu chào bác ạ!'}],
      'notes': [{'ref': 1, 'text': 'Before a noun: Thảo không phải là người Pháp "Thảo is not French". {dạ} is Southern.'}],
      'new_words': [{'w': 'cháu', 'en': 'grandchild'}, {'w': 'chào', 'en': 'hello'}, {'w': 'bác', 'en': 'uncle'},
                    {'w': 'ạ', 'en': '(polite)'}],
      'exercises': {'translate': [{'vi': 'Thảo không phải là người Pháp.', 'en': 'x'}]}}
L2 = {'id': 2, 'dialogue': [{'n': 1, 'vi': 'Chào em.'}],
      'notes': [{'ref': 1, 'text': 'The South says mắc for "expensive"; ơi calls (Mandarin nán); the letter o.'}],
      'new_words': [{'w': 'ấy', 'en': 'that (cô ấy she)'}],
      'exercises': {'fill': [{'vi': 'Cháu ___ bác ạ!', 'answer': 'chào', 'en': 'x'}]}}
msgs = []
lint.notes_order_and_copies([('/x/01.yaml', L1), ('/x/02.yaml', L2)], msgs)
out = '\n'.join(m for _, m in msgs)
ok('exercise sentence taken from a note example of this lesson' in out, 'lint: an exercise copying a note example')
ok('exercise sentence taken from lesson 1 line 1' in out, "lint: an exercise copying an earlier lesson's line")
ok('mắc' in out and 'ơi' in out and 'dạ' not in out, 'lint: an untaught word in a note (mắc, ơi), a {preview} accepted')
ok('gloss of ấy uses words not yet taught: cô' in out, 'lint: an untaught word in a new_words gloss (cô ấy)')
ok('nán' not in out and ' o ' not in out, 'lint: Chinese readings and spelling letters in notes are not words')

# 4. Lesson 0: a sound table's example word shows the sound of its row
import lesson0  # noqa: E402
bad0 = {'sections': [{'id': 'consonants', 'body': [{'table': {'head': ['Letter', 'Example'], 'rows': [
    ['h, l, m, n', '[[mẹ]] mother · [[nhé]] OK?'], ['c, k, q', '[[quán]] café'], ['d, gi, r', '[[gì]] what']]}}]},
    {'id': 'finals', 'body': [{'table': {'head': ['Final', 'Example'], 'rows': [['-nh, -ch', '[[anh]] · [[thích]]'],
                                                                                 ['-ng', '[[năm~five]]']]}}]}]}
pr = lesson0.example_problems(bad0)
ok(len(pr) == 2 and 'nhé' in pr[0][1] and 'năm' in pr[1][1],
   f'Lesson 0: nhé is not an example of n, năm not of -ng; quán (qu), gì (gi), anh, thích are fine {pr}')
ok(lesson0.example_problems(lesson0.load()) == [], 'Lesson 0: every example word of the sound tables shows its sound')

print(f'\n{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
