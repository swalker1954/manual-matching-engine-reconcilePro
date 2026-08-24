# Creates a "Manual Matching Process" shortcut on the current user's Desktop,
# pointing at the built executable (run build_exe.bat first).
#
# Usage (from the launcher folder, in PowerShell):
#   .\create_desktop_shortcut.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExePath = Join-Path $ScriptDir "dist\Manual Matching Process.exe"

if (-not (Test-Path $ExePath)) {
    Write-Error "Could not find '$ExePath'. Run build_exe.bat first to build the executable."
    exit 1
}

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Manual Matching Process.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = Split-Path $ExePath
$Shortcut.IconLocation = $ExePath
$Shortcut.Description = "Manual Matching Process"
$Shortcut.Save()

Write-Host "Desktop shortcut created: $ShortcutPath"
