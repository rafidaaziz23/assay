@echo off
REM Strict /goal gate for the Assay DEV3 overnight run. Exit 0 = goal may be done.
REM Wrapper around tools/gate_dev3_done.py (all the logic lives there, unicode-safe).
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  echo GATE RED: venv missing - do unit H0.1
  exit /b 1
)
".venv\Scripts\python.exe" "tools\gate_dev3_done.py"
exit /b %ERRORLEVEL%
