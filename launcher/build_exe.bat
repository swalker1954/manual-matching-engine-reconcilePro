@echo off
REM Builds Manual Matching Process.exe from app.py using PyInstaller.
REM Run this from the "launcher" folder on a Windows machine with Python installed.

pip install -r requirements.txt
pyinstaller --onefile --windowed --icon=icon.ico --name "Manual Matching Process" app.py

echo.
echo Build complete. The executable is at dist\Manual Matching Process.exe
echo Run create_desktop_shortcut.ps1 next to add the desktop launch icon.
