import streamlit as st
import pandas as pd
import sqlite3
from requests import get
from bs4 import BeautifulSoup as bs
import time
import os

# Configuration de la page
st.set_page_config(page_title="CoinAfrique Animal Scraper", layout="centered")

# Traductions
TRANSLATIONS = {
    'fr': {
        'title': '🐾 COINAFRIQUE ANIMAL DATA APP',
        'description': 'Cette application vous permet de télécharger des données scrapées sur les animaux de CoinAfrique Sénégal',
        'libraries': 'Librairies Python:',
        'source': 'Source de données:',
        'navigation': '📋 Navigation',
        'quick_stats': '📊 Statistiques rapides',
        'ads': 'Annonces',
        'categories': 'Catégories',
        'avg_price': 'Prix moyen',
        'no_data': 'Aucune donnée disponible',
        'about': 'ℹ️ À propos',
        'version': 'Version:',
        'tech': 'Tech:',
        'useful_links': '🔗 Liens utiles',
        'menu_scraper': '🔍 Scraper des données',
        'menu_download': '📥 Télécharger données Web Scraper',
        'menu_dashboard': '📊 Dashboard (données nettoyées)',
        'menu_forms': '📝 Formulaires d\'évaluation',
        'scraper_header': '🔍 Scraper des données sur plusieurs pages',
        'scraper_warning': '⚠️ Le scraping peut prendre quelques minutes selon le nombre de pages.',
        'category': 'Catégorie à scraper',
        'num_pages': 'Nombre de pages',
        'start_scraping': '🚀 Lancer le scraping',
        'scraping_progress': 'Scraping en cours pour',
        'success_scraped': 'annonces scrapées avec succès !',
        'saved_db': '💾 Données sauvegardées dans la base de données SQLite',
        'preview': '📋 Aperçu des données',
        'download': '📥 Télécharger',
        'no_data_found': '⚠️ Aucune donnée trouvée.',
        'dogs': '🐕 Chiens',
        'sheep': '🐑 Moutons',
        'poultry': '🐔 Poules, lapins et pigeons',
        'other_animals': '🦎 Autres animaux',
        'developed_by': 'Développé avec ❤️ par Rafiatou | Données de',
        'rights': '© 2024 - Tous droits réservés'
    },
    'en': {
        'title': '🐾 COINAFRIQUE ANIMAL DATA APP',
        'description': 'This application allows you to download scraped data on animals from CoinAfrique Senegal',
        'libraries': 'Python Libraries:',
        'source': 'Data Source:',
        'navigation': '📋 Navigation',
        'quick_stats': '📊 Quick Stats',
        'ads': 'Ads',
        'categories': 'Categories',
        'avg_price': 'Average Price',
        'no_data': 'No data available',
        'about': 'ℹ️ About',
        'version': 'Version:',
        'tech': 'Tech:',
        'useful_links': '🔗 Useful Links',
        'menu_scraper': '🔍 Scrape Data',
        'menu_download': '📥 Download Web Scraper Data',
        'menu_dashboard': '📊 Dashboard (cleaned data)',
        'menu_forms': '📝 Evaluation Forms',
        'scraper_header': '🔍 Scrape data from multiple pages',
        'scraper_warning': '⚠️ Scraping may take a few minutes depending on the number of pages.',
        'category': 'Category to scrape',
        'num_pages': 'Number of pages',
        'start_scraping': '🚀 Start Scraping',
        'scraping_progress': 'Scraping in progress for',
        'success_scraped': 'ads scraped successfully!',
        'saved_db': '💾 Data saved in SQLite database',
        'preview': '📋 Data Preview',
        'download': '📥 Download',
        'no_data_found': '⚠️ No data found.',
        'dogs': '🐕 Dogs',
        'sheep': '🐑 Sheep',
        'poultry': '🐔 Chickens, rabbits and pigeons',
        'other_animals': '🦎 Other animals',
        'developed_by': 'Developed with ❤️ by Rafiatou | Data from',
        'rights': '© 2024 - All rights reserved'
    }
}

# Initialiser la langue dans session_state
if 'language' not in st.session_state:
    st.session_state.language = 'fr'

def get_text(key):
    return TRANSLATIONS[st.session_state.language][key]

# Style personnalisé avec le thème sombre
st.markdown("""
<style>
    /* Container centré */
    .main .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Background principal */
    .stApp {
        background: linear-gradient(135deg, #1a1d29 0%, #2d3748 100%);
    }
    
    /* Sidebar */
    [data-testid=stSidebar] {
        background: linear-gradient(180deg, #1e2433 0%, #252d3d 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Cartes et containers */
    .stMarkdown, .stDataFrame {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Titres */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Métriques */
    [data-testid="stMetricValue"] {
        color: #4FD1C5 !important;
        font-weight: bold;
    }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Texte */
    p, span, label {
        color: #e2e8f0 !important;
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    /* Tableaux */
    .dataframe {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
    }
    
    /* Bouton de langue */
    .language-button {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# Bouton de changement de langue en haut à droite
col1, col2, col3 = st.columns([8, 1, 1])
with col2:
    if st.button("🇫🇷 FR", key="fr_btn", use_container_width=True):
        st.session_state.language = 'fr'
        st.rerun()
with col3:
    if st.button("🇬🇧 EN", key="en_btn", use_container_width=True):
        st.session_state.language = 'en'
        st.rerun()

st.markdown(f"<h1 style='text-align: center; color: #4FD1C5; text-shadow: 0 0 20px rgba(79, 209, 197, 0.5);'>{get_text('title')}</h1>", unsafe_allow_html=True)

st.markdown(f"""
<div style='background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 10px; border-left: 4px solid #4FD1C5;'>
{get_text('description')}
<ul style='margin-top: 10px;'>
    <li><b>{get_text('libraries')}</b> pandas, streamlit, sqlite3, beautifulsoup4, requests</li>
    <li><b>{get_text('source')}</b> <a href='https://sn.coinafrique.com/' target='_blank' style='color: #4FD1C5;'>CoinAfrique Sénégal</a></li>
</ul>
</div>
""", unsafe_allow_html=True)

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

# Fonction de scraping avec max_pages=500
def scrape_all_pages(base_url, category_name, max_pages=500):
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
                try:
                    name = container.find('p', 'ad__card-description').text.strip()
                except:
                    name = "Non spécifié"
                
                try:
                    price = container.find('p', 'ad__card-price').text.replace('CFA', '').replace(' ', '').strip()
                    if not price:
                        price = "0"
                except:
                    price = "0"
                
                try:
                    adresse = container.find('p', 'ad__card-location').span.text.strip()
                except:
                    adresse = "Non spécifiée"
                
                try:
                    image_url = container.find('img', class_='ad__card-img')['src']
                except:
                    image_url = "Non disponible"

                dic = {
                    'category': category_name,
                    'name': name,
                    'price': price,
                    'address': adresse,
                    'image_url': image_url
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
    df_clean['price_clean'] = df_clean['price'].str.replace(r'\D', '', regex=True)
    df_clean['price_clean'] = pd.to_numeric(df_clean['price_clean'], errors='coerce')
    df_clean = df_clean.drop_duplicates(subset=['name', 'address'])
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

# Initialiser la base de données
init_database()

# ==================== SIDEBAR ====================
st.sidebar.markdown(f"""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;'>
    <h2 style='color: white; margin: 0; font-size: 24px;'>🐾 Animal Data</h2>
    <p style='color: rgba(255,255,255,0.9); font-size: 14px; margin: 5px 0 0 0;'>Application de scraping</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

st.sidebar.markdown(f"<h3 style='color: #4FD1C5; margin-bottom: 15px;'>{get_text('navigation')}</h3>", unsafe_allow_html=True)

menu_options = [
    get_text('menu_scraper'),
    get_text('menu_download'),
    get_text('menu_dashboard'),
    get_text('menu_forms')
]

menu = st.sidebar.selectbox(
    "Choisissez une section :",
    menu_options,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Statistiques rapides dans la sidebar
st.sidebar.markdown(f"<h3 style='color: #4FD1C5; margin-bottom: 15px;'>{get_text('quick_stats')}</h3>", unsafe_allow_html=True)
try:
    df_stats = load_from_database()
    if not df_stats.empty:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.markdown(f"""
            <div style='background: rgba(79, 209, 197, 0.1); padding: 15px; border-radius: 10px; text-align: center;'>
                <p style='color: #4FD1C5; font-size: 24px; font-weight: bold; margin: 0;'>{len(df_stats)}</p>
                <p style='color: #e2e8f0; font-size: 12px; margin: 5px 0 0 0;'>{get_text('ads')}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style='background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 10px; text-align: center;'>
                <p style='color: #667eea; font-size: 24px; font-weight: bold; margin: 0;'>{df_stats['category'].nunique()}</p>
                <p style='color: #e2e8f0; font-size: 12px; margin: 5px 0 0 0;'>{get_text('categories')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        df_clean_stats = clean_data(df_stats)
        if not df_clean_stats.empty and 'price_clean' in df_clean_stats.columns:
            avg_price = df_clean_stats['price_clean'].mean()
            st.markdown(f"""
            <div style='background: rgba(118, 75, 162, 0.1); padding: 15px; border-radius: 10px; text-align: center; margin-top: 10px;'>
                <p style='color: #764ba2; font-size: 20px; font-weight: bold; margin: 0;'>{avg_price:,.0f} CFA</p>
                <p style='color: #e2e8f0; font-size: 12px; margin: 5px 0 0 0;'>{get_text('avg_price')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.info(get_text('no_data'))
except:
    st.sidebar.info(get_text('no_data'))

st.sidebar.markdown("---")

# Informations supplémentaires
st.sidebar.markdown(f"<h3 style='color: #4FD1C5; margin-bottom: 15px;'>{get_text('about')}</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div style='background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; font-size: 13px; color: #cbd5e0;'>
📦 <b style='color: #4FD1C5;'>{get_text('version')}</b> 1.0.0<br>
🔧 <b style='color: #4FD1C5;'>{get_text('tech')}</b> Streamlit + BeautifulSoup<br>
🌐 <b style='color: #4FD1C5;'>{get_text('source')}</b> CoinAfrique SN<br>
</div>
""", unsafe_allow_html=True)

# ==================== SECTION 1: SCRAPER ====================
if menu == get_text('menu_scraper'):
    st.header(get_text('scraper_header'))
    
    st.info(get_text('scraper_warning'))
    
    categories = {
        get_text('dogs'): "https://sn.coinafrique.com/categorie/chiens",
        get_text('sheep'): "https://sn.coinafrique.com/categorie/moutons",
        get_text('poultry'): "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
        get_text('other_animals'): "https://sn.coinafrique.com/categorie/autres-animaux"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_category = st.selectbox(get_text('category'), list(categories.keys()))
    
    with col2:
        max_pages = st.slider(get_text('num_pages'), 1, 500, 50)
    
    if st.button(get_text('start_scraping'), type="primary"):
        with st.spinner(f"{get_text('scraping_progress')} {selected_category}..."):
            category_name = selected_category.split(' ', 1)[1]
            df_scraped = scrape_all_pages(categories[selected_category], category_name, max_pages)
            
            if not df_scraped.empty:
                st.success(f"✅ {len(df_scraped)} {get_text('success_scraped')}")
                
                save_to_database(df_scraped)
                st.info(get_text('saved_db'))
                
                st.subheader(get_text('preview'))
                st.dataframe(df_scraped)
                
                csv = df_scraped.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"{get_text('download')} {category_name} (CSV)",
                    data=csv,
                    file_name=f'{category_name.lower().replace(" ", "_")}.csv',
                    mime='text/csv',
                )
            else:
                st.warning(get_text('no_data_found'))

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; margin-top: 50px;'>
    <p style='color: #cbd5e0; margin: 0;'>{get_text('developed_by')} <a href='https://sn.coinafrique.com' target='_blank' style='color: #4FD1C5;'>CoinAfrique Sénégal</a></p>
    <p style='font-size: 12px; color: #718096; margin-top: 10px;'>{get_text('rights')}</p>
</div>
""", unsafe_allow_html=True)
