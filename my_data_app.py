import streamlit as st
import pandas as pd
import sqlite3
from requests import get
from bs4 import BeautifulSoup as bs
import time
from io import BytesIO

# Configuration de la page
st.set_page_config(page_title="CoinAfrique Animal Scraper", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF6B35;'>🐾 CoinAfrique Animal Data App</h1>", unsafe_allow_html=True)

st.markdown("""
Cette application vous permet de :
* **Scraper des données** d'animaux sur plusieurs pages de CoinAfrique
* **Télécharger des données** déjà scrapées (non nettoyées)
* **Visualiser un dashboard** avec les données nettoyées
* **Remplir un formulaire** d'évaluation de l'application

**Librairies Python:** pandas, streamlit, sqlite3, beautifulsoup4, requests
**Source de données:** [CoinAfrique Sénégal](https://sn.coinafrique.com/)
""")

# Fonction pour créer la base de données SQLite
def init_database():
    conn = sqlite3.connect('coinafrique_animals.db')
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

# Fonction de scraping
def scrape_category(base_url, category_name, max_pages=10):
    df = pd.DataFrame()
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?page={page}"
            res = get(url, timeout=10)
            soup = bs(res.content, 'html.parser')
            containers = soup.find_all('div', class_='col s6 m4 l3')
            
            if not containers:
                break
            
            data = []
            for container in containers:
                try:
                    name = container.find('p', 'ad__card-description').text.strip()
                    price = container.find('p', 'ad__card-price').text.replace('CFA', '').replace(' ', '').strip()
                    adresse = container.find('p', 'ad__card-location').span.text.strip()
                    image_url = container.find('img', class_='ad__card-img')['src']
                    
                    dic = {
                        'category': category_name,
                        'name': name,
                        'price': price,
                        'address': adresse,
                        'image_url': image_url,
                        'scrape_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    data.append(dic)
                except:
                    pass
            
            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis=0).reset_index(drop=True)
            time.sleep(1)  # Pause entre les pages
            
        except Exception as e:
            st.warning(f"Erreur page {page}: {str(e)}")
            break
    
    return df

# Fonction pour nettoyer les données
def clean_data(df):
    df_clean = df.copy()
    
    # Nettoyer les prix
    df_clean['price_clean'] = df_clean['price'].str.replace(r'\D', '', regex=True)
    df_clean['price_clean'] = pd.to_numeric(df_clean['price_clean'], errors='coerce')
    
    # Supprimer les doublons
    df_clean = df_clean.drop_duplicates(subset=['name', 'address'])
    
    # Supprimer les lignes avec des valeurs manquantes importantes
    df_clean = df_clean.dropna(subset=['name', 'price_clean'])
    
    return df_clean

# Fonction pour sauvegarder dans SQLite
def save_to_database(df):
    conn = sqlite3.connect('coinafrique_animals.db')
    df.to_sql('animals', conn, if_exists='append', index=False)
    conn.close()

# Fonction pour charger depuis SQLite
def load_from_database():
    conn = sqlite3.connect('coinafrique_animals.db')
    df = pd.read_sql_query("SELECT * FROM animals", conn)
    conn.close()
    return df

# Initialiser la base de données
init_database()

# Sidebar pour la navigation
menu = st.sidebar.radio("Menu", ["🔍 Scraper des données", "📥 Télécharger données brutes", "📊 Dashboard", "📝 Formulaire d'évaluation"])

# SECTION 1: Scraper des données
if menu == "🔍 Scraper des données":
    st.header("Scraper des données CoinAfrique")
    
    categories = {
        "Chiens": "https://sn.coinafrique.com/categorie/chiens",
        "Moutons": "https://sn.coinafrique.com/categorie/moutons",
        "Poules, lapins et pigeons": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
        "Autres animaux": "https://sn.coinafrique.com/categorie/autres-animaux"
    }
    
    selected_category = st.selectbox("Sélectionner une catégorie", list(categories.keys()))
    max_pages = st.slider("Nombre de pages à scraper", 1, 20, 5)
    
    if st.button("🚀 Lancer le scraping", key="scrape_btn"):
        with st.spinner(f"Scraping en cours pour {selected_category}..."):
            df_scraped = scrape_category(categories[selected_category], selected_category, max_pages)
            
            if not df_scraped.empty:
                st.success(f"✅ {len(df_scraped)} annonces scrapées !")
                
                # Sauvegarder dans la base de données
                save_to_database(df_scraped)
                st.info("💾 Données sauvegardées dans la base de données SQLite")
                
                # Afficher un aperçu
                st.subheader("Aperçu des données scrapées")
                st.dataframe(df_scraped)
            else:
                st.warning("Aucune donnée trouvée.")

# SECTION 2: Télécharger données brutes
elif menu == "📥 Télécharger données brutes":
    st.header("Télécharger les données brutes (non nettoyées)")
    
    try:
        df_raw = load_from_database()
        
        if not df_raw.empty:
            st.write(f"**Total d'annonces:** {len(df_raw)}")
            st.write(f"**Dimensions:** {df_raw.shape[0]} lignes × {df_raw.shape[1]} colonnes")
            
            # Grouper par catégorie
            category_counts = df_raw['category'].value_counts()
            st.write("**Répartition par catégorie:**")
            st.dataframe(category_counts)
            
            # Bouton de téléchargement
            csv = df_raw.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger toutes les données (CSV)",
                data=csv,
                file_name='coinafrique_animals_raw.csv',
                mime='text/csv',
            )
            
            # Afficher les données
            if st.checkbox("Afficher toutes les données"):
                st.dataframe(df_raw)
        else:
            st.info("Aucune donnée disponible. Veuillez d'abord scraper des données.")
    except Exception as e:
        st.error(f"Erreur lors du chargement: {str(e)}")

# SECTION 3: Dashboard
elif menu == "📊 Dashboard":
    st.header("Dashboard des données nettoyées")
    
    try:
        df_raw = load_from_database()
        
        if not df_raw.empty:
            df_clean = clean_data(df_raw)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total d'annonces", len(df_clean))
            with col2:
                st.metric("Prix moyen", f"{df_clean['price_clean'].mean():,.0f} CFA")
            with col3:
                st.metric("Catégories", df_clean['category'].nunique())
            
            st.subheader("📈 Statistiques par catégorie")
            category_stats = df_clean.groupby('category').agg({
                'price_clean': ['count', 'mean', 'min', 'max']
            }).round(0)
            category_stats.columns = ['Nombre', 'Prix moyen', 'Prix min', 'Prix max']
            st.dataframe(category_stats)
            
            st.subheader("💰 Distribution des prix")
            st.bar_chart(df_clean.groupby('category')['price_clean'].mean())
            
            st.subheader("📍 Répartition par localisation")
            top_locations = df_clean['address'].value_counts().head(10)
            st.bar_chart(top_locations)
            
            st.subheader("🔍 Explorer les données nettoyées")
            st.dataframe(df_clean)
            
            # Télécharger les données nettoyées
            csv_clean = df_clean.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger les données nettoyées (CSV)",
                data=csv_clean,
                file_name='coinafrique_animals_clean.csv',
                mime='text/csv',
            )
        else:
            st.info("Aucune donnée disponible. Veuillez d'abord scraper des données.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

# SECTION 4: Formulaire d'évaluation
elif menu == "📝 Formulaire d'évaluation":
    st.header("Formulaire d'évaluation de l'application")
    
    with st.form("evaluation_form"):
        st.subheader("Votre avis compte !")
        
        nom = st.text_input("Nom (optionnel)")
        email = st.text_input("Email (optionnel)")
        
        rating = st.slider("Notez l'application", 1, 5, 3)
        
        ease_of_use = st.select_slider(
            "Facilité d'utilisation",
            options=["Très difficile", "Difficile", "Moyen", "Facile", "Très facile"]
        )
        
        features = st.multiselect(
            "Quelles fonctionnalités avez-vous utilisées ?",
            ["Scraping", "Téléchargement", "Dashboard", "Toutes"]
        )
        
        feedback = st.text_area("Commentaires et suggestions")
        
        submit = st.form_submit_button("Soumettre l'évaluation")
        
        if submit:
            # Sauvegarder l'évaluation
            evaluation_data = {
                'nom': nom,
                'email': email,
                'rating': rating,
                'ease_of_use': ease_of_use,
                'features': ', '.join(features),
                'feedback': feedback,
                'date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            conn = sqlite3.connect('coinafrique_animals.db')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS evaluations
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          nom TEXT, email TEXT, rating INTEGER,
                          ease_of_use TEXT, features TEXT,
                          feedback TEXT, date TEXT)''')
            
            pd.DataFrame([evaluation_data]).to_sql('evaluations', conn, if_exists='append', index=False)
            conn.close()
            
            st.success("✅ Merci pour votre évaluation !")
            st.balloons()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Développé avec ❤️ par Streamlit | Données de CoinAfrique Sénégal</p>
</div>
""", unsafe_allow_html=True)

