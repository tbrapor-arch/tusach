"""The golden check of the word cards (layer 3 of the card design, review 2): `make test` fails when a built card
contradicts tests/golden/cards.tsv, or when the dictionary labels contradict tests/golden/opaque-sample.tsv.

    python3 -I tools/test_golden.py            # check (exit 1 on a contradiction)
    python3 -I tools/test_golden.py --write    # rewrite cards.tsv from the cards built now: READ the diff before
                                               # committing it (git diff tests/golden/cards.tsv): it is a review

tests/golden/cards.tsv (review 3, finding 7): a REVIEWED SNAPSHOT of what the learner sees on the cards of every
course lexicon row (tagged and untagged ids), every word of the draft word list (course/syllabus.yaml draft) and the
300 most frequent words: the English, the label, the characters, the readings in display order (Hán-Việt per
character, Mandarin, Cantonese, Taigi literary and its layer, Taigi colloquial), the older loan's etymon, the
dictionary etymology used, the example text and its source, the usage and false-friend notes. It protects what the
lexicon does NOT state: a change of a dictionary rule, a reading order or an example filter that alters any of these
fails `make test` until the diff is read and the snapshot rewritten (--write). Generated from the cards and read by
Claude (NOT a native speaker).
tests/golden/opaque-sample.tsv: review 2's sample of "opaque" Hán-Việt analyses judged T (transparent) or O; the
dictionary layer's label (no lexicon) is counted: false same (O labelled same/gram) must be 0, false opaque (T
labelled opaque/doubtful) may not exceed the number in the file's `max-false-opaque` line.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cards  # noqa: E402
import lexicon  # noqa: E402
import vi  # noqa: E402

GOLDEN = os.path.join(ROOT, 'tests/golden/cards.tsv')
SAMPLE = os.path.join(ROOT, 'tests/golden/opaque-sample.tsv')
# the readings in the order the learner sees them (cards.DISPLAY_LANGS: Mandarin first, owner 19 Nov 2026); Taigi's
# layer and colloquial reading follow its literary one
COLS = (('id', 'en', 'label', 'chars', 'hv')
        + tuple(x for k, _, _ in cards.DISPLAY_LANGS for x in ((k, 'nan_layer', 'nan_coll') if k == 'nan' else (k,)))
        + ('etymon', 'ety', 'ex', 'ex_src', 'use', 'ff'))
TOP = 300


def ids(con):
    out = []
    for r in lexicon.load():
        if r['pos'] == 'name':
            continue
        for cid in (r['cid'], r['k']):
            if cid not in out:
                out.append(cid)
    import plan
    _, rows, _ = plan.load()
    for r in rows:
        if r['type'] != 'name':
            base, _, tag = vi.nfc(r['word']).partition('~')
            cid = vi.card_id(cards.canon(vi.key(base.replace('_', ' '))), tag or None)
            if cid not in out:
                out.append(cid)
    for (k,) in con.execute("SELECT e.key FROM entry e JOIN source s ON s.id = e.source WHERE s.fixture = 0 AND "
                            "e.freq_rank IS NOT NULL GROUP BY e.key ORDER BY min(e.freq_rank) LIMIT ?", (TOP,)):
        if k not in out:
            out.append(k)
    return out


def row(cid):
    k, _, tag = cid.partition('~')
    got = cards.lookup(k, tag or None)
    c = cards.dictionary.get(got) if got else None
    if not c:
        return dict({x: '' for x in COLS}, id=cid, en='(no card)')
    pc = c.get('per_char')
    per = lambda x: ' · '.join(f"{p['c']} {p.get(x) or '—'}" for p in pc) if pc else c.get(x, '')  # noqa: E731
    et = c.get('etymon') or {}
    ex = c.get('ex') or {}
    out = {'id': cid, 'en': c.get('en', ''), 'label': c.get('label', ''), 'chars': c.get('chars', ''),
           'hv': c.get('hv', '') if not pc else ' · '.join(f"{p['c']} {p.get('hv', '')}" for p in pc),
           'yue': per('yue'), 'nan': per('nan'), 'nan_layer': c.get('nan_layer', '') + (' ' + c['nan_flag'] if
                                                                                    c.get('nan_flag') else ''),
           'nan_coll': per('nan_coll') if pc else c.get('nan_coll', ''), 'cmn': per('cmn'),
           'etymon': ' '.join(x for x in (et.get('chars', ''), et.get('hv', '')) if x), 'ety': c.get('ety', ''),
           'ex': (ex.get('vi', '') + ' / ' + ex.get('en', '')) if ex else '',
           'ex_src': (ex.get('src') or ('fixture' if ex else '')).split(' by ')[0], 'use': c.get('use', ''),
           'ff': c.get('ff', '')}
    return {x: str(v).replace('\t', ' ').replace('\n', ' ') for x, v in out.items()}


def read(path=GOLDEN):
    """The snapshot's rows, by its own header; a header that is not COLS (a changed display order) is an error."""
    out, head = [], None
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        p = line.rstrip('\n').split('\t')
        if p[0] == 'id':
            head = tuple(p)
            if head != COLS:
                raise SystemExit(f'{path}: columns {" ".join(head)} are not the display order {" ".join(COLS)}: '
                                 'tools/test_golden.py --write, then read the diff')
            continue
        out.append(dict(zip(COLS, p + [''] * (len(COLS) - len(p)))))
    return out


def opaque_sample(con):
    """(false opaque, false same, judged, max allowed) on tests/golden/opaque-sample.tsv, dictionary labels."""
    mx, rows = None, []
    for line in open(SAMPLE, encoding='utf-8'):
        m = re.match(r'#\s*max-false-opaque:\s*(\d+)', line)
        if m:
            mx = int(m.group(1))
        if line.startswith('#') or line.startswith('key\t') or not line.strip():
            continue
        rows.append(line.rstrip('\n').split('\t'))
    fo, fs, n, bad = 0, 0, 0, []
    for k, ch, j in rows:
        r = con.execute("SELECT label FROM entry WHERE key=? AND chars=? AND source='wiktionary' AND pos != 'name' "
                        "ORDER BY id LIMIT 1", (vi.key(k), ch)).fetchone()
        if not r:
            continue
        n += 1
        if j == 'T' and r[0] in ('opaque', 'doubtful'):
            fo += 1
            bad.append(f'{k} {ch} (T) is {r[0]}')
        if j == 'O' and r[0] in ('same', 'gram'):
            fs += 1
            bad.append(f'{k} {ch} (O) is {r[0]}')
    return fo, fs, n, mx, bad


def main():
    con = cards.open_db('public')
    cards.init(con)
    want = ids(con)
    if '--write' in sys.argv:
        head = ('# Golden word cards (tools/test_golden.py): generated from the cards on ' + __import__('datetime').date
                .today().isoformat() + ' and reviewed by Claude, NOT checked by a native speaker.\n')
        with open(GOLDEN, 'w', encoding='utf-8') as f:
            f.write(head + '\t'.join(COLS) + '\n')
            for cid in want:
                r = row(cid)
                f.write('\t'.join(r[c].replace('\t', ' ') for c in COLS) + '\n')
        print(f'{GOLDEN}: {len(want)} cards written: read `git diff` before committing')
        return 0
    errors = []
    gold = read()
    have = {g['id'] for g in gold}
    for g in gold:
        r = row(g['id'])
        for c in COLS[1:]:
            if g[c] != r[c]:
                errors.append(f'{g["id"]}: {c} {g[c][:70]!r} -> {r[c][:70]!r}')
    for cid in want:
        if cid not in have:
            errors.append(f'{cid}: a lexicon or top-{TOP} card with no golden row (tools/test_golden.py --write, then '
                          'review)')
    fo, fs, n, mx, bad = opaque_sample(con)
    print(f'golden: {len(gold)} cards checked, {len(errors)} contradiction(s); opaque sample: {n} analyses, '
          f'false opaque {fo} (max {mx}), false same {fs}')
    if fs or (mx is not None and fo > mx):
        errors += bad
    for e in errors[:60]:
        print('  ' + e)
    if len(errors) > 60:
        print(f'  … {len(errors) - 60} more')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
