"""Look up a word in the database by Vietnamese (with or without tones), chữ Hán, or English.

  python3 -I tools/lookup.py học_sinh        # Vietnamese, exact
  python3 -I tools/lookup.py hoc sinh        # without tone marks: every word with these letters
  python3 -I tools/lookup.py 學生            # chữ Hán
  python3 -I tools/lookup.py -e student      # English
  option: --db PATH (default data/build/vi.db)
"""
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vi  # noqa: E402

args = sys.argv[1:]
db = os.path.join(os.path.dirname(HERE), 'data/build/vi.db')
if '--db' in args:
    i = args.index('--db')
    db = args[i + 1]
    del args[i:i + 2]
if not args:
    sys.exit(__doc__)
con = sqlite3.connect(db)
eng = args[0] == '-e'
q = ' '.join(args[1:] if eng else args)
COLS = 'e.id, e.source, e.word, e.english, e.chars, e.label, e.freq_rank'
if eng:
    rows = con.execute(f'SELECT {COLS} FROM entry e WHERE e.english LIKE ? LIMIT 40', (f'%{q}%',)).fetchall()
elif vi.CJK.search(q):
    rows = con.execute(f'SELECT {COLS} FROM entry e WHERE e.chars = ? LIMIT 40', (q,)).fetchall()
else:
    k = vi.key(q)
    rows = con.execute(f'SELECT {COLS} FROM entry e WHERE e.key = ? OR e.toneless = ? ORDER BY e.key = ? DESC LIMIT 40',
                       (k, vi.toneless(k), k)).fetchall()
for eid, src, w, en, chars, label, rank in rows:
    print(f'{w}  {chars or ""}  [{src}{", " + label if label else ""}{f", #{rank}" if rank else ""}]  {en or ""}')
    if chars:
        for lang, r in con.execute('SELECT lang, reading FROM chinese WHERE chars = ?', (chars,)):
            print(f'    {dict(yue="Cantonese", nan="Taigi", cmn="Mandarin")[lang]}: {r}')
    for v, e in con.execute('SELECT vi, en FROM example WHERE entry_id = ? LIMIT 2', (eid,)):
        print(f'    e.g. {v} / {e}')
if not rows:
    print('not found')
