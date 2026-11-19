"""Tests of the review 6 lint changes (run by `make test`; needs data/build/vi.db).

8   lint: an exercise may not be the example a card of one of its words shows (lexicon or Tatoeba example).
13  lint: a false-friend note (topic false-friend) names a lexicon false friend's characters next to its word; other
    characters only from that row's false-friend note; at most one per lesson.
(15, the cast names in English notes, is in tools/test_plan.py.)
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint  # noqa: E402

failures = []


def ok(cond, what):
    print(('ok    ' if cond else 'FAIL  ') + what)
    if not cond:
        failures.append(what)


lint.D = lint.DB_(lint.DB)
lint.listed = None

# 13. false friends
ok(lint.false_friend_problem('bác sĩ is 博士 "doctor", but Chinese 博士 is a PhD; a physician is 醫生.') == '',
   'lint: bác sĩ 博士 with 醫生 from its false-friend note is a false-friend note')
ok(lint.false_friend_problem('tuần is 旬, ten days in Chinese.') == '', 'lint: tuần 旬 is a false-friend note')
ok(lint.false_friend_problem('sinh is 生 (Mandarin shēng).') != '', 'lint: 生 sinh is no false friend (no such note)')
ok(lint.false_friend_problem('bác sĩ is 博士; 大學 is a university.') != '',
   "lint: characters outside the row's characters and note are refused")
ok(lint.false_friend_problem('bác sĩ is a false friend.') != '', 'lint: a false-friend note without characters')
keys, tags = lint.load_db()
L = {'id': 12, 'title': {'vi': 'x', 'en': 'x'}, 'dialogue': [{'n': 1, 'speaker': 'A', 'vi': 'Tôi gặp bác_sĩ.', 'en': 'x'}],
     'notes': [{'ref': 1, 'topic': 'false-friend', 'text': 'bác sĩ is 博士, a PhD in Chinese.'},
               {'ref': 1, 'topic': 'false-friend', 'text': 'tuần is 旬, ten days in Chinese.'}],
     'new_words': []}
msgs = []
lint.lint('/x/12.yaml', L, keys, tags, collections.defaultdict(set), set(), msgs, collections.defaultdict(set))
ok(any('more than one false-friend note' in m for _, m in msgs), 'lint: two false-friend notes in one lesson are refused')

# 8. an exercise equal to a card example
L1 = {'id': 1, 'dialogue': [{'n': 1, 'vi': 'Chào chị.'}], 'notes': [], 'new_words': [],
      'exercises': {'translate': [{'vi': 'Em tên là gì?', 'en': 'x'}, {'vi': 'Chị Lan tên là gì?', 'en': 'x'}],
                    'fill': [{'vi': 'Tôi ___ cái này.', 'answer': 'lấy', 'en': 'x'}]}}
msgs = []
lint.card_example_copies([('/x/01.yaml', L1)], msgs)
out = '\n'.join(m for _, m in msgs)
ok('translate[0]' in out and 'card em' in out, 'lint: an exercise equal to the lexicon example of em is refused')
ok('fill[0]' in out, 'lint: a fill exercise, once filled, equal to a card example (cái, lấy) is refused')
ok('translate[1]' not in out, 'lint: a new sentence passes')

print(f'{len(failures)} failure(s)')
sys.exit(1 if failures else 0)
