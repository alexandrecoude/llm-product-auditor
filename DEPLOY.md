# 🚀 Guide de déploiement - LLM Product Auditor

## Option 1 : Déploiement sur Streamlit Cloud (RECOMMANDÉ - GRATUIT)

### ✅ Avantages
- Gratuit jusqu'à 1 app publique
- Déploiement en 5 minutes
- Mise à jour automatique via Git
- URL publique accessible partout
- Aucune maintenance serveur

### 📋 Prérequis
- Un compte GitHub (gratuit)
- Les fichiers de ce projet

### 🎯 Étapes détaillées

#### 1. Créer un repository GitHub

1. Va sur https://github.com
2. Clique sur le bouton **"+"** en haut à droite → **"New repository"**
3. Remplis les informations :
   - **Repository name** : `llm-product-auditor`
   - **Description** : "Outil SaaS d'audit de pages produits e-commerce"
   - **Public** ✅ (requis pour Streamlit Cloud gratuit)
   - Ne coche PAS "Add a README" (on a déjà le nôtre)
4. Clique sur **"Create repository"**

#### 2. Pousser le code sur GitHub

Ouvre un terminal dans le dossier du projet et exécute :

```bash
# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - LLM Product Auditor"

# Lier au repository GitHub (remplace TON-USERNAME)
git remote add origin https://github.com/TON-USERNAME/llm-product-auditor.git

# Pousser le code
git branch -M main
git push -u origin main
```

**Note** : Remplace `TON-USERNAME` par ton nom d'utilisateur GitHub

#### 3. Déployer sur Streamlit Cloud

1. Va sur https://streamlit.io/cloud
2. Clique sur **"Sign up"** et connecte-toi avec GitHub
3. Clique sur **"New app"**
4. Remplis le formulaire :
   - **Repository** : Sélectionne `ton-username/llm-product-auditor`
   - **Branch** : `main`
   - **Main file path** : `app.py`
   - **App URL** (optionnel) : choisis un nom personnalisé
5. Clique sur **"Deploy!"**

⏱️ Attends 2-3 minutes... et c'est en ligne ! 🎉

#### 4. Tester ton app

Tu reçois une URL du type : `https://ton-app.streamlit.app`

Partage cette URL à tes clients, teste-la, etc.

#### 5. Mettre à jour l'app

Pour modifier l'app après déploiement :

```bash
# Modifie app.py ou autre fichier
# Puis :
git add .
git commit -m "Description de tes modifications"
git push

# Streamlit Cloud redéploie automatiquement !
```

---

## Option 2 : Test en local (développement)

### Sur Mac/Linux

```bash
# Lancer le script
./start.sh
```

Ou manuellement :

```bash
# Créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
```

### Sur Windows

```bash
# Double-cliquer sur start.bat
```

Ou manuellement :

```bash
# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate.bat

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
```

L'app s'ouvre sur : http://localhost:8501

---

## Option 3 : Déploiement sur un serveur VPS (avancé)

Si tu veux héberger sur ton propre serveur :

### Avec Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build et run
docker build -t product-auditor .
docker run -p 8501:8501 product-auditor
```

### Avec systemd (Linux)

```bash
# Installer sur le serveur
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Cloner le repo
git clone https://github.com/TON-USERNAME/llm-product-auditor.git
cd llm-product-auditor

# Installer les dépendances
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Créer un service systemd
sudo nano /etc/systemd/system/product-auditor.service
```

Contenu du service :

```ini
[Unit]
Description=LLM Product Auditor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/llm-product-auditor
Environment="PATH=/path/to/llm-product-auditor/.venv/bin"
ExecStart=/path/to/llm-product-auditor/.venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer
sudo systemctl enable product-auditor
sudo systemctl start product-auditor

# Configurer nginx comme reverse proxy
sudo nano /etc/nginx/sites-available/product-auditor
```

---

## 🔐 Configuration avancée

### Variables d'environnement (optionnel)

Si tu veux ajouter des secrets (clés API, etc.) :

1. Sur Streamlit Cloud :
   - Va dans **Settings** → **Secrets**
   - Ajoute tes variables au format TOML

2. En local :
   - Crée `.streamlit/secrets.toml`
   - Ajoute tes secrets (ce fichier est déjà dans .gitignore)

Exemple :

```toml
# .streamlit/secrets.toml
API_KEY = "ta-cle-api"
DATABASE_URL = "postgresql://..."
```

Utilisation dans le code :

```python
import streamlit as st

api_key = st.secrets["API_KEY"]
```

---

## 📊 Analytics et monitoring

### Activer les analytics Streamlit

Dans `.streamlit/config.toml`, change :

```toml
[browser]
gatherUsageStats = true  # Activer les stats
```

### Ajouter Google Analytics

Ajoute dans `app.py` :

```python
# Avant st.set_page_config()
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", unsafe_allow_html=True)
```

---

## 🚨 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### "Port already in use"
```bash
# Changer le port
streamlit run app.py --server.port=8502
```

### "Cannot connect to backend"
- Vérifie que httpx n'est pas bloqué par un firewall
- Certains sites bloquent les user-agents automatisés

### L'app est lente
- Réduis `max_pages` dans les paramètres
- Ajoute des filtres pour cibler uniquement les pages produits

---

## 💰 Passer en version payante (monétisation)

### Option 1 : Streamlit Cloud Teams ($250/mois)
- Apps privées
- Plus de ressources
- Support prioritaire

### Option 2 : Créer une version SaaS complète

Fonctionnalités à ajouter :

1. **Authentification** (utilisateurs payants)
   - Streamlit Authenticator
   - Auth0, Firebase, Supabase

2. **Base de données** (historique des scans)
   - PostgreSQL sur Supabase
   - MongoDB Atlas

3. **Système de paiement**
   - Stripe
   - Plans : Free (10 scans/mois), Pro (illimité), Agency (multi-sites)

4. **API REST**
   - Pour les intégrations
   - Webhooks

5. **Tableau de bord avancé**
   - Graphiques d'évolution
   - Comparaison concurrentielle
   - Alertes email

---

## 🎯 Prochaines étapes

Une fois déployé :

1. ✅ Teste l'app avec 3-5 sites réels
2. ✅ Collecte les feedbacks
3. ✅ Identifie les bugs et améliore
4. ✅ Ajoute des fonctionnalités selon les demandes
5. ✅ Commence à promouvoir (LinkedIn, communautés SEO, Reddit)

---

**Besoin d'aide ?** Ouvre une issue sur GitHub ou contacte-moi !
