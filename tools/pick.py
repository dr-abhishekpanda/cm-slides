"""Contact sheet of chosen pages. Usage: python3 tools/pick.py <dir> 3 5 9 12 -> <dir>/pick.png"""
import sys
from PIL import Image
d, pages = sys.argv[1], [int(x) for x in sys.argv[2:]]
cols = 2 if len(pages) <= 4 else 3
rows = -(-len(pages) // cols); w, h = 1600 // cols, 900 // cols
im = Image.new("RGB", (w * cols, h * rows), "white")
for j, p in enumerate(pages):
    im.paste(Image.open(f"{d}/s{p:02d}.png").resize((w, h)), ((j % cols) * w, (j // cols) * h))
im.save(f"{d}/pick.png")
