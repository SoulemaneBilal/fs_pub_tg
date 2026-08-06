import streamlit as st
import pandas as pd
import os
import plotly.express as px
from sklearn.cluster import DBSCAN
import folium
from streamlit_folium import st_folium
from folium import plugins
from utils.map_utils import create_base_map, add_markers

@st.cache_data
def get_data():
    file_path = 'data/processed/etablissements_clean.parquet'
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    return pd.DataFrame()

df = get_data()

st.title("Accessibilité Spatiale & Distances")
st.markdown("C'est la page la plus stratégique pour le pilotage de projets.", help="Identification des déserts médicaux et clusters")
st.markdown("---")

if df.empty or 'latitude' not in df.columns:
    st.warning("Données non disponibles ou coordonnées manquantes.")
else:
    df = df.dropna(subset=['latitude', 'longitude']).copy()
    
    if len(df) > 0:
        st.subheader("Matrice des distances et Déserts médicaux")
        st.write("Identification des structures isolées.")
        
        cols_to_show = [c for c in ['nom_fs', 'region_nom_bdd', 'categorie_type'] if c in df.columns]
        st.dataframe(df.head(20)[cols_to_show], use_container_width=True)
        
        st.markdown("---")
        
        # Clustering
        coords = df[['latitude', 'longitude']].values
        db = DBSCAN(eps=0.05, min_samples=2, metric='euclidean').fit(coords)
        df['cluster'] = db.labels_
        df['cluster_str'] = df['cluster'].astype(str)
        df.loc[df['cluster'] == -1, 'cluster_str'] = 'Isolé'

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Analyse spatiale de densité (Déserts médicaux)")
            m_density = create_base_map(center=[8.6, 0.98], zoom=6)
            
            # Création du HeatMap
            heat_data = [[row['latitude'], row['longitude'], row['score_services'] if 'score_services' in row and pd.notna(row['score_services']) else 1] for index, row in df.iterrows()]
            plugins.HeatMap(heat_data, radius=15, blur=10).add_to(m_density)
            
            st_folium(m_density, width="100%", height=500, returned_objects=[], key="density_map")
            
        with col2:
            st.subheader("Clustering Spatial (DBSCAN)")
            st.write("Aggrégation des structures distantes de moins de 5.5km.")
            m_cluster = create_base_map(center=[8.6, 0.98], zoom=6)
            
            color_map = {
                'Isolé': '#e74c3c'  # Rouge pour isolé, les autres auront couleur par défaut
            }
            
            # Utilisation de couleurs par défaut générées pour les autres clusters
            unique_clusters = df['cluster_str'].unique()
            colors = ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e67e22', '#1abc9c', '#34495e']
            for i, c in enumerate(unique_clusters):
                if c != 'Isolé':
                    color_map[c] = colors[i % len(colors)]
                    
            m_cluster = add_markers(
                m_cluster, df, 
                color_col="cluster_str",
                color_map=color_map,
                popup_cols={"cluster_str": "Cluster"},
                radius=6,
                use_cluster=False,
                layer_name="Clusters DBSCAN"
            )
            
            st_folium(m_cluster, width="100%", height=500, returned_objects=[], key="cluster_map")
