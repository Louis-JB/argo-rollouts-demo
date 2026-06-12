#!/usr/bin/env python3
"""Rend un fichier texte (sortie kubectl) en image PNG style terminal.
Usage: python3 render_terminal.py <input.txt> <output.png> "<titre fenêtre>"
"""
import sys, re
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BG = (24, 26, 32)
BAR = (38, 41, 50)
FG = (220, 223, 228)
GREEN = (87, 200, 110)
RED = (240, 100, 90)
BLUE = (90, 170, 245)
ORANGE = (239, 118, 39)
GREY = (130, 136, 148)

SIZE = 22
PAD = 28
BAR_H = 40

# colorisation par mot-clé (regex -> couleur)
RULES = [
    (re.compile(r"Healthy|✔|Successful|ANALYSE OK|200|Running"), GREEN),
    (re.compile(r"Degraded|✖|Failed|RolloutAborted|ANALYSE KO|500|Error|aborted"), RED),
    (re.compile(r"Paused|Progressing|◌|॥|AnalysisRun"), BLUE),
    (re.compile(r"setWeight|SetWeight|Step|canary|stable|Strategy|Canary"), ORANGE),
]

def color_for(line):
    for rx, col in RULES:
        if rx.search(line):
            return col
    if line.strip().startswith(("Name:", "Namespace:", "Images:", "Replicas:", "Message:", "Status:")):
        return GREY
    return FG

def main():
    src, out, title = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(src, encoding="utf-8", errors="replace").read()
    # retire d'éventuels codes ANSI
    raw = re.sub(r"\x1b\[[0-9;]*m", "", raw)
    lines = [l.rstrip() for l in raw.splitlines() if l.strip() != ""]

    font = ImageFont.truetype(FONT, SIZE)
    font_b = ImageFont.truetype(FONT_B, SIZE)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    cw = tmp.textlength("M", font=font)
    lh = SIZE + 8

    maxlen = max((len(l) for l in lines), default=40)
    W = int(PAD * 2 + cw * min(maxlen, 110))
    H = int(BAR_H + PAD * 2 + lh * len(lines))

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # barre de titre + pastilles
    d.rectangle([0, 0, W, BAR_H], fill=BAR)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([18 + i * 22, 14, 30 + i * 22, 26], fill=c)
    d.text((100, 10), title, font=font_b, fill=FG)

    y = BAR_H + PAD
    for l in lines:
        d.text((PAD, y), l, font=font, fill=color_for(l))
        y += lh
    img.save(out)
    print(f"OK -> {out}  ({W}x{H})")

if __name__ == "__main__":
    main()
