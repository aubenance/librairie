@echo off
chcp 65001 >nul 2>&1
title LibrairieCI - Gestion de Librairie

:: Nettoyer les caches Python
echo Nettoyage du cache...
for /d /r "%~dp0client" %%d in (__pycache__) do (
    if exist "%%d" rd /s /q "%%d" 2>nul
)

:: Lancer l'application
echo Demarrage de LibrairieCI...
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0client"
python main.py
if errorlevel 1 (
    echo.
    echo ERREUR - L'application a rencontre un probleme.
    echo Appuyez sur une touche pour fermer...
    pause >nul
)
