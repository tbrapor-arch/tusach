"""Regenerate the database columns of an 11-column word list (course/proposal/wordlist-1.tsv; tools/course.py
WORDLIST_COLS) from the word cards (tools/cards.py: the one word pipeline), keeping its words, lessons and the
human part of each note.

    python3 -I tools/wordlist.py course/proposal/wordlist-1.tsv            # rewrite the file in place
    python3 -I tools/wordlist.py course/proposal/wordlist-1.tsv --check    # say which rows would change, write nothing

Columns written: english (the card's English, cut at 90 characters), freq_rank (the card's rank; none for a person's
name), type (the card label in words: Hán-Việt, Hán-Việt formed in Vietnamese, Hán-Việt (opaque), Hán-Việt
(doubtful), older Chinese loan, loan, native, compound, unknown, name), characters, han_viet, cantonese,
taigi_literary, mandarin (the bridge row; for an older Chinese loan, those of its etymon; for a compound formed in
Vietnamese, each character's readings marked "per character"). The note keeps what a person wrote; the part in
[db: …] is rewritten (origin evidence, doubt, Taigi colloquial reading, older-loan etymon).
A person's name (type name, or a note starting "(name) Name") is looked up as the name entry (`lan~name`). A row
drafted with another sense than the card's main one (từ "from", not 詞 "word") keeps it through a sense tag
(`từ~from`, cards.sense_tag), named in the note so that lessons write it.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cards  # noqa: E402
import course  # noqa: E402
import vi  # noqa: E402

TYPE = {'same': 'Hán-Việt', 'hv-vn': 'Hán-Việt formed in Vietnamese', 'opaque': 'Hán-Việt (opaque)',
        'doubtful': 'Hán-Việt (doubtful)', 'older-loan': 'older Chinese loan', 'loan': 'loan', 'native': 'native',
        'compound': 'compound', 'false-friend': 'Hán-Việt (false friend)', '': 'unknown'}


def short(en, n=90):
    return en if len(en) <= n else en[:n].rsplit(' ', 1)[0] + ' …'


def human_note(note):
    note = re.sub(r'\s*\[db:[^\]]*\]', '', note)
    note = re.sub(r'\s*Taigi colloquial/everyday: [^.]*\.', '', note)
    return re.sub(r'^\(name\)\s*', '', note).strip()


def sense_of(k, english):
    """A sense tag (a part of speech or a word of the English) that names the etymology whose English contains the
    first sense the list was drafted with ("from" for từ, not 詞 "word"), or None when the card's main sense is it."""
    first = english.split(';')[0].replace('…', '').strip().lower()
    if not first:
        return None
    rows = [dict(zip(cards.COLS, x)) for x in cards.con.execute(
        f"SELECT {cards.SQL_COLS} FROM entry e JOIN source s ON s.id = e.source WHERE e.key=?", (k,))]
    groups = cards.senses(rows)
    if not groups or first in (cards._group_en(groups[0]) or '').lower():
        return None
    want = next((g for g in groups if first in (cards._group_en(g) or '').lower()
                 or any(first in (x['english'] or '').lower() for x in g)), None)
    if not want:
        return None
    for t in [w for w in re.findall(r'[a-z]+', first) if len(w) >= 3] + sorted({x['pos'] for x in want}):
        hit = cards.sense_tag(rows, t)
        if hit is not None and hit in want and first in (hit['english'] or '').lower():
            return t
    return None


def row_for(r):
    """The new row (dict) for one word-list row."""
    word = vi.nfc(r['word'])
    base, _, tag = word.partition('~')
    person = r['type'] == 'name' or r['note'].startswith('(name) Name')
    k = cards.canon(vi.key(base.replace('_', ' ')))
    stag = None if tag or person else sense_of(k, r['english'])
    cid = cards.lookup(k, 'name' if person and not tag else (tag or stag))
    c = cards.dictionary.get(cid) if cid else None
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
    if stag:
        db.insert(0, f'sense tag {base}~{stag}')
    if person:
        note = '(name) ' + note
    out['note'] = note + (f" [db: {'; '.join(db)}]" if db else '')
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
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
