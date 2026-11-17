"""Check typed Vietnamese words against the dictionary database and print a short list of suspects.

  python3 -I tools/verify_words.py --lessons        # every word of the lessons (lines, exercises, new_words): `make lint`
  python3 -I tools/verify_words.py words.tsv        # word <TAB> English [<TAB> chữ Hán], one per line (a word list)
  python3 -I tools/verify_words.py < words.tsv      # the same from stdin
  options: --db PATH (default data/build/vi.db), --all (every suspect, not the first 60 of each class),
           --strict (exit 1 when there is any suspect of class 1–3)

Classes, most serious first:
  1 spelling        not NFC, or not a possible quốc ngữ syllable (tools/vi.py syllable_problems)
  2 tone            not in the dictionary, but a dictionary word differs only by its tones (likely a typo)
  3 nodict          not in any dictionary (names declared in new_words are left out)
  4 join            two or more neighbouring words of a line that the dictionary has as ONE word (học sinh written as
                    two words): the line's boundaries may be wrong
  5 chars           chữ Hán given for the word whose Hán-Việt readings (table hanviet) do not give its syllables
  6 fixture         a word only the test fixture has, outside the fixture
  7 hv_suspect      (whole database, --lessons) a Sino-Vietnamese analysis whose characters do not match the word's
                    syllables (number or Hán-Việt readings): not shown as "same word" on the card
  8 hv_none         (whole database, --lessons) a character of a Sino-Vietnamese entry that no source reads in
                    Hán-Việt (the card shows "—", never "?")
Nothing here changes any file: it only prints (Tsheh-tû's verifier found 27 misread characters this way).
"""
import collections
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import course  # noqa: E402
import vi  # noqa: E402

CLASSES = [('spelling', 'spelling (NFC, impossible syllable)'), ('tone', 'only the tones differ from a dictionary word'),
           ('nodict', 'in no dictionary'), ('join', 'the dictionary has these neighbouring words as one word'),
           ('chars', 'chữ Hán whose Hán-Việt readings do not give the word'), ('fixture', 'only in the test fixture'),
           ('hv_suspect', 'dictionary: Sino-Vietnamese analysis not matching the syllables (not shown as same word)'),
           ('hv_none', 'dictionary: character with no Hán-Việt reading')]


class Dict:
    def __init__(self, path):
        con = sqlite3.connect(path)
        self.keys = collections.defaultdict(set)      # key -> {is fixture}
        self.by_toneless = collections.defaultdict(set)
        for k, tl, fx in con.execute('SELECT e.key, e.toneless, s.fixture FROM entry e JOIN source s ON s.id = e.source'):
            self.keys[k].add(bool(fx))
            self.by_toneless[tl].add(k)
        self.hv = collections.defaultdict(set)
        for ch, r in con.execute("SELECT char, reading FROM hanviet WHERE kind IN ('hv', 'hannom')"):
            self.hv[ch].add(vi.tkey(r))


def check_word(D, word, label, out, chars=None, fixture_ok=False):
    """One typed word (with underscores or spaces between syllables)."""
    w = vi.nfc(word)
    k = vi.key(w)
    if w != word:
        out['spelling'].append((label, word, 'not NFC'))
    probs = [p for s in k.split() for p in vi.syllable_problems(s)]
    if probs:
        out['spelling'].append((label, word, '; '.join(probs)))
    if k not in D.keys:
        near = sorted(D.by_toneless.get(vi.toneless(k), ()))
        if near:
            out['tone'].append((label, word, 'dictionary: ' + ', '.join(near[:5])))
        else:
            out['nodict'].append((label, word, ''))
    elif D.keys[k] == {True} and not fixture_ok:
        out['fixture'].append((label, word, ''))
    if chars and D.hv:
        syls = [vi.tkey(s) for s in k.split()]
        cs = [c for c in chars if vi.CJK.match(c)]
        if len(cs) != len(syls):
            out['chars'].append((label, word, f'{chars}: {len(cs)} characters for {len(syls)} syllables'))
        else:
            bad = [f'{c} is not read {s}' if D.hv.get(c) else f'no Hán-Việt reading known for {c}'
                   for c, s in zip(cs, syls) if s not in D.hv.get(c, ())]
            if bad:
                out['chars'].append((label, word, f'{chars}: ' + '; '.join(bad)))


def check_line(D, text, label, out, names, fixture_ok):
    ws = [t for t in vi.words(text) if t[0] == 'w']
    for _, surf, k, tag, _ in ws:
        if surf.replace('_', ' ') in names:
            continue
        check_word(D, surf, label, out, fixture_ok=fixture_ok)
    # neighbouring words that the dictionary has as one word (up to 4 syllables in all)
    plain = [t[2] for t in ws]
    for i in range(len(plain)):
        for j in range(i + 2, min(len(plain), i + 4) + 1):
            k = ' '.join(plain[i:j])
            if len(k.split()) <= vi.MAX and k in D.keys and not (D.keys[k] == {True} and not fixture_ok):
                out['join'].append((label, ' + '.join(plain[i:j]), f'dictionary word: {k}'))


def lessons(D, out):
    ls = [(f, course.load(f)) for f in course.lesson_files()]
    names = {vi.nfc(w['w']).replace('_', ' ') for _, d in ls for w in d.get('new_words') or [] if w.get('name')}
    n = 0
    for f, d in ls:
        lid = f"{'fixture ' if d.get('fixture') else ''}L{d.get('id')}"
        fx = bool(d.get('fixture'))
        for ln in d.get('dialogue') or []:
            check_line(D, ln.get('vi') or '', f"{lid}.{ln.get('n')}", out, names, fx)
            n += 1
        for kind, items in (d.get('exercises') or {}).items():
            for j, it in enumerate(items or []):
                t = (it.get('vi') or '').replace('___', str(it.get('answer', '')).replace(' ', '_'))
                check_line(D, t, f'{lid}.{kind}{j + 1}', out, names, fx)
                n += 1
        for w in d.get('new_words') or []:
            if not w.get('name'):
                check_word(D, w['w'], f'{lid}.new_words', out, w.get('chars'), fx)
    return n


def database_suspects(db, out):
    """Classes 7 and 8: suspects of the dictionary itself (tools/build_db.py word_checks)."""
    import bridge
    con = sqlite3.connect(db)
    for src, word, chars, chk in con.execute("SELECT source, word, chars, hv_check FROM entry WHERE hv_check IN "
                                             "('differs', 'length') ORDER BY freq_rank IS NULL, freq_rank"):
        why = (f'{len(chars)} characters for {len(word.split())} syllables' if chk == 'length' else
               '; '.join(f'{c} {"/".join(bridge.hv_readings(con, c)) or "—"}' for c in chars))
        out['hv_suspect'].append((src, f'{word} {chars}', why))
    seen = set()
    for (chars,) in con.execute("SELECT DISTINCT chars FROM entry WHERE chars != '' AND hv_check NOT IN "
                                "('differs', 'length')"):
        for c in chars:
            if c not in seen and not bridge.hv_readings(con, c):
                seen.add(c)
                out['hv_none'].append(('dictionary', c, f'in {chars}'))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    db = sys.argv[sys.argv.index('--db') + 1] if '--db' in sys.argv else (
        os.environ.get('TUSACH_DB') or os.path.join(ROOT, 'data/build/vi.db'))
    if '--db' in sys.argv:
        args = [a for a in args if a != db]
    D = Dict(db)
    out = collections.defaultdict(list)
    if '--lessons' in sys.argv:
        n = lessons(D, out)
        database_suspects(db, out)
        what = f'{n} lesson lines and exercises'
    else:
        src = open(args[0], encoding='utf-8') if args else sys.stdin
        n = 0
        for i, row in enumerate(src, 1):
            if not row.strip() or row.startswith('#'):
                continue
            cols = row.rstrip('\n').split('\t')
            check_word(D, cols[0], f'line {i}', out, cols[2] if len(cols) > 2 else None)
            n += 1
        what = f'{n} words'
    limit = None if '--all' in sys.argv else 60
    total = 0
    for cls, title in CLASSES:
        items = list(dict.fromkeys(out.get(cls, [])))
        if not items:
            continue
        total += len(items)
        print(f'== {CLASSES.index((cls, title)) + 1} {title}: {len(items)}')
        for label, word, why in items[:limit]:
            print(f'  {label}\t{word}\t{why}')
        if limit and len(items) > limit:
            print(f'  … {len(items) - limit} more (--all)')
    print(f'verify_words: {what} checked, {total} suspect(s)')
    serious = sum(len(out.get(c, [])) for c in ('spelling', 'tone', 'nodict'))
    sys.exit(1 if '--strict' in sys.argv and serious else 0)


if __name__ == '__main__':
    main()
