#!/bin/sh
# Download the open data sources into data/raw, each pinned to a version (commit, package version or SHA-256).
# Nothing in data/raw is committed to this repo (see .gitignore). Licences: ATTRIBUTION.md. Loaders: tools/build_db.py.
#
# A source that cannot be downloaded does not stop this script: it prints "MISSING" with the file the owner must put
# in place, and tools/build_db.py then builds without it and says so ("source X not fetched").
# A file whose SHA-256 differs from its pin is refused (deleted) and reported: the pin is updated on purpose only.
cd "$(dirname "$0")"
mkdir -p raw
missing=0

# fetch NAME URL COMMIT: a git repository at a pinned commit
fetch() {
  if [ ! -d "raw/$1/.git" ]; then
    git clone --quiet --filter=blob:none "$2" "raw/$1" 2>/dev/null || { echo "MISSING $1: could not clone $2"; missing=1; return 0; }
  fi
  git -C "raw/$1" fetch --quiet --depth 1 origin "$3" 2>/dev/null || true
  if git -C "raw/$1" -c advice.detachedHead=false checkout --quiet "$3" 2>/dev/null; then
    echo "ok  $1 @ $(git -C "raw/$1" rev-parse --short HEAD)"
  else
    echo "MISSING $1: commit $3 not available"; missing=1
  fi
}

# get OUT URL SHA256: one file, checked against its SHA-256. SHA256 = "unpinned" downloads it and prints the hash to
# pin (used only where the publisher keeps no dated copy; see ATTRIBUTION.md).
get() {
  if [ -f "$1" ] && [ "$3" != unpinned ] && echo "$3  $1" | sha256sum -c --quiet - >/dev/null 2>&1; then
    echo "ok  $1"; return 0
  fi
  if [ ! -f "$1" ]; then
    mkdir -p "$(dirname "$1")"
    if ! curl -sSfL --max-time 900 -o "$1.part" "$2" 2>/dev/null; then
      rm -f "$1.part"; echo "MISSING $1: could not download $2 (put the file there by hand; see ATTRIBUTION.md)"
      missing=1; return 0
    fi
    mv "$1.part" "$1"
  fi
  have=$(sha256sum "$1" | cut -d' ' -f1)
  if [ "$3" = unpinned ]; then
    echo "ok  $1 (UNPINNED: sha256 $have; write it into data/fetch.sh)"
  elif [ "$have" = "$3" ]; then
    echo "ok  $1"
  else
    echo "REFUSED $1: sha256 $have, pinned $3 (the publisher changed the file: check it, then update the pin)"
    mv "$1" "$1.refused"; missing=1
  fi
}

# --- Vietnamese: Wiktionary via kaikki.org (CC BY-SA 4.0 / GFDL). Words, English, Sino-Vietnamese etymologies with
# their characters (vi-etym-sino), Hán-Việt and Nôm readings of characters. kaikki replaces the file in place and keeps
# no dated copy: the pin is the file of 2026-10-30 (83,424,329 bytes, extraction from the enwiktionary dump of
# 2026-10-01). Its SHA-256 below was published by another project (arvicco/nabu, test/fixtures/wiktionary-vi/README.md),
# not computed here: this sandbox could not reach kaikki.org. Keep the downloaded file (e.g. as a release asset of
# tusach-private) so the build can be repeated once kaikki changes it.
get raw/kaikki/kaikki.org-dictionary-Vietnamese.jsonl \
  https://kaikki.org/dictionary/Vietnamese/kaikki.org-dictionary-Vietnamese.jsonl \
  186cd0a62d876dada70c9761bc05e598c8cf7b9a48e0aa518bab6c649e28d945

# --- Thiều Chửu, Hán Việt tự điển (public domain in Vietnam; repository CC0 1.0): Hán-Việt readings per character,
# the cross-check of Wiktionary's and the fallback for characters it lacks. Readings only.
get raw/thieuchuu/TudienThienChuu.tab \
  https://raw.githubusercontent.com/catusf/tudien/a7dd918ecc67de8c2d15034f885d919b9295eba4/dict/TudienThienChuu.tab \
  6266861966039b984126d0fb2852c918727b7e4930888c7ed2a31e66e0f68f28

# --- Unihan kVietnamese, Unicode 18.0.0 (Unicode License v3): last resort, mixes Hán-Việt and Nôm, marked unchecked.
get raw/unihan/kVietnamese.txt \
  https://raw.githubusercontent.com/unicode-org/unicodetools/ccc86e576dcadf94ef9f86969e7b5cb51e432ddc/unicodetools/data/ucd/18.0.0/Unihan/kVietnamese.txt \
  d1214bfda23e7e6d8a581157655ca3769cdfbb6fd6829ae22261f9796e915789

# --- Cantonese: rime-cantonese (CC BY 4.0 for the files used; jyut6ping3.maps is ODbL and not read). Same commit as
# the Cantonese app (pyue).
fetch rime-cantonese https://github.com/rime/rime-cantonese.git 259f0e48bba840c3a2e0d117539e96937f3d89bc

# --- Taigi: the MOE dictionary (CC BY-ND 3.0 TW) as g0v exports it, the same source and commit as Tsheh-tû's taigi.db.
# Literary (文讀) readings of characters and readings of whole words, reproduced unaltered.
fetch moedict-data-twblg https://github.com/g0v/moedict-data-twblg.git 4626bfcfccd6087496d14aac702b5e8a6a82e974

# --- Mandarin: CC-CEDICT (CC BY-SA 4.0) as JSON. Same pin as Tsheh-tû and the Cantonese app.
if [ ! -f raw/cedict/package/cedict.json ]; then
  mkdir -p raw/cedict
  (cd raw/cedict && npm pack cedict-json@1.3.20251213 --silent >/dev/null 2>&1 && tar xzf cedict-json-1.3.20251213.tgz) \
    || { echo "MISSING cedict-json: npm pack failed"; missing=1; }
fi
[ -f raw/cedict/package/cedict.json ] && echo "ok  cedict-json @ 1.3.20251213"

# --- Example sentences: Tatoeba (CC BY 2.0 FR; some sentences CC0). Weekly exports, no dated archive: the first
# download prints the SHA-256 to pin here, and the files are kept in tusach-private. The per-language paths are the
# usual ones but were not confirmed on the downloads page (rendered by script). UNPINNED until the owner's first run.
for f in vie_sentences_detailed.tsv.bz2 eng_sentences_detailed.tsv.bz2 vie-eng_links.tsv.bz2; do
  case $f in eng_*) d=eng ;; *) d=vie ;; esac
  get raw/tatoeba/$f https://downloads.tatoeba.org/exports/per_language/$d/$f unpinned
done

# --- Tatoeba sentences as published on GitHub by Helsinki-NLP (Tatoeba Translation Challenge): the eng-vie test set,
# 2,500 pairs, no sentence ids or authors. README: test/dev data CC BY 2.0 FR; the repository's LICENSE file is
# CC BY-NC-SA 4.0 (stated for the training data). Used only for the cutter reference (tests/cutter) and as a
# build-time corpus for word counts; never shown on a card.
get raw/tatoeba-challenge/eng-vie-test.txt \
  https://raw.githubusercontent.com/Helsinki-NLP/Tatoeba-Challenge/bd05f087e91e359a88594bd6d6c99a079e0ac621/data/test/eng-vie/test.txt \
  38a59fc5daf44b4f84db0a0aa87da721c8ea58baa5e8800b63491651af30d958

# --- Fallback syllable frequencies when the wordfreq package is not installed: hermitdave/FrequencyWords, OpenSubtitles
# 2018 (content CC BY-SA 4.0). Counts syllables, not words.
get raw/frequencywords/vi_50k.txt \
  https://raw.githubusercontent.com/hermitdave/FrequencyWords/525f9b560de45753a5ea01069454e72e9aa541c6/content/2018/vi/vi_50k.txt \
  3f5b112e4324136c2ba82d3151038607e3dd1dfa0911c226929d7544cc11adf3

# --- Fallback voice (not used by the build yet, TODO(audio)): Piper vi_VN-vais1000-medium (model MIT, data CC BY 4.0).
# 60 MB, so only with TUSACH_FETCH_VOICE=1.
if [ "${TUSACH_FETCH_VOICE:-0}" = 1 ]; then
  PIPER=e9ab671f2a0e50a701b34361136ba3e6a3a9eb0c
  get raw/piper/vi_VN-vais1000-medium.onnx \
    https://huggingface.co/rhasspy/piper-voices/resolve/$PIPER/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx \
    ec7c89e2c85f4d1edc24b6120c18aaf1bda614f06b511567eb9c7c0de15e2dab
  get raw/piper/vi_VN-vais1000-medium.onnx.json \
    https://huggingface.co/rhasspy/piper-voices/resolve/$PIPER/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx.json \
    fafb9da1354ed4b77c31af228ed41fb41cd825c14cffa105454b25e6ae751ee0
fi

# Build-time Python packages (not in data/raw): requirements-build.txt (wordfreq, underthesea).
[ $missing = 0 ] || echo "fetch.sh: some sources are missing (above); make db builds without them and says so"
exit 0
