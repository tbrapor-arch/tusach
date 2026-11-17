"""The card check, run at the end of every build (tools/build_app.py calls it, and the private module's build must too)
and on every push (.github/workflows/check.yml). Handover section 4.5.

    python3 -I tools/check_cards.py [--store data/build/cards.json] [--page app/dist/index.html]
                                    [--published app/published-card-ids.txt] [--english app/published-english.tsv]

Errors (exit 1):
  - a word without a card: a word token of any module whose card was not found (the store's `missing` lists)
  - a card lost: an id a module lists, or a published id (app/published-card-ids.txt), with no card in the store / page
  - a card without English (owner's rule: English on every card)
  - poorer English than before: a card whose English rank (tools/english.py RANK) is lower than the rank recorded when
    it was last published (app/published-english.tsv, written by tools/published_ids.py)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import english  # noqa: E402


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def read_ids(path):
    if not os.path.exists(path):
        return []
    return [l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('#')]


def read_english(path):
    out = {}
    if os.path.exists(path):
        for l in open(path, encoding='utf-8'):
            if l.startswith('#') or not l.strip():
                continue
            cid, r, en = (l.rstrip('\n').split('\t') + ['', ''])[:3]
            out[cid] = (int(r or 0), en)
    return out


def page_dict(page):
    s = open(page, encoding='utf-8').read()
    m = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', s, re.S)
    return json.loads(m.group(1))['dict']


def check(store_path, page=None, published=None, english_tsv=None, modules=None):
    """Returns a list of error strings (empty: all good)."""
    errs = []
    st = json.load(open(store_path, encoding='utf-8'))
    cards, mods = st.get('cards', {}), st.get('modules', {})
    for name, m in sorted(mods.items()):
        if modules and name not in modules and name != '_published':
            continue
        for w in m.get('missing', []):
            errs.append(f'word without a card: "{w}" ({name})')
        for i in m.get('cards', []):
            if i not in cards:
                errs.append(f'card lost: {i} (listed by {name}, not in the store)')
    shown = page_dict(page) if page else cards
    for i in read_ids(published) if published else []:
        if i not in shown:
            errs.append(f'card lost: {i} (a published page had it)')
    for i, c in sorted(shown.items()):
        if not (c.get('en') or '').strip():
            errs.append(f'card without English: {i}')
    before = read_english(english_tsv) if english_tsv else {}
    for i, (r, en) in sorted(before.items()):
        c = shown.get(i)
        if c is not None and english.rank(c.get('en_src')) < r:
            errs.append(f'poorer English than before: {i}: "{c.get("en")}" ({c.get("en_src") or "none"}) '
                        f'was "{en}" (rank {r})')
    return errs


def main():
    store = arg('--store', os.path.join(ROOT, 'data/build/cards.json'))
    page = arg('--page', os.path.join(ROOT, 'app/dist/index.html'))
    errs = check(store, page if os.path.exists(page) else None,
                 arg('--published', os.path.join(ROOT, 'app/published-card-ids.txt')),
                 arg('--english', os.path.join(ROOT, 'app/published-english.tsv')))
    for e in errs[:200]:
        print('E', e)
    print(f'card check: {len(errs)} error(s)')
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
