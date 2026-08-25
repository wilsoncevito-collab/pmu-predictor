import json
import pandas as pd
from core.config import get_supabase

# Charger les données
with open('cotes_courses.json', 'r') as f:
    odds_data = json.load(f)

supabase = get_supabase()

print(f"📥 Import de {len(odds_data)} courses dans ZeroDB...")

for race in odds_data:
    race_no = race.get('raceNo')
    if race_no is None:
        continue
    
    # Créer une réunion fictive si besoin
    meeting_data = {
        'venue_code': 'HK',
        'meeting_date': '2026-08-22',
        'meeting_name': 'Réunion HK - 2026-08-22'
    }
    
    meeting_response = supabase.table('meetings').insert(meeting_data).execute()
    meeting_id = meeting_response.data[0]['id']
    
    # Créer la course
    race_data = {
        'meeting_id': meeting_id,
        'race_no': race_no,
        'total_runners': len(race.get('odds', {}).get('WIN', []))
    }
    
    race_response = supabase.table('races').insert(race_data).execute()
    race_id = race_response.data[0]['id']
    
    # Ajouter les runners
    odds = race.get('odds', {})
    win_odds = odds.get('WIN', [])
    
    for w in win_odds:
        runner_data = {
            'race_id': race_id,
            'runner_no': w.get('runnerNo'),
            'win_odds': w.get('odds'),
            'horse_name': f"Cheval {w.get('runnerNo')}"
        }
        supabase.table('runners').insert(runner_data).execute()
    
    print(f"   ✅ Course {race_no} importée")

print("✅ Import terminé !")