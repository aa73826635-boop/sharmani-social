@echo off
cd /d "%~dp0"
where node >nul 2>nul || (echo Install Node.js first & pause & exit /b 1)
call npm run check
if errorlevel 1 (echo Code check failed) else (echo Code syntax OK)
pause
