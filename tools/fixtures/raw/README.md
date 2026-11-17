# TEST FIXTURE: a data/raw directory for tools/test_db.py

`kaikki/kaikki.org-dictionary-Vietnamese.jsonl`: eleven lines written for the tests in the shape of kaikki.org's
Vietnamese JSONL (wiktextract: `related` items tagged `han-viet-reading` / `nom-reading`, `forms` tagged `Hán-Nôm`,
`etymology_templates` with `vi-etym-sino`, `inh`, `bor`). Not Wiktionary data, not course content. The other sources
are absent on purpose: the test checks that the build says "not fetched" and goes on.
