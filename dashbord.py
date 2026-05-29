import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.wkt import loads
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Dashboard Décisionnel - Santé Togo", layout="wide")

# Fonction de nettoyage des services
def clean_services(val):
    if pd.isna(val):
        return []
    cleaned = val.strip("{}")
    if not cleaned:
        return []
    return [s.strip() for s in cleaned.split(',')]

# Chargement et mise en cache des données
@st.cache_data
def load_data():
    missing_values = ["N/a", "N/A", "na", "NA", "None", "", "Nsp", "nan", "NaN"]
    df = pd.read_csv("Formations sanitaires  Publiques.csv", na_values=missing_values)
    df['geometry'] = df['geometry'].apply(loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    
    gdf['services_nettoyes'] = gdf['services_proposes'].apply(clean_services)
    gdf['annee'] = pd.to_numeric(gdf['annee'], errors='coerce')
    return gdf

gdf = load_data()

# Titre principal orienté Décisionnel
st.title("🇹🇬 Dashbord ded Infrastructures Sanitaires du Togo")
st.markdown("---")

# BARRE LATÉRALE - FILTRES STRATÉGIQUES
st.sidebar.header("Filtres")

regions = ["Toutes"] + list(gdf['region_nom_bdd'].unique())
selected_region = st.sidebar.selectbox("Région Administrative", regions)

types = ["Tous"] + list(gdf['etablissement_type'].unique())
selected_type = st.sidebar.selectbox("Type / Niveau de Spécialité", types)

all_services = sorted(list(set([svc for sublist in gdf['services_nettoyes'] for svc in sublist])))
selected_services = st.sidebar.multiselect("Disponibilité des Services de Soins", all_services)

# Application des filtres
gdf_filtered = gdf.copy()
if selected_region != "Toutes":
    gdf_filtered = gdf_filtered[gdf_filtered['region_nom_bdd'] == selected_region]
if selected_type != "Tous":
    gdf_filtered = gdf_filtered[gdf_filtered['etablissement_type'] == selected_type]
if selected_services:
    gdf_filtered = gdf_filtered[gdf_filtered['services_nettoyes'].apply(lambda x: all(svc in x for svc in selected_services))]

# INDICATEURS CLÉS (KPIs)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Infrastructures Sélectionnées", f"{gdf_filtered.shape[0]} / {gdf.shape[0]}")
with col2:
    st.metric("Régions Impactées", f"{gdf_filtered['region_nom_bdd'].nunique()} / {gdf['region_nom_bdd'].nunique()}")
with col3:
    st.metric("Préfectures Couvertes", f"{gdf_filtered['prefecture_nom_bdd'].nunique()}")
with col4:
    total_services = len(set([svc for sublist in gdf_filtered['services_nettoyes'] for svc in sublist]))
    st.metric("Types de Soins Uniques", f"{total_services}")

st.markdown("---")

# ORGANISATION EN ONGLETS POUR UNE ANALYSE EXHAUSTIVE
tab1, tab2, tab3 = st.tabs(["Analyses Statisques & Spécialités", "Évolution Temporelle", "Cartographie & Densité (Heatmap)"])

# ONGLET 1 : STATISTIQUES ET SPÉCIALITÉS
with tab1:
    st.subheader("Répartition Géographique et Spécialisation des Structures")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        if not gdf_filtered.empty:
            st.markdown("**Top Préfectures par volume d'infrastructures**")
            data_pref = gdf_filtered['prefecture_nom_bdd'].value_counts().head(10).reset_index()
            data_pref.columns = ['Préfecture', 'Nombre de structures']
            fig_pref = px.bar(data_pref, x='Nombre de structures', y='Préfecture', orientation='h',
                              color='Nombre de structures', color_continuous_scale='Viridis', height=350)
            fig_pref.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_pref, width="stretch")
        else:
            st.info("Aucune donnée.")

    with col_chart2:
        if not gdf_filtered.empty:
            st.markdown("**Niveau de Spécialité (Typologie des Centres)**")
            data_type = gdf_filtered['etablissement_type'].value_counts().reset_index()
            data_type.columns = ['Type d\'établissement', 'Total']
            fig_type = px.pie(data_type, values='Total', names='Type d\'établissement', 
                              hole=0.4, color_discrete_sequence=px.colors.sequential.Plotly3, height=350)
            fig_type.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_type, width="stretch")

    st.markdown("**Vue tabulaire des structures sélectionnées**")
    st.dataframe(gdf_filtered[['nom_fs', 'etablissement_type', 'region_nom_bdd', 'prefecture_nom_bdd', 'canton_nom_bdd']], height=250, width="stretch")

# ONGLET 2 : ÉVOLUTION TEMPORELLE
with tab2:
    st.subheader("Analyse de la Trajectoire Temporelle des Infrastructures")
    
    # Filtrage des lignes ayant une année valide
    df_time = gdf_filtered[gdf_filtered['annee'].notnull()].copy()
    
    if not df_time.empty:
        df_time['annee'] = df_time['annee'].astype(int)
        
        # Calcul du cumul historique
        time_counts = df_time['annee'].value_counts().sort_index().reset_index()
        time_counts.columns = ['Année', 'Nouvelles Ouvertures']
        time_counts['Cumul Historique'] = time_counts['Nouvelles Ouvertures'].cumsum()
        
        fig_time = px.line(
            time_counts, 
            x='Année', 
            y='Cumul Historique', 
            title="Croissance cumulée du réseau sanitaire public (Perspective historique depuis 1900)",
            markers=True, 
            labels={'Cumul Historique': 'Nombre total de structures'},
            color_discrete_sequence=['#1f77b4'],
            range_x=[1900, 2026] 
        )
        
        fig_time.update_layout(
            height=400,
            xaxis=dict(
                tickmode='linear',
                tick0=1900,
                dtick=10 
            )
        )
        st.plotly_chart(fig_time, width="stretch")
        
        # Métrique additionnelle pour l'aide à la décision
        recent_openings = df_time[df_time['annee'] >= 2015].shape[0]
        st.info(f"**Note d'analyse :** {recent_openings} structures de la sélection actuelle ont été ouvertes depuis 2015.")
    else:
        st.warning("Les données temporelles ne sont pas disponibles pour les critères sélectionnés.")
# ONGLET 3 : CARTOGRAPHIE ET CARTE DE CHALEUR (HEATMAP)
with tab3:
    st.subheader("Visualisation de la Densité Spatiale")
    
    if not gdf_filtered.empty:
        lat_c = gdf_filtered['geometry'].y.mean()
        lon_c = gdf_filtered['geometry'].x.mean()
        
        # Sélecteur de mode de visualisation cartographique
        map_mode = st.radio("Mode de visualisation :", ["Carte de Chaleur (Densité)", "Marqueurs Individuels (Détails)"], horizontal=True)
        
        m = folium.Map(location=[lat_c, lon_c], zoom_start=8, tiles="OpenStreetMap")
        
        if map_mode == "Carte de Chaleur (Densité)":
            # Extraction des listes de [latitude, longitude] pour la HeatMap
            heat_data = [[row['geometry'].y, row['geometry'].x] for idx, row in gdf_filtered.iterrows()]
            # Ajout de la couche HeatMap
            HeatMap(heat_data, radius=15, blur=10, min_opacity=0.4).add_to(m)
            st.markdown("*Les zones rouges/oranges représentent les plus fortes concentrations d'infrastructures de santé publiques.*")
        
        else:
            from folium.plugins import MarkerCluster
            marker_cluster = MarkerCluster().add_to(m)
            for idx, row in gdf_filtered.iterrows():
                annee_txt = str(int(row['annee'])) if pd.notnull(row['annee']) else 'Inconnue'
                services_txt = ", ".join(row['services_nettoyes']) if row['services_nettoyes'] else "Non renseignés"
                
                popup_text = f"""
                <div style="font-family: Arial; width: 220px;">
                    <h4 style="color: #2c3e50; margin-bottom:5px;">{row['nom_fs']}</h4>
                    <b>Type :</b> {row['etablissement_type']}<br>
                    <b>Préfecture :</b> {row['prefecture_nom_bdd']}<br>
                    <b>Année :</b> {annee_txt}<br>
                    <details><summary><b>Services</b></summary><span style="font-size:11px; color:#555;">{services_txt}</span></details>
                </div>
                """
                folium.Marker(location=[row['geometry'].y, row['geometry'].x],
                              popup=folium.Popup(popup_text, max_width=250),
                              tooltip=row['nom_fs']).add_to(marker_cluster)
        
        # Affichage de la carte
        st_folium(m, width=1100, height=550)
    else:
        st.warning("Aucune structure disponible pour générer la cartographie.")