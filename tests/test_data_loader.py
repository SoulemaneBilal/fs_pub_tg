import pytest
import pandas as pd
import numpy as np
import os
from utils.data_loader import load_and_clean_data

@pytest.fixture
def dummy_csv_path(tmp_path):
    """Création d'un faux fichier CSV pour les tests."""
    file_path = tmp_path / "dummy_data.csv"
    data = {
        'etablissement_nom': ['USP Lomé', 'Hopital Kara', 'Clinique privée'],
        'etablissement_type': ['USP 1', 'HOPITAL 2', 'POLYCLINIQUE'],
        'annee': ['2015', 'Nsp', '2020'],
        'geometry': ['POINT (1.22 6.12)', 'POINT (1.15 9.55)', 'POINT (None None)'],
        'ouverture_jour': ['{Lundi, Mardi}', '{}', '{Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi, Dimanche}'],
        'services_proposes': ['{has_accouchement, has_paludisme}', '{has_urgences, has_laboratoire, has_vih}', 'N/A']
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    return file_path

def test_load_and_clean_data(dummy_csv_path):
    df_clean = load_and_clean_data(dummy_csv_path)
    
    # 1. Vérifier la taille
    assert len(df_clean) == 3
    
    # 2. Vérifier le typage des catégories
    assert df_clean.iloc[0]['categorie_type'] == 'USP'
    assert df_clean.iloc[1]['categorie_type'] == 'Hôpital'
    assert df_clean.iloc[2]['categorie_type'] == 'Spécialisé'
    
    # 3. Vérifier l'extraction de l'année (Gestion des Nsp)
    assert df_clean.iloc[0]['annee'] == 2015
    assert pd.isna(df_clean.iloc[1]['annee'])
    
    # 4. Vérifier l'extraction des coordonnées
    assert df_clean.iloc[0]['longitude'] == 1.22
    assert df_clean.iloc[0]['latitude'] == 6.12
    assert pd.isna(df_clean.iloc[2]['longitude'])
    
    # 5. Vérifier le parsing des listes et les scores
    assert df_clean.iloc[0]['score_accessibilite'] == 2  # Lundi, Mardi
    assert df_clean.iloc[1]['score_accessibilite'] == 0  # {}
    assert df_clean.iloc[2]['score_accessibilite'] == 7  # 7 jours
    
    # 6. Vérifier les services booléens critiques
    assert df_clean.iloc[0]['has_accouchement'] == True
    assert df_clean.iloc[0]['has_laboratoire'] == False
    assert df_clean.iloc[1]['has_urgences'] == True
