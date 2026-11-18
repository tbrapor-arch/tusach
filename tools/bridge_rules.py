"""Measure the sound correspondences the syllabus teaches (course/proposal/syllabus-proposal.md, bridge strand) against
the cards, and check the bridge-note examples of the proposal with lint's bridge-note test.

    python3 -I tools/bridge_rules.py                 # every rule: hits / total, %, main exceptions (markdown table)
    python3 -I tools/bridge_rules.py --examples FILE # the chữ Hán between <!-- bridge-examples --> and
                                                     # <!-- /bridge-examples --> in FILE, each through lint's test

The data: every key of rank <= 3,000 whose card (tools/cards.py lookup: the course lexicon, else the main etymology)
is Hán-Việt (label same, gram, hv-vn, opaque, false-friend); each distinct (character, Hán-Việt syllable) of these
cards is one item. A Chinese reading is the word's own reading when the source has the word (Cantonese, Mandarin;
Taigi only when it is one of the character's literary readings), else every reading of the character; a feature
(initial, rhyme, tone) counts only when all candidate readings agree on it, else the item is left out of that rule.
A rule's total is the items its condition covers (an item whose prediction cannot be judged, its readings
disagreeing, is left out); kind(): a rule at 80 % or more is taught as a rule, from 60 % as a tendency, else not.
Each rule has a direction: zh>vi (from the Chinese word he knows to the Vietnamese), vi>zh (from the Vietnamese
heard or read to the Chinese), spell (writing a sound Hà Nội merges), drop (the first proposal's, not taught).
"""
import collections
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cards  # noqa: E402
import vi  # noqa: E402

TOP = 3000
LABELS = ('same', 'gram', 'hv-vn', 'opaque', 'false-friend')


def _marks_off(s, keep=''):
    d = unicodedata.normalize('NFD', s.lower())
    return unicodedata.normalize('NFC', ''.join(c for c in d if unicodedata.category(c) != 'Mn' or c in keep))


def readings(con, ch, lang):
    rs = con.execute("SELECT reading, note FROM chinese WHERE chars=? AND lang=? AND level='char' AND source!='fixture' "
                     "ORDER BY ord", (ch, lang)).fetchall()
    if lang == 'nan':
        lit = [r for r, n in rs if n == 'literary']
        return lit or [r for r, n in rs if 'colloquial' not in (n or '')]
    return [r for r, _ in rs]


def _split_pinyin(con, word, chars):
    w, out, pos = word.replace("'", '').replace(' ', ''), [], 0
    for ch in chars:
        for r in sorted(set(readings(con, ch, 'cmn')), key=len, reverse=True):
            seg = w[pos:pos + len(r)]
            if _marks_off(seg, '̈') == _marks_off(r, '̈'):
                out.append(seg)
                pos += len(seg)
                break
        else:
            return None
    return out if pos == len(w) else None


def candidates(con, ch, i, chars, lang):
    rs = readings(con, ch, lang)
    if not rs:
        return []
    if len(chars) > 1:
        wr = con.execute("SELECT reading FROM chinese WHERE chars=? AND lang=? AND level='word' AND source!='fixture' "
                         "ORDER BY ord", (chars, lang)).fetchone()
        if wr:
            wr = wr[0]
            parts = wr.split() if lang == 'yue' else re.split(r'[- ]', wr) if lang == 'nan' else \
                _split_pinyin(con, wr, chars)
            if parts and len(parts) == len(chars):
                p = parts[i].lower()
                if lang == 'nan' and p in [x.lower() for x in rs]:
                    return [p]
                if lang == 'cmn' and any(_marks_off(x, '̈') == _marks_off(p, '̈') for x in rs):
                    return [p]
                if lang == 'yue' and p in rs:
                    return [p]
    return [x.lower() for x in dict.fromkeys(rs)]


def items(con):
    """[{ch, hv, yue: [..], nan: [..], cmn: [..], words}] (see the module docstring)."""
    cards.init(con)
    seen = {}
    for (k,) in con.execute("SELECT DISTINCT key FROM entry WHERE freq_rank<=? AND source!='fixture' ORDER BY freq_rank",
                            (TOP,)):
        cid = cards.lookup(k)
        c = cards.dictionary.get(cid) if cid else None
        if not c or not c.get('chars') or c.get('label') not in LABELS or len(k.split()) != len(c['chars']):
            continue
        for i, (s, ch) in enumerate(zip(k.split(), c['chars'])):
            if (ch, s) in seen:
                seen[(ch, s)]['words'].append(k)
                continue
            seen[(ch, s)] = {'ch': ch, 'hv': s, 'words': [k],
                             **{lang: candidates(con, ch, i, c['chars'], lang) for lang in ('yue', 'nan', 'cmn')}}
    return list(seen.values())


# --- features -------------------------------------------------------------------------------------------------------
HV_ON = ('ngh', 'ng', 'nh', 'ch', 'tr', 'th', 'ph', 'kh', 'gh', 'gi', 'qu', 'đ', 'd', 'b', 'c', 'k', 'g', 'h', 'l', 'm',
         'n', 'r', 's', 't', 'v', 'x')
ON = {'yue': ('gw', 'kw', 'ng', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'w', 'z', 'c', 's', 'j'),
      'nan': ('tsh', 'ts', 'ph', 'th', 'kh', 'ng', 'p', 'b', 'm', 't', 'n', 'l', 'k', 'g', 'h', 'j', 's'),
      'cmn': ('zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's',
              'y', 'w')}
SON = {'m', 'n', 'nh', 'ng', 'l', 'v', 'd'}     # Hán-Việt initials from old sonorants (m n ŋ l ɲ, 微 云 以 日)
TONE = {1: 'ngang', 2: 'huyền', 3: 'sắc', 4: 'hỏi', 5: 'ngã', 6: 'nặng'}


def hv_split(s):
    b = _marks_off(s, '̛̆̂')
    for o in HV_ON:
        if b.startswith(o):
            rest = b[len(o):]
            if o == 'gi' and rest and rest[0] not in 'aăâeêioôơuưy':
                return 'g', b[1:]
            return {'k': 'c', 'gh': 'g', 'ngh': 'ng', 'qu': 'c'}.get(o, o), rest
    return '', b


def split(lang, r):
    s = re.sub(r'\d', '', r) if lang == 'yue' else _marks_off(r).replace('ü', 'v')
    for o in ON[lang]:
        if s.startswith(o):
            return o, s[len(o):]
    return '', s


def tone(lang, r):
    if lang == 'yue':
        m = re.search(r'\d', r)
        return int(m.group()) if m else None
    d = unicodedata.normalize('NFD', r)
    if lang == 'cmn':
        return next((t for m, t in (('̄', 1), ('́', 2), ('̌', 3), ('̀', 4)) if m in d), 0)
    for m, t in (('̍', 8), ('́', 2), ('̀', 3), ('̂', 5), ('̄', 7), ('̌', 6)):
        if m in d:
            return t
    return 4 if _marks_off(r)[-1:] in 'ptkh' else 1


def features(d):
    f = {'ch': d['ch'], 'hv': d['hv']}
    f['hi'], f['hr'] = hv_split(d['hv'])
    f['ht'] = TONE[vi.tone(d['hv'])]
    m = re.search(r'(nh|ng|ch|p|t|c|m|n)$', _marks_off(d['hv'], '̛̆̂'))
    f['coda'] = m.group(1) if m else ''
    f['chk'] = f['coda'] in ('p', 't', 'c', 'ch')
    f['son'] = f['hi'] in SON
    for lang, p in (('yue', 'y'), ('nan', 'n'), ('cmn', 'm')):
        rs = d.get(lang) or []
        for name, fn in (('i', lambda r: split(lang, r)[0]), ('r', lambda r: split(lang, r)[1]),
                         ('t', lambda r: tone(lang, r))):
            vals = {fn(r) for r in rs}
            f[p + name] = vals.pop() if len(vals) == 1 else None
    return f


def yue_coda(f):
    m = re.search(r'(ng|p|t|k|m|n)$', f['yr'])
    return m.group(1) if m else ''


def yue_tone(f):
    """The Hán-Việt tone the T rules predict from the Cantonese tone (and the Vietnamese initial's class)."""
    t = f['yt']
    if f['chk']:
        return 'sắc' if t in (1, 3) else 'nặng'
    return {1: 'ngang', 2: 'hỏi', 3: 'sắc', 6: 'nặng', 4: 'ngang' if f['son'] else 'huyền',
            5: 'ngã' if f['son'] else 'nặng'}.get(t)


def nan_tone(f):
    """The Hán-Việt tone the T rules predict from the Taigi literary tone (and the Vietnamese initial's class)."""
    t = f['nt']
    return {1: 'ngang', 3: 'sắc', 4: 'sắc', 7: 'nặng', 8: 'nặng', 5: 'ngang' if f['son'] else 'huyền',
            2: 'ngã' if f['son'] else 'hỏi', 6: 'nặng'}.get(t)


JING = lambda f: f['mi'] in ('z', 'c', 's', 'j', 'q', 'x') and f['yi'] in ('z', 'c', 's')   # noqa: E731 精 series
OPEN = lambda f: not f['chk']                                                                # noqa: E731
ASP = ('ph', 'th', 'kh', 'x', 's')                 # Hán-Việt letters from old aspirates (and the 章 / 莊 fricatives)
UNASP = ('b', 'đ', 'c', 't', 'tr', 'ch', 'gi')     # Hán-Việt letters from old plain or voiced stops and affricates


def _is(key, *vals):
    """f[key] in vals; None when the feature is undetermined (the readings disagree or are missing): measure() then
    leaves the item out of the rule."""
    return lambda f: None if f[key] is None else f[key] in vals


def _known(key):
    return lambda f: None if f[key] is None else True


def _all(*fns):
    def test(f):
        vals = [g(f) for g in fns]
        return None if None in vals else all(vals)
    return test


def _spell(pair, test):
    """A spelling rule for two letters Hà Nội pronounces alike: among the syllables spelt with either, the first letter
    is written exactly when `test` holds."""
    return lambda f: f['hi'] in pair, lambda f: None if test(f) is None else (f['hi'] == pair[0]) == bool(test(f))


HV, YI, NI, MI = (lambda *v: _is('hi', *v)), (lambda *v: _is('yi', *v)), (lambda *v: _is('ni', *v)), \
    (lambda *v: _is('mi', *v))
YT, MT = (lambda *v: _is('yt', *v)), (lambda *v: _is('mt', *v))

# Directions: 'zh>vi' guess the Vietnamese from the Chinese word he knows; 'vi>zh' find the Chinese word from the
# Vietnamese he hears or reads; 'spell' write a sound Hà Nội merges (d / gi / r, tr / ch, s / x) from the Chinese;
# 'drop' a rule of the first proposal, measured and not taught.
# (id, direction, rule as taught, condition, prediction). Ids are the syllabus's.
RULES = [
    ('B1', 'zh>vi', 'Cantonese -p → -p', lambda f: yue_coda(f) == 'p', lambda f: f['coda'] == 'p'),
    ('B1', 'zh>vi', 'Cantonese -t → -t', lambda f: yue_coda(f) == 't', lambda f: f['coda'] == 't'),
    ('B1', 'zh>vi', 'Cantonese -k → -c / -ch', lambda f: yue_coda(f) == 'k', lambda f: f['coda'] in ('c', 'ch')),
    ('B2', 'zh>vi', 'Cantonese -m → -m', lambda f: yue_coda(f) == 'm', lambda f: f['coda'] == 'm'),
    ('B2', 'zh>vi', 'Taigi -m → -m', lambda f: re.search('m$', f['nr']) is not None and not f['nr'].endswith('nn'),
     lambda f: f['coda'] == 'm'),
    ('B3', 'vi>zh', 'Hán-Việt -nh / -ch ← Cantonese -ng / -k', lambda f: f['coda'] in ('nh', 'ch') and f['yr'] is not None,
     lambda f: yue_coda(f) in ('ng', 'k')),
    ('B3', 'zh>vi', 'Mandarin -ing → -nh (-ưng / -ăng for some)', lambda f: f['mr'] == 'ing',
     lambda f: f['coda'] == 'nh'),
    ('B3x', 'drop', 'Cantonese -ing / -ik → -nh / -ch', lambda f: f['yr'] in ('ing', 'ik'),
     lambda f: f['coda'] in ('nh', 'ch')),
    ('V1', 'zh>vi', 'Cantonese -oeng / -oek → -ương / -ươc', lambda f: f['yr'] in ('oeng', 'oek'),
     lambda f: 'ươ' in f['hr']),
    ('V2', 'zh>vi', 'Cantonese -in / -it → -iên / -iêt', lambda f: f['yr'] in ('in', 'it'),
     lambda f: 'iê' in f['hr'] or 'yê' in f['hr']),
    ('T1', 'zh>vi', 'Cantonese 1 (open syllable) → ngang', lambda f: OPEN(f) and f['yt'] == 1,
     lambda f: f['ht'] == 'ngang'),
    ('T1', 'zh>vi', 'Cantonese 4, obstruent initial → huyền',
     lambda f: OPEN(f) and f['yt'] == 4 and not f['son'] and f['hi'], lambda f: f['ht'] == 'huyền'),
    ('T1', 'zh>vi', 'Cantonese 4, sonorant initial (m n nh ng l v d) → ngang',
     lambda f: OPEN(f) and f['yt'] == 4 and f['son'], lambda f: f['ht'] == 'ngang'),
    ('T1', 'zh>vi', 'Taigi 5, sonorant initial → ngang', lambda f: OPEN(f) and f['nt'] == 5 and f['son'],
     lambda f: f['ht'] == 'ngang'),
    ('T1x', 'drop', 'Cantonese 4 → huyền, whatever the initial (first proposal)', lambda f: OPEN(f) and f['yt'] == 4,
     lambda f: f['ht'] == 'huyền'),
    ('T1', 'zh>vi', 'Taigi 1 (open syllable) → ngang', lambda f: OPEN(f) and f['nt'] == 1, lambda f: f['ht'] == 'ngang'),
    ('T1', 'zh>vi', 'Taigi 5, obstruent or no initial → huyền', lambda f: OPEN(f) and f['nt'] == 5 and not f['son'],
     lambda f: f['ht'] == 'huyền'),
    ('T1', 'zh>vi', 'Mandarin 1 (open syllable) → ngang', lambda f: OPEN(f) and f['mt'] == 1, lambda f: f['ht'] == 'ngang'),
    ('T1', 'zh>vi', 'Mandarin 2, obstruent or no initial (open) → huyền', lambda f: OPEN(f) and f['mt'] == 2 and not f['son'],
     lambda f: f['ht'] == 'huyền'),
    ('T1', 'vi>zh', 'huyền → Cantonese 4', lambda f: f['ht'] == 'huyền', YT(4)),
    ('T1', 'vi>zh', 'ngang → Cantonese 1, or 4 after m n nh ng l v d', lambda f: f['ht'] == 'ngang',
     lambda f: None if f['yt'] is None else f['yt'] == 1 or (f['yt'] == 4 and f['son'])),
    ('T2', 'zh>vi', 'Cantonese 2 → hỏi', lambda f: OPEN(f) and f['yt'] == 2, lambda f: f['ht'] == 'hỏi'),
    ('T2', 'zh>vi', 'Cantonese 5, sonorant initial → ngã', lambda f: OPEN(f) and f['yt'] == 5 and f['son'],
     lambda f: f['ht'] == 'ngã'),
    ('T2', 'zh>vi', 'Taigi 2, obstruent or no initial → hỏi', lambda f: OPEN(f) and f['nt'] == 2 and not f['son'],
     lambda f: f['ht'] == 'hỏi'),
    ('T2', 'zh>vi', 'Taigi 2, sonorant initial → ngã', lambda f: OPEN(f) and f['nt'] == 2 and f['son'],
     lambda f: f['ht'] == 'ngã'),
    ('T2', 'zh>vi', 'Mandarin 3, sonorant initial → ngã', lambda f: OPEN(f) and f['mt'] == 3 and f['son'],
     lambda f: f['ht'] == 'ngã'),
    ('T2', 'zh>vi', 'Cantonese 5, obstruent initial → nặng (old voiced 上)', lambda f: OPEN(f) and f['yt'] == 5 and not f['son']
     and f['hi'], lambda f: f['ht'] == 'nặng'),
    ('T2', 'vi>zh', 'hỏi → Cantonese 2', lambda f: f['ht'] == 'hỏi', YT(2)),
    ('T2', 'vi>zh', 'ngã → Cantonese 5', lambda f: f['ht'] == 'ngã', YT(5)),
    ('T2', 'vi>zh', 'ngã → Mandarin 3', lambda f: f['ht'] == 'ngã', MT(3)),
    ('T3', 'zh>vi', 'Cantonese 3 → sắc', lambda f: OPEN(f) and f['yt'] == 3, lambda f: f['ht'] == 'sắc'),
    ('T3', 'zh>vi', 'Cantonese 6 → nặng', lambda f: OPEN(f) and f['yt'] == 6, lambda f: f['ht'] == 'nặng'),
    ('T3', 'zh>vi', 'Taigi 3 → sắc', lambda f: OPEN(f) and f['nt'] == 3, lambda f: f['ht'] == 'sắc'),
    ('T3', 'zh>vi', 'Taigi 7 → nặng', lambda f: OPEN(f) and f['nt'] == 7, lambda f: f['ht'] == 'nặng'),
    ('T3', 'vi>zh', 'sắc (open syllable) → Cantonese 3', lambda f: OPEN(f) and f['ht'] == 'sắc', YT(3)),
    ('T3', 'vi>zh', 'nặng (open syllable) → Cantonese 6', lambda f: OPEN(f) and f['ht'] == 'nặng', YT(6)),
    ('T3', 'vi>zh', 'nặng (open syllable) → Mandarin 4', lambda f: OPEN(f) and f['ht'] == 'nặng', MT(4)),
    ('T4', 'vi>zh', '-p -t -c -ch → sắc or nặng only', lambda f: f['chk'], lambda f: f['ht'] in ('sắc', 'nặng')),
    ('T4', 'zh>vi', 'checked, Cantonese 1 / 3 → sắc', lambda f: f['chk'] and f['yt'] in (1, 3),
     lambda f: f['ht'] == 'sắc'),
    ('T4', 'zh>vi', 'checked, Cantonese 6 → nặng', lambda f: f['chk'] and f['yt'] in (2, 4, 5, 6),
     lambda f: f['ht'] == 'nặng'),
    ('T4', 'zh>vi', 'Taigi 4 → sắc', lambda f: f['chk'] and f['nt'] == 4, lambda f: f['ht'] == 'sắc'),
    ('T4', 'zh>vi', 'Taigi 8 → nặng', lambda f: f['chk'] and f['nt'] == 8, lambda f: f['ht'] == 'nặng'),
    ('T*', 'zh>vi', 'every tone from Cantonese (the T1–T4 rules together)', lambda f: f['yt'] is not None,
     lambda f: f['ht'] == yue_tone(f)),
    ('T*', 'zh>vi', 'every tone from Taigi (the T1–T4 rules together)', lambda f: f['nt'] is not None,
     lambda f: f['ht'] == nan_tone(f)),
    # --- initials, by the class of the Middle Chinese initial ---------------------------------------------------
    # labials 幫滂並 / 非敷奉 / 明微
    ('IP', 'zh>vi', 'ph ← Mandarin f-', MI('f'), HV('ph')),
    ('IP', 'zh>vi', 'b ← Mandarin b-', MI('b'), HV('b')),
    ('IP', 'zh>vi', 'b ← Taigi p-', NI('p'), HV('b')),
    ('IP', 'vi>zh', 'ph → Mandarin f- or p-', HV('ph'), MI('f', 'p')),
    ('IP', 'vi>zh', 'b → Mandarin b- or p-', HV('b'), MI('b', 'p')),
    ('IM', 'zh>vi', 'm ← Mandarin m-', MI('m'), HV('m')),
    ('IM', 'vi>zh', 'm → Mandarin m-', HV('m'), MI('m')),
    ('IM', 'zh>vi', 'v ← Cantonese m- with Mandarin w-', _all(YI('m'), MI('w')), HV('v')),
    ('IM', 'vi>zh', 'v → Mandarin w- or y-', HV('v'), MI('w', 'y')),
    # dentals 端透定 / 泥來
    ('ID', 'zh>vi', 'đ ← Mandarin d-', MI('d'), HV('đ')),
    ('ID', 'zh>vi', 'đ ← Mandarin t- in tone 2', _all(MI('t'), MT(2)), HV('đ')),
    ('ID', 'zh>vi', 'th ← Mandarin t- in tones 1 3 4', _all(MI('t'), MT(1, 3, 4)), HV('th')),
    ('ID', 'zh>vi', 'đ ← Taigi t- with Mandarin d- / t-', _all(NI('t'), MI('d', 't')), HV('đ')),
    ('ID', 'vi>zh', 'đ → Mandarin d- or t-', HV('đ'), MI('d', 't')),
    ('ID', 'zh>vi', 'n ← Mandarin n-', MI('n'), HV('n')),
    ('ID', 'zh>vi', 'l ← Mandarin l-', MI('l'), HV('l')),
    ('ID', 'vi>zh', 'n → Mandarin n-', HV('n'), MI('n')),
    ('ID', 'vi>zh', 'l → Mandarin l-', HV('l'), MI('l')),
    ('ID', 'zh>vi', 'Taigi l- → l or n (Mandarin decides)', NI('l'), HV('l', 'n')),
    # retroflex series 知徹澄 / 莊初崇生 / 章昌船書禪
    ('IR', 'zh>vi', 'tr ← Mandarin zh- / ch- with Taigi t- / th-', _all(MI('zh', 'ch'), NI('t', 'th')), HV('tr')),
    ('IR', 'zh>vi', 'ch ← Mandarin zh- with Taigi ts- (tendency)', _all(MI('zh'), NI('ts')), HV('ch')),
    ('IR', 'zh>vi', 'ch or tr ← Mandarin zh-', MI('zh'), HV('ch', 'tr')),
    ('IR', 'vi>zh', 'ch → Mandarin zh-', HV('ch'), MI('zh')),
    ('IR', 'vi>zh', 'tr → Mandarin zh- or ch-', HV('tr'), MI('zh', 'ch')),
    ('IR', 'zh>vi', 'th ← Mandarin sh- (tendency; s for some)', MI('sh'), HV('th')),
    ('IR', 'zh>vi', 'th or s ← Mandarin sh-', MI('sh'), HV('th', 's')),
    ('IR', 'zh>vi', 'x or s ← Mandarin ch- in tones 1 3 4', _all(MI('ch'), MT(1, 3, 4)), HV('x', 's')),
    ('IR', 'zh>vi', 'tr or th ← Mandarin ch- in tone 2', _all(MI('ch'), MT(2)), HV('tr', 'th')),
    ('IR', 'vi>zh', 'x → Mandarin ch- (tendency)', HV('x'), MI('ch')),
    ('IR', 'vi>zh', 's → Mandarin sh- or ch- (tendency)', HV('s'), MI('sh', 'ch')),
    # dental sibilants 精清從心邪
    ('IS', 'zh>vi', 't ← Mandarin z-', MI('z'), HV('t')),
    ('IS', 'zh>vi', 'Mandarin j q x with Cantonese z c s → t or th', _all(MI('j', 'q', 'x'), YI('z', 'c', 's')),
     HV('t', 'th')),
    ('IS', 'zh>vi', 'old ts- s- series, Taigi ts- / s- → t', lambda f: JING(f) and f['ni'] in ('ts', 's'), HV('t')),
    ('IS', 'zh>vi', 'old ts- s- series, Taigi tsh- → th', lambda f: JING(f) and f['ni'] == 'tsh', HV('th')),
    ('IS', 'vi>zh', 't → Mandarin z c s j q x', HV('t'), MI('z', 'c', 's', 'j', 'q', 'x')),
    ('IS', 'vi>zh', 't → Cantonese z c s', HV('t'), YI('z', 'c', 's')),
    # velars 見溪群 / 疑 / 曉匣
    ('IK', 'zh>vi', 'c / k / q ← Mandarin g-', MI('g'), HV('c')),
    ('IK', 'zh>vi', 'c / k / q or gi ← Taigi k-', NI('k'), HV('c', 'gi')),
    ('IK', 'zh>vi', 'Mandarin j q x with Cantonese g k h → c kh h gi',
     _all(MI('j', 'q', 'x'), YI('g', 'k', 'gw', 'kw', 'h', 'f')), HV('c', 'kh', 'h', 'gi')),
    ('IK', 'zh>vi', 'gi ← Mandarin j- with Cantonese g- + aa / o',
     lambda f: f['mi'] == 'j' and f['yi'] == 'g' and f['yr'][:2] in ('aa', 'ok', 'on'), HV('gi')),
    ('IK', 'zh>vi', 'kh ← Cantonese h- / f- with Mandarin k- / q-', _all(YI('h', 'f'), MI('k', 'q')), HV('kh')),
    ('IK', 'zh>vi', 'kh ← Taigi kh- (tendency)', NI('kh'), HV('kh')),
    ('IK', 'vi>zh', 'c / k / q → Mandarin g j k q', HV('c'), MI('g', 'j', 'k', 'q')),
    ('IK', 'vi>zh', 'c / k / q → Taigi k-', HV('c'), NI('k')),
    ('IK', 'vi>zh', 'kh → Mandarin k- or q-', HV('kh'), MI('k', 'q')),
    ('IK', 'vi>zh', 'kh → Taigi kh-', HV('kh'), NI('kh')),
    ('IK', 'vi>zh', 'gi → Mandarin j- with Cantonese g-', HV('gi'), _all(MI('j'), YI('g'))),
    ('IG', 'zh>vi', 'ng / ngh ← Taigi g-', NI('g'), HV('ng')),
    ('IG', 'vi>zh', 'ng / ngh → Taigi g-', HV('ng'), NI('g')),
    ('IH', 'zh>vi', 'h ← Mandarin h- / x- with Cantonese h- / f- / w- / j-',
     _all(MI('h', 'x'), YI('h', 'f', 'w', 'j')), HV('h')),
    ('IH', 'zh>vi', 'Taigi h- → h, but ph when Mandarin has f-', _all(NI('h'), _known('mi')),
     lambda f: f['hi'] == ('ph' if f['mi'] == 'f' else 'h')),
    ('IH', 'vi>zh', 'h → Mandarin h- or x-', HV('h'), MI('h', 'x')),
    ('IH', 'vi>zh', 'h → Taigi h-', HV('h'), NI('h')),
    # 影云以日: no initial, v, d, nh
    ('IY', 'zh>vi', 'nh ← Mandarin r-', MI('r'), HV('nh')),
    ('IY', 'vi>zh', 'nh → Mandarin r- (tendency)', HV('nh'), MI('r')),
    ('IY', 'vi>zh', 'nh → Mandarin r-, y- or none', HV('nh'), MI('r', 'y', '')),
    ('IY', 'zh>vi', 'nh ← Taigi j-', NI('j'), HV('nh')),
    ('IY', 'zh>vi', 'd ← Mandarin y- with Cantonese j- in a low tone (4 5 6), Taigi none (tendency)',
     _all(MI('y'), YI('j'), YT(4, 5, 6), NI('')), HV('d')),
    ('IY', 'vi>zh', 'd → Mandarin y- (tendency, at the threshold)', HV('d'), MI('y')),
    ('IY', 'vi>zh', 'd → Cantonese j- (tendency)', HV('d'), YI('j')),
    ('IY', 'zh>vi', 'no initial ← Mandarin y- / w- / none with Cantonese j- / w- / none in tone 1 2 3',
     _all(MI('y', 'w', ''), YI('j', 'w', ''), YT(1, 2, 3)), HV('')),
    ('IY', 'vi>zh', 'no initial → Mandarin y-, w- or none', HV(''), MI('y', 'w', '')),
    ('IY', 'vi>zh', 'no Hán-Việt syllable starts with r', lambda f: True, lambda f: f['hi'] != 'r'),
    # aspiration, across the classes
    ('IA', 'zh>vi', 'Cantonese p t k kw c in tone 4 / 5 → b đ c t tr ch gi (old voiced)',
     _all(YI('p', 't', 'k', 'kw', 'c'), YT(4, 5)), HV(*UNASP)),
    ('IA', 'zh>vi', 'Mandarin p t k q c ch in tone 2 → b đ c t tr ch gi (old voiced)',
     _all(MI('p', 't', 'k', 'q', 'c', 'ch'), MT(2)), HV(*UNASP)),
    ('IA', 'zh>vi', 'Mandarin p t k q c ch in tones 1 3 4 → ph th kh x s',
     _all(MI('p', 't', 'k', 'q', 'c', 'ch'), MT(1, 3, 4)), HV(*ASP)),
    # spelling what Hà Nội merges
    ('Z1', 'spell', 'd or gi: gi when Cantonese has g-', *_spell(('gi', 'd'), YI('g'))),
    ('Z1', 'spell', 'd or gi: gi when Mandarin has j-', *_spell(('gi', 'd'), MI('j'))),
    ('Z2', 'spell', 'tr or ch: ch when Taigi has ts-', *_spell(('ch', 'tr'), NI('ts'))),
    ('Z3', 'spell', 's or x: x when Mandarin has ch- (tendency)', *_spell(('x', 's'), MI('ch'))),
    ('Z3', 'spell', 's or x: x when Taigi has tsh- (tendency)', *_spell(('x', 's'), NI('tsh'))),
    # the first proposal's initials, measured and dropped
    ('I1x', 'drop', 'kh ← Cantonese h-', YI('h'), HV('kh')),
    ('I2x', 'drop', 'ph ← Cantonese f-', YI('f'), HV('ph')),
    ('I3x', 'drop', 'v ← Cantonese m-', YI('m'), HV('v')),
    ('I3x', 'drop', 'v ← Mandarin w-', MI('w'), HV('v')),
    ('I4x', 'drop', 'gi ← Mandarin j-', MI('j'), HV('gi')),
    ('I5x', 'drop', 'tr or ch: tr when Taigi t-, ch when ts- (replaced by Z2)', lambda f: f['hi'] in ('tr', 'ch') and f['ni'] in ('t', 'ts'),
     lambda f: (f['hi'] == 'tr') == (f['ni'] == 't')),
    ('I6x', 'drop', 's or x: s when Mandarin sh-, x when ch-', lambda f: f['hi'] in ('s', 'x') and f['mi'] in ('sh', 'ch'),
     lambda f: (f['hi'] == 's') == (f['mi'] == 'sh')),
    ('I7x', 'drop', 'd ← Mandarin y-', MI('y'), HV('d')),
]


def measure(fs, show=8):
    out = []
    for rid, way, text, cond, pred in RULES:
        hit = tot = 0
        exc = []
        for f in fs:
            try:
                if not cond(f):
                    continue
                p = pred(f)
            except (TypeError, AttributeError):     # a feature left undetermined
                continue
            if p is None:                           # the prediction's feature is undetermined
                continue
            tot += 1
            if p:
                hit += 1
            else:
                exc.append(f"{f['ch']} {f['hv']}")
        out.append((rid, way, text, hit, tot, exc[:show]))
    return out


def kind(way, hit, tot):
    """How the syllabus may teach a measured rule: 'rule' at 80 % or more, 'tendency' from 60 %, else 'drop'."""
    if way == 'drop' or not tot:
        return 'drop'
    r = hit / tot
    return 'rule' if r >= 0.795 else 'tendency' if r >= 0.6 else 'drop'


def check_examples(path):
    """The chữ Hán of the bridge-examples block of `path`, each through lint's bridge-note test."""
    import lint
    lint.D = lint.DB_(lint.DB)
    text = open(path, encoding='utf-8').read()
    blocks = re.findall(r'<!-- bridge-examples -->(.*?)<!-- /bridge-examples -->', text, re.S)
    runs = list(dict.fromkeys(re.findall(r'[㐀-鿿\U00020000-\U0002ffff]+', ''.join(blocks))))
    bad = [(r, lint.D.bridge_example(r)) for r in runs]
    bad = [(r, why) for r, why in bad if why]
    for r, why in bad:
        print(f'E bridge example {r}: {why}')
    print(f'{path}: {len(runs)} bridge examples, {len(bad)} refused')
    return 1 if bad else 0


def main():
    if '--examples' in sys.argv:
        sys.exit(check_examples(sys.argv[sys.argv.index('--examples') + 1]))
    con = cards.open_db('public')
    data = items(con)
    fs = [features(d) for d in data]
    words = {w for d in data for w in d['words']}
    print(f'{len(fs)} syllables (character + Hán-Việt reading) of {len(words)} Hán-Việt cards of rank <= {TOP}\n')
    print('| id | direction | rule | hits / total | % | kind | main exceptions |\n|---|---|---|---|---|---|---|')
    for rid, way, text, hit, tot, exc in measure(fs):
        print(f"| {rid} | {way} | {text} | {hit} / {tot} | {100 * hit / tot if tot else 0:.0f} | {kind(way, hit, tot)} "
              f"| {' '.join(exc)} |")
    if '--json' in sys.argv:
        json.dump(data, open(sys.argv[sys.argv.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
