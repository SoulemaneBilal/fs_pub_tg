import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Analyse des Services", layout="wide")

@st.cache_data
def get_data():
    file_path = 'data/processed/etablissements_clean.parquet'
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    return pd.DataFrame()

df = get_data()

st.title("Analyse des Services & Qualité")
st.markdown("---")

if df.empty:
    st.warning("Données non disponibles.")
else:
    services = ['has_accouchement', 'has_vih', 'has_paludisme', 'has_tuberculose', 
                'has_vaccination', 'has_planification_familiale', 'has_urgences', 'has_laboratoire']
    
    # Calculate global KPIs safely
    kpis = {}
    for s in services:
        if s in df.columns:
            kpis[s] = (df[s] == True).mean() * 100
        else:
            kpis[s] = 0.0

    # Row 1 - KPIs Services
    cols = st.columns(5)
    cols[0].metric("% Accouchement", f"{kpis.get('has_accouchement', 0):.1f}%")
    cols[1].metric("% VIH/SIDA", f"{kpis.get('has_vih', 0):.1f}%")
    cols[2].metric("% Laboratoire", f"{kpis.get('has_laboratoire', 0):.1f}%")
    cols[3].metric("% Urgences", f"{kpis.get('has_urgences', 0):.1f}%")
    cols[4].metric("% Vaccination", f"{kpis.get('has_vaccination', 0):.1f}%")
    
    st.markdown("---")

    # Heatmap Region x Service
    st.subheader("Matrice de Couverture")
    if 'region_nom_bdd' in df.columns and any(s in df.columns for s in services):
        available_services = [s for s in services if s in df.columns]
        agg_df = df.groupby('region_nom_bdd')[available_services].mean() * 100
        # Renaming columns for clarity
        agg_df.columns = [s.replace('has_', '').capitalize() for s in agg_df.columns]
        heatmap_fig = px.imshow(
            agg_df.values.T,
            x=agg_df.index,
            y=agg_df.columns,
            color_continuous_scale='RdYlGn',
            aspect="auto",
            title="Pourcentage de couverture par service et par région"
        )
        heatmap_fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(heatmap_fig, use_container_width=True)

    st.markdown("---")

    # Gap analysis: USP sans accouchement ou Hôpital sans urgences
    st.subheader("Gap Analysis (Structures à risque)")
    st.write("Structures manquant de services essentiels pour leur type (ex: USP sans accouchement ou Hôpital sans urgences).")
    gap_df = pd.DataFrame()
    if 'categorie_type' in df.columns and 'has_accouchement' in df.columns:
        gap_mask = (df['categorie_type'] == 'USP') & (df['has_accouchement'] == False)
        if 'has_urgences' in df.columns:
            gap_mask = gap_mask | ((df['categorie_type'] == 'Hôpital') & (df['has_urgences'] == False))
        
        gap_df = df[gap_mask][['nom_fs', 'region_nom_bdd', 'prefecture_nom_bdd', 'categorie_type']]

    if not gap_df.empty:
        st.dataframe(gap_df, use_container_width=True)
    else:
        st.success("Aucune structure à risque détectée ou données insuffisantes.")
