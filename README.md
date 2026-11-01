# PureMetal N64 Demo Cartridges

Nintendo 64 demos written in **PureMetal** and compiled by **PureMetal Forge**'s
VR4300 back end - its own boot code (IPL3), no SDK, no libultra.

## The cartridges (`cartridges/`)

| Cartridge | What it is |
|---|---|
| `PureMetalDemo.z64` | The first PureMetal N64 demo: copper bars, a three-speed starfield, a flat-shaded cube and an octahedron going round it, a colour-cycling title, a sine scroller and a four-voice synthesiser (pulse lead, saw arpeggio, square bass, drums) playing an original tune. |
| `WardensMarchLive.z64` | *The Warden's March*: copper bars, a Gouraud-lit torus, a starfield and a sine scroller at 60 frames a second over the main theme of Warden's Key, played live - the sequencer and envelopes on the VR4300, every sample (FM, wavetables, noise, reverb, 48 kHz) on the RSP, which also turns, lights, sorts and sets up the torus's triangles between pieces of music. An on-screen panel names what is heard and what is drawn. |

Both are big-endian `.z64` images with a 6102-compatible checksum; they run on
the PureMetal N64 emulator and should run on any N64 emulator that boots a
cartridge's own IPL3.

## The source

`PureMetalDemo/` holds everything needed to build the first demo in the
PureMetal Forge IDE. The source of *The Warden's March* will follow.
