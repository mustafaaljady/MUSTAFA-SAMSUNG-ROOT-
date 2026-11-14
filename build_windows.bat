@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name MUSTAFA_ALJADY_Samsung_Tool mustafa_samsung_tool.py
if errorlevel 1 (
  echo Build failed. Check the error messages above.
  pause
  exit /b 1
)
echo.
echo SUCCESS: dist\MUSTAFA_ALJADY_Samsung_Tool.exe
pause
