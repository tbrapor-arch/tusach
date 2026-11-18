"""Run by .github/workflows/snapshot.yml: read kaikki's raw English-Wiktionary extraction (JSON lines, already
narrowed by grep to lines that mention a Vietnamese translation) on stdin and write one TSV row per Vietnamese
translation of an English-language entry:

  english_word  pos  sense_number  sense  vietnamese  tags

With --lang vi,cmn,yue,nan,zh: one row per translation into any of these languages, with the language code as a 7th
column (the Chinese rows of the tables that have a Vietnamese one: the sense check of Hán-Việt analyses).

sense_number is the 1-based index of the English sense the translation table belongs to when wiktextract attached it
to a sense (else 0); sense is the translation table's own gloss (else the sense's first gloss). Nothing else of the
raw file is kept. Licence: English Wiktionary, CC BY-SA 4.0 (ATTRIBUTION.md).
"""
import json
import sys


def clean(s):
    return ' '.join(str(s or '').split())


LANGS = {'vi'}


def code(t):
    return t.get('lang_code') or t.get('code') or ''


def is_vi(t):
    return code(t) in LANGS


def main():
    global LANGS
    multi = '--lang' in sys.argv
    if multi:
        LANGS = set(sys.argv[sys.argv.index('--lang') + 1].split(','))
    out = sys.stdout
    n = 0
    for line in sys.stdin:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get('lang_code') != 'en' or not e.get('word'):
            continue
        rows = []
        for t in e.get('translations') or []:
            if is_vi(t):
                rows.append((0, t.get('sense') or '', t))
        for i, s in enumerate(e.get('senses') or [], 1):
            g = (s.get('glosses') or [''])[-1]
            for t in s.get('translations') or []:
                if is_vi(t):
                    rows.append((i, t.get('sense') or g, t))
        for i, sense, t in rows:
            w = clean(t.get('word'))
            if not w:
                continue
            cols = [clean(e['word']), clean(e.get('pos')), str(i), clean(sense), w,
                    ','.join(clean(x) for x in t.get('tags') or [])]
            out.write('\t'.join(cols + ([code(t)] if multi else [])) + '\n')
            n += 1
    print(f'snapshot-translations: {n} rows', file=sys.stderr)


if __name__ == '__main__':
    main()
