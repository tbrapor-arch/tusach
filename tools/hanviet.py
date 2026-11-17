"""Hán-Việt readings: Northern standard first, Southern variants labelled, the Unihan fallback (tools/build_db.py).

SOUTHERN: the Southern (Nguyễn-era taboo or regional) forms of Hán-Việt readings that the Thiều Chửu dictionary
sometimes gives instead of, or before, the Northern standard form. Each rule is (Southern form, Northern form, Mandarin
readings of the characters it applies to). The Mandarin condition keeps the rule to the characters of that sound
class, so a character whose standard reading merely looks Southern is left alone: 螢 huỳnh (yíng) is the standard
reading, 黃 huỳnh (huáng) is the Southern form of hoàng; 笨 bổn (bèn) and 舌 thiệt (shé) are not touched.

    hanviet.southern(reading, mandarin_readings)  -> the Northern form, or None
    hanviet.hv_shaped(reading, inventory)         -> a Unihan reading may stand in for a missing Hán-Việt reading

For a character whose reading is Southern: if the character also has the Northern form (any Hán-Việt source), the
Northern one is shown first and the Southern one after it, labelled "Southern variant"; if it has only the Southern
form (政 chánh, 甥 sanh), the Northern form is derived by the rule, stored with source `derived`, labelled "derived",
and shown first. Nothing in the database is edited by hand.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vi  # noqa: E402

SOUTHERN = [
    ('sanh', 'sinh', {'shēng'}),                 # 生 甥 笙
    ('chánh', 'chính', {'zhèng', 'zhēng'}),      # 正 政
    ('tánh', 'tính', {'xìng'}),                  # 性 姓
    ('thạnh', 'thịnh', {'shèng', 'chéng'}),      # 盛 晟
    ('nhơn', 'nhân', {'rén'}),                   # 人 仁
    ('chơn', 'chân', {'zhēn'}),                  # 真
    ('huỳnh', 'hoàng', {'huáng'}),               # 黃 (taboo of Nguyễn Hoàng); 螢 huỳnh yíng is standard
    ('phước', 'phúc', {'fú'}),                   # 福
    ('nhứt', 'nhất', {'yī'}),                    # 一
    ('võ', 'vũ', {'wǔ'}),                        # 武 (võ is also used in Northern fixed words: võ thuật)
]
_RULE = {vi.key(s): (vi.key(n), m) for s, n, m in SOUTHERN}


def southern(reading, mandarin):
    """The Northern form of `reading` if it is a Southern form for a character read `mandarin` (a set of pinyin with
    tone marks), else None."""
    r = _RULE.get(vi.key(reading))
    if r and set(mandarin) & r[1]:
        return r[0]
    return None


def shape(reading):
    """(initial, rhyme) of a reading (toneless), or None when it is not a Vietnamese syllable."""
    base = vi.toneless(vi.key(reading))
    if vi.syllable_problems(vi.key(reading)):
        return None
    ps = vi.parses(base)
    return ps[0] if ps else None


def inventory(readings):
    """The initials and rhymes seen in a list of Hán-Việt readings (Thiều Chửu's): what a Hán-Việt syllable may be."""
    inits, rhymes = set(), set()
    for r in readings:
        s = shape(r)
        if s:
            inits.add(s[0])
            rhymes.add(s[1])
    return inits, rhymes


def hv_shaped(reading, inv):
    """A Unihan kVietnamese reading may stand in for a missing Hán-Việt reading only when it is a valid syllable whose
    initial and rhyme both occur among the Thiều Chửu readings (Nôm readings such as 'mắt', 'chẻm' do not)."""
    s = shape(reading)
    return bool(s) and s[0] in inv[0] and s[1] in inv[1]


def _test():
    assert southern('sanh', {'shēng'}) == 'sinh' and southern('chánh', {'zhèng'}) == 'chính'
    assert southern('huỳnh', {'yíng'}) is None and southern('huỳnh', {'huáng'}) == 'hoàng'
    assert southern('sinh', {'shēng'}) is None
    inv = inventory(['nhất', 'bộ', 'đại', 'học'])
    assert hv_shaped('nhất', inv) and hv_shaped('bộ', inv) and not hv_shaped('mắt', inv) and not hv_shaped('xyz', inv)
    print('hanviet.py: all tests passed')


if __name__ == '__main__':
    _test()
