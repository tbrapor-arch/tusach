"""Tests of the enforcement rules (handover section 4) on the test fixture: `make test` (needs `make db db-nc`).

  python3 -I tools/test_pipeline.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cards  # noqa: E402
import check_cards  # noqa: E402
import compare  # noqa: E402
import vi  # noqa: E402

failures = []


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


def refuses(fn):
    try:
        fn()
    except SystemExit:
        return True
    return False


def run(args, env=None):
    return subprocess.run([sys.executable, '-I'] + args, cwd=ROOT, capture_output=True, text=True,
                          env=dict(os.environ, **(env or {})))


# 1. one database rule, enforced by the code
ok(refuses(lambda: cards.open_db('public', cards.DB['private'])), 'the public build refuses vi-nc.db')
ok(refuses(lambda: cards.open_db('private', cards.DB['public'])), 'the private build refuses vi.db')
ok(not refuses(lambda: cards.open_db('public')), 'the public build accepts vi.db')
r = run(['tools/build_db.py', 'data/raw', os.path.join(tempfile.gettempdir(), 'x.db'), '--nc'])
ok(r.returncode != 0 and 'refusing' in r.stdout + r.stderr, 'build_db refuses to write a non-commercial build to *.db')

# 2. one word pipeline: course lines are cut by their own boundaries; texts without boundaries by the dictionary
con = cards.open_db('public')
cards.init(con, {'name:Lan': {'w': 'Lan', 'en': 'Lan (a name)', 'name': True}})
toks = cards.tokenize('Tôi là học_sinh, Lan.')
ok([t['w']['id'] for t in toks if 'w' in t] == ['tôi', 'là', 'học sinh', 'name:Lan'], 'a course line keeps its boundaries')
toks2 = cards.tokenize_text('Tôi là học sinh.')
ok([t['w']['id'] for t in toks2 if 'w' in t] == ['tôi', 'là', 'học sinh'], 'the dictionary cutter joins học sinh')
hs = cards.dictionary['học sinh']
ok(hs.get('chars') == '學生' and all(hs.get(k) for k in ('yue', 'nan', 'cmn', 'hv')),
   'a Hán-Việt card carries its characters, Hán-Việt readings and the three Chinese readings')
ok(all(cards.dictionary[i]['en'] for i in cards.dictionary), 'every card from the pipeline has English')

# 3. partial builds add to the shared card file; nothing has to be restored
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, 'cards.json')
    st = cards.Store(path)
    st.replace_module('lessons', cards.tokenize('Tôi là học_sinh.'))
    st.replace_module('book:a', cards.tokenize('Chào chị.') + cards.tokenize('Xin chào.'))
    st.save()
    st = cards.Store(path)
    st.replace_module('lessons', cards.tokenize('Chào anh.'))       # rebuild one module only
    st.save()
    d = json.load(open(path, encoding='utf-8'))
    ok('chị' in d['cards'] and 'chào' in d['cards'], "rebuilding one module keeps the other module's cards")
    ok('học sinh' not in d['cards'], 'a card no module uses any more leaves the file')
    ok(d['modules']['book:a']['missing'] == ['Xin'], 'a word without a card is recorded as missing')
    errs = check_cards.check(path)
    ok(any('word without a card: "Xin"' in e for e in errs), 'the card check fails on a word without a card')
    # card lost / English poorer / no English
    pub = os.path.join(tmp, 'ids.txt')
    open(pub, 'w').write('gone\n')
    en = os.path.join(tmp, 'en.tsv')
    open(en, 'w').write('chào\t3\thello\n')
    errs = check_cards.check(path, None, pub, en, modules=('lessons',))
    ok(any('card lost: gone' in e for e in errs), 'the card check fails on a lost published card')
    ok(any('poorer English than before: chào' in e for e in errs), 'the card check fails on poorer English')
    d['cards']['chào']['en'] = ''
    json.dump(d, open(path, 'w', encoding='utf-8'))
    ok(any('card without English: chào' in e for e in check_cards.check(path)), 'the card check fails on a card without English')

# 4. lint: the content rules
BAD = '''id: 1
title: {vi: Thử, en: Test}
dialogue:
- {n: 1, speaker: A, vi: "Tôi là 學生.", en: x}
- {n: 2, speaker: B, vi: "Tôi là học_sinh.", en: x}
- {n: 3, speaker: B, vi: "Tôi là hoc_sinh.", en: x}
notes: [{ref: 9, text: x}]
new_words: [{w: cũng}]
exercises:
  translate: [{vi: "Tôi là học_sinh.", en: x}]
'''
with tempfile.TemporaryDirectory() as tmp:
    open(os.path.join(tmp, '01.yaml'), 'w', encoding='utf-8').write(BAD.replace('Thử', unicodedata.normalize('NFD', 'Thử')))
    r = run(['tools/lint.py'], {'TUSACH_COURSE': tmp})
    out = r.stdout
    ok(r.returncode == 1, 'lint fails on a bad lesson')
    for needle, what in [('before the owner approved', 'a lesson before the syllabus and word list are approved'),
                         ('not in Unicode NFC', 'text not in NFC'), ('chữ Hán in a lesson line', 'characters in a line'),
                         ('takes only sắc or nặng', 'an impossible tone on -c'),
                         ('exercise sentence taken from the dialogue', 'an exercise copied from the dialogue'),
                         ('is not a line of the dialogue', 'a note on a missing line'),
                         ('no English (English on every card)', 'a new word without English'),
                         ('only in the test fixture', 'a real lesson using a fixture-only word')]:
        ok(needle in out, f'lint catches {what}')

# 5. measure before and after
a = {'lines': {'L1.1': {'text': 'Tôi là học sinh.', 'cut': [['Tôi', 'tôi'], ['là', 'là'], ['học sinh', 'học sinh']]}},
     'cards': {'tôi': {'en': 'I', 'en_src': 'course'}, 'học sinh': {'en': 'pupil', 'en_src': 'course'}}}
b = {'lines': {'L1.1': {'text': 'Tôi là học sinh.', 'cut': [['Tôi', 'tôi'], ['là', 'là'], ['học', 'học'], ['sinh', 'sinh']]}},
     'cards': {'tôi': {'en': 'I', 'en_src': 'parts'}}}
ok(compare.diff(a, b) == 2, 'compare blocks on a lost card and poorer English, and lists the changed cut')

print(f'\n{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
