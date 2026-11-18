"""Tests of the loud-failure rules for the data sources (`make test`): data/fetch.sh and data/fetch-lib.sh, the
snapshot pins, and the publication gate (tools/build_db.py, tools/build_app.py, tools/site.py).

  python3 -I tools/test_fetch.py

Network-free: the git source is a local repository, the files are file:// URLs, the npm tarball is made here.
"""
import hashlib
import os
import re
import sqlite3
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pin_snapshot  # noqa: E402

failures = []


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


def sh(script, env=None, cwd=ROOT):
    e = {k: v for k, v in os.environ.items() if k != 'TUSACH_ALLOW_MISSING'}
    e.update(env or {})
    r = subprocess.run(['sh', '-c', script], cwd=cwd, env=e, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def lib(body, raw, env=None):
    return sh(f'. data/fetch-lib.sh; {body}; finish', dict(env or {}, TUSACH_RAW=raw))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


with tempfile.TemporaryDirectory() as tmp:
    raw = os.path.join(tmp, 'raw')
    # 1. a PENDING snapshot is a missing source, and a missing source fails the script; only the list lets it go on
    code, out = lib('snap wiktionary k/k.jsonl k.jsonl PENDING PENDING', raw)
    ok(code == 1 and 'MISSING wiktionary' in out and 'PENDING' in out, 'fetch.sh exits 1 on a PENDING snapshot')
    code, out = lib('snap wiktionary k/k.jsonl k.jsonl PENDING PENDING', raw,
                    {'TUSACH_ALLOW_MISSING': 'tatoeba,wiktionary'})
    ok(code == 0 and 'allowed by TUSACH_ALLOW_MISSING' in out, 'only TUSACH_ALLOW_MISSING lets it go on')
    # the real fetch.sh: every snapshot source pinned to a release of ours by SHA-256, none PENDING, and never
    # fetched from the moving upstream URL
    fetch_sh = open(os.path.join(ROOT, 'data/fetch.sh'), encoding='utf-8').read()
    code_lines = [x for x in fetch_sh.splitlines() if x.strip() and not x.lstrip().startswith('#')]
    snaps = [x.split() for x in code_lines if x.split()[0] == 'snap']
    ok(len(snaps) == 5 and all(len(p) == 6 and re.fullmatch(r'data-\d{4}-\d\d-\d\d(\.\d+)?', p[4])
                               and re.fullmatch(r'[0-9a-f]{64}', p[5]) for p in snaps)
       and not any('://kaikki.org' in x or 'tatoeba.org/' in x for x in code_lines),
       'every snapshot source is pinned to a release tag and a SHA-256, never to the moving upstream URL')

    # 2. a file whose SHA-256 differs is refused and fails the script
    src = os.path.join(tmp, 'f.txt')
    open(src, 'w').write('content\n')
    code, out = lib(f'get x x/f.txt file://{src} {"0" * 64}', raw)
    ok(code == 1 and 'REFUSED' in out and os.path.exists(os.path.join(raw, 'x/f.txt.refused')), 'a wrong SHA-256 is refused, exit 1')
    code, out = lib(f'get x x/f.txt file://{src} {sha(src)}', raw)
    ok(code == 0 and 'ok  x' in out, 'the right SHA-256 passes')

    # 3. a git source: verified as a clean checkout at the pinned commit
    repo = os.path.join(tmp, 'repo')
    os.makedirs(repo)
    g = ['git', '-C', repo, '-c', 'user.name=t', '-c', 'user.email=t@t']
    subprocess.run(['git', 'init', '-q', repo], check=True)
    open(os.path.join(repo, 'data.txt'), 'w').write('pinned\n')
    subprocess.run(g + ['add', '.'], check=True)
    subprocess.run(g + ['commit', '-qm', 'one'], check=True)
    pin = subprocess.run(g + ['rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    code, out = lib(f'fetch r r file://{repo} {pin}', raw)
    ok(code == 0 and 'clean checkout' in out, 'a git source at its pinned commit')
    open(os.path.join(raw, 'r/data.txt'), 'w').write('edited by hand\n')
    open(os.path.join(raw, 'r/extra.txt'), 'w').write('not in the commit\n')
    code, out = lib(f'fetch r r file://{repo} {pin}', raw)
    ok(code == 0 and 'restored' in out and open(os.path.join(raw, 'r/data.txt')).read() == 'pinned\n'
       and not os.path.exists(os.path.join(raw, 'r/extra.txt')), 'an edited checkout is restored to the pinned content')
    code, out = lib(f'fetch r r file://{repo} {"1" * 40}', raw)
    ok(code == 1 and 'MISSING r' in out, 'a commit that does not exist fails')

    # 4. an npm tarball: SHA-256 pinned, extracted afresh
    pkgd = os.path.join(tmp, 'pkgsrc', 'package')
    os.makedirs(pkgd)
    open(os.path.join(pkgd, 'cedict.json'), 'w').write('[]')
    os.makedirs(os.path.join(raw, 'n'))
    tgz = os.path.join(raw, 'n', 'p-1.0.tgz')
    with tarfile.open(tgz, 'w:gz') as t:
        t.add(pkgd, 'package')
    good = sha(tgz)
    code, out = lib(f'npmpkg n n p 1.0 {good}', raw)
    open(os.path.join(raw, 'n/package/cedict.json'), 'w').write('[tampered]')
    code, out = lib(f'npmpkg n n p 1.0 {good}', raw)
    ok(code == 0 and open(os.path.join(raw, 'n/package/cedict.json')).read() == '[]',
       'the npm package is re-extracted from the verified tarball')
    code, out = lib(f'npmpkg n n p 1.0 {"2" * 64}', raw)
    ok(code == 1 and 'REFUSED' in out, 'an npm tarball with another SHA-256 is refused')

    # 5. snapshot pins
    text = 'snap wiktionary kaikki/k.jsonl k.jsonl PENDING PENDING\nsnap tatoeba t/a.bz2 a.bz2 PENDING PENDING\n'
    new, pinned, lacking = pin_snapshot.rewrite(text, 'data-2026-11-18', pin_snapshot.parse_sums(f'{"a" * 64}  k.jsonl\n'))
    ok(f'snap wiktionary kaikki/k.jsonl k.jsonl data-2026-11-18 {"a" * 64}' in new and lacking == ['a.bz2'],
       'pin_snapshot writes tag and SHA-256, and reports a file the release lacks')
    code, out = lib('snap s s/a a data-2026-11-18 ' + '3' * 64, raw)
    ok(code == 1 and 'github.com/tbrapor-arch/tusach/releases/download/data-2026-11-18/a' in out,
       'a pinned snapshot is fetched from the release asset URL')

    # 6. build_db: a missing source fails the build unless allowed, and is recorded in meta.missing
    db = os.path.join(tmp, 'vi.db')
    env = {k: v for k, v in os.environ.items() if k != 'TUSACH_ALLOW_MISSING'}
    r = subprocess.run([sys.executable, '-I', 'tools/build_db.py', 'tools/fixtures/raw', db], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    ok(r.returncode != 0 and 'FAILED' in r.stdout + r.stderr and not os.path.exists(db), 'build_db fails on a missing source')
    allow = 'wiktionary-tr,thieuchuu,unihan,rime,moe,cedict,tatoeba,tatoeba-challenge,frequencywords'
    r = subprocess.run([sys.executable, '-I', 'tools/build_db.py', 'tools/fixtures/raw', db], cwd=ROOT,
                       env=dict(env, TUSACH_ALLOW_MISSING=allow), capture_output=True, text=True)
    meta = dict(sqlite3.connect(db).execute('SELECT key, value FROM meta')) if r.returncode == 0 else {}
    ok(r.returncode == 0 and 'rime' in meta.get('missing', '').split(), 'with the list it builds and records meta.missing')

    # 7. the publication gate: build_app refuses such a database unless allowed; site.py refuses its page
    out_dir = os.path.join(tmp, 'dist')
    benv = dict(env, TUSACH_DB=db, TUSACH_OUT=out_dir, TUSACH_STORE=os.path.join(tmp, 'cards.json'))
    r = subprocess.run([sys.executable, '-I', 'tools/build_app.py'], cwd=ROOT, env=benv, capture_output=True, text=True)
    ok(r.returncode != 0 and 'REFUSED' in r.stdout + r.stderr, 'build_app refuses a database with meta.missing')
    r = subprocess.run([sys.executable, '-I', 'tools/build_app.py'], cwd=ROOT, env=dict(benv, TUSACH_ALLOW_MISSING=allow),
                       capture_output=True, text=True)
    ok(r.returncode == 0 and 'NOT PUBLISHABLE' in r.stdout, 'allowed: it builds and says the page is not publishable')
    r = subprocess.run([sys.executable, '-I', 'tools/site.py', os.path.join(tmp, 'site')], cwd=ROOT,
                       env=dict(env, TUSACH_DIST=out_dir), capture_output=True, text=True)
    ok(r.returncode != 0 and 'REFUSED' in r.stdout + r.stderr, 'site.py refuses to publish a page built with missing sources')

    # 8. the workflows: pages runs the same checks as check, and never allows a missing source
    pages = open(os.path.join(ROOT, '.github/workflows/pages.yml'), encoding='utf-8').read()
    ok(all(x in pages for x in ('make db\n', 'make db-nc', 'make lint', 'make test', 'make app', 'make check',
                                "TUSACH_ALLOW_MISSING: ''")), 'pages.yml runs db, db-nc, lint, test, app, check; no escape')
    snap = open(os.path.join(ROOT, '.github/workflows/snapshot.yml'), encoding='utf-8').read()
    ok('contents: write' in snap and 'workflow_dispatch' in snap and 'data/snapshot-request.txt' in snap
       and 'SHA256SUMS' in snap and 'NOTES.md' in snap, 'snapshot.yml: dispatch or commit, release assets, sums, notes')

print(f'\n{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
