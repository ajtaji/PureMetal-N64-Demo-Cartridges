# build.ps1 - builds the PureMetal N64 demo into PureMetalDemo.z64 (and raises its build number)
#   .\build.ps1 [-Forge <PureMetalForge.exe>]
param([string]$Forge = (Join-Path $PSScriptRoot "..\..\..\..\PureMetalForge.exe"))
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
# the build number: version.n64's #DEMO_BUILD, one more on every build (the version is on screen)
$vf = Join-Path $PSScriptRoot "version.n64"
$v = Get-Content $vf
$v = $v | ForEach-Object { if ($_ -match '^#DEMO_BUILD = (\d+)') { "#DEMO_BUILD = " + ([int]$Matches[1] + 1) } else { $_ } }
Set-Content -Path $vf -Value $v -Encoding ASCII
"build " + (($v | Select-String '^#DEMO_MAJOR = (\d+)').Matches[0].Groups[1].Value) + "." + (($v | Select-String '^#DEMO_MINOR = (\d+)').Matches[0].Groups[1].Value) + "." + (($v | Select-String '^#DEMO_BUILD = (\d+)').Matches[0].Groups[1].Value)
& $Forge --compile demo.n64 -o PureMetalDemo.bin
if ($LASTEXITCODE -ne 0) { throw "the demo did not compile" }
"built " + (Join-Path $PSScriptRoot "PureMetalDemo.z64")
