@echo off
REM Per-unit smoke gate for the Assay DEV3 run. Exit 0 = green.
REM ASCII-only on purpose: cmd.exe reads .cmd in the OEM codepage, so non-ASCII
REM bytes (em dash, smart quotes) corrupt parsing. All logic lives in the .py.
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  echo GAGAL: venv belum ada - kerjakan unit H0.1
  exit /b 1
)
".venv\Scripts\python.exe" "tools\gate_dev3_smoke.py"
exit /b %ERRORLEVEL%
