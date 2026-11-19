"""Tests of tools/plan.py, the plan / word list / proposal checks (`make test`, needs the public database).

  python3 -I tools/test_plan.py

Review 3's finding 1, each case reproduced on a small plan: a grammar point using a word taught later (L3 "không
phải là" with phải at L8), a note using one (L4 "Đắt quá!" with quá at L9, L5 "Cháu mấy tuổi?" with cháu at L12, L1
"chào bác ạ" with bác at L12), a new word in a review lesson (L7), counts that leave the word list, a particle its
lesson does not name; {preview} passes. Then the real files: 0 errors, and --write would change nothing.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cards  # noqa: E402
import lexicon  # noqa: E402
import plan  # noqa: E402

failures = []


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


con = cards.open_db('public')


def wrow(n, word, typ='native', note=''):
    return {'lesson': str(n), 'word': word, 'type': typ, 'note': note, 'line': 0, 'english': '', 'freq_rank': '',
            'characters': '', 'han_viet': '', 'cantonese': '', 'taigi_literary': '', 'mandarin': ''}


def lesson(n, grammar='', review=False, native=0, hv=0, vi=''):
    return {'n': n, 'en': f'L{n}', 'vi': vi, 'grammar': grammar, 'review': review, 'lines': 7,
            'new_words': {'native': native, 'hv': hv}}


def run(lessons, rows, particles=(), lex=None):
    syl = {'lessons': lessons, 'particles': list(particles), 'cast': ['Sacha', 'Lan']}
    saved = plan.load, lexicon.load
    plan.load = lambda: (syl, rows, 'test.tsv')
    lexicon.load = lambda path=None: lex or []
    try:
        return [m for lv, m in plan.check(con) if lv == 'E']
    finally:
        plan.load, lexicon.load = saved


base = [wrow(1, 'chào'), wrow(1, 'chị'), wrow(1, 'ạ'), wrow(2, 'không'), wrow(2, 'là'), wrow(3, 'đắt'),
        wrow(3, 'mấy'), wrow(3, 'tuổi'), wrow(8, 'phải~right'), wrow(9, 'quá'), wrow(12, 'cháu'), wrow(12, 'bác')]
counts = {1: 3, 2: 2, 3: 3, 8: 1, 9: 1, 12: 2}
L = [lesson(n, native=counts.get(n, 0), review=n == 7) for n in range(1, 13)]

e = run(L, base)
ok(not [m for m in e if 'not yet taught' in m], f'a clean plan passes (got {e[:3]})')
L3 = [dict(x, grammar='không phải là') if x['n'] == 3 else x for x in L]
ok(any('lesson 3 grammar' in m and 'phải' in m for m in run(L3, base)), 'L3 grammar "không phải là" with phải at L8')
rows = [dict(r, note='Đắt quá!') if r['word'] == 'đắt' else r for r in base]
ok(any('quá' in m for m in run(L, rows)), 'L3 note "Đắt quá!" with quá at L9')
rows = [dict(r, note='Cháu mấy tuổi?') if r['word'] == 'mấy' else r for r in base]
ok(any('Cháu' in m for m in run(L, rows)), 'note "Cháu mấy tuổi?" with cháu at L12')
rows = [dict(r, note='chào chị ạ; {chào bác ạ}') if r['word'] == 'chào' else r for r in base]
ok(not [m for m in run(L, rows) if 'not yet taught' in m], 'a {preview} is not checked')
rows = [dict(r, note='chào bác ạ') if r['word'] == 'chào' else r for r in base]
ok(any('bác' in m for m in run(L, rows)), 'L1 note "chào bác ạ" with bác at L12')
rows = base + [wrow(7, 'quả')]
ok(any('review' in m for m in run(L, rows)), 'a new word in review lesson 7 is refused')
L2 = [dict(x, new_words={'native': 5, 'hv': 0}) if x['n'] == 2 else x for x in L]
ok(any('lesson 2 plans' in m for m in run(L2, base)), 'counts that leave the word list are refused')
ok(any('particle ạ' in m for m in run(L, base, [{'w': 'ạ', 'n': 1, 'use': ''}])),
   'a particle its lesson\'s grammar does not name is refused')
ok(any('particle quá' in m and 'L9' in m for m in run(
    [dict(x, grammar='quá') if x['n'] == 3 else x for x in L], base, [{'w': 'quá', 'n': 3, 'use': ''}])),
   'a particle the word list teaches later than its lesson is refused')
lex = [{'key': 'đắt', 'k': 'đắt', 'cid': 'đắt', 'pos': 'adj', 'usage': 'Đắt quá!', 'false_friend': '', 'n': 1,
        'example': '', 'tag': None}]
ok(any('usage' in m and 'quá' in m for m in run(L, base, lex=lex)), 'a lexicon usage note of the lesson is checked too')
w = plan.Words(con, ['Lan'])
ok(w.runs('the word quán cà phê, a café') == [['quán', 'cà', 'phê']], 'runs: English words and "café" are left out')
ok(not w.late('Hán-Việt, sắc and nặng', 1, {}), 'metalanguage (Hán-Việt, tone names) is not a lesson word')
# review 6, finding 15: a cast name is read as its common word only at a sentence start and when that word is taught
w = plan.Words(con, ['Lan', 'Minh', 'Mai'])
ok(not w.late('With Lan: Minh is anh.', 5, {'anh': 1}), 'runs: "…: Minh is anh" (after a colon) is the name Minh')
ok(not w.late('He says: "Minh is anh".', 5, {'anh': 1}), 'runs: a name after an opening quote is the name')
ok(not w.late('Minh is older. Mai is 27.', 11, {}), 'runs: a sentence-initial name whose common word is not taught')
ok(w.runs('Bye. Mai gặp nhé', {'mai': 6, 'gặp': 1, 'nhé': 3}, 6)[-1][0] == 'mai',
   'runs: a sentence-initial name whose common word is taught is read as that word (mai "tomorrow")')
ok(w.runs('Bye. Mai gặp nhé', {'gặp': 1, 'nhé': 3}, 6)[-1][0] == 'Mai', 'runs: … and stays the name when it is not')

# the real files
real = [m for lv, m in plan.check(con) if lv == 'E']
ok(not real, f'the plan, word list 2 and the notes agree (got {real[:3]})')
outs = plan.outputs(con)
stale = [p for p, t in outs.items() if open(p, encoding='utf-8').read() != t]
ok(not stale, f'syllabus.yaml, the proposal and the to-check list are as plan.py --write writes them ({stale})')

print(f'{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
