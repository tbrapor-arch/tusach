"""Build the app: course/ + database -> app/dist/index.html (one self-contained page), then the card check.

  python3 -I tools/build_app.py

Every word goes through tools/cards.py (the one word pipeline) and the cards are added to the shared card file
data/build/cards.json as module `lessons`. The build ends with tools/check_cards.py and fails on any error.
Environment (used by tools/compare.py): TUSACH_DB (database), TUSACH_OUT (output directory, default app/dist),
TUSACH_STORE (card file), TUSACH_COURSE (lesson directory), TUSACH_FIXTURE=1 (add the test fixture to real lessons).
"""
import base64
from collections import Counter
import datetime
import hashlib
import json
import os
import re
import sys
import unicodedata

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import appfont  # noqa: E402
import cards  # noqa: E402
import check_cards  # noqa: E402
import course  # noqa: E402
import vi  # noqa: E402

OUT = os.path.abspath(os.environ.get('TUSACH_OUT') or os.path.join(ROOT, 'app/dist'))
STORE = os.environ.get('TUSACH_STORE') or cards.STORE
FONT = os.path.join(ROOT, 'app/fonts/noto-sans-viet.woff2')
PUBLISHED_IDS = os.path.join(ROOT, 'app/published-card-ids.txt')
PUBLISHED_EN = os.path.join(ROOT, 'app/published-english.tsv')
os.makedirs(OUT, exist_ok=True)

con = cards.open_db('public')          # refuses vi-nc.db: no non-commercial source on the public page
# a database built without some sources (meta.missing) makes a page only when every one of them is allowed on purpose
# (TUSACH_ALLOW_MISSING, sandboxes); the page records them and tools/site.py refuses to publish it
MISSING = (dict(con.execute('SELECT key, value FROM meta')).get('missing') or '').split()
_allowed = {x.strip() for x in os.environ.get('TUSACH_ALLOW_MISSING', '').split(',') if x.strip()}
if set(MISSING) - _allowed:
    raise SystemExit(f'build_app: REFUSED: the database was built without {", ".join(sorted(set(MISSING) - _allowed))} '
                     '(meta.missing). Fetch every source (make db), or set TUSACH_ALLOW_MISSING for a sandbox build '
                     'that will not be published.')
if MISSING:
    print(f'build_app: NOT PUBLISHABLE: the database lacks {", ".join(MISSING)} (allowed by TUSACH_ALLOW_MISSING)')
raw = course.lessons()
fixture_build = any(L.get('fixture') for L in raw)
if fixture_build:
    print('build_app: TEST FIXTURE build (no lesson in course/lessons yet): the page says so')
cards.init(con, cards.course_words(raw))


FONT_BYTES = appfont.font_bytes(FONT)


def font_css():
    """Noto Sans (OFL), subset to Latin with Vietnamese and the combining marks, with its mark-positioning tables;
    embedded so stacked marks (ế, ự, ỗ) and the Taigi marks (a̍, ô) draw the same everywhere, offline included."""
    b64 = base64.b64encode(FONT_BYTES).decode()
    return (f"@font-face{{font-family:'VietSans';font-weight:400 800;font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


def check_font(texts):
    """Every letter and mark the page shows (Vietnamese, and the readings on cards) in the embedded font, positioned."""
    probs, n = appfont.font_problems(texts, FONT_BYTES)
    if probs:
        raise SystemExit('build_app: the embedded font (app/fonts/noto-sans-viet.woff2 + appfont.MARK_SHAPES): '
                         + '; '.join(probs[:20]))
    return n


def unbrace(text):
    """A note or gloss as shown: a {preview} (a word not yet taught, marked for lint) without its braces."""
    return re.sub(r'\{([^{}]*)\}', r'\1', text)


# ---- lessons: every line, exercise and new word through the one word pipeline
lessons, all_tokens, extra_ids = [], [], []
for d in raw:
    lines = []
    for ln in d['dialogue']:
        toks = cards.tokenize(ln['vi'])
        all_tokens += toks
        lines.append({'n': ln['n'], 'speaker': ln.get('speaker') or '', 'en': ln['en'], 'lit': ln.get('lit') or '',
                      'vi': vi.display(ln['vi']),
                      'tokens': toks})
    ex = []
    for kind, items in (d.get('exercises') or {}).items():
        for it in items or []:
            e = {'kind': kind, 'en': it.get('en', ''), 'vi': vi.display(it['vi'].replace('___', '‗'))
                 .replace('‗', '___')}
            if kind == 'fill':
                e['answer'] = vi.display(str(it['answer']))
                full = it['vi'].replace('___', str(it['answer']).replace(' ', '_'))
                all_tokens += cards.tokenize(full)
            else:
                e['tokens'] = cards.tokenize(it['vi'])
                all_tokens += e['tokens']
            ex.append(e)
    new_words = []
    for w in d.get('new_words') or []:
        surf = vi.nfc(w['w']).replace('_', ' ')
        cid = cards.name_card(surf) if w.get('name') else cards.lookup(vi.key(surf), w.get('tag'), surf)
        new_words.append({'w': surf, 'en': unbrace(w.get('en') or ''), 'id': cid})
        extra_ids.append(cid)
    lessons.append({'id': d['id'], 'title': d['title'], 'review': bool(d.get('review')), 'setting': d.get('setting', ''),
                    'fixture': bool(d.get('fixture')), 'native_check': d.get('native_check'),
                    'lines': lines, 'notes': [dict(n, text=unbrace(n.get('text') or '')) for n in d.get('notes') or []],
                    'new_words': new_words, 'exercises': ex})

# ---- Lesson 0, "Reading Vietnamese" (course/lesson0.yaml, tools/lesson0.py): its Vietnamese words through the same
# pipeline, their cards in module `lessons`
import lesson0  # noqa: E402


def tok0(text):
    toks = cards.tokenize(text)
    all_tokens.extend(toks)
    return toks


lesson_zero = lesson0.render(lesson0.load(), tok0)

# ---- the shared card file: this build replaces module `lessons` only (a partial build adds, never restores)
store = cards.Store(STORE)
store.replace_module('lessons', all_tokens, extra_ids)
# every card id a published page has had keeps its card (a word saved on a device, a link from the private module)
published = check_cards.read_ids(PUBLISHED_IDS)
for cid in published:
    if cid not in cards.dictionary:
        got = cards.name_card(cid[5:]) if cid.startswith('name:') else cards.lookup(*(cid.split('~', 1) + [None])[:2])
        if got != cid:
            raise SystemExit(f'{PUBLISHED_IDS}: {cid} no longer gives this card (no card lost: fix the source or the course)')
    store.cards[cid] = cards.dictionary[cid]
store.keep(published)
store.save()
dictionary = store.page_cards(cards.PUBLIC_MODULES + ('_published',))

# ---- audio. TODO(audio): no source of word recordings yet (handover section 6: a voice or open recordings, Northern
# accent). A card gets ▶ when app/dist/audio/w/<slug>.mp3 exists; app/dist/audio-needed.txt lists slug and word for the
# tool that will provide them.
need = []
for cid, c in dictionary.items():
    if c.get('name'):
        continue
    slug = hashlib.sha1(cid.encode()).hexdigest()[:12]
    need.append(f"{slug}\t{c['w']}")
    if os.path.exists(os.path.join(OUT, 'audio/w', slug + '.mp3')):
        c['audio'] = f'audio/w/{slug}.mp3'
open(os.path.join(OUT, 'audio-needed.txt'), 'w', encoding='utf-8').write('\n'.join(need) + '\n')

# ---- native-speaker recordings of the dialogues: course/audio/lessons/L001-03.mp3 (tools/import_recordings.py)
REC = os.path.join(ROOT, 'course/audio/lessons')
REC_META = os.path.join(ROOT, 'course/audio/recordings.yaml')
rec_meta = yaml.safe_load(open(REC_META, encoding='utf-8')) if os.path.exists(REC_META) else {}
n_rec = 0
for L in lessons:
    for ln in L['lines']:
        cid = f"L{L['id']:03d}-{ln['n']:02d}"
        if os.path.exists(os.path.join(REC, cid + '.mp3')):
            ln['audio'] = f'audio/lessons/{cid}.mp3'
            ln['voice'] = rec_meta.get('voice') or 'native speaker'
            n_rec += 1

syllabus = course.syllabus()
data = {'lessons': lessons, 'dict': dictionary, 'syllabus': syllabus.get('lessons') or [], 'fixture': fixture_build,
        'zh': [list(x) for x in cards.DISPLAY_LANGS], 'lesson0': lesson_zero,
        'bridge': sorted(i for i, c in dictionary.items() if c.get('chars')), 'recorded': n_rec,
        'built': datetime.date.today().isoformat(), 'missing': MISSING}


def card_readings(c):
    """Every romanised reading a card shows (Hán-Việt, the Chinese columns, colloquial Taigi, etymon, per character)."""
    out = [c.get(k) or '' for k in ('hv', 'nan_coll') + tuple(x[0] for x in cards.DISPLAY_LANGS)]
    for sub in [c.get('etymon') or {}] + list(c.get('per_char') or []):
        out += [str(v) for k, v in sub.items() if k != 'chars' and isinstance(v, str)]
    return [x for x in out if x]


n_letters = check_font([t for _, t in lesson0.spans(lesson0.load())] + [L['title']['vi'] for L in lessons] + [ln['vi'] for L in lessons for ln in L['lines']]
                       + [c['w'] for c in dictionary.values()] + [c['ex']['vi'] for c in dictionary.values() if c.get('ex')]
                       + [r for c in dictionary.values() for r in card_readings(c)])

tpl = open(os.path.join(ROOT, 'app/index.template.html'), encoding='utf-8').read()
tpl = tpl.replace('/*__FONTS__*/', font_css())
# the data goes into <script type="application/json">: every '<' is escaped so no '</script' can end the block
payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
out = os.path.join(OUT, 'index.html')
open(out, 'w', encoding='utf-8').write(unicodedata.normalize('NFC', tpl.replace('/*__DATA__*/null', payload)))
# recording page for native speakers (record.html): the dialogue lines only
rtpl = open(os.path.join(ROOT, 'app/record.template.html'), encoding='utf-8').read()
rdata = {'voice': rec_meta.get('voice', 'native speaker'),
         'lessons': [{'id': L['id'], 'title': L['title'], 'lines': [{k: ln[k] for k in ('n', 'speaker', 'vi', 'en')}
                                                                    for ln in L['lines']]} for L in lessons]}
rjson = json.dumps(rdata, ensure_ascii=False)
rtpl = rtpl.replace('/*__FONTS__*/', font_css()).replace('/*__DATA__*/null', rjson.replace('</', '<\\/'))
open(os.path.join(OUT, 'record.html'), 'w', encoding='utf-8').write(unicodedata.normalize('NFC', rtpl))

src = Counter((c.get('en_src') or 'none').split(':')[0] for c in dictionary.values())
print('English on word cards:', ', '.join(f'{k} {v}' for k, v in src.most_common()))
open(os.path.join(OUT, 'english-auto.txt'), 'w', encoding='utf-8').write(''.join(
    f"{c['w']}\t{c.get('en_src') or 'none'}\t{c.get('en') or ''}\n" for c in dictionary.values()
    if c.get('en_src') not in ('course', 'lexicon')))
print(f'{out}: {"Lesson 0 + " if lesson_zero else ""}{len(lessons)} lessons, {len(dictionary)} cards ({sum(1 for c in dictionary.values() if c.get("chars"))} '
      f'Hán-Việt), {sum(1 for c in dictionary.values() if c.get("audio"))} with audio, {n_rec} recorded lines, '
      f'{n_letters} letters and marks checked in the font, {os.path.getsize(out) // 1024} KB')

# ---- the card check, at the end of every build: no word without a card, no card lost, no poorer English
warn = []
errs = check_cards.check(STORE, out, PUBLISHED_IDS, PUBLISHED_EN, modules=cards.PUBLIC_MODULES, warn=warn)
for w in warn[:100]:
    print('W', w)
for e in errs[:100]:
    print('E', e)
print(f'card check: {len(errs)} error(s)')
if errs:
    sys.exit(1)
