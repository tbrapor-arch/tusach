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
SIZES = sorted({1000, TOP, 5000})
BANDS = ((1, 500), (501, 1000), (1001, 2000), (2001, 3000), (3001, 5000))
LIST = 30
con = sqlite3.connect(os.environ.get('TUSACH_DB') or os.path.join(os.path.dirname(HERE), 'data/build/vi.db'))
meta = dict(con.execute('SELECT key, value FROM meta'))
print(f"database: sources {meta.get('sources') or 'none'}; not fetched: {meta.get('missing') or 'none'}")
print(f"frequency: {meta.get('freq_method') or 'none'}")
# one row per ranked key: (key, rank, has English, origins, is a name, chữ Hán shown on its card). The characters are
# the card's own (tools/cards.py: its main etymology), so the measurement and the card agree: a homograph whose main
# sense is native (tốt "good", khi "when") does not count by its rarer Sino-Vietnamese twin (卒 "pawn", 欺 "to slight").
import cards  # noqa: E402
cards.init(con)
rows = []
for k, rank, en, org, name in con.execute('''
  SELECT e.key, min(e.freq_rank), max(e.english != ''), group_concat(DISTINCT e.origin), max(e.pos = 'name')
  FROM entry e JOIN source s ON s.id = e.source
  WHERE s.fixture = 0 AND e.freq_rank IS NOT NULL GROUP BY e.key ORDER BY min(e.freq_rank) LIMIT ?''',
                                          (max(SIZES),)).fetchall():
    card = cards.dictionary.get(cards.lookup(k)) or {}
    rows.append((k, rank, en, org, name, card.get('chars', '')))
if not rows:
    sys.exit(f"coverage: no ranked dictionary word (Wiktionary {'not fetched' if 'wiktionary' in (meta.get('missing') or '') else 'has no frequency'}): "
             'the coverage of the frequent words cannot be measured on this build (only the test fixture is there)')
B = {r[0]: r[1:] for r in con.execute('SELECT chars, hv, yue, yue_by, nan, nan_by, cmn, cmn_by, n, nan_coll FROM bridge')}
pct = lambda a, b: f'{a} ({100 * a / max(1, b):.1f} %)'  # noqa: E731
print('''
"Most frequent" = the dictionary's own words (distinct Wiktionary keys, names included; hyphenated spellings counted
once) ranked by entry.freq_rank (tools/freq.py: wordfreq's syllable counts divided among the words by a Tatoeba +
Wiktionary-examples corpus cut by vi.cut()). Known bias: only words Wiktionary lists can rank (every one has English
by construction); wordfreq leans to Wikipedia/web text (administrative words, names) and to English leaking into it
(the, in); the corpus is small and translated (tiếng Pháp ranks high). "Hán-Việt analysis" = chữ Hán shown on the card
(Wiktionary vi-etym-sino matching the syllables); a borrowing read the non-Hán-Việt way (giấy 紙) is not one.''')


def table(part):
    n = len(part)
    hv = [r for r in part if r[5]]
    br = [B.get(r[5]) for r in hv]
    by_n = Counter(b[7] if b else 0 for b in br)
    multi = [b for r, b in zip(hv, br) if b and len(r[5]) > 1]
    nan = Counter('single character' if len(r[5]) == 1 and b and b[3] else
                  {'word': 'attested as a word', 'char': 'composed by character', '': 'missing'}[b[4] if b else '']
                  for r, b in zip(hv, br))
    yue = Counter(b[2] for b in multi)
    cmn = Counter(b[6] for b in multi)
    print(f'\nThe {n} most frequent words:')
    print(f'  with an English gloss:              {pct(sum(r[2] for r in part), n)}')
    print(f'  names (Wiktionary pos name):        {pct(sum(r[4] for r in part), n)}')
    print(f'  with a Hán-Việt analysis (chữ Hán): {pct(len(hv), n)}')
    print(f'    Chinese readings: all three {pct(by_n[3], len(hv))}, two {pct(by_n[2], len(hv))}, '
          f'one {pct(by_n[1], len(hv))}, none {pct(by_n[0], len(hv))}')
    print(f'    Taigi literary reading: ' + ', '.join(f'{k} {pct(nan[k], len(hv))}' for k in
          ('attested as a word', 'composed by character', 'single character', 'missing')))
    print(f'    words of 2+ characters ({len(multi)}): Cantonese as a word {yue["word"]}, by character {yue["char"]}, '
          f'missing {yue[""]}; Mandarin as a word {cmn["word"]}, by character {cmn["char"]}, missing {cmn[""]}')
    org = Counter((r[3] or '').split(',')[0] or 'unknown' for r in part)
    print(f'  origin (first Wiktionary etymology of the key): {dict(org)}')


for size in SIZES:
    table(rows[:size])

print('\nShare of words with a Hán-Việt analysis by frequency band:')
for lo, hi in BANDS:
    part = rows[lo - 1:hi]
    if part:
        print(f'  {lo:>5}-{hi:<5} {pct(sum(1 for r in part if r[5]), len(part))}')


def row_text(r):
    b = B.get(r[5])
    if not b:
        return f'{r[0]} {r[5]}: no bridge row'
    hv, yue, yb, nan, nb, cmn, cb, n, coll = b
    return (f'{r[0]} {r[5]} | {hv} | yue {yue or "—"} ({yb or "missing"}) | nan {nan or "—"} ({nb or "missing"})'
            + (f' [colloquial {coll}]' if coll else '') + f' | cmn {cmn or "—"} ({cb or "missing"})')


def why_missing(chars, b):
    out = []
    for i, lang in ((1, 'yue'), (3, 'nan'), (5, 'cmn')):
        if b[i]:
            continue
        lack = [c for c in chars if not con.execute("SELECT 1 FROM chinese WHERE chars=? AND lang=? AND level='char'",
                                                     (c, lang)).fetchone()]
        src = {'yue': 'rime-cantonese', 'nan': 'MOE (literary or unmarked)', 'cmn': 'CC-CEDICT (traditional)'}[lang]
        out.append(f'{lang}: {src} lacks the word and ' + (' '.join(lack) if lack else '?'))
    return '; '.join(out)


hv_rows = [r for r in rows if r[5]]
print(f'\nThe {LIST} most frequent words with a Hán-Việt analysis (rank word chars | Hán-Việt | Cantonese | Taigi '
      '| Mandarin; (word) = the source has the whole word, (char) = composed by character):')
for r in hv_rows[:LIST]:
    print(f'  {r[1]:>5} {row_text(r)}')
lacking = [r for r in hv_rows if B.get(r[5]) and B[r[5]][7] < 3]
print(f'\nThe {LIST} most frequent ones lacking a Chinese reading (of {len(lacking)} in the top {max(SIZES)}):')
for r in lacking[:LIST]:
    print(f'  {r[1]:>5} {r[0]} {r[5]}: {why_missing(r[5], B[r[5]])}')

# characters of the frequent Hán-Việt words that no source reads in Hán-Việt (shown "—" on the card, never "?")
sys.path.insert(0, HERE)
import bridge  # noqa: E402
none = sorted({c for r in hv_rows[:TOP] for c in r[5] if not bridge.hv_readings(con, c)})
print(f"\ncharacters with no Hán-Việt reading (top {TOP}): {len(none)}{': ' + ' '.join(none) if none else ''}")

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
