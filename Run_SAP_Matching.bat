@echo off
setlocal enabledelayedexpansion

rem ============================================================
rem  GL/Bank Matching - double-click launcher
rem
rem  The engine code (this .bat, engine\) lives on the Desktop.
rem  The DATA lives elsewhere, organized by period, with one raw export
rem  per engine sitting side by side in the same folder:
rem
rem    ReconcilePro\Operating_files\Periods\<period>\
rem      raw\Manual Matching\<Engine>_<period>_MM.xlsx   <- one per engine
rem      raw\Manual Matching\output\                      <- results land
rem                                                            here (auto-
rem                                                            created; safe
rem                                                            to delete to
rem                                                            reset)
rem
rem  You'll be asked for the period and the engine name; the engine name
rem  must match the start of that engine's raw file name (e.g. SAP for
rem  SAP_2025-12_MM.xlsx, Oracle_Cash for Oracle_Cash_2025-12_MM.xlsx).
rem ============================================================

set "ENGINE_DIR=%~dp0engine"
set "DATA_ROOT=C:\users\swalk\documents\ReconcilePro\Operating_files\Periods"

echo ============================================================
echo  GL/Bank Matching
echo ============================================================
echo.
set /p PERIOD=Enter the period folder to run (e.g. 2025-12):

if "%PERIOD%"=="" (
    echo No period entered - stopping.
    echo.
    pause
    exit /b 1
)

set /p ENGINE=Enter the engine name (must match the start of the raw file's name, e.g. SAP, Oracle_Cash):

if "%ENGINE%"=="" (
    echo No engine name entered - stopping.
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
echo Looking for a raw export .xlsx starting with "%ENGINE%_" in:
echo   %RAW_DIR%
echo.

set "INPUT_FILE="
set "COUNT=0"
for %%F in ("%RAW_DIR%\%ENGINE%_*.xlsx") do (
    set "INPUT_FILE=%%F"
    set /a COUNT+=1
)

if "%COUNT%"=="0" (
    echo No .xlsx file starting with "%ENGINE%_" found in %RAW_DIR%
    echo Files present there:
    for %%F in ("%RAW_DIR%\*.xlsx") do echo   %%~nxF
    echo.
    echo Check the engine name spelling ^(it must match the start of the
    echo raw file's name^) and try again.
    echo.
    pause
    exit /b 1
)

if not "%COUNT%"=="1" (
    echo Found more than one .xlsx starting with "%ENGINE%_" - not sure
    echo which one is the raw export:
    for %%F in ("%RAW_DIR%\%ENGINE%_*.xlsx") do echo   %%F
    echo.
    echo Please keep only ONE raw export per engine in that folder
    echo ^(move old/output files elsewhere^), then try again.
    echo.
    pause
    exit /b 1
)

echo Using: %INPUT_FILE%
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

for %%A in ("%INPUT_FILE%") do set "BASENAME=%%~nA"
set "FINAL_FILE=%OUTPUT_DIR%\%BASENAME%_Matched.xlsx"

rem SAP's raw export used to mix multiple source systems in one sheet (an
rem upstream query issue) -- filter defensively for SAP only. Other
rem engines' raw exports are already single-engine by the time they land
rem here, so no filter is applied for them.
set "FILTER_ARGS="
if /I "%ENGINE%"=="SAP" set "FILTER_ARGS=--gl-filter-col Source --gl-filter-value SAP"

echo.
echo === Step 1/2: matching engine ===
echo This can take several minutes depending on the size of this engine's
echo file (roughly 10-15 minutes for a SAP-sized export). The window will
echo look idle - that is normal, it is working. Do not close this window.
echo.

python "%ENGINE_DIR%\match_workbook.py" ^
  --input "%INPUT_FILE%" ^
  --output "%FINAL_FILE%" ^
  %FILTER_ARGS% ^
  --id-col "Matching ID" ^
  --secondary-id-col "Matching/Group ID" ^
  --engine-col "Matched By Engine" ^
  --engine-tag "Manual" ^
  --status-col "Match Status" ^
  --status-value "Matched" ^
  --prefix "%ENGINE%" ^
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
  --input "%FINAL_FILE%" ^
  --output "%FINAL_FILE%" ^
  --bank-sheet Bank --source-label "%ENGINE%"

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
echo    %FINAL_FILE%
echo ============================================================
echo.

start "" "%FINAL_FILE%"

pause
