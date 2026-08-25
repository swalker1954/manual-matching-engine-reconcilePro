# Run the full SAP GL/Bank matching pipeline: match_workbook.py then
# build_analysis_tab.py, chained, with the SAP defaults validated on the
# December 2025 data (Matching ID as primary code column, Matching/Group ID
# mirrored, Match Status flipped to Matched, date window 15, max 10 items).
#
# Usage (from PowerShell):
#   .\run_sap.ps1 <input.xlsx> <prefix> <period> [output_dir]
#
# Example:
#   .\run_sap.ps1 ..\workspace\ReconcilePro_Matching_202512.xlsx SAP 2025-12 ..\workspace\output
#
# If PowerShell blocks the script with an "execution policy" error, run
# this once first (in an admin PowerShell, or just for your user):
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

param(
    [Parameter(Mandatory=$true)][string]$InputFile,
    [Parameter(Mandatory=$true)][string]$Prefix,
    [Parameter(Mandatory=$true)][string]$Period,
    [string]$OutDir = $null
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $InputFile)) {
    Write-Error "Input file not found: $InputFile"
    exit 1
}

if (-not $OutDir) {
    $OutDir = Split-Path -Parent (Resolve-Path $InputFile)
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseName = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
$Final = Join-Path $OutDir "$($BaseName)_Matched.xlsx"

Write-Host "=== Step 1/2: matching engine ===" -ForegroundColor Cyan
python "$ScriptDir\match_workbook.py" `
  --input "$InputFile" `
  --output "$Final" `
  --gl-filter-col "Source" --gl-filter-value "SAP" `
  --id-col "Matching ID" `
  --secondary-id-col "Matching/Group ID" `
  --engine-col "Matched By Engine" `
  --engine-tag "Manual" `
  --status-col "Match Status" `
  --status-value "Matched" `
  --prefix "$Prefix" --period "$Period" `
  --max-items 10 --date-window 15 --cap-entries 2000000

if ($LASTEXITCODE -ne 0) {
    Write-Error "Matching step failed (exit code $LASTEXITCODE)"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "=== Step 2/2: analysis tab ===" -ForegroundColor Cyan
python "$ScriptDir\build_analysis_tab.py" `
  --input "$Final" `
  --output "$Final" `
  --bank-sheet Bank --source-label "$Prefix"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Analysis tab step failed (exit code $LASTEXITCODE)"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Done: $Final" -ForegroundColor Green
