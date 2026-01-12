# 🔍 LLM Product Page Auditor

Un outil SaaS pour auditer automatiquement vos pages produits e-commerce et optimiser votre SEO.

## 🎯 Fonctionnalités

- ✅ **Analyse automatique** via sitemap.xml ou crawl léger
- ✅ **Détection de schema.org** (Product, Offer, AggregateRating, FAQPage)
- ✅ **Scoring intelligent** sur 100 points
- ✅ **Recommandations actionnables** pour chaque page
- ✅ **Templates prédéfinis** : Shopify, PrestaShop, Magento, WooCommerce
- ✅ **Export CSV** pour suivre vos optimisations
- ✅ **Interface simple** et intuitive

## 🚀 Déploiement sur Streamlit Cloud (GRATUIT)

### Étape 1 : Créer un repo GitHub

1. Va sur [github.com](https://github.com) et crée un nouveau repository
2. Nomme-le `llm-product-auditor` (ou ce que tu veux)
3. Rends-le **public** (requis pour Streamlit Cloud gratuit)

### Étape 2 : Pusher les fichiers

```bash
# Clone ton repo
git clone https://github.com/TON-USERNAME/llm-product-auditor.git
cd llm-product-auditor

# Copie les 3 fichiers dans le repo :
# - app.py
# - requirements.txt
# - README.md

# Commit et push
git add .
git commit -m "Initial commit - LLM Product Auditor"
git push origin main
```

### Étape 3 : Déployer sur Streamlit Cloud

1. Va sur [streamlit.io/cloud](https://streamlit.io/cloud)
2. Connecte-toi avec ton compte GitHub
3. Clique sur **"New app"**
4. Sélectionne :
   - **Repository** : `ton-username/llm-product-auditor`
   - **Branch** : `main`
   - **Main file path** : `app.py`
5. Clique sur **"Deploy"**

⏱️ Attends 2-3 minutes et ton app est en ligne ! 🎉

Tu obtiendras une URL du type : `https://ton-app.streamlit.app`

## 💻 Tester en local (optionnel)

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
```

L'app s'ouvre automatiquement sur `http://localhost:8501`

## 📖 Guide d'utilisation

### 1. Configuration de base

- **URL du site** : Entre l'URL complète de ton site (ex: `https://www.monsite.com`)
- **Nombre max de pages** : Limite le nombre de pages à analyser (défaut: 50)

### 2. Filtres avancés (sidebar)

**Templates prédéfinis** :
- **Shopify** : Filtre automatiquement `/products/`
- **PrestaShop** : URLs type `/123-nom-produit.html`
- **Magento** : URLs se terminant par `.html`
- **WooCommerce** : URLs contenant `/product/`
- **Personnalisé** : Définis tes propres regex

**Patterns d'inclusion** : Regex pour ne garder que certaines URLs
- Ex: `/products/` ou `/[0-9]+-.*\.html$`

**Patterns d'exclusion** : URLs à ignorer
- Ex: `/account`, `/cart`, `/checkout`

### 3. Lancer le scan

Clique sur "🚀 Lancer le scan" et attends quelques secondes...

### 4. Analyser les résultats

**Métriques globales** :
- 📄 Pages analysées
- 🛍️ Pages produits détectées
- 📊 Score moyen
- ⚠️ Pages à optimiser (score < 70)

**Tableau détaillé** :
- Filtre par type (product/other/error)
- Filtre par score minimum
- Voir les recommandations pour chaque page

### 5. Exporter les résultats

Clique sur "💾 Exporter en CSV" pour télécharger un fichier avec :
- URL
- Type de page
- Status HTTP
- Score
- Recommandations

## 🎯 Interprétation du score

- **🟢 70-100** : Excellente page, bien optimisée
- **🟡 40-69** : Page correcte, quelques améliorations possibles
- **🔴 0-39** : Page à optimiser en priorité

## 📊 Recommandations types

| Reco | Impact | Priorité |
|------|--------|----------|
| 🔴 Ajouter schema.org Product | Très élevé | Critique |
| 🟠 Ajouter des avis clients | Élevé | Important |
| 🟡 Ajouter tableau de specs | Moyen | Recommandé |
| 🟡 Ajouter une FAQ | Moyen | Recommandé |
| 🟢 Ajouter plus d'images | Faible | Bonus |

## 🔧 Améliorations futures possibles

- [ ] Intégration Claude AI pour recommandations personnalisées
- [ ] Analyse de la concurrence
- [ ] Suivi historique des scores
- [ ] Alertes automatiques
- [ ] Export PDF des rapports
- [ ] API REST pour intégrations
- [ ] Dashboard analytique avancé
- [ ] Multi-langue et multi-pays

## 💡 Cas d'usage

**Pour les agences SEO** :
- Auditer rapidement les sites de vos clients
- Identifier les quick wins
- Générer des rapports automatiques

**Pour les e-commerçants** :
- Vérifier la qualité de vos pages produits
- Comparer avec la concurrence
- Suivre vos optimisations dans le temps

**Pour les développeurs** :
- Valider l'implémentation du schema.org
- Tester avant la mise en prod
- Automatiser les audits SEO

## 📞 Support

Pour toute question ou suggestion d'amélioration, ouvre une issue sur GitHub !

## 📄 Licence

MIT - Libre d'utilisation et de modification

---

**Créé avec ❤️ et Streamlit**
