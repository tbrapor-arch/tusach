"""The numbers of docs/STATE.md, printed from the build so that they cannot drift (review 3, finding 8: the
top-1000 Hán-Việt analyses, opaque and false-friend counts had drifted from the tools' output).

    python3 -I tools/state.py            # print the numbers
    python3 -I tools/state.py --write    # rewrite the block between <!-- state:numbers --> and <!-- /state --> in
                                         # docs/STATE.md
    python3 -I tools/state.py --check    # exit 1 when that block is not what --write would write (`make test`)

Every number comes from one function of the pipeline: the cards (tools/cards.py lookup) of the most frequent keys,
the course lexicon (tools/lexicon.py), the golden file, the word list and plan (tools/plan.py), the sound rules
(tools/bridge_rules.py) and the database's Taigi layer notes.
"""
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import cards  # noqa: E402
import lexicon  # noqa: E402

STATE = os.path.join(ROOT, 'docs/STATE.md')


def top_keys(con, n):
    out, seen = [], set()
    for (k,) in con.execute("SELECT e.key FROM entry e JOIN source s ON s.id = e.source WHERE s.fixture = 0 AND "
                            "e.freq_rank IS NOT NULL GROUP BY e.key ORDER BY min(e.freq_rank)"):
        k = cards.canon(k)
        if k not in seen:
            seen.add(k)
            out.append(k)
        if len(out) >= n:
            break
    return out


def numbers(con):
    cards.init(con)
    rows = lexicon.load()
    conf = collections.Counter(r['conf'] for r in rows)
    ex = sum(1 for r in rows if r.get('example'))
    ov = sum(1 for r in rows if r['override'])
    gold = sum(1 for line in open(os.path.join(ROOT, 'tests/golden/cards.tsv'), encoding='utf-8')
               if line.strip() and not line.startswith('#') and not line.startswith('id\t'))
    labels = collections.Counter()
    hv = {}
    keys = top_keys(con, 5000)
    for i, k in enumerate(keys):
        c = cards.dictionary.get(cards.lookup(k)) or {}
        if i < 1000:
            labels[c.get('label') or 'unknown'] += 1
        for size in (1000, 3000, 5000):
            if i < size and c.get('chars'):
                hv[size] = hv.get(size, 0) + 1
    lab = ', '.join(f'{k} {labels[k]}' for k in ('same', 'gram', 'hv-vn', 'doubtful', 'opaque', 'older-loan', 'loan',
                                                 'native', 'compound', 'false-friend', 'unknown') if labels[k])
    coll = con.execute("SELECT count(DISTINCT chars) FROM chinese WHERE lang='nan' AND level='char' AND "
                       "note='colloquial'").fetchone()[0]
    import plan
    syl, wl, _ = plan.load()
    import bridge_rules
    groups, ms, data = bridge_rules.render(con)
    return [f'Course lexicon: {len(rows)} rows (doubt {conf["doubt"]}, likely {conf["likely"]}, sure {conf["sure"]}; '
            f'{ov} with an override; {ex} with an example written by Claude); golden cards: {gold}.',
            f'Top 1,000 cards, labels: {lab}.',
            f'Cards showing chữ Hán (Hán-Việt analysis) among the top 1,000 / 3,000 / 5,000: {hv.get(1000, 0)} / '
            f'{hv.get(3000, 0)} / {hv.get(5000, 0)}.',
            f'Taigi: {coll} characters with a reading found colloquial (coda class or 麻 rhyme).',
            plan.list_counts(wl) if wl else 'No draft word list.',
            'Sound rules: ' + groups['summary']]


def block(con):
    return '\n'.join(f'- {x}' for x in numbers(con))


def main():
    con = cards.open_db('public')
    b = block(con)
    if '--write' in sys.argv or '--check' in sys.argv:
        text = open(STATE, encoding='utf-8').read()
        new = re.sub(r'<!-- state:numbers -->.*?<!-- /state -->', lambda m: f'<!-- state:numbers -->\n{b}\n<!-- /state -->',
                     text, flags=re.S)
        if '--write' in sys.argv:
            open(STATE, 'w', encoding='utf-8').write(new)
            print(f'{STATE}: numbers {"rewritten" if new != text else "unchanged"}')
            return 0
        if new != text:
            print('E docs/STATE.md: its numbers are not the build\'s: tools/state.py --write')
            return 1
        print('docs/STATE.md: numbers agree with the build')
        return 0
    print(b)
    return 0


if __name__ == '__main__':
    sys.exit(main())
