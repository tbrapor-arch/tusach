"""The one thing a lesson writer (or reviewer) reads (26 Nov 2026): rules digest, plan, cast, particle strand, every
word taught so far, the story so far, the two lessons before; and the cheap lookups beside it.

    python3 -I tools/brief.py 29 35              # the writer's brief for lessons 29-35
    python3 -I tools/brief.py --review 29 35     # the reviewer's: the same digest and words, then lessons 29-35 compactly
    python3 -I tools/brief.py --where học_sinh 'ăn cơm' đường~road   # where a word is first taught and first used
    python3 -I tools/brief.py --untaught [TOP] [--before N]           # frequent words not yet taught (default 120)
    python3 -I tools/brief.py --doubts [N M]     # every lesson's `doubt` entries: the list for a native speaker

Words are course keys (tools/vi.py key, the spelling groups of tools/cards.py canon, `~tag`): no second cutter. The
brief ends with its own size in characters (target: under about 45,000, some 15k tokens).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import course  # noqa: E402
import vi  # noqa: E402

RULES = """\
## Rules (digest of CLAUDE.md, docs/REFERENCE.md "Lesson format" and what tools/lint.py refuses)
Vietnamese first. Northern (Hà Nội) speech; lessons in English; Claude's text, labelled not native-checked.
File course/lessons/NN.yaml (file name = id; nothing else there). Keys: id, title {vi, en}, review, setting (English,
one or two sentences), dialogue, notes, new_words, exercises, doubt (optional). Copy course/lesson_template.yaml.
Text: Unicode NFC. QUOTE every flow value with a comma or a colon: {w: tôi, en: "I, me"} (else: unknown key, error).
Dialogue {n, speaker, vi, en, lit?}: lit is a word-for-word gloss where the order differs. Lines: the plan's (+-1),
  growing smoothly (+0 to +2 on the last non-review lesson). Speakers: the cast below, or a role (Landlady, Clerk).
Word boundaries: underscores join one word's syllables (học_sinh, Hà_Nội, cảm_ơn), spaces separate words, as in
  docs/SEGMENTATION.md; lint warns on a course word written apart (cảm ơn): usually a missing underscore.
Homographs: word~tag (đường~road, năm~year, ba~three, tầng ba~three). A word with several lexicon senses, or several
  dictionary etymologies and no lexicon row, MUST carry its tag (error); a tag names a lexicon row, a dictionary tag,
  a part of speech (phải~verb) or a word of one etymology's English.
Spelling: impossible syllables are errors; house spelling (lý do, công ty, kỹ thuật, Mỹ; but bác sĩ, bánh mì);
  traditional tone marks (hòa, khỏe, thủy, mùa, hoàn). No chữ Hán in vi lines, titles or exercises.
Every word of a line or exercise is a new word of this lesson or an earlier one (the list below). Names: declared
  once, with name: true in new_words (cast already declared: below). Numbers are not words.
Review lessons (every 7th, review: true): no new word at all; recombine the last six lessons; recap notes.
New words (chosen while you write; the list is generated afterwards and approved by the owner):
- {w, en, tag?, name?}; en on every word: it is what the card shows (short, card-ready; quote it).
- Counts per lesson: the plan's native / hv (Hán-Việt) +-1, Hán-Việt share within 0.2 (other = older and Western
  loans, counted in native). Choose what the scene, the grammar and the bridge need; the frequent untaught words
  below are the pool (more: --untaught 400). Check a card first: make lookup W=word.
- Each new word appears in the dialogue or an exercise. Never one already taught, or in an approved list (error).
- Never chars / label in new_words (error): an origin or a characters claim is a lexicon row.
- A course/lexicon.tsv row (columns in tools/lexicon.py) ONLY where the dictionary alone gives a wrong or poor card:
  several senses (write the row of the sense taught, tag it); a false friend (false_friend column); an origin or
  characters claim (an hv word your bridge note pairs with characters, unless its card is already labelled same);
  lint's warning "the dictionary card says …" (another sense or a poor gloss). example/example_en are optional
  (the card falls back to the dictionary's). A row must pass tools/lexicon.py (lint); honest confidence
  (doubt: reason); its usage / false-friend notes use taught words only, or {preview}.
Notes (about 9; topics grammar, usage, pronouns, particles, bridge, false-friend):
- {ref: line n, or 0 for a recap; topic; text}. A Vietnamese word in a note or a gloss must be taught by this lesson
  or earlier, else written {in braces} (a preview, shown without braces). Cast names and grammar terms pass.
- ONE bridge note (topic bridge), one or two lines, on a word he knows, Mandarin first, then Cantonese, Taigi. Its
  chữ Hán: the same word in Chinese for the sense taught (lexicon hv / hv-gram not doubtful, or card label same /
  gram), next to its Vietnamese word ("học sinh is 學生"); "phải is 被" kinds are refused. Characters, not pinyin
  runs; avoid romanisations that read as Vietnamese (gam2, tóng, sim).
- At most one false-friend note (topic false-friend), on a word whose lexicon row has false_friend: its characters
  next to it; other characters only from that note.
- Particles: as the strand below; Northern forms (no final nha / vậy before L67). Person terms of one sentence form
  a pair (anh-em, chị-em, bác-cháu, ông/bà/chú/cô-cháu; tôi with any): lint warns otherwise.
Exercises (about 5 translate + 3 fill): translate {vi, en}; fill {vi with ___, answer, en}; one right answer per
  fill (hint the register in en: "(to someone older)"). NEW sentences: not a dialogue line of this or an earlier
  lesson, not inside one, not one minus its greeting or first clause, not a note example, not the example a card of
  its words shows (errors; a warning at similarity 0.8).
Doubts: doubt: [{line: n (0 = the lesson) or "exercises.fill[1]", text: "…"}]: your hesitations for a native speaker,
  never shown (brief.py --doubts collects them). NOTES-for-native-speaker.md is no longer extended.
Check: make lint-lesson L=N-M until 0 errors; read its warnings and the verifier's suspects (a "join" often means a
  missing underscore). Before a commit: make lint, make test, make app. Then (once per batch): tools/wordlist.py
  --from-lessons N M course/proposal/wordlist-K.tsv writes the list and the owner's approval table.
"""


def load_lessons():
    return [d for d in course.lessons() if not d.get('fixture') and isinstance(d.get('id'), int)]


def short(en, n=28):
    en = re.sub(r'\s*\([^)]*\)', '', en or '').split(';')[0].strip() or (en or '')
    return en if len(en) <= n else en[:n].rsplit(' ', 1)[0] + '…'


def wtag(w):
    return w['w'] + (f"~{w['tag']}" if w.get('tag') else '')


def taught_section(ls, n):
    out = [f'## Words taught before L{n} (word=English, by lesson; names apart)']
    names = []
    for d in ls:
        if d['id'] >= n:
            continue
        ws = [f'{wtag(w)}={short(w.get("en"))}' for w in d.get('new_words') or [] if w.get('w') and not w.get('name')]
        names += [w['w'] for w in d.get('new_words') or [] if w.get('name')]
        if ws:
            out.append(f'L{d["id"]}: ' + ' · '.join(ws))
    out.append('Names: ' + ', '.join(names))
    return out


def plan_section(syl, a, b):
    out = ['## Plan (course/syllabus.yaml)']
    prop = os.path.join(ROOT, (syl.get('draft') or {}).get('proposal') or 'course/proposal/syllabus-proposal.md')
    rules = {}
    if os.path.exists(prop):
        for line in open(prop, encoding='utf-8'):
            m = re.match(r'\| ([A-Z]{1,2}\d+) \| ([^|]*)\|[^|]*\| ([^|]*)\|', line)
            if m:
                rules.setdefault(m.group(1), f'{m.group(1)}: {m.group(2).strip()} ({m.group(3).strip()})')
    for p in syl.get('lessons') or []:
        if not a <= p['n'] <= b:
            continue
        nw = p.get('new_words') or {}
        bits = [f"L{p['n']} {p.get('en', '')}" + (' (REVIEW)' if p.get('review') else ''), f"grammar: {p.get('grammar', '')}"]
        if p.get('bridge'):
            bits.append(f"bridge: {p['bridge']}")
        if p.get('strand'):
            bits.append(f"strand: {p['strand']}")
        bits.append(f"lines {p.get('lines')}; new words native {nw.get('native', 0)} (other {nw.get('other', 0)}), "
                    f"hv {nw.get('hv', 0)}")
        out.append(' | '.join(bits))
        for code in re.findall(r'\b([A-Z]{1,2}\d+)\b', p.get('bridge') or ''):
            if code in rules:
                out.append(f'    rule {rules[code]}')
    out.append('Cast: ' + ', '.join(syl.get('cast') or []))
    parts = syl.get('particles') or []
    out.append('Particles already in: ' + ', '.join(f"{p['w']} (L{p['n']})" for p in parts if p['n'] < a))
    for p in parts:
        if a <= p['n'] <= b:
            out.append(f"Particle at L{p['n']}: {p['w']}: {p['use']}")
    return out


def story_section(ls, n):
    out = ['## Story so far (settings)']
    for d in ls:
        if d['id'] < n:
            s = ' '.join((d.get('setting') or '').split())
            out.append(f"L{d['id']} {d['title'].get('en', '')}: {s[:110] + ('…' if len(s) > 110 else '')}")
    return out


def dialogue(d, lit=False):
    out = [f"### L{d['id']} {d['title'].get('vi', '')} / {d['title'].get('en', '')}" + (' (review)' if d.get('review')
                                                                                         else '')]
    for ln in d.get('dialogue') or []:
        out.append(f"{ln.get('n')} {ln.get('speaker', '')}: {ln.get('vi', '')} | {ln.get('en', '')}"
                   + (f" | lit: {ln['lit']}" if lit and ln.get('lit') else ''))
    return out


def compact(d):
    out = dialogue(d, lit=True)
    out.insert(1, 'setting: ' + ' '.join((d.get('setting') or '').split()))
    for nt in d.get('notes') or []:
        out.append(f"note {nt.get('ref')} {nt.get('topic', '')}: {nt.get('text', '')}")
    out.append('new: ' + ' · '.join(f"{wtag(w)}={w.get('en', '')}" + (' (name)' if w.get('name') else '')
                                    for w in d.get('new_words') or []))
    for kind, items in (d.get('exercises') or {}).items():
        for it in items or []:
            out.append(f"{kind}: {it.get('vi', '')}" + (f" [{it['answer']}]" if it.get('answer') else '')
                       + f" | {it.get('en', '')}")
    for dt in d.get('doubt') or []:
        out.append(f"doubt {dt.get('line')}: {dt.get('text', '')}")
    return out


# ------------------------------------------------------------------------------------------------------- lookups
def _cards():
    import cards
    cards.init(cards.open_db('public'))
    return cards


def taught_keys(ls, before=None):
    """{card key: first lesson} of the new words (every tag of a key counts) of the lessons before `before`."""
    import cards
    out = {}
    for d in ls:
        if before is not None and d['id'] >= before:
            continue
        for w in d.get('new_words') or []:
            if w.get('w') and not w.get('name'):
                out.setdefault(cards.canon(vi.key(w['w'])), d['id'])
    return out


def untaught(ls, top=120, before=None, card_en=True):
    """[(rank, word, English, label)] of the most frequent dictionary words no lesson (before `before`) teaches."""
    cards = _cards()
    have = taught_keys(ls, before)
    names = {vi.key(w['w']) for d in ls for w in d.get('new_words') or [] if w.get('name')}
    out = []
    for k, rank in cards.con.execute(
            "SELECT e.key, min(e.freq_rank) FROM entry e JOIN source s ON s.id = e.source WHERE s.fixture = 0 AND "
            "e.freq_rank IS NOT NULL AND e.pos NOT IN ('name', 'character-reading') GROUP BY e.key "
            "ORDER BY min(e.freq_rank)"):
        k = cards.canon(k)
        if k in have or k in names or vi.syllable_problems(k.split()[0]):
            continue
        have[k] = 0
        cid = cards.lookup(k) if card_en else None
        c = cards.dictionary.get(cid) or {}
        out.append((rank, k.replace(' ', '_'), short(c.get('en', ''), 34), c.get('label', '')))
        if len(out) >= top:
            break
    return out


def where(ls, word):
    """Where a word is first taught (new_words), first used (lines, exercises) and listed (word lists)."""
    cards = _cards()
    base, _, tag = vi.nfc(word).partition('~')
    k = cards.canon(vi.key(base.replace('_', ' ')))
    taught, used = [], None
    for d in ls:
        for w in d.get('new_words') or []:
            if w.get('w') and cards.canon(vi.key(w['w'])) == k and (not tag or w.get('tag') == tag):
                taught.append(f"L{d['id']} {wtag(w)} \"{w.get('en', '')}\"")
        if used is None:
            texts = [(f"{d['id']}.{ln.get('n')}", ln.get('vi') or '') for ln in d.get('dialogue') or []]
            texts += [(f"{d['id']}.{kind}{j + 1}", (it.get('vi') or '').replace('___', str(it.get('answer', ''))))
                      for kind, items in (d.get('exercises') or {}).items() for j, it in enumerate(items or [])]
            for place, text in texts:
                if any(t[0] == 'w' and cards.canon(t[2]) == k and (not tag or t[3] == tag) for t in vi.words(text)):
                    used = f'L{place}'
                    break
    listed = []
    for p in course.plan_word_lists():
        for r in course.wordlist(p):
            rb, _, rt = vi.nfc(r['word']).partition('~')
            if cards.canon(vi.key(rb.replace('_', ' '))) == k and (not tag or rt == tag):
                listed.append(f"{os.path.basename(p)} L{r['lesson']}")
    rank = cards.con.execute('SELECT min(freq_rank) FROM entry WHERE key=?', (k,)).fetchone()[0]
    cid = cards.lookup(k, tag or None)
    en = (cards.dictionary.get(cid) or {}).get('en', '') if cid else ''
    parts = ''
    if not taught and ' ' in k:                  # a free sequence of taught words? (ăn cơm: ăn L?, cơm L?)
        have = taught_keys(ls)
        parts = '; parts: ' + ', '.join(f"{s} {'L' + str(have[s]) if s in have else 'untaught'}" for s in k.split())
    return (f"{word}: taught {'; '.join(taught) or 'never'}; first used {used or 'never'}; "
            f"listed {', '.join(listed) or 'no'}; rank {rank or '-'}; card: {short(en, 60) or '(no card)'}{parts}")


def doubts(ls, a=None, b=None):
    out = []
    for d in ls:
        if a is not None and not a <= d['id'] <= b:
            continue
        for dt in d.get('doubt') or []:
            out.append(f"- L{d['id']}.{dt.get('line')}: {dt.get('text', '')}")
    return out


# ---------------------------------------------------------------------------------------------------------- main
def brief(a, b, review=False):
    ls = load_lessons()
    syl = course.syllabus()
    by = {d['id']: d for d in ls}
    out = [f"# {'Review' if review else 'Writer'}'s brief: lessons {a}-{b} (tools/brief.py; read this, not the files)",
           '']
    out += RULES.rstrip('\n').split('\n') + ['']
    out += plan_section(syl, a, b) + ['']
    out += taught_section(ls, a) + ['']
    if review:
        out.append(f'## Lessons {a}-{b} as written')
        for n in range(a, b + 1):
            if n in by:
                out += compact(by[n]) + ['']
        out.append('Fix high and medium faults directly; list them in the commit message (no findings file).')
    else:
        pool = untaught(ls, 120, a)
        out.append('## Frequent words not yet taught (rank word=English label; more: --untaught 400)')
        out += [' · '.join(f'{r} {w}={en}' + (f' [{lab}]' if lab else '') for r, w, en, lab in pool[i:i + 6])
                for i in range(0, len(pool), 6)] + ['']
        out += story_section(ls, a) + ['']
        out.append('## The two lessons before (vi | en)')
        for n in (a - 2, a - 1):
            if n in by:
                out += dialogue(by[n])
        out.append('')
        if a in by or b in by:
            out.append(f'(Lessons {", ".join(str(n) for n in range(a, b + 1) if n in by)} exist already: '
                       f'brief.py --review {a} {b} shows them.)')
    text = '\n'.join(out) + '\n'
    sys.stdout.write(text)
    print(f'[brief: {len(text):,} characters]')


def main():
    args = sys.argv[1:]
    ls = None
    if args[:1] == ['--where'] and len(args) > 1:
        ls = load_lessons()
        for w in args[1:]:
            print(where(ls, w))
    elif args[:1] == ['--untaught']:
        before = int(args[args.index('--before') + 1]) if '--before' in args else None
        nums = [int(x) for x in args[1:] if x.isdigit() and x != str(before)]
        for r, w, en, lab in untaught(load_lessons(), nums[0] if nums else 120, before):
            print(f'{r}\t{w}\t{en}\t{lab}')
    elif args[:1] == ['--doubts']:
        nums = [int(x) for x in args[1:]]
        out = doubts(load_lessons(), *(nums[:2] if len(nums) >= 2 else ()))
        print('\n'.join(out) if out else 'no doubt recorded in the lessons')
    elif args[:1] == ['--review'] and len(args) == 3:
        brief(int(args[1]), int(args[2]), review=True)
    elif len(args) == 2 and all(x.isdigit() for x in args):
        brief(int(args[0]), int(args[1]))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
