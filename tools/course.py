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


def stray_files():
    """Files in the lesson directory that are not NN.yaml lessons (tools/lint.py reports them as errors)."""
    d = lesson_dir()
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d) if not re.fullmatch(r'\d\d+\.yaml', f))


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
    p = os.path.join(ROOT, 'course/syllabus.yaml')
    return load(p) if os.path.exists(p) else {}
