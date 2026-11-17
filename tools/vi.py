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

INITIALS = sorted('b c ch d đ g gh gi h k kh l m n ng ngh nh p ph qu r s t th tr v x'.split() + [''],
                  key=len, reverse=True)
RHYMES = set('''
a ai ao au ay an am ang anh ac ach ap at
ăn ăm ăng ăc ăp ăt
âu ây ân âm âng âc âp ât
e eo en em eng ec ep et
ê êu ên êm ênh êch êp êt
i ia iu in im inh ich ip it
iêu iên iêm iêng iêc iêp iêt
o oi on om ong oc op ot oong ooc
ô ôi ôn ôm ông ôc ôp ôt
ơ ơi ơn ơm ơp ơt
u ua ui un um ung uc up ut uy uya uyu uân uât uyên uyêt uynh uych uơ
ư ưa ưi ưu ưn ưng ưc ưt ươi ươu ươn ươm ương ươc ươp ươt
uôi uôn uôm uông uôc uôt
y yêu yên yêm yêt
oa oai oao oay oan oam oang oanh oac oach oap oat oăn oăm oăng oăc oăt
oe oeo oen oem oet
uê uênh uêch
'''.split())
CHECKED = ('c', 'ch', 'p', 't')     # a syllable ending in -c -ch -p -t takes only sắc or nặng


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


def key(word):
    """Card key of a word as written in a lesson: underscores and spaces alike, NFC, lower case."""
    return ' '.join(nfc(word).replace('_', ' ').lower().split())


def tkey(word):
    """Key that ignores where the tone mark sits (hoà = hòa, thuỷ = thủy): toneless syllable + tone number."""
    out = []
    for s in key(word).split():
        base, t, _ = _split_tone(s)
        out.append(f'{base}{t}')
    return ' '.join(out)


def syllables(word):
    return key(word).split()


def syllable_problems(syl):
    """Spelling problems of one lower-case syllable (empty list when it is a possible quốc ngữ syllable)."""
    if not syl:
        return ['empty syllable']
    base, t, n = _split_tone(syl.lower())
    out = []
    if n > 1:
        out.append(f'{syl}: two tone marks')
    if not re.fullmatch(r'[a-zăâêôơưđ]+', base):
        return out + [f'{syl}: letters outside quốc ngữ']
    parses = [(i, base[len(i):]) for i in INITIALS if base.startswith(i) and base[len(i):] in RHYMES]
    if base == 'gi':                        # gì, gỉ: gi + an empty rhyme
        parses.insert(0, ('gi', ''))
    if not parses:
        return out + [f'{syl}: not a Vietnamese syllable']
    ini, rhyme = parses[0]
    front = rhyme[:1] in ('i', 'e', 'ê', 'y')
    if ini == 'c' and front:
        out.append(f'{syl}: c before e/ê/i/y is written k')
    if ini == 'k' and rhyme and not front:
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
    return out


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
