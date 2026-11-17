# make data      download the open sources (data/raw), pinned in data/fetch.sh; a missing one fails (exit 1) unless
#                listed in TUSACH_ALLOW_MISSING=id,id (sandboxes; the page then cannot be published)
# make db        public build: data/build/vi.db (commercial-use sources + the test fixture)
# make db-nc     private build: data/build/vi-nc.db (also non-commercial sources); the public page refuses it
# make lint      lesson rules (tools/lint.py) + the word verifier (tools/verify_words.py)
# make app       app/dist/index.html, then the card check (tools/check_cards.py)
# make check     the card check alone, on the last build
# make test      unit tests of the Vietnamese helpers, the word pipeline, the build guards, the database and bridge;
#                then the cutter report (tests/cutter, not a gate)
# make smoke     click through the built app (Playwright)
# make lookup W=học_sinh
PY = python3 -I
RAW = data/raw
OUT = data/build

.PHONY: data db db-nc lookup clean lint test app check smoke coverage cutter
data:
	sh data/fetch.sh

db: data
	mkdir -p $(OUT)
	$(PY) tools/build_db.py $(RAW) $(OUT)/vi.db

db-nc: data
	mkdir -p $(OUT)
	$(PY) tools/build_db.py $(RAW) $(OUT)/vi-nc.db --nc

lookup:
	$(PY) tools/lookup.py "$(W)"

clean:
	rm -rf $(OUT)

lint:
	$(PY) tools/lint.py
	$(PY) tools/verify_words.py --lessons

test: db db-nc
	$(PY) tools/vi.py
	$(PY) tools/test_fetch.py
	$(PY) tools/test_pipeline.py
	$(PY) tools/test_db.py
	@echo '--- cutter report (not a gate; reference NOT checked by a native speaker)'
	-$(PY) tools/cutter_test.py
	-$(PY) tools/cutter_test.py --known viet74k --max 5

app:
	$(PY) tools/build_app.py

check:
	$(PY) tools/check_cards.py

smoke:
	$(PY) tools/smoke.py

coverage:
	$(PY) tools/coverage.py

cutter:
	$(PY) tools/cutter_test.py --max 30
