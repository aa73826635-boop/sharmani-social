@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>&1 || (echo Install Node.js 22 first. & pause & exit /b 1)
if not exist ".env" (
  echo Creating .env from .env.render.local.example
  copy /Y ".env.render.local.example" ".env" >nul
  echo IMPORTANT: edit .env and set JWT_SECRET before continuing.
  notepad ".env"
)
if not exist "node_modules" (call npm install || (pause & exit /b 1))
call npm start
pause
