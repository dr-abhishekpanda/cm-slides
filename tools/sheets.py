"""Make 2x2 contact sheets from tools/shoot.js output. Usage: python3 tools/sheets.py <dir>"""
import glob, sys
from PIL import Image
d = sys.argv[1]; f = sorted(glob.glob(d + "/s*.png"))
for k in range(0, len(f), 4):
    im = Image.new("RGB", (1600, 900), "white")
    for j, fn in enumerate(f[k:k + 4]):
        im.paste(Image.open(fn).resize((800, 450)), ((j % 2) * 800, (j // 2) * 450))
    im.save(f"{d}/sheet{k // 4}.png")
print(len(f))
