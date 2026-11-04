"""Compile deck sources into single-file HTML decks.

src/<file>.html  ->  decks/<file>.html   (complete page, images embedded, works offline apart from web fonts)
                 ->  build/artifact/<file>.html (same deck without the outer document tags, for claude.ai previews)

A source file starts with a <!--meta {json} --> block, followed by <section> slides and an optional <script>.
The build adds the title sheet, running heads, page numbers, footers (source + image credit) and the reference sheet.

Usage: python3 tools/build.py [file-stem ...]   (no argument = build all)
"""
import base64, html, json, mimetypes, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT, ART, IMG = ROOT / "src", ROOT / "decks", ROOT / "build/artifact", ROOT / "img"
CSS = (ROOT / "engine/deck.css").read_text()
JS = (ROOT / "engine/deck.js").read_text()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..600'
         '&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">')
AUTHOR = ('<b>Prepared by:</b> Dr. Abhishek Panda, MD Community Medicine<br>'
          '<b>Email:</b> support@dr-abhishekpanda-cm.app')
CHROME = '''<div id="notes" hidden></div>
<div id="toc" hidden><ol id="tocList"></ol></div>
<nav id="bar" aria-label="Slide controls">
  <button id="bPrev" aria-label="Previous">&larr;</button><button id="bNext" aria-label="Next">&rarr;</button>
  <span id="count"></span><div class="grow"><div id="prog"></div></div>
  <span id="clock" title="Start or pause the 60-minute timer">00:00 / 60</span>
  <button id="bToc" class="hide-sm" title="Contents (O)">Contents</button>
  <button id="bNotes" class="hide-sm" title="Speaker notes (N)">Notes</button>
  <button id="bFs" title="Full screen (F)">&#x26F6;</button>
</nav>'''


def credit(name):
    j = IMG / (Path(name).stem + ".json")
    if j.exists():
        c = json.loads(j.read_text())
        return f'{c["artist"]}, {c["license"]}, via {c["via"]}'
    return None


def embed(m):
    p = IMG / m.group(1)
    if not p.exists():
        print(f"  ! missing image img/{m.group(1)}: placeholder used")
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect width="400" height="300" fill="#ECEEE7"/>'
               '<text x="200" y="155" text-anchor="middle" font-family="monospace" font-size="16" fill="#7B877E">IMAGE: ' + m.group(1) + '</text></svg>')
        return f'src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"'
    mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
    return f'src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"'


def slide(attrs, body, short):
    a = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
    title = a.get("data-title", "")
    run = a.get("data-run", title)
    cls = a.get("class", "")
    head = f'<div class="run"><span><b>{short}</b> · {run}</span><span class="pn"></span></div>'
    if "section" in cls.split():
        head = f'<div class="run"><span><b>{short}</b></span><span class="pn"></span></div>'
    foot = ""
    srcs = [f'<span class="src">{a["data-src"]}</span>'] if a.get("data-src") else []
    imgs = []
    for n in dict.fromkeys(re.findall(r'src="img/([^"]+)"', body)):
        c = credit(n)
        if c and c not in imgs:
            imgs.append(c)
    if imgs:
        srcs.append(f'<span class="img">{"; ".join(imgs)}</span>')
    if srcs:
        foot = '<div class="foot">' + "".join(srcs) + "</div>"
    tab = f'<div class="tab">{a["data-tab"]}</div>' if a.get("data-tab") else ""
    if tab:
        cls += " has-tab"
    keep = " ".join(f'{k}="{v}"' for k, v in a.items() if k not in ("class", "data-src", "data-tab", "data-run"))
    return f'<section class="slide {cls.strip()}" {keep}>{head}{body}{foot}{tab}</section>'


def build(path):
    raw = path.read_text()
    m = re.match(r"\s*<!--meta(.*?)-->", raw, re.S)
    meta = json.loads(m.group(1))
    rest = raw[m.end():]
    style = ""
    st = re.search(r"\s*<style>(.*?)</style>", rest, re.S)
    if st:
        style, rest = st.group(1), rest[:st.start()] + rest[st.end():]
    script = ""
    sm = re.search(r"<script>(.*?)</script>\s*$", rest, re.S)
    if sm:
        script, rest = sm.group(1), rest[:sm.start()]
    short = meta["short"]
    slides = [slide(a, b, short) for a, b in re.findall(r"<section([^>]*)>(.*?)</section>", rest, re.S)]
    codes = "".join(f'<span class="chip">{c}</span>' for c in meta.get("codes", []))
    title = (f'<section class="slide title" data-title="Title"><div class="run"><span><b>Community Medicine</b> · {meta.get("part","")}</span>'
             f'<span class="pn"></span></div>{meta.get("art","")}<h1{' class="long"' if len(re.sub(r"<[^>]+>", "", meta["title"])) > 26 else ""}>{meta["title"]}</h1><p class="sub">{meta.get("sub","")}</p>'
             f'<div class="codes">{codes}</div><div class="by">{AUTHOR}</div><div class="tag">#CM-APP</div>'
             f'<aside class="notes"><p>{meta.get("notes","")}</p><p>Keys: &rarr; / Space next, &larr; back, N notes, O contents, F full screen, B blank screen. Click the clock to start the 60-minute timer.</p></aside></section>')
    refs = "".join(f"<li>{r}</li>" for r in meta.get("refs", []))
    ref = (f'<section class="slide" data-title="References"><div class="run"><span><b>{short}</b> · References</span><span class="pn"></span></div>'
           f'<h2 class="xs">References</h2><ol style="font-size:22px;line-height:1.42;padding-left:30px;max-width:1300px;display:grid;gap:9px">{refs}</ol>'
           f'<div class="by" style="position:absolute;left:168px;bottom:40px;font-family:var(--font-mono);font-size:17px;color:var(--ink-soft);line-height:1.6">{AUTHOR}</div>'
           f'<div style="position:absolute;right:120px;bottom:40px;font-family:var(--font-mono);font-size:20px;letter-spacing:.14em;color:var(--amber)">#CM-APP</div></section>')
    body = "\n".join([title] + slides + [ref])
    body = re.sub(r'src="img/([^"]+)"', embed, body)
    page_title = html.unescape(re.sub(r"<[^>]+>", "", meta["title"])).strip()
    inner = (f'<title>{page_title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
             f'<meta name="description" content="{html.escape(meta.get("desc",""))}">\n{FONTS}\n<style>{CSS}{style}</style>\n'
             f'<div id="viewport"><div id="stage">\n{body}\n</div></div>\n{CHROME}\n'
             f'<script>window.POLL_URL="";</script>\n<script>{JS}</script>\n'
             + (f"<script>(function(){{{script}}})();</script>\n" if script else ""))
    full = ('<!doctype html>\n<html lang="en-IN">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            + inner.replace("<div id=\"viewport\">", "</head>\n<body>\n<div id=\"viewport\">", 1) + "</body>\n</html>\n")
    OUT.mkdir(exist_ok=True); ART.mkdir(parents=True, exist_ok=True)
    (OUT / path.name).write_text(full)
    (ART / path.name).write_text(inner)
    print(f"built {path.stem}: {len(slides) + 2} slides, {len(full)//1024} KB")


if __name__ == "__main__":
    stems = sys.argv[1:]
    for p in sorted(SRC.glob("*.html")):
        if not stems or p.stem in stems or any(p.stem.startswith(s) for s in stems):
            build(p)
