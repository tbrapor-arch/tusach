"""The bridge join on characters (handover section 5): for the chữ Hán of a Sino-Vietnamese word, its Hán-Việt
readings and the same word in Cantonese (Jyutping), Taigi (Tâi-lô) and Mandarin (pinyin).

    import bridge
    bridge.join(con, '學生')   # {'hv': '學 học · 生 sinh/sanh', 'yue': 'hok6 saang1', 'yue_by': 'word', 'nan': …, 'n': 3}

For each language: when the source has the characters as one word, all its readings of that word ('/' between them,
in the source's order). Otherwise the word is built character by character from every reading of each character
(`by` = 'char', as for a single character); a character with several readings shows them all in brackets, main
reading first, so nothing is chosen silently: 'hok6 (saang1/sang1)'. When the source lacks the word and one of its
characters, the language is missing ('' and by ''). Used by tools/build_db.py (table `bridge`, coverage) and
tools/cards.py (word cards), so the card and the measurement agree.
"""
import re
import unicodedata

LANGS = ('yue', 'nan', 'cmn')
SEP = {'yue': ' ', 'nan': '-', 'cmn': ' '}

_TONE = {'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì', 'o': 'ōóǒò', 'u': 'ūúǔù', 'ü': 'ǖǘǚǜ'}


def pinyin_marks(numbered):
    """CC-CEDICT numbered pinyin -> tone marks: 'xue2 sheng5' -> 'xué sheng', 'lu:4' -> 'lǜ'."""
    out = []
    for syl in numbered.split():
        m = re.fullmatch(r'([A-Za-züÜ:v]+)([1-5])', syl)
        if not m:
            out.append(syl)
            continue
        s, t = m.group(1).replace('u:', 'ü').replace('U:', 'Ü').replace('v', 'ü'), int(m.group(2))
        if t < 5:
            low = s.lower()
            i = next((low.index(c) for c in 'ae' if c in low), None)
            if i is None:
                i = low.index('ou') if 'ou' in low else max((j for j, c in enumerate(low) if c in 'iouü'), default=None)
            if i is not None:
                v = _TONE[low[i]][t - 1]
                s = s[:i] + (v.upper() if s[i].isupper() else v) + s[i + 1:]
        out.append(s)
    # CC-CEDICT writes a word's syllables apart; pinyin writes them together
    return unicodedata.normalize('NFC', ''.join(out) if all(re.fullmatch(r'[^\W\d_]+', x) for x in out) else ' '.join(out))


def _rows(con, chars, lang, level):
    """Readings in display order: the main ones, then by the source's share, names last. The test fixture's rows are
    used only where no real source has the characters."""
    rows = con.execute(
        "SELECT c.reading, s.fixture FROM chinese c JOIN source s ON s.id = c.source WHERE c.chars=? AND c.lang=? "
        "AND c.level=? ORDER BY (c.note='name'), c.share IS NOT NULL, c.share DESC, c.ord", (chars, lang, level)).fetchall()
    real = [r for r, fx in rows if not fx]
    return real or [r for r, _ in rows]


def _uniq(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def lang_reading(con, chars, lang):
    """(reading shown, how: 'word' | 'char' | '')."""
    if len(chars) > 1:
        w = _uniq(_rows(con, chars, lang, 'word'))
        if w:
            return ' / '.join(w), 'word'
    per = []
    for ch in chars:
        rs = _uniq(_rows(con, ch, lang, 'char') or _rows(con, ch, lang, 'word'))
        if not rs:
            return '', ''
        per.append(rs[0] if len(rs) == 1 else ('(' + '/'.join(rs) + ')' if len(chars) > 1 else ' / '.join(rs)))
    return SEP[lang].join(per), 'char'


def hv_readings(con, ch):
    """Hán-Việt readings of one character, Wiktionary's first, then Thiều Chửu's (kind hv only)."""
    rows = con.execute("SELECT h.reading, s.fixture FROM hanviet h JOIN source s ON s.id = h.source WHERE h.char=? "
                       "AND h.kind='hv' ORDER BY h.source != 'wiktionary', h.ord", (ch,)).fetchall()
    return _uniq([r for r, fx in rows if not fx] or [r for r, _ in rows])


def join(con, chars):
    out = {'hv': ' · '.join(f"{c} {'/'.join(hv_readings(con, c)) or '?'}" for c in chars), 'n': 0}
    for lang in LANGS:
        r, by = lang_reading(con, chars, lang)
        out[lang], out[lang + '_by'] = r, by
        out['n'] += bool(r)
    return out
