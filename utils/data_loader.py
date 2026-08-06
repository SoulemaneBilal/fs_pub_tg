import pandas as pd
import numpy as np
import re
import os

def load_and_clean_data(file_path):
    """
    Charge le fichier brut CSV, nettoie les données et retourne un DataFrame propre.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier non trouvé : {file_path}")
        
    df = pd.read_csv(file_path)
    
    # 1. Nettoyage des valeurs manquantes
    na_values = ['N/a', 'Nsp', 'N/A', 'NSP', 'None', '', ' ']
    df.replace(na_values, np.nan, inplace=True)
    
    # annee : Convertir en numérique, remplacer les NaN par None
    if 'annee' in df.columns:
        df['annee'] = pd.to_numeric(df['annee'], errors='coerce')
        df['annee'] = df['annee'].replace({np.nan: None})
        
    # Helper pour parser les listes {}
    def parse_set_string(val):
        if pd.isna(val) or val == '{}':
            return []
        val = str(val).strip('{}')
        return [v.strip() for v in val.split(',')] if val else []

    if 'ouverture_jour' in df.columns:
        df['ouverture_jour'] = df['ouverture_jour'].apply(parse_set_string)
        
    if 'services_proposes' in df.columns:
        df['services_proposes'] = df['services_proposes'].apply(parse_set_string)

    # geometry : Extraire longitude et latitude
    if 'geometry' in df.columns:
        def extract_lon_lat(geom_str):
            if pd.isna(geom_str):
                return np.nan, np.nan
            match = re.search(r'POINT\s*\(([-\d.]+)\s+([-\d.]+)\)', str(geom_str))
            if match:
                return float(match.group(1)), float(match.group(2))
            return np.nan, np.nan
            
        coords = df['geometry'].apply(extract_lon_lat)
        df['longitude'] = [c[0] for c in coords]
        df['latitude'] = [c[1] for c in coords]

    # 2. Enrichissement des données
    # score_accessibilite : Nombre de jours d'ouverture par semaine
    if 'ouverture_jour' in df.columns:
        df['score_accessibilite'] = df['ouverture_jour'].apply(len)
        
    # score_services : Nombre total de services proposés
    if 'services_proposes' in df.columns:
        df['score_services'] = df['services_proposes'].apply(len)
        
    # categorie_type
    if 'etablissement_type' in df.columns:
        def categorize_type(t):
            if pd.isna(t):
                return 'Autre'
            t_upper = str(t).upper()
            if 'USP' in t_upper or 'CMS' in t_upper:
                return 'USP'
            elif 'HOPITAL' in t_upper or 'HÔPITAL' in t_upper or 'CHU' in t_upper:
                return 'Hôpital'
            elif 'POLYCLINIQUE' in t_upper or 'PSYCHIATRIQUE' in t_upper:
                return 'Spécialisé'
            return 'Autre'
        df['categorie_type'] = df['etablissement_type'].apply(categorize_type)

    # services_critiques
    if 'services_proposes' in df.columns:
        services_map = {
            'has_accouchement': 'Accouchement',
            'has_vih': 'VIH',
            'has_paludisme': 'Paludisme',
            'has_tuberculose': 'Tuberculose',
            'has_vaccination': 'Vaccination',
            'has_planification_familiale': 'Planification',
            'has_urgences': 'Urgences',
            'has_laboratoire': 'Laboratoire'
        }
        
        for col, keyword in services_map.items():
            df[col] = df['services_proposes'].apply(
                lambda x: any(keyword.lower() in str(s).lower() for s in x) if isinstance(x, list) else False
            )

    return df

def process_and_save(raw_path='data/raw/etablissements_sante.csv', processed_path='data/processed/etablissements_clean.parquet'):
    """
    Exécute le pipeline de nettoyage et sauvegarde en Parquet.
    """
    df = load_and_clean_data(raw_path)
    
    # Créer le répertoire processed si inexistant
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    
    # Sauvegarde
    df.to_parquet(processed_path, index=False)
    print(f"Données traitées et sauvegardées dans {processed_path}")
    return df
