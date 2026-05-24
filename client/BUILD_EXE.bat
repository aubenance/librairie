@echo off
chcp 65001 > nul
echo.
echo ╔══════════════════════════════════════════════╗
echo ║     LibrairieCI Pro - Construction EXE       ║
echo ╚══════════════════════════════════════════════╝
echo.

:: Vérifier Python
python --version > nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Python n'est pas installé ou non dans le PATH.
    echo Téléchargez Python 3.11+ sur https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Installation des dépendances...
pip install customtkinter requests pillow pyinstaller --quiet
IF ERRORLEVEL 1 (
    echo [ERREUR] Échec de l'installation des packages.
    pause
    exit /b 1
)

echo [2/4] Nettoyage des anciens builds...
IF EXIST "dist" rmdir /S /Q dist
IF EXIST "build" rmdir /S /Q build

echo [3/4] Compilation en cours (peut prendre 2-5 minutes)...
pyinstaller LibrairieCI.spec --clean --noconfirm
IF ERRORLEVEL 1 (
    echo [ERREUR] La compilation a échoué.
    pause
    exit /b 1
)

echo [4/4] Copie du fichier de configuration...
copy config.json dist\LibrairieCI\config.json > nul

echo.
echo ╔══════════════════════════════════════════════╗
echo ║        ✅ BUILD RÉUSSI !                     ║
echo ╚══════════════════════════════════════════════╝
echo.
echo Le logiciel compilé se trouve dans :
echo   dist\LibrairieCI\LibrairieCI.exe
echo.
echo IMPORTANT : Avant de distribuer, modifiez config.json
echo pour y mettre l'URL de votre serveur hébergé.
echo.
pause
