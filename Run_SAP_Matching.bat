@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  SAP GL/Bank Matching - double-click launcher
rem
rem  Layout expected (this .bat file lives at the top level):
rem    Manual Matching\
rem      Run_SAP_Matching.bat   <- this file
rem      engine\                <- the Python scripts
rem      <raw export>.xlsx      <- put exactly one raw export here
rem      output\                <- results land here (auto-created;
rem                                 safe to delete anytime to reset)
rem ============================================================

set "BASE=%~dp0"
set "ENGINE_DIR=%BASE%engine"
set "OUTPUT_DIR=%BASE%output"

echo Looking for a raw export .xlsx directly in:
echo   %BASE%
echo.

set "INPUT_FILE="
set "COUNT=0"
for %%F in ("%BASE%*.xlsx") do (
    set "INPUT_FILE=%%F"
    set /a COUNT+=1
)

if "%COUNT%"=="0" (
    echo No .xlsx file found in %BASE%
    echo Place the raw SAP export directly in this folder, next to this
    echo .bat file, then double-click it again.
    echo.
    pause
    exit /b 1
)

if not "%COUNT%"=="1" (
    echo Found more than one .xlsx file directly in %BASE% - not sure which
    echo one is the raw export:
    for %%F in ("%BASE%*.xlsx") do echo   %%F
    echo.
    echo Please keep only ONE raw export .xlsx directly in this folder
    echo ^(move old/output files elsewhere^), then try again.
    echo.
    pause
    exit /b 1
)

echo Using: %INPUT_FILE%
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo.
echo === Step 1/2: matching engine ===
echo This takes roughly 10-15 minutes. The window will look idle - that
echo is normal, it is working. Do not close this window.
echo.

python "%ENGINE_DIR%\match_workbook.py" ^
  --input "%INPUT_FILE%" ^
  --output "%OUTPUT_DIR%\matched.xlsx" ^
  --id-col "Matching ID" ^
  --secondary-id-col "Matching/Group ID" ^
  --engine-col "Matched By Engine" ^
  --engine-tag "Manual" ^
  --status-col "Match Status" ^
  --status-value "Matched" ^
  --prefix SAP ^
  --max-items 10 --date-window 15 --cap-entries 2000000

if errorlevel 1 (
    echo.
    echo *** Matching step failed - see the error above. ***
    echo.
    pause
    exit /b 1
)

echo.
echo === Step 2/2: analysis tab ===

python "%ENGINE_DIR%\build_analysis_tab.py" ^
  --input "%OUTPUT_DIR%\matched.xlsx" ^
  --output "%OUTPUT_DIR%\matched_analysis.xlsx" ^
  --bank-sheet Bank --source-label SAP

if errorlevel 1 (
    echo.
    echo *** Analysis tab step failed - see the error above. ***
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Done. Results are in:
echo    %OUTPUT_DIR%\matched_analysis.xlsx
echo ============================================================
echo.
pause
