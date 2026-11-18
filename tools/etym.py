"""Origin of a Vietnamese word from the evidence in its Wiktionary entry (used by tools/build_db.py).

    origin, note = etym.classify(templates, text)

The origin of an entry is decided by the first decisive piece of evidence, in this order:
  1. {{vi-etym-sino}} (handled by build_db.sino_analysis): sino (a Hán-Việt word) or nonhv (an older Chinese loan,
     "Non-Sino-Vietnamese reading of Chinese X").
  2. etymology templates, in the order they appear in the etymology:
     inh / inh+ from Proto-Vietic, Proto-Mon-Khmer, Proto-Austroasiatic or Middle Vietnamese -> vietic (native);
     bor / der / lbor / obor / ubor / uder / psm from a Chinese variety (Middle, Old, Literary Chinese, Cantonese, Min…)
       -> nonhv (an older Chinese loan, etymon = the Chinese word given);
     the same from any other language -> loan ("borrowed from French gare");
     cal (calque) -> compound with the note "calque of …" (formed in Vietnamese on a foreign model: hệ điều hành);
     com / af / compound (a compound of Vietnamese words: hôm + nay) and vi-etym-redup (chắc chắn) -> compound;
     a language code no table names (sit, omx) is named from the template's own expansion (Sino-Tibetan, Old Mon).
  3. the etymology text, when no template decided: "Nativisation of Chinese 感恩" / "nativized form of Chinese 感恩" /
     "borrowed from (Middle) Chinese X" -> nonhv; "From French …" -> loan; "From Proto-Vietic …" -> vietic.
  4. cognate evidence (cog templates or "Cognate with Muong …"): a cognate in a Vietic or other Austroasiatic language
     (Muong, Chut, Thavung, Pacoh, Khmer, Mon, Bahnar, Khmu…) -> vietic, note "cognate with Muong chi".
  Review 4: the note says what the etymology says about THIS word ("Alteration of năm after mười" is not "inherited
  from" mười's ancestor); a cognate is shown only with its form ({{cog|mtq|-}} takes it from the text, "Muong Bi
  tỏl", else no note); an ancestor stage given with {{cog}} is no cognate (Middle Vietnamese: "inherited from"; a
  proto-form: "related to"); an inherited form identical to the word (chị < Middle Vietnamese chị) is no note.
  5. nothing: '' (unknown). Later steps of the build give an origin to alternative forms (that of their target) and to
     compounds whose syllables all have one (tools/build_db.py origins_after_load).

`doubt_words(text)`: Wiktionary's own uncertainty about the etymology ("possibly", "perhaps", "alternatively"…), in
the sentence that gives the source (the first one) or in a sentence offering another source ("Alternatively, from
Proto-Tai…"); a doubt about a later detail (the tone of phần, a deeper ancestry of mỗi's 每, a contaminated sense of
khám) does not make the analysis doubtful (review 2, finding 4).
"""
import re

CJK = r'[㐀-鿿豈-﫿\U00020000-\U0003ffff]'
CHINESE = {'zh', 'ltc', 'och', 'lzh', 'lzh-lit', 'cmn', 'yue', 'nan', 'nan-hbl', 'nan-hok', 'zh-min', 'hak', 'wuu',
           'csp', 'cpx', 'cdo', 'gan', 'hsn', 'cjy', 'zhx-sic', 'sit-pro'}
NATIVE_INH = ('mkh-', 'aav-')
ANCESTORS = {'mkh-mvi', 'mkh-vie-pro', 'mkh-pro', 'aav-pro'}   # the stages of Vietnamese's own line            # mkh-vie-pro, mkh-pro, mkh-mvi (Middle Vietnamese), aav-pro, mkh-kat-pro…
# Vietic and other Austroasiatic languages whose cognates Wiktionary gives (codes as in the snapshot of 18 Nov 2026)
AA_COGNATE = {'mtq', 'scb', 'pac', 'mnw', 'km', 'kha', 'bdq', 'tou', 'aem', 'kjg', 'thm', 'kpm', 'sea', 'omx', 'xtq',
              'brv', 'kxm', 'cma', 'sct', 'stg', 'vi-mid', 'mlf', 'ksz', 'sss', 'lbn', 'ngt', 'kdt', 'krr', 'jah',
              'pcj', 'kuf', 'jeh', 'rmx', 'mng', 'cog', 'mml', 'mtq-ban'}
BORROW = {'bor', 'bor+', 'bor-lite', 'der', 'der+', 'der-lite', 'lbor', 'obor', 'ubor', 'uder', 'psm', 'slbor'}
INHERIT = {'inh', 'inh+', 'inh-lite'}
LANG = {'fr': 'French', 'en': 'English', 'ja': 'Japanese', 'la': 'Latin', 'la-new': 'New Latin', 'ru': 'Russian',
        'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'es': 'Spanish', 'de': 'German', 'sa': 'Sanskrit',
        'pi': 'Pali', 'km': 'Khmer', 'th': 'Thai', 'lo': 'Lao', 'tai': 'Tai', 'tai-pro': 'Proto-Tai',
        'tai-swe-pro': 'Proto-Southwestern Tai', 'cmc': 'Chamic', 'cja': 'Cham', 'ms': 'Malay', 'ko': 'Korean',
        'ar': 'Arabic', 'fa': 'Persian', 'hi': 'Hindi', 'grc': 'Ancient Greek', 'el': 'Greek', 'cmc-pro':
        'Proto-Chamic', 'poz-pro': 'Proto-Malayo-Polynesian', 'map-pro': 'Proto-Austronesian', 'mn': 'Mongolian',
        'bo': 'Tibetan', 'tyz': 'Tày', 'nut': 'Nùng', 'zh': 'Chinese', 'ltc': 'Middle Chinese', 'och': 'Old Chinese',
        'lzh': 'Literary Chinese', 'cmn': 'Mandarin', 'yue': 'Cantonese', 'nan': 'Min Nan', 'hak': 'Hakka',
        'mtq': 'Muong', 'scb': 'Chut', 'pac': 'Pacoh', 'mnw': 'Mon', 'kha': 'Khasi', 'bdq': 'Bahnar', 'tou': 'Tho',
        'aem': 'Arem', 'kjg': 'Khmu', 'thm': 'Thavung', 'kpm': 'Koho', 'sea': 'Semai', 'mkh-vie-pro': 'Proto-Vietic',
        'mkh-pro': 'Proto-Mon-Khmer', 'aav-pro': 'Proto-Austroasiatic', 'mkh-mvi': 'Middle Vietnamese',
        'mkh-kat-pro': 'Proto-Katuic'}
NATIVE_TEXT = re.compile(r'\b(?:From|Inherited from|Derived from) ((?:Late |Early )?Proto-(?:Vietic|Viet-Muong|'
                         r'Mon-Khmer|Austroasiatic))\b(?: (\*[^\s,.;()]+))?')
_AA = (r'(?:Muong|Mường|Chut|Thavung|Pacoh|Khmer|Mon|Bahnar|Khmu|Arem|Maleng|Ruc|Rục|Thổ|Tho|Kri|Sach|May)')
COGNATE_LANG_TEXT = re.compile(r'\b[Cc]ognates? (?:with|to) ' + _AA + r'\b')
# "Cognate with Muong Bi tỏl", "Cognate with Kri Phoong praŋ⁴²ˀ": the language (with a capitalised variety) and the form
COGNATE_TEXT = re.compile(r'\b[Cc]ognates? (?:with|to) (' + _AA + r'(?: \[[^\]]*\]| [A-ZĐ][^\s,.;()\[]*)?) '
                          r'([^\s,.;()“”\[\]A-Z][^\s,.;()“”\[\]]*)')
# lăm: "Alteration of năm (“five”) after mười (“ten”)": what the template's word is to THIS word (review 4, A)
ALTERATION_TEXT = re.compile(r'^(Alteration|Variant|Contraction|Clipping|Shortening) of ([^\s,.;()]+)(?: \(“([^”]*)”\))?'
                             r'(?: after ([^\s,.;()]+)(?: \(“([^”]*)”\))?)?')


def _same(form, headword):
    """True when an ancestor form says nothing new: the modern word itself (chị < Middle Vietnamese chị)."""
    import unicodedata
    n = lambda x: unicodedata.normalize('NFC', x).lower().strip()
    return bool(headword) and all(n(f) == n(headword) for f in form.split(','))


def _alteration(m):
    s = f'an {m.group(1).lower()} of {m.group(2)}' + (f' “{m.group(3)}”' if m.group(3) else '')
    if m.group(4):
        s += f' after {m.group(4)}' + (f' “{m.group(5)}”' if m.group(5) else '')
    return s.replace('an variant', 'a variant').replace('an contraction', 'a contraction').replace(
        'an clipping', 'a clipping').replace('an shortening', 'a shortening')
CHINESE_TEXT = re.compile(r'(?:[Nn]ativi[sz](?:ation|ed form)|[Vv]ernacular(?:ized)? (?:form|reading)|[Bb]orrowed|'
                          r'[Ll]oan(?:word)?) (?:of|from) (?:Late |Early )?(?:Middle |Old |Literary |Classical )?'
                          r'(?:Chinese|Cantonese|Hokkien|Min Nan) (' + CJK + r'+)')
LOAN_TEXT = re.compile(r'^(?:Borrowed from|From|Ultimately from) (French|English|Khmer|Cham|Thai|Tai|Sanskrit|'
                       r'Portuguese|Dutch|Russian|Japanese|Latin|Malay|Spanish|Italian|German)\b(?: ([^\s,.;(]+))?')
DOUBT = re.compile(r'\b(possibl[ey]|perhaps|uncertain|unclear|disputed|doubtful|maybe|may be|might be|alternatively|'
                   r'or else from|folk etymology|contaminat\w*|not certain|obscure)\b', re.I)


def _lang(code, expansion='', word=''):
    """A language's name: the table's, else the template's own expansion without the word ("Old Mon lṅim" -> "Old
    Mon"), else "another language": a raw code (sit, omx) is never shown (review 2, finding 9)."""
    if code in LANG:
        return LANG[code]
    e = (expansion or '').strip()
    if word and word in e:
        e = e[:e.index(word)].strip()
    e = re.sub(r'\s*[(“].*$', '', e).strip()
    e = re.sub(r'^(?:[Bb]orrowed from|[Ff]rom|[Cc]ognate with|[Cc]alque of|[Oo]f)\s+', '', e)
    e = re.sub(r'\s+origin$', '', e)
    return e if e and re.fullmatch(r"[A-Z][\w' -]*", e) else 'another language'


def _word(args, i='3'):
    w = (args.get(i) or '').split('//')[0].strip()
    return '' if w in ('-', '') else w


def classify(templates, text, headword=''):
    """(origin, note) of one Wiktionary etymology without {{vi-etym-sino}}: vietic | nonhv | loan | compound | '' and
    the evidence in words. For nonhv, the note starts with the Chinese etymon: '感恩 (Chinese)'."""
    cognate = ''
    native = None            # an inherited line that names no form other than the word itself (chị < MV chị)
    text = text or ''
    alt = ALTERATION_TEXT.match(text.strip())
    ts = list(templates or [])
    for i, t in enumerate(ts):
        name, a = t.get('name'), t.get('args') or {}
        exp = t.get('expansion') or ''
        src = a.get('2', '')
        if name in INHERIT and src.startswith(NATIVE_INH):
            w = _word(a)
            if alt:              # lăm: "Alteration of năm after mười, which derives from Proto-Vietic *maːl"
                return 'vietic', _alteration(alt)
            if not w or _same(w, headword):
                native = native or ('vietic', '')
                continue
            return 'vietic', f'inherited from {_lang(src, exp, w)} {w}'
        if name in BORROW:
            if src in CHINESE:
                w = _word(a)
                if not re.fullmatch(CJK + '+', w):        # cuốn: {{der|vi|och}} then {{och-l|卷}}
                    nxt = next((x for x in ts[i + 1:i + 3] if x.get('name', '').endswith('-l')), None)
                    m = re.match(CJK + '+', (nxt or {}).get('args', {}).get('1', '') or '') if nxt else None
                    w = m.group(0) if m else ''
                if re.fullmatch(CJK + '+', w):
                    return 'nonhv', f'{w} ({_lang(src)})'
                continue          # "from Chinese" with no characters: not decisive
            if src.startswith(NATIVE_INH):
                return 'vietic', f'from {_lang(src, exp, _word(a))} {_word(a)}'.strip()
            if src and src != 'vi':
                return 'loan', f'borrowed from {_lang(src, exp, _word(a))} {_word(a)}'.strip()
        if name in ('com', 'af', 'affix', 'compound', 'com+') and a.get('1') == 'vi' and exp:
            return 'compound', re.sub(r'\s+', ' ', exp)
        if name in ('vi-etym-redup', 'reduplication', 'rdp') and exp:
            return 'compound', exp
        if name in ('cal', 'calque', 'clq') and src and src != 'vi':
            return 'compound', f'calque of {_lang(src, exp, _word(a))} {_word(a)}: formed in Vietnamese'.strip()
        if name in ('cog', 'cog-lite') and not cognate:
            c, w = a.get('1', ''), _word(a, '2')
            if c in ANCESTORS:
                # an ancestor stage of the same line given with {{cog}} is not a cognate (review 4, A): Middle
                # Vietnamese is an attested ancestor ("from"); a proto-form so marked is hedged ("related to")
                if w and not _same(w, headword):
                    cognate = (f'inherited from {_lang(c, exp, w)} {w}' if c == 'mkh-mvi' else
                               f'related to {_lang(c, exp, w)} {w}')
            elif c in AA_COGNATE or c.startswith(NATIVE_INH):      # Proto-Katuic: a sister branch
                if not w:                       # {{cog|mtq|-}}: the form is in the text ("Cognate with Muong Bi tỏl")
                    m = COGNATE_TEXT.search(text)
                    w = m.group(2) if m else ''
                    lang = m.group(1) if m else ''
                else:
                    lang = _lang(c, exp, w)
                if w:                           # a cognate is shown only with its form
                    cognate = f'cognate with {lang} {w}'
    if alt and native:
        return 'vietic', _alteration(alt)
    if native:
        return native
    m = CHINESE_TEXT.search(text) or OLD_CHINESE_TEXT.search(text.strip())
    if m:
        return 'nonhv', f'{m.group(1)} (Chinese)'
    m = LOAN_TEXT.search(text.strip())
    if m:
        return 'loan', f'borrowed from {m.group(1)}' + (f' {m.group(2)}' if m.group(2) else '')
    m = NATIVE_TEXT.search(text)
    if m:                    # the note only when the text names the proto-form
        return 'vietic', (f'inherited from {m.group(1)} {m.group(2)}' if m.group(2) else '')
    if cognate:
        return 'vietic', cognate
    m = COGNATE_TEXT.search(text)
    if m:
        return 'vietic', f'cognate with {m.group(1)} {m.group(2)}'
    if COGNATE_LANG_TEXT.search(text):
        return 'vietic', ''      # a cognate named with no form: native, no note
    m = COMPOUND_TEXT.match(text.strip())
    if m:
        return 'compound', m.group(0).rstrip('.')
    return '', ''


OLD_CHINESE_TEXT = re.compile(r'^From (?:Late |Early )?(?:Old|Middle|Literary|Classical) Chinese (' + CJK + r'+)')
COMPOUND_TEXT = re.compile(r'^[^\W\d_]+(?: [^\W\d_]+)?(?: \(“[^”]*”\))? \+ [^\W\d_]+(?: [^\W\d_]+)?(?: \(“[^”]*”\))?')


def doubt_words(text):
    """The words of an etymology text that express Wiktionary's own uncertainty about the source ('' if none): in
    its first sentence, or in a sentence that offers another source (starting "Alternatively", "Or", "Another")."""
    t = (text or '').strip()
    sents = re.split(r'(?<=[.])\s+|\n+', t)
    scope = sents[:1] + [x for x in sents[1:] if re.match(r'(?:Alternatively|Or (?:from|perhaps|possibly)|Another|'
                                                           r'Possibly|Perhaps|Maybe)\b', x)]
    found = []
    for x in scope:
        for m in DOUBT.finditer(x):
            w = m.group(1).lower()
            if w not in found:
                found.append(w)
    return ', '.join(found)


def _selftest():
    assert classify([{'name': 'inh', 'args': {'1': 'vi', '2': 'mkh-vie-pro', '3': '*ʔɛːm'}}], '')[0] == 'vietic'
    assert classify([{'name': 'bor', 'args': {'1': 'vi', '2': 'fr', '3': 'gare'}}], '') == ('loan', 'borrowed from French gare')
    assert classify([], 'Nativisation of Chinese 感恩 (modern SV: cảm ân).') == ('nonhv', '感恩 (Chinese)')
    assert classify([{'name': 'cog', 'args': {'1': 'mtq', '2': 'chi'}}], 'Cognate with Muong chi.') == \
        ('vietic', 'cognate with Muong chi')
    assert classify([{'name': 'cog', 'args': {'1': 'th', '2': 'x'}}], '') == ('', '')
    assert classify([{'name': 'der', 'args': {'1': 'vi', '2': 'ltc', '3': '牢'}}], '')[0] == 'nonhv'
    assert classify([], 'From French ga.')[0] == 'loan'
    assert doubt_words('Possible non-Sino-Vietnamese reading of Chinese 朝; thus, possibly a doublet') == 'possible, possibly'
    assert doubt_words('Sino-Vietnamese word from 冊.') == ''
    assert doubt_words('Sino-Vietnamese word from 分. The tone here is rather problematic, alternatively x.') == ''
    assert doubt_words('Sino-Vietnamese word from 唐. Doublet of đàng.\nAlternatively, from Proto-Tai *daːŋ.') == \
        'alternatively'
    assert classify([{'name': 'bor', 'args': {'1': 'vi', '2': 'sit'}, 'expansion': 'Sino-Tibetan'}], '') == \
        ('loan', 'borrowed from Sino-Tibetan')
    assert classify([{'name': 'cog', 'args': {'1': 'omx', '2': 'lṅim'}, 'expansion': 'Old Mon lṅim'}], '') == \
        ('vietic', 'cognate with Old Mon lṅim')
    assert classify([{'name': 'com', 'args': {'1': 'vi'}, 'expansion': 'hôm (“day”) + nay (“this; now”)'}], '')[0] \
        == 'compound'
    assert classify([{'name': 'der', 'args': {'1': 'vi', '2': 'och'}}, {'name': 'och-l', 'args': {'1': '卷'}}],
                    '')[0] == 'nonhv'
    assert classify([], 'vì (“because; for”) + sao (“why; how”).')[0] == 'compound'
    # review 4, A: the note says what the etymology says about THIS word, with a form, and an ancestor is no cognate
    lam = [{'name': 'inh', 'args': {'1': 'vi', '2': 'mkh-vie-pro', '3': '*maːl'}},
           {'name': 'cog', 'args': {'1': 'mtq', '2': 'mườl'}}]
    assert classify(lam, 'Alteration of năm (“five”) after mười (“ten”) (realized as mươi), which historically derives '
                    'from Proto-Vietic *maːl, whence also Muong mườl.', 'lăm') == \
        ('vietic', 'an alteration of năm “five” after mười “ten”')
    assert classify([{'name': 'cog', 'args': {'1': 'mkh-mvi', '2': 'muốn, muấn'}}], 'Attested as …', 'muốn') == \
        ('vietic', 'inherited from Middle Vietnamese muốn, muấn')
    assert classify([{'name': 'cog', 'args': {'1': 'mkh-vie-pro', '2': '*p-laːŋʔ'}}], 'x', 'sáng') == \
        ('vietic', 'related to Proto-Vietic *p-laːŋʔ')
    assert classify([{'name': 'cog', 'args': {'1': 'mtq', '2': '-'}}], 'Cognate with Muong Bi tỏl.', 'đói') == \
        ('vietic', 'cognate with Muong Bi tỏl')
    assert classify([{'name': 'cog', 'args': {'1': 'thm', '2': '-'}}], 'Cognate with Thavung (Suwilai, 2000).', 'x') \
        == ('vietic', '')
    assert classify([{'name': 'inh', 'args': {'1': 'vi', '2': 'mkh-mvi', '3': 'chị'}}], 'From Middle Vietnamese chị.',
                    'chị') == ('vietic', '')
    assert classify([{'name': 'inh', 'args': {'1': 'vi', '2': 'mkh-mvi', '3': 'chị'}},
                     {'name': 'inh', 'args': {'1': 'vi', '2': 'mkh-vie-pro', '3': '*ɟiːʔ'}}], '', 'chị') == \
        ('vietic', 'inherited from Proto-Vietic *ɟiːʔ')
    assert classify([], 'From Proto-Vietic.', 'x') == ('vietic', '')
    assert classify([{'name': 'cog', 'args': {'1': 'mkh-kat-pro', '2': '*sool'}}], '', 'tôi') == \
        ('vietic', 'cognate with Proto-Katuic *sool')
    assert classify([{'name': 'cog', 'args': {'1': 'tou', '2': '-'}}], 'Cognate with Tho [Cuối Chăm] kʰrɐː⁶.', 'giữa') \
        == ('vietic', 'cognate with Tho [Cuối Chăm] kʰrɐː⁶')
    print('etym: self-test ok')


if __name__ == '__main__':
    _selftest()
