import streamlit as st
import pandas as pd
import os
from streamlit_folium import st_folium
import folium
from utils.map_utils import create_base_map, add_markers
import plotly.express as px

st.set_page_config(page_title="Cartographie", layout="wide")

@st.cache_data
def get_data():
    file_path = 'data/processed/etablissements_clean.parquet'
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    return pd.DataFrame()

df = get_data()

st.title("Cartographie des Formations Sanitaires")

if df.empty:
    st.warning("Données non disponibles.")
elif 'latitude' not in df.columns or 'longitude' not in df.columns:
    st.error("Coordonnées GPS manquantes dans les données.")
else:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Filtres Cartographiques")
        
        # Filtre type de structure
        types_dispos = df['categorie_type'].dropna().unique().tolist() if 'categorie_type' in df.columns else []
        selected_types = st.multiselect("Type de structure:", types_dispos, default=types_dispos)
        
        # Apply filter
        df_filtered = df[df['categorie_type'].isin(selected_types)] if selected_types else df
        
        st.markdown("---")
        st.subheader("Mini distribution par région :")
        if 'region_nom_bdd' in df_filtered.columns:
            fig_hist = px.histogram(df_filtered, y='region_nom_bdd', title="")
            st.plotly_chart(fig_hist, use_container_width=True)
            
    with col2:
        # Configuration des couleurs
        color_map = {
            "USP": "#5DADE2",
            "Hôpital": "#00A86B",
            "Spécialisé": "#8E44AD",
            "Autre": "#E67E22"
        }
        
        m = create_base_map(center=[8.6, 0.98], zoom=7)
        
        popup_cols = {
            "etablissement_type": "Type détaillé",
            "categorie_type": "Catégorie",
            "score_services": "Score des services"
        }
        
        m = add_markers(
            m, df_filtered, 
            color_col="categorie_type" if 'categorie_type' in df_filtered.columns else None,
            color_map=color_map,
            popup_cols=popup_cols,
            radius=6,
            use_cluster=True,
            layer_name="Formations Sanitaires"
        )
        
        # Ajout du contrôle des couches
        folium.LayerControl().add_to(m)
        
        st_folium(m, width="100%", height=600, returned_objects=[])
