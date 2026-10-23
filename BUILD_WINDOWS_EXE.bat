@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (py -3 -m venv .venv || (pause & exit /b 1))
".venv\Scripts\python.exe" -m pip install -r windows_app\requirements.txt || (pause & exit /b 1)
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --windowed --onedir --name SharmaniSocial --distpath dist --workpath build --specpath build windows_app\app.py
if errorlevel 1 (echo Build failed & pause & exit /b 1)
echo EXE created at dist\SharmaniSocial\SharmaniSocial.exe
pause
