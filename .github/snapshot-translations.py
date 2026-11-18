"""Run by .github/workflows/snapshot.yml: read kaikki's raw English-Wiktionary extraction (JSON lines, already
narrowed by grep to lines that mention a Vietnamese translation) on stdin and write one TSV row per Vietnamese
translation of an English-language entry:

  english_word  pos  sense_number  sense  vietnamese  tags

sense_number is the 1-based index of the English sense the translation table belongs to when wiktextract attached it
to a sense (else 0); sense is the translation table's own gloss (else the sense's first gloss). Nothing else of the
raw file is kept. Licence: English Wiktionary, CC BY-SA 4.0 (ATTRIBUTION.md).
"""
import json
import sys


def clean(s):
    return ' '.join(str(s or '').split())


def is_vi(t):
    return t.get('lang_code') == 'vi' or t.get('code') == 'vi'


def main():
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
            out.write('\t'.join([clean(e['word']), clean(e.get('pos')), str(i), clean(sense), w,
                                 ','.join(clean(x) for x in t.get('tags') or [])]) + '\n')
            n += 1
    print(f'snapshot-translations: {n} rows', file=sys.stderr)


if __name__ == '__main__':
    main()
