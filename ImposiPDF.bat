@echo off
REM -------------------------------------------------
REM ImposiPDF.bat - Lance le script ImposiPDF.py
REM -------------------------------------------------

REM Détecte le dossier actuel du .bat
SET SCRIPT_DIR=%~dp0

REM Vérifie si Python est installé
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python n'est pas trouve sur votre systeme.
    echo Veuillez installer Python 3.8+ : https://www.python.org/downloads/
    pause
    exit /b
)

REM Installer les dépendances si nécessaire
echo Installation des modules requis...
pip install -r "%SCRIPT_DIR%requirements.txt"

REM Lancer le script Python
echo Lancement de ImposiPDF.py...
python "%SCRIPT_DIR%ImposiPDF.py"

echo.
echo Appuyez sur une touche pour fermer la fenêtre...
pause >nul
