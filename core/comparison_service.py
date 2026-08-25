import pandas as pd
import os

def get_comparison_stats():
    """Récupère les statistiques de comparaison"""
    
    if not os.path.exists('courses_with_results.csv'):
        return {
            'total_races': 0,
            'correct_predictions': 0,
            'win_rate': 0,
            'avg_odds': 0,
            'roi': 0,
            'results': []
        }
    
    df = pd.read_csv('courses_with_results.csv')
    
    # Nettoyer
    df['win_odds'] = pd.to_numeric(df['win_odds'], errors='coerce')
    df['winner'] = pd.to_numeric(df['winner'], errors='coerce').fillna(0)
    df['horse_number'] = pd.to_numeric(df['horse_number'], errors='coerce')
    df['race_no'] = pd.to_numeric(df['race_no'], errors='coerce')
    df['date'] = df['date'].fillna('2026-08-22')
    df['venue'] = df['venue'].fillna('S4')
    
    results = []
    total_races = 0
    correct = 0
    favorites_odds = []
    
    grouped = df.groupby(['venue', 'race_no'])
    
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
        
        winner_number = winner_row.iloc[0]['horse_number']
        winner_name = winner_row.iloc[0]['horse_name']
        favorite_number = favorite['horse_number']
        favorite_name = favorite['horse_name']
        is_correct = favorite_number == winner_number
        
        if is_correct:
            correct += 1
        
        results.append({
            'venue': str(venue),
            'race_no': int(race_no),
            'favorite_name': str(favorite_name),
            'favorite_odds': float(favorite_odds),
            'winner_name': str(winner_name),
            'is_correct': bool(is_correct)  # Convertir en bool Python standard
        })
    
    win_rate = (correct / total_races * 100) if total_races > 0 else 0
    avg_odds = sum(favorites_odds) / len(favorites_odds) if favorites_odds else 0
    roi = (correct / total_races * avg_odds - 1) if total_races > 0 else 0
    
    return {
        'total_races': int(total_races),
        'correct_predictions': int(correct),
        'win_rate': round(win_rate, 2),
        'avg_odds': round(avg_odds, 2),
        'roi': round(roi * 100, 2),
        'results': results
    }