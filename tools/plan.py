"""The course plan from ONE source (review 3, finding 1): course/syllabus.yaml (lessons, particles, cast, the draft word
list) and the word list it names. This tool writes what derives from them and checks what must agree.

    python3 -I tools/plan.py --write    # syllabus.yaml's new-word counts of the listed lessons (from the word list);
                                        # the proposal's lesson table, particle strand, word-list counts and trà / chè
                                        # figures (between <!-- plan:NAME --> and <!-- /plan --> markers), and the
                                        # same trà / chè figures in the to-check list
    python3 -I tools/plan.py --check    # what --write would change, and the checks below (exit 1 on an error);
                                        # `make lint` runs it

Checks (E = error):
  E  a word of a REVIEW lesson in the word list (a review has no new words), or new words planned for one
  E  a non-review lesson up to the last listed one without words; a listed lesson that is not in the plan
  E  the plan's new-word counts of a listed lesson differ from the word list's (run --write)
  E  a Vietnamese word, before it is taught (word list lesson), in: the word list's own notes (the part a person
     wrote), a course-lexicon usage or false-friend note of a word taught in that lesson, the lesson's planned title,
     grammar and strand (syllabus.yaml); a word written {in braces} is a marked preview and is not checked (cards
     show it without the braces); names of the cast and of the course lexicon pass
  E  a particle of the strand taught after the lesson that brings it in, or not named in that lesson's grammar
  E  a generated block of the proposal or the to-check list not as --write would write it
  I  the course-lexicon examples of a lesson's words that use words not yet taught (they are cards, not lines: listed,
     not refused)
A Vietnamese word is found as a run of syllables of which at least one has a Vietnamese letter or tone mark (plain
syllables join a run only when the dictionary has them and they are not common English words), cut by the
dictionary cutter (tools/vi.py cut()); a word whose every syllable is taught passes (tiếng Pháp, người Việt).
"""
import collections
import os
import re
import sys
import unicodedata

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import course  # noqa: E402
import lexicon  # noqa: E402
import vi  # noqa: E402

SYLLABUS = os.path.join(ROOT, 'course/syllabus.yaml')
TO_CHECK = os.path.join(ROOT, 'course/proposal/wordlist-2-to-check.md')
EN_COMMON = {'a', 'an', 'as', 'at', 'by', 'do', 'go', 'he', 'hi', 'in', 'is', 'it', 'me', 'my', 'no', 'of', 'on', 'or',
             'so', 'to', 'up', 'us', 'we', 'ban', 'bin', 'can', 'hot', 'long', 'man', 'men', 'mom', 'son', 'tin',
             'ten', 'than', 'then', 'them', 'him', 'his', 'her', 'had', 'has', 'not', 'but', 'and', 'for', 'one', 'all',
             'out', 'how', 'who', 'see', 'say', 'that', 'this', 'when', 'with', 'also', 'here', 'there', 'later',
             'same', 'once', 'some', 'into', 'only', 'then', 'one', 'ago', 'mi', 'la', 'ha', 'na', 'cam', 'pho', 'ca'}   # 'con' is not here: it is Vietnamese (review 4)
COMMON_RANK = 1500     # a name that is also a word of at most this rank is that word at a sentence start
VI_MARK = re.compile('[ăâêôơưđ̣̀́̃̉]')
KIND = (('Hán-Việt', 'hv'), ('older Chinese loan', 'other'), ('loan', 'other'), ('name', 'name'))
PLAN_ORDER = ('n', 'en', 'vi', 'review', 'grammar', 'bridge', 'strand', 'lines', 'new_words')


# ---------------------------------------------------------------------------------------------------------- data
def load():
    """(syllabus, rows of every word list of the plan, the last list's path): the approved lists and the draft
    (course.plan_word_lists), read together; each row keeps its `file`."""
    syl = course.syllabus()
    paths = course.plan_word_lists(syl)
    rows = [dict(r, file=p) for p in paths for r in course.wordlist(p)]
    return syl, rows, (paths[-1] if paths else None)


def kind(t):
    for prefix, k in KIND:
        if t.startswith(prefix):
            return k
    return 'native'


def counts(rows):
    """{lesson: {native, hv, other}} of a word list (names apart; native counts the others too, as lint does)."""
    out = collections.defaultdict(lambda: {'native': 0, 'hv': 0, 'other': 0})
    for r in rows:
        k = kind(r['type'])
        if k == 'name':
            continue
        n = int(r['lesson'])
        if k == 'hv':
            out[n]['hv'] += 1
        else:
            out[n]['native'] += 1
            if k == 'other':
                out[n]['other'] += 1
    return out


def base_key(word):
    return vi.key(vi.nfc(word).partition('~')[0].replace('_', ' '))


# ---------------------------------------------------------------------------------------------------------- yaml
def _flow(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, int):
        return str(v)
    if isinstance(v, dict):
        return '{' + ', '.join(f'{k}: {_flow(x)}' for k, x in v.items()) + '}'
    if isinstance(v, list):
        return '[' + ', '.join(_flow(x) for x in v) + ']'
    s = str(v)
    if not re.fullmatch(r'[\w][\w ./-]*', s) or re.fullmatch(r'(?:yes|no|true|false|null|on|off)', s, re.I):
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return s


def dump_syllabus(d, head):
    out = [head.rstrip('\n')]
    out.append('approved:')
    for k in ('syllabus', 'word_list'):
        v = (d.get('approved') or {}).get(k)
        out.append(f'  {k}: {_flow(v) if v else "null"}' + ('        # e.g. {by: owner, date: 2026-11-20}' if k == 'syllabus'
                                                           and not v else '       # e.g. {by: owner, date: 2026-11-20, '
                                                           'file: course/proposal/wordlist-2.tsv}' if not v else ''))
    out.append('# the draft the owner is asked to approve: tools/plan.py checks it against this plan (make lint)')
    out.append('draft: ' + _flow(d.get('draft') or {}))
    out.append('cast: ' + _flow(d.get('cast') or []))
    out.append('# the Northern particle strand: each particle, the lesson that brings it in (its grammar names it), its use')
    out.append('particles:')
    for p in d.get('particles') or []:
        out.append('  - ' + _flow(p))
    out.append('lessons:')
    for L in d.get('lessons') or []:
        out.append('  - ' + _flow({k: L[k] for k in PLAN_ORDER if k in L}))
    return '\n'.join(out) + '\n'


def syllabus_head():
    text = open(SYLLABUS, encoding='utf-8').read()
    return text[:text.index('approved:')]


# ---------------------------------------------------------------------------------------------------------- text
TERMS = {'hán việt', 'hán', 'việt', 'nôm', 'chữ nôm', 'chữ hán', 'quốc ngữ', 'tâi lô', 'ngang', 'huyền', 'sắc', 'hỏi',
         'ngã', 'nặng'}   # metalanguage, not lesson words
EN_MORE = {'the', 'café', 'cafe', 'pho', 'no', 'ha', 'ma', 'me', 'he', 'be', 'see', 'ten', 'tea', 'sang', 'pan', 'bang',
           'long', 'tan', 'can', 'ban', 'dan', 'man', 'nam', 'van', 'ton', 'non', 'chi', 'yin', 'tai', 'lo', 'ho', 'do',
           'day', 'loan', 'don', 'ti', 'hen'}


class Words:
    """Vietnamese words in mixed English / Vietnamese text (module docstring)."""

    def __init__(self, con, names):
        self.known = {k for (k,) in con.execute('SELECT DISTINCT key FROM entry')}
        self.canon = dict(con.execute('SELECT key, canon FROM spelling'))
        self.names = {vi.key(n) for n in names}
        # a name that is also a common word (Mai / mai "tomorrow", Minh / minh): at the start of a sentence it is read
        # as the word (review 4, C)
        self.common = {k for (k,) in con.execute('SELECT DISTINCT key FROM entry WHERE freq_rank <= ?', (COMMON_RANK,))}

    def runs(self, text, taught=None, n=None):
        """[[syllable, …]] of the Vietnamese runs of `text` (module docstring). Every token is classified on its own
        (review 4, C: a lone mua, cho, ba, ai, xa is a Vietnamese word, checked like any other); a capitalised name
        of the cast keeps its capital (exempt) except at the start of a sentence (after . ! ? ; or a line break, not
        after a colon or a quote: review 6) when it is also a common word that lesson n teaches (`taught`: key ->
        lesson), where it is lower-cased and read as that word ("Mai gặp nhé" with mai "tomorrow" taught). A name
        whose common word is not taught yet stays a name: "…: Minh is anh" is no error."""
        text = re.sub(r'\{[^}]*\}', ' ', vi.nfc(text))          # {preview}
        text = re.sub(vi.CJK.pattern + '+', ' ', text)
        out, run, last = [], [], None

        def flush():
            if run:
                out.append(list(run))
            run.clear()
        for m in re.finditer(r"[^\W\d_]+", text):
            t = m.group(0)
            low = t.lower()
            viet = (bool(VI_MARK.search(unicodedata.normalize('NFD', low))) and low not in EN_MORE) or (
                low in self.known and low not in EN_COMMON | EN_MORE and not vi.syllable_problems(low))
            if t[:1].isupper() and vi.key(t) in self.names:
                viet = True
                before = text[:m.start()].rstrip(' ')
                k = self.canon.get(vi.key(t), vi.key(t))
                if (not before or before[-1] in '.!?;\n') and vi.key(t) in self.common and taught is not None \
                        and taught.get(k, 999) <= (n or 0):
                    t = low                                  # sentence-initial and taught: the common word
            gap = text[last.end():m.start()] if last else ''
            if not viet or (run and re.search(r'[^\s]', gap)):
                flush()
            if viet:
                run.append(t)
            last = m
        flush()
        return out

    def late(self, text, n, taught):
        """The words of `text` not taught by lesson n: (surface, the lesson that teaches them or None)."""
        bad = []
        multi = [k.split() for k, w in taught.items() if w <= n and ' ' in k]
        for run in self.runs(text, taught, n):
            syl = [vi.key(x) for x in run]
            covered = [False] * len(syl)
            for i, s in enumerate(syl):
                k = self.canon.get(s, s)
                if taught.get(k, 999) <= n or (s in self.names and run[i][:1].isupper()):
                    covered[i] = True
            for ks in multi:                               # a taught word of several syllables covers them
                for i in range(len(syl) - len(ks) + 1):
                    if [self.canon.get(x, x) for x in syl[i:i + len(ks)]] == ks or syl[i:i + len(ks)] == ks:
                        covered[i:i + len(ks)] = [True] * len(ks)
            for i, nm in enumerate(syl):                  # names of several syllables (Hoàn Kiếm, Hà Nội)
                for j in range(i + 2, len(syl) + 1):
                    if ' '.join(syl[i:j]) in TERMS or (' '.join(syl[i:j]) in self.names and run[i][:1].isupper()):
                        covered[i:j] = [True] * (j - i)
            if all(covered):
                continue
            s = ' '.join(run)
            pos = 0
            for w in vi.words(vi.cut(s, self.known)):
                if w[0] != 'w':
                    continue
                m = len(w[1].replace('_', ' ').split())
                if not all(covered[pos:pos + m]):
                    k = self.canon.get(w[2], w[2])
                    if k not in TERMS and not (k in self.names and w[1][:1].isupper()):
                        bad.append(f'{w[1].replace("_", " ")} ({"L" + str(taught[k]) if k in taught else "not in the list"})')
                pos += m
        return bad


# ---------------------------------------------------------------------------------------------------------- checks
def check(con, verbose=False):
    """[(level, message)] of the checks in the module docstring."""
    syl, rows, wl = load()
    msgs = []
    if not rows:
        return msgs
    plans = {L['n']: L for L in syl.get('lessons') or []}
    reviews = {n for n, L in plans.items() if L.get('review')}
    cnt = counts(rows)
    last = max(cnt) if cnt else 0
    first = {}
    for r in rows:
        n = int(r['lesson'])
        f = r.get('file') or wl
        if n in reviews:
            msgs.append(('E', f'{f}:{r["line"]}: E {r["word"]}: lesson {n} is a review: no new word'))
        if n not in plans:
            msgs.append(('E', f'{f}:{r["line"]}: E {r["word"]}: lesson {n} is not in the plan'))
        cid = (r['type'] == 'name', base_key(r['word']), vi.nfc(r['word']).partition('~')[2])
        if cid in first and first[cid][0] != f:
            msgs.append(('E', f'{f}:{r["line"]}: E {r["word"]} is already in {first[cid][0]} (line {first[cid][1]}): '
                              'a word list teaches only new words'))
        first.setdefault(cid, (f, r['line']))
    for n, L in plans.items():
        nw = L.get('new_words') or {}
        if n in reviews and (nw.get('native') or nw.get('hv')):
            msgs.append(('E', f'course/syllabus.yaml: E lesson {n} is a review and plans new words'))
        if n <= last and n not in reviews and n not in cnt:
            msgs.append(('E', f'{wl}: E lesson {n} (not a review) has no words'))
        if n in cnt and (nw.get('native'), nw.get('hv'), nw.get('other', 0)) != \
                (cnt[n]['native'], cnt[n]['hv'], cnt[n]['other']):
            msgs.append(('E', f'course/syllabus.yaml: E lesson {n} plans {nw} new words, the word list has '
                              f'{dict(cnt[n])}: run tools/plan.py --write'))
    # words before they are taught
    lex = lexicon.load()
    by_cid, by_key = lexicon.index(lex)
    names = list(syl.get('cast') or []) + [r['key'] for r in lex if r['pos'] == 'name'] + \
        [r['word'].replace('_', ' ') for r in rows if r['type'] == 'name']
    W = Words(con, names)
    taught = {}
    for r in rows:
        if r['type'] != 'name':
            k = base_key(r['word'])
            k = W.canon.get(k, k)
            taught[k] = min(int(r['lesson']), taught.get(k, 999))

    def late(text, n):
        return W.late(text, n, taught)
    import wordlist
    for r in rows:
        n = int(r['lesson'])
        bad = late(wordlist.human_note(r['note']).replace('(name) ', ''), n)
        if bad:
            msgs.append(('E', f'{r.get("file") or wl}:{r["line"]}: E {r["word"]} (L{n}) note uses words not yet taught: '
                              f'{", ".join(dict.fromkeys(bad))} (teach them first, or mark {{preview}})'))
        if r['type'] == 'name':
            continue
        base, _, tag = vi.nfc(r['word']).partition('~')
        k = base_key(r['word'])
        lx = by_cid.get(vi.card_id(k, tag or None)) or (by_key.get(k) or [None])[0]
        if lx:
            for col in ('usage', 'false_friend'):
                bad = late(lx[col], n)
                if bad:
                    msgs.append(('E', f'course/lexicon.tsv:{lx["n"]}: E {lx["key"]} (L{n}) {col} note uses words not '
                                      f'yet taught: {", ".join(dict.fromkeys(bad))} (mark {{preview}})'))
            if verbose and lx.get('example'):
                bad = late(lx['example'], n)
                if bad:
                    msgs.append(('I', f'course/lexicon.tsv:{lx["n"]}: I {lx["key"]} (L{n}) example uses '
                                      f'{", ".join(dict.fromkeys(bad))}'))
    for n, L in plans.items():
        if n > last:
            continue
        for col in ('vi', 'grammar', 'strand'):
            bad = late(L.get(col) or '', n)
            if bad:
                msgs.append(('E', f'course/syllabus.yaml: E lesson {n} {col} uses words not yet taught: '
                                  f'{", ".join(dict.fromkeys(bad))}'))
    for p in syl.get('particles') or []:
        n, w = p['n'], vi.key(p['w'])
        if n <= last and any(taught.get(s, 999) > n for s in w.split()):
            msgs.append(('E', f'course/syllabus.yaml: E particle {p["w"]} enters at L{n} but the word list teaches it '
                              f'at L{max(taught.get(s, 999) for s in w.split())}'))
        if not re.search(rf'(?<!\w){re.escape(p["w"])}(?!\w)', (plans.get(n) or {}).get('grammar', ''), re.I):
            msgs.append(('E', f'course/syllabus.yaml: E particle {p["w"]}: lesson {n}\'s grammar does not name it'))
    return msgs


# ---------------------------------------------------------------------------------------------------------- render
def tra_che(con):
    f = dict(con.execute("SELECT key, max(freq) FROM entry WHERE key IN ('trà', 'chè') AND source = 'wiktionary' "
                         "GROUP BY key"))
    r = dict(con.execute("SELECT key, min(freq_rank) FROM entry WHERE key IN ('trà', 'chè') AND source = 'wiktionary' "
                         "GROUP BY key"))
    return (f"trà {f.get('trà', 0):,} against chè {f.get('chè', 0):,} per billion words (course ranks {r.get('trà')} and "
            f"{r.get('chè')}; tools/freq.py, chè counting the dessert too)")


def lesson_table(syl, rows):
    cnt = counts(rows)
    out = ['| # | Situation | Grammar | Bridge / false friend | Lines | New: nat / HV / oth |',
           '|---|---|---|---|---|---|']
    for L in syl.get('lessons') or []:
        n = L['n']
        if L.get('review'):
            new = '—'
        elif n in cnt:
            c = cnt[n]
            new = f"{c['native'] - c['other']} / {c['hv']} / {c['other']}"
        else:
            nw = L.get('new_words') or {}
            new = f"{nw.get('native', 0) - nw.get('other', 0)} / {nw.get('hv', 0)} / {nw.get('other', 0)}"
        title = f"**{L['en']}**" if L.get('review') else L['en']
        out.append(f"| {n} | {title} | {L.get('grammar', '')} | {L.get('bridge') or '—'} | {L.get('lines', '')} | {new} |")
    return '\n'.join(out)


def particle_table(syl):
    out = ['| Particle | Lesson | Use |', '|---|---|---|']
    for p in syl.get('particles') or []:
        out.append(f"| {p['w']} | L{p['n']} | {p['use']} |")
    return '\n'.join(out)


def list_name(path, syl=None):
    """"Word list 2" for course/proposal/wordlist-2.tsv; ", draft" when the owner has not approved it."""
    m = re.search(r'wordlist-(\d+)', path or '')
    name = f'Word list {m.group(1)}' if m else f'Word list {os.path.basename(path or "")}'
    return name, (path not in course.approved_word_lists(syl)) if path else False


def list_counts(rows):
    """One sentence per word list of the plan (rows grouped by their `file`)."""
    files = list(dict.fromkeys(r.get('file') for r in rows))
    return ' '.join(_list_counts([r for r in rows if r.get('file') == f], f) for f in files)


def _list_counts(rows, path):
    cnt = counts(rows)
    names = sum(1 for r in rows if r['type'] == 'name')
    words = len(rows) - names
    hv = sum(c['hv'] for c in cnt.values())
    other = sum(c['other'] for c in cnt.values())
    older = sum(1 for r in rows if r['type'].startswith('older Chinese loan'))
    doubt = sum(1 for r in rows if r['type'] == 'older Chinese loan (doubtful)')
    unknown = sum(1 for r in rows if r['type'] == 'unknown')
    per = ', '.join(f"L{n} {c['native'] + c['hv']}" for n, c in sorted(cnt.items()))
    name, draft = list_name(path) if path else ('Word list 2', False)
    return (f"{name} ({'draft, not approved; ' if draft else ''}L{min(cnt)}–{max(cnt)}): {words} words + {names} names ({per}); Hán-Việt {hv} "
            f"({100 * hv / words:.0f} %), older Chinese loans {older} ({doubt} with a doubtful etymon, characters hidden), "
            f"Western loans {other - older}, the rest native, compounds and {unknown} with no etymology recorded.")


def blocks(con):
    syl, rows, _ = load()
    return {'lessons': lesson_table(syl, rows), 'particles': particle_table(syl), 'counts': list_counts(rows),
            'tra-che': tra_che(con)}


def rewrite(text, bl):
    return re.sub(r'<!-- plan:([\w-]+) -->.*?<!-- /plan -->',
                  lambda m: f'<!-- plan:{m.group(1)} -->' + ('\n' if '\n' in bl[m.group(1)] else '') + bl[m.group(1)]
                  + ('\n' if '\n' in bl[m.group(1)] else '') + '<!-- /plan -->', text, flags=re.S)


def new_syllabus():
    syl, rows, _ = load()
    cnt = counts(rows)
    for L in syl.get('lessons') or []:
        if L['n'] in cnt:
            c = cnt[L['n']]
            L['new_words'] = {'native': c['native'], 'hv': c['hv'], **({'other': c['other']} if c['other'] else {})}
    return dump_syllabus(syl, syllabus_head())


def outputs(con):
    syl = course.syllabus()
    prop = os.path.join(ROOT, (syl.get('draft') or {}).get('proposal') or 'course/proposal/syllabus-proposal.md')
    bl = blocks(con)
    out = {SYLLABUS: new_syllabus()}
    for p in (prop, TO_CHECK):
        if os.path.exists(p):
            out[p] = rewrite(open(p, encoding='utf-8').read(), bl)
    return out


def main():
    import cards
    con = cards.open_db('public')
    if '--write' in sys.argv:
        for p, text in outputs(con).items():
            old = open(p, encoding='utf-8').read() if os.path.exists(p) else ''
            if text != old:
                open(p, 'w', encoding='utf-8').write(text)
                print(f'{os.path.relpath(p, ROOT)}: rewritten')
        return 0
    msgs = check(con, verbose='--verbose' in sys.argv)
    for p, text in outputs(con).items():
        if os.path.exists(p) and open(p, encoding='utf-8').read() != text:
            msgs.append(('E', f'{os.path.relpath(p, ROOT)}: E not as tools/plan.py --write would write it'))
    for lv, m in msgs:
        print(m)
    e = sum(1 for lv, _ in msgs if lv == 'E')
    print(f'plan: {e} error(s)')
    return 1 if e else 0


if __name__ == '__main__':
    sys.exit(main())
