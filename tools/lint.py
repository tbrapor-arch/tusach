"""Check the lesson files: content rules and every word against the database.

  python3 -I tools/lint.py [lesson.yaml ...]      (default: course/lessons/NN.yaml, or the test fixture while there is none)

Checks (E = error, exit 1; W = warning; I = information)
  E  a lesson exists while the syllabus or the first word list is not approved by the owner (course/syllabus.yaml)
  E  YAML error, missing field, file name not the lesson id, two lessons with one id
  E  a file in course/lessons/ not named NN.yaml; `fixture: true` outside tools/fixtures/
  E  an unknown key or a key with no value in a lesson item: a YAML flow mapping cut at an unquoted comma
     ({w: tôi, en: I, me} reads as en: I plus a key "me"): quote the text
  E  text not in Unicode NFC (every string of the file)
  E  chữ Hán in a lesson line, a title or an exercise sentence (characters belong on cards and in the bridge)
  E  impossible quốc ngữ syllable (tools/vi.py): letters, c/k, g/gh, ng/ngh, -c -ch -p -t with a tone other than sắc/nặng
  E  tone mark not placed in the house style (hòa, khỏe, thủy: docs/REFERENCE.md); keys ignore the placement
  E  word in no dictionary of the database and not declared as a name in new_words
  E  word that only the test fixture has, in a real lesson
  E  `~tag` that no dictionary entry and no new_words entry defines
  E  new_words entry without English (English on every card), or not used in the lesson
  E  exercise sentence taken from the dialogue: equal to a line, contained in a line, or equal to one after removing a
     greeting / first clause (normalised: case, punctuation, word boundaries)
  W  exercise sentence very similar to a dialogue line (similarity >= SIMILAR): check it is a new sentence
  E  note pointing to a line the dialogue does not have
  E  fill exercise without ___ or answer
  W  lines per lesson do not grow smoothly (owner's choice: a smooth growth; checked over the non-review lessons)
  W  review flag not on every 7th lesson
  E  a word not in the house spelling of its spelling group (lý do, not lí do; docs/REFERENCE.md "Spelling groups")
  E  a word without ~tag whose key has several senses in the course lexicon (course/lexicon.tsv), or, when the
     lexicon has no row for it, several etymologies in the dictionary: tag it (từ~from, năm~year), never a silent
     first card
  E  a bridge note (topic bridge) whose chữ Hán example is not the same word in Chinese for the sense taught: a
     course lexicon row with these characters and origin hv / hv-gram (not doubtful, not a false friend), else (no
     lexicon row has them) a database word with them labelled same / gram; and all four readings (Hán-Việt,
     Cantonese, Taigi literary, Mandarin)
  E  a conflict of the course lexicon with the data (tools/lexicon.py) that the row does not override with a reason
  E  (once the owner approved a word list: approved.word_list.file in course/syllabus.yaml) a new_words entry not in
     that list, or listed for another lesson; W a word the list gives the lesson that its new_words lacks; E the list
     not in the 11-column format (tools/course.py WORDLIST_COLS), a row listed twice, a lesson number that is not a
     lesson of the syllabus
  E  an unknown key in a lesson plan of course/syllabus.yaml (n, en, vi, review, grammar, bridge, strand, lines,
     new_words {native, hv}); W a written lesson whose dialogue length or new words (native / Hán-Việt) leave the
     plan by more than one, or whose Hán-Việt share is more than 0.2 from the plan's
  I  lesson not checked by a native speaker (no native_check: {by, date}); the app labels it
The words of the lines are also checked by tools/verify_words.py (`make lint` runs both).
"""
import collections
import os
import re
import sqlite3
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import course  # noqa: E402
import lexicon  # noqa: E402
import vi  # noqa: E402

LEX = lexicon.load()
LEX_CID, LEX_KEY = lexicon.index(LEX)

DB = os.environ.get('TUSACH_DB') or os.path.join(ROOT, 'data/build/vi.db')
REQUIRED = ('id', 'title', 'dialogue', 'notes', 'new_words')
KEYS = {'top': {'id', 'title', 'review', 'setting', 'native_check', 'dialogue', 'notes', 'new_words', 'exercises',
                'fixture'},
        'title': {'vi', 'en'}, 'dialogue': {'n', 'speaker', 'vi', 'en'}, 'notes': {'ref', 'topic', 'text'},
        'new_words': {'w', 'en', 'tag', 'chars', 'label', 'name'}, 'translate': {'vi', 'en'},
        'fill': {'vi', 'answer', 'en'}, 'native_check': {'by', 'date'}}
SIMILAR = 0.8


def norm_tokens(text):
    """Word keys of a line, without punctuation or case: the unit of the exercise-copy check."""
    return [t[2] for t in vi.words(text) if t[0] == 'w']


def clauses(text):
    """The clauses of a line (split at , ; : ! ? . …), each as a token list."""
    return [c for c in (norm_tokens(x) for x in re.split(r'[,;:!?.…]+', vi.display(text))) if c]


def copied(ex, line):
    """'copy' when the exercise is a dialogue line, part of one, or one without its first clause (or the other way
    round); a similarity ratio otherwise."""
    import difflib
    e, l_ = norm_tokens(vi.display(ex)), norm_tokens(vi.display(line))
    if not e or not l_:
        return 0.0

    def inside(a, b):
        return len(a) >= 2 and any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))
    ec, lc = clauses(ex), clauses(line)
    e_rest = [t for c in ec[1:] for t in c]
    l_rest = [t for c in lc[1:] for t in c]
    if e == l_ or inside(e, l_) or (e_rest and (e_rest == l_ or inside(e_rest, l_))) or (l_rest and e == l_rest):
        return 'copy'
    return difflib.SequenceMatcher(None, e, l_).ratio()


def check_keys(m, where, item, kind):
    if not isinstance(item, dict):
        return
    for k, v in item.items():
        if k not in KEYS[kind]:
            m('E', where, f'unknown key "{k}"' + (' (an unquoted comma in a flow mapping cut the text before it: '
                                                   'quote the value)' if v is None else ''))
        elif v is None and k != 'native_check':
            m('E', where, f'"{k}" has no value')


class DB_:
    """What lint needs of the database: keys, tags, spelling groups, sense tags, bridge-note checks."""

    def __init__(self, path):
        self.con = con = sqlite3.connect(path)
        cols = {r[1] for r in con.execute('PRAGMA table_info(entry)')}
        self.spelling = dict(con.execute('SELECT key, canon FROM spelling')) if con.execute(
            "SELECT 1 FROM sqlite_master WHERE name='spelling'").fetchone() else {}
        self.cols = cols

    def rows(self, k):
        import cards
        want = [c for c in cards.COLS if c in self.cols or c == 'fixture']
        sql = ', '.join('s.fixture' if c == 'fixture' else 'e.' + c for c in want)
        return [dict(zip(want, r)) for r in self.con.execute(
            f'SELECT {sql} FROM entry e JOIN source s ON s.id = e.source WHERE e.key=?', (k,))]

    def sense_tag(self, k, tag):
        import cards
        return cards.sense_tag(self.rows(k), tag) is not None

    def senses(self, k):
        """The word-etymologies of a key (not names, character readings, pronunciation spellings or English-less
        stubs): what an untagged lesson word would have to choose between."""
        import cards
        gs = cards.senses([r for r in self.rows(k) if r.get('pos') not in ('name', 'character-reading')
                           and r.get('alt_kind') != 'pron' and r.get('english') and not r.get('fixture')])
        return gs

    def bridge_example(self, chars, word=None):
        """'' when `chars` may be a bridge-note example, else why not. The sense taught decides: a lexicon row with
        these characters (唐 is đường~road's analysis, doubtful: refused even though the Tang dynasty is 唐), else
        the database words with them (names aside). With the Vietnamese `word` the note pairs them with (review 3,
        finding 7: "phải is 被", "thì is 時", "bằng is 平", "nôm is 南" passed on the characters alone), the PAIR is
        judged on that word's card for the sense: its lexicon rows (one with these characters, origin hv / hv-gram,
        not doubtful, not a false friend), else its database entries with these characters labelled same / gram
        and not doubtful; a single character must also be read so the Hán-Việt way."""
        if word:
            why = self.pairing(chars, word)
            if why:
                return why
        rows = [r for r in LEX if r['chars'] == chars and r['pos'] != 'name']
        if rows:
            good = [r for r in rows if r['origin'] in ('hv', 'hv-gram') and r['conf'] != 'doubt' and
                    not r['false_friend']]
            if not good:
                r = rows[0]
                return (f'the course lexicon gives {chars} to {r["key"]} as {r["origin"]}'
                        f'{" (doubtful)" if r["conf"] == "doubt" else ""}{" (false friend)" if r["false_friend"] else ""}'
                        ': not the same word in Chinese')
        else:
            labels = [r[0] for r in self.con.execute("SELECT label FROM entry WHERE chars=? AND source != 'fixture' "
                                                     "AND pos NOT IN ('name', ?)", (chars, 'character-reading' if
                                                                                    len(chars) > 1 else ''))]
            if not labels:
                return 'no database word has these characters'
            if 'same' not in labels and 'gram' not in labels:
                return f'its analysis is not "same word in Chinese" ({", ".join(sorted(set(labels)))})'
        b = self.con.execute('SELECT hv, n FROM bridge WHERE chars=?', (chars,)).fetchone()
        if not b or b[1] < 3 or '—' in (b[0] or ''):
            return 'not all four readings exist (Hán-Việt, Cantonese, Taigi literary, Mandarin)'
        return ''


def _pair_ok(self, chars, word):
    import bridge
    k = vi.key(word)
    k = self.spelling.get(k, k)
    if len(k.split()) != len(chars):
        return f'{word} has {len(k.split())} syllable(s) for {len(chars)} character(s)'
    if len(chars) == 1 and lexicon.rkey(k) not in {lexicon.rkey(x) for x in bridge.hv_readings(self.con, chars)}:
        return f'{word} is not a Hán-Việt reading of {chars} ({"/".join(bridge.hv_readings(self.con, chars)) or "none"})'
    rows = [r for r in LEX_KEY.get(k, []) if r['pos'] != 'name']
    if rows:
        good = [r for r in rows if r['chars'] in bridge.spellings(self.con, chars) and r['origin'] in ('hv', 'hv-gram')
                and r['conf'] != 'doubt' and not r['false_friend']]
        if not good:
            r = next((x for x in rows if x['chars'] in bridge.spellings(self.con, chars)), rows[0])
            what = r['origin'] + (f' {r["chars"] or r["etymon"]}' if r['chars'] or r['etymon'] else '')
            return (f'the course lexicon gives {word} as {what}{" (doubtful)" if r["conf"] == "doubt" else ""}'
                    f'{" (false friend)" if r["false_friend"] else ""}: not "{word} is {chars}"')
        return ''
    labels = {lb for lb, dbt, ch in self.con.execute(
        "SELECT label, doubt, chars FROM entry WHERE key=? AND source != 'fixture' AND pos NOT IN ('name', "
        "'character-reading') AND chars != ''", (k,)) if ch in bridge.spellings(self.con, chars) and not dbt}
    if not labels & {'same', 'gram'}:
        if len(chars) == 1:          # a character read the Hán-Việt way, its word not in the dictionary: its own label
            return ''
        return f'no word {word} with {chars} labelled "same word in Chinese" in the dictionary'
    return ''


DB_.pairing = _pair_ok


def cjk_pairs(text):
    """[(chữ Hán run, the Vietnamese word written next to it or '')]: "平 bình", "學生 học sinh" (after the run), "học
    sinh is 學生" (before it): as many syllables as characters."""
    out = []
    syl = r"[^\W\d_]+"
    for m in re.finditer(vi.CJK.pattern + '+', text):
        run, n = m.group(0), len(m.group(0))
        after = re.match(r'\s+(' + r'\s+'.join([syl] * n) + r')\b', text[m.end():])
        before = re.search(r'\b(' + r'\s+'.join([syl] * n) + r')\s+(?:is|=|:|,)?\s*$', text[:m.start()])
        word = ''
        for cand in ((after.group(1) if after else ''), (before.group(1) if before else '')):
            if cand and all(not vi.syllable_problems(x.lower()) for x in cand.split()):
                word = cand
                break
        out.append((run, word))
    return out


def untagged(k):
    """Why an untagged word cannot be written so ('' when it can): several senses in the lexicon, or (no lexicon row)
    several etymologies in the dictionary."""
    rs = LEX_KEY.get(k, [])
    if len(rs) > 1:
        return (f'the course lexicon has {len(rs)} senses of it: write one of '
                f'{", ".join(r["key"] for r in rs if r["tag"]) or "its tags"}')
    if not rs and D is not None:
        n = len(D.senses(k))
        if n > 1:
            return f'{n} etymologies in the dictionary and no lexicon row: add the sense to course/lexicon.tsv or tag it'
    return ''


D = None


def load_db():
    con = sqlite3.connect(DB)
    keys = collections.defaultdict(set)     # key -> {(source is fixture)}
    tags = collections.defaultdict(set)
    for k, tag, fx in con.execute('SELECT e.key, e.tag, s.fixture FROM entry e JOIN source s ON s.id = e.source'):
        keys[k].add(bool(fx))
        if tag:
            tags[k].add(tag)
    return keys, tags


def strings(o, path=''):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from strings(k, path) if isinstance(k, str) else ()
            yield from strings(v, f'{path}.{k}' if path else str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, f'{path}[{i}]')


LABELS = ('same', 'false-friend', 'native', 'hv-vn', 'older-loan', 'loan', 'compound', 'doubtful', 'opaque')
D = None          # DB_ of the run
listed = None     # {card id: {lesson numbers}} of the approved word list, None while none is approved


def word_list_ids(path):
    """{card id: {lessons}} of an 11-column word list (tools/course.py wordlist): a word with ~tag keeps it; a name
    (type name) is 'name:' + surface."""
    out = collections.defaultdict(set)
    for r in course.wordlist(path):
        w = vi.nfc(r['word'])
        base, _, tag = w.partition('~')
        if r['type'] == 'name':
            cid = 'name:' + base.replace('_', ' ')
        else:
            k = vi.key(base.replace('_', ' '))
            cid = vi.card_id(D.spelling.get(k, k) if D else k, tag or None)
        out[cid].add(int(r['lesson']) if r['lesson'].isdigit() else r['lesson'])
    return out


def plan_checks(loaded, msgs):
    """The lesson plans of course/syllabus.yaml against the written lessons."""
    plans = {}
    for i, p in enumerate(course.syllabus().get('lessons') or []):
        if not isinstance(p, dict):
            continue
        for k in p:
            if k not in course.PLAN_KEYS:
                msgs.append(('E', f'course/syllabus.yaml: lessons[{i}]: E unknown key "{k}" (one of '
                                  f'{", ".join(sorted(course.PLAN_KEYS))})'))
        if isinstance(p.get('new_words'), dict):
            for k in p['new_words']:
                if k not in ('native', 'hv'):
                    msgs.append(('E', f'course/syllabus.yaml: lessons[{i}].new_words: E unknown key "{k}" (native, hv)'))
        if p.get('n') is not None:
            plans[p['n']] = p
    import cards
    for f, d in loaded:
        p = plans.get(d.get('id'))
        if not p or d.get('fixture'):
            continue
        name = os.path.basename(f)
        n = len(d.get('dialogue') or [])
        if isinstance(p.get('lines'), int) and abs(n - p['lines']) > 1:
            msgs.append(('W', f'{name}: W {n} dialogue lines, the plan says {p["lines"]}'))
        nw = p.get('new_words') or {}
        if isinstance(nw, dict) and (nw.get('native') is not None or nw.get('hv') is not None):
            hv = nat = 0
            for w in d.get('new_words') or []:
                if w.get('name'):
                    continue
                k = vi.key(w['w'])
                cid = cards.lookup(k, w.get('tag')) if cards.con else None
                card = (cards.dictionary.get(cid) or {}) if cid else {}
                lab = w.get('label') or card.get('label', '')
                if lab in ('same', 'gram', 'hv-vn', 'doubtful', 'opaque', 'false-friend') and not card.get('etymon'):
                    hv += 1
                else:
                    nat += 1
            for kind, have in (('native', nat), ('hv', hv)):
                if isinstance(nw.get(kind), int) and abs(have - nw[kind]) > 1:
                    msgs.append(('W', f'{name}: W {have} {kind} new words, the plan says {nw[kind]}'))
            want = (nw.get('hv') or 0) / max(1, (nw.get('hv') or 0) + (nw.get('native') or 0))
            if hv + nat and abs(hv / (hv + nat) - want) > 0.2:
                msgs.append(('W', f'{name}: W Hán-Việt share of new words {hv / (hv + nat):.2f}, the plan {want:.2f}'))


def lint(path, d, keys, tags, all_tags, names, msgs, spellings):
    def m(level, where, text):
        msgs.append((level, f'{os.path.relpath(path, ROOT)}:{where}: {level} {text}'))

    for f in REQUIRED:
        if f not in d:
            m('E', 0, f'missing field: {f}')
    if d.get('fixture_claimed'):
        m('E', 0, '`fixture: true` is accepted only under tools/fixtures/, never in course/lessons/')
    check_keys(m, 0, {k: v for k, v in d.items() if k != 'fixture_claimed'}, 'top')
    if isinstance(d.get('title'), dict):
        check_keys(m, 'title', d['title'], 'title')
    if isinstance(d.get('native_check'), dict):
        check_keys(m, 'native_check', d['native_check'], 'native_check')
    for kind in ('dialogue', 'notes', 'new_words'):
        for i, it in enumerate(d.get(kind) or []):
            check_keys(m, f'{kind}[{i}]', it, kind)
    for kind, items in (d.get('exercises') or {}).items():
        if kind in KEYS:
            for i, it in enumerate(items or []):
                check_keys(m, f'exercises.{kind}[{i}]', it, kind)
    real = not d.get('fixture')
    name = os.path.basename(path)
    if not re.fullmatch(r'\d\d+\.yaml', name) or int(name.split('.')[0]) != d.get('id'):
        m('E', 0, f'file name {name} does not match id {d.get("id")} (NN.yaml)')
    for where, s in strings(d):
        if not vi.is_nfc(s):
            m('E', where, f'not in Unicode NFC: "{s[:40]}"')
    title = d.get('title') or {}
    if not title.get('vi') or not title.get('en'):
        m('E', 'title', 'title needs vi and en')
    if vi.CJK.search(str(title.get('vi', ''))):
        m('E', 'title', 'chữ Hán in the title')
    nc = d.get('native_check')
    if nc and not (isinstance(nc, dict) and nc.get('by') and nc.get('date')):
        m('E', 'native_check', 'native_check needs {by, date}')
    if real and not nc:
        m('I', 0, 'not checked by a native speaker (the app says so)')
    lesson_names = {vi.nfc(w['w']).replace('_', ' ') for w in d.get('new_words') or [] if w.get('name')}
    used = set()

    def check_line(where, text):
        if vi.CJK.search(text):
            m('E', where, 'chữ Hán in a lesson line (characters go on cards and in the bridge only)')
        for t in vi.words(text):
            if t[0] != 'w':
                continue
            _, surf, k, tag, start = t
            shown = surf.replace('_', ' ')
            used.add(vi.card_id(k, tag))
            if shown in names or shown in lesson_names:
                used.add('name:' + shown)
                continue
            for s in shown.lower().split():
                for p in vi.syllable_problems(s, style=True):
                    m('E', where, p)
            if D.spelling.get(k, k) != k:
                m('E', where, f'"{shown}": write the house spelling "{D.spelling[k]}" (spelling group, '
                              'docs/REFERENCE.md)')
                k = D.spelling[k]
            if tag and tag not in tags.get(k, set()) | all_tags.get(k, set()) and vi.card_id(k, tag) not in LEX_CID \
                    and not D.sense_tag(k, tag):
                m('E', where, f'"{surf}": tag ~{tag} is defined by no lexicon row, no dictionary entry, no new_words '
                              'entry, and names no part of speech or single sense of the word')
            if not tag and k in keys and not (shown in names or shown in lesson_names):
                why = untagged(k)
                if why:
                    m('E', where, f'"{shown}": {why}')
            if k not in keys:
                hint = ' (a name? declare it in new_words with name: true)' if surf[:1].isupper() and not start else ''
                m('E', where, f'"{shown}" is in no dictionary{hint}')
            elif real and keys[k] == {True}:
                m('E', where, f'"{shown}" is only in the test fixture, not in a real source')

    lines = d.get('dialogue') or []
    ns = set()
    for ln in lines:
        n = ln.get('n', '?')
        ns.add(n)
        for f in ('vi', 'en'):
            if not ln.get(f):
                m('E', f'line {n}', f'missing {f}')
        check_line(f'line {n}', ln.get('vi') or '')
    for i, note in enumerate(d.get('notes') or []):
        if note.get('ref') != 0 and note.get('ref') not in ns:
            m('E', f'notes[{i}]', f"note ref {note.get('ref')} is not a line of the dialogue (use 0 for a recap note)")
        if not note.get('text'):
            m('E', f'notes[{i}]', 'empty note')
        if note.get('topic') == 'bridge':
            for run, word in sorted(set(cjk_pairs(note.get('text') or ''))):
                why = D.bridge_example(run, word or None)
                if why:
                    m('E', f'notes[{i}]', f'bridge example {run} {word}: {why}')
    for kind, items in (d.get('exercises') or {}).items():
        if kind not in ('translate', 'fill'):
            m('E', f'exercises.{kind}', 'unknown exercise kind (translate, fill)')
        for j, it in enumerate(items or []):
            where = f'exercises.{kind}[{j}]'
            text = it.get('vi') or ''
            if not it.get('en'):
                m('E', where, 'missing en')
            if kind == 'fill':
                if '___' not in text or not it.get('answer'):
                    m('E', where, 'a fill item needs ___ in vi and an answer')
                text = text.replace('___', str(it.get('answer', '')).replace(' ', '_'))
            check_line(where, text)
            best = 0.0
            for ln in lines:
                c = copied(text, ln.get('vi') or '')
                if c == 'copy':
                    m('E', where, f'exercise sentence taken from the dialogue (line {ln.get("n")}): write a new one')
                    break
                best = max(best, c)
            else:
                if best >= SIMILAR:
                    m('W', where, f'exercise sentence very similar to a dialogue line ({best:.2f}): is it new?')
    for j, w in enumerate(d.get('new_words') or []):
        if not w.get('w'):
            m('E', f'new_words[{j}]', 'missing w')
            continue
        if not (w.get('en') or '').strip():
            m('E', f'new_words[{j}]', f'{w["w"]}: no English (English on every card)')
        cid = ('name:' + vi.nfc(w['w']).replace('_', ' ')) if w.get('name') else vi.card_id(vi.key(w['w']), w.get('tag'))
        if cid not in used:
            m('E', f'new_words[{j}]', f'{w["w"]} is not used in the dialogue or the exercises')
        if w.get('chars') and not vi.CJK.search(w['chars']):
            m('E', f'new_words[{j}]', f'{w["w"]}: chars must be chữ Hán')
        if w.get('label') and w['label'] not in LABELS:
            m('E', f'new_words[{j}]', f'{w["w"]}: label must be one of {", ".join(LABELS)}')
        if listed is not None and real and not w.get('name'):
            lk = vi.card_id(D.spelling.get(vi.key(w['w']), vi.key(w['w'])), w.get('tag'))
            if lk not in listed:
                m('E', f'new_words[{j}]', f'{w["w"]} is not in the approved word list')
            elif d.get('id') not in listed[lk]:
                m('E', f'new_words[{j}]', f'{w["w"]}: the approved word list gives it to lesson '
                                          f'{", ".join(map(str, sorted(listed[lk])))}')
    if listed is not None and real:
        mine = {vi.card_id(D.spelling.get(vi.key(w['w']), vi.key(w['w'])), w.get('tag'))
                for w in d.get('new_words') or [] if w.get('w')}
        for lk, ls in sorted(listed.items()):
            if d.get('id') in ls and lk not in mine and not lk.startswith('name:'):
                m('W', 'new_words', f'{lk}: the approved word list gives it to this lesson; new_words lacks it')


def main():
    global D, listed
    if '--wordlist' in sys.argv:          # check a word list file alone (format, words, spellings, tags)
        sys.exit(check_wordlist(sys.argv[sys.argv.index('--wordlist') + 1]))
    files = sys.argv[1:] or course.lesson_files()
    keys, tags = load_db()
    D = DB_(DB)
    try:
        import cards
        cards.init(D.con)
    except Exception:                    # noqa: BLE001 - an old database: the plan's Hán-Việt counts are skipped
        pass
    msgs = []
    syl = course.syllabus().get('approved') or {}
    wl = (syl.get('word_list') or {}).get('file') if isinstance(syl.get('word_list'), dict) else None
    if wl:
        try:
            listed = word_list_ids(wl)
        except (OSError, ValueError) as e:
            msgs.append(('E', f'course/syllabus.yaml: E approved word list: {e}'))
    reals = [f for f in files if not course.load(f).get('fixture')] if files else []
    if reals and not (syl.get('syllabus') and syl.get('word_list')):
        msgs.append(('E', f'course/syllabus.yaml: E {len(reals)} lesson(s) drafted before the owner approved the '
                          'syllabus and the first word list (fixed decision): approve them first'))
    for f in course.stray_files():
        msgs.append(('E', f'{os.path.relpath(f, ROOT)}:0: E not a lesson file: only NN.yaml may be in the lesson '
                          'directory (the template is course/lesson_template.yaml)'))
    if not course.real_files():
        print('lint: no lesson in course/lessons yet: checking the test fixture (tools/fixtures/lessons)')
    loaded = []
    for f in files:
        try:
            loaded.append((f, course.load(f)))
        except yaml.YAMLError as e:
            msgs.append(('E', f'{os.path.relpath(f, ROOT)}:0: E YAML error: {e}'))
    # names and tags declared anywhere in the course count everywhere
    all_tags = collections.defaultdict(set)
    names = set()
    for _, d in loaded:
        for w in d.get('new_words') or []:
            if w.get('name'):
                names.add(vi.nfc(w['w']).replace('_', ' '))
            elif w.get('tag'):
                all_tags[vi.key(w['w'])].add(w['tag'])
    spellings = collections.defaultdict(set)
    seen = {}
    for f, d in loaded:
        if d.get('id') in seen:
            msgs.append(('E', f'{os.path.relpath(f, ROOT)}:0: E id {d.get("id")} already used by {seen[d.get("id")]}'))
        seen[d.get('id')] = os.path.basename(f)
        lint(f, d, keys, tags, all_tags, names, msgs, spellings)
    plan_checks(loaded, msgs)
    # pacing: a smooth growth of lines per lesson (non-review lessons, in order)
    real = sorted((d['id'], len(d.get('dialogue') or []), os.path.basename(f)) for f, d in loaded
                  if not d.get('fixture') and not d.get('review') and isinstance(d.get('id'), int))
    for (a, na, _), (b, nb, fb) in zip(real, real[1:]):
        if nb < na - 1 or nb > na + 2:
            msgs.append(('W', f'{fb}: W {nb} lines after {na} in lesson {a}: lines per lesson should grow smoothly'))
    for f, d in loaded:
        if isinstance(d.get('id'), int) and d['id'] > 0 and not d.get('fixture') and bool(d.get('review')) != (d['id'] % 7 == 0):
            msgs.append(('W', f'{os.path.basename(f)}: W review lessons are every 7th (7, 14, …)'))
    res = lexicon.validate(D.con, LEX)
    for r, kind, msg in res:
        if kind not in lexicon.overrides(r):
            msgs.append(('E', f'course/lexicon.tsv:{r["n"]}: E {r["key"]}: {kind}: {msg} (resolve it, or override it '
                              'with a reason: tools/lexicon.py)'))
    print(f'lint: course lexicon: {len(LEX)} rows, {len(res)} conflicts with the data, '
          f'{sum(1 for r, k, _ in res if k in lexicon.overrides(r))} overridden with a reason')
    errors = 0
    for level, text in msgs:
        print(text)
        errors += level == 'E'
    print(f'{len(files)} file(s), {errors} error(s)')
    sys.exit(1 if errors else 0)


def check_wordlist(path):
    """`lint.py --wordlist FILE`: the 11-column format, every word in the database in its house spelling, every tag
    resolvable. Returns the exit code."""
    global D
    D = DB_(DB)
    keys, tags = load_db()
    try:
        rows = course.wordlist(path)
    except (OSError, ValueError) as e:
        print(f'E {e}')
        return 1
    errors = 0
    n_lessons = len(course.syllabus().get('lessons') or []) or 100
    seen = {}
    for r in rows:
        where = f'{path}:{r["line"]}'
        try:
            n = int(r['lesson'])
        except (TypeError, ValueError):
            n = None
        if n is None or not 1 <= n <= n_lessons:
            print(f'{where}: E lesson {r["lesson"]!r} is not a lesson of the syllabus (1-{n_lessons})')
            errors += 1
        if r['word'] in seen:
            print(f'{where}: E "{r["word"]}" is listed twice (line {seen[r["word"]]})')
            errors += 1
        seen.setdefault(r['word'], r['line'])
        if r['type'] == 'name':
            continue
        base, _, tag = vi.nfc(r['word']).partition('~')
        k = vi.key(base.replace('_', ' '))
        if D.spelling.get(k, k) != k:
            print(f'{where}: E "{base}": write the house spelling "{D.spelling[k]}"')
            errors += 1
            k = D.spelling[k]
        if k not in keys:
            print(f'{where}: E "{base}" is in no dictionary')
            errors += 1
        elif tag and tag not in tags.get(k, set()) and vi.card_id(k, tag) not in LEX_CID and not D.sense_tag(k, tag):
            print(f'{where}: E "{r["word"]}": tag ~{tag} names no lexicon row, entry, part of speech or single sense')
            errors += 1
        elif not tag and untagged(k):
            print(f'{where}: E "{base}": {untagged(k)}')
            errors += 1
    print(f'{path}: {len(rows)} rows, {errors} error(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    main()
