import pandas as pd
import numpy as np
import joblib

# Charger le modèle et les encodeurs
model = joblib.load('best_model.pkl')
scaler = joblib.load('scaler.pkl')

# Charger la liste des caractéristiques
with open('features.txt', 'r') as f:
    features = f.read().split(',')

print(f"📋 Caractéristiques du modèle: {features}")

def safe_transform(encoder, value, default=0):
    """Transforme une valeur avec gestion des valeurs inconnues"""
    try:
        return encoder.transform([value])[0]
    except (ValueError, AttributeError):
        return default

def predict_winner(horse_data):
    """
    Prédit la probabilité de victoire d'un cheval
    
    horse_data: dict avec les champs:
        - rating: float
        - win_odds: float
        - weight: float
        - draw: float
        - trainer: str
        - jockey: str
        - sex: str (G = gelding, M = male, F = female)
    """
    # Créer un DataFrame avec les valeurs
    df = pd.DataFrame([{
        'rating': float(horse_data.get('rating', 0)),
        'win_odds': float(horse_data.get('win_odds', 10)),
        'weight': float(horse_data.get('weight', 120)),
        'draw': float(horse_data.get('draw', 5)),
        'trainer': str(horse_data.get('trainer', 'unknown')),
        'jockey': str(horse_data.get('jockey', 'unknown')),
        'race_no': int(horse_data.get('race_no', 1))
    }])
    
    # Créer les caractéristiques dérivées (comme dans ml_model_fixed.py)
    # 1. Rang de la cote (dans une course complète, on aurait besoin des autres chevaux)
    # Pour une prédiction individuelle, on utilise des valeurs par défaut
    df['odds_rank'] = 1  # Par défaut, on suppose que c'est le favori
    df['rating_rank'] = 1  # Par défaut, on suppose que c'est le meilleur rating
    df['weight_rating_ratio'] = df['weight'] / df['rating'] if df['rating'].iloc[0] > 0 else 0
    df['race_size'] = 10  # Taille moyenne d'une course
    df['top3_rating'] = 1 if df['rating_rank'].iloc[0] <= 3 else 0
    df['top3_odds'] = 1 if df['odds_rank'].iloc[0] <= 3 else 0
    
    # Fréquence de l'entraîneur (pour simplifier, on utilise une valeur moyenne)
    df['trainer_freq'] = 0.1
    df['jockey_freq'] = 0.1
    
    # S'assurer que toutes les colonnes existent
    for col in features:
        if col not in df.columns:
            df[col] = 0
    
    # Standardiser les caractéristiques numériques
    numeric_cols = ['rating', 'win_odds', 'weight', 'draw', 'weight_rating_ratio']
    
    # S'assurer que les colonnes existent
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0
    
    # Standardiser
    try:
        df[numeric_cols] = scaler.transform(df[numeric_cols])
    except Exception as e:
        print(f"⚠️ Erreur de standardisation: {e}")
        # Fallback: utiliser les valeurs brutes
        pass
    
    # Prédire
    proba = model.predict_proba(df[features])[0][1]
    return proba

def predict_multiple_horses(horses_data):
    """Prédit pour plusieurs chevaux d'une même course"""
    results = []
    for horse in horses_data:
        try:
            proba = predict_winner(horse)
            results.append({
                'name': horse.get('name', 'Unknown'),
                'probability': proba,
                'horse': horse
            })
        except Exception as e:
            print(f"⚠️ Erreur pour {horse.get('name', 'Unknown')}: {e}")
            results.append({
                'name': horse.get('name', 'Unknown'),
                'probability': 0.0,
                'horse': horse
            })
    
    # Trier par probabilité décroissante
    results.sort(key=lambda x: x['probability'], reverse=True)
    return results

# Exemple d'utilisation
if __name__ == "__main__":
    print("=" * 60)
    print("🔮 PRÉDICTION DES GAGNANTS")
    print("=" * 60)
    
    # Exemple : une course avec plusieurs chevaux
    course = [
        {'name': 'Cheval A', 'rating': 105, 'win_odds': 3.5, 'weight': 130, 'draw': 5, 'trainer': 'Chris Waller', 'jockey': 'James McDonald', 'race_no': 1},
        {'name': 'Cheval B', 'rating': 98, 'win_odds': 5.0, 'weight': 128, 'draw': 3, 'trainer': 'Ciaron Maher', 'jockey': 'Ethan Brown', 'race_no': 1},
        {'name': 'Cheval C', 'rating': 112, 'win_odds': 2.8, 'weight': 132, 'draw': 8, 'trainer': 'Joseph Pride', 'jockey': 'Nash Rawiller', 'race_no': 1},
        {'name': 'Cheval D', 'rating': 85, 'win_odds': 15.0, 'weight': 122, 'draw': 1, 'trainer': 'Bjorn Baker', 'jockey': 'Rachel King', 'race_no': 1},
    ]
    
    print("\n📋 Résultats de la prédiction:")
    results = predict_multiple_horses(course)
    
    for i, result in enumerate(results, 1):
        horse = result['horse']
        prob = result['probability']
        name = result['name']
        print(f"{i}. {name}: {prob:.2%} (Rating: {horse['rating']}, Cote: {horse['win_odds']})")
    
    print("\n" + "=" * 60)
    print(f"🏆 GAGNANT PRÉDIT: {results[0]['name']} avec {results[0]['probability']:.2%}")
    print("=" * 60)