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
# word list 3 (19 Nov 2026): several word lists read together, the approved ones and then the draft
import course  # noqa: E402
ok(course.approved_word_lists({'approved': {'word_list': {'file': 'a.tsv'}}}) == ['a.tsv'], 'approved list: one path')
ok(course.approved_word_lists({'approved': {'word_list': {'file': ['a.tsv', 'b.tsv']}}}) == ['a.tsv', 'b.tsv'],
   'approved lists: several paths, in order')
ok(course.plan_word_lists({'approved': {'word_list': {'file': 'a.tsv'}}, 'draft': {'word_list': 'b.tsv'}})
   == ['a.tsv', 'b.tsv'], 'the plan reads the approved list, then the draft')
ok(course.plan_word_lists({'approved': {'word_list': {'file': ['a.tsv', 'b.tsv']}}, 'draft': {'word_list': 'b.tsv'}})
   == ['a.tsv', 'b.tsv'], 'a draft already approved is read once')
ok(course.plan_word_lists({'approved': {'word_list': None}, 'draft': {'word_list': 'b.tsv'}}) == ['b.tsv'],
   'nothing approved: the draft alone')
two = [dict(r, file='a.tsv') for r in base] + [dict(wrow(13, 'rẻ', note='Đắt quá!'), file='b.tsv')]
L13 = L + [lesson(13, native=1)]
e = [m for m in run(L13, two) if 'not yet taught' in m]
ok(not e, f'a note of list b may use the words list a teaches (got {e[:2]})')
dup = two + [dict(wrow(13, 'chào'), file='b.tsv')]
L13d = L + [lesson(13, native=2)]
ok(any('already in a.tsv' in m for m in run(L13d, dup)), 'a word of list a listed again in list b is refused')
ok(plan.list_counts(two).count('Word list') == 2, 'list_counts: one sentence per list')
# word list 3 review, finding 9: lint counts only the approved lists; a draft word in a lesson is refused
import re, subprocess, tempfile  # noqa: E401,E402
ROOT = os.path.dirname(HERE)
L15 = """id: 15
title: {vi: Thử, en: Test}
review: false
setting: test
dialogue:
- {n: 1, speaker: Lan, vi: "Cái này rẻ hơn.", en: "This one is cheaper."}
notes: []
new_words:
- {w: hơn, en: "more (than), -er"}
"""
real_syl = open(os.path.join(ROOT, 'course/syllabus.yaml'), encoding='utf-8').read()
both = re.sub(r'(?m)^(  word_list: \{.*file: )course/proposal/wordlist-2.tsv\}',
              r'\1[course/proposal/wordlist-2.tsv, course/proposal/wordlist-3.tsv]}', real_syl)
ok(both != real_syl, 'test syllabus: list 3 added to approved.word_list.file')
with tempfile.TemporaryDirectory() as tmp:
    les = os.path.join(tmp, 'lessons')
    os.mkdir(les)
    open(os.path.join(les, '15.yaml'), 'w', encoding='utf-8').write(L15)
    outs_ = {}
    for name, text in (('draft', real_syl), ('approved', both)):
        sp = os.path.join(tmp, name + '.yaml')
        open(sp, 'w', encoding='utf-8').write(text)
        r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'lint.py')], cwd=ROOT, capture_output=True,
                           text=True, env=dict(os.environ, TUSACH_COURSE=les, TUSACH_SYLLABUS=sp))
        outs_[name] = r.stdout + r.stderr
ok('hơn is not in the approved word list' in outs_['draft'], 'lint: a word of the draft list 3 is not approved')
ok('hơn is not in the approved word list' not in outs_['approved'] and 'approved word list:' not in outs_['approved'],
   'lint: with file: [list 2, list 3] the word is approved (both lists read)')
# a [db: …] part holding brackets is cut whole (word list 3 review, finding 24: sạch's note grew at each run)
import wordlist  # noqa: E402
ok(wordlist.human_note('clean. [db: cognate with Tho [Cuối Chăm] pʰrɛːk⁸]') == 'clean.',
   'human_note: a [db: …] part with brackets inside is removed whole')
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
ok(not real, f'the plan, the word lists and the notes agree (got {real[:3]})')
outs = plan.outputs(con)
stale = [p for p, t in outs.items() if open(p, encoding='utf-8').read() != t]
ok(not stale, f'syllabus.yaml, the proposal and the to-check list are as plan.py --write writes them ({stale})')

print(f'{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
