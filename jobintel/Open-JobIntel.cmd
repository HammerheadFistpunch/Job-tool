@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo JobIntel is not installed. Run Install-JobIntel.cmd first.
  pause
  exit /b 1
)
for /f %%P in ('powershell -NoProfile -Command "(Get-Content 'config/settings.json' -Raw | ConvertFrom-Json).dashboard.port"') do set JOBINTEL_PORT=%%P
if not defined JOBINTEL_PORT set JOBINTEL_PORT=8000
start "JobIntel" /min .venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port %JOBINTEL_PORT%
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:%JOBINTEL_PORT%
