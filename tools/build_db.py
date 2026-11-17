"""Build the Vietnamese learner database from the pinned open sources in data/raw (data/fetch.sh).

    python3 -I tools/build_db.py data/raw data/build/vi.db            # public build: commercial-use sources only
    python3 -I tools/build_db.py data/raw data/build/vi-nc.db --nc    # private build: also non-commercial sources

The two builds go to two different files and say which they are in `meta.nc`: tools/cards.py open_db() refuses a
public build (the app page) from vi-nc.db and a private build (the private module) from vi.db, so the rule "no
non-commercial source on the public page" is enforced by the code, not by a document.

The source list is EMPTY on purpose (17 Nov 2026): the licences of the candidates in the handover (section 6) are being
verified by another session. TODO(sources): for each verified source, add it to data/fetch.sh pinned to a version, a row
to ATTRIBUTION.md, and an entry to SOURCES below with a loader. Nothing else in the build changes.

The invented test fixture (tools/fixtures/dict.yaml) is always loaded, as source `fixture` (fixture = 1): it lets
`make app`, `make lint` and tools/smoke.py run before any real source exists. tools/lint.py refuses a real lesson that
uses a word only the fixture has.
"""
import datetime
import os
import sqlite3
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import vi  # noqa: E402

FIXTURE = os.path.join(HERE, 'fixtures', 'dict.yaml')

# Each source: {'id', 'name', 'version', 'licence', 'url', 'commercial_ok': bool, 'load': function(raw_dir, add)}.
# `add` is the Adder below. TODO(sources): empty until the licences are verified (see the docstring).
SOURCES = []


class Adder:
    """What a source loader writes through. Every text is put in NFC and keyed with tools/vi.py."""

    def __init__(self, con, source):
        self.con, self.source = con, source
        self.n = 0

    def entry(self, word, english='', chars='', label='', pos='', tag='', src_id='', freq=None, examples=()):
        word = vi.nfc(word).strip()
        cur = self.con.execute(
            'INSERT INTO entry(source, src_id, word, key, tkey, toneless, tag, pos, english, chars, label, freq) '
            'VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            (self.source, src_id, word, vi.key(word), vi.tkey(word), vi.toneless(vi.key(word)), tag or '', pos,
             vi.nfc(english), vi.nfc(chars), label or '', freq))
        for ex in examples:
            self.con.execute('INSERT INTO example(entry_id, source, vi, en) VALUES (?,?,?,?)',
                             (cur.lastrowid, self.source, vi.nfc(ex.get('vi')), vi.nfc(ex.get('en'))))
        self.n += 1
        return cur.lastrowid

    def hanviet(self, char, reading):
        self.con.execute('INSERT INTO hanviet VALUES (?,?,?)', (char, vi.nfc(reading).lower(), self.source))

    def chinese(self, chars, lang, reading):
        assert lang in ('yue', 'nan', 'cmn'), lang
        self.con.execute('INSERT INTO chinese VALUES (?,?,?,?)', (chars, lang, vi.nfc(reading), self.source))


def load_fixture(add):
    d = yaml.safe_load(open(FIXTURE, encoding='utf-8'))
    for e in d['entries']:
        add.entry(e['word'], e.get('en', ''), e.get('chars', ''), e.get('label', ''), e.get('pos', ''), e.get('tag', ''),
                  examples=[e['example']] if e.get('example') else ())
    for ch, r in (d.get('hanviet') or {}).items():
        for x in str(r).split('/'):
            add.hanviet(ch, x.strip())
    for chars, langs in (d.get('chinese') or {}).items():
        for lang, r in langs.items():
            add.chinese(chars, lang, r)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2:
        sys.exit(__doc__)
    raw, out = args
    nc = '--nc' in sys.argv
    # one database rule, enforced here and in tools/cards.py open_db(): the non-commercial build has its own file
    if nc != out.endswith('-nc.db'):
        sys.exit(f'build_db: refusing to write a {"non-commercial" if nc else "public"} build to {out} '
                 f'(public builds go to *.db, non-commercial ones to *-nc.db)')
    tmp = out + '.tmp'
    if os.path.exists(tmp):
        os.remove(tmp)
    con = sqlite3.connect(tmp)
    con.executescript(open(os.path.join(HERE, 'schema.sql'), encoding='utf-8').read())
    used = []
    for s in SOURCES:
        if not s['commercial_ok'] and not nc:
            continue
        con.execute('INSERT INTO source VALUES (?,?,?,?,?,?,0)',
                    (s['id'], s['name'], s['version'], s['licence'], s['url'], int(s['commercial_ok'])))
        add = Adder(con, s['id'])
        s['load'](raw, add)
        used.append(s['id'])
        print(f"{s['id']}: {add.n} entries")
    con.execute("INSERT INTO source VALUES ('fixture', 'TEST FIXTURE (invented entries, not course content)', '', "
                "'CC0 (written for this repository)', '', 1, 1)")
    add = Adder(con, 'fixture')
    load_fixture(add)
    print(f'fixture: {add.n} entries (test fixture, tools/fixtures/dict.yaml)')
    if not SOURCES:
        print('build_db: no data source yet (TODO(sources) in tools/build_db.py): the database holds the fixture only')
    # frequency rank over all sources that give a frequency
    for i, (eid,) in enumerate(con.execute('SELECT id FROM entry WHERE freq IS NOT NULL ORDER BY freq DESC').fetchall()):
        con.execute('UPDATE entry SET freq_rank=? WHERE id=?', (i + 1, eid))
    con.executemany('INSERT INTO meta VALUES (?,?)', [('nc', '1' if nc else '0'),
                                                      ('built', datetime.date.today().isoformat()),
                                                      ('sources', ' '.join(used))])
    con.commit()
    con.close()
    os.replace(tmp, out)
    print(f'{out}: {"non-commercial (private builds only)" if nc else "public"} build')


if __name__ == '__main__':
    main()
