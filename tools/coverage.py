"""Coverage of the frequent vocabulary: by the dictionary (English, Hán-Việt analysis, Chinese readings) and by the
lessons.

  python3 -I tools/coverage.py [TOP]      # TOP: size of the frequent-word list measured (default 3000)

"Most frequent": the TOP dictionary words (distinct keys of the Wiktionary headwords, names included) with the best
entry.freq_rank, i.e. the frequency estimated by tools/freq.py (syllable frequencies divided among the dictionary words
by a segmented corpus; meta.freq_method says which data the build had). The test fixture is not counted.
For each word: English = an entry of the key has an English gloss; Hán-Việt analysis = an entry has chữ Hán
(Wiktionary vi-etym-sino); Chinese readings = the bridge row of its characters (tools/bridge.py): Cantonese, Taigi,
Mandarin each present as a whole word or built character by character (the best of the key's spellings counts).
"""
import os
import sqlite3
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import course  # noqa: E402
import vi  # noqa: E402

TOP = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
con = sqlite3.connect(os.environ.get('TUSACH_DB') or os.path.join(os.path.dirname(HERE), 'data/build/vi.db'))
meta = dict(con.execute('SELECT key, value FROM meta'))
print(f"database: sources {meta.get('sources') or 'none'}; not fetched: {meta.get('missing') or 'none'}")
print(f"frequency: {meta.get('freq_method') or 'none'}")
rows = con.execute('''
  SELECT e.key, min(e.freq_rank), max(e.english != ''), max(e.chars != ''), group_concat(DISTINCT e.origin),
         max(coalesce(b.n, -1)), group_concat(DISTINCT e.hv_check), group_concat(DISTINCT CASE WHEN length(b.chars) > 1 THEN b.yue_by || b.nan_by || b.cmn_by END)
  FROM entry e JOIN source s ON s.id = e.source LEFT JOIN bridge b ON b.chars = e.chars AND e.chars != ''
  WHERE s.fixture = 0 AND e.freq_rank IS NOT NULL GROUP BY e.key ORDER BY min(e.freq_rank) LIMIT ?''', (TOP,)).fetchall()
if not rows:
    sys.exit(f"coverage: no ranked dictionary word (Wiktionary {'not fetched' if 'wiktionary' in (meta.get('missing') or '') else 'has no frequency'}): "
             'the coverage of the frequent words cannot be measured on this build (only the test fixture is there)')

n = len(rows)
en = sum(r[2] for r in rows)
hv = [r for r in rows if r[3]]
by_n = Counter(r[5] for r in hv)
built = sum(1 for r in hv if r[7] and 'char' in r[7])
pct = lambda a, b: f'{a} ({100 * a / max(1, b):.1f} %)'  # noqa: E731
print(f'\nThe {n} most frequent dictionary words:')
print(f'  with an English gloss:            {pct(en, n)}')
print(f'  with a Hán-Việt analysis (chữ Hán): {pct(len(hv), n)}')
print(f'  of these, Chinese readings present: all three {pct(by_n[3], len(hv))}, two {pct(by_n[2], len(hv))}, '
      f'one {pct(by_n[1], len(hv))}, none {pct(by_n[0], len(hv))}')
print(f'  of these, words with at least one language built character by character: {built}')
chk = Counter(c for r in hv for c in (r[6] or '').split(',') if c)
print(f"  Hán-Việt check of the syllables against the characters: {dict(chk)}")
org = Counter((r[4] or '').split(',')[0] or 'unknown' for r in rows)
print(f'  origin (Wiktionary etymology): {dict(org)}')
for top in (100, 300, 1000):
    part = rows[:top]
    print(f'  top {top:>4}: Hán-Việt {sum(1 for r in part if r[3])}, all three readings '
          f'{sum(1 for r in part if r[3] and r[5] == 3)}, English {sum(r[2] for r in part)}')

# the lessons
seen = set()
for d in course.lessons():
    if d.get('fixture'):
        continue
    texts = [ln.get('vi') or '' for ln in d.get('dialogue') or []]
    texts += [(it.get('vi') or '').replace('___', str(it.get('answer', ''))) for items in (d.get('exercises') or {}).values()
              for it in items or []]
    for t in texts:
        seen.update(w[2] for w in vi.words(t) if w[0] == 'w')
print(f'\nLessons: {len(seen)} distinct words used')
for top in (100, 300, 1000, 3000):
    part = rows[:top]
    got = sum(1 for r in part if r[0] in seen)
    print(f'  top {top:>4}: {got}/{len(part)} used')
