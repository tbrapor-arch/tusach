"""The cutter test: tools/vi.py cut() and underthesea against the hand-cut reference (tests/cutter/reference.tsv).
A report, not a gate (`make test` prints it; it never fails the build). The reference is NOT checked by a native
speaker (see its header).

  python3 -I tools/cutter_test.py [--known db|viet74k] [--max 15]

--known db (default): vi.cut() with every key of data/build/vi.db (what tools/cards.py tokenize_text() uses).
--known viet74k: vi.cut() with underthesea's bundled word list Viet74K.txt instead, a stand-in when the database has
  no real dictionary (Wiktionary not fetched); test use only, nothing published.

Scores: word boundaries compared as syllable spans (a word is right only if it starts and ends where the reference
word does); precision, recall and F1 over all words of the 200 sentences. Then the spans where vi.cut() and
underthesea disagree, most frequent first, with which one the reference agrees with.
"""
import os
import re
import sqlite3
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import vi  # noqa: E402

REF = os.path.join(ROOT, 'tests/cutter/reference.tsv')


def load_reference(path=REF):
    out = []
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        n, cut = line.rstrip('\n').split('\t')
        out.append((int(n), vi.nfc(cut)))
    return out


def words_of_line(line):
    """[[syllable, …], …] for a line with underscores inside words (numbers and punctuation dropped)."""
    return [vi.key(t[1]).split() for t in vi.words(line) if t[0] == 'w']


def words_of_tokens(tokens):
    """The same from a list of tokens (underthesea): pieces with no letter are dropped, punctuation stripped."""
    out = []
    for t in tokens:
        syls = [vi.strip_punct(s)[1].lower() for s in vi.nfc(t).split()]
        syls = [s for s in syls if s and any(c.isalpha() for c in s)]
        if syls and not re.fullmatch(r'[0-9.,:%]+', ''.join(syls)):
            out.append(syls)
    return out


def spans(words):
    out, i = set(), 0
    for w in words:
        out.add((i, i + len(w)))
        i += len(w)
    return out


def score(pairs):
    """pairs: [(reference words, system words)] -> (precision, recall, F1, sentences compared, sentences skipped)."""
    tp = fp = fn = skipped = 0
    for ref, sys_ in pairs:
        if [s for w in ref for s in w] != [s for w in sys_ for s in w]:
            skipped += 1             # the two disagree on the syllables themselves (punctuation, numbers): not compared
            continue
        r, s = spans(ref), spans(sys_)
        tp += len(r & s)
        fp += len(s - r)
        fn += len(r - s)
    p = tp / max(1, tp + fp)
    r = tp / max(1, tp + fn)
    return p, r, 2 * p * r / max(1e-9, p + r), len(pairs) - skipped, skipped


def known_words(kind):
    if kind == 'viet74k':
        try:
            import underthesea
        except ImportError:
            sys.exit('cutter test: underthesea not installed (requirements-build.txt): no Viet74K word list')
        p = os.path.join(os.path.dirname(underthesea.__file__), 'corpus', 'data', 'Viet74K.txt')
        return {vi.key(x) for x in open(p, encoding='utf-8') if x.strip()}, "underthesea's Viet74K.txt word list"
    db = os.environ.get('TUSACH_DB') or os.path.join(ROOT, 'data/build/vi.db')
    con = sqlite3.connect(db)
    meta = dict(con.execute('SELECT key, value FROM meta'))
    k = {r[0] for r in con.execute('SELECT DISTINCT key FROM entry')}
    return k, f"{os.path.relpath(db, ROOT)} ({len(k)} keys; sources: {meta.get('sources') or 'none'}" + (
        f"; NOT FETCHED: {meta['missing']})" if meta.get('missing') else ')')


def disagreements(ref, a, b):
    """The stretches of syllables that cutters a and b cut differently, each as (a's cut, b's cut, kind, which one the
    reference sides with: a | b | neither). kind: 'a joins more' (fewer words in a), 'b joins more', 'crossing'."""
    out = []
    for r, x, y in zip(ref, a, b):
        flat = [s for w in r for s in w]
        if flat != [s for w in x for s in w] or flat != [s for w in y for s in w]:
            continue
        sr, sx, sy = spans(r), spans(x), spans(y)
        diff = sorted(sx ^ sy)
        regions = []
        for lo, hi in diff:                       # overlapping differing words form one stretch
            if regions and lo < regions[-1][1]:
                regions[-1][1] = max(regions[-1][1], hi)
            else:
                regions.append([lo, hi])
        for lo, hi in regions:
            def cut(sp):
                return [w for w in sorted(sp) if lo <= w[0] and w[1] <= hi]
            ca, cb, cr = cut(sx), cut(sy), cut(sr)
            text = lambda ws: ' | '.join(' '.join(flat[w[0]:w[1]]) for w in ws)  # noqa: E731
            kind = 'a joins more' if len(ca) < len(cb) else 'b joins more' if len(cb) < len(ca) else 'crossing'
            who = 'a' if ca == cr else 'b' if cb == cr else 'neither'
            out.append((text(ca), text(cb), kind, who))
    return out


def main():
    kind = sys.argv[sys.argv.index('--known') + 1] if '--known' in sys.argv else 'db'
    limit = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 15
    ref = load_reference()
    print(f'cutter test: {len(ref)} reference sentences (tests/cutter/reference.tsv), written and cut by Claude by '
          'docs/SEGMENTATION.md, NOT checked by a native speaker: the scores measure agreement with one non-native '
          "model's judgement")
    raw = [c.replace('_', ' ') for _, c in ref]
    ref_w = [words_of_line(c) for _, c in ref]
    known, kdesc = known_words(kind)
    cut_w = [words_of_line(vi.cut(t, known)) for t in raw]
    p, r, f, n, sk = score(list(zip(ref_w, cut_w)))
    print(f'  vi.cut() with {kdesc}:\n    precision {p:.3f}  recall {r:.3f}  F1 {f:.3f}  ({n} sentences, {sk} skipped)')
    try:
        from underthesea import word_tokenize
        import underthesea
    except ImportError:
        print('  underthesea not installed (requirements-build.txt): not compared')
        return
    ut_w = [words_of_tokens(word_tokenize(t)) for t in raw]
    p, r, f, n, sk = score(list(zip(ref_w, ut_w)))
    print(f'  underthesea {underthesea.__version__} word_tokenize:\n    precision {p:.3f}  recall {r:.3f}  F1 {f:.3f}  '
          f'({n} sentences, {sk} skipped)')
    d = disagreements(ref_w, cut_w, ut_w)
    who = Counter(x[3] for x in d)
    print(f'  stretches cut differently by vi.cut() and underthesea: {len(d)}; the reference sides with vi.cut() {who["a"]}, '
          f'with underthesea {who["b"]}, with neither {who["neither"]}')
    names = {'a joins more': 'vi.cut() joins more', 'b joins more': 'underthesea joins more', 'crossing': 'crossing'}
    print('  kinds: ' + ', '.join(f'{names[k]} {v}' for k, v in Counter(x[2] for x in d).most_common()))
    print('  most frequent (vi.cut() -> underthesea [reference sides with]):')
    for (a, b, _, w), c in Counter(d).most_common(limit):
        print(f'    {c:>3}  {a}  ->  {b}  [{dict(a="vi.cut", b="underthesea", neither="neither")[w]}]')


if __name__ == '__main__':
    main()
