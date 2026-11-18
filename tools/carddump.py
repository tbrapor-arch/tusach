"""Dump real word cards through a tree's OWN tools/cards.py and database (used by tools/compare.py run; also by hand).

    python3 -I tools/carddump.py TREE DB OUT.json KEYS.txt

TREE: a source tree (this repository or a git worktree of an older commit); DB: a database built by that tree's
build_db.py; KEYS.txt: one word per line (`từ~from` for a tagged card; underscores or spaces). Writes {word: card
fields or null} with the fields compared (tools/compare.py CARD_FIELDS). Works with older trees whose cards.init()
takes fewer arguments.
"""
import json
import os
import sqlite3
import sys

FIELDS = ('en', 'en_src', 'chars', 'label', 'origin', 'doubt', 'ex', 'other', 'yue', 'nan', 'nan_coll', 'cmn', 'rank',
          'no_main', 'ff', 'per_char', 'etymon')


def main():
    tree, db, out, keys = sys.argv[1:5]
    sys.path.insert(0, os.path.join(os.path.abspath(tree), 'tools'))
    os.chdir(tree)
    import cards
    import vi
    con = sqlite3.connect(db)
    cards.init(con)
    res = {}
    for line in open(keys, encoding='utf-8'):
        w = line.strip()
        if not w:
            continue
        base, _, tag = w.partition('~')
        k = vi.key(base.replace('_', ' '))
        k = cards.canon(k) if hasattr(cards, 'canon') else k
        try:
            cid = cards.lookup(k, tag or None)
        except Exception as e:                       # an older tree that cannot build this card
            res[w] = {'error': str(e)[:200]}
            continue
        c = cards.dictionary.get(cid) if cid else None
        if not c:
            res[w] = None
            continue
        d = {f: c[f] for f in FIELDS if c.get(f) not in (None, '', [], {})}
        if 'ex' in d:
            d['ex'] = {'vi': d['ex'].get('vi', ''), 'en': d['ex'].get('en', '')}
        if 'other' in d:
            d['other'] = [{'en': o.get('en', ''), 'chars': o.get('chars', '')} for o in d['other']]
        if 'per_char' in d:
            d['per_char'] = 1
        res[w] = d
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    print(f'carddump: {len(res)} words, {sum(1 for v in res.values() if v and "error" not in v)} cards -> {out}')


if __name__ == '__main__':
    main()
