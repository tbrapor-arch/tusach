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

Biases, stated plainly:
- F: wordfreq 3.1.1 (Wikipedia, OpenSubtitles 2018, web text; frozen around 2021), else FrequencyWords (subtitles).
- The shares come from a small corpus (example sentences: Tatoeba, Wiktionary's examples) cut by underthesea, whose
  model follows the VLSP 2013 news conventions; the dictionary's headwords and underthesea's words do not always agree.
  Words the corpus never shows keep the prior split, which favours compounds of frequent syllables and long words of
  common syllables (an upper bound rather than an estimate).
- A monosyllable used mostly inside compounds (quốc, học) is pushed down only as far as the corpus shows it.
"""
import math
from collections import Counter, defaultdict

import vi

A = 10.0


def syllable_freqs(raw_dir, syllables):
    """({syllable: frequency per word token}, description). wordfreq when installed, else FrequencyWords."""
    try:
        import wordfreq
        return ({s: wordfreq.word_frequency(s, 'vi') for s in syllables},
                f'wordfreq {getattr(wordfreq, "__version__", "3.1.1")} syllable frequencies')
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


def segmenter(known):
    """(function text -> list of word keys, description). underthesea when installed, else the dictionary cutter."""
    try:
        from underthesea import word_tokenize
        import underthesea

        def cut(text):
            return [vi.key(t) for t in word_tokenize(vi.nfc(text)) if any(c.isalpha() for c in t)]
        return cut, f'underthesea {underthesea.__version__} word_tokenize'
    except ImportError:
        def cut(text):
            return [w[2] for w in vi.words(vi.cut(text, known)) if w[0] == 'w']
        return cut, 'tools/vi.py cut() (longest dictionary match; underthesea not installed)'


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
        syls = t.split()
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
