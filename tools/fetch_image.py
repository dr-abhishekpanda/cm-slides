"""Fetch an openly licensed image from Wikimedia Commons into img/, with a credit file.

Usage:
  python3 tools/fetch_image.py search "<query>"            list candidate files with their licences
  python3 tools/fetch_image.py get "File:Name.jpg" <stem>  save img/<stem>.jpg and img/<stem>.json

Only public-domain, CC0, CC BY and CC BY-SA files are accepted. The credit line printed on each slide
comes from the .json file, so keep it accurate if you replace an image by hand.
"""
import io, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

from PIL import Image

API = "https://commons.wikimedia.org/w/api.php"
IMG = Path(__file__).resolve().parent.parent / "img"
UA = {"User-Agent": "cm-slides/1.0 (https://github.com/dr-abhishekpanda/cm-slides; educational slide decks)"}
OK = re.compile(r"^(public domain|pd|cc0|cc by(-sa)? [0-9.]+|cc by(-sa)?)", re.I)


def api(**params):
    params.update(format="json")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=40))


def info(title):
    d = api(action="query", titles=title, prop="imageinfo", iiprop="url|extmetadata|size", iiurlwidth=960)
    page = next(iter(d["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    md = ii["extmetadata"]
    clean = lambda k: re.sub(r"<[^>]+>", "", md.get(k, {}).get("value", "")).strip()
    return ii, clean("LicenseShortName"), clean("Artist") or "Unknown", clean("ImageDescription")[:160]


def search(q):
    d = api(action="query", generator="search", gsrsearch=q + " filetype:bitmap", gsrnamespace=6, gsrlimit=10,
            prop="imageinfo", iiprop="extmetadata|size")
    for page in d.get("query", {}).get("pages", {}).values():
        ii = page["imageinfo"][0]
        md = ii["extmetadata"]
        clean = lambda k: re.sub(r"<[^>]+>", "", md.get(k, {}).get("value", "")).strip()
        lic = clean("LicenseShortName")
        print(f'{"OK " if OK.match(lic) else "-- "}{page["title"]} | {lic} | {clean("Artist")[:40]} | {ii["width"]}x{ii["height"]}')


def get(title, stem, maxw=1300):
    ii, lic, artist, desc = info(title)
    if not OK.match(lic):
        sys.exit(f"Refused: licence '{lic}' is not open")
    req = urllib.request.Request(ii.get("thumburl") or ii["url"], headers=UA)
    im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=60).read())).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)))
    IMG.mkdir(exist_ok=True)
    im.save(IMG / f"{stem}.jpg", quality=80, optimize=True)
    lic = "Public Domain" if lic.lower().startswith(("public domain", "pd")) else lic
    (IMG / f"{stem}.json").write_text(json.dumps({"artist": artist[:80], "license": lic, "via": "Wikimedia Commons",
                                                  "file": title, "url": ii["descriptionurl"], "desc": desc}, indent=1))
    print(f"saved img/{stem}.jpg {im.width}x{im.height} | {lic} | {artist[:60]}")


def get_direct(title, stem, width=960):
    """Fallback when the API is rate-limited: read licence and author from the file page, image from upload server."""
    import hashlib, html as H
    name = title.replace("File:", "").replace(" ", "_")
    page = urllib.request.urlopen(urllib.request.Request(
        "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(name), headers=UA), timeout=40).read().decode()
    lic = re.search(r'class="licensetpl(?:_|&#95;)short[^"]*"[^>]*>(.*?)</', page, re.S)
    lic = H.unescape(re.sub(r"<[^>]+>", "", lic.group(1))).strip() if lic else ""
    if not lic and re.search(r"public domain", page, re.I):
        lic = "Public Domain"
    flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", H.unescape(page)))
    aut = re.search(r"Author (.*?) (?:Licensing|Permission|Other versions|Camera location|Attribution)", flat)
    artist = aut.group(1).strip()[:80] if aut else "Unknown"
    if not OK.match(lic):
        sys.exit(f"Refused: licence '{lic}' is not open")
    h = hashlib.md5(name.encode()).hexdigest()
    url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{urllib.parse.quote(name)}/{width}px-{urllib.parse.quote(name)}"
    if name.lower().endswith(".svg"):
        url += ".png"
    im = Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())).convert("RGB")
    im.save(IMG / f"{stem}.jpg", quality=80, optimize=True)
    lic = "Public Domain" if lic.lower().startswith(("public domain", "pd")) else lic
    (IMG / f"{stem}.json").write_text(json.dumps({"artist": artist, "license": lic, "via": "Wikimedia Commons", "file": title,
                                                  "url": "https://commons.wikimedia.org/wiki/File:" + name}, indent=1))
    print(f"saved img/{stem}.jpg {im.width}x{im.height} | {lic} | {artist}")


def search_html(q):
    url = "https://commons.wikimedia.org/w/index.php?" + urllib.parse.urlencode({"search": q, "ns6": 1, "fulltext": 1})
    page = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read().decode()
    for m in dict.fromkeys(re.findall(r'title="(File:[^"]+\.(?:jpe?g|png|JPG|svg))"', page)):
        print(m)


if __name__ == "__main__":
    {"search": lambda: search(sys.argv[2]), "get": lambda: get(sys.argv[2], sys.argv[3]), "direct": lambda: get_direct(sys.argv[2], sys.argv[3]), "find": lambda: search_html(sys.argv[2])}[sys.argv[1]]()
