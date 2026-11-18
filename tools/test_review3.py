"""Review 3's reproduced cases, each a test on the real build (`make test`, after `make db`).

  python3 -I tools/test_review3.py

Every case below failed at 16c8b24 (review 3, 18 Nov 2026) and must stay fixed: guards of the course lexicon,
the bridge-note pairing, the Hán-Việt readings, the Taigi layer, the order of polyphonic readings, the card's origin
line and the example filters. The word-list and plan checks have their own test in tools/test_plan.py.
"""
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402
import build_db  # noqa: E402
import cards  # noqa: E402
import lexicon  # noqa: E402
import lint  # noqa: E402
import vi  # noqa: E402

failures = []


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


con = cards.open_db('public')
cards.init(con)


def card(w):
    k, _, t = w.partition('~')
    return cards.dictionary[cards.lookup(vi.key(k), t or None)]


def row(**kw):
    d = {c: '' for c in lexicon.COLS}
    d.update(kw)
    d['n'], d['tag'] = 0, None
    d['k'] = vi.key(d['key'].split('~')[0])
    d['cid'] = vi.card_id(d['k'], d['key'].partition('~')[2] or None)
    d['conf'] = d['confidence'].split(':')[0]
    return d


def kinds(r):
    return {k for _, k, _ in lexicon.validate(con, [r])}


# finding 7: the lexicon guards
ok('chars-sense' in kinds(row(key='cam', pos='noun', en='orange (fruit)', origin='hv', chars='甘', confidence='sure')),
   'cam 甘 "orange": the etymology with 甘 is not the orange (chars-sense)')
ok('chars-sense' not in kinds(row(key='cam', pos='noun', en='orange (fruit)', origin='hv', chars='柑',
                                  confidence='sure')), 'cam 柑 "orange" passes')
ok('en-item' in kinds(row(key='nhà', pos='noun', en='house, home; dog', origin='native', confidence='sure')),
   'nhà "house, home; dog": the added sense is refused (en-item)')
ok('en-item' in kinds(row(key='thuộc', pos='verb', en='to belong to; to know by heart', origin='hv', chars='屬',
                          confidence='sure')), 'thuộc 屬 "to know by heart": another etymology\'s sense (en-item)')
ok('only-claim' in kinds(row(key='đầu tiên', pos='adj', en='first', origin='hv', chars='頭先', confidence='likely',
                             false_friend='頭先 is a word of Cantonese only')), '"a word of Cantonese only" is refused')
ok('example' in kinds(row(key='ai', pos='pron', en='who', origin='native', confidence='sure',
                          example='Tụi bây nghĩ cô ấy ở với ai?', example_en='Who do you think she is with?')),
   'a Southern lexicon example (tụi bây) is refused')
open_ = [(r['key'], k) for r, k, _ in lexicon.validate(con) if k not in lexicon.overrides(r)]
ok(not open_, f'the course lexicon validates (open: {open_[:5]})')

# finding 7: the bridge-note pairing
lint.D = lint.DB_(lint.DB)
for chars, word in (('被', 'phải'), ('時', 'thì'), ('平', 'bằng'), ('南', 'nôm')):
    ok(bool(lint.D.bridge_example(chars, word)), f'"{word} is {chars}" is refused as a bridge example')
for chars, word in (('學生', 'học sinh'), ('平', 'bình'), ('南', 'nam')):
    ok(not lint.D.bridge_example(chars, word), f'"{word} is {chars}" passes')
ok(lint.cjk_pairs('học sinh is 學生; 平 bình') == [('學生', 'học sinh'), ('平', 'bình')], 'notes pair a run with its word')

# finding 6: Hán-Việt readings and labels
ok('nôm' not in card('Việt Nam')['hv'] and card('Việt Nam')['hv'].startswith('越 việt'),
   f"Việt Nam: 南 is read nam only (got {card('Việt Nam')['hv']})")
ok('bằng' not in bridge.hv_readings(con, '平') and 'cuộc' not in bridge.hv_readings(con, '局'),
   '平 bằng and 局 cuộc are not Hán-Việt readings')
ok(card('bằng~equal')['label'] == 'older-loan' and card('nôm')['label'] == 'older-loan',
   'bằng "equal" and nôm are older loans')
ok(card('thì').get('origin') == 'no etymology recorded', 'thì: "no etymology recorded", never "(not Chinese)"')
ok('only' not in card('đầu tiên').get('ff', ''), 'đầu tiên: no "only" claim in the false-friend note')
ok(card('cơ')['en'].startswith('(final particle') and card('cơ~muscle')['chars'] == '肌',
   'cơ: the particle and the muscle are two rows')
for w, gone in (('công', 'public'), ('tiêu', 'pepper'), ('thuộc', 'heart'), ('kinh', 'afraid'), ('đàn', 'flock')):
    ok(gone not in card(w)['en'], f'{w}: no "{gone}" under its characters')

# finding 6: the Taigi layer
c = card('trà~tea')
ok(not c.get('nan') and 'tê' in (c.get('nan_coll') or ''), f"trà 茶: tê is colloquial, not literary (got {c.get('nan')})")
ok(card('điều').get('nan_layer') == 'unmarked', 'điều 條: the layer the MOE does not mark is said so')

# finding 6: polyphonic readings ordered by fit with the card's Hán-Việt syllable
for w, lang, first in (('hàng', 'yue', 'hong4'), ('hàng', 'cmn', 'háng'), ('chỉ~only', 'yue', 'zi2'),
                       ('chỉ~only', 'cmn', 'zhǐ'), ('số', 'cmn', 'shù'), ('thích', 'yue', 'sik1'),
                       ('tiền', 'yue', 'cin4'), ('đang', 'cmn', 'dāng')):
    got = card(w).get(lang, '')
    ok(got.startswith(first), f'{w}: {lang} {first} first (got {got})')
ok('(also ' in card('hàng')['yue'], 'the other readings come after "also"')

# finding 5: examples
for w in ('bộ', 'tối', 'chẳng', 'ai', 'nghĩ', 'tính', 'cháu', 'chủ nhật', 'chuyển', 'no', 'thế nào', 'ra', 'tin', 'sống',
          'thành', 'là', 'trước', 'nghìn', 'một', 'đó', 'vì', 'em', 'yêu', 'nhỉ', 'cái', 'được', 'đá~ice', 'khu'):
    ex = card(w).get('ex') or {}
    ok(ex.get('src') == cards.LEX_EXAMPLE_SRC, f'{w}: the lexicon\'s own example ({ex.get("vi")})')
south = build_db.southern_markers(con)
ok({'tui', 'tụi', 'xài', 'nha', 'hoài', 'thiệt'} <= south and 'mùng' not in south, 'Southern markers')
ok(build_db.misaligned('Bộ phim yêu thích của bạn là gì?', 'Why is this movie your favourite?', []) != '' and
   build_db.misaligned('Tôi phải về nhà mỗi khi trời tối.', 'I have to get home before it gets dark.', []) != '' and
   build_db.misaligned('Bạn có tiến triển gì không?', 'Have you made any progress?', []) == '',
   'a mistranslated question or "whenever" is refused; gì "any" in a yes/no question is not')
ok(build_db.EX_UNSUITABLE_EN.search('I have no reason to live.') and build_db.EX_UNSUITABLE_EN.search(
    'She believes he committed suicide.'), 'self-harm translations are unsuitable')
db = sqlite3.connect(cards.DB['public'])
shown = {v for (v,) in db.execute("SELECT vi FROM example WHERE flags = ''")}
for v in ('Tụi bây nghĩ cô ấy ở với ai?', 'Tui phải tính xem tuần sau tui sẽ xài bao nhiêu tiền.',
          'Tôi không có lí do gì để sống.', 'Bộ phim yêu thích của bạn là gì?'):
    ok(v not in shown, f'never a card example: {v}')

# finding 7: the opaque sample (孤 依 left; the others fixed)
import test_golden  # noqa: E402
fo, fs, n, mx, bad = test_golden.opaque_sample(con)
ok(fo <= 2 and fs == 0, f'false opaque {fo} (孤 依 are not fixable from the data), false same {fs}')

print(f'\n{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
