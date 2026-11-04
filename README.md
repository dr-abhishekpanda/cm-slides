# CM Lecture Decks

One-hour interactive lecture decks for Community Medicine (MBBS). The decks are organised by topic and mapped to the NMC CBME 2024 competencies. Content follows Park's Textbook of PSM first, then other standard textbooks, then current Government of India and WHO sources.

## Layout

```
src/<id>-<topic>.html    deck source: meta block, <section> slides, optional <style> and <script>
engine/deck.css, deck.js shared look and behaviour for every deck
img/<name>.jpg + .json   images with licence and credit (credit prints in the slide footer)
decks/<id>-<topic>.html  built single-file deck (images embedded; works offline apart from web fonts)
review/<id>-<topic>.md   review notes: points to verify, image suggestions, local data to add
TOPIC-MAP.md             the curriculum split into 133 one-hour units
index.html               deck catalogue
```

## Build

```bash
python3 tools/build.py            # all decks
```

```bash
python3 tools/build.py H05        # one deck (prefix match)
```

```bash
python3 tools/index.py            # refresh index.html
```

## Presenting

| Key | Action |
|---|---|
| → / Space | Next step or slide |
| ← | Back |
| N | Speaker notes (timings, answers, points to verify) |
| O | Contents |
| F | Full screen |
| B | Blank screen |
| Click the clock | Start or pause the 60-minute timer |

Optional live polls: set `window.POLL_URL` in the built deck (or in `tools/build.py`) to a Mentimeter, Slido or Google Form link. A QR code then appears on pages that have a poll box.

## Images

```bash
python3 tools/fetch_image.py find "Aedes aegypti"                  # list Commons files
```

```bash
python3 tools/fetch_image.py direct "File:Name.jpg" aedes          # save img/aedes.jpg + credit
```

Only public-domain, CC0, CC BY and CC BY-SA files are accepted. To use your own photo, put `img/<name>.jpg` and a `img/<name>.json` with `artist`, `license` and `via`.

## Content Rules

- Verbatim textbook text appears in quotation marks; the source is named in the page footer.
- No source names in slide bodies; speaker notes may name them.
- Local figures appear as `[INSERT: …]` placeholders, never invented numbers.

Prepared by: Dr. Abhishek Panda, MD Community Medicine · support@dr-abhishekpanda-cm.app · #CM-APP
