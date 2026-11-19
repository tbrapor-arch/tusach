"""Measure the sound correspondences the syllabus teaches (course/proposal/syllabus-proposal.md, bridge strand) against
the cards, write the proposal's rule tables, and check the bridge-note examples of the proposal with lint's test.

    python3 -I tools/bridge_rules.py                 # every rule as a markdown table (all the columns below)
    python3 -I tools/bridge_rules.py --write FILE    # rewrite the generated rule tables of FILE (between
                                                     # <!-- rules:GROUP --> and <!-- /rules --> markers)
    python3 -I tools/bridge_rules.py --check FILE    # exit 1 when FILE's tables are not what --write would write
    python3 -I tools/bridge_rules.py --examples FILE # the chữ Hán between <!-- bridge-examples --> and
                                                     # <!-- /bridge-examples --> in FILE, each through lint's test

The data: every key of rank <= 3,000 whose card (tools/cards.py lookup: the course lexicon, else the main etymology)
is Hán-Việt (label same, gram, hv-vn, opaque, false-friend); each distinct (character, Hán-Việt syllable) of these
cards is one item, with the first (most frequent) word that has it.

The reading the learner would use (review 3, finding 2), per language, stated and data-based:
  * the WORD's own reading of the character when the source has the word (rime-cantonese, the MOE, CC-CEDICT);
  * else the character's most frequent reading by the source's own order (rime's share for Cantonese; the MOE's
    literary reading, its order; Unihan kMandarin then CC-CEDICT use for Mandarin: tools/build_db.py rank_chinese);
  * Cantonese changed tone (變音): a tone-2 reading whose syllable the source also reads in tone 4, 5 or 6 (錢
    cin2 beside cin4, 社會 se5 wui2 beside 會 wui6) is a changed tone: the main reading is the base tone, and the
    item is counted among the "changed tone" ones (the note under the table).
Three rates per rule: MAIN (that reading), STRICT (every candidate reading must fit: the word's reading, else every
reading of the character; an item whose candidates all leave the condition is out), LENIENT (one candidate fits).
For zh>vi the main rate is the honest one; for vi>zh (from the Vietnamese heard to the Chinese) the lenient one is
fair (any of his readings will do). The thresholds apply to the MAIN rate: a rule at 80 % or more, a tendency from 60
%, else dropped; a rule whose prediction is a set of letters (or readings) is quoted with its BEST SINGLE GUESS (the
most frequent outcome's share): under 60 % it is taught as "narrows it to these letters", not as a prediction.
A rule's condition uses only what the learner has on the side he starts from (review 3, finding 3): a zh>vi rule
tests Cantonese / Taigi / Mandarin features only (a "sonorant initial" is the Chinese one: Cantonese m n ng l j w or
none, Taigi m n ng l j b g or none, Mandarin m n l r y w or none); a vi>zh rule tests the Vietnamese only. Directions:
zh>vi, vi>zh, spell (the letter for a sound Hà Nội merges, from the Chinese; he hears the sound), fact (a fact of
Vietnamese spelling, not a correspondence), drop (measured and not taught).
"""
import collections
import itertools
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cards  # noqa: E402
import soundfit  # noqa: E402
import vi  # noqa: E402
from soundfit import hv_split, split, tone, marks_off  # noqa: E402,F401  (used by tests)

TOP = 3000
LABELS = ('same', 'gram', 'hv-vn', 'opaque', 'false-friend')
LANGS = ('yue', 'nan', 'cmn')


def readings(con, ch, lang):
    """A character's readings in the source's order (Taigi: the literary layer, tools/bridge.py)."""
    rs = con.execute("SELECT reading, note FROM chinese WHERE chars=? AND lang=? AND level='char' AND source!='fixture' "
                     "AND note != 'name' ORDER BY rank, ord", (ch, lang)).fetchall()
    if lang == 'nan':
        lit = [r for r, n in rs if n == 'literary']
        return lit or [r for r, n in rs if 'colloquial' not in (n or '')]
    return [r for r, _ in rs]


def changed_tone(r, rs):
    """The base reading when Cantonese `r` is a changed tone: tone 2 (the rising 變音), the same syllable also read in
    a low tone 4, 5 or 6 by the source (錢 cin2 / cin4, 會 wui2 / wui6, 院 jyun2 / jyun6); the base is the first such
    reading in the source's order. A tone-2 reading beside a tone 3 one is a word of its own (好 hou2 / hou3)."""
    if tone('yue', r) != 2:
        return None
    seg = re.sub(r'\d', '', r)
    base = [x for x in rs if re.sub(r'\d', '', x) == seg and tone('yue', x) in (4, 5, 6)]
    return base[0] if base else None


def candidates(con, ch, i, chars, lang):
    """(main reading, candidate readings, changed tone?) of character `ch` at position i of the word `chars`."""
    rs = [x.lower() for x in dict.fromkeys(readings(con, ch, lang))]
    if not rs:
        return None, [], False
    word = None
    if len(chars) > 1:
        wr = con.execute("SELECT reading FROM chinese WHERE chars=? AND lang=? AND level='word' AND source!='fixture' "
                         "AND note != 'name' ORDER BY rank, ord", (chars, lang)).fetchone()
        if wr:
            parts = soundfit.word_syllables(lang, wr[0], [readings(con, c, lang) for c in chars])
            if parts:
                p = parts[i].lower()
                if lang == 'nan' and p in rs:
                    word = p
                elif lang == 'cmn' and any(marks_off(x, '̈') == marks_off(p, '̈') for x in rs):
                    word = p
                elif lang == 'yue' and (p in rs or changed_tone(p, rs + [p])):
                    word = p
    if word:
        cands = [word]
    else:
        cands = rs
    main = cands[0]
    changed = False
    if lang == 'yue':
        base = changed_tone(main, rs if main in rs else rs + [main])
        if base:
            main, changed = base, True
            if base not in cands:
                cands = cands + [base]
    return main, cands, changed


def items(con):
    """[{ch, hv, words, yue / nan / cmn: candidates, yue_main…, yue_changed}] (see the module docstring)."""
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
            d = {'ch': ch, 'hv': s, 'words': [k]}
            for lang in LANGS:
                d[lang + '_main'], d[lang], d[lang + '_changed'] = candidates(con, ch, i, c['chars'], lang)
            seen[(ch, s)] = d
    return list(seen.values())


# --- features -------------------------------------------------------------------------------------------------------
SON = {'m', 'n', 'nh', 'ng', 'l', 'v', 'd'}     # Hán-Việt initials from old sonorants (m n ŋ l ɲ, 微 云 以 日)
YSON = {'m', 'n', 'ng', 'l', 'j', 'w', ''}       # Cantonese sonorant (or no) initial
NSON = {'m', 'n', 'ng', 'l', 'j', 'b', 'g', ''}  # Taigi: b g come from old m ŋ
MSON = {'m', 'n', 'l', 'r', 'y', 'w', ''}        # Mandarin
TONE = soundfit.TONE
FRONT = ('i', 'y', 'ê', 'iê', 'yê', 'ư', 'ươ')    # Hán-Việt rhymes after which Mandarin palatalised (j q x)


def features(d):
    """The features of an item whose language entries are lists of readings: a feature counts only when all the
    readings agree on it (else None). Called with one reading per language (main, or one combination)."""
    f = {'ch': d['ch'], 'hv': d['hv']}
    f['hi'], f['hr'] = hv_split(d['hv'])
    f['ht'] = TONE[vi.tone(d['hv'])]
    m = re.search(r'(nh|ng|ch|p|t|c|m|n)$', marks_off(d['hv'], '̛̆̂'))
    f['coda'] = m.group(1) if m else ''
    f['chk'] = f['coda'] in ('p', 't', 'c', 'ch')
    f['son'] = f['hi'] in SON
    f['front'] = f['hr'].startswith(FRONT)
    for lang, p in (('yue', 'y'), ('nan', 'n'), ('cmn', 'm')):
        rs = d.get(lang) or []
        for name, fn in (('i', lambda r: split(lang, r)[0]), ('r', lambda r: split(lang, r)[1]),
                         ('t', lambda r: tone(lang, r))):
            vals = {fn(r) for r in rs}
            f[p + name] = vals.pop() if len(vals) == 1 else None
    f['ycoda'] = None if f['yr'] is None else (re.search(r'(ng|p|t|k|m|n)$', f['yr']) or [''])[0]
    f['ychk'] = None if f['ycoda'] is None else f['ycoda'] in ('p', 't', 'k')
    f['yson'] = None if f['yi'] is None else f['yi'] in YSON
    f['nchk'] = None if f['nt'] is None else f['nt'] in (4, 8)
    f['nson'] = None if f['ni'] is None else f['ni'] in NSON
    f['mson'] = None if f['mi'] is None else f['mi'] in MSON
    return f


def main_features(d):
    return features({**d, **{lang: [d[lang + '_main']] if d.get(lang + '_main') else [] for lang in LANGS}})


def combo_features(d):
    """The features of every combination of candidate readings (one per language)."""
    opts = [(d.get(lang) or [None]) for lang in LANGS]
    out = []
    for combo in itertools.product(*opts):
        out.append(features({**d, **{lang: [r] if r else [] for lang, r in zip(LANGS, combo)}}))
    return out


def yue_coda(f):
    return f['ycoda'] or ''


def yue_tone(f):
    """The Hán-Việt tone predicted from the Cantonese tone, the Cantonese coda and the Cantonese initial only."""
    t = f['yt']
    if f['ychk']:
        return 'sắc' if t in (1, 3) else 'nặng'
    return {1: 'ngang', 2: 'hỏi', 3: 'sắc', 6: 'nặng', 4: 'ngang' if f['yson'] else 'huyền',
            5: 'ngã' if f['yson'] else 'nặng'}.get(t)


def nan_tone(f):
    """The Hán-Việt tone predicted from the Taigi literary tone and the Taigi initial only."""
    t = f['nt']
    return {1: 'ngang', 3: 'sắc', 4: 'sắc', 7: 'nặng', 8: 'nặng', 5: 'ngang' if f['nson'] else 'huyền',
            2: 'ngã' if f['nson'] else 'hỏi', 6: 'nặng'}.get(t)


ASP = ('ph', 'th', 'kh', 'x', 's')                 # Hán-Việt letters from old aspirates (and the 章 / 莊 fricatives)
UNASP = ('b', 'đ', 'c', 't', 'tr', 'ch', 'gi')     # Hán-Việt letters from old plain or voiced stops and affricates


def _is(key, *vals):
    """f[key] in vals; None when the feature is undetermined (the readings disagree or are missing)."""
    return lambda f: None if f[key] is None else f[key] in vals


def _all(*fns):
    def test(f):
        vals = [g(f) for g in fns]
        return None if None in vals else all(vals)
    return test


def _not(fn):
    return lambda f: None if fn(f) is None else not fn(f)


def _spell(pair, test):
    """A spelling rule for two letters Hà Nội pronounces alike: among the syllables spelt with either (he hears the
    sound), the first letter is written exactly when `test` holds."""
    return lambda f: f['hi'] in pair, lambda f: None if test(f) is None else (f['hi'] == pair[0]) == bool(test(f))


HV, YI, NI, MI = (lambda *v: _is('hi', *v)), (lambda *v: _is('yi', *v)), (lambda *v: _is('ni', *v)), \
    (lambda *v: _is('mi', *v))
YT, NT, MT = (lambda *v: _is('yt', *v)), (lambda *v: _is('nt', *v)), (lambda *v: _is('mt', *v))
YOPEN = _is('ychk', False)
YCHK = _is('ychk', True)
YSONI, NSONI, MSONI = _is('yson', True), _is('nson', True), _is('mson', True)
YOBS, NOBS, MOBS = _is('yson', False), _is('nson', False), _is('mson', False)
HT = lambda *v: _is('ht', *v)  # noqa: E731

# (id, direction, group, rule as taught, condition, prediction, outcome feature of a multi-outcome rule or None).
# Groups: the proposal's tables (tools/bridge_rules.py --write). Ids are the syllabus's.
RULES = [
    # --- tones from Cantonese
    ('T1', 'zh>vi', 'tones-yue', 'Cantonese 1, not -p -t -k → ngang', _all(YOPEN, YT(1)), HT('ngang'), None),
    ('T1', 'zh>vi', 'tones-yue', 'Cantonese 4, initial m n ng l j w or none → ngang', _all(YT(4), YSONI), HT('ngang'), None),
    ('T1', 'zh>vi', 'tones-yue', 'Cantonese 4, other initial → huyền', _all(YT(4), YOBS), HT('huyền'), None),
    ('T2', 'zh>vi', 'tones-yue', 'Cantonese 2 → hỏi', _all(YOPEN, YT(2)), HT('hỏi'), None),
    ('T2', 'zh>vi', 'tones-yue', 'Cantonese 5, initial m n ng l j w or none → ngã', _all(YT(5), YSONI), HT('ngã'), None),
    ('T2', 'zh>vi', 'tones-yue', 'Cantonese 5, other initial → nặng (old voiced 上)', _all(YT(5), YOBS), HT('nặng'), None),
    ('T3', 'zh>vi', 'tones-yue', 'Cantonese 3, not -p -t -k → sắc', _all(YOPEN, YT(3)), HT('sắc'), None),
    ('T3', 'zh>vi', 'tones-yue', 'Cantonese 6, not -p -t -k → nặng', _all(YOPEN, YT(6)), HT('nặng'), None),
    ('T4', 'zh>vi', 'tones-yue', 'Cantonese -p -t -k in tone 1 or 3 → sắc', _all(YCHK, YT(1, 3)), HT('sắc'), None),
    ('T4', 'zh>vi', 'tones-yue', 'Cantonese -p -t -k in tone 6 → nặng', _all(YCHK, YT(6)), HT('nặng'), None),
    ('T*', 'zh>vi', 'tones-yue', 'every tone from Cantonese (the rules above together)', _is('yt', 1, 2, 3, 4, 5, 6),
     lambda f: None if f['ychk'] is None or f['yson'] is None else f['ht'] == yue_tone(f), None),
    ('T1x', 'drop', 'tones-yue', 'Cantonese 4 → huyền, whatever the initial (first proposal)', _all(YOPEN, YT(4)),
     HT('huyền'), None),
    ('T1x', 'drop', 'tones-yue', 'Cantonese 4 → ngang when the VIETNAMESE initial is m n nh ng l v d (proposal 2: '
     'circular)', lambda f: f['yt'] == 4 and f['son'], HT('ngang'), None),
    # --- tones from Taigi
    ('T1', 'zh>vi', 'tones-nan', 'Taigi 1 → ngang', NT(1), HT('ngang'), None),
    ('T1', 'zh>vi', 'tones-nan', 'Taigi 5, initial m n ng l j b g or none → ngang', _all(NT(5), NSONI), HT('ngang'), None),
    ('T1', 'zh>vi', 'tones-nan', 'Taigi 5, other initial → huyền', _all(NT(5), NOBS), HT('huyền'), None),
    ('T2', 'zh>vi', 'tones-nan', 'Taigi 2, initial m n ng l j b g or none → ngã', _all(NT(2), NSONI), HT('ngã'), None),
    ('T2', 'zh>vi', 'tones-nan', 'Taigi 2, other initial → hỏi', _all(NT(2), NOBS), HT('hỏi'), None),
    ('T3', 'zh>vi', 'tones-nan', 'Taigi 3 → sắc', NT(3), HT('sắc'), None),
    ('T3', 'zh>vi', 'tones-nan', 'Taigi 7 → nặng', NT(7), HT('nặng'), None),
    ('T4', 'zh>vi', 'tones-nan', 'Taigi 4 → sắc', NT(4), HT('sắc'), None),
    ('T4', 'zh>vi', 'tones-nan', 'Taigi 8 → nặng', NT(8), HT('nặng'), None),
    ('T*', 'zh>vi', 'tones-nan', 'every tone from Taigi (the rules above together)', _is('nt', 1, 2, 3, 4, 5, 7, 8),
     lambda f: None if f['nson'] is None else f['ht'] == nan_tone(f), None),
    # --- tones from Mandarin (no checked syllables: Cantonese or Taigi tells them)
    ('T1', 'zh>vi', 'tones-cmn', 'Mandarin 1 → ngang', MT(1), HT('ngang'), None),
    ('T1', 'zh>vi', 'tones-cmn', 'Mandarin 1, not -p -t -k in Cantonese → ngang', _all(MT(1), YOPEN), HT('ngang'), None),
    ('T1', 'zh>vi', 'tones-cmn', 'Mandarin 2, initial m n l r y w or none → ngang', _all(MT(2), MSONI, YOPEN),
     HT('ngang'), None),
    ('T1', 'zh>vi', 'tones-cmn', 'Mandarin 2, other initial → huyền', _all(MT(2), MOBS, YOPEN), HT('huyền'), None),
    ('T2', 'zh>vi', 'tones-cmn', 'Mandarin 3, initial m n l r y w or none → ngã', _all(MT(3), MSONI), HT('ngã'), None),
    ('T2', 'zh>vi', 'tones-cmn', 'Mandarin 3, other initial → hỏi', _all(MT(3), MOBS), HT('hỏi'), None),
    ('T3', 'zh>vi', 'tones-cmn', 'Mandarin 4, not -p -t -k in Cantonese → sắc or nặng', _all(MT(4), YOPEN),
     HT('sắc', 'nặng'), 'ht'),
    # --- from the Vietnamese tone heard
    ('T5', 'vi>zh', 'tones-vi', 'huyền → Cantonese 4', HT('huyền'), YT(4), None),
    ('T5', 'vi>zh', 'tones-vi', 'ngang → Cantonese 1, or 4 after m n nh ng l v d', HT('ngang'),
     lambda f: None if f['yt'] is None else f['yt'] == 1 or (f['yt'] == 4 and f['son']), None),
    ('T5', 'vi>zh', 'tones-vi', 'hỏi → Cantonese 2', HT('hỏi'), YT(2), None),
    ('T5', 'vi>zh', 'tones-vi', 'ngã → Cantonese 5', HT('ngã'), YT(5), None),
    ('T5', 'vi>zh', 'tones-vi', 'ngã → Mandarin 3', HT('ngã'), MT(3), None),
    ('T5', 'vi>zh', 'tones-vi', 'sắc, open syllable → Cantonese 3', lambda f: not f['chk'] and f['ht'] == 'sắc', YT(3),
     None),
    ('T5', 'vi>zh', 'tones-vi', 'nặng, open syllable → Cantonese 6', lambda f: not f['chk'] and f['ht'] == 'nặng', YT(6),
     None),
    ('T5', 'vi>zh', 'tones-vi', 'nặng, open syllable → Mandarin 4', lambda f: not f['chk'] and f['ht'] == 'nặng', MT(4),
     None),
    ('T4f', 'fact', 'tones-vi', 'a syllable in -p -t -c -ch has sắc or nặng (a fact of Vietnamese spelling)',
     lambda f: f['chk'], HT('sắc', 'nặng'), None),
    # --- finals
    ('B1', 'zh>vi', 'finals', 'Cantonese -p → -p', _is('ycoda', 'p'), lambda f: f['coda'] == 'p', None),
    ('B1', 'zh>vi', 'finals', 'Cantonese -t → -t', _is('ycoda', 't'), lambda f: f['coda'] == 't', None),
    ('B1', 'zh>vi', 'finals', 'Cantonese -k → -c / -ch', _is('ycoda', 'k'), lambda f: f['coda'] in ('c', 'ch'), 'coda'),
    ('B2', 'zh>vi', 'finals', 'Cantonese -m → -m', _is('ycoda', 'm'), lambda f: f['coda'] == 'm', None),
    ('B2', 'zh>vi', 'finals', 'Taigi -m → -m', lambda f: None if f['nr'] is None else f['nr'].endswith('m'),
     lambda f: f['coda'] == 'm', None),
    ('B3', 'vi>zh', 'finals', 'Hán-Việt -nh / -ch → Cantonese -ng / -k', lambda f: f['coda'] in ('nh', 'ch'),
     lambda f: None if f['ycoda'] is None else f['ycoda'] in ('ng', 'k'), None),
    ('B4', 'zh>vi', 'finals', 'Mandarin -ing → -nh', _is('mr', 'ing'), lambda f: f['coda'] == 'nh', None),
    ('B3x', 'drop', 'finals', 'Cantonese -ing / -ik → -nh / -ch', _is('yr', 'ing', 'ik'),
     lambda f: f['coda'] in ('nh', 'ch'), None),
    ('V1', 'zh>vi', 'finals', 'Cantonese -oeng / -oek → -ương / -ươc', _is('yr', 'oeng', 'oek'),
     lambda f: 'ươ' in f['hr'], None),
    ('V2', 'zh>vi', 'finals', 'Cantonese -in / -it → -iên / -iêt', _is('yr', 'in', 'it'),
     lambda f: 'iê' in f['hr'] or 'yê' in f['hr'], None),
    # --- initials: labials 幫滂並 / 非敷奉 / 明微
    ('IP', 'zh>vi', 'labials', 'ph ← Mandarin f-', MI('f'), HV('ph'), None),
    ('IP', 'zh>vi', 'labials', 'b ← Mandarin b-', MI('b'), HV('b'), None),
    ('IP', 'zh>vi', 'labials', 'b ← Taigi p-', NI('p'), HV('b'), None),
    ('IP', 'vi>zh', 'labials', 'ph → Mandarin f- or p-', HV('ph'), MI('f', 'p'), 'mi'),
    ('IP', 'vi>zh', 'labials', 'b → Mandarin b- or p-', HV('b'), MI('b', 'p'), 'mi'),
    ('IM', 'zh>vi', 'labials', 'm ← Mandarin m-', MI('m'), HV('m'), None),
    ('IM', 'vi>zh', 'labials', 'm → Mandarin m-', HV('m'), MI('m'), None),
    ('IM', 'zh>vi', 'labials', 'v ← Cantonese m- with Mandarin w-', _all(YI('m'), MI('w')), HV('v'), None),
    ('IM', 'zh>vi', 'labials', 'v ← Mandarin w- (alone)', MI('w'), HV('v'), None),
    ('IM', 'vi>zh', 'labials', 'v → Mandarin w- or y-', HV('v'), MI('w', 'y'), 'mi'),
    # dentals 端透定 / 泥來
    ('ID', 'zh>vi', 'dentals', 'đ ← Mandarin d-', MI('d'), HV('đ'), None),
    ('ID', 'zh>vi', 'dentals', 'đ ← Mandarin t- in tone 2', _all(MI('t'), MT(2)), HV('đ'), None),
    ('ID', 'zh>vi', 'dentals', 'th ← Mandarin t- in tones 1 3 4', _all(MI('t'), MT(1, 3, 4)), HV('th'), None),
    ('ID', 'zh>vi', 'dentals', 'đ ← Taigi t- with Mandarin d- / t-', _all(NI('t'), MI('d', 't')), HV('đ'), None),
    ('ID', 'vi>zh', 'dentals', 'đ → Mandarin d- or t-', HV('đ'), MI('d', 't'), 'mi'),
    ('ID', 'zh>vi', 'dentals', 'n ← Mandarin n-', MI('n'), HV('n'), None),
    ('ID', 'zh>vi', 'dentals', 'l ← Mandarin l-', MI('l'), HV('l'), None),
    ('ID', 'vi>zh', 'dentals', 'n → Mandarin n-', HV('n'), MI('n'), None),
    ('ID', 'vi>zh', 'dentals', 'l → Mandarin l-', HV('l'), MI('l'), None),
    ('ID', 'zh>vi', 'dentals', 'Taigi l- → l or n (Mandarin decides)', NI('l'), HV('l', 'n'), 'hi'),
    # retroflex series 知徹澄 / 莊初崇生 / 章昌船書禪
    ('IR', 'zh>vi', 'retroflex', 'ch or tr ← Mandarin zh-', MI('zh'), HV('ch', 'tr'), 'hi'),
    ('IR', 'zh>vi', 'retroflex', 'tr ← Mandarin zh- / ch- with Taigi t- / th-', _all(MI('zh', 'ch'), NI('t', 'th')),
     HV('tr'), None),
    ('IR', 'zh>vi', 'retroflex', 'ch ← Mandarin zh- with Taigi ts-', _all(MI('zh'), NI('ts')), HV('ch'), None),
    ('IR', 'vi>zh', 'retroflex', 'ch → Mandarin zh-', HV('ch'), MI('zh'), None),
    ('IR', 'vi>zh', 'retroflex', 'tr → Mandarin zh- or ch-', HV('tr'), MI('zh', 'ch'), 'mi'),
    ('IR', 'zh>vi', 'retroflex', 'th or s ← Mandarin sh-', MI('sh'), HV('th', 's'), 'hi'),
    ('IR', 'zh>vi', 'retroflex', 'x or s ← Mandarin ch- in tones 1 3 4', _all(MI('ch'), MT(1, 3, 4)), HV('x', 's'),
     'hi'),
    ('IR', 'zh>vi', 'retroflex', 'x ← Mandarin ch- in tones 1 3 4 with Taigi tsh-', _all(MI('ch'), MT(1, 3, 4), NI('tsh')),
     HV('x'), None),
    ('IR', 'zh>vi', 'retroflex', 'tr or th ← Mandarin ch- in tone 2', _all(MI('ch'), MT(2)), HV('tr', 'th'), 'hi'),
    ('IR', 'zh>vi', 'retroflex', 'tr ← Mandarin ch- in tone 2 with Taigi t-', _all(MI('ch'), MT(2), NI('t')), HV('tr'),
     None),
    ('IR', 'zh>vi', 'retroflex', 'th ← Mandarin ch- in tone 2 with Taigi s- / tsh-', _all(MI('ch'), MT(2),
                                                                                         NI('s', 'tsh')), HV('th'), None),
    ('IR', 'vi>zh', 'retroflex', 'x → Mandarin ch-', HV('x'), MI('ch'), None),
    ('IR', 'vi>zh', 'retroflex', 's → Mandarin sh- or ch-', HV('s'), MI('sh', 'ch'), 'mi'),
    # dental sibilants 精清從心邪
    ('IS', 'zh>vi', 'sibilants', 't ← Mandarin z-', MI('z'), HV('t'), None),
    ('IS', 'zh>vi', 'sibilants', 't or th ← Mandarin j q x with Cantonese z c s', _all(MI('j', 'q', 'x'),
                                                                                     YI('z', 'c', 's')),
     HV('t', 'th'), 'hi'),
    ('IS', 'zh>vi', 'sibilants', 't ← Mandarin z c s j q x with Cantonese z c s and Taigi ts- / s-',
     _all(MI('z', 'c', 's', 'j', 'q', 'x'), YI('z', 'c', 's'), NI('ts', 's')), HV('t'), None),
    ('IS', 'zh>vi', 'sibilants', 'th ← Mandarin z c s j q x with Cantonese z c s and Taigi tsh-',
     _all(MI('z', 'c', 's', 'j', 'q', 'x'), YI('z', 'c', 's'), NI('tsh')), HV('th'), None),
    ('IS', 'vi>zh', 'sibilants', 't → Mandarin z c s j q x', HV('t'), MI('z', 'c', 's', 'j', 'q', 'x'), 'mi'),
    ('IS', 'vi>zh', 'sibilants', 't + i y ê iê ư ươ → Mandarin j q x', _all(HV('t'), _is('front', True)),
     MI('j', 'q', 'x'), 'mi'),
    ('IS', 'vi>zh', 'sibilants', 't + other vowels → Mandarin z c s', _all(HV('t'), _is('front', False)),
     MI('z', 'c', 's'), 'mi'),
    ('IS', 'vi>zh', 'sibilants', 't → Cantonese z c s', HV('t'), YI('z', 'c', 's'), 'yi'),
    # velars 見溪群 / 疑 / 曉匣
    ('IK', 'zh>vi', 'velars', 'c / k / q ← Mandarin g-', MI('g'), HV('c'), None),
    ('IK', 'zh>vi', 'velars', 'c / k / q or gi ← Taigi k-', NI('k'), HV('c', 'gi'), 'hi'),
    ('IK', 'zh>vi', 'velars', 'c, kh, h or gi ← Mandarin j q x with Cantonese g k h', _all(MI('j', 'q', 'x'),
                                                                                         YI('g', 'k', 'gw', 'kw', 'h', 'f')),
     HV('c', 'kh', 'h', 'gi'), 'hi'),
    ('IK', 'zh>vi', 'velars', 'gi ← Mandarin j- with Cantonese g- + aa / o',
     lambda f: None if f['mi'] is None or f['yi'] is None or f['yr'] is None else
     f['mi'] == 'j' and f['yi'] == 'g' and f['yr'][:2] in ('aa', 'ok', 'on'), HV('gi'), None),
    ('IK', 'zh>vi', 'velars', 'c ← Mandarin j- / q- with Cantonese g- / k- (not + aa / o)',
     lambda f: None if f['mi'] is None or f['yi'] is None or f['yr'] is None else
     f['mi'] in ('j', 'q') and f['yi'] in ('g', 'k', 'gw', 'kw') and f['yr'][:2] not in ('aa', 'ok', 'on'), HV('c'), None),
    ('IK', 'zh>vi', 'velars', 'kh ← Cantonese h- / f- with Mandarin k- / q-', _all(YI('h', 'f'), MI('k', 'q')), HV('kh'),
     None),
    ('IK', 'zh>vi', 'velars', 'kh ← Taigi kh-', NI('kh'), HV('kh'), None),
    ('IK', 'vi>zh', 'velars', 'c / k / q → Mandarin g j k q', HV('c'), MI('g', 'j', 'k', 'q'), 'mi'),
    ('IK', 'vi>zh', 'velars', 'c / k / q + i y ê iê ư ươ → Mandarin j q', _all(HV('c'), _is('front', True)),
     MI('j', 'q'), 'mi'),
    ('IK', 'vi>zh', 'velars', 'c / k / q + other vowels → Mandarin g k', _all(HV('c'), _is('front', False)),
     MI('g', 'k'), 'mi'),
    ('IK', 'vi>zh', 'velars', 'c / k / q → Taigi k-', HV('c'), NI('k'), None),
    ('IK', 'vi>zh', 'velars', 'kh → Mandarin k- or q-', HV('kh'), MI('k', 'q'), 'mi'),
    ('IK', 'vi>zh', 'velars', 'kh → Taigi kh-', HV('kh'), NI('kh'), None),
    ('IK', 'vi>zh', 'velars', 'gi → Mandarin j- with Cantonese g-', HV('gi'), _all(MI('j'), YI('g')), None),
    ('IG', 'zh>vi', 'velars', 'ng / ngh ← Taigi g-', NI('g'), HV('ng'), None),
    ('IG', 'vi>zh', 'velars', 'ng / ngh → Taigi g-', HV('ng'), NI('g'), None),
    ('IH', 'zh>vi', 'velars', 'h ← Mandarin h- / x- with Cantonese h- / f- / w- / j-', _all(MI('h', 'x'),
                                                                                        YI('h', 'f', 'w', 'j')),
     HV('h'), None),
    ('IH', 'zh>vi', 'velars', 'Taigi h- → h, but ph when Mandarin has f-',
     lambda f: None if f['ni'] is None or f['mi'] is None else f['ni'] == 'h',
     lambda f: f['hi'] == ('ph' if f['mi'] == 'f' else 'h'), None),
    ('IH', 'vi>zh', 'velars', 'h → Mandarin h- or x-', HV('h'), MI('h', 'x'), 'mi'),
    ('IH', 'vi>zh', 'velars', 'h → Taigi h-', HV('h'), NI('h'), None),
    # 影云以日: no initial, v, d, nh
    ('IY', 'zh>vi', 'glides', 'nh ← Mandarin r-', MI('r'), HV('nh'), None),
    ('IY', 'vi>zh', 'glides', 'nh → Mandarin r-, y- or none', HV('nh'), MI('r', 'y', ''), 'mi'),
    ('IY', 'zh>vi', 'glides', 'nh ← Taigi j-', NI('j'), HV('nh'), None),
    ('IY', 'zh>vi', 'glides', 'd ← Mandarin y- with Cantonese j- in tone 4 5 6, Taigi no initial',
     _all(MI('y'), YI('j'), YT(4, 5, 6), NI('')), HV('d'), None),
    ('IY', 'vi>zh', 'glides', 'd → Mandarin y-', HV('d'), MI('y'), None),
    ('IY', 'vi>zh', 'glides', 'd → Cantonese j-', HV('d'), YI('j'), None),
    ('IY', 'zh>vi', 'glides', 'no initial ← Mandarin y- / w- / none with Cantonese j- / w- / none in tone 1 2 3',
     _all(MI('y', 'w', ''), YI('j', 'w', ''), YT(1, 2, 3)), HV(''), None),
    ('IY', 'vi>zh', 'glides', 'no initial → Mandarin y-, w- or none', HV(''), MI('y', 'w', ''), 'mi'),
    ('IY', 'fact', 'glides', 'no Hán-Việt syllable starts with r', lambda f: True, lambda f: f['hi'] != 'r', None),
    # aspiration, across the classes
    ('IA', 'zh>vi', 'aspiration', 'Cantonese p t k kw c in tone 4 / 5 → b đ c t tr ch gi (old voiced)',
     _all(YI('p', 't', 'k', 'kw', 'c'), YT(4, 5)), HV(*UNASP), 'hi'),
    ('IA', 'zh>vi', 'aspiration', 'Mandarin p t k q c ch in tone 2 → b đ c t tr ch gi (old voiced)',
     _all(MI('p', 't', 'k', 'q', 'c', 'ch'), MT(2)), HV(*UNASP), 'hi'),
    ('IA', 'zh>vi', 'aspiration', 'Mandarin p t k q c ch in tones 1 3 4 → ph th kh x s',
     _all(MI('p', 't', 'k', 'q', 'c', 'ch'), MT(1, 3, 4)), HV(*ASP), 'hi'),
    # spelling what Hà Nội merges (he hears the sound: [z] is d or gi, [c] ch or tr, [s] s or x)
    ('Z1', 'spell', 'spelling', 'd or gi: gi when Cantonese has g-', *_spell(('gi', 'd'), YI('g')), None),
    ('Z1', 'spell', 'spelling', 'd or gi: gi when Mandarin has j-', *_spell(('gi', 'd'), MI('j')), None),
    ('Z2', 'spell', 'spelling', 'tr or ch: ch when Taigi has ts-', *_spell(('ch', 'tr'), NI('ts')), None),
    ('Z3', 'spell', 'spelling', 's or x: x when Mandarin has ch-', *_spell(('x', 's'), MI('ch')), None),
    ('Z3', 'spell', 'spelling', 's or x: x when Taigi has tsh-', *_spell(('x', 's'), NI('tsh')), None),
    # the first proposal's initials, measured and dropped
    ('I1x', 'drop', 'dropped', 'kh ← Cantonese h-', YI('h'), HV('kh'), None),
    ('I2x', 'drop', 'dropped', 'ph ← Cantonese f- (replaced by ph ← Mandarin f-, which misses one)', YI('f'), HV('ph'),
     None),
    ('I3x', 'drop', 'dropped', 'v ← Cantonese m- (replaced by v ← Cantonese m- with Mandarin w-)', YI('m'), HV('v'),
     None),
    ('I4x', 'drop', 'dropped', 'gi ← Mandarin j-', MI('j'), HV('gi'), None),
    ('I7x', 'drop', 'dropped', 'd ← Mandarin y-', MI('y'), HV('d'), None),
]


def _ev(fn, f):
    try:
        return fn(f)
    except (TypeError, AttributeError, KeyError):
        return None


def measure(data, show=8):
    """[{id, way, group, text, hit, tot, exc, strict (hit, tot), lenient (hit, tot), best (outcome, n), changed}] for
    every rule: main reading (main_features), strict and lenient over the candidate combinations (combo_features)."""
    mains = [d.get('_f') or main_features(d) for d in data]
    combos = [d.get('_c') or combo_features(d) for d in data]
    out = []
    for rid, way, group, text, cond, pred, okey in RULES:
        hit = tot = 0
        exc, outcomes = [], collections.Counter()
        changed = 0
        for d, f in zip(data, mains):
            if not _ev(cond, f):
                continue
            p = _ev(pred, f)
            if p is None:
                continue
            tot += 1
            if okey:
                outcomes[f[okey]] += 1
            if p:
                hit += 1
            else:
                exc.append(f"{f['ch']} {f['hv']}")
            if d.get('yue_changed'):
                changed += 1
        sh = st = lh = 0
        for cs in combos:
            ps = [_ev(pred, x) for x in cs if _ev(cond, x)]
            ps = [x for x in ps if x is not None]
            if not ps:
                continue
            st += 1
            sh += all(ps)
            lh += any(ps)
        best = outcomes.most_common(1)[0] if outcomes else None
        out.append({'id': rid, 'way': way, 'group': group, 'text': text, 'hit': hit, 'tot': tot, 'exc': exc[:show],
                    'strict': (sh, st), 'lenient': (lh, st), 'best': best, 'changed': changed})
    return out


def kind(way, hit, tot, best=None):
    """How the syllabus may teach a measured rule (on the MAIN rate): 'rule' at 80 % or more, 'tendency' from 60 %,
    else 'drop'; a multi-outcome rule whose best single guess is under 60 % 'narrows' (it narrows the choice to its
    letters, it does not predict one); a fact of spelling is 'fact'."""
    if way == 'drop' or not tot:
        return 'drop'
    if way == 'fact':
        return 'fact'
    r = hit / tot
    k = 'rule' if r >= 0.795 else 'tendency' if r >= 0.595 else 'drop'
    if k != 'drop' and best and best[1] / tot < 0.595:
        return 'narrows'
    return k


def pct(a, b):
    return f'{a} / {b}, {100 * a / b:.0f} %' if b else '—'


def _best(m):
    if not m['best']:
        return ''
    o, n = m['best']
    return f"{o or 'none'} {100 * n / m['tot']:.0f} %"


def kind_cell(m):
    """The kind in bold; beside a rule or tendency of several outcomes whose best single guess is under 80 %, that
    guess, so a "rule" of "tr or th" (tr 61 %) is not read as a prediction of one letter (review 4, C)."""
    k = kind(m['way'], m['hit'], m['tot'], m['best'])
    cell = f'**{k}**'
    if k in ('rule', 'tendency') and m['best'] and m['best'][1] < m['hit'] and m['best'][1] / m['tot'] < 0.795:
        cell += f' (one guess: {_best(m)})'
    return cell


GROUP_TITLES = {'tones-yue': 'From Cantonese (zh→vi)', 'tones-nan': 'From Taigi (zh→vi)',
                'tones-cmn': 'From Mandarin (zh→vi)', 'tones-vi': 'From the Vietnamese tone heard (vi→zh)'}
WAY = {'zh>vi': 'zh→vi', 'vi>zh': 'vi→zh', 'spell': 'spell', 'fact': 'fact', 'drop': 'dropped'}


def table(ms, group):
    rows = [m for m in ms if m['group'] == group]
    out = ['| Id | Rule | Dir | Main | Strict | Lenient | Best single guess | Kind | Main exceptions |',
           '|---|---|---|---|---|---|---|---|---|']
    for m in rows:
        out.append(f"| {m['id']} | {m['text']} | {WAY[m['way']]} | {pct(m['hit'], m['tot'])} | {pct(*m['strict'])} | "
                   f"{pct(*m['lenient']) if m['way'] == 'vi>zh' else ''} | {_best(m)} | "
                   f"{kind_cell(m)} | {' '.join(m['exc']) or '—'} |")
    ch = sum(m['changed'] for m in rows if m['id'] == 'T*')
    if group == 'tones-yue' and ch:
        out.append('')
        out.append(f'Changed tones: {ch} items of the Cantonese total have a changed tone (變音: 錢 cin2, 社會 se5 wui2) '
                   'in the word; the main rate uses the base tone (cin4, wui6), as the tones of Hán-Việt do; the strict '
                   'rate counts the changed tone too.')
    return '\n'.join(out)


def summary(ms):
    """Counts of kinds and the headline tone rates, for the proposal and the report."""
    c = collections.Counter(kind(m['way'], m['hit'], m['tot'], m['best']) for m in ms)
    star = {m['text']: m for m in ms if m['id'] == 'T*'}
    yue = next(m for t, m in star.items() if 'Cantonese' in t)
    nan = next(m for t, m in star.items() if 'Taigi' in t)
    return (f"{len(ms)} measured: {c['rule']} rules, {c['tendency']} tendencies, {c['narrows']} that narrow the choice, "
            f"{c['fact']} facts of spelling, {c['drop']} dropped. Every tone from Cantonese: main "
            f"{pct(yue['hit'], yue['tot'])}, strict {pct(*yue['strict'])}; from Taigi: main {pct(nan['hit'], nan['tot'])}, "
            f"strict {pct(*nan['strict'])}.")


def render(con):
    data = items(con)
    for d in data:
        d['_f'], d['_c'] = main_features(d), combo_features(d)
    ms = measure(data)
    words = {w for d in data for w in d['words']}
    head = f'{len(data)} syllables (character + Hán-Việt reading) of {len(words)} Hán-Việt cards of rank <= {TOP}'
    groups = {g: table(ms, g) for g in dict.fromkeys(m['group'] for m in ms)}
    groups['summary'] = head + '. ' + summary(ms)
    return groups, ms, data


def rewrite(text, groups):
    def sub(m):
        g = m.group(1)
        if g not in groups:
            raise SystemExit(f'bridge_rules: unknown rules group {g!r}')
        return f'<!-- rules:{g} -->\n{groups[g]}\n<!-- /rules -->'
    return re.sub(r'<!-- rules:([\w-]+) -->.*?<!-- /rules -->', sub, text, flags=re.S)


def check_examples(path):
    """The chữ Hán of the bridge-examples blocks of `path`, each through lint's bridge-note test, with the Vietnamese
    syllables written after it (平 bình) as the word it is paired with."""
    import lint
    lint.D = lint.DB_(lint.DB)
    text = open(path, encoding='utf-8').read()
    blocks = ''.join(re.findall(r'<!-- bridge-examples -->(.*?)<!-- /bridge-examples -->', text, re.S))
    pairs = list(dict.fromkeys(lint.cjk_pairs(blocks)))
    bad = [(r, w, lint.D.bridge_example(r, w)) for r, w in pairs]
    bad = [x for x in bad if x[2]]
    for r, w, why in bad:
        print(f'E bridge example {r} {w or ""}: {why}')
    print(f'{path}: {len(pairs)} bridge examples, {len(bad)} refused')
    return 1 if bad else 0


def main():
    if '--examples' in sys.argv:
        sys.exit(check_examples(sys.argv[sys.argv.index('--examples') + 1]))
    con = cards.open_db('public')
    groups, ms, data = render(con)
    for flag in ('--write', '--check'):
        if flag in sys.argv:
            path = sys.argv[sys.argv.index(flag) + 1]
            old = open(path, encoding='utf-8').read()
            new = rewrite(old, groups)
            if flag == '--write':
                open(path, 'w', encoding='utf-8').write(new)
                print(f'{path}: rule tables {"rewritten" if new != old else "unchanged"}')
                return 0
            if new != old:
                print(f'E {path}: its rule tables are not the measured ones: run tools/bridge_rules.py --write {path}')
                return 1
            print(f'{path}: rule tables agree with the measure')
            return 0
    print(groups['summary'] + '\n')
    for g, t in groups.items():
        if g != 'summary':
            print(f'## {g}\n\n{t}\n')
    if '--json' in sys.argv:
        json.dump([{k: v for k, v in d.items() if not k.startswith('_')} for d in data],
                  open(sys.argv[sys.argv.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False)
    return 0


if __name__ == '__main__':
    sys.exit(main())
