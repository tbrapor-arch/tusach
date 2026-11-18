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
ALL_BUT_WIKTIONARY = 'wiktionary-tr,thieuchuu,unihan,rime,moe,cedict,tatoeba,tatoeba-challenge,frequencywords'


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
    ok(e.get('cà phê', ())[:3] == ('', 'loan', 'loan'), 'a borrowing is neither same nor native: a loan')
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
       and sung.get('other') == [{'en': 'to fill, to supplement', 'chars': '充'}] and sung.get('no_main') == 1,
       'sung "cluster fig" does not get 充: one etymology per card sense, the other listed apart; no corpus '
       'evidence: no main sense claimed')
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

# 2b. the Wiktionary loader on REAL lines of the snapshot (tools/fixtures/raw-real, CC BY-SA 4.0, see its README)
with tempfile.TemporaryDirectory() as tmp:
    db = os.path.join(tmp, 'vi.db')
    r = subprocess.run([sys.executable, '-I', 'tools/build_db.py', 'tools/fixtures/raw-real', db], cwd=ROOT,
                       capture_output=True, text=True, env=dict(os.environ, TUSACH_ALLOW_MISSING=ALL_BUT_WIKTIONARY))
    ok(r.returncode == 0, 'build_db reads the real kaikki lines')
    con = sqlite3.connect(db)
    e = {r[0]: r[1:] for r in con.execute("SELECT key, chars, origin, label, etymon, english FROM entry "
                                          "WHERE source='wiktionary'")}
    ok(e.get('học sinh', ())[:3] == ('學生', 'sino', 'same'), 'real: vi-etym-sino 1=學 2=gloss 3=生 4=gloss')
    ok(e.get('thế giới', ())[:1] == ('世界',), 'real: vi-etym-sino with the whole word in 1')
    ok(e.get('giấy', ())[:4] == ('', 'nonhv', 'older-loan', '紙 chỉ') and
       e.get('và', ())[:4] == ('', 'nonhv', 'older-loan', '和 hoà'),
       'real: "Non-Sino-Vietnamese reading" (hv=/preMC=) is a borrowing, not a Hán-Việt analysis; etymon kept')
    ok(e.get('câu lạc bộ', ())[:2] == ('俱樂部', 'sino'), 'real: an empty vi-etym-sino takes the borrowed characters')
    ok(e.get('nguyệt thực', ())[:1] == ('月食',), 'real: two vi-etym-sino (月食 / 月蝕) are alternatives, not joined')
    ok(e.get('học sinh', ('',) * 5)[4].startswith('a pupil'), 'real: an archaic sense ("a student") comes after')
    ok('misspelling' not in e.get('chuyện', ('',) * 5)[4], 'real: a "misspelling of" sense is not English')
    ok(not con.execute("SELECT 1 FROM entry WHERE key='y' AND pos != 'character-reading'").fetchone(),
       'real: "Sino-Vietnamese reading of 衣" is not a word (only a character-reading entry, tagged 衣)')
    hv = set(con.execute("SELECT char, reading, kind, label FROM hanviet WHERE source='wiktionary'"))
    ok(('衣', 'y', 'hv', 'romanization') in hv, 'real: ... it is a Hán-Việt reading of 衣')
    ok(('世', 'thế', 'hv', '') in hv and ('世', 'thá', 'nom', '') in hv, 'real: readings tagged inside senses[].related')
    ok(('車', 'xa', 'hannom', '') in hv and ('車', 'xe', 'hannom', '') in hv, 'real: untagged Hán-Nôm forms stay hannom')
    ok(('值', 'trị', 'hv', 'attested') in hv, 'real: a Hán-Nôm reading read so by a Sino-Vietnamese word (giá trị)')
    ok(('平', 'bằng', 'hv', 'attested') in hv, 'real: a Nôm reading read so by 2+ Sino-Vietnamese words (bằng, công bằng)')
    chk = dict(con.execute("SELECT key, hv_check FROM entry WHERE chars != '' AND source='wiktionary'"))
    ok(chk.get('bằng') == 'ok' and chk.get('học sinh') == 'ok', 'real: the check accepts the attested reading')
    import cards  # noqa: E402
    cards.init(cards.open_db('public', db), lex_rows=[])   # the dictionary layer alone
    lai, thich = (cards.dictionary[cards.lookup(k)] for k in ('lại', 'thích'))
    ok('chars' not in lai and lai['en'].startswith('once more') and thich.get('chars') == '適',
       'real: a card takes its characters from its own etymology (lại "again" not 賴 of the surname; thích 適 not 釋)')

# 2c. Tatoeba: lines that are not Vietnamese (real sentences of the snapshot: #451795 by GrizaLeono, #13958199 by
# TanukiKun, #8854364 by dotheduyet1999, #13594913 by leucammieuvu; CC BY 2.0 FR)
import build_db  # noqa: E402
ok(build_db.tatoeba_problem('Nenormalas havi la koron dekstraflanke.') == 'not Vietnamese'
   and build_db.tatoeba_problem('𤾓𢆥𥪞揆𠊛些').startswith('Han')
   and build_db.tatoeba_problem('Tôi thích golf.') == ''
   and build_db.tatoeba_problem('Laptop của tôi đang chạy Linux.') == '',
   'tatoeba: a line in another language or in chữ Nôm is refused; names and loans are kept')

# 3. the join: whole word first, else character by character with every reading, nothing chosen silently
con = sqlite3.connect(':memory:')
con.executescript(open(os.path.join(HERE, 'schema.sql'), encoding='utf-8').read())
con.execute("INSERT INTO source VALUES ('s', '', '', '', '', 1, 0)")
con.executemany("INSERT INTO chinese VALUES (?,?,?,'s',?,?,?,?,NULL)", [
    ('銀', 'yue', 'ngan4', 'char', None, '', 1), ('行', 'yue', 'hong4', 'char', 5, '', 2),
    ('行', 'yue', 'hang4', 'char', None, '', 1), ('行', 'yue', 'haang4', 'char', 5, '', 3),
    ('銀行', 'cmn', 'yínháng', 'word', None, '', 1), ('銀', 'cmn', 'yín', 'char', None, '', 1),
    ('行', 'cmn', 'Háng', 'char', None, 'name', 1), ('行', 'cmn', 'xíng', 'char', None, '', 2)])
con.executemany("INSERT INTO hanviet VALUES (?,?,'hv','s',?,NULL,'',0)", [('銀', 'ngân', 0), ('行', 'hành', 0), ('行', 'hàng', 1)])
j = bridge.join(con, '銀行')
ok(j['yue'] == 'ngan4 (hang4/hong4/haang4)' and j['yue_by'] == 'char',
   'built by character: every reading kept, main reading first, then by share')
ok(j['cmn'] == 'yínháng' and j['cmn_by'] == 'word', 'the whole word wins over the characters')
ok(j['nan'] == '' and j['nan_by'] == '' and j['n'] == 2, 'a missing language stays empty and is counted')
ok(j['hv'] == '銀 ngân · 行 hành/hàng', 'Hán-Việt readings per character')
ok(bridge.join(con, '行')['cmn'] == 'xíng', 'a surname reading is dropped when there are others')
ok('Háng' in bridge.join(con, '行', names=True)['cmn'], '… and kept for a name')

# 3a. a variant spelling (Unihan kSemanticVariant): Wiktionary's 行爲 finds CC-CEDICT's 行為, and says so; usage order
con.executemany("INSERT INTO variant VALUES (?,?)", [('爲', '為'), ('為', '爲')])
con.execute("INSERT INTO chinese VALUES ('行為', 'cmn', 'xíngwéi', 's', 'word', NULL, '', 1, NULL)")
j = bridge.join(con, '行爲')
ok(j['cmn'] == 'xíngwéi' and j['cmn_by'] == 'word' and j['via'] == '行為', 'a variant spelling finds the word, via 行為')
ok(bridge.join(con, '銀行')['via'] == '', 'no variant needed: via empty')
con.execute("UPDATE hanviet SET use=5 WHERE char='行' AND reading='hàng'")
ok(bridge.hv_readings(con, '行') == ['hàng', 'hành'], 'Hán-Việt readings: the one more Sino-Vietnamese words use first')
con.execute("UPDATE hanviet SET use=0")

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

# 3b'. MOE loader: a character's unmarked readings are used only when it has no literary one (rows copied from the
# MOE dictionary, 詞目總檔.csv, CC BY-ND 3.0 TW: 共 kā 0 / kiōng 1, 高 ko 0, 過 kò 1 / koh 0)
import build_db  # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    os.makedirs(os.path.join(tmp, 'moedict-data-twblg', 'uni'))
    open(os.path.join(tmp, 'moedict-data-twblg', 'uni', '詞目總檔.csv'), 'w', encoding='utf-8').write(
        '主編碼,屬性,詞目,音讀,文白屬性,部首\n1,1,共,kā,0,八\n2,1,共,kiōng,1,八\n3,1,高,ko,0,高\n4,1,過,kò,1,辵\n'
        '5,2,過,koh,0,辵\n')
    mc = sqlite3.connect(':memory:')
    mc.executescript(open(os.path.join(HERE, 'schema.sql'), encoding='utf-8').read())
    build_db.load_moe(tmp, build_db.Adder(mc, 'moe'))
    got = {(c, r) for c, r in mc.execute("SELECT chars, reading FROM chinese WHERE level='char'")}
    ok(got == {('共', 'kiōng'), ('高', 'ko'), ('過', 'kò')},
       'MOE: literary readings only when a character has one (共 kiōng, not kā); else the unmarked one (高 ko)')

# 3c. Hán-Việt: Northern first, Southern variant labelled, the Northern form derived where only a Southern one exists;
# the Unihan fallback; no silent "?"
import build_db  # noqa: E402
import hanviet  # noqa: E402
con.execute("INSERT INTO source VALUES ('thieuchuu', '', '', '', '', 1, 0)")
con.execute("INSERT INTO source VALUES ('unihan', '', '', '', '', 1, 0)")
con.executemany("INSERT INTO hanviet VALUES (?,?,'hv','thieuchuu',?,NULL,'',0)", [('生', 'sanh', 0), ('生', 'sinh', 1),
                                                                               ('政', 'chánh', 0), ('學', 'học', 0), ('日', 'nhật', 0)])
con.executemany("INSERT INTO hanviet VALUES (?,?,'unchecked','unihan',0,NULL,'',0)", [('一', 'nhất'), ('步', 'mắt')])
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


# 18 Nov 2026 (data quality): spelling groups, Taigi coda layers, sense tags
import build_db  # noqa: E402
import bridge as bridge_  # noqa: E402
ok(build_db.iy_key('lý do') == build_db.iy_key('lí do') and build_db.iy_key('quý') == 'quí'
   and build_db.iy_key('tuy') == 'tuy' and build_db.iy_key('ý') == 'ý', 'i/y spellings of one syllable are one key')
ok(not bridge_.coda_agrees(bridge_.coda_hv('sách'), bridge_.coda_nan('tsheh'))
   and not bridge_.coda_agrees(bridge_.coda_hv('viện'), bridge_.coda_nan('īnn'))
   and bridge_.coda_agrees(bridge_.coda_hv('phẩm'), bridge_.coda_nan('phín'))
   and bridge_.coda_agrees(bridge_.coda_hv('học'), bridge_.coda_nan('ha̍k')),
   'Taigi: -h / -nn readings are colloquial where Hán-Việt has a stop / nasal; m/n and p/t agree')
import cards as cards_  # noqa: E402
_rows = [{'source': 'w', 'src_id': '1', 'chars': '', 'origin': '', 'pos': 'num', 'english': 'five', 'id': 1},
         {'source': 'w', 'src_id': '2', 'chars': '', 'origin': '', 'pos': 'noun', 'english': 'year', 'id': 2}]
ok(cards_.sense_tag(_rows, 'year') is _rows[1] and cards_.sense_tag(_rows, 'num') is _rows[0]
   and cards_.sense_tag(_rows, 'cat') is None, 'a sense tag names a part of speech or a word of one etymology')

print(f'\n{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
