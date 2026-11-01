# build.ps1 - builds THE WARDEN'S MARCH, the Nintendo 64 demo, into WardensMarch.z64
#
#   .\build.ps1 [-WardensKey <folder>] [-Forge <PureMetalForge.exe>]
#
# 1. the song: export_song.pb, compiled with the host compiler, writes the Warden's Key
#    main theme as data - the game's own tables, instruments and note rows - into
#    theme.wkmu, which the N64 plays live (wk_rsp.n64 + wk_synth.rsp). Not kept in git:
#    rebuilt from the Warden's Key repository when that is present, else used as committed
# 2. the tables: make_assets.py -> wardens_assets.n64 (kept in git; rerun after editing it)
# 3. the cartridge: PureMetal Forge, headless, -> WardensMarch.bin and WardensMarch.z64
param(
  [string]$WardensKey = "C:\Embedded Compiler\WardensKey",
  [string]$Forge = "",
  [string]$HostCompiler = "C:\Users\rajta\AppData\Local\Programs\PureBasic\Compilers\pbcompilerc.exe"
)
$ErrorActionPreference = "Stop"
# PureMetal Forge: as given, or beside the compiler's own examples, or on the PATH
if ($Forge -eq "") {
  $beside = Join-Path $PSScriptRoot "..\..\..\..\PureMetalForge.exe"
  if (Test-Path $beside) { $Forge = $beside }
  elseif (Get-Command PureMetalForge.exe -ErrorAction SilentlyContinue) { $Forge = (Get-Command PureMetalForge.exe).Source }
  else { throw "PureMetalForge.exe was not found: put it on the PATH or pass -Forge <path>" }
}
Set-Location $PSScriptRoot
# the build number: version.n64's #DEMO_BUILD, one more on every build (the version is on screen)
$vf = Join-Path $PSScriptRoot "version.n64"
$v = Get-Content $vf
$v = $v | ForEach-Object { if ($_ -match '^#DEMO_BUILD = (\d+)') { "#DEMO_BUILD = " + ([int]$Matches[1] + 1) } else { $_ } }
Set-Content -Path $vf -Value $v -Encoding ASCII
"build " + (($v | Select-String '^#DEMO_MAJOR = (\d+)').Matches[0].Groups[1].Value) + "." + (($v | Select-String '^#DEMO_MINOR = (\d+)').Matches[0].Groups[1].Value) + "." + (($v | Select-String '^#DEMO_BUILD = (\d+)').Matches[0].Groups[1].Value)
# the song: exported from the Warden's Key game's own repository when it is here (the
# developer's machine); everyone else builds with the theme.wkmu in this folder
if ((Test-Path $WardensKey) -and (Test-Path $HostCompiler)) {
  & $HostCompiler "export_song.pb" /CONSOLE /EXE "export_song.exe" | Select-Object -Last 2
  if ($LASTEXITCODE -ne 0) { throw "export_song.pb did not build" }
  & .\export_song.exe $WardensKey theme theme.wkmu
  if ($LASTEXITCODE -ne 0) { throw "the song did not export" }
} else {
  "the song: theme.wkmu as committed (the Warden's Key repository is not here)"
}
& python make_assets.py
if ($LASTEXITCODE -ne 0) { throw "make_assets.py failed" }
# (Forge is a windowed program: PowerShell does not wait for it or see its exit code
# unless started this way)
$fp = Start-Process -FilePath $Forge -ArgumentList '--compile','wardens_march.n64','-o','WardensMarch.bin' -NoNewWindow -Wait -PassThru
if ($fp.ExitCode -ne 0) { throw "the demo did not compile" }
"built " + (Join-Path $PSScriptRoot "WardensMarch.z64")
