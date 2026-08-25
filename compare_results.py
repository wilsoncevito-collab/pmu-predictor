import pandas as pd
from core.config import get_db
from core.models_sqlite import Race, Runner, Result, Meeting
from datetime import datetime

def compare_predictions_vs_results():
    """Compare les prédictions avec les résultats réels"""
    db = get_db()
    
    # Récupérer toutes les réunions des 22, 23, 24 août
    meetings = db.query(Meeting).filter(
        Meeting.meeting_date.in_(['2026-08-22', '2026-08-23', '2026-08-24'])
    ).all()
    
    total_races = 0
    correct_predictions = 0
    results = []
    
    for meeting in meetings:
        print(f"\n📅 {meeting.meeting_date} - {meeting.meeting_name}")
        print("-" * 50)
        
        races = db.query(Race).filter(Race.meeting_id == meeting.id).all()
        
        for race in races:
            total_races += 1
            
            # Récupérer les runners
            runners = db.query(Runner).filter(Runner.race_id == race.id).all()
            
            # Récupérer le résultat
            result = db.query(Result).filter(Result.race_id == race.id).first()
            
            if not result:
                print(f"   Course {race.race_no}: ⏳ Pas de résultat")
                continue
            
            # Trouver le favori (cote la plus basse)
            favorite = None
            min_odds = float('inf')
            for runner in runners:
                if runner.win_odds and runner.win_odds < min_odds:
                    min_odds = runner.win_odds
                    favorite = runner
            
            if not favorite:
                print(f"   Course {race.race_no}: ⚠️ Pas de favori identifié")
                continue
            
            # Vérifier si le favori a gagné
            is_correct = favorite.runner_no == result.winner_number
            if is_correct:
                correct_predictions += 1
            
            result_data = {
                'date': meeting.meeting_date,
                'race_no': race.race_no,
                'favorite_name': favorite.horse_name,
                'favorite_odds': favorite.win_odds,
                'winner_name': result.winner_name,
                'winner_number': result.winner_number,
                'is_correct': is_correct
            }
            results.append(result_data)
            
            status = "✅" if is_correct else "❌"
            print(f"   Course {race.race_no}: {status} Favori: {favorite.horse_name} ({favorite.win_odds}) → Gagnant: {result.winner_name}")
    
    db.close()
    
    # Statistiques
    print("\n" + "=" * 50)
    print("📊 STATISTIQUES DE PERFORMANCE")
    print("=" * 50)
    print(f"Total courses analysées: {total_races}")
    print(f"Prédictions correctes: {correct_predictions}")
    print(f"Taux de réussite: {(correct_predictions / total_races * 100) if total_races > 0 else 0:.2f}%")
    
    # Créer un DataFrame pour l'export
    df = pd.DataFrame(results)
    df.to_csv('comparaison_predictions.csv', index=False)
    print(f"\n📁 Résultats détaillés sauvegardés dans comparaison_predictions.csv")
    
    return results

if __name__ == '__main__':
    compare_predictions_vs_results()