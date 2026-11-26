"""Regenerate the database columns of an 11-column word list (course/proposal/wordlist-2.tsv; tools/course.py
WORDLIST_COLS) from the word cards (tools/cards.py: the one word pipeline), keeping its words, lessons and the
human part of each note.

    python3 -I tools/wordlist.py course/proposal/wordlist-2.tsv            # rewrite the file in place
    python3 -I tools/wordlist.py course/proposal/wordlist-2.tsv --check    # say which rows would change, write nothing
    python3 -I tools/wordlist.py course/proposal/wordlist-2.tsv --to-check course/proposal/wordlist-2-to-check.md
        # write the to-check list: the course lexicon's doubts and overrides, with the lesson that teaches each word;
        # a hand-written section from the heading "## For a native speaker" on is kept

Columns written: english (the card's English, cut at 90 characters), freq_rank (the card's rank; none for a person's
name), type (the card label in words: Hán-Việt, Hán-Việt formed in Vietnamese, Hán-Việt (opaque), Hán-Việt
(doubtful), older Chinese loan, older Chinese loan (doubtful), loan, native, compound, unknown, name), characters, han_viet, cantonese,
taigi_literary, mandarin (the bridge row; for an older Chinese loan, those of its etymon; for a compound formed in
Vietnamese, each character's readings marked "per character"). The note keeps what a person wrote; the part in
[db: …] is rewritten (origin evidence, doubt, Taigi colloquial reading, older-loan etymon).
    python3 -I tools/wordlist.py --from-lessons 29 35 course/proposal/wordlist-4.tsv [--table OUT.md]
        # words chosen while writing (26 Nov 2026): the word list of lessons 29-35 FROM their new_words (english = the
        # lesson's, which the card shows; the other columns as above; names left out, as in word list 3), and the
        # owner's approval table (lesson, word, English, type; names included), by default beside the list as
        # wordlist-4-approval.md. Then: draft.word_list in course/syllabus.yaml, tools/plan.py --write, make lint;
        # the owner approves the table: add the list to approved.word_list.file (date), tools/test_golden.py --write.

A person's name (type name, or a note starting "(name) Name") is looked up as the name entry (`lan~name`). A word
with several senses is written with its sense tag (`từ~from`: course/lexicon.tsv; `make lint` refuses it untagged).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cards  # noqa: E402
import course  # noqa: E402
import vi  # noqa: E402

TYPE = {'same': 'Hán-Việt', 'gram': 'Hán-Việt (same morpheme, grammatical use)', 'hv-vn': 'Hán-Việt formed in Vietnamese', 'opaque': 'Hán-Việt (opaque)',
        'doubtful': 'Hán-Việt (doubtful)', 'older-loan': 'older Chinese loan', 'loan': 'loan', 'native': 'native',
        'compound': 'compound', 'false-friend': 'Hán-Việt (false friend)', '': 'unknown'}


def short(en, n=90):
    return en if len(en) <= n else en[:n].rsplit(' ', 1)[0] + ' …'


STALE = re.compile(r'[Dd]atabase|to-check|[Cc]ard shows|[Tt]he Taigi column')


def human_note(note):
    """The part of a note a person wrote: without the [db: …] part and without the sentences that described the
    database as it was when the note was drafted ("Database has bận as a verb only …", "see to-check"): those facts
    are now in [db: …]."""
    note = re.sub(r'\s*\[db:.*\Z', '', note, flags=re.S)   # the [db: …] part ends the note; it may hold brackets
    note = re.sub(r'\s*Taigi colloquial/everyday: [^.]*\.', '', note)
    note = re.sub(r'^\(name\)\s*', '', note).strip()
    parts = re.split(r'(?<=[.;])\s+(?=[A-Z"(])', note)
    return ' '.join(x for x in parts if not STALE.search(x)).strip()


def row_for(r):
    """The new row (dict) for one word-list row."""
    word = vi.nfc(r['word'])
    base, _, tag = word.partition('~')
    person = r['type'] == 'name' or r['note'].startswith('(name) Name')
    k = cards.canon(vi.key(base.replace('_', ' ')))
    cid = cards.lookup(k, 'name' if person and not tag else (tag or None))
    c = cards.dictionary.get(cid) if cid else None
    lx = cards.LEX_CID.get('name:' + base.replace('_', ' ')) if person else None
    if lx:                      # a name of the course lexicon (Lan 蘭): its English and characters
        c = {'en': lx['en'], 'en_src': 'lexicon', 'conf': lx['conf'], 'label': '', **(
            {'chars': lx['chars'], **cards._bridge(lx['chars'])} if lx['chars'] else {})}
    out = dict(r)
    note = human_note(r['note'])
    db = []
    if not c:
        out.update(english='', freq_rank='', characters='', han_viet='', cantonese='', taigi_literary='', mandarin='')
        out['type'] = 'name' if person else 'not in the database'
    else:
        out['english'] = short(c.get('en', ''))
        out['freq_rank'] = '' if person else str(c.get('rank', ''))
        out['type'] = 'name' if person else TYPE.get(c.get('label', ''), c.get('label', ''))
        if c.get('label') == 'doubtful' and c.get('etymon'):     # a doubtful older loan is not Hán-Việt (decision 5)
            out['type'] = 'older Chinese loan (doubtful)'
        out['characters'] = c.get('chars', '')
        hv = yue = nan = cmn = ''
        if c.get('per_char'):
            hv = ' · '.join(f"{p['c']} {p.get('hv', '')}" for p in c['per_char'])
            yue, nan, cmn = (' · '.join(f"{p['c']} {p.get(x) or '—'}" for p in c['per_char']) + ' (per character)'
                             for x in ('yue', 'nan', 'cmn'))
        elif c.get('chars'):
            hv, yue, nan, cmn = c.get('hv', ''), c.get('yue', ''), c.get('nan', ''), c.get('cmn', '')
        out.update(han_viet=hv, cantonese=yue, taigi_literary=nan, mandarin=cmn)
        if c.get('nan_coll'):
            db.append(('Taigi colloquial only' if c.get('nan_flag') else 'Taigi colloquial/everyday')
                      + f": {c['nan_coll']}")
        if c.get('etymon'):
            e = c['etymon']
            db.append(f"older loan of {e['chars']} ({e.get('hv', '')}); yue {e.get('yue') or '—'}, nan "
                      f"{e.get('nan') or '—'}, cmn {e.get('cmn') or '—'}")
        if c.get('origin') and not c.get('etymon'):
            db.append(f"origin {c['origin']}")
        if c.get('doubt'):
            db.append(f"{c.get('label', 'doubt')}: {c['doubt']}")
    if c and c.get('en_src') == 'lexicon':
        db.insert(0, f"course lexicon (Claude, not native-checked), confidence {c.get('conf', '')}"
                  + (f"; false friend: {c['ff']}" if c.get('ff') else ''))
    if person:
        note = '(name) ' + note
    out['note'] = note + (f" [db: {'; '.join(db)}]" if db else '')
    return out


def to_check(list_path, out_path):
    """The to-check list of a word list: the course lexicon's rows with confidence doubt and its overrides."""
    import lexicon
    rows = lexicon.load()
    wl = {}                     # the lesson that teaches each word, in every list of the plan and this one
    for p in course.plan_word_lists() + [list_path]:
        if os.path.exists(p if os.path.isabs(p) else os.path.join(os.path.dirname(HERE), p)):
            for r in course.wordlist(p):
                wl.setdefault(r['word'].replace('_', ' '), r['lesson'])

    def lesson(r):
        for k in (r['key'], r['key'].split('~')[0]):
            if k in wl:
                return f'L{wl[k]}'
        return '—'
    doubt = [r for r in rows if r['conf'] == 'doubt']
    ov = [r for r in rows if r['override']]
    name = os.path.basename(list_path)
    out = [f'# {name}: what to check first', '',
           'Generated by `tools/wordlist.py --to-check` from `course/lexicon.tsv` (Claude\'s course lexicon, NOT checked by a',
           'native speaker): its rows with confidence **doubt** and its rows that keep a conflict with the data on purpose',
           '(**override**), each with the reason. The other rows of the list come from lexicon rows marked sure or likely;',
           'they too need a native speaker\'s reading, but these come first. Column "list": the lesson that teaches the',
           'word (— when only the lexicon has it).', '',
           f'## Doubt ({len(doubt)})', '', '| word | list | English | origin | doubt |', '|---|---|---|---|---|']
    for r in doubt:
        why = r['confidence'].split(':', 1)[1].strip() if ':' in r['confidence'] else ''
        o = r['origin'] + (' ' + (r['chars'] or r['etymon']) if (r['chars'] or r['etymon']) else '')
        out.append(f"| {r['key']} | {lesson(r)} | {r['en']} | {o} | {why} |")
    out += ['', f'## Override ({len(ov)})', '', '| word | list | conflict kept | reason |', '|---|---|---|---|']
    for r in ov:
        for k, why in lexicon.overrides(r).items():
            out.append(f"| {r['key']} | {lesson(r)} | {k} | {why} |")
    hand = ''                   # the hand-written part (from HAND on) survives regeneration
    if os.path.exists(out_path):
        old = open(out_path, encoding='utf-8').read()
        if HAND in old:
            hand = '\n' + old[old.index(HAND):].rstrip('\n') + '\n'
    open(out_path, 'w', encoding='utf-8').write('\n'.join(out) + '\n' + hand)
    print(f'{out_path}: {len(doubt)} doubts, {len(ov)} overrides' + (', hand-written section kept' if hand else ''))


HAND = '## For a native speaker'


def from_lessons(a, b, out_path, table_path=None):
    """The word list of lessons a-b generated from their new_words, and the owner's approval table."""
    ls = [L for L in course.lessons() if not L.get('fixture') and isinstance(L.get('id'), int) and a <= L['id'] <= b]
    cards.init(cards.open_db('public'), cards.course_words(course.lessons()))
    rows, table = [], []
    for L in ls:
        for w in L.get('new_words') or []:
            if not w.get('w'):
                continue
            word = vi.nfc(w['w']) + (f"~{w['tag']}" if w.get('tag') and not w.get('name') else '')
            if w.get('name'):
                table.append(f"| {L['id']} | {word.replace('_', ' ')} | {w.get('en', '')} | name |")
                continue
            r = row_for({'lesson': str(L['id']), 'word': word, 'type': '', 'note': '', 'line': 0,
                         **{c: '' for c in course.WORDLIST_COLS if c not in ('lesson', 'word', 'type', 'note')}})
            r['english'] = short(w.get('en') or r['english'])
            r['note'] = r['note'].strip()
            rows.append(r)
            table.append(f"| {L['id']} | {word.replace('_', ' ')} | {w.get('en', '')} | {r['type']} |")
    lines = ['\t'.join(course.WORDLIST_COLS)] + ['\t'.join(str(r[x]).replace('\t', ' ') for x in course.WORDLIST_COLS)
                                                 for r in rows]
    open(out_path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    table_path = table_path or re.sub(r'\.tsv$', '', out_path) + '-approval.md'
    name = os.path.basename(out_path)
    head = [f'# {name}: the words of lessons {a}–{b}, for the owner\'s approval', '',
            f'Generated by `tools/wordlist.py --from-lessons {a} {b}` from the lessons\' `new_words` (chosen while writing;',
            'Claude\'s, NOT checked by a native speaker). English: as the card shows it. To approve: add the list to',
            '`approved.word_list.file` in course/syllabus.yaml with the date.', '',
            '| L | word | English | type |', '|---|---|---|---|']
    open(table_path, 'w', encoding='utf-8').write('\n'.join(head + table) + '\n')
    print(f'{out_path}: {len(rows)} words of lessons {a}-{b}; approval table {table_path} ({len(table)} lines)')
    return rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--from-lessons' in sys.argv:
        table = sys.argv[sys.argv.index('--table') + 1] if '--table' in sys.argv else None
        args = [x for x in args if x != table]
        if len(args) != 3:
            sys.exit(__doc__)
        from_lessons(int(args[0]), int(args[1]), args[2], table)
        return
    if '--to-check' in sys.argv:
        return to_check(args[0], sys.argv[sys.argv.index('--to-check') + 1])
    if len(args) != 1:
        sys.exit(__doc__)
    path = args[0]
    cards.init(cards.open_db('public'))
    rows = course.wordlist(path)
    new = [row_for(r) for r in rows]
    changed = sum(1 for a, b in zip(rows, new) if any(a[x] != b[x] for x in course.WORDLIST_COLS))
    if '--check' in sys.argv:
        print(f'{path}: {changed} of {len(rows)} rows would change')
        return
    lines = ['\t'.join(course.WORDLIST_COLS)] + ['\t'.join(r[x].replace('\t', ' ') for x in course.WORDLIST_COLS)
                                                 for r in new]
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(f'{path}: {changed} of {len(rows)} rows rewritten from the cards')


if __name__ == '__main__':
    main()
