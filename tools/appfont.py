"""The page's embedded font (tools/build_app.py): app/fonts/noto-sans-viet.woff2 with the Taigi vertical-line mark redrawn
(MARK_SHAPES), and the check that every letter and mark the page shows is in it and positioned on its letter.

    import appfont
    data = appfont.font_bytes()                       # woff2 bytes, embedded in the page
    problems, n = appfont.font_problems(texts, data)  # [] when every letter and mark of texts draws properly
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import vi  # noqa: E402

FONT = os.path.join(ROOT, 'app/fonts/noto-sans-viet.woff2')

# U+030D COMBINING VERTICAL LINE ABOVE (the Tâi-lô 8th-tone mark: ha̍k, o̍) is a short stroke in Noto Sans, 164 units
# tall and 80 wide: at text size on a phone it reads as a dot (review 5, finding 6; the positioning tables are there
# and work). The page's copy of the font draws it as a clear vertical line: MARK_SHAPES gives the outline (the same
# 4 points in the same order, so the weight axis's deltas still apply), patched in at build time; the file in
# app/fonts stays the upstream subset. Noto Sans is OFL 1.1 without a Reserved Font Name: a modified copy is allowed.
MARK_SHAPES = {'uni030D': [(30, 812), (30, 586), (-30, 586), (-30, 812)]}
MIN_STROKE_RATIO = 3          # a vertical-line mark at least 3 times as tall as wide (check_font)


def font_bytes(path=FONT):
    """The embedded font: app/fonts/noto-sans-viet.woff2 with MARK_SHAPES patched in (woff2 bytes)."""
    from fontTools.ttLib import TTFont
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    f = TTFont(path)
    glyf = f['glyf']
    for name, pts in MARK_SHAPES.items():
        g = glyf[name]
        if g.numberOfContours != 1 or len(g.coordinates) != len(pts):
            raise SystemExit(f'appfont: {name} in {path} is not the 4-point stroke MARK_SHAPES expects')
        g.coordinates = GlyphCoordinates(pts)
        g.recalcBounds(glyf)
    buf = io.BytesIO()
    f.flavor = 'woff2'
    f.save(buf)
    return buf.getvalue()




def font_problems(texts, font_bytes_):
    """What the embedded font cannot draw properly in `texts` (the page's Vietnamese and every reading a card shows):
    a letter or combining mark it lacks; a combining mark without mark-to-base positioning (GPOS) on the letter it
    follows (it would float beside it); a vertical-line mark that is not a vertical stroke (MIN_STROKE_RATIO)."""
    import unicodedata as ud
    from fontTools.ttLib import TTFont
    f = TTFont(io.BytesIO(font_bytes_))
    cmap = f.getBestCmap()
    probs, pairs = [], set()
    for t in texts:
        t = ud.normalize('NFC', t)
        for i, c in enumerate(t):
            if vi.CJK.match(c) or not (c.isalpha() or ud.category(c) == 'Mn'):
                continue
            if ord(c) not in cmap:
                probs.append(f'lacks U+{ord(c):04X} {ud.name(c, "?")} ("{t[:30]}")')
            elif ud.category(c) == 'Mn':
                j = i - 1
                while j >= 0 and ud.category(t[j]) == 'Mn':
                    j -= 1
                if j >= 0 and t[j].isalpha() and ord(t[j]) in cmap:
                    pairs.add((cmap[ord(t[j])], cmap[ord(c)], t[j] + c))
    positioned = set()
    lookups = f['GPOS'].table.LookupList.Lookup
    for lk in lookups:
        for st in lk.SubTable:
            st = st.ExtSubTable if lk.LookupType == 9 else st
            if getattr(st, 'LookupType', lk.LookupType) != 4:
                continue
            marks, bases = st.MarkCoverage.glyphs, st.BaseCoverage.glyphs
            for base, mark, _ in pairs:
                if mark in marks and base in bases:
                    cls = st.MarkArray.MarkRecord[marks.index(mark)].Class
                    if st.BaseArray.BaseRecord[bases.index(base)].BaseAnchor[cls] is not None:
                        positioned.add((base, mark))
    for base, mark, shown in sorted(pairs):
        if (base, mark) not in positioned:
            probs.append(f'no mark positioning for {shown} ({base} + {mark})')
    glyf = f['glyf']
    for name in MARK_SHAPES:
        g = glyf[name]
        if (g.yMax - g.yMin) < MIN_STROKE_RATIO * (g.xMax - g.xMin):
            probs.append(f'{name} is {g.xMax - g.xMin} wide and {g.yMax - g.yMin} tall: it draws as a dot, not a '
                         'vertical line')
    return probs, len({c for t in texts for c in ud.normalize('NFC', t) if c.isalpha() or ud.category(c) == 'Mn'})
