import json
import os
import pandas as pd
from datetime import datetime
from core.config import get_db
from core.models_sqlite import Meeting, Race, Runner

def get_horse_names_from_csv():
    """Récupère les noms des chevaux depuis courses_with_results.csv"""
    names_dict = {}
    if os.path.exists('courses_with_results.csv'):
        df = pd.read_csv('courses_with_results.csv')
        for _, row in df.iterrows():
            race_no = row.get('race_no')
            horse_number = row.get('horse_number')
            horse_name = row.get('horse_name')
            if pd.notna(race_no) and pd.notna(horse_number) and pd.notna(horse_name):
                key = f"{int(race_no)}_{int(horse_number)}"
                names_dict[key] = horse_name
    return names_dict

def import_from_json():
    db = get_db()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'cotes_courses.json')
    
    if not os.path.exists(json_path):
        return f"❌ Fichier non trouvé: {json_path}"
    
    # Charger les noms depuis courses_with_results.csv
    names_dict = get_horse_names_from_csv()
    print(f"📋 {len(names_dict)} noms de chevaux chargés")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        odds_data = json.load(f)
    
    # Utiliser la date d'aujourd'hui
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Supprimer les anciennes données
    db.query(Runner).delete()
    db.query(Race).delete()
    db.query(Meeting).delete()
    db.commit()
    
    # Créer une réunion avec la date du jour
    meeting = Meeting(
        venue_code='HK',
        meeting_date=today,
        meeting_name=f'Réunion HK - {today}'
    )
    db.add(meeting)
    db.commit()
    
    count = 0
    for idx, race in enumerate(odds_data):
        odds_list = race.get('odds', [])
        
        win_odds = None
        for item in odds_list:
            if item.get('oddsType') == 'WIN':
                win_odds = item.get('oddsNodes', [])
                break
        
        if not win_odds:
            continue
        
        race_no = idx + 1
        race_obj = Race(
            meeting_id=meeting.id,
            race_no=race_no,
            total_runners=len(win_odds)
        )
        db.add(race_obj)
        db.commit()
        
        for w in win_odds:
            odds_value = w.get('oddsValue')
            if odds_value == 'SCR' or not odds_value:
                continue
            
            try:
                odds_float = float(odds_value)
            except (ValueError, TypeError):
                continue
            
            runner_no = w.get('runnerNo')
            
            # Récupérer le nom depuis le CSV
            key = f"{race_no}_{runner_no}"
            horse_name = names_dict.get(key, f"Cheval {runner_no}")
            
            runner = Runner(
                race_id=race_obj.id,
                runner_no=runner_no,
                win_odds=odds_float,
                horse_name=horse_name,
                rating=0,
                draw=None,
                trainer=None,
                jockey=None
            )
            db.add(runner)
        
        db.commit()
        count += 1
    
    db.close()
    return f"✅ {count} courses importées pour le {today} avec les vrais noms"

if __name__ == '__main__':
    print(import_from_json())