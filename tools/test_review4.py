"""Tests of the review 4 code faults (run by `make test`; needs data/build/vi.db).

A  origin notes: what the etymology says about THIS word, with a form; an ancestor is never a cognate (etym.py
   self-test, repeated here on the real entries).
B  a Unihan variant lends its readings only when it sounds the same (bridge.same_sound): 襖 is not read as 澳.
C  the order check works on tokens: a lone plain word (mua, cho) is checked, a sentence-initial name that is also a
   common word (Mai / mai) is checked as the word; the rule tables show the best single guess beside the kind.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402
import bridge_rules  # noqa: E402
import cards  # noqa: E402
import etym  # noqa: E402
import plan  # noqa: E402

con = cards.open_db('public')
cards.init(con)


def card(w):
    return cards.dictionary[cards.lookup(w)]


# A
etym._selftest()
assert card('lăm')['origin'].endswith('an alteration of năm “five” after mười “ten”'), card('lăm')['origin']
assert 'maːl' not in card('lăm')['origin']
assert 'cognate' not in card('muốn')['origin'] and 'cognate' not in card('sáng')['origin']
for w in ('ngon', 'đói', 'bận', 'nên', 'tốt'):
    o = card(w)['origin']
    assert not o.endswith(('Muong', 'Thavung')), (w, o)
assert 'Middle Vietnamese chị' not in card('chị')['origin']

# B
assert not bridge.same_sound(con, '襖', '澳')
assert bridge.same_sound(con, '迹', '跡')
assert not card('áo').get('nan') or 'ò' not in card('áo')['nan'], card('áo').get('nan')

# C
W = plan.Words(con, ['Mai', 'Lan'])
taught = {'mua': 13, 'cho': 3, 'tôi': 1, 'gặp': 1, 'nhé': 3, 'chị': 1}
assert any(x.startswith('mua') for x in W.late('mua; bao nhiêu', 4, taught)), W.late('mua; bao nhiêu', 4, taught)
assert W.late('mua', 13, taught) == []
assert any(x.startswith('cho') for x in W.late('cho', 2, taught))
# review 6, finding 15 changed C: a sentence-initial cast name is read as its common word only when that word is
# taught (else it is the name: no false error in English notes); tools/test_plan.py has the cases
assert W.late('Mai gặp nhé', 3, taught) == [], W.late('Mai gặp nhé', 3, taught)
assert W.late('Tôi gặp chị Mai', 3, taught) == [], W.late('Tôi gặp chị Mai', 3, taught)
m = {'way': 'zh>vi', 'hit': 22, 'tot': 23, 'best': ('tr', 14), 'text': 'tr or th ← Mandarin ch- in tone 2'}
assert bridge_rules.kind_cell(m) == '**rule** (one guess: tr 61 %)', bridge_rules.kind_cell(m)
m1 = dict(m, best=('tr', 22))
assert bridge_rules.kind_cell(m1) == '**rule**'
print('review 4: ok')
