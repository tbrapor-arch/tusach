# Data sources and attribution

None of these datasets are stored in this repository. `make data` (`data/fetch.sh`) downloads them at pinned versions
into `data/raw/` (git-ignored) and fails if one is missing or differs from its pin, and `make db` builds `data/build/vi.db` locally (`tools/build_db.py`, `SOURCES`). A
source is added here only after its licence is checked on its own page; non-commercial sources reach only `make db-nc`
(private builds): at present only the Tatoeba Challenge copy, whose licence is in conflict. Licences were read on the pages named in the sources report of
17 Nov 2026; items marked **UNVERIFIED** could not be confirmed on a primary page.

| Dataset | Rights holder / maintainer | Licence | Version pinned | Commercial use | How it is used |
|---|---|---|---|---|---|
| English Wiktionary, Vietnamese entries, via [kaikki.org](https://kaikki.org/dictionary/Vietnamese/) (wiktextract) | Wiktionary contributors; extraction by Tatu Ylonen | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) and [GFDL 1.1+](https://www.gnu.org/licenses/fdl-1.3.html) (dual); used under CC BY-SA 4.0 | our own snapshot, release `data-2026-11-17` of this repository (`.github/workflows/snapshot.yml`, run 44179962577), `kaikki.org-dictionary-Vietnamese.jsonl`, SHA-256 `186cd0a6…` in `data/fetch.sh` | yes | Words, English glosses, Sino-Vietnamese words and their characters (`vi-etym-sino`), Hán-Việt and Nôm readings of characters (tags `han-viet-reading`, `nom-reading`), example sentences. |
| English Wiktionary, the Vietnamese (and, of the same tables, Chinese) translations of English entries, filtered from kaikki.org's raw extraction ([raw data](https://kaikki.org/dictionary/rawdata.html)) by `.github/snapshot-translations.py` | Wiktionary contributors; extraction by Tatu Ylonen | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) and GFDL (same as the row above: the same wiki) | snapshot release `data-2026-11-18.2`, `en-translations.tsv.gz`, SHA-256 in `data/fetch.sh` (NOTES.md names the raw file and its SHA-256) | yes | Card English: which sense of a word is the main one, and its English when its own senses lack it (bận "busy"); the Chinese rows: the sense check of Hán-Việt analyses |
| Thiều Chửu, *Hán Việt tự điển*, digitised text via [catusf/tudien](https://github.com/catusf/tudien) (`dict/TudienThienChuu.tab`) | Thiều Chửu (Nguyễn Hữu Kha, 1902–1954); digitisation: catusf | Public domain in Vietnam (author died 1954; life + 50 years). Repository marked CC0 1.0 | commit `a7dd918`, SHA-256 `62668619…` | yes | Hán-Việt readings of characters: cross-check of Wiktionary's, and fallback for characters it lacks. Readings only, no definitions. |
| Unihan `kVietnamese`, `kMandarin`, `kSemanticVariant`, `kZVariant` (Unicode 18.0.0), via [unicode-org/unicodetools](https://github.com/unicode-org/unicodetools) | Unicode, Inc. | [Unicode License v3](https://www.unicode.org/license.txt) | commit `ccc86e5`, each file by SHA-256 (`data/fetch.sh`) | yes | kVietnamese: last resort for a character no Hán-Việt source reads, labelled "unchecked, Unihan" (it mixes Hán-Việt and Nôm readings). kMandarin: first key of the pinyin order. kSemanticVariant/kZVariant: a word written with a variant character (爲, 祕, 墻) finds its Chinese readings under the other form; the card says so. |
| rime-cantonese ([rime/rime-cantonese](https://github.com/rime/rime-cantonese)) | CanCLID (粵語計算語言學基礎建設組) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (files used); `jyut6ping3.maps` is ODbL 1.0 and is not read | commit `259f0e48` (same as the Cantonese app) | yes | Jyutping of characters (with rime's share of each reading) and of words. |
| 教育部臺灣台語常用詞辭典, via [g0v/moedict-data-twblg](https://github.com/g0v/moedict-data-twblg) | Ministry of Education, Taiwan | [CC BY-ND 3.0 TW](https://creativecommons.org/licenses/by-nd/3.0/tw/) | commit `4626bfc` (same as Tsheh-tû) | yes | Tâi-lô literary (文讀) or unmarked readings of characters and readings of words, reproduced unaltered. |
| CC-CEDICT, via [cedict-json](https://www.npmjs.com/package/cedict-json) | MDBG and CC-CEDICT contributors | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | 1.3.20251213, tarball SHA-256 `9a1857e4…` (its sha512 equals the npm registry's `dist.integrity`) | yes | Pinyin (converted to tone marks) of characters and words. |
| Tatoeba, Vietnamese–English sentences ([downloads](https://tatoeba.org/en/downloads)) | Tatoeba contributors (each sentence's author is named on the card) | [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/) (some sentences CC0 1.0) | our own snapshot of the exports (`vie_sentences_detailed`, `eng_sentences_detailed`, `vie-eng_links`), release `data-2026-11-17`, SHA-256 pinned; export URLs `https://downloads.tatoeba.org/exports/per_language/{vie,eng}/…` verified by the snapshot run's successful download (17 Nov 2026) | yes | Example sentences on cards, with sentence id and author; corpus for word counts (build time). |
| Tatoeba sentences as published by Helsinki-NLP, [Tatoeba Translation Challenge](https://github.com/Helsinki-NLP/Tatoeba-Challenge) (`data/test/eng-vie/test.txt`, 2,500 pairs) | Tatoeba contributors; compilation Helsinki-NLP | README: test and dev data **CC BY 2.0 FR** (its link points to the BY-SA 2.0 FR deed); the repository's LICENSE file is **CC BY-NC-SA 4.0**, stated for the training data. **Conflict UNRESOLVED** | commit `bd05f08`, SHA-256 `38a59fc5…` | **no** (`commercial_ok: False`, licence conflict) | Private build (`vi-nc.db`) only: build-time corpus for word counts. Not in the public database, never on a card, no longer in the cutter reference (removed 18 Nov 2026, see HISTORY). |
| wordfreq 3.1.1, via [PyPI](https://pypi.org/project/wordfreq/) | Robyn Speer; sources include Wikipedia, OpenSubtitles 2018, web text | Code Apache-2.0; data [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | 3.1.1 (`requirements-build.txt`) | yes | Build time only: syllable frequencies, turned into a frequency per word (`tools/freq.py`). Only a rank per word is published. |
| FrequencyWords ([hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords)), `content/2018/vi/vi_50k.txt` | Hermit Dave; data from OpenSubtitles 2018 | Content CC BY-SA 4.0, code MIT | commit `525f9b5`, SHA-256 `3f5b112e…` | yes | Fallback syllable frequencies when wordfreq is not installed. |
| underthesea 9.5.0, via [PyPI](https://pypi.org/project/underthesea/) | Vu Anh and underthesea contributors | Apache-2.0 (licence of the bundled models: **UNVERIFIED**, none found separately) | 9.5.0 (`requirements-build.txt`) | yes | Test time only: compared with `vi.cut()` in the cutter report. It decides nothing on a card or in the ranks (one cutter: the project's own `vi.cut()`). |
| Piper voice `vi_VN-vais1000-medium`, via [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices) | Model: Piper project; data: VAIS-1000 by Truong Do | Model MIT; data CC BY 4.0 | commit `e9ab671`, SHA-256 pinned; fetched only with `TUSACH_FETCH_VOICE=1` | yes | Not used yet (TODO(audio)): fallback synthetic Northern voice. |

**Snapshots we redistribute.** kaikki.org and Tatoeba keep no dated copy of their exports, so the build fetches its
own snapshot of them, kept unchanged as release assets of this repository with `SHA256SUMS` and `NOTES.md` (upstream URL,
download date, licence). Both licences permit redistribution with attribution: Wiktionary content (kaikki extraction)
under CC BY-SA 4.0 (attribution to the Wiktionary contributors and kaikki.org/wiktextract, same licence for the
files), Tatoeba sentences under CC BY 2.0 FR (attribution to the Tatoeba contributors; each sentence's author is in
the file). The release notes state this for each file.

**Excerpts kept in this repository** (tests, not content): `tools/fixtures/raw-real/` holds 27 unchanged lines of the
Wiktionary snapshot (CC BY-SA 4.0, attributed in its README); `tests/cutter/heldout.tsv` holds 100 Tatoeba sentences
(CC BY 2.0 FR), each with its sentence id and author; `tools/test_db.py` quotes five MOE rows and four Tatoeba sentences
with their ids.

Romanisations: Vietnamese quốc ngữ; Cantonese Jyutping (LSHK); Taigi Tâi-lô (Ministry of Education); Mandarin Hanyu
Pinyin.

Evaluated, not used: the **Vietnamese Wiktionary** (vi.wiktionary.org) as kaikki extracts it (`vi-extract.jsonl.gz`,
snapshot `data-2026-11-18.2`, fetched only with `TUSACH_FETCH_EVAL=1`, read only by `tools/eval_viwikt.py`). Its licence
could not be read on a primary page on 18 Nov 2026 (vi.wiktionary.org and meta.wikimedia.org were not reachable; kaikki's
pages state no licence; the Wikimedia dumps' legal page, GFDL + CC BY-SA 4.0 for all wikis, was read only on a mirror,
wikimedia.mirror.clarkson.edu/legal.html): **UNVERIFIED**, so nothing of it is in a database. It would add little anyway:
of the 159 top-1000 words with no known origin it would class 4 (eval_viwikt.py).

Not used, on purpose: the Free Vietnamese Dictionary Project and the Open Vietnamese Dictionary Project (GPL-2.0, not
compatible with CC BY-SA content); the Piper `vivos` voice (CC BY-NC-SA data) and `25hours_single` (data licence
unknown); Tatoeba audio (licence per contributor).

## Unverified or open (from the sources report, 17 Nov 2026)
1. **Thiều Chửu**: first edition 1942 (stated only in a README); the Vietnamese law text was read on a secondary site;
   **US status** (possible URAA restoration to 2037) not checked; who digitised `catusf/tudien` and from which
   edition is unknown, and the upstream `catusphan/dictionary` says MIT where `catusf/tudien` says CC0.
2. **Wiktionary**: CC BY-SA 4.0 + GFDL read on Wiktionary:Copyrights through a mirror host; kaikki.org states "the
   same licenses as Wiktionary", without a version.
3. **kaikki pin**: the per-language file is marked deprecated, with no dated archive: pinned through our own snapshot
   release `data-2026-11-18.2` (same Vietnamese file as `data-2026-11-17`; downloaded from kaikki.org by the snapshot workflow; the release's NOTES.md names the URL).
4. **Unihan kVietnamese**: provisional field, no Hán-Việt/Nôm distinction (UAX #38 rev. 41, read on a staging host).
5. **Tatoeba**: the per-language export URLs worked (snapshot of 17 Nov 2026); the per-sentence CC0 list is not read (all sentences are treated
   as CC BY 2.0 FR, which is safe). The Helsinki-NLP copy has the licence conflict stated in the table.
6. **MOE**: the ministry's own download page states no licence for the dictionary data; CC BY-ND 3.0 TW is stated by
   g0v and ChhoeTaigi. Whether one literary reading taken out of an entry is still "unaltered" is Tsheh-tû's position,
   not confirmed.
7. **underthesea models**: no separate licence found.
8. **OPUS OpenSubtitles terms** (inside wordfreq and FrequencyWords): page not readable; wordfreq says the data "may
   be used with attribution to OpenSubtitles".
9. **Hosted TTS** terms and **Common Voice** current licence: not needed yet (audio not built).
