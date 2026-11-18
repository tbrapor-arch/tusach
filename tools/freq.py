"""Word frequency for Vietnamese WORDS, from syllable frequencies and a segmented corpus (used by tools/build_db.py).

The open frequency lists (wordfreq, FrequencyWords) count syllables: they split on spaces, so they see `học` and `sinh`,
never `học sinh`. A syllable's count F(s) is the sum of its uses in every word that contains it. This module divides
each syllable's count among the dictionary words containing it, in the proportions observed in a corpus cut into
words, and estimates a word's frequency from each of its syllables:

    share(w|s) = (c(w,s) + A * prior(w|s)) / (c(s) + A)        c: counts in the segmented corpus, A = 10
    prior(w|s) = E(w) / sum of E(w') over the dictionary words w' containing s
    E(w)       = wordfreq's own estimate for a phrase: 1 / sum(1 / F(s)) over its syllables
    f(w)       = geometric mean over the syllables s of w of F(s) * share(w|s)

c(s) counts every use of s in the corpus, also inside tokens that are not dictionary words, so the share left to the
dictionary words is not inflated. With no corpus, share = prior (the estimate rests on F alone).

The corpus is cut by the project's own cutter (tools/vi.py cut(), with the dictionary's keys and the rules of
docs/SEGMENTATION.md): one cutter (CLAUDE.md rule 1), so the counts use the same word boundaries as the cards.
underthesea decides nothing here; it appears only as a comparison in the cutter report (tools/cutter_test.py).

Biases, stated plainly:
- F: wordfreq 3.1.1 (Wikipedia, OpenSubtitles 2018, web text; frozen around 2021), else FrequencyWords (subtitles).
- The shares come from a small corpus of example sentences (our Tatoeba snapshot and Wiktionary's examples; the
  private build also has the Tatoeba Challenge copy), short and conversational, translated from English by volunteers.
- vi.cut() is a longest match: where the dictionary lists a free phrase that its rules do not catch, the phrase takes
  the count from its syllables (đi học); where the dictionary lacks a word, its syllables keep it. Its rules split
  function-word sequences and classifier + noun, so those pairs lose counts they would get from a longest match.
- Words the corpus never shows keep the prior split, which favours compounds of frequent syllables and long words of
  common syllables (an upper bound rather than an estimate). With no corpus (sandbox build without Tatoeba and
  Wiktionary) every share is the prior.
- A monosyllable used mostly inside compounds (quốc, học) is pushed down only as far as the corpus shows it.
- English in the Vietnamese web and subtitle text: `the` (Vietnamese "gauze") and `in` ("to print") ranked near 250 on
  the syllable counts of English text. Corrected since 18 Nov 2026 (english_leak()): each syllable loses the share
  that the English word of the same letters explains. wordfreq's Wikipedia share lifts administrative words (huyện,
  quận, tỉnh, Nguyễn): not corrected (no automatic rule separates them from real formal vocabulary; HISTORY).
- Names: a key that is only a name (Việt Nam, Hà Nội) is ranked like a word. A key shared by a name and a common
  word (Lan / lan "orchid", Hoa / hoa "flower"): a capitalised use inside a sentence counts for the name, not for the
  common word, and the name's entries get no rank (tools/build_db.py frequencies). The Tatoeba corpus favours its
  own topics (tiếng Pháp).
"""
import math
from collections import Counter, defaultdict

import vi

A = 10.0


LEAK_FLOOR = 0.02      # a syllable keeps at least this share of its count after the English leakage is removed


def english_leak():
    """k, the share of English text in wordfreq's Vietnamese counts: the median, over the 300 most frequent English
    words that cannot be Vietnamese syllables (of, and, with, which…), of their Vietnamese count divided by their
    English one (0.0073 on wordfreq 3.1.1). A Vietnamese syllable that is also an English word then loses
    k x its English frequency: the English `the` (5.4 % of English words) accounts for all of `the` "gauze" in the
    Vietnamese list, the English `in` for 29 % of `in` "to print". None without wordfreq."""
    try:
        import wordfreq
    except ImportError:
        return None
    r = sorted(wordfreq.word_frequency(w, 'vi') / wordfreq.word_frequency(w, 'en')
               for w in wordfreq.top_n_list('en', 300)
               if w.isalpha() and vi.syllable_problems(w) and wordfreq.word_frequency(w, 'vi') > 0)
    return r[len(r) // 2] if r else None


def syllable_freqs(raw_dir, syllables):
    """({syllable: frequency per word token}, description). wordfreq when installed (English leakage removed:
    english_leak()), else FrequencyWords."""
    try:
        import wordfreq
        k = english_leak() or 0.0
        out = {}
        for s in syllables:
            f = wordfreq.word_frequency(s, 'vi')
            out[s] = max(f - k * wordfreq.word_frequency(s, 'en'), LEAK_FLOOR * f) if f else 0.0
        return (out, f'wordfreq {getattr(wordfreq, "__version__", "3.1.1")} syllable frequencies, less the English '
                     f'leakage (k = {k:.4f} x the English frequency of the same letters)')
    except ImportError:
        pass
    import os
    path = os.path.join(raw_dir, 'frequencywords', 'vi_50k.txt')
    if not os.path.exists(path):
        return {}, ''
    counts = {}
    for line in open(path, encoding='utf-8'):
        p = line.split()
        if len(p) == 2 and p[1].isdigit():
            counts[vi.nfc(p[0]).lower()] = counts.get(vi.nfc(p[0]).lower(), 0) + int(p[1])
    total = sum(counts.values()) or 1
    return {s: counts.get(s, 0) / total for s in syllables}, 'FrequencyWords 2018 vi_50k syllable counts (wordfreq not installed)'


def segmenter(known, canon=None, name_keys=()):
    """(function text -> list of word keys, description): the project's own cutter, tools/vi.py cut(). canon: {key:
    house key} of the spelling groups (lí do counts for lý do). name_keys: keys that are also names: a capitalised
    use not at the start of a sentence is the name ('name:' + key, a key no word has), not the common word."""
    canon = canon or {}

    def cut(text):
        out = []
        for w in vi.words(vi.cut(text, known)):
            if w[0] != 'w':
                continue
            k = canon.get(w[2], w[2])
            if k in name_keys and not w[4] and w[1][:1].isupper():
                k = 'name:' + k
            out.append(k)
        return out
    return cut, 'tools/vi.py cut() (longest dictionary match with the rules of docs/SEGMENTATION.md)'


def estimate(keys, F, corpus_tokens):
    """{key: frequency per word token}. keys: dictionary word keys; F: syllable frequencies; corpus_tokens: word keys
    of the segmented corpus (may be empty)."""
    keys = [k for k in keys if k and all(F.get(s) for s in k.split())]
    E = {k: 1.0 / sum(1.0 / F[s] for s in k.split()) for k in keys}
    by_syl = defaultdict(list)
    for k in keys:
        for s in set(k.split()):
            by_syl[s].append(k)
    prior_den = {s: sum(E[k] for k in ws) for s, ws in by_syl.items()}
    kset = set(keys)
    c_ws, c_s = Counter(), Counter()
    for t in corpus_tokens:
        syls = (t[5:] if t.startswith('name:') else t).split()
        for s in syls:
            c_s[s] += 1
        if t in kset:
            for s in syls:
                c_ws[(t, s)] += 1
    out = {}
    for k in keys:
        logs = []
        for s in k.split():
            prior = E[k] / prior_den[s]
            share = (c_ws[(k, s)] + A * prior) / (c_s[s] + A)
            logs.append(math.log(F[s] * share))
        out[k] = math.exp(sum(logs) / len(logs))
    return out


def phrase_freq(raw_dir, syllables):
    """A function key -> wordfreq-style estimate of the spelling as a phrase, 1 / sum(1 / F(s)) over its syllables
    (F: syllable_freqs, English leakage removed); 0 when a syllable has no count. Used to choose the house spelling
    of a spelling group (tools/build_db.py spelling_groups)."""
    F, _ = syllable_freqs(raw_dir, syllables)

    def f(k):
        xs = k.replace('-', ' ').split()
        if not xs or not all(F.get(x) for x in xs):
            return 0.0
        return 1.0 / sum(1.0 / F[x] for x in xs)
    return f
