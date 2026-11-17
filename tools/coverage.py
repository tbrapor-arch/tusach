"""How much of the frequent vocabulary the lessons already use, and the most frequent words not yet taught.

  python3 -I tools/coverage.py [TOP]      # default TOP=400 for the list of words not yet taught

Needs a frequency source in the database (entry.freq_rank). TODO(sources): none yet, so it says so and stops.
"""
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import course  # noqa: E402
import vi  # noqa: E402

con = sqlite3.connect(os.environ.get('TUSACH_DB') or os.path.join(os.path.dirname(HERE), 'data/build/vi.db'))
ranked = con.execute('SELECT freq_rank, key, word, english, label FROM entry WHERE freq_rank IS NOT NULL '
                     'GROUP BY key ORDER BY min(freq_rank)').fetchall()
if not ranked:
    sys.exit('coverage: no word frequency in the database yet (TODO(sources))')
seen = set()
for d in course.lessons():
    texts = [ln.get('vi') or '' for ln in d.get('dialogue') or []]
    texts += [(it.get('vi') or '').replace('___', str(it.get('answer', ''))) for items in (d.get('exercises') or {}).values()
              for it in items or []]
    for t in texts:
        seen.update(w[2] for w in vi.words(t) if w[0] == 'w')
for top in (100, 300, 1000, 3000):
    part = [r for r in ranked if r[0] <= top]
    got = sum(1 for r in part if r[1] in seen)
    print(f'top {top:>4}: {got}/{len(part)} used ({100 * got // max(1, len(part))}%)')
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 400
print(f'\nMost frequent words not yet in any lesson (top {limit}):')
for r in [r for r in ranked if r[1] not in seen and r[0] <= limit][:40]:
    print(f'  #{r[0]:<5} {r[2]}  {r[3] or ""}  ({r[4] or "?"})')
