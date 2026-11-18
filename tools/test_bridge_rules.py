"""Tests of tools/bridge_rules.py, the measure of the syllabus's sound correspondences (`make test`).

  python3 -I tools/test_bridge_rules.py

No database: the syllable splitters, the tone readers, the rule kinds and measure() on hand-made items, including
the items whose readings disagree (left out of a rule, never counted as an exception).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge_rules as br  # noqa: E402

failures = []


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


# Hán-Việt initials: digraphs first, k / q / gh / ngh folded, gi before a consonant is g + i
for s, want in (('nghiệp', 'ng'), ('ngôn', 'ng'), ('nhân', 'nh'), ('kinh', 'c'), ('quốc', 'c'), ('cao', 'c'),
                ('gia', 'gi'), ('giáo', 'gi'), ('khách', 'kh'), ('phát', 'ph'), ('trung', 'tr'), ('chính', 'ch'),
                ('thư', 'th'), ('đông', 'đ'), ('dân', 'd'), ('việt', 'v'), ('ý', ''), ('ổn', '')):
    ok(br.hv_split(s)[0] == want, f'hv_split({s}) initial {want} (got {br.hv_split(s)[0]})')

# Chinese initials and tones
ok(br.split('cmn', 'zhōng') == ('zh', 'ong'), 'Mandarin zhōng = zh + ong')
ok(br.split('nan', 'tshù')[0] == 'tsh', 'Taigi tsh- before ts-')
ok(br.split('yue', 'gwok3') == ('gw', 'ok'), 'Cantonese gwok3 = gw + ok')
ok(br.split('cmn', 'ān') == ('', 'an'), 'Mandarin zero initial')
ok(br.tone('yue', 'naam4') == 4, 'Cantonese tone digit')
ok(br.tone('cmn', 'xué') == 2 and br.tone('cmn', 'shuǐ') == 3 and br.tone('cmn', 'de') == 0, 'Mandarin tone marks')
ok(br.tone('nan', 'ha̍k') == 8 and br.tone('nan', 'kok') == 4 and br.tone('nan', 'sim') == 1, 'Taigi checked and level')
ok(br.tone('nan', 'lâm') == 5 and br.tone('nan', 'pīng') == 7 and br.tone('nan', 'kám') == 2, 'Taigi marked tones')

# features of one item: Hán-Việt tone, coda, sonorant initial; a feature the readings disagree on is None
f = br.features({'ch': '南', 'hv': 'nam', 'yue': ['naam4'], 'nan': ['lâm'], 'cmn': ['nán']})
ok(f['ht'] == 'ngang' and f['son'] and f['coda'] == 'm' and f['yt'] == 4 and f['nt'] == 5, '南 nam features')
f = br.features({'ch': '行', 'hv': 'hành', 'yue': ['hang4', 'hong4'], 'nan': ['hîng'], 'cmn': ['xíng', 'háng']})
ok(f['yi'] == 'h' and f['yr'] is None and f['mi'] is None and f['mt'] == 2, 'disagreeing readings give None')

# kind(): the syllabus's thresholds
ok(br.kind('zh>vi', 80, 100) == 'rule' and br.kind('zh>vi', 79, 100) == 'tendency', '80 % is a rule, 79 % a tendency')
ok(br.kind('vi>zh', 60, 100) == 'tendency' and br.kind('vi>zh', 59, 100) == 'drop', '60 % is a tendency')
ok(br.kind('drop', 100, 100) == 'drop' and br.kind('zh>vi', 0, 0) == 'drop', 'a dropped or empty rule is dropped')

# every rule has a known direction and an id
ok(all(len(r) == 5 and r[1] in ('zh>vi', 'vi>zh', 'spell', 'drop') and r[0] for r in br.RULES), 'rules well formed')


def item(hi, mi, ni='', yi='', mt=1, yt=1):
    return {'ch': '?', 'hv': hi + 'a', 'hi': hi, 'mi': mi, 'ni': ni, 'yi': yi, 'mt': mt, 'yt': yt}


# measure(): hits, total, exceptions; an undetermined feature leaves the item out on either side of the rule
saved = br.RULES
try:
    br.RULES = [('T', 'zh>vi', 'ph ← Mandarin f-', br.MI('f'), br.HV('ph')),
                ('T', 'vi>zh', 'ph → Mandarin f-', br.HV('ph'), br.MI('f')),
                ('T', 'spell', 'd or gi: gi when Cantonese g-', *br._spell(('gi', 'd'), br.YI('g')))]
    fs = [item('ph', 'f'), item('b', 'f'), item('ph', None), item('ph', 'p'),
          item('gi', 'j', yi='g'), item('d', 'y', yi='j'), item('gi', 'j', yi=None), item('d', 'y', yi='g')]
    (_, _, _, h1, t1, e1), (_, _, _, h2, t2, e2), (_, _, _, h3, t3, e3) = br.measure(fs)
    ok((h1, t1) == (1, 2) and e1 == ['? ba'], f'forward rule 1 / 2 with exception b (got {h1}/{t1} {e1})')
    ok((h2, t2) == (1, 2), f'reverse rule 1 / 2, the undetermined Mandarin left out (got {h2}/{t2})')
    ok((h3, t3) == (2, 3), f'spelling rule 2 / 3, the undetermined Cantonese left out (got {h3}/{t3})')
finally:
    br.RULES = saved

print(f'{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
