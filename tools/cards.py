"""The one word pipeline: every module (lessons now; books, podcast, lists, subtitles later, public or private) cuts its
text into words and gets its word cards here, so a word has the same card wherever it is tapped. No module may build
cards or cut text another way (handover section 4.1: Tsheh-tû's book lists had their own path, and 42 % of their
example lines had a wrong reading).

    import cards
    con = cards.open_db('public')              # the app page; 'private' for the private module (refuses the wrong db)
    cards.init(con, course=cards.course_words(lesson_dicts))
    toks = cards.tokenize('Tôi là học_sinh.')  # a course line: cut by its own boundaries, never guessed
    toks = cards.tokenize_text('Tôi là học sinh.')   # a text without boundaries (books…): cut by the dictionary
    cards.dictionary                           # card id -> card, filled as words are looked up

    store = cards.Store('data/build/cards.json')    # the shared card file of this repository
    store.replace_module('lessons', toks_of_the_module)   # a partial build adds to it; other modules keep their cards
    store.save()

A token is {'p': text} (punctuation, spaces, numbers) or {'w': {'t': surface, 'id': card id or None}}. A word with no
card is kept in the store's `missing` list and fails tools/check_cards.py: "no word without a card".

Card (JSON, in the page's DATA.dict): w (the word), k (key), en, en_src, en_rank, chars (chữ Hán, Hán-Việt words only),
yue / nan / cmn (Jyutping, Tâi-lô literary, pinyin), label (same | false-friend | native | ''), ex {vi, en},
parts (syllable card ids), name (1 for a person or place name), fixture (1 if only the test fixture has it), src.
"""
import datetime
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import english  # noqa: E402
import vi  # noqa: E402

DB = {'public': os.path.join(ROOT, 'data/build/vi.db'), 'private': os.path.join(ROOT, 'data/build/vi-nc.db')}
STORE = os.path.join(ROOT, 'data/build/cards.json')
PUBLIC_MODULES = ('lessons',)

dictionary = {}
con = ENGLISH = None
COURSE = {}       # card id -> course data for the word (en, chars, label, name) from the lessons' new_words
NAMES = {}        # surface (spaces, original case) -> card id, for names declared in new_words with `name: true`
KNOWN = set()     # every dictionary key, for the dictionary cutter


def open_db(purpose, path=None):
    """The database for a build. 'public' (the app page) must be a public build (meta nc = 0, vi.db); 'private' (the
    private module) must be the non-commercial build (meta nc = 1, vi-nc.db). Anything else stops the build."""
    if purpose not in DB:
        raise SystemExit(f'cards.open_db: unknown purpose {purpose!r}')
    path = path or os.environ.get('TUSACH_DB') or DB[purpose]
    if not os.path.exists(path):
        raise SystemExit(f'cards.open_db: {path} not found: run `make {"db" if purpose == "public" else "db-nc"}`')
    c = sqlite3.connect(path)
    try:
        nc = dict(c.execute('SELECT key, value FROM meta')).get('nc')
    except sqlite3.Error:
        nc = None
    want = '0' if purpose == 'public' else '1'
    if nc != want:
        raise SystemExit(f'cards.open_db: refusing {path} for a {purpose} build: it is '
                         f'{"a non-commercial" if nc == "1" else "a public" if nc == "0" else "an unmarked"} database '
                         f'(public page: `make db` -> vi.db; private module: `make db-nc` -> vi-nc.db)')
    return c


def course_words(lessons):
    """{card id: {en, chars, label, name, w}} from lesson dicts (their new_words). Course English wins on the card."""
    out = {}
    for L in lessons:
        for w in L.get('new_words') or []:
            surf = vi.nfc(w['w']).replace('_', ' ')
            cid = ('name:' + surf) if w.get('name') else vi.card_id(vi.key(surf), w.get('tag'))
            out[cid] = {'w': surf, **{k: w[k] for k in ('en', 'chars', 'label', 'name', 'tag') if w.get(k)}}
    return out


def init(connection, course=None, written=None):
    global con, ENGLISH
    con = connection
    dictionary.clear()
    COURSE.clear()
    COURSE.update(course or {})
    NAMES.clear()
    for cid, c in COURSE.items():
        if c.get('name'):
            NAMES[c['w']] = cid
    ENGLISH = english.English(con, {cid: c['en'] for cid, c in COURSE.items() if c.get('en')}, written)
    KNOWN.clear()
    KNOWN.update(k for (k,) in con.execute('SELECT DISTINCT key FROM entry'))


def _bridge(chars):
    out = {}
    for lang, r in con.execute('SELECT lang, reading FROM chinese WHERE chars=? ORDER BY rowid', (chars,)):
        out.setdefault(lang, [])
        if r not in out[lang]:
            out[lang].append(r)
    return {lang: ' / '.join(v) for lang, v in out.items()}


def lookup(k, tag=None, surface=None):
    """Card id for the word with key `k` (and homograph tag), or None when neither the dictionary nor the course has it."""
    cid = vi.card_id(k, tag)
    if cid in dictionary:
        return cid
    rows = con.execute("SELECT e.word, e.english, e.chars, e.label, e.source, s.fixture, e.id, e.freq_rank "
                       "FROM entry e JOIN source s ON s.id = e.source WHERE e.key=? AND (?='' OR e.tag=?) "
                       "ORDER BY s.fixture, e.freq_rank IS NULL, e.freq_rank, e.id", (k, tag or '', tag or '')).fetchall()
    course = COURSE.get(cid, {})
    if not rows and not course:
        return None
    card = {'w': course.get('w') or (rows[0][0] if rows else (surface or k).replace('_', ' ')), 'k': k}
    if tag:
        card['tag'] = tag
    chars = course.get('chars') or next((r[2] for r in rows if r[2]), '')
    label = course.get('label') or next((r[3] for r in rows if r[3]), '')
    if chars:
        card['chars'] = chars
        card.update(_bridge(chars))
    if label:
        card['label'] = label
    if rows and all(r[5] for r in rows):     # only the test fixture has the word: the card says so
        card['fixture'] = 1
    if rows:
        card['src'] = sorted({r[4] for r in rows})
        rank = next((r[7] for r in rows if r[7]), None)
        if rank:
            card['rank'] = rank
        ex = con.execute(f"SELECT vi, en FROM example WHERE entry_id IN ({','.join('?' * len(rows))}) ORDER BY id LIMIT 1",
                         [r[6] for r in rows]).fetchone()
        if ex:
            card['ex'] = {'vi': ex[0], 'en': ex[1]}
    syls = k.split()
    if len(syls) > 1:
        card['parts'] = [p for p in (lookup(s) for s in syls) if p]
    parts = [(dictionary[p].get('en'), dictionary[p].get('en_src')) for p in card.get('parts', [])]
    en, src = ENGLISH.gloss(cid, k, tag, parts if len(parts) == len(syls) else ())
    card['en'], card['en_src'], card['en_rank'] = en, src, english.rank(src)
    dictionary[cid] = card
    return cid


def name_card(surface):
    cid = NAMES.get(surface)
    if cid and cid not in dictionary:
        c = COURSE[cid]
        en = c.get('en') or ''
        dictionary[cid] = {'w': surface, 'k': surface, 'name': 1, 'en': en, 'en_src': 'course' if en else '',
                           'en_rank': english.rank('course' if en else ''), 'label': c.get('label', '')}
    return cid


def tokenize(line):
    """A course line, cut by its own boundaries (underscores inside words, `~tag` for homographs): nothing is guessed."""
    out = []
    for t in vi.words(line):
        if t[0] != 'w':
            out.append({'p': t[1].replace('_', ' ')})
            continue
        _, surf, k, tag, _start = t
        shown = surf.replace('_', ' ')
        cid = name_card(shown) if shown in NAMES and not tag else lookup(k, tag, surf)
        out.append({'w': {'t': shown, 'id': cid}})
    merged = []
    for t in out:
        if 'p' in t and merged and 'p' in merged[-1]:
            merged[-1]['p'] += t['p']
        else:
            merged.append(t)
    return merged


def tokenize_text(text):
    """A text with no boundaries of its own (books, transcripts, subtitles): cut by the dictionary (tools/vi.py cut()),
    then exactly as a course line. TODO(cutter): measure the cut against a hand-cut reference (handover step 5)."""
    return tokenize(vi.cut(text, KNOWN | {vi.key(n) for n in NAMES}))


def ids_of(tokens):
    return [t['w']['id'] for t in tokens if 'w' in t]


class Store:
    """The shared card file of a repository. Each module (lessons, a book, a podcast…) records the cards it uses and
    the words it has; building one module replaces only its own record and adds its cards, so a partial build never
    leaves another module's words without a card and never needs generated files restored (handover section 4.4)."""

    def __init__(self, path=STORE):
        self.path = path
        d = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
        self.cards = d.get('cards', {})
        self.modules = d.get('modules', {})

    def replace_module(self, name, tokens, extra_ids=()):
        """`tokens`: every token of the module's texts (from tokenize / tokenize_text); `extra_ids`: other card ids the
        module shows (new-word lists, example lists). The cards come from cards.dictionary."""
        words = [t['w'] for t in tokens if 'w' in t]
        ids = sorted({w['id'] for w in words if w['id']} | {i for i in extra_ids if i})
        # a compound's parts are shown on its card: they are part of the module too
        todo = list(ids)
        while todo:
            for p in dictionary[todo.pop()].get('parts', []):
                if p not in ids:
                    ids.append(p)
                    todo.append(p)
        self.modules[name] = {'cards': sorted(ids), 'missing': sorted({w['t'] for w in words if not w['id']}),
                              'built': datetime.date.today().isoformat()}
        for i in ids:
            self.cards[i] = dictionary[i]

    def keep(self, ids):
        """Cards a published page has had (app/published-card-ids.txt): kept even when no module uses them now."""
        self.modules['_published'] = {'cards': sorted(i for i in ids if i in self.cards), 'missing': [], 'built': ''}

    def page_cards(self, modules):
        ids = {i for m in modules for i in self.modules.get(m, {}).get('cards', [])}
        return {i: self.cards[i] for i in sorted(ids)}

    def save(self):
        used = {i for m in self.modules.values() for i in m['cards']}
        self.cards = {i: c for i, c in sorted(self.cards.items()) if i in used}
        tmp = self.path + '.tmp'
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        json.dump({'cards': self.cards, 'modules': self.modules}, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False,
                  indent=0, sort_keys=True)
        os.replace(tmp, self.path)
