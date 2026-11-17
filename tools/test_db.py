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
import json  # noqa: F401

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
    ok('quốc' in e and 'ken' not in e and '馬' not in e and 'dog' not in e,
       'keeps a glossless Sino-Vietnamese entry; drops empty stubs, Han-character headwords and other languages')
    hv = set(con.execute("SELECT char, reading, kind FROM hanviet WHERE source='wiktionary'"))
    ok(('學', 'học', 'hv') in hv and ('學', 'học', 'nom') in hv and ('犭', 'khuyển', 'hannom') in hv
       and ('生', 'sinh', 'hv') in hv, 'character readings kept apart: Hán-Việt, Nôm, Hán-Nôm')
    ok(con.execute("SELECT count(*) FROM example WHERE source='wiktionary'").fetchone()[0] == 2,
       "Wiktionary's examples (english or translation) are kept")
    ok(dict(con.execute("SELECT key, hv_check FROM entry WHERE source='wiktionary' AND chars != ''")).get('học sinh') == 'ok',
       'the Hán-Việt check of học sinh is ok')
    # homographs: the card's English, characters and label come from one etymology (finding 8)
    import cards  # noqa: E402
    cards.init(cards.open_db('public', db))
    sung = cards.dictionary[cards.lookup('sung')]
    ok(sung['en'] == 'cluster fig (Ficus racemosa)' and 'chars' not in sung and sung.get('label') == 'native'
       and sung.get('other') == [{'en': 'to fill; to supplement', 'chars': '充'}],
       'sung "cluster fig" does not get 充: one etymology per card sense, the other listed apart')
    sh = cards.dictionary[cards.lookup('sinh học')]
    ok('chars' not in sh and sh.get('label') != 'same', 'an analysis not matching the syllables is not shown as same word')
    chk = dict(con.execute("SELECT key, hv_check FROM entry WHERE source='wiktionary' AND chars != ''"))
    ok(chk.get('sinh học') == 'differs' and chk.get('học') == 'length', 'hv_check: differs, length')
    r = subprocess.run([sys.executable, '-I', 'tools/verify_words.py', '--lessons', '--db', db], cwd=ROOT,
                       capture_output=True, text=True)
    ok('sinh học 學生' in r.stdout and 'học 學生' in r.stdout, 'make lint (verify_words) prints them as suspects')
    b = dict((r[0], r[1:]) for r in con.execute('SELECT chars, n, yue FROM bridge'))
    ok(b.get('學生', (0,))[0] == 3 and b.get('大學', (9,))[0] == 0,
       'bridge: 學生 has three readings (fixture), 大學 none (no Chinese source fetched)')

# 3. the join: whole word first, else character by character with every reading, nothing chosen silently
con = sqlite3.connect(':memory:')
con.executescript(open(os.path.join(HERE, 'schema.sql'), encoding='utf-8').read())
con.execute("INSERT INTO source VALUES ('s', '', '', '', '', 1, 0)")
con.executemany("INSERT INTO chinese VALUES (?,?,?,'s',?,?,?,?,NULL)", [
    ('銀', 'yue', 'ngan4', 'char', None, '', 1), ('行', 'yue', 'hong4', 'char', 5, '', 2),
    ('行', 'yue', 'hang4', 'char', None, '', 1), ('行', 'yue', 'haang4', 'char', 5, '', 3),
    ('銀行', 'cmn', 'yínháng', 'word', None, '', 1), ('銀', 'cmn', 'yín', 'char', None, '', 1),
    ('行', 'cmn', 'Háng', 'char', None, 'name', 1), ('行', 'cmn', 'xíng', 'char', None, '', 2)])
con.executemany("INSERT INTO hanviet VALUES (?,?,'hv','s',?,NULL,'')", [('銀', 'ngân', 0), ('行', 'hành', 0), ('行', 'hàng', 1)])
j = bridge.join(con, '銀行')
ok(j['yue'] == 'ngan4 (hang4/hong4/haang4)' and j['yue_by'] == 'char',
   'built by character: every reading kept, main reading first, then by share')
ok(j['cmn'] == 'yínháng' and j['cmn_by'] == 'word', 'the whole word wins over the characters')
ok(j['nan'] == '' and j['nan_by'] == '' and j['n'] == 2, 'a missing language stays empty and is counted')
ok(j['hv'] == '銀 ngân · 行 hành/hàng', 'Hán-Việt readings per character')
ok(bridge.join(con, '行')['cmn'] == 'xíng', 'a surname reading is dropped when there are others')
ok('Háng' in bridge.join(con, '行', names=True)['cmn'], '… and kept for a name')

# 3b. Taigi: the literary reading composed from the characters; the MOE word reading, if different, is colloquial
con.executemany("INSERT INTO chinese VALUES (?,'nan',?,'s',?,NULL,?,?,NULL)", [
    ('生', 'sing', 'char', 'literary', 1), ('日', 'ji̍t', 'char', 'unmarked', 1), ('日', 'li̍t', 'char', 'unmarked', 2),
    ('生日', 'senn-ji̍t', 'word', '', 1), ('生日', 'sinn-li̍t', 'word', '', 2), ('先', 'sian', 'char', 'literary', 1),
    ('先生', 'sian-sinn', 'word', '', 1), ('學', 'ha̍k', 'char', 'literary', 1), ('學生', 'ha̍k-sing', 'word', '', 1)])
j = bridge.join(con, '生日')
ok(j['nan'] == 'sing-(ji̍t/li̍t)' and j['nan_by'] == 'char' and j['nan_coll'] == 'senn-ji̍t / sinn-li̍t',
   'Taigi 生日: literary sing-ji̍t composed, senn-ji̍t only as colloquial / everyday')
j = bridge.join(con, '先生')
ok(j['nan'] == 'sian-sing' and j['nan_coll'] == 'sian-sinn', 'Taigi 先生: sian-sinn is never shown as literary')
j = bridge.join(con, '學生')
ok(j['nan'] == 'ha̍k-sing' and j['nan_by'] == 'word' and j['nan_coll'] == '', 'Taigi 學生: the word reading attests the literary one')

# 3c. Hán-Việt: Northern first, Southern variant labelled, the Northern form derived where only a Southern one exists;
# the Unihan fallback; no silent "?"
import build_db  # noqa: E402
import hanviet  # noqa: E402
con.execute("INSERT INTO source VALUES ('thieuchuu', '', '', '', '', 1, 0)")
con.execute("INSERT INTO source VALUES ('unihan', '', '', '', '', 1, 0)")
con.executemany("INSERT INTO hanviet VALUES (?,?,'hv','thieuchuu',?,NULL,'')", [('生', 'sanh', 0), ('生', 'sinh', 1),
                                                                               ('政', 'chánh', 0), ('學', 'học', 0), ('日', 'nhật', 0)])
con.executemany("INSERT INTO hanviet VALUES (?,?,'unchecked','unihan',0,NULL,'')", [('一', 'nhất'), ('步', 'mắt')])
con.executemany("INSERT INTO chinese VALUES (?,'cmn',?,'s','char',NULL,'',1,NULL)", [('生', 'shēng'), ('政', 'zhèng')])
aff = build_db.southern_variants(con)
build_db.unihan_fallback(con)
ok(sorted((c, how) for c, _, _, how in aff) == [('政', 'derived'), ('生', 'both given')], 'Southern variants found by rule')
ok(bridge.hv_text(con, '生') == '生 sinh/sanh (Southern variant)', 'Northern sinh first, sanh labelled Southern variant')
ok(bridge.hv_text(con, '政') == '政 chính (derived)/chánh (Southern variant)', '政: chính derived, labelled')
ok(bridge.hv_text(con, '一') == '一 nhất (unchecked, Unihan)', 'a character no Hán-Việt source reads: Unihan, labelled')
ok(bridge.hv_text(con, '步') == '步 — (no Hán-Việt reading)' and bridge.join(con, '步')['hv_missing'] == ['步'],
   'a Nôm-shaped Unihan reading is not used; no reading is said, never "?"')
ok(build_db.thieuchuu_head('đại (5 n)<br>x') == ['đại'] and build_db.thieuchuu_head('tạo|tháo (11 n)<br>') == ['tạo', 'tháo']
   and build_db.thieuchuu_head('nảm.<br>') == ['nảm'], 'Thiều Chửu heads with a stroke count or a full stop are read')

# 3d. Mandarin: traditional forms only, names, the order, apostrophe, syllabic nasals
ok(bridge.pinyin_marks('nu:3 er2') == "nǚ'ér" and bridge.pinyin_marks('Xi1 an1') == "Xī'ān", 'pinyin keeps the apostrophe')
ok(bridge.pinyin_marks('m2') == 'ḿ' and bridge.pinyin_marks('ng2') == 'ńg' and bridge.pinyin_marks('n4') == 'ǹ',
   'pinyin: the tone of syllabic m, n, ng')
with tempfile.TemporaryDirectory() as tmp:
    os.makedirs(os.path.join(tmp, 'cedict', 'package'))
    import json  # noqa: E402
    json.dump([{'traditional': '隻', 'simplified': '只', 'pinyin': 'zhi1'}, {'traditional': '只', 'simplified': '只', 'pinyin': 'zhi3'},
               {'traditional': '了', 'simplified': '了', 'pinyin': 'liao3'}, {'traditional': '了', 'simplified': '了', 'pinyin': 'le5'},
               {'traditional': '了解', 'simplified': '了解', 'pinyin': 'liao3 jie3'}, {'traditional': '單', 'simplified': '单', 'pinyin': 'Shan4'},
               {'traditional': '單', 'simplified': '单', 'pinyin': 'dan1'}],
              open(os.path.join(tmp, 'cedict', 'package', 'cedict.json'), 'w'))
    c2 = sqlite3.connect(':memory:')
    c2.executescript(open(os.path.join(HERE, 'schema.sql'), encoding='utf-8').read())
    c2.execute("INSERT INTO source VALUES ('cedict', '', '', '', '', 1, 0)")
    build_db.load_cedict(tmp, build_db.Adder(c2, 'cedict'))
    c2.execute("INSERT INTO mandarin_pref VALUES ('了', 'le', 0)")
    build_db.rank_chinese(c2)
    ok(bridge.join(c2, '只')['cmn'] == 'zhǐ', '只 is not given 隻\'s zhī (no simplified form merged)')
    ok(bridge.join(c2, '了')['cmn'] == 'le / liǎo', "Unihan kMandarin's reading first: 了 le, then liǎo")
    ok(bridge.join(c2, '單')['cmn'] == 'dān', 'a surname reading is not the main reading')
    order1 = c2.execute('SELECT chars, reading, rank FROM chinese ORDER BY rowid').fetchall()
    build_db.rank_chinese(c2)
    ok(order1 == c2.execute('SELECT chars, reading, rank FROM chinese ORDER BY rowid').fetchall(), 'the order is deterministic')

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

# 6. licences and the one cutter (findings 11, 12, 13)
import build_db  # noqa: E402,F811
src = {x['id']: x for x in build_db.SOURCES}
ok(src['tatoeba-challenge']['commercial_ok'] is False, 'the Tatoeba Challenge copy is commercial_ok False (private build only)')
pub = os.path.join(ROOT, 'data/build/vi.db')
if os.path.exists(pub):
    m = dict(sqlite3.connect(pub).execute('SELECT key, value FROM meta'))
    ok('tatoeba-challenge' not in (m.get('sources') or '').split(), 'the public database has nothing from it')
ref_text = {c.replace('_', ' ') for _, c in cutter_test.load_reference()}
ch = os.path.join(ROOT, 'data/raw/tatoeba-challenge/eng-vie-test.txt')
if os.path.exists(ch):
    chs = {x.rstrip('\n').split('\t')[3] for x in open(ch, encoding='utf-8') if x.count('\t') >= 3}
    ok(not (ref_text & chs), 'no cutter reference sentence comes from the Tatoeba Challenge copy')
head = open(cutter_test.REF, encoding='utf-8').read(800)
ok('WRITTEN AND CUT BY CLAUDE, NOT CHECKED BY A NATIVE SPEAKER' in head, 'the reference says who wrote and cut it')
ok(freq.segmenter({'học sinh'})[1].startswith('tools/vi.py cut()') and freq.segmenter({'học sinh'})[0]('Tôi là học sinh.')
   == ['tôi', 'là', 'học sinh'], 'the frequency counts use the project\'s own cutter, not underthesea')

print(f'\n{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
