@echo off
echo 🚀 Démarrage de LLM Product Auditor...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé. Installez-le depuis python.org
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Créer un environnement virtuel si nécessaire
if not exist ".venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv .venv
)

REM Activer l'environnement
echo 🔧 Activation de l'environnement...
call .venv\Scripts\activate.bat

REM Installer les dépendances
echo 📥 Installation des dépendances...
pip install -q -r requirements.txt

REM Lancer Streamlit
echo.
echo ✨ Lancement de l'application...
echo ➡️  L'app va s'ouvrir dans votre navigateur
echo ➡️  Ctrl+C pour arrêter
echo.

streamlit run app.py
