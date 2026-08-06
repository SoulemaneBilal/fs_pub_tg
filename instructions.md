# Instructions Dashboard — Système Sanitaire du Togo

## 1. Contexte & Objectif Stratégique

Ce dashboard vise à **piloter des projets d'amélioration du système sanitaire** au Togo. Il doit fournir une vision opérationnelle et stratégique de la couverture, de l'accessibilité et de la qualité des 792 établissements de santé. L'outil doit permettre :
- L'identification des **zones sous-desservies** (déserts médicaux)
- L'**optimisation de la répartition** des ressources humaines et matérielles
- Le **suivi de la couverture en services essentiels** (maternité, VIH/SIDA, paludisme, tuberculose, etc.)
- L'**analyse de l'accessibilité géographique** et temporelle
- La **priorisation des investissements** par région/préfecture

---

## 2. Arborescence du Projet

```
sante-dashboard/
├── app.py                      # Point d'entrée Dash avec multi-pages
├── requirements.txt            # dash, pandas, numpy, plotly, scipy, sklearn, geopy, folium
├── data/
│   ├── raw/
│   │   └── etablissements_sante.csv
│   └── processed/
│       └── etablissements_clean.parquet
├── pages/                      # Chaque fichier = une fenêtre du dashboard
│   ├── __init__.py
│   ├── p1_vue_globale.py       # Vue d'ensemble & KPIs
│   ├── p2_cartographie.py      # Carte interactive & heatmap spatiale
│   ├── p3_accessibilite.py     # Distances, isochrones, déserts médicaux
│   ├── p4_services.py          # Analyse des services proposés
│   ├── p5_temporel.py          # Évolution temporelle & vieillissement
│   └── p6_hierarchie.py        # Drill-down Région → Préfecture → Commune → Canton
├── components/
│   ├── __init__.py
│   ├── layout.py               # Layout commun (navbar, sidebar, thème)
│   ├── maps.py                 # Fonctions de cartographie (Plotly + Folium)
│   ├── kpis.py                 # Composants KPI
│   ├── filters.py              # Filtres globaux (région, type, secteur, services)
│   └── spatial_analysis.py     # Calculs de distance, clustering, Voronoi
├── utils/
│   ├── __init__.py
│   ├── data_loader.py          # Chargement, nettoyage, parsing des listes
│   ├── geo_utils.py            # Extraction lat/lon, calculs de distance
│   └── analytics.py            # Fonctions d'analyse statistique
└── assets/
    ├── style.css                 # Thème CSS professionnel (couleurs santé : bleu, vert, blanc)
    └── logo.png
```

---

## 3. Architecture Technique

- **Framework** : Dash (Plotly) avec `dash.page_registry` pour le routage multi-pages
- **Callbacks** : Tous les filtres globaux doivent être synchronisés via `dcc.Store`
- **Performance** : Utiliser `pandas` + `numpy` côté serveur. Pour 792 points, les calculs de distance matricielle sont faisables en mémoire.
- **Cartographie** : 
  - Plotly Scattermapbox / Densitymapbox pour les cartes interactives rapides
  - Folium pour les couches avancées (Voronoi, isochrones, buffers de distance)
- **Analyse spatiale** : `scipy.spatial.distance_matrix`, `sklearn.cluster.DBSCAN` pour le clustering spatial
- **Thème visuel** : Palette "Santé publique" — bleu médical (#0066CC), vert soin (#00A86B), alerte rouge (#E74C3C), neutre gris (#F5F5F5)

---

## 4. Prétraitement des Données (OBLIGATOIRE)

Avant toute visualisation, effectuer ces transformations dans `data_loader.py` :

### 4.1 Nettoyage des valeurs manquantes
- **Codes manquants** : `N/a`, `Nsp`, `N/A`, `NSP`, `None`, chaînes vides → `NaN`
- **annee** : Convertir en numérique, remplacer les NaN par `None` (afficher "Inconnue")
- **ouverture_jour** : Parser les accolades `{}` en listes Python. Si NaN → `[]`
- **services_proposes** : Parser les accolades en listes. Si NaN → `[]`
- **geometry** : Extraire `longitude` et `latitude` depuis `POINT (lon lat)` via regex

### 4.2 Enrichissement des données
- **score_accessibilite** : Nombre de jours d'ouverture par semaine (len de la liste des jours)
- **score_services** : Nombre total de services proposés par structure
- **categorie_type** : Regrouper `etablissement_type` en :
  - `USP` (USP 1, USP 2, CMS, etc. contenant "USP" ou "CMS")
  - `Hôpital` (Hopital 1, Hopital 2, CHU, etc. contenant "Hopital" ou "CHU")
  - `Spécialisé` (Polyclinique, Psychiatrique, etc.)
  - `Autre` (le reste)
- **services_critiques** : Liste de booléens pour chaque service essentiel :
  - `has_accouchement`, `has_vih`, `has_paludisme`, `has_tuberculose`, `has_vaccination`, `has_planification_familiale`, `has_urgences`, `has_laboratoire`
- **densite_region** : Nombre de structures par 10 000 habitants (nécessite données démographiques — si indisponibles, utiliser densité relative)
- **distance_plus_proche** : Pour chaque structure, distance (km) vers la structure de niveau supérieur la plus proche (USP → Hôpital, Hôpital → Hôpital de référence)

---

## 5. Description Détaillée des Fenêtres (Pages)

### PAGE 1 — Vue d'ensemble & KPIs Stratégiques (`p1_vue_globale.py`)
**Objectif** : Donner en 5 secondes l'état de santé du système.

**Layout** :
- **Row 1 — KPI Cards** (4-6 cartes en haut) :
  - `Total Structures` : 792
  - `Structures Publiques` : % vs Privées
  - `Taux de couverture USP` : % de communes avec au moins 1 USP
  - `Taux de couverture Hôpital` : % de préfectures avec au moins 1 Hôpital
  - `Moyenne Services/Structure` : score moyen
  - `Structures ouvertes 7j/7` : nombre et %

- **Row 2 — Graphiques** :
  - **Sunburst** (Plotly) : Hiérarchie Région → Préfecture → Commune, coloré par nombre de structures. Permet de cliquer pour zoomer.
  - **Bar chart horizontal** : Top 10 des préfectures par nombre de structures + moyenne de services
  - **Pie chart** : Répartition par `categorie_type` et par `secteur`

- **Row 3 — Tableau de synthèse** :
  - DataTable interactive avec tri/filtre : Région | Préfecture | Nb Structures | Nb USP | Nb Hôpitaux | Score Services Moyen | % Structures 7j/7

**Interactions** :
- Cliquer sur un segment du Sunburst filtre automatiquement les autres graphiques
- Les KPI cards doivent se mettre à jour dynamiquement selon les filtres globaux

---

### PAGE 2 — Cartographie Interactive (`p2_cartographie.py`)
**Objectif** : Visualiser la répartition géographique et identifier les clusters/déserts.

**Layout** :
- **Carte principale** (occupant 70% de l'écran) :
  - Scattermapbox avec tous les points colorés par `categorie_type`
  - Taille des points proportionnelle au `score_services`
  - Popup au clic : Nom, Type, Adresse, Services (liste), Jours d'ouverture, Année
  - **Couche de densité** (Densitymapbox) toggleable : heatmap des concentrations
  - **Fond de carte** : CartoDB positron (clair, professionnel)

- **Panneau latéral** (30%) :
  - **Filtres rapides** : Type, Secteur, Service spécifique (dropdown multiselect)
  - **Légende dynamique** : Compte des points visibles
  - **Mini-graphique** : Distribution des structures visibles par région

**Fonctionnalités avancées** :
- **Sélection par rectangle** (box select) sur la carte → zoom et filtre des autres pages
- **Affichage des noms de localités** au survol
- **Clustering automatique** : À zoom faible, regrouper les points proches en clusters numérotés

---

### PAGE 3 — Accessibilité Spatiale & Distances (`p3_accessibilite.py`)
**Objectif** : Mesurer l'accessibilité géographique, identifier les zones vulnérables, calculer les distances entre structures. **C'est la page la plus stratégique pour le pilotage de projets.**

**Layout** :
- **Section A — Matrice des distances** (tableau + heatmap) :
  - **Heatmap** : Distance moyenne entre structures d'une même région/préfecture
  - **Tableau** : Pour chaque structure, afficher :
    - Distance vers la structure de même type la plus proche
    - Distance vers le Hôpital/Polyclinique le plus proche
    - Distance vers la structure avec service d'accouchement le plus proche
    - Distance vers la structure avec laboratoire le plus proche
  - **Métrique clé** : "X% des USP sont à plus de Y km d'un hôpital"

- **Section B — Analyse des déserts médicaux** :
  - **Carte Folium** avec buffers circulaires (rayon configurable : 5km, 10km, 15km, 20km) autour de chaque structure
  - Zones sans chevauchement = déserts médicaux potentiels
  - **Coloration** : Vert (couvert par ≥2 structures), Orange (couvert par 1), Rouge (non couvert)
  - **Statistiques** : Surface (km²) et population estimée des zones non couvertes

- **Section C — Diagramme de Voronoi** :
  - Partitionner l'espace selon la structure la plus proche
  - Colorer les cellules par `score_services` ou `categorie_type`
  - Identifier les cellules de très grande superficie = zones mal desservies

- **Section D — Clustering spatial (DBSCAN)** :
  - Identifier les agglomérations de structures (clusters) vs les points isolés (noise)
  - Paramètres : eps=0.05 degrés (~5.5km), min_samples=2
  - Afficher les clusters sur une carte avec couleurs distinctes
  - Tableau : Nombre de clusters, taille moyenne, structures isolées

**Calculs de distance obligatoires** :
```python
# Utiliser la formule de Haversine pour les distances réelles en km
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))
```
- Calculer la **matrice de distance complète** (792×792) une fois au chargement, stocker dans un fichier `.npy` pour éviter de recalculer
- Pour chaque structure, calculer les k-plus-proches-voisins (k=1, 3, 5)

---

### PAGE 4 — Analyse des Services & Qualité (`p4_services.py`)
**Objectif** : Évaluer la couverture en services essentiels et identifier les lacunes.

**Layout** :
- **Row 1 — KPIs Services** :
  - % structures avec accouchement
  - % structures avec traitement VIH
  - % structures avec laboratoire
  - % structures avec urgences obstétricales
  - % structures avec vaccination enfant

- **Row 2 — Matrice de couverture** :
  - **Heatmap** : Services (axes Y) × Niveau administratif (axes X : Région ou Préfecture)
  - Valeur = % de structures dans cette zone proposant ce service
  - Color scale : Rouge (0%) → Jaune (50%) → Vert (100%)

- **Row 3 — Analyse des combinaisons de services** :
  - **Upset plot** ou **Venn simplifié** : Quelles combinaisons de services coexistent ?
  - Exemple : "Structures avec accouchement MAIS sans urgences obstétricales" → risque
  - **Bar chart** : Top 10 des combinaisons de services les plus fréquentes

- **Row 4 — Gap Analysis** :
  - Tableau des structures "à risque" : celles qui manquent des services critiques selon leur type
  - Exemple : USP 2 sans laboratoire, Hôpital sans urgences, etc.
  - Score de conformité par type d'établissement

---

### PAGE 5 — Évolution Temporelle & Vieillissement (`p5_temporel.py`)
**Objectif** : Comprendre l'historique d'installation et anticiper les besoins en rénovation.

**Layout** :
- **Row 1 — Timeline** :
  - **Histogramme cumulé** : Nombre de structures créées par décennie/année
  - **Line chart** : Évolution du nombre total de structures actives dans le temps
  - **Coloration** par type d'établissement

- **Row 2 — Vieillissement du parc** :
  - **Histogramme** : Distribution des âges des structures (2026 - annee)
  - **Box plot** : Âge moyen par région et par type
  - **Alerte** : Structures de plus de 50 ans (à rénover prioritairement)

- **Row 3 — Corrélations temporelles** :
  - Scatter : Année de création vs Nombre de services (les structures récentes ont-elles plus de services ?)
  - Bar chart : Nombre de structures créées par période (avant 1960, 1960-1980, 1980-2000, 2000-2010, 2010-2020, après 2020)

---

### PAGE 6 — Drill-down Hiérarchique (`p6_hierarchie.py`)
**Objectif** : Permettre une navigation descendante du national au canton pour le pilotage local.

**Layout** :
- **Sélecteurs en cascade** : Région → Préfecture → Commune → Canton (dropdowns dépendants)
- **Vue synthétique du niveau sélectionné** :
  - Carte zoomée sur la zone
  - Fiches des structures (cards) avec photo/infos
  - Radar chart comparant la zone sélectionnée à la moyenne nationale sur :
    - Densité de structures
    - Score services moyen
    - Accessibilité (jours d'ouverture)
    - Diversité des types
    - Couverture en services critiques

- **Tableau détaillé** : Toutes les structures du niveau sélectionné avec leurs attributs complets
- **Export** : Bouton "Télécharger le rapport PDF/Excel" pour la zone sélectionnée

---

## 6. Filtres Globaux (Sidebar Persistante)

Une sidebar à gauche, visible sur TOUTES les pages, contenant :
- **Région** : Multi-select (toutes les régions du dataset)
- **Préfecture** : Multi-select (dynamique selon région)
- **Type d'établissement** : Multi-select (USP 1, USP 2, Hopital 1, Hopital 2, etc.)
- **Secteur** : Radio (Tous / Public / Privé)
- **Service spécifique** : Multi-select (liste extraite de tous les services uniques)
- **Année** : Range slider (min-max des années connues)
- **Jours d'ouverture** : Multi-select (Lundi à Dimanche)
- **Bouton "Réinitialiser"**

Ces filtres doivent être stockés dans un `dcc.Store(id='global-filters')` et propagés à toutes les pages via callbacks.

---

## 7. Insights & Alertes Automatiques (Bandeau Supérieur)

En haut de chaque page, un bandeau d'alertes intelligent (collapsible) qui affiche dynamiquement :
- 🚨 **Alertes rouges** :
  - "X structures n'ont aucun service renseigné"
  - "Y USP sont à plus de 20km du hôpital le plus proche"
  - "Z structures n'ont pas de coordonnées GPS"

- ⚠️ **Alertes oranges** :
  - "Région [Nom] : seulement X% des structures proposent l'accouchement"
  - "A structures ont plus de 50 ans et nécessitent une évaluation"

- ✅ **Points positifs** :
  - "Région [Nom] : meilleure couverture en services VIH du pays"
  - "X% des structures sont ouvertes 7j/7"

Ces alertes doivent être recalculées à chaque changement de filtre.

---

## 8. Spécifications des Visualisations

### Couleurs par catégorie
| Catégorie | Couleur | Code HEX |
|-----------|---------|----------|
| USP 1 | Bleu clair | #5DADE2 |
| USP 2 | Bleu foncé | #2874A6 |
| CMS | Cyan | #17A589 |
| Hopital 1 | Vert | #00A86B |
| Hopital 2 | Vert foncé | #1E8449 |
| Polyclinique | Violet | #8E44AD |
| Spécialisé | Orange | #E67E22 |
| Public | Bleu | #0066CC |
| Privé | Gris bleu | #5D6D7E |
| Alerte/Désert | Rouge | #E74C3C |
| Warning | Orange | #F39C12 |
| OK | Vert | #27AE60 |

### Typography
- Titres : Inter ou Roboto, 24px, weight 600
- Sous-titres : 16px, weight 500, couleur #5D6D7E
- Corps : 14px, weight 400
- KPIs : 32px, weight 700

### Responsive
- Layout en grid CSS (`display: grid`)
- Sur écran < 1200px : passer la sidebar en hamburger menu
- Sur écran < 768px : empiler les graphiques verticalement

---

## 9. Performance & Optimisation

- **Chargement des données** : Utiliser `parquet` pour le dataset traité (plus rapide que CSV)
- **Matrice de distances** : Pré-calculer et sauvegarder dans `data/processed/distance_matrix.npy`
- **Callbacks** : Éviter les chaînes de callbacks longues. Utiliser `dash.callback` avec `allow_duplicate=True` si nécessaire.
- **Cartes** : Limiter le nombre de points affichés simultanément si > 1000 (ici 792, donc ok)
- **Memoization** : Utiliser `functools.lru_cache` sur les fonctions de calcul lourdes (matrice de distance, Voronoi)

---

## 10. Export & Partage

- **Bouton "Exporter le tableau"** : CSV/Excel sur chaque page avec tableau
- **Bouton "Exporter la vue"** : PNG/SVG de chaque graphique (via Plotly native)
- **Bouton "Générer le rapport"** (Page 6 uniquement) : Génère un PDF récapitulatif de la zone sélectionnée avec carte + tableaux + KPIs

---

## 11. Exemples de Questions que le Dashboard Doit Pouvoir Répondre

1. Quelles sont les 5 communes les plus sous-desservies en termes de distance à un hôpital ?
2. Quel est le taux de couverture en accouchement par région ?
3. Y a-t-il une corrélation entre l'ancienneté d'une structure et son nombre de services ?
4. Quelles structures publiques n'ont pas de coordonnées GPS ?
5. Quel est le nombre moyen de jours d'ouverture par type de structure ?
6. Où se situent les plus grands déserts médicaux (zones à > 15km de toute structure) ?
7. Quelles structures offrent le plus de services mais sont dans des zones déjà bien couvertes (redondance) ?
8. Quel est le ratio USP/Hôpital par préfecture ?
9. Quelles structures manquent des services critiques obligatoires pour leur type ?
10. Comment la densité de structures varie-t-elle entre le nord (Kara) et le sud (Maritime) ?

---

## 12. Notes Importantes pour l'Implémentation

- **Parsing des listes** : Les champs `ouverture_jour` et `services_proposes` utilisent le format `{item1,item2,item3}`. Il faut parser en retirant les accolades et en splittant sur la virgule.
- **Coordonnées GPS** : Le format est `POINT (longitude latitude)`. Extraire avec regex : `POINT\s*\(([-\d.]+)\s+([-
d.]+)\)`
- **Distances** : TOUJOURS utiliser la formule de Haversine, jamais la distance euclidienne sur des degrés (la Terre est sphérique).
- **Données démographiques** : Si non fournies, calculer des ratios relatifs (structures par km², ou structures par nombre de cantons) plutôt que des taux de couverture populationnelle.
- **Gestion des "Nsp"** : Dans les graphiques temporels, exclure les années inconnues ou les regrouper dans une catégorie "Date inconnue".
- **Services** : Certains services ont des noms très longs en français. Créer des labels courts pour les visualisations (ex: "Accouchement", "VIH/SIDA", "Paludisme", "Tuberculose", "Vaccination", "Planif. familiale", "Urgences", "Laboratoire").
