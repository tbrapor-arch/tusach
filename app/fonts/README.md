`noto-sans-viet.woff2`: Noto Sans (Google), SIL Open Font License 1.1, subset to Latin with Vietnamese and the
combining marks, with its mark-positioning tables. Embedded in the app by `tools/build_app.py` (and used by
`tools/make_icons.py`), so stacked marks (ế, ự, ỗ) draw the same everywhere; the build fails if a letter the page shows
is missing from it. Carried over from Tsheh-tû (`tailo-noto-sans.woff2`).
