@echo off
title LibrairieCI Build

echo =========================
echo INSTALLATION DEPENDANCES
echo =========================

python -m pip install --upgrade pip
pip install -r requirements.txt

echo =========================
echo COMPILATION APPLICATION
echo =========================

pyinstaller --onefile --windowed --name LibrairieCI main.py

echo.
echo =========================
echo BUILD TERMINE
echo =========================

pause