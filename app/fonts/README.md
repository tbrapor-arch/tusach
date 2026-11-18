`noto-sans-viet.woff2`: Noto Sans (Google), SIL Open Font License 1.1, subset to Latin with Vietnamese and the
combining marks, with its mark-positioning tables. Embedded in the app by `tools/build_app.py` (and used by
`tools/make_icons.py`), so stacked marks (ế, ự, ỗ) draw the same everywhere; the build fails if a letter the page shows
is missing from it. Carried over from Tsheh-tû (`tailo-noto-sans.woff2`).

Review 5 (19 Nov 2026): U+030D (the Tâi-lô vertical line, ha̍k) is a 164 x 80 stroke in Noto Sans and read as a dot on
a phone. `tools/appfont.py` (MARK_SHAPES) redraws it as a 226 x 60 stroke in the page's copy at build time (this file
stays the upstream subset; OFL 1.1, no Reserved Font Name); `make app` fails if a letter or mark of the page or of a
card's readings is missing, has no mark positioning on its letter, or if that stroke is not a vertical line.
