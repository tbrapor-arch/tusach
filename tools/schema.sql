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
  origin TEXT,            -- sino (vi-etym-sino, a Hán-Việt word) | nonhv (vi-etym-sino rendering "Non-Sino-Vietnamese
                          -- reading of Chinese X": an older/colloquial borrowing, e.g. giấy 紙; chars '', see etymon) |
                          -- vietic (inherited from Proto-Vietic / Austroasiatic) | '' (unknown)
  hv_check TEXT,          -- for a word with chars: ok (each syllable is a Hán-Việt reading of its character in Wiktionary
                          -- or Thiều Chửu) | differs (at least one is not) | length (chars and syllables differ) | ''
                          -- differs/length: not shown as "same word" (no chars, no label); `make lint` lists them
  label TEXT,             -- same | native | '' (computed from origin); false-friend comes from course/false_friends.tsv
  freq INT,               -- estimated occurrences per billion words (tools/freq.py; method in meta.freq_method)
  freq_rank INT,          -- 1 = most frequent key; entries of one key share its rank
  etymon TEXT,            -- origin nonhv: the Chinese etymon and its Hán-Việt reading ('紙 chỉ'); not a Hán-Việt analysis
  alt_of TEXT DEFAULT '', -- a Wiktionary entry whose every sense is "alternative spelling/form of X": the key of X
  alt_kind TEXT DEFAULT '', -- spelling (same word, other spelling: công ty / công ti) | form (another form of the word:
                          -- cảm ơn / cám ơn, Northern / Southern) | ''
  origin_note TEXT DEFAULT '', -- the evidence for origin, in words ('inherited from Proto-Vietic *ʔɛːm', 'cognate with
                          -- Muong chi', 'borrowed from French ga', 'as cám ơn (alternative form)')
  sino_kind TEXT DEFAULT '', -- origin sino: word (the characters are a Chinese word in CC-CEDICT, rime or the MOE, or one
                          -- character) | vn (a compound formed in Vietnamese or in Vietnamese order: 場學 trường học)
  doubt TEXT DEFAULT '',  -- '' | doubtful (Wiktionary's own uncertainty, or course/etymology-review.tsv) | opaque (the
                          -- analysis holds but a Chinese reader would not see the word: sense not in CC-CEDICT's English
                          -- of the characters, a grammaticalised function word, a rare character)
  doubt_why TEXT DEFAULT '', -- the evidence for `doubt`, in words
  en_score REAL           -- tools/english.py compose(): evidence for the entry's first English (the card puts the
                          -- entry with the best score first among the entries of one etymology)
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
-- label: '' | attested (read so by Wiktionary's Sino-Vietnamese words, tools/build_db.py hannom_attested) | romanization
-- (a Wiktionary entry "Sino-Vietnamese reading of X") | southern (a Southern form, e.g. sanh, chánh: shown after the Northern one) | derived (the Northern form
-- derived from a Southern one by tools/hanviet.py SOUTHERN; source 'derived') | fallback (a Unihan reading of the right
-- shape for a character no Hán-Việt source reads; shown as "unchecked (Unihan)").
-- use: how many Wiktionary Sino-Vietnamese words (hv_check ok) read the character so (tone-mark placement and i/y
-- ignored): the display order of a character's Northern readings (Wiktionary lists them alphabetically: 員 vân/viên).
CREATE TABLE hanviet(char TEXT, reading TEXT, kind TEXT, source TEXT, ord INT, checked INT, label TEXT DEFAULT '',
                     use INT DEFAULT 0);
CREATE INDEX hanviet_char ON hanviet(char);

-- the Chinese side of the bridge. lang = yue (Cantonese, Jyutping), nan (Taigi, Tâi-lô), cmn (Mandarin, pinyin).
-- level: word (the source has these characters as one word) | char (a single character's reading).
-- share: the source's own weight for this reading, when it gives one (rime-cantonese: % of the character's uses; a
-- character's main reading has none). note: nan = literary (文讀) | unmarked (the MOE gives no literary/colloquial
-- split for it) | colloquial (unmarked, but its coda does not match Hán-Việt: tools/build_db.py taigi_layers); cmn = name (CC-CEDICT capitalised reading: surname or place; not shown unless the word is a name).
-- Only CC-CEDICT's traditional forms are keyed (a simplified form's readings never reach a traditional character).
-- rank: display order within (chars, lang, level), set after loading (tools/build_db.py rank_chinese): yue rime's main
-- reading then its share; cmn Unihan kMandarin's reading first, then by the number of CC-CEDICT words using the
-- reading; nan the source order. Ties by reading, so the order never depends on the run.
CREATE TABLE chinese(chars TEXT, lang TEXT, reading TEXT, source TEXT, level TEXT, share INT, note TEXT, ord INT,
                     rank INT);
-- Unihan kMandarin: the customary Mandarin reading(s) of a character, in Unihan's order (order of the cmn readings)
CREATE TABLE mandarin_pref(char TEXT, reading TEXT, ord INT);
-- how many CC-CEDICT words (traditional) read the character so: the second key of the Mandarin order
CREATE TABLE cmn_use(char TEXT, reading TEXT, n INT);
CREATE INDEX chinese_chars ON chinese(chars);
-- Unihan kSemanticVariant / kZVariant: variant forms of a character (爲 為), both directions (tools/bridge.py spellings)
CREATE TABLE variant(char TEXT, var TEXT);
CREATE INDEX variant_char ON variant(char);

-- the bridge join on characters (tools/bridge.py join()), one row per distinct chars of the entries: the readings shown
-- on the card, and how each was obtained: word (the whole word in the source) | char (built character by character) |
-- '' (missing: the source lacks the word and at least one of its characters). n: languages present (0-3).
-- nan is the LITERARY (文讀) reading, composed from the characters' literary readings; nan_by = word when the MOE word
-- entry reads the word exactly so (attested); nan_coll = the MOE word reading when it differs (colloquial / everyday).
-- via: the variant spelling under which some Chinese reading was found ('' when the word's own characters gave all)
-- nan_flag: colloquial-only (a character has no literary Taigi reading, only a colloquial one: 冊 tsheh; the literary
-- column is then empty and nan_coll gives the colloquial reading)
CREATE TABLE bridge(chars TEXT PRIMARY KEY, hv TEXT, yue TEXT, yue_by TEXT, nan TEXT, nan_by TEXT, cmn TEXT,
                    cmn_by TEXT, n INT, nan_coll TEXT, via TEXT, nan_flag TEXT);

-- the senses of a Wiktionary entry as kaikki gives them (before any reordering): gloss (the last, most specific gloss
-- of the sense), tags (comma-separated), examples (number of examples), alt_of (the "alternative form of" target)
CREATE TABLE sense(entry_id INT, n INT, gloss TEXT, tags TEXT, examples INT, alt_of TEXT);
CREATE INDEX sense_entry ON sense(entry_id);
-- the English Wiktionary's Vietnamese translations of English entries (source wiktionary-tr): en (the English
-- headword), pos, sense (the translation table's gloss), key (the Vietnamese translation, tools/vi.py key()), tags,
-- n_vi (how many Vietnamese translations that table gives: 1 = specific). Card English (tools/build_db.py
-- compose_english): which English is a word's main one.
CREATE TABLE translation(en TEXT, pos TEXT, sense TEXT, key TEXT, tags TEXT, n_vi INT);
CREATE INDEX translation_key ON translation(key);
-- the Chinese words (Mandarin, Cantonese, Min Nan; traditional and simplified) of the same translation tables: a
-- Hán-Việt analysis whose characters appear in a Chinese translation of a table that has the Vietnamese word is
-- the same word in that sense (tools/build_db.py etymology_states)
CREATE TABLE translation_zh(en TEXT, pos TEXT, sense TEXT, word TEXT);
CREATE INDEX translation_zh_t ON translation_zh(en, pos, sense);
-- a spelling group (tools/build_db.py spelling_groups): every key of a group of spellings of ONE word (i/y: lí do /
-- lý do; Wiktionary "alternative spelling of") -> the house spelling (canon, docs/REFERENCE.md); how: iy | alt
CREATE TABLE spelling(key TEXT PRIMARY KEY, canon TEXT, how TEXT);
-- CC-CEDICT's English of a traditional form (all its entries, '; '): the sense check of a Hán-Việt analysis (doubt)
CREATE TABLE cedict_en(chars TEXT, english TEXT);
CREATE INDEX cedict_en_chars ON cedict_en(chars);
