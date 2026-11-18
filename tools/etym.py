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
     cal (calque) -> vietic with the note "calque of …" (native material built on a foreign model).
  3. the etymology text, when no template decided: "Nativisation of Chinese 感恩" / "nativized form of Chinese 感恩" /
     "borrowed from (Middle) Chinese X" -> nonhv; "From French …" -> loan; "From Proto-Vietic …" -> vietic.
  4. cognate evidence (cog templates or "Cognate with Muong …"): a cognate in a Vietic or other Austroasiatic language
     (Muong, Chut, Thavung, Pacoh, Khmer, Mon, Bahnar, Khmu…) -> vietic, note "cognate with Muong chi".
  5. nothing: '' (unknown). Later steps of the build give an origin to alternative forms (that of their target) and to
     compounds whose syllables all have one (tools/build_db.py origins_after_load).

`doubt_words(text)`: Wiktionary's own uncertainty about the etymology ("possibly", "perhaps", "alternatively"…).
"""
import re

CJK = r'[㐀-鿿豈-﫿\U00020000-\U0003ffff]'
CHINESE = {'zh', 'ltc', 'och', 'lzh', 'lzh-lit', 'cmn', 'yue', 'nan', 'nan-hbl', 'nan-hok', 'zh-min', 'hak', 'wuu',
           'csp', 'cpx', 'cdo', 'gan', 'hsn', 'cjy', 'zhx-sic', 'sit-pro'}
NATIVE_INH = ('mkh-', 'aav-')            # mkh-vie-pro, mkh-pro, mkh-mvi (Middle Vietnamese), aav-pro, mkh-kat-pro…
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
NATIVE_TEXT = re.compile(r'\b(?:From|Inherited from|Derived from) (?:Late |Early )?Proto-(?:Vietic|Viet-Muong|'
                         r'Mon-Khmer|Austroasiatic)\b')
COGNATE_TEXT = re.compile(r'\b[Cc]ognates? (?:with|to) (?:Muong|Mường|Chut|Thavung|Pacoh|Khmer|Mon|Bahnar|Khmu|'
                          r'Arem|Maleng|Ruc|Rục|Thổ|Tho|Kri|Sach|May)\b')
CHINESE_TEXT = re.compile(r'(?:[Nn]ativi[sz](?:ation|ed form)|[Vv]ernacular(?:ized)? (?:form|reading)|[Bb]orrowed|'
                          r'[Ll]oan(?:word)?) (?:of|from) (?:Late |Early )?(?:Middle |Old |Literary |Classical )?'
                          r'(?:Chinese|Cantonese|Hokkien|Min Nan) (' + CJK + r'+)')
LOAN_TEXT = re.compile(r'^(?:Borrowed from|From|Ultimately from) (French|English|Khmer|Cham|Thai|Tai|Sanskrit|'
                       r'Portuguese|Dutch|Russian|Japanese|Latin|Malay|Spanish|Italian|German)\b(?: ([^\s,.;(]+))?')
DOUBT = re.compile(r'\b(possibl[ey]|perhaps|uncertain|unclear|disputed|doubtful|maybe|may be|might be|alternatively|'
                   r'or else from|folk etymology|contaminat\w*|not certain|obscure)\b', re.I)


def _lang(code):
    return LANG.get(code, code)


def _word(args, i='3'):
    w = (args.get(i) or '').split('//')[0].strip()
    return '' if w in ('-', '') else w


def classify(templates, text):
    """(origin, note) of one Wiktionary etymology without {{vi-etym-sino}}: vietic | nonhv | loan | '' and the evidence
    in words. For nonhv, the note starts with the Chinese etymon: '感恩 (Chinese)'."""
    cognate = ''
    for t in templates or []:
        name, a = t.get('name'), t.get('args') or {}
        src = a.get('2', '')
        if name in INHERIT and src.startswith(NATIVE_INH):
            return 'vietic', f'inherited from {_lang(src)} {_word(a)}'.strip()
        if name in BORROW:
            if src in CHINESE:
                w = _word(a)
                if re.fullmatch(CJK + '+', w):
                    return 'nonhv', f'{w} ({_lang(src)})'
                continue          # "from Chinese" with no characters: not decisive
            if src.startswith(NATIVE_INH):
                return 'vietic', f'from {_lang(src)} {_word(a)}'.strip()
            if src and src != 'vi':
                return 'loan', f'borrowed from {_lang(src)} {_word(a)}'.strip()
        if name in ('cal', 'calque', 'clq') and src and src != 'vi':
            return 'vietic', f'calque of {_lang(src)} {_word(a)}'.strip()
        if name in ('cog', 'cog-lite') and not cognate:
            c = a.get('1', '')
            if c in AA_COGNATE or c.startswith(NATIVE_INH):
                cognate = f'cognate with {_lang(c)} {_word(a, "2")}'.strip()
    text = text or ''
    m = CHINESE_TEXT.search(text)
    if m:
        return 'nonhv', f'{m.group(1)} (Chinese)'
    m = LOAN_TEXT.search(text.strip())
    if m:
        return 'loan', f'borrowed from {m.group(1)}' + (f' {m.group(2)}' if m.group(2) else '')
    if NATIVE_TEXT.search(text):
        return 'vietic', NATIVE_TEXT.search(text).group(0)[0].lower() + NATIVE_TEXT.search(text).group(0)[1:]
    if cognate:
        return 'vietic', cognate
    m = COGNATE_TEXT.search(text)
    if m:
        return 'vietic', m.group(0)[0].lower() + m.group(0)[1:]
    return '', ''


def doubt_words(text):
    """The words of an etymology text that express Wiktionary's own uncertainty ('' if none)."""
    found = []
    for m in DOUBT.finditer(text or ''):
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
    print('etym: self-test ok')


if __name__ == '__main__':
    _selftest()
