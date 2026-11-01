; ======================================================================
;  export_song.pb - a Warden's Key song as DATA for the N64's own player
; ======================================================================
;  pbcompilerc export_song.pb /CONSOLE /EXE export_song.exe
;  export_song.exe <WardensKey folder> <song> <out.wkmu> [<reference.pcm> <seconds>]
;
;  The N64 synthesises the song itself, live (wk_player.n64, a PureMetal
;  port of the game's src/wk_music.pbi). This writes what that port reads:
;  the engine's own tables, computed BY the engine's own code (FmInit and
;  MuInit run here, unchanged, and their arrays are copied out - so the
;  console's tables are the game's, not a second derivation of them), the
;  instruments, and the song's order flattened into rows of note events.
;
;  With a reference path it also renders the first <seconds> with the game's
;  engine (16-bit stereo, big-endian, 48 kHz): the console's output is
;  compared against it, sample for sample.
;
;  THE FILE, big-endian, every section on 8 bytes:
;    header, 32 words: "WKMU", 1, tempo, speed, rows, loopRow, instruments,
;      vibratoTurns (the sine table's size), then the byte offsets of:
;      [8] FmSin [9] FmAmp [10] FmAttackK [11] FmDecayInc [12] MuCentQ
;      [13] MuNoteMip [14] MuTab [15] instruments [16] row index [17] events
;      [18] the vibrato sine [19] the file's length
;      [20..21] MuIncCents' C-1 increment x 65536, a 64-bit number
;      [22] the 512-step wavetables (7 x 8 x 512 x int16), for the RSP
;    FmSin, FmAmp      4096 x int16
;    FmAttackK, FmDecayInc  32 x int32
;    MuCentQ           1200 x int32
;    MuNoteMip         128 x byte
;    MuTab             7 x 8 x 2048 x int16   (the noise kind has no table)
;    instruments       64 x int32 each (#WKI_* below)
;    row index         rows + 1 x int32: each row's first event
;    events            8 bytes: channel, kind (1 note, 0 release only),
;                      instrument, note, velocity, 0, 0, 0
;    vibrato sine      16384 x int32, Sin x 2^30
; ======================================================================
EnableExplicit

CompilerIf Not Defined(WK_SRC, #PB_Constant)
  #WK_SRC = "C:/Embedded Compiler/WardensKey/src/"
CompilerEndIf
XIncludeFile #WK_SRC + "wk_fm.pbi"
XIncludeFile #WK_SRC + "wk_music.pbi"

#VIB_N = 16384

Procedure Fail(msg.s)
  PrintN("export_song: " + msg)
  End 1
EndProcedure

Global *out, outLen.i
Procedure Grow(n.i)
  If outLen + n > MemorySize(*out) : *out = ReAllocateMemory(*out, (outLen + n) * 2) : EndIf
EndProcedure
Procedure W32(v.q)
  Grow(4)
  PokeA(*out + outLen, (v >> 24) & 255) : PokeA(*out + outLen + 1, (v >> 16) & 255)
  PokeA(*out + outLen + 2, (v >> 8) & 255) : PokeA(*out + outLen + 3, v & 255)
  outLen + 4
EndProcedure
Procedure W16(v.i)
  Grow(2) : PokeA(*out + outLen, (v >> 8) & 255) : PokeA(*out + outLen + 1, v & 255) : outLen + 2
EndProcedure
Procedure W8(v.i)
  Grow(1) : PokeA(*out + outLen, v & 255) : outLen + 1
EndProcedure
Procedure Align8()
  While outLen & 7 : W8(0) : Wend
EndProcedure
Procedure Patch32(at.i, v.q)
  PokeA(*out + at, (v >> 24) & 255) : PokeA(*out + at + 1, (v >> 16) & 255)
  PokeA(*out + at + 2, (v >> 8) & 255) : PokeA(*out + at + 3, v & 255)
EndProcedure

OpenConsole()
If CountProgramParameters() <> 3 And CountProgramParameters() <> 5
  Fail("usage: export_song <WardensKey folder> <song> <out.wkmu> [<reference.pcm> <seconds>]")
EndIf
Define wk.s = ProgramParameter(0), song.s = LCase(ProgramParameter(1)), outPath.s = ProgramParameter(2)
If Right(wk, 1) <> "\" And Right(wk, 1) <> "/" : wk + "\" : EndIf
If MuLoadDir(wk + "music") = 0 : Fail(MuError) : EndIf
Define *s.MuSong = MuFindSong(song)
If *s = 0 : Fail("no song '" + song + "'") : EndIf
MuInit()                                    ; the engine's tables, by the engine (FmInit too)

*out = AllocateMemory(1 << 20)
Define i.i, j.i, k.i
For i = 0 To 31 : W32(0) : Next             ; the header, patched below

Patch32(32, outLen) : For i = 0 To 4095 : W16(FmSin(i)) : Next : Align8()
Patch32(36, outLen) : For i = 0 To 4095 : W16(FmAmp(i)) : Next : Align8()
Patch32(40, outLen) : For i = 0 To 31 : W32(FmAttackK(i)) : Next
Patch32(44, outLen) : For i = 0 To 31 : W32(FmDecayInc(i)) : Next
Patch32(48, outLen) : For i = 0 To 1199 : W32(MuCentQ(i)) : Next
Patch32(52, outLen) : For i = 0 To 127 : W8(MuNoteMip(i)) : Next : Align8()
Patch32(56, outLen) : For i = 0 To 7 * #MU_MIPS * #MU_TABLE - 1 : W16(MuTab(i)) : Next : Align8()

; the instruments, in the song's order
Patch32(60, outLen)
Define nIns.i = 0, o.i, vibInc.q
ForEach *s\ins()
  W32(*s\ins()\fm) : W32(*s\ins()\wave)
  W32(*s\ins()\a) : W32(*s\ins()\d) : W32(*s\ins()\s) : W32(*s\ins()\r)
  W32(*s\ins()\vol) : W32(*s\ins()\send)
  W32(*s\ins()\sweep) : W32(*s\ins()\sweepMs)
  W32(*s\ins()\vib) : W32(*s\ins()\vibDelay)
  vibInc = Round(*s\ins()\vibHz * 4294967296.0 / #FM_RATE, #PB_Round_Nearest)
  W32(vibInc)
  W32(*s\ins()\alg) : W32(*s\ins()\fb)
  W32(MuPanGain(*s\ins()\pan, 0)) : W32(MuPanGain(*s\ins()\pan, 1))
  For o = 0 To 3
    W32(*s\ins()\op[o]\mul) : W32(*s\ins()\op[o]\dt) : W32(*s\ins()\op[o]\tl) : W32(*s\ins()\op[o]\ar)
    W32(*s\ins()\op[o]\dr) : W32(*s\ins()\op[o]\sl) : W32(*s\ins()\op[o]\sr) : W32(*s\ins()\op[o]\rr)
  Next
  ; THE ENVELOPES 32 SAMPLES AT A TIME, for the RSP synth (wk_rsp.n64), which
  ; steps them at the engine's own pitch cadence. Each is the engine's
  ; per-sample recurrence taken 32 times in closed form (Q16 factors):
  ;   decay    lev' = tgt + (lev - tgt) x (1 - 4/D)^32                    49
  ;   release  lev' = lev x (1 - 4/R)^32 - (1 - (1 - 4/R)^32) / (4/R)     50, 51
  ;   attack   att' = att x (1 - K)^32 - 32 x (1 - (1 - K)^32) / K        52 + 2 op, 53 + 2 op
  Define fD.d, fR.d, kA.d
  fD = 0 : If *s\ins()\d > 0 : fD = Pow(1 - 4.0 / (*s\ins()\d * 48), 32) : EndIf
  W32(Round(fD * 65536, #PB_Round_Nearest))
  fR = 0 : If *s\ins()\r > 0 : fR = Pow(1 - 4.0 / (*s\ins()\r * 48), 32) : EndIf
  W32(Round(fR * 65536, #PB_Round_Nearest))
  If *s\ins()\r > 0 : W32(Round((1 - fR) / (4.0 / (*s\ins()\r * 48)), #PB_Round_Nearest)) : Else : W32(0) : EndIf
  For o = 0 To 3
    kA = FmAttackK(*s\ins()\op[o]\ar) / 65536.0
    W32(Round(Pow(1 - kA, 32) * 65536, #PB_Round_Nearest))
    If *s\ins()\op[o]\ar = 0
      W32(0)
    ElseIf kA > 0
      W32(Round(32 * (1 - Pow(1 - kA, 32)) / kA, #PB_Round_Nearest))
    Else
      W32(32 * 32)
    EndIf
  Next
  For j = 1 To 64 - 60 : W32(0) : Next      ; 60 fields, padded to 64
  nIns + 1
Next

; the rows: the order flattened, each channel's token as events
Structure Ev : chan.i : kind.i : ins.i : note.i : vel.i : EndStructure
Global NewList evs.Ev()
Define NewList rowStart.i(), rows.i = 0, loopRow.i = -1, oi.i = 0, *p.MuPattern, r.i, ci.i, tok.s, n.i, part.s, vel.i, note.i, insIdx.i, kitItem.s, name.s, idx.i
ForEach *s\order()
  If oi = *s\loopAt : loopRow = rows : EndIf
  SelectElement(*s\pats(), *s\order()) : *p = @*s\pats()
  For r = 0 To *p\rows - 1
    AddElement(rowStart()) : rowStart() = ListSize(evs())
    ci = 0
    ForEach *s\chans()
      If FindMapElement(*p\cells(), *s\chans()\name + ":" + Str(r))
        tok = *p\cells()
        If tok <> "" And tok <> "."
          AddElement(evs()) : evs()\chan = ci : evs()\kind = 0          ; the channel's notes released
          If tok <> "-"
            n = CountString(tok, "+") + 1
            For k = 1 To n
              part = StringField(tok, k, "+") : vel = 100
              If FindString(part, ":") : vel = Val(StringField(part, 2, ":")) : part = StringField(part, 1, ":") : EndIf
              note = -1 : insIdx = -1
              If *s\chans()\kit <> ""
                For j = 1 To CountString(*s\chans()\kit, ",") + 1
                  kitItem = StringField(*s\chans()\kit, j, ",")
                  If StringField(kitItem, 1, "=") = part
                    name = StringField(StringField(kitItem, 2, "="), 1, ":")
                    idx = 0 : ForEach *s\ins() : If *s\ins()\name = name : insIdx = idx : EndIf : idx + 1 : Next
                    note = Val(StringField(StringField(kitItem, 2, "="), 2, ":"))
                  EndIf
                Next
              Else
                note = MuNoteNum(part)
                idx = 0 : ForEach *s\ins() : If @*s\ins() = *s\chans()\ins : insIdx = idx : EndIf : idx + 1 : Next
              EndIf
              If note >= 0 And insIdx >= 0
                AddElement(evs()) : evs()\chan = ci : evs()\kind = 1 : evs()\ins = insIdx : evs()\note = note : evs()\vel = vel
              EndIf
            Next
          EndIf
        EndIf
      EndIf
      ci + 1
    Next
    rows + 1
  Next
  oi + 1
Next
If loopRow < 0 : Fail("the song does not loop") : EndIf
If ListSize(*s\chans()) > 16 : Fail("more than 16 channels") : EndIf

Patch32(64, outLen) : ForEach rowStart() : W32(rowStart()) : Next : W32(ListSize(evs()))
Patch32(68, outLen)
ForEach evs() : W8(evs()\chan) : W8(evs()\kind) : W8(evs()\ins) : W8(evs()\note) : W8(evs()\vel) : W8(0) : W8(0) : W8(0) : Next
Align8()
Patch32(72, outLen) : For i = 0 To #VIB_N - 1 : W32(Round(Sin(2 * #PI * i / #VIB_N) * 1073741824.0, #PB_Round_Nearest)) : Next
; THE WAVETABLES AT 512 STEPS, for the RSP (a table in its 4 KB data memory
; costs a quarter of what the engine's 2048 do). Every 4th sample of the
; engine's own table: each table is band-limited to at most 200 harmonics,
; below the 256 that 512 points carry, so nothing of its content is lost.
Patch32(88, outLen) : For i = 0 To (7 * #MU_MIPS * 512) - 1 : W16(MuTab((i / 512) * #MU_TABLE + (i % 512) * 4)) : Next : Align8()
Patch32(76, outLen + 0)

PokeA(*out, 'W') : PokeA(*out + 1, 'K') : PokeA(*out + 2, 'M') : PokeA(*out + 3, 'U')
Patch32(4, 1) : Patch32(8, *s\tempo) : Patch32(12, *s\speed) : Patch32(16, rows) : Patch32(20, loopRow)
Patch32(24, nIns) : Patch32(28, #VIB_N)
; MuIncCents' starting value, C-1's increment x 65536, made here by the same
; expression the engine evaluates (a double rounded into a quad by the host
; compiler), so the console starts from the engine's exact number
Define incC1.q = (8.1757989156 * 4294967296.0 / #FM_RATE) * 65536
Patch32(80, incC1 >> 32) : Patch32(84, incC1 & $FFFFFFFF)
Define f.i = CreateFile(#PB_Any, outPath)
If f = 0 : Fail("cannot write " + outPath) : EndIf
WriteData(f, *out, outLen) : CloseFile(f)
PrintN("wrote " + outPath + ": " + Str(nIns) + " instruments, " + Str(rows) + " rows (loop to " + Str(loopRow) + "), " + Str(ListSize(evs())) + " events, " + Str(ListSize(*s\chans())) + " channels, " + Str(outLen) + " bytes")

; the reference: the game's engine, the first <seconds>
If CountProgramParameters() = 5
  Define secs.i = Val(ProgramParameter(4)), total.i = 48000 * secs, done.i = 0, v.i
  ; 1600 frames a call, as the console renders: MuRender stamps each voice's
  ; age with its sample counter, which advances a call at a time, so voice
  ; stealing compares the same numbers only when the calls are the same size
  Define *mix = AllocateMemory(1600 * 8), *pcm = AllocateMemory(total * 4)
  MuVoicesReset() : MuReverbReset() : MuPlay(song)
  While done < total
    n = 1600 : If total - done < n : n = total - done : EndIf
    FillMemory(*mix, n * 8, 0) : MuRender(*mix, n)
    For i = 0 To n * 2 - 1
      v = PeekL(*mix + i * 4)
      If v > 32767 : v = 32767 : ElseIf v < -32768 : v = -32768 : EndIf
      PokeA(*pcm + (done * 2 + i) * 2, (v >> 8) & 255) : PokeA(*pcm + (done * 2 + i) * 2 + 1, v & 255)
    Next
    done + n
  Wend
  f = CreateFile(#PB_Any, ProgramParameter(3))
  WriteData(f, *pcm, total * 4) : CloseFile(f)
  PrintN("wrote the reference " + ProgramParameter(3) + ": " + Str(secs) + " s by the game's engine; peak voices " + Str(MuVoicePeak))
EndIf
