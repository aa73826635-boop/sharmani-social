@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .env (echo Run START_WINDOWS.bat first & pause & exit /b 1)
if not exist node_modules (call npm install)
echo Administrator email: aa73826635@gmail.com
echo Enter a strong password (12+ characters). It will be visible while typing.
set /p "ADMIN_INITIAL_PASSWORD=Password: "
set "ADMIN_EMAIL=aa73826635@gmail.com"
call npm run admin:setup
set "ADMIN_INITIAL_PASSWORD="
pause
