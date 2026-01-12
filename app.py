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

# Configuration du style
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 LLM Product Page Auditor")
st.markdown("**Auditez vos pages produits e-commerce** : détection de schema.org, scoring SEO et recommandations d'optimisation.")

# Sidebar pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres du scan")
    
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
        st.warning("⚠️ Aucun filtre : toutes les pages seront analysées")
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
    """Vérifie si l'URL appartient au même domaine que la racine"""
    return urlparse(url).netloc == urlparse(root).netloc

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
            urls = []
            
            # Gestion des sitemap index (multiples sitemaps)
            sitemap_files = [loc for loc in locs if loc.endswith(".xml") and "sitemap" in loc.lower()]
            
            if sitemap_files:
                progress_bar.progress(0.2, text=f"📄 {len(sitemap_files)} sitemap(s) trouvé(s)...")
                for i, sitemap_file in enumerate(sitemap_files):
                    try:
                        subxml = await fetch_text(client, sitemap_file)
                        urls.extend(SITEMAP_RE.findall(subxml))
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

def score_page(html: str) -> dict:
    """Analyse une page HTML et calcule un score de qualité"""
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True).lower()
    
    jsonlds = extract_jsonld(html)
    product_schema = has_product_schema(jsonlds)
    
    # Détection des éléments clés
    findings = {
        "has_jsonld": len(jsonlds) > 0,
        "has_product_schema": product_schema,
        "has_specs_table": bool(soup.select("table")),
        "mentions_reviews": any(k in text for k in ["avis", "reviews", "étoiles", "note", "rating"]),
        "has_faq": any(k in text for k in ["faq", "questions fréquentes", "questions frequentes", "frequently asked"]),
        "has_many_images": len(soup.select("img")) >= 3,
    }
    
    # Calcul du score (sur 100)
    weights = {
        "has_product_schema": 40,
        "has_jsonld": 10,
        "has_specs_table": 15,
        "mentions_reviews": 15,
        "has_faq": 10,
        "has_many_images": 10,
    }
    
    score = sum(w for k, w in weights.items() if findings.get(k))
    
    # Génération des recommandations
    recos = []
    if not findings["has_product_schema"]:
        recos.append("🔴 Ajouter JSON-LD schema.org Product + Offer (prix, devise, stock, GTIN/SKU)")
    if not findings["has_specs_table"]:
        recos.append("🟡 Ajouter un tableau de spécifications (matière, poids, dimensions, normes)")
    if not findings["has_faq"]:
        recos.append("🟡 Ajouter une FAQ produit (8-15 Q/R) + balisage FAQPage")
    if not findings["mentions_reviews"]:
        recos.append("🟠 Ajouter des avis clients (note, volume, verbatim) + AggregateRating")
    if not findings["has_many_images"]:
        recos.append("🟢 Ajouter plus d'images (packshot, détails, contexte) avec alt descriptifs")
    
    return {
        "score": score,
        "findings": findings,
        "recommendations": recos
    }

async def run_audit(root_url: str, max_pages: int, include_pattern: str, 
                   exclude_patterns: list, progress_bar, status_text):
    """Lance l'audit complet du site"""
    
    # Découverte des URLs
    urls = await discover_urls(root_url, progress_bar)
    
    # Filtrage
    urls_before_filter = len(urls)
    urls = [u for u in urls if same_domain(u, root_url)]
    urls = [u for u in urls if url_allowed(u, include_pattern, exclude_patterns)]
    urls = urls[:max_pages]
    
    # Vérification si on a des URLs à analyser
    if len(urls) == 0:
        return {
            "error": True,
            "message": f"Aucune URL trouvée après filtrage. {urls_before_filter} URL(s) découverte(s) mais aucune ne correspond aux filtres.",
            "suggestions": [
                "✅ Essayez sans filtre (sélectionnez 'Personnalisé' et laissez le champ vide)",
                "✅ Vérifiez que le site a un sitemap.xml accessible",
                "✅ Ou entrez directement une URL de page produit",
                f"✅ URLs découvertes : {urls_before_filter}"
            ]
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
                return
            
            # Stocke les résultats dans la session
            st.session_state.results = results
            st.session_state.root_url = root_url
            
            # Statistiques globales
            total = len(results)
            products = len([r for r in results if r["type"] == "product"])
            avg_score = sum(r["score"] for r in results) / total if total > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📄 Pages analysées", total)
            col2.metric("🛍️ Pages produits", products)
            col3.metric("📊 Score moyen", f"{avg_score:.0f}/100")
            col4.metric("⚠️ Pages à optimiser", len([r for r in results if r["score"] < 70]))
            
            st.success(f"✅ Scan terminé ! {total} page(s) analysée(s)")
            
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
                "Score": r["score"],
                "Recommendations": " | ".join(r["recommendations"])
            }
            for r in filtered_results
        ])
        
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger le CSV",
            data=csv,
            file_name=f"audit_{urlparse(st.session_state.root_url).netloc}_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    st.info(f"Affichage de {len(filtered_results)} page(s) sur {len(results)}")
    
    # Tableau des résultats
    for i, r in enumerate(filtered_results):
        with st.expander(
            f"{'🛍️' if r['type'] == 'product' else '📄'} "
            f"**Score: {r['score']}/100** - {r['url'][:80]}{'...' if len(r['url']) > 80 else ''}",
            expanded=(i < 5)  # Affiche les 5 premiers
        ):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.caption("🔗 URL complète")
                st.code(r["url"], language=None)
            
            with col2:
                st.caption("📊 Détails")
                st.write(f"**Type:** {r['type']}")
                st.write(f"**Status:** {r['status']}")
                
            with col3:
                st.caption("🎯 Score")
                score_color = "🟢" if r['score'] >= 70 else "🟡" if r['score'] >= 40 else "🔴"
                st.write(f"{score_color} **{r['score']}/100**")
            
            if r["recommendations"]:
                st.caption("💡 Recommandations")
                for reco in r["recommendations"]:
                    st.markdown(f"- {reco}")
else:
    st.info("👆 Entrez une URL et lancez un scan pour commencer l'audit")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🔍 <strong>LLM Product Page Auditor</strong> - Optimisez vos pages produits pour le SEO e-commerce</p>
    <p style='font-size: 0.9em;'>Détection automatique de schema.org, scoring intelligent et recommandations actionnables</p>
</div>
""", unsafe_allow_html=True)
