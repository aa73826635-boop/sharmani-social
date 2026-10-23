@echo off
chcp 65001 >nul
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
 echo Node.js not installed. Install Node.js LTS from https://nodejs.org/
 pause
 exit /b 1
)
if not exist .env (
 if exist .env.example copy .env.example .env >nul
 echo First run: edit .env, set JWT_SECRET and DATA_DIR=./data
 notepad .env
)
if not exist node_modules (
 call npm install
 if errorlevel 1 (echo Install failed & pause & exit /b 1)
)
set NODE_ENV=development
start "" http://localhost:3000
call npm start
pause
