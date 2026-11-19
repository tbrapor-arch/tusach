"""Which lesson files a build uses, shared by build_app.py, lint.py, verify_words.py and coverage.py.

Real lessons: course/lessons/NN.yaml. While there is none (until the syllabus and word list are approved), the build
uses the test fixture tools/fixtures/lessons/*.yaml instead, and says so; TUSACH_FIXTURE=1 adds the fixture to real
lessons (for tests). TUSACH_COURSE=DIR reads lessons from another directory (tools/compare.py, tests).
"""
import glob
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_DIR = os.path.join(ROOT, 'tools/fixtures/lessons')


def lesson_dir():
    return os.environ.get('TUSACH_COURSE') or os.path.join(ROOT, 'course/lessons')


def real_files():
    return sorted(glob.glob(os.path.join(lesson_dir(), '[0-9][0-9]*.yaml')))


def fixture_files():
    return sorted(glob.glob(os.path.join(FIXTURE_DIR, '[0-9][0-9]*.yaml')))


def lesson_files():
    real = real_files()
    if not real or os.environ.get('TUSACH_FIXTURE') == '1':
        return real + fixture_files()
    return real


def is_fixture_path(path):
    return os.path.abspath(path).startswith(os.path.abspath(FIXTURE_DIR) + os.sep)


# the one other file allowed beside the lessons: the hesitations for a native speaker (never read by the build)
NOT_SHOWN = {'NOTES-for-native-speaker.md'}


def stray_files():
    """Files in the lesson directory that are not NN.yaml lessons (tools/lint.py reports them as errors)."""
    d = lesson_dir()
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d) if not re.fullmatch(r'\d\d+\.yaml', f) and f not in NOT_SHOWN)


def load(path):
    """A lesson file. `fixture: true` counts only under tools/fixtures/: anywhere else it is dropped (the lesson is
    treated as real) and tools/lint.py reports it."""
    d = yaml.safe_load(open(path, encoding='utf-8'))
    if isinstance(d, dict) and d.get('fixture') and not is_fixture_path(path):
        d = dict(d, fixture=False, fixture_claimed=True)
    return d


def lessons():
    out = [load(f) for f in lesson_files()]
    return sorted(out, key=lambda d: d.get('id', 0))


def syllabus():
    """course/syllabus.yaml; TUSACH_SYLLABUS=FILE reads another copy (tests: a syllabus not yet approved)."""
    p = os.environ.get('TUSACH_SYLLABUS') or os.path.join(ROOT, 'course/syllabus.yaml')
    return load(p) if os.path.exists(p) else {}


def approved_word_lists(syl=None):
    """The approved word lists: approved.word_list.file of course/syllabus.yaml, one path or a list of paths (the owner
    approves one list after another: [course/proposal/wordlist-2.tsv, course/proposal/wordlist-3.tsv])."""
    syl = syllabus() if syl is None else syl
    wl = (syl.get('approved') or {}).get('word_list')
    f = wl.get('file') if isinstance(wl, dict) else None
    return [x for x in ([f] if isinstance(f, str) else list(f or [])) if x]


def plan_word_lists(syl=None):
    """Every word list of the plan, in order: the approved ones, then the draft (draft.word_list) unless it is one of
    them. The plan, its checks and lint read them together: a word list builds on the ones before it."""
    syl = syllabus() if syl is None else syl
    out = approved_word_lists(syl)
    d = (syl.get('draft') or {}).get('word_list')
    return out + ([d] if d and d not in out else [])


WORDLIST_COLS = ('lesson', 'word', 'english', 'freq_rank', 'type', 'characters', 'han_viet', 'cantonese',
                 'taigi_literary', 'mandarin', 'note')
PLAN_KEYS = {'n', 'en', 'vi', 'review', 'grammar', 'bridge', 'strand', 'lines', 'new_words'}


def wordlist(path):
    """The rows of a word list in the 11-column format of course/proposal/wordlist-2.tsv (WORDLIST_COLS, with a header
    line). Raises ValueError when the header is not that format."""
    path = path if os.path.isabs(path) else os.path.join(ROOT, path)
    lines = open(path, encoding='utf-8').read().split('\n')
    head = tuple(lines[0].split('\t'))
    if head != WORDLIST_COLS:
        raise ValueError(f'{os.path.relpath(path, ROOT)}: header must be the 11 columns {" ".join(WORDLIST_COLS)}')
    out = []
    for i, line in enumerate(lines[1:], 2):
        if not line.strip() or line.startswith('#'):
            continue
        p = line.split('\t')
        if len(p) != len(WORDLIST_COLS):
            raise ValueError(f'{os.path.relpath(path, ROOT)}:{i}: {len(p)} columns, not {len(WORDLIST_COLS)}')
        out.append(dict(zip(WORDLIST_COLS, p), line=i))
    return out
