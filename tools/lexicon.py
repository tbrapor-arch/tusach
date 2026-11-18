"""The curated course lexicon: course/lexicon.tsv, one row per SENSE the course teaches (layer 1 of the card design,
review 2). Written by Claude, NOT checked by a native speaker, like the lessons. On a card the lexicon wins for the
English, the sense (etymology) chosen, the origin label, the characters and the false-friend note; the READINGS
(Hán-Việt per character, Jyutping, Tâi-lô, pinyin) never come from it: tools/cards.py joins them from the database
on the lexicon's characters (tools/bridge.py).

    python3 -I tools/lexicon.py            # validate every row against the database; exit 1 on unresolved conflicts
    python3 -I tools/lexicon.py --all      # also list the conflicts resolved by an override

Columns (TSV, # starts a comment, header row first):
  key          house spelling, lower case except names, spaces between syllables; `~tag` for a homograph or a sense
               (từ~from, từ~word, năm~five, năm~year). The FIRST row of a key is its main sense (the untagged card).
  pos          noun verb adj adv pron num classifier particle conj prep intj phrase name
  en           English as taught: short, card-ready
  origin       hv (Hán-Việt, the same word in Chinese) | hv-gram (Hán-Việt, the same morpheme in a grammatical use:
               如 như, 被 bị) | hv-opaque (Hán-Việt by history, but a reader of Chinese does not see the sense) |
               hv-vn (Hán-Việt formed in Vietnam: no such Chinese word) | older-loan (an older Chinese loan, not
               read the Hán-Việt way: etymon column) | french | loan (another language: say which in `usage` or
               `source`) | native | compound (of Vietnamese words: the parts' origins on their own cards) | unknown
  chars        the chữ Hán of THIS sense (hv*), else empty
  etymon       older-loan: the Chinese characters it was borrowed from
  false_friend a note when the modern Vietnamese meaning differs from the Chinese word's (bác sĩ, thời tiết)
  usage        register, Northern/Southern, how it is used (shown on the card)
  confidence   sure | likely | doubt[: reason]   (doubt on a Chinese origin makes the card say "doubtful")
  source       the database entry or sense that supports the row ("wikt: …", "cedict: …"), or "Claude"
  override     `kind: reason` for each validation conflict the row keeps on purpose, separated by " | "

Validation (validate()): every row against the data, printing conflicts instead of trusting either side:
  no-key          the key is not in the database
  hv-mismatch     a character's Hán-Việt readings do not include the word's syllable
  origin-conflict the origin contradicts an explicit Wiktionary etymology of the word (every etymology that has one)
  chars-conflict  Wiktionary analyses the word with other characters (and none of its etymologies has these)
  en-unsupported  the English shares no content word with any dictionary sense or translation of the word
  not-attested    origin hv/hv-gram with several characters that no Chinese source has as a word
  bad-row         a malformed row (unknown origin / confidence / pos, chars on a non-Chinese origin…, an override
                  of a conflict the row does not have)
`make lint` fails on any conflict whose kind the row does not override.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import vi  # noqa: E402

PATH = os.path.join(ROOT, 'course/lexicon.tsv')
COLS = ('key', 'pos', 'en', 'origin', 'chars', 'etymon', 'false_friend', 'usage', 'confidence', 'source', 'override')
ORIGINS = ('hv', 'hv-gram', 'hv-opaque', 'hv-vn', 'older-loan', 'french', 'loan', 'native', 'compound', 'unknown')
POS = {'noun', 'verb', 'adj', 'adv', 'pron', 'num', 'classifier', 'particle', 'conj', 'prep', 'intj', 'phrase', 'name',
       'det'}
HV = ('hv', 'hv-gram', 'hv-opaque', 'hv-vn')
CONFLICTS = ('no-key', 'hv-mismatch', 'origin-conflict', 'chars-conflict', 'en-unsupported', 'not-attested', 'bad-row')
# the card label of an origin (tools/cards.py; app LABEL)
LABEL = {'hv': 'same', 'hv-gram': 'gram', 'hv-opaque': 'opaque', 'hv-vn': 'hv-vn', 'older-loan': 'older-loan',
         'french': 'loan', 'loan': 'loan', 'native': 'native', 'compound': 'compound', 'unknown': ''}
ORIGIN_TEXT = {'hv': 'Hán-Việt (the same word in Chinese)', 'hv-gram': 'Hán-Việt: the same morpheme, in a grammatical use',
               'hv-opaque': 'Hán-Việt by history; the Chinese sense is not visible', 'hv-vn': 'Hán-Việt formed in Vietnam',
               'older-loan': 'older Chinese loan', 'french': 'loan from French', 'loan': 'loan',
               'native': 'native Vietnamese', 'compound': 'compound of Vietnamese words',
               'unknown': 'no etymology recorded'}
# what a Wiktionary origin (entry.origin) allows
DB_ALLOWS = {'sino': set(HV), 'nonhv': {'older-loan'}, 'vietic': {'native', 'compound'},
             'loan': {'french', 'loan'}, 'compound': {'compound', 'native', 'hv-vn', 'hv'}}
EN_STOP = {'to', 'a', 'an', 'the', 'of', 'is', 'one', 'someone', 'something', 'sb', 'sth', 'etc', 'it', 'its', 'used',
           'for', 'and', 'or', 'in', 'on', 'at', 'by', 'as', 'with', 'up', 'out', 'off', 'into', 'from', 'word',
           'particle', 'marker', 'classifier', 'form', 'question', 'final', 'sentence', 'very'}
SYNONYMS = [{'mother', 'mom', 'mum', 'mama'}, {'father', 'dad', 'papa'}, {'glass', 'cup', 'tumbler'},
            {'big', 'large', 'great'}, {'small', 'little', 'tiny'}, {'fast', 'quick', 'quickly'},
            {'grandfather', 'grandpa'}, {'grandmother', 'grandma'}, {'film', 'movie'}, {'photo', 'photograph', 'picture'},
            {'tired', 'weary'}, {'ill', 'sick'}, {'begin', 'start'}, {'finish', 'complete', 'end'},
            {'look', 'see', 'watch'}, {'speak', 'say', 'talk', 'tell'}, {'road', 'street', 'way'},
            {'lake', 'pond'}, {'hot', 'warm'}, {'right', 'correct'}, {'reason', 'cause'}, {'ok', 'okay', 'alright'},
            {'programme', 'program'}, {'colour', 'color'}, {'say', 'said', 'tell'}]


def load(path=PATH):
    """[row dict] in file order (with 'n': the line number); 'cid': the card id (key, ~tag)."""
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as f:
        rd = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        header = None
        for n, row in enumerate(rd, 1):
            if not row or row[0].startswith('#'):
                continue
            if header is None:
                header = row
                continue
            d = {c: vi.nfc((row[i] if i < len(row) else '').strip()) for i, c in enumerate(COLS)}
            d['n'] = n
            raw = d['key']
            k, tag = (raw.split('~', 1) + [None])[:2]
            d['tag'] = tag or None
            d['k'] = k if d['pos'] == 'name' else vi.key(k)
            d['cid'] = ('name:' + k) if d['pos'] == 'name' else vi.card_id(vi.key(k), tag)
            d['conf'] = d['confidence'].split(':')[0].strip()
            out.append(d)
    return out


def index(rows):
    """({card id: row}, {key: [rows of the key, main first]})."""
    by_cid, by_key = {}, {}
    for r in rows:
        by_cid.setdefault(r['cid'], r)
        if r['pos'] != 'name':
            by_key.setdefault(r['k'], []).append(r)
    return by_cid, by_key


def overrides(row):
    """{conflict kind: reason} from the override column ("en-unsupported: a particle, no English in any source")."""
    out = {}
    for part in (row.get('override') or '').split(' | '):
        m = re.match(r'\s*([a-z-]+)\s*:\s*(.+)', part)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def words(text):
    out = set()
    for w in re.findall(r'[a-z]+', (text or '').lower()):
        if w in EN_STOP or len(w) < 2:
            continue
        for suf in ('ing', 'ies', 'ed', 'es', 's', 'ly'):
            if len(w) > len(suf) + 3 and w.endswith(suf):
                w = w[:-len(suf)] + ('y' if suf == 'ies' else '')
                break
        out.add(w)
    for syn in SYNONYMS:
        if out & syn:
            out |= syn
    return out


def rkey(s):
    return re.sub(r'^([bcdđghklmnprstvx]+)y(\d)$', r'\1i\2', vi.tkey(s))


def attested(con, chars):
    """The Chinese sources that have `chars` (or a Unihan variant spelling of it) as a word: cmn (CC-CEDICT), yue
    (rime-cantonese), nan (MOE), zh-tr (a Chinese row of an English Wiktionary translation table). One character is
    attested by any reading; a name attests a name (臨安 Lâm An). Used by the lexicon check and by tools/build_db.py etymology_states (hv-vn)."""
    import bridge
    out = []
    for sp in bridge.spellings(con, chars):
        for lang in ('cmn', 'yue', 'nan'):
            lvl = 'char' if len(sp) == 1 else 'word'
            if lang not in out and con.execute("SELECT 1 FROM chinese WHERE chars=? AND lang=? AND level=? LIMIT 1",
                                               (sp, lang, lvl)).fetchone():
                out.append(lang)
        if 'zh-tr' not in out and len(sp) > 1 and con.execute(
                'SELECT 1 FROM translation_zh WHERE word=? LIMIT 1', (sp,)).fetchone():
            out.append('zh-tr')
    return out


def validate(con, rows=None):
    """[(row, kind, message)] for every row (overridden ones included: the caller filters with overrides())."""
    import bridge
    rows = load() if rows is None else rows
    canon = dict(con.execute('SELECT key, canon FROM spelling'))
    out = []
    seen = {}
    for r in rows:
        def bad(kind, msg):
            out.append((r, kind, msg))
        if r['cid'] in seen:
            bad('bad-row', f'duplicate card id {r["cid"]} (line {seen[r["cid"]]})')
        seen[r['cid']] = r['n']
        if r['origin'] not in ORIGINS:
            bad('bad-row', f'unknown origin {r["origin"]!r}')
        if r['conf'] not in ('sure', 'likely', 'doubt'):
            bad('bad-row', f'unknown confidence {r["confidence"]!r}')
        if r['pos'] not in POS:
            bad('bad-row', f'unknown part of speech {r["pos"]!r}')
        if not r['en']:
            bad('bad-row', 'no English')
        if r['chars'] and r['origin'] not in HV:
            bad('bad-row', f'characters on origin {r["origin"]}: use the etymon column for an older loan')
        if r['origin'] in HV and not r['chars']:
            bad('bad-row', 'a Hán-Việt origin needs its characters')
        if r['origin'] == 'older-loan' and not r['etymon']:
            bad('bad-row', 'an older loan needs its etymon')
        for kind in overrides(r):
            if kind not in CONFLICTS:
                bad('bad-row', f'override of an unknown conflict kind {kind!r}')
        if r['pos'] == 'name':
            continue
        k = canon.get(r['k'], r['k'])
        if k != r['k']:
            bad('bad-row', f'not the house spelling: {k!r}')
        ents = con.execute("SELECT e.id, e.origin, e.chars, e.english, e.etymon, e.hv_check, e.origin_note FROM entry e "
                           "JOIN source s ON s.id = e.source WHERE e.key=? AND s.fixture = 0 AND e.pos != "
                           "'character-reading' ORDER BY e.pos = 'name'", (k,)).fetchall()
        if not ents:
            bad('no-key', f'{r["k"]!r} is not a word of the database')
        # characters against the syllables
        syl = r['k'].replace('-', ' ').split()
        if r['chars']:
            if len(r['chars']) != len(syl):
                bad('hv-mismatch', f'{len(r["chars"])} characters for {len(syl)} syllables')
            else:
                for s, c in zip(syl, r['chars']):
                    rd = bridge.hv_readings(con, c)
                    if rkey(s) not in {rkey(x) for x in rd}:
                        bad('hv-mismatch', f'{c} is read {"/".join(rd) or "(no reading)"}, not {s}')
        # origin and characters against Wiktionary's etymologies
        dbo = {e[1] for e in ents if e[1]}
        if dbo and r['origin'] not in ('unknown',) and not any(r['origin'] in DB_ALLOWS.get(o, set()) for o in dbo):
            bad('origin-conflict', f'Wiktionary: {", ".join(sorted(dbo))} ({next((e[6] for e in ents if e[6]), "")[:60]})')
        dbc = {e[2] for e in ents if e[2] and e[5] not in ('differs', 'length')}
        if r['chars'] and dbc and r['chars'] not in dbc and not any(r['chars'] in bridge.spellings(con, c) for c in dbc):
            bad('chars-conflict', f'Wiktionary analyses {"/".join(sorted(dbc))}')
        ety = {re.match(r'\S*', e[4]).group(0) for e in ents if e[4]}
        if r['etymon'] and ety and not any(r['etymon'] in x or x in r['etymon'] for x in ety):
            bad('chars-conflict', f'Wiktionary\'s etymon is {"/".join(sorted(ety))}')
        # English against every sense and translation of the word
        if ents:
            ids = [e[0] for e in ents]
            texts = [e[3] for e in ents] + [g for (g,) in con.execute(
                f"SELECT gloss FROM sense WHERE entry_id IN ({','.join('?' * len(ids))})", ids)]
            texts += [t for (t,) in con.execute('SELECT en FROM translation WHERE key=?', (k,))]
            known = set().union(*(words(t) for t in texts)) if texts else set()
            mine = words(r['en'])
            if mine and not (mine & known):
                bad('en-unsupported', 'no English word shared with any dictionary sense or translation')
        if r['origin'] in ('hv', 'hv-gram') and len(r['chars']) > 1 and not attested(con, r['chars']):
            bad('not-attested', f'{r["chars"]} is a word of no Chinese source (CC-CEDICT, rime, MOE, translations)')
    kinds = {}
    for r, k, _ in out:
        kinds.setdefault(id(r), set()).add(k)
    for r in rows:
        for k in overrides(r):
            if k in CONFLICTS and k not in kinds.get(id(r), set()):
                out.append((r, 'bad-row', f'override of {k!r}, a conflict the row does not have: remove it'))
    return out


def main():
    sys.path.insert(0, HERE)
    import cards
    con = cards.open_db('public')
    rows = load()
    res = validate(con, rows)
    open_ = [(r, k, m) for r, k, m in res if k not in overrides(r)]
    shown = res if '--all' in sys.argv else open_
    for r, k, m in shown:
        tag = '' if k not in overrides(r) else f' [override: {overrides(r)[k]}]'
        print(f'lexicon line {r["n"]} {r["key"]}: {k}: {m}{tag}')
    conf = {}
    for r in rows:
        conf[r['conf']] = conf.get(r['conf'], 0) + 1
    print(f'lexicon: {len(rows)} rows ({", ".join(f"{k} {v}" for k, v in sorted(conf.items()))}); '
          f'{sum(1 for r in rows if r["override"])} with an override; conflicts: {len(res)} found, '
          f'{len(res) - len(open_)} resolved by an override, {len(open_)} open')
    return 1 if open_ else 0


if __name__ == '__main__':
    sys.exit(main())
