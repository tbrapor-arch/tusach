"""Click through the built app in a phone-sized browser and report problems.

  python3 tools/smoke.py [app/dist/index.html] [--shots DIR]
  SMOKE_IDS=1,2 python3 tools/smoke.py      # only these lessons

Checks: JS errors, horizontal overflow, the embedded Vietnamese font is used for stacked marks, every lesson renders,
every word token opens a card (a word without a card is a problem), every card shows English, new-word chips and notes
open, exercises accept their answer and point out a tone-only mistake, a lesson can be finished, a review session runs,
lists, bridge and settings render, every page maps to a tab; the private-module loader and its merge rule against a
mocked API (TUSACH_PRIVATE, default ../tusach-private). A part that cannot run is reported "NOT TESTED" and smoke
exits 2, unless TUSACH_SMOKE_ALLOW_UNTESTED=1.
"""
import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--shots']
PAGE = os.path.abspath(args[0] if args else os.path.join(ROOT, 'app/dist/index.html'))
SHOTS = sys.argv[sys.argv.index('--shots') + 1] if '--shots' in sys.argv else None
problems = []
not_tested = []    # a part that could not run: smoke fails (exit 2) unless TUSACH_SMOKE_ALLOW_UNTESTED=1


def p(msg):
    problems.append(msg)
    print('PROBLEM', msg)


def overflow(page, where):
    w = page.evaluate('document.documentElement.scrollWidth - window.innerWidth')
    if w > 1:
        bad = page.evaluate('''() => [...document.querySelectorAll('#main *')].filter(e => e.getBoundingClientRect().right > window.innerWidth + 1
            && !e.closest('.vwrap')).slice(0, 3).map(e => e.tagName + '.' + e.className + ' ' + (e.textContent || '').slice(0, 30))''')
        p(f'{where}: page scrolls sideways by {w}px {bad}')


def shot(page, name):
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True)
        page.screenshot(path=f'{SHOTS}/{name}.png')


with sync_playwright() as pw:
    b = pw.chromium.launch()
    page = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    page.on('pageerror', lambda e: p(f'JS error: {e}'))
    page.on('console', lambda m: m.type == 'error' and 'fonts.g' not in m.text and 'ERR_' not in m.text and p(f'console: {m.text}'))
    page.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    page.route('**/fonts.gstatic.com/**', lambda r: r.abort())
    page.goto('file://' + PAGE)
    page.wait_for_selector('.lgrid')
    overflow(page, 'lessons')
    shot(page, 'lessons')
    # the embedded font draws the stacked marks itself (no fallback font for ế, ự, ỗ)
    page.evaluate('document.fonts.ready')
    if not page.evaluate("document.fonts.check('24px VietSans', 'ế ự ỗ ặ ẫ')"):
        p('the embedded VietSans font is not available for ế ự ỗ ặ ẫ')
    ids = page.evaluate('DATA.lessons.map(l => l.id)')
    if os.environ.get('SMOKE_IDS'):
        ids = [int(x) for x in os.environ['SMOKE_IDS'].split(',')]
    for lid in ids:
        page.evaluate(f"location.hash = 'lesson-{lid}'")
        page.wait_for_selector('.lines')
        overflow(page, f'lesson {lid}')
        n_lines = page.evaluate(f'DATA.lessons.find(l => l.id === {lid}).lines.length')
        if page.locator('.sent').count() != n_lines:
            p(f'lesson {lid}: {page.locator(".sent").count()} lines shown, {n_lines} in data')
        nocard = page.evaluate("[...document.querySelectorAll('.lines .tok.nocard')].map(t => t.textContent)")
        if nocard:
            p(f'lesson {lid}: words without a card: {nocard}')
        toks = page.locator('.lines .tok[data-tok]')
        for i in range(toks.count()):
            t = toks.nth(i)
            t.click()
            if i == 0:
                page.wait_for_timeout(350)
            ok = page.evaluate("document.getElementById('sheet').classList.contains('open') && !!document.querySelector('#sheet .wc-w') && document.querySelector('#sheet .wc-gloss').textContent.trim() !== ''")
            if not ok:
                p(f'lesson {lid}: token {i} "{t.inner_text()}" did not open a card with English')
            if i == 0:
                page.evaluate("document.getElementById('sheet').scrollTop = 9999")
                vis = page.evaluate("(() => { const r = document.querySelector('#sheet .x').getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; })()")
                if not vis:
                    p(f'lesson {lid}: close button scrolled out of view')
                shot(page, f'card-{lid}')
            page.keyboard.press('Escape')
        chips = page.locator('[data-word]')
        for i in range(chips.count()):
            chips.nth(i).click()
            if not page.evaluate("!!document.querySelector('#sheet.open .wc-gloss') && document.querySelector('#sheet.open .wc-gloss').textContent.trim() !== ''"):
                p(f'lesson {lid}: new word {i} card is empty')
            page.keyboard.press('Escape')
        notes = page.locator('.under [data-note]')
        for i in range(notes.count()):
            notes.nth(i).click()
            if not page.evaluate("document.querySelector('#sheet.open .note-body') !== null"):
                p(f'lesson {lid}: note button {i} did not open')
            page.keyboard.press('Escape')
        for f in page.locator('form[data-ex]').all():
            k = f.get_attribute('data-ex')
            ans = page.evaluate(f'DATA.lessons.find(l => l.id === {lid}).exercises[{k}].answer')
            f.locator('input').fill(ans)
            f.locator('button[type=submit]').click()
            if 'ok' not in (page.locator(f'#fb-{k}').get_attribute('class') or ''):
                p(f'lesson {lid}: exercise {k} rejects its own answer "{ans}"')
            bare = page.evaluate(f'toneless({ans!r})')
            if bare != ans.lower():
                f.locator('input').fill(bare)
                f.locator('button[type=submit]').click()
                if 'near' not in (page.locator(f'#fb-{k}').get_attribute('class') or ''):
                    p(f'lesson {lid}: exercise {k}: "{bare}" (tones missing) is not pointed out as nearly right')
        for bt in page.locator('[data-ans]').all():
            bt.click()
        page.evaluate('window.scrollTo(0,0)')
        shot(page, f'lesson-{lid}')
    # every card of the page has English (owner's rule), opened one by one
    empty = page.evaluate("Object.keys(DATA.dict).filter(id => { openCard(id); const g = document.querySelector('#sheet .wc-gloss'); return !g || !g.textContent.trim(); })")
    page.keyboard.press('Escape')
    if empty:
        p(f'cards without English: {empty[:10]}')
    # finish the first lesson, add a word to a list, review
    first = ids[0]
    page.evaluate(f"location.hash = 'lesson-{first}'")
    page.wait_for_selector('#mark')
    page.click('#mark')
    page.locator('.lines .tok[data-tok]').first.click()
    page.click('#add-card')
    page.keyboard.press('Escape')
    page.evaluate("location.hash = 'lists'")
    page.wait_for_selector('.item')
    page.locator('.item').first.click()
    page.wait_for_selector('#lfc')
    overflow(page, 'list')
    page.evaluate("location.hash = 'review'")
    page.wait_for_selector('.segs')
    overflow(page, 'review')
    page.locator(f'[data-study="L{first}"][data-mode="all"]').click()
    for _ in range(60):
        if page.locator('#flip').count():
            page.click('#flip')
        elif page.locator('#good').count():
            page.click('#good')
        else:
            break
    if not page.locator('text=Xong rồi').count():
        p('review session did not finish')
    page.evaluate("location.hash = 'lessons'")
    page.wait_for_selector('.lgrid')
    if not page.locator('.journal li').count():
        p('home: journal is empty after finishing a lesson')
    if len(ids) > 1:
        page.evaluate(f"location.hash = 'lesson-{ids[0]}'")
        page.wait_for_selector('.lbar')
        page.keyboard.press('ArrowRight')
        page.wait_for_timeout(150)
        if page.evaluate('location.hash') != f'#lesson-{ids[1]}':
            p('ArrowRight does not go to the next lesson')
    for h in ('lists', 'review', 'bridge', 'settings', 'lessons'):
        page.evaluate(f"location.hash = '{h}'")
        page.wait_for_timeout(150)
        overflow(page, h)
        if page.evaluate('currentTab()') not in ('lessons', 'review', 'books', 'settings'):
            p(f'{h}: currentTab() names no tab')
        shot(page, h)
    page.evaluate("location.hash = 'bridge'")
    page.wait_for_timeout(150)
    rows = page.locator('.vtable [data-word]')
    if page.evaluate('DATA.bridge.length') and not rows.count():
        p('bridge: no Hán-Việt word listed')
    elif rows.count():
        rows.first.click()
        page.wait_for_timeout(350)
        if not page.evaluate("!!document.querySelector('#sheet.open .wc-chars')"):
            p('bridge: a Hán-Việt card shows no characters')
        if page.evaluate("[...document.querySelectorAll('#sheet.open .zhgrid b')].length") != 3:
            p('bridge: the card does not show Cantonese, Taigi and Mandarin side by side')
        shot(page, 'bridge-card')
    # the private-module loader, against a mocked GitHub API serving the private repository's module/ files
    # (TUSACH_PRIVATE, default ../tusach-private) and a test cards.json: the merge rule keeps a public card unless the
    # private one has a strictly better English rank, and adds the cards the page lacks
    priv = os.path.abspath(os.environ.get('TUSACH_PRIVATE') or os.path.join(ROOT, '..', 'tusach-private'))
    if os.path.isdir(os.path.join(priv, 'module')):
        import json
        pg = b.new_page(viewport={'width': 390, 'height': 844})
        pg.on('pageerror', lambda e: p(f'private module: JS error: {e}'))
        pg.goto('file://' + PAGE)
        pg.wait_for_selector('.lgrid')
        pub_id = pg.evaluate("Object.keys(DATA.dict).find(i => DATA.dict[i].en_rank === 3)")
        pub_en = pg.evaluate(f"DATA.dict[{json.dumps(pub_id)}].en")
        test_cards = {pub_id: {'w': 'x', 'k': pub_id, 'en': 'POORER', 'en_src': 'parts', 'en_rank': 1},
                      'private-only': {'w': 'private only', 'k': 'private-only', 'en': 'from the private module',
                                       'en_src': 'dict:x', 'en_rank': 2}}

        def api(route):
            url = route.request.url
            if '/contents/module/' in url:
                name = url.split('/contents/module/')[1].split('?')[0]
                if name == 'cards.json':
                    return route.fulfill(status=200, body=json.dumps(test_cards))
                path = os.path.join(priv, 'module', name)
                return route.fulfill(status=200, body=open(path, 'rb').read()) if os.path.exists(path) else route.fulfill(status=404)
            if url.rstrip('/').endswith('/repos/tbrapor-arch/tusach-private'):
                return route.fulfill(status=200, body='{}')
            return route.fulfill(status=404, body='{}')
        pg.route('https://api.github.com/**', api)
        pg.evaluate("store.set('gistToken', 'test-token')")
        pg.reload()
        pg.wait_for_selector('.lgrid')
        pg.evaluate("location.hash = 'private'")
        try:
            pg.wait_for_function("!!window.PrivateModule && document.querySelector('#main .xm-empty') !== null", timeout=8000)
        except Exception:
            p('private module: the loader did not load module/app.js and route #private')
        got = pg.evaluate(f"[DATA.dict[{json.dumps(pub_id)}].en, (DATA.dict['private-only'] || {{}}).en]")
        if got[0] != pub_en:
            p(f'private module: the public card {pub_id} was replaced by a poorer one ("{got[0]}")')
        if got[1] != 'from the private module':
            p('private module: a card the page lacks was not added')
        pg.close()
    else:
        not_tested.append(f'the private-module merge (no {priv}/module: set TUSACH_PRIVATE)')
        print(f'\n*** NOT TESTED: the private-module loader and merge rule: {priv}/module not found '
              '(set TUSACH_PRIVATE to a checkout of tusach-private; TUSACH_SMOKE_ALLOW_UNTESTED=1 to pass anyway) ***')
    b.close()

print(f'\n{len(problems)} problem(s)' + (f'; NOT TESTED: {"; ".join(not_tested)}' if not_tested else ''))
if not_tested and os.environ.get('TUSACH_SMOKE_ALLOW_UNTESTED') != '1':
    sys.exit(2)
sys.exit(1 if problems else 0)
