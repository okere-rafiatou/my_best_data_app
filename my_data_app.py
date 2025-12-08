import streamlit as st
import pandas as pd
import sqlite3
from requests import get
from bs4 import BeautifulSoup as bs
import time

# Configuration de la page
st.set_page_config(page_title="CoinAfrique Animal Scraper", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF6B35;'>🐾 COINAFRIQUE ANIMAL DATA APP</h1>", unsafe_allow_html=True)

st.markdown("""
Cette application vous permet de télécharger des données scrapées sur les animaux de CoinAfrique Sénégal
* **Librairies Python:** pandas, streamlit, sqlite3, beautifulsoup4, requests
* **Source de données:** [CoinAfrique Sénégal](https://sn.coinafrique.com/)
""")

# Fonction pour créer la base de données SQLite
def init_database():
    conn = sqlite3.connect('data/coinafrique_animals.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS animals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT,
                  name TEXT,
                  price TEXT,
                  address TEXT,
                  image_url TEXT,
                  scrape_date TEXT)''')
    conn.commit()
    conn.close()

# Fonction de scraping améliorée avec gestion des valeurs manquantes
def scrape_all_pages(base_url, category_name, max_pages=10):
    df = pd.DataFrame()

    for page in range(1, max_pages + 1):
        try:
            print(f"Scraping page {page}...")
            
            url = f"{base_url}?page={page}"
            res = get(url, timeout=10)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', class_='col s6 m4 l3')

            if not containers:
                print("Plus d'annonces trouvées. Fin du scraping.")
                break

            data = []
            for container in containers:
                # Extraire le nom (si absent, mettre "Non spécifié")
                try:
                    name = container.find('p', 'ad__card-description').text.strip()
                except:
                    name = "Non spécifié"
                
                # Extraire le prix (si absent, mettre "0")
                try:
                    price = container.find('p', 'ad__card-price').text.replace('CFA', '').replace(' ', '').strip()
                    if not price:
                        price = "0"
                except:
                    price = "0"
                
                # Extraire l'adresse (si absente, mettre "Non spécifiée")
                try:
                    adresse = container.find('p', 'ad__card-location').span.text.strip()
                except:
                    adresse = "Non spécifiée"
                
                # Extraire l'URL de l'image (si absente, mettre "Non disponible")
                try:
                    image_url = container.find('img', class_='ad__card-img')['src']
                except:
                    image_url = "Non disponible"

                dic = {
                    'category': category_name,
                    'name': name,
                    'price': price,
                    'address': adresse,
                    'image_url': image_url,
                    'scrape_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                data.append(dic)

            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis=0).reset_index(drop=True)
            time.sleep(1)
            
        except Exception as e:
            print(f"Erreur page {page}: {str(e)}")
            break

    return df

# Fonction pour nettoyer les données
def clean_data(df):
    df_clean = df.copy()
    
    # Nettoyer les prix (enlever les caractères non numériques)
    df_clean['price_clean'] = df_clean['price'].str.replace(r'\D', '', regex=True)
    df_clean['price_clean'] = pd.to_numeric(df_clean['price_clean'], errors='coerce')
    
    # Supprimer les doublons
    df_clean = df_clean.drop_duplicates(subset=['name', 'address'])
    
    # Supprimer les lignes avec des prix manquants
    df_clean = df_clean.dropna(subset=['price_clean'])
    
    return df_clean

# Fonction pour sauvegarder dans SQLite
def save_to_database(df):
    conn = sqlite3.connect('data/coinafrique_animals.db')
    df.to_sql('animals', conn, if_exists='append', index=False)
    conn.close()

# Fonction pour charger depuis SQLite
def load_from_database():
    try:
        conn = sqlite3.connect('data/coinafrique_animals.db')
        df = pd.read_sql_query("SELECT * FROM animals", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# Fonction pour afficher les données (adaptée de votre code)
def load_data(dataframe, title, key):
    st.markdown("""
    <style>
    div.stButton {text-align:center}
    </style>""", unsafe_allow_html=True)
    
    if st.button(title, key=key):
        st.subheader('Dimension des données')
        st.write('Dimension: ' + str(dataframe.shape[0]) + ' lignes et ' + str(dataframe.shape[1]) + ' colonnes.')
        st.dataframe(dataframe)

# Styles pour les boutons (adapté de votre code)
st.markdown('''<style> .stButton>button {
    font-size: 12px;
    height: 3em;
    width: 25em;
}</style>''', unsafe_allow_html=True)

# Initialiser la base de données
init_database()

# ==================== SIDEBAR ====================
st.sidebar.image("https://via.placeholder.com/300x100/FF6B35/FFFFFF?text=CoinAfrique+Scraper", use_container_width=True)

st.sidebar.markdown("""
<div style='text-align: center; padding: 10px;'>
    <h2 style='color: #FF6B35; margin: 0;'>🐾 Animal Data</h2>
    <p style='color: #666; font-size: 14px;'>Application de scraping</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation avec style
st.sidebar.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #f8f9fa;
    }
    .sidebar-menu {
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.subheader("📋 Navigation")

menu = st.sidebar.radio(
    "Choisissez une section :",
    [
        "🔍 Scraper des données", 
        "📥 Télécharger données Web Scraper", 
        "📊 Dashboard (données nettoyées)", 
        "📝 Formulaires d'évaluation"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Statistiques rapides dans la sidebar
st.sidebar.subheader("📊 Statistiques rapides")
try:
    df_stats = load_from_database()
    if not df_stats.empty:
        st.sidebar.metric("Total annonces", len(df_stats))
        st.sidebar.metric("Catégories", df_stats['category'].nunique())
        
        df_clean_stats = clean_data(df_stats)
        if not df_clean_stats.empty and 'price_clean' in df_clean_stats.columns:
            avg_price = df_clean_stats['price_clean'].mean()
            st.sidebar.metric("Prix moyen", f"{avg_price:,.0f} CFA")
    else:
        st.sidebar.info("Aucune donnée disponible")
except:
    st.sidebar.info("Aucune donnée disponible")

st.sidebar.markdown("---")

# Informations supplémentaires
st.sidebar.subheader("ℹ️ À propos")
st.sidebar.markdown("""
<div style='font-size: 12px; color: #666;'>
📦 <b>Version:</b> 1.0.0<br>
🔧 <b>Tech:</b> Streamlit + BeautifulSoup<br>
🌐 <b>Source:</b> CoinAfrique SN<br>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Liens utiles
with st.sidebar.expander("🔗 Liens utiles"):
    st.markdown("""
    - [CoinAfrique](https://sn.coinafrique.com)
    - [Documentation Streamlit](https://docs.streamlit.io)
    - [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
    """)

# ==================== SECTION 1: SCRAPER ====================
if menu == "🔍 Scraper des données":
    st.header("🔍 Scraper des données sur plusieurs pages")
    
    st.info("⚠️ Le scraping peut prendre quelques minutes selon le nombre de pages.")
    
    categories = {
        "🐕 Chiens": "https://sn.coinafrique.com/categorie/chiens",
        "🐑 Moutons": "https://sn.coinafrique.com/categorie/moutons",
        "🐔 Poules, lapins et pigeons": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
        "🦎 Autres animaux": "https://sn.coinafrique.com/categorie/autres-animaux"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_category = st.selectbox("Catégorie à scraper", list(categories.keys()))
    
    with col2:
        max_pages = st.slider("Nombre de pages", 1, 20, 5)
    
    if st.button("🚀 Lancer le scraping", type="primary"):
        with st.spinner(f"Scraping en cours pour {selected_category}..."):
            category_name = selected_category.split(' ', 1)[1]  # Enlever l'emoji
            df_scraped = scrape_all_pages(categories[selected_category], category_name, max_pages)
            
            if not df_scraped.empty:
                st.success(f"✅ {len(df_scraped)} annonces scrapées avec succès !")
                
                # Sauvegarder dans la base de données
                save_to_database(df_scraped)
                st.info("💾 Données sauvegardées dans la base de données SQLite")
                
                # Afficher un aperçu
                st.subheader("📋 Aperçu des données")
                st.dataframe(df_scraped.head(10))
                
                # Télécharger immédiatement
                csv = df_scraped.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Télécharger {category_name} (CSV)",
                    data=csv,
                    file_name=f'{category_name.lower().replace(" ", "_")}.csv',
                    mime='text/csv',
                )
            else:
                st.warning("⚠️ Aucune donnée trouvée.")

# ==================== SECTION 2: TÉLÉCHARGER DONNÉES BRUTES ====================
elif menu == "📥 Télécharger données Web Scraper":
    st.header("📥 Télécharger les données brutes (non nettoyées)")
    
    st.markdown("""
    Cette section vous permet de télécharger les données scrapées avec Web Scraper (format brut, sans nettoyage).
    """)
    
    df_raw = load_from_database()
    
    if not df_raw.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total d'annonces", len(df_raw))
        with col2:
            st.metric("📂 Catégories", df_raw['category'].nunique())
        with col3:
            st.metric("📅 Dernière mise à jour", df_raw['scrape_date'].max()[:10] if 'scrape_date' in df_raw.columns else "N/A")
        
        # Grouper par catégorie
        st.subheader("📑 Répartition par catégorie")
        category_counts = df_raw['category'].value_counts().reset_index()
        category_counts.columns = ['Catégorie', 'Nombre d\'annonces']
        st.dataframe(category_counts, use_container_width=True)
        
        # Charger les données par catégorie (comme votre code original)
        st.subheader("📁 Données par catégorie")
        
        categories_list = df_raw['category'].unique()
        
        for idx, cat in enumerate(categories_list, 1):
            df_cat = df_raw[df_raw['category'] == cat]
            load_data(df_cat, f"Données {cat}", str(idx))
        
        # Télécharger toutes les données
        st.subheader("💾 Télécharger toutes les données")
        csv_all = df_raw.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger toutes les données (CSV)",
            data=csv_all,
            file_name='coinafrique_animals_all.csv',
            mime='text/csv',
        )
        
    else:
        st.info("ℹ️ Aucune donnée disponible. Veuillez d'abord scraper des données.")
        st.markdown("👉 Allez dans **🔍 Scraper des données** pour commencer.")

# ==================== SECTION 3: DASHBOARD ====================
elif menu == "📊 Dashboard (données nettoyées)":
    st.header("📊 Dashboard des données nettoyées")
    
    df_raw = load_from_database()
    
    if not df_raw.empty:
        df_clean = clean_data(df_raw)
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Annonces totales", len(df_clean))
        with col2:
            st.metric("💰 Prix moyen", f"{df_clean['price_clean'].mean():,.0f} CFA")
        with col3:
            st.metric("💵 Prix min", f"{df_clean['price_clean'].min():,.0f} CFA")
        with col4:
            st.metric("💸 Prix max", f"{df_clean['price_clean'].max():,.0f} CFA")
        
        # Statistiques par catégorie
        st.subheader("📈 Statistiques par catégorie")
        category_stats = df_clean.groupby('category').agg({
            'price_clean': ['count', 'mean', 'min', 'max']
        }).round(0)
        category_stats.columns = ['Nombre', 'Prix moyen (CFA)', 'Prix min (CFA)', 'Prix max (CFA)']
        st.dataframe(category_stats, use_container_width=True)
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Prix moyen par catégorie")
            avg_prices = df_clean.groupby('category')['price_clean'].mean().sort_values(ascending=False)
            st.bar_chart(avg_prices)
        
        with col2:
            st.subheader("📊 Nombre d'annonces par catégorie")
            counts = df_clean['category'].value_counts()
            st.bar_chart(counts)
        
        # Top localisations
        st.subheader("📍 Top 10 des localisations")
        top_locations = df_clean['address'].value_counts().head(10)
        st.bar_chart(top_locations)
        
        # Explorer les données
        st.subheader("🔍 Explorer les données nettoyées")
        
        # Filtre par catégorie
        selected_cat = st.multiselect(
            "Filtrer par catégorie",
            options=df_clean['category'].unique(),
            default=df_clean['category'].unique()
        )
        
        df_filtered = df_clean[df_clean['category'].isin(selected_cat)]
        
        st.write(f"**{len(df_filtered)}** annonces affichées")
        st.dataframe(df_filtered[['category', 'name', 'price', 'price_clean', 'address']], use_container_width=True)
        
        # Télécharger les données nettoyées
        csv_clean = df_clean.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les données nettoyées (CSV)",
            data=csv_clean,
            file_name='coinafrique_animals_clean.csv',
            mime='text/csv',
        )
        
    else:
        st.info("ℹ️ Aucune donnée disponible. Veuillez d'abord scraper des données.")

# ==================== SECTION 4: FORMULAIRES D'ÉVALUATION ====================
elif menu == "📝 Formulaires d'évaluation":
    st.header("📝 Formulaires d'évaluation de l'application")
    
    st.markdown("""
    Votre avis est important pour nous aider à améliorer cette application. 
    Merci de prendre quelques instants pour répondre à l'un de ces questionnaires.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Formulaire KoboToolbox")
        st.markdown("""
        Remplissez le formulaire d'évaluation sur **KoboToolbox** pour nous faire part de votre expérience.
        
        Ce formulaire permet une collecte de données structurée et professionnelle.
        """)
        
        st.link_button(
            "🔗 Ouvrir le formulaire KoboToolbox",
            "https://ee.kobotoolbox.org/x/JWIzi1ib",
            use_container_width=True
        )
        
        st.markdown("---")
        st.info("💡 **KoboToolbox** est une plateforme de collecte de données utilisée pour des enquêtes professionnelles.")
    
    with col2:
        st.subheader("📝 Formulaire Google Forms")
        st.markdown("""
        Vous préférez **Google Forms** ? Remplissez ce formulaire pour partager vos commentaires et suggestions.
        
        Interface simple et familière.
        """)
        
        st.link_button(
            "🔗 Ouvrir le formulaire Google Forms",
            "https://docs.google.com/forms/d/e/1FAIpQLSfZWFZCFv5vK3ULo0TK5kJAhojavgBRrAk8LJhT64afKlnhYw/viewform?usp=dialog",
            use_container_width=True
        )
        
        st.markdown("---")
        st.info("💡 **Google Forms** permet un accès rapide et facile depuis n'importe quel appareil.")
    
    st.markdown("---")
    
    # Section pourquoi évaluer
    st.subheader("❓ Pourquoi votre évaluation est importante")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎯 Amélioration continue
        Vos retours nous aident à identifier les fonctionnalités à améliorer.
        """)
    
    with col2:
        st.markdown("""
        ### 💡 Nouvelles fonctionnalités
        Vos suggestions guident le développement de nouvelles features.
        """)
    
    with col3:
        st.markdown("""
        ### 🤝 Expérience utilisateur
        Votre avis façonne l'évolution de l'application.
        """)
    
    st.success("✅ Merci d'avance pour votre contribution !")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Développé avec ❤️ par Streamlit | Données de <a href='https://sn.coinafrique.com' target='_blank'>CoinAfrique Sénégal</a></p>
    <p style='font-size: 12px;'>© 2024 - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
