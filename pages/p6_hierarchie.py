import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from streamlit_folium import st_folium
import folium
from utils.map_utils import create_base_map, add_markers

st.set_page_config(page_title="Drill-down Hiérarchique", layout="wide")

@st.cache_data
def get_data():
    file_path = 'data/processed/etablissements_clean.parquet'
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    return pd.DataFrame()

df = get_data()

st.title("Drill-down : Région → Préfecture → Commune → Canton")
st.markdown("---")

if df.empty:
    st.warning("Données non disponibles.")
else:
    regions = df['region_nom_bdd'].dropna().unique().tolist() if 'region_nom_bdd' in df.columns else []
    
    col_filters, col_content = st.columns([1, 3])
    
    with col_filters:
        st.subheader("Sélecteurs en cascade")
        selected_region = st.selectbox("Région", [""] + regions, index=0)
        
        prefs = []
        if selected_region and 'prefecture_nom_bdd' in df.columns:
            prefs = df[df['region_nom_bdd'] == selected_region]['prefecture_nom_bdd'].dropna().unique().tolist()
            
        selected_prefecture = st.selectbox("Préfecture", [""] + prefs, index=0)
        
        coms = []
        if selected_prefecture and 'commune_nom_bdd' in df.columns:
            coms = df[df['prefecture_nom_bdd'] == selected_prefecture]['commune_nom_bdd'].dropna().unique().tolist()
            
        selected_commune = st.selectbox("Commune", [""] + coms, index=0)
        
        st.button("Générer le rapport PDF", type="primary", use_container_width=True)
        
    with col_content:
        st.subheader("Vue synthétique de la zone (Radar Chart & Détails)")
        
        filtered_df = df.copy()
        if selected_region:
            filtered_df = filtered_df[filtered_df['region_nom_bdd'] == selected_region]
        if selected_prefecture:
            filtered_df = filtered_df[filtered_df['prefecture_nom_bdd'] == selected_prefecture]
        if selected_commune:
            filtered_df = filtered_df[filtered_df['commune_nom_bdd'] == selected_commune]
            
        col_radar, col_map = st.columns(2)
        
        with col_radar:
            avg_nat_services = df['score_services'].mean() if 'score_services' in df.columns else 0
            avg_loc_services = filtered_df['score_services'].mean() if 'score_services' in filtered_df.columns else 0
            
            avg_nat_jours = df['score_accessibilite'].mean() if 'score_accessibilite' in df.columns else 0
            avg_loc_jours = filtered_df['score_accessibilite'].mean() if 'score_accessibilite' in filtered_df.columns else 0
            
            categories = ['Score Services', 'Jours d\'ouverture', 'Couverture Accouchement', 'Couverture Labo']
            
            val_nat = [
                avg_nat_services, avg_nat_jours, 
                df['has_accouchement'].mean()*10 if 'has_accouchement' in df.columns else 0,
                df['has_laboratoire'].mean()*10 if 'has_laboratoire' in df.columns else 0
            ]
            
            val_loc = [
                avg_loc_services, avg_loc_jours,
                filtered_df['has_accouchement'].mean()*10 if 'has_accouchement' in filtered_df.columns else 0,
                filtered_df['has_laboratoire'].mean()*10 if 'has_laboratoire' in filtered_df.columns else 0
            ]
            
            if len(filtered_df) > 0:
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(r=val_nat, theta=categories, fill='toself', name='Moyenne Nationale'))
                fig_radar.add_trace(go.Scatterpolar(r=val_loc, theta=categories, fill='toself', name='Zone Sélectionnée'))
                
                max_val = max([v for v in val_nat + val_loc if not pd.isna(v)] or [0])
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max_val + 1])), showlegend=True, margin=dict(l=30, r=30, t=30, b=30))
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("Pas de données pour ce filtre.")
                
        with col_map:
            if 'latitude' in filtered_df.columns and not filtered_df.empty:
                # Center map on the filtered points
                center_lat = filtered_df['latitude'].mean() if not filtered_df['latitude'].empty else 8.6
                center_lon = filtered_df['longitude'].mean() if not filtered_df['longitude'].empty else 0.98
                
                m = create_base_map(center=[center_lat, center_lon], zoom=9)
                
                color_map = {
                    "USP": "#5DADE2",
                    "Hôpital": "#00A86B",
                    "Spécialisé": "#8E44AD",
                    "Autre": "#E67E22"
                }
                
                m = add_markers(
                    m, filtered_df, 
                    color_col="categorie_type" if 'categorie_type' in filtered_df.columns else None,
                    color_map=color_map,
                    popup_cols={"categorie_type": "Catégorie", "secteur": "Secteur"},
                    radius=6,
                    use_cluster=True,
                    layer_name="Structures Filtrées"
                )
                
                st_folium(m, width="100%", height=400, returned_objects=[], key="hierarchy_map")
            else:
                st.info("Carte non disponible.")
                
        st.markdown("---")
        st.subheader("Détail des structures")
        
        if not filtered_df.empty:
            disp_cols = ['nom_fs', 'categorie_type', 'secteur', 'score_services', 'score_accessibilite']
            disp_cols = [c for c in disp_cols if c in filtered_df.columns]
            st.dataframe(filtered_df[disp_cols].head(50), use_container_width=True)
        else:
            st.info("Aucune structure à afficher.")
