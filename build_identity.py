#!/usr/bin/env python3
"""
SYLHETYHACKVENGER // THE-ERROR808  --  identity.svg builder
------------------------------------------------------------
Run this from the ROOT of your GitHub repository:

    python build_identity.py

It reads   assets/1.jpeg ... assets/6.jpeg   (monitor wall)
and        assets/sylhetyhackvenger.png      (hero logo)
and writes identity.svg with every picture EMBEDDED (base64).

WHY EMBED?  GitHub shows README images through <img>/camo. In that mode an SVG
is NOT allowed to load other files, so  <image href="assets/1.jpeg">  stays
blank. Embedded data-URIs are the only thing that works there.

Options:
    --assets DIR   folder with the pictures   (default: assets)
    --out FILE     output file                (default: identity.svg)
Pillow (pip install pillow) is optional: if present, pictures are resized and
compressed so the SVG stays small.
"""
import argparse, base64, io, os, random, sys, textwrap
from html import escape

# ───────────────────────── configuration ─────────────────────────
W = 1280                 # canvas width  (2x the old 640 -> crisp, high-res)
LOGO_CLIP_CIRCLE = True  # True = round badge, False = show logo uncropped
MARGIN = 60
CW = W - 2 * MARGIN      # content width = 1160

DISPLAY = "'Orbitron','Eurostile','Bank Gothic','Segoe UI','Arial Black',sans-serif"
MONO = "'JetBrains Mono','Fira Code','SF Mono','Courier New',Consolas,monospace"

CY, CY2, GR, RD, MG, AM = "#00f0ff", "#0a84ff", "#00ff9c", "#ff3b5c", "#ff2bd6", "#ffb020"

random.seed(808)

# ───────────────────────── asset loading ─────────────────────────
def find_asset(folder, base, exts):
    if not os.path.isdir(folder):
        return None
    names = {n.lower(): n for n in os.listdir(folder)}
    for e in exts:
        k = f"{base}.{e}".lower()
        if k in names:
            return os.path.join(folder, names[k])
    return None

def to_data_uri(path, kind):
    raw = open(path, "rb").read()
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "webp": "image/webp"}[path.rsplit(".", 1)[-1].lower()]
    try:
        from PIL import Image
        im = Image.open(path)
        buf = io.BytesIO()
        if kind == "photo":
            im = im.convert("RGB"); im.thumbnail((900, 640))
            im.save(buf, "JPEG", quality=78, optimize=True, progressive=True)
            mime = "image/jpeg"
        else:
            im = im.convert("RGBA"); im.thumbnail((760, 760))
            im.save(buf, "PNG", optimize=True)
            mime = "image/png"
        raw = buf.getvalue()
    except Exception:
        pass
    return f"data:{mime};base64," + base64.b64encode(raw).decode()

def asset_href(folder, base, exts, kind):
    p = find_asset(folder, base, exts)
    if p:
        print(f"  [ok]      embedded {p}")
        return to_data_uri(p, kind), True
    print(f"  [MISSING] {folder}/{base}.* not found -> using relative link (won't show on GitHub README)")
    return f"{folder}/{base}.{exts[0]}", False

# ───────────────────────── tiny svg helpers ─────────────────────────
_uid = [0]
def uid(p="u"):
    _uid[0] += 1
    return f"{p}{_uid[0]}"

def T(x, y, s, size=16, fill="#cfefff", anchor="start", weight=400, ls=0,
      font=MONO, extra="", op=None):
    o = f' opacity="{op}"' if op is not None else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" '
            f'letter-spacing="{ls}"{o} {extra}>{escape(s)}</text>')

def chamfer(x, y, w, h, c=18):
    return (f"M{x+c},{y} H{x+w-c} L{x+w},{y+c} V{y+h-c} L{x+w-c},{y+h} "
            f"H{x+c} L{x},{y+h-c} V{y+c} Z")

def panel(x, y, w, h, c=18, accent=CY, fill="url(#panelfill)", glow=True):
    d = chamfer(x, y, w, h, c)
    s = f'<path d="{d}" fill="{fill}" stroke="url(#pstroke)" stroke-width="1.6"/>'
    s += f'<path d="{d}" fill="url(#panelsheen)" opacity=".55"/>'
    # corner brackets
    L = 26
    s += (f'<g fill="none" stroke="{accent}" stroke-width="2.4" stroke-linecap="square"{" filter=\"url(#glow)\"" if glow else ""}>'
          f'<path d="M{x+c+4},{y+3} H{x+c+4+L}"/><path d="M{x+3},{y+c+4} V{y+c+4+L}"/>'
          f'<path d="M{x+w-c-4},{y+h-3} H{x+w-c-4-L}"/><path d="M{x+w-3},{y+h-c-4} V{y+h-c-4-L}"/></g>')
    return s

def blink(dur=1.2, begin=0):
    return (f'<animate attributeName="opacity" values="1;1;0.15;1" keyTimes="0;.55;.75;1" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')

def rec_tag(x, y, label="REC", color=RD):
    """x = RIGHT edge of the tag; dot position adapts to label length"""
    wtxt = len(label) * 10.9
    return (f'<circle cx="{x-wtxt-14:.0f}" cy="{y-5}" r="5" fill="{color}" filter="url(#glow)">{blink(1.1)}</circle>'
            + T(x, y, label, 13, color, "end", 700, 3))

def section_header(y, num, title, sub, tag="REC"):
    x = MARGIN
    hx = [(x + 26 + 24 * __import__("math").cos(__import__("math").radians(a)),
           y + 30 + 24 * __import__("math").sin(__import__("math").radians(a)))
          for a in range(0, 360, 60)]
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in hx)
    s = (f'<polygon points="{pts}" fill="#04141f" stroke="{CY}" stroke-width="2" filter="url(#glow)"/>'
         f'<polygon points="{pts}" fill="none" stroke="{CY}" stroke-width="1" opacity=".35" transform="rotate(30 {x+26} {y+30})">'
         f'<animateTransform attributeName="transform" type="rotate" from="0 {x+26} {y+30}" to="360 {x+26} {y+30}" dur="18s" repeatCount="indefinite"/></polygon>')
    s += T(x + 26, y + 37, num, 18, CY, "middle", 800, 0, DISPLAY)
    s += T(x + 66, y + 30, title, 34, "#ffffff", weight=800, ls=6, font=DISPLAY, extra='filter="url(#textglow)"')
    s += T(x + 68, y + 54, sub, 12.5, CY, ls=4, op=.75)
    s += f'<rect x="{x}" y="{y+70}" width="{CW}" height="2" fill="url(#hline)"/>'
    s += f'<rect x="{x}" y="{y+66}" width="90" height="10" fill="{CY}" opacity=".9" filter="url(#glow)"><animate attributeName="x" values="{x};{x+CW-90};{x}" dur="9s" repeatCount="indefinite"/></rect>'
    s += rec_tag(W - MARGIN, y + 30, tag)
    return s, y + 105

# ───────────────────────── main build ─────────────────────────
def build(assets_dir):
    print("Loading assets...")
    logo_href, _ = asset_href(assets_dir, "sylhetyhackvenger", ["png", "jpg", "jpeg", "webp"], "logo")
    cams = [asset_href(assets_dir, str(i), ["jpeg", "jpg", "png", "webp"], "photo")[0] for i in range(1, 7)]

    o = []           # body parts
    y = 0

    # ═══════════════ HERO ═══════════════
    HERO_H = 1070
    cx, cyh = W // 2, 400
    o.append(f'<rect width="{W}" height="{HERO_H}" fill="url(#herobg)"/>')
    o.append(f'<circle cx="{cx}" cy="{cyh}" r="520" fill="url(#heroglow)"/>')
    # top HUD bar
    o.append(f'<rect x="0" y="0" width="{W}" height="58" fill="#00060e" opacity=".85"/>'
             f'<rect x="0" y="57" width="{W}" height="1.5" fill="url(#hline)"/>')
    o.append(T(40, 36, "root@ERROR808:~# ./boot", 17, GR, ls=1) +
             f'<rect x="333" y="21" width="10" height="19" fill="{GR}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    o.append(T(cx, 37, "[ OPERATOR IDENTITY FILE ]", 16, CY, "middle", 700, 8, DISPLAY))
    o.append(T(W - 40, 37, "0x808", 22, "#ffffff", "end", 800, 4, DISPLAY, 'filter="url(#glow)"'))

    # logo rings
    ring = []
    ring.append(f'<circle cx="{cx}" cy="{cyh}" r="300" fill="none" stroke="{CY}" stroke-opacity=".12" stroke-width="1"/>')
    ring.append(f'<circle cx="{cx}" cy="{cyh}" r="262" fill="none" stroke="{CY}" stroke-width="2" stroke-dasharray="3 9" opacity=".6">'
                f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cyh}" to="360 {cx} {cyh}" dur="70s" repeatCount="indefinite"/></circle>')
    ring.append(f'<circle cx="{cx}" cy="{cyh}" r="240" fill="none" stroke="{CY}" stroke-width="16" stroke-dasharray="1.6 11.4" opacity=".55">'
                f'<animateTransform attributeName="transform" type="rotate" from="360 {cx} {cyh}" to="0 {cx} {cyh}" dur="90s" repeatCount="indefinite"/></circle>')
    ring.append(f'<circle cx="{cx}" cy="{cyh}" r="222" fill="none" stroke="{CY}" stroke-width="2.4" stroke-dasharray="160 40 60 40 20 40 220 60" filter="url(#glow)">'
                f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cyh}" to="360 {cx} {cyh}" dur="28s" repeatCount="indefinite"/></circle>')
    ring.append(f'<circle cx="{cx}" cy="{cyh}" r="204" fill="none" stroke="{CY2}" stroke-width="4" stroke-dasharray="90 700" stroke-linecap="round" filter="url(#glow)">'
                f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cyh}" to="-360 {cx} {cyh}" dur="6s" repeatCount="indefinite"/></circle>')
    ring.append(f'<circle cx="{cx}" cy="{cyh}" r="192" fill="#00060d" stroke="{CY}" stroke-width="2.5" filter="url(#glow)"/>')
    ring.append(f'<circle cx="{cx}" cy="{cyh}" r="192" fill="url(#logoback)"/>')
    # orbiting satellites
    for i, (r, dur, col) in enumerate([(262, 14, CY), (240, 21, MG), (222, 9, GR)]):
        ring.append(f'<circle r="5" fill="{col}" filter="url(#glow)"><animateMotion dur="{dur}s" repeatCount="indefinite" '
                    f'path="M{cx-r},{cyh} a{r},{r} 0 1,1 {2*r},0 a{r},{r} 0 1,1 -{2*r},0"/></circle>')
    o.append("".join(ring))
    # logo image
    lw = 350
    if LOGO_CLIP_CIRCLE:
        o.append(f'<clipPath id="logoclip"><circle cx="{cx}" cy="{cyh}" r="188"/></clipPath>')
        o.append(f'<image href="{logo_href}" xlink:href="{logo_href}" x="{cx-lw//2}" y="{cyh-lw//2}" width="{lw}" height="{lw}" '
                 f'preserveAspectRatio="xMidYMid meet" clip-path="url(#logoclip)"/>')
    else:
        o.append(f'<image href="{logo_href}" xlink:href="{logo_href}" x="{cx-lw//2}" y="{cyh-lw//2}" width="{lw}" height="{lw}" preserveAspectRatio="xMidYMid meet"/>')
    # scan beam over logo
    o.append(f'<clipPath id="logoclip2"><circle cx="{cx}" cy="{cyh}" r="188"/></clipPath>'
             f'<g clip-path="url(#logoclip2)"><rect x="{cx-200}" y="{cyh-200}" width="400" height="46" fill="url(#beam)" opacity=".55">'
             f'<animate attributeName="y" values="{cyh-240};{cyh+200};{cyh-240}" dur="5s" repeatCount="indefinite"/></rect>'
             f'<rect x="{cx-200}" y="{cyh-200}" width="400" height="400" fill="url(#scan)" opacity=".5"/></g>')
    # side HUD readouts
    def side(x, anchor, lines):
        s = ""
        for i, (k, v, c) in enumerate(lines):
            yy = 250 + i * 54
            s += T(x, yy, k, 12, CY, anchor, ls=3, op=.65) + T(x, yy + 22, v, 19, c, anchor, 700, 2, DISPLAY)
        sgn = -1 if anchor == "end" else 1
        s += f'<path d="M{x+sgn*0},{236} V{236+len(lines)*54-6}" stroke="{CY}" stroke-opacity=".35" stroke-width="2" transform="translate({-sgn*-14},0)"/>'
        return s
    o.append(side(110, "start", [("NODE", "SYLHET // BD", "#ffffff"), ("STATUS", "ONLINE", GR), ("MODE", "GRAY HAT", AM), ("INTEGRITY", "100%", CY)]))
    o.append(side(W - 110, "end", [("CODENAME", "THE-ERROR808", "#ffffff"), ("CLEARANCE", "0x808", MG), ("LAT / LON", "24.89N 91.87E", CY), ("THREAT", "CONTAINED", GR)]))
    # title
    ty = 745
    tl = 1040
    title = "SYLHETYHACKVENGER"
    o.append(f'<text x="{cx}" y="{ty}" font-family="{DISPLAY}" font-size="86" font-weight="900" fill="{CY}" text-anchor="middle" textLength="{tl}" lengthAdjust="spacingAndGlyphs" opacity=".75">{title}'
             f'<animate attributeName="x" values="{cx-5};{cx-5};{cx-9};{cx-3};{cx-5}" keyTimes="0;.8;.84;.9;1" dur="4s" repeatCount="indefinite"/></text>')
    o.append(f'<text x="{cx}" y="{ty}" font-family="{DISPLAY}" font-size="86" font-weight="900" fill="{MG}" text-anchor="middle" textLength="{tl}" lengthAdjust="spacingAndGlyphs" opacity=".6">{title}'
             f'<animate attributeName="x" values="{cx+5};{cx+5};{cx+10};{cx+2};{cx+5}" keyTimes="0;.8;.84;.9;1" dur="4s" repeatCount="indefinite"/></text>')
    o.append(f'<text x="{cx}" y="{ty}" font-family="{DISPLAY}" font-size="86" font-weight="900" fill="url(#tg)" text-anchor="middle" textLength="{tl}" lengthAdjust="spacingAndGlyphs" filter="url(#textglow)">{title}</text>')
    o.append(f'<text x="{cx}" y="{ty}" font-family="{DISPLAY}" font-size="86" font-weight="900" fill="none" stroke="#ffffff" stroke-opacity=".55" stroke-width=".8" text-anchor="middle" textLength="{tl}" lengthAdjust="spacingAndGlyphs">{title}</text>')
    # codename
    o.append(f'<rect x="{cx-330}" y="{ty+22}" width="660" height="2" fill="url(#hline)"/>')
    o.append(T(cx, ty + 72, "CODE :: THE-ERROR808", 36, CY, "middle", 800, 12, DISPLAY, 'filter="url(#glow)"'))
    # badges
    def badge(x, w, label, col):
        return (f'<path d="{chamfer(x, ty+105, w, 44, 10)}" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-width="1.8" filter="url(#glow)"/>'
                + T(x + w / 2, ty + 134, label, 17, col, "middle", 800, 4, DISPLAY))
    o.append(badge(cx - 440, 380, "DEFENSIVE ◆ OFFENSIVE", CY))
    o.append(badge(cx + 20, 420, "GRAY HAT RESEARCHER", MG))
    o.append(T(cx, ty + 196, "Defend. Research. Explore. Repeat.", 22, "#bfeaff", "middle", 400, 4, MONO, 'font-style="italic"'))
    # scroll chevrons
    for i in range(3):
        yy = HERO_H - 70 + i * 16
        o.append(f'<path d="M{cx-18},{yy} L{cx},{yy+12} L{cx+18},{yy}" fill="none" stroke="{CY}" stroke-width="2.5" opacity=".2" stroke-linecap="round">'
                 f'<animate attributeName="opacity" values=".15;1;.15" dur="1.8s" begin="{i*0.25}s" repeatCount="indefinite"/></path>')
    y = HERO_H + 20

    # ═══════════════ 01 DOSSIER ═══════════════
    s, y = section_header(y, "01", "DOSSIER", "// ABOUT THE OPERATOR")
    o.append(s)
    ph = 690
    o.append(panel(MARGIN, y, 720, ph))
    about = [
        "SYLHETYHACKVENGER — operating under the codename THE-ERROR808 — is a gray-hat security researcher based in Sylhet, Bangladesh.",
        "His work sits at the intersection of offense and defense: breaking systems in controlled lab environments to understand exactly how they fail, then turning those findings into practical hardening work.",
        "The focus spans network auditing, digital reconnaissance, and open-source intelligence gathering — built on the view that the strongest defenses come from operators who already think like an attacker.",
        "Much of this is sharpened through Capture The Flag competition, a discipline that rewards speed, precision, and creative problem-solving under pressure.",
        "The lab itself runs on Kali Linux and Termux for field and mobile work, scaling into Linux server administration and cloud infrastructure for deeper research.",
    ]
    ty2 = y + 84
    o.append(T(MARGIN + 34, y + 38, "▌ FILE: OPERATOR.DOSSIER", 13, CY, ls=4, op=.8))
    for i, para in enumerate(about):
        lines = textwrap.wrap(para, 56, break_on_hyphens=False)
        o.append(f'<rect x="{MARGIN+34}" y="{ty2-14}" width="3" height="{len(lines)*29-6}" fill="{CY if i%2==0 else MG}" opacity=".8"/>')
        for ln in lines:
            o.append(T(MARGIN + 54, ty2 + 4, ln, 19, "#d4f4ff"))
            ty2 += 29
        ty2 += 18
    # biometric panel
    bx, bw = MARGIN + 740, 420
    o.append(panel(bx, y, bw, ph))
    o.append(T(bx + 28, y + 38, "BIOMETRIC AUTH", 15, "#ffffff", ls=5, weight=800, font=DISPLAY))
    o.append(rec_tag(bx + bw - 28, y + 38))
    fx, fy = bx + bw / 2, y + 285
    o.append(f'<ellipse cx="{fx}" cy="{fy}" rx="128" ry="158" fill="#001018" stroke="{CY}" stroke-opacity=".4"/>')
    fp = []
    for i in range(1, 16):
        rx = 6 + i * 6.6
        ry = rx * 1.26
        da = f"{random.randint(24,95)} {random.randint(4,12)} {random.randint(8,34)} {random.randint(3,9)}"
        fp.append(f'<ellipse cx="{fx}" cy="{fy + (i%3)*1.5}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="{CY}" stroke-width="2.2" stroke-dasharray="{da}" opacity="{.35+ (i%4)*.14:.2f}" transform="rotate({random.randint(-8,8)} {fx} {fy})"/>')
    o.append(f'<g filter="url(#glow)">{"".join(fp)}</g>')
    o.append(f'<clipPath id="fpclip"><ellipse cx="{fx}" cy="{fy}" rx="128" ry="158"/></clipPath>'
             f'<g clip-path="url(#fpclip)"><rect x="{fx-130}" y="{fy-160}" width="260" height="50" fill="url(#beam)">'
             f'<animate attributeName="y" values="{fy-190};{fy+150};{fy-190}" dur="3.2s" repeatCount="indefinite"/></rect></g>')
    for sx in (-1, 1):
        for sy in (-1, 1):
            o.append(f'<path d="M{fx+sx*150},{fy+sy*140} h{-sx*26} M{fx+sx*150},{fy+sy*140} v{-sy*26}" stroke="{CY}" stroke-width="3" fill="none" filter="url(#glow)"/>')
    o.append(T(bx + bw / 2, y + 508, "PATTERN ANALYSIS IN PROGRESS", 14, CY, "middle", 700, 3))
    o.append(f'<rect x="{bx+40}" y="{y+524}" width="{bw-80}" height="12" fill="#001a22" stroke="{CY}" stroke-opacity=".5"/>'
             f'<rect x="{bx+43}" y="{y+527}" width="0" height="6" fill="{CY}" filter="url(#glow)"><animate attributeName="width" values="0;{bw-86};{bw-86};0" keyTimes="0;.7;.95;1" dur="5s" repeatCount="indefinite"/></rect>')
    o.append(f'<g><path d="{chamfer(bx+40, y+568, bw-80, 62, 12)}" fill="{GR}" fill-opacity=".1" stroke="{GR}" stroke-width="2" filter="url(#glow)"/>'
             + T(bx + bw / 2, y + 608, "✓ ACCESS GRANTED", 20, GR, "middle", 800, 3, DISPLAY, 'filter="url(#glow)"') +
             '<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.68;.74;.95;1" dur="5s" repeatCount="indefinite"/></g>')
    y += ph + 70

    # ═══════════════ 02 FIELD METRICS ═══════════════
    s, y = section_header(y, "02", "FIELD METRICS", "// LIVE TELEMETRY", "METRICS")
    o.append(s)
    metrics = [("35+", "REPOSITORIES", .72, CY), ("38+", "STARS EARNED", .78, AM), ("3", "CONTEST WINS", .6, GR), ("PY", "PRIMARY LANG", 1.0, MG)]
    tw = (CW - 3 * 24) / 4
    for i, (v, lab, frac, col) in enumerate(metrics):
        x = MARGIN + i * (tw + 24)
        o.append(panel(x, y, tw, 200, 16, col))
        rcx, rcy, rr = x + 70, y + 100, 44
        circ = 2 * 3.14159 * rr
        o.append(f'<circle cx="{rcx}" cy="{rcy}" r="{rr}" fill="none" stroke="{col}" stroke-opacity=".15" stroke-width="9"/>'
                 f'<circle cx="{rcx}" cy="{rcy}" r="{rr}" fill="none" stroke="{col}" stroke-width="9" stroke-linecap="round" stroke-dasharray="{circ*frac:.1f} {circ:.1f}" transform="rotate(-90 {rcx} {rcy})" filter="url(#glow)">'
                 f'<animate attributeName="stroke-dasharray" values="0 {circ:.1f};{circ*frac:.1f} {circ:.1f};{circ*frac:.1f} {circ:.1f}" keyTimes="0;.35;1" dur="6s" repeatCount="indefinite"/></circle>')
        o.append(f'<circle cx="{rcx}" cy="{rcy}" r="28" fill="none" stroke="{col}" stroke-width="1.5" stroke-dasharray="3 6" opacity=".6"><animateTransform attributeName="transform" type="rotate" from="0 {rcx} {rcy}" to="360 {rcx} {rcy}" dur="10s" repeatCount="indefinite"/></circle>')
        o.append(T(x + 132, y + 112, v, 62 if len(v) < 4 else 54, "#ffffff", weight=900, font=DISPLAY, extra=f'filter="url(#textglow)"'))
        o.append(T(x + 132, y + 146, lab, 13, col, ls=1.5, weight=700))
        o.append(T(x + 24, y + 34, f"MET-0{i+1}", 12, col, ls=3, op=.7))
        o.append(f'<rect x="{x+24}" y="{y+170}" width="{tw-48}" height="3" fill="{col}" opacity=".35"/><rect x="{x+24}" y="{y+170}" width="46" height="3" fill="{col}" filter="url(#glow)"><animate attributeName="x" values="{x+24};{x+tw-70};{x+24}" dur="{4+i}s" repeatCount="indefinite"/></rect>')
    y += 200 + 70

    # ═══════════════ 03 ARCHIVE / PROJECTS ═══════════════
    s, y = section_header(y, "03", "ARCHIVE", "// CLASSIFIED PROJECT FILES", "PROJECTS")
    o.append(s)
    def ic_net(c):
        return (f'<g stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"><path d="M32,16 L14,46 M32,16 L50,46 M14,46 H50"/>'
                f'<circle cx="32" cy="16" r="7" fill="#021018"/><circle cx="14" cy="46" r="7" fill="#021018"/><circle cx="50" cy="46" r="7" fill="#021018"/></g>')
    def ic_phone(c):
        return (f'<g stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"><rect x="19" y="8" width="26" height="48" rx="5"/><path d="M28,14 h8 M30,50 h4"/>'
                f'<path d="M26,28 a9,9 0 0,1 12,0 M23,24 a14,14 0 0,1 18,0" /><circle cx="32" cy="34" r="2" fill="{c}"/></g>')
    def ic_cam(c):
        return (f'<g stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="18" width="36" height="28" rx="4"/><path d="M44,28 L56,20 V44 L44,36"/>'
                f'<circle cx="26" cy="32" r="8"/><circle cx="26" cy="32" r="3" fill="{c}"/></g><circle cx="14" cy="24" r="2" fill="{RD}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></circle>')
    def ic_card(c):
        return (f'<g stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"><rect x="6" y="16" width="52" height="34" rx="5"/><path d="M6,26 H58"/>'
                f'<rect x="12" y="34" width="12" height="9" rx="2"/><path d="M32,40 h18"/></g>')
    def ic_radar(c):
        return (f'<g stroke="{c}" stroke-width="2" fill="none"><circle cx="32" cy="32" r="24"/><circle cx="32" cy="32" r="14"/><path d="M32,6 V58 M6,32 H58" stroke-opacity=".4"/>'
                f'<path d="M32,32 L32,8" stroke-width="3" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 32 32" to="360 32 32" dur="3s" repeatCount="indefinite"/></path></g>'
                f'<circle cx="44" cy="22" r="3" fill="{GR}"/><circle cx="22" cy="42" r="2.5" fill="{GR}"/>')
    def ic_flag(c):
        return (f'<g stroke="{c}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M16,8 V58"/><path d="M16,10 H50 L42,20 L50,30 H16" fill="{c}" fill-opacity=".25"/></g>')
    projs = [
        ("Network & Protocol Auditing", "Assessing exposed services & hardening", ic_net, CY),
        ("Mobile App Security Research", "Android app structure & trust analysis", ic_phone, MG),
        ("IoT / Camera System Research", "Camera & IoT exposure assessments", ic_cam, AM),
        ("Payment Flow QA Tooling", "Sandboxed payment gateway QA data", ic_card, GR),
        ("OSINT Recon Scripts", "Automated recon & footprint mapping", ic_radar, CY),
        ("CTF Writeups & Labs", "Challenge solutions & lab notes", ic_flag, MG),
    ]
    pw, ph2 = (CW - 2 * 26) / 3, 236
    for i, (t, d, ic, col) in enumerate(projs):
        x = MARGIN + (i % 3) * (pw + 26)
        yy = y + (i // 3) * (ph2 + 26)
        o.append(panel(x, yy, pw, ph2, 16, col))
        hx0, hy0 = x + 28, yy + 26
        o.append(f'<polygon points="{hx0+36},{hy0-4} {hx0+72},{hy0+16} {hx0+72},{hy0+56} {hx0+36},{hy0+76} {hx0},{hy0+56} {hx0},{hy0+16}" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-width="1.8" filter="url(#glow)"/>')
        o.append(f'<g transform="translate({hx0+4},{hy0+6}) scale(1.0)">{ic(col)}</g>')
        o.append(T(x + pw - 24, yy + 38, f"PRJ-0{i+1}", 13, col, "end", 700, 3))
        o.append(T(x + pw - 24, yy + 58, "STATUS: ACTIVE", 11, GR, "end", 400, 2, op=.85))
        o.append(T(x + 28, yy + 138, t, 19, "#ffffff", weight=800, ls=0.5, font=DISPLAY))
        for k, ln in enumerate(textwrap.wrap(d, 31)):
            o.append(T(x + 28, yy + 166 + k * 21, ln, 14.5, "#9fd8ee"))
        o.append(f'<rect x="{x+28}" y="{yy+ph2-26}" width="{pw-56}" height="4" fill="{col}" opacity=".18"/>'
                 f'<rect x="{x+28}" y="{yy+ph2-26}" width="{(pw-56)*(0.55+0.07*i):.0f}" height="4" fill="{col}" filter="url(#glow)"/>')
    y += 2 * ph2 + 26 + 70

    # ═══════════════ 04 DATA CENTER ═══════════════
    s, y = section_header(y, "04", "DATA CENTER", "// PC <-> ROUTER <-> SERVERS // LIVE TRAFFIC", "REC")
    o.append(s)
    dh = 620
    x0, y0 = MARGIN, y
    o.append(panel(x0, y0, CW, dh))
    o.append(f'<rect x="{x0+6}" y="{y0+6}" width="{CW-12}" height="{dh-12}" fill="url(#grid)" opacity=".8"/>')
    ny = y0 + 290
    # links
    web_y, db_y, auth_y = y0 + 140, y0 + 290, y0 + 440
    sx_ = x0 + 860
    links = {
        "ws": f"M{x0+270},{ny} L{x0+470},{ny}",
        "web": f"M{x0+590},{ny} C{x0+700},{ny} {x0+740},{web_y+45} {sx_},{web_y+45}",
        "db": f"M{x0+590},{ny} L{sx_},{db_y+45}",
        "auth": f"M{x0+590},{ny} C{x0+700},{ny} {x0+740},{auth_y+45} {sx_},{auth_y+45}",
    }
    o.append(T(x0 + 30, y0 + 40, "NETWORK TOPOLOGY", 15, "#ffffff", ls=5, weight=800, font=DISPLAY))
    o.append(rec_tag(x0 + CW - 28, y0 + 40))
    for k, d in links.items():
        gl = "" if k == "ws" else ' filter="url(#glow)"'
        o.append(f'<path d="{d}" fill="none" stroke="{CY}" stroke-opacity=".22" stroke-width="10"/>'
                 f'<path d="{d}" fill="none" stroke="{CY}" stroke-width="2.6" stroke-dasharray="10 8"{gl}><animate attributeName="stroke-dashoffset" values="36;0" dur="1.2s" repeatCount="indefinite"/></path>')
    def packet(d, col, dur, begin, rev=False):
        kp = 'keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if rev else ""
        return (f'<circle r="6.5" fill="{col}" filter="url(#softglow)"><animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" path="{d}" {kp}/></circle>')
    o.append(packet(links["ws"], CY, 1.8, 0) + packet(links["ws"], CY, 1.8, .9) + packet(links["ws"], GR, 1.8, .45, True))
    for k, c, dur in (("web", CY, 2.4), ("db", AM, 2.0), ("auth", MG, 2.8)):
        o.append(packet(links[k], c, dur, 0) + packet(links[k], GR, dur, dur / 2, True))
    o.append(T(x0 + 370, ny - 28, "REQ: GET /login", 15, CY, "middle", 700, 1))
    o.append(T(x0 + 370, ny + 44, "RES: 200 OK", 15, GR, "middle", 700, 1))
    for (lab, yy, c) in (("HTTPS:443", web_y + 18, CY), ("SQL:3306", db_y + 18, AM), ("SSH:22", auth_y + 18, MG)):
        o.append(f'<path d="{chamfer(x0+712, yy-18, 112, 30, 6)}" fill="#020c14" stroke="{c}" stroke-width="1.4"/>' + T(x0 + 768, yy + 3, lab, 14, c, "middle", 800, 1))
    # workstation
    wx, wy = x0 + 60, ny - 85
    o.append(f'<rect x="{wx}" y="{wy}" width="210" height="140" rx="9" fill="url(#bezel)" stroke="#5b7a92" stroke-width="1.5"/>'
             f'<rect x="{wx+10}" y="{wy+10}" width="190" height="112" rx="3" fill="#00130f" stroke="{GR}" stroke-opacity=".6"/>'
             f'<rect x="{wx+10}" y="{wy+10}" width="190" height="112" fill="url(#scan)" opacity=".6"/>'
             f'<path d="M{wx+95},{wy+140} l-12,38 h54 l-12,-38 Z" fill="#10202e" stroke="#4a6a82"/><rect x="{wx+60}" y="{wy+176}" width="90" height="8" rx="3" fill="#18303f" stroke="#4a6a82"/>')
    for k, (ln, c) in enumerate((("$ ping srv", GR), ("64 bytes ok", "#9ffcc8"), ("$ _", GR))):
        o.append(T(wx + 22, wy + 40 + k * 24, ln, 15, c))
    o.append(T(wx + 105, wy + 214, "WORKSTATION", 16, "#ffffff", "middle", 800, 3, DISPLAY) + T(wx + 105, wy + 236, "10.0.0.2", 14, CY, "middle", 400, 2))
    # router
    rx_, ry_ = x0 + 530, ny
    o.append(f'<path d="M{rx_-80},{ry_} l22,-38 h116 l22,38 l-22,38 h-116 Z" fill="url(#bezel)" stroke="{CY}" stroke-width="2" filter="url(#glow)"/>'
             f'<path d="M{rx_-62},{ry_} l16,-26 h92 l16,26 l-16,26 h-92 Z" fill="#031521" stroke="{CY}" stroke-opacity=".5"/>')
    for k in range(5):
        o.append(f'<circle cx="{rx_-40+k*20}" cy="{ry_}" r="4.5" fill="{[GR,CY,GR,AM,GR][k]}"><animate attributeName="opacity" values="1;.2;1" dur="{.6+k*.23}s" repeatCount="indefinite"/></circle>')
    o.append(f'<path d="M{rx_-50},{ry_-38} l-14,-34 M{rx_+50},{ry_-38} l14,-34" stroke="#5b7a92" stroke-width="4" stroke-linecap="round"/>')
    for s_ in (-1, 1):
        o.append(f'<path d="M{rx_+s_*70},{ry_-86} a14,14 0 0,{1 if s_>0 else 0} {s_*18},-12" fill="none" stroke="{CY}" stroke-width="2"><animate attributeName="opacity" values="1;.1;1" dur="1.6s" repeatCount="indefinite"/></path>')
    o.append(T(rx_, ry_ + 84, "ROUTER", 16, "#ffffff", "middle", 800, 3, DISPLAY) + T(rx_, ry_ + 106, "192.168.1.1", 14, CY, "middle", 400, 2))
    # servers
    for (nm, ip, yy, c) in (("WEB-SRV", "10.0.1.10", web_y, CY), ("DB-SRV", "10.0.1.20", db_y, AM), ("AUTH-SRV", "10.0.1.30", auth_y, MG)):
        o.append(f'<rect x="{sx_}" y="{yy}" width="280" height="90" rx="6" fill="url(#bezel)" stroke="{c}" stroke-width="1.8" filter="url(#glow)"/>'
                 f'<rect x="{sx_+10}" y="{yy+10}" width="260" height="30" rx="3" fill="#020b12" stroke="#2c4458"/><rect x="{sx_+10}" y="{yy+48}" width="260" height="30" rx="3" fill="#020b12" stroke="#2c4458"/>')
        o.append(T(sx_ + 24, yy + 31, nm, 16, "#ffffff", weight=800, ls=2, font=DISPLAY) + T(sx_ + 24, yy + 69, ip, 15, c, ls=1))
        for k in range(6):
            o.append(f'<rect x="{sx_+170+k*14}" y="{yy+20}" width="8" height="10" fill="{GR if k%2==0 else c}"><animate attributeName="opacity" values="1;.15;1" dur="{.5+((k*7)%5)*.2}s" repeatCount="indefinite"/></rect>'
                     f'<rect x="{sx_+170+k*14}" y="{yy+58}" width="8" height="10" fill="{c}" opacity=".85"><animate attributeName="opacity" values=".2;1;.2" dur="{.7+((k*3)%4)*.25}s" repeatCount="indefinite"/></rect>')
    # TCP handshake strip
    hy = y0 + dh - 70
    o.append(f'<rect x="{x0+40}" y="{hy-14}" width="{CW-80}" height="1.5" fill="url(#hline)"/>')
    for k, (lab, c) in enumerate((("TCP SYN  →", CY), ("←  TCP SYN-ACK", GR), ("TCP ACK  →", AM))):
        bx_ = x0 + 60 + k * 230
        o.append(f'<path d="{chamfer(bx_, hy, 210, 40, 9)}" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-width="1.5"><animate attributeName="fill-opacity" values=".08;.08;.4;.08;.08" keyTimes="0;{k*.22:.2f};{k*.22+.12:.2f};{k*.22+.24:.2f};1" dur="3.2s" repeatCount="indefinite"/></path>'
                 + T(bx_ + 105, hy + 26, lab, 15, c, "middle", 800, 2))
    o.append(f'<circle cx="{x0+CW-420}" cy="{hy+20}" r="6" fill="{GR}" filter="url(#glow)">{blink(1)}</circle>')
    o.append(T(x0 + CW - 400, hy + 26, "LINK UP 1Gbps // 3 NODES ONLINE", 16, GR, "start", 800, 2))
    y += dh + 70

    # ═══════════════ 05 SKILL MATRIX ═══════════════
    s, y = section_header(y, "05", "SKILL MATRIX", "// CAPABILITY ANALYSIS", "SKILLS")
    o.append(s)
    sh = 640
    o.append(panel(MARGIN, y, 720, sh))
    skills = [("CYBERSECURITY RESEARCH", 22, CY), ("NETWORK AUDITING", 21, CY), ("DIGITAL RECONNAISSANCE", 20, CY),
              ("OSINT INTELLIGENCE", 21, MG), ("ETHICAL HACKING LABS", 22, MG), ("CAPTURE THE FLAG", 23, MG),
              ("KALI LINUX", 23, GR), ("TERMUX", 21, GR), ("LINUX SERVERS", 19, AM), ("CLOUD", 17, AM)]
    seg_w = 26.0
    for i, (nm, n, c) in enumerate(skills):
        yy = y + 62 + i * 56
        o.append(T(MARGIN + 34, yy + 16, nm, 16, "#ffffff", weight=700, ls=2, font=DISPLAY))
        bx_ = MARGIN + 34
        by_ = yy + 28
        total = 24 * seg_w
        o.append(f'<line x1="{bx_}" y1="{by_+6}" x2="{bx_+total-4}" y2="{by_+6}" stroke="{c}" stroke-opacity=".13" stroke-width="14" stroke-dasharray="22 4"/>')
        o.append(f'<line x1="{bx_}" y1="{by_+6}" x2="{bx_+n*seg_w-4}" y2="{by_+6}" stroke="{c}" stroke-opacity=".28" stroke-width="22" stroke-dasharray="22 4"/>')
        o.append(f'<line x1="{bx_}" y1="{by_+6}" x2="{bx_+n*seg_w-4}" y2="{by_+6}" stroke="{c}" stroke-width="14" stroke-dasharray="22 4">'
                 f'<animate attributeName="stroke-opacity" values="1;.78;1" dur="{2+i*.2:.1f}s" repeatCount="indefinite"/></line>')
        o.append(f'<rect x="{bx_}" y="{by_-1}" width="40" height="14" fill="url(#shimmer)" opacity=".9"><animate attributeName="x" values="{bx_-30};{bx_+n*seg_w};{bx_-30}" dur="{3+i*.35:.2f}s" repeatCount="indefinite"/></rect>')
        pass
    # packet stream panel
    pxs, pws = MARGIN + 740, 420
    o.append(panel(pxs, y, pws, sh))
    o.append(T(pxs + 28, y + 38, "PACKET STREAM", 15, "#ffffff", ls=5, weight=800, font=DISPLAY))
    o.append(rec_tag(pxs + pws - 28, y + 38))
    o.append(f'<clipPath id="pkclip"><rect x="{pxs+20}" y="{y+56}" width="{pws-40}" height="360"/></clipPath>')
    rows = []
    hexs = "F997 AA53 BA6D 0AEF 2BE9 6176 4731 B292 C143 94BD B0CC 0278".split()
    for k in range(36):
        a = f"0x{k*16:04X}"
        row = " ".join(random.choice(hexs) for _ in range(3))
        col = GR if k % 5 == 0 else (CY if k % 3 else "#9fd8ee")
        rows.append(T(pxs + 34, y + 84 + k * 26, f"{a}  {row}", 15, col, op=.95 if k % 5 == 0 else .7))
    o.append(f'<g clip-path="url(#pkclip)"><g>{"".join(rows)}<animateTransform attributeName="transform" type="translate" values="0 0;0 -468" dur="14s" repeatCount="indefinite"/></g></g>')
    o.append(f'<rect x="{pxs+20}" y="{y+56}" width="{pws-40}" height="40" fill="url(#fadeTop)"/><rect x="{pxs+20}" y="{y+376}" width="{pws-40}" height="40" fill="url(#fadeBot)"/>')
    # oscilloscope
    oy = y + 520
    o.append(f'<rect x="{pxs+26}" y="{oy-70}" width="{pws-52}" height="140" fill="#00100c" stroke="{GR}" stroke-opacity=".5"/><rect x="{pxs+26}" y="{oy-70}" width="{pws-52}" height="140" fill="url(#grid)"/>')
    def wave(ph):
        pts = []
        for i in range(0, 41):
            xx = pxs + 26 + i * (pws - 52) / 40
            yy = oy + 38 * __import__("math").sin(i / 2.6 + ph) * (0.35 + 0.65 * __import__("math").sin(i / 7 + ph * .7) ** 2)
            pts.append(f"{xx:.1f},{yy:.1f}")
        return "M" + " L".join(pts)
    o.append(f'<path d="{wave(0)}" fill="none" stroke="{GR}" stroke-width="2.4" filter="url(#glow)"><animate attributeName="d" dur="2.4s" repeatCount="indefinite" values="{wave(0)};{wave(2.1)};{wave(4.2)};{wave(6.28)}"/></path>')
    o.append(T(pxs + 38, oy - 76 + 0, "", 1))
    o.append(T(pxs + 30, y + 436, "SIGNAL // 1Gbps  ▲ RX  ▼ TX", 13, GR, ls=2))
    y += sh + 70

    # ═══════════════ 06 TIMELINE ═══════════════
    s, y = section_header(y, "06", "TIMELINE", "// SERVICE RECORD", "TIMELINE")
    o.append(s)
    events = [("3RD PLACE", "C Program Contest, Sylhet", "url(#bronze)", "#e08a45"),
              ("1ST PLACE", "Python Program Contest, Sylhet", "url(#gold)", "#ffd23f"),
              ("1ST PLACE", "Gray Hat Hacker Comp, BD Region", "url(#gold)", "#ffd23f"),
              ("ONGOING", "Security research lab work", None, GR)]
    aly = y + 40
    o.append(f'<rect x="{MARGIN}" y="{aly-2}" width="{CW}" height="4" fill="{CY}" opacity=".18"/>'
             f'<rect x="{MARGIN}" y="{aly-2}" width="{CW}" height="4" fill="url(#hline)" filter="url(#glow)"/>'
             f'<path d="M{W-MARGIN-4},{aly-12} l18,12 l-18,12 Z" fill="{CY}" filter="url(#glow)"/>'
             f'<circle r="7" cy="{aly}" fill="#fff" filter="url(#softglow)"><animate attributeName="cx" values="{MARGIN};{W-MARGIN}" dur="6s" repeatCount="indefinite"/></circle>')
    cwid = (CW - 3 * 24) / 4
    for i, (rk, ev, grad, col) in enumerate(events):
        x = MARGIN + i * (cwid + 24)
        nx = x + cwid / 2
        o.append(f'<line x1="{nx}" y1="{aly}" x2="{nx}" y2="{aly+50}" stroke="{col}" stroke-width="2" stroke-dasharray="4 4"/>'
                 f'<circle cx="{nx}" cy="{aly}" r="12" fill="#02121b" stroke="{col}" stroke-width="3" filter="url(#glow)"/>'
                 f'<circle cx="{nx}" cy="{aly}" r="12" fill="none" stroke="{col}" stroke-width="2"><animate attributeName="r" values="12;26;12" dur="2.6s" begin="{i*.4}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0;.8" dur="2.6s" begin="{i*.4}s" repeatCount="indefinite"/></circle>')
        o.append(panel(x, aly + 50, cwid, 190, 14, col))
        o.append(T(x + 26, aly + 90, f"EVT-0{i+1}", 12, col, ls=3, op=.8))
        if grad:
            o.append(f'<circle cx="{x+cwid-50}" cy="{aly+104}" r="26" fill="{grad}" stroke="#fff" stroke-opacity=".5" filter="url(#glow)"/>'
                     + T(x + cwid - 50, aly + 114, rk[0], 28, "#2a1a00", "middle", 900, 0, DISPLAY))
        else:
            o.append(f'<circle cx="{x+cwid-50}" cy="{aly+104}" r="26" fill="none" stroke="{col}" stroke-width="3" stroke-dasharray="14 6" filter="url(#glow)"><animateTransform attributeName="transform" type="rotate" from="0 {x+cwid-50} {aly+104}" to="360 {x+cwid-50} {aly+104}" dur="4s" repeatCount="indefinite"/></circle>'
                     f'<circle cx="{x+cwid-50}" cy="{aly+104}" r="7" fill="{col}">{blink(1)}</circle>')
        o.append(T(x + 26, aly + 152, rk, 28, col, weight=900, ls=2, font=DISPLAY, extra='filter="url(#glow)"'))
        for k, ln in enumerate(textwrap.wrap(ev, 24)):
            o.append(T(x + 26, aly + 188 + k * 22, ln, 16, "#d4f4ff"))
    y += 40 + 50 + 190 + 70

    # ═══════════════ 07 MONITOR WALL ═══════════════
    s, y = section_header(y, "07", "MONITOR WALL", "// SURVEILLANCE GRID // 6 CHANNELS", "REC")
    o.append(s)
    sw_, sh_, bz = 336, 230, 14
    ow, oh = sw_ + 2 * bz, sh_ + 2 * bz + 22
    gap = (CW - 3 * ow) / 2 - 8
    wall_pad = 22
    wall_h = 2 * oh + gap + 2 * wall_pad + 20
    o.append(panel(MARGIN, y, CW, wall_h, 20))
    startx = MARGIN + (CW - (3 * ow + 2 * gap)) / 2
    for i in range(6):
        col_, row_ = i % 3, i // 3
        mx = startx + col_ * (ow + gap)
        my = y + wall_pad + 10 + row_ * (oh + gap)
        scx, scy = mx + bz, my + bz
        cid = f"cam{i+1}"
        accent = [CY, MG, GR, AM, CY, MG][i]
        cl = f'<clipPath id="{cid}"><rect x="{scx}" y="{scy}" width="{sw_}" height="{sh_}" rx="3"/></clipPath>'
        o.append(cl)
        # bezel + glow
        o.append(f'<rect x="{mx-3}" y="{my-3}" width="{ow+6}" height="{oh+6}" rx="14" fill="{accent}" opacity=".10" filter="url(#softglow)"/>')
        o.append(f'<rect x="{mx}" y="{my}" width="{ow}" height="{oh}" rx="11" fill="url(#bezel)" stroke="#6b8aa3" stroke-width="1.5"/>'
                 f'<rect x="{mx+2}" y="{my+2}" width="{ow-4}" height="{oh-4}" rx="9" fill="none" stroke="#fff" stroke-opacity=".08"/>')
        # screen base
        o.append(f'<rect x="{scx-2}" y="{scy-2}" width="{sw_+4}" height="{sh_+4}" rx="5" fill="#000" stroke="{accent}" stroke-opacity=".6"/>')
        o.append(f'<g clip-path="url(#{cid})">')
        # fallback "no signal" under the image
        o.append(f'<rect x="{scx}" y="{scy}" width="{sw_}" height="{sh_}" fill="url(#nosig)"/>' + T(scx + sw_ / 2, scy + sh_ / 2 + 5, "NO SIGNAL", 20, accent, "middle", 800, 6, DISPLAY, op=.5))
        # photo with slow push-in
        grow = 26
        cxm, cym = scx + sw_ / 2, scy + sh_ / 2
        dur = 14 + i * 1.7
        o.append(f'<image href="{cams[i]}" xlink:href="{cams[i]}" x="{scx}" y="{scy}" width="{sw_}" height="{sh_}" preserveAspectRatio="xMidYMid slice">'
                 f'<animate attributeName="x" values="{scx};{scx-grow/2};{scx}" dur="{dur}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{scy};{scy-grow/2*sh_/sw_:.1f};{scy}" dur="{dur}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="width" values="{sw_};{sw_+grow};{sw_}" dur="{dur}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="height" values="{sh_};{sh_+grow*sh_/sw_:.1f};{sh_}" dur="{dur}s" repeatCount="indefinite"/></image>')
        # grading & overlays
        o.append(f'<rect x="{scx}" y="{scy}" width="{sw_}" height="{sh_}" fill="{accent}" opacity=".10"/>'
                 f'<rect x="{scx}" y="{scy}" width="{sw_}" height="{sh_}" fill="url(#camvig)"/>'
                 f'<rect x="{scx}" y="{scy}" width="{sw_}" height="{sh_}" fill="url(#scan)" opacity=".55"/>')
        # rolling bar
        o.append(f'<rect x="{scx}" y="{scy-40}" width="{sw_}" height="40" fill="url(#roll)" opacity=".5"><animate attributeName="y" values="{scy-60};{scy+sh_+20}" dur="{5+i*.7:.1f}s" repeatCount="indefinite"/></rect>')
        # HUD brackets
        L = 22
        o.append(f'<g fill="none" stroke="{accent}" stroke-width="2.4" filter="url(#glow)">'
                 f'<path d="M{scx+10},{scy+10+L} V{scy+10} H{scx+10+L}"/><path d="M{scx+sw_-10-L},{scy+10} H{scx+sw_-10} V{scy+10+L}"/>'
                 f'<path d="M{scx+10},{scy+sh_-10-L} V{scy+sh_-10} H{scx+10+L}"/><path d="M{scx+sw_-10-L},{scy+sh_-10} H{scx+sw_-10} V{scy+sh_-10-L}"/></g>')
        # reticle
        o.append(f'<g stroke="{accent}" stroke-opacity=".7" stroke-width="1.4" fill="none"><circle cx="{cxm}" cy="{cym}" r="16"/><path d="M{cxm-26},{cym} h14 M{cxm+12},{cym} h14 M{cxm},{cym-26} v14 M{cxm},{cym+12} v14"/></g>')
        # tracking box
        bxx = scx + 60 + (i * 37) % 120
        byy = scy + 60 + (i * 23) % 60
        o.append(f'<g><rect x="{bxx}" y="{byy}" width="58" height="42" fill="none" stroke="{GR}" stroke-width="1.6" stroke-dasharray="6 3"/>'
                 + T(bxx, byy - 5, f"ID:0x{(0xA3F+i*0x1D7):X}", 10, GR) +
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;22 -8;-10 10;0 0" dur="{7+i}s" repeatCount="indefinite"/></g>')
        # texts
        o.append(T(scx + 18, scy + 32, f"CAM-0{i+1}", 17, "#ffffff", weight=800, ls=3, font=DISPLAY, extra='filter="url(#glow)"'))
        o.append(f'<circle cx="{scx+sw_-92}" cy="{scy+26}" r="5.5" fill="{RD}" filter="url(#glow)">{blink(1.0, i*.15)}</circle>')
        o.append(T(scx + sw_ - 78, scy + 32, "LIVE", 15, RD, weight=800, ls=2))
        o.append(T(scx + 18, scy + sh_ - 20, f"SYL-NODE-0{i+1} // 24.89N 91.87E", 11, accent, ls=1))
        o.append(T(scx + sw_ - 18, scy + sh_ - 20, "60FPS 4K", 11, "#fff", "end", 700, 1, op=.8))
        # glass reflection + occasional glitch
        o.append(f'<path d="M{scx},{scy} H{scx+sw_*0.62} L{scx+sw_*0.18},{scy+sh_} H{scx} Z" fill="url(#glass)"/>')
        o.append(f'<rect x="{scx}" y="{scy}" width="{sw_}" height="{sh_}" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;0;.14;0;.08;0;0" keyTimes="0;.86;.87;.89;.9;.92;1" dur="{6+i*1.3:.1f}s" repeatCount="indefinite"/></rect>')
        o.append('</g>')
        # bottom plate on bezel
        o.append(T(mx + ow / 2, my + oh - 8, f"MONITOR // CH-0{i+1}", 11, "#7fa8c0", "middle", 600, 4))
        o.append(f'<circle cx="{mx+ow-22}" cy="{my+oh-12}" r="3.2" fill="{GR}"><animate attributeName="opacity" values="1;.3;1" dur="2s" repeatCount="indefinite"/></circle>')
    y += wall_h + 70

    # ═══════════════ 08 ACHIEVEMENTS ═══════════════
    s, y = section_header(y, "08", "ACHIEVEMENTS", "// HONOURS & DISTINCTIONS", "ACHIEVEMENTS")
    o.append(s)

    def logo_hat():   # gray-hat shield emblem, 0..100 box
        return (f'<path d="M50,6 L88,20 V52 C88,74 70,90 50,96 C30,90 12,74 12,52 V20 Z" fill="#06141f" stroke="#c9d6df" stroke-width="3"/>'
                f'<path d="M50,14 L80,25 V51 C80,69 66,82 50,88 C34,82 20,69 20,51 V25 Z" fill="none" stroke="{CY}" stroke-width="1.2" opacity=".7"/>'
                f'<ellipse cx="50" cy="46" rx="29" ry="6.5" fill="#aab6bf"/><path d="M33,46 C33,26 41,22 50,22 C59,22 67,26 67,46 Z" fill="#8b98a2"/>'
                f'<path d="M33,43 H67 V38 H33 Z" fill="#1d2933"/><path d="M38,60 L47,68 L38,76 M52,76 H64" fill="none" stroke="{GR}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    def logo_py():
        blue = "M49,10 C30,10 31,18 31,18 L31,27 H50 V30 H24 C24,30 10,28 10,50 C10,72 22,71 22,71 H29 V61 C29,61 28,49 41,49 H58 C58,49 70,49 70,38 V22 C70,22 72,10 49,10 Z"
        return (f'<path d="{blue}" fill="#3b78b4"/><circle cx="41" cy="19.5" r="3.4" fill="#e8f2fb"/>'
                f'<path d="{blue}" fill="#ffd43b" transform="rotate(180 50 50)"/><circle cx="59" cy="80.5" r="3.4" fill="#fff8d6"/>')
    def logo_c():
        return (f'<polygon points="50,4 91,27 91,73 50,96 9,73 9,27" fill="#06141f" stroke="#7ab8ff" stroke-width="3"/>'
                f'<path d="M66,36 A22,22 0 1 0 66,64" fill="none" stroke="#7ab8ff" stroke-width="10" stroke-linecap="round"/>'
                f'<path d="M30,18 L22,26 M70,82 L78,74" stroke="{CY}" stroke-width="2"/>')
    ach = [
        ("1", "ST", "GRAY HAT HACKER", "COMPETITION", "CTF — BD REGION", "url(#gold)", "#ffd23f", logo_hat, "CHAMPION", "ACH-01"),
        ("1", "ST", "PYTHON PROGRAM", "CONTEST", "SYLHET REGION", "url(#gold)", "#ffd23f", logo_py, "CHAMPION", "ACH-02"),
        ("3", "RD", "C PROGRAM", "CONTEST", "SYLHET REGION", "url(#bronze)", "#e08a45", logo_c, "PODIUM", "ACH-03"),
    ]
    aw, ah = (CW - 2 * 26) / 3, 700
    for i, (num, suf, t1, t2, reg, grad, col, logo, status, aid) in enumerate(ach):
        x = MARGIN + i * (aw + 26)
        acx = x + aw / 2
        o.append(f'<ellipse cx="{acx}" cy="{y+150}" rx="{aw*0.55}" ry="190" fill="{col}" opacity=".10" filter="url(#bloom)"/>')
        o.append(panel(x, y, aw, ah, 22, col))
        o.append(f'<clipPath id="achclip{i}"><path d="{chamfer(x, y, aw, ah, 22)}"/></clipPath>')
        o.append(f'<g clip-path="url(#achclip{i})"><rect x="{x-80}" y="{y}" width="70" height="{ah}" fill="url(#holo)" opacity=".35" transform="skewX(-14)"><animate attributeName="x" values="{x-160};{x+aw+120};{x+aw+120}" keyTimes="0;.45;1" dur="7s" begin="{i*1.2}s" repeatCount="indefinite"/></rect></g>')
        o.append(T(x + 26, y + 38, "▌ ACHIEVEMENT UNLOCKED", 11.5, col, ls=3, weight=700))
        o.append(T(x + aw - 26, y + 38, aid, 12, col, "end", ls=3, op=.8))
        # medal
        my_ = y + 170
        o.append(f'<path d="M{acx-46},{my_+40} L{acx-66},{my_+130} L{acx-38},{my_+114} L{acx-24},{my_+140} L{acx-8},{my_+52} Z" fill="{CY2}" stroke="{CY}" stroke-width="1.5" opacity=".9"/>'
                 f'<path d="M{acx+46},{my_+40} L{acx+66},{my_+130} L{acx+38},{my_+114} L{acx+24},{my_+140} L{acx+8},{my_+52} Z" fill="#0b4fa0" stroke="{CY}" stroke-width="1.5" opacity=".9"/>')
        o.append(f'<circle cx="{acx}" cy="{my_}" r="104" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="4 10" opacity=".7"><animateTransform attributeName="transform" type="rotate" from="0 {acx} {my_}" to="360 {acx} {my_}" dur="30s" repeatCount="indefinite"/></circle>'
                 f'<circle cx="{acx}" cy="{my_}" r="92" fill="none" stroke="{col}" stroke-width="3" stroke-dasharray="120 30 40 30" filter="url(#glow)"><animateTransform attributeName="transform" type="rotate" from="360 {acx} {my_}" to="0 {acx} {my_}" dur="16s" repeatCount="indefinite"/></circle>'
                 f'<circle cx="{acx}" cy="{my_}" r="78" fill="{grad}" stroke="#ffffff" stroke-opacity=".7" stroke-width="2" filter="url(#glow)"/>'
                 f'<circle cx="{acx}" cy="{my_}" r="64" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="2"/>'
                 f'<circle cx="{acx}" cy="{my_}" r="58" fill="url(#medalshine)"/>')
        o.append(T(acx - 8, my_ + 28, num, 86, "#2a1800", "middle", 900, 0, DISPLAY))
        o.append(T(acx + 38, my_ - 4, suf, 22, "#2a1800", "start", 900, 1, DISPLAY))
        # logo frame
        ly = y + 395
        hexp = f"{acx},{ly-62} {acx+54},{ly-31} {acx+54},{ly+31} {acx},{ly+62} {acx-54},{ly+31} {acx-54},{ly-31}"
        o.append(f'<polygon points="{hexp}" fill="#020c14" stroke="{col}" stroke-width="2.4" filter="url(#glow)"/>'
                 f'<polygon points="{hexp}" fill="none" stroke="{col}" stroke-width="1" opacity=".4" transform="scale(1.18)" style="transform-origin:{acx}px {ly}px"/>')
        o.append(f'<g transform="translate({acx-38},{ly-38}) scale(.76)">{logo()}</g>')
        # title
        o.append(f'<rect x="{x+30}" y="{y+488}" width="{aw-60}" height="2" fill="url(#hline)"/>')
        o.append(T(acx, y + 540, t1, 26, "#ffffff", "middle", 900, 2, DISPLAY, 'filter="url(#textglow)"'))
        o.append(T(acx, y + 574, t2, 26, "#ffffff", "middle", 900, 2, DISPLAY, 'filter="url(#textglow)"'))
        o.append(T(acx, y + 612, reg, 15, col, "middle", 700, 4))
        o.append(f'<path d="{chamfer(acx-130, y+634, 260, 40, 10)}" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-width="1.6" filter="url(#glow)"/>'
                 + T(acx, y + 660, f"RANK #{num} ◆ {status}", 14, col, "middle", 800, 2, DISPLAY))
    y += ah + 70

    # ═══════════════ 09 BREACH SIM ═══════════════
    s, y = section_header(y, "09", "BREACH SIM", "// BRUTE-FORCE SEQUENCE // LAB ENVIRONMENT ONLY", "BREACH SIM")
    o.append(s)
    bh = 420
    o.append(panel(MARGIN, y, 720, bh))
    o.append(f'<rect x="{MARGIN+4}" y="{y+4}" width="712" height="34" fill="#000" opacity=".5"/>')
    for k, c in enumerate((RD, AM, GR)):
        o.append(f'<circle cx="{MARGIN+34+k*22}" cy="{y+22}" r="6" fill="{c}"/>')
    o.append(T(MARGIN + 140, y + 27, "bruteforce.sh — sandbox", 13, "#7fa8c0", ls=2))
    lines = [("root@ERROR808:~# ./bruteforce --target vault.local", GR, 0), ("[*] wordlist loaded // threads: 8", CY, 1),
             ("[001] admin123  ............ DENIED", RD, 2), ("[002] letmein   ............ DENIED", RD, 3),
             ("[003] qwerty    ............ DENIED", RD, 4), ("[004] P@ssw0rd  ............ DENIED", RD, 5),
             ("[005] ********  ............ MATCH", GR, 6)]
    for txt, c, k in lines:
        o.append(f'<g opacity="0">{T(MARGIN+34, y+84+k*36, txt, 18, c)}<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{k*.07:.2f};{k*.07+.02:.2f};.93;1" dur="12s" repeatCount="indefinite"/></g>')
    o.append(f'<rect x="{MARGIN+34}" y="{y+352}" width="652" height="12" fill="#001a22" stroke="{CY}" stroke-opacity=".5"/>'
             f'<rect x="{MARGIN+37}" y="{y+355}" width="0" height="6" fill="{CY}" filter="url(#glow)"><animate attributeName="width" values="0;646;646;0" keyTimes="0;.5;.93;1" dur="12s" repeatCount="indefinite"/></rect>')
    o.append(f'<g opacity="0">{T(MARGIN+34, y+398, "✓ ACCESS GRANTED", 22, GR, "start", 800, 4, DISPLAY, "filter=\"url(#glow)\"")}<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.5;.56;.93;1" dur="12s" repeatCount="indefinite"/></g>')
    qx, qw = MARGIN + 740, 420
    o.append(panel(qx, y, qw, bh, 18, MG))
    qcx = qx + qw / 2
    o.append(T(qx + 30, y + 120, "“", 120, MG, font=DISPLAY, weight=900, op=.5))
    for k, ln in enumerate(("The best defense is", "understanding the", "offense.")):
        o.append(T(qx + 40, y + 170 + k * 44, ln, 31, "#ffffff", weight=800, ls=0.5, font=DISPLAY, extra='filter="url(#textglow)"'))
    o.append(f'<rect x="{qx+40}" y="{y+312}" width="70" height="3" fill="{MG}" filter="url(#glow)"/>')
    o.append(T(qx + 40, y + 346, "— THE-ERROR808", 18, MG, ls=3, weight=800))
    o.append(T(qx + 40, y + 384, "EST. 808", 22, CY, ls=8, weight=900, font=DISPLAY, extra='filter="url(#glow)"'))
    y += bh + 70

    # ═══════════════ FOOTER ═══════════════
    o.append(f'<rect x="0" y="{y}" width="{W}" height="2" fill="url(#hline)"/>')
    o.append(f'<circle cx="{MARGIN+10}" cy="{y+60}" r="8" fill="{GR}" filter="url(#glow)">{blink(1.2)}</circle>')
    o.append(T(MARGIN + 32, y + 68, "ALL SYSTEMS ONLINE", 22, GR, weight=900, ls=6, font=DISPLAY, extra='filter="url(#glow)"'))
    o.append(T(W - MARGIN, y + 68, "IDENTITY.SVG // THE-ERROR808", 17, CY, "end", 700, 4))
    ecg = "M0,0 H80 l10,-4 l10,4 H150 l8,-6 l10,48 l12,-84 l12,66 l8,-24 H300 l10,-8 l14,8 H420"
    o.append(f'<g transform="translate({MARGIN},{y+130})"><clipPath id="ecgclip"><rect x="0" y="-90" width="{CW}" height="140"/></clipPath><g clip-path="url(#ecgclip)"><g>'
             + "".join(f'<path d="{ecg}" transform="translate({k*420},0)" fill="none" stroke="{GR}" stroke-width="2.4" filter="url(#glow)"/>' for k in range(4)) +
             f'<animateTransform attributeName="transform" type="translate" values="0 0;-420 0" dur="4s" repeatCount="indefinite"/></g></g></g>')
    y += 230
    H = int(y)

    # ═══════════════ ASSEMBLE ═══════════════
    # matrix rain background
    rain = []
    glyphs = "01ABCDEF$#%*+=<>/"
    for c in range(16):
        xx = 30 + c * 80
        chars = "".join(f'<tspan x="{xx}" dy="19">{escape(random.choice(glyphs))}</tspan>' for _ in range(70))
        dur = random.uniform(30, 55)
        rain.append(f'<g opacity="{random.choice([.05,.06,.08])}"><animateTransform attributeName="transform" type="translate" values="0 -1400;0 {H}" dur="{dur:.1f}s" begin="-{random.uniform(0,dur):.1f}s" repeatCount="indefinite"/>'
                    f'<text x="{xx}" y="0" font-family="{MONO}" font-size="16" fill="{GR}">{chars}</text></g>')

    defs = f'''<defs>
<linearGradient id="bg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{H}"><stop offset="0" stop-color="#06142a"/><stop offset=".35" stop-color="#030b18"/><stop offset=".7" stop-color="#02070f"/><stop offset="1" stop-color="#000206"/></linearGradient>
<radialGradient id="herobg" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#0a2a44" stop-opacity=".9"/><stop offset=".6" stop-color="#04101f" stop-opacity=".4"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<radialGradient id="heroglow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{CY}" stop-opacity=".38"/><stop offset=".5" stop-color="{CY2}" stop-opacity=".12"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></radialGradient>
<radialGradient id="logoback" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#0c3350" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity=".2"/></radialGradient>
<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".48" stop-color="#bdf8ff"/><stop offset=".52" stop-color="#38d6ff"/><stop offset="1" stop-color="#e2fcff"/></linearGradient>
<linearGradient id="hline" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset=".15" stop-color="{CY}"/><stop offset=".85" stop-color="{CY2}"/><stop offset="1" stop-color="{CY2}" stop-opacity="0"/></linearGradient>
<linearGradient id="panelfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b2234" stop-opacity=".92"/><stop offset="1" stop-color="#030a13" stop-opacity=".96"/></linearGradient>
<linearGradient id="panelsheen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".07"/><stop offset=".35" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="pstroke" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CY}" stop-opacity=".95"/><stop offset=".5" stop-color="{CY2}" stop-opacity=".35"/><stop offset="1" stop-color="{CY}" stop-opacity=".8"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff6c2"/><stop offset=".35" stop-color="#ffd23f"/><stop offset=".7" stop-color="#b8860b"/><stop offset="1" stop-color="#ffe58a"/></linearGradient>
<linearGradient id="bronze" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffdcb8"/><stop offset=".35" stop-color="#e08a45"/><stop offset=".7" stop-color="#8a4a1c"/><stop offset="1" stop-color="#f4b87e"/></linearGradient>
<radialGradient id="medalshine" cx="35%" cy="30%" r="70%"><stop offset="0" stop-color="#fff" stop-opacity=".65"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="bezel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#46586b"/><stop offset=".08" stop-color="#2a3846"/><stop offset=".5" stop-color="#16212c"/><stop offset="1" stop-color="#0a1118"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".20"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset=".85" stop-color="{CY}" stop-opacity=".6"/><stop offset="1" stop-color="#e8ffff" stop-opacity=".95"/></linearGradient>
<linearGradient id="roll" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="shimmer" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="holo" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="{MG}" stop-opacity="0"/></linearGradient>
<linearGradient id="fadeTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b2234"/><stop offset="1" stop-color="#0b2234" stop-opacity="0"/></linearGradient>
<linearGradient id="fadeBot" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#050d17"/><stop offset="1" stop-color="#050d17" stop-opacity="0"/></linearGradient>
<linearGradient id="nosig" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a1620"/><stop offset="1" stop-color="#02060a"/></linearGradient>
<radialGradient id="camvig" cx="50%" cy="50%" r="72%"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".72"/></radialGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".8"/><stop offset=".12" stop-color="#000" stop-opacity="0"/><stop offset=".88" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".8"/></linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset=".5" stop-color="{CY}" stop-opacity=".10"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="{CY}" stroke-opacity=".07"/></pattern>
<pattern id="hex" width="56" height="97" patternUnits="userSpaceOnUse"><path d="M28 0 L56 16 L56 48 L28 64 L0 48 L0 16 Z M28 64 L28 97 M0 48 L0 81 L28 97 L56 81 L56 48" fill="none" stroke="{CY}" stroke-opacity=".055"/></pattern>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.3" fill="#000" fill-opacity=".38"/></pattern>
<filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="softglow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="textglow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="7" result="b"/><feColorMatrix in="b" type="matrix" values="0 0 0 0 0  0 0 0 0 .85  0 0 0 0 1  0 0 0 .9 0" result="c"/><feMerge><feMergeNode in="c"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="bloom" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
<filter id="noise" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 1  0 0 0 0 1  0 0 0 .05 0"/></filter>
</defs>'''

    head = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="SYLHETYHACKVENGER // THE-ERROR808 cinematic identity">'
            f'<title>SYLHETYHACKVENGER // THE-ERROR808</title>')
    back = (f'<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#hex)"/>'
            f'<rect width="{W}" height="{H}" fill="url(#grid)"/>' + "".join(rain))
    sweep = (f'<rect x="0" y="-300" width="{W}" height="300" fill="url(#sweep)"><animate attributeName="y" values="-300;{H}" dur="16s" repeatCount="indefinite"/></rect>')
    post = (f'<rect width="{W}" height="{H}" fill="url(#edge)" opacity=".65"/>'
            )
    svg = head + defs + back + "".join(o) + sweep + post + "</svg>"
    return svg, H

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default="assets")
    ap.add_argument("--out", default="identity.svg")
    a = ap.parse_args()
    svg, H = build(a.assets)
    open(a.out, "w", encoding="utf-8").write(svg)
    print(f"\nWrote {a.out}  ({len(svg)/1024:.0f} KB, {W}x{H})")
