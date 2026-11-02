# build.ps1 - builds the PureMetal N64 demo into PureMetalDemo.z64 (and raises its build number)
#   .\build.ps1 [-Forge <PureMetalForge.exe>]
param([string]$Forge = "")
$ErrorActionPreference = "Stop"
# PureMetal Forge: as given, or beside the compiler's own examples, or on the PATH
if ($Forge -eq "") {
  $beside = Join-Path $PSScriptRoot "..\..\..\..\PureMetalForge.exe"
  if (Test-Path $beside) { $Forge = $beside }
  elseif (Get-Command PureMetalForge.exe -ErrorAction SilentlyContinue) { $Forge = (Get-Command PureMetalForge.exe).Source }
  else { throw "PureMetalForge.exe was not found: put it on the PATH or pass -Forge <path>" }
}
Set-Location $PSScriptRoot
# the build number (version.n64's #DEMO_BUILD, on screen) is the compiler's: one more on every build, in the IDE too
# (Forge is a windowed program: PowerShell does not wait for it or see its exit code
# unless started this way)
$fp = Start-Process -FilePath $Forge -ArgumentList '--compile','demo.n64','-o','PureMetalDemo.bin' -NoNewWindow -Wait -PassThru
if ($fp.ExitCode -ne 0) { throw "the demo did not compile" }
"built " + (Join-Path $PSScriptRoot "PureMetalDemo.z64")
