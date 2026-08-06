import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Évolution Temporelle", layout="wide")

@st.cache_data
def get_data():
    file_path = 'data/processed/etablissements_clean.parquet'
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    return pd.DataFrame()

df = get_data()

st.title("Évolution Temporelle & Vieillissement")
st.markdown("---")

if df.empty:
    st.warning("Données non disponibles.")
else:
    if 'annee' in df.columns:
        df_annee = df.dropna(subset=['annee']).copy()
        df_annee['annee'] = pd.to_numeric(df_annee['annee'], errors='coerce')
        df_annee = df_annee.dropna(subset=['annee'])
        df_annee['age'] = 2026 - df_annee['annee']
    else:
        df_annee = pd.DataFrame()

    if not df_annee.empty:
        st.subheader("Historique d'installation")
        fig_timeline = px.histogram(
            df_annee, x='annee', color='categorie_type' if 'categorie_type' in df_annee.columns else None,
            title="Créations d'établissements par année", nbins=50
        )
        fig_timeline.update_layout(bargap=0.1, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vieillissement du parc (Âge en années)")
            if 'region_nom_bdd' in df_annee.columns:
                fig_age_box = px.box(
                    df_annee, x='region_nom_bdd', y='age', color='categorie_type' if 'categorie_type' in df_annee.columns else None,
                    title="Âge des structures par région"
                )
                fig_age_box.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_age_box, use_container_width=True)
                
        with col2:
            st.subheader("Corrélations")
            if 'score_services' in df_annee.columns:
                fig_corr = px.scatter(
                    df_annee, x='annee', y='score_services', color='categorie_type' if 'categorie_type' in df_annee.columns else None,
                    trendline="ols", title="Corrélation : Année de création vs Nombre de services",
                    opacity=0.6
                )
                fig_corr.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Données sur les années de création non disponibles.")
