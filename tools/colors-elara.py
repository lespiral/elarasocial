#!/usr/bin/env python3
"""Passa una infografia de Camins d'Esperança [Activa] als colors d'Elara Social.

Ús:  python3 tools/colors-elara.py src/templates/infografies/infografia-<nom>.html [...]

Canvia el fitxer al seu lloc. Es pot passar més d'un cop: el resultat no canvia.
- L'estructura (camins, punts encesos, textos) passa del verd fosc de Camins al blau marí d'Elara.
- La natura (turons, arbres, fulles) passa dels verds blavosos de Camins al verd del logo d'Elara.
- Els grisos verdosos (boira, núvols) passen a grisos blavosos.
- El groc del sol, els crems i els marrons no canvien: el sol és l'únic color càlid.
"""
import colorsys, re, sys
from pathlib import Path

# Colors de Camins amb un equivalent directe a site.css d'Elara
EXACT = {
    "#11352c": "#002445",  # green-900 → blau-900
    "#1a4d40": "#01315b",  # green-800 → blau-800 (el blau marí del logo)
    "#22604f": "#1a4a75",  # green-700 → blau-700
    "#2e7561": "#557e4c",  # green-600 → verd del logo
    "#c9dcd4": "#c8d6e3",  # green-200 → blau-200
    "#e3eee9": "#e1e9f1",  # green-100 → blau-100
    "#f0f6f3": "#f0f4f8",  # green-50  → blau-50
    "#56635d": "#55606a",  # muted
    "#23302b": "#1f2a33",  # ink
    "#e7e1d4": "#e3e7e4",  # line
    "#4f6158": "#4e5a48",  # tronc d'arbre (verd grisós)
}
VARS = [("--green-900", "--blau-900"), ("--green-800", "--blau-800"), ("--green-700", "--blau-700"),
        ("--green-600", "--verd"), ("--green-200", "--blau-200"), ("--green-100", "--blau-100"),
        ("--green-50", "--blau-50"), ("--sun-ink", "--sol-ink"), ("--sun", "--sol")]
RGBA = {(17, 53, 44): (1, 49, 91), (26, 77, 64): (1, 49, 91), (34, 96, 79): (26, 74, 117), (46, 117, 97): (85, 126, 76)}
VERD_HUE, BLAU_HUE = 109 / 360, 210 / 360


def remap(rgb):
    r, g, b = (c / 255 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    deg = h * 360
    if s >= .15 and 125 <= deg <= 185:      # verds blavosos de Camins → verd d'Elara
        h = VERD_HUE
    elif 0 < s < .15 and 120 <= deg <= 200:  # grisos verdosos → grisos blavosos
        h = BLAU_HUE
    else:
        return None
    return tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, l, s))


def hexcolor(m):
    v = m.group(0).lower()
    if v in EXACT:
        return EXACT[v]
    if v in EXACT.values():
        return v
    x = v[1:]
    if len(x) == 3:
        x = "".join(c * 2 for c in x)
    rgb = tuple(int(x[i:i + 2], 16) for i in (0, 2, 4))
    new = remap(rgb)
    return "#%02x%02x%02x" % new if new else v


def rgba(m):
    rgb = tuple(int(p) for p in re.split(r"\s*,\s*", m.group(1)))
    return "rgba(%d, %d, %d," % RGBA.get(rgb, rgb)


for f in sys.argv[1:]:
    p = Path(f)
    t = p.read_text(encoding="utf-8")
    for a, b in VARS:
        t = re.sub(re.escape(a) + r"(?![\w-])", b, t)
    t = re.sub(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b(?![0-9a-fA-F])", hexcolor, t)
    t = re.sub(r"rgba\(\s*(\d+\s*,\s*\d+\s*,\s*\d+)\s*,", rgba, t)
    p.write_text(t, encoding="utf-8")
    print("colors d'Elara:", f)
