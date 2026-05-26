@echo off
chcp 65001 >nul 2>&1
title LibrairieCI - Mode Debug

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0client"
python main.py 2>&1 | tee debug_log.txt
echo.
echo Log sauvegarde dans client\debug_log.txt
pause
