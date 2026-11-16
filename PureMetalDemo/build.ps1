# build.ps1 - builds PureMetalDemo.z64 (and raises its build number)
#   .\build.ps1 [-Forge <PureMetalForge.exe>]
param([string]$Forge = "")
$ErrorActionPreference = "Stop"
# PureMetal Forge: as given, or on the PATH
if ($Forge -eq "") {
  if (Get-Command PureMetalForge.exe -ErrorAction SilentlyContinue) { $Forge = (Get-Command PureMetalForge.exe).Source }
  else { throw "PureMetalForge.exe was not found: put it on the PATH or pass -Forge <path>" }
}
Set-Location $PSScriptRoot
python (Join-Path $PSScriptRoot "..\build.py") --forge $Forge --demo PureMetalDemo
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
