"""Evaluate the Vietnamese Wiktionary extract (kaikki vi-extract.jsonl.gz) against the database, WITHOUT loading it:
its licence was not read on a primary page of vi.wiktionary.org (ATTRIBUTION.md), so nothing of it reaches a
database or a page. Fetch it with TUSACH_FETCH_EVAL=1 sh data/fetch.sh.

    python3 -I tools/eval_viwikt.py [TOP]        # TOP: frequent words measured (default 1000)

Reports, for the TOP most frequent words: how many have a vi.wiktionary entry, English translations (its "Dịch"
tables), an etymology, and among the words whose card origin is unknown, how many vi.wiktionary would class
(Hán-Việt "Âm Hán-Việt của chữ Hán X", older loan "Âm phi Hán-Việt", native "Việt-Mường nguyên thủy", loan
"Từ tiếng Pháp"…), with examples.
"""
import gzip
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cards  # noqa: E402
import vi  # noqa: E402

RULES = [('sino', re.compile(r'Âm Hán[- ]Việt của chữ Hán|[Tt]ừ Hán[- ]Việt')),
         ('nonhv', re.compile(r'Âm phi Hán[- ]Việt|[Hh]án[- ]Việt cổ|tiếng Trung Quốc')),
         ('vietic', re.compile(r'Việt[- ]Mường nguyên thủy|Môn[- ]Khmer|Nam Á nguyên thủy|[Cc]ùng gốc với tiếng Mường')),
         ('loan', re.compile(r'[Tt]ừ tiếng (Pháp|Anh|Khmer|Chăm|Thái|Bồ Đào Nha|Hà Lan|Nga|Nhật)'))]


def main():
    top = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    path = os.path.join(ROOT, 'data', 'raw', 'kaikki', 'vi-extract.jsonl.gz')
    if not os.path.exists(path):
        sys.exit('eval_viwikt: data/raw/kaikki/vi-extract.jsonl.gz missing: TUSACH_FETCH_EVAL=1 sh data/fetch.sh')
    con = cards.open_db('public')
    cards.init(con)
    keys = [k for (k,) in con.execute("SELECT e.key FROM entry e JOIN source s ON s.id = e.source WHERE s.fixture = 0 "
                                      "AND e.freq_rank IS NOT NULL GROUP BY e.key ORDER BY min(e.freq_rank) LIMIT ?",
                                      (top,))]
    want = set(keys)
    ety, tr, has = defaultdict(set), defaultdict(set), set()
    for line in gzip.open(path, 'rt', encoding='utf-8'):
        e = json.loads(line)
        if e.get('lang_code') != 'vi':
            continue
        k = cards.canon(vi.key(e.get('word', '')))
        if k not in want:
            continue
        has.add(k)
        for t in e.get('etymology_texts') or []:
            if t.strip() and not t.startswith('__'):
                ety[k].add(t.replace('__NOEDITSECTION__', '').strip())
        for t in e.get('translations') or []:
            if t.get('lang_code') == 'en' and t.get('word'):
                tr[k].add(t['word'])
    unknown = [k for k in keys if not (cards.dictionary.get(cards.lookup(k)) or {}).get('label')
               and not (cards.dictionary.get(cards.lookup(k)) or {}).get('name')]
    cls = Counter()
    ex = defaultdict(list)
    for k in unknown:
        text = ' '.join(ety.get(k, ()))
        c = next((name for name, rx in RULES if rx.search(text)), 'none' if not text else 'unclassified')
        cls[c] += 1
        if len(ex[c]) < 12:
            ex[c].append(k)
    print(f'vi.wiktionary (kaikki vi-extract), top {top} words: entry {len(has)}, English translations '
          f'{sum(1 for k in keys if tr.get(k))}, etymology text {sum(1 for k in keys if ety.get(k))}')
    print(f'cards with unknown origin: {len(unknown)}; what vi.wiktionary would say: {dict(cls)}')
    for c, ks in ex.items():
        print(f'  {c}: {", ".join(ks)}')
    print('NOT loaded: licence not verified on a primary page (ATTRIBUTION.md).')


if __name__ == '__main__':
    main()
