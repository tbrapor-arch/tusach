"""Check the lesson files: content rules and every word against the database.

  python3 -I tools/lint.py [lesson.yaml ...]      (default: course/lessons/NN.yaml, or the test fixture while there is none)

Checks (E = error, exit 1; W = warning; I = information)
  E  a lesson exists while the syllabus or the first word list is not approved by the owner (course/syllabus.yaml)
  E  YAML error, missing field, file name not the lesson id, two lessons with one id
  E  a file in course/lessons/ not named NN.yaml; `fixture: true` outside tools/fixtures/
  E  an unknown key or a key with no value in a lesson item: a YAML flow mapping cut at an unquoted comma
     ({w: tôi, en: I, me} reads as en: I plus a key "me"): quote the text
  E  text not in Unicode NFC (every string of the file)
  E  chữ Hán in a lesson line, a title or an exercise sentence (characters belong on cards and in the bridge)
  E  impossible quốc ngữ syllable (tools/vi.py): letters, c/k, g/gh, ng/ngh, -c -ch -p -t with a tone other than sắc/nặng
  E  tone mark not placed in the house style (hòa, khỏe, thủy: docs/REFERENCE.md); keys ignore the placement
  E  word in no dictionary of the database and not declared as a name in new_words
  E  word that only the test fixture has, in a real lesson
  E  `~tag` that no dictionary entry and no new_words entry defines
  E  new_words entry without English (English on every card), or not used in the lesson
  E  exercise sentence taken from the dialogue: equal to a line, contained in a line, or equal to one after removing a
     greeting / first clause (normalised: case, punctuation, word boundaries)
  W  exercise sentence very similar to a dialogue line (similarity >= SIMILAR): check it is a new sentence
  E  note pointing to a line the dialogue does not have
  E  fill exercise without ___ or answer
  W  lines per lesson do not grow smoothly (owner's choice: a smooth growth; checked over the non-review lessons)
  W  review flag not on every 7th lesson
  I  lesson not checked by a native speaker (no native_check: {by, date}); the app labels it
The words of the lines are also checked by tools/verify_words.py (`make lint` runs both).
"""
import collections
import os
import re
import sqlite3
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import course  # noqa: E402
import vi  # noqa: E402

DB = os.environ.get('TUSACH_DB') or os.path.join(ROOT, 'data/build/vi.db')
REQUIRED = ('id', 'title', 'dialogue', 'notes', 'new_words')
KEYS = {'top': {'id', 'title', 'review', 'setting', 'native_check', 'dialogue', 'notes', 'new_words', 'exercises',
                'fixture'},
        'title': {'vi', 'en'}, 'dialogue': {'n', 'speaker', 'vi', 'en'}, 'notes': {'ref', 'topic', 'text'},
        'new_words': {'w', 'en', 'tag', 'chars', 'label', 'name'}, 'translate': {'vi', 'en'},
        'fill': {'vi', 'answer', 'en'}, 'native_check': {'by', 'date'}}
SIMILAR = 0.8


def norm_tokens(text):
    """Word keys of a line, without punctuation or case: the unit of the exercise-copy check."""
    return [t[2] for t in vi.words(text) if t[0] == 'w']


def clauses(text):
    """The clauses of a line (split at , ; : ! ? . …), each as a token list."""
    return [c for c in (norm_tokens(x) for x in re.split(r'[,;:!?.…]+', vi.display(text))) if c]


def copied(ex, line):
    """'copy' when the exercise is a dialogue line, part of one, or one without its first clause (or the other way
    round); a similarity ratio otherwise."""
    import difflib
    e, l_ = norm_tokens(vi.display(ex)), norm_tokens(vi.display(line))
    if not e or not l_:
        return 0.0

    def inside(a, b):
        return len(a) >= 2 and any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))
    ec, lc = clauses(ex), clauses(line)
    e_rest = [t for c in ec[1:] for t in c]
    l_rest = [t for c in lc[1:] for t in c]
    if e == l_ or inside(e, l_) or (e_rest and (e_rest == l_ or inside(e_rest, l_))) or (l_rest and e == l_rest):
        return 'copy'
    return difflib.SequenceMatcher(None, e, l_).ratio()


def check_keys(m, where, item, kind):
    if not isinstance(item, dict):
        return
    for k, v in item.items():
        if k not in KEYS[kind]:
            m('E', where, f'unknown key "{k}"' + (' (an unquoted comma in a flow mapping cut the text before it: '
                                                   'quote the value)' if v is None else ''))
        elif v is None and k != 'native_check':
            m('E', where, f'"{k}" has no value')


def load_db():
    con = sqlite3.connect(DB)
    keys = collections.defaultdict(set)     # key -> {(source is fixture)}
    tags = collections.defaultdict(set)
    for k, tag, fx in con.execute('SELECT e.key, e.tag, s.fixture FROM entry e JOIN source s ON s.id = e.source'):
        keys[k].add(bool(fx))
        if tag:
            tags[k].add(tag)
    return keys, tags


def strings(o, path=''):
    if isinstance(o, str):
        yield path, o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from strings(k, path) if isinstance(k, str) else ()
            yield from strings(v, f'{path}.{k}' if path else str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings(v, f'{path}[{i}]')


def lint(path, d, keys, tags, all_tags, names, msgs, spellings):
    def m(level, where, text):
        msgs.append((level, f'{os.path.relpath(path, ROOT)}:{where}: {level} {text}'))

    for f in REQUIRED:
        if f not in d:
            m('E', 0, f'missing field: {f}')
    if d.get('fixture_claimed'):
        m('E', 0, '`fixture: true` is accepted only under tools/fixtures/, never in course/lessons/')
    check_keys(m, 0, {k: v for k, v in d.items() if k != 'fixture_claimed'}, 'top')
    if isinstance(d.get('title'), dict):
        check_keys(m, 'title', d['title'], 'title')
    if isinstance(d.get('native_check'), dict):
        check_keys(m, 'native_check', d['native_check'], 'native_check')
    for kind in ('dialogue', 'notes', 'new_words'):
        for i, it in enumerate(d.get(kind) or []):
            check_keys(m, f'{kind}[{i}]', it, kind)
    for kind, items in (d.get('exercises') or {}).items():
        if kind in KEYS:
            for i, it in enumerate(items or []):
                check_keys(m, f'exercises.{kind}[{i}]', it, kind)
    real = not d.get('fixture')
    name = os.path.basename(path)
    if not re.fullmatch(r'\d\d+\.yaml', name) or int(name.split('.')[0]) != d.get('id'):
        m('E', 0, f'file name {name} does not match id {d.get("id")} (NN.yaml)')
    for where, s in strings(d):
        if not vi.is_nfc(s):
            m('E', where, f'not in Unicode NFC: "{s[:40]}"')
    title = d.get('title') or {}
    if not title.get('vi') or not title.get('en'):
        m('E', 'title', 'title needs vi and en')
    if vi.CJK.search(str(title.get('vi', ''))):
        m('E', 'title', 'chữ Hán in the title')
    nc = d.get('native_check')
    if nc and not (isinstance(nc, dict) and nc.get('by') and nc.get('date')):
        m('E', 'native_check', 'native_check needs {by, date}')
    if real and not nc:
        m('I', 0, 'not checked by a native speaker (the app says so)')
    lesson_names = {vi.nfc(w['w']).replace('_', ' ') for w in d.get('new_words') or [] if w.get('name')}
    used = set()

    def check_line(where, text):
        if vi.CJK.search(text):
            m('E', where, 'chữ Hán in a lesson line (characters go on cards and in the bridge only)')
        for t in vi.words(text):
            if t[0] != 'w':
                continue
            _, surf, k, tag, start = t
            shown = surf.replace('_', ' ')
            used.add(vi.card_id(k, tag))
            if shown in names or shown in lesson_names:
                used.add('name:' + shown)
                continue
            for s in shown.lower().split():
                for p in vi.syllable_problems(s, style=True):
                    m('E', where, p)
            if tag and tag not in tags.get(k, set()) | all_tags.get(k, set()):
                m('E', where, f'"{surf}": tag ~{tag} is defined by no dictionary entry and no new_words entry')
            if k not in keys:
                hint = ' (a name? declare it in new_words with name: true)' if surf[:1].isupper() and not start else ''
                m('E', where, f'"{shown}" is in no dictionary{hint}')
            elif real and keys[k] == {True}:
                m('E', where, f'"{shown}" is only in the test fixture, not in a real source')

    lines = d.get('dialogue') or []
    ns = set()
    for ln in lines:
        n = ln.get('n', '?')
        ns.add(n)
        for f in ('vi', 'en'):
            if not ln.get(f):
                m('E', f'line {n}', f'missing {f}')
        check_line(f'line {n}', ln.get('vi') or '')
    for i, note in enumerate(d.get('notes') or []):
        if note.get('ref') != 0 and note.get('ref') not in ns:
            m('E', f'notes[{i}]', f"note ref {note.get('ref')} is not a line of the dialogue (use 0 for a recap note)")
        if not note.get('text'):
            m('E', f'notes[{i}]', 'empty note')
    for kind, items in (d.get('exercises') or {}).items():
        if kind not in ('translate', 'fill'):
            m('E', f'exercises.{kind}', 'unknown exercise kind (translate, fill)')
        for j, it in enumerate(items or []):
            where = f'exercises.{kind}[{j}]'
            text = it.get('vi') or ''
            if not it.get('en'):
                m('E', where, 'missing en')
            if kind == 'fill':
                if '___' not in text or not it.get('answer'):
                    m('E', where, 'a fill item needs ___ in vi and an answer')
                text = text.replace('___', str(it.get('answer', '')).replace(' ', '_'))
            check_line(where, text)
            best = 0.0
            for ln in lines:
                c = copied(text, ln.get('vi') or '')
                if c == 'copy':
                    m('E', where, f'exercise sentence taken from the dialogue (line {ln.get("n")}): write a new one')
                    break
                best = max(best, c)
            else:
                if best >= SIMILAR:
                    m('W', where, f'exercise sentence very similar to a dialogue line ({best:.2f}): is it new?')
    for j, w in enumerate(d.get('new_words') or []):
        if not w.get('w'):
            m('E', f'new_words[{j}]', 'missing w')
            continue
        if not (w.get('en') or '').strip():
            m('E', f'new_words[{j}]', f'{w["w"]}: no English (English on every card)')
        cid = ('name:' + vi.nfc(w['w']).replace('_', ' ')) if w.get('name') else vi.card_id(vi.key(w['w']), w.get('tag'))
        if cid not in used:
            m('E', f'new_words[{j}]', f'{w["w"]} is not used in the dialogue or the exercises')
        if w.get('chars') and not vi.CJK.search(w['chars']):
            m('E', f'new_words[{j}]', f'{w["w"]}: chars must be chữ Hán')
        if w.get('label') and w['label'] not in ('same', 'false-friend', 'native'):
            m('E', f'new_words[{j}]', f'{w["w"]}: label must be same, false-friend or native')


def main():
    files = sys.argv[1:] or course.lesson_files()
    keys, tags = load_db()
    msgs = []
    syl = course.syllabus().get('approved') or {}
    reals = [f for f in files if not course.load(f).get('fixture')] if files else []
    if reals and not (syl.get('syllabus') and syl.get('word_list')):
        msgs.append(('E', f'course/syllabus.yaml: E {len(reals)} lesson(s) drafted before the owner approved the '
                          'syllabus and the first word list (fixed decision): approve them first'))
    for f in course.stray_files():
        msgs.append(('E', f'{os.path.relpath(f, ROOT)}:0: E not a lesson file: only NN.yaml may be in the lesson '
                          'directory (the template is course/lesson_template.yaml)'))
    if not course.real_files():
        print('lint: no lesson in course/lessons yet: checking the test fixture (tools/fixtures/lessons)')
    loaded = []
    for f in files:
        try:
            loaded.append((f, course.load(f)))
        except yaml.YAMLError as e:
            msgs.append(('E', f'{os.path.relpath(f, ROOT)}:0: E YAML error: {e}'))
    # names and tags declared anywhere in the course count everywhere
    all_tags = collections.defaultdict(set)
    names = set()
    for _, d in loaded:
        for w in d.get('new_words') or []:
            if w.get('name'):
                names.add(vi.nfc(w['w']).replace('_', ' '))
            elif w.get('tag'):
                all_tags[vi.key(w['w'])].add(w['tag'])
    spellings = collections.defaultdict(set)
    seen = {}
    for f, d in loaded:
        if d.get('id') in seen:
            msgs.append(('E', f'{os.path.relpath(f, ROOT)}:0: E id {d.get("id")} already used by {seen[d.get("id")]}'))
        seen[d.get('id')] = os.path.basename(f)
        lint(f, d, keys, tags, all_tags, names, msgs, spellings)
    # pacing: a smooth growth of lines per lesson (non-review lessons, in order)
    real = sorted((d['id'], len(d.get('dialogue') or []), os.path.basename(f)) for f, d in loaded
                  if not d.get('fixture') and not d.get('review') and isinstance(d.get('id'), int))
    for (a, na, _), (b, nb, fb) in zip(real, real[1:]):
        if nb < na - 1 or nb > na + 2:
            msgs.append(('W', f'{fb}: W {nb} lines after {na} in lesson {a}: lines per lesson should grow smoothly'))
    for f, d in loaded:
        if isinstance(d.get('id'), int) and d['id'] > 0 and not d.get('fixture') and bool(d.get('review')) != (d['id'] % 7 == 0):
            msgs.append(('W', f'{os.path.basename(f)}: W review lessons are every 7th (7, 14, …)'))
    errors = 0
    for level, text in msgs:
        print(text)
        errors += level == 'E'
    print(f'{len(files)} file(s), {errors} error(s)')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
