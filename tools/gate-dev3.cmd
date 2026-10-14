@echo off
REM Gate DEV3 — offline, deterministik. Exit 0 = hijau.
REM
REM Kenapa offline: plafon gate Hermes = 300s (hermes_cli/goals.py
REM DEFAULT_GATE_TIMEOUT_SECONDS, nol config key). Panggilan model live bisa
REM lewat plafon dan gate yang kehabisan waktu dilaporkan gagal. Jadi gate cuma
REM nguji yang deterministik: import, unit test, bentuk katalog. Bukti live
REM dijalankan manual per unit dan ditempel di docs/DEV3-OVERNIGHT-LOG.md.
REM
REM PATH di-set eksplisit: cmd.exe mewarisi environment Hermes; python sistem
REM bisa beda. Kita pakai venv repo, bukan python global.
setlocal
cd /d "%~dp0.."
set "PY=%~dp0..\.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo GAGAL: venv belum ada: %PY%
  echo        kerjakan unit H0.1 dulu (lihat docs/DEV3-OVERNIGHT-BRIEF.md)
  exit /b 1
)

"%PY%" -c "import ai; print('ai import OK')" || exit /b 1

if exist "eval\tests" (
  "%PY%" -m pytest eval\tests -q || exit /b 1
)

if exist "prompts\honeypot-catalog.json" (
  "%PY%" -c "import json,sys; d=json.load(open('prompts/honeypot-catalog.json',encoding='utf-8')); e=d if isinstance(d,list) else d.get('terms') or d.get('catalog') or []; sys.exit(0 if len(e)>=10 else 1)" || (
    echo GAGAL: prompts/honeypot-catalog.json harus punya >= 10 entri
    exit /b 1
  )
)

if exist "ai\FIXTURES.md" ( echo FIXTURES OK ) else ( echo GAGAL: ai/FIXTURES.md belum ada & exit /b 1 )

echo GATE HIJAU
exit /b 0
