"""Measure before and after: compare two builds of the page by script, not by eye (handover section 4.6). Run it for any
change to the dictionary (sources, build_db.py), the cutter (tools/vi.py cut) or the word pipeline (tools/cards.py,
english.py), before publishing. For anything risky, a second agent that did not do the work reads the result.

  python3 -I tools/compare.py run [--ref origin/main] [--before-db PATH] [--after-db PATH] [--max 20]
                                  [--top 3000] [--cards-out FILE.tsv]
      builds REF (default: origin/main if it exists, else HEAD) in a temporary git worktree and the working tree, each
      with its OWN database built by its own tools/build_db.py from data/raw (so a change to the database build shows;
      a source the ref's data/fetch.sh leaves PENDING is left out of its build, as it was then), then compares the
      pages AND the real word cards: the --top most frequent words of either database plus every course word (the
      lexicon's card ids, the proposal word lists), each side built by its own tools/cards.py (tools/carddump.py).
      Printed: lost cards, changed English leads, labels, characters, examples, with a summary; --cards-out writes
      every changed card (rank, field, before, after) for reading. --before-db / --after-db use an existing database.
  python3 -I tools/compare.py snapshot [app/dist/index.html] OUT.json
  python3 -I tools/compare.py diff BEFORE.json AFTER.json [--max 20]

What is compared: every lesson line and exercise (the text shown, the cut into words, the card id of each word) and
every card (English and its source, chữ Hán, Hán-Việt readings, Cantonese / Taigi (literary, colloquial) / Mandarin
readings, variant spelling, label, example, the other etymologies of the spelling).
Exit 1 when a line's text changed, a card was lost (a page card, or the card of a course word), or a page card's
English rank went down; other changes are listed.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import english  # noqa: E402

FIELDS = ('en', 'en_src', 'chars', 'hv', 'yue', 'nan', 'nan_coll', 'cmn', 'via', 'label', 'ex', 'other')


def page_data(page):
    s = open(page, encoding='utf-8').read()
    m = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', s, re.S)
    return json.loads(m.group(1))


def snapshot(page):
    d = page_data(page)
    lines = {}
    for L in d['lessons']:
        for ln in L['lines']:
            lines[f"L{L['id']}.{ln['n']}"] = {'text': ln['vi'], 'cut': [[t['w']['t'], t['w']['id']] for t in ln['tokens'] if 'w' in t]}
        for i, e in enumerate(L.get('exercises') or []):
            lines[f"L{L['id']}.ex{i + 1}"] = {'text': e['vi'], 'cut': [[t['w']['t'], t['w']['id']] for t in e.get('tokens') or [] if 'w' in t]}
    cards = {i: {f: c.get(f) for f in FIELDS if c.get(f) is not None} for i, c in d['dict'].items()}
    return {'lines': lines, 'cards': cards}


def diff(a, b, limit=20):
    """Prints the differences; returns the number of blocking ones."""
    out = {}

    def add(cls, item):
        out.setdefault(cls, []).append(item)

    for k in sorted(set(a['lines']) | set(b['lines'])):
        x, y = a['lines'].get(k), b['lines'].get(k)
        if x is None:
            add('line added', f'{k}: {y["text"]}')
        elif y is None:
            add('line removed', f'{k}: {x["text"]}')
        else:
            if x['text'] != y['text']:
                add('LINE TEXT CHANGED', f'{k}: "{x["text"]}" -> "{y["text"]}"')
            if x['cut'] != y['cut']:
                add('cut or card id changed', f'{k}: {" | ".join(w for w, _ in x["cut"])}  ->  {" | ".join(w for w, _ in y["cut"])}'
                    + ('' if [w for w, _ in x['cut']] != [w for w, _ in y['cut']] else
                       '  ids: ' + ', '.join(f'{p}->{q}' for (_, p), (_, q) in zip(x['cut'], y['cut']) if p != q)))
    for i in sorted(set(a['cards']) | set(b['cards'])):
        x, y = a['cards'].get(i), b['cards'].get(i)
        if y is None:
            add('CARD LOST', i)
        elif x is None:
            add('card added', i)
        else:
            if english.rank(y.get('en_src')) < english.rank(x.get('en_src')):
                add('ENGLISH POORER', f'{i}: "{x.get("en")}" ({x.get("en_src")}) -> "{y.get("en")}" ({y.get("en_src")})')
            for f in FIELDS:
                if x.get(f) != y.get(f) and f != 'en_src':
                    add(f'card {f} changed', f'{i}: {json.dumps(x.get(f), ensure_ascii=False)} -> {json.dumps(y.get(f), ensure_ascii=False)}')
    blocking = 0
    for cls in sorted(out, key=lambda c: (not c.isupper(), c)):
        items = out[cls]
        blocking += len(items) if cls.isupper() else 0
        print(f'== {cls}: {len(items)}')
        for it in items[:limit]:
            print('  ' + it)
        if len(items) > limit:
            print(f'  … {len(items) - limit} more')
    print(f"compare: {len(a['lines'])} -> {len(b['lines'])} lines, {len(a['cards'])} -> {len(b['cards'])} cards; "
          f'{sum(len(v) for v in out.values())} difference(s), {blocking} blocking')
    return blocking


def build(src_root, db, out_dir):
    env = dict(os.environ, TUSACH_DB=os.path.abspath(db), TUSACH_OUT=out_dir,
               TUSACH_STORE=os.path.join(out_dir, 'cards.json'))
    import sqlite3
    missing = dict(sqlite3.connect(db).execute('SELECT key, value FROM meta')).get('missing') or ''
    if missing:                  # an older tree built without its PENDING sources: a comparison page, never published
        env['TUSACH_ALLOW_MISSING'] = ','.join(missing.split())
    r = subprocess.run([sys.executable, '-I', os.path.join(src_root, 'tools/build_app.py')], env=env, cwd=src_root,
                       capture_output=True, text=True)
    page = os.path.join(out_dir, 'index.html')
    if not os.path.exists(page):
        sys.exit(f'compare: the build in {src_root} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}')
    if r.returncode:
        print(f'compare: note: the build in {src_root} ended with errors (card check?):\n{r.stdout[-800:]}')
    return page


def db_plan(wt, tmp, before_db=None, after_db=None):
    """[(side, source tree, database path, build it?)]: by default each side builds its own database."""
    return [('before', wt, before_db or os.path.join(tmp, 'before-db', 'vi.db'), before_db is None),
            ('after', ROOT, after_db or os.path.join(tmp, 'after-db', 'vi.db'), after_db is None)]


def pending_sources(fetch_sh):
    """{source id: data/raw subdirectory} of the snapshot sources that a data/fetch.sh text leaves PENDING (not pinned
    yet): that tree was built without them, so its database is built without them here too."""
    out = {}
    for line in fetch_sh.splitlines():
        p = line.split()
        if len(p) == 6 and p[0] == 'snap' and p[4] == 'PENDING':
            out[p[1]] = p[2].split('/')[0]
    return out


def build_db(src_root, db):
    """Builds `db` with the tools of `src_root` from data/raw, restricted to the sources that tree's data/fetch.sh pins:
    a source it leaves PENDING is hidden and allowed missing (TUSACH_ALLOW_MISSING), as that tree's own build had it."""
    os.makedirs(os.path.dirname(db), exist_ok=True)
    raw, env = os.path.join(ROOT, 'data/raw'), dict(os.environ)
    pend = pending_sources(open(os.path.join(src_root, 'data/fetch.sh'), encoding='utf-8').read())
    if pend:
        raw = os.path.join(os.path.dirname(db), 'raw')
        os.makedirs(raw, exist_ok=True)
        for name in os.listdir(os.path.join(ROOT, 'data/raw')):
            if name not in pend.values():
                os.symlink(os.path.join(ROOT, 'data/raw', name), os.path.join(raw, name))
        env['TUSACH_ALLOW_MISSING'] = ','.join(sorted(pend))
        print(f'compare: {src_root}: its data/fetch.sh leaves {", ".join(sorted(pend))} PENDING: built without them')
    r = subprocess.run([sys.executable, '-I', os.path.join(src_root, 'tools/build_db.py'), raw, db], cwd=src_root,
                       capture_output=True, text=True, env=env)
    if r.returncode or not os.path.exists(db):
        sys.exit(f'compare: the database build in {src_root} failed:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}')


def course_words():
    """The course's own words: every card id of course/lexicon.tsv (not names) and every word of the proposal word
    lists (tag kept)."""
    import course
    import lexicon
    out = []
    for r in lexicon.load():
        if r['pos'] != 'name':
            out += [r['cid'], r['k']]
    import glob
    for f in sorted(glob.glob(os.path.join(ROOT, 'course/proposal/wordlist-*.tsv'))):
        try:
            out += [r['word'].replace('_', ' ') for r in course.wordlist(f) if r['type'] != 'name']
        except ValueError:
            pass
    seen = set()
    return [w for w in out if not (w in seen or seen.add(w))]


def top_keys(db, n):
    import sqlite3
    return [k for (k,) in sqlite3.connect(db).execute(
        "SELECT e.key FROM entry e JOIN source s ON s.id = e.source WHERE s.fixture = 0 AND e.freq_rank IS NOT NULL "
        "GROUP BY e.key ORDER BY min(e.freq_rank) LIMIT ?", (n,))]


def dump_cards(src_root, db, words, out_dir):
    """{word: card fields} through src_root's own tools/cards.py and `db` (tools/carddump.py)."""
    os.makedirs(out_dir, exist_ok=True)
    kf, out = os.path.join(out_dir, 'keys.txt'), os.path.join(out_dir, 'cards.json')
    open(kf, 'w', encoding='utf-8').write('\n'.join(words) + '\n')
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'carddump.py'), src_root, db, out, kf],
                       capture_output=True, text=True)
    if r.returncode or not os.path.exists(out):
        sys.exit(f'compare: card dump in {src_root} failed:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}')
    return json.load(open(out, encoding='utf-8'))


def lead(c):
    return ((c or {}).get('en') or '').split('; ')[0]


def diff_cards(a, b, course, ranks, limit=20, out_path=None):
    """Prints the real-card differences; returns the number of blocking ones (a course word that lost its card)."""
    classes = {}
    rows = []

    def add(cls, w, x, y):
        classes.setdefault(cls, []).append(f'{w}: {x} -> {y}')
        rows.append((ranks.get(w.split('~')[0], ''), w, cls, x, y))
    for w in sorted(set(a) | set(b), key=lambda w: (ranks.get(w.split('~')[0], 10 ** 9), w)):
        x, y = a.get(w), b.get(w)
        if x and not y:
            add('CARD LOST' if w in course else 'card lost', w, lead(x), '(none)')
            continue
        if y and not x:
            add('card gained', w, '(none)', lead(y))
            continue
        if not x or not y:
            continue
        if lead(x) != lead(y):
            add('English lead changed', w, json.dumps(lead(x), ensure_ascii=False), json.dumps(lead(y), ensure_ascii=False))
        elif x.get('en') != y.get('en'):
            add('English (later items) changed', w, json.dumps(x.get('en'), ensure_ascii=False),
                json.dumps(y.get('en'), ensure_ascii=False))
        for f in ('label', 'chars'):
            if (x.get(f) or '') != (y.get(f) or ''):
                add(f'{f} changed', w, x.get(f) or '-', y.get(f) or '-')
        ex, ey = (x.get('ex') or {}).get('vi', ''), (y.get('ex') or {}).get('vi', '')
        if ex != ey:
            add('example lost' if not ey else 'example gained' if not ex else 'example changed', w, ex or '-', ey or '-')
    blocking = len(classes.get('CARD LOST', []))
    print(f'== real cards: {len(a)} words before, {len(b)} after ({len(course)} course words)')
    for cls in sorted(classes, key=lambda c: (not c.isupper(), c)):
        print(f'== {cls}: {len(classes[cls])}')
        for it in classes[cls][:limit]:
            print('  ' + it)
        if len(classes[cls]) > limit:
            print(f'  … {len(classes[cls]) - limit} more')
    print('cards: ' + '; '.join(f'{c} {len(v)}' for c, v in sorted(classes.items())) + f'; {blocking} blocking')
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('rank\tword\tchange\tbefore\tafter\n')
            for r in rows:
                f.write('\t'.join(str(x).replace('\t', ' ') for x in r) + '\n')
        print(f'compare: every changed card written to {out_path}')
    return blocking


def run():
    arg = lambda n, d: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d   # noqa: E731
    ref = arg('--ref', None)
    if ref is None:
        ok = subprocess.run(['git', 'rev-parse', '--verify', '-q', 'origin/main'], cwd=ROOT, capture_output=True).returncode == 0
        ref = 'origin/main' if ok else 'HEAD'
    tmp = tempfile.mkdtemp(prefix='tusach-compare-')
    wt = os.path.join(tmp, 'src')
    try:
        subprocess.run(['git', 'worktree', 'add', '--detach', '-q', wt, ref], cwd=ROOT, check=True)
        plan = db_plan(wt, tmp, arg('--before-db', None), arg('--after-db', None))
        for side, src, db, fresh in plan:
            if fresh:
                build_db(src, db)
            print(f'{side}: {"working tree" if src == ROOT else ref} with {"its own new" if fresh else "the given"} '
                  f'database {db}')
        (_, _, before_db, _), (_, _, after_db, _) = plan
        a = snapshot(build(wt, before_db, os.path.join(tmp, 'before')))
        b = snapshot(build(ROOT, after_db, os.path.join(tmp, 'after')))
        blocking = diff(a, b, int(arg('--max', 20)))
        n = int(arg('--top', 3000))
        course = course_words()
        tb, ta = top_keys(before_db, n), top_keys(after_db, n)
        words = list(dict.fromkeys(ta + tb + course))
        ranks = {k: i + 1 for i, k in enumerate(ta)}
        ca = dump_cards(wt, before_db, words, os.path.join(tmp, 'cards-before'))
        cb = dump_cards(ROOT, after_db, words, os.path.join(tmp, 'cards-after'))
        return blocking + diff_cards(ca, cb, set(course), ranks, int(arg('--max', 20)), arg('--cards-out', None))
    finally:
        subprocess.run(['git', 'worktree', 'remove', '--force', wt], cwd=ROOT, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    limit = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 20
    pos = [a for i, a in enumerate(sys.argv[2:], 2) if not a.startswith('--') and sys.argv[i - 1] != '--max']
    if cmd == 'snapshot':
        page, out = (pos if len(pos) == 2 else [os.path.join(ROOT, 'app/dist/index.html')] + pos)
        json.dump(snapshot(page), open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{out}: snapshot of {page}')
        return
    if cmd == 'diff':
        a, b = (json.load(open(p, encoding='utf-8')) for p in pos[:2])
        sys.exit(1 if diff(a, b, limit) else 0)
    if cmd == 'run':
        sys.exit(1 if run() else 0)
    sys.exit(__doc__)


if __name__ == '__main__':
    main()
