#!/usr/bin/env python3
"""make_assets.py - writes wardens_assets.n64, the tables the Warden's March demo reads:
the sine table, the font, and the texts. Run it again after changing any of them:

    python make_assets.py

THE FONT is this demo's own: 5 x 7 glyphs drawn below as text, '#' a dot, stored one
byte a row (the top bit the left column), eight rows a glyph (the eighth blank), for
the characters 32..95 - space, punctuation, digits and capitals.
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))

GLYPHS = {
    " ": ".....|.....|.....|.....|.....|.....|.....",
    "!": "..#..|..#..|..#..|..#..|..#..|.....|..#..",
    "'": "..#..|..#..|.#...|.....|.....|.....|.....",
    "(": "...#.|..#..|.#...|.#...|.#...|..#..|...#.",
    ")": ".#...|..#..|...#.|...#.|...#.|..#..|.#...",
    "*": ".....|#.#.#|.###.|#####|.###.|#.#.#|.....",
    "+": ".....|..#..|..#..|#####|..#..|..#..|.....",
    ",": ".....|.....|.....|.....|.##..|..#..|.#...",
    "-": ".....|.....|.....|#####|.....|.....|.....",
    ".": ".....|.....|.....|.....|.....|.##..|.##..",
    "/": "....#|...#.|...#.|..#..|.#...|.#...|#....",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|..##.|.#...|#....|#####",
    "3": "####.|....#|....#|.###.|....#|....#|####.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    ":": ".....|.##..|.##..|.....|.##..|.##..|.....",
    "=": ".....|.....|#####|.....|#####|.....|.....",
    "?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
    "&": ".##..|#..#.|#.#..|.#...|#.#.#|#..#.|.##.#",
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.",
    "D": "###..|#..#.|#...#|#...#|#...#|#..#.|###..",
    "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": ".###.|..#..|..#..|..#..|..#..|..#..|.###.",
    "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#",
    "N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
}

TITLE = "THE WARDEN'S MARCH"
SCROLL = ("   PUREMETAL FORGE PRESENTS   * * *   THE WARDEN'S MARCH   * * *   "
          "A DEMO FOR THE NINTENDO 64, WRITTEN IN PUREMETAL AND COMPILED BY THE FORGE'S OWN "
          "VR4300 BACK END: SIXTY-FOUR-BIT MIPS III, BIG-ENDIAN, BOOTED BY ITS OWN IPL3   * * *   "
          "THE MUSIC IS THE MAIN THEME OF WARDEN'S KEY, PLAYED LIVE BY THE GAME'S OWN ENGINE PORTED TO PUREMETAL: "
          "THE SEQUENCER, PITCH AND ENVELOPES RUN ON THE VR4300, AND EVERY ONE OF THE 48000 SAMPLES A SECOND "
          "IS MADE ON THE RSP'S EIGHT-LANE VECTOR UNIT - FOUR-OPERATOR FM, WAVETABLES, NOISE AND REVERB - "
          "UP TO 32 VOICES AT ONCE   * * *   "
          "EVERY PIXEL HERE IS DRAWN BY THE RDP: GOURAUD TRIANGLES, COPPER BARS AND FILL RECTANGLES   * * *   "
          "GREETINGS TO EVERYONE STILL CODING FOR OLD IRON   * * *   PUREMETAL LABS 2026   * * *         ")

# THE HUD: what is being heard and seen, named on screen in two narrow
# columns beside the torus (12 characters, 6 pixels each). A caption is three
# such lines; they are stored at a fixed width (CAP_W = 3 x 12, space-padded)
# so the demo indexes them without a table.
CAP_W = 36
CAPTIONS = [
    ("TORUS", "128 QUADS", "GOURAUD-LIT"),
    ("STARFIELD", "56 STARS", "IN DEPTH"),
    ("COPPER BARS", "SHADED", "RECTANGLES"),
    ("SCROLLER", "ON A SINE", "5X7 FONT"),
    ("THE FLOOR", "14 BANDS", "RUSHING IN"),
    ("ALL OF IT", "DRAWN BY", "THE RDP"),
]
HUD = {
    "HudHear1": "HEARING:",
    "HudHear2": "LIVE SYNTH",
    "HudHear3": "ON THE RSP",
    "HudVoices": "VOICES",
    "HudOf": "/32",
    "HudFm": "FM",
    "HudWave": "WAVE",
    "HudRev1": "REVERB:",
    "HudRev2": "8 COMBS",
    "HudRev3": "4 ALL-PASS",
    "HudSee": "SEEING:",
    "HudMade": "WRITTEN AND COMPILED IN PUREMETAL",
}


def glyph_rows(ch):
    g = GLYPHS.get(ch, GLYPHS[" "])
    rows = []
    for r in g.split("|"):
        b = 0
        for i, c in enumerate(r):
            if c == "#":
                b |= 0x80 >> i
        rows.append(b)
    return rows + [0]


def data_lines(kind, values, per=16):
    out = []
    for i in range(0, len(values), per):
        out.append("  Data.%s %s" % (kind, ", ".join(str(v) for v in values[i:i + per])))
    return out


def main():
    for k, g in GLYPHS.items():
        rows = g.split("|")
        assert len(rows) == 7 and all(len(r) == 5 for r in rows), k
    sin = [int(round(math.sin(2 * math.pi * i / 256) * 16384)) for i in range(256)]
    font = []
    for c in range(32, 96):
        font += glyph_rows(chr(c))
    assert all(len(l) <= 12 for c in CAPTIONS for l in c), CAPTIONS
    for t in [TITLE, SCROLL] + [l for c in CAPTIONS for l in c] + list(HUD.values()):
        bad = [c for c in t if not (32 <= ord(c) < 96)]
        assert not bad, bad
    lines = [
        "; wardens_assets.n64 - GENERATED by make_assets.py; do not edit by hand.",
        "; The sine table (256 steps a turn, 16384 = 1), the font (5 x 7, characters 32..95,",
        "; eight bytes a glyph, the top bit the left column) and the texts.",
        "#SCROLL_LEN = %d" % len(SCROLL),
        "#TITLE_LEN = %d" % len(TITLE),
        "#CAP_W = %d" % CAP_W,
        "#CAP_N = %d" % len(CAPTIONS),
        "",
        "DataSection",
        "SinTab:",
    ]
    lines += data_lines("w", sin)
    lines.append("Font:")
    lines += data_lines("a", font)
    lines.append("TitleText:")
    lines += data_lines("a", [ord(c) for c in TITLE] + [0])
    lines.append("ScrollText:")
    lines += data_lines("a", [ord(c) for c in SCROLL] + [0])
    lines.append("CapText:")
    lines += data_lines("a", [ord(ch) for c in CAPTIONS for l in c for ch in l.ljust(12)])
    for name, t in HUD.items():
        lines.append(name + ":")
        lines += data_lines("a", [ord(c) for c in t] + [0])
    lines.append("EndDataSection")
    path = os.path.join(HERE, "wardens_assets.n64")
    with open(path, "w", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", path, "-", len(SCROLL), "characters of scroller")


if __name__ == "__main__":
    main()
