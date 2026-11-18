"""Lesson 0, "Reading Vietnamese": course/lesson0.yaml, a page of sections (paragraphs, tables, lists) before lesson 1.

Format (docs/REFERENCE.md "Lesson 0"):
    title: {en: …, vi: …}
    intro: text
    sections:
    - {id: slug, h: heading, body: [{p: text} | {ul: [text, …]} | {table: {head: [text, …], rows: [[text, …], …]}}]}
Inline markup in any text: **bold**, *italic*, `code` (IPA, letters), and [[vi words]]: Vietnamese written with the
course's word boundaries (học_sinh, ma~ghost), cut and given cards by tools/cards.py like a lesson line (one word
pipeline); tools/lint.py checks every word of them as it checks lesson lines. Chữ Hán are set in the Chinese font.

    import lesson0
    d = lesson0.load()                          # None when there is no course/lesson0.yaml, or TUSACH_LESSON0=none
TUSACH_LESSON0=FILE builds another Lesson 0 (a test); a FILE that does not exist is an error (review 5: a mistyped
path silently dropped Lesson 0); TUSACH_LESSON0=none builds without one, on purpose.
    for where, text in lesson0.spans(d): …      # every [[…]] span (lint)
    page = lesson0.render(d, cards.tokenize)    # the page's DATA.lesson0 (build_app)
"""
import html
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import vi  # noqa: E402

PATH = os.path.join(ROOT, 'course/lesson0.yaml')
SPAN = re.compile(r'\[\[(.+?)\]\]')
KEYS = {'top': {'title', 'intro', 'sections'}, 'section': {'id', 'h', 'body'}, 'block': {'p', 'ul', 'table'},
        'table': {'head', 'rows'}}
# a sound of another language is only ever "close to" a Vietnamese one: no text may claim more (the owner's page is
# read before any audio exists)
OVERCLAIM = re.compile(r'\b(exactly|identical|precisely|just like|the same sound)\b', re.I)


NONE = 'none'          # TUSACH_LESSON0=none: no Lesson 0, on purpose (tests building a fixture page)


def path():
    return os.environ.get('TUSACH_LESSON0') or PATH


def load():
    p = path()
    if p == NONE:
        return None
    if not os.path.exists(p):
        if p != PATH:
            raise SystemExit(f'lesson0: TUSACH_LESSON0={p}: no such file (TUSACH_LESSON0=none builds without Lesson 0)')
        return None
    return yaml.safe_load(open(p, encoding='utf-8'))


def texts(d, only=None):
    """(where, text) of every text of the page (`only`: of the section with this id)."""
    if not d:
        return
    if only is None:
        yield 'intro', d.get('intro') or ''
    for i, s in enumerate(d.get('sections') or []):
        if only is not None and s.get('id') != only:
            continue
        yield f'sections[{i}].h', s.get('h') or ''
        for j, b in enumerate(s.get('body') or []):
            w = f'sections[{i}].body[{j}]'
            if 'p' in b:
                yield w, b['p'] or ''
            for k, t in enumerate(b.get('ul') or []):
                yield f'{w}.ul[{k}]', t or ''
            tb = b.get('table') or {}
            for k, t in enumerate(tb.get('head') or []):
                yield f'{w}.head[{k}]', t or ''
            for r, row in enumerate(tb.get('rows') or []):
                for k, t in enumerate(row or []):
                    yield f'{w}.rows[{r}][{k}]', str(t if t is not None else '')


def spans(d):
    """(where, Vietnamese text) of every [[…]] span."""
    for where, t in texts(d):
        for m in SPAN.finditer(str(t)):
            yield where, m.group(1)


def problems(d):
    """Format problems of the page: (where, message)."""
    out = []
    if not isinstance(d, dict):
        return [('0', 'not a mapping')]
    for k in d:
        if k not in KEYS['top']:
            out.append(('0', f'unknown key "{k}"'))
    t = d.get('title') or {}
    if not (isinstance(t, dict) and t.get('en') and t.get('vi')):
        out.append(('title', 'title needs en and vi'))
    for i, s in enumerate(d.get('sections') or []):
        for k in s:
            if k not in KEYS['section']:
                out.append((f'sections[{i}]', f'unknown key "{k}"'))
        if not s.get('id') or not re.fullmatch(r'[a-z0-9-]+', str(s['id'])):
            out.append((f'sections[{i}]', 'id must be a slug (a-z, 0-9, -)'))
        for j, b in enumerate(s.get('body') or []):
            if not isinstance(b, dict) or len(b) != 1 or next(iter(b)) not in KEYS['block']:
                out.append((f'sections[{i}].body[{j}]', 'a block is one of {p: …}, {ul: […]}, {table: {head, rows}}'))
                continue
            tb = b.get('table')
            if tb is not None:
                if not isinstance(tb, dict) or set(tb) - KEYS['table'] or not tb.get('head'):
                    out.append((f'sections[{i}].body[{j}]', 'table needs head and rows only'))
                else:
                    for r, row in enumerate(tb.get('rows') or []):
                        if len(row or []) != len(tb['head']):
                            out.append((f'sections[{i}].body[{j}].rows[{r}]', f'{len(row or [])} cells for '
                                                                               f'{len(tb["head"])} columns'))
    for where, t in texts(d):
        if not vi.is_nfc(str(t)):
            out.append((where, 'not in Unicode NFC'))
        m = OVERCLAIM.search(SPAN.sub('', str(t)))
        if m:
            out.append((where, f'"{m.group(0)}": a foreign sound is only ever close to a Vietnamese one'))
        if vi.CJK.search(''.join(SPAN.findall(str(t)))):
            out.append((where, 'chữ Hán inside [[…]]: Vietnamese words only'))
    return out + example_problems(d)


# the example words of the sound tables must show the sound of their row (review 5, finding 4: nhé was the example of
# initial n): by section id, how a word is matched with the letters of the row's first cell
INITIALS = sorted('ngh ng nh gh gi kh ph th tr ch qu b c d đ g h k l m n p r s t v x'.split(), key=len, reverse=True)
CODAS = ('ch', 'nh', 'ng', 'c', 'm', 'n', 'p', 't')
TONES = {'\u0300', '\u0301', '\u0303', '\u0309', '\u0323'}


def _toneless(w):
    import unicodedata as ud
    return ud.normalize('NFC', ''.join(c for c in ud.normalize('NFD', w.lower()) if c not in TONES))


def _initial(syl):
    s = _toneless(syl)
    i = next((x for x in INITIALS if s.startswith(x)), '')
    return 'q' if i == 'qu' else i


def _coda(syl):
    s = _toneless(syl)
    return next((c for c in CODAS if s.endswith(c)), '')


def example_problems(d):
    """(where, message) for a sound-table example word that does not show its row's sound: consonants and mergers by
    the initial, finals by the final, vowels and diphthongs by the vowel letters (tone marks ignored)."""
    out = []
    for i, s in enumerate((d or {}).get('sections') or []):
        kind = s.get('id')
        if kind not in ('consonants', 'mergers', 'finals', 'vowels'):
            continue
        for j, b in enumerate(s.get('body') or []):
            tb = b.get('table') if isinstance(b, dict) else None
            if not tb:
                continue
            cols = [k for k, h in enumerate(tb.get('head') or []) if str(h).lower().startswith('example')]
            for r, row in enumerate(tb.get('rows') or []):
                letters = {x.strip('-').strip() for x in re.split(r'[,/]| ', str(row[0])) if x.strip('-').strip()}
                for k in cols:
                    for m in SPAN.finditer(str(row[k])):
                        first = m.group(1).split('~')[0].split()[0].split('_')[0]
                        if kind in ('consonants', 'mergers'):
                            good = _initial(first) in letters
                        elif kind == 'finals':
                            good = _coda(first) in letters
                        else:
                            good = any(x in _toneless(first) for x in letters)
                        if not good:
                            out.append((f'sections[{i}].body[{j}].rows[{r}]', f'example [[{m.group(1)}]] does not '
                                        f'show {", ".join(sorted(letters))}'))
    return out


def inline(text, tokenize):
    """Text -> parts for the page: strings of HTML (escaped here) and {'v': tokens} for each [[…]] span."""
    parts, pos = [], 0
    for m in SPAN.finditer(text):
        if m.start() > pos:
            parts.append(_html(text[pos:m.start()]))
        parts.append({'v': tokenize(m.group(1))})
        pos = m.end()
    if pos < len(text):
        parts.append(_html(text[pos:]))
    return parts


def _html(t):
    s = html.escape(t, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    return vi.CJK.sub(lambda m: f'<span class="han">{m.group(0)}</span>', s)


def render(d, tokenize):
    """DATA.lesson0 for the page: {title, intro, sections: [{id, h, body: [{p} | {ul} | {table: {head, rows}}]}]},
    every text as parts (inline())."""
    if not d:
        return None
    f = lambda t: inline(str(t if t is not None else ''), tokenize)  # noqa: E731
    secs = []
    for s in d.get('sections') or []:
        body = []
        for b in s.get('body') or []:
            if 'p' in b:
                body.append({'p': f(b['p'])})
            elif 'ul' in b:
                body.append({'ul': [f(x) for x in b['ul']]})
            elif 'table' in b:
                body.append({'table': {'head': [f(x) for x in b['table']['head']],
                                       'rows': [[f(x) for x in r] for r in b['table'].get('rows') or []]}})
        secs.append({'id': s['id'], 'h': f(s.get('h')), 'body': body})
    return {'title': d['title'], 'intro': f(d.get('intro')), 'sections': secs}
