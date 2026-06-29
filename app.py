import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
from shapely.wkt import loads
import plotly.express as px

# 1. INITIALISATION DE L'APPLICATION
# Utilisation d'un thème Bootstrap pour un design soigné
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "Dashboard Décisionnel - Santé Togo"

# 2. PRÉPARATION DES DONNÉES
def clean_services(val):
    if pd.isna(val):
        return []
    cleaned = str(val).strip("{}")
    if not cleaned:
        return []
    return [s.strip() for s in cleaned.split(',')]

def load_data():
    missing_values = ["N/a", "N/A", "na", "NA", "None", "", "Nsp", "nan", "NaN"]
    df = pd.read_csv("Formations sanitaires  Publiques.csv", na_values=missing_values)
    df['geometry'] = df['geometry'].apply(loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    
    gdf['services_nettoyes'] = gdf['services_proposes'].apply(clean_services)
    gdf['annee'] = pd.to_numeric(gdf['annee'], errors='coerce')
    
    # Extraction des coordonnées pour Plotly Mapbox
    gdf['lat'] = gdf.geometry.y
    gdf['lon'] = gdf.geometry.x
    return gdf

# Chargement unique au démarrage
gdf = load_data()

# Préparation des listes pour les filtres
regions = ["Toutes"] + sorted([r for r in gdf['region_nom_bdd'].unique() if pd.notna(r)])
types = ["Tous"] + sorted([t for t in gdf['etablissement_type'].unique() if pd.notna(t)])
all_services = sorted(list(set([svc for sublist in gdf['services_nettoyes'] for svc in sublist])))

# 3. MISE EN PAGE (LAYOUT)
sidebar = html.Div(
    [
        html.H4("Filtres", className="display-6"),
        html.Hr(),
        html.Label("Région Administrative"),
        dcc.Dropdown(id='region-filter', options=[{'label': r, 'value': r} for r in regions], value="Toutes", clearable=False, className="mb-3"),
        
        html.Label("Type / Niveau de Spécialité"),
        dcc.Dropdown(id='type-filter', options=[{'label': t, 'value': t} for t in types], value="Tous", clearable=False, className="mb-3"),
        
        html.Label("Disponibilité des Services de Soins"),
        dcc.Dropdown(id='services-filter', options=[{'label': s, 'value': s} for s in all_services], multi=True, placeholder="Sélectionnez des services...", className="mb-3"),
    ],
    style={"padding": "2rem", "backgroundColor": "#f8f9fa", "height": "100vh"}
)

kpi_cards = dbc.Row([
    dbc.Col(dbc.Card(dbc.CardBody([html.H6("Infrastructures"), html.H3(id="kpi-infra")])), width=3),
    dbc.Col(dbc.Card(dbc.CardBody([html.H6("Régions Impactées"), html.H3(id="kpi-regions")])), width=3),
    dbc.Col(dbc.Card(dbc.CardBody([html.H6("Préfectures Couvertes"), html.H3(id="kpi-prefectures")])), width=3),
    dbc.Col(dbc.Card(dbc.CardBody([html.H6("Types de Soins Uniques"), html.H3(id="kpi-soins")])), width=3),
], className="mb-4")

tabs = dbc.Tabs(
    [
        dbc.Tab(label="Analyses Statisques & Spécialités", tab_id="tab-1", children=[
            dbc.Row([
                dbc.Col(dcc.Graph(id="bar-chart"), width=6),
                dbc.Col(dcc.Graph(id="pie-chart"), width=6),
            ], className="mt-4"),
            html.H5("Vue tabulaire des structures sélectionnées", className="mt-4"),
            dash_table.DataTable(
                id='data-table',
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '5px', 'fontFamily': 'sans-serif'},
                style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
            )
        ]),
        dbc.Tab(label="Évolution Temporelle", tab_id="tab-2", children=[
            dcc.Graph(id="line-chart", className="mt-4"),
            html.Div(id="recent-openings-info", className="mt-2 text-info fw-bold")
        ]),
        dbc.Tab(label="Cartographie & Densité", tab_id="tab-3", children=[
            html.Div([
                html.Label("Mode de visualisation : ", className="fw-bold me-2 mt-3"),
                dbc.RadioItems(
                    id="map-mode",
                    options=[
                        {"label": "Carte de Chaleur (Densité)", "value": "heat"},
                        {"label": "Marqueurs Individuels", "value": "markers"},
                    ],
                    value="heat",
                    inline=True,
                ),
            ], className="mb-3"),
            dcc.Graph(id="map-chart", style={"height": "60vh"})
        ]),
    ],
    id="tabs",
    active_tab="tab-1",
)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(sidebar, width=3),
        dbc.Col([
            html.H2("🇹🇬 Dashboard des Infrastructures Sanitaires du Togo", className="mt-4 mb-4"),
            kpi_cards,
            tabs
        ], width=9, style={"padding": "2rem"}),
    ])
], fluid=True)

# 4. CALLBACKS (LOGIQUE INTERACTIVE)
@app.callback(
    [
        Output("kpi-infra", "children"), Output("kpi-regions", "children"),
        Output("kpi-prefectures", "children"), Output("kpi-soins", "children"),
        Output("bar-chart", "figure"), Output("pie-chart", "figure"),
        Output("data-table", "data"), Output("data-table", "columns"),
        Output("line-chart", "figure"), Output("recent-openings-info", "children"),
        Output("map-chart", "figure")
    ],
    [
        Input("region-filter", "value"), Input("type-filter", "value"),
        Input("services-filter", "value"), Input("map-mode", "value")
    ]
)
def update_dashboard(selected_region, selected_type, selected_services, map_mode):
    # Filtrage des données
    dff = gdf.copy()
    if selected_region != "Toutes":
        dff = dff[dff['region_nom_bdd'] == selected_region]
    if selected_type != "Tous":
        dff = dff[dff['etablissement_type'] == selected_type]
    if selected_services:
        dff = dff[dff['services_nettoyes'].apply(lambda x: all(svc in x for svc in selected_services))]

    # Variables vides par défaut si pas de données
    empty_fig = px.bar(title="Aucune donnée pour cette sélection")
    
    if dff.empty:
        return "0", "0", "0", "0", empty_fig, empty_fig, [], [], empty_fig, "Aucune donnée récente.", empty_fig

    # KPIs
    kpi1 = f"{dff.shape[0]} / {gdf.shape[0]}"
    kpi2 = f"{dff['region_nom_bdd'].nunique()}"
    kpi3 = f"{dff['prefecture_nom_bdd'].nunique()}"
    total_services = len(set([svc for sublist in dff['services_nettoyes'] for svc in sublist]))
    kpi4 = f"{total_services}"

    # Tab 1: Bar Chart (Top Préfectures)
    data_pref = dff['prefecture_nom_bdd'].value_counts().head(10).reset_index()
    data_pref.columns = ['Préfecture', 'Nombre']
    fig_bar = px.bar(data_pref, x='Nombre', y='Préfecture', orientation='h', title="Top Préfectures", color='Nombre', color_continuous_scale='Viridis')
    fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False, margin=dict(l=0, r=0, t=30, b=0))

    # Tab 1: Pie Chart (Typologie)
    data_type = dff['etablissement_type'].value_counts().reset_index()
    data_type.columns = ['Type', 'Total']
    fig_pie = px.pie(data_type, values='Total', names='Type', hole=0.4, title="Niveau de Spécialité", color_discrete_sequence=px.colors.sequential.Plotly3)
    fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    # Tab 1: DataTable
    table_data = dff[['nom_fs', 'etablissement_type', 'region_nom_bdd', 'prefecture_nom_bdd']].to_dict('records')
    table_cols = [{"name": i, "id": i} for i in ['nom_fs', 'etablissement_type', 'region_nom_bdd', 'prefecture_nom_bdd']]

    # Tab 2: Line Chart (Temporel)
    df_time = dff[dff['annee'].notnull()].copy()
    if not df_time.empty:
        time_counts = df_time['annee'].astype(int).value_counts().sort_index().reset_index()
        time_counts.columns = ['Année', 'Ouvertures']
        time_counts['Cumul'] = time_counts['Ouvertures'].cumsum()
        fig_line = px.line(time_counts, x='Année', y='Cumul', title="Croissance cumulée du réseau sanitaire", markers=True)
        recent_count = df_time[df_time['annee'] >= 2015].shape[0]
        recent_text = f"ℹ️ Note d'analyse : {recent_count} structures de la sélection actuelle ont été ouvertes depuis 2015."
    else:
        fig_line = empty_fig
        recent_text = "Pas de données temporelles."

    # Tab 3: Cartographie
    lat_c = dff['lat'].mean() if not dff['lat'].isna().all() else 8.6
    lon_c = dff['lon'].mean() if not dff['lon'].isna().all() else 1.0

    if map_mode == "heat":
        # Densité (Heatmap)
        # On ajoute une colonne de "poids" = 1 pour forcer la carte de chaleur
        dff['weight'] = 1
        fig_map = px.density_mapbox(
            dff, lat='lat', lon='lon', z='weight', radius=15, 
            center=dict(lat=lat_c, lon=lon_c), zoom=6,
            mapbox_style="open-street-map", opacity=0.6,
            title="Carte de chaleur des infrastructures"
        )
    else:
        # Marqueurs individuels
        fig_map = px.scatter_mapbox(
            dff, lat='lat', lon='lon', hover_name='nom_fs',
            hover_data={'etablissement_type': True, 'prefecture_nom_bdd': True, 'annee': True, 'lat': False, 'lon': False},
            center=dict(lat=lat_c, lon=lon_c), zoom=7,
            mapbox_style="open-street-map",
            color_discrete_sequence=["#e74c3c"], size_max=15
        )
        fig_map.update_traces(marker=dict(size=9))
    
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    return kpi1, kpi2, kpi3, kpi4, fig_bar, fig_pie, table_data, table_cols, fig_line, recent_text, fig_map

if __name__ == '__main__':
    app.run(debug=True)