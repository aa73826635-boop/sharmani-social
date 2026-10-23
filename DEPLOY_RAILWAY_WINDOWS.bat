@echo off
chcp 65001 >nul
cd /d "%~dp0"
where railway >nul 2>&1
if errorlevel 1 (
 echo Railway CLI is not installed. Install Node.js and run: npm install -g @railway/cli
 pause
 exit /b 1
)
echo Login to Railway in your browser...
railway login
if errorlevel 1 goto failed
echo Select an existing Railway project and service or create one from dashboard first.
railway link
if errorlevel 1 goto failed
echo Deploying project to Railway...
railway up
if errorlevel 1 goto failed
echo Deployment command submitted. Check logs and configure Volume + Variables in Railway dashboard.
railway status
pause
exit /b 0
:failed
echo Deployment was not completed. Check the error above.
pause
exit /b 1
