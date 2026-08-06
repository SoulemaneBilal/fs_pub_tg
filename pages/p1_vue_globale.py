import streamlit as st
import plotly.express as px
import pandas as pd
import os

st.set_page_config(page_title="Vue Globale", layout="wide")

@st.cache_data
def get_data():
    file_path = 'data/processed/etablissements_clean.parquet'
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    return pd.DataFrame()

df = get_data()

st.title("Vue d'Ensemble & KPIs Stratégiques")
st.markdown("---")

if df.empty:
    st.warning("Aucune donnée disponible. Veuillez d'abord exécuter le prétraitement des données.")
else:
    # Statistiques basiques pour les KPIs
    total_structures = len(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Structures", total_structures)
    with col2:
        st.metric("Taux de couverture", "À calculer")
        
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Répartition par Type")
        if 'categorie_type' in df.columns:
            fig = px.pie(df, names='categorie_type')
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.subheader("Top Préfectures")
        st.info("Graphique des préfectures à venir...")
