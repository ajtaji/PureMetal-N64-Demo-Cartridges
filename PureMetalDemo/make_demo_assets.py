#!/usr/bin/env python3
"""make_demo_assets.py - writes demo_assets.n64, the tables the PureMetal demo reads.

Everything here is this project's own: the 8x8 font is drawn below, the tune is
written below. The tables are DataSection blocks the demo reaches with ?Label:

  SinTab     256 x Data.w   sin(2 pi i / 256) * 16384
  Font       Data.a         8 bytes a glyph (top row first, bit 7 the left pixel),
                            glyph g for character code 32 + g, codes 32-95
  NoteInc    Data.l         the oscillator's phase step for MIDI notes 0-95 at the
                            demo's sample rate (32-bit phase, so step = f * 2^32 / rate)
  SongLead / SongArp / SongBass / SongDrum
             Data.a         one byte a sixteenth (a "row"): a MIDI note, 0 for
                            nothing new; the drum track's 1 kick, 2 snare, 3 hat
  SongRows   Data.l         how many rows the song has before it loops

usage: py -3 make_demo_assets.py   (writes demo_assets.n64 beside itself)
"""
import math, os

RATE = 22050                     # the sample rate the demo programs the AI for

# --- the font: 8x8, '#' a lit pixel ------------------------------------------
GLYPHS = {
" ": ["........"] * 8,
"!": ["...##...", "...##...", "...##...", "...##...", "...##...", "........", "...##...", "........"],
"'": ["...##...", "...##...", "..##....", "........", "........", "........", "........", "........"],
",": ["........", "........", "........", "........", "........", "...##...", "...##...", "..##...."],
"-": ["........", "........", "........", ".######.", "........", "........", "........", "........"],
".": ["........", "........", "........", "........", "........", "...##...", "...##...", "........"],
"/": [".....##.", "....##..", "...##...", "..##....", ".##.....", "##......", "........", "........"],
":": ["........", "...##...", "...##...", "........", "...##...", "...##...", "........", "........"],
"?": [".#####..", "##...##.", ".....##.", "...###..", "...##...", "........", "...##...", "........"],
"0": [".#####..", "##...##.", "##..###.", "##.####.", "####.##.", "###..##.", ".#####..", "........"],
"1": ["...##...", "..###...", ".####...", "...##...", "...##...", "...##...", ".######.", "........"],
"2": [".#####..", "##...##.", ".....##.", "...###..", ".###....", "##......", "#######.", "........"],
"3": [".#####..", "##...##.", ".....##.", "..####..", ".....##.", "##...##.", ".#####..", "........"],
"4": ["....###.", "...####.", "..##.##.", ".##..##.", "#######.", ".....##.", ".....##.", "........"],
"5": ["#######.", "##......", "######..", ".....##.", ".....##.", "##...##.", ".#####..", "........"],
"6": ["..####..", ".##.....", "##......", "######..", "##...##.", "##...##.", ".#####..", "........"],
"7": ["#######.", ".....##.", "....##..", "...##...", "..##....", "..##....", "..##....", "........"],
"8": [".#####..", "##...##.", "##...##.", ".#####..", "##...##.", "##...##.", ".#####..", "........"],
"9": [".#####..", "##...##.", "##...##.", ".######.", ".....##.", "....##..", ".####...", "........"],
"A": ["..###...", ".##.##..", "##...##.", "##...##.", "#######.", "##...##.", "##...##.", "........"],
"B": ["######..", "##...##.", "##...##.", "######..", "##...##.", "##...##.", "######..", "........"],
"C": [".#####..", "##...##.", "##......", "##......", "##......", "##...##.", ".#####..", "........"],
"D": ["#####...", "##..##..", "##...##.", "##...##.", "##...##.", "##..##..", "#####...", "........"],
"E": ["#######.", "##......", "##......", "#####...", "##......", "##......", "#######.", "........"],
"F": ["#######.", "##......", "##......", "#####...", "##......", "##......", "##......", "........"],
"G": [".#####..", "##...##.", "##......", "##.####.", "##...##.", "##...##.", ".######.", "........"],
"H": ["##...##.", "##...##.", "##...##.", "#######.", "##...##.", "##...##.", "##...##.", "........"],
"I": [".######.", "...##...", "...##...", "...##...", "...##...", "...##...", ".######.", "........"],
"J": ["....###.", ".....##.", ".....##.", ".....##.", "##...##.", "##...##.", ".#####..", "........"],
"K": ["##...##.", "##..##..", "##.##...", "####....", "##.##...", "##..##..", "##...##.", "........"],
"L": ["##......", "##......", "##......", "##......", "##......", "##......", "#######.", "........"],
"M": ["##...##.", "###.###.", "#######.", "##.#.##.", "##...##.", "##...##.", "##...##.", "........"],
"N": ["##...##.", "###..##.", "####.##.", "##.####.", "##..###.", "##...##.", "##...##.", "........"],
"O": [".#####..", "##...##.", "##...##.", "##...##.", "##...##.", "##...##.", ".#####..", "........"],
"P": ["######..", "##...##.", "##...##.", "######..", "##......", "##......", "##......", "........"],
"Q": [".#####..", "##...##.", "##...##.", "##...##.", "##.#.##.", "##..##..", ".###.##.", "........"],
"R": ["######..", "##...##.", "##...##.", "######..", "##.##...", "##..##..", "##...##.", "........"],
"S": [".#####..", "##...##.", "##......", ".#####..", ".....##.", "##...##.", ".#####..", "........"],
"T": [".######.", "...##...", "...##...", "...##...", "...##...", "...##...", "...##...", "........"],
"U": ["##...##.", "##...##.", "##...##.", "##...##.", "##...##.", "##...##.", ".#####..", "........"],
"V": ["##...##.", "##...##.", "##...##.", "##...##.", ".##.##..", "..###...", "...#....", "........"],
"W": ["##...##.", "##...##.", "##...##.", "##.#.##.", "#######.", "###.###.", "##...##.", "........"],
"X": ["##...##.", ".##.##..", "..###...", "..###...", "..###...", ".##.##..", "##...##.", "........"],
"Y": [".##..##.", ".##..##.", ".##..##.", "..####..", "...##...", "...##...", "...##...", "........"],
"Z": ["#######.", ".....##.", "....##..", "...##...", "..##....", ".##.....", "#######.", "........"],
}

def glyph_bytes(ch):
    rows = GLYPHS.get(ch, GLYPHS["?"])
    out = []
    for r in rows:
        v = 0
        for i, c in enumerate(r):
            if c == "#":
                v |= 0x80 >> i
        out.append(v)
    return out

# --- the tune: A minor, 120 beats a minute, four rows (sixteenths) a beat ----
# Bars of 16 rows. The chords: Am F C G | Am F G E, twice, with the melody's
# answer the second time round.
A3, C4, D4, E4, F4, G4, A4, B4, C5, D5, E5, F5, G5, A5 = 57, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81
CHORDS = {
    "Am": (45, [57, 60, 64]),     # bass A2; A C E
    "F":  (41, [53, 57, 60]),     # bass F2; F A C
    "C":  (48, [55, 60, 64]),     # bass C3; G C E (inverted)
    "G":  (43, [55, 59, 62]),     # bass G2; G B D
    "E":  (40, [56, 59, 64]),     # bass E2; G# B E
}
PROGRESSION = ["Am", "F", "C", "G", "Am", "F", "G", "E"] * 2
# the melody, a note a beat (four rows), 0 a rest; two eight-bar phrases
MELODY = [
    E5, 0, D5, C5,   A4, 0, C5, D5,   E5, G5, 0, E5,   D5, 0, B4, 0,
    C5, 0, E5, A5,   G5, 0, F5, E5,   D5, 0, E5, D5,   B4, 0, 0, 0,
    A5, 0, G5, E5,   F5, 0, E5, C5,   E5, 0, G5, C5,   B4, 0, D5, 0,
    C5, E5, A5, 0,   C5, D5, F5, 0,   D5, 0, B4, G4,   E4, 0, 0, 0,
]
ROWS = 16 * len(PROGRESSION)

def song():
    lead, arp, bass, drum = [0] * ROWS, [0] * ROWS, [0] * ROWS, [0] * ROWS
    for bar, name in enumerate(PROGRESSION):
        root, tones = CHORDS[name]
        for k in range(16):
            row = bar * 16 + k
            # the arpeggio: up and down the chord, an octave up every other beat
            seq = [tones[0], tones[1], tones[2], tones[1]]
            arp[row] = seq[k % 4] + (12 if (k // 4) % 2 else 0)
            # the bass: root on the beat, the octave on the off-beats, a push before the bar
            if k in (0, 6, 8, 14):
                bass[row] = root
            elif k in (3, 11):
                bass[row] = root + 12
            elif k == 15:
                bass[row] = root + 7
            # the drums: kick on 1 and 3 (and the push), snare on 2 and 4, hats between
            if k in (0, 8, 10):
                drum[row] = 1
            elif k in (4, 12):
                drum[row] = 2
            elif k % 2 == 1:
                drum[row] = 3
        # the melody: a note a beat; it starts in the second half
        for beat in range(4):
            idx = (bar % 16) * 4 + beat
            if bar >= 0 and idx < len(MELODY):
                lead[bar * 16 + beat * 4] = MELODY[idx]
    return lead, arp, bass, drum

def data_lines(kind, values, per=16):
    out = []
    for i in range(0, len(values), per):
        out.append("  Data.%s %s" % (kind, ", ".join(str(v) for v in values[i:i + per])))
    return out

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    L = ["; demo_assets.n64 - GENERATED by make_demo_assets.py; do not edit by hand.",
         "; The sine table, the 8x8 font, the oscillator steps and the song.",
         "#DEMO_RATE = %d" % RATE,
         "#SONG_ROWS = %d" % ROWS,
         "#ROW_SAMPLES = %d   ; a sixteenth at 120 beats a minute" % (RATE * 60 // (120 * 4)),
         "", "DataSection"]
    L.append("SinTab:")
    L += data_lines("w", [int(round(math.sin(2 * math.pi * i / 256) * 16384)) for i in range(256)])
    L.append("Font:")
    for code in range(32, 96):
        L.append("  Data.a %s   ; %r" % (", ".join(str(b) for b in glyph_bytes(chr(code))), chr(code)))
    L.append("NoteInc:")
    incs = []
    for n in range(96):
        f = 440.0 * 2 ** ((n - 69) / 12.0)
        incs.append(int(round(f * 4294967296.0 / RATE)))
    L += data_lines("l", incs, 8)
    lead, arp, bass, drum = song()
    for name, track in (("SongLead", lead), ("SongArp", arp), ("SongBass", bass), ("SongDrum", drum)):
        L.append(name + ":")
        L += data_lines("a", track, 16)
    L.append("ScrollText:")
    msg = ("      HELLO FROM PUREMETAL FORGE ON THE NINTENDO 64 ...  "
           "A 64-BIT VR4300 BACK END, ITS OWN ASSEMBLER AND ITS OWN BOOT CODE ...  "
           "FLAT SHADED 3D ON THE RDP, A FOUR VOICE SYNTH ON THE AI ...  "
           "NO NINTENDO CODE, NO LIBULTRA, NO GCC - JUST PUREMETAL ...  "
           "RUNNING ON THE N64 EMULATOR ...  GREETINGS TO EVERY EMULATOR ON THE BENCH ...      ")
    L += data_lines("a", [ord(c) for c in msg] + [0], 24)
    L.append("EndDataSection")
    open(os.path.join(here, "demo_assets.n64"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote demo_assets.n64: %d rows of song, %d glyphs" % (ROWS, 64))

main()
