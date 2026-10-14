"""Embed assets/1.jpeg .. 6.jpeg into identity.svg as base64 (standalone file).
Run from the folder that contains identity.svg and assets/:
    python embed_images.py
Output: identity.embedded.svg   (pip install pillow  -> optional, shrinks the images)
"""
import base64, io, re, pathlib

src = pathlib.Path('identity.svg')
svg = src.read_text(encoding='utf-8')

try:
    from PIL import Image
except ImportError:
    Image = None

def data_uri(path):
    raw = pathlib.Path(path).read_bytes()
    if Image:  # cells are 180x125, so 540px wide is plenty
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        im.thumbnail((540, 380))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=80, optimize=True)
        raw = buf.getvalue()
    return 'data:image/jpeg;base64,' + base64.b64encode(raw).decode()

svg = re.sub(r'xlink:href="(assets/\d+\.jpe?g)"',
             lambda m: f'xlink:href="{data_uri(m.group(1))}"', svg)
pathlib.Path('identity.embedded.svg').write_text(svg, encoding='utf-8')
print('wrote identity.embedded.svg', len(svg) // 1024, 'KB')
