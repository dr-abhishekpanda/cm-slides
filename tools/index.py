"""Write index.html (deck catalogue for GitHub Pages / the website) from the deck sources.
Usage: python3 tools/index.py"""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PARTS = {"A": "Foundations", "B": "Epidemiology and Screening", "C": "Communicable Diseases", "D": "Non-communicable Diseases",
         "E": "Health Programmes", "F": "Demography, Family Planning and RMNCH+A", "G": "Nutrition", "H": "Environment and Health",
         "I": "Occupational, Genetic and Mental Health", "J": "Biostatistics", "K": "Communication, Planning and Health Systems"}
rows = {}
for p in sorted((ROOT / "src").glob("*.html")):
    meta = json.loads(re.match(r"\s*<!--meta(.*?)-->", p.read_text(), re.S).group(1))
    title = re.sub(r"<[^>]+>", "", meta["title"])
    rows.setdefault(p.stem[0], []).append((p.stem, title, meta.get("sub", ""), ", ".join(meta.get("codes", []))))
body = ""
for k, name in PARTS.items():
    if k not in rows:
        continue
    items = "".join(f'<a class="row" href="decks/{s}.html"><span class="id">{s.split("-")[0]}</span><span><b>{t}</b><br><small>{sub}</small></span><span class="cm">{c}</span></a>'
                    for s, t, sub, c in rows[k])
    body += f"<h2>Part {k} · {name}</h2>{items}"
html = f"""<!doctype html><html lang="en-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CM Lecture Decks</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,450&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--paper:#F4F5F1;--ink:#15201B;--soft:#4B5A52;--teal:#0C5E4E;--amber:#BE651F;--line:#D7DCD1}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:"IBM Plex Sans",Calibri,sans-serif;padding:40px max(16px,env(safe-area-inset-left))}}
main{{max-width:960px;margin:0 auto}} h1{{font-family:Fraunces,Georgia,serif;font-weight:450;font-size:clamp(2.2rem,6vw,3.6rem);margin:0 0 8px}}
h2{{font-family:Fraunces,Georgia,serif;font-weight:450;font-size:1.6rem;margin:40px 0 12px;color:var(--teal)}}
p.l{{color:var(--soft);max-width:60ch}}
.row{{display:grid;grid-template-columns:70px 1fr auto;gap:16px;align-items:center;padding:14px 16px;border-bottom:1px solid var(--line);text-decoration:none;color:inherit}}
.row:hover{{background:#ECEEE7}} .id{{font-family:"IBM Plex Mono",Consolas,monospace;color:var(--amber)}} .cm{{font-family:"IBM Plex Mono",Consolas,monospace;font-size:.8rem;color:var(--soft)}}
small{{color:var(--soft)}} footer{{margin-top:60px;font-family:"IBM Plex Mono",Consolas,monospace;font-size:.8rem;color:var(--soft);line-height:1.7}}
@media(max-width:600px){{.row{{grid-template-columns:52px 1fr}} .cm{{display:none}}}}
</style></head><body><main>
<h1>Community Medicine Lecture Decks</h1>
<p class="l">One-hour interactive lecture decks, organised by topic and mapped to the NMC CBME 2024 competencies. Open a deck and press F for full screen, N for speaker notes.</p>
{body}
<footer>Prepared by: Dr. Abhishek Panda, MD Community Medicine<br>Email: support@dr-abhishekpanda-cm.app<br>#CM-APP</footer>
</main></body></html>"""
(ROOT / "index.html").write_text(html)
print("index.html:", sum(len(v) for v in rows.values()), "decks")
