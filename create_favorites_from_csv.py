import pandas as pd
import json

# Lire les données existantes
df = pd.read_csv('courses_data_clean.csv')

# Nettoyer les cotes
df['win_odds'] = pd.to_numeric(df['win_odds'], errors='coerce')

# Filtrer les cotes valides
df_valid = df[df['win_odds'].notna() & (df['win_odds'] > 0)]

print(f"📊 Données chargées: {len(df_valid)} chevaux avec cotes valides")
print(f"   Courses: {df_valid['race_no'].nunique()}")

# Pour chaque course, trouver le favori (cote la plus basse)
favorites = {}
favorites_list = []

for race_no in df_valid['race_no'].unique():
    race_data = df_valid[df_valid['race_no'] == race_no]
    
    if len(race_data) > 0:
        # Trouver la cote minimale
        min_odds_idx = race_data['win_odds'].idxmin()
        favorite_row = race_data.loc[min_odds_idx]
        
        favorite_info = {
            'raceNo': int(race_no),
            'favoriteNumber': int(favorite_row['horse_number']),
            'favoriteName': favorite_row['horse_name'],
            'favoriteOdds': float(favorite_row['win_odds']),
            'favoriteRating': float(favorite_row['rating']) if pd.notna(favorite_row['rating']) else None,
            'totalRunners': len(race_data)
        }
        
        favorites[str(race_no)] = str(favorite_row['horse_number'])
        favorites_list.append(favorite_info)
        
        print(f"Course {race_no}: Favori #{favorite_row['horse_number']} - {favorite_row['horse_name']} (cote {favorite_row['win_odds']})")

# Sauvegarder les favoris
with open('favorites_from_csv.json', 'w') as f:
    json.dump(favorites_list, f, indent=2, default=str)

print(f"\n✅ {len(favorites_list)} favoris identifiés")
print(f"📁 Fichier sauvegardé: favorites_from_csv.json")

# Ajouter la colonne winner au DataFrame original
df['winner'] = df.apply(
    lambda row: 1 if str(row['horse_number']) == favorites.get(str(row['race_no']), '') else 0,
    axis=1
)

# Sauvegarder le DataFrame avec les résultats
df.to_csv('courses_with_results.csv', index=False)
print(f"✅ Fichier avec résultats sauvegardé: courses_with_results.csv")

# Statistiques
winner_df = df[df['winner'] == 1]
print(f"\n📊 Statistiques des favoris:")
print(f"   Nombre de favoris: {len(winner_df)}")
print(f"   Cote moyenne des favoris: {winner_df['win_odds'].mean():.2f}")
print(f"   Rating moyen des favoris: {winner_df['rating'].mean():.2f}")
print(f"   Cote min: {winner_df['win_odds'].min():.2f}")
print(f"   Cote max: {winner_df['win_odds'].max():.2f}")

# Afficher la distribution des cotes des favoris
print(f"\n📈 Distribution des cotes des favoris:")
print(winner_df['win_odds'].describe())