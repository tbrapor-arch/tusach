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
A rule's total is the items its condition covers; a rule under 80 % is taught as a tendency, or not at all.
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


JING = lambda f: f['mi'] in ('z', 'c', 's', 'j', 'q', 'x') and f['yi'] in ('z', 'c', 's')   # noqa: E731 精 series
OPEN = lambda f: not f['chk']                                                                # noqa: E731

# (id, rule as taught, condition, prediction). Ids are the syllabus's.
RULES = [
    ('B1', 'Cantonese -p → -p', lambda f: yue_coda(f) == 'p', lambda f: f['coda'] == 'p'),
    ('B1', 'Cantonese -t → -t', lambda f: yue_coda(f) == 't', lambda f: f['coda'] == 't'),
    ('B1', 'Cantonese -k → -c / -ch', lambda f: yue_coda(f) == 'k', lambda f: f['coda'] in ('c', 'ch')),
    ('B2', 'Cantonese -m → -m', lambda f: yue_coda(f) == 'm', lambda f: f['coda'] == 'm'),
    ('B2', 'Taigi -m → -m', lambda f: re.search('m$', f['nr']) is not None and not f['nr'].endswith('nn'),
     lambda f: f['coda'] == 'm'),
    ('B3', 'Hán-Việt -nh / -ch ← Cantonese -ng / -k', lambda f: f['coda'] in ('nh', 'ch') and f['yr'] is not None,
     lambda f: yue_coda(f) in ('ng', 'k')),
    ('B3', 'Mandarin -ing → -nh (tendency: -ưng/-ăng for some)', lambda f: f['mr'] == 'ing', lambda f: f['coda'] == 'nh'),
    ('B3x', 'Cantonese -ing / -ik → -nh / -ch (dropped)', lambda f: f['yr'] in ('ing', 'ik'),
     lambda f: f['coda'] in ('nh', 'ch')),
    ('V1', 'Cantonese -oeng / -oek → -ương / -ươc', lambda f: f['yr'] in ('oeng', 'oek'), lambda f: 'ươ' in f['hr']),
    ('V2', 'Cantonese -in / -it → -iên / -iêt', lambda f: f['yr'] in ('in', 'it'),
     lambda f: 'iê' in f['hr'] or 'yê' in f['hr']),
    ('T1', 'Cantonese 1 (open syllable) → ngang', lambda f: OPEN(f) and f['yt'] == 1, lambda f: f['ht'] == 'ngang'),
    ('T1', 'Cantonese 4, obstruent initial → huyền', lambda f: OPEN(f) and f['yt'] == 4 and not f['son'] and f['hi'],
     lambda f: f['ht'] == 'huyền'),
    ('T1', 'Cantonese 4, sonorant initial (m n nh ng l v d) → ngang', lambda f: OPEN(f) and f['yt'] == 4 and f['son'],
     lambda f: f['ht'] == 'ngang'),
    ('T1', 'Taigi 5, sonorant initial → ngang', lambda f: OPEN(f) and f['nt'] == 5 and f['son'],
     lambda f: f['ht'] == 'ngang'),
    ('T1x', 'Cantonese 4 → huyền, whatever the initial (old table)', lambda f: OPEN(f) and f['yt'] == 4,
     lambda f: f['ht'] == 'huyền'),
    ('T2', 'Cantonese 2 → hỏi', lambda f: OPEN(f) and f['yt'] == 2, lambda f: f['ht'] == 'hỏi'),
    ('T2', 'Cantonese 5, sonorant initial → ngã', lambda f: OPEN(f) and f['yt'] == 5 and f['son'],
     lambda f: f['ht'] == 'ngã'),
    ('T2', 'Taigi 2, obstruent or no initial → hỏi', lambda f: OPEN(f) and f['nt'] == 2 and not f['son'],
     lambda f: f['ht'] == 'hỏi'),
    ('T2', 'Taigi 2, sonorant initial → ngã', lambda f: OPEN(f) and f['nt'] == 2 and f['son'], lambda f: f['ht'] == 'ngã'),
    ('T2', 'Mandarin 3, sonorant initial → ngã', lambda f: OPEN(f) and f['mt'] == 3 and f['son'],
     lambda f: f['ht'] == 'ngã'),
    ('T3', 'Cantonese 3 → sắc', lambda f: OPEN(f) and f['yt'] == 3, lambda f: f['ht'] == 'sắc'),
    ('T3', 'Cantonese 6 → nặng', lambda f: OPEN(f) and f['yt'] == 6, lambda f: f['ht'] == 'nặng'),
    ('T3', 'Taigi 3 → sắc', lambda f: OPEN(f) and f['nt'] == 3, lambda f: f['ht'] == 'sắc'),
    ('T3', 'Taigi 7 → nặng', lambda f: OPEN(f) and f['nt'] == 7, lambda f: f['ht'] == 'nặng'),
    ('T4', '-p -t -c -ch → sắc or nặng only', lambda f: f['chk'], lambda f: f['ht'] in ('sắc', 'nặng')),
    ('T4', 'checked, Cantonese 1 / 3 → sắc', lambda f: f['chk'] and f['yt'] in (1, 3), lambda f: f['ht'] == 'sắc'),
    ('T4', 'checked, Cantonese 6 → nặng', lambda f: f['chk'] and f['yt'] in (2, 4, 5, 6), lambda f: f['ht'] == 'nặng'),
    ('T4', 'Taigi 4 → sắc', lambda f: f['chk'] and f['nt'] == 4, lambda f: f['ht'] == 'sắc'),
    ('T4', 'Taigi 8 → nặng', lambda f: f['chk'] and f['nt'] == 8, lambda f: f['ht'] == 'nặng'),
    ('I1', 'kh ← Cantonese h- / f- with Mandarin k- / q-', lambda f: f['yi'] in ('h', 'f') and f['mi'] in ('k', 'q'),
     lambda f: f['hi'] == 'kh'),
    ('I1', 'h ← Cantonese h- / f- / w- / j- with Mandarin h- / x-',
     lambda f: f['yi'] in ('h', 'f', 'w', 'j') and f['mi'] in ('h', 'x'), lambda f: f['hi'] == 'h'),
    ('I1x', 'kh ← Cantonese h- (old I1)', lambda f: f['yi'] == 'h', lambda f: f['hi'] == 'kh'),
    ('I1x', 'kh ← Taigi kh- (old I1)', lambda f: f['ni'] == 'kh', lambda f: f['hi'] == 'kh'),
    ('I2', 'ph ← Mandarin f-', lambda f: f['mi'] == 'f', lambda f: f['hi'] == 'ph'),
    ('I2x', 'ph ← Cantonese f- (old I2)', lambda f: f['yi'] == 'f', lambda f: f['hi'] == 'ph'),
    ('I3', 'v ← Cantonese m- with Mandarin w-', lambda f: f['yi'] == 'm' and f['mi'] == 'w', lambda f: f['hi'] == 'v'),
    ('I3x', 'v ← Mandarin w- (old I3)', lambda f: f['mi'] == 'w', lambda f: f['hi'] == 'v'),
    ('I4', 'gi ← Mandarin j- with Cantonese g- + aa / o',
     lambda f: f['mi'] == 'j' and f['yi'] == 'g' and f['yr'][:2] in ('aa', 'ok', 'on'), lambda f: f['hi'] == 'gi'),
    ('I4', 'spelling d or gi: gi when Cantonese has g-', lambda f: f['hi'] in ('d', 'gi') and f['yi'] is not None,
     lambda f: (f['hi'] == 'gi') == (f['yi'] == 'g')),
    ('I4x', 'gi ← Mandarin j- (old I4)', lambda f: f['mi'] == 'j', lambda f: f['hi'] == 'gi'),
    ('I5', 'tr ← Mandarin zh- / ch- with Taigi t- / th-', lambda f: f['mi'] in ('zh', 'ch') and f['ni'] in ('t', 'th'),
     lambda f: f['hi'] == 'tr'),
    ('I5', 'ch ← Mandarin zh- with Taigi ts- (tendency)', lambda f: f['mi'] == 'zh' and f['ni'] == 'ts',
     lambda f: f['hi'] == 'ch'),
    ('I5x', 'spelling tr or ch: tr when Taigi t-, ch when ts- (old I5)',
     lambda f: f['hi'] in ('tr', 'ch') and f['ni'] in ('t', 'ts'), lambda f: (f['hi'] == 'tr') == (f['ni'] == 't')),
    ('I6', 'th ← Mandarin sh- (tendency; s in a closed set)', lambda f: f['mi'] == 'sh', lambda f: f['hi'] == 'th'),
    ('I6', 'th or s ← Mandarin sh-', lambda f: f['mi'] == 'sh', lambda f: f['hi'] in ('th', 's')),
    ('I6x', 'spelling s or x: s when Mandarin sh-, x when ch- (old I6)',
     lambda f: f['hi'] in ('s', 'x') and f['mi'] in ('sh', 'ch'), lambda f: (f['hi'] == 's') == (f['mi'] == 'sh')),
    ('I6x', 'spelling s or x: x when Taigi tsh-', lambda f: f['hi'] in ('s', 'x') and f['ni'] is not None,
     lambda f: (f['hi'] == 'x') == (f['ni'] == 'tsh')),
    ('I7', 'd ← Mandarin y- with Cantonese j- in a low tone (4 5 6), Taigi not g- (tendency)',
     lambda f: f['mi'] == 'y' and f['yi'] == 'j' and f['yt'] in (4, 5, 6) and f['ni'] not in ('g', 'j', 'h'),
     lambda f: f['hi'] == 'd'),
    ('I7x', 'd ← Mandarin y- (old I7)', lambda f: f['mi'] == 'y', lambda f: f['hi'] == 'd'),
    ('I7', 'no Hán-Việt syllable starts with r', lambda f: True, lambda f: f['hi'] != 'r'),
    ('I8', 'nh ← Mandarin r-', lambda f: f['mi'] == 'r', lambda f: f['hi'] == 'nh'),
    ('I9', 'ng / ngh ← Taigi g-', lambda f: f['ni'] == 'g', lambda f: f['hi'] == 'ng'),
    ('I10', 'Mandarin j q x: Cantonese g k h → c kh h gi',
     lambda f: f['mi'] in ('j', 'q', 'x') and f['yi'] in ('g', 'k', 'gw', 'kw', 'h', 'f'),
     lambda f: f['hi'] in ('c', 'kh', 'h', 'gi')),
    ('I10', 'Mandarin j q x: Cantonese z c s → t th', lambda f: f['mi'] in ('j', 'q', 'x') and f['yi'] in ('z', 'c', 's'),
     lambda f: f['hi'] in ('t', 'th')),
    ('I10', 'Mandarin z- → t', lambda f: f['mi'] == 'z', lambda f: f['hi'] == 't'),
    ('I10', 'old ts- s- series, Taigi ts- / s- → t', lambda f: JING(f) and f['ni'] in ('ts', 's'), lambda f: f['hi'] == 't'),
    ('I10', 'old ts- s- series, Taigi tsh- → th', lambda f: JING(f) and f['ni'] == 'tsh', lambda f: f['hi'] == 'th'),
    ('I11', 'đ ← Mandarin d-', lambda f: f['mi'] == 'd', lambda f: f['hi'] == 'đ'),
    ('I11', 'đ ← Mandarin t- in tone 2', lambda f: f['mi'] == 't' and f['mt'] == 2, lambda f: f['hi'] == 'đ'),
    ('I11', 'th ← Mandarin t- in tones 1 3 4', lambda f: f['mi'] == 't' and f['mt'] in (1, 3, 4),
     lambda f: f['hi'] == 'th'),
]


def measure(fs, show=8):
    out = []
    for rid, text, cond, pred in RULES:
        hit = tot = 0
        exc = []
        for f in fs:
            try:
                if not cond(f):
                    continue
            except (TypeError, AttributeError):     # a feature left undetermined
                continue
            tot += 1
            if pred(f):
                hit += 1
            else:
                exc.append(f"{f['ch']} {f['hv']}")
        out.append((rid, text, hit, tot, exc[:show]))
    return out


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
    print('| id | rule | hits / total | % | main exceptions |\n|---|---|---|---|---|')
    for rid, text, hit, tot, exc in measure(fs):
        print(f"| {rid} | {text} | {hit} / {tot} | {100 * hit / tot if tot else 0:.0f} | {' '.join(exc)} |")
    if '--json' in sys.argv:
        json.dump(data, open(sys.argv[sys.argv.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
