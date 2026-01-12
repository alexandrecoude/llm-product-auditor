#!/bin/bash

echo "🚀 Démarrage de LLM Product Auditor..."
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Installez-le depuis python.org"
    exit 1
fi

echo "✅ Python détecté"

# Créer un environnement virtuel si nécessaire
if [ ! -d ".venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

# Activer l'environnement
echo "🔧 Activation de l'environnement..."
source .venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -q -r requirements.txt

# Lancer Streamlit
echo ""
echo "✨ Lancement de l'application..."
echo "➡️  L'app va s'ouvrir dans votre navigateur"
echo "➡️  Ctrl+C pour arrêter"
echo ""

streamlit run app.py
