@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  SAP GL/Bank Matching - double-click launcher
rem
rem  The engine code (this .bat, engine\) lives on the Desktop.
rem  The DATA lives elsewhere, organized by period:
rem
rem    ReconcilePro\Operating_files\Periods\<period>\
rem      raw\Manual Matching\<raw export>.xlsx   <- input
rem      raw\Manual Matching\output\              <- results land here
rem                                                   (auto-created; safe
rem                                                    to delete to reset)
rem ============================================================

set "ENGINE_DIR=%~dp0engine"
set "DATA_ROOT=C:\users\swalk\documents\ReconcilePro\Operating_files\Periods"

echo ============================================================
echo  SAP GL/Bank Matching
echo ============================================================
echo.
set /p PERIOD=Enter the period folder to run (e.g. 2025-12):

if "%PERIOD%"=="" (
    echo No period entered - stopping.
    echo.
    pause
    exit /b 1
)

set "PERIOD_DIR=%DATA_ROOT%\%PERIOD%"
set "RAW_DIR=%PERIOD_DIR%\raw\Manual Matching"
set "OUTPUT_DIR=%RAW_DIR%\output"

if not exist "%PERIOD_DIR%" (
    echo Period folder not found:
    echo   %PERIOD_DIR%
    echo Check the spelling ^(e.g. 2025-12^) and try again.
    echo.
    pause
    exit /b 1
)

if not exist "%RAW_DIR%" (
    echo Raw data folder not found:
    echo   %RAW_DIR%
    echo.
    pause
    exit /b 1
)

echo.
echo Looking for a raw export .xlsx directly in:
echo   %RAW_DIR%
echo.

set "INPUT_FILE="
set "COUNT=0"
for %%F in ("%RAW_DIR%\*.xlsx") do (
    set "INPUT_FILE=%%F"
    set /a COUNT+=1
)

if "%COUNT%"=="0" (
    echo No .xlsx file found in %RAW_DIR%
    echo Place the raw SAP export there, then try again.
    echo.
    pause
    exit /b 1
)

if not "%COUNT%"=="1" (
    echo Found more than one .xlsx file in %RAW_DIR% - not sure which
    echo one is the raw export:
    for %%F in ("%RAW_DIR%\*.xlsx") do echo   %%F
    echo.
    echo Please keep only ONE raw export .xlsx in that folder
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
echo  Done. Opening in Excel:
echo    %OUTPUT_DIR%\matched_analysis.xlsx
echo ============================================================
echo.

start "" "%OUTPUT_DIR%\matched_analysis.xlsx"

pause
