"""Which lesson files a build uses, shared by build_app.py, lint.py, verify_words.py and coverage.py.

Real lessons: course/lessons/NN.yaml. While there is none (until the syllabus and word list are approved), the build
uses the test fixture tools/fixtures/lessons/*.yaml instead, and says so; TUSACH_FIXTURE=1 adds the fixture to real
lessons (for tests). TUSACH_COURSE=DIR reads lessons from another directory (tools/compare.py, tests).
"""
import glob
import os

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


def load(path):
    return yaml.safe_load(open(path, encoding='utf-8'))


def lessons():
    out = [load(f) for f in lesson_files()]
    return sorted(out, key=lambda d: d.get('id', 0))


def syllabus():
    p = os.path.join(ROOT, 'course/syllabus.yaml')
    return load(p) if os.path.exists(p) else {}
