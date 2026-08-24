# Manual Matching Process — Launcher (v1)

Finds the source Excel file for a chosen Engine + Date Period (per the formula in
`Work_Order_2.txt`) and opens it in Excel. This tool does not read or write the
xlsx itself — Excel stays the source of truth; the matching work happens there.

## Quick run (for review, no build needed)

Requires Python 3 with Tkinter (standard on Windows installs).

```
cd launcher
python app.py
```

## Run the tests

```
cd launcher
pip install -r requirements.txt
pytest
```

## Build the desktop app (.exe) and add the desktop icon

On the target Windows machine:

```
cd launcher
build_exe.bat
powershell -ExecutionPolicy Bypass -File create_desktop_shortcut.ps1
```

This produces `dist\Manual Matching Process.exe` and adds a
**"Manual Matching Process"** shortcut to the desktop that launches it directly
(no console window, no Python install required to run it after building).

## How it finds the file

```
%USERPROFILE%\Documents\ReconcilePro\operating_files\periods\{YYYY-MM}\raw\Manual Matching\{Engine}_{YYYY-MM}-MM.xlsx
```

Assumes every teammate's machine has this folder structure under their own
Windows profile (an admin/setup task, not something the app configures).

## Open item to confirm

The filename formula was only demonstrated with single-word engines (`SAP`,
`Spreadsheet`). Multi-word engines in the dropdown (`Oracle Cash`, `Manual
Journal`, `Monthly Journal`, `Oracle Payables`, `Oracle Receivables`) currently
produce filenames with the space kept literally, e.g.
`Oracle Cash_2025-09-MM.xlsx`. Confirm this matches how those files are
actually named/exported before relying on it — if they use no space or an
underscore instead, `path_resolver.py` (`resolve_source_path`) is the only
place that needs to change.
