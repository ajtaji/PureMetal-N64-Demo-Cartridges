"""Build the N64 demo cartridges with PureMetal Forge.

    python build.py --forge path/to/PureMetalForge.exe [--output dist] [--demo NAME]

Needs PureMetal Forge (its VR4300/RSP back end) with LibPureMetal64, the system
library that ships with it: the sources include it by name
(Mips/Lib/LibPureMetalN64/...), found under the Forge installation (or under
PMF_ROOT if that is set). The fonts are made first by Forge's font tool
(tools/pmfont.py beside the compiler, or --font-tool), which needs Python 3 and
Pillow. Each cartridge is written beside its source; --output also copies it.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
CARTS = {
    "PureMetalDemo": ("demo.n64", "PureMetalDemo", (
        ("pmd_title", 44, ["FFFFFFFF"]), ("pmd_scroll", 22, ["FFFFFFFF"]),
        ("pmd_small", 11, ["FFFFFFFF"]))),
    "TrueTypeDemo": ("truetype_demo.n64", "TrueTypeDemo", (
        ("ttd_big", 40, ["FFD040FF"]), ("ttd_medium", 22, ["FFFFFFFF"]),
        ("ttd_small", 14, ["A8D8FFFF", "D0D0D0FF", "808898FF"]))),
    "WardensMarch": ("wardens_march.n64", "WardensMarchLive", (
        ("wm_title", 26, ["FFFFFFFF"]), ("wm_scroll", 24, ["FFFFFFFF"]),
        ("wm_hud", 10, ["FFDC5AFF", "DCDCDCFF", "FF6EE6FF", "6EDCFFFF", "FFFFFFFF"]))),
    "RspFuzz": ("rsp_fuzz.n64", "RspFuzz", (
        ("fuzz_title", 16, ["FFD250FF"]),
        ("fuzz_table", 12, ["C8C8DCFF", "78C8FFFF", "DCDCDCFF", "78FF8CFF",
                            "FF5050FF", "8C8CA0FF", "FFD250FF"]))),
}
SAVE_TYPES = {"RspFuzz": 0x30}         # SRAM 256 Kbit

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--forge", type=Path, required=True)
    parser.add_argument("--font-tool", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--demo", choices=CARTS, action="append")
    args = parser.parse_args()
    forge = args.forge.resolve(strict=True)
    font_tool = (args.font_tool or forge.parent / "tools" / "pmfont.py").resolve(strict=True)
    selected = args.demo or list(CARTS)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("PMF_ROOT", str(forge.parent))
    for name in selected:
        source, image, fonts = CARTS[name]
        cwd = ROOT / name
        for font, size, colours in fonts:
            styles = []
            for number, colour in enumerate(colours):
                styles += ["--style", f"{number}={colour}"]
            subprocess.run(
                [sys.executable, "-I", str(font_tool), "Lato-Regular.ttf",
                 f"{font}.pmft", "--size", str(size), "--range", "0x20-0x7E", *styles],
                cwd=cwd, check=True)
        subprocess.run(
            [str(forge), "--compile", source, "-o", f"{image}.bin"],
            cwd=cwd, env=env, check=True)
        rom = cwd / f"{image}.z64"
        if name in SAVE_TYPES:
            # the header's save type, as the SummerCart64 menu and sc64deployer read it ("ED" at $3C, the type at
            # $3F); the header is outside both checksums, so they stay valid
            with open(rom, "r+b") as f:
                f.seek(0x3C)
                f.write(b"ED")
                f.seek(0x3F)
                f.write(bytes([SAVE_TYPES[name]]))
        if args.output:
            shutil.copyfile(rom, args.output / rom.name)
        print(f"Built {rom}", flush=True)

if __name__ == "__main__":
    main()
