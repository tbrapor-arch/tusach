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
yue / nan / cmn (Jyutping, Tâi-lô LITERARY reading, pinyin; tools/bridge.py), nan_coll (the MOE word reading when it is
not the literary one: colloquial / everyday), hv (Hán-Việt readings per character, labelled), other (the other
etymologies of the spelling: en, chars), by_char
(languages built character by character), label (same | false-friend | native | ''), ff (false-friend note), ex {vi, en},
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
import bridge  # noqa: E402
import english  # noqa: E402
import vi  # noqa: E402

DB = {'public': os.path.join(ROOT, 'data/build/vi.db'), 'private': os.path.join(ROOT, 'data/build/vi-nc.db')}
STORE = os.path.join(ROOT, 'data/build/cards.json')
FALSE_FRIENDS = os.path.join(ROOT, 'course/false_friends.tsv')
PUBLIC_MODULES = ('lessons',)

dictionary = {}
con = ENGLISH = None
COURSE = {}       # card id -> course data for the word (en, chars, label, name) from the lessons' new_words
NAMES = {}        # surface (spaces, original case) -> card id, for names declared in new_words with `name: true`
KNOWN = set()     # every dictionary key, for the dictionary cutter
CANON = {}        # key of a spelling -> the house spelling's key (table `spelling`: lí do -> lý do)


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
    CANON.clear()
    try:
        CANON.update(con.execute('SELECT key, canon FROM spelling'))
    except sqlite3.Error:              # a database built before spelling groups existed
        pass
    KNOWN.update(CANON)


def canon(k):
    """The key a spelling is filed under: the house spelling of its spelling group (lí do -> lý do), else itself."""
    return CANON.get(k, k)


def load_false_friends(path=FALSE_FRIENDS):
    """{(word key, chữ Hán or ''): note} from course/false_friends.tsv (hand-curated: false friends cannot be detected
    automatically). Format in the file's header: word <TAB> chữ Hán <TAB> note in English; # starts a comment."""
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            if not line.strip() or line.startswith('#'):
                continue
            p = (line.rstrip('\n').split('\t') + ['', ''])[:3]
            out[(vi.key(p[0]), p[1].strip())] = p[2].strip()
    return out


FF = load_false_friends()


def per_char(chars):
    """The readings of each character of a compound formed in Vietnamese (trường học 場學): [{c, hv, yue, nan, cmn}],
    shown "per character", never composed into a Chinese word that does not exist."""
    out = []
    for c in chars:
        j = bridge.join(con, c)
        out.append({'c': c, 'hv': '/'.join(bridge.hv_readings(con, c)), **{x: j[x] for x in bridge.LANGS if j[x]},
                    **({'nan_coll': j['nan_coll']} if j['nan_coll'] else {})})
    return out


def _bridge(chars):
    """The Chinese side of a Hán-Việt card, from tools/bridge.py (the same join the database and coverage use)."""
    j = bridge.join(con, chars)
    out = {lang: j[lang] for lang in bridge.LANGS if j[lang]}
    out['hv'] = j['hv']
    if j['nan_coll']:
        out['nan_coll'] = j['nan_coll']          # the MOE word reading, colloquial / everyday (never as literary)
    if j.get('via'):
        out['via'] = j['via']                    # readings found under a variant spelling (Unihan): 行爲 -> 行為
    if j.get('nan_flag'):
        out['nan_flag'] = j['nan_flag']          # colloquial-only: no literary Taigi reading (冊 tsheh)
    by_char = [lang for lang in bridge.LANGS if j[lang] and j[lang + '_by'] == 'char' and len(chars) > 1]
    if by_char:
        out['by_char'] = by_char
    return out


def senses(rows):
    """The dictionary rows of one key grouped by etymology, main one first: real sources before the fixture, then the
    English source order (english.SOURCE_RANK), then the etymology number, then a group that is not only names, then the
    source order. The characters, label, English and example of a card all come from ONE group, so two homographs are
    never mixed (sung 'cluster fig' never gets the 充 of sung 'to fill').
    An etymology is (source, Wiktionary etymology number, characters, origin): kaikki gives the number only on pages
    with several etymologies, and gives the same number (or none) to parts of speech with etymologies of their own, so
    on the first real build lại "again" (no number) took 賴 from the surname entry and anh "elder brother" took 英 from
    the name/adjective entry under Etymology 1."""
    groups = {}
    real = [r for r in rows if r.get('english') or r.get('chars') or not r.get('alt_kind')]
    for r in (real or rows):         # an "alternative spelling" row pooled with its word has no English of its own
        groups.setdefault((r['source'], r['src_id'], r['chars'], r.get('origin') or ''), []).append(r)
    order = {s: i for i, s in enumerate(english.SOURCE_RANK)}

    def k(item):
        (src, sid, _, _), rs = item
        # an entry with no etymology number on a page that has numbered ones (thích 釋, a surname) comes after them;
        # a character reading (tam~三) and an English-less group come last
        return (rs[0]['fixture'], all(r.get('pos') == 'character-reading' for r in rs),
                not any(r.get('english') for r in rs), order.get(src, len(order)),
                int(sid) if str(sid).isdigit() else 10 ** 6, all(r.get('pos') == 'name' for r in rs), rs[0]['id'])
    out = [rs for _, rs in sorted(groups.items(), key=k)]
    # a later etymology with English the English Wiktionary attests (en_score >= 3) goes before a first one whose
    # senses are all archaic/dialectal/literary (score <= -2): khám "to examine" before the Southern khám "jail"
    score = lambda g: max((r['en_score'] if r.get('en_score') is not None else -9) for r in g)  # noqa: E731
    if len(out) > 1 and score(out[0]) <= -2 and not out[0][0]['fixture']:
        best = max(range(len(out)), key=lambda i: (score(out[i]) >= 3, -i))
        if score(out[best]) >= 3 and not all(r.get('pos') in ('name', 'character-reading') for r in out[best]):
            out.insert(0, out.pop(best))
    # inside one etymology, the entry with the best English evidence first (tools/english.py compose: bận "busy"
    # before the literary noun "time; occurrence"), then the source order
    return [sorted(rs, key=lambda r: (-(r.get('en_score') if r.get('en_score') is not None else -9), r['id']))
            for rs in out]


def _group_en(rs):
    """The English of one etymology: its entries' English, best-attested entry first, at most 4 items and
    english.MAX_TOTAL characters (the first item always)."""
    gl = []
    for r in rs:
        for g in (r['english'] or '').split('; '):
            if g and g not in gl and len(gl) < 4 and (not gl or len('; '.join(gl + [g])) <= english.MAX_TOTAL):
                gl.append(g)
    return '; '.join(gl)


def _group_chars(rs):
    """(chars, label) of one etymology; an analysis that does not match the syllables (hv_check differs or length) is
    not shown (build_db word_checks; `make lint` lists it)."""
    for r in rs:
        if r['chars'] and r['hv_check'] not in ('differs', 'length'):
            return r['chars'], r['label']
    return '', next((r['label'] for r in rs if r['label'] and not r['chars']), '')


COLS = ('word', 'english', 'chars', 'label', 'source', 'fixture', 'id', 'freq_rank', 'src_id', 'hv_check', 'origin', 'pos',
        'alt_kind', 'en_score', 'etymon', 'origin_note', 'doubt', 'doubt_why', 'sino_kind', 'tag', 'key')
SQL_COLS = ', '.join('s.fixture' if c == 'fixture' else 'e.' + c for c in COLS)
ORIGIN_TEXT = {'sino': 'Hán-Việt', 'nonhv': 'older Chinese loan', 'vietic': 'native', 'loan': 'loan',
               'compound': 'compound'}


def sense_tag(rows, tag):
    """The entry a homograph tag names when no entry carries the tag itself (phải~must, năm~year): an entry whose part
    of speech is the tag (phải~verb), else the one entry whose English has the tag as a word. None if not exactly
    one etymology matches (tools/lint.py says so)."""
    t = tag.lower()
    hit = [r for r in rows if (r.get('pos') or '') == t]
    if not hit:
        hit = [r for r in rows if r.get('english') and english.has_word(r['english'], t)]
    keys = {(r['source'], r['src_id'], r['chars'], r.get('origin') or '') for r in hit}
    return hit[0] if len(keys) == 1 else None


def lookup(k, tag=None, surface=None):
    """Card id for the word with key `k` (and homograph tag), or None when neither the dictionary nor the course has it."""
    k = canon(k)
    cid = vi.card_id(k, tag)
    if cid in dictionary:
        return cid
    rows = [dict(zip(COLS, r)) for r in con.execute(
        f"SELECT {SQL_COLS} FROM entry e JOIN source s ON s.id = e.source WHERE e.key=? "
        "ORDER BY s.fixture, e.freq_rank IS NULL, e.freq_rank, e.id", (k,)).fetchall()]
    chosen = None
    if tag:
        tagged = [r for r in rows if r['tag'] == tag]
        if tagged:
            rows = tagged
        else:
            chosen = sense_tag(rows, tag)            # a sense tag: the etymology and entry it names come first
            if not chosen:
                rows = []
    course = COURSE.get(cid, {})
    if not rows and not course:
        return None
    groups = senses(rows)
    if chosen:
        groups.sort(key=lambda g: chosen not in g)
        groups[0].sort(key=lambda r: r is not chosen)
    if course.get('chars'):          # the course names the etymology by its characters
        groups.sort(key=lambda g: not any(r['chars'] == course['chars'] for r in g))
    main = groups[0] if groups else []
    house = next((r['word'] for g in groups for r in g if vi.key(r['word']) == k), None)
    card = {'w': course.get('w') or house or (main[0]['word'] if main else (surface or k).replace('_', ' ')), 'k': k}
    if tag:
        card['tag'] = tag
    gchars, glabel = _group_chars(main)
    chars = course.get('chars') or gchars
    label = course.get('label') or (glabel if not course.get('chars') or chars == gchars else '')
    if chars:
        card['chars'] = chars
        card.update(_bridge(chars))
        if next((r['sino_kind'] for r in main if r['chars'] == chars), '') == 'vn' and len(chars) > 1:
            card['per_char'] = per_char(chars)     # formed in Vietnamese: no Chinese "word" is composed
            for lang in bridge.LANGS:
                card.pop(lang, None)
            card.pop('by_char', None)
            card.pop('nan_coll', None)
    if main and not course.get('chars'):
        top = main[0]
        if top.get('origin'):
            card['origin'] = ORIGIN_TEXT.get(top['origin'], top['origin'])
            if top.get('origin_note') and top['origin'] != 'sino':
                card['origin'] += ': ' + top['origin_note']
        if top.get('doubt'):
            card['doubt'] = top['doubt_why'] or top['doubt']
        if top.get('origin') == 'nonhv':
            em = next((r['etymon'] for r in main if r.get('etymon')), '')
            ec = ''.join(c for c in em.split(' ')[0] if vi.CJK.match(c))
            if ec:
                j = bridge.join(con, ec)
                card['etymon'] = {'chars': ec, 'hv': j['hv'], **{x: j[x] for x in bridge.LANGS if j[x]}}
    ff = FF.get((k, chars)) if (k, chars) in FF else FF.get((k, ''))
    if ff is not None and not course.get('label'):
        label = 'false-friend'
        if ff:
            card['ff'] = ff
    if label:
        card['label'] = label
    if rows and all(r['fixture'] for r in rows):     # only the test fixture has the word: the card says so
        card['fixture'] = 1
    if rows:
        card['src'] = sorted({r['source'] for r in rows})
        rank = next((r['freq_rank'] for r in rows if r['freq_rank']), None)
        if rank:
            card['rank'] = rank
        # a whole sentence first (Tatoeba, chosen by build_db attach_examples), then Wiktionary's own examples, short
        # ones first; one over 200 characters is not shown (a usage note of Wiktionary's, 32 lines on chị)
        ex = con.execute(f"SELECT vi, en, source, ref FROM example WHERE entry_id IN ({','.join('?' * len(main))}) "
                         "AND length(vi) <= 200 ORDER BY source != 'tatoeba', length(vi), id LIMIT 1",
                         [r['id'] for r in main]).fetchone()
        if ex:
            card['ex'] = {'vi': ex[0], 'en': ex[1]}
            if ex[2] != 'fixture':        # attribution: Tatoeba names the sentence and its author
                card['ex']['src'] = ex[2] + (' ' + ex[3] if ex[3] else '')
        other = [{'en': _group_en(g), **({'chars': _group_chars(g)[0]} if _group_chars(g)[0] else {})}
                 for g in groups[1:] if _group_en(g) and not g[0]['fixture']
                 and not all(r['pos'] == 'character-reading' for r in g)]
        if other:
            card['other'] = other         # the other etymologies of this spelling, each with its own English and chars
    syls = k.split()
    if len(syls) > 1:
        card['parts'] = [p for p in (lookup(s) for s in syls) if p]
    parts = [(dictionary[p].get('en'), dictionary[p].get('en_src')) for p in card.get('parts', [])]
    den = (_group_en(main), f"dict:{main[0]['source']}") if main and _group_en(main) else None
    en, src = ENGLISH.gloss(cid, k, tag, parts if len(parts) == len(syls) else (), dict_entry=den)
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
    then exactly as a course line. The cut follows docs/SEGMENTATION.md; measured by `make cutter` on
    tests/cutter/reference.tsv (written and cut by Claude, not native-checked)."""
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
