"""Check deck sources against the house rules. Usage: python3 tools/lint.py"""
import re, sys
from pathlib import Path
BANNED = r"\b(delve|intricate|pivotal|underscore|crucial|landscape|realm|tapestry|testament|meticulous|commendable|foster|showcase|paramount|resonate|unwavering|compelling|elevate|surpass|holistic|seamless)\w*"
LABELS = r"\b(verbatim|interactive|exit ticket|exit slip|sundargarh|phase[- ]i)\b"
SRCNAMES = r"\b(Park|Gordis|Abramson|Sunder Lal|Maxcy|Rothman)\b"
bad = 0
for p in sorted(Path(__file__).resolve().parent.parent.glob("src/*.html")):
    t = p.read_text()
    t = re.sub(r"<!--meta.*?-->", "", t, flags=re.S)
    body = re.sub(r"<aside class=\"notes\">.*?</aside>|<script>.*?</script>|data-src=\"[^\"]*\"", "", t, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", body)
    for name, rx, src in [("banned word", BANNED, t), ("label", LABELS, text), ("source name in body", SRCNAMES, text)]:
        for m in re.finditer(rx, src if name == "banned word" else text, re.I):
            ctx = (src if name == "banned word" else text)[max(0, m.start() - 50):m.end() + 30].replace("\n", " ")
            print(f"{p.stem}: {name}: …{ctx}…"); bad += 1
    if re.search(r'class="eyebrow"', t):
        print(f"{p.stem}: eyebrow used"); bad += 1
    if "Moreover" in t or "Furthermore" in t or "It is important to note" in t:
        print(f"{p.stem}: banned opener"); bad += 1
print("issues:", bad)
