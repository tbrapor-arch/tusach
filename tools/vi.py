"""Vietnamese text helpers shared by every tool: NFC, tones, syllable checks, keys, and the course's word boundaries.

    import vi
    vi.is_nfc(s)                 # text must be stored in Unicode NFC (checked by tools/lint.py)
    vi.tone('học')               # 6   (1 ngang, 2 huyền, 3 sắc, 4 hỏi, 5 ngã, 6 nặng)
    vi.toneless('học sinh')      # 'hoc sinh'   (vowel marks ă â ê ô ơ ư and đ are kept: they are letters)
    vi.key('Học_sinh')           # 'học sinh'   card key: NFC, lower case, one space between syllables
    vi.tkey('hoà')               # 'hoa2'       tone-place independent key (hoà = hòa), for comparing spellings
    vi.syllable_problems('cết')  # ['c before e/ê/i/y is written k']
    vi.words('Tôi là học_sinh.') # [('Tôi', 'tôi', None), ('là', ...), ('học_sinh', 'học sinh', None)] + punctuation

Word boundaries in the course (decided 17 Nov 2026, see docs/REFERENCE.md): a lesson line is written with an
underscore between the syllables of one word (`học_sinh`, `Hà_Nội`) and spaces between words, so every space-separated
piece of a line is one word and nothing is guessed. A piece may end in `~tag` to pick one of two homographs
(`đường~road`, `đường~sugar`); the tag is never shown. The app shows underscores as spaces.
"""
import re
import unicodedata

TONE_MARKS = {'̀': 2, '́': 3, '̉': 4, '̃': 5, '̣': 6}   # huyền sắc hỏi ngã nặng
TONE_NAMES = {1: 'ngang', 2: 'huyền', 3: 'sắc', 4: 'hỏi', 5: 'ngã', 6: 'nặng'}
CJK = re.compile(r'[㐀-鿿豈-﫿\U00020000-\U0003ffff]')
PUNCT = '.,!?;:…"\'“”‘’()[]«»—–-'
WORD_RE = re.compile(r'^([^\s~]+?)(?:~([A-Za-z0-9-]+))?$')

# ---- the syllable table, built from a description of Vietnamese phonotactics and its spelling (not a word list).
# A syllable is (initial) + (medial /w/) + nucleus + (coda) + tone.
#  * Nuclei and the codas each takes, written as quốc ngữ spells them (PLAIN): the short vowels ă and â never stand
#    open; ng/c are written nh/ch after a (anh, ach), ê and i; the diphthong iê is written ia when open, ua for uô and
#    ưa for ươ; the off-glides are written i/y and u/o (ai, ay, ao, au; oi, ôi, ơi, ui, ưi; iu, êu, ưu, eo).
#    Long o before ng/c is written oo (xoong, soóc). ưm (ừm, hừm) and eng/ec (xẻng, éc) are rare but standard.
#  * The medial /w/ (WRHYMES) is written o before a, ă, e and u before â, ê, i (spelled y), iê (spelled yê, open ya) and
#    ơ. It never comes before a rounded nucleus (o, ô, u, ư, uô, ươ). After /k/ the medial is written with the initial:
#    qu + the w-rhyme without its first letter (qua, quân, quý, quỳnh, quyết, quơ); c/k never take a w-rhyme (cuơ).
#    One spelling breaks the rounding rule: quốc (qu + ôc); quô, quu, quư are impossible. Open qu + y may be written
#    qu + i (quí, quĩ: Thiều Chửu's spelling of quý, quỹ), as open i may be y or i elsewhere.
#  * Spelling of iê at the start of a syllable: yê (yêu, yên, yểng, yết); open i may be written i or y (kí/ký).
#  * gi is the initial /z/: a rhyme beginning with i loses that i after it (gì, gìn, giếng = gi + iêng), so gii and
#    giiêng are impossible.
#  * Tones: a syllable ending in -p -t -c -ch takes only sắc or nặng (checked in syllable_problems).
# The table is validated at build time against real syllables (validate_syllables: FrequencyWords and Thiều Chửu).
INITIALS = sorted('b c ch d đ g gh gi h k kh l m n ng ngh nh p ph qu r s t th tr v x'.split() + [''],
                  key=len, reverse=True)
PLAIN = {
    'a': 'a ai ao am an ang anh ap at ac ach', 'ă': 'au ay ăm ăn ăng ăp ăt ăc', 'â': 'âu ây âm ân âng âp ât âc',
    'e': 'e eo em en eng ep et ec', 'ê': 'ê êu êm ên ênh êp êt êch', 'i': 'i y iu im in inh ip it ich',
    'o': 'o oi om on ong op ot oc oong ooc', 'ô': 'ô ôi ôm ôn ông ôp ôt ôc', 'ơ': 'ơ ơi ơm ơn ơp ơt',
    'u': 'u ui um un ung up ut uc', 'ư': 'ư ưi ưu ưm ưng ưt ưc',
    'iê': 'ia iêu iêm iên iêng iêp iêt iêc', 'uô': 'ua uôi uôm uôn uông uôt uôc',
    'ươ': 'ưa ươi ươu ươm ươn ương ươp ươt ươc',
}
WRHYMES = set('''oa oai oay oao oam oan oang oanh oap oat oac oach  oăm oăn oăng oăt oăc  oe oeo oen oet
uân uâng uât uây  uê uên uênh uêch  uy uyu uynh uyt uych  uya uyên uyêt  uơ'''.split())
PLAIN_RHYMES = {r for v in PLAIN.values() for r in v.split()}
_IE = {r for r in PLAIN['iê'].split() if r.startswith('iê')}
RHYMES = PLAIN_RHYMES | WRHYMES                                       # after an ordinary initial
RHYMES_NONE = (RHYMES - _IE) | {'y' + r[1:] for r in _IE}              # no initial: yêu, yên (not iêu, iên)
RHYMES_QU = {r[1:] for r in WRHYMES} | {'ôc', 'i'}                     # qu + a, â, ê, y, yên, ơ…; quốc; quí
RHYMES_GI = {r for r in RHYMES if r[:1] not in ('i', 'y')} | {r[1:] for r in PLAIN_RHYMES if r[:1] == 'i'}


def rhymes_after(initial):
    return {'': RHYMES_NONE, 'qu': RHYMES_QU, 'gi': RHYMES_GI}.get(initial, RHYMES)


CHECKED = ('c', 'ch', 'p', 't')     # a syllable ending in -c -ch -p -t takes only sắc or nặng
VOWELS = set('aăâeêioôơuưy')
MARKED = set('ăâêôơư')
# House style for the tone mark (decided 18 Nov 2026, docs/REFERENCE.md): the traditional placement, as in most
# Vietnamese print and Wikipedia: in an open rhyme of two vowels the mark sits on the first (hòa, khỏe, thủy, mùa);
# otherwise on the vowel with a diacritic (ơ in ươ), else on the last vowel before a coda (hoàn, toán), else on the
# middle one of three (ngoái, khuỷu). Keys ignore the placement (key() writes every syllable in the house style),
# so hoà and hòa are one word; lesson text keeps its own spelling, and lint asks for the house style.
def nfc(s):
    return unicodedata.normalize('NFC', str(s or ''))


def is_nfc(s):
    return unicodedata.is_normalized('NFC', s) if hasattr(unicodedata, 'is_normalized') else nfc(s) == s


def _split_tone(syl):
    """(toneless syllable in NFC, tone number, number of tone marks found)."""
    d = unicodedata.normalize('NFD', syl)
    marks = [TONE_MARKS[c] for c in d if c in TONE_MARKS]
    base = unicodedata.normalize('NFC', ''.join(c for c in d if c not in TONE_MARKS))
    return base, (marks[0] if marks else 1), len(marks)


def tone(syl):
    return _split_tone(syl)[1]


def toneless(s):
    return ' '.join(_split_tone(x)[0] for x in nfc(s).split())


def parses(base):
    """Every (initial, rhyme) reading of a toneless lower-case syllable allowed by the table (longest initial first)."""
    return [(i, base[len(i):]) for i in INITIALS if base.startswith(i) and base[len(i):] in rhymes_after(i)]


def _mark_index(base):
    """Index in `base` of the letter that carries the tone mark in the house style, or None (not a syllable)."""
    ps = parses(base)
    if not ps:
        return None
    ini, rhyme = ps[0]
    off = len(ini)
    vs = [i for i, c in enumerate(rhyme) if c in VOWELS]
    if not vs:                                   # gì, gìn: the i of gi carries it
        return off - 1 if ini == 'gi' else None
    marked = [i for i in vs if rhyme[i] in MARKED]
    if marked:
        j = marked[-1]                           # ơ of ươ, ô of uô, ê of iê/yê, â of uâ
    elif rhyme[-1] not in VOWELS:
        j = vs[-1]                               # closed: hoàn, toán, huỳnh, quýt
    elif len(vs) == 3:
        j = vs[1]                                # ngoái, khuỷu
    else:
        j = vs[0]                                # hòa, khỏe, thủy, mùa, mía, mái (one vowel: itself)
    return off + j


def place_tone(base, t):
    """The syllable `base` (toneless, lower case) with tone t written in the house style; None if not a syllable."""
    i = _mark_index(base)
    if i is None:
        return None
    if t == 1:
        return base
    mark = {v: k for k, v in TONE_MARKS.items()}[t]
    return unicodedata.normalize('NFC', base[:i + 1] + mark + base[i + 1:])


def canon(syl):
    """One syllable (lower case) in the house style of tone-mark placement: canon('hoà') == 'hòa'. Anything that is not
    a possible syllable (a loanword, two tone marks) is returned unchanged."""
    base, t, n = _split_tone(syl)
    if n != 1:
        return syl
    return place_tone(base, t) or syl


def key(word):
    """Card key of a word as written in a lesson: underscores and spaces alike, NFC, lower case, every syllable in the
    house style of tone-mark placement (hoà and hòa have one key)."""
    return ' '.join(canon(s) for s in nfc(word).replace('_', ' ').lower().split())


def tkey(word):
    """Key that ignores where the tone mark sits (hoà = hòa, thuỷ = thủy): toneless syllable + tone number."""
    out = []
    for s in key(word).split():
        base, t, _ = _split_tone(s)
        out.append(f'{base}{t}')
    return ' '.join(out)


def syllables(word):
    return key(word).split()


def syllable_problems(syl, style=False):
    """Spelling problems of one syllable (empty list when it is a possible quốc ngữ syllable). style=True also reports
    a tone mark not placed in the house style (tools/lint.py)."""
    if not syl:
        return ['empty syllable']
    syl = syl.lower()
    base, t, n = _split_tone(syl)
    out = []
    if n > 1:
        out.append(f'{syl}: two tone marks')
    d = unicodedata.normalize('NFD', syl).replace('\u0302', '').replace('\u0306', '').replace('\u031b', '')
    if any(c in TONE_MARKS and (i == 0 or d[i - 1] not in 'aeiouy') for i, c in enumerate(d)):
        out.append(f'{syl}: tone mark on a consonant')
    if not re.fullmatch(r'[a-zăâêôơưđ]+', base):
        return out + [f'{syl}: letters outside quốc ngữ']
    ps = parses(base)
    if not ps:
        return out + [f'{syl}: not a Vietnamese syllable']
    ini, rhyme = ps[0]
    front = rhyme[:1] in ('i', 'e', 'ê', 'y')
    if ini in ('c', 'k') and rhyme in WRHYMES:
        out.append(f'{syl}: /k/ + medial w is written qu')
    elif ini == 'c' and front:
        out.append(f'{syl}: c before e/ê/i/y is written k')
    if ini == 'k' and rhyme and not front and rhyme not in WRHYMES:
        out.append(f'{syl}: k is only written before e/ê/i/y (else c)')
    if ini == 'g' and rhyme[:1] in ('e', 'ê'):          # (g + i… is the initial gi: gìn, gì)
        out.append(f'{syl}: g before e/ê is written gh')
    if ini == 'ng' and rhyme[:1] in ('e', 'ê', 'i'):
        out.append(f'{syl}: ng before e/ê/i is written ngh')
    if ini in ('gh', 'ngh') and not rhyme[:1] in ('e', 'ê', 'i'):
        out.append(f'{syl}: {ini} is only written before e/ê/i')
    if rhyme.endswith(CHECKED) and t not in (3, 6):
        out.append(f'{syl}: a syllable ending in -{next(c for c in ("ch", "c", "p", "t") if rhyme.endswith(c))} '
                   f'takes only sắc or nặng, not {TONE_NAMES[t]}')
    if style and n == 1 and not out and canon(syl) != syl:
        out.append(f'{syl}: tone mark placement: write {canon(syl)} (house style, docs/REFERENCE.md)')
    return out


def validate_syllables(sylls):
    """Check the syllable table against real syllables: {syllable: count}. Returns (accepted, rejected with a
    Vietnamese letter or tone mark [(syllable, count, problem)], count of the other rejects, examples). The other rejects
    are plain ASCII (foreign words, names, abbreviations: ok, ko, john) or contain digits, dots or hyphens (subtitle
    markup, mr., cà-phê); the ones with Vietnamese letters only are read one by one (build_db prints them)."""
    acc, viet, ascii_n, ascii_ex = 0, [], 0, []
    for w, c in sorted(sylls.items(), key=lambda x: -x[1]):
        probs = syllable_problems(w)
        if not probs:
            acc += 1
        elif re.fullmatch(r'[a-z]+', w) or not re.fullmatch(r'[a-zăâêôơưđ]+', _split_tone(w)[0]):
            ascii_n += 1
            if len(ascii_ex) < 12:
                ascii_ex.append(w)
        else:
            viet.append((w, c, probs[0].split(': ', 1)[-1]))
    return acc, viet, ascii_n, ascii_ex


def strip_punct(piece):
    """('“', 'học_sinh', '.”') for '“học_sinh.”'."""
    m = re.match(r'^([' + re.escape(PUNCT) + r']*)(.*?)([' + re.escape(PUNCT) + r']*)$', piece)
    return m.group(1), m.group(2), m.group(3)


def words(line):
    """A course line cut by its own boundaries: a list of ('w', surface, key, tag, sentence_start) for words and
    ('p', text) for punctuation and spaces. `surface` keeps the line's own letters (with underscores); numbers are
    punctuation-like tokens ('n', text)."""
    out = []
    start = True
    for i, piece in enumerate(nfc(line).split(' ')):
        if i:
            out.append(('p', ' '))
        if not piece:
            continue
        pre, core, post = strip_punct(piece)
        if pre:
            out.append(('p', pre))
        if core:
            m = WORD_RE.match(core)
            surf, tag = (m.group(1), m.group(2)) if m else (core, None)
            if re.fullmatch(r'[0-9.,:%]+', surf):
                out.append(('n', surf))
            else:
                out.append(('w', surf, key(surf), tag, start))
            start = False
        if post:
            out.append(('p', post))
        if re.search(r'[.!?…:]["”’»)]*$', piece):
            start = True
    # neighbouring punctuation joined into one piece
    merged = []
    for t in out:
        if t[0] == 'p' and merged and merged[-1][0] == 'p':
            merged[-1] = ('p', merged[-1][1] + t[1])
        else:
            merged.append(t)
    return merged


def display(line):
    """The line as the learner reads it: underscores as spaces, tags removed."""
    return ''.join(t[1].replace('_', ' ') if t[0] in ('w', 'n') else t[1] for t in words(line))


def card_id(k, tag=None):
    return f'{k}~{tag}' if tag else k


# ---- the dictionary cutter, for text that has no boundaries of its own (books, transcripts, subtitles). Lessons never
# use it. Longest dictionary match over syllables, up to MAX syllables; a syllable no word starts with stays alone.
# Measured against a hand-cut reference before any module relies on it (handover step 5: 200 sentences): TODO.
MAX = 4


def cut(text, known):
    """`known`: a set of keys (lower-case NFC words, syllables separated by spaces). Returns the text re-written with
    underscores inside the words found, so that the result goes through words() like a lesson line."""
    out = []
    for piece_line in nfc(text).split('\n'):
        pieces = piece_line.split(' ')
        res, i = [], 0
        while i < len(pieces):
            pre, core, post = strip_punct(pieces[i])
            best = 1
            if core and not post:
                for n in range(MAX, 1, -1):
                    if i + n > len(pieces):
                        continue
                    group = [strip_punct(p) for p in pieces[i:i + n]]
                    if any(g[0] for g in group[1:]) or any(g[2] for g in group[:-1]) or not all(g[1] for g in group):
                        continue
                    if key(' '.join(g[1] for g in group)) in known:
                        best = n
                        break
            if best == 1:
                res.append(pieces[i])
            else:
                group = [strip_punct(p) for p in pieces[i:i + best]]
                res.append(group[0][0] + '_'.join(g[1] for g in group) + group[-1][2])
            i += best
        out.append(' '.join(res))
    return '\n'.join(out)


def _test():
    assert tone('học') == 6 and tone('sinh') == 1 and tone('Việt') == 6 and tone('ngã') == 5
    assert toneless('Việt Nam') == 'Viêt Nam'
    assert key('Học_sinh') == 'học sinh'
    assert tkey('hoà') == tkey('hòa') == 'hoa2' and tkey('thuỷ') == tkey('thủy')
    for ok in ('học', 'sinh', 'nghĩ', 'ghế', 'kia', 'quốc', 'gì', 'giường', 'người', 'khuya', 'chuyện', 'thuở',
               'xoong', 'oan', 'uống', 'yêu', 'tiếng', 'Việt', 'đường', 'nước', 'ạ', 'ơi'):
        assert not syllable_problems(ok.lower()), (ok, syllable_problems(ok.lower()))
    for bad in ('cết', 'kan', 'ngi', 'ge', 'ghá', 'hoc', 'mắt̀', 'xyz', 'họcs'):
        assert syllable_problems(bad), bad
    # the syllable table (finding 10): rhymes uyt, uâng, ưm, qu + y…; no qu + rounded vowel, no gi + i
    for ok in ('quýt', 'huýt', 'xuýt', 'nguýt', 'huỵt', 'khuâng', 'ừm', 'hừm', 'quỳnh', 'quýnh', 'yểng', 'quên',
               'quốc', 'giếng', 'gìn', 'khuỷu', 'ngoẹo', 'xoong', 'xẻng', 'huỵch', 'khuây', 'ỉa', 'yết', 'thuở', 'quí'):
        assert not syllable_problems(ok), (ok, syllable_problems(ok))
    for bad in ('quu', 'quuy', 'quô', 'quư', 'cuơ', 'gii', 'giiêng', 'iêu', 'ăn̉', 'coa', 'kuy'):
        assert syllable_problems(bad), bad
    # one house style for the tone mark; keys ignore the placement (finding 9)
    for a, b in (('hoà', 'hòa'), ('thuỷ', 'thủy'), ('khoẻ', 'khỏe'), ('ngòai', 'ngoài'), ('tòan', 'toàn'),
                 ('qúa', 'quá'), ('đựơc', 'được'), ('gìn', 'gìn'), ('giếng', 'giếng'), ('quỳnh', 'quỳnh'),
                 ('khuỷu', 'khuỷu'), ('mùa', 'mùa'), ('uỷ', 'ủy'), ('oái', 'oái'), ('soóc', 'soóc')):
        assert canon(a) == b, (a, canon(a), b)
    assert key('Hoà_bình') == key('hòa bình') == 'hòa bình' and key('quí') != key('quý')
    assert syllable_problems('hoà', style=True) and not syllable_problems('hòa', style=True)
    assert syllable_problems('học')[0:] == [] and 'sắc or nặng' in syllable_problems('hoc')[0]
    ws = words('Chào anh_Nam! Tôi là học_sinh.')
    assert [w[2] for w in ws if w[0] == 'w'] == ['chào', 'anh nam', 'tôi', 'là', 'học sinh'], ws
    assert [w[4] for w in ws if w[0] == 'w'] == [True, False, True, False, False]
    assert display('Tôi ăn đường~sugar.') == 'Tôi ăn đường.'
    assert cut('Tôi là học sinh, bạn là học sinh.', {'học sinh'}) == 'Tôi là học_sinh, bạn là học sinh.'.replace(
        'là học sinh.', 'là học_sinh.')
    print('vi.py: all tests passed')


if __name__ == '__main__':
    _test()
