import streamlit as st
import re
import json
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time

st.set_page_config(
    page_title="LLM Product Page Auditor",
    page_icon="🔍",
    layout="wide"
)

# Configuration de la page
st.set_page_config(
    page_title="LLM Product Auditor - GEO",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé inspiré de Finary
st.markdown("""
<style>
    /* Imports Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Variables globales */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #f59e0b;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
    }
    
    /* Reset & Base */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Corps principal */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0 !important;
    }
    
    .block-container {
        padding: 3rem 4rem !important;
        max-width: 1400px !important;
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        margin: 2rem auto !important;
        box-shadow: var(--shadow-xl);
    }
    
    /* Titres */
    h1 {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em !important;
    }
    
    h2 {
        font-size: 1.875rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Sous-titre */
    .element-container:has(> .stMarkdown > p:first-child) p:first-of-type {
        font-size: 1.125rem !important;
        color: var(--text-secondary) !important;
        font-weight: 400 !important;
        line-height: 1.75 !important;
    }
    
    /* Cards et containers */
    .stExpander {
        background: white !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-sm) !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stExpander:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px);
    }
    
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.25rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: var(--shadow-md) !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
    }
    
    .stButton > button:hover {
        box-shadow: var(--shadow-lg) !important;
        transform: translateY(-2px);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--success-color) 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.625rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        border: 2px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        background: white !important;
    }
    
    /* Alerts */
    .stAlert {
        background: linear-gradient(135deg, #ede9fe 0%, #f3f4f6 100%) !important;
        border: none !important;
        border-left: 4px solid var(--primary-color) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem 1.25rem !important;
        color: var(--text-primary) !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%) !important;
        border-left-color: var(--success-color) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%) !important;
        border-left-color: var(--warning-color) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%) !important;
        border-left-color: var(--danger-color) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        border-radius: 9999px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%) !important;
        border-right: 1px solid var(--border-color) !important;
        padding: 2rem 1.5rem !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    /* Code blocks */
    code {
        background: var(--bg-secondary) !important;
        color: var(--primary-color) !important;
        padding: 0.25rem 0.5rem !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }
    
    /* Tables */
    table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
        width: 100% !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    thead {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
    }
    
    thead th {
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        text-align: left !important;
    }
    
    tbody tr {
        background: white !important;
        border-bottom: 1px solid var(--border-color) !important;
    }
    
    tbody tr:hover {
        background: var(--bg-secondary) !important;
    }
    
    tbody td {
        padding: 1rem !important;
        color: var(--text-primary) !important;
    }
    
    /* Badges pour les priorités */
    .priority-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-critical {
        background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%);
        color: #dc2626;
    }
    
    .badge-important {
        background: linear-gradient(135deg, #fed7aa 0%, #ffedd5 100%);
        color: #ea580c;
    }
    
    .badge-recommended {
        background: linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%);
        color: #ca8a04;
    }
    
    .badge-bonus {
        background: linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%);
        color: #059669;
    }
    
    /* Dividers */
    hr {
        border: none !important;
        height: 1px !important;
        background: var(--border-color) !important;
        margin: 2rem 0 !important;
    }
    
    /* Colonnes */
    [data-testid="column"] {
        background: transparent !important;
        padding: 0.5rem !important;
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 9999px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 9999px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-color);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .block-container {
            padding: 1.5rem 1rem !important;
            margin: 1rem !important;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='margin-bottom: 0.5rem;'>🔍 LLM Product Auditor</h1>
    <div style='display: inline-block; background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 1rem;'>
        OPTIMISATION GEO
    </div>
    <p style='font-size: 1.25rem; color: #64748b; max-width: 800px; margin: 1rem auto 0 auto; line-height: 1.6;'>
        Auditez et optimisez vos pages produits pour les LLMs (ChatGPT, Claude, Perplexity, etc.)
        <br><span style='font-size: 1rem; color: #94a3b8;'>Analyse approfondie • Scoring par catégorie • Recommandations priorisées</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres du scan")
    
    with st.expander("💡 C'est quoi le GEO ?", expanded=False):
        st.markdown("""
        **GEO = Generative Engine Optimization**
        
        C'est l'optimisation pour les LLMs comme :
        - 🤖 ChatGPT (OpenAI)
        - 🧠 Claude (Anthropic)  
        - 🔍 Perplexity
        - 💬 Gemini (Google)
        
        **Pourquoi c'est important ?**
        Les gens posent de plus en plus de questions aux IA plutôt qu'à Google. Pour que vos produits soient recommandés, il faut :
        
        ✅ Données structurées complètes
        ✅ Contenu riche et contextualisé
        ✅ Signaux d'autorité/crédibilité
        ✅ FAQ et réponses directes
        
        **Le GEO = le nouveau SEO !**
        """)
    
    st.info("""
    💡 **Astuce** : 
    - Pour scanner **tout un site** → utilisez l'URL racine + un template
    - Pour scanner **une page unique** → entrez l'URL complète de la page
    """)
    
    max_pages = st.number_input("Nombre max de pages", min_value=1, max_value=200, value=50)
    
    st.subheader("Filtres d'URL")
    st.caption("Les filtres permettent de cibler uniquement les pages produits")
    
    template = st.selectbox(
        "Template prédéfini",
        ["Personnalisé", "Shopify", "PrestaShop", "Magento", "WooCommerce", "Aucun filtre"]
    )
    
    if template == "Shopify":
        include_pattern = "/products/"
        exclude_patterns = ["/account", "/cart", "/checkout", "/collections"]
    elif template == "PrestaShop":
        include_pattern = r"/[0-9]+-.*\.html$"
        exclude_patterns = ["/panier", "/commande", "/mon-compte"]
    elif template == "Magento":
        include_pattern = r"\.html$"
        exclude_patterns = ["/checkout", "/customer", "/cart"]
    elif template == "WooCommerce":
        include_pattern = "/product/"
        exclude_patterns = ["/cart", "/checkout", "/my-account"]
    elif template == "Aucun filtre":
        include_pattern = ""
        exclude_patterns = []
        st.success("✅ Mode 'Aucun filtre' activé - Toutes les pages seront analysées")
        st.info(f"🔍 Inclusions : `(aucune)` | Exclusions : `(aucune)`")
    else:
        include_pattern = st.text_input(
            "Pattern d'inclusion (regex)",
            value="",
            help="Ex: /products/ ou /[0-9]+-.*\.html$ - Laissez vide pour tout inclure"
        )
        exclude_patterns_text = st.text_area(
            "Patterns d'exclusion (un par ligne)",
            value="/account\n/cart\n/checkout",
            help="URLs à exclure du scan - Laissez vide pour ne rien exclure"
        )
        exclude_patterns = [p.strip() for p in exclude_patterns_text.split("\n") if p.strip()]

# Regex pour parser le sitemap
SITEMAP_RE = re.compile(r"<loc>(.*?)</loc>", re.IGNORECASE)

def same_domain(url: str, root: str) -> bool:
    """Vérifie si l'URL appartient au même domaine que la racine (gère www/non-www)"""
    url_domain = urlparse(url).netloc.lower().replace('www.', '')
    root_domain = urlparse(root).netloc.lower().replace('www.', '')
    return url_domain == root_domain

def url_allowed(url: str, include_pattern: str, exclude_patterns: list) -> bool:
    """Vérifie si l'URL respecte les filtres"""
    # Exclusions
    if any(re.search(p, url) for p in exclude_patterns):
        return False
    # Inclusions (si pattern défini)
    if include_pattern and not re.search(include_pattern, url):
        return False
    return True

async def fetch_text(client: httpx.AsyncClient, url: str) -> str:
    """Télécharge le contenu texte d'une URL"""
    r = await client.get(url, timeout=20)
    r.raise_for_status()
    return r.text

async def discover_urls(root_url: str, progress_bar) -> list[str]:
    """Découvre les URLs via sitemap.xml"""
    sitemap_url = urljoin(root_url.rstrip("/") + "/", "sitemap.xml")
    
    async with httpx.AsyncClient(
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": "LLM-Product-Auditor/1.0"}
    ) as client:
        try:
            progress_bar.progress(0.1, text="🔍 Recherche du sitemap...")
            xml = await fetch_text(client, sitemap_url)
            locs = SITEMAP_RE.findall(xml)
            
            # Nettoyer les balises CDATA des URLs
            def clean_url(url):
                """Nettoie les balises XML comme <![CDATA[ et ]]>"""
                url = url.replace('<![CDATA[', '').replace(']]>', '').strip()
                return url
            
            locs = [clean_url(loc) for loc in locs]
            urls = []
            
            # Gestion des sitemap index (multiples sitemaps)
            sitemap_files = [loc for loc in locs if loc.endswith(".xml") and "sitemap" in loc.lower()]
            
            if sitemap_files:
                progress_bar.progress(0.2, text=f"📄 {len(sitemap_files)} sitemap(s) trouvé(s)...")
                for i, sitemap_file in enumerate(sitemap_files):
                    try:
                        subxml = await fetch_text(client, sitemap_file)
                        sub_locs = SITEMAP_RE.findall(subxml)
                        sub_locs = [clean_url(loc) for loc in sub_locs]
                        urls.extend(sub_locs)
                        progress_bar.progress(0.2 + (i+1)/len(sitemap_files) * 0.2, 
                                            text=f"📄 Lecture sitemap {i+1}/{len(sitemap_files)}...")
                    except Exception:
                        pass
            else:
                urls = locs
            
            progress_bar.progress(0.5, text=f"✅ {len(urls)} URLs découvertes")
            return sorted(set(urls))
            
        except Exception as e:
            progress_bar.progress(0.5, text="⚠️ Pas de sitemap, scan de la page d'accueil uniquement")
            return [root_url]

def extract_jsonld(html: str) -> list[dict]:
    """Extrait tous les blocs JSON-LD de la page"""
    soup = BeautifulSoup(html, "lxml")
    out = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.get_text(strip=True))
            if isinstance(data, list):
                out.extend([d for d in data if isinstance(d, dict)])
            elif isinstance(data, dict):
                out.append(data)
        except Exception:
            continue
    return out

def has_product_schema(jsonlds: list[dict]) -> bool:
    """Vérifie si un schema Product est présent"""
    for d in jsonlds:
        t = d.get("@type")
        if t == "Product" or (isinstance(t, list) and "Product" in t):
            return True
    return False

def analyze_schema_completeness(jsonlds: list[dict]) -> dict:
    """Analyse la complétude des schemas Product"""
    product_schemas = [d for d in jsonlds if d.get("@type") in ["Product", "ProductModel"] or 
                      (isinstance(d.get("@type"), list) and "Product" in d.get("@type"))]
    
    if not product_schemas:
        return {"found": False, "completeness": 0, "missing": []}
    
    product = product_schemas[0]
    
    # Champs essentiels pour les LLMs
    essential_fields = {
        "name": "Nom du produit",
        "description": "Description détaillée",
        "image": "Images",
        "brand": "Marque",
        "offers": "Informations de prix"
    }
    
    # Champs recommandés pour l'enrichissement
    recommended_fields = {
        "sku": "SKU/Référence",
        "gtin": "Code-barres GTIN/EAN",
        "mpn": "Numéro fabricant",
        "aggregateRating": "Note moyenne",
        "review": "Avis clients"
    }
    
    missing = []
    score = 0
    total_points = len(essential_fields) * 2 + len(recommended_fields)
    
    # Vérifier les champs essentiels (2 points chacun)
    for field, label in essential_fields.items():
        if field in product and product[field]:
            score += 2
        else:
            missing.append(f"Champ essentiel : {label}")
    
    # Vérifier les champs recommandés (1 point chacun)
    for field, label in recommended_fields.items():
        if field in product and product[field]:
            score += 1
        else:
            missing.append(f"Champ recommandé : {label}")
    
    # Vérifier la complétude de l'offre si présente
    if "offers" in product:
        offer = product["offers"]
        if isinstance(offer, dict):
            if "price" in offer and "priceCurrency" in offer:
                score += 2
            if "availability" in offer:
                score += 1
                
    completeness = int((score / total_points) * 100)
    
    return {"found": True, "completeness": completeness, "missing": missing, "schema": product}

def analyze_content_quality(soup, text) -> dict:
    """Analyse la qualité et la structure du contenu"""
    findings = {}
    
    # Longueur du contenu
    word_count = len(text.split())
    findings["word_count"] = word_count
    findings["sufficient_content"] = word_count >= 300
    
    # Structure des titres
    h1 = soup.find_all("h1")
    h2 = soup.find_all("h2")
    h3 = soup.find_all("h3")
    findings["has_h1"] = len(h1) > 0
    findings["has_hierarchy"] = len(h2) > 0 or len(h3) > 0
    findings["heading_count"] = len(h1) + len(h2) + len(h3)
    
    # Listes et tableaux
    findings["has_lists"] = len(soup.find_all(["ul", "ol"])) > 0
    findings["has_tables"] = len(soup.find_all("table")) > 0
    findings["list_count"] = len(soup.find_all(["ul", "ol"]))
    findings["table_count"] = len(soup.find_all("table"))
    
    # Contenu structuré pour LLMs
    findings["has_paragraphs"] = len(soup.find_all("p")) >= 3
    
    # Détection de contenu comparatif/contexte
    comparison_keywords = ["vs", "versus", "comparaison", "compare", "difference", "meilleur", "top"]
    findings["has_comparison"] = any(kw in text for kw in comparison_keywords)
    
    usage_keywords = ["utilisation", "usage", "comment utiliser", "mode d'emploi", "guide", "tutoriel"]
    findings["has_usage_guide"] = any(kw in text for kw in usage_keywords)
    
    specs_keywords = ["caractéristiques", "spécifications", "specs", "techniques", "dimensions", "poids", "matière"]
    findings["has_specs"] = any(kw in text for kw in specs_keywords)
    
    return findings

def analyze_authority_signals(soup, text) -> dict:
    """Analyse les signaux d'autorité et crédibilité"""
    findings = {}
    
    # Informations sur l'auteur/marque
    findings["has_author"] = bool(soup.find(attrs={"rel": "author"})) or "par " in text.lower()
    
    # Dates de publication/mise à jour
    time_tags = soup.find_all("time")
    findings["has_publish_date"] = len(time_tags) > 0
    
    # Certifications et garanties
    cert_keywords = ["certifié", "certification", "norme", "garantie", "warranty", "iso", "ce"]
    findings["has_certifications"] = any(kw in text for kw in cert_keywords)
    
    # Informations contact/entreprise
    contact_keywords = ["contact", "téléphone", "email", "adresse", "siret"]
    findings["has_contact_info"] = any(kw in text for kw in contact_keywords)
    
    # Liens externes/sources
    external_links = soup.find_all("a", href=True)
    findings["has_external_links"] = any(link.get("rel") == ["nofollow"] for link in external_links)
    
    return findings

def analyze_metadata(soup) -> dict:
    """Analyse les métadonnées de la page"""
    findings = {}
    
    # Meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    findings["has_meta_description"] = meta_desc is not None and len(meta_desc.get("content", "")) > 50
    
    # Open Graph
    og_tags = soup.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")})
    findings["has_open_graph"] = len(og_tags) >= 3
    
    # Twitter Cards
    twitter_tags = soup.find_all("meta", attrs={"name": lambda x: x and x.startswith("twitter:")})
    findings["has_twitter_cards"] = len(twitter_tags) >= 2
    
    # Title tag
    title = soup.find("title")
    findings["has_title"] = title is not None and 30 <= len(title.text) <= 70
    
    # Canonical
    findings["has_canonical"] = soup.find("link", attrs={"rel": "canonical"}) is not None
    
    return findings

def analyze_faq_schema(jsonlds: list[dict]) -> dict:
    """Analyse la présence et qualité du schema FAQPage"""
    faq_schemas = [d for d in jsonlds if d.get("@type") == "FAQPage"]
    
    if not faq_schemas:
        return {"found": False, "question_count": 0}
    
    faq = faq_schemas[0]
    questions = faq.get("mainEntity", [])
    
    return {
        "found": True,
        "question_count": len(questions) if isinstance(questions, list) else 1,
        "well_structured": len(questions) >= 5 if isinstance(questions, list) else False
    }

def score_page(html: str) -> dict:
    """Analyse approfondie orientée GEO/LLM avec scoring par catégorie"""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True).lower()
    
    # Extraction des données structurées
    jsonlds = extract_jsonld(html)
    
    # === ANALYSE PAR CATÉGORIE ===
    
    # 1. DONNÉES STRUCTURÉES (40 points max)
    schema_analysis = analyze_schema_completeness(jsonlds)
    faq_analysis = analyze_faq_schema(jsonlds)
    
    structured_data_score = 0
    structured_data_findings = {}
    
    if schema_analysis["found"]:
        structured_data_score += int(schema_analysis["completeness"] * 0.25)  # Max 25 points
        structured_data_findings["product_schema_completeness"] = schema_analysis["completeness"]
    
    if faq_analysis["found"]:
        structured_data_score += 10 if faq_analysis["well_structured"] else 5
        structured_data_findings["faq_questions"] = faq_analysis["question_count"]
    
    # Autres schemas utiles
    has_breadcrumb = any(d.get("@type") == "BreadcrumbList" for d in jsonlds)
    if has_breadcrumb:
        structured_data_score += 5
        
    structured_data_findings["has_product_schema"] = schema_analysis["found"]
    structured_data_findings["has_faq_schema"] = faq_analysis["found"]
    structured_data_findings["has_breadcrumb"] = has_breadcrumb
    
    # 2. QUALITÉ DU CONTENU (30 points max)
    content_quality = analyze_content_quality(soup, text)
    
    content_score = 0
    if content_quality["sufficient_content"]:
        content_score += 10
    if content_quality["has_h1"] and content_quality["has_hierarchy"]:
        content_score += 5
    if content_quality["has_lists"]:
        content_score += 3
    if content_quality["has_tables"]:
        content_score += 5
    if content_quality["has_comparison"]:
        content_score += 3
    if content_quality["has_usage_guide"]:
        content_score += 2
    if content_quality["has_specs"]:
        content_score += 2
    
    # 3. AUTORITÉ & CRÉDIBILITÉ (15 points max)
    authority = analyze_authority_signals(soup, text)
    
    authority_score = 0
    if authority["has_author"]:
        authority_score += 3
    if authority["has_publish_date"]:
        authority_score += 3
    if authority["has_certifications"]:
        authority_score += 5
    if authority["has_contact_info"]:
        authority_score += 4
    
    # 4. MÉTADONNÉES (15 points max)
    metadata = analyze_metadata(soup)
    
    metadata_score = 0
    if metadata["has_meta_description"]:
        metadata_score += 5
    if metadata["has_open_graph"]:
        metadata_score += 4
    if metadata["has_twitter_cards"]:
        metadata_score += 2
    if metadata["has_title"]:
        metadata_score += 2
    if metadata["has_canonical"]:
        metadata_score += 2
    
    # SCORE TOTAL (100 points max)
    total_score = structured_data_score + content_score + authority_score + metadata_score
    
    # === GÉNÉRATION DES RECOMMANDATIONS PRIORISÉES ===
    recommendations = []
    
    # Recommandations critiques (impact élevé sur LLMs)
    if not schema_analysis["found"]:
        recommendations.append({
            "priority": "🔴 CRITIQUE",
            "category": "Données Structurées",
            "text": "Ajouter schema.org Product complet avec name, description, image, brand, offers (prix + devise + disponibilité)",
            "impact": "Très élevé - Les LLMs s'appuient massivement sur ces données"
        })
    elif schema_analysis["completeness"] < 70:
        recommendations.append({
            "priority": "🔴 CRITIQUE", 
            "category": "Données Structurées",
            "text": f"Compléter le schema Product (complétude: {schema_analysis['completeness']}%). Manquants: {', '.join(schema_analysis['missing'][:3])}",
            "impact": "Très élevé"
        })
    
    if not content_quality["sufficient_content"]:
        recommendations.append({
            "priority": "🔴 CRITIQUE",
            "category": "Contenu",
            "text": f"Enrichir le contenu ({content_quality['word_count']} mots actuellement, minimum 300-500 mots recommandé)",
            "impact": "Très élevé - Les LLMs ont besoin de contexte"
        })
    
    # Recommandations importantes
    if not faq_analysis["found"] or not faq_analysis["well_structured"]:
        recommendations.append({
            "priority": "🟠 IMPORTANT",
            "category": "Données Structurées",
            "text": "Ajouter une FAQ structurée (minimum 8-12 questions) avec schema FAQPage",
            "impact": "Élevé - Les LLMs adorent les Q&R structurées"
        })
    
    if not content_quality["has_tables"] and not content_quality["has_specs"]:
        recommendations.append({
            "priority": "🟠 IMPORTANT",
            "category": "Contenu",
            "text": "Ajouter un tableau de spécifications techniques détaillé (dimensions, matériaux, normes, poids, etc.)",
            "impact": "Élevé - Facilite les comparaisons par les LLMs"
        })
    
    if not content_quality["has_hierarchy"]:
        recommendations.append({
            "priority": "🟠 IMPORTANT",
            "category": "Contenu",
            "text": "Structurer le contenu avec des titres H2/H3 (ex: Caractéristiques, Utilisation, Avantages)",
            "impact": "Élevé - Aide les LLMs à comprendre la structure"
        })
    
    if not metadata["has_meta_description"]:
        recommendations.append({
            "priority": "🟠 IMPORTANT",
            "category": "Métadonnées",
            "text": "Ajouter une meta description concise (150-160 caractères) avec les infos clés du produit",
            "impact": "Élevé"
        })
    
    # Recommandations recommandées
    if not authority["has_certifications"]:
        recommendations.append({
            "priority": "🟡 RECOMMANDÉ",
            "category": "Autorité",
            "text": "Mentionner les certifications, normes, garanties (ISO, CE, garantie 2 ans, etc.)",
            "impact": "Moyen - Renforce la crédibilité"
        })
    
    if not content_quality["has_comparison"]:
        recommendations.append({
            "priority": "🟡 RECOMMANDÉ",
            "category": "Contenu",
            "text": "Ajouter une section comparative (vs produits similaires, cas d'usage différents)",
            "impact": "Moyen - Aide aux recommandations contextuelles"
        })
    
    if not has_breadcrumb:
        recommendations.append({
            "priority": "🟡 RECOMMANDÉ",
            "category": "Données Structurées",
            "text": "Ajouter un fil d'Ariane avec schema BreadcrumbList",
            "impact": "Moyen - Contexte de navigation"
        })
    
    if not authority["has_author"] or not authority["has_publish_date"]:
        recommendations.append({
            "priority": "🟡 RECOMMANDÉ",
            "category": "Autorité",
            "text": "Indiquer la date de publication/mise à jour et l'auteur/source",
            "impact": "Moyen - Indicateur de fraîcheur"
        })
    
    # Bonus
    if content_quality["has_lists"]:
        recommendations.append({
            "priority": "🟢 BONUS",
            "category": "Contenu",
            "text": "Continuer à utiliser des listes à puces - excellent pour la lisibilité par LLMs",
            "impact": "Faible - Déjà bien fait"
        })
    
    if not content_quality["has_usage_guide"]:
        recommendations.append({
            "priority": "🟢 BONUS",
            "category": "Contenu",
            "text": "Ajouter un guide d'utilisation ou mode d'emploi",
            "impact": "Faible - Enrichissement contextuel"
        })
    
    if not metadata["has_open_graph"]:
        recommendations.append({
            "priority": "🟢 BONUS",
            "category": "Métadonnées",
            "text": "Ajouter les balises Open Graph (og:title, og:description, og:image)",
            "impact": "Faible - Meilleur partage social"
        })
    
    return {
        "score": total_score,
        "score_breakdown": {
            "structured_data": structured_data_score,
            "content_quality": content_score,
            "authority": authority_score,
            "metadata": metadata_score
        },
        "findings": {
            "structured_data": structured_data_findings,
            "content_quality": content_quality,
            "authority": authority,
            "metadata": metadata
        },
        "recommendations": recommendations,
        "schema_analysis": schema_analysis
    }

async def run_audit(root_url: str, max_pages: int, include_pattern: str, 
                   exclude_patterns: list, progress_bar, status_text):
    """Lance l'audit complet du site"""
    
    # Découverte des URLs
    urls = await discover_urls(root_url, progress_bar)
    
    # Debug : échantillon d'URLs découvertes
    sample_urls = urls[:5] if len(urls) > 0 else []
    
    # Filtrage avec debug
    urls_discovered = len(urls)
    urls_before_domain = urls.copy()
    urls = [u for u in urls if same_domain(u, root_url)]
    urls_after_domain = len(urls)
    
    # Debug : pourquoi certaines URLs sont rejetées
    rejected_by_domain = []
    if urls_after_domain < urls_discovered:
        for u in urls_before_domain[:5]:
            if not same_domain(u, root_url):
                url_domain = urlparse(u).netloc.lower().replace('www.', '')
                root_domain = urlparse(root_url).netloc.lower().replace('www.', '')
                rejected_by_domain.append(f"{u} (domaine: {url_domain} vs {root_domain})")
    
    urls = [u for u in urls if url_allowed(u, include_pattern, exclude_patterns)]
    urls_after_patterns = len(urls)
    urls = urls[:max_pages]
    
    # Vérification si on a des URLs à analyser
    if len(urls) == 0:
        suggestions = [
            f"📊 **Debug** : {urls_discovered} URLs découvertes → {urls_after_domain} après filtre domaine → {urls_after_patterns} après filtres patterns",
            f"🌐 **Domaine root** : `{urlparse(root_url).netloc}` (sans www: `{urlparse(root_url).netloc.lower().replace('www.', '')}`)",
        ]
        
        if sample_urls:
            suggestions.append(f"🔗 **Échantillon d'URLs trouvées** :")
            for url in sample_urls[:3]:
                suggestions.append(f"   - {url}")
        
        if rejected_by_domain:
            suggestions.append(f"❌ **URLs rejetées par filtre domaine** :")
            for rej in rejected_by_domain[:3]:
                suggestions.append(f"   - {rej}")
        
        suggestions.extend([
            f"🔍 **Pattern inclusion** : `{include_pattern if include_pattern else '(aucun)'}`",
            f"🚫 **Patterns exclusion** : `{exclude_patterns if exclude_patterns else '(aucun)'}`",
            "💡 **Solution** : Copiez une URL du sitemap ci-dessus et utilisez-la directement"
        ])
        
        return {
            "error": True,
            "message": f"Aucune URL trouvée après filtrage.",
            "suggestions": suggestions
        }
    
    status_text.text(f"📊 Analyse de {len(urls)} page(s)...")
    
    results = []
    
    async with httpx.AsyncClient(
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": "LLM-Product-Auditor/1.0"}
    ) as client:
        
        for i, url in enumerate(urls):
            try:
                progress = 0.5 + (i / len(urls)) * 0.5
                progress_bar.progress(progress, text=f"🔍 Analyse {i+1}/{len(urls)}...")
                
                r = await client.get(url, timeout=20)
                ct = r.headers.get("content-type", "")
                
                if "text/html" in ct:
                    html = r.text
                    data = score_page(html)
                    page_type = "product" if data["findings"].get("has_product_schema") else "other"
                    
                    results.append({
                        "url": url,
                        "status": r.status_code,
                        "type": page_type,
                        "score": data["score"],
                        "findings": data["findings"],
                        "recommendations": data["recommendations"]
                    })
                else:
                    results.append({
                        "url": url,
                        "status": r.status_code,
                        "type": "error",
                        "score": 0,
                        "findings": {},
                        "recommendations": ["⚠️ Page non HTML"]
                    })
                    
            except Exception as e:
                results.append({
                    "url": url,
                    "status": 0,
                    "type": "error",
                    "score": 0,
                    "findings": {},
                    "recommendations": [f"❌ Erreur: {str(e)[:50]}"]
                })
    
    # Tri : produits d'abord, puis par score croissant (pages à améliorer en priorité)
    results.sort(key=lambda x: (0 if x["type"] == "product" else 1, x["score"]))
    
    progress_bar.progress(1.0, text="✅ Analyse terminée !")
    
    return results

# Interface principale
root_url = st.text_input(
    "🌐 URL à auditer",
    value="https://www.vetdepro.com",
    help="Entrez soit l'URL du site complet (ex: https://monsite.com) soit l'URL d'une page produit spécifique",
    placeholder="Ex: https://www.monsite.com ou https://www.monsite.com/produit/chaussures"
)

col1, col2 = st.columns([1, 4])

with col1:
    scan_button = st.button("🚀 Lancer le scan", type="primary", use_container_width=True)

with col2:
    with st.expander("💡 Exemples d'utilisation"):
        st.markdown("""
        **Cas 1 : Scanner tout un site e-commerce**
        - URL : `https://www.monsite.com`
        - Template : Shopify / PrestaShop / etc.
        - Résultat : Analyse toutes les pages produits du site
        
        **Cas 2 : Scanner une page produit spécifique**
        - URL : `https://www.monsite.com/produit/chaussures-123`
        - Template : Aucun filtre (ou Personnalisé sans filtre)
        - Résultat : Analyse uniquement cette page
        
        **Cas 3 : Si aucune page n'est trouvée**
        - Sélectionnez "Aucun filtre" dans la sidebar
        - Ou entrez directement l'URL de la page produit
        """)

if scan_button:
    if not root_url:
        st.error("⚠️ Veuillez entrer une URL")
    else:
        # Debug : afficher les filtres actifs
        with st.expander("🔧 Debug - Filtres actifs", expanded=False):
            st.write(f"**Template sélectionné** : {template}")
            st.write(f"**Pattern d'inclusion** : `{include_pattern if include_pattern else '(aucun)'}`")
            st.write(f"**Patterns d'exclusion** : `{exclude_patterns if exclude_patterns else '(aucun)'}`")
        
        # Affichage de la progression
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Lance l'audit
            import asyncio
            results = asyncio.run(run_audit(
                root_url, 
                max_pages, 
                include_pattern, 
                exclude_patterns,
                progress_bar,
                status_text
            ))
            
            status_text.empty()
            progress_bar.empty()
            
            # Vérifier si c'est une erreur
            if isinstance(results, dict) and results.get("error"):
                st.error(f"⚠️ {results['message']}")
                st.info("💡 **Suggestions :**")
                for suggestion in results.get("suggestions", []):
                    st.write(suggestion)
            else:
                # Stocke les résultats dans la session
                st.session_state.results = results
                st.session_state.root_url = root_url
                
                # Statistiques globales avec style moderne
                total = len(results)
                products = len([r for r in results if r["type"] == "product"])
                avg_score = sum(r["score"] for r in results) / total if total > 0 else 0
                to_optimize = len([r for r in results if r["score"] < 70])
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📊 Aperçu de l'audit")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ede9fe 0%, #f3f4f6 100%); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #6366f1; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'>
                        <div style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>PAGES ANALYSÉES</div>
                        <div style='font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{total}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #10b981; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'>
                        <div style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>PAGES PRODUITS</div>
                        <div style='font-size: 2.5rem; font-weight: 800; color: #10b981;'>{products}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    score_color = "#10b981" if avg_score >= 70 else "#f59e0b" if avg_score >= 40 else "#ef4444"
                    score_bg = "linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%)" if avg_score >= 70 else "linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%)" if avg_score >= 40 else "linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%)"
                    st.markdown(f"""
                    <div style='background: {score_bg}; padding: 1.5rem; border-radius: 16px; border-left: 4px solid {score_color}; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'>
                        <div style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>SCORE MOYEN</div>
                        <div style='font-size: 2.5rem; font-weight: 800; color: {score_color};'>{avg_score:.0f}<span style='font-size: 1.5rem; color: #94a3b8;'>/100</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #fed7aa 0%, #ffedd5 100%); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #ea580c; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'>
                        <div style='color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>À OPTIMISER</div>
                        <div style='font-size: 2.5rem; font-weight: 800; color: #ea580c;'>{to_optimize}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.success(f"✅ Scan terminé ! {total} page(s) analysée(s) • {products} page(s) produit détectée(s)")
            
        except Exception as e:
            st.error(f"❌ Erreur lors du scan : {str(e)}")
            progress_bar.empty()
            status_text.empty()

# Affichage des résultats
if "results" in st.session_state and st.session_state.results:
    results = st.session_state.results
    
    st.markdown("---")
    st.subheader("📊 Résultats détaillés")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox("Type", ["Tous", "product", "other", "error"])
    with col2:
        filter_score = st.slider("Score minimum", 0, 100, 0)
    with col3:
        export_csv = st.button("💾 Exporter en CSV", use_container_width=True)
    
    # Application des filtres
    filtered_results = results
    if filter_type != "Tous":
        filtered_results = [r for r in filtered_results if r["type"] == filter_type]
    filtered_results = [r for r in filtered_results if r["score"] >= filter_score]
    
    # Export CSV
    if export_csv:
        df_export = pd.DataFrame([
            {
                "URL": r["url"],
                "Type": r["type"],
                "Status": r["status"],
                "Score Total": r["score"],
                "Score Données Structurées": r.get("score_breakdown", {}).get("structured_data", 0),
                "Score Contenu": r.get("score_breakdown", {}).get("content_quality", 0),
                "Score Autorité": r.get("score_breakdown", {}).get("authority", 0),
                "Score Métadonnées": r.get("score_breakdown", {}).get("metadata", 0),
                "Nombre Recommandations": len(r["recommendations"]),
                "Recommandations Critiques": len([rec for rec in r["recommendations"] if "CRITIQUE" in rec.get("priority", "")]),
                "Top 3 Recommandations": " | ".join([rec.get("text", rec) if isinstance(rec, dict) else rec for rec in r["recommendations"][:3]])
            }
            for r in filtered_results
        ])
        
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger le rapport CSV",
            data=csv,
            file_name=f"audit_geo_{urlparse(st.session_state.root_url).netloc}_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    st.info(f"Affichage de {len(filtered_results)} page(s) sur {len(results)}")
    
    # Tableau des résultats
    for i, r in enumerate(filtered_results):
        # Déterminer la couleur du score
        score_color = "🟢" if r['score'] >= 70 else "🟡" if r['score'] >= 40 else "🔴"
        score_emoji = "🛍️" if r['type'] == 'product' else "📄"
        
        with st.expander(
            f"{score_emoji} **Score: {score_color} {r['score']}/100** - {r['url'][:70]}{'...' if len(r['url']) > 70 else ''}",
            expanded=(i < 3)  # Affiche les 3 premiers
        ):
            # En-tête avec URL et statut
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.caption("🔗 URL")
                st.code(r["url"], language=None)
            
            with col2:
                st.caption("📊 Statut")
                st.write(f"**Type:** {r['type']}")
                st.write(f"**HTTP:** {r['status']}")
            
            # Scores par catégorie (si disponibles)
            if "score_breakdown" in r:
                st.markdown("---")
                st.markdown("#### 📊 Scores détaillés")
                
                breakdown = r["score_breakdown"]
                
                # Données structurées
                pct_struct = (breakdown['structured_data'] / 40) * 100
                color_struct = "#10b981" if pct_struct >= 70 else "#f59e0b" if pct_struct >= 40 else "#ef4444"
                st.markdown(f"""
                <div style='margin-bottom: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                        <span style='font-weight: 600; color: #0f172a; font-size: 0.875rem;'>🔢 Données Structurées</span>
                        <span style='font-weight: 700; color: {color_struct}; font-size: 0.875rem;'>{breakdown['structured_data']}/40</span>
                    </div>
                    <div style='background: #e2e8f0; height: 8px; border-radius: 9999px; overflow: hidden;'>
                        <div style='background: {color_struct}; height: 100%; width: {pct_struct}%; transition: width 0.3s ease;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Contenu
                pct_content = (breakdown['content_quality'] / 30) * 100
                color_content = "#10b981" if pct_content >= 70 else "#f59e0b" if pct_content >= 40 else "#ef4444"
                st.markdown(f"""
                <div style='margin-bottom: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                        <span style='font-weight: 600; color: #0f172a; font-size: 0.875rem;'>📝 Qualité Contenu</span>
                        <span style='font-weight: 700; color: {color_content}; font-size: 0.875rem;'>{breakdown['content_quality']}/30</span>
                    </div>
                    <div style='background: #e2e8f0; height: 8px; border-radius: 9999px; overflow: hidden;'>
                        <div style='background: {color_content}; height: 100%; width: {pct_content}%; transition: width 0.3s ease;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Autorité
                pct_authority = (breakdown['authority'] / 15) * 100
                color_authority = "#10b981" if pct_authority >= 70 else "#f59e0b" if pct_authority >= 40 else "#ef4444"
                st.markdown(f"""
                <div style='margin-bottom: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                        <span style='font-weight: 600; color: #0f172a; font-size: 0.875rem;'>🏆 Autorité</span>
                        <span style='font-weight: 700; color: {color_authority}; font-size: 0.875rem;'>{breakdown['authority']}/15</span>
                    </div>
                    <div style='background: #e2e8f0; height: 8px; border-radius: 9999px; overflow: hidden;'>
                        <div style='background: {color_authority}; height: 100%; width: {pct_authority}%; transition: width 0.3s ease;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Métadonnées
                pct_metadata = (breakdown['metadata'] / 15) * 100
                color_metadata = "#10b981" if pct_metadata >= 70 else "#f59e0b" if pct_metadata >= 40 else "#ef4444"
                st.markdown(f"""
                <div style='margin-bottom: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                        <span style='font-weight: 600; color: #0f172a; font-size: 0.875rem;'>🏷️ Métadonnées</span>
                        <span style='font-weight: 700; color: {color_metadata}; font-size: 0.875rem;'>{breakdown['metadata']}/15</span>
                    </div>
                    <div style='background: #e2e8f0; height: 8px; border-radius: 9999px; overflow: hidden;'>
                        <div style='background: {color_metadata}; height: 100%; width: {pct_metadata}%; transition: width 0.3s ease;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Recommandations priorisées
            if r["recommendations"]:
                st.markdown("---")
                st.markdown("#### 💡 Recommandations GEO")
                
                # Grouper par priorité
                critiques = [rec for rec in r["recommendations"] if "CRITIQUE" in rec.get("priority", "")]
                importantes = [rec for rec in r["recommendations"] if "IMPORTANT" in rec.get("priority", "")]
                recommandees = [rec for rec in r["recommendations"] if "RECOMMANDÉ" in rec.get("priority", "")]
                bonus = [rec for rec in r["recommendations"] if "BONUS" in rec.get("priority", "")]
                
                # Afficher par priorité avec style moderne
                if critiques:
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%); padding: 1rem 1.25rem; border-radius: 12px; border-left: 4px solid #ef4444; margin-bottom: 1rem;'>
                        <div style='font-weight: 700; color: #dc2626; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>
                            🔴 ACTIONS CRITIQUES (à faire en priorité)
                        </div>
                    """, unsafe_allow_html=True)
                    for rec in critiques:
                        st.markdown(f"""
                        <div style='background: white; padding: 0.875rem; border-radius: 8px; margin-bottom: 0.5rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);'>
                            <div style='font-weight: 600; color: #0f172a; margin-bottom: 0.25rem;'>
                                <span style='background: #fee2e2; color: #dc2626; padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.5rem;'>{rec['category']}</span>
                                {rec['text']}
                            </div>
                            <div style='color: #64748b; font-size: 0.875rem;'>💥 Impact: {rec['impact']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if importantes:
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #fed7aa 0%, #ffedd5 100%); padding: 1rem 1.25rem; border-radius: 12px; border-left: 4px solid #ea580c; margin-bottom: 1rem;'>
                        <div style='font-weight: 700; color: #ea580c; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>
                            🟠 ACTIONS IMPORTANTES
                        </div>
                    """, unsafe_allow_html=True)
                    for rec in importantes:
                        st.markdown(f"""
                        <div style='background: white; padding: 0.875rem; border-radius: 8px; margin-bottom: 0.5rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);'>
                            <div style='font-weight: 600; color: #0f172a; margin-bottom: 0.25rem;'>
                                <span style='background: #fed7aa; color: #ea580c; padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.5rem;'>{rec['category']}</span>
                                {rec['text']}
                            </div>
                            <div style='color: #64748b; font-size: 0.875rem;'>📈 Impact: {rec['impact']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if recommandees:
                    with st.expander("🟡 Actions Recommandées (cliquer pour voir)", expanded=False):
                        for rec in recommandees:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%); padding: 0.875rem; border-radius: 8px; margin-bottom: 0.5rem;'>
                                <div style='font-weight: 600; color: #0f172a; margin-bottom: 0.25rem;'>
                                    <span style='background: #fbbf24; color: white; padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.5rem;'>{rec['category']}</span>
                                    {rec['text']}
                                </div>
                                <div style='color: #64748b; font-size: 0.875rem;'>Impact: {rec['impact']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                if bonus:
                    with st.expander("🟢 Améliorations Bonus", expanded=False):
                        for rec in bonus:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%); padding: 0.875rem; border-radius: 8px; margin-bottom: 0.5rem;'>
                                <div style='font-weight: 600; color: #0f172a; margin-bottom: 0.25rem;'>
                                    <span style='background: #10b981; color: white; padding: 0.125rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-right: 0.5rem;'>{rec['category']}</span>
                                    {rec['text']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Détails techniques (expandable)
            if "findings" in r:
                with st.expander("🔧 Détails techniques", expanded=False):
                    st.json(r["findings"])
else:
    st.info("👆 Entrez une URL et lancez un scan pour commencer l'audit")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🔍 <strong>LLM Product Page Auditor</strong> - Optimisation GEO pour les moteurs IA génératifs</p>
    <p style='font-size: 0.9em;'>Analyse approfondie orientée LLMs : données structurées complètes, contenu riche, signaux d'autorité et métadonnées optimisées</p>
    <p style='font-size: 0.8em; margin-top: 10px;'>💡 GEO = Generative Engine Optimization - Le nouveau SEO pour ChatGPT, Claude, Perplexity & co.</p>
</div>
""", unsafe_allow_html=True)
