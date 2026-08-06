import folium
from folium import plugins
import pandas as pd

def create_base_map(center=[8.6, 0.98], zoom=7):
    """
    Crée une carte de base folium avec un joli design (CartoDB positron).
    """
    m = folium.Map(
        location=center, 
        zoom_start=zoom, 
        tiles="CartoDB positron", 
        control_scale=True,
        attr="CartoDB"
    )
    
    # Ajout de couches optionnelles pour plus de richesse
    folium.TileLayer(
        'OpenStreetMap',
        name='OpenStreetMap',
        attr='OpenStreetMap'
    ).add_to(m)
    
    # Outil plein écran
    plugins.Fullscreen(position='topright').add_to(m)
    
    return m

def get_color(value, color_map, default="#3388ff"):
    if pd.isna(value) or not color_map:
        return default
    return color_map.get(value, default)

def add_markers(m, df, lat_col="latitude", lon_col="longitude", 
               color_col=None, color_map=None, popup_cols=None, radius=6, use_cluster=False, layer_name="Structures"):
    """
    Ajoute des marqueurs personnalisés à la carte.
    """
    if df.empty or lat_col not in df.columns or lon_col not in df.columns:
        return m
        
    group = plugins.MarkerCluster(name=layer_name) if use_cluster else folium.FeatureGroup(name=layer_name)
    
    for _, row in df.iterrows():
        lat = row[lat_col]
        lon = row[lon_col]
        
        if pd.isna(lat) or pd.isna(lon):
            continue
            
        color = get_color(row.get(color_col) if color_col else None, color_map)
        
        # Construction du popup HTML
        html = "<div style='font-family: sans-serif; font-size: 13px; width: 250px;'>"
        if 'nom_fs' in row and pd.notna(row['nom_fs']):
            html += f"<h4 style='margin-bottom:5px; margin-top:0; color:#2c3e50;'>{row['nom_fs']}</h4><hr style='margin:5px 0;'>"
            
        if popup_cols:
            for col, label in popup_cols.items():
                val = row.get(col, 'N/A')
                html += f"<b>{label}</b>: {val}<br>"
        html += "</div>"
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            weight=1.5,
            popup=folium.Popup(html, max_width=300),
            tooltip=row.get('nom_fs', 'Détails')
        ).add_to(group)
        
    group.add_to(m)
    return m
