<#
  install_shortcut.ps1 -- create a Start Menu (+ Desktop) shortcut that launches
  Storyboard Editor in Microsoft Edge as a standalone app window.

  After running: open Start, find the app, right-click, select Pin to taskbar.
  Usage:  powershell -ExecutionPolicy Bypass -File install_shortcut.ps1
          (add -NoDesktop to skip the desktop copy)
#>
param([switch]$NoDesktop)
$ErrorActionPreference = "Stop"

$AppName   = "Storyboard Editor"
$scripts   = $PSScriptRoot
$root      = Split-Path -Parent $scripts
$indexPath = Join-Path $root "index.html"

if (-not (Test-Path $indexPath)) {
    throw "index.html not found in project root: $root"
}

$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) {
    throw "Microsoft Edge executable not found at '$edge'"
}

$ico = Join-Path $scripts "storyboard_editor.ico"
if (-not (Test-Path $ico)) {
    throw "Icon file not found at '$ico'. Run make_icon.py first."
}
$iconLoc = "$ico,0"

$url = (New-Object System.Uri $indexPath).AbsoluteUri
$arguments = "--app=`"$url`""

$ws = New-Object -ComObject WScript.Shell
function New-Lnk($path) {
    $s = $ws.CreateShortcut($path)
    $s.TargetPath       = $edge
    $s.Arguments        = $arguments
    $s.WorkingDirectory = $root
    $s.IconLocation     = $iconLoc
    $s.Description      = "Storyboard Editor visual novel asset pipeline"
    $s.Save()
    "Created: $path"
}

# Windows caches shortcut icons by path, so an existing .lnk keeps showing the
# icon it was created with. Delete before recreating.
$startMenu = [Environment]::GetFolderPath('Programs')
$desktop   = [Environment]::GetFolderPath('Desktop')
$taskbar   = Join-Path $env:APPDATA "Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar"

$targets = @((Join-Path $startMenu "$AppName.lnk"))
if (-not $NoDesktop) { $targets += (Join-Path $desktop "$AppName.lnk") }
# A taskbar pin is its own .lnk and does not follow the Start Menu one.
$pinned = Join-Path $taskbar "$AppName.lnk"
if (Test-Path $pinned) { $targets += $pinned }

foreach ($t in $targets) {
    if (Test-Path $t) { Remove-Item $t -Force; "Removed stale: $t" }
}
foreach ($t in $targets) { New-Lnk $t }

# Force the Start Menu to re-render rather than serve its cached tile art.
try { Stop-Process -Name StartMenuExperienceHost -Force -ErrorAction SilentlyContinue } catch {}
""
"Done. Open Start, find '$AppName'. Right-click, select Pin to taskbar."
"Launcher: $edge $arguments"
