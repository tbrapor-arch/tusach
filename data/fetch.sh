#!/bin/sh
# Download the open data sources into data/raw, each pinned by content: a git commit checked out clean, or a SHA-256.
# Nothing in data/raw is committed to this repo (see .gitignore). Licences: ATTRIBUTION.md. Loaders: tools/build_db.py.
#
# A source that cannot be downloaded, or whose content differs from its pin, makes this script exit 1 (and so
# `make db`). Only an explicit TUSACH_ALLOW_MISSING=id,id (a sandbox that cannot reach a host) lets the build go on
# without it; the database then lists it in meta.missing and its page cannot be published. Functions: fetch-lib.sh.
cd "$(dirname "$0")" || exit 1
. ./fetch-lib.sh
mkdir -p "$RAW"

# --- Our own snapshots (.github/workflows/snapshot.yml) of the sources whose publisher keeps no dated copy: release
# assets of tbrapor-arch/tusach, tag data-YYYY-MM-DD, pinned by SHA-256 here (tools/pin_snapshot.py TAG writes the
# lines). Never fetched from the moving upstream URL. PENDING: no snapshot yet, so the source counts as missing.
# Wiktionary via kaikki.org (CC BY-SA 4.0 / GFDL): words, English, Sino-Vietnamese etymologies (vi-etym-sino), Hán-Việt
# and Nôm readings of characters. Upstream: https://kaikki.org/dictionary/Vietnamese/kaikki.org-dictionary-Vietnamese.jsonl
snap wiktionary kaikki/kaikki.org-dictionary-Vietnamese.jsonl kaikki.org-dictionary-Vietnamese.jsonl PENDING PENDING
# Tatoeba (CC BY 2.0 FR; some sentences CC0): example sentences with id and author.
# Upstream: https://downloads.tatoeba.org/exports/per_language/{vie,eng}/…
snap tatoeba tatoeba/vie_sentences_detailed.tsv.bz2 vie_sentences_detailed.tsv.bz2 PENDING PENDING
snap tatoeba tatoeba/eng_sentences_detailed.tsv.bz2 eng_sentences_detailed.tsv.bz2 PENDING PENDING
snap tatoeba tatoeba/vie-eng_links.tsv.bz2 vie-eng_links.tsv.bz2 PENDING PENDING

# --- Thiều Chửu, Hán Việt tự điển (public domain in Vietnam; repository CC0 1.0): Hán-Việt readings per character.
get thieuchuu thieuchuu/TudienThienChuu.tab \
  https://raw.githubusercontent.com/catusf/tudien/a7dd918ecc67de8c2d15034f885d919b9295eba4/dict/TudienThienChuu.tab \
  6266861966039b984126d0fb2852c918727b7e4930888c7ed2a31e66e0f68f28

# --- Unihan kVietnamese, Unicode 18.0.0 (Unicode License v3): last resort, mixes Hán-Việt and Nôm, marked unchecked.
get unihan unihan/kVietnamese.txt \
  https://raw.githubusercontent.com/unicode-org/unicodetools/ccc86e576dcadf94ef9f86969e7b5cb51e432ddc/unicodetools/data/ucd/18.0.0/Unihan/kVietnamese.txt \
  d1214bfda23e7e6d8a581157655ca3769cdfbb6fd6829ae22261f9796e915789

# --- Cantonese: rime-cantonese (CC BY 4.0 for the files used; jyut6ping3.maps is ODbL and not read). Same commit as
# the Cantonese app (pyue).
fetch rime rime-cantonese https://github.com/rime/rime-cantonese.git 259f0e48bba840c3a2e0d117539e96937f3d89bc

# --- Taigi: the MOE dictionary (CC BY-ND 3.0 TW) as g0v exports it, the same source and commit as Tsheh-tû's taigi.db.
fetch moe moedict-data-twblg https://github.com/g0v/moedict-data-twblg.git 4626bfcfccd6087496d14aac702b5e8a6a82e974

# --- Mandarin: CC-CEDICT (CC BY-SA 4.0) as JSON, npm cedict-json 1.3.20251213. The tarball's SHA-256 (its sha512 is
# the registry's dist.integrity, checked on 18 Nov 2026).
npmpkg cedict cedict cedict-json 1.3.20251213 9a1857e4eb6f1cfd558eee6b31fe55bf850765b1fa7c5bc640af5b703b5f8949

# --- Tatoeba sentences as published on GitHub by Helsinki-NLP (Tatoeba Translation Challenge), eng-vie test set. Its
# licence conflicts (README CC BY 2.0 FR, LICENSE CC BY-NC-SA 4.0): commercial_ok False, private build (vi-nc.db) only.
get tatoeba-challenge tatoeba-challenge/eng-vie-test.txt \
  https://raw.githubusercontent.com/Helsinki-NLP/Tatoeba-Challenge/bd05f087e91e359a88594bd6d6c99a079e0ac621/data/test/eng-vie/test.txt \
  38a59fc5daf44b4f84db0a0aa87da721c8ea58baa5e8800b63491651af30d958

# --- Syllable frequencies: hermitdave/FrequencyWords, OpenSubtitles 2018 (content CC BY-SA 4.0). Fallback when
# wordfreq is not installed, and the real syllable list that validates tools/vi.py's syllable table at build time.
get frequencywords frequencywords/vi_50k.txt \
  https://raw.githubusercontent.com/hermitdave/FrequencyWords/525f9b560de45753a5ea01069454e72e9aa541c6/content/2018/vi/vi_50k.txt \
  3f5b112e4324136c2ba82d3151038607e3dd1dfa0911c226929d7544cc11adf3

# --- Fallback voice (not used by the build yet, TODO(audio)): Piper vi_VN-vais1000-medium (model MIT, data CC BY 4.0).
# 60 MB, so only with TUSACH_FETCH_VOICE=1.
if [ "${TUSACH_FETCH_VOICE:-0}" = 1 ]; then
  PIPER=e9ab671f2a0e50a701b34361136ba3e6a3a9eb0c
  get piper piper/vi_VN-vais1000-medium.onnx \
    https://huggingface.co/rhasspy/piper-voices/resolve/$PIPER/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx \
    ec7c89e2c85f4d1edc24b6120c18aaf1bda614f06b511567eb9c7c0de15e2dab
  get piper piper/vi_VN-vais1000-medium.onnx.json \
    https://huggingface.co/rhasspy/piper-voices/resolve/$PIPER/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx.json \
    fafb9da1354ed4b77c31af228ed41fb41cd825c14cffa105454b25e6ae751ee0
fi

# Build-time Python packages (not in data/raw): requirements-build.txt (wordfreq, underthesea).
finish
