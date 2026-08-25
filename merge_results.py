import pandas as pd
import json

# Lire les données existantes
df = pd.read_csv('courses_data_clean.csv')

# Lire les résultats
with open('resultats_courses.json', 'r') as f:
    results_data = json.load(f)

# Créer un dictionnaire des gagnants par course
winners = {}
for race_result in results_data:
    race_no = race_result['raceNo']
    if race_result['result'] and 'runners' in race_result['result']:
        for runner in race_result['result']['runners']:
            if runner.get('position') == 1:
                winners[race_no] = runner.get('runnerNo') or runner.get('no')
                break

# Ajouter la colonne 'winner' au DataFrame
df['winner'] = df.apply(
    lambda row: 1 if str(row['horse_number']) == str(winners.get(row['race_no'], -1)) else 0,
    axis=1
)

# Sauvegarder le fichier avec les résultats
df.to_csv('courses_with_results.csv', index=False)
print(f"✅ Fichier avec résultats sauvegardé: courses_with_results.csv")
print(f"   Nombre de courses avec gagnant identifié: {len(winners)}")
print(f"   Nombre de chevaux gagnants dans les données: {df['winner'].sum()}")