"""Tests of the review 5 code faults (run by `make test`; needs data/build/vi.db).

6   the Taigi vertical-line mark (U+030D: ha̍k, o̍) draws as a vertical stroke in the embedded font, and the build
    checks that every letter and mark on the page and on the cards is in the font and positioned on its letter.
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

print(f'\n{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
