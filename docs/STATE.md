# State (one small entry per module; newest facts only)

## Repository (18 Nov 2026)
Forked from Tsheh-tû `dict-all` df02bfe; review fixes of 18 Nov 2026 in. Builds, lints, tests and click-tests on the
test fixture only, in a sandbox build (`TUSACH_ALLOW_MISSING=wiktionary,tatoeba`: not publishable). Next steps:
run `.github/workflows/snapshot.yml` (a commit to `data/snapshot-request.txt` or the Actions tab), then
`tools/pin_snapshot.py data-YYYY-MM-DD` and commit the pins → first full build with every source, `make coverage` →
a native speaker checks the cutter reference → syllabus and first word list, wait for the owner → lessons 1–7.
Until the snapshot pins exist, `make db` fails on purpose and so does CI (check.yml, pages.yml).

## Data sources (18 Nov 2026)
`data/fetch.sh` pins every source by content (ATTRIBUTION.md). Fetched in the sandbox: Thiều Chửu, Unihan
(kVietnamese, kMandarin), rime-cantonese, MOE, CC-CEDICT, the Tatoeba Challenge copy (private build only),
FrequencyWords. kaikki (Wiktionary) and Tatoeba: our own snapshot release, **PENDING** (kaikki.org and tatoeba.org are
refused from the sandbox; release assets on github.com download fine from it).

## Database
A missing source fails `make db` unless allowed. Without kaikki the public database has no Vietnamese words but the
fixture: 11,803 Thiều Chửu readings (9,897 characters), 3,557 Unihan readings used as labelled fallback, rime/MOE/
CEDICT readings, 3 bridge rows. The syllable table is validated at each build (HISTORY). The Wiktionary loader is
tested only on a kaikki-shaped test file: check its counts on the first real build.

## Bridge and labels
Join on characters in `tools/bridge.py`: Taigi literary reading with the colloquial word reading apart; Northern
Hán-Việt first (7 characters with Southern forms: 政 甥 笙 derived, 正 生 晟 武 reordered). False friends:
`course/false_friends.tsv`, empty. Sound-correspondence drills: TODO(bridge).

## Word frequency and coverage
`tools/freq.py` ranks words with vi.cut() over the pinned corpus and the wordfreq prior. Coverage of the 3,000 most
frequent words (`make coverage`): NOT MEASURED yet, it needs the Wiktionary word list.

## Cutter
`tests/cutter/reference.tsv`: 200 sentences written and cut by Claude (docs/SEGMENTATION.md), **not checked by a
native speaker**. F1 with underthesea's Viet74K list as vi.cut()'s dictionary (stand-in): 0.942; underthesea 0.930
(comparison only); with the sandbox database's keys (fixture only) 0.811. To re-measure with the Wiktionary keys.

## Lessons
None. `course/syllabus.yaml`: syllabus and word list not approved. The build uses `tools/fixtures/lessons/00.yaml`.

## Audio
No source of word recordings (TODO(audio)); cards say "No recording yet". The native-speaker recording page
(`record.html`) and `tools/import_recordings.py` are kept; no clip.

## Private companion
`tusach-private`: loader contract with neutral names (module/, window.PrivateModule, `#private`), merge rule (no
poorer card over a public one), cards built with the course words; no content. Repository `tbrapor-arch/tusach-private`.

## Publishing
Not on GitHub yet. `app/published-card-ids.txt` and `app/published-english.tsv` are empty (no page published).
