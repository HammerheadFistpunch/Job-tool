@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo JobIntel is not installed. Run Install-JobIntel.cmd first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m backend.diagnostics
pause
