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
  - English that drops senses: a gloss shorter than the published one that lacks one of its senses (split at ; and ,),
    unless the change is recorded in app/english-changes.tsv (card id <TAB> new English <TAB> reason)
Warnings (printed, for review): a published card whose gloss changed within the same rank.
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


CHANGES = os.path.join(ROOT, 'app/english-changes.tsv')


def senses(en):
    return [x.strip().lower() for x in re.split(r'[;,]', en or '') if x.strip()]


def read_changes(path):
    """{(card id, new English)}: gloss changes recorded on purpose (app/english-changes.tsv)."""
    out = set()
    if path and os.path.exists(path):
        for l in open(path, encoding='utf-8'):
            if l.strip() and not l.startswith('#'):
                p = (l.rstrip('\n').split('\t') + ['', ''])[:3]
                out.add((p[0], p[1]))
    return out


def page_dict(page):
    s = open(page, encoding='utf-8').read()
    m = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', s, re.S)
    return json.loads(m.group(1))['dict']


def check(store_path, page=None, published=None, english_tsv=None, modules=None, warn=None, changes=CHANGES):
    """Returns a list of error strings (empty: all good); warnings are appended to `warn` (a list) when given."""
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
        if c is None:
            continue
        new = c.get('en') or ''
        if english.rank(c.get('en_src')) < r:
            errs.append(f'poorer English than before: {i}: "{new}" ({c.get("en_src") or "none"}) '
                        f'was "{en}" (rank {r})')
        elif en and new != en:
            lost = [x for x in senses(en) if x not in senses(new)]
            if len(new) < len(en) and lost and (i, new) not in read_changes(changes):
                errs.append(f'English drops senses: {i}: "{new}" was "{en}" (lost: {"; ".join(lost)}); record it in '
                            'app/english-changes.tsv if meant')
            elif warn is not None:
                warn.append(f'gloss changed within the same rank (review): {i}: "{en}" -> "{new}"')
    return errs


def main():
    store = arg('--store', os.path.join(ROOT, 'data/build/cards.json'))
    page = arg('--page', os.path.join(ROOT, 'app/dist/index.html'))
    warn = []
    errs = check(store, page if os.path.exists(page) else None,
                 arg('--published', os.path.join(ROOT, 'app/published-card-ids.txt')),
                 arg('--english', os.path.join(ROOT, 'app/published-english.tsv')), warn=warn)
    for w in warn[:200]:
        print('W', w)
    for e in errs[:200]:
        print('E', e)
    print(f'card check: {len(errs)} error(s)')
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
