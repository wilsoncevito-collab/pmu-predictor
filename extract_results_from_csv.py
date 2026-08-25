import pandas as pd
import json
from core.config import get_db
from core.models_sqlite import Meeting, Race, Runner, Result

def extract_results_from_csv():
    """Extrait les résultats depuis courses_with_results.csv"""
    
    csv_file = 'courses_with_results.csv'
    if not pd.io.common.file_exists(csv_file):
        print(f"❌ Fichier {csv_file} non trouvé")
        return 0
    
    df = pd.read_csv(csv_file)
    
    # Voir les colonnes disponibles
    print(f"Colonnes: {df.columns.tolist()}")
    
    # Nettoyer
    df['winner'] = pd.to_numeric(df['winner'], errors='coerce').fillna(0)
    df['horse_number'] = pd.to_numeric(df['horse_number'], errors='coerce')
    df['race_no'] = pd.to_numeric(df['race_no'], errors='coerce')
    df['date'] = df['date'].fillna('2026-08-22')
    
    # Filtrer les gagnants
    winners = df[df['winner'] == 1]
    
    if len(winners) == 0:
        print("⚠️ Aucun gagnant trouvé dans le CSV")
        return 0
    
    print(f"✅ {len(winners)} gagnants trouvés")
    
    db = get_db()
    
    # Récupérer toutes les réunions
    meetings = db.query(Meeting).all()
    
    count = 0
    for meeting in meetings:
        date_str = meeting.meeting_date
        print(f"\n📅 {date_str}")
        
        # Récupérer les courses de cette réunion
        races = db.query(Race).filter(Race.meeting_id == meeting.id).all()
        
        for race in races:
            race_no = race.race_no
            
            # Chercher le gagnant dans le CSV
            winner_row = winners[(winners['race_no'] == race_no)]
            
            if len(winner_row) == 0:
                print(f"   Course {race_no}: ⏳ Pas de résultat dans le CSV")
                continue
            
            winner_number = int(winner_row.iloc[0]['horse_number'])
            winner_name = winner_row.iloc[0]['horse_name']
            
            # Sauvegarder le résultat dans la base
            result = Result.save_result(race.id, winner_number, winner_name)
            
            # Marquer le runner comme gagnant
            db.query(Runner).filter(
                Runner.race_id == race.id,
                Runner.runner_no == winner_number
            ).update({'is_winner': True})
            
            db.commit()
            count += 1
            print(f"   ✅ Course {race_no}: {winner_name} gagne")
    
    db.close()
    print(f"\n✅ {count} résultats importés au total")
    return count

if __name__ == '__main__':
    extract_results_from_csv()