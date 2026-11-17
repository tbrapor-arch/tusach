"""English for the word cards: one gloss for every card, with where it came from and a rank.

Order (first one found wins):
  1. course   English written in the lessons' `new_words` (passed in by tools/cards.py)
  2. written  course/glosses_en.tsv: short glosses written for the course (word <TAB> English [<TAB> tag])
  3. dict     the English of the word's dictionary entry (the source with the best rank in SOURCE_RANK; non-commercial
              sources exist only in vi-nc.db, i.e. in private builds)
  4. parts    the English of the word's syllables joined with " + " (automatic; a word no source has)

RANK is what tools/check_cards.py compares with app/published-english.tsv: a card's English may change, but its rank
may never go down ("no card with poorer English than before"). Every card must have English (owner's rule).
Used by tools/build_app.py and by the private module's build through tools/cards.py, so a word gets the same English
everywhere.
"""
import csv
import os

import vi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRITTEN = os.path.join(ROOT, 'course/glosses_en.tsv')
RANK = {'course': 3, 'written': 3, 'dict': 2, 'parts': 1, '': 0}
# Order of the dictionary sources for English, best first. Wiktionary is the only open, compatible Vietnamese-English
# source (ATTRIBUTION.md: the GPL dictionaries are not used); a checked source would go before it. The fixture is last.
SOURCE_RANK = ['wiktionary']


def rank(src):
    return RANK.get((src or '').split(':')[0], 0)


def load_written(path=WRITTEN):
    """{card id: English}. Lines starting with # are comments."""
    out = {}
    if os.path.exists(path):
        for row in csv.reader(open(path, encoding='utf-8'), delimiter='\t'):
            if not row or row[0].startswith('#') or len(row) < 2 or not row[1].strip():
                continue
            tag = row[2].strip() if len(row) > 2 else ''
            out[vi.card_id(vi.key(row[0]), tag or None)] = row[1].strip()
    return out


class English:
    def __init__(self, con, course=None, written=None):
        """`course`: {card id: English} from the lessons' new_words."""
        self.con = con
        self.course = course or {}
        self.written = load_written() if written is None else written

    def dict_en(self, k, tag=None):
        rows = self.con.execute("SELECT e.english, e.source, s.fixture FROM entry e JOIN source s ON s.id = e.source "
                                "WHERE e.key=? AND e.english != '' AND (?='' OR e.tag=?)", (k, tag or '', tag or '')).fetchall()
        if not rows:
            return None, None
        order = {s: i for i, s in enumerate(SOURCE_RANK)}
        rows.sort(key=lambda r: (r[2], order.get(r[1], len(order))))
        return rows[0][0], f'dict:{rows[0][1]}'

    def gloss(self, cid, k, tag=None, parts=()):
        """(English, source) for card `cid` (key `k`, homograph tag `tag`). `parts`: [(English, source)] of its
        syllables, for the last resort."""
        if cid in self.course:
            return self.course[cid], 'course'
        if cid in self.written:
            return self.written[cid], 'written'
        en, src = self.dict_en(k, tag)
        if en:
            return en, src
        if parts and all(p[0] for p in parts) and len(parts) > 1:
            return ' + '.join(p[0].split(';')[0].strip() for p in parts), 'parts'
        return '', ''
