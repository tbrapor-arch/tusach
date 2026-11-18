"""Write the pins of a snapshot release (.github/workflows/snapshot.yml) into data/fetch.sh.

  python3 -I tools/pin_snapshot.py data-2026-11-18                 # reads SHA256SUMS of that release on GitHub
  python3 -I tools/pin_snapshot.py data-2026-11-18 --sums FILE     # the same from a local SHA256SUMS (tests)

Every `snap ID OUT FILE TAG SHA256` line of data/fetch.sh whose FILE is listed in SHA256SUMS gets TAG and its SHA-256.
A snap line whose file the release lacks stays as it was and is reported (exit 1).
"""
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FETCH = os.path.join(ROOT, 'data', 'fetch.sh')
REPO = 'tbrapor-arch/tusach'


def parse_sums(text):
    out = {}
    for line in text.splitlines():
        m = re.fullmatch(r'([0-9a-f]{64})\s+\*?(\S+)', line.strip())
        if m:
            out[m.group(2)] = m.group(1)
    return out


def rewrite(text, tag, sums):
    """(new fetch.sh text, files pinned, snap files the release lacks)."""
    pinned, lacking, out = [], [], []
    for line in text.split('\n'):
        p = line.split()
        if len(p) == 6 and p[0] == 'snap':
            if p[3] in sums:
                line = ' '.join(p[:4] + [tag, sums[p[3]]])
                pinned.append(p[3])
            else:
                lacking.append(p[3])
        out.append(line)
    return '\n'.join(out), pinned, lacking


def main():
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--sums']
    if len(args) != 1 or not re.fullmatch(r'data-\d{4}-\d\d-\d\d(\.\d+)?', args[0]):
        sys.exit(__doc__)
    tag = args[0]
    if '--sums' in sys.argv:
        text = open(sys.argv[sys.argv.index('--sums') + 1], encoding='utf-8').read()
    else:
        url = f'https://github.com/{REPO}/releases/download/{tag}/SHA256SUMS'
        text = urllib.request.urlopen(url, timeout=60).read().decode()
    new, pinned, lacking = rewrite(open(FETCH, encoding='utf-8').read(), tag, parse_sums(text))
    open(FETCH, 'w', encoding='utf-8').write(new)
    print(f'data/fetch.sh: {len(pinned)} file(s) pinned to {tag}: {", ".join(pinned)}')
    if lacking:
        print(f'NOT in the release (still as before): {", ".join(lacking)}')
        sys.exit(1)


if __name__ == '__main__':
    main()
