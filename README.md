# PureMetal N64 Demo Cartridges

**Nintendo 64 homebrew demos written in PureMetal** - a BASIC-style language -
and compiled by **[PureMetal Forge](https://puremetalforge.ajtaji.com)**, an IDE
and compiler that builds straight to N64 machine code with its own boot code
(IPL3): no SDK, no libultra, no C.

![The Warden's March](screenshots/wardens-march-2.png)

## The cartridges

Ready to play: download them from [`cartridges/`](cartridges) or from the
[Releases](../../releases) page.

| Cartridge | |
|---|---|
| [`PureMetalDemo.z64`](cartridges/PureMetalDemo.z64) | **PureMetal Demo** - the first PureMetal N64 demo. Copper bars, a three-speed starfield, a flat-shaded cube with an octahedron going round it, a colour-cycling title, a sine scroller, and a four-voice synthesiser (pulse lead, saw arpeggio, square bass, drums) playing an original tune - all on the VR4300 CPU, drawn by the RDP. |
| [`WardensMarchLive.z64`](cartridges/WardensMarchLive.z64) | **The Warden's March** - 60 frames a second: copper bars, a Gouraud-lit torus, a starfield and a sine scroller over the main theme of *Warden's Key*, played **live** - the game's sequencer and envelopes on the VR4300, every sample (4-operator FM, wavetables, noise, reverb, 48 kHz, up to 32 voices) on the **RSP**'s vector unit, which also turns, lights, sorts and sets up the torus's triangles between pieces of music. A panel names what you are hearing and what is being drawn. |

<p>
<img src="screenshots/puremetal-demo-1.png" width="320" alt="PureMetal Demo">
<img src="screenshots/puremetal-demo-2.png" width="320" alt="PureMetal Demo">
<img src="screenshots/wardens-march-1.png" width="320" alt="The Warden's March">
</p>

### Playing them

They are standard big-endian `.z64` images (2-3 MB) with a 6102-compatible
checksum and their own IPL3. Load one in an N64 emulator the way you load any
`.z64`.

- **Tested on:** the PureMetal N64 emulator (the one these demos were developed
  on), 60 frames a second, sound at 48 kHz; and **ares v148** (paraLLEl-RDP),
  which boots them like a console would: through their own boot code.
- **Not yet tested on:** real hardware (a flash cartridge such as an EverDrive
  or SummerCart64). The boot block is signed for the 6102 CIC and initialises
  RDRAM, the caches and the PIF itself, as a console needs, so it should run;
  reports are welcome in [Issues](../../issues).
- **The boot code is the compiler's own**, in two stages, no Nintendo code: a
  signed first stage that never changes and a second stage in the cartridge.
- **The version is on screen**, bottom right (`V1.1.n`, `n` the build number,
  raised by `build.ps1` on every build).

## Building them yourself

You need **PureMetal Forge** - from the **Microsoft Store** (search for
"PureMetal Forge") or from **[puremetalforge.ajtaji.com](https://puremetalforge.ajtaji.com)** -
with its Nintendo 64 back end (the VR4300, and the RSP for *The Warden's
March*), and **Python 3** only if you change a demo's tables.

### In the IDE

1. Download or clone this repository:
   `git clone https://github.com/ajtaji/PureMetal-N64-Demo-Cartridges.git`
2. Start PureMetal Forge and open the demo with **File > Open...**:
   `PureMetalDemo/demo.n64`.
3. The `.n64` extension selects the target. Check the **Board** menu reads
   **Game consoles > Nintendo 64 (NTSC, 4 MB RDRAM)**.
4. **Compiler > Compile.** The Compiler Log ends with the assembler's success
   line, and the cartridge is written beside the source:
   `PureMetalDemo/demo.z64` (with `demo.bin`, the raw image, and `demo.bin.sym`,
   its symbols).
5. Run `demo.z64` in an emulator.

### From the command line

    cd PureMetalDemo
    PureMetalForge.exe --compile demo.n64 -o demo.bin

writes `demo.bin` and `demo.z64` the same way, without opening the IDE.
`PureMetalDemouild.ps1` does that and raises the build number in
`version.n64` first (the version the demo shows bottom right).

### Changing the tables

Everything the demo reads - the sine table, the 5x7 font, the note steps, the
tune and the scroller's message - is in `demo_assets.n64`, written by
`make_demo_assets.py`. Edit the Python (the song is a list of rows, the
message a string), then

    python make_demo_assets.py

and compile again.

### What is in each demo's folder

| `PureMetalDemo/` | |
|---|---|
| `demo.n64` | the demo, in PureMetal |
| `demo_assets.n64` | its tables, generated - do not edit by hand |
| `make_demo_assets.py` | the generator of `demo_assets.n64` |

The program starts with `XIncludeFile "Mips/Lib/n64.n64"`: the Nintendo 64
library that comes with PureMetal Forge (video and the RDP, audio, the
cartridge, the RSP), so nothing else is needed.

The cartridges in `cartridges/` were built by earlier versions of the
compiler; a build from this source today gives the same demo, not
byte-for-byte the same file.

*The Warden's March*'s source - the PureMetal player of the Warden's Key music
engine, its RSP synthesiser and the torus microcode - will be added here.

## How they work

- **The CPU (VR4300)** runs the PureMetal program: MIPS III, 64-bit registers,
  compiled by Forge's VR4300 back end.
- **The RDP** draws everything: fill rectangles for the copper bars, stars and
  text, shaded triangles for the torus and the sky. Each frame's command list is
  built while the RDP draws the previous one.
- **The AI** plays 16-bit stereo at 48 kHz from buffers the program keeps full.
- **The RSP** (in *The Warden's March*) is shared between two microcode
  programs - the music synthesiser and the torus - each put back on the RSP
  when it is its turn, with the music's state saved in between.

## License

MIT - see [LICENSE](LICENSE).
