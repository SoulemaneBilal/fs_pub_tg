import numpy as np
from math import radians, cos, sin, asin, sqrt, atan2
from scipy.spatial import distance_matrix

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcule la distance du grand cercle en kilomètres entre deux points 
    sur la terre (spécifiés en degrés décimaux).
    """
    R = 6371.0 # Rayon de la terre en km
    
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))

def calculate_distance_matrix(df):
    """
    Calcule la matrice de distances complète pour tous les points du dataframe.
    """
    # Filtrer les points sans coordonnées
    valid_coords = df.dropna(subset=['latitude', 'longitude'])
    coords = valid_coords[['latitude', 'longitude']].values
    
    # Initialisation de la matrice (n x n)
    n = len(coords)
    dist_matrix = np.zeros((n, n))
    
    # Calcul via Haversine
    for i in range(n):
        for j in range(i+1, n):
            dist = haversine(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
            
    return dist_matrix
