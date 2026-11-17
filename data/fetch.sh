#!/bin/sh
# Download the open data sources into data/raw, each pinned to a version (commit, package version or checksum).
# Nothing in data/raw is committed to this repo (see .gitignore and ATTRIBUTION.md).
#
# TODO(sources): EMPTY on purpose (17 Nov 2026). The candidates in the handover (section 6: Unihan kVietnamese,
# Wiktionary/kaikki, the Free Vietnamese Dictionary Project, Tatoeba, frequency lists, CC-CEDICT, the Cantonese app's
# rime-cantonese data, Tsheh-tû's taigi.db) are having their licences verified by another session. Add a source here
# only after its licence is checked and recorded in ATTRIBUTION.md, then give it a loader in tools/build_db.py
# (SOURCES). Non-commercial sources must have commercial_ok = False there: they then reach only `make db-nc`.
set -e
cd "$(dirname "$0")"
mkdir -p raw

# fetch NAME URL COMMIT: a git repository at a pinned commit (kept for the sources to come)
fetch() {
  if [ ! -d "raw/$1/.git" ]; then
    git clone --quiet --filter=blob:none "$2" "raw/$1"
  fi
  git -C "raw/$1" fetch --quiet --depth 1 origin "$3" 2>/dev/null || true
  git -C "raw/$1" -c advice.detachedHead=false checkout --quiet "$3"
  echo "ok  $1 @ $(git -C "raw/$1" rev-parse --short HEAD)"
}

echo "no data source yet (TODO(sources) in data/fetch.sh)"
