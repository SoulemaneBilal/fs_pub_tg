# Togo Santé - Dashboard d'Analyse du Système Sanitaire

Ce projet est une application de tableau de bord interactive développée avec **Streamlit** pour analyser et piloter les projets d'amélioration du système sanitaire au Togo. Il fournit une vue stratégique et opérationnelle sur les 792 établissements de santé du pays.

## 🎯 Objectifs

L'outil permet de :
- Identifier les zones sous-desservies (déserts médicaux)
- Optimiser la répartition des ressources et la planification
- Suivre la couverture en services essentiels (maternité, laboratoires, etc.)
- Analyser l'accessibilité spatiale (distance, clusters)
- Mener des analyses hiérarchiques par région, préfecture et commune

## 🚀 Fonctionnalités Principales

1. **Vue Globale & KPIs** : Une synthèse rapide de l'état du système de santé (nombre de structures, taux de couverture).
2. **Cartographie Interactive (Folium)** : Représentation spatiale détaillée des infrastructures de santé avec des couches personnalisées, clusters et info-bulles, rendue élégante grâce à `streamlit-folium`.
3. **Accessibilité Spatiale** : Cartes de chaleur (HeatMap) et algorithme de clustering spatial (DBSCAN) pour identifier les déserts médicaux.
4. **Analyse des Services** : Évaluation de la couverture et des combinaisons de services vitaux proposés par les formations sanitaires.
5. **Évolution Temporelle** : Visualisation de l'historique d'installation et du vieillissement du parc.
6. **Drill-down Hiérarchique** : Navigation granulaire (Région → Préfecture → Commune → Canton) pour une analyse focalisée sur une zone précise.

## 🛠️ Stack Technique

- **Interface Web** : [Streamlit](https://streamlit.io/)
- **Manipulation de Données** : Pandas, NumPy, PyArrow
- **Cartographie & Graphes** : Folium, Streamlit-Folium, Plotly Express
- **Analyse Spatiale** : Scikit-learn (DBSCAN), SciPy

## 📦 Installation et Lancement

1. Clonez ce dépôt :
```bash
git clone https://github.com/SoulemaneBilal/fs_pub_tg.git
cd fs_pub_tg
```

2. Créez un environnement virtuel (recommandé) et installez les dépendances :
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Lancez l'application Streamlit :
```bash
streamlit run app.py
```

L'application sera accessible depuis votre navigateur à l'adresse locale `http://localhost:8501`.

## 📁 Structure du Projet

- `app.py` : Point d'entrée de l'application Streamlit
- `pages/` : Modules contenant les différentes pages de l'application (Vue globale, Cartographie, Accessibilité, etc.)
- `utils/` : Fonctions utilitaires (traitement de données, génération de cartes folium centralisée)
- `data/` : Dossier hébergeant les données (brutes et traitées via parquet)
- `components/` : Composants réutilisables d'analyse et de visualisation

## 🤝 Contribution

Toute contribution visant à améliorer l'analyse, ajouter de nouveaux jeux de données ou optimiser le code est la bienvenue.
