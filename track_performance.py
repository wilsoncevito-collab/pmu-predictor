import pandas as pd
from datetime import datetime

def track_performance():
    """Affiche un résumé des performances"""
    
    if not pd.io.common.file_exists('courses_with_results.csv'):
        print("❌ Fichier non trouvé")
        return
    
    df = pd.read_csv('courses_with_results.csv')
    
    # Nettoyer
    df['win_odds'] = pd.to_numeric(df['win_odds'], errors='coerce')
    df['winner'] = pd.to_numeric(df['winner'], errors='coerce').fillna(0)
    df['horse_number'] = pd.to_numeric(df['horse_number'], errors='coerce')
    df['race_no'] = pd.to_numeric(df['race_no'], errors='coerce')
    
    # Date
    df['date'] = df['date'].fillna('2026-08-22')
    df['venue'] = df['venue'].fillna('S4')
    
    # Analyser par course
    grouped = df.groupby(['venue', 'race_no'])
    
    total_races = 0
    correct = 0
    favorites_odds = []
    
    for (venue, race_no), group in grouped:
        total_races += 1
        
        valid = group[group['win_odds'].notna() & (group['win_odds'] > 0)]
        if len(valid) == 0:
            continue
        
        favorite = valid.loc[valid['win_odds'].idxmin()]
        favorite_odds = favorite['win_odds']
        favorites_odds.append(favorite_odds)
        
        winner_row = group[group['winner'] == 1]
        if len(winner_row) == 0:
            continue
        
        if favorite['horse_number'] == winner_row.iloc[0]['horse_number']:
            correct += 1
    
    # Résultats
    print("=" * 50)
    print("📊 PERFORMANCE GLOBALE")
    print("=" * 50)
    print(f"Total courses: {total_races}")
    print(f"Prédictions correctes: {correct}")
    print(f"Taux de réussite: {(correct/total_races*100):.2f}%")
    
    if favorites_odds:
        print(f"Cote moyenne des favoris: {sum(favorites_odds)/len(favorites_odds):.2f}")
        print(f"ROI simulé (tous les paris): {(correct/total_races) * (sum(favorites_odds)/len(favorites_odds)) - 1:.2%}")

if __name__ == '__main__':
    track_performance()