@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if errorlevel 1 goto :fail
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :fail
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :fail
.venv\Scripts\python.exe -m backend.diagnostics
echo.
echo JobIntel setup is complete. No Scheduled Task was created.
echo Run Open-JobIntel.cmd when you are ready to use the dashboard.
pause
exit /b 0
:fail
echo.
echo JobIntel setup failed. Review the messages above.
pause
exit /b 1
