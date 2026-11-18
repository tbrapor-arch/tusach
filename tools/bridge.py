"""The bridge join on characters (handover section 5): for the chữ Hán of a Sino-Vietnamese word, its Hán-Việt
readings and the same word in Cantonese (Jyutping), Taigi (Tâi-lô) and Mandarin (pinyin).

    import bridge
    bridge.join(con, '學生')   # {'hv': '學 học · 生 sinh/sanh (Southern variant)', 'yue': 'hok6 saang1', 'yue_by': 'word',
                               #  'nan': 'ha̍k-sing', 'nan_by': 'word', 'nan_coll': '', 'cmn': 'xuéshēng', …, 'n': 3}

Cantonese and Mandarin: when the source has the characters as one word, all its readings of that word ('/' between
them, in display order). Otherwise the word is built character by character from every reading of each character
(`by` = 'char'); a character with several readings shows them all in brackets, main reading first, so nothing is
chosen silently: 'hok6 (saang1/sang1)'. When the source lacks the word and one of its characters, the language is
missing ('' and by '').

Taigi: the bridge column is the LITERARY (文讀) reading, because that is the layer that corresponds to Hán-Việt. It is
composed from the characters' literary readings (MOE 文白屬性 1, or 0 where the MOE makes no split). If the MOE's own
entry for the word reads it exactly so, it is attested (`nan_by` = 'word'). If the MOE word reading differs (生日
senn-ji̍t, 先生 sian-sinn: colloquial readings), it is never shown as literary: it goes to `nan_coll`, labelled
"colloquial / everyday" on the card, and the literary composition stays in `nan` (by character).

Mandarin: CC-CEDICT's traditional forms only; surname and place-name readings (capitalised) are left out when there
are others, unless the word is a name (a word CC-CEDICT has only as a name, 越南 Yuènán, is one); the order is Unihan kMandarin's customary reading first, then the number of CC-CEDICT words using the
reading (tools/build_db.py rank_chinese). Used by tools/build_db.py (table `bridge`, coverage) and tools/cards.py (word
cards), so the card and the measurement agree.
"""
import itertools
import re
import unicodedata

LANGS = ('yue', 'nan', 'cmn')
SEP = {'yue': ' ', 'nan': '-', 'cmn': ' '}
HV_LABEL = {'southern': 'Southern variant', 'derived': 'derived', 'fallback': 'unchecked, Unihan'}

_TONE = {'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì', 'o': 'ōóǒò', 'u': 'ūúǔù', 'ü': 'ǖǘǚǜ'}
_COMB = {1: '̄', 2: '́', 3: '̌', 4: '̀'}


def _syl_marks(syl):
    m = re.fullmatch(r'([A-Za-züÜ:v]+)([1-5])', syl)
    if not m:
        return syl
    s, t = m.group(1).replace('u:', 'ü').replace('U:', 'Ü').replace('v', 'ü'), int(m.group(2))
    if t == 5:
        return s
    low = s.lower()
    i = next((low.index(c) for c in 'ae' if c in low), None)
    if i is None:
        i = low.index('ou') if 'ou' in low else max((j for j, c in enumerate(low) if c in 'iouü'), default=None)
    if i is not None:
        v = _TONE[low[i]][t - 1]
        return s[:i] + (v.upper() if s[i].isupper() else v) + s[i + 1:]
    if low in ('m', 'n', 'ng', 'hm', 'hng'):            # syllabic nasals: 呣 m̄/ḿ, 嗯 ń/ňg; the mark on m or n
        j = low.index('m') if 'm' in low else low.index('n')
        return unicodedata.normalize('NFC', s[:j + 1] + _COMB[t] + s[j + 1:])
    return s


def pinyin_marks(numbered):
    """CC-CEDICT numbered pinyin -> tone marks: 'xue2 sheng5' -> 'xuésheng', 'lu:4' -> 'lǜ', 'nu:3 er2' -> "nǚ'ér"
    (the apostrophe before a, o, e inside a word), 'n2' -> 'ń', 'm2' -> 'ḿ'."""
    out = [_syl_marks(x) for x in numbered.split()]
    if not all(re.fullmatch(r'[^\W\d_]+', x) for x in out):
        return unicodedata.normalize('NFC', ' '.join(out))
    word = ''
    for i, x in enumerate(out):
        if i and unicodedata.normalize('NFD', x)[:1].lower() in ('a', 'o', 'e'):
            word += "'"
        word += x
    return unicodedata.normalize('NFC', word)


_TONE_MARKS = re.compile('[\u0300-\u036f]')


def coda_hv(r):
    """Coda class of a Hán-Việt reading: p, t, k (-c, -ch), m, n, ng (-ng, -nh), or v (a vowel or glide)."""
    r = unicodedata.normalize('NFD', r.lower())
    r = _TONE_MARKS.sub('', r)
    for end, cls in (('ch', 'k'), ('nh', 'ng'), ('ng', 'ng'), ('c', 'k'), ('p', 'p'), ('t', 't'), ('m', 'm'), ('n', 'n')):
        if r.endswith(end):
            return cls
    return 'v'


def coda_nan(r):
    """Coda class of a Tâi-lô syllable: p, t, k, h (glottal stop), m, n, ng, nn (nasal vowel), or v."""
    r = _TONE_MARKS.sub('', unicodedata.normalize('NFD', r.lower())).replace('ⁿ', 'nn')
    if r.endswith('h'):
        return 'h'
    for end, cls in (('nn', 'nn'), ('ng', 'ng'), ('p', 'p'), ('t', 't'), ('k', 'k'), ('m', 'm'), ('n', 'n')):
        if r.endswith(end):
            return cls
    return 'v'


# regular literary correspondences that change the coda class: labial dissimilation (凡 phàm / huân, 法 pháp / huat,
# 品 phẩm / phín) and Hokkien -k/-t crossings in the literary layer (直 trực / ti̍t, 室 thất / sik)
CODA_PAIRS = ({'m', 'n'}, {'p', 't'}, {'k', 't'})


def coda_agrees(hv_class, nan_class):
    """True when a Taigi reading's coda class can be the literary counterpart of a Hán-Việt coda class."""
    return hv_class == nan_class or {hv_class, nan_class} in CODA_PAIRS


def _rows(con, chars, lang, level, names=False):
    """Readings in display order (chinese.rank). Name readings (CC-CEDICT capitalised) are dropped when the source
    has other readings, unless the word is a name; a word the source has only as a name (越南, 西安) is a name.
    The test fixture's rows are used only where no real source has the characters."""
    rows = con.execute(
        "SELECT c.reading, s.fixture, c.note FROM chinese c JOIN source s ON s.id = c.source WHERE c.chars=? AND c.lang=? "
        "AND c.level=? ORDER BY c.rank, c.ord, c.reading", (chars, lang, level)).fetchall()
    if not names and any(r[2] != 'name' for r in rows):
        rows = [r for r in rows if r[2] != 'name']      # a surname or place reading is not the word's reading
    real = [r for r, fx, _ in rows if not fx]
    return real or [r for r, _, _ in rows]


def _uniq(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def _by_char(per, lang, n):
    return SEP[lang].join(rs[0] if len(rs) == 1 else ('(' + '/'.join(rs) + ')' if n > 1 else ' / '.join(rs))
                          for rs in per)


def variants(con, ch):
    """Variant forms of a character (Unihan kSemanticVariant / kZVariant, both directions): 爲 -> 為."""
    try:
        return [v for (v,) in con.execute('SELECT var FROM variant WHERE char=? ORDER BY var', (ch,))]
    except Exception:                                   # a database built before the table existed
        return []


def spellings(con, chars, limit=8):
    """The word's own characters first, then the same word with characters replaced by their variant forms (Wiktionary
    writes 行爲, 祕密, 墻; the Chinese sources 行為, 秘密, 牆): at most `limit` spellings."""
    opts = [[c] + variants(con, c) for c in chars]
    return [''.join(p) for p in itertools.islice(itertools.product(*opts), limit)]


def _nan_char(con, chars, colloquial=False):
    """A character's Taigi readings of one layer: literary (MOE 文讀, or unmarked readings whose coda agrees with
    Hán-Việt: tools/build_db.py taigi_layers) or, with colloquial=True, the unmarked readings found colloquial."""
    rows = con.execute("SELECT c.reading, s.fixture FROM chinese c JOIN source s ON s.id = c.source WHERE c.chars=? "
                       "AND c.lang='nan' AND c.level='char' AND (c.note = 'colloquial') = ? ORDER BY c.rank, c.ord, "
                       "c.reading", (chars, int(colloquial))).fetchall()
    real = [r for r, fx in rows if not fx]
    return real or [r for r, _ in rows]


def _char_rows(con, ch, lang, level_first, names=False, colloquial=False):
    """(readings, the form they were found under) of one character: its own, else a variant's."""
    for form in [ch] + variants(con, ch):
        if lang == 'nan':
            rs = _uniq(_nan_char(con, form, colloquial))
        else:
            rs = _uniq(_rows(con, form, lang, level_first, names) or
                       (_rows(con, form, lang, 'word', names) if level_first == 'char' else []))
        if rs:
            return rs, form
    return [], ch


def lang_reading(con, chars, lang, names=False):
    """(reading shown, how: 'word' | 'char' | '', the spelling it was found under) for Cantonese and Mandarin."""
    if len(chars) > 1:
        for sp in spellings(con, chars):
            w = _uniq(_rows(con, sp, lang, 'word', names))
            if w:
                return ' / '.join(w), 'word', sp
    per, forms = [], ''
    for ch in chars:
        rs, form = _char_rows(con, ch, lang, 'char', names)
        if not rs:
            return '', '', chars
        per.append(rs)
        forms += form
    return _by_char(per, lang, len(chars)), 'char', forms


def colloquial_only(con, chars):
    """The characters of `chars` that have a Taigi reading but no literary one (only readings found colloquial)."""
    return [ch for ch in chars if not _char_rows(con, ch, 'nan', 'char')[0]
            and _char_rows(con, ch, 'nan', 'char', colloquial=True)[0]]


def taigi(con, chars):
    """(literary reading, how: 'word' attested | 'char' composed | '', colloquial / everyday word reading or '', the
    spelling it was found under). A character with only colloquial readings (冊 tsheh) has no literary reading: the
    literary column is then empty, and the colloquial reading (the MOE word's, else composed with the colloquial
    reading of that character) is given as colloquial / everyday."""
    per, forms = [], ''
    coll_per = []
    for ch in chars:
        rs, form = _char_rows(con, ch, 'nan', 'char')
        if not rs:
            cr, _ = _char_rows(con, ch, 'nan', 'char', colloquial=True)
            if cr and coll_per is not None:
                coll_per.append(cr)
            else:
                coll_per = None
            per = None
            continue
        if coll_per is not None:
            coll_per.append(rs)
        if per is not None:
            per.append(rs)
            forms += form
    word, wsp = [], chars
    if len(chars) > 1:
        for sp in spellings(con, chars):
            word = _uniq(_rows(con, sp, 'nan', 'word'))
            if word:
                wsp = sp
                break
    if per is None:
        if not word and coll_per:
            word = [_by_char(coll_per, 'nan', len(chars))]
        return '', '', ' / '.join(word), wsp
    combos = {'-'.join(c).lower() for c in itertools.product(*per)} if len(chars) > 1 else set()
    attested = [w for w in word if w.lower() in combos]
    if attested:
        coll = [w for w in word if w.lower() not in combos]
        return attested[0], 'word', ' / '.join(coll), wsp
    return _by_char(per, 'nan', len(chars)), 'char', ' / '.join(word), forms


def hv_readings(con, ch, labels=False):
    """Hán-Việt readings of one character in display order: the Northern standard first, the most used first (hanviet.use:
    how many Sino-Vietnamese words read it so; then Wiktionary, Thiều Chửu or the Northern form derived from a Southern
    one), Southern variants after; when no Hán-Việt source reads the
    character, Unihan's readings of Hán-Việt shape. labels=True: [(reading, label)]."""
    rows = con.execute(
        "SELECT h.reading, s.fixture, h.label FROM hanviet h JOIN source s ON s.id = h.source WHERE h.char=? "
        "AND (h.kind='hv' OR h.label='fallback') ORDER BY h.label='fallback', h.label='southern', h.use DESC, "
        "CASE h.source WHEN 'wiktionary' THEN 0 WHEN 'derived' THEN 1 ELSE 2 END, h.ord, h.reading", (ch,)).fetchall()
    real = [(r, lb) for r, fx, lb in rows if not fx]
    rows = real or [(r, lb) for r, _, lb in rows]
    if any(lb != 'fallback' for _, lb in rows):
        rows = [x for x in rows if x[1] != 'fallback']
    out = []
    for r, lb in rows:
        if r not in [x[0] for x in out]:
            out.append((r, lb))
    return out if labels else [r for r, _ in out]


def hv_text(con, chars):
    """'生 sinh/sanh (Southern variant) · 日 nhật'; a character with no reading: '部 — (no Hán-Việt reading)'."""
    parts = []
    for c in chars:
        rs = hv_readings(con, c, labels=True)
        parts.append(f"{c} " + ('/'.join(r + (f' ({HV_LABEL[lb]})' if lb in HV_LABEL else '') for r, lb in rs)
                                if rs else '— (no Hán-Việt reading)'))
    return ' · '.join(parts)


def join(con, chars, names=False):
    """The bridge row of a chữ Hán spelling. `via`: the variant spelling under which a reading was found, when the
    word's own characters did not give it ('' otherwise)."""
    out = {'hv': hv_text(con, chars), 'hv_missing': [c for c in chars if not hv_readings(con, c)], 'n': 0}
    via = []
    for lang in LANGS:
        if lang == 'nan':
            r, by, out['nan_coll'], sp = taigi(con, chars)
        else:
            r, by, sp = lang_reading(con, chars, lang, names)
        out[lang], out[lang + '_by'] = r, by
        out['n'] += bool(r)
        if r and sp != chars and sp not in via:
            via.append(sp)
    out['via'] = ' / '.join(via)
    out['nan_flag'] = 'colloquial-only' if not out['nan'] and out['nan_coll'] and colloquial_only(con, chars) else ''
    return out
