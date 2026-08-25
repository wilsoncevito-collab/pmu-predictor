import pandas as pd
import joblib
from predict import predict_winner

# Charger les données existantes
df = pd.read_csv('courses_with_results.csv')

# Prendre une course comme exemple (la dernière)
last_race = df['race_no'].max()
race_data = df[df['race_no'] == last_race]

print(f"🔮 Prédiction pour la course {last_race}")
print("=" * 50)

# Prédire pour chaque cheval
results = []
for _, row in race_data.iterrows():
    horse = {
        'name': row['horse_name'],
        'rating': row['rating'],
        'win_odds': row['win_odds'],
        'weight': row['weight'],
        'draw': row['draw'],
        'trainer': row['trainer'],
        'jockey': row['jockey'],
        'sex': row['sex'] if pd.notna(row['sex']) else 'M'
    }
    
    proba = predict_winner(horse)
    results.append({
        'name': horse['name'],
        'probability': proba,
        'win_odds': horse['win_odds'],
        'rating': horse['rating'],
        'is_actual_winner': row['winner'] == 1
    })

# Trier par probabilité
results.sort(key=lambda x: x['probability'], reverse=True)

# Afficher les résultats
for i, r in enumerate(results, 1):
    winner_marker = "🏆" if r['is_actual_winner'] else ""
    print(f"{i}. {r['name']}: {r['probability']:.2%} (Cote: {r['win_odds']}, Rating: {r['rating']}) {winner_marker}")

print("=" * 50)
print(f"🏆 GAGNANT PRÉDIT: {results[0]['name']} avec {results[0]['probability']:.2%}")
print(f"✅ GAGNANT RÉEL: {[r['name'] for r in results if r['is_actual_winner']][0] if any(r['is_actual_winner'] for r in results) else 'Non trouvé'}")