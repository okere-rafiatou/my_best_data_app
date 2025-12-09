import streamlit as st
import pandas as pd
import sqlite3
from requests import get
from bs4 import BeautifulSoup as bs
import time
import os

# Configuration de la page
st.set_page_config(page_title="CoinAfrique Animal Scraper", layout="centered")

# Traductions complètes
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
        
        # Menu
        'menu_scraper': '🔍 Scraper des données',
        'menu_download': '📥 Télécharger données Web Scraper',
        'menu_dashboard': '📊 Dashboard (données nettoyées)',
        'menu_forms': '📝 Formulaires d\'évaluation',
        
        # Scraper
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
        
        # Téléchargement
        'download_header': '📥 Télécharger les données brutes (non nettoyées)',
        'download_desc': 'Cette section vous permet de télécharger les données scrapées avec Web Scraper (format brut, sans nettoyage).',
        'files_found': 'fichier(s) CSV trouvé(s) dans le dossier',
        'available_files': '📂 Fichiers CSV disponibles',
        'rows': '📊 Lignes',
        'columns': '📋 Colonnes',
        'size': '💾 Taille',
        'show_data': '👁️ Afficher les données de',
        'download_file': '📥 Télécharger',
        'download_all': '📦 Télécharger toutes les données combinées',
        'combine_download': '🔗 Combiner et télécharger tous les CSV',
        'combined_success': 'lignes combinées depuis',
        'files': 'fichiers',
        'download_combined': '📥 Télécharger toutes les données (CSV)',
        'no_csv_found': '⚠️ Aucun fichier CSV trouvé dans le dossier',
        'advice': '💡 Conseil: Allez dans',
        'to_create': 'pour créer de nouveaux fichiers.',
        'folder_not_exist': '❌ Le dossier data/ n\'existe pas.',
        'create_folder': '💡 Créez un dossier data/ à la racine de votre projet et placez-y vos fichiers CSV.',
        
        # Dashboard
        'dashboard_header': '📊 Dashboard des données nettoyées',
        'total_ads': '📊 Annonces totales',
        'min_price': '💵 Prix min',
        'max_price': '💸 Prix max',
        'stats_by_category': '📈 Statistiques par catégorie',
        'count': 'Nombre',
        'avg_price_cfa': 'Prix moyen (CFA)',
        'min_price_cfa': 'Prix min (CFA)',
        'max_price_cfa': 'Prix max (CFA)',
        'avg_by_category': '💰 Prix moyen par catégorie',
        'ads_by_category': '📊 Nombre d\'annonces par catégorie',
        'top_locations': '📍 Top 10 des localisations',
        'explore_data': '🔍 Explorer les données nettoyées',
        'filter_by_category': 'Filtrer par catégorie',
        'ads_displayed': 'annonces affichées',
        'download_clean': '📥 Télécharger les données nettoyées (CSV)',
        'no_data_scrape_first': 'ℹ️ Aucune donnée disponible. Veuillez d\'abord scraper des données.',
        
        # Formulaires
        'forms_header': '📝 Formulaires d\'évaluation de l\'application',
        'forms_desc': 'Votre avis est important pour nous aider à améliorer cette application. Merci de prendre quelques instants pour répondre à l\'un de ces questionnaires.',
        'kobo_title': '📋 Formulaire KoboToolbox',
        'kobo_desc': 'Remplissez le formulaire d\'évaluation sur KoboToolbox pour nous faire part de votre expérience.',
        'kobo_info': 'Ce formulaire permet une collecte de données structurée et professionnelle.',
        'kobo_button': '🔗 Ouvrir le formulaire KoboToolbox',
        'kobo_note': '💡 KoboToolbox est une plateforme de collecte de données utilisée pour des enquêtes professionnelles.',
        'google_title': '📝 Formulaire Google Forms',
        'google_desc': 'Vous préférez Google Forms ? Remplissez ce formulaire pour partager vos commentaires et suggestions.',
        'google_info': 'Interface simple et familière.',
        'google_button': '🔗 Ouvrir le formulaire Google Forms',
        'google_note': '💡 Google Forms permet un accès rapide et facile depuis n\'importe quel appareil.',
        'why_evaluate': '❓ Pourquoi votre évaluation est importante',
        'continuous_improvement': '🎯 Amélioration continue',
        'improvement_desc': 'Vos retours nous aident à identifier les fonctionnalités à améliorer.',
        'new_features': '💡 Nouvelles fonctionnalités',
        'features_desc': 'Vos suggestions guident le développement de nouvelles features.',
        'user_experience': '🤝 Expérience utilisateur',
        'experience_desc': 'Votre avis façonne l\'évolution de l\'application.',
        'thank_you': '✅ Merci d\'avance pour votre contribution !',
        
        # Animaux
        'dogs': '🐕 Chiens',
        'sheep': '🐑 Moutons',
        'poultry': '🐔 Poules, lapins et pigeons',
        'other_animals': '🦎 Autres animaux',
        
        # Footer
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
        
        # Menu
        'menu_scraper': '🔍 Scrape Data',
        'menu_download': '📥 Download Web Scraper Data',
        'menu_dashboard': '📊 Dashboard (cleaned data)',
        'menu_forms': '📝 Evaluation Forms',
        
        # Scraper
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
        
        # Download
        'download_header': '📥 Download raw data (uncleaned)',
        'download_desc': 'This section allows you to download data scraped with Web Scraper (raw format, without cleaning).',
        'files_found': 'CSV file(s) found in folder',
        'available_files': '📂 Available CSV files',
        'rows': '📊 Rows',
        'columns': '📋 Columns',
        'size': '💾 Size',
        'show_data': '👁️ Show data from',
        'download_file': '📥 Download',
        'download_all': '📦 Download all combined data',
        'combine_download': '🔗 Combine and download all CSVs',
        'combined_success': 'rows combined from',
        'files': 'files',
        'download_combined': '📥 Download all data (CSV)',
        'no_csv_found': '⚠️ No CSV file found in folder',
        'advice': '💡 Tip: Go to',
        'to_create': 'to create new files.',
        'folder_not_exist': '❌ The data/ folder does not exist.',
        'create_folder': '💡 Create a data/ folder at the root of your project and place your CSV files there.',
        
        # Dashboard
        'dashboard_header': '📊 Dashboard of cleaned data',
        'total_ads': '📊 Total Ads',
        'min_price': '💵 Min Price',
        'max_price': '💸 Max Price',
        'stats_by_category': '📈 Statistics by category',
        'count': 'Count',
        'avg_price_cfa': 'Average price (CFA)',
        'min_price_cfa': 'Min price (CFA)',
        'max_price_cfa': 'Max price (CFA)',
        'avg_by_category': '💰 Average price by category',
        'ads_by_category': '📊 Number of ads by category',
        'top_locations': '📍 Top 10 locations',
        'explore_data': '🔍 Explore cleaned data',
        'filter_by_category': 'Filter by category',
        'ads_displayed': 'ads displayed',
        'download_clean': '📥 Download cleaned data (CSV)',
        'no_data_scrape_first': 'ℹ️ No data available. Please scrape data first.',
        
        # Forms
        'forms_header': '📝 Application Evaluation Forms',
        'forms_desc': 'Your feedback is important to help us improve this application. Thank you for taking a few moments to answer one of these questionnaires.',
        'kobo_title': '📋 KoboToolbox Form',
        'kobo_desc': 'Fill out the evaluation form on KoboToolbox to share your experience with us.',
        'kobo_info': 'This form allows for structured and professional data collection.',
        'kobo_button': '🔗 Open KoboToolbox form',
        'kobo_note': '💡 KoboToolbox is a data collection platform used for professional surveys.',
        'google_title': '📝 Google Forms',
        'google_desc': 'Prefer Google Forms? Fill out this form to share your comments and suggestions.',
        'google_info': 'Simple and familiar interface.',
        'google_button': '🔗 Open Google Forms',
        'google_note': '💡 Google Forms allows quick and easy access from any device.',
        'why_evaluate': '❓ Why your evaluation is important',
        'continuous_improvement': '🎯 Continuous improvement',
        'improvement_desc': 'Your feedback helps us identify features to improve.',
        'new_features': '💡 New features',
        'features_desc': 'Your suggestions guide the development of new features.',
        'user_experience': '🤝 User experience',
        'experience_desc': 'Your feedback shapes the evolution of the application.',
        'thank_you': '✅ Thank you in advance for your contribution!',
        
        # Animals
        'dogs': '🐕 Dogs',
        'sheep': '🐑 Sheep',
        'poultry': '🐔 Chickens, rabbits and pigeons',
        'other_animals': '🦎 Other animals',
        
        # Footer
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
        max-width: 1500px;
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
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
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
    if not os.path.exists('data'):
        os.makedirs('data')
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

# ==================== SECTION 2: TÉLÉCHARGER DONNÉES ====================
elif menu == get_text('menu_download'):
    st.header(get_text('download_header'))
    
    st.markdown(get_text('download_desc'))
    
    data_folder = "data"
    
    if os.path.exists(data_folder):
        csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
        
        if csv_files:
            st.success(f"✅ {len(csv_files)} {get_text('files_found')} `data/`")
            
            st.subheader(get_text('available_files'))
            
            for idx, file in enumerate(csv_files, 1):
                with st.expander(f"📄 {file}"):
                    try:
                        df_file = pd.read_csv(os.path.join(data_folder, file))
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(get_text('rows'), df_file.shape[0])
                        with col2:
                            st.metric(get_text('columns'), df_file.shape[1])
                        with col3:
                            file_size = os.path.getsize(os.path.join(data_folder, file)) / 1024
                            st.metric(get_text('size'), f"{file_size:.1f} KB")
                        
                        if st.button(f"{get_text('show_data')} {file}", key=f"show_{idx}"):
                            st.dataframe(df_file, use_container_width=True)
                        
                        csv_bytes = df_file.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label=f"{get_text('download_file')} {file}",
                            data=csv_bytes,
                            file_name=file,
                            mime="text/csv",
                            key=f"download_{idx}"
                        )
                    except Exception as e:
                        st.error(f"❌ {str(e)}")
            
            st.markdown("---")
            st.subheader(get_text('download_all'))
            
            if st.button(get_text('combine_download')):
                try:
                    all_dfs = []
                    for file in csv_files:
                        df_temp = pd.read_csv(os.path.join(data_folder, file))
                        all_dfs.append(df_temp)
                    
                    df_combined = pd.concat(all_dfs, ignore_index=True)
                    st.success(f"✅ {len(df_combined)} {get_text('combined_success')} {len(csv_files)} {get_text('files')}")
                    
                    st.dataframe(df_combined.head(10), use_container_width=True)
                    
                    csv_combined = df_combined.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label=get_text('download_combined'),
                        data=csv_combined,
                        file_name="coinafrique_animals_all_combined.csv",
                        mime="text/csv",
                    )
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        else:
            st.warning(get_text('no_csv_found') + " `data/`")
            st.info(f"{get_text('advice')} **{get_text('menu_scraper')}** {get_text('to_create')}")
    else:
        st.error(get_text('folder_not_exist'))
        st.info(get_text('create_folder'))

# ==================== SECTION 3: DASHBOARD ====================
elif menu == get_text('menu_dashboard'):
    st.header(get_text('dashboard_header'))
    
    df_raw = load_from_database()
    
    if not df_raw.empty:
        df_clean = clean_data(df_raw)
        
        # Métriques principales avec design amélioré
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; text-align: center;'>
                <p style='color: white; font-size: 14px; margin: 0;'>📊 """ + get_text('total_ads') + """</p>
                <p style='color: white; font-size: 32px; font-weight: bold; margin: 10px 0;'>""" + str(len(df_clean)) + """</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 15px; text-align: center;'>
                <p style='color: white; font-size: 14px; margin: 0;'>💰 """ + get_text('avg_price') + """</p>
                <p style='color: white; font-size: 32px; font-weight: bold; margin: 10px 0;'>""" + f"{df_clean['price_clean'].mean():,.0f}" + """</p>
                <p style='color: white; font-size: 12px; margin: 0;'>CFA</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 15px; text-align: center;'>
                <p style='color: white; font-size: 14px; margin: 0;'>💵 """ + get_text('min_price') + """</p>
                <p style='color: white; font-size: 32px; font-weight: bold; margin: 10px 0;'>""" + f"{df_clean['price_clean'].min():,.0f}" + """</p>
                <p style='color: white; font-size: 12px; margin: 0;'>CFA</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 20px; border-radius: 15px; text-align: center;'>
                <p style='color: white; font-size: 14px; margin: 0;'>💸 """ + get_text('max_price') + """</p>
                <p style='color: white; font-size: 32px; font-weight: bold; margin: 10px 0;'>""" + f"{df_clean['price_clean'].max():,.0f}" + """</p>
                <p style='color: white; font-size: 12px; margin: 0;'>CFA</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Statistiques par catégorie
        st.subheader(get_text('stats_by_category'))
        category_stats = df_clean.groupby('category').agg({
            'price_clean': ['count', 'mean', 'min', 'max']
        }).round(0)
        category_stats.columns = [get_text('count'), get_text('avg_price_cfa'), get_text('min_price_cfa'), get_text('max_price_cfa')]
        st.dataframe(category_stats, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Graphiques avec Plotly
        import plotly.express as px
        import plotly.graph_objects as go
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(get_text('avg_by_category'))
            avg_prices = df_clean.groupby('category')['price_clean'].mean().sort_values(ascending=False).reset_index()
            fig1 = px.bar(avg_prices, x='category', y='price_clean',
                         color='price_clean',
                         color_continuous_scale='Viridis',
                         labels={'price_clean': 'Prix moyen (CFA)', 'category': 'Catégorie'},
                         title='')
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader(get_text('ads_by_category'))
            counts = df_clean['category'].value_counts().reset_index()
            counts.columns = ['category', 'count']
            fig2 = px.pie(counts, values='count', names='category',
                         color_discrete_sequence=px.colors.qualitative.Set3,
                         title='',
                         hole=0.4)
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Distribution des prix
        st.subheader("📊 Distribution des prix")
        fig3 = px.box(df_clean, x='category', y='price_clean',
                     color='category',
                     color_discrete_sequence=px.colors.qualitative.Pastel,
                     labels={'price_clean': 'Prix (CFA)', 'category': 'Catégorie'},
                     title='')
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Top localisations
        st.subheader(get_text('top_locations'))
        top_locations = df_clean['address'].value_counts().head(10).reset_index()
        top_locations.columns = ['address', 'count']
        fig4 = px.bar(top_locations, x='count', y='address',
                     orientation='h',
                     color='count',
                     color_continuous_scale='Plasma',
                     labels={'count': 'Nombre d\'annonces', 'address': 'Localisation'},
                     title='')
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            showlegend=False,
            height=450
        )
        st.plotly_chart(fig4, use_container_width=True)
        
        # Analyse des prix par localisation (top 10)
        st.subheader("💰 Prix moyen par localisation (Top 10)")
        top_10_locations = df_clean['address'].value_counts().head(10).index
        df_top_locations = df_clean[df_clean['address'].isin(top_10_locations)]
        avg_price_location = df_top_locations.groupby('address')['price_clean'].mean().sort_values(ascending=False).reset_index()
        
        fig5 = px.bar(avg_price_location, x='address', y='price_clean',
                     color='price_clean',
                     color_continuous_scale='Blues',
                     labels={'price_clean': 'Prix moyen (CFA)', 'address': 'Localisation'},
                     title='')
        fig5.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            showlegend=False,
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig5, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Explorer les données
        st.subheader(get_text('explore_data'))
        
        selected_cat = st.multiselect(
            get_text('filter_by_category'),
            options=df_clean['category'].unique(),
            default=df_clean['category'].unique()
        )
        
        df_filtered = df_clean[df_clean['category'].isin(selected_cat)]
        
        st.write(f"**{len(df_filtered)}** {get_text('ads_displayed')}")
        st.dataframe(df_filtered[['category', 'name', 'price', 'price_clean', 'address']], use_container_width=True)
        
        csv_clean = df_clean.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=get_text('download_clean'),
            data=csv_clean,
            file_name='coinafrique_animals_clean.csv',
            mime='text/csv',
        )
        
    else:
        st.info(get_text('no_data_scrape_first'))
# ==================== SECTION 4: FORMULAIRES ====================
elif menu == get_text('menu_forms'):
    st.header(get_text('forms_header'))
    
    st.markdown(get_text('forms_desc'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(get_text('kobo_title'))
        st.markdown(get_text('kobo_desc'))
        st.markdown(get_text('kobo_info'))
        
        st.link_button(
            get_text('kobo_button'),
            "https://ee.kobotoolbox.org/x/JWIzi1ib",
            use_container_width=True
        )
        
        st.markdown("---")
        st.info(get_text('kobo_note'))
    
    with col2:
        st.subheader(get_text('google_title'))
        st.markdown(get_text('google_desc'))
        st.markdown(get_text('google_info'))
        
        st.link_button(
            get_text('google_button'),
            "https://docs.google.com/forms/d/e/1FAIpQLSfZWFZCFv5vK3ULo0TK5kJAhojavgBRrAk8LJhT64afKlnhYw/viewform?usp=dialog",
            use_container_width=True
        )
        
        st.markdown("---")
        st.info(get_text('google_note'))
    
    st.markdown("---")
    
    st.subheader(get_text('why_evaluate'))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        ### {get_text('continuous_improvement')}
        {get_text('improvement_desc')}
        """)
    
    with col2:
        st.markdown(f"""
        ### {get_text('new_features')}
        {get_text('features_desc')}
        """)
    
    with col3:
        st.markdown(f"""
        ### {get_text('user_experience')}
        {get_text('experience_desc')}
        """)
    
    st.success(get_text('thank_you'))

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; margin-top: 50px;'>
    <p style='color: #cbd5e0; margin: 0;'>{get_text('developed_by')} <a href='https://sn.coinafrique.com' target='_blank' style='color: #4FD1C5;'>CoinAfrique Sénégal</a></p>
    <p style='font-size: 12px; color: #718096; margin-top: 10px;'>{get_text('rights')}</p>
</div>
""", unsafe_allow_html=True)

