"""Sound correspondences between a Hán-Việt syllable and a Cantonese, Taigi or Mandarin reading, MEASURED on the
database (review 3, finding 6): which of a polyphonic character's readings is the one of the word on the card.

    import soundfit
    soundfit.order(con, 'hàng', 'yue', ['hang4', 'hong4', 'haang4', 'hang6'])   # ['hong4', 'hang4', 'haang4', 'hang6']

The table: every Sino-Vietnamese word of two or more characters (Wiktionary analysis, every syllable a Hán-Việt
reading of its character: entry.hv_check ok) whose characters the Chinese source has AS A WORD (rime-cantonese, the
MOE, CC-CEDICT) gives, for each of its characters, a pair (Hán-Việt syllable, the word's own reading of that
character): no polyphonic character is guessed. Counted per language: initial against initial, final (rhyme without
tone) against final, Hán-Việt tone against Chinese tone. A reading's score is the sum of the three log-probabilities
P(Chinese part | Hán-Việt part) with add-half smoothing; the best-scoring reading comes first; equal scores keep the
source's own order (rime's share, the MOE's order, Unihan kMandarin then CC-CEDICT use: tools/build_db.py
rank_chinese). The same split functions serve tools/bridge_rules.py (the syllabus's sound rules).
"""
import math
import re
import unicodedata

HV_ON = ('ngh', 'ng', 'nh', 'ch', 'tr', 'th', 'ph', 'kh', 'gh', 'gi', 'qu', 'đ', 'd', 'b', 'c', 'k', 'g', 'h', 'l', 'm',
         'n', 'r', 's', 't', 'v', 'x')
ON = {'yue': ('gw', 'kw', 'ng', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'w', 'z', 'c', 's', 'j'),
      'nan': ('tsh', 'ts', 'ph', 'th', 'kh', 'ng', 'p', 'b', 'm', 't', 'n', 'l', 'k', 'g', 'h', 'j', 's'),
      'cmn': ('zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's',
              'y', 'w')}
TONE = {1: 'ngang', 2: 'huyền', 3: 'sắc', 4: 'hỏi', 5: 'ngã', 6: 'nặng'}
_HV_TONE = {'̀': 'huyền', '́': 'sắc', '̉': 'hỏi', '̃': 'ngã', '̣': 'nặng'}


def marks_off(s, keep=''):
    d = unicodedata.normalize('NFD', s.lower())
    return unicodedata.normalize('NFC', ''.join(c for c in d if unicodedata.category(c) != 'Mn' or c in keep))


def hv_split(s):
    """(initial, rhyme) of a Hán-Việt syllable, the rhyme with its vowel marks (ă â ê ô ơ ư) and without tone; c/k/q
    are one initial c, gh g, ngh ng; gi before a consonant is g + i…"""
    b = marks_off(s, '̛̆̂')
    for o in HV_ON:
        if b.startswith(o):
            rest = b[len(o):]
            if o == 'gi' and rest and rest[0] not in 'aăâeêioôơuưy':
                return 'g', b[1:]
            if o == 'qu':
                return 'c', 'u' + rest
            return {'k': 'c', 'gh': 'g', 'ngh': 'ng'}.get(o, o), rest
    return '', b


def hv_tone(s):
    d = unicodedata.normalize('NFD', s.lower())
    return next((t for m, t in _HV_TONE.items() if m in d), 'ngang')


def split(lang, r):
    """(initial, final) of a Jyutping, Tâi-lô or pinyin syllable, lower case, without tone."""
    s = re.sub(r'\d', '', r.lower()) if lang == 'yue' else marks_off(r).replace('ü', 'v')
    for o in ON[lang]:
        if s.startswith(o):
            return o, s[len(o):]
    return '', s


def tone(lang, r):
    """Cantonese 1-6, Taigi 1-8 (Tâi-lô marks; 4 and 8 checked), Mandarin 1-4 (0 neutral)."""
    if lang == 'yue':
        m = re.search(r'\d', r)
        return int(m.group()) if m else None
    d = unicodedata.normalize('NFD', r)
    if lang == 'cmn':
        return next((t for m, t in (('̄', 1), ('́', 2), ('̌', 3), ('̀', 4)) if m in d), 0)
    for m, t in (('̍', 8), ('́', 2), ('̀', 3), ('̂', 5), ('̄', 7), ('̌', 6)):
        if m in d:
            return t
    return 4 if marks_off(r)[-1:] in 'ptkh' else 1


def split_pinyin(word, per_char):
    """A CC-CEDICT word reading without spaces ("xuésheng") cut at the characters' own readings (per_char: [[readings
    of character 1], …]), or None."""
    w, out, pos = word.replace("'", '').replace(' ', ''), [], 0
    for rs in per_char:
        for r in sorted(set(rs), key=len, reverse=True):
            seg = w[pos:pos + len(r)]
            if marks_off(seg, '̈') == marks_off(r, '̈'):
                out.append(seg)
                pos += len(seg)
                break
        else:
            return None
    return out if pos == len(w) else None


def word_syllables(lang, reading, per_char):
    if lang == 'yue':
        p = reading.split()
    elif lang == 'nan':
        p = [x for x in re.split(r'[- ]+', reading) if x]
    else:
        p = split_pinyin(reading, per_char)
    return p if p and len(p) == len(per_char) else None


_TABLES = {}


def table(con):
    """{lang: {'i'|'f'|'t': {hv part: Counter(chinese part)}}} measured on the database (module docstring)."""
    key = id(con)
    if key in _TABLES:
        return _TABLES[key]
    from collections import Counter, defaultdict
    t = {lang: {x: defaultdict(Counter) for x in 'ift'} for lang in ON}
    char_r = defaultdict(list)
    for ch, lang, r in con.execute("SELECT chars, lang, reading FROM chinese WHERE level='char' AND note != 'name' "
                                   "AND source != 'fixture'"):
        char_r[(ch, lang)].append(r)
    words = {}
    for chars, lang, r in con.execute("SELECT chars, lang, reading FROM chinese WHERE level='word' AND note != 'name' "
                                      "AND source != 'fixture' ORDER BY rank, ord"):
        words.setdefault((chars, lang), r)
    for k, chars in con.execute("SELECT DISTINCT key, chars FROM entry WHERE origin='sino' AND hv_check='ok' AND "
                                "length(chars) > 1 AND source != 'fixture'"):
        syl = k.split()
        if len(syl) != len(chars):
            continue
        for lang in ON:
            wr = words.get((chars, lang))
            if not wr:
                continue
            parts = word_syllables(lang, wr, [char_r.get((c, lang), []) for c in chars])
            if not parts:
                continue
            for s, p in zip(syl, parts):
                hi, hr = hv_split(s)
                ci, cf = split(lang, p)
                t[lang]['i'][hi][ci] += 1
                t[lang]['f'][hr][cf] += 1
                t[lang]['t'][hv_tone(s)][tone(lang, p)] += 1
    _TABLES[key] = t
    return t


def score(con, hv, lang, r):
    """log P(initial) + log P(final) + log P(tone) of reading `r` given the Hán-Việt syllable `hv` (add-half
    smoothing over the parts seen with that Hán-Việt part)."""
    t = table(con)[lang]
    hi, hr = hv_split(hv)
    ci, cf = split(lang, r)
    out = 0.0
    for part, a, b in (('i', hi, ci), ('f', hr, cf), ('t', hv_tone(hv), tone(lang, r))):
        c = t[part].get(a)
        n = sum(c.values()) if c else 0
        out += math.log(((c[b] if c else 0) + 0.5) / (n + 0.5 * (len(c) + 1 if c else 1)))
    return out


def order(con, hv, lang, readings):
    """`readings` (in the source's order) with the one that best fits the Hán-Việt syllable `hv` first; equal scores
    keep the source's order."""
    if len(readings) < 2 or not hv:
        return list(readings)
    sc = {r: score(con, hv, lang, r) for r in readings}
    # a Mandarin neutral-tone reading (過 guo) is never a character's citation reading: last
    return sorted(readings, key=lambda r: (lang == 'cmn' and tone('cmn', r) == 0, -round(sc[r], 6), readings.index(r)))
