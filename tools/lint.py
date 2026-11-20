"""Check deck sources against the house rules. Usage: python3 tools/lint.py"""
import re, sys
from pathlib import Path
BANNED = r"\b(delve|intricate|pivotal|underscore|crucial|landscape|realm|tapestry|testament|meticulous|commendable|foster|showcase|paramount|resonate|unwavering|compelling|elevate|surpass|holistic|seamless)\w*"
LABELS = r"\b(verbatim|interactive|exit ticket|exit slip|sundargarh|phase[- ](i|ii|iii)\s+mbbs|mbbs\s+phase)\b"
SRCNAMES = r"\b(Park|Gordis|Abramson|Sunder Lal|Maxcy|Rothman)\b"
OPENERS = r"(^|[.!?]\s+|<p>|<li>)(Moreover|Furthermore|Additionally|It is important to note|It is worth noting|In today's world|In conclusion)\b"
# American spellings to avoid in slide text and notes (Indian English). Official names are allowed below.
US = (r"\b(program|programs|immunization|immunize|immunized|organization|center|centers|color|colors|labor|behavior|behaviour?al?|fiber|"
      r"hemoglobin|hemorrhage|hemorrhagic|anemia|anemic|diarrhea|edema|esophagus|esophageal|ischemic|ischemia|leukemia|anesthesia|"
      r"hematocrit|pediatric|pediatrics|fetus|fetal|estrogen|tumor|tumors|gray|mold|favor|honor|defense|"
      r"analyze|analyzed|organize|organized|recognize|recognized|utilize|minimize|prioritize|prioritized|standardize|standardized|"
      r"hospitalization|mobilization|urbanization|utilization|stabilization|sterilization|randomized|characterized|"
      r"modeling|traveling|counseling|catalog|aluminum|fulfill|enroll|aging)\b")
OFFICIAL = [r"World Health Organization", r"National Center for Vector Borne Diseases Control", r"Anemia Mukt Bharat",
            r"Immunization Handbook", r"Universal Immunization Programme", r"Global Polio Eradication", r"Pan American",
            r"Mission Indradhanush", r"Centers for Disease Control", r"National Immunization Schedule", r"Immunization Agenda",
            r"Intensified Mission", r"Expanded Programme on Immunization", r"Food and Agriculture Organization",
            r"International Labour Organization", r"Organization for", r"Population Research Center", r"Cancer Center",
            r"CDC", r"NCVBDC", r"behaviour", r"behavioural", r"Diabetes Prevention Program", r"\bGray\b"]
CURLY = "‘’“”"
bad = 0
def report(stem, kind, ctx):
    global bad
    print(f"{stem}: {kind}: …{ctx}…"); bad += 1
for p in sorted(Path(__file__).resolve().parent.parent.glob("src/*.html")):
    t = p.read_text()
    meta = re.search(r"<!--meta.*?-->", t, flags=re.S)
    t_nometa = re.sub(r"<!--meta.*?-->", "", t, flags=re.S)
    body = re.sub(r"<aside class=\"notes\">.*?</aside>|<script>.*?</script>|data-src=\"[^\"]*\"", "", t_nometa, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", body)
    for m in re.finditer(BANNED, t, re.I):
        report(p.stem, "banned word", t[max(0, m.start() - 50):m.end() + 30].replace("\n", " "))
    for rx, name in [(LABELS, "label"), (SRCNAMES, "source name in body")]:
        for m in re.finditer(rx, text, re.I if name == "label" else 0):
            report(p.stem, name, text[max(0, m.start() - 50):m.end() + 30].replace("\n", " "))
    if re.search(r'class="eyebrow"', t):
        report(p.stem, "eyebrow used", "")
    for m in re.finditer(OPENERS, t_nometa):
        report(p.stem, "banned opener", t_nometa[m.start():m.end() + 40].replace("\n", " "))
    # spelling: slide text and notes, skipping references, data-src and scripts
    sp = re.sub(r"<script>.*?</script>|<style>.*?</style>|<blockquote>.*?</blockquote>|data-src=\"[^\"]*\"", "", t_nometa, flags=re.S)
    sp = re.sub(r"<[^>]+>", " ", sp)
    for o in OFFICIAL:
        sp = re.sub(o, " ", sp)
    for m in re.finditer(US, sp, re.I):
        report(p.stem, "US spelling", sp[max(0, m.start() - 40):m.end() + 20].replace("\n", " "))
    for c in CURLY:
        if c in t:
            i = t.index(c); report(p.stem, "curly quote", t[max(0, i - 30):i + 10].replace("\n", " "))
    words = len(re.findall(r"\w+", text))
    dashes = text.count("—")
    if dashes and dashes > max(1, words // 300):
        report(p.stem, f"em-dashes ({dashes} in {words} words)", "")
print("issues:", bad)
