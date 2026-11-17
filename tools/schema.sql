-- vi.db / vi-nc.db: the Vietnamese learner database, built by tools/build_db.py from pinned open sources. Never edited
-- by hand. Text is NFC. A word's key is lower-case NFC with one space between syllables (tools/vi.py key()).

CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
-- meta rows: nc = 0 | 1 (1: non-commercial sources included, private builds only), built (date), sources (ids)

CREATE TABLE source(
  id TEXT PRIMARY KEY,
  name TEXT,
  version TEXT,           -- pinned version / commit, as in data/fetch.sh
  licence TEXT,
  url TEXT,
  commercial_ok INT,      -- 0: non-commercial licence, only in `make db-nc` (vi-nc.db)
  fixture INT DEFAULT 0   -- 1: the invented test fixture (tools/fixtures/dict.yaml), never course content
);

-- one row per headword (and sense group) per source
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
  chars TEXT,             -- chữ Hán of a Sino-Vietnamese (Hán-Việt) word, '' for native words
  label TEXT,             -- same | false-friend | native | '' (unknown)
  freq INT,
  freq_rank INT
);
CREATE INDEX entry_key ON entry(key);
CREATE INDEX entry_tkey ON entry(tkey);
CREATE INDEX entry_toneless ON entry(toneless);

CREATE TABLE example(id INTEGER PRIMARY KEY, entry_id INT, source TEXT, vi TEXT, en TEXT);
CREATE INDEX example_entry ON example(entry_id);

-- Hán-Việt reading of one character (e.g. Unihan kVietnamese, once its licence is checked)
CREATE TABLE hanviet(char TEXT, reading TEXT, source TEXT);
CREATE INDEX hanviet_char ON hanviet(char);

-- the Chinese side of the bridge, joined on the characters: lang = yue (Cantonese, Jyutping), nan (Taigi, Tâi-lô
-- literary reading), cmn (Mandarin, pinyin)
CREATE TABLE chinese(chars TEXT, lang TEXT, reading TEXT, source TEXT);
CREATE INDEX chinese_chars ON chinese(chars);
