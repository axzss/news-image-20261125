#!/usr/bin/env python3
"""Render THE WORLD front page for Wednesday 25 November 2026.

Draws a 1024x1024 newspaper front page with PIL only: masthead, dateline
band, lead headline, a PIL-drawn hero illustration (sea drones striking a
Russian corvette at Benghazi), three news columns, a second row, an
"Also today" strip, a markets ticker and a sources footer. All text is
drawn with PIL fonts, so every glyph is sharp and legible.

Stories are the overnight news cycle as reported on 25 November 2026
(Western datelines Tuesday 24 November; Wednesday 25 November in Asia):
Kyiv confirms sea strikes on Russian ships; Gaza strikes; Houthi drone
hits Riyadh's tallest tower; IRGC tanker-mine claim; Sarkozy/Bruni trial;
Giuliani Medal of Freedom; Russian death-toll analysis; EU sanctions;
Laos LDC graduation; Houthis near Aden; Tuesday market close.
Disputed claims are attributed in the text, never stated as raw fact.
COP31 is deliberately absent: it ended on 22 November, not the 25th.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (158, 24, 24)
GREY = (90, 86, 76)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, leading, fill=INK,
                  align="left"):
    lines = wrap(draw, text, fnt, max_w)
    for line in lines:
        if align == "center":
            lx = x + (max_w - draw.textlength(line, font=fnt)) / 2
        else:
            lx = x
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_hero(draw, box):
    """Dusk sea scene: burning corvette, smoke, two sea drones. No text."""
    x0, y0, x1, y1 = box
    horizon = y0 + int((y1 - y0) * 0.52)
    rnd = random.Random(20261125)
    # Sky: dusk gradient, deep navy to burnt orange at the horizon.
    for yy in range(y0, horizon):
        t = (yy - y0) / max(1, horizon - y0)
        r = int(24 + 214 * t)
        g = int(32 + 118 * t)
        b = int(64 + 52 * t)
        draw.line([(x0, yy), (x1, yy)], fill=(r, g, b))
    # Low sun glow: concentric discs, bright core to pale halo.
    sx, sy = x0 + int((x1 - x0) * 0.72), horizon - 26
    for rr, col in [(56, (205, 110, 55)), (44, (232, 142, 62)),
                    (32, (250, 172, 72)), (22, (255, 212, 122))]:
        draw.ellipse([sx - rr, sy - rr // 2, sx + rr, sy + rr // 2], fill=col)
    # Sea: dark blue with lighter wave strokes.
    for yy in range(horizon, y1):
        t = (yy - horizon) / max(1, y1 - horizon)
        draw.line([(x0, yy), (x1, yy)],
                  fill=(int(16 + 8 * t), int(34 + 10 * t), int(58 + 14 * t)))
    for _ in range(90):
        wx = rnd.randint(x0 + 8, x1 - 60)
        wy = rnd.randint(horizon + 6, y1 - 6)
        ln = rnd.randint(18, 64)
        draw.line([(wx, wy), (wx + ln, wy)], fill=(70, 110, 150), width=2)
    # Distant harbour silhouette on the left.
    draw.rectangle([x0, horizon - 34, x0 + 150, horizon], fill=(30, 32, 48))
    for cx in range(x0 + 12, x0 + 145, 26):
        draw.rectangle([cx, horizon - 58, cx + 14, horizon - 34],
                       fill=(30, 32, 48))
    # The corvette: dark hull, superstructure, mast, listing slightly.
    hx, hy = x0 + 300, horizon + 6
    hull = [(hx, hy), (hx + 330, hy), (hx + 306, hy + 30), (hx + 24, hy + 30)]
    draw.polygon(hull, fill=(12, 12, 16))
    draw.rectangle([hx + 130, hy - 34, hx + 210, hy], fill=(16, 16, 20))
    draw.rectangle([hx + 160, hy - 58, hx + 176, hy - 34], fill=(16, 16, 20))
    draw.line([(hx + 168, hy - 58), (hx + 168, hy - 78)], fill=(16, 16, 20),
              width=4)
    # Fire: layered orange/yellow tongues along the deck + one big plume.
    for fx, fh, fw in [(hx + 60, 46, 34), (hx + 120, 66, 44), (hx + 190, 56, 38),
                       (hx + 250, 40, 30), (hx + 290, 30, 24)]:
        for k in range(3):
            col = [(230, 90, 20), (250, 160, 40), (255, 220, 110)][k]
            w = fw - k * 9
            draw.polygon([(fx, hy - 2), (fx + w // 2, hy - fh + k * 12),
                          (fx + w, hy - 2)], fill=col)
    # Smoke: grey puffs rising above the ship, kept low so they stay
    # inside the hero panel.
    for i, (sx2, sy2, sr) in enumerate(
            [(hx + 140, hy - 62, 26), (hx + 170, hy - 88, 32),
             (hx + 205, hy - 108, 36), (hx + 245, hy - 120, 38),
             (hx + 290, hy - 126, 34)]):
        draw.ellipse([sx2 - sr, sy2 - sr // 2, sx2 + sr, sy2 + sr // 2],
                     fill=(58 + i * 6, 58 + i * 6, 62 + i * 6))
    # Fire reflection on the water.
    for i in range(14):
        rw = 120 - i * 6
        draw.line([(hx + 150 - rw // 2, hy + 34 + i * 7),
                   (hx + 150 + rw // 2, hy + 34 + i * 7)],
                  fill=(200, 110, 30), width=3)
    # Two sea drones with white wakes, heading for the ship.
    for dx, dy, s in [(x0 + 90, horizon + 96, 1.0), (x0 + 640, horizon + 128, 0.8)]:
        draw.polygon([(dx, dy), (dx + 46 * s, dy - 8 * s),
                      (dx + 52 * s, dy + 4 * s), (dx + 8 * s, dy + 10 * s)],
                     fill=(210, 210, 205))
        draw.line([(dx - 70 * s, dy + 14 * s), (dx, dy + 8 * s)],
                  fill=(220, 230, 235), width=3)
        draw.line([(dx - 50 * s, dy + 22 * s), (dx, dy + 12 * s)],
                  fill=(180, 195, 205), width=2)
    # A few gulls.
    for gx, gy in [(x0 + 700, y0 + 40), (x0 + 760, y0 + 62), (x0 + 820, y0 + 34)]:
        draw.arc([gx, gy, gx + 18, gy + 10], 200, 340, fill=(230, 230, 225),
                 width=2)
        draw.arc([gx + 18, gy, gx + 36, gy + 10], 200, 340,
                 fill=(230, 230, 225), width=2)


def column(draw, x, y, w, kicker, headline, body, head_size=21,
           body_size=15):
    draw.text((x, y), kicker, font=font(SANS_B, 13), fill=RED)
    y += 22
    y = draw_wrapped(draw, x, y, headline, font(SERIF_B, head_size), w,
                     head_size + 5)
    y += 4
    y = draw_wrapped(draw, x, y, body, font(SERIF, body_size), w,
                     body_size + 6)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36  # margin
    # --- Masthead ---
    d.line([(mx, 10), (W - mx, 10)], fill=INK, width=3)
    title = "THE WORLD"
    tf = font(SERIF_B, 92)
    d.text(((W - d.textlength(title, font=tf)) / 2, 14), title, font=tf,
           fill=INK)
    tag = "T H E   D A Y ' S   N E W S   ·   O N E   P A G E   ·   N O   N O I S E"
    sf = font(SANS, 13)
    d.text(((W - d.textlength(tag, font=sf)) / 2, 116), tag, font=sf, fill=GREY)
    # --- Dateline band ---
    d.rectangle([mx, 138, W - mx, 168], fill=INK)
    bf = font(SANS_B, 17)
    d.text((mx + 12, 145), "WEDNESDAY, 25 NOVEMBER 2026", font=bf,
           fill=(255, 255, 255))
    right = "EDITION Nº 25  ·  FREE"
    d.text((W - mx - 12 - d.textlength(right, font=bf), 145), right, font=bf,
           fill=(255, 255, 255))
    # --- Lead headline + dek ---
    d.text(((W - d.textlength("KYIV CONFIRMS SEA STRIKES", font=font(SERIF_B, 46))) / 2,
            178), "KYIV CONFIRMS SEA STRIKES", font=font(SERIF_B, 46), fill=INK)
    d.text(((W - d.textlength("ON RUSSIAN SHIPS", font=font(SERIF_B, 46))) / 2,
            228), "ON RUSSIAN SHIPS", font=font(SERIF_B, 46), fill=INK)
    dek = ("Zelenskiy says sea drones sank the corvette Merkury at Benghazi and "
           "confirms the Sparta II hit in the Gulf of Finland — as Moscow warns "
           "of “painful consequences” and calls the strike terrorism.")
    draw_wrapped(d, mx + 10, 282, dek, font(SERIF, 17), W - 2 * (mx + 10), 22,
                 align="center")
    # --- Hero illustration (drawn on its own layer so nothing escapes) ---
    hero = Image.new("RGB", (W - 2 * mx, 236), PAPER)
    hd = ImageDraw.Draw(hero)
    draw_hero(hd, (0, 0, W - 2 * mx, 236))
    img.paste(hero, (mx, 330))
    d.rectangle([mx, 330, W - mx, 566], outline=INK, width=2)
    cap = ("ILLUSTRATION — Ukrainian sea drones strike the Russian corvette "
           "Merkury at Benghazi, Libya. Artwork, not a photograph.")
    draw_wrapped(d, mx, 574, cap, font(SANS, 13), W - 2 * mx, 17, fill=GREY)
    d.line([(mx, 602), (W - mx, 602)], fill=INK, width=2)
    # --- Row 1: three columns ---
    cols = [
        ("GAZA",
         "SEVEN KILLED IN GAZA STRIKES AS CEASEFIRE FRAYS",
         "Israeli strikes killed seven Palestinians across Gaza on Tuesday, "
         "health officials said. Gaza's Health Ministry puts the toll since "
         "the October 2025 ceasefire began at 1,679 killed."),
        ("RIYADH",
         "HOUTHI DRONE HITS RIYADH'S TALLEST TOWER; 11 HURT",
         "A drone struck the PIF Tower in Riyadh on Tuesday, the second hit "
         "on the tallest tower in a week. Saudi Civil Defence said 11 were "
         "hurt; Britain sanctioned four Houthi officials."),
        ("STRAIT OF HORMUZ",
         "IRGC SAYS THREE MORE TANKERS HIT MINES",
         "Iran's Revolutionary Guard said three oil tankers struck naval "
         "mines in the Strait of Hormuz and caught fire, despite US escort. "
         "The claim, carried by state media, has not been independently "
         "verified."),
    ]
    col_w = 300
    xs = [mx, mx + 326, mx + 652]
    for (x, (kick, head, body)) in zip(xs, cols):
        column(d, x, 614, col_w, kick, head, body, head_size=19,
               body_size=14)
    for x in (mx + 313, mx + 639):
        d.line([(x, 614), (x, 806)], fill=(180, 174, 160), width=1)
    d.line([(mx, 814), (W - mx, 814)], fill=INK, width=2)
    # --- Row 2: two wider columns ---
    cols2 = [
        ("PARIS",
         "SARKOZY AND BRUNI ORDERED TO STAND TRIAL",
         "French judges sent the former president and his wife to trial over "
         "alleged witness tampering; 11 defendants face trial in late 2027."),
        ("WASHINGTON",
         "TRUMP GIVES GIULIANI MEDAL OF FREEDOM",
         "President Trump awarded the nation's highest civilian honour to "
         "Rudy Giuliani, 82, in a private Oval Office ceremony on Tuesday."),
    ]
    for (x, (kick, head, body)) in zip([mx, mx + 490], cols2):
        column(d, x, 824, 462, kick, head, body, head_size=18,
               body_size=13)
    d.line([(mx + 476, 824), (mx + 476, 922)], fill=(180, 174, 160), width=1)
    # --- Also today strip ---
    d.line([(mx, 934), (W - mx, 934)], fill=INK, width=1)
    also = ("ALSO TODAY:  700,000+ Russian dead, new Mediazona–Meduza analysis "
            "finds  ·  EU envoys meet on the 22nd Russia sanctions package  ·  "
            "Laos graduates from least-developed status  ·  Houthis 60 km from "
            "Aden, Yemen's army says")
    draw_wrapped(d, mx, 942, also, font(SANS, 13), W - 2 * mx, 17)
    # --- Markets ticker ---
    d.rectangle([mx, 980, W - mx, 1004], fill=INK)
    tick = "MARKETS —  NASDAQ −1.5%   ·   S&P 500 −0.5%   ·   DOW +0.9%   ·   NVIDIA −6% AFTER MONDAY'S +31% RALLY"
    tf2 = font(SANS_B, 13)
    d.text(((W - d.textlength(tick, font=tf2)) / 2, 987), tick, font=tf2,
           fill=(255, 255, 255))
    # --- Footer ---
    foot = ("Sources: Reuters · AP · BBC · Al Jazeera · Le Monde · CNN · RFE/RL · UN.  "
            "Disputed claims are attributed. Illustration is artwork.")
    ff = font(SANS, 12)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 1010), foot, font=ff,
           fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "assets", "entry.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
