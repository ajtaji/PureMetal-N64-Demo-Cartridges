#!/usr/bin/env python3
"""rspfuzz_diff.py - two logs of the RSP fuzz cartridge (RspFuzz.z64) compared case by case.

  rspfuzz_diff.py <reference log> <other log> [--show N]

A log is any text holding the cartridge's ISViewer lines - a console's (SummerCart64 / 64drive USB output), an
emulator's --test report, ares' stdout: the lines "C oo e v c <128 bytes in, hex> <128 bytes out, hex>" are read
and the rest ignored. The reference is normally the console's.

For each opcode it prints how many cases agree, and for those that do not, which parts differ: the accumulator
read before the instruction (it should always agree - if not, the setup itself differs), vd, the accumulator after
(high, middle, low), VCO VCC VCE. --show N prints N differing cases in full, lane by lane.

A case's input (32 words): vs, vt, vd before, A, B, C, D (the accumulator set by vmudh A, B; vmadn C, D), then
VCO VCC (one word) and VCE (the next word's high half). Its record (32 words): accumulator high, middle, low before,
vd after, accumulator high, middle, low after, then VCO VCC VCE as halves.
"""
import sys

NAMES = {16: "VADD", 0: "VMULF", 18: "VSUT", 22: "VADDB", 23: "VSUBB", 24: "VACCB", 25: "VSUCB", 26: "VSAD",
         27: "VSAC", 28: "VSUM", 30: "V30", 31: "V31", 46: "V46", 47: "V47", 55: "VNOP", 56: "VEXTT", 57: "VEXTQ",
         58: "VEXTN", 59: "V59", 60: "VINST", 61: "VINSQ", 62: "VINSN", 63: "VNULL"}
ORDER = [16, 0, 18, 22, 23, 24, 25, 26, 27, 28, 30, 31, 46, 47, 55, 56, 57, 58, 59, 60, 61, 62, 63]
PARTS = [("acc before", 0, 48), ("vd", 48, 64), ("acc high", 64, 80), ("acc mid", 80, 96), ("acc low", 96, 112),
         ("flags", 112, 118)]


def read(path):
    cases = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        f = line.strip().split()
        if len(f) == 7 and f[0] == "C" and len(f[5]) == 256 and len(f[6]) == 256:
            cases[(int(f[1], 16), int(f[2], 16), int(f[3], 16), int(f[4], 16))] = (bytes.fromhex(f[5]), bytes.fromhex(f[6]))
    return cases


def lanes(b):
    return " ".join(b[i:i + 2].hex().upper() for i in range(0, len(b), 2))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    show = int(sys.argv[sys.argv.index("--show") + 1]) if "--show" in sys.argv else 0
    ref, oth = read(sys.argv[1]), read(sys.argv[2])
    print(f"{len(ref)} cases in the reference, {len(oth)} in the other")
    shown, bad = 0, 0
    for op in range(len(ORDER)):
        keys = sorted(k for k in ref if k[0] == op)
        if not keys:
            continue
        same, diff, parts = 0, 0, {}
        for k in keys:
            if k not in oth:
                continue
            a, b = ref[k][1], oth[k][1]
            if ref[k][0] != oth[k][0]:
                print(f"  {k}: the INPUTS differ - not the same cartridge build?")
            if a == b:
                same += 1
                continue
            diff += 1
            for name, lo, hi in PARTS:
                if a[lo:hi] != b[lo:hi]:
                    parts[name] = parts.get(name, 0) + 1
            if shown < show:
                shown += 1
                i = ref[k][0]
                print(f"--- {NAMES[ORDER[op]]} e={k[1]} variant={k[2]} case={k[3]}")
                print(f"    vs      {lanes(i[0:16])}\n    vt      {lanes(i[16:32])}\n    vd old  {lanes(i[32:48])}")
                for name, lo, hi in PARTS:
                    mark = "  " if a[lo:hi] == b[lo:hi] else "!="
                    print(f" {mark} {name:9} ref {lanes(a[lo:hi])}")
                    if a[lo:hi] != b[lo:hi]:
                        print(f"    {'':9} oth {lanes(b[lo:hi])}")
        bad += diff
        what = ", ".join(f"{n} {c}" for n, c in parts.items())
        print(f"{NAMES[ORDER[op]]:6} (funct {ORDER[op]:2}): {same:3} the same, {diff:3} differ{'  [' + what + ']' if what else ''}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
