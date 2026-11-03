# build.ps1 - builds the TrueType demo into TrueTypeDemo.z64 (and raises its build number)
#   .\build.ps1 [-Forge <PureMetalForge.exe>]
param([string]$Forge = (Join-Path $PSScriptRoot "..\..\..\..\PureMetalForge.exe"))
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
# the build number (version.n64's #DEMO_BUILD, on screen) is the compiler's: one more on every build, in the IDE too
# (Forge is a windowed program: PowerShell does not wait for it or see its exit code
# unless started this way)
$fp = Start-Process -FilePath $Forge -ArgumentList '--compile','truetype_demo.n64','-o','TrueTypeDemo.bin' -NoNewWindow -Wait -PassThru
if ($fp.ExitCode -ne 0) { throw "the demo did not compile" }
"built " + (Join-Path $PSScriptRoot "TrueTypeDemo.z64")
