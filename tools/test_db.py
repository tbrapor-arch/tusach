"""Tests of the database build, the bridge join and the word frequency (`make test`).

  python3 -I tools/test_db.py

Builds a database from tools/fixtures/raw (a kaikki-shaped test file; every other source absent) and checks the
Wiktionary loader, the "not fetched" path, the labels, the Hán-Việt readings by kind, the bridge join and freq.py.
"""
import os
import sqlite3
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bridge  # noqa: E402
import freq  # noqa: E402

failures = []
ALL_BUT_WIKTIONARY = 'thieuchuu,unihan,rime,moe,cedict,tatoeba,tatoeba-challenge,frequencywords'


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


# 1. pinyin
ok(bridge.pinyin_marks('xue2 sheng5') == 'xuésheng', 'pinyin: xue2 sheng5 -> xuésheng')
ok(bridge.pinyin_marks('Yue4 nan2') == 'Yuènán', 'pinyin keeps capitals: Yuènán')
ok(bridge.pinyin_marks('lu:4 gui4 liu2') == 'lǜguìliú', 'pinyin: ü, -ui, -iu')

# 2. a build from the kaikki-shaped fixture, the other sources missing
with tempfile.TemporaryDirectory() as tmp:
    db = os.path.join(tmp, 'vi.db')
    r = subprocess.run([sys.executable, '-I', 'tools/build_db.py', 'tools/fixtures/raw', db], cwd=ROOT,
                       capture_output=True, text=True, env=dict(os.environ, TUSACH_ALLOW_MISSING=ALL_BUT_WIKTIONARY))
    out = r.stdout + r.stderr
    ok(r.returncode == 0, 'build_db runs with most sources missing when they are allowed (TUSACH_ALLOW_MISSING)')
    ok('source thieuchuu not fetched' in out and 'source rime not fetched' in out, 'a missing source is reported')
    con = sqlite3.connect(db)
    meta = dict(con.execute('SELECT key, value FROM meta'))
    ok('wiktionary' in meta['sources'].split() and 'rime' in meta['missing'].split(), 'meta lists used and missing sources')
    e = {r[0]: r[1:] for r in con.execute("SELECT key, chars, origin, label, english FROM entry WHERE source='wiktionary'")}
    ok(e.get('học sinh', ())[:3] == ('學生', 'sino', 'same'), 'vi-etym-sino gives the characters (odd arguments) and label same')
    ok(e.get('đại học', ())[:1] == ('大學',), 'vi-etym-sino with the whole word in one argument')
    ok(e.get('chó', ())[:3] == ('', 'vietic', 'native'), 'an inherited Vietic word is labelled native')
    ok(e.get('cà phê', ())[:3] == ('', '', ''), 'a borrowing is neither same nor native')
    ok('sung' in e and 'ken' not in e and '馬' not in e and 'dog' not in e,
       'keeps a glossless Sino-Vietnamese entry; drops empty stubs, Han-character headwords and other languages')
    hv = set(con.execute("SELECT char, reading, kind FROM hanviet WHERE source='wiktionary'"))
    ok(('學', 'học', 'hv') in hv and ('學', 'học', 'nom') in hv and ('犭', 'khuyển', 'hannom') in hv
       and ('生', 'sinh', 'hv') in hv, 'character readings kept apart: Hán-Việt, Nôm, Hán-Nôm')
    ok(con.execute("SELECT count(*) FROM example WHERE source='wiktionary'").fetchone()[0] == 2,
       "Wiktionary's examples (english or translation) are kept")
    ok(dict(con.execute("SELECT key, hv_check FROM entry WHERE source='wiktionary' AND chars != ''")).get('học sinh') == 'ok',
       'the Hán-Việt check of học sinh is ok')
    b = dict((r[0], r[1:]) for r in con.execute('SELECT chars, n, yue FROM bridge'))
    ok(b.get('學生', (0,))[0] == 3 and b.get('大學', (9,))[0] == 0,
       'bridge: 學生 has three readings (fixture), 大學 none (no Chinese source fetched)')

# 3. the join: whole word first, else character by character with every reading, nothing chosen silently
con = sqlite3.connect(':memory:')
con.executescript(open(os.path.join(HERE, 'schema.sql'), encoding='utf-8').read())
con.execute("INSERT INTO source VALUES ('s', '', '', '', '', 1, 0)")
con.executemany("INSERT INTO chinese VALUES (?,?,?,'s',?,?,?,?)", [
    ('銀', 'yue', 'ngan4', 'char', None, '', 1), ('行', 'yue', 'hong4', 'char', 5, '', 2),
    ('行', 'yue', 'hang4', 'char', None, '', 1), ('行', 'yue', 'haang4', 'char', 5, '', 3),
    ('銀行', 'cmn', 'yínháng', 'word', None, '', 1), ('銀', 'cmn', 'yín', 'char', None, '', 1),
    ('行', 'cmn', 'Háng', 'char', None, 'name', 1), ('行', 'cmn', 'xíng', 'char', None, '', 2)])
con.executemany("INSERT INTO hanviet VALUES (?,?,'hv','s',?,NULL)", [('銀', 'ngân', 0), ('行', 'hành', 0), ('行', 'hàng', 1)])
j = bridge.join(con, '銀行')
ok(j['yue'] == 'ngan4 (hang4/hong4/haang4)' and j['yue_by'] == 'char',
   'built by character: every reading kept, main reading first, then by share')
ok(j['cmn'] == 'yínháng' and j['cmn_by'] == 'word', 'the whole word wins over the characters')
ok(j['nan'] == '' and j['nan_by'] == '' and j['n'] == 2, 'a missing language stays empty and is counted')
ok(j['hv'] == '銀 ngân · 行 hành/hàng', 'Hán-Việt readings per character')
ok(bridge.join(con, '行')['cmn'] == 'xíng / Háng', 'a name reading comes last')

# 4. word frequency from syllable frequencies and a segmented corpus
F = {'học': 1e-3, 'sinh': 1e-3, 'quốc': 1e-4}
keys = ['học', 'sinh', 'học sinh', 'quốc']
est0 = freq.estimate(keys, F, [])
ok(abs(est0['học'] + est0['học sinh'] - 1e-3) < 1e-4, 'without a corpus a syllable is split by the prior')
est = freq.estimate(keys, F, ['học sinh'] * 50 + ['học'] * 5 + ['sinh'] * 5)
ok(est['học sinh'] > est['học'] and est['học sinh'] > est0['học sinh'],
   'a corpus that shows học mostly inside học sinh moves the count to học sinh')
ok('quốc' in est and est['quốc'] == freq.estimate(['quốc'], F, [])['quốc'], 'a word alone with its syllable keeps F')

# 5. the cutter test's scoring
import cutter_test  # noqa: E402
ref = [cutter_test.words_of_line('Tôi là học_sinh.')]
p_, r_, f_ = cutter_test.score([(ref[0], cutter_test.words_of_line('Tôi là học sinh.'))])[:3]
ok(p_ == 0.5 and abs(r_ - 2 / 3) < 1e-9, 'cutter score: precision 2 of 4 words, recall 2 of 3')
ok(cutter_test.words_of_tokens(['Tôi', 'là', 'học sinh', '.']) == ref[0], 'underthesea tokens become syllable lists')
d = cutter_test.disagreements(ref, [cutter_test.words_of_line('Tôi là học sinh.')], ref)
ok(d == [('học | sinh', 'học sinh', 'b joins more', 'b')], 'a disagreement is one stretch, with the reference side')
ok(len(cutter_test.load_reference()) == 200, 'the cutter reference has 200 sentences')

print(f'\n{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
