"""Tests of tools/bridge_rules.py, the measure of the syllabus's sound correspondences (`make test`).

  python3 -I tools/test_bridge_rules.py

No database: the syllable splitters, the tone readers, the learner-side conditions, the changed-tone rule, the main /
strict / lenient rates, the best single guess and the rule kinds, on hand-made items (review 3, findings 2 and 3).
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

# features: the Chinese side's own sonorant initial and checked final (what the learner has)
f = br.features({'ch': '南', 'hv': 'nam', 'yue': ['naam4'], 'nan': ['lâm'], 'cmn': ['nán']})
ok(f['ht'] == 'ngang' and f['yson'] and f['nson'] and f['mson'] and f['ychk'] is False and f['yt'] == 4, '南 features')
f = br.features({'ch': '形', 'hv': 'hình', 'yue': ['jing4'], 'nan': ['hîng'], 'cmn': ['xíng']})
ok(f['yson'] and not f['nson'] and f['son'] is False, '形 hình: Cantonese j- counts as sonorant, Taigi h- does not')
f = br.features({'ch': '行', 'hv': 'hành', 'yue': ['hang4', 'hong4'], 'nan': ['hîng'], 'cmn': ['xíng', 'háng']})
ok(f['yi'] == 'h' and f['yr'] is None and f['mi'] is None and f['mt'] == 2, 'disagreeing readings give None')

# the tone prediction from Cantonese / Taigi alone (review 3: no Vietnamese initial in a zh>vi condition)
for hv, yue, nan, want_y, want_n in (('nam', 'naam4', 'lâm', 'ngang', 'ngang'), ('trà', 'caa4', 'tsâ', 'huyền', 'huyền'),
                                     ('mã', 'maa5', 'bé', 'ngã', 'ngã'), ('cảm', 'gam2', 'kám', 'hỏi', 'hỏi'),
                                     ('động', 'dung6', 'tōng', 'nặng', 'nặng'), ('học', 'hok6', 'ha̍k', 'nặng', 'nặng'),
                                     ('quốc', 'gwok3', 'kok', 'sắc', 'sắc'), ('hình', 'jing4', 'hîng', 'ngang', 'huyền')):
    f = br.features({'ch': '?', 'hv': hv, 'yue': [yue], 'nan': [nan], 'cmn': []})
    ok(br.yue_tone(f) == want_y and br.nan_tone(f) == want_n, f'{hv}: {want_y} from {yue}, {want_n} from {nan} '
                                                             f'(got {br.yue_tone(f)}, {br.nan_tone(f)})')

# changed tones: tone 2 beside a low tone of the same syllable is the 變音; beside tone 3 it is a word of its own
ok(br.changed_tone('cin2', ['cin2', 'cin4', 'zin2']) == 'cin4', '錢 cin2 is a changed tone of cin4 (whatever the order)')
ok(br.changed_tone('wui2', ['wui6', 'wui5', 'wui2']) == 'wui6', '會 wui2 -> wui6')
ok(br.changed_tone('hou2', ['hou2', 'hou3']) is None, '好 hou2 / hou3: not a changed tone')
ok(br.changed_tone('cin4', ['cin4', 'cin2']) is None, 'a low tone is never a changed tone')

# kind(): the thresholds on the main rate; a set of outcomes whose best single guess is under 60 % "narrows"
ok(br.kind('zh>vi', 80, 100) == 'rule' and br.kind('zh>vi', 79, 100) == 'tendency', '80 % is a rule, 79 % a tendency')
ok(br.kind('vi>zh', 60, 100) == 'tendency' and br.kind('vi>zh', 59, 100) == 'drop', '60 % is a tendency')
ok(br.kind('drop', 100, 100) == 'drop' and br.kind('zh>vi', 0, 0) == 'drop', 'a dropped or empty rule is dropped')
ok(br.kind('zh>vi', 94, 100, ('tr', 49)) == 'narrows' and br.kind('zh>vi', 94, 100, ('th', 76)) == 'rule',
   'ch or tr ← zh- (tr 49 %) narrows; th or s ← sh- (th 76 %) is a rule with th as the guess')
ok(br.kind('fact', 166, 166) == 'fact', '-p -t -c -ch → sắc / nặng is a fact of spelling, not a rule')

# every rule is well formed; no zh>vi condition reads a Vietnamese feature (circularity, review 3 finding 3)
ok(all(len(r) == 7 and r[1] in ('zh>vi', 'vi>zh', 'spell', 'fact', 'drop') and r[0] and r[2] for r in br.RULES),
   'rules well formed')
probe = br.features({'ch': '?', 'hv': 'nam', 'yue': ['naam4'], 'nan': ['lâm'], 'cmn': ['nán']})
leaks = []
for rid, way, _, text, cond, _, _ in br.RULES:
    if way != 'zh>vi':
        continue
    for k in ('hi', 'son', 'coda', 'chk', 'ht', 'front'):
        g = dict(probe)
        g[k] = {'hi': 'zz', 'son': not probe['son'], 'coda': 'zz', 'chk': not probe['chk'], 'ht': 'zz',
                'front': not probe['front']}[k]
        if br._ev(cond, g) != br._ev(cond, probe):
            leaks.append(f'{text} reads {k}')
ok(not leaks, 'no zh>vi condition depends on the Vietnamese syllable' + (f': {leaks}' if leaks else ''))


# measure(): main, strict and lenient rates and the best single guess on hand-made items
def item(hv, yue, cmn, nan=None, main=None):
    d = {'ch': hv[:1], 'hv': hv, 'words': [hv], 'yue': yue, 'cmn': cmn, 'nan': nan or [],
         'yue_main': (main or yue)[0], 'cmn_main': cmn[0] if cmn else None, 'nan_main': (nan or [None])[0],
         'yue_changed': False}
    return d


saved = br.RULES
try:
    br.RULES = [('T2', 'zh>vi', 'g', 'Cantonese 2 → hỏi', br._all(br.YOPEN, br.YT(2)), br.HT('hỏi'), None),
                ('IR', 'zh>vi', 'g', 'ch or tr ← Mandarin zh-', br.MI('zh'), br.HV('ch', 'tr'), 'hi')]
    data = [item('cảm', ['gam2'], ['gǎn']),
            item('tiền', ['cin2', 'cin4'], ['qián'], main=['cin4']),    # changed tone: main cin4, out of the rule
            item('hội', ['wui2', 'wui6'], ['huì']),                      # main wui2 (no base given): an exception
            item('trung', ['zung1'], ['zhōng']), item('chủ', ['zyu2'], ['zhǔ']), item('chính', ['zing3'], ['zhèng']),
            item('sạn', ['zaan6'], ['zhàn'])]
    t2, ir = br.measure(data)
    ok((t2['hit'], t2['tot']) == (2, 3), f"main: 錢 counted with its base tone, 會 wui2 an exception (got "
                                         f"{t2['hit']}/{t2['tot']})")
    ok(t2['strict'] == (2, 4) and t2['lenient'] == (2, 4), f"strict and lenient count every reading (got "
                                                           f"{t2['strict']} {t2['lenient']})")
    ok((ir['hit'], ir['tot']) == (3, 4) and ir['best'] == ('ch', 2), f"ch or tr ← zh-: 3 / 4, best single guess ch 2 "
                                                                     f"(got {ir['hit']}/{ir['tot']} {ir['best']})")
finally:
    br.RULES = saved

# the proposal's tables are rewritten between markers, nothing else
text = 'a\n<!-- rules:x -->\nold\n<!-- /rules -->\nb'
ok(br.rewrite(text, {'x': 'new'}) == 'a\n<!-- rules:x -->\nnew\n<!-- /rules -->\nb', 'rewrite() replaces a block only')

print(f'{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
