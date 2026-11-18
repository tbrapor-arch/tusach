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

sys_path = os.path.dirname(os.path.abspath(__file__))
import sys  # noqa: E402
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)
import vi  # noqa: E402

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

    def gloss(self, cid, k, tag=None, parts=(), dict_entry=None):
        """(English, source) for card `cid` (key `k`, homograph tag `tag`). `parts`: [(English, source)] of its
        syllables, for the last resort. `dict_entry`: (English, 'dict:SOURCE') of the etymology the card shows
        (tools/cards.py senses), so the English and the characters come from the same entry."""
        if cid in self.course:
            return self.course[cid], 'course'
        if cid in self.written:
            return self.written[cid], 'written'
        en, src = dict_entry if dict_entry else self.dict_en(k, tag)
        if en:
            return en, src
        if parts and all(p[0] for p in parts) and len(parts) > 1:
            return ' + '.join(p[0].split(';')[0].strip() for p in parts), 'parts'
        return '', ''


# ------------------------------------------------------------------------------------- dictionary English for a card
# Used by tools/build_db.py compose_english (each Wiktionary entry's `english`) and by tools/coverage.py (the measure
# of unusable glosses). Written 18 Nov 2026; the thresholds were read on the top 1,000 words, not tuned on a held-out
# set.
import math  # noqa: E402
import re  # noqa: E402

SKIP_TAGS = {'misspelling', 'no-gloss'}
LATE_TAGS = {'archaic', 'obsolete', 'rare', 'dialectal', 'Southern', 'Central', 'historical', 'dated', 'uncommon',
             'literary', 'Hán-Nôm', 'in-compounds', 'nonstandard', 'poetic', 'Internet', 'slang', 'vulgar',
             'derogatory', 'euphemistic', 'figuratively', 'humorous'}
FORM_OF = re.compile(r"^(?:(?:alternative|obsolete|archaic|dated|nonstandard|less common|rare|common|standard|eye dialect|"
                     r"informal|superseded|pre-reform|former|older|Northern(?: Vietnam)?|Southern(?: Vietnam)?|"
                     r"(?:South |North )?Central(?: Vietnam)?(?: and Southern Vietnam)?|"
                     r"[A-Z][\w ]* Vietnam(?: and [\w ]+ Vietnam)?) )*(?:spelling|form|variant|misspelling|"
                     r"abbreviation|clipping|contraction|initialism|acronym|short(?:ening)?|reduplicant|synonym)"
                     r"(?: form)? (?:of|for)\b", re.I)
SHORT_FOR = re.compile(r'^(?:short for|clipping of|abbreviation of|ellipsis of)\b', re.I)
DESCRIPTION = re.compile(r'^(?:used\b|negates\b|indicates\b|expresses\b|denotes\b|marks\b|an? (?:interrogative|'
                         r'particle|word|term|expression|marker)\b|(?:\w+ )?(?:particle|marker|pronoun|classifier) '
                         r'(?:used|that|which|for|of|to)\b|placed\b|added\b|equivalent to\b)', re.I)
MAX_FIRST = 60          # a first sense longer than this is "too long" for a card
MAX_TOTAL = 100         # composed English is cut after the sense that reaches this length
MIN_EVIDENCE = 3.0      # translation evidence below this is ignored (zipf of the English word - log2 of rivals)
POS_OK = {'noun': {'noun', 'name'}, 'verb': {'verb', 'adj'}, 'adj': {'adj', 'verb'}, 'adv': {'adv', 'phrase'},
          'pron': {'pron', 'adv', 'det'}, 'intj': {'intj', 'phrase'}, 'phrase': {'phrase', 'intj', 'adv', 'prep_phrase'},
          'particle': {'particle', 'intj', 'adv'}, 'num': {'num', 'noun'}, 'conj': {'conj'}, 'prep': {'prep'},
          'classifier': {'noun'}, 'det': {'det', 'pron'}, 'postp': {'prep'}, 'name': set(), 'character': {'num', 'noun'}}


def first_sense(text):
    return (text or '').split('; ')[0].strip()


def problems(text, missing=''):
    """Why an English text is not usable on a card ([] if it is): form-of (an alternative form / spelling / short
    for…, no English of its own), description (a usage description in place of a translation: "Used to…",
    "Negates…"), too-long (first sense over MAX_FIRST characters), missing-main (the English Wiktionary translates
    `missing`, a frequent English word, by this word, and the text lacks it), empty."""
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


def zipf_en(w, _cache={}):
    if w not in _cache:
        try:
            import wordfreq
            _cache[w] = wordfreq.zipf_frequency(w, 'en')
        except ImportError:                       # sandbox without wordfreq: every English word counts the same
            _cache[w] = 4.0
    return _cache[w]


def evidence(rows, pos):
    """{English headword: score} from translation rows (en, en_pos, sense, tags, n_vi) of one Vietnamese word, for an
    entry of part of speech `pos`: zipf frequency of the English word minus log2 of the number of Vietnamese words
    the same table gives (a table that lists only this word is specific). Rows tagged archaic/dialectal, of another
    part of speech, or below MIN_EVIDENCE are left out."""
    ok = POS_OK.get(pos, {pos}) if pos else None
    out = {}
    heads = {r[0] for r in rows}
    for en, en_pos, sense, tags, n_vi in rows:
        if (ok is not None and en_pos not in ok) or LATE_TAGS & set(filter(None, (tags or '').split(','))):
            continue
        if any(h != en and has_word(sense, h) for h in heads):
            continue      # a table defined by another English word of the same Vietnamese word: "love" (tennis) = "zero"
        s = zipf_en(en) - math.log2(max(n_vi, 1))
        if s >= MIN_EVIDENCE and s > out.get(en, -9):
            out[en] = s
    return out


def head_text(en, en_pos):
    return ('to ' + en) if en_pos == 'verb' and not en.startswith('to ') else en


def compose(senses, ev, en_pos=None, leads=()):
    """(English text, score) of one entry. senses: [(gloss, tags set, examples, is_alt_of)] in the source order; ev:
    {English word: score} (evidence()); en_pos: {English word: its part of speech} for the "to …" of verbs; leads:
    the attested English words that no entry of the word contains, given to this entry (tools/build_db.py
    compose_english gives them to one entry of the word only: bận "busy").
    Senses: misspellings and empty ones dropped; "alternative form of" senses dropped when the entry has others;
    ordered: ordinary before archaic/dialectal/literary…, then a sense containing an attested English word before
    one that contains none (thế nào: "how" before "inevitably"), then the source order. The leads come first. Cut
    after MAX_TOTAL characters (the first item is always kept), at most 4 items. score: the evidence of the first
    English shown (0 when none), minus 5 for a form-of text, minus 2 for an archaic/dialectal first sense:
    tools/cards.py puts the entry with the best score first among one etymology's entries."""
    ss = [s for s in senses if s[0] and not SKIP_TAGS & s[1]]
    if any(not s[3] for s in ss):
        ss = [s for s in ss if not s[3]]

    def match(g):
        return max((sc for w, sc in ev.items() if has_word(g, w)), default=0.0)
    order = sorted(range(len(ss)), key=lambda i: (bool(LATE_TAGS & ss[i][1]), match(ss[i][0]) == 0, i))
    gl = []
    for i in order:
        if ss[i][0] not in gl:
            gl.append(ss[i][0])
    lead = [head_text(w, (en_pos or {}).get(w)) for w in leads]
    items = []
    for g in lead + gl:
        if g not in items and (not items or len('; '.join(items + [g])) <= MAX_TOTAL) and len(items) < 4:
            items.append(g)
    text = '; '.join(items)
    if not text:
        return '', -9.0
    top = max([ev.get(w, 0.0) for w in leads] + [match(items[0])])
    late = bool(order) and not leads and bool(LATE_TAGS & ss[order[0]][1])
    return text, top - (5 if 'form-of' in problems(text) else 0) - (2 if late else 0)


def leads_for(ev, glosses, n=1):
    """The attested English words (evidence) to put first: only when none of `glosses` (every sense of every entry
    of the word) contains any attested English word (bận: no sense says "busy"); then the best, at most n, within 1.0
    of the best. A word whose senses already contain one (xa "far", tên "name") gets none: an English homonym's table
    ("remote", "title") never goes before the word's own senses."""
    if not ev or any(has_word(g, w) for w in ev for g in glosses):
        return []
    free = sorted(ev.items(), key=lambda x: (-x[1], x[0]))
    return [w for w, sc in free[:n] if sc >= free[0][1] - 1.0]


def _selftest():
    s = [('to get occupied doing something', set(), 0, False)]
    ev = {'busy': 4.7}
    t, sc = compose(s, ev, {'busy': 'adj'}, leads_for(ev, [x[0] for x in s]))
    assert t == 'busy; to get occupied doing something' and sc > 4, (t, sc)
    assert leads_for({'far': 4.3, 'remote': 4.4}, ['far']) == []
    s = [('inevitably, somehow or other', set(), 0, False), ('how', set(), 1, False)]
    assert compose(s, {'how': 5.0})[0].startswith('how')
    assert problems('alternative form of cám ơn (“thank you”)') == ['form-of']
    assert problems('Alternative spelling of lí do.') == ['form-of']
    assert problems('Negates the meaning of the modified verb') == ['description']
    assert problems('busy') == []
    assert problems('a' * 70) == ['too-long']
    print('english: self-test ok')


if __name__ == '__main__':
    _selftest()
