"""English for the word cards: one gloss for every card, with where it came from and a rank.

Order (first one found wins):
  1. course   English written in the lessons' `new_words` (passed in by tools/cards.py)
  2. lexicon  course/lexicon.tsv (tools/lexicon.py), chosen by tools/cards.py before calling gloss()
  3. dict     the English of the word's dictionary entry (the source with the best rank in SOURCE_RANK; non-commercial
              sources exist only in vi-nc.db, i.e. in private builds)
  4. parts    the English of the word's syllables joined with " + " (automatic; a word no source has)

RANK is what tools/check_cards.py compares with app/published-english.tsv: a card's English may change, but its rank
may never go down ("no card with poorer English than before"). Every card must have English (owner's rule).
Used by tools/build_app.py and by the private module's build through tools/cards.py, so a word gets the same English
everywhere.
"""
import os

sys_path = os.path.dirname(os.path.abspath(__file__))
import sys  # noqa: E402
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)
import vi  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RANK = {'course': 3, 'lexicon': 3, 'dict': 2, 'parts': 1, '': 0}
# Order of the dictionary sources for English, best first. Wiktionary is the only open, compatible Vietnamese-English
# source (ATTRIBUTION.md: the GPL dictionaries are not used); a checked source would go before it. The fixture is last.
SOURCE_RANK = ['wiktionary']


def rank(src):
    return RANK.get((src or '').split(':')[0], 0)


class English:
    def __init__(self, con, course=None):
        """`course`: {card id: English} from the lessons' new_words."""
        self.con = con
        self.course = course or {}

    def dict_en(self, k, tag=None):
        rows = self.con.execute("SELECT e.english, e.source, s.fixture FROM entry e JOIN source s ON s.id = e.source "
                                "WHERE e.key=? AND e.english != '' AND (?='' OR e.tag=?)", (k, tag or '', tag or '')).fetchall()
        if not rows:
            return None, None
        order = {s: i for i, s in enumerate(SOURCE_RANK)}
        rows.sort(key=lambda r: (r[2], order.get(r[1], len(order))))
        return rows[0][0], f'dict:{rows[0][1]}'

    def gloss(self, cid, k, tag=None, parts=(), dict_entry=None):
        """(English, source) for card `cid` (key `k`, homograph tag `tag`). `parts`: [(English, source)] of its
        syllables, for the last resort. `dict_entry`: (English, 'dict:SOURCE') of the etymology the card shows
        (tools/cards.py senses), so the English and the characters come from the same entry."""
        if cid in self.course:
            return self.course[cid], 'course'
        en, src = dict_entry if dict_entry else self.dict_en(k, tag)
        if en:
            return en, src
        if parts and all(p[0] for p in parts) and len(parts) > 1:
            return ' + '.join(p[0].split(';')[0].strip() for p in parts), 'parts'
        return '', ''


# ------------------------------------------------------------------------------------- dictionary English for a card
# Used by tools/build_db.py compose_english (each Wiktionary entry's `english`) and by tools/coverage.py (the measure
# of unusable glosses). Rewritten 18 Nov 2026 after review 2 (finding 2): the translation-table scoring, the head-word
# cancellation, the global part-of-speech map and the comma-cut shortening made cards worse (cho lost "give", ăn led
# with "to capture", đánh with "finger"). What is left is a plain rule whose failures are visible: Wiktionary's own
# sense order, misspellings and form-of senses dropped (when there are others), late senses (archaic, rare, vulgar,
# slang, dialectal…) last, long non-first senses left out. The course lexicon (course/lexicon.tsv) decides the
# English of every word it has; this is for the others. Translation tables are only evidence (missing_main: report).
import re  # noqa: E402

SKIP_TAGS = {'misspelling', 'no-gloss'}
LATE_TAGS = {'archaic', 'obsolete', 'rare', 'dialectal', 'Southern', 'Central', 'historical', 'dated', 'uncommon',
             'literary', 'Hán-Nôm', 'in-compounds', 'nonstandard', 'poetic', 'Internet', 'slang', 'vulgar',
             'derogatory', 'euphemistic', 'humorous', 'pronunciation-spelling', 'offensive', 'ironic', 'childish'}
FORM_OF = re.compile(r"^(?:(?:alternative|obsolete|archaic|dated|nonstandard|less common|rare|common|standard|eye dialect|"
                     r"informal|superseded|pre-reform|former|older|pronunciation|traditional|letter-case|"
                     r"Northern(?: Vietnam)?|Southern(?: Vietnam)?|"
                     r"(?:South |North )?Central(?: Vietnam)?(?: and Southern Vietnam)?|"
                     r"[A-Z][\w ]* Vietnam(?: and [\w ]+ Vietnam)?) )*(?:(?:tone[- ]placement|letter-case) )?"
                     r"(?:spelling|form|variant|misspelling|"
                     r"abbreviation|clipping|contraction|initialism|acronym|short(?:ening)?|reduplicant|synonym)"
                     r"(?: form)? (?:of|for)\b", re.I)
SHORT_FOR = re.compile(r'^(?:short for|clipping of|abbreviation of|ellipsis of)\b', re.I)
DESCRIPTION = re.compile(r'^(?:used\b|negates\b|indicates\b|expresses\b|denotes\b|marks\b|an? (?:interrogative|'
                         r'particle|word|term|expression|marker)\b|(?:\w+ )?(?:particle|marker|pronoun|classifier) '
                         r'(?:used|that|which|for|of|to)\b|placed\b|added\b|equivalent to\b)', re.I)
MAX_FIRST = 60          # a first sense longer than this is "too long" for a card (measure); a later one is left out
MAX_TOTAL = 100         # composed English stops before the sense that would pass this length (the first is kept)
MAX_ITEMS = 4
CROSS_REF = re.compile(r'(?:[;,.]\s*|\s+)\(?(?:compare|see also|see|cf\.)\s.*$', re.I)


def late(tags):
    """True for a sense the card puts after the ordinary ones (archaic, dialectal, Southern, slang, vulgar…). A sense
    tagged Northern is the course's own variety (Hà Nội): Wiktionary's "dialectal" beside "Northern" does not make it
    late (thế nào "how" is tagged Northern, dialectal)."""
    t = set(tags)
    if 'Northern' in t:
        t -= {'dialectal', 'Northern', 'Vietnam'}
    return bool(LATE_TAGS & t)


def first_sense(text):
    return (text or '').split('; ')[0].strip()


def problems(text, missing=''):
    """Why an English text is not usable on a card ([] if it is): form-of (an alternative form / spelling / short
    for…, no English of its own), description (a usage description in place of a translation: "Used to…",
    "Negates…"), too-long (first sense over MAX_FIRST characters), missing-main (the English Wiktionary translates
    `missing` by this word, and the text has none of its attested English words: missing_main()), empty."""
    t = first_sense(text)
    out = []
    if not t:
        return ['empty']
    if FORM_OF.match(t) or SHORT_FOR.match(t):
        out.append('form-of')
    elif DESCRIPTION.match(t):
        out.append('description')
    if len(t) > MAX_FIRST:
        out.append('too-long')
    if missing:
        out.append('missing-main')
    return out


PHRASE_STOP = {'have', 'with', 'from', 'into', 'about', 'that', 'this', 'what', 'some', 'very', 'more', 'most'}


def has_word(text, w):
    """`w` is in `text` as a word; a phrase ("older brother", "thank you") when one of its words of 4+ letters is."""
    t = (text or '').lower()
    if re.search(r'(?<![\w-])' + re.escape(w.lower()) + r'(?![\w-])', t):
        return True
    parts = [x for x in w.lower().split() if len(x) >= 4 and x not in PHRASE_STOP]
    return len(w.split()) > 1 and any(re.search(r'(?<![\w-])' + re.escape(x) + r'(?![\w-])', t) for x in parts)


def missing_main(text, rows, min_rows=2):
    """A REPORT, never a lead: the English word that the English Wiktionary's translation tables give for this word
    most often (at least `min_rows` tables, any part of speech) when the text contains none of the words of those
    tables, else ''. rows: (en, en_pos, sense, tags, n_vi)."""
    heads = {}
    for r in rows:
        if not late(filter(None, (r[3] or '').split(','))):
            heads[r[0]] = heads.get(r[0], 0) + 1
    if not heads or any(has_word(text, w) for w in heads):
        return ''
    w, n = max(heads.items(), key=lambda x: (x[1], x[0]))
    return w if n >= min_rows else ''


def clean(g):
    """One sense for a card: a trailing cross-reference ("…; compare mũi (“tip”)") removed, inner "; " made ", " (so
    that a sense is never split into fragments), whitespace normalised. A gloss that is only a cross-reference is ''."""
    g = ' '.join((g or '').split())
    if re.match(r'^\(?(?:compare|see also|see|cf\.)\s', g, re.I):
        return ''
    g = CROSS_REF.sub('', g).strip().rstrip(';,')
    return g.replace('; ', ', ').strip()


def compose(senses):
    """(English text, flags) of one entry. senses: [(gloss, tags set, examples, is_alt_of)] in Wiktionary's order.
    Misspellings and empty senses dropped; "alternative form of" senses dropped when the entry has others; ordinary
    senses in the source order, then late ones (archaic, rare, slang, vulgar, dialectal…); a sense longer than
    MAX_FIRST characters only as the first item (and then without its bracketed explanations if that leaves a text);
    at most MAX_ITEMS items and MAX_TOTAL characters. flags: 'late-first' when every sense is late, 'form-of' when
    the text is only a cross-reference."""
    ss = [s for s in senses if s[0] and not SKIP_TAGS & s[1]]
    if any(not s[3] for s in ss):
        ss = [s for s in ss if not s[3]]
    order = sorted(range(len(ss)), key=lambda i: (late(ss[i][1]), i))
    items = []
    for i in order:
        g = clean(ss[i][0])
        if not g or g in items:
            continue
        if len(g) > MAX_FIRST:
            if items:
                continue
            t = re.sub(r'\s*\([^()]*\)', '', g).strip()
            g = t if len(t) >= 3 else g
        if items and (len('; '.join(items + [g])) > MAX_TOTAL or len(items) >= MAX_ITEMS):
            break
        items.append(g)
    text = '; '.join(items)
    flags = set()
    if ss and all(late(s[1]) for s in ss):
        flags.add('late-first')
    if text and problems(text) and 'form-of' in problems(text):
        flags.add('form-of')
    return text, flags


def support(text, heads):
    """How many English words of the translation tables (heads: {English word: number of tables}) the text contains,
    weighted by tables: evidence for choosing BETWEEN etymologies only."""
    return sum(n for w, n in heads.items() if has_word(text, w))


def _selftest():
    assert compose([('to give', set(), 0, False), ('to let; to make; to cause', set(), 0, False),
                    ('for; to', set(), 0, False)])[0] == 'to give; to let, to make, to cause; for, to'
    t, _ = compose([('head', set(), 0, False), ('an end or extremity; compare mũi (“tip”)', set(), 0, False)])
    assert t == 'head; an end or extremity', t
    t, _ = compose([('what the fuck', {'vulgar'}, 0, False), ('to stop', set(), 0, False)])
    assert t.startswith('to stop'), t
    t, _ = compose([('to have', set(), 0, False), ('the left side of the balance sheet records the existing capital '
                                                    '(fixed capital, ...)', set(), 0, False)])
    assert t == 'to have', t
    assert problems('alternative form of cám ơn (“thank you”)') == ['form-of']
    assert problems('Traditional tone placement spelling of toà.') == ['form-of']
    assert problems('alternative letter-case form of ta') == ['form-of']
    assert problems('Negates the meaning of the modified verb') == ['description']
    assert problems('busy') == []
    assert missing_main('fine silk', [('be', 'verb', 'x', '', 1), ('be', 'verb', 'y', '', 1)]) == 'be'
    assert missing_main('to drink', [('take', 'verb', 'x', '', 1), ('drink', 'verb', 'y', '', 1)]) == ''
    print('english: self-test ok')


if __name__ == '__main__':
    _selftest()
