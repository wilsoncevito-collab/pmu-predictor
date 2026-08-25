import pandas as pd

def compare_from_csv():
    # Lire le fichier CSV
    df = pd.read_csv('courses_with_results.csv')
    
    # Nettoyer les données
    df['win_odds'] = pd.to_numeric(df['win_odds'], errors='coerce')
    df['winner'] = pd.to_numeric(df['winner'], errors='coerce').fillna(0)
    df['horse_number'] = pd.to_numeric(df['horse_number'], errors='coerce')
    df['race_no'] = pd.to_numeric(df['race_no'], errors='coerce')
    
    # Remplir les dates vides avec la date par défaut
    df['date'] = df['date'].fillna('2026-08-22')
    df['venue'] = df['venue'].fillna('S4')
    
    # Grouper par venue et race_no seulement (sans date)
    total_races = 0
    correct_predictions = 0
    
    grouped = df.groupby(['venue', 'race_no'])
    
    for (venue, race_no), group in grouped:
        total_races += 1
        
        # Filtrer les lignes avec des cotes valides
        valid = group[group['win_odds'].notna() & (group['win_odds'] > 0)]
        
        if len(valid) == 0:
            print(f"{venue} Course {race_no}: ⏳ Pas de cote valide")
            continue
        
        # Trouver le favori (cote la plus basse)
        favorite = valid.loc[valid['win_odds'].idxmin()]
        favorite_name = favorite['horse_name']
        favorite_odds = favorite['win_odds']
        favorite_number = favorite['horse_number']
        
        # Vérifier si le favori a gagné
        winner_row = group[group['winner'] == 1]
        
        if len(winner_row) == 0:
            print(f"{venue} Course {race_no}: ⏳ Pas de résultat")
            continue
        
        winner_number = winner_row.iloc[0]['horse_number']
        winner_name = winner_row.iloc[0]['horse_name']
        
        is_correct = favorite_number == winner_number
        if is_correct:
            correct_predictions += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{venue} Course {race_no}: {status} Favori: {favorite_name} ({favorite_odds}) → Gagnant: {winner_name}")
    
    # Statistiques
    print("\n" + "=" * 50)
    print("📊 STATISTIQUES DE PERFORMANCE")
    print("=" * 50)
    print(f"Total courses analysées: {total_races}")
    print(f"Prédictions correctes: {correct_predictions}")
    print(f"Taux de réussite: {(correct_predictions / total_races * 100) if total_races > 0 else 0:.2f}%")

if __name__ == '__main__':
    compare_from_csv()