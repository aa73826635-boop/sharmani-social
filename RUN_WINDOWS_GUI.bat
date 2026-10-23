@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (echo Please install Python 3.11+ from python.org & pause & exit /b 1)
if not exist ".venv\Scripts\python.exe" (py -3 -m venv .venv || (pause & exit /b 1))
".venv\Scripts\python.exe" -m pip install -r windows_app\requirements.txt || (pause & exit /b 1)
".venv\Scripts\python.exe" windows_app\app.py
if errorlevel 1 pause
