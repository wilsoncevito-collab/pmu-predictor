import json
import os
from datetime import datetime
from core.config import get_db
from core.models_sqlite import Meeting, Race, Runner, Result

def collect_results_for_date(day):
    """Collecte les résultats pour un jour donné (22, 23, 24)"""
    print(f"📡 Collecte des résultats du {day} août 2026...")
    
    # Nom du fichier sans le 2026-08-
    json_file = f'cotes_courses_{day}.json'
    if not os.path.exists(json_file):
        print(f"   ⚠️ Fichier {json_file} non trouvé")
        return 0
    
    with open(json_file, 'r', encoding='utf-8') as f:
        odds_data = json.load(f)
    
    db = get_db()
    
    # Date complète
    date_str = f'2026-08-{day}'
    
    # Récupérer la réunion
    meeting = db.query(Meeting).filter(Meeting.meeting_date == date_str).first()
    if not meeting:
        print(f"   ⚠️ Réunion du {date_str} non trouvée")
        db.close()
        return 0
    
    count = 0
    for idx, race in enumerate(odds_data):
        race_no = idx + 1
        
        # Récupérer la course
        race_obj = db.query(Race).filter(
            Race.meeting_id == meeting.id,
            Race.race_no == race_no
        ).first()
        
        if not race_obj:
            continue
        
        # Récupérer les résultats depuis l'API HKJC
        try:
            from hkjc_api import HorseRacingAPI
            api = HorseRacingAPI()
            result_data = api.getRaceResult(race_no)
            
            if result_data and result_data.get('runners'):
                for r in result_data.get('runners', []):
                    if r.get('position') == 1:
                        winner_number = r.get('runnerNo')
                        winner_name = r.get('horseName')
                        
                        # Sauvegarder le résultat
                        Result.save_result(race_obj.id, winner_number, winner_name)
                        
                        # Marquer le runner comme gagnant
                        db.query(Runner).filter(
                            Runner.race_id == race_obj.id,
                            Runner.runner_no == winner_number
                        ).update({'is_winner': True})
                        
                        db.commit()
                        print(f"   ✅ Course {race_no}: {winner_name} gagne")
                        count += 1
                        break
        except Exception as e:
            print(f"   ⚠️ Pas de résultat pour course {race_no}: {e}")
    
    db.close()
    return count

def collect_all_results():
    """Collecte les résultats pour les jours 22, 23, 24 août"""
    days = ['22', '23', '24']
    total = 0
    
    for day in days:
        count = collect_results_for_date(day)
        total += count
        print()
    
    print(f"✅ {total} résultats collectés au total")
    return total

if __name__ == '__main__':
    collect_all_results()