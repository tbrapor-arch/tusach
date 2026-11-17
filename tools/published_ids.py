"""Record the word cards of a page that is being published: their ids in app/published-card-ids.txt (never removes
any) and their English rank in app/published-english.tsv (keeps the best rank seen).

    python3 tools/published_ids.py [app/dist/index.html]

Run it on the page that is being published (after `make app`), and commit both files with the change. Every later
build keeps a card for each listed id (tools/build_app.py), so a word saved on a device or opened from the private
module never stops opening; and tools/check_cards.py fails a build in which a published card's English got poorer.
A test-fixture card (fixture: 1) is never recorded."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, 'app', 'published-card-ids.txt')
EN = os.path.join(ROOT, 'app', 'published-english.tsv')
HEAD = ('# Every word-card id the published page has had: tools/build_app.py keeps a card for each, so a saved word or\n'
        '# a link from the private module never stops opening. Add ids (tools/published_ids.py), never remove any.\n')
EN_HEAD = ('# Card id <TAB> English rank <TAB> English, as last published (tools/published_ids.py). tools/check_cards.py\n'
           '# fails a build in which a card\'s English rank is lower than here. Ranks: tools/english.py RANK.\n')


def cards_of(page):
    s = open(page, encoding='utf-8').read()
    m = re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', s, re.S)
    return {i: c for i, c in json.loads(m.group(1))['dict'].items() if not c.get('fixture')}


def main():
    page = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'app', 'dist', 'index.html')
    old = {l.strip() for l in open(FILE, encoding='utf-8') if l.strip() and not l.startswith('#')} if os.path.exists(FILE) else set()
    cards = cards_of(page)
    open(FILE, 'w', encoding='utf-8').write(HEAD + ''.join(i + '\n' for i in sorted(old | set(cards))))
    en = {}
    if os.path.exists(EN):
        for l in open(EN, encoding='utf-8'):
            if l.strip() and not l.startswith('#'):
                i, r, g = (l.rstrip('\n').split('\t') + ['', ''])[:3]
                en[i] = (int(r or 0), g)
    for i, c in cards.items():
        r = int(c.get('en_rank') or 0)
        if r >= en.get(i, (-1, ''))[0]:
            en[i] = (r, (c.get('en') or '').replace('\t', ' '))
    open(EN, 'w', encoding='utf-8').write(EN_HEAD + ''.join(f'{i}\t{r}\t{g}\n' for i, (r, g) in sorted(en.items())))
    print(f'{FILE}: {len(old | set(cards))} ids ({len(set(cards) - old)} added); {EN}: {len(en)} rows')


if __name__ == '__main__':
    main()
