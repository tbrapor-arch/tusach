"""Build the Vietnamese learner database from the pinned open sources in data/raw (data/fetch.sh).

    python3 -I tools/build_db.py data/raw data/build/vi.db            # public build: commercial-use sources only
    python3 -I tools/build_db.py data/raw data/build/vi-nc.db --nc    # private build: also non-commercial sources

The two builds go to two different files and say which they are in `meta.nc`: tools/cards.py open_db() refuses a
public build (the app page) from vi-nc.db and a private build (the private module) from vi.db, so the rule "no
non-commercial source on the public page" is enforced by the code, not by a document.

SOURCES below: one loader per source of data/fetch.sh, licence as in ATTRIBUTION.md. A source whose file is not in
data/raw stops the build (exit 1), unless its id is listed in TUSACH_ALLOW_MISSING=id,id (a sandbox that cannot reach
a host): then it is skipped with "source X not fetched: …" and listed in meta.missing, and tools/build_app.py and
tools/site.py refuse to make a publishable page from that database.
After the sources: the frequency of each word (tools/freq.py), the Hán-Việt cross-check, the labels, and the bridge
join on characters (tools/bridge.py, table `bridge`). Nothing is edited by hand.

The invented test fixture (tools/fixtures/dict.yaml) is always loaded, as source `fixture` (fixture = 1): it lets
`make app`, `make lint` and tools/smoke.py run before any real source exists. tools/lint.py refuses a real lesson that
uses a word only the fixture has.
"""
import bz2
import csv
import datetime
import json
import os
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bridge  # noqa: E402
import english  # noqa: E402
import etym  # noqa: E402
import freq  # noqa: E402
import hanviet  # noqa: E402
import vi  # noqa: E402

FIXTURE = os.path.join(HERE, 'fixtures', 'dict.yaml')
csv.field_size_limit(1 << 24)


class Missing(Exception):
    """A source file is not in data/raw."""


def allowed_missing():
    """Source ids that may be missing on purpose (TUSACH_ALLOW_MISSING=id,id; sandboxes only)."""
    return {x.strip() for x in os.environ.get('TUSACH_ALLOW_MISSING', '').split(',') if x.strip()}


def snapshot_pin(source_id):
    """'snapshot TAG, sha256 SHA8' for a source fetched from our own snapshot release (data/fetch.sh `snap` lines),
    'snapshot PENDING' before the first snapshot."""
    for line in open(os.path.join(ROOT, 'data', 'fetch.sh'), encoding='utf-8'):
        p = line.split()
        if len(p) == 6 and p[0] == 'snap' and p[1] == source_id:
            return f'snapshot {p[4]}' + ('' if p[4] == 'PENDING' else f', sha256 {p[5][:8]}')
    return 'snapshot (not in data/fetch.sh)'


def need(raw, *parts):
    p = os.path.join(raw, *parts)
    if not os.path.exists(p):
        raise Missing(os.path.join('data/raw', *parts))
    return p


def is_cjk_word(s):
    return bool(s) and all(vi.CJK.match(c) for c in s)


# ---------------------------------------------------------------------------------------------- Wiktionary (kaikki)
VIETIC = ('mkh-vie-pro', 'mkh-pro', 'aav-pro', 'mkh-vie')   # Proto-Vietic, Proto-Mon-Khmer, Proto-Austroasiatic
READING_TAGS = {'han-viet-reading': 'hv', 'nom-reading': 'nom', 'han-nom-reading': 'hannom'}


def _sino_parse(t):
    """(chars, kind, sv) of one {{vi-etym-sino}}. Argument layouts seen in the snapshot of 17 Nov 2026 (tools/fixtures/
    kaikki-real.jsonl): the whole word in 1 (`1=詞典`, 5,138 uses), or characters and glosses alternating (`1=飛 2=to fly
    3=場 4=field`, also with groups of several characters: `1=不動 2=… 3=產`), with optional lit=, suffix=, tr=, t=.
    kind 'hv': a Sino-Vietnamese (Hán-Việt) word. kind 'nonhv': the template renders "Non-Sino-Vietnamese reading of
    Chinese X (SV: …)" (parameters hv= or preMC= with any value; ~880 uses: và 和, giấy 紙, chào 朝, đũa 箸): a word
    borrowed from Chinese in an older or colloquial layer, NOT read the Hán-Việt way; argument 3 is then the Hán-Việt
    reading (sv), not a character, and the word is not a Hán-Việt analysis."""
    args = t.get('args') or {}
    exp = (t.get('expansion') or '').lower()
    nonhv = exp.startswith('non-sino-vietnamese') or any(args.get(k) for k in ('hv', 'preMC'))
    if nonhv:
        return (args.get('1', '') if is_cjk_word(args.get('1', '')) else ''), 'nonhv', vi.nfc(args.get('3', ''))
    chars = ''.join(v for k, v in sorted(((int(k), v) for k, v in args.items() if k.isdigit()), key=lambda x: x[0])
                    if k % 2 == 1 and is_cjk_word(v))
    return chars, 'hv', ''


BORROWING = ('bor', 'bor+', 'obor', 'der', 'der+', 'cal', 'calque', 'lbor')


def sino_analysis(entry):
    """(chars, kind, sv) of a word's Sino-Vietnamese etymology, None without {{vi-etym-sino}}. Several templates in one
    etymology (36 entries) are alternatives ("from 薦 or from 進", 月食 / 月蝕): the first Hán-Việt one whose characters
    are as many as the syllables wins, else the first. No characters in the arguments (40 entries, `câu lạc bộ`): the
    word given to {{etymid}} next to it."""
    tpls = entry.get('etymology_templates') or []
    found = [_sino_parse(t) for t in tpls if t.get('name') == 'vi-etym-sino']
    if not found:
        return None
    n = len(vi.key(entry.get('word', '')).split())
    best = next((f for f in found if f[1] == 'hv' and len(f[0]) == n), found[0])
    if not best[0]:
        for t in tpls:
            a = t.get('args') or {}
            if t.get('name') == 'etymid' and is_cjk_word(a.get('2', '')):
                return a['2'], best[1], best[2]
        # `{{vi-etym-sino}}` with no argument, then the borrowing itself: "Sino-Vietnamese, orthographic borrowing from
        # Japanese 俱樂部" (câu lạc bộ): a bor/obor/der/cal template whose argument 3 has one character per syllable
        for t in tpls:
            a = t.get('args') or {}
            if t.get('name') in BORROWING and is_cjk_word(a.get('3', '')) and len(a['3']) == n:
                return a['3'], best[1], best[2]
    return best


def sino_chars(entry):
    """Characters of a Sino-Vietnamese (Hán-Việt) word; '' for a borrowing that is not read the Hán-Việt way or has no
    characters; None without {{vi-etym-sino}}."""
    a = sino_analysis(entry)
    return None if a is None else (a[0] if a[1] == 'hv' else '')


def origin_of(entry, analysis):
    """(origin, note): sino | nonhv from {{vi-etym-sino}}, else the evidence of tools/etym.py classify() (inherited,
    borrowed, cognate templates; the etymology text)."""
    if analysis is not None:
        if analysis[1] == 'hv':
            return 'sino', ''
        return 'nonhv', f'{analysis[0]} {analysis[2]}'.strip()
    return etym.classify(entry.get('etymology_templates'), entry.get('etymology_text'))


# senses never used for English: a misspelling ("chuyện: misspelling of truyện"), an empty sense; senses with these
# tags come after the ordinary ones (học sinh: "a student" is archaic, "a pupil" is today's sense)
SKIP_SENSE = {'misspelling', 'no-gloss'}
LATE_SENSE = {'archaic', 'obsolete', 'rare', 'dialectal', 'Southern', 'Central', 'historical', 'dated', 'uncommon'}


def sense_rows(entry):
    """[(gloss, tags, examples, alt_of)] of an entry's senses: of a sense with a general gloss and a more specific one
    (kaikki's nested senses), the general one when it is short and not a usage description (với: "with", not its
    sub-sense "to or by", which lost the card its main sense), else the last; alt_of: the target of an "alternative
    form/spelling of X" sense (kaikki's alt_of / form_of, or the gloss itself)."""
    out = []
    for s in entry.get('senses') or []:
        gl = [g.strip() for g in s.get('glosses') or [] if g.strip()]
        tags = set(s.get('tags') or [])
        alt = ''
        for f in (s.get('alt_of') or []) + (s.get('form_of') or []):
            if f.get('word'):
                alt = vi.nfc(f['word'])
                break
        if not alt and gl and english.FORM_OF.match(gl[-1]) and not english.SHORT_FOR.match(gl[-1]):
            m = re.search(r'\b(?:of|for) ([^\s(“"][^(“"]*?)(?:\s*\(|[.:]|$)', gl[-1])
            alt = vi.nfc(m.group(1).strip()) if m else ''
        if gl and TONE_PLACEMENT.match(gl[-1]):
            continue          # "Traditional tone placement spelling of toà": the same key (vi.key), not a sense
        if alt and ('pronunciation-spelling' in tags or PRON_SPELLING.search(gl[-1] if gl else '')):
            tags = tags | {'pronunciation-spelling'}
        g = gl[0] if len(gl) > 1 and not english.DESCRIPTION.match(gl[0]) and len(gl[0]) <= english.MAX_FIRST \
            else (gl[-1] if gl else '')
        out.append((g, tags, len(s.get('examples') or []), alt))
    return out


TONE_PLACEMENT = re.compile(r'^(?:traditional|modern|new|old)?\s*tone[- ]placement (?:spelling|variant|form) of\b', re.I)
PRON_SPELLING = re.compile(r'\b(?:pronunciation spelling|eye dialect|eye-dialect|dialectal spelling)\b', re.I)


def alt_of(senses):
    """(target key, 'spelling' | 'pron' | 'form') when every usable sense of an entry is an alternative spelling/form of
    one word, else ('', ''). 'pron': a pronunciation / eye-dialect spelling (ga of ra, í of ấy, dậy of vậy): another
    word's key, never pooled with it (review 2, finding 1)."""
    ss = [s for s in senses if s[0] and not english.SKIP_TAGS & s[1]]
    if ss and all(s[3] for s in ss):
        kind = 'pron' if any('pronunciation-spelling' in s[1] for s in ss) else \
            'spelling' if any(re.search(r'\bspelling\b', s[0], re.I) for s in ss) else 'form'
        return vi.key(ss[0][3]), kind
    return '', ''


def english_of(entry):
    ss = [s for s in entry.get('senses') or [] if not SKIP_SENSE & set(s.get('tags') or [])]
    ss = sorted(ss, key=lambda s: bool(LATE_SENSE & set(s.get('tags') or [])))      # stable: the source order otherwise
    gl = []
    for s in ss:
        for g in s.get('glosses') or []:
            g = g.strip()
            if g and g not in gl and not TONE_PLACEMENT.match(g):
                gl.append(g)
    return '; '.join(gl[:4])


SV_READING = re.compile(r'^Sino-Vietnamese reading of ([㐀-鿿豈-﫿\U00020000-\U0003ffff])')


def load_kaikki(raw, add):
    path = need(raw, 'kaikki', 'kaikki.org-dictionary-Vietnamese.jsonl')
    n_chars = Counter()
    for line in open(path, encoding='utf-8'):
        e = json.loads(line)
        if e.get('lang_code') != 'vi':
            continue
        word = vi.nfc(e.get('word', '')).strip()
        if not word:
            continue
        if len(word) == 1 and is_cjk_word(word):          # a character: its readings
            ords = Counter()
            rel = list(e.get('related') or []) + [r for s in e.get('senses') or [] for r in s.get('related') or []]
            for r in rel:
                kind = next((READING_TAGS[t] for t in r.get('tags') or [] if t in READING_TAGS), None)
                if kind and r.get('word'):
                    for x in re.split(r'[,;/]', r['word']):
                        if x.strip():
                            add.hanviet(word, x.strip(), kind, ords[kind])
                            ords[kind] += 1
                            n_chars[kind] += 1
            for f in e.get('forms') or []:
                if 'Hán-Nôm' in (f.get('tags') or []) and f.get('form'):
                    add.hanviet(word, f['form'], 'hannom', ords['hannom'])
                    ords['hannom'] += 1
                    n_chars['hannom'] += 1
            continue
        if vi.CJK.search(word) or e.get('pos') == 'character':
            continue
        if e.get('pos') == 'romanization':
            # 786 entries "y: Sino-Vietnamese reading of 衣": a Hán-Việt reading of a character (kind hv), not a word.
            # Each is also kept as an entry of pos `character-reading`, tagged with the character (tam~三): the card
            # of a character taught without a word entry (Sino-Vietnamese numerals); never a word of its own (not
            # ranked, not the main sense of its spelling, not in coverage counts).
            for s in e.get('senses') or []:
                g = (s.get('glosses') or [''])[0]
                m = SV_READING.match(g)
                if m and len(word.split()) == 1:
                    add.hanviet(m.group(1), word, 'hv', 99, label='romanization')
                    n_chars['hv-rom'] += 1
                    gm = re.search(r'\(“([^”]+)”', g)
                    add.entry(word, gm.group(1) if gm else '', m.group(1), pos='character-reading', tag=m.group(1),
                              origin='sino', origin_note=f'Hán-Việt reading of {m.group(1)}')
            continue
        en = english_of(e)
        ana = sino_analysis(e)
        if not en and ana is None and not e.get('etymology_text'):
            continue                                       # an empty stub
        examples = []
        for s in e.get('senses') or []:
            for x in s.get('examples') or []:
                if x.get('text') and (x.get('english') or x.get('translation')) and not vi.CJK.search(x['text']):
                    examples.append({'vi': x['text'], 'en': x.get('english') or x.get('translation')})
        chars = ana[0] if ana and ana[1] == 'hv' else ''
        origin, note = origin_of(e, ana)
        etymon = ''
        if origin == 'nonhv':
            m = re.match(etym.CJK + '+', note)
            etymon = note if ana else (m.group(0) if m else '')
            note = '' if ana else note
        senses = sense_rows(e)
        alt, alt_kind = alt_of(senses)
        doubt = etym.doubt_words(e.get('etymology_text')) if origin in ('sino', 'nonhv') else ''
        eid = add.entry(word, en, chars, pos=e.get('pos', ''), src_id=str(e.get('etymology_number') or ''),
                        origin=origin, examples=examples[:3], etymon=etymon, alt_of=alt, alt_kind=alt_kind,
                        origin_note=note, doubt_why=doubt)
        add.con.executemany('INSERT INTO sense VALUES (?,?,?,?,?,?)',
                            [(eid, i, vi.nfc(g), ','.join(sorted(t)), x, a) for i, (g, t, x, a) in enumerate(senses)])
    print(f"  wiktionary character readings: {n_chars['hv']} Hán-Việt, {n_chars['nom']} Nôm, "
          f"{n_chars['hannom']} Hán-Nôm (not told apart), {n_chars['hv-rom']} Hán-Việt from 'Sino-Vietnamese reading "
          f"of X' entries")
    if add.n and not n_chars['hv']:
        print('  WARNING: no han-viet-reading found: the kaikki format may have changed (tools/build_db.py load_kaikki)')


# ---------------------------------------------------------------------------------------------- Thiều Chửu
def load_thieuchuu(raw, add):
    for line in open(need(raw, 'thieuchuu', 'TudienThienChuu.tab'), encoding='utf-8'):
        ch, _, body = line.partition('\t')
        ch = ch.strip()
        if len(ch) != 1 or not is_cjk_word(ch):
            continue
        for i, r in enumerate(thieuchuu_head(body)):
            add.hanviet(ch, r, 'hv', i)
            add.n += 1


def thieuchuu_head(body):
    """The readings at the head of a Thiều Chửu article: 'sanh|sinh<br>…' -> ['sanh', 'sinh']. A head may carry the
    stroke count ('đại (5 n)') or a full stop ('nảm.'); 1,350 lines use the Icelandic Ð (U+00D0) for Đ. A piece that
    is still not one word is reported, never dropped silently."""
    head = body.split('<br>')[0].replace('Ð', 'Đ')
    out = []
    for x in head.split('|'):
        x = re.sub(r'\s*\(\s*\d+\s*n\s*\)\s*$', '', x.strip()).rstrip('.').strip()
        if re.fullmatch(r'[^\W\d_]+', x):
            out.append(x)
        elif x:
            print(f'  thieuchuu: head piece not read: {x!r}')
    return out


# ---------------------------------------------------------------------------------------------- Unihan kVietnamese
def load_unihan(raw, add):
    kmandarin = need(raw, 'unihan', 'kMandarin.txt')
    for line in open(kmandarin, encoding='utf-8'):
        if line.startswith('#') or '\t' not in line:
            continue
        cp, val = line.rstrip('\n').split('\t')
        a, _, b = cp.partition('..')
        for c in range(int(a, 16), int(b or a, 16) + 1):
            add.con.executemany('INSERT INTO mandarin_pref VALUES (?,?,?)',
                                [(chr(c), vi.nfc(r), i) for i, r in enumerate(val.split())])
    pairs = set()
    for name in ('kSemanticVariant.txt', 'kZVariant.txt'):
        for line in open(need(raw, 'unihan', name), encoding='utf-8'):
            if line.startswith('#') or '\t' not in line:
                continue
            cp, val = line.rstrip('\n').split('\t')
            a = chr(int(cp.split('..')[0], 16))
            for m in re.finditer(r'U\+([0-9A-F]+)', val):
                b = chr(int(m.group(1), 16))
                if a != b:
                    pairs |= {(a, b), (b, a)}
    add.con.executemany('INSERT INTO variant VALUES (?,?)', sorted(pairs))
    for line in open(need(raw, 'unihan', 'kVietnamese.txt'), encoding='utf-8'):
        if line.startswith('#') or '\t' not in line:
            continue
        cp, val = line.rstrip('\n').split('\t')
        a, _, b = cp.partition('..')
        for c in range(int(a, 16), int(b or a, 16) + 1):
            for i, r in enumerate(val.split()):
                add.hanviet(chr(c), r, 'unchecked', i)
                add.n += 1


# ---------------------------------------------------------------------------------------------- rime-cantonese
def rime_rows(path):
    body = False
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line == '...':
            body = True
            continue
        if not body or not line or line.startswith('#'):
            continue
        p = line.split('\t')
        if len(p) >= 2:
            yield p[0], p[1], (p[2] if len(p) > 2 else '')


def load_rime(raw, add):
    for ch, j, w in rime_rows(need(raw, 'rime-cantonese', 'jyut6ping3.chars.dict.yaml')):
        share = int(w.rstrip('%')) if w.endswith('%') else None
        add.chinese(ch, 'yue', j, 'char', share)
    for wd, j, _ in rime_rows(need(raw, 'rime-cantonese', 'jyut6ping3.words.dict.yaml')):
        if len(wd) > 1 and is_cjk_word(wd):
            add.chinese(wd, 'yue', j, 'word')


# ---------------------------------------------------------------------------------------------- MOE (Taigi)
MOE_WORD_TYPES = {'1', '2', '3', '5'}       # 屬性: main entries, single characters, synonyms, words shared with Mandarin


def load_moe(raw, add):
    """Taigi readings. A character's literary layer: its readings marked literary (文白屬性 1); only when it has none, its
    unmarked ones (0). On the first real build the unmarked readings of characters that also have a literary one were
    colloquial words: 共 kā "with" beside 共 kiōng, 過 koh "again" beside 過 kò, which made 黨共產 tóng-(kā/kiōng)-sán."""
    path = need(raw, 'moedict-data-twblg', 'uni', '詞目總檔.csv')
    chars = defaultdict(list)                 # char -> [(reading, wb)] in the MOE's order
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if r['屬性'] not in MOE_WORD_TYPES:
            continue
        h, t, wb = vi.nfc(r['詞目']), vi.nfc(r['音讀']), r['文白屬性']
        if not is_cjk_word(h) or not t:
            continue
        # 'ji̍t/li̍t': the main reading, then the accent variants, each its own row in the MOE's order
        for v in [x.strip() for x in t.split('/') if x.strip()]:
            if len(h) == 1:
                if wb in ('1', '0'):              # 1 literary (文讀), 0 no literary/colloquial split
                    chars[h].append((v, wb))
            elif wb in ('0', '1'):                # the word's own reading (often colloquial: 生日 senn-ji̍t)
                add.chinese(h, 'nan', v, 'word', note='literary' if wb == '1' else '')
    for h, rs in chars.items():
        lit = [x for x in rs if x[1] == '1']
        for v, wb in (lit or rs):
            add.chinese(h, 'nan', v, 'char', note='literary' if wb == '1' else 'unmarked')


# ---------------------------------------------------------------------------------------------- CC-CEDICT
def load_cedict(raw, add):
    """Keyed on the TRADITIONAL form only (Vietnamese chữ Hán are traditional): the readings of a simplified form never
    reach a traditional character (只 is not read zhī because 隻 simplifies to 只). Capitalised pinyin = a name."""
    use = Counter()
    for e in json.load(open(need(raw, 'cedict', 'package', 'cedict.json'), encoding='utf-8')):
        t, p = e.get('traditional') or '', e.get('pinyin') or ''
        if not is_cjk_word(t) or not p:
            continue
        note = 'name' if p[:1].isupper() else ''
        add.chinese(t, 'cmn', bridge.pinyin_marks(p), 'char' if len(t) == 1 else 'word', note=note)
        if e.get('english') and not note:
            add.con.execute('INSERT INTO cedict_en VALUES (?,?)', (t, '; '.join(e['english'])))
        syl = p.split()
        if len(t) > 1 and len(syl) == len(t) and not note:
            for c, x in zip(t, syl):
                use[(c, bridge.pinyin_marks(x).lower())] += 1
    add.con.executemany('INSERT INTO cmn_use VALUES (?,?,?)', [(c, r, n) for (c, r), n in sorted(use.items())])


# ---------------------------------------------------------------------------------------------- Tatoeba
VI_LETTERS = re.compile(r'[ăâêôơưđ]|[\u0300\u0301\u0303\u0309\u0323]')


def tatoeba_problem(text):
    """Why a Tatoeba sentence filed as Vietnamese is not used ('' if it is). Measured on the snapshot of 17 Nov 2026
    (33,328 sentences, 22,190 with an English translation): 3 are written in chữ Nôm, a few are not Vietnamese at all
    (an Esperanto line); 257 have over 30% of words that are not Vietnamese syllables, nearly all because of names and
    loans (Boston, golf, Linux), which are kept. A sentence is refused when it contains Han characters, or when none of
    its words has a Vietnamese letter or tone mark and fewer than half are possible Vietnamese syllables."""
    t = vi.nfc(text)
    if vi.CJK.search(t):
        return 'Han characters (chữ Nôm)'
    toks = re.findall(r'[^\W\d_]+', t.lower())
    if not toks:
        return 'no word'
    valid = sum(1 for x in toks if not vi.syllable_problems(x))
    if not VI_LETTERS.search(unicodedata.normalize('NFD', t.lower())) and valid * 2 < len(toks):
        return 'not Vietnamese'
    return ''


def load_tatoeba(raw, add):
    """Example sentences with their English translation, sentence id and author, attached after the dictionary is
    loaded (see attach_examples). Sentences without an author (orphans, 4) are not used: each example is credited to
    its author. tatoeba_problem() drops lines that are not Vietnamese. The snapshot has no information on authors'
    proficiency (Tatoeba's user_languages export is not in it); the six authors with most sentences (two thirds of
    them) were sampled by eye on 18 Nov 2026 and read as fluent, so no author is filtered."""
    def rows(name):
        with bz2.open(need(raw, 'tatoeba', name), 'rt', encoding='utf-8') as f:
            for line in f:
                yield line.rstrip('\n').split('\t')
    vie = {p[0]: (vi.nfc(p[2]), p[3]) for p in rows('vie_sentences_detailed.tsv.bz2') if len(p) >= 4}
    eng = {p[0]: p[2] for p in rows('eng_sentences_detailed.tsv.bz2') if len(p) >= 3}
    dropped = Counter()
    pairs = {}
    for p in rows('vie-eng_links.tsv.bz2'):
        if len(p) >= 2 and p[0] in vie and p[1] in eng and p[0] not in pairs:
            pairs[p[0]] = eng[p[1]]
    for i in list(pairs):
        why = 'no author' if vie[i][1] in ('', '\\N') else tatoeba_problem(vie[i][0])
        if why:
            dropped[why] += 1
            del pairs[i]
    add.sentences = [(vie[i][0], en, f'#{i} by {vie[i][1]}') for i, en in pairs.items()]
    add.n = len(add.sentences)
    print(f'  tatoeba: {len(vie)} Vietnamese sentences, {len(pairs) + sum(dropped.values())} with English; used '
          f'{len(pairs)}; not used: {dict(dropped)}')


def load_tatoeba_challenge(raw, add):
    """Vietnamese sentences of the Tatoeba Challenge eng-vie test set (no ids, no authors): build-time corpus for the
    word counts only, never stored in the database (licence conflict: see ATTRIBUTION.md)."""
    p = need(raw, 'tatoeba-challenge', 'eng-vie-test.txt')
    add.corpus = [vi.nfc(x.rstrip('\n').split('\t')[3]) for x in open(p, encoding='utf-8') if x.count('\t') >= 3]
    add.n = len(add.corpus)


def load_translations(raw, add):
    """The English Wiktionary's translation tables that have a Vietnamese row (snapshot file derived by
    .github/snapshot-translations.py): one row per (English headword, part of speech, table, language, word).
    Vietnamese rows (table `translation`): written in quốc ngữ (not chữ Nôm, not "various"), keyed with tools/vi.py;
    n_vi = the number of Vietnamese words of the same table; used for card English (compose_english): which sense of a
    word is the main one, and its English when the entry's own senses lack it (bận "busy"). Chinese rows (Mandarin,
    Cantonese, Min Nan; table `translation_zh`): the sense check of Hán-Việt analyses (etymology_states)."""
    import gzip
    tables = defaultdict(list)
    zh = []
    with gzip.open(need(raw, 'kaikki', 'en-translations.tsv.gz'), 'rt', encoding='utf-8') as f:
        for line in f:
            p = (line.rstrip('\n').split('\t') + [''] * 7)[:7]
            en, pos, _n, sense, word, tags, lang = p
            word = vi.nfc(word).strip()
            if not en or not word:
                continue
            if lang in ('cmn', 'zh', 'yue', 'nan'):
                if is_cjk_word(word):
                    zh.append((en, pos, sense, word))
                continue
            if lang != 'vi' or vi.CJK.search(word) or word.lower() in ('various', 'see', '-'):
                continue
            if not all(re.fullmatch(r"[^\W\d_]+", x) for x in word.replace('-', ' ').split()):
                continue
            tables[(en, pos, sense)].append((vi.key(word), tags))
    rows = []
    for (en, pos, sense), vs in tables.items():
        keys = {k for k, _ in vs}
        for k, tags in vs:
            rows.append((en, pos, sense, k, tags, len(keys)))
    add.con.executemany('INSERT INTO translation VALUES (?,?,?,?,?,?)', rows)
    add.con.executemany('INSERT INTO translation_zh VALUES (?,?,?,?)', sorted(set(zh)))
    add.n = len(rows) + len(zh)


def load_frequencywords(raw, add):
    """FrequencyWords' syllable counts: read by tools/freq.py (fallback when wordfreq is not installed) and by the
    syllable-table validation (tools/vi.py validate_syllables); nothing is stored but the source row."""
    need(raw, 'frequencywords', 'vi_50k.txt')


# Each source: id, name, version (as pinned in data/fetch.sh), licence, url, commercial_ok, loader.
SOURCES = [
    {'id': 'wiktionary', 'name': 'English Wiktionary, Vietnamese entries (kaikki.org extraction)',
     'version': snapshot_pin('wiktionary'), 'licence': 'CC BY-SA 4.0 / GFDL',
     'url': 'https://kaikki.org/dictionary/Vietnamese/', 'commercial_ok': True, 'load': load_kaikki},
    {'id': 'wiktionary-tr', 'name': "English Wiktionary, the Vietnamese translations of English entries (kaikki.org "
     "raw extraction, filtered on our snapshot runner)", 'version': snapshot_pin('wiktionary-tr'),
     'licence': 'CC BY-SA 4.0 / GFDL', 'url': 'https://kaikki.org/dictionary/rawdata.html', 'commercial_ok': True,
     'load': load_translations},
    {'id': 'thieuchuu', 'name': 'Thiều Chửu, Hán Việt tự điển (catusf/tudien)', 'version': 'a7dd918',
     'licence': 'public domain in Vietnam; repository CC0 1.0', 'url': 'https://github.com/catusf/tudien',
     'commercial_ok': True, 'load': load_thieuchuu},
    {'id': 'unihan', 'name': 'Unihan kVietnamese, kMandarin, kSemanticVariant, kZVariant (Unicode 18.0.0)', 'version': 'unicodetools ccc86e5',
     'licence': 'Unicode License v3', 'url': 'https://github.com/unicode-org/unicodetools', 'commercial_ok': True,
     'load': load_unihan},
    {'id': 'rime', 'name': 'rime-cantonese (CanCLID)', 'version': '259f0e4', 'licence': 'CC BY 4.0',
     'url': 'https://github.com/rime/rime-cantonese', 'commercial_ok': True, 'load': load_rime},
    {'id': 'moe', 'name': '教育部臺灣台語常用詞辭典 (g0v/moedict-data-twblg)', 'version': '4626bfc',
     'licence': 'CC BY-ND 3.0 TW', 'url': 'https://github.com/g0v/moedict-data-twblg', 'commercial_ok': True,
     'load': load_moe},
    {'id': 'cedict', 'name': 'CC-CEDICT (cedict-json)', 'version': '1.3.20251213', 'licence': 'CC BY-SA 4.0',
     'url': 'https://www.mdbg.net/chinese/dictionary?page=cc-cedict', 'commercial_ok': True, 'load': load_cedict},
    {'id': 'tatoeba', 'name': 'Tatoeba, Vietnamese-English sentences', 'version': snapshot_pin('tatoeba'),
     'licence': 'CC BY 2.0 FR (some CC0 1.0)', 'url': 'https://tatoeba.org/en/downloads', 'commercial_ok': True,
     'load': load_tatoeba},
    # licence in conflict (README CC BY 2.0 FR, LICENSE CC BY-NC-SA 4.0): treated as non-commercial, so it never
    # reaches the public database (vi.db), only the private build's word counts
    {'id': 'tatoeba-challenge', 'name': 'Tatoeba sentences, Helsinki-NLP Tatoeba Challenge eng-vie test set (corpus '
     'for word counts only, not stored)', 'version': 'bd05f08', 'licence': 'CC BY 2.0 FR per README; repo LICENSE '
     'CC BY-NC-SA 4.0 (conflict, see ATTRIBUTION.md)', 'url': 'https://github.com/Helsinki-NLP/Tatoeba-Challenge',
     'commercial_ok': False, 'load': load_tatoeba_challenge},
    {'id': 'frequencywords', 'name': 'FrequencyWords, OpenSubtitles 2018 vi_50k (syllable counts)', 'version': '525f9b5',
     'licence': 'CC BY-SA 4.0 (content)', 'url': 'https://github.com/hermitdave/FrequencyWords', 'commercial_ok': True,
     'load': load_frequencywords},
]


class Adder:
    """What a source loader writes through. Every text is put in NFC and keyed with tools/vi.py."""

    def __init__(self, con, source):
        self.con, self.source = con, source
        self.n = 0
        self.sentences = []
        self.corpus = []
        self._ord = Counter()

    def entry(self, word, english='', chars='', label='', pos='', tag='', src_id='', freq=None, examples=(),
              origin='', etymon='', alt_of='', alt_kind='', origin_note='', doubt_why=''):
        word = vi.nfc(word).strip()
        cur = self.con.execute(
            'INSERT INTO entry(source, src_id, word, key, tkey, toneless, tag, pos, english, chars, origin, label, freq, '
            'etymon, alt_of, alt_kind, origin_note, doubt_why) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (self.source, src_id, word, vi.key(word), vi.tkey(word), vi.toneless(vi.key(word)), tag or '', pos,
             vi.nfc(english), vi.nfc(chars), origin, label or '', freq, vi.nfc(etymon), alt_of, alt_kind,
             vi.nfc(origin_note), doubt_why))
        for ex in examples:
            self.con.execute('INSERT INTO example(entry_id, source, vi, en, ref) VALUES (?,?,?,?,?)',
                             (cur.lastrowid, self.source, vi.nfc(ex.get('vi')), vi.nfc(ex.get('en')), ex.get('ref', '')))
        self.n += 1
        return cur.lastrowid

    def hanviet(self, char, reading, kind='hv', ord_=None, label=''):
        self.con.execute('INSERT INTO hanviet(char, reading, kind, source, ord, label) VALUES (?,?,?,?,?,?)',
                         (char, vi.nfc(reading).lower(), kind, self.source, ord_, label))

    def chinese(self, chars, lang, reading, level=None, share=None, note=''):
        assert lang in bridge.LANGS, lang
        level = level or ('char' if len(chars) == 1 else 'word')
        self._ord[(chars, lang)] += 1
        self.con.execute('INSERT INTO chinese VALUES (?,?,?,?,?,?,?,?,NULL)',
                         (chars, lang, vi.nfc(reading), self.source, level, share, note, self._ord[(chars, lang)]))
        self.n += 1


def load_fixture(add):
    d = yaml.safe_load(open(FIXTURE, encoding='utf-8'))
    for e in d['entries']:
        add.entry(e['word'], e.get('en', ''), e.get('chars', ''), e.get('label', ''), e.get('pos', ''), e.get('tag', ''),
                  examples=[e['example']] if e.get('example') else (), origin='sino' if e.get('chars') else '')
    for ch, r in (d.get('hanviet') or {}).items():
        for x in str(r).split('/'):
            add.hanviet(ch, x.strip())
    for chars, langs in (d.get('chinese') or {}).items():
        for lang, r in langs.items():
            for x in str(r).split(' / '):
                add.chinese(chars, lang, x.strip())


# ---------------------------------------------------------------------------------------------- after the sources
def hv_crosscheck(con):
    """hanviet.checked: Wiktionary's Hán-Việt readings against Thiều Chửu's and back (tone-mark placement ignored)."""
    sets = defaultdict(lambda: defaultdict(set))
    for ch, r, src in con.execute("SELECT char, reading, source FROM hanviet WHERE kind='hv'"):
        sets[src][ch].add(vi.tkey(r))
    rows = []
    for a, b in (('wiktionary', 'thieuchuu'), ('thieuchuu', 'wiktionary')):
        for rid, ch, r in con.execute("SELECT rowid, char, reading FROM hanviet WHERE kind='hv' AND source=?", (a,)).fetchall():
            other = sets[b].get(ch)
            rows.append((None if not other else int(vi.tkey(r) in other), rid))
    con.executemany('UPDATE hanviet SET checked=? WHERE rowid=?', rows)
    st = Counter(c for (c,) in con.execute("SELECT checked FROM hanviet WHERE kind='hv' AND source='wiktionary'"))
    if sum(st.values()):
        print(f'Hán-Việt cross-check, Wiktionary readings: {st[1]} also in Thiều Chửu, {st[0]} not, '
              f'{st[None]} for characters Thiều Chửu lacks')


def southern_variants(con):
    """Northern standard first (tools/hanviet.py SOUTHERN): a Southern form gets label 'southern'; where the character
    has no Northern form in any Hán-Việt source, the Northern form is derived (source 'derived', label 'derived').
    Returns the characters affected, printed by the build."""
    mand = defaultdict(set)
    for ch, r in con.execute("SELECT chars, reading FROM chinese WHERE lang='cmn' AND level='char' AND note != 'name'"):
        mand[ch].add(r)
    con.execute("INSERT INTO source VALUES ('derived', 'Northern Hán-Việt forms derived from Southern ones (tools/hanviet.py "
                "SOUTHERN)', '', 'MIT (this repository)', '', 1, 0)")
    rows = con.execute("SELECT rowid, char, reading FROM hanviet WHERE kind='hv' AND source != 'fixture'").fetchall()
    have = defaultdict(set)
    for _, ch, r in rows:
        have[ch].add(vi.key(r))
    affected = []
    for rid, ch, r in rows:
        north = hanviet.southern(r, mand.get(ch, ()))
        if not north or (north not in have[ch] and vi.key(r) in hanviet.NO_DERIVE):
            continue
        con.execute("UPDATE hanviet SET label='southern' WHERE rowid=?", (rid,))
        if north in have[ch]:
            affected.append((ch, r, north, 'both given'))
        else:
            con.execute("INSERT INTO hanviet(char, reading, kind, source, ord, label) VALUES (?,?,'hv','derived',-1,"
                        "'derived')", (ch, north))
            have[ch].add(north)
            affected.append((ch, r, north, 'derived'))
    if affected:
        print(f'Hán-Việt Southern variants (tools/hanviet.py): {len(affected)}: '
              + ', '.join(f'{c} {r}->{n} ({how})' for c, r, n, how in affected))
    return affected


def check_syllables(k):
    """The syllables of a key for the Hán-Việt check: hyphens and punctuation separate them (Pháp-Hoa 法華, "ôn, lương,
    cung" 溫良恭)."""
    return re.sub(r'[^\w\s]', ' ', k).split()


def rkey(s):
    """Reading key for comparing a syllable with a character's reading: tone-mark placement ignored (vi.tkey), and the
    i/y spellings of one syllable equal (kì = kỳ, tỉ = tỷ; quí/quý and uy untouched)."""
    return re.sub(r'^([bcdđghklmnprstvx]+)y(\d)$', r'\1i\2', vi.tkey(s))


def hannom_attested(con, min_words=2):
    """Readings of a character attested by Wiktionary's own Sino-Vietnamese words, used as Hán-Việt (kind hv, label
    'attested', source wiktionary):
      * Wiktionary gives 5,308 characters only as untagged "Hán-Nôm" readings (Hán-Việt and Nôm not told apart: 車 xa,
        xe, xế). For a character no Hán-Việt source reads (Thiều Chửu's copy lacks 告 值 冊), a Hán-Nôm reading that a
        Sino-Vietnamese word reads it with (價值 giá trị -> 值 trị);
      * for any character, a reading that some source gives it (Wiktionary Hán-Nôm or Nôm, Unihan) and that at least
        `min_words` Sino-Vietnamese words read it with: 實 thực (thực tế, thực hiện, hiện thực…; Thiều Chửu has only
        thật, Wiktionary has no tagged reading), 平 bằng (công bằng, Cao Bằng).
    Returns the number of readings added."""
    have = {c for (c,) in con.execute("SELECT DISTINCT char FROM hanviet WHERE kind='hv' AND source != 'fixture'")}
    hvset = defaultdict(set)
    for ch, r in con.execute("SELECT char, reading FROM hanviet WHERE kind='hv'"):
        hvset[ch].add(rkey(r))
    cand = defaultdict(lambda: defaultdict(set))       # char -> rkey -> kinds
    for ch, r, kind in con.execute("SELECT char, reading, kind FROM hanviet WHERE kind IN ('hannom', 'nom', 'unchecked')"):
        cand[ch][rkey(r)].add(kind)
    used = defaultdict(set)                            # (char, rkey) -> words
    spelled = {}
    for k, chars in con.execute("SELECT key, chars FROM entry WHERE origin='sino' AND chars != '' AND "
                                "pos != 'character-reading'").fetchall():
        syl = check_syllables(k)
        if len(syl) == len(chars):
            for s, c in zip(syl, chars):
                rk = rkey(s)
                if rk in cand.get(c, ()) and rk not in hvset[c]:
                    used[(c, rk)].add(k)
                    spelled.setdefault((c, rk), s)
    added = []
    for (c, rk), ws in sorted(used.items()):
        if len(ws) >= min_words or (c not in have and 'hannom' in cand[c][rk]):
            added.append((c, spelled[(c, rk)], len(ws)))
    con.executemany("INSERT INTO hanviet(char, reading, kind, source, ord, label) VALUES (?,?,'hv','wiktionary',98,"
                    "'attested')", [(c, r) for c, r, _ in added])
    top = sorted(added, key=lambda x: -x[2])[:12]
    print(f'readings attested by Sino-Vietnamese words, used as Hán-Việt: {len(added)} ({len({c for c, _, _ in added})} '
          f'characters), e.g. ' + ', '.join(f'{c} {r} ({n} words)' for c, r, n in top))
    return len(added)


def unihan_fallback(con):
    """A character no Hán-Việt source reads (Wiktionary, Thiều Chửu) gets its Unihan kVietnamese readings of Hán-Việt
    shape (tools/hanviet.py hv_shaped), labelled 'fallback' and shown as "unchecked (Unihan)"."""
    inv = hanviet.inventory([r for (r,) in con.execute("SELECT reading FROM hanviet WHERE source='thieuchuu'")])
    if not inv[1]:
        return
    rows = con.execute("SELECT rowid, char, reading FROM hanviet h WHERE source='unihan' AND NOT EXISTS (SELECT 1 FROM "
                       "hanviet x WHERE x.char = h.char AND x.kind = 'hv' AND x.source != 'fixture')").fetchall()
    ok = [(rid,) for rid, ch, r in rows if hanviet.hv_shaped(r, inv)]
    con.executemany("UPDATE hanviet SET label='fallback' WHERE rowid=?", ok)
    print(f'Unihan fallback: {len(ok)} readings of Hán-Việt shape for characters no Hán-Việt source reads '
          f'({len(rows) - len(ok)} others, Nôm-shaped or invalid, not used)')


def rank_chinese(con):
    """chinese.rank: the display order of a character's or word's readings (schema.sql). Mandarin: Unihan kMandarin's
    customary reading first, then by the number of CC-CEDICT words that use the reading, then by reading (stable)."""
    pref = {(c, r): o for c, r, o in con.execute('SELECT char, reading, ord FROM mandarin_pref')}
    use = Counter({(c, r): n for c, r, n in con.execute('SELECT char, reading, n FROM cmn_use')})
    rows = con.execute('SELECT rowid, chars, lang, level, reading, share, ord, note FROM chinese').fetchall()
    groups = defaultdict(list)
    for r in rows:
        groups[(r[1], r[2], r[3])].append(r)
    upd = []
    for (chars, lang, level), rs in groups.items():
        if lang == 'cmn':
            k = lambda r: (r[7] == 'name', pref.get((chars, r[4]), 99), -use[(chars, r[4].lower())], r[6], r[4])  # noqa: E731
        elif lang == 'yue':
            k = lambda r: (r[5] is not None, -(r[5] or 0), r[6], r[4])  # noqa: E731
        else:
            k = lambda r: (r[6], r[4])  # noqa: E731
        upd += [(i, r[0]) for i, r in enumerate(sorted(rs, key=k))]
    con.executemany('UPDATE chinese SET rank=? WHERE rowid=?', upd)


def word_checks(con):
    """entry.hv_check, and the computed labels: same (Sino-Vietnamese) and native (inherited from Vietic). A Sino-
    Vietnamese analysis whose characters do not match the syllables (number, or readings) is not labelled same and its
    characters are not shown (cards.py); `make lint` prints these suspects (tools/verify_words.py). False friends
    cannot be detected: they come from the course lexicon's false_friend column (course/lexicon.tsv, tools/cards.py)."""
    hv = defaultdict(set)
    for ch, r in con.execute("SELECT char, reading FROM hanviet WHERE kind IN ('hv', 'hannom') OR label = 'fallback'"):
        hv[ch].add(rkey(r))
    rows = []
    for eid, k, chars in con.execute("SELECT id, key, chars FROM entry WHERE chars != ''").fetchall():
        syl = check_syllables(k)
        if len(syl) != len(chars):
            rows.append(('length', eid))
        elif all(hv.get(c) for c in chars):
            rows.append(('ok' if all(rkey(s) in hv[c] for s, c in zip(syl, chars)) else 'differs', eid))
        else:
            rows.append(('', eid))
    con.executemany('UPDATE entry SET hv_check=? WHERE id=?', rows)
    con.execute("UPDATE entry SET label='same' WHERE label='' AND origin='sino' AND hv_check NOT IN ('differs', 'length')")
    con.execute("UPDATE entry SET label='native' WHERE label='' AND origin='vietic'")
    c = Counter(r for r, _ in rows)
    if rows:
        print(f"Sino-Vietnamese entries vs the Hán-Việt readings: {c['ok']} ok, {c['differs']} differ, "
              f"{c['length']} with characters and syllables of different number (these two: suspects, `make lint`), "
              f"{c['']} not checkable")
    none = sorted({ch for (chars,) in con.execute("SELECT DISTINCT chars FROM entry WHERE chars != ''") for ch in chars
                   if not bridge.hv_readings(con, ch)})
    if none:
        print(f'characters of Sino-Vietnamese entries with NO Hán-Việt reading: {len(none)}: {" ".join(none[:80])}')


# ---------------------------------------------------------------------------------------------- spelling groups
IY = re.compile(r'^([bcdđghklmnprstvx]+|qu)([yýỳỷỹỵ])$')
I_FOR_Y = dict(zip('yýỳỷỹỵ', 'iíìỉĩị'))


def iy_key(k):
    """The key with the i/y spellings of one syllable made equal (lý = lí, kỳ = kì, quý = quí): a consonant (or qu)
    + y, the whole rhyme, is the same syllable as the consonant + i. y alone (ý) and the rhyme uy (tuy) are untouched."""
    return ' '.join(IY.sub(lambda m: m.group(1) + I_FOR_Y[m.group(2)], x) for x in k.split())


def ortho_key(k):
    """The key with only orthographic differences removed: i/y (iy_key), hyphens as syllable breaks, letter case."""
    return iy_key(' '.join(k.lower().replace('-', ' ').split()))


def spelling_groups(con, raw):
    """Pool the SPELLINGS of one word into one key (table `spelling`, entry.key rewritten): keys equal but for the i/y
    spelling of a syllable (lí do / lý do, kĩ thuật / kỹ thuật, Mĩ / Mỹ), hyphens or letter case (tiến-hoá / tiến hoá,
    châu âu / châu Âu); tone-mark placement is already one key (vi.key). Nothing else is pooled (review 2, finding 1:
    pooling every Wiktionary "alternative / pronunciation spelling of" pair merged ga into ra, ấy into ý, dậy into
    vậy, nhỉ into nhờ): an alternative form, a pronunciation or eye-dialect spelling, a dialectal form keeps its own
    key, senses and rank; its card shows the cross-reference only.
    The house spelling of a group (the key every entry of the group gets, the spelling lint asks for in lessons) is
    a spelling without hyphens (today's orthography: a lô, not a-lô), then the most frequent one: wordfreq's estimate for the spelling as a phrase (tools/freq.py phrase_freq, English
    leakage removed, so `my` does not win over `mi` by the English word), ties to the spelling Wiktionary has its
    main entry under. Returns the number of groups."""
    keys = [k for (k,) in con.execute("SELECT DISTINCT e.key FROM entry e JOIN source s ON s.id = e.source "
                                      "WHERE s.fixture = 0")]
    parent = {k: k for k in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    by_iy = defaultdict(list)
    for k in keys:
        by_iy[ortho_key(k)].append(k)
    for ks in by_iy.values():
        for k in ks[1:]:
            union(ks[0], k)
    groups = defaultdict(list)
    for k in keys:
        groups[find(k)].append(k)
    groups = [sorted(g) for g in groups.values() if len(g) > 1]
    main = {k for (k,) in con.execute("SELECT DISTINCT key FROM entry WHERE alt_kind = '' AND pos != 'character-reading'")}
    pf = freq.phrase_freq(raw, {x for g in groups for k in g for x in k.replace('-', ' ').split()})
    rows = []
    for g in groups:
        canon = max(g, key=lambda k: ('-' not in k, pf(k), k in main, -len(k), k))   # spaced (a lô) over a-lô
        for k in g:
            how = 'iy' if iy_key(k) == iy_key(canon) else 'ortho'
            rows.append((k, canon, how))
    con.executemany('INSERT INTO spelling VALUES (?,?,?)', rows)
    con.executemany('UPDATE entry SET key=?, tkey=?, toneless=? WHERE key=?',
                    [(c, vi.tkey(c), vi.toneless(c), k) for k, c, _ in rows if k != c])
    # an "alternative spelling of X" entry pooled with X has no English of its own: the group's entries give it
    con.execute("UPDATE entry SET english = '' WHERE alt_kind = 'spelling' AND key IN (SELECT canon FROM spelling) AND "
                "EXISTS (SELECT 1 FROM entry x WHERE x.key = entry.key AND x.alt_kind = '' AND x.english != '')")
    print(f'spelling groups: {len(groups)} groups ({len(rows)} keys) pooled under one key each; examples: '
          + ', '.join(f"{'/'.join(g)} -> {next(c for k, c, _ in rows if k == g[0])}" for g in groups[:6]))
    return len(groups)


def alt_forms(con):
    """An "alternative form of X" entry (cảm ơn of cám ơn, tui of tôi) or an alternative spelling whose X is not
    pooled with it: it keeps its own key, card and frequency, and takes X's characters and origin when it has none
    (note "as X"); its English is composed from X's senses (compose_english). A pronunciation / eye-dialect spelling
    (alt_kind 'pron': ga of ra) takes nothing: its sense stays a cross-reference."""
    n = 0
    for eid, target, pos in con.execute("SELECT id, alt_of, pos FROM entry WHERE alt_of != '' AND alt_of != key "
                                        "AND alt_kind != 'pron'").fetchall():
        tk = con.execute('SELECT canon FROM spelling WHERE key=?', (target,)).fetchone()
        tk = tk[0] if tk else target
        t = con.execute("SELECT chars, origin, etymon, origin_note, hv_check FROM entry WHERE key=? AND alt_kind = '' "
                        "AND pos NOT IN ('name', 'character-reading') ORDER BY pos != ?, id LIMIT 1", (tk, pos)).fetchone()
        if not t:
            continue
        cur = con.execute('SELECT chars, origin FROM entry WHERE id=?', (eid,)).fetchone()
        if not cur[1] and t[1]:
            con.execute("UPDATE entry SET chars=?, origin=?, etymon=?, origin_note=? WHERE id=?",
                        (t[0], t[1], t[2], f'as {tk} (alternative form)' + (f'; {t[3]}' if t[3] else ''), eid))
            n += 1
    print(f'alternative forms: {n} took the characters and origin of the word they are a form of')


def origins_after_load(con):
    """A compound with no etymology of its own whose syllables all have an origin (from their main entry): origin
    `compound`, note "nói (native) + chuyện (older Chinese loan)". Returns the number of entries given one."""
    main = {}
    for k, origin, sid in con.execute("SELECT key, origin, src_id FROM entry WHERE pos NOT IN ('name', "
                                      "'character-reading') AND source != 'fixture' ORDER BY id"):
        n = int(sid) if str(sid).isdigit() else 10 ** 6
        if k not in main or n < main[k][1]:
            main[k] = (origin, n)            # the first etymology of the syllable, as its card shows it
    rows = []
    for eid, k in con.execute("SELECT id, key FROM entry WHERE origin = '' AND chars = '' AND pos != 'name' AND "
                              "key LIKE '% %' AND source != 'fixture'").fetchall():
        syl = k.replace('-', ' ').split()
        os_ = [main.get(x, ('', 0))[0] for x in syl]
        if all(os_):
            if all(o == 'vietic' for o in os_):
                rows.append(('vietic', 'compound of native words: ' + ' + '.join(syl), eid))
            else:
                rows.append(('compound', 'formed in Vietnamese from ' + ' + '.join(syl) + ' (see each syllable)', eid))
    con.executemany("UPDATE entry SET origin=?, origin_note=? WHERE id=?", rows)
    print(f'compounds whose syllables all have an origin: {len(rows)} '
          f'({sum(1 for r in rows if r[0] == "vietic")} of native words only)')


def compose_english(con):
    """entry.english of every Wiktionary entry by tools/english.py compose() (Wiktionary's sense order; misspellings,
    form-of senses beside real ones and long later senses left out; late senses last), and entry.en_score: how many
    English Wiktionary translation tables give this word with an English word the entry's senses contain (evidence
    for choosing between etymologies only, never a lead: review 2, finding 2). An entry that is only "alternative
    form / spelling of X" is composed from X's senses; a pronunciation / eye-dialect spelling (alt_kind 'pron') keeps
    its cross-reference ("pronunciation spelling of ra")."""
    canon = dict(con.execute('SELECT key, canon FROM spelling'))
    heads = defaultdict(Counter)
    for en, k, tags in con.execute('SELECT en, key, tags FROM translation'):
        if not english.late(filter(None, (tags or '').split(','))):
            heads[canon.get(k, k)][en] += 1
    senses = defaultdict(list)
    for eid, g, tags, x, a in con.execute('SELECT entry_id, gloss, tags, examples, alt_of FROM sense ORDER BY entry_id, n'):
        senses[eid].append((g, set(filter(None, tags.split(','))), x, bool(a)))
    entries = defaultdict(list)
    for r in con.execute("SELECT id, key, pos, alt_of, english, src_id, alt_kind FROM entry WHERE source='wiktionary' "
                         "AND pos != 'character-reading'"):
        entries[r[1]].append(r)
    rows, changed = [], 0
    for k, es in entries.items():
        for eid, _, pos, alt_of, english_now, _, alt_kind in es:
            if alt_of and not english_now and canon.get(alt_of, alt_of) == k:
                rows.append(('', 0, eid))          # pooled spelling: its group has the English
                continue
            ss = senses.get(eid, [])
            if alt_of and alt_kind != 'pron' and ss and all(s[3] for s in ss if s[0]):
                t = canon.get(alt_of, alt_of)
                if t != k:
                    ss = [s for c in entries.get(t, []) if not c[3] and c[2] == pos for s in senses.get(c[0], [])] or \
                         [s for c in entries.get(t, [])[:2] if not c[3] for s in senses.get(c[0], [])] or ss
            text, _flags = english.compose(ss)
            if text != english_now:
                changed += 1
            rows.append((text or english_now, english.support(text or english_now, heads.get(k, {})), eid))
    con.executemany('UPDATE entry SET english=?, en_score=? WHERE id=?', rows)
    print(f'card English composed for {len(rows)} entries ({changed} differ from the loader\'s first four glosses)')


def character_readings(con):
    """English of the `character-reading` entries (tam~三): the gloss Wiktionary gives the reading, else CC-CEDICT's
    first sense of the character, + "(Hán-Việt reading of 三)"."""
    rows = []
    for eid, ch, en in con.execute("SELECT id, chars, english FROM entry WHERE pos='character-reading'").fetchall():
        if not en:
            c = con.execute('SELECT english FROM cedict_en WHERE chars=? LIMIT 1', (ch,)).fetchone()
            en = c[0].split('; ')[0] if c else ''
        rows.append(((f'{en} ' if en else '') + f'(Hán-Việt reading of {ch})', eid))
    con.executemany('UPDATE entry SET english=? WHERE id=?', rows)


def freq_key(k):
    """The key a word is ranked under: hyphens are syllable breaks (Wiktionary keeps old hyphenated spellings such as
    thế-giới, công-nhân, việt-nam as entries; wordfreq read each as one phrase with no competitor, which put 20 of them
    in the top 300 on the first real build). None for a key that is not made of letters only (3, "m*", "cung,") or is
    a one- or two-letter non-syllable (m, c, l: ranked 367, 386, 403 by the counts of letters): such a key is not
    ranked."""
    f = ' '.join(k.replace('-', ' ').split())
    if not f or not all(re.fullmatch(r'[^\W\d_]+', x) for x in f.split()):
        return None
    if len(f) <= 2 and vi.syllable_problems(f):
        return None        # a letter or texting abbreviation (m, c, l, ko): its count is that of the letter in text
    return f


def hv_usage(con):
    """hanviet.use: how many Wiktionary Sino-Vietnamese words whose syllables match their characters (hv_check ok) read
    each character with each reading. It orders a character's readings (tools/bridge.py hv_readings): Wiktionary lists
    them alphabetically (員 vân/viên, 義 ngãi/nghì/nghĩa), Thiều Chửu by its own order."""
    use = Counter()
    for k, chars in con.execute("SELECT DISTINCT key, chars FROM entry WHERE hv_check='ok' AND pos != 'character-reading'"):
        for s, c in zip(check_syllables(k), chars):
            use[(c, rkey(s))] += 1
    rows = [(use[(c, rkey(r))], rid) for rid, c, r in con.execute("SELECT rowid, char, reading FROM hanviet WHERE kind='hv'")
            if use[(c, rkey(r))]]
    con.executemany('UPDATE hanviet SET use=? WHERE rowid=?', rows)


def frequencies(con, raw, corpus):
    """entry.freq and freq_rank (tools/freq.py). A key is ranked under freq_key(); a hyphenated spelling whose spaced
    form is also a key (thế-giới / thế giới) gets the same freq but no rank of its own, so a word is counted once."""
    keys = [k for (k,) in con.execute("SELECT DISTINCT e.key FROM entry e JOIN source s ON s.id = e.source "
                                      "WHERE (s.fixture = 0 OR NOT EXISTS (SELECT 1 FROM entry x JOIN source y ON "
                                      "y.id = x.source WHERE y.fixture = 0)) AND e.pos != 'character-reading'")]
    fk = {k: freq_key(k) for k in keys}
    fkeys = sorted({f for f in fk.values() if f})
    syls = {s for k in fkeys for s in k.split()}
    F, fdesc = freq.syllable_freqs(raw, syls)
    if not F:
        print('frequency: no syllable frequency source (wordfreq not installed, FrequencyWords not fetched)')
        return ''
    canon = dict(con.execute('SELECT key, canon FROM spelling'))
    pos = defaultdict(set)
    lower_common = set()
    for k, p, w in con.execute("SELECT key, pos, word FROM entry WHERE pos != 'character-reading'"):
        pos[k].add(p)
        if p != 'name' and w[:1].islower():
            lower_common.add(k)
    # a name sharing its key with a lower-case common word (Lan / lan "orchid"); not Trung Quốc, whose other entries
    # (the adjective "Chinese") are written with capitals too (review 2, finding 7: Trung Quốc was ranked 3254)
    name_keys = {k for k, ps in pos.items() if 'name' in ps and k in lower_common}
    # not ranked: a common word + a name (tiếng Pháp, người Việt: free in the corpus, which is full of "speaks
    # French") and keys of 4+ syllables (bài tập về nhà): phrases, whose rank would mislead (finding 7)
    phrase = set()
    for k, w in con.execute("SELECT DISTINCT key, word FROM entry WHERE pos != 'name'"):
        ws = w.replace('-', ' ').split()
        if (len(ws) > 1 and ws[0][:1].islower() and any(x[:1].isupper() for x in ws[1:])) or len(ws) >= 4:
            phrase.add(k)
    for k in phrase:
        if k in fk and not ('name' in pos[k] and len(k.split()) < 4):
            fk[k] = None
    fkeys = sorted({f for f in fk.values() if f})
    cut, cdesc = freq.segmenter(set(keys) | set(canon), canon, name_keys)
    tokens = [fk.get(t) or t for s in corpus for t in cut(s)]
    est = freq.estimate(fkeys, F, tokens)
    ranked = sorted(est, key=lambda k: (-est[k], k))
    rank = {k: i + 1 for i, k in enumerate(ranked)}
    rows = []
    for k, f in fk.items():
        if f in est:
            variant = f != k and f in fk           # the spaced spelling is a key of its own: it carries the rank
            rows.append((round(est[f] * 1e9), None if variant else rank[f], k))
    con.executemany('UPDATE entry SET freq=?, freq_rank=? WHERE key=?', rows)
    # a name sharing its key with a common word (Lan / lan "orchid") does not carry the common word's rank
    con.executemany("UPDATE entry SET freq_rank=NULL WHERE key=? AND pos='name'", [(k,) for k in sorted(name_keys)])
    con.execute("UPDATE entry SET freq=NULL, freq_rank=NULL WHERE pos='character-reading'")
    desc = (f'{fdesc}, divided among the dictionary words by their shares in a corpus of {len(corpus)} sentences '
            f'({len(tokens)} words) cut by {cdesc} (tools/freq.py); hyphenated spellings ranked as spaced ones; '
            f'spelling groups ranked once, under their house spelling; a name sharing a key with a common word unranked')
    print(f'frequency: {len(ranked)} words ranked ({sum(1 for k in keys if not fk[k])} keys not made of letters, '
          f'not ranked): {desc}')
    return desc


EX_MIN, EX_BEST, EX_MAX = 4, 8, 20     # syllables of a card example: 4-20, the closest to 8 first
EX_PER_KEY = 40                        # candidates kept per word; tools/cards.py chooses the one that fits the sense
# a sentence a course card never shows (review 2, finding 6): profanity, sex, drugs (English side, the linked
# translation; Vietnamese side for what a translation may soften)
EX_UNSUITABLE_EN = re.compile(r"\b(?:fuck\w*|shit\w*|bitch\w*|damn\w*|bastard\w*|asshole|arse|sex\w*|stoned|high on|"
                              r"drugs?|cocaine|heroin|marijuana|weed|joint|porn\w*|rape\w*|naked|nude|penis|vagina|"
                              r"genital\w*|private parts|masturbat\w*|condom\w*|prostitut\w*|whore\w*|horny|erotic|"
                              r"suicide|kill (?:my|him|her|your)self)\b", re.I)
EX_UNSUITABLE_VI = re.compile(r'\b(?:đụ|địt|đéo|lồn|buồi|cặc|đĩ|phê thuốc|ma túy|ma tuý|cần sa|vùng kín|tình dục|'
                              r'làm tình|khiêu dâm|hiếp|mẹ kiếp|chết tiệt|khốn nạn)\b', re.I)


def cut_corpus(sentences, known):
    """[(vi, en, ref, words)] of the Tatoeba sentences: words = the canonical keys vi.cut() finds (whole words only:
    hơi is not a word of "xe hơi", chiều is one of "buổi chiều" only when the cutter leaves it alone)."""
    out = []
    for v, en, ref in sentences:
        ws = [w for w in vi.words(vi.cut(v, known)) if w[0] == 'w']
        out.append((v, en, ref, ws))
    return out


def example_flags(v, en, ws, known):
    """Why a sentence is not shown on a card ('' when it can be): unsuitable (profanity, sex, drugs), slash
    (alternatives "Cô ấy/Bà ấy"), unknown-word (a word no dictionary has: a typo such as "đên"; a capitalised word is
    a name and passes)."""
    if EX_UNSUITABLE_EN.search(en) or EX_UNSUITABLE_VI.search(v.lower()):
        return 'unsuitable'
    if '/' in v:
        return 'slash'
    if any(w[2] not in known and not w[1][:1].isupper() for w in ws):
        return 'unknown-word'
    return ''


def attach_examples(con, cut, known, per_word=EX_PER_KEY):
    """Tatoeba sentences on the words they contain as whole words (cut_corpus), up to `per_word` candidates per key
    (table example, column key): sentences of EX_MIN-EX_MAX syllables, the closest to EX_BEST first, then by length
    and id, so the choice never depends on the run. tools/cards.py picks among them the first one whose translation
    matches the card's sense (review 2, finding 6). flags: example_flags()."""
    first = {}
    for k, eid in con.execute('SELECT key, min(id) FROM entry GROUP BY key'):
        first[k] = eid
    canon = dict(con.execute('SELECT key, canon FROM spelling'))
    have = Counter()
    rows = []
    usable = [x for x in cut if EX_MIN <= len(x[0].split()) <= EX_MAX]
    flagged = Counter()
    for v, en, ref, ws in sorted(usable, key=lambda x: (abs(len(x[0].split()) - EX_BEST), len(x[0]), x[2])):
        fl = example_flags(v, en, ws, known)
        flagged[fl] += 1
        for w in sorted({canon.get(w[2], w[2]) for w in ws}):
            if w in first and have[w] < per_word:
                have[w] += 1
                rows.append((first[w], 'tatoeba', v, en, ref, w, fl))
    con.executemany('INSERT INTO example(entry_id, source, vi, en, ref, key, flags) VALUES (?,?,?,?,?,?,?)', rows)
    print(f'tatoeba: {len(rows)} example candidates on {len(have)} words (from {len(usable)} sentences of '
          f'{EX_MIN}-{EX_MAX} syllables; flagged: {dict((k, n) for k, n in flagged.items() if k)})')


USE_STOP = {'to', 'a', 'an', 'the', 'of', 'one', 'someone', 'something', 'sb', 'sth', 'etc', 'used', 'it', 'its',
            'oneself', 'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'such', 'as', 'or',
            'and', 'in', 'on', 'at', 'by', 'for', 'out', 'up', 'that', 'this', 'which', 'who', 'what'}
BE = {'is', 'are', 'was', 'were', 'am', 'been', 'being', 's', 'm', 're'}


def gloss_words(text):
    """The words of an English gloss, lower case, light stemming (plural / -ing / -ed), without USE_STOP; forms of
    "be" count as be (là "to be")."""
    out = set()
    for w in re.findall(r"[a-z]+", (text or '').lower()):
        if w in BE:
            w = 'be'
        if w in USE_STOP:
            continue
        for suf in ('ing', 'ed', 'es', 's'):
            if len(w) > len(suf) + 3 and w.endswith(suf):
                w = w[:-len(suf)]
                break
        out.add(w)
    return out


def etymology_usage(con, cut, min_n=3, ratio=2.0):
    """Which etymology of a spelling is in use (review 2, finding 3), from the corpus: each Tatoeba sentence that has
    the word (cut_corpus) counts for an etymology when its English translation contains a word of that etymology's
    senses that no other etymology of the spelling has (từ: "from"/"since" for 自, "word" for 詞). entry.use_n: the
    count of the entry's etymology; entry.use_main: 1 for every entry of the etymology with at least `min_n`
    sentences and `ratio` times the next one, 0 for the others of that key; NULL where the evidence is weak (the card
    then keeps Wiktionary's page order and says that it claims no main sense). Returns (strong, weak) key counts."""
    groups = defaultdict(lambda: defaultdict(list))
    for eid, k, src, sid, chars, origin, pos in con.execute(
            "SELECT id, key, source, src_id, chars, origin, pos FROM entry WHERE source = 'wiktionary' AND pos NOT IN "
            "('name', 'character-reading', 'combining_form') AND alt_kind != 'pron' ORDER BY id"):
        groups[k][(src, sid, chars, origin)].append(eid)
    multi = {k: g for k, g in groups.items() if len(g) > 1}
    if not multi:
        return 0, 0
    words, unmeasurable = {}, set()
    for k, g in multi.items():
        for gk, ids in g.items():
            ws = set()
            for g_, tags in con.execute(f"SELECT gloss, tags FROM sense WHERE entry_id IN ({','.join('?' * len(ids))}) "
                                        "ORDER BY entry_id, n", ids):
                g_ = english.clean(g_)
                if not g_ or 'alt-of' in tags or 'form-of' in tags or 'morpheme' in tags or english.late(
                        filter(None, tags.split(','))) or english.FORM_OF.match(g_) or english.SHORT_FOR.match(g_):
                    continue
                if english.DESCRIPTION.match(g_) or re.search(r'\b(?:marker|particle|classifier)\b', g_, re.I):
                    unmeasurable.add((k, gk))      # a usage description is never in a translation
                    continue
                gw = gloss_words(g_)
                ws |= gw if len(g_) <= english.MAX_FIRST else set(sorted(gw, key=g_.lower().find)[:3])
            words[(k, gk)] = ws
    canon = dict(con.execute('SELECT key, canon FROM spelling'))
    count = defaultdict(Counter)
    for v, en, ref, ws in cut:
        tw = gloss_words(en)
        for k in {canon.get(w[2], w[2]) for w in ws} & multi.keys():
            gs = list(multi[k])
            for gk in gs:
                own = words[(k, gk)] - set().union(*(words[(k, o)] for o in gs if o != gk))
                if own & tw:
                    count[k][gk] += 1
    rows, strong, weak = [], 0, 0
    for k, g in multi.items():
        first = min(g, key=lambda gk: (int(gk[1]) if str(gk[1]).isdigit() else 10 ** 6, g[gk][0]))
        ranked = sorted(g, key=lambda gk: (-count[k][gk], gk != first))
        top, nxt = count[k][ranked[0]], count[k][ranked[1]]
        is_strong = top >= min_n and top >= ratio * max(nxt, 1) if nxt else top >= min_n
        if ranked[0] != first and (k, first) in unmeasurable:
            is_strong = False         # các "Plural marker" cannot be counted: page order, no main claimed
        strong += is_strong
        weak += not is_strong
        for gk in g:
            main = (1 if gk == ranked[0] else 0) if is_strong else None
            rows += [(count[k][gk], main, eid) for eid in g[gk]]
    con.executemany('UPDATE entry SET use_n=?, use_main=? WHERE id=?', rows)
    print(f'etymology in use (Tatoeba translations): {len(multi)} spellings with several etymologies; a main one '
          f'attested for {strong}, weak evidence (page order, no main claimed) for {weak}')
    return strong, weak


FW_MIN = 200     # FrequencyWords syllables seen at least this often (3,588 syllables in vi_50k) validate the table


def validate_syllables(con, raw):
    """tools/vi.py's syllable table against real syllables: every Thiều Chửu reading and the FrequencyWords syllables
    seen at least FW_MIN times. Prints what it rejects; a rejected Thiều Chửu reading is listed one by one, as is any
    rejected subtitle syllable with a Vietnamese letter or tone mark (plain-ASCII ones are counted: foreign words,
    names, abbreviations). Investigated on 18 Nov 2026: docs/HISTORY.md."""
    tc = Counter(r for (r,) in con.execute("SELECT reading FROM hanviet WHERE source='thieuchuu'"))
    fw = Counter()
    p = os.path.join(raw, 'frequencywords', 'vi_50k.txt')
    if os.path.exists(p):
        for line in open(p, encoding='utf-8'):
            x = line.split()
            if len(x) == 2 and x[1].isdigit():
                fw[vi.nfc(x[0]).lower()] += int(x[1])
    fw = Counter({w: c for w, c in fw.items() if c >= FW_MIN})
    for name, sylls in (('Thiều Chửu readings', tc), (f'FrequencyWords syllables (count >= {FW_MIN})', fw)):
        if not sylls:
            continue
        acc, viet, n_ascii, ex = vi.validate_syllables(sylls)
        print(f'syllable table vs {len(sylls)} {name}: {acc} accepted; rejected: {len(viet)} with Vietnamese letters'
              + (f', {n_ascii} plain ASCII or with digits/punctuation (e.g. {", ".join(ex[:8])})' if n_ascii else ''))
        for w, c, why in viet:
            print(f'  rejected {w} ({c}): {why}')


# ---------------------------------------------------------------------------------------------- etymology states
FUNCTION_POS = {'particle', 'conj', 'prep', 'adv', 'pron', 'det', 'postp', 'intj', 'classifier'}
STOP = {'to', 'a', 'an', 'the', 'of', 'be', 'is', 'one', 'sth', 'sb', 'something', 'someone', 'etc', 'used', 'in',
        'with', 'for', 'by', 'as', 'on', 'oneself', 'its', 'it', 'that', 'this', 'which', 'who', 'and', 'or', 'not',
        'no', 'from', 'into', 'at', 'up', 'out', 'very', 'thing', 'person', 'make', 'have', 'has', 'variant', 'old',
        'literary', 'classical', 'surname', 'name', 'see', 'also', 'kind', 'type', 'form', 'abbr', 'used', 'cl',
        'pr', 'esp', 'usually', 'often', 'certain', 'other', 'another'}
# function words compared as such when the sense has no content word (như 如 "like, as", bị 被 "by", tự 自 "self")
FUNC_KEEP = {'like', 'as', 'by', 'from', 'self', 'oneself', 'since', 'at', 'in', 'on', 'if', 'or', 'and', 'but', 'with',
             'for', 'not', 'no', 'all', 'each', 'every', 'then', 'only', 'still', 'also', 'again', 'more', 'most'}
RARE_CHAR = 3        # a character used in fewer CC-CEDICT words than this (variants counted) is rare for a reader
# words that name the same sense in the two dictionaries' different wording (loose comparison)
SENSE_SYN = [{'become', 'turn', 'into', 'achieve', 'accomplish', 'succeed'}, {'create', 'make', 'build', 'produce'},
             {'far', 'distant', 'remote'}, {'old', 'elder', 'grandfather', 'venerable'}, {'friend', 'companion',
             'partner', 'mate'}, {'number', 'count', 'figure', 'amount'}, {'part', 'portion', 'share', 'section'},
             {'fruit', 'result'}, {'self', 'oneself', 'own', 'personally', 'from', 'since'}, {'like', 'as', 'if'},
             {'suffer', 'passive', 'by', 'subject'}, {'member', 'staff', 'employee', 'personnel'},
             {'feeling', 'emotion', 'love', 'affection', 'sentiment'}, {'mirror', 'lens', 'glass', 'glasses'},
             {'shop', 'store', 'street', 'lane'}, {'county', 'district', 'prefecture'},
             {'body', 'oneself', 'relative'}, {'occupy', 'seize', 'take'},
             {'diploma', 'certificate', 'proof', 'evidence'}, {'front', 'before', 'previous', 'former'},
             {'separate', 'apart', 'distance'}, {'orange', 'tangerine', 'mandarin'}]


def _tokens(text, stop=True):
    out = set()
    for w in re.findall(r'[a-z]+', (text or '').lower()):
        if stop and (w in STOP or len(w) < 3):
            continue
        for suf in ('ing', 'ied', 'ies', 'ed', 'es', 's', 'ly'):
            if len(w) > len(suf) + 3 and w.endswith(suf):
                w = w[:-len(suf)] + ('y' if suf in ('ied', 'ies') else '')
                break
        out.add(w)
    return out


def _loose(tokens):
    out = set(tokens)
    for syn in SENSE_SYN:
        if out & syn:
            out |= syn
    return out


def etymology_states(con):
    """For each etymology of a word (its entries of one source, etymology number, characters and origin) that is a
    Sino-Vietnamese analysis (origin sino, characters matching the syllables) or an older Chinese loan:
    entry.sino_kind (word: the characters are a word of CC-CEDICT, rime-cantonese, the MOE or a Chinese row of the
    English Wiktionary's translation tables, under their own or a Unihan variant spelling (tools/lexicon.py
    attested), or one character; vn: none of them has it, a compound formed in Vietnamese: 場學 trường học) and
    entry.doubt (rewritten after review 2, finding 4, so that it does not hide good bridges):
      doubtful  Wiktionary's own etymology doubts the source (etym.doubt_words: the first sentence, or "Alternatively,
                from …"), and the sense test below does not confirm it;
      opaque    the analysis holds but a reader of Chinese would not see the word: a character rare in CC-CEDICT
                (fewer than RARE_CHAR words, its variant forms counted: 爲, 墻, 舖 are not rare); or ONE character
                whose senses, ALL of them, share no word (light stemming, SENSE_SYN synonyms) with ANY of CC-CEDICT's
                senses of the character or of its variants, and no English Wiktionary translation table of the word
                gives a Chinese word with the character. A function word compares its function words too (如 "like,
                as", 被 "by", 自 "from, self"): when that is what matches, label `gram` (the same morpheme in a
                grammatical use) instead of `same`.
    Then the label: same | gram | hv-vn | doubtful | opaque | older-loan | loan | native | compound | '' (unknown).
    The course lexicon (course/lexicon.tsv) decides the label of the words it has. Returns a Counter of labels."""
    import lexicon
    ced = defaultdict(list)
    for ch, en in con.execute('SELECT chars, english FROM cedict_en'):
        ced[ch].append(en)
    use = Counter()
    for ch, n in con.execute('SELECT char, sum(n) FROM cmn_use GROUP BY char'):
        use[ch] = n
    zh_by_table = defaultdict(set)
    for en, pos, sense, w in con.execute('SELECT en, pos, sense, word FROM translation_zh'):
        zh_by_table[(en, pos, sense)].add(w)
    tables = defaultdict(list)                        # vietnamese key -> [table]
    canon = dict(con.execute('SELECT key, canon FROM spelling'))
    for en, pos, sense, k in con.execute('SELECT en, pos, sense, key FROM translation'):
        tables[canon.get(k, k)].append((en, pos, sense))
    senses_of = defaultdict(list)
    for eid, g in con.execute('SELECT entry_id, gloss FROM sense'):
        senses_of[eid].append(g)

    def forms(c):
        return [c] + bridge.variants(con, c)

    def zh_support(k, c):
        return any(f in w for t in tables.get(k, []) for w in zh_by_table.get(t, ()) for f in forms(c))
    groups = defaultdict(list)
    for r in con.execute("SELECT id, key, pos, english, chars, origin, hv_check, etymon, doubt_why, en_score, source, "
                         "src_id FROM entry WHERE origin IN ('sino', 'nonhv') AND source != 'fixture' AND pos != "
                         "'character-reading'").fetchall():
        groups[(r[1], r[10], r[11], r[4], r[5])].append(r)
    rows, gram = [], []
    for (k, _src, _sid, chars, origin), rs in groups.items():
        etymon = next((r[7] for r in rs if r[7]), '')
        c = chars if origin == 'sino' else (re.match(etym.CJK + '+', etymon) or [''])[0]
        if not c:
            continue
        kind = ''
        if origin == 'sino' and chars and all(r[6] not in ('differs', 'length') for r in rs):
            kind = 'word' if len(chars) == 1 or lexicon.attested(con, chars) else 'vn'
        why = next((r[8] for r in rs if r[8]), '')
        words = [r for r in rs if r[2] != 'name']
        doubt, reason, is_gram = '', '', False
        if words and ced:
            cedict = ' ; '.join(x for ch in ([c] if len(c) > 1 else []) + list(c) for f in forms(ch)
                                for x in ced.get(f, []))
            mine_all = ' ; '.join([r[3] or '' for r in words] + [g for r in words for g in senses_of.get(r[0], [])])
            content = _loose(_tokens(mine_all)) & _loose(_tokens(cedict))
            func = ({w for w in _tokens(mine_all, stop=False) if w in FUNC_KEEP} &
                    {w for w in _tokens(cedict, stop=False) if w in FUNC_KEEP})
            main = max(words, key=lambda r: (r[9] if r[9] is not None else -9, -r[0]))
            rare = [ch for ch in c if use and max(use[f] for f in forms(ch)) < RARE_CHAR]
            supported = bool(content) or zh_support(k, c)
            if rare:
                doubt, reason = 'opaque', f'rare character for a reader of Chinese: {"".join(rare)}'
            elif len(c) == 1 and not supported:
                if main[2] in FUNCTION_POS and func:
                    is_gram = True
                else:
                    doubt = 'opaque'
                    reason = (f'no sense of the word ("{english.first_sense(main[3])[:40]}"…) is among CC-CEDICT\'s '
                              f'senses of {c} ({cedict[:50]}), nor in a translation table with {c}')
            elif len(c) == 1 and main[2] in FUNCTION_POS and not content and func:
                is_gram = True
            if why and not doubt and not (len(c) == 1 and supported):
                doubt, reason = 'doubtful', f"Wiktionary's etymology says: {why}"
        elif why:
            doubt, reason = 'doubtful', f"Wiktionary's etymology says: {why}"
        rows += [(kind, doubt, reason, x[0]) for x in rs]
        if is_gram and not doubt:
            gram += [(x[0],) for x in rs]
    con.executemany('UPDATE entry SET sino_kind=?, doubt=?, doubt_why=? WHERE id=?', rows)
    con.execute("UPDATE entry SET label = CASE "
                "WHEN source = 'fixture' THEN label "
                "WHEN origin = 'sino' AND chars != '' AND hv_check NOT IN ('differs', 'length') THEN "
                "  CASE WHEN doubt != '' THEN doubt WHEN sino_kind = 'vn' THEN 'hv-vn' ELSE 'same' END "
                "WHEN origin = 'nonhv' THEN 'older-loan' WHEN origin = 'loan' THEN 'loan' "
                "WHEN origin = 'vietic' THEN 'native' WHEN origin = 'compound' THEN 'compound' ELSE '' END")
    con.executemany("UPDATE entry SET label='gram' WHERE id=? AND label='same'", gram)
    c = Counter(r for (r,) in con.execute("SELECT label FROM entry WHERE source != 'fixture'"))
    d = Counter(r for (r,) in con.execute("SELECT doubt FROM entry WHERE doubt != ''"))
    print(f'etymology labels (entries): {dict(c)}; doubtful/opaque analyses: {dict(d)}')
    return c


def taigi_layers(con):
    """The MOE marks no literary reading for most characters (文白屬性 0: no split); for some the one reading it gives
    is in fact colloquial (冊 tsheh, 院 īnn, 醬 tsiùnn). A literary reading keeps the Middle Chinese coda, as Hán-Việt
    does, so an unmarked reading whose coda class differs from every Hán-Việt reading of the character is colloquial:
    -h (glottal stop) for a stop (冊 tsheh / sách), a nasal vowel -nn for -n/-ng (院 īnn / viện, 醬 tsiùnn / tương),
    a bare vowel for a nasal or stop. Classes: p, t, k (Hán-Việt -c/-ch), m, n, ng (Hán-Việt -nh), h, nn, vowel;
    m/n, p/t and k/t agree (regular literary correspondences: 凡 phàm / huân, 法 pháp / huat, 直 trực / ti̍t), and so
    do a nasal vowel with an open rhyme (他 thann / tha) and -in with -ng (孕 īn / dựng): bridge.coda_agrees.
    Blind spots (REFERENCE): a colloquial reading with the coda class of the literary one (條 tiâu beside liâu) is
    not found; a colloquial nasalised open syllable (鼻 phīnn, 怕 phànn) is no longer found either; a character whose
    Hán-Việt reading is irregular (呆 ngốc, 炸 tạc) is judged against it.
    Such readings get note 'colloquial' (chinese table): the bridge never shows them as literary; a character left
    with none is "colloquial only" on the card. Readings the MOE marks literary (1) are not touched. Returns the
    characters changed."""
    rows, changed = [], set()
    by_char = defaultdict(list)
    for rid, ch, r in con.execute("SELECT rowid, chars, reading FROM chinese WHERE lang='nan' AND level='char' AND "
                                  "note='unmarked'"):
        by_char[ch].append((rid, r))
    for ch, rs in by_char.items():
        hv = bridge.hv_readings(con, ch)
        if not hv:
            continue
        hcls = {bridge.coda_hv(x) for x in hv}
        bad = [(rid, r) for rid, r in rs if not any(bridge.coda_agrees(h, bridge.coda_nan(r), r) for h in hcls)]
        if bad:
            changed.add(ch)
            rows += [(rid,) for rid, _ in bad]
    con.executemany("UPDATE chinese SET note='colloquial' WHERE rowid=?", rows)
    only = sorted(ch for ch in changed if len(by_char[ch]) == sum(1 for rid, _ in by_char[ch] if (rid,) in set(rows)))
    print(f'Taigi: {len(changed)} characters have an unmarked MOE reading whose coda does not match Hán-Việt (now '
          f'"colloquial"); {len(only)} of them have no other reading (colloquial only): {"".join(only[:60])}')
    return changed


def build_bridge(con):
    rows = []
    spell = {c for (c,) in con.execute("SELECT DISTINCT chars FROM entry WHERE chars != '' AND hv_check NOT IN "
                                       "('differs', 'length')")}
    for (e,) in con.execute("SELECT DISTINCT etymon FROM entry WHERE origin = 'nonhv' AND etymon != ''"):
        m = re.match(etym.CJK + '+', e)
        if m:
            spell.add(m.group(0))          # an older loan's etymon: its readings on the card (giấy 紙)
    for chars in sorted(spell):
        j = bridge.join(con, chars)
        rows.append((chars, j['hv'], j['yue'], j['yue_by'], j['nan'], j['nan_by'], j['cmn'], j['cmn_by'], j['n'],
                     j['nan_coll'], j.get('via', ''), j['nan_flag']))
    con.executemany('INSERT INTO bridge VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', rows)
    c = Counter(r[8] for r in rows)
    print(f'bridge: {len(rows)} distinct chữ Hán spellings; with 3 Chinese readings {c[3]}, 2 {c[2]}, 1 {c[1]}, 0 {c[0]}; '
          f'{sum(1 for r in rows if r[-1])} found partly under a variant spelling (Unihan)')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2:
        sys.exit(__doc__)
    raw, out = args
    nc = '--nc' in sys.argv
    # one database rule, enforced here and in tools/cards.py open_db(): the non-commercial build has its own file
    if nc != out.endswith('-nc.db'):
        sys.exit(f'build_db: refusing to write a {"non-commercial" if nc else "public"} build to {out} '
                 f'(public builds go to *.db, non-commercial ones to *-nc.db)')
    tmp = out + '.tmp'
    if os.path.exists(tmp):
        os.remove(tmp)
    con = sqlite3.connect(tmp)
    con.executescript(open(os.path.join(HERE, 'schema.sql'), encoding='utf-8').read())
    used, missing, sentences, corpus = [], [], [], []
    for s in SOURCES:
        if not s['commercial_ok'] and not nc:
            continue
        add = Adder(con, s['id'])
        try:
            s['load'](raw, add)
        except Missing as e:
            con.rollback()
            if s['id'] not in allowed_missing():
                con.close()
                os.remove(tmp)
                sys.exit(f"build_db: FAILED: source {s['id']} not fetched: {e} is missing (run `make data`; in a sandbox "
                         f"that cannot reach the host, TUSACH_ALLOW_MISSING={s['id']} builds without it, unpublishable)")
            missing.append(s['id'])
            print(f"source {s['id']} not fetched: {e} is missing, allowed by TUSACH_ALLOW_MISSING "
                  "(this database cannot make a publishable page)")
            continue
        con.execute('INSERT INTO source VALUES (?,?,?,?,?,?,0)',
                    (s['id'], s['name'], s['version'], s['licence'], s['url'], int(s['commercial_ok'])))
        con.commit()
        sentences += add.sentences
        corpus += add.corpus
        used.append(s['id'])
        print(f"{s['id']}: {add.n} rows")
    con.execute("INSERT INTO source VALUES ('fixture', 'TEST FIXTURE (invented entries, not course content)', '', "
                "'CC0 (written for this repository)', '', 1, 1)")
    add = Adder(con, 'fixture')
    load_fixture(add)
    print(f'fixture: {add.n} rows (test fixture, tools/fixtures/dict.yaml)')
    hv_crosscheck(con)
    validate_syllables(con, raw)
    rank_chinese(con)
    hannom_attested(con)          # before southern_variants: an attested Southern form (義 ngãi) is labelled too
    southern_variants(con)
    unihan_fallback(con)
    spelling_groups(con, raw)
    alt_forms(con)
    word_checks(con)
    origins_after_load(con)
    hv_usage(con)
    taigi_layers(con)
    known = {k for (k,) in con.execute('SELECT DISTINCT key FROM entry')} | \
        {k for (k,) in con.execute('SELECT key FROM spelling')}
    cut = cut_corpus(sentences, known) if sentences else []
    if sentences:
        attach_examples(con, cut, known)
    # the corpus for word counts: Tatoeba, Wiktionary's examples (+ the Tatoeba Challenge copy in the private build)
    corpus = [v for v, _, _ in sentences] + [v for (v,) in con.execute(
        "SELECT vi FROM example WHERE source = 'wiktionary'")] + corpus
    fdesc = frequencies(con, raw, corpus)
    compose_english(con)
    etymology_usage(con, cut)
    character_readings(con)
    build_bridge(con)
    etymology_states(con)
    con.executemany('INSERT INTO meta VALUES (?,?)', [('nc', '1' if nc else '0'),
                                                      ('built', datetime.date.today().isoformat()),
                                                      ('sources', ' '.join(used)), ('missing', ' '.join(missing)),
                                                      ('freq_method', fdesc)])
    con.commit()
    con.close()
    os.replace(tmp, out)
    print(f'{out}: {"non-commercial (private builds only)" if nc else "public"} build'
          + (f'; NOT FETCHED: {", ".join(missing)}' if missing else ''))


if __name__ == '__main__':
    main()
