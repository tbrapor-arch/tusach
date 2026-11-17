# shellcheck shell=sh
# The functions of data/fetch.sh (sourced; tools/test_fetch.py sources it on its own to test them).
#
# Every source has an id (the same id as in tools/build_db.py SOURCES). A source that cannot be fetched, or whose
# content does not match its pin, is MISSING, and finish() then exits 1: a build never goes on silently without a
# source. The only escape is an explicit list, TUSACH_ALLOW_MISSING=id,id (sandboxes that cannot reach a host);
# tools/build_db.py then records the missing ids in meta.missing, and a page built from such a database cannot be
# published (tools/build_app.py, tools/site.py, .github/workflows/pages.yml).
#
#   RAW                 download directory (default data/raw; TUSACH_RAW overrides it)
#   TUSACH_FETCH_ONLY   id,id: fetch only these (tests)

RAW=${TUSACH_RAW:-raw}
missing_ids=''
allowed_ids=''

_in_list() {  # ID LIST(comma-separated)
  case ",$2," in *",$1,"*) return 0 ;; esac
  return 1
}

want() {
  [ -z "${TUSACH_FETCH_ONLY:-}" ] && return 0
  _in_list "$1" "$TUSACH_FETCH_ONLY"
}

# miss ID MESSAGE: the source is missing (allowed only when listed in TUSACH_ALLOW_MISSING)
miss() {
  if _in_list "$1" "${TUSACH_ALLOW_MISSING:-}"; then
    echo "MISSING $1 (allowed by TUSACH_ALLOW_MISSING; a page built without it cannot be published): $2"
    _in_list "$1" "$(echo $allowed_ids | tr ' ' ,)" || allowed_ids="$allowed_ids $1"
  else
    echo "MISSING $1: $2"
    _in_list "$1" "$(echo $missing_ids | tr ' ' ,)" || missing_ids="$missing_ids $1"
  fi
}

# fetch ID DIR URL COMMIT: a git repository, checked out clean at the pinned commit (full 40-character hash). Local
# changes and extra files are removed, then the checkout is verified: HEAD is the pin and `git status --porcelain
# --ignored` is empty, so the build reads exactly the pinned content.
fetch() {
  want "$1" || return 0
  d="$RAW/$2"
  if [ ! -d "$d/.git" ]; then
    rm -rf "$d"
    git clone --quiet --no-checkout "$3" "$d" 2>/dev/null || { miss "$1" "could not clone $3"; return 0; }
  fi
  git -C "$d" cat-file -e "$4^{commit}" 2>/dev/null || git -C "$d" fetch --quiet origin "$4" 2>/dev/null || true
  if ! git -C "$d" -c advice.detachedHead=false checkout --quiet --force "$4" 2>/dev/null; then
    miss "$1" "commit $4 not available from $3"; return 0
  fi
  if [ -n "$(git -C "$d" status --porcelain --ignored)" ]; then
    echo "fetch: $2 had local changes or extra files: restored to $4"
    git -C "$d" reset --quiet --hard "$4"
    git -C "$d" clean --quiet -ffdx
  fi
  head=$(git -C "$d" rev-parse HEAD)
  if [ "$head" != "$4" ] || [ -n "$(git -C "$d" status --porcelain --ignored)" ]; then
    miss "$1" "REFUSED: $d is not a clean checkout of $4 (HEAD $head)"; return 0
  fi
  echo "ok  $1 @ $(echo "$4" | cut -c1-7) (clean checkout)"
}

# get ID OUT URL SHA256: one file, checked against its SHA-256. A file that differs is moved to OUT.refused.
get() {
  want "$1" || return 0
  out="$RAW/$2"
  if [ ! -f "$out" ]; then
    mkdir -p "$(dirname "$out")"
    if ! curl -sSfL --max-time 900 -o "$out.part" "$3" 2>/dev/null; then
      rm -f "$out.part"; miss "$1" "could not download $3"; return 0
    fi
    mv "$out.part" "$out"
  fi
  have=$(sha256sum "$out" | cut -d' ' -f1)
  if [ "$have" = "$4" ]; then
    echo "ok  $1: $2"
  else
    mv "$out" "$out.refused"
    miss "$1" "REFUSED $2: sha256 $have, pinned $4 (moved to $2.refused)"
  fi
}

# snap ID OUT FILE TAG SHA256: a file kept as an asset of our own snapshot release (.github/workflows/snapshot.yml),
# for sources whose publisher keeps no dated copy. TAG = PENDING: no snapshot yet, the source is missing.
SNAPSHOT_REPO=tbrapor-arch/tusach
snap() {
  want "$1" || return 0
  if [ "$4" = PENDING ]; then
    miss "$1" "$3: snapshot PENDING (run the snapshot workflow, then tools/pin_snapshot.py TAG)"; return 0
  fi
  get "$1" "$2" "https://github.com/$SNAPSHOT_REPO/releases/download/$4/$3" "$5"
}

# npmpkg ID DIR PACKAGE VERSION SHA256: an npm package tarball pinned by SHA-256, extracted afresh on every run (so
# the extracted files are always those of the verified tarball).
npmpkg() {
  want "$1" || return 0
  d="$RAW/$2"
  tgz="$d/$3-$4.tgz"
  mkdir -p "$d"
  if [ ! -f "$tgz" ]; then
    (cd "$d" && npm pack "$3@$4" --silent >/dev/null 2>&1) || { miss "$1" "npm pack $3@$4 failed"; return 0; }
  fi
  have=$(sha256sum "$tgz" | cut -d' ' -f1)
  if [ "$have" != "$5" ]; then
    mv "$tgz" "$tgz.refused"; miss "$1" "REFUSED $3-$4.tgz: sha256 $have, pinned $5"; return 0
  fi
  rm -rf "$d/package"
  (cd "$d" && tar xzf "$3-$4.tgz") || { miss "$1" "could not extract $3-$4.tgz"; return 0; }
  echo "ok  $1: $3@$4 (tarball verified, extracted)"
}

finish() {
  if [ -n "$missing_ids" ]; then
    list=$(echo $missing_ids $allowed_ids | tr ' ' ',')
    echo "fetch.sh: FAILED, missing:$missing_ids. In a sandbox that cannot reach a host, build without them on purpose" \
         "with TUSACH_ALLOW_MISSING=$list (the page cannot be published then)." >&2
    exit 1
  fi
  [ -z "$allowed_ids" ] || echo "fetch.sh: allowed missing:$allowed_ids (TUSACH_ALLOW_MISSING)"
  exit 0
}
