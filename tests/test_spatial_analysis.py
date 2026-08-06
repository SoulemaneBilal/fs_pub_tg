import pytest
import numpy as np
import pandas as pd
from components.spatial_analysis import haversine, calculate_distance_matrix

def test_haversine():
    # Distance entre Lomé (6.13, 1.22) et Kara (9.55, 1.15)
    # Approximativement 380 km
    lat1, lon1 = 6.13, 1.22
    lat2, lon2 = 9.55, 1.15
    
    dist = haversine(lat1, lon1, lat2, lon2)
    
    assert 370 < dist < 390  # Vérification de l'ordre de grandeur

def test_haversine_same_point():
    # Distance vers soi-même = 0
    assert haversine(6.13, 1.22, 6.13, 1.22) == 0.0

def test_calculate_distance_matrix():
    data = {
        'etablissement_nom': ['Point A', 'Point B', 'Point C'],
        'latitude': [0.0, 1.0, 0.0],
        'longitude': [0.0, 0.0, 1.0]
    }
    df = pd.DataFrame(data)
    
    matrix = calculate_distance_matrix(df)
    
    # 3 points -> matrice 3x3
    assert matrix.shape == (3, 3)
    
    # La diagonale doit être 0
    assert np.all(np.diag(matrix) == 0)
    
    # Symétrie
    assert matrix[0, 1] == matrix[1, 0]
    
    # Point A à Point B (1 degré de latitude ~ 111 km)
    assert 110 < matrix[0, 1] < 112
    
    # Point A à Point C (1 degré de longitude à l'équateur ~ 111 km)
    assert 110 < matrix[0, 2] < 112
