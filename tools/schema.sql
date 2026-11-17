-- vi.db / vi-nc.db: the Vietnamese learner database, built by tools/build_db.py from pinned open sources. Never edited
-- by hand. Text is NFC. A word's key is lower-case NFC with one space between syllables (tools/vi.py key()).

CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
-- meta rows: nc = 0 | 1 (1: non-commercial sources included, private builds only), built (date), sources (ids used),
-- missing (ids of sources not fetched), freq_method (how entry.freq was computed, in words)

CREATE TABLE source(
  id TEXT PRIMARY KEY,
  name TEXT,
  version TEXT,           -- pinned version / commit, as in data/fetch.sh
  licence TEXT,
  url TEXT,
  commercial_ok INT,      -- 0: non-commercial licence, only in `make db-nc` (vi-nc.db)
  fixture INT DEFAULT 0   -- 1: the invented test fixture (tools/fixtures/dict.yaml), never course content
);

-- one row per headword (and part of speech / etymology) per source
CREATE TABLE entry(
  id INTEGER PRIMARY KEY,
  source TEXT REFERENCES source(id),
  src_id TEXT,
  word TEXT,              -- as the source writes it (NFC)
  key TEXT,               -- tools/vi.py key(): 'học sinh'
  tkey TEXT,              -- tools/vi.py tkey(): 'hoc6 sinh1' (tone-mark placement ignored)
  toneless TEXT,          -- 'hoc sinh'
  tag TEXT,               -- homograph tag when the course needs one ('road', 'sugar'); '' otherwise
  pos TEXT,
  english TEXT,
  chars TEXT,             -- chữ Hán of a Sino-Vietnamese (Hán-Việt) word (Wiktionary vi-etym-sino), '' otherwise
  origin TEXT,            -- sino (vi-etym-sino) | vietic (inherited from Proto-Vietic / Austroasiatic) | '' (unknown)
  hv_check TEXT,          -- for a word with chars: ok (each syllable is a Hán-Việt reading of its character in Wiktionary
                          -- or Thiều Chửu) | differs (at least one is not) | length (chars and syllables differ) | ''
  label TEXT,             -- same | native | '' (computed from origin); false-friend comes from course/false_friends.tsv
  freq INT,               -- estimated occurrences per billion words (tools/freq.py; method in meta.freq_method)
  freq_rank INT           -- 1 = most frequent key; entries of one key share its rank
);
CREATE INDEX entry_key ON entry(key);
CREATE INDEX entry_tkey ON entry(tkey);
CREATE INDEX entry_toneless ON entry(toneless);
CREATE INDEX entry_chars ON entry(chars);

-- example sentences; ref: the source's sentence id and author where it has them (Tatoeba: '#123456 by user')
CREATE TABLE example(id INTEGER PRIMARY KEY, entry_id INT, source TEXT, vi TEXT, en TEXT, ref TEXT);
CREATE INDEX example_entry ON example(entry_id);

-- readings of one character in quốc ngữ. kind: hv (Hán-Việt) | nom (Nôm reading) | hannom (Wiktionary's older shape,
-- Hán-Việt and Nôm not told apart) | unchecked (Unihan kVietnamese: mixes both, last resort). ord: the source's order.
-- checked (hv rows): 1 the other Hán-Việt source (Wiktionary <-> Thiều Chửu) has the same reading, 0 it has the
-- character without this reading, NULL it lacks the character.
CREATE TABLE hanviet(char TEXT, reading TEXT, kind TEXT, source TEXT, ord INT, checked INT);
CREATE INDEX hanviet_char ON hanviet(char);

-- the Chinese side of the bridge. lang = yue (Cantonese, Jyutping), nan (Taigi, Tâi-lô), cmn (Mandarin, pinyin).
-- level: word (the source has these characters as one word) | char (a single character's reading).
-- share: the source's own weight for this reading, when it gives one (rime-cantonese: % of the character's uses; a
-- character's main reading has none). note: nan = literary (文讀) | unmarked (the MOE gives no literary/colloquial
-- split for it); cmn = name (CC-CEDICT capitalised reading: surname or place).
CREATE TABLE chinese(chars TEXT, lang TEXT, reading TEXT, source TEXT, level TEXT, share INT, note TEXT, ord INT);
CREATE INDEX chinese_chars ON chinese(chars);

-- the bridge join on characters (tools/bridge.py join()), one row per distinct chars of the entries: the readings shown
-- on the card, and how each was obtained: word (the whole word in the source) | char (built character by character) |
-- '' (missing: the source lacks the word and at least one of its characters). n: languages present (0-3).
CREATE TABLE bridge(chars TEXT PRIMARY KEY, hv TEXT, yue TEXT, yue_by TEXT, nan TEXT, nan_by TEXT, cmn TEXT,
                    cmn_by TEXT, n INT);
