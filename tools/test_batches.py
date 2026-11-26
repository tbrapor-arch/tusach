"""The cheaper batch method end to end (26 Nov 2026), on copies: no file of the repository is changed.

  python3 -I tools/test_batches.py        (`make test`; needs the public database)

1. A throwaway lesson 29 (TEST, not course content), beyond the approved word lists, in a temporary copy of the
   real lessons 1-28 only (so the test does not depend on how many real lessons exist): plain lint passes in the draft state (its words declared in its own new_words; I "draft words").
2. Its guarantees in the draft state: a word already taught, a new word in a review lesson, chars in new_words and a
   doubt pointing to no line are errors (lint --lessons, the quiet check).
3. tools/wordlist.py --from-lessons generates its word list and the approval table; the list passes lint --wordlist
   and the plan's checks as the draft list.
4. Approval as today (the list added to approved.word_list.file of a copy of the syllabus, tools/plan.py --write on
   the copies): plain lint passes, lesson 29 now checked against the approved list.
Also: tools/brief.py prints its digest, the plan and the taught words within its size target; --doubts finds the
lesson's doubt.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
failures = []


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


L29 = """id: 29
title: {vi: Ở ngân_hàng, en: At the bank (TEST)}
review: false
setting: TEST FIXTURE of tools/test_batches.py, not course content.
dialogue:
- {n: 1, speaker: Sacha, vi: "Chào chị, tôi muốn đổi tiền.", en: "Hello, I'd like to change money."}
- {n: 2, speaker: Clerk, vi: "Vâng, ngân_hàng này đổi tiền.", en: "Yes, this bank changes money."}
notes:
- {ref: 2, topic: usage, text: "ngân hàng \\"bank\\"; đổi \\"to change\\"."}
new_words:
- {w: ngân_hàng, en: bank}
- {w: đổi, en: "to change, to exchange"}
exercises:
  translate:
  - {vi: "Ngân_hàng ở đâu?", en: "Where is the bank?"}
doubt:
- {line: 2, text: "Is this how a clerk would answer?"}
"""
L30_BAD = """id: 30
title: {vi: Thử, en: Test}
review: false
setting: TEST.
dialogue:
- {n: 1, speaker: Lan, vi: "Tôi là học_sinh.", en: "I'm a student."}
notes: []
new_words:
- {w: học_sinh, en: student, chars: 學生}
doubt:
- {line: 7, text: "no such line"}
"""
L35_BAD = """id: 35
title: {vi: Ôn tập, en: Review}
review: true
setting: TEST.
dialogue:
- {n: 1, speaker: Lan, vi: "Tôi muốn rút tiền.", en: "I want to take out money."}
notes: []
new_words:
- {w: rút, en: to withdraw}
"""


def run(args, env):
    r = subprocess.run([sys.executable, '-I'] + args, cwd=ROOT, capture_output=True, text=True,
                       env=dict(os.environ, **env))
    return r.returncode, r.stdout + r.stderr


def errors(out):
    m = re.search(r'(\d+) error\(s\)\s*$', out.strip().split('\n')[-1]) or re.search(r'(\d+) error\(s\)', out)
    return int(m.group(1)) if m else -1


with tempfile.TemporaryDirectory() as tmp:
    les = os.path.join(tmp, 'lessons')
    # only the real lessons before the throwaway lesson 29: later real lessons would be checked against a plan
    # and word lists the test replaces, and their words would no longer be new
    shutil.copytree(os.path.join(ROOT, 'course/lessons'), les,
                    ignore=lambda d, names: [x for x in names if re.fullmatch(r'\d\d\.yaml', x) and int(x[:2]) >= 29])
    open(os.path.join(les, '29.yaml'), 'w', encoding='utf-8').write(L29)
    syl_text = open(os.path.join(ROOT, 'course/syllabus.yaml'), encoding='utf-8').read()
    prop = os.path.join(tmp, 'syllabus-proposal.md')
    shutil.copy(os.path.join(ROOT, 'course/proposal/syllabus-proposal.md'), prop)
    syl = os.path.join(tmp, 'syllabus.yaml')
    open(syl, 'w', encoding='utf-8').write(syl_text)
    env = {'TUSACH_COURSE': les, 'TUSACH_SYLLABUS': syl}

    # 1. the draft state
    rc, out = run([os.path.join(HERE, 'lint.py')], env)
    ok(rc == 0 and errors(out) == 0, f'draft state: plain lint passes with lesson 29 beyond the approved lists '
                                     f'({errors(out)} errors: {[x for x in out.splitlines() if ": E " in x][:3]})')
    ok('29.yaml:0: I draft words: 2 new words chosen in this lesson' in out, 'lint names the draft state of lesson 29')

    # 2. what the draft state still refuses
    bad = os.path.join(tmp, 'lessons-bad')
    shutil.copytree(les, bad)
    open(os.path.join(bad, '30.yaml'), 'w', encoding='utf-8').write(L30_BAD)
    open(os.path.join(bad, '35.yaml'), 'w', encoding='utf-8').write(L35_BAD)
    rc, out = run([os.path.join(HERE, 'lint.py'), '--lessons', '30-35'], dict(env, TUSACH_COURSE=bad))
    ok('30.yaml:new_words[0]: E học_sinh is already taught by lesson 16' in out, 'draft: a word already taught')
    ok('chars / label in new_words' in out, 'draft: chars in new_words (a claim for the lexicon)')
    ok('doubt line 7 is not a line of the dialogue' in out, 'a doubt pointing to no line')
    ok('35.yaml:new_words: E a review lesson has no new word' in out, 'a new word in a review lesson')
    ok(rc == 1 and out.strip().splitlines()[-1].startswith('lint L30-35:'), 'quiet check: exit 1, one summary line')

    # 3. the word list from the lessons, and the approval table
    wl = os.path.join(tmp, 'wordlist-4.tsv')
    rc, out = run([os.path.join(HERE, 'wordlist.py'), '--from-lessons', '29', '29', wl], env)
    rows = open(wl, encoding='utf-8').read().splitlines() if os.path.exists(wl) else []
    ok(rc == 0 and len(rows) == 3 and rows[1].startswith('29\tngân_hàng\tbank\t'),
       f'wordlist.py --from-lessons: header + 2 rows, the lesson\'s English ({rows[1:2]})')
    table = os.path.join(tmp, 'wordlist-4-approval.md')
    tab = open(table, encoding='utf-8').read() if os.path.exists(table) else ''
    ok('| 29 | ngân hàng | bank | Hán-Việt |' in tab and '| 29 | đổi |' in tab, 'the approval table: one line a word')
    rc, out = run([os.path.join(HERE, 'lint.py'), '--wordlist', wl], env)
    ok(rc == 0, f'the generated list passes lint --wordlist ({out.strip().splitlines()[-1:]})')
    draft_syl = re.sub(r'(?m)^draft: .*$', f'draft: {{word_list: {wl}, proposal: {prop}}}', syl_text)
    open(syl, 'w', encoding='utf-8').write(draft_syl)
    rc, out = run([os.path.join(HERE, 'plan.py'), '--write'], env)
    rc, out = run([os.path.join(HERE, 'plan.py'), '--check'], env)
    ok(rc == 0, f'the generated list as the draft list: the plan\'s checks pass ({out.strip().splitlines()[-3:]})')

    # 4. approval as today: the list added to approved.word_list.file
    text = open(syl, encoding='utf-8').read()
    text = re.sub(r'(?m)^(  word_list: \{.*file: \[)([^\]]*)\]', lambda m: f'{m.group(1)}{m.group(2)}, {wl}]', text)
    ok(wl in text.split('draft:')[0], 'test syllabus: the generated list added to approved.word_list.file')
    open(syl, 'w', encoding='utf-8').write(text)
    rc, out = run([os.path.join(HERE, 'plan.py'), '--write'], env)
    plan_l29 = [x for x in open(syl, encoding='utf-8').read().splitlines() if '{n: 29,' in x]
    ok(plan_l29 and 'new_words: {native: 1, hv: 1}' in plan_l29[0], f'plan.py --write: L29 counts from the list '
                                                                     f'({plan_l29[:1]})')
    rc, out = run([os.path.join(HERE, 'lint.py')], env)
    ok(rc == 0 and errors(out) == 0, f'approved: plain lint passes ({[x for x in out.splitlines() if ": E " in x][:3]})')
    ok('I draft words' not in out, 'approved: lesson 29 is no longer a draft (checked against the approved list)')
    l29b = L29.replace('- {w: đổi, en: "to change, to exchange"}', '- {w: đổi, en: "to change, to exchange"}\n'
                       '- {w: rút, en: to withdraw}').replace('Ngân_hàng ở đâu?', 'Ngân_hàng rút tiền.')
    open(os.path.join(les, '29.yaml'), 'w', encoding='utf-8').write(l29b)
    rc, out = run([os.path.join(HERE, 'lint.py'), '--lessons', '29'], env)
    ok('rút is not in the approved word list' in out, 'approved: a word added later to lesson 29 is refused again')

    # brief.py
    rc, out = run([os.path.join(HERE, 'brief.py'), '29', '35'], env)
    size = re.search(r'\[brief: ([\d,]+) characters\]', out)
    ok(rc == 0 and size and int(size.group(1).replace(',', '')) < 45000 and '## Rules' in out and 'L29 At the bank'
       in out and 'L28: ' not in out and 'L27: còn=' in out, f'brief.py 29 35: digest, plan, taught words, size '
                                                             f'{size.group(1) if size else "?"}')
    rc, out = run([os.path.join(HERE, 'brief.py'), '--doubts'], env)
    ok('L29.2: Is this how a clerk would answer?' in out, 'brief.py --doubts collects the lessons\' doubts')

print(f'{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
