# Tủ sách

A Northern (Hà Nội) Vietnamese course in English, Assimil-style, for a learner who already knows Cantonese, Mandarin
and Taigi: Sino-Vietnamese (Hán-Việt) words are shown with their Chinese counterparts. Modelled on the Taigi app
Tsheh-tû. Status: the build, the checks and the app run on a test fixture; no data source and no lesson yet
(`docs/STATE.md`).

```sh
make db && make lint && make test && make app    # app/dist/index.html, one self-contained page
make smoke                                       # click through it in a phone-sized browser (Playwright)
```
Rules for working here: `CLAUDE.md`. Formats and tools: `docs/REFERENCE.md`.

Code: MIT (`LICENSE`). Course content: CC BY-SA 4.0 (`LICENSE-CONTENT.md`). Data sources: `ATTRIBUTION.md`.
