import json
from core.config import get_db
from core.models_sqlite import Meeting, Race, Runner

def import_date(date_str, file_name):
    print(f"📥 Import du {date_str} depuis {file_name}...")
    
    db = get_db()
    
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"   ⚠️ Fichier {file_name} non trouvé")
        db.close()
        return 0
    
    # Créer la réunion avec la date spécifique
    meeting = Meeting(
        venue_code='HK',
        meeting_date=date_str,
        meeting_name=f'Réunion HK - {date_str}'
    )
    db.add(meeting)
    db.commit()
    
    count = 0
    for idx, race in enumerate(data):
        race_no = idx + 1
        
        # Trouver les cotes WIN
        odds_list = race.get('odds', [])
        win_odds = None
        for item in odds_list:
            if item.get('oddsType') == 'WIN':
                win_odds = item.get('oddsNodes', [])
                break
        
        if not win_odds:
            continue
        
        # Créer la course
        race_obj = Race(
            meeting_id=meeting.id,
            race_no=race_no,
            total_runners=len(win_odds)
        )
        db.add(race_obj)
        db.commit()
        
        # Ajouter les runners
        for w in win_odds:
            odds_value = w.get('oddsValue')
            if odds_value == 'SCR' or not odds_value:
                continue
            
            try:
                odds_float = float(odds_value)
            except:
                continue
            
            runner_no = w.get('runnerNo')
            
            runner = Runner(
                race_id=race_obj.id,
                runner_no=runner_no,
                win_odds=odds_float,
                horse_name=f"Cheval {runner_no}"
            )
            db.add(runner)
        
        db.commit()
        count += 1
    
    db.close()
    print(f"   ✅ {count} courses importées pour le {date_str}")
    return count

if __name__ == '__main__':
    # Importer les 3 jours
    # 22 août = cotes_courses.json (fichier principal)
    import_date('2026-08-22', 'cotes_courses.json')
    import_date('2026-08-23', 'cotes_courses_23.json')
    import_date('2026-08-24', 'cotes_courses_24.json')
    print("\n✅ Import terminé !")